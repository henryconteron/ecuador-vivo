from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

SCRIPT='''
import streamlit as st
from studio_blender_ui import show_blender_ui
show_blender_ui(None,lambda doc:st.session_state.update(accepted=doc),key='b3d',store=st.session_state['test_store'])
'''


class BlenderUiTests(unittest.TestCase):
    def test_open_and_parameter_changes_do_not_launch_a_render(self):
        with tempfile.TemporaryDirectory() as folder,patch('studio_blender_ui.blender_executable',return_value=Path('verified-blender.exe')),patch('studio_blender_ui.start_job',return_value='f'*64+'-poster') as launch,patch('studio_blender_ui.job_status',return_value={'state':'queued','progress':0,'message':'Preparando'}):
            app=AppTest.from_string(SCRIPT,default_timeout=30);app.session_state['test_store']=folder
            app.run();self.assertFalse(app.exception)
            self.assertFalse(launch.called)
            app.slider(key='b3d_yaw').set_value(45.)
            app.button(key='b3d_poster').click().run()
            self.assertFalse(app.exception)
            self.assertEqual(launch.call_args.args[0]['yaw'],45.)
            self.assertEqual(launch.call_args.kwargs['mode'],'poster')

    def test_missing_blender_has_an_actionable_message_not_a_crash(self):
        with tempfile.TemporaryDirectory() as folder,patch('studio_blender_ui.blender_executable',side_effect=ValueError('Blender no disponible')):
            app=AppTest.from_string(SCRIPT,default_timeout=30);app.session_state['test_store']=folder
            app.run();self.assertFalse(app.exception)
            self.assertTrue(app.warning)


if __name__=='__main__':unittest.main()
