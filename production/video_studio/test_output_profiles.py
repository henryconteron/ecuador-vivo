"""Output geometry and independent adaptive regions, including legacy delivery."""
import sys
import unittest
from pathlib import Path

from PIL import Image
sys.path.insert(0, str(Path(__file__).parent))
from output_profiles import profile_for, adaptive_regions, contain_bounds
from storyboard import dimensions, format_preview


class OutputProfileTests(unittest.TestCase):
    def test_invalid_custom_input_reports_error_and_preserves_last_valid_profile(self):
        from streamlit.testing.v1 import AppTest
        def script():
            import streamlit as st
            from model import default_project
            from storyboard_ui import show_storyboard
            st.session_state.setdefault('project', default_project())
            show_storyboard(st.session_state.project, always_open=True)
        app = AppTest.from_function(script, default_timeout=15).run()
        app.selectbox(key='story_profile').select('custom').run()
        app.number_input(key='story_custom_width').set_value(1081).run()
        self.assertFalse(app.exception)
        self.assertTrue(app.error)
        self.assertEqual(dimensions(app.session_state.project), (1080,1920))

    def test_profile_can_be_selected_and_custom_size_reopens_in_the_shared_ui(self):
        from streamlit.testing.v1 import AppTest
        def script():
            import streamlit as st
            from model import default_project
            from storyboard_ui import show_storyboard
            st.session_state.setdefault('project', default_project())
            show_storyboard(st.session_state.project, always_open=True)
        app = AppTest.from_function(script, default_timeout=15).run()
        app.selectbox(key='story_profile').select('custom').run()
        app.number_input(key='story_custom_width').set_value(1440)
        app.number_input(key='story_custom_height').set_value(900).run()
        self.assertFalse(app.exception)
        self.assertEqual(dimensions(app.session_state.project), (1440,900))
        app.run()
        self.assertEqual(app.number_input(key='story_custom_width').value,1440)
        app.selectbox(key='story_profile').select('youtube').run()
        self.assertFalse(app.exception)
        self.assertEqual(dimensions(app.session_state.project), (1920,1080))

    def test_required_profiles_and_sizes_are_explicit(self):
        for name, size in [('tiktok', (1080,1920)), ('instagram_reels', (1080,1920)),
                           ('instagram_stories', (1080,1920)), ('youtube_shorts', (1080,1920)),
                           ('instagram_portrait', (1080,1350)), ('instagram_square', (1080,1080)),
                           ('youtube', (1920,1080)), ('presentation', (1920,1080))]:
            profile = profile_for({'id': name})
            self.assertEqual((profile.width, profile.height), size)
            self.assertEqual(dimensions({'delivery': {'output_profile': {'id': name}}}), size)
            self.assertEqual(profile.guide_source, 'editorial_recommendation')

    def test_custom_dimensions_validate_codec_and_resource_limits(self):
        self.assertEqual(dimensions({'delivery': {'output_profile': {
            'id': 'custom', 'width': 1440, 'height': 900}}}), (1440, 900))
        for width, height in [(1001,1000), (-2,1000), (1000,0), (float('nan'),1000),
                              (10000,10000), (True,1080)]:
            with self.assertRaises(ValueError):
                profile_for({'id':'custom', 'width':width, 'height':height})

    def test_adaptive_landscape_reflows_rather_than_scaling_portrait(self):
        tall = adaptive_regions(profile_for({'id': 'tiktok'}))
        wide = adaptive_regions(profile_for({'id': 'youtube'}))
        self.assertGreater(tall['metric']['y'], tall['map']['y'] + tall['map']['height'])
        self.assertGreater(wide['metric']['x'], wide['map']['x'] + wide['map']['width'])
        self.assertEqual(wide['map']['y'], wide['metric']['y'])

    def test_regions_and_contained_map_stay_inside_every_output(self):
        for name in ('tiktok', 'instagram_portrait', 'instagram_square', 'youtube'):
            profile = profile_for({'id':name})
            for region in adaptive_regions(profile).values():
                self.assertGreater(region['width'], 0)
                self.assertGreater(region['height'], 0)
                self.assertGreaterEqual(region['x'], 0)
                self.assertGreaterEqual(region['y'], 0)
                self.assertLessEqual(region['x']+region['width'], profile.width)
                self.assertLessEqual(region['y']+region['height'], profile.height)
            box = contain_bounds((650,700), adaptive_regions(profile)['map'])
            self.assertAlmostEqual(box['width']/box['height'], 650/700)

    def test_custom_preview_and_export_share_dimensions_without_exporting_guides(self):
        config = {'delivery': {'output_profile': {'id':'custom', 'width':640, 'height':360}}}
        image = Image.new('RGB', (200,100), 'red')
        preview = format_preview(image, config)
        self.assertEqual(preview.size, dimensions(config))
        self.assertEqual(preview.getpixel((320,180)), (255,0,0))
        self.assertEqual(image.size, (200,100))


if __name__ == '__main__':
    unittest.main()
