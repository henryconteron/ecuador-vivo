"""Regression: a fragment's captured source must not overwrite a saved rename."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from test_studio_jobs import small_project

class CapturedFragmentSourceTests(unittest.TestCase):
    def test_saved_name_survives_fragment_rerun_and_keeps_history(self):
        import streamlit as st
        from streamlit.testing.v1 import AppTest
        import studio_workspace
        from studio_recovery import recover_snapshot
        payloads=[]
        def component(**values):
            payloads.append(values['data'])
            message=st.session_state.pop('test_command',None)
            if message:
                st.session_state[values['key']]={'command':message}
                values['on_command_change']()
        script='import sys\nsys.path.insert(0,{!r})\nfrom studio_workspace import show_workspace\nshow_workspace({!r},key="captured",canonical=True)'.format(str(Path(__file__).parent),small_project())
        with tempfile.TemporaryDirectory() as directory,patch.object(studio_workspace,'STORE',Path(directory)),patch.object(studio_workspace,'_COMPONENT',component):
            app=AppTest.from_string(script,default_timeout=30).run()
            self.assertFalse(app.exception)
            app.session_state['test_command']={'action':'rename','name':'Name accepted by the callback',
                'scene':payloads[-1]['scene'],'version':payloads[-1]['version']}
            app.run();self.assertFalse(app.exception)
            app.run();self.assertFalse(app.exception)
            self.assertEqual(app.session_state['project_document'].get('name'),'Name accepted by the callback')
            self.assertEqual(payloads[-1]['project']['name'],'Name accepted by the callback')
            self.assertEqual(app.session_state['captured_version'],1)
            self.assertEqual(len(app.session_state['captured_workspace_history']),1)
            disk,_=recover_snapshot(app.session_state['captured_draft'])
            self.assertEqual(disk['name'],app.session_state['project_document']['name'])

if __name__=='__main__':unittest.main()
