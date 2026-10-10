"""Real Streamlit forms, analytical fixtures and canonical transactions."""
import copy,unittest
from types import SimpleNamespace
from unittest.mock import patch
import test_sig_map_ui as fixtures
from studio_project import workspace_key
from studio_sig_layers import workspace_for
from studio_sig_vector import layer_features


class VectorUiTests(unittest.TestCase):
    setUp=fixtures.SigMapUiTests.setUp
    tearDown=fixtures.SigMapUiTests.tearDown
    app=fixtures.SigMapUiTests.app
    patches=fixtures.SigMapUiTests.patches
    component=fixtures.SigMapUiTests.component
    assert_clean=fixtures.SigMapUiTests.assert_clean

    def test_csv_error_then_buffer_and_numeric_field_actual_forms(self):
        app=self.app();data=b'lon,lat,reading,absent\n-78.5,-0.1,0,\n-78.49,-0.11,-5,\n'
        upload=SimpleNamespace(name='analytic-points.csv',getvalue=lambda:data)
        with self.patches(),patch('studio_sig_vector_ui.st.file_uploader',return_value=upload):
            app.run();app.selectbox(key='sig_import_format').select('CSV de puntos').run()
            app.selectbox(key='sig_csv_x').select('lon');app.selectbox(key='sig_csv_y').select('lat')
            app.text_input(key='sig_general_citation').input('Analytic fixture, no environmental observation')
            app.text_input(key='sig_general_license').input('CC0 fixture')
            before=copy.deepcopy(app.session_state['project_document'])
            app.button(key='sig_general_submit').click().run()
            self.assertFalse(app.exception);self.assertTrue(app.error)
            self.assertEqual(app.session_state['project_document'],before)
            app.text_input(key='sig_general_crs').input('EPSG:4326')
            app.button(key='sig_general_submit').click().run();self.assert_clean(app)
            project=app.session_state['project_document'];lid=workspace_for(project)['active_layer'];key=workspace_key(project)
            self.assertEqual(layer_features(project,lid)[1][0]['properties']['reading'],'0')
            app.segmented_control[0].set_value(None).run();self.assert_clean(app)
            self.assertEqual(app.segmented_control[0].value,'Estilo');self.assertTrue(app.slider)
            app.button(key='sig_analyze').click().run();self.assert_clean(app)
            app.text_input(key='sig_analysis_crs').input('EPSG:32717')
            from shapely.errors import GEOSException
            before=copy.deepcopy(app.session_state['project_document'])
            with patch('studio_sig_vector_ui.run_operation',side_effect=GEOSException('Fixture topology failure')):
                app.button(key='sig_analysis_run').click().run()
                self.assertFalse(app.exception);self.assertTrue(app.error)
                self.assertEqual(app.session_state['project_document'],before)
            app.button(key='sig_analysis_run').click().run();self.assert_clean(app)
            project=app.session_state['project_document'];self.assertEqual(len(workspace_for(project)['layers']),2)
            self.assertEqual(layer_features(project,workspace_for(project)['active_layer'])[0]['operation']['tool'],'buffer')
            # Choose original layer and execute a finite numeric field calculation.
            app.button(key='sig_active_'+lid).click().run();app.button(key='sig_analyze').click().run()
            app.selectbox(key=key+'_vector_operation').select('Calcular campo').run()
            app.selectbox(key='sig_analysis_field').select('reading')
            app.selectbox(key='sig_calc_operator').select('multiply');app.number_input(key='sig_calc_constant').set_value(2.)
            app.button(key='sig_analysis_run').click().run();self.assert_clean(app)
            project=app.session_state['project_document'];new=workspace_for(project)['active_layer']
            self.assertEqual([f['properties']['resultado'] for f in layer_features(project,new)[1]],[0.,-10.])
            self.assertEqual(project['studio']['calculations'],self.project['studio']['calculations'])

    def test_standalone_sig_creation_does_not_require_video_configuration(self):
        from streamlit.testing.v1 import AppTest
        def script():
            import streamlit as st
            from studio_home import show_home
            def opened(project):
                from studio_project import request_studio_navigation
                st.session_state['test_created']=project
                request_studio_navigation(st.session_state)
            show_home(opened,store=st.session_state['test_store'])
        app=AppTest.from_function(script);app.session_state['test_store']=self.temp.name
        app.run();app.button(key='home_new_sig').click().run()
        self.assertFalse(any(s.key=='home_profile' for s in app.selectbox))
        app.text_input(key='home_sig_name').input('Standalone analytical SIG')
        app.button(key='home_create_sig').click().run();self.assert_clean(app)
        self.assertEqual(app.session_state['section'],'SIG')
        self.assertNotIn('_pending_studio_navigation',app.session_state)
        self.assertEqual(app.session_state['test_created']['name'],'Standalone analytical SIG')


if __name__=='__main__':unittest.main()
