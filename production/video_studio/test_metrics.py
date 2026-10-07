"""Pruebas de los cálculos del cierre de métricas (sin red)."""
import datetime as dt
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_bounds

sys.path.insert(0, str(Path(__file__).parent))
import data as D
import endcard as E
from model import default_project, validate
from variables import detect_profile, endcard_copy, resolve_aggregation

BOX = (-81.5, -5.2, -75.0, 1.8)


def project(**kw):
    p = default_project()
    p.update(kw)
    return p


def squares(n=24):
    """24 provincias sintéticas que teselan el encuadre; la última es Galápagos."""
    feats = []
    cols, rows = 6, 4
    w = (BOX[2] - BOX[0]) / cols
    h = (BOX[3] - BOX[1]) / rows
    for i in range(n):
        r, c = divmod(i, cols)
        x0, y0 = BOX[0] + c * w, BOX[1] + r * h
        ring = [[x0, y0], [x0 + w, y0], [x0 + w, y0 + h], [x0, y0 + h], [x0, y0]]
        name = 'Galápagos' if i == n - 1 else f'P{i:02d}'
        feats.append({'type': 'Feature', 'properties': {'shapeName': name},
                      'geometry': {'type': 'Polygon', 'coordinates': [ring]}})
    return feats


def accumulator(p, features=None):
    acc = E.SummaryAccumulator(p, {'type': 'FeatureCollection', 'features': []})
    acc.rank_features = features or []
    acc.rank_names = {f['properties']['shapeName'] for f in acc.rank_features}
    acc.national = len(acc.rank_features) == 24
    return acc


class VariableDetection(unittest.TestCase):
    def test_kinds(self):
        cases = [
            (dict(units='mm/día', cadence='Diaria', variable='Lluvia'), 'sum'),
            (dict(units='mm/mes', cadence='Mensual', variable='Lluvia'), 'sum'),
            (dict(units='°C', cadence='Diaria', variable='Temperatura'), 'mean'),
            (dict(units='K', cadence='Diaria', variable='LST'), 'mean'),
            (dict(units='', cadence='Mensual', variable='NDVI'), 'mean'),
            (dict(units='m/s', cadence='Diaria', variable='Viento'), 'mean'),
            (dict(units='%', cadence='Diaria', variable='Nube'), 'mean'),
            (dict(units='°C', cadence='Mensual', variable='Anomalía'), 'mean'),
            (dict(units='', cadence='Diaria', variable='???'), 'mean'),
        ]
        for case, expected in cases:
            self.assertEqual(detect_profile(case)['aggregation'], expected, case)

    def test_rate_with_wrong_cadence_is_not_summed(self):
        prof = detect_profile(dict(units='mm/día', cadence='Mensual',
                                   variable='Lluvia'))
        self.assertEqual(prof['aggregation'], 'mean')
        self.assertTrue(prof['warnings'])

    def test_manual_sum_of_temperature_is_rejected(self):
        p = project(units='°C', variable='Temperatura',
                    endcard_aggregation_mode='manual',
                    endcard_aggregation='sum')
        with self.assertRaises(ValueError):
            resolve_aggregation(p)

    def test_auto_overrides_stale_sum_default_for_temperature(self):
        p = project(units='°C', variable='Temperatura')  # default says 'sum'
        self.assertEqual(resolve_aggregation(p)[0], 'mean')

    def test_direction_is_rejected_instead_of_averaged_arithmetically(self):
        p = project(units='grados', variable='Dirección del viento')
        self.assertFalse(detect_profile(p)['supported'])
        with self.assertRaises(ValueError):
            resolve_aggregation(p)

    def test_automatic_copy_changes_for_temperature(self):
        p = project(units='°C', variable='Temperatura', cadence='Diaria')
        summary = dict(year=2024, aggregation='mean', ranking_kind='provinces',
                       province_rank=[{}] * 24)
        copy = endcard_copy(p, summary)
        self.assertEqual(copy['section_1'], '2024 EN CIFRAS')
        self.assertIn('TEMPERATURA', copy['subtitle'].upper())
        self.assertIn('CALOR', copy['section_2'])
        self.assertEqual(copy['period_label'], 'Mes más cálido')

    def test_manual_copy_preserves_user_rank_title(self):
        p = project(units='°C', variable='Temperatura', endcard_auto_text=False,
                    endcard_section_2='MI PREGUNTA')
        copy = endcard_copy(p, dict(year=None, aggregation='mean'),
                            detect_profile(p))
        self.assertEqual(copy['section_2'], 'MI PREGUNTA')


