"""Home lists every saved document and opens only on an explicit choice."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


def home_script():
    import streamlit as st
    from studio_home import show_home
    def opened(project):
        st.session_state['opened'] = project
    show_home(opened, store=st.session_state['test_store'])


class HomeCatalogTests(unittest.TestCase):
    def fixture(self, folder, count=8):
        from studio_home import create_project
        destination = Path(folder) / 'projects'
        destination.mkdir()
        for index in range(count):
            project = create_project('free', {'id': 'tiktok'}, name=f'Piloto {index + 1:02}')
            (destination / f'pilot-{index:03}.json').write_text(json.dumps(project), encoding='utf-8')
        return destination

    def test_catalog_never_silently_truncates_at_one_hundred_files(self):
        from studio_home import project_files
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for index in range(125):
                (root / f'project-{index:03}.json').write_text('{}', encoding='utf-8')
            (root / 'project-124.previous.json').write_text('{}', encoding='utf-8')
            self.assertEqual(len(project_files(root)), 125)

    def test_all_eight_pilots_visible_and_openable_without_thumbnail(self):
        with tempfile.TemporaryDirectory() as folder:
            self.fixture(folder)
            with patch('studio_home_visual.thumbnail', side_effect=OSError('Missing preview asset')):
                app = AppTest.from_function(home_script, default_timeout=20)
                app.session_state['test_store'] = folder
                app.run()
                self.assertFalse(app.exception)
                app.checkbox(key='home_project_thumbnails').check().run()
                self.assertFalse(app.exception)
                buttons = [button for button in app.button if button.key.startswith('home_project_open_')]
                self.assertEqual(len(buttons), 8)
                buttons[-1].click().run()
                self.assertFalse(app.exception)
                self.assertIn('Piloto', app.session_state['opened']['name'])

    def test_search_finds_older_project_beyond_first_page_by_its_real_name(self):
        with tempfile.TemporaryDirectory() as folder:
            self.fixture(folder, count=15)
            app = AppTest.from_function(home_script, default_timeout=20)
            app.session_state['test_store'] = folder
            app.run()
            self.assertFalse(app.exception)
            app.text_input(key='home_project_search').set_value('Piloto 01').run()
            self.assertFalse(app.exception)
            buttons = [button for button in app.button if button.key.startswith('home_project_open_')]
            self.assertEqual(len(buttons), 1)
            buttons[0].click().run()
            self.assertEqual(app.session_state['opened']['name'], 'Piloto 01')

    def test_every_project_is_reachable_through_pagination(self):
        with tempfile.TemporaryDirectory() as folder:
            self.fixture(folder, count=15)
            app = AppTest.from_function(home_script, default_timeout=20)
            app.session_state['test_store'] = folder
            app.run()
            self.assertFalse(app.exception)
            first_page = [button.key for button in app.button if button.key.startswith('home_project_open_')]
            self.assertEqual(len(first_page), 12)
            page = next(widget for widget in app.selectbox if widget.key.startswith('home_project_page_'))
            page.set_value(2).run()
            self.assertFalse(app.exception)
            second_page = [button.key for button in app.button if button.key.startswith('home_project_open_')]
            self.assertEqual(len(second_page), 3)
            self.assertFalse(set(first_page) & set(second_page))

    def test_scientific_creation_with_empty_home_does_not_offer_factory_project(self):
        with tempfile.TemporaryDirectory() as folder:
            app = AppTest.from_function(home_script, default_timeout=20)
            app.session_state['test_store'] = folder
            app.run()
            app.button(key='home_scientific').click().run()
            self.assertFalse(app.exception)
            self.assertNotIn('Proyecto actual', app.selectbox(key='science_route').options)

    def test_close_project_returns_to_empty_home_without_deleting_saved_copy(self):
        def script():
            import streamlit as st
            from studio_home import show_home
            show_home(lambda value: None, store=st.session_state['test_store'],
                      document=st.session_state.get('project_document'))
        with tempfile.TemporaryDirectory() as folder:
            saved = self.fixture(folder, count=1) / 'pilot-000.json'
            project = json.loads(saved.read_text(encoding='utf-8'))
            app = AppTest.from_function(script, default_timeout=20)
            app.session_state['test_store'] = folder
            app.session_state['project_document'] = project
            app.session_state['project'] = project
            app.run()
            app.button(key='home_close_project').click().run()
            self.assertFalse(app.exception)
            self.assertIsNone(app.session_state['project_document'])
            self.assertIsNone(app.session_state['project'])
            self.assertTrue(saved.is_file())

    def test_existing_explicit_project_survives_app_rerun(self):
        from studio_home import create_project
        from studio_project import source_projection
        project = create_project('free', {'id': 'tiktok'}, name='Mi proyecto elegido')
        with tempfile.TemporaryDirectory() as folder, patch('model.STORE', Path(folder)), patch('studio_home.STORE', Path(folder)):
            app = AppTest.from_file(str(Path(__file__).with_name('app.py')), default_timeout=30)
            app.session_state['project_document'] = project
            app.session_state['project'] = source_projection(project)
            app.run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state['project_document']['name'], 'Mi proyecto elegido')
            self.assertEqual(app.session_state['project_document']['studio'], project['studio'])

    def test_empty_home_sig_button_opens_working_draft_without_factory_example(self):
        # Updated requirement: enter SIG without a naming form. Loading an
        # example climate dataset still must not happen on ordinary entry.
        with tempfile.TemporaryDirectory() as folder, patch('studio_sig_references.initial_map',side_effect=lambda p:p):
            app = AppTest.from_function(home_script, default_timeout=20)
            app.session_state['test_store'] = folder
            app.run()
            app.button(key='home_sig').click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state['section'], 'SIG')
            self.assertNotIn('home_mode',app.session_state)
            self.assertEqual(app.session_state['project_document']['name'],'Mapa sin título')
            self.assertFalse(app.session_state['project_document']['studio']['datasets'])

    def test_app_entrypoint_does_not_initialize_a_rain_document(self):
        with tempfile.TemporaryDirectory() as folder, patch('model.STORE', Path(folder)), patch('studio_home.STORE', Path(folder)):
            app = AppTest.from_file(str(Path(__file__).with_name('app.py')), default_timeout=30).run()
            self.assertFalse(app.exception)
            self.assertIsNone(app.session_state['project'])
            self.assertIsNone(app.session_state['project_document'])
            self.assertEqual(app.session_state['section'], 'Inicio')


if __name__ == '__main__':
    unittest.main()
