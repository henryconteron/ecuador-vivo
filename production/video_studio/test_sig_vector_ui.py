"""Real Streamlit forms, analytical fixtures and canonical transactions."""
import copy,unittest
from types import SimpleNamespace
from pathlib import Path
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
    event=fixtures.SigMapUiTests.event

    def test_csv_error_then_buffer_and_numeric_field_actual_forms(self):
        app=self.app();data=b'lon,lat,reading,absent\n-78.5,-0.1,0,\n-78.49,-0.11,-5,\n'
        upload=SimpleNamespace(name='analytic-points.csv',getvalue=lambda:data)
        import studio_sig_analysis_jobs as jobs
        with (self.patches(),patch('studio_sig_vector_ui.st.file_uploader',return_value=upload),
              patch.object(jobs,'ROOT',Path(self.temp.name)/'analysis'),
              patch.object(jobs.subprocess,'Popen',return_value=SimpleNamespace(pid=12345))):
            app.run();self.event(app,'import')
            app.selectbox(key='sig_import_format').select('CSV de puntos').run()
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
            self.event(app,'tool',tool='Análisis vectorial');self.assert_clean(app)
            app.text_input(key='sig_analysis_crs').input('EPSG:32717')
            from shapely.errors import GEOSException
            before=copy.deepcopy(app.session_state['project_document'])
            with patch('studio_sig_vector.run_operation',side_effect=GEOSException('Fixture topology failure')):
                app.button(key='sig_analysis_run').click().run()
                jobs.execute(app.session_state[key+'_sig_analysis_job'])
                app.run();self.assertFalse(app.exception)
                self.assertTrue(any('Fixture topology failure' in text.value for text in app.markdown))
                self.assertEqual(app.session_state['project_document'],before)
            app.button(key='sig_analysis_dismiss').click().run()
            self.event(app,'tool',tool='Análisis vectorial')
            app.text_input(key='sig_analysis_crs').input('EPSG:32717')
            app.button(key='sig_analysis_run').click().run();self.assert_clean(app)
            jobs.execute(app.session_state[key+'_sig_analysis_job'])
            app.run();app.button(key='sig_analysis_accept').click().run();self.assert_clean(app)
            project=app.session_state['project_document'];self.assertEqual(len(workspace_for(project)['layers']),2)
            self.assertEqual(layer_features(project,workspace_for(project)['active_layer'])[0]['operation']['tool'],'buffer')
            # Choose original layer and execute a finite numeric field calculation.
            self.event(app,'layer',command={'action':'active','layer_id':lid})
            self.event(app,'tool',tool='Análisis vectorial')
            app.selectbox(key=key+'_vector_operation').select('Calcular campo').run()
            app.selectbox(key='sig_analysis_field').select('reading')
            app.selectbox(key='sig_calc_operator').select('multiply');app.number_input(key='sig_calc_constant').set_value(2.)
            app.button(key='sig_analysis_run').click().run();self.assert_clean(app)
            jobs.execute(app.session_state[key+'_sig_analysis_job'])
            app.run();app.button(key='sig_analysis_accept').click().run();self.assert_clean(app)
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
        app.run();app.session_state['home_mode']='gis';app.run()
        self.assertFalse(any(s.key=='home_profile' for s in app.selectbox))
        app.text_input(key='home_sig_name').input('Standalone analytical SIG')
        app.button(key='home_create_sig').click().run();self.assert_clean(app)
        self.assertEqual(app.session_state['section'],'SIG')
        self.assertNotIn('_pending_studio_navigation',app.session_state)
        self.assertEqual(app.session_state['test_created']['name'],'Standalone analytical SIG')


if __name__=='__main__':unittest.main()
