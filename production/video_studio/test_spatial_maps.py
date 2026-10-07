"""Geography-first previews, CSV validation and native-grid map calculations."""
import calendar
import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin

sys.path.insert(0, str(Path(__file__).parent))
from comparison_maps import native_fields, map_steps, display_grid, scale_limits
from comparison_video import render_preview, render_comparison_endcard, create_comparison_job
from spatial_csv import prepare_csv, read_csv, spatial_summary


class GeographicMaps(unittest.TestCase):
    def test_missing_rasters_do_not_create_a_mean_colored_country(self):
        output = dict(years=[2024], first_month=1, last_month=1, parameter='T2M', receipts=[])
        with self.assertRaisesRegex(ValueError, 'GeoTIFF originales'):
            native_fields(output)

    def test_two_maps_always_show_same_month_and_all_years_are_used(self):
        output = dict(years=[2016, 2024, 2026], first_month=1, last_month=2)
        steps = map_steps(output, {'map_layout': 'Dos mapas'})
        self.assertEqual(steps, [((2016, 1), (2024, 1)), ((2016, 2), (2024, 2)),
                                 ((2016, 1), (2026, 1)), ((2016, 2), (2026, 2))])
        self.assertEqual(len(map_steps(output, {'map_layout': 'Un mapa · años secuenciales'})), 6)

    def test_native_month_field_preserves_negative_temperature_and_missing_pixel(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.tif'
            with rasterio.open(path, 'w', driver='GTiff', width=2, height=1, count=31,
                               dtype='float32', crs='EPSG:4326', transform=from_origin(-78, 0, .5, .5), nodata=-9999) as src:
                for day in range(1, 32):
                    src.write(np.array([[-5, -9999 if day == 5 else 2]], dtype='float32'), day)
                    src.set_band_description(day, f'2024-01-{day:02d}')
            output = dict(years=[2024], first_month=1, last_month=1, parameter='T2M', receipts=[{'tiff_path': str(path)}])
            temp, transform, crs = native_fields(output)[(2024, 1)]
            self.assertEqual(temp[0, 0], -5.)
            self.assertTrue(np.isnan(temp[0, 1]))
            output['parameter'] = 'PRECTOTCORR'
            rain = native_fields(output)[(2024, 1)][0]
            self.assertTrue(np.isnan(rain[0, 0]))  # negative precipitation is invalid
            self.assertTrue(np.isnan(rain[0, 1]))
            projected = display_grid((temp, transform, crs), (-78, -.5, -77, 0), 40, 20)
            self.assertTrue(np.isnan(projected[:, 20:]).all())

    def test_incomplete_month_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.tif'
            with rasterio.open(path, 'w', driver='GTiff', width=1, height=1, count=1,
                dtype='float32', crs='EPSG:4326', transform=from_origin(-78, 0, .5, .5)) as src:
                src.write(np.ones((1, 1), dtype='float32'), 1)
                src.set_band_description(1, '2024-01-01')
            output = dict(years=[2024], first_month=1, last_month=1, parameter='T2M', receipts=[{'tiff_path': str(path)}])
            with self.assertRaisesRegex(ValueError, 'mes incompleto'):
                native_fields(output)

    def test_csv_points_validate_numeric_coordinates_and_out_of_frame_rows(self):
        data = read_csv(b'lat;lon;species;period\n-0,994;-77,813;A;2024\n-0,8;-77,8;B;2024\n999;0;A;2024\n0;0;A;2024\n')
        with self.assertRaisesRegex(ValueError, '2 fila'):
            prepare_csv(data, kind='points', latitude='lat', longitude='lon', category='species', period='period')
        result = prepare_csv(data, kind='points', latitude='lat', longitude='lon', category='species', period='period', allow_invalid=True)
        self.assertEqual(result['valid_rows'], 2)
        self.assertEqual(result['rejected_rows'], 2)
        self.assertAlmostEqual(result['records'][0]['lon'], -77.813)
        summary = spatial_summary(result, {})
        self.assertEqual(summary['units'], 'registros')
        self.assertIn('No son individuos', summary['comparison_cards'][0]['sub'])

    def test_provincial_csv_rejects_unknown_province_and_duplicate(self):
        frame = pd.DataFrame({'province': ['Napo', 'Imbabura', 'Atlantida'], 'value': [2., 3., 4.]})
        with self.assertRaises(ValueError):
            prepare_csv(frame, kind='polygons', province='province', value='value')
        output = prepare_csv(frame, kind='polygons', province='province', value='value', allow_invalid=True)
        self.assertEqual(len(output['records']), 2)
        self.assertEqual(scale_limits(output, {}), (2., 3.))
        duplicate = pd.DataFrame({'province': ['Napo', 'Napo'], 'value': [2., 3.]})
        with self.assertRaisesRegex(ValueError, 'varias filas'):
            prepare_csv(duplicate, kind='polygons', province='province', value='value')

    def test_points_and_polygon_preview_and_endcard_need_no_raster(self):
        cases = [prepare_csv(pd.DataFrame({'lat': [-.994], 'lon': [-77.813], 'species': ['TEST RECORD']}),
                    kind='points', latitude='lat', longitude='lon', category='species'),
                 prepare_csv(pd.DataFrame({'province': ['Napo', 'Galápagos'], 'value': [2., 3.]}),
                    kind='polygons', province='province', value='value')]
        for output in cases:
            with self.subTest(kind=output['map_kind']):
                frame = pd.DataFrame(output['records'])
                image = render_preview(frame, output, {'title': 'TEST GEOGRAPHIC MAP'})
                self.assertEqual(image.size, (1080, 1920))
                closing, summary = render_comparison_endcard(frame, output, {'title': 'TEST GEOGRAPHIC MAP'})
                self.assertEqual(closing.size, (1080, 1920))
                self.assertTrue(summary['comparison_cards'])

    def test_csv_export_preserves_records_and_distinguishes_metrics(self):
        output = prepare_csv(pd.DataFrame({'lat': [-.994], 'lon': [-77.813], 'species': ['TEST RECORD']}),
                    kind='points', latitude='lat', longitude='lon', category='species')
        with tempfile.TemporaryDirectory() as directory:
            job = create_comparison_job(pd.DataFrame(output['records']), output,
                 {'title': 'TEST RECORDS', 'duration': 6, 'endcard_enabled': False, 'citation': 'Test fixture'}, jobs_root=directory)
            receipt = json.loads((job/'receipt.json').read_text(encoding='utf-8'))
            self.assertEqual(receipt['render_type'], 'geographic_csv')
            self.assertEqual(receipt['comparison']['records'][0]['lat'], -.994)
            self.assertIn('not population', receipt['comparison']['aggregation'])
            self.assertIsNone(receipt['project']['start'])

    def test_csv_mode_is_in_editor_and_saved_project_reopens(self):
        from streamlit.testing.v1 import AppTest
        from model import default_project
        app = Path(__file__).parent / 'app.py'
        at = AppTest.from_file(str(app), default_timeout=30).run()
        next(row for row in at.selectbox if row.label == 'Tipo de video').select('CSV geográfico').run()
        self.assertFalse(at.exception)
        self.assertTrue(at.get('file_uploader'))
        project = default_project()
        project['video_type'] = 'CSV geográfico'
        project['spatial_data'] = prepare_csv(pd.DataFrame({'lat': [-.994], 'lon': [-77.813]}),
                    kind='points', latitude='lat', longitude='lon')
        at = AppTest.from_file(str(app), default_timeout=30)
        at.session_state['project'] = project
        at.run()
        self.assertFalse(at.exception, [row.message for row in at.exception])
        at.segmented_control(key='studio_phase').set_value('Maqueta').run()
        self.assertFalse(at.exception, [row.message for row in at.exception])
        self.assertTrue(at.get('bidi_component'))
        self.assertFalse(any('vista previa' in row.label.lower() for row in at.button))
        at.segmented_control(key='studio_phase').set_value('Exportar').run()
        self.assertFalse(at.exception, [row.message for row in at.exception])
        button = next(row for row in at.button if row.label == 'Generar video geográfico · MP4')
        self.assertTrue(button.disabled)  # source + coordinate review required


if __name__ == '__main__':
    unittest.main()
