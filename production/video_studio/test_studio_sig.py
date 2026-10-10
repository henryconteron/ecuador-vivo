"""Integrated SIG/Studio shares the canonical document; synthetic data only."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from studio_home import create_project
from studio_project import publish_document, source_projection, workspace_key
from studio_workspace import WorkspaceSession
from test_studio_science import scientific_fixture


class SigTests(unittest.TestCase):
    def proposal(self):
        from studio_preparation import create_from_review
        from studio_editing import snapshot_revision
        source, snapshot = scientific_fixture()
        review = {'source': source, 'snapshot': snapshot, 'revision': snapshot_revision(snapshot)}
        with patch('studio_preparation.verify_sources'):
            return create_from_review(review, {'id': 'youtube'}, selected=['mean'], duration=.1)

    def test_scientific_transfer_preserves_document_scenes_and_is_idempotent(self):
        from studio_sig import merge_scientific_proposal
        old = create_project('free', {'id': 'youtube'})
        before = copy.deepcopy(old)
        with patch('data.load_values', side_effect=AssertionError('Presentation recalculated')):
            merged, selected = merge_scientific_proposal(old, self.proposal())
            again, repeated = merge_scientific_proposal(merged, self.proposal())
        self.assertEqual(old, before)
        self.assertEqual(merged['project_meta']['id'], old['project_meta']['id'])
        self.assertEqual(merged['studio']['scenes'][0], old['studio']['scenes'][0])
        self.assertEqual(merged['studio']['timeline'][0], old['studio']['timeline'][0])
        self.assertEqual(again, merged)
        self.assertEqual(repeated, selected)
        self.assertTrue(merged['studio']['calculations'])

    def test_transfer_commit_undo_redo_reopen_and_visual_edit_preserve_science(self):
        from studio_sig import merge_scientific_proposal
        from studio_recovery import recover_snapshot
        old = create_project('free', {'id': 'youtube'})
        state = {}; publish_document(state, old)
        key = workspace_key(old)
        with tempfile.TemporaryDirectory() as root:
            session = WorkspaceSession(state, key, source_projection(old), store=root, canonical=True)
            candidate, scene = merge_scientific_proposal(old, self.proposal())
            session.commit(candidate); state[key+'_selected'] = scene
            science = copy.deepcopy(session.project['studio']['calculations'])
            identity = session.project['project_meta']['id']
            session.dispatch({'version':session.version, 'scene':scene, 'action':'undo'})
            self.assertEqual(session.project['studio']['scenes'], old['studio']['scenes'])
            session.dispatch({'version':session.version, 'scene':session.selected, 'action':'redo'})
            self.assertEqual(session.project['project_meta']['id'], identity)
            self.assertEqual(session.project['studio']['calculations'], science)
            recovered, _ = recover_snapshot(Path(state[key+'_draft']))
            self.assertEqual(recovered, session.project)
            self.assertEqual(workspace_key(recovered), key)

    def test_conflicting_registry_and_profile_are_rejected_without_mutation(self):
        from studio_sig import merge_scientific_proposal
        old = create_project('free', {'id': 'youtube'})
        proposal = self.proposal()
        old['studio']['calculations'] = copy.deepcopy(proposal['studio']['calculations'])
        next(iter(old['studio']['calculations'].values()))['value'] = 999
        before = copy.deepcopy(old)
        with self.assertRaises(ValueError): merge_scientific_proposal(old, proposal)
        self.assertEqual(old, before)
        old = create_project('free', {'id':'instagram_square'})
        with self.assertRaises(ValueError): merge_scientific_proposal(old, proposal)

    def test_sig_and_home_navigation_do_not_replace_or_recalculate_document(self):
        from streamlit.testing.v1 import AppTest
        def script():
            import streamlit as st
            from studio_sig import show_sig
            from studio_project import consume_studio_navigation, source_projection
            consume_studio_navigation(st.session_state)
            if st.session_state.get('section') == 'SIG':
                show_sig(source_projection(st.session_state['project_document']))
        with tempfile.TemporaryDirectory() as root, patch('studio_workspace.STORE', Path(root)):
            app = AppTest.from_function(script, default_timeout=20)
            old = create_project('free', {'id':'youtube'})
            app.session_state['project_document'] = old
            app.session_state['section'] = 'SIG'
            with patch('data.load_values', side_effect=AssertionError('Navigation requested raster')):
                app.run(); self.assertFalse(app.exception)
                app.button(key='sig_studio').click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state['section'], 'Editor')
            self.assertEqual(app.session_state['studio_phase'], 'Estudio')
            self.assertEqual(app.session_state['project_document'], old)

    def test_sig_prepared_review_uses_shared_profile_and_commits_to_existing_identity(self):
        from streamlit.testing.v1 import AppTest
        from studio_preparation import ROOT, execute
        from jobs import write_json
        import uuid
        source, snapshot = scientific_fixture()
        job = ROOT / ('sig-test-'+uuid.uuid4().hex); job.mkdir(parents=True)
        write_json(job/'source.json', source)
        with patch('studio_preparation.capture_snapshot', return_value=snapshot): execute(job)
        def script():
            import streamlit as st
            from studio_sig import show_sig
            from studio_project import source_projection
            show_sig(source_projection(st.session_state['project_document']))
        old = create_project('free', {'id':'youtube'})
        with tempfile.TemporaryDirectory() as root, patch('studio_workspace.STORE', Path(root)):
            app = AppTest.from_function(script, default_timeout=20)
            app.session_state['project_document'] = old
            app.session_state['science_job'] = str(job)
            app.run(); self.assertFalse(app.exception)
            app.selectbox(key=workspace_key(old)+'_sig_tool').select('Ciencia').run()
            self.assertTrue(app.selectbox(key='science_profile_'+job.name).disabled)
            self.assertEqual(app.selectbox(key='science_profile_'+job.name).value, 'youtube')
            with patch('studio_preparation.verify_sources'), patch('data.load_values', side_effect=AssertionError('UI recalculated')):
                app.button(key='science_create').click().run()
            self.assertFalse(app.exception); self.assertFalse(app.error)
            current = app.session_state['project_document']
            self.assertEqual(current['project_meta']['id'], old['project_meta']['id'])
            self.assertEqual(current['studio']['timeline'][0], old['studio']['timeline'][0])
            self.assertTrue(current['studio']['calculations'])


class SigMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_studio_temporal import raster_project, SHAPE
        from studio_map_jobs import execute, read_resource
        from jobs import write_json
        cls.root = tempfile.TemporaryDirectory()
        cls.project = raster_project()
        job = Path(cls.root.name)/'map'; job.mkdir()
        write_json(job/'request.json', {'project':cls.project,'duration':7/30})
        with patch('data.boundary', return_value=SHAPE): execute(job, root=cls.root.name)
        cls.record = read_resource(job, root=cls.root.name)

    @classmethod
    def tearDownClass(cls): cls.root.cleanup()

    def test_map_send_reuses_scene_and_exports_same_calendar_without_raster_reads(self):
        from studio_sig import send_map
        from studio_timeline import PreparedTimeline, export_movie
        from studio_temporal import calendar_receipt
        from studio_recovery import recover_snapshot
        state = {}; publish_document(state, self.project)
        key = workspace_key(self.project)
        with tempfile.TemporaryDirectory() as root:
            session = WorkspaceSession(state,key,source_projection(self.project),store=root,canonical=True)
            science = copy.deepcopy(session.project['studio']['calculations'])
            with patch('data.load_values', side_effect=AssertionError('Presentation loaded raster')):
                send_map(session,self.record)
                selected = session.selected
                scene_count = len(session.project['studio']['scenes'])
                send_map(session,self.record)
                self.assertEqual(session.selected,selected)
                self.assertEqual(len(session.project['studio']['scenes']),scene_count)
                scene = next(s for s in session.project['studio']['scenes'] if s['id']==selected)
                from studio_workspace_commands import workspace_command
                edited = workspace_command(session.project,selected,{'action':'canvas','entries':{
                    scene['elements'][0]['id']:{'x':10,'y':10,'w':280,'h':160}}})
                session.commit(edited)
                recovered,_ = recover_snapshot(Path(state[key+'_draft']))
                self.assertEqual(recovered,session.project)
                receipt = export_movie(recovered,Path(root)/'sig-bridge.mp4')
                self.assertEqual(receipt['scientific_calendar'],calendar_receipt(recovered,PreparedTimeline(recovered).rows))
            self.assertEqual(session.project['studio']['calculations'],science)


if __name__ == '__main__': unittest.main()
