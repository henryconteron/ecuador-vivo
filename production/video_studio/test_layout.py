"""Shared editor/export scene geometry; no remote requests."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from layout_engine import begin_layout, finish_layout, place_layer, clean_layout, draw
from comparison_video import render_preview, render_comparison_endcard
from spatial_csv import prepare_csv


class LayoutTests(unittest.TestCase):
    def fixture(self):
        output = prepare_csv(pd.DataFrame({'lat': [-.994], 'lon': [-77.813], 'species': ['TEST RECORD']}),
                             kind='points', latitude='lat', longitude='lon', category='species')
        return pd.DataFrame(output['records']), output

    def test_browser_json_rejects_nonfinite_measurements_and_code_or_file_icons(self):
        for value in [float('nan'), float('inf'), -1]:
            with self.assertRaises(ValueError):
                clean_layout({'map': {'test': {'w': value}}})
        with self.assertRaises(ValueError):
            clean_layout({'map': {'test': {'icon': '../../secret'}}})

    def test_map_resize_is_uniform_and_movement_does_not_modify_source(self):
        source = Image.new('RGBA', (200, 100), 'red')
        canvas = begin_layout(Image.new('RGBA', (1080, 1920), 'black'),
            {'visual_layout': {'map': {'main': {'x': 50, 'y': 70, 'w': 400, 'h': 900}}}}, 'map')
        place_layer(canvas, source, (200, 300), key='main', kind='map')
        result = finish_layout(canvas)
        row = result.info['visual_scene'].items[0]
        self.assertEqual((row['x'], row['y'], row['w'], row['h']), (50, 70, 400, 200))
        self.assertEqual(source.size, (200, 100))
        self.assertEqual(result.getpixel((50,70)), (255,0,0,255))

    def test_card_namespaces_are_independent(self):
        config = {'visual_layout': {'map': {'x': {'hidden': True}}, 'endcard': {'x': {'x': 80}}}}
        for name, hidden in [('map', True), ('endcard', False)]:
            canvas = begin_layout(Image.new('RGBA', (1080,1920)), config, name)
            place_layer(canvas, Image.new('RGBA',(20,20),'red'), (10,10), key='x')
            self.assertEqual(finish_layout(canvas).info['visual_scene'].items[0]['hidden'], hidden)

    def test_scene_capture_matches_existing_comparison_pixels(self):
        frame, output = self.fixture()
        config = {'title': 'TEST GEOGRAPHIC MAP', 'citation': 'Test fixture'}
        expected = render_preview(frame, output, config)
        actual = render_preview(frame, output, {**config, '_layout_capture': True})
        delta = np.abs(np.asarray(expected).astype(int)-np.asarray(actual).astype(int))
        self.assertLess(delta.mean(), .1)
        scene = actual.info['visual_scene']
        maps = [row for row in scene.items if row['kind'] == 'map']
        self.assertTrue(any(row['id'].endswith('.main') for row in maps))
        self.assertTrue(any(row['id'] == 'legend.shared' for row in maps))
        json.dumps(scene.payload())

    def test_data_bound_numbers_cannot_be_replaced_with_manual_fake_values(self):
        canvas = begin_layout(Image.new('RGBA', (1080,1920)), {'_layout_capture': True})
        d = draw(canvas)
        d.text((20,20), '22.4 °C', fill='white')
        first = finish_layout(canvas).info['visual_scene'].items[0]
        self.assertFalse(first['content_editable'])

    def test_custom_text_and_icons_roundtrip(self):
        config = {'visual_layout': {'full_canvas': True, 'map': {
            'custom.note': {'x': 100, 'y': 110, 'w': 400, 'h': 80, 'text': 'Una nota', 'font_size': 35},
            'custom.icon': {'x': 400, 'y': 110, 'w': 80, 'h': 80, 'icon': 'temperature'}}}}
        canvas = begin_layout(Image.new('RGBA', (1080,1920)), config)
        ids = {row['id'] for row in finish_layout(canvas).info['visual_scene'].items}
        self.assertEqual(ids, {'custom.note', 'custom.icon'})

    def test_deleted_text_roundtrips_and_is_absent_from_export_but_recoverable(self):
        original = Image.new('RGBA', (200, 200), 'black')
        tile = Image.new('RGBA', (20, 20), 'white')
        config = {'visual_layout': {'map': {'label': {'deleted': True}}}}
        config = json.loads(json.dumps(config))
        canvas = begin_layout(original, config)
        place_layer(canvas, tile, (10, 10), key='label', kind='text', text='Delete me')
        result = finish_layout(canvas)
        self.assertEqual(result.getpixel((10, 10)), (0, 0, 0, 255))
        row = result.info['visual_scene'].items[0]
        self.assertTrue(row['deleted'])
        self.assertEqual(result.info['visual_scene'].payload()['layers'][0]['text'], 'Delete me')
        config['visual_layout']['map']['label']['deleted'] = False
        canvas = begin_layout(original, config)
        place_layer(canvas, tile, (10, 10), key='label', kind='text')
        self.assertEqual(finish_layout(canvas).getpixel((10, 10)), (255, 255, 255, 255))

    def test_removing_a_metric_changes_only_its_presentation(self):
        frame = pd.DataFrame([dict(year=y, month=1, area='Ecuador', value=v, complete=True)
            for y,v in [(2024,20.),(2026,21.)]])
        output = dict(parameter='T2M', mode='nacional', area='Ecuador', years=[2024,2026], first_month=1,last_month=1)
        image, expected = render_comparison_endcard(frame,output,{'units':'°C','_layout_capture':True})
        row = next(x for x in image.info['visual_scene'].items if x['kind']=='text' and not x['content_editable'])
        changed, actual = render_comparison_endcard(frame, output, {'units':'°C','visual_layout':{
            'full_canvas':True,'endcard':{row['id']:{'deleted':True}}}})
        self.assertEqual(expected, actual)
        self.assertTrue(next(x for x in changed.info['visual_scene'].items if x['id']==row['id'])['deleted'])

    def test_deleted_custom_text_can_be_recovered_and_namespaces_do_not_leak(self):
        layout = {'map':{'custom.a':{'text':'Test','deleted':True}}, 'endcard':{}}
        config = {'visual_layout': clean_layout(layout)}
        image = finish_layout(begin_layout(Image.new('RGBA',(1080,1920)), config))
        self.assertFalse(image.getbbox())
        self.assertTrue(image.info['visual_scene'].items[0]['deleted'])
        config['visual_layout']['map']['custom.a']['deleted']=False
        image = finish_layout(begin_layout(Image.new('RGBA',(1080,1920)), config))
        self.assertTrue(image.getbbox())

    def test_empty_text_stays_selectable_and_can_be_edited_again(self):
        image = begin_layout(Image.new('RGBA', (200, 200)), {'_layout_capture': True})
        draw(image).text((20, 20), 'A label', fill='white')
        key = finish_layout(image).info['visual_scene'].items[0]['id']
        config = {'visual_layout': {'map': {key: {'text': ''}}}}
        image = begin_layout(Image.new('RGBA', (200, 200)), config)
        draw(image).text((20, 20), 'A label', fill='white')
        result = finish_layout(image)
        self.assertIsNone(result.getbbox())
        scene = result.info['visual_scene']
        self.assertEqual(scene.items[0]['id'], key)
        self.assertTrue(scene.items[0]['content_editable'])
        config['visual_layout']['map'][key]['text'] = 'Recovered'
        image = begin_layout(Image.new('RGBA', (200, 200)), config)
        draw(image).text((20, 20), 'A label', fill='white')
        self.assertIsNotNone(finish_layout(image).getbbox())

    def test_imported_custom_elements_have_a_memory_budget(self):
        with self.assertRaises(ValueError):
            clean_layout({'map': {'custom.a': {'w': 3840, 'h': 3840},
                                  'custom.b': {'w': 3840, 'h': 3840}}})

    def test_rain_metric_scene_matches_classic_canvas_and_keeps_all_provinces(self):
        from model import default_project
        from endcard import compose_endcard
        project = default_project()
        project.update(units='mm/día')
        summary = dict(days=12, year=2024, aggregation='sum', units='mm/día', aggregate_units='mm',
            mean_period=2.4, peak_date='2024-03-01', peak_date_mean=12., peak_pixel_date='2024-03-02',
            peak_pixel_value=31., peak_month='MAR', peak_month_number=3, peak_month_year=2024,
            peak_month_value=1.1, decimals=1, peak_period_kind='month',
            city_rank=[dict(name=f'TEST PROVINCE {i}', value=100-i, days=12, coverage=1.) for i in range(24)])
        # Compare the same authoring canvas, before the legacy template's
        # automatic social-margin shrink (the visual editor owns its margins).
        with patch('endcard.compose_final', side_effect=lambda image: image):
            expected = compose_endcard(project, summary)
        captured = compose_endcard({**project, '_layout_capture': True}, summary)
        delta = np.abs(np.asarray(expected).astype(int)-np.asarray(captured).astype(int))
        self.assertLess(delta.mean(), .1)
        rows = captured.info['visual_scene'].items
        self.assertTrue(any('TEST PROVINCE 23' in row['text'] for row in rows))

    def test_editorial_closing_can_move_text_and_swap_icon_without_changing_metrics(self):
        frame = pd.DataFrame([dict(year=year, month=1, area='Ecuador', value=value, complete=True)
                              for year, value in [(2024,20.), (2026,21.)]])
        output = dict(parameter='T2M', mode='nacional', area='Ecuador', years=[2024,2026],first_month=1,last_month=1)
        first, summary = render_comparison_endcard(frame,output,{'units':'°C','_layout_capture':True})
        icon = next(row for row in first.info['visual_scene'].items if row['kind']=='icon')
        changed, next_summary = render_comparison_endcard(frame,output,{'units':'°C','visual_layout':{
            'full_canvas':True,'endcard':{icon['id']:{'x':60,'y':500,'w':80,'h':80,'icon':'wind'}}}})
        self.assertEqual(summary['period_values'],next_summary['period_values'])
        row = next(row for row in changed.info['visual_scene'].items if row['id']==icon['id'])
        self.assertEqual(row['icon'],'wind')
        self.assertEqual((row['x'],row['y']), (60,500))


if __name__ == '__main__':
    unittest.main()
