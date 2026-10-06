"""Run with the studio environment: python -m unittest discover -s production/video_studio."""
import copy
import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import rasterio
from rasterio.transform import from_bounds
from streamlit.testing.v1 import AppTest

from model import default_project, upgrade_project, TEXT_DEFAULTS, validate, frame_counts, STORE, ROOT
from data import load_values, inspect_file, boundary
from render import compose, colorize
from jobs import execute, write_json, read_json, process_alive
from social import LAYOUTS, guided_preview
import io
import os


class StudioTests(unittest.TestCase):
    def test_duration_includes_every_date(self):
        self.assertEqual(frame_counts(366, 549), [45] * 366)
        counts = frame_counts(366, 61.1)
        self.assertEqual(sum(counts), 1833)
        self.assertTrue(all(n >= 1 for n in counts))
        with self.assertRaises(ValueError):
            frame_counts(366, 1)

    def test_chirps_dates(self):
        p = default_project()
        rows = validate(p)
        self.assertEqual(len(rows), 366)
        self.assertEqual(rows[-1]['date'], '2024-12-31')
        p['end'] = '2023-01-01'
        with self.assertRaises(ValueError):
            validate(p)

    def test_raster_import_conversion_and_categories(self):
        (STORE/'imports').mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=STORE/'imports') as folder:
            path = Path(folder)/'temperature.tif'
            with rasterio.open(path, 'w', driver='GTiff', height=8, width=8, count=2,
                               dtype='float32', crs='EPSG:4326', transform=from_bounds(-81.5,-5.2,-75,1.8,8,8), nodata=-9999) as dst:
                dst.write(np.full((8,8), 300, dtype='float32'), 1)
                dst.write(np.full((8,8), -9999, dtype='float32'), 2)
                dst.set_band_description(1, '20240101_value')
                dst.set_band_description(2, 'valid_days')
            info = inspect_file(path, path.name)
            self.assertEqual(info[0]['fecha'], '2024-01-01')
            self.assertFalse(info[1]['usar'])
            p = default_project()
            p.update(source='local', offset=-273.15, entries=[{'date':'2024-01-01','path':str(path),'band':1}])
            rows = validate(p)
            values, _ = load_values(p, rows[0])
            self.assertAlmostEqual(float(values[0,0]), 26.85, places=3)
            with self.assertRaises(ValueError):
                load_values(p, dict(rows[0], band=2))
            p.update(offset=0, kind='categorical')
            with self.assertRaisesRegex(ValueError, 'Faltan clases'):
                load_values(p, rows[0])
            p['classes'] = [{'value':300,'label':'Clase conocida','color':'#123456'}]
            values, _ = load_values(p, rows[0])
            self.assertTrue(np.all(colorize(values,p)==np.array([18,52,86])))

    def test_project_rejects_bad_paths_and_duplicate_dates(self):
        p = default_project()
        p.update(source='local', entries=[{'date':'2024-01-01','path':str(ROOT/'README.md'),'band':1}])
        with self.assertRaises(ValueError):
            validate(p)
        p['entries'] *= 2
        with self.assertRaisesRegex(ValueError, 'duplicadas'):
            validate(p)

    def test_preview_real_cache(self):
        p = default_project()
        values, _ = load_values(p, {'date':'2024-01-01'})
        frame = compose(p, values, boundary(), '2024-01-01', 0, 366)
        self.assertEqual(frame.size, (1080,1920))
        self.assertEqual(frame.getpixel((0,0)), (11,25,34))
        p['background'] = '#f4f0e8'
        frame2 = compose(p, values, boundary(), '2024-01-01', 0, 366)
        self.assertEqual(frame2.getpixel((0,0)), (244,240,232))

    def test_social_bounds_and_overflow(self):
        p=default_project()
        p.update(author='Elaborado por Henry P. Conteron Moreta',credits='Cartografía y divulgación · Ecuador Vivo')
        values=np.ones((8,8),dtype='float32')
        for mode in LAYOUTS:
            p['layout']=mode
            frame=compose(p,values,boundary(),'2024-01-01',0,366)
            left,top,right,bottom=LAYOUTS[mode]
            for box in frame.info['safe_text_boxes']:
                self.assertGreaterEqual(box[0],left)
                self.assertGreaterEqual(box[1],top)
                self.assertLessEqual(box[2],right)
                self.assertLessEqual(box[3],bottom)
            self.assertEqual(frame.getpixel((100,1800)), (11,25,34))
            buf=io.BytesIO();frame.save(buf,format='PNG')
            guided=guided_preview(buf.getvalue(),mode)
            self.assertNotEqual(guided.getpixel((100,1800)),frame.getpixel((100,1800)))
        p['title']='Título muy extenso para un video móvil ' * 5
        with self.assertRaisesRegex(ValueError,'Título: acorta'):
            compose(p,values,boundary(),'2024-01-01',0,366)
        p=default_project();p.update(width=720,kind='categorical')
        self.assertEqual(compose(p,values,boundary(),'2024-01-01',0,366).size,(720,1280))

    def test_editor_changes_persist_and_preview(self):
        at = AppTest.from_file(str(Path(__file__).with_name('app.py')), default_timeout=30).run()
        self.assertFalse(at.exception)
        at.segmented_control(key='step').set_value('Diseño').run()
        at.text_input(key='title_0').set_value('Mi historia del agua').run()
        self.assertEqual(at.session_state['project']['title'], 'Mi historia del agua')
        at.segmented_control(key='step').set_value('Textos y créditos').run()
        at.text_input(key='author_0').set_value('Elaborado por Henry').run()
        at.text_input(key='credits_0').set_value('Cartografía · Ecuador Vivo').run()
        at.text_input(key='brand_0').set_value('MI MARCA').run()
        at.text_input(key='counter_0').set_value('DAY').run()
        at.text_input(key='city_label_Tena_0').set_value('Tena / Napo').run()
        at.segmented_control(key='step').set_value('Mapa y tiempo').run()
        at.number_input(key='duration_0').set_value(61.).run()
        at.segmented_control(key='step').set_value('Diseño').run()
        self.assertEqual(at.text_input(key='title_0').value, 'Mi historia del agua')
        at.segmented_control(key='step').set_value('Textos y créditos').run()
        self.assertEqual(at.text_input(key='author_0').value, 'Elaborado por Henry')
        self.assertEqual(at.text_input(key='city_label_Tena_0').value, 'Tena / Napo')
        at.button(key='preview_button').click().run()
        self.assertFalse(at.exception)
        self.assertIsNotNone(at.session_state['preview'])

    def test_credit_migration_and_rendered_text(self):
        p = default_project()
        for key in TEXT_DEFAULTS:
            del p[key]
        validate(p)
        self.assertEqual(p['author'], '')
        p.update(author='Autoría de prueba', credits='Crédito de prueba', brand='Marca propia',
                 counter_label='DAY', scale_note='Escala personalizada', boundary_note='Límites: geoBoundaries · Ecuador')
        values = np.ones((8,8), dtype='float32')
        with patch('render.ImageDraw.ImageDraw.text') as draw_text:
            compose(p, values, boundary(), '2024-01-01', 0, 366)
            texts = [call.args[1] for call in draw_text.call_args_list]
        for label in [p['author'], p['credits'], p['brand'], p['scale_note'], p['boundary_note'], 'DAY 01 / 366']:
            self.assertIn(label, texts)
        saved = json.loads(json.dumps(p))
        self.assertEqual(upgrade_project(saved)['author'], p['author'])
        p['author'] = 'x' * 201
        with self.assertRaises(ValueError):
            validate(p)

    def test_cancelled_job_never_publishes_final(self):
        (STORE/'jobs').mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=STORE/'jobs') as folder:
            job = Path(folder)
            p = default_project()
            p.update(end='2024-01-01', duration=1.5)
            write_json(job/'project.json', p)
            (job/'cancel.request').touch()
            execute(job)
            self.assertEqual(read_json(job/'status.json')['state'], 'cancelled')
            self.assertFalse((job/'ecuador-vivo.mp4').exists())
            self.assertFalse((job/'receipt.json').exists())
        self.assertTrue(process_alive(os.getpid()))


if __name__ == '__main__':
    unittest.main()
