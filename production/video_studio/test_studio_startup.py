"""Inicio must not load map/video engines or invalidate other sessions' caches."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import builtins
import os

from streamlit.testing.v1 import AppTest

APP = Path(__file__).with_name('app.py')


def home_stub(*args, **kwargs):
    import streamlit as st
    st.title('Ecuador Vivo')


class StartupTests(unittest.TestCase):
    def test_inicio_does_not_import_legacy_render_data_or_download_engines(self):
        original_import = builtins.__import__

        def guarded_import(name, *args, **kwargs):
            if name in {'data', 'render', 'endcard', 'providers', 'jobs', 'social'}:
                raise AssertionError('Inicio loaded an unrelated engine: ' + name)
            return original_import(name, *args, **kwargs)

        with tempfile.TemporaryDirectory() as folder, patch('model.STORE', Path(folder)), \
                patch('studio_home.show_home', home_stub), \
                patch.dict(os.environ, {'ECUADOR_VIVO_DEVELOPMENT_RELOAD': '0'}), \
                patch('builtins.__import__', guarded_import):
            app = AppTest.from_file(str(APP), default_timeout=30).run()
            self.assertFalse(app.exception, [e.value for e in app.exception])
            self.assertIsNone(app.session_state['project'])
            self.assertIsNone(app.session_state['project_document'])
            self.assertEqual(app.session_state['section'], 'Inicio')

    def test_new_session_does_not_clear_process_wide_cached_data(self):
        with tempfile.TemporaryDirectory() as folder, patch('model.STORE', Path(folder)), \
                patch('studio_home.show_home', home_stub), \
                patch('streamlit.cache_data.clear', side_effect=AssertionError('Global cache eviction')):
            app = AppTest.from_file(str(APP), default_timeout=30).run()
            self.assertFalse(app.exception, [e.value for e in app.exception])
            app.run()
            self.assertFalse(app.exception)

    def test_deferred_download_route_retains_all_existing_sources(self):
        with tempfile.TemporaryDirectory() as folder, patch('model.STORE', Path(folder)):
            app = AppTest.from_file(str(APP), default_timeout=30)
            app.session_state['section'] = 'Obtener datos'
            app.run()
            self.assertFalse(app.exception, [e.value for e in app.exception])
            self.assertEqual(app.selectbox(key='provider_source').options,
                             ['CHIRPS v3 · lluvia', 'NASA POWER · clima', 'INAMHI · estaciones'])
            self.assertIsNone(app.session_state['project'])
            app.selectbox(key='provider_source').select('NASA POWER · clima').run()
            self.assertFalse(app.exception, [e.value for e in app.exception])
            self.assertTrue(app.selectbox(key='provider_power_parameter').options)


if __name__ == '__main__':
    unittest.main()
