"""Resource creation uses the normal editable project and explicit actions."""
from pathlib import Path
import tempfile
import unittest
from streamlit.testing.v1 import AppTest


SCRIPT='''
import streamlit as st
from studio_resources_ui import show_resources
def accept(project):st.session_state['accepted']=project
show_resources(st.session_state.get('accepted'),accept,key='designer',store=st.session_state['test_store'])
'''


class ResourceDesignerUiTests(unittest.TestCase):
    def test_small_custom_video_does_not_crash_template_gallery(self):
        from studio_home import create_project
        with tempfile.TemporaryDirectory() as folder:
            app=AppTest.from_string(SCRIPT,default_timeout=30)
            app.session_state['test_store']=folder
            app.session_state['accepted']=create_project('free',{'id':'custom','width':320,'height':320},name='Pequeño')
            app.run()
            self.assertFalse(app.exception)
            app.segmented_control(key='designer_view').set_value('blank').run()
            self.assertFalse(app.exception)

    def test_card_selection_can_leave_a_different_category(self):
        with tempfile.TemporaryDirectory() as folder:
            from studio_resources import RESOURCE_CATALOG
            app=AppTest.from_string(SCRIPT,default_timeout=30)
            app.session_state['test_store']=folder
            app.run()
            first=RESOURCE_CATALOG[0]
            other=next(item for item in RESOURCE_CATALOG if item['category']!=first['category'])
            app.selectbox(key='designer_category').set_value(first['category']).run()
            app.button(key='designer_card_'+other['id']).click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.selectbox(key='designer_choice').value,other['id'])

    def test_blank_creation_requires_confirmation_and_preserves_store(self):
        with tempfile.TemporaryDirectory() as folder:
            app=AppTest.from_string(SCRIPT,default_timeout=30)
            app.session_state['test_store']=folder
            app.run();self.assertFalse(app.exception)
            self.assertNotIn('accepted',app.session_state)
            app.segmented_control(key='designer_view').set_value('blank').run()
            app.text_input(key='designer_blank_name').set_value('Mi explicación')
            app.button(key='designer_blank_create').click().run()
            self.assertFalse(app.exception)
            doc=app.session_state['accepted']
            self.assertEqual(doc['project_meta']['resource']['name'],'Mi explicación')
            self.assertEqual(doc['studio']['scenes'][0]['elements'],[])
            self.assertEqual(list(Path(folder).rglob('*.json')),[])

    def test_template_edit_is_separate_from_the_open_video(self):
        from studio_home import create_project
        with tempfile.TemporaryDirectory() as folder:
            video=create_project('free',{'id':'tiktok'},name='Mi video')
            app=AppTest.from_string(SCRIPT,default_timeout=30)
            app.session_state['test_store']=folder
            app.session_state['accepted']=video
            app.run();app.button(key='designer_edit_template').click().run()
            self.assertFalse(app.exception)
            resource=app.session_state['accepted']
            self.assertNotEqual(video['project_meta']['id'],resource['project_meta']['id'])
            self.assertIn('resource',resource['project_meta'])
            self.assertEqual(video['name'],'Mi video')

    def test_library_reopens_resource_and_inserts_copy_into_video(self):
        from studio_resource_projects import create_resource_project
        from studio_home import create_project
        from studio_recovery import save_snapshot
        with tempfile.TemporaryDirectory() as folder:
            saved=create_resource_project('Mi lluvia',{'id':'tiktok'},resource_id='rain_volume')
            save_snapshot(Path(folder)/'projects'/'resource.json',saved)
            video=create_project('free',{'id':'youtube'},name='Video')
            app=AppTest.from_string(SCRIPT,default_timeout=30)
            app.session_state['test_store']=folder;app.session_state['accepted']=video
            app.run();app.segmented_control(key='designer_view').set_value('saved').run()
            self.assertFalse(app.exception)
            app.button(key='designer_saved_insert').click().run()
            self.assertFalse(app.exception)
            inserted=app.session_state['accepted']
            self.assertEqual(inserted['project_meta']['id'],video['project_meta']['id'])
            self.assertEqual(len(inserted['studio']['timeline']),2)
            self.assertEqual(saved['name'],'Mi lluvia')


if __name__=='__main__':unittest.main()