class Accumulation(unittest.TestCase):
    def test_partial_months_do_not_win(self):
        p = project(clip_ecuador=False)
        acc = accumulator(p)
        start = dt.date(2024, 1, 20)           # enero incompleto, marzo incompleto
        for i in range(60):
            acc.observe(str(start + dt.timedelta(days=i)),
                        np.full((70, 65), 5.0, 'float32'))
        out = acc.to_dict()
        self.assertEqual(out['peak_month'], 'FEB')   # único mes completo
        self.assertAlmostEqual(out['peak_month_value'], 5.0 * 29, places=4)
        self.assertTrue(any('incompletos' in w for w in out['warnings']))

    def test_complete_month_requires_calendar_dates_not_only_row_count(self):
        p = project(clip_ecuador=False)
        acc = accumulator(p)
        # Una serie importada se valida sin duplicados; esta prueba conserva
        # la defensa aquí para que una llamada programática no pueda hacer
        # pasar dos veces el 1 de febrero por el 29 de febrero.
        for _ in range(29):
            acc.observe('2024-02-01', np.full((70, 65), 5.0, 'float32'))
        out = acc.to_dict()
        self.assertTrue(any('Ningún mes está completo' in w
                            for w in out['warnings']))

    def test_annual_period_groups_by_year_not_by_month(self):
        p = project(clip_ecuador=False, units='mm/año', variable='Lluvia',
                    cadence='Anual')
        acc = accumulator(p)
        for date, value in [('2023-01-01', 3.), ('2023-02-01', 3.),
                            ('2024-01-01', 4.), ('2024-02-01', 4.)]:
            acc.observe(date, np.full((70, 65), value, 'float32'))
        out = acc.to_dict()
        self.assertEqual(out['peak_period_kind'], 'year')
        self.assertEqual(out['peak_month_year'], 2024)
        self.assertIsNone(out['peak_month_number'])
        self.assertAlmostEqual(out['peak_month_value'], 8.0)

    def test_missing_province_days_are_reported(self):
        acc = accumulator(project(clip_ecuador=False))
        acc.rank_names = {'A', 'B'}
        for i in range(10):
            acc.observe(f'2024-01-{i + 1:02d}', np.full((70, 65), 5., 'float32'),
                        province_samples={'A': 5., 'B': 5. if i >= 3 else None})
        out = acc.to_dict()
        rows = {r['name']: r for r in out['province_rank']}
        self.assertEqual(rows['A']['coverage'], 1.0)
        self.assertAlmostEqual(rows['B']['coverage'], 0.7)
        self.assertTrue(any('subestimado' in w for w in out['warnings']))

    def test_temperature_uses_mean_and_keeps_negatives(self):
        p = project(units='°C', variable='Temperatura', clip_ecuador=False)
        acc = accumulator(p)
        for i, v in enumerate((-4., 2., 6.)):
            acc.observe(f'2024-01-{i + 1:02d}', np.full((70, 65), v, 'float32'))
        out = acc.to_dict()
        self.assertEqual(out['aggregation'], 'mean')
        self.assertAlmostEqual(out['mean_period'], 4 / 3, places=5)
        self.assertEqual(out['minimum_pixel_value'], -4.0)


