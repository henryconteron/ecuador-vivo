"""Free/template project creation never downloads or calculates science."""
import tempfile
import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from output_profiles import profile_for


class StudioHomeTests(unittest.TestCase):
    def test_create_free_project_with_profile_and_editable_blank_scene(self):
        from studio_home import create_project
        from studio_timeline import PreparedTimeline
        with patch('data.load_values',side_effect=AssertionError('Free project requested data')):
            project=create_project('free',{'id':'youtube'})
            self.assertEqual(project['project_meta']['mode'],'free')
            studio=project['studio']
            self.assertEqual(len(studio['timeline']),1)
            scene=next(s for s in studio['scenes'] if s['id']==studio['timeline'][0])
            self.assertEqual(scene['elements'],[])
            self.assertFalse(studio['calculations'])
            self.assertEqual(PreparedTimeline(project).frame_at(0).size,(1920,1080))

    def test_template_project_is_editable_and_bound_template_requires_results(self):
        from studio_home import create_project
        project=create_project('template',{'id':'instagram_square'},template='cover')
        studio=project['studio']
        scene=next(s for s in studio['scenes'] if s['id']==studio['timeline'][0])
        self.assertTrue(scene['elements'])
        self.assertEqual(profile_for(studio['output_profile']).width,1080)
        with self.assertRaises(ValueError): create_project('template',{'id':'youtube'},template='metric_focus')

    def test_start_ui_creates_project_through_the_same_document(self):
        def script():
            import streamlit as st
            from studio_home import show_home
            def open_project(project): st.session_state['opened']=project
            show_home(open_project,store=st.session_state['test_store'])
        with tempfile.TemporaryDirectory() as directory:
            app=AppTest.from_function(script,default_timeout=15)
            app.session_state['test_store']=directory
            app.run();self.assertFalse(app.exception)
            app.button(key='home_free').click().run()
            app.selectbox(key='home_profile').select('youtube').run()
            app.button(key='home_create').click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state['opened']['project_meta']['mode'],'free')
            self.assertEqual(app.session_state['opened']['studio']['output_profile']['id'],'youtube')

    def test_recent_projects_include_saved_legacy_projects_and_exclude_backups(self):
        from pathlib import Path
        from studio_home import project_files
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in ('20241001-project.json','borrador-studio-one.json','borrador-studio-one.previous.json'):
                (root/name).write_text('{}',encoding='utf-8')
            self.assertEqual({p.name for p in project_files(root)}, {'20241001-project.json','borrador-studio-one.json'})

    def test_malformed_recent_project_does_not_crash_home(self):
        from pathlib import Path
        def script():
            import streamlit as st
            from studio_home import show_home
            show_home(lambda p:None,store=st.session_state['test_store'])
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)/'projects';folder.mkdir()
            (folder/'invalid.json').write_text('[]',encoding='utf-8')
            app=AppTest.from_function(script,default_timeout=15)
            app.session_state['test_store']=directory
            app.run();self.assertFalse(app.exception);self.assertTrue(app.warning)


if __name__=='__main__':unittest.main()
