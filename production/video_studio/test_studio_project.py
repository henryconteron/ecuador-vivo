"""Single document ownership across legacy/source view and Studio editing."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from test_studio_jobs import small_project


class ProjectDocumentTests(unittest.TestCase):
    def test_source_changes_preserve_scenes_bindings_and_unknown_fields(self):
        from studio_project import synchronize_source, source_projection, workspace_key
        state = {'project': small_project()}
        first = synchronize_source(state, state['project'])
        key = workspace_key(first)
        before = copy.deepcopy(first['studio'])
        source = source_projection(first)
        self.assertNotIn('studio', source)
        source['title'] = 'A new editorial title'
        source['unknown']['nested'] = ['retain']
        second = synchronize_source(state, source)
        self.assertEqual(second['studio'], before)
        self.assertEqual(workspace_key(second), key)
        self.assertEqual(second['project_meta']['revision'], first['project_meta']['revision'] + 1)
        self.assertEqual(second['unknown']['nested'], ['retain'])
        self.assertEqual(synchronize_source(state, source), second)

    def test_workspace_edits_and_undo_publish_the_same_document(self):
        from studio_project import synchronize_source, workspace_key
        from studio_workspace import WorkspaceSession
        state = {'project': small_project()}
        document = synchronize_source(state, state['project'])
        with tempfile.TemporaryDirectory() as directory:
            session = WorkspaceSession(state, workspace_key(document), state['project'], store=directory, canonical=True)
            candidate = copy.deepcopy(session.project)
            candidate['name'] = 'Edited in Studio'
            session.commit(candidate)
            self.assertIs(state['project_document'], session.project)
            self.assertEqual(state['project']['name'], 'Edited in Studio')
            self.assertNotIn('studio', state['project'])
            session.dispatch({'action':'undo','version':session.version,'scene':session.selected})
            self.assertEqual(state['project_document'].get('name'), document.get('name'))
            self.assertEqual(state['project_document']['studio']['calculations'], document['studio']['calculations'])

    def test_failed_save_does_not_publish_canonical_document_or_history(self):
        from studio_project import synchronize_source, workspace_key
        from studio_workspace import WorkspaceSession
        state = {'project': small_project()}
        document = synchronize_source(state, state['project'])
        with tempfile.TemporaryDirectory() as directory:
            key = workspace_key(document)
            session = WorkspaceSession(state, key, state['project'], store=directory, canonical=True)
            before = copy.deepcopy(state['project_document'])
            candidate = copy.deepcopy(before);candidate['name'] = 'Not saved'
            with patch('studio_workspace.save_snapshot', side_effect=OSError('disk unavailable')):
                with self.assertRaises(OSError): session.commit(candidate)
            self.assertEqual(state['project_document'], before)
            self.assertFalse(state[key+'_workspace_history'])

    def test_explicit_open_creates_identity_without_touching_input(self):
        from studio_project import replace_document, synchronize_source
        state = {'project': small_project()}
        first = synchronize_source(state, state['project'])
        saved = copy.deepcopy(first)
        opened = replace_document(state, saved)
        self.assertNotEqual(opened['project_meta']['id'], first['project_meta']['id'])
        self.assertEqual(opened['studio'], saved['studio'])
        self.assertEqual(saved, first)

    def test_source_widget_revision_does_not_reset_workspace_history(self):
        from studio_project import synchronize_source, workspace_key
        from studio_workspace import WorkspaceSession
        state = {'project':small_project(), 'revision':0}
        document = synchronize_source(state,state['project'])
        with tempfile.TemporaryDirectory() as directory:
            key = workspace_key(document)
            first = WorkspaceSession(state,key,state['project'],store=directory,canonical=True)
            candidate = copy.deepcopy(first.project);candidate['name']='Persisted'
            first.commit(candidate)
            state['revision'] += 1
            second = WorkspaceSession(state,key,state['project'],store=directory,canonical=True)
            self.assertEqual(second.project['name'],'Persisted')
            self.assertEqual(len(state[key+'_workspace_history']),1)
            self.assertEqual(second.version, first.version)

    def test_import_and_undo_restore_revision_metadata_without_reusing_old_clock(self):
        from studio_project import synchronize_source,workspace_key
        from studio_workspace import WorkspaceSession
        state={'project':small_project()}
        initial=synchronize_source(state,state['project'])
        with tempfile.TemporaryDirectory() as directory:
            session=WorkspaceSession(state,workspace_key(initial),state['project'],store=directory,canonical=True)
            candidate=copy.deepcopy(session.project)
            candidate['project_meta'].update(mode='free',scientific_revision='c'*64)
            session.commit(candidate,new_draft=True)
            self.assertEqual(session.project['project_meta']['mode'],'free')
            self.assertEqual(session.project['project_meta']['scientific_revision'],'c'*64)
            first_revision=session.project['project_meta']['revision']
            session.dispatch({'action':'undo','version':session.version,'scene':session.selected})
            self.assertEqual(session.project['project_meta']['mode'],initial['project_meta']['mode'])
            self.assertGreater(session.project['project_meta']['revision'],first_revision)

    def test_future_and_malformed_document_metadata_are_rejected(self):
        from studio_project import synchronize_source
        for patch_value in ({'document_version':2},{'document_version':True},{'mode':'unsupported'}):
            project=small_project();project['project_meta']=patch_value
            with self.subTest(metadata=patch_value),self.assertRaises(ValueError):
                synchronize_source({},project)

    def test_studio_navigation_after_native_widget_is_queued_until_next_rerun(self):
        from streamlit.testing.v1 import AppTest
        def script():
            import streamlit as st
            from studio_project import request_studio_navigation,consume_studio_navigation
            consume_studio_navigation(st.session_state)
            st.segmented_control('Phase',['Maqueta','Estudio'],default='Maqueta',key='studio_phase')
            if st.button('Create from results',key='request'):
                request_studio_navigation(st.session_state)
                st.rerun()
        app=AppTest.from_function(script,default_timeout=15).run()
        app.button(key='request').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['studio_phase'],'Estudio')


if __name__ == '__main__': unittest.main()
