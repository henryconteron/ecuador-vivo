"""4b.4a publication: a whole authorized scene, durable transaction and no science."""
import copy,json
from pathlib import Path
import unittest
from unittest.mock import patch
import test_studio_map_temporal as fixtures

class MapPublicationTests(unittest.TestCase):
    setUp=fixtures.TemporalLayersTests.setUp
    tearDown=fixtures.TemporalLayersTests.tearDown

    def test_factory_profiles_complete_bindings_no_computation_and_reuse(self):
        from studio_temporal import attach_map_layers,calendar_at
        from studio_timeline import PreparedTimeline
        from output_profiles import PRESETS
        with patch('data.load_values',side_effect=AssertionError('Scientific read')), \
                patch('endcard.SummaryAccumulator',side_effect=AssertionError('Scientific calculation')):
            for pid in [*PRESETS,'custom']:
                p=copy.deepcopy(self.project)
                p['studio']['output_profile']={'id':pid} if pid!='custom' else {'id':'custom','width':320,'height':180}
                candidate=attach_map_layers(p,self.record)
                scene=candidate['studio']['scenes'][-1]
                self.assertEqual(len(scene['map_instances']),1)
                self.assertEqual({e['temporal_binding']['channel'] for e in scene['elements'] if e.get('temporal_binding')},
                    {'continent','galapagos','date','legend_static'})
                prepared=PreparedTimeline(candidate);start=prepared.rows[-1]['start_frame']
                for local,date in ((0,'2025-01-01'),(3,'2025-01-03'),(6,'2025-01-03')):
                    self.assertEqual({v['date'] for v in calendar_at(candidate,start+local)},{date})
                if pid=='custom':
                    with prepared.frame_at(start+3):pass
                self.assertEqual(candidate['studio']['datasets'],p['studio']['datasets'])
                self.assertEqual(candidate['studio']['calculations'],p['studio']['calculations'])
                self.assertEqual(candidate['studio']['scenes'][:-1],p['studio']['scenes'])
                second=attach_map_layers(candidate,self.record)
                self.assertEqual(len(second['studio']['media']),1)
                self.assertNotEqual(second['studio']['scenes'][-1]['map_instances'],scene['map_instances'])
        self.assertEqual(self.project,self.before)

    def test_rejects_unauthorized_stale_or_corrupt_without_partial_change(self):
        from studio_temporal import attach_map_layers,_hash
        bad=copy.deepcopy(self.record);bad['scientific_revision']='f'*64
        for record in (bad,self.record):
            p=copy.deepcopy(self.project)
            if record==self.record:p['studio']['calculations'].clear()
            before=copy.deepcopy(p)
            with self.assertRaises(ValueError):attach_map_layers(p,record)
            self.assertEqual(p,before)
        with self.assertRaisesRegex(ValueError,'proyecto cambió'):
            attach_map_layers(self.project,self.record,base_sha256='0'*64)
        candidate=attach_map_layers(self.project,self.record,base_sha256=_hash(self.project))
        self.assertEqual(self.project,self.before)
        manifest_path=Path(self.record['manifest_path'])
        from studio_map_bundles import read_bundle
        manifest=read_bundle(self.record)
        tile=manifest_path.parent/manifest['observations'][0]['layers']['continent']['path']
        tile.write_bytes(b'corrupt')
        before=copy.deepcopy(candidate)
        with self.assertRaises(ValueError):attach_map_layers(candidate,self.record)
        self.assertEqual(candidate,before)

    def test_legacy_missing_auxiliary_requires_explicit_preparation(self):
        from studio_temporal import attach_map_layers
        from studio_map_bundles import read_bundle,_bytes,_digest
        manifest=read_bundle(self.record);aux=manifest.pop('auxiliaries')
        content=_bytes(manifest);Path(self.record['manifest_path']).write_bytes(content)
        old=copy.deepcopy(self.record);old['manifest_sha256']=_digest(content)
        old['bytes']=len(content)+manifest['thumbnail']['bytes']+sum(i['bytes'] for o in manifest['observations'] for i in o['layers'].values())
        read_bundle(old)
        with self.assertRaisesRegex(ValueError,'Prepara explícitamente'):
            attach_map_layers(self.project,old)
        self.assertEqual(Path(old['manifest_path']).read_bytes(),content)
        self.assertEqual(self.project,self.before)

    def test_durable_commit_undo_redo_reopen_and_failed_save(self):
        from studio_temporal import attach_map_layers
        from studio_workspace import WorkspaceSession
        from studio_project import publish_document
        from studio_recovery import recover_snapshot
        state={};publish_document(state,self.project)
        session=WorkspaceSession(state,'publication',self.project,self.temp.name,canonical=True)
        before=copy.deepcopy(session.project);candidate=attach_map_layers(before,self.record)
        with patch('studio_workspace.save_snapshot',side_effect=OSError('Disk unavailable')):
            with self.assertRaises(OSError):session.commit(candidate)
        self.assertEqual(session.project,before)
        self.assertFalse(state['publication_workspace_history'])
        session.commit(candidate);accepted=copy.deepcopy(session.project)
        recovered,_=recover_snapshot(state['publication_draft']);self.assertEqual(recovered,accepted)
        for action in ('undo','redo'):
            session.dispatch({'action':action,'scene':session.selected,'version':session.version})
        self.assertEqual(session.project['studio'],accepted['studio'])
        self.assertEqual(session.project['project_meta']['scientific_revision'],accepted['project_meta']['scientific_revision'])
        self.assertGreater(session.project['project_meta']['revision'],accepted['project_meta']['revision'])
        self.assertEqual(session.project['studio']['datasets'],before['studio']['datasets'])

    def review_app(self):
        from streamlit.testing.v1 import AppTest
        def script():
            import streamlit as st
            from studio_workspace import WorkspaceSession
            from studio_map_ui import show_layer_review
            session=WorkspaceSession(st.session_state,'publication',st.session_state['source'],st.session_state['store'])
            show_layer_review(session,'publication',st.session_state['resource'])
        app=AppTest.from_function(script,default_timeout=20)
        app.session_state['source']=self.project;app.session_state['store']=self.temp.name
        app.session_state['resource']=self.record
        return app

    def test_review_ui_cancel_publish_and_coverage_warning(self):
        app=self.review_app().run();self.assertFalse(app.exception)
        before=copy.deepcopy(app.session_state['publication_document'])
        self.assertTrue(any('Galápagos: 1/2' in w.value for w in app.warning))
        self.assertTrue(any(self.record['units'] in v.value for v in app.markdown))
        app.button(key='publication_layers_close').click().run()
        self.assertEqual(app.session_state['publication_document'],before)
        with patch('data.load_values',side_effect=AssertionError('Presentation recalculated')):
            app.button(key='publication_layers_publish').click().run()
        self.assertFalse(app.exception,[e.value for e in app.exception])
        self.assertEqual(len(app.session_state['publication_document']['studio']['timeline']),len(before['studio']['timeline'])+1)
        self.assertEqual(app.session_state['publication_document']['studio']['calculations'],before['studio']['calculations'])

    def test_review_ui_error_preserves_document_and_history(self):
        app=self.review_app().run();self.assertFalse(app.exception)
        before=copy.deepcopy(app.session_state['publication_document'])
        app.session_state['publication_layer_review_base']['project']='0'*64
        app.button(key='publication_layers_publish').click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any('proyecto cambió' in e.value for e in app.error))
        self.assertEqual(app.session_state['publication_document'],before)
        self.assertFalse(app.session_state['publication_workspace_history'])

    def test_preparation_route_uses_bundle_worker_and_publishes_only_on_accept(self):
        from streamlit.testing.v1 import AppTest
        def script():
            import streamlit as st
            from studio_workspace import WorkspaceSession
            from studio_map_ui import show_map_dialog
            session=WorkspaceSession(st.session_state,'prepared',st.session_state['source'],st.session_state['store'])
            show_map_dialog(session,'prepared',representation='rgba_observation_bundle')
        app=AppTest.from_function(script,default_timeout=20)
        app.session_state['source']=self.project;app.session_state['store']=self.temp.name
        job=Path(self.temp.name)/'job'
        with patch('studio_map_ui.start_map_job',return_value=job) as start, \
                patch('studio_map_ui.map_status',return_value={'state':'complete'}), \
                patch('studio_map_ui.read_bundle_resource',return_value=self.record):
            app.run();before=copy.deepcopy(app.session_state['prepared_document'])
            app.button(key='prepared_map_start').click().run()
            self.assertEqual(start.call_args.kwargs,{'representation':'rgba_observation_bundle'})
            self.assertEqual(app.session_state['prepared_document'],before)
            app.button(key='prepared_layers_publish').click().run()
        self.assertFalse(app.exception,[e.value for e in app.exception])
        self.assertEqual(len(app.session_state['prepared_document']['studio']['media']),1)

    def test_workspace_library_review_callback_and_commit(self):
        from streamlit.testing.v1 import AppTest
        from studio_temporal import attach_map_layers
        import studio_workspace
        import streamlit as st
        def component(**values):
            message=st.session_state.pop('library_command',None)
            if message:
                st.session_state[values['key']]={'command':message}
                values['on_command_change']()
        def script():
            import streamlit as st
            from studio_workspace import show_workspace
            show_workspace(st.session_state['source'],key='library')
        app=AppTest.from_function(script,default_timeout=30)
        app.session_state['source']=attach_map_layers(self.project,self.record)
        with patch.object(studio_workspace,'STORE',Path(self.temp.name)),patch.object(studio_workspace,'_COMPONENT',component):
            app.run();self.assertFalse(app.exception)
            before=copy.deepcopy(app.session_state['library_document'])
            aid=next(iter(before['studio']['media']))
            app.session_state['library_command']={'action':'review_map_layers','asset_id':aid,
                'scene':app.session_state.get('library_selected',before['studio']['timeline'][0]),'version':app.session_state['library_version']}
            app.run();self.assertFalse(app.exception)
            self.assertEqual(app.session_state['library_document'],before)
            app.button(key='library_layers_publish').click().run()
            self.assertFalse(app.exception,[e.value for e in app.exception])
            accepted=app.session_state['library_document']
            self.assertEqual(len(accepted['studio']['media']),1)
            self.assertEqual(len(accepted['studio']['timeline']),len(before['studio']['timeline'])+1)
            self.assertEqual(app.session_state['library_selected'],accepted['studio']['timeline'][-1])

    def test_legacy_review_offers_explicit_new_preparation_without_overwriting(self):
        from studio_map_bundles import read_bundle,_bytes,_digest
        manifest=read_bundle(self.record);manifest.pop('auxiliaries')
        content=_bytes(manifest);Path(self.record['manifest_path']).write_bytes(content)
        old=copy.deepcopy(self.record);old['manifest_sha256']=_digest(content)
        old['bytes']=len(content)+manifest['thumbnail']['bytes']+sum(i['bytes'] for o in manifest['observations'] for i in o['layers'].values())
        app=self.review_app();app.session_state['resource']=old
        app.session_state['publication_layers_map_job']='retained-old-job'
        app.run();self.assertFalse(app.exception)
        before=copy.deepcopy(app.session_state['publication_document'])
        self.assertTrue(any('Prepara explícitamente' in e.value for e in app.error))
        self.assertFalse([b for b in app.button if b.key=='publication_layers_publish'])
        app.button(key='publication_layers_prepare_again').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['publication_dialog'],'temporal_layers')
        self.assertNotIn('publication_layers_map_job',app.session_state)
        self.assertEqual(app.session_state['publication_document'],before)
        self.assertEqual(Path(old['manifest_path']).read_bytes(),content)

if __name__=='__main__':unittest.main()
