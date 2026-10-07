"""Offline tests for official data-source connectors."""

import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.parse

from rasterio.io import MemoryFile

import providers


class ProviderTests(unittest.TestCase):
    def test_chirps_product_urls_and_coverage_start(self):
        day = dt.date(2026, 9, 30)
        self.assertEqual(
            providers.chirps_v3_url(day, 'prelim'),
            'https://data.chc.ucsb.edu/products/CHIRPS/v3.0/'
            'daily/prelim/sat/2026/chirps-v3.0.prelim.2026.09.30.tif',
        )
        self.assertTrue(
            providers.chirps_v3_url(day, 'final_sat').endswith(
                '/daily/final/sat/cogs/2026/chirps-v3.0.sat.2026.09.30.cog'
            )
        )
        self.assertTrue(
            providers.chirps_v3_url(dt.date(1981, 1, 1), 'final_rnl').endswith(
                '/daily/final/rnl/cogs/1981/chirps-v3.0.rnl.1981.01.01.cog'
            )
        )
        with self.assertRaisesRegex(ValueError, 'comienza'):
            providers.chirps_v3_url(dt.date(2000, 12, 31), 'final_sat')

    def test_nasa_power_request_is_regional_single_parameter_and_utc(self):
        url = providers.power_daily_url(
            dt.date(2026, 9, 1), dt.date(2026, 9, 30), 'T2M',
            bbox=(-80, -2, -78, 0),
        )
        query = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        self.assertEqual(query['parameters'], ['T2M'])
        self.assertEqual(query['start'], ['20260901'])
        self.assertEqual(query['end'], ['20260930'])
        self.assertEqual(query['time-standard'], ['UTC'])
        self.assertIn('regional', urllib.parse.urlparse(url).path)

    def test_power_ecuador_bbox_is_split_into_legal_overlapping_requests(self):
        regions = providers.power_daily_regions()
        self.assertGreater(len(regions), 1)
        self.assertTrue(all(2 <= east - west <= 10 for west, _, east, _ in regions))
        self.assertTrue(all(2 <= north - south <= 10 for _, south, _, north in regions))
        ordered = sorted(regions, key=lambda region: region[0])
        self.assertEqual(ordered[0][0], providers.ECUADOR_DATA_BBOX[0])
        self.assertEqual(ordered[-1][2], providers.ECUADOR_DATA_BBOX[2])
        self.assertGreater(ordered[0][2], ordered[1][0])
        with self.assertRaisesRegex(ValueError, '10'):
            providers.power_daily_url(
                dt.date(2026, 9, 1), dt.date(2026, 9, 2), 'T2M'
            )
        with self.assertRaisesRegex(ValueError, '2'):
            providers.power_daily_regions((-80, -1, -78, 0))

    def test_power_parser_preserves_zero_and_missing_values(self):
        content = '''NASA POWER Daily Regional Data\nLAT,LON,YEAR,MO,DY,T2M\n0.25,-79.5,2026,9,1,0\n0.25,-79.5,2026,9,2,-999\n0.25,-79.5,2026,10,1,21.5\n'''
        rows = providers.parse_power_regional_csv(
            content, 'T2M', dt.date(2026, 9, 1), dt.date(2026, 9, 2)
        )
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['value'], 0)
        self.assertIsNone(rows[1]['value'])
        self.assertEqual(rows[0]['date'], '2026-09-01')

    def test_power_geotiff_has_one_native_date_band_and_nodata(self):
        rows = [
            {'date': '2026-09-01', 'lat': 0.25, 'lon': -79.5, 'value': 0},
            {'date': '2026-09-01', 'lat': 0.25, 'lon': -79.0, 'value': 20},
            {'date': '2026-09-02', 'lat': 0.25, 'lon': -79.5, 'value': None},
            {'date': '2026-09-02', 'lat': 0.25, 'lon': -79.0, 'value': 21},
            {'date': '2026-09-01', 'lat': 0.75, 'lon': -79.5, 'value': 10},
            {'date': '2026-09-01', 'lat': 0.75, 'lon': -79.0, 'value': 15},
            {'date': '2026-09-02', 'lat': 0.75, 'lon': -79.5, 'value': 11},
            {'date': '2026-09-02', 'lat': 0.75, 'lon': -79.0, 'value': 16},
        ]
        payload, days, dx, dy = providers._power_geotiff_bytes(rows, 'T2M')
        self.assertEqual(days, ['2026-09-01', '2026-09-02'])
        self.assertEqual((dx, dy), (0.5, 0.5))
        with MemoryFile(payload) as memory:
            with memory.open() as source:
                self.assertEqual(source.count, 2)
                self.assertEqual(source.crs.to_string(), 'EPSG:4326')
                self.assertEqual(source.descriptions, ('2026-09-01', '2026-09-02'))
                self.assertEqual(source.nodata, -9999)
                self.assertEqual(source.read(1)[0, 0], 10)
                self.assertEqual(source.read(1)[0, 1], 15)
                self.assertEqual(source.read(2)[0, 0], 11)

    def test_inamhi_download_filters_dates_keeps_zero_and_bundles_receipt(self):
        response = {
            'data': [
                {'fecha_toma_dato': '2026-09-01', 'valor': 0},
                {'fecha_toma_dato': '2026-09-03', 'valor': 4.2},
                {'fecha_toma_dato': '2026-10-01', 'valor': 8.0},
            ]
        }
        station = {
            'id': 71234, 'code': 'H9999', 'name': 'Estación de prueba',
            'province': 'Napo', 'canton': 'Tena', 'longitude': -77.8,
            'latitude': -0.98, 'altitude_m': 600,
        }
        parameter = {
            'code': 'PP24', 'name': 'Precipitación', 'statistic': 'Suma diaria',
            'units': 'mm',
        }
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(providers, 'STORE', Path(temp)), patch.object(
                providers, '_request_json', return_value=response
            ) as request:
                result = providers.download_inamhi_daily(
                    station, parameter, dt.date(2026, 9, 1), dt.date(2026, 9, 3)
                )
            self.assertEqual(result['count'], 2)
            self.assertEqual([row['value'] for row in result['rows']], [0, 4.2])
            self.assertEqual(result['missing_dates'], ['2026-09-02'])
            self.assertEqual(result['returned_date_span_before_filter'], {
                'start': '2026-09-01', 'end': '2026-10-01'
            })
            request.assert_called_once()
            with Path(result['csv_path']).open(encoding='utf-8-sig') as handle:
                self.assertEqual(len(handle.readlines()), 3)
            with Path(result['zip_path']).open('rb') as handle:
                self.assertTrue(handle.read(4).startswith(b'PK'))
            manifest = json.loads(Path(result['manifest_path']).read_text(encoding='utf-8'))
            self.assertIn('puntuales', manifest['spatial_note'])
            self.assertEqual(manifest['request_body']['start_date'], '2026-09-01')


if __name__ == '__main__':
    unittest.main()
