"""Home chrome is independent of project rendering and draft entry is explicit."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest


def home_script():
    import streamlit as st
    from studio_home import show_home
    show_home(lambda p: st.session_state.update(opened=p), store=st.session_state['test_store'],
              document=st.session_state.get('project_document'))


class HomeEntryDesignTests(unittest.TestCase):
    def test_three_workspace_entries_never_render_saved_projects_for_cover(self):
        from studio_home import create_project
        from studio_recovery import save_snapshot
        with tempfile.TemporaryDirectory() as folder:
            save_snapshot(Path(folder)/'projects'/'saved.json', create_project('free', {'id':'tiktok'}))
            with patch('studio_home_visual.thumbnail', side_effect=AssertionError('Cover must not decode project')) as render:
                app=AppTest.from_function(home_script,default_timeout=20)
                app.session_state['test_store']=folder
                app.run()
                self.assertFalse(app.exception)
                self.assertEqual(render.call_count,0)
                self.assertEqual(app.button(key='home_resources').label,'Abrir Recursos')
                self.assertEqual(app.button(key='home_open_saved').label,'Abrir proyecto')
                self.assertEqual(app.button(key='home_free').label,'Crear proyecto')

    def test_sig_opens_empty_draft_without_name_form_or_disk_write(self):
        with tempfile.TemporaryDirectory() as folder, patch('studio_sig_references.initial_map',side_effect=lambda p:p):
            app=AppTest.from_function(home_script,default_timeout=20)
            app.session_state['test_store']=folder
            app.run();app.button(key='home_sig').click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state['section'],'SIG')
            self.assertIsNotNone(app.session_state['project_document'])
            self.assertNotIn('home_mode',app.session_state)
            self.assertEqual(list(Path(folder).rglob('*.json')),[])

    def test_create_form_is_before_workspace_cards_and_close_is_non_destructive(self):
        with tempfile.TemporaryDirectory() as folder:
            app=AppTest.from_function(home_script,default_timeout=20)
            app.session_state['test_store']=folder
            app.run();app.button(key='home_free').click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.text_input(key='home_name').label,'Nombre del proyecto')
            app.button(key='home_cancel_create').click().run()
            self.assertFalse(app.exception)
            self.assertNotIn('home_mode',app.session_state)
            self.assertEqual(list(Path(folder).rglob('*.json')),[])


if __name__=='__main__':unittest.main()