class NativeExtremes(unittest.TestCase):
    def test_national_max_comes_from_native_raster_not_display_grid(self):
        rng = np.random.default_rng(1)
        H, W = 3500, 3250
        base = rng.normal(24, 2, (H, W)).astype('float32')
        base[rng.random((H, W)) < 0.0005] = 45.0
        with tempfile.TemporaryDirectory() as tmp:
            tif = Path(tmp) / 'hi.tif'
            with rasterio.open(tif, 'w', driver='GTiff', height=H, width=W,
                               count=1, dtype='float32', crs='EPSG:4326',
                               transform=from_bounds(*BOX, W, H),
                               nodata=-9999) as dst:
                dst.write(base, 1)
            p = project(source='local', clip_ecuador=False, units='°C',
                        variable='Temperatura')
            feats = squares()
            values, meta = D.load_values(
                p, {'date': '2024-01-01', 'band': 1, 'path': str(tif)},
                province_features=feats)
            self.assertLess(np.nanmax(values), 40)         # la rejilla lo pierde
            acc = accumulator(p, feats)
            acc.observe('2024-01-01', values, None, meta['province_samples'],
                        meta['province_extremes'])
            out = acc.to_dict()
            self.assertAlmostEqual(out['peak_pixel_value'], 45.0, places=3)

    def test_geographic_zonal_mean_uses_approximate_cell_area_weights(self):
        feature = {
            'type': 'Feature', 'properties': {'shapeName': 'Test'},
            'geometry': {'type': 'Polygon', 'coordinates': [[
                [0, 0], [1, 0], [1, 60], [0, 60], [0, 0]
            ]]},
        }
        with tempfile.TemporaryDirectory() as tmp:
            tif = Path(tmp) / 'latitudes.tif'
            with rasterio.open(tif, 'w', driver='GTiff', height=2, width=1,
                               count=1, dtype='float32', crs='EPSG:4326',
                               transform=from_bounds(0, 0, 1, 60, 1, 2),
                               nodata=-9999) as dst:
                dst.write(np.array([[0.], [100.]], dtype='float32'), 1)
            with rasterio.open(tif) as src:
                result = D._polygon_stats(src, 1, [feature])['Test']['mean']
            self.assertNotAlmostEqual(result, 50.0, places=2)
            self.assertGreater(result, 50.0)

    def test_regional_zonal_statistic_is_clipped_to_the_visible_frame(self):
        feature = {
            'type': 'Feature', 'properties': {'shapeName': 'Province'},
            'geometry': {'type': 'Polygon', 'coordinates': [[
                [0, 0], [4, 0], [4, 1], [0, 1], [0, 0]
            ]]},
        }
        with tempfile.TemporaryDirectory() as tmp:
            tif = Path(tmp) / 'regional.tif'
            with rasterio.open(tif, 'w', driver='GTiff', height=1, width=4,
                               count=1, dtype='float32', crs='EPSG:4326',
                               transform=from_bounds(0, 0, 4, 1, 4, 1),
                               nodata=-9999) as dst:
                dst.write(np.array([[2., 2., 10., 10.]], dtype='float32'), 1)
            with rasterio.open(tif) as src:
                result = D._polygon_stats(
                    src, 1, [feature], clip_bounds=(0, 0, 2, 1)
                )['Province']['mean']
            self.assertAlmostEqual(result, 2.0)


class NegativeRanking(unittest.TestCase):
    def test_card_renders_with_negative_values(self):
        p = project(units='°C', variable='Anomalía de temperatura',
                    clip_ecuador=False)
        names = [f'Provincia {i}' for i in range(24)]
        rank = [{'name': n, 'value': 2.0 - 0.25 * i, 'days': 12, 'coverage': 1.0}
                for i, n in enumerate(names)]
        summary = dict(days=12, year=2024, aggregation='mean', units='°C',
                       aggregate_units='°C', mean_period=0.4, peak_date='2024-03-01',
                       peak_date_mean=1.2, peak_pixel_date='2024-03-02',
                       peak_pixel_value=3.1, peak_month='MAR', peak_month_number=3,
                       peak_month_year=2024, peak_month_value=1.1, city_rank=rank,
                       decimals=2, peak_period_kind='month')
        img = E.compose_endcard(p, summary)
        self.assertEqual(img.size, (1080, 1920))


if __name__ == '__main__':
    unittest.main()


class AxisAndCopy(unittest.TestCase):
    def test_axis_fill_is_reasonable(self):
        for top in (142.6, 4096, 31.9, 2.6, 0.83):
            step = E._nice_step(top)
            self.assertGreater(top / (step * 8), 0.70, top)
            self.assertLessEqual(top, step * 8)

    def test_section_title_follows_variable_but_respects_edits(self):
        from variables import section_2_title
        temp = project(units='°C', variable='Temperatura')
        self.assertIn('CALOR', section_2_title(temp, detect_profile(temp)))
        temp['endcard_section_2'] = 'MI TÍTULO'
        self.assertEqual(section_2_title(temp, detect_profile(temp)), 'MI TÍTULO')
