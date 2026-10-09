"""Persistent layer controls and canvas geometry use the export scene graph."""
import json
import sys
import unittest
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from layout_engine import begin_layout, finish_layout, place_layer, clean_layout


class CanvasFeatureTests(unittest.TestCase):
    def test_layer_names_and_locks_survive_save_and_render_without_changing_pixels(self):
        original = Image.new('RGBA', (300, 200), 'black')
        layout = clean_layout({'map': {'main': {'name': 'Mapa Ecuador', 'locked': True}}})
        layout = json.loads(json.dumps(layout))
        canvas = begin_layout(original, {'visual_layout': layout})
        place_layer(canvas, Image.new('RGBA', (40,20), 'red'), (10,30), key='main', kind='map')
        rendered = finish_layout(canvas)
        item = rendered.info['visual_scene'].payload()['layers'][0]
        self.assertEqual(item['label'], 'Mapa Ecuador')
        self.assertTrue(item['locked'])
        self.assertEqual(rendered.getpixel((10,30)), (255,0,0,255))
        self.assertEqual(original.getpixel((10,30)), (0,0,0,255))

    def test_payload_reports_the_actual_authoring_dimensions(self):
        canvas = begin_layout(Image.new('RGBA', (640,360)), {'_layout_capture': True})
        scene = finish_layout(canvas).info['visual_scene']
        self.assertEqual((scene.payload()['width'],scene.payload()['height']), (640,360))

    def test_new_layer_metadata_is_strict_and_does_not_accept_path_icons(self):
        for item in ({'locked':'false'}, {'name':'X'*181}, {'icon':'../../file'}):
            with self.assertRaises(ValueError):
                clean_layout({'map':{'e':item}})


if __name__ == '__main__':
    unittest.main()
