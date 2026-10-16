"""SIG shell callbacks preserve the same canonical transaction acceptance criteria."""
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
        self.payload=kwargs['data'];self.component_key=kwargs['key']
        for test_key,channel,callback in [('test_map_command','command','on_command_change'),('test_ui_event','ui_event','on_ui_event_change')]:
            message=st.session_state.pop(test_key,None)
            if message:
                st.session_state[self.component_key]={channel:message};kwargs[callback]();st.rerun()
    def patches(self):
        from contextlib import ExitStack
        stack=ExitStack()
        stack.enter_context(patch('studio_workspace.STORE',Path(self.temp.name)))
        stack.enter_context(patch('studio_sig_map_ui._OL_COMPONENT',self.component))
        return stack
    def assert_clean(self,app):self.assertFalse(app.exception);self.assertFalse(app.error)
    def event(self,app,action,**values):
        app.session_state['test_ui_event']={'action':action,'version':self.payload['version'],**values}
        app.run();self.assert_clean(app)
    def layer(self,app,action,**values):self.event(app,'layer',command={'action':action,**values})
    def test_catalog_direct_operation_executes_derived_layer_and_exports(self):
        import studio_sig_analysis_jobs as jobs
        from studio_project import workspace_key
        from studio_sig_layers import add_geojson_layer
        from studio_sig_vector import layer_features
        document,lid=add_geojson_layer(self.project,self.content,'regions.geojson',self.provenance)
        app=self.app(document)
        with self.patches(),patch.object(jobs,'ROOT',Path(self.temp.name)/'analysis'),patch.object(jobs.subprocess,'Popen',return_value=SimpleNamespace(pid=12345)):
            app.run();self.event(app,'operation',operation='boundary')
            self.assertEqual(app.selectbox(key=workspace_key(document)+'_vector_operation').value,'Extraer contornos')
            app.button(key='sig_analysis_run').click().run();self.assert_clean(app)
            self.assertEqual(app.session_state['project_document'],document)
            jobs.execute(app.session_state[workspace_key(document)+'_sig_analysis_job'])
            app.run();app.button(key='sig_analysis_accept').click().run();self.assert_clean(app)
            updated=app.session_state['project_document'];new=updated['studio']['geography']['map_workspace']['active_layer']
            self.assertNotEqual(new,lid)
            self.assertEqual(layer_features(updated,new)[0]['operation']['tool'],'boundary')
            self.assertEqual(layer_features(updated,new)[1][0]['geometry']['type'],'MultiLineString')
            self.event(app,'tool',tool='Exportar capa')
            self.assertTrue(any(item.proto.label=='Exportar capa GeoJSON' for item in app.get('download_button')))
            self.assertEqual(updated['studio']['scenes'],document['studio']['scenes'])
    def test_import_identify_attributes_visibility_style_and_explicit_save(self):
        from studio_project import workspace_key
        from studio_recovery import recover_snapshot
        app=self.app();fake=SimpleNamespace(name='regions.geojson',getvalue=lambda:self.content)
        with self.patches(),patch('studio_sig_map_ui.st.file_uploader',return_value=fake):
            app.run();self.event(app,'import')
            app.text_input(key='sig_u1_citation').input(self.provenance['citation'])
            app.text_input(key='sig_u1_license').input(self.provenance['license'])
            app.button(key='sig_u1_import_submit').click().run();self.assert_clean(app)
            document=app.session_state['project_document'];state=document['studio']['geography']['map_workspace'];lid=state['active_layer']
            rid=next(iter(document['studio']['geography']['regions']))
            self.assertEqual(len(self.payload['layers'][0]['features']),3)
            self.layer(app,'select',layer_id=lid,region_id=rid)
            self.assertEqual(self.payload['selection'],[rid])
            attributes=self.payload['workspace']['attributes'];row=attributes['rows'][attributes['ids'].index(rid)]
            self.assertEqual(row,{'name':'Brasil sintético','population':0,'signed':-5})
            style={**self.payload['layers'][0]['style'],'opacity':.3}
            self.layer(app,'style',layer_id=lid,style=style);self.assertEqual(self.payload['layers'][0]['style']['opacity'],.3)
            self.layer(app,'visibility',layer_id=lid,visible=False)
            self.assertFalse(self.payload['layers'][0]['visible']);self.assertEqual(self.payload['selection'],[])
            self.layer(app,'visibility',layer_id=lid,visible=True)
            before_history=len(app.session_state[workspace_key(document)+'_workspace_history'])
            self.event(app,'save')
            self.assertEqual(len(app.session_state[workspace_key(document)+'_workspace_history']),before_history)
            recovered,_=recover_snapshot(app.session_state[workspace_key(document)+'_draft'])
            self.assertEqual(recovered,app.session_state['project_document'])
            for k in ('calculations','datasets','scenes'):self.assertEqual(recovered['studio'][k],self.project['studio'][k])
    def test_native_layer_order_remove_and_foreign_geography(self):
        from studio_sig_layers import add_geojson_layer
        first,lid=add_geojson_layer(self.project,self.content,'regions.geojson',self.provenance)
        raw=json.dumps({'type':'Feature','properties':{'name':'France fixture'},'geometry':{'type':'Polygon','coordinates':fixtures.polygon(2,46,1)}}).encode()
        document,second=add_geojson_layer(first,raw,'france.geojson',self.provenance);app=self.app(document)
        with self.patches():
            app.run();self.assert_clean(app)
            self.assertEqual([l['id'] for l in self.payload['layers']],[lid,second])
            self.layer(app,'order',layer_id=second,offset=-1)
            self.assertEqual([l['id'] for l in self.payload['layers']],[second,lid])
            self.layer(app,'remove',layer_id=second)
            self.assertEqual([l['id'] for l in self.payload['layers']],[lid])
            self.assertEqual(app.session_state['project_document']['studio']['geography']['sources'],document['studio']['geography']['sources'])
    def test_stale_invalid_and_noop_map_commands_acknowledged_without_partial_changes(self):
        from studio_sig_layers import add_geojson_layer
        from studio_project import workspace_key
        project,lid=add_geojson_layer(self.project,self.content,'regions.geojson',self.provenance);app=self.app(project)
        with self.patches():
            app.run();before=copy.deepcopy(app.session_state['project_document']);key=workspace_key(project)
            for message in ({'action':'select','layer_id':lid,'region_id':'invented','version':self.payload['version']},{'action':'view','bbox':[0,0,1,1],'version':-1}):
                app.session_state['test_map_command']=message;app.run()
                self.assertFalse(app.exception);self.assertTrue(self.payload['error'])
                self.assertEqual(app.session_state['project_document'],before);self.assertEqual(app.session_state[key+'_workspace_history'],[])
            self.assertEqual(self.payload['ack'],2)
            app.session_state['test_map_command']={'action':'clear_selection','version':self.payload['version']};app.run()
            self.assert_clean(app);self.assertEqual(self.payload['ack'],3);self.assertEqual(self.payload['error'],'')
            app.session_state['test_ui_event']={'action':'operation','operation':'centroid','version':-1};app.run()
            self.assertFalse(app.exception);self.assertTrue(self.payload['error'])
            self.assertEqual(app.session_state['project_document'],before)
    def test_invalid_upload_never_publishes_empty_layer(self):
        app=self.app();fake=SimpleNamespace(name='bad.geojson',getvalue=lambda:b'{"type":"Point","coordinates":[0,0]}')
        with self.patches(),patch('studio_sig_map_ui.st.file_uploader',return_value=fake):
            app.run();self.event(app,'import');before=copy.deepcopy(app.session_state['project_document'])
            app.text_input(key='sig_u1_citation').input('Synthetic');app.text_input(key='sig_u1_license').input('CC0')
            app.button(key='sig_u1_import_submit').click().run()
            self.assertFalse(app.exception);self.assertTrue(app.error);self.assertEqual(app.session_state['project_document'],before)
    def test_openlayers_sequence_confirmation_and_native_undo_redo(self):
        from studio_sig_layers import add_geojson_layer
        project,lid=add_geojson_layer(self.project,self.content,'regions.geojson',self.provenance);app=self.app(project)
        with self.patches():
            app.run();self.assert_clean(app);rid=next(iter(project['studio']['geography']['regions']))
            message={'client':'b'*32,'version':self.payload['version'],'sequence':1,'commands':[{'sequence':1,'action':'select','layer_id':lid,'region_id':rid}]}
            app.session_state['test_map_command']=message;app.run();self.assert_clean(app)
            self.assertEqual(self.payload['confirmation']['status'],'saved');self.assertEqual(self.payload['selection'],[rid])
            self.event(app,'undo');self.assertEqual(self.payload['selection'],[])
            self.event(app,'redo');self.assertEqual(self.payload['selection'],[rid])

    def test_ui_action_flushes_camera_before_save_and_rejects_external_replay(self):
        from studio_sig_layers import add_geojson_layer
        project,_=add_geojson_layer(self.project,self.content,'regions.geojson',self.provenance);app=self.app(project)
        with self.patches():
            app.run();base=self.payload['version'];box=[-54,-16,-46,-8]
            envelope={'client':'c'*32,'version':base,'sequence':1,'commands':[{'sequence':1,'action':'view','bbox':box}]}
            self.event(app,'save',map_intents=envelope)
            self.assertEqual(self.payload['view']['bbox'],box)
            self.assertEqual(self.payload['confirmation']['status'],'saved')
            before=copy.deepcopy(app.session_state['project_document'])
            app.session_state['test_ui_event']={'action':'save','version':base,'map_intents':envelope};app.run()
            self.assertFalse(app.exception);self.assertTrue(self.payload['error'])
            self.assertEqual(self.payload['confirmation']['status'],'rejected')
            self.assertEqual(app.session_state['project_document'],before)

if __name__=='__main__':unittest.main()
