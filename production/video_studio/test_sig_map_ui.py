"""SIG-U1 real Streamlit controls over canonical transactions (map callback seam)."""
import copy,json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest
import test_studio_geography as fixtures

class SigMapUiTests(unittest.TestCase):
    setUp=fixtures.GeographyTests.setUp
    tearDown=fixtures.GeographyTests.tearDown
    def app(self,document=None):
        from streamlit.testing.v1 import AppTest
        from studio_project import publish_document
        def script():
            import streamlit as st
            from studio_project import workspace_key,source_projection
            from studio_workspace import WorkspaceSession
            from studio_sig_map_ui import show_sig_map
            document=st.session_state['project_document']
            session=WorkspaceSession(st.session_state,workspace_key(document),source_projection(document),canonical=True)
            show_sig_map(session)
        app=AppTest.from_function(script,default_timeout=20)
        publish_document(app.session_state,document or self.project)
        return app
    def component(self,**kwargs):
        import streamlit as st
        self.payload=kwargs['data'];self.callback=kwargs['on_command_change'];self.component_key=kwargs['key']
        message=st.session_state.pop('test_map_command',None)
        if message:
            st.session_state[self.component_key]={'command':message};self.callback();st.rerun()
    def patches(self):
        from contextlib import ExitStack
        stack=ExitStack()
        stack.enter_context(patch('studio_workspace.STORE',Path(self.temp.name)))
        stack.enter_context(patch('studio_sig_map_ui._COMPONENT',self.component))
        return stack
    def assert_clean(self,app):self.assertFalse(app.exception);self.assertFalse(app.error)
    def test_import_identify_attributes_visibility_style_and_explicit_save(self):
        from studio_project import workspace_key
        from studio_recovery import recover_snapshot
        app=self.app();fake=SimpleNamespace(name='regions.geojson',getvalue=lambda:self.content)
        with self.patches(),patch('studio_sig_map_ui.st.file_uploader',return_value=fake):
            app.run();self.assert_clean(app)
            app.text_input(key='sig_u1_citation').input(self.provenance['citation'])
            app.text_input(key='sig_u1_license').input(self.provenance['license'])
            app.button(key='sig_u1_import_submit').click().run();self.assert_clean(app)
            document=app.session_state['project_document'];state=document['studio']['geography']['map_workspace'];lid=state['active_layer']
            rid=next(iter(document['studio']['geography']['regions']))
            self.assertEqual(len(self.payload['layers'][0]['features']),3)
            app.session_state['test_map_command']={'action':'select','layer_id':lid,'region_id':rid,'version':self.payload['version']}
            app.run();self.assert_clean(app)
            self.assertEqual(self.payload['selection'],[rid])
            attributes=json.loads(app.json[-1].value)
            self.assertEqual(attributes,{'name':'Brasil sintético','population':0,'signed':-5})
            app.slider[0].set_value(.3)
            next(b for b in app.button if b.label=='Aplicar estilo').click().run();self.assert_clean(app)
            self.assertEqual(self.payload['layers'][0]['style']['opacity'],.3)
            app.checkbox[0].uncheck().run();self.assert_clean(app)
            self.assertFalse(self.payload['layers'][0]['visible']);self.assertEqual(self.payload['selection'],[])
            app.checkbox[0].check().run()
            before_history=len(app.session_state[workspace_key(document)+'_workspace_history'])
            app.button(key='sig_save_project').click().run();self.assert_clean(app)
            self.assertEqual(len(app.session_state[workspace_key(document)+'_workspace_history']),before_history)
            recovered,_=recover_snapshot(app.session_state[workspace_key(document)+'_draft'])
            self.assertEqual(recovered,app.session_state['project_document'])
            for k in ('calculations','datasets','scenes'):self.assertEqual(recovered['studio'][k],self.project['studio'][k])
    def test_native_layer_order_remove_and_foreign_geography(self):
        from studio_sig_layers import add_geojson_layer
        first,lid=add_geojson_layer(self.project,self.content,'regions.geojson',self.provenance)
        raw=json.dumps({'type':'Feature','properties':{'name':'France fixture'},'geometry':{'type':'Polygon','coordinates':fixtures.polygon(2,46,1)}}).encode()
        document,second=add_geojson_layer(first,raw,'france.geojson',self.provenance)
        app=self.app(document)
        with self.patches():
            app.run();self.assert_clean(app)
            self.assertEqual([l['id'] for l in self.payload['layers']],[lid,second])
            app.button(key='sig_down').click().run();self.assert_clean(app)
            self.assertEqual([l['id'] for l in self.payload['layers']],[second,lid])
            app.button(key='sig_remove').click().run();self.assert_clean(app)
            self.assertEqual([l['id'] for l in self.payload['layers']],[lid])
            self.assertEqual(app.session_state['project_document']['studio']['geography']['sources'],document['studio']['geography']['sources'])
    def test_stale_invalid_and_noop_map_commands_acknowledged_without_partial_changes(self):
        from studio_sig_layers import add_geojson_layer
        from studio_project import workspace_key
        project,lid=add_geojson_layer(self.project,self.content,'regions.geojson',self.provenance);app=self.app(project)
        with self.patches():
            app.run();before=copy.deepcopy(app.session_state['project_document']);key=workspace_key(project)
            for message in ({'action':'select','layer_id':lid,'region_id':'invented','version':self.payload['version']},
                            {'action':'view','bbox':[0,0,1,1],'version':-1}):
                app.session_state['test_map_command']=message;app.run()
                self.assertFalse(app.exception);self.assertTrue(self.payload['error'])
                self.assertEqual(app.session_state['project_document'],before)
                self.assertEqual(app.session_state[key+'_workspace_history'],[])
            self.assertEqual(self.payload['ack'],2)
            app.session_state['test_map_command']={'action':'clear_selection','version':self.payload['version']};app.run()
            self.assert_clean(app);self.assertEqual(self.payload['ack'],3);self.assertEqual(self.payload['error'],'')
    def test_invalid_upload_never_publishes_empty_layer(self):
        app=self.app();fake=SimpleNamespace(name='bad.geojson',getvalue=lambda:b'{"type":"Point","coordinates":[0,0]}')
        with self.patches(),patch('studio_sig_map_ui.st.file_uploader',return_value=fake):
            app.run();before=copy.deepcopy(app.session_state['project_document'])
            app.text_input(key='sig_u1_citation').input('Synthetic')
            app.text_input(key='sig_u1_license').input('CC0')
            app.button(key='sig_u1_import_submit').click().run()
            self.assertFalse(app.exception);self.assertTrue(app.error)
            self.assertEqual(app.session_state['project_document'],before)

if __name__=='__main__':unittest.main()
