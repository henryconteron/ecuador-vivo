"""Resources remain editable illustrations, never invented observations."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parent))
from output_profiles import PRESETS, profile_for
from studio_home import create_project
from studio_model import validate_scene, validate_studio
from studio_render import render_scene
from studio_resources import RESOURCE_CATALOG, insert_resource, resource_scene


class ResourceTests(unittest.TestCase):
    def test_six_resources_render_with_editable_parts_and_visible_disclaimer(self):
        self.assertEqual(len(RESOURCE_CATALOG), 6)
        for resource in RESOURCE_CATALOG:
            scene = resource_scene(resource['id'], profile_for({'id': 'tiktok'}))
            validate_scene(scene)
            self.assertEqual(scene['renderer'], 'studio')
            self.assertTrue(scene['resource']['illustrative'])
            self.assertTrue(scene['resource']['sources'])
            self.assertTrue(all(e['type'] in ('shape', 'text', 'source') for e in scene['elements']))
            self.assertTrue(any('ESQUEMA ILUSTRATIVO' in e['style'].get('text', '') for e in scene['elements']))
            self.assertTrue(any(e['animation']['in'] != 'none' for e in scene['elements']))
            with tempfile.TemporaryDirectory() as directory:
                frame = render_scene(scene, profile_for({'id': 'tiktok'}), {}, time=3)
                frame.save(Path(directory) / 'frame.png')
                self.assertEqual(frame.size, (1080, 1920))
                frame.close()

    def test_all_output_presets_keep_every_object_on_canvas(self):
        for profile_id in PRESETS:
            profile = profile_for({'id': profile_id})
            for resource in RESOURCE_CATALOG:
                scene = resource_scene(resource['id'], profile)
                for element in scene['elements']:
                    box = element['transform']
                    self.assertGreaterEqual(box['x'], 0)
                    self.assertGreaterEqual(box['y'], 0)
                    self.assertLessEqual(box['x'] + box['width'], profile.width)
                    self.assertLessEqual(box['y'] + box['height'], profile.height)
                frame = render_scene(scene, profile, {}, time=3)
                frame.close()

    def test_insert_appends_without_touching_science_or_original(self):
        project = create_project('free', {'id': 'youtube'}, name='Mi proyecto')
        project['studio']['datasets'] = {'retained': {'source': 'original'}}
        project['studio']['calculations'] = {'retained': {'value': 12}}
        before = copy.deepcopy(project)
        result = insert_resource(project, 'rain_volume', duration=7)
        validate_studio(result['studio'])
        self.assertEqual(project, before)
        self.assertEqual(result['studio']['timeline'][:-1], project['studio']['timeline'])
        self.assertEqual(result['studio']['calculations'], project['studio']['calculations'])
        self.assertEqual(result['studio']['datasets'], project['studio']['datasets'])
        self.assertEqual(result['studio']['scenes'][-1]['duration'], 7)
        again = insert_resource(result, 'rain_volume')
        self.assertNotEqual(again['studio']['timeline'][-1], result['studio']['timeline'][-1])

    def test_overlay_preserves_scene_duration_existing_elements_and_map_clock(self):
        project = create_project('free', {'id': 'tiktok'})
        sid = project['studio']['timeline'][0]
        current = next(s for s in project['studio']['scenes'] if s['id'] == sid)
        current['duration'] = 2
        current['resource_test_context'] = {'date_index': 4, 'native_resolution': 'retained'}
        before = copy.deepcopy(project)
        result = insert_resource(project, 'focus_legend', mode='overlay', scene_id=sid)
        updated = next(s for s in result['studio']['scenes'] if s['id'] == sid)
        self.assertEqual(project, before)
        self.assertEqual(updated['duration'], 2)
        self.assertEqual(result['studio']['timeline'], project['studio']['timeline'])
        self.assertEqual(updated['elements'][:len(current['elements'])], current['elements'])
        self.assertEqual(updated['resource_test_context'], current['resource_test_context'])
        self.assertTrue(updated['resource_overlays'])
        frame = render_scene(updated, profile_for({'id': 'tiktok'}), {}, time=1)
        frame.close()

    def test_invalid_authoring_inputs_fail_explicitly(self):
        profile = profile_for({'id': 'tiktok'})
        for kwargs in ({'duration': 0}, {'duration': True}, {'accent': 'red'}, {'title': 10}, {'title': 'x' * 181}):
            with self.assertRaises(ValueError):
                resource_scene('rain_volume', profile, **kwargs)
        with self.assertRaises(ValueError): resource_scene('invented', profile)
        project = create_project('free', {'id': 'tiktok'})
        with self.assertRaises(ValueError): insert_resource(project, 'rain_volume', mode='unknown')
        with self.assertRaises(ValueError): insert_resource(project, 'rain_volume', mode='overlay')
        with self.assertRaisesRegex(ValueError, '480 px'):
            resource_scene('rain_volume', {'id': 'custom', 'width': 160, 'height': 160})

    def test_short_resources_finish_their_entrances_before_last_frame(self):
        profile = profile_for({'id': 'tiktok'})
        for seconds in (1 / 30, 2 / 30, .3, 1):
            scene = resource_scene('enso_anomaly', profile, duration=seconds)
            for element in scene['elements']:
                animation = element['animation']
                if animation['in'] != 'none':
                    self.assertLessEqual(animation['delay'] + animation['duration'], scene['duration'] - 1 / 30 + 1e-9)
            frame = render_scene(scene, profile, {}, time=0)
            frame.close()


class ResourceUiTests(unittest.TestCase):
    def test_overlay_preview_and_insert_use_the_destination_duration(self):
        from streamlit.testing.v1 import AppTest
        script = '''
import streamlit as st
from studio_home import create_project
from studio_resources_ui import show_resources
if 'document' not in st.session_state:
    project = create_project('free', {'id': 'tiktok'})
    next(s for s in project['studio']['scenes'] if s['id'] == project['studio']['timeline'][0])['duration'] = 2
    st.session_state['document'] = project
def changed(project):
    st.session_state['document'] = project
show_resources(st.session_state['document'], changed, key='overlay_resources')
'''
        app = AppTest.from_string(script).run(timeout=15)
        self.assertFalse(app.exception)
        initial = copy.deepcopy(app.session_state['document'])
        app.segmented_control(key='overlay_resources_mode').set_value('overlay').run()
        self.assertFalse(app.exception)
        self.assertEqual(app.slider[0].max, 2)
        app.button(key='overlay_resources_insert').click().run()
        self.assertFalse(app.exception)
        updated = app.session_state['document']
        self.assertEqual(updated['studio']['timeline'], initial['studio']['timeline'])
        target = next(s for s in updated['studio']['scenes'] if s['id'] == updated['studio']['timeline'][0])
        self.assertEqual(target['duration'], 2)
        self.assertEqual(target['resource_overlays'][0]['id'], 'focus_legend')

    def test_gallery_without_project_does_not_create_until_author_confirms(self):
        from streamlit.testing.v1 import AppTest
        script = '''
import streamlit as st
from studio_resources_ui import show_resources
def changed(project):
    st.session_state['inserted_document'] = project
show_resources(st.session_state.get('inserted_document'), changed, key='test_resources')
'''
        app = AppTest.from_string(script).run(timeout=15)
        self.assertFalse(app.exception)
        self.assertNotIn('inserted_document', app.session_state)
        self.assertEqual(len(app.selectbox(key='test_resources_choice').options), 6)
        app.selectbox(key='test_resources_choice').select('rain_volume').run()
        self.assertFalse(app.exception)
        app.button(key='test_resources_insert').click().run()
        self.assertFalse(app.exception)
        project = app.session_state['inserted_document']
        sid = project['studio']['timeline'][-1]
        scene = next(s for s in project['studio']['scenes'] if s['id'] == sid)
        self.assertEqual(scene['resource']['id'], 'rain_volume')
        self.assertEqual(len(project['studio']['timeline']), 1)


if __name__ == '__main__':
    unittest.main()
