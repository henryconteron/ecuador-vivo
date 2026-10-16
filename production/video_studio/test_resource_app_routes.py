"""The actual app opens resource authoring independently and sends an explicit copy."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
APP=Path(__file__).with_name('app.py')

def component_stub(**values):
    import streamlit as st
    st.session_state['last_canvas_payload']=values['data']
    message=st.session_state.pop('test_resource_command',None)
    if message:
        st.session_state[values['key']]={'command':message}
        values['on_command_change']()

class ResourceAppRouteTests(unittest.TestCase):
    def setup_app(self,folder,video=None):
        from studio_project import source_projection
        app=AppTest.from_file(str(APP),default_timeout=40)
        if video:
            app.session_state['project_document']=video
            app.session_state['project']=source_projection(video)
            app.session_state['section']='Recursos'
        return app
    def command(self,app,action,**values):
        data=app.session_state['last_canvas_payload']
        app.session_state['test_resource_command']={'action':action,'scene':data['scene'],'version':data['version'],**values}
        app.run();app.run()
        self.assertFalse(app.exception,[item.value for item in app.exception])
    def test_home_opens_real_canvas_without_gallery_form_or_automatic_render(self):
        with tempfile.TemporaryDirectory() as folder,patch('model.STORE',Path(folder)),patch('studio_workspace.STORE',Path(folder)),patch('studio_workspace._COMPONENT',component_stub),patch('studio_blender.start_job') as render:
            app=self.setup_app(folder).run()
            app.button(key='home_resources').click().run()
            self.assertFalse(app.exception)
            self.assertTrue(app.session_state['last_canvas_payload']['resource_mode'])
            self.assertIsNone(app.session_state['project_document'])
            self.assertFalse(render.called)
            self.assertNotIn('resource_library_view',[e.key for e in app.segmented_control])
    def test_new_resource_is_independent_and_old_draft_is_recoverable(self):
        with tempfile.TemporaryDirectory() as folder,patch('model.STORE',Path(folder)),patch('studio_workspace.STORE',Path(folder)),patch('studio_workspace._COMPONENT',component_stub):
            app=self.setup_app(folder).run();app.button(key='home_resources').click().run()
            old=app.session_state['scientific_resources_document']['project_meta']['id']
            self.command(app,'resource_blank')
            self.assertNotEqual(old,app.session_state['scientific_resources_document']['project_meta']['id'])
            self.assertIsNone(app.session_state['project_document'])
            self.assertGreaterEqual(len(list((Path(folder)/'projects').glob('*.json'))),2)
    def test_send_adds_scene_to_video_and_opens_it_without_touching_original(self):
        from studio_home import create_project
        video=create_project('free',{'id':'tiktok'},name='Mi video');before=copy.deepcopy(video)
        with tempfile.TemporaryDirectory() as folder,patch('model.STORE',Path(folder)),patch('studio_workspace.STORE',Path(folder)),patch('studio_workspace._COMPONENT',component_stub):
            app=self.setup_app(folder,video).run()
            self.command(app,'resource_send')
            self.assertEqual(app.session_state['section'],'Editor')
            updated=app.session_state['project_document']
            self.assertEqual(len(updated['studio']['timeline']),2)
            self.assertEqual(updated['name'],'Mi video')
            self.assertNotIn('resource',updated['project_meta'])
            self.assertEqual(video,before)
if __name__=='__main__':unittest.main()
