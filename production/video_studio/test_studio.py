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
from data import load_values, inspect_file, boundary, province_boundaries
from render import compose, colorize
from jobs import execute, write_json, read_json, process_alive
from social import LAYOUTS, guided_preview
from endcard import CAPITALS, SummaryAccumulator, compose_endcard
import io
import os
import gzip

from maqueta import (load_galapagos_scene, GALAPAGOS_BOX, GAL_W_MAX,
                     GAL_ASPECT, DESIGN_CROP, MAIN_BOX, MAIN_W, MAIN_H,
                     MAIN_X, MAIN_Y, build_mask_and_rings, place_galapagos)


class StudioTests(unittest.TestCase):
    def test_galapagos_native_values_do_not_include_ocean_or_fake_zero(self):
        # Match CHIRPS files that encode -9999 without declaring nodata.
        with tempfile.TemporaryDirectory() as folder:
            tif = Path(folder) / 'islands.tif'
            compressed = Path(folder) / 'islands.tif.gz'
            gal_w = GAL_W_MAX
            gal_h = round(gal_w * GAL_ASPECT)
            def scene_for(values):
                with rasterio.open(tif, 'w', driver='GTiff', height=8, width=8,
                                   count=1, dtype='float32', crs='EPSG:4326',
                                   transform=from_bounds(*GALAPAGOS_BOX, 8, 8)) as dst:
                    dst.write(values, 1)
                compressed.write_bytes(gzip.compress(tif.read_bytes()))
                with patch('maqueta.rain_path', return_value=(compressed, 'fixture')):
                    return load_galapagos_scene(default_project(), '2024-04-01',
                                                gal_w, gal_h)

            values = np.full((8, 8), -9999, dtype='float32')
            values[3:5, 3:5] = [[0, 10], [20, 30]]
            scene = scene_for(values)
            self.assertEqual(scene['valid_pixels'], 4)
            self.assertEqual(scene['mean'], 15)
            self.assertEqual(scene['max'], 30)
            self.assertTrue(np.isnan(scene['values'][0, 0]))
            self.assertGreater(np.nanmax(scene['values']), 20)
            self.assertGreater(scene['values'][gal_h*9//16, gal_w*9//16],
                               scene['values'][gal_h*7//16, gal_w*7//16])

            values[3:5, 3:5] = 0
            scene = scene_for(values)
            self.assertEqual(scene['mean'], 0)
            self.assertTrue(np.isfinite(scene['values']).any())
            scene = scene_for(np.full((8, 8), -9999, dtype='float32'))
            self.assertIsNone(scene['mean'])
            self.assertIsNone(scene['max'])
            self.assertTrue(np.isnan(scene['values']).all())

    def test_galapagos_fits_crop_and_keeps_mainland_visible(self):
        mask, _, _ = build_mask_and_rings(boundary(), MAIN_BOX, MAIN_W, MAIN_H)
        gal = place_galapagos(mask, MAIN_X, MAIN_Y)
        self.assertIsNotNone(gal)
        left, top, right, bottom = gal['panel']
        self.assertGreaterEqual(left, DESIGN_CROP[0])
        self.assertGreaterEqual(top, DESIGN_CROP[1])
        self.assertLessEqual(right, DESIGN_CROP[2])
        self.assertLessEqual(bottom, DESIGN_CROP[3])
        self.assertAlmostEqual(gal['w'] / gal['h'],
                               (GALAPAGOS_BOX[2]-GALAPAGOS_BOX[0]) /
                               (GALAPAGOS_BOX[3]-GALAPAGOS_BOX[1]), places=2)
        mainland = np.asarray(mask)
        self.assertTrue(mainland.any())
        # The inset may overlap the western ocean area of the mainland layout,
        # but it must never cover the entire map or move outside the crop.
        outside = mainland.copy()
        outside[max(0, top-MAIN_Y):min(MAIN_H, bottom-MAIN_Y),
                max(0, left-MAIN_X):min(MAIN_W, right-MAIN_X)] = 0
        self.assertTrue(outside.any())

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
        self.assertEqual(frame.getpixel((0,0)), (4,20,31))
        p['background'] = '#f4f0e8'
        frame2 = compose(p, values, boundary(), '2024-01-01', 0, 366)
        self.assertEqual(frame2.getpixel((0,0)), (244,240,232))

    def test_endcard_is_editable_and_uses_source_summary(self):
        p = default_project()
        self.assertTrue(p['endcard_enabled'])
        self.assertEqual(p['endcard_duration'], 6.0)
        values = np.ones((8, 8), dtype='float32')
        summary = SummaryAccumulator(p, boundary())
        summary.observe('2024-01-01', values)
        p['endcard_title'] = 'CIERRE DE PRUEBA'
        image = compose_endcard(p, summary.to_dict())
        self.assertEqual(image.size, (1080, 1920))
        p['endcard_duration'] = 31
        with self.assertRaisesRegex(ValueError, 'entre 1 y 30'):
            validate(p)

    def test_endcard_ranks_all_24_provinces_including_galapagos(self):
        p = default_project()
        summary = SummaryAccumulator(p, boundary())
        self.assertEqual(len(summary.rank_features), 24)
        samples = {
            feature['properties']['shapeName']: 2.5
            for feature in province_boundaries()
        }
        values = np.ones((8, 8), dtype='float32')
        summary.observe('2024-01-01', values, province_samples=samples)
        ranking = summary.to_dict()['city_rank']
        self.assertEqual(len(ranking), 24)
        self.assertIn('Galápagos',
                      {row['name'] for row in ranking})

    def test_provincial_statistics_use_native_raster_and_include_galapagos(self):
        """An imported raster covering Ecuador + islands yields 24 ADM1 means.

        All cells deliberately share one value: the test verifies coverage and
        polygon sampling, not a visually resampled map colour.
        """
        (STORE / 'imports').mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=STORE / 'imports') as folder:
            path = Path(folder) / 'ecuador_y_galapagos.tif'
            with rasterio.open(
                path, 'w', driver='GTiff', height=90, width=190, count=1,
                dtype='float32', crs='EPSG:4326',
                transform=from_bounds(-93, -6, -74, 3, 190, 90),
            ) as dst:
                dst.write(np.full((90, 190), 7.25, dtype='float32'), 1)
            p = default_project()
            p.update(source='local', entries=[{
                'date': '2024-01-01', 'path': str(path), 'band': 1,
            }], endcard_aggregation='mean', units='°C')
            row = validate(p)[0]
            values, metadata = load_values(
                p, row, province_features=province_boundaries()
            )
            self.assertTrue(np.isfinite(values).any())
            samples = metadata['province_samples']
            self.assertEqual(len(samples), 24)
            self.assertAlmostEqual(samples['Galápagos'], 7.25, places=5)
            scene = load_galapagos_scene(
                p, row['date'], GAL_W_MAX, round(GAL_W_MAX * GAL_ASPECT)
            )
            self.assertIsNotNone(scene)
            self.assertTrue(np.isfinite(scene['values']).any())
            summary = SummaryAccumulator(p, boundary())
            summary.observe(row['date'], values,
                            province_samples=samples)
            ranking = summary.to_dict()['province_rank']
            self.assertEqual(len(ranking), 24)
            self.assertIn('Galápagos', {item['name'] for item in ranking})

    def test_endcard_keeps_negative_intensive_values_and_averages_them(self):
        p = default_project()
        p.update(source='local', endcard_aggregation='mean', units='°C')
        values_a = np.full((8, 8), -2.0, dtype='float32')
        values_b = np.full((8, 8), 6.0, dtype='float32')
        summary = SummaryAccumulator(p, boundary())
        summary.observe('2024-01-01', values_a)
        summary.observe('2024-02-01', values_b)
        result = summary.to_dict()
        self.assertAlmostEqual(result['mean_period'], 2.0)
        self.assertAlmostEqual(result['peak_month_value'], 6.0)
        self.assertEqual(result['aggregate_units'], '°C')
        self.assertEqual(result['aggregation'], 'mean')

    def test_endcard_does_not_merge_months_from_different_years(self):
        p = default_project()
        p['endcard_aggregation'] = 'sum'
        summary = SummaryAccumulator(p, boundary())
        summary.observe('2024-01-01', np.full((8, 8), 10, dtype='float32'))
        summary.observe('2025-01-01', np.full((8, 8), 10, dtype='float32'))
        summary.observe('2024-02-01', np.full((8, 8), 15, dtype='float32'))
        result = summary.to_dict()
        self.assertEqual(result['peak_month_number'], 2)
        self.assertEqual(result['peak_month_year'], 2024)
        self.assertIsNone(result['year'])

    def test_categorical_project_requires_a_non_numeric_endcard(self):
        p = default_project()
        p['kind'] = 'categorical'
        with self.assertRaisesRegex(ValueError, 'variable continua'):
            validate(p)

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
            self.assertEqual(frame.getpixel((100,1800)), (4,20,31))
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
        at.button(key='home_legacy').click().run()
        if not hasattr(at, 'segmented_control'):
            self.skipTest('La versión instalada de AppTest no expone segmented_control.')
        at.segmented_control(key='studio_phase').set_value('Maqueta').run()
        title_key = next(widget.key for widget in at.text_input if widget.key.startswith('title_'))
        at.text_input(key=title_key).set_value('Mi historia del agua').run()
        self.assertEqual(at.session_state['project']['title'], 'Mi historia del agua')
        at.segmented_control(key='step').set_value('Textos y créditos').run()
        author_key = next(widget.key for widget in at.text_input if widget.key.startswith('author_'))
        credits_key = next(widget.key for widget in at.text_input if widget.key.startswith('credits_'))
        brand_key = next(widget.key for widget in at.text_input if widget.key.startswith('brand_'))
        counter_key = next(widget.key for widget in at.text_input if widget.key.startswith('counter_'))
        city_key = next(widget.key for widget in at.text_input if widget.key.startswith('city_label_Tena_'))
        at.text_input(key=author_key).set_value('Elaborado por Henry').run()
        at.text_input(key=credits_key).set_value('Cartografía · Ecuador Vivo').run()
        at.text_input(key=brand_key).set_value('MI MARCA').run()
        at.text_input(key=counter_key).set_value('DAY').run()
        at.text_input(key=city_key).set_value('Tena / Napo').run()
        at.segmented_control(key='studio_phase').set_value('Montaje').run()
        duration_key = next(widget.key for widget in at.number_input if widget.key.startswith('map_seconds_'))
        at.number_input(key=duration_key).set_value(61.).run()
        at.segmented_control(key='studio_phase').set_value('Maqueta').run()
        at.segmented_control(key='step').set_value('Diseño').run()
        title_key = next(widget.key for widget in at.text_input if widget.key.startswith('title_'))
        self.assertEqual(at.text_input(key=title_key).value, 'Mi historia del agua')
        at.segmented_control(key='step').set_value('Textos y créditos').run()
        author_key = next(widget.key for widget in at.text_input if widget.key.startswith('author_'))
        city_key = next(widget.key for widget in at.text_input if widget.key.startswith('city_label_Tena_'))
        self.assertEqual(at.text_input(key=author_key).value, 'Elaborado por Henry')
        self.assertEqual(at.text_input(key=city_key).value, 'Tena / Napo')
        self.assertFalse(at.exception)
        self.assertTrue(at.get('bidi_component'))
        self.assertFalse(any('vista previa' in row.label.lower() for row in at.button))
        self.assertEqual(at.session_state['project']['duration'], 61.)

    def test_credit_migration_and_rendered_text(self):
        p = default_project()
        for key in TEXT_DEFAULTS:
            del p[key]
        validate(p)
        self.assertEqual(p['author'], 'Henry P. Conteron Moreta')
        p.update(author='Autoría de prueba', credits='Crédito de prueba', brand='Marca propia',
                 counter_label='DAY', scale_note='Escala personalizada', boundary_note='Límites: geoBoundaries · Ecuador')
        values = np.ones((8,8), dtype='float32')
        frame = compose(p, values, boundary(), '2024-01-01', 0, 366)
        self.assertEqual(frame.size, (1080, 1920))
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
