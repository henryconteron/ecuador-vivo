import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.io import MemoryFile
from rasterio.transform import from_origin

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "video_studio"))

from climate_comparison import (  # noqa: E402
    _monthly_grid,
    annual_rank,
    display_units,
    ee_climate_script,
    parse_cpc_index,
    year_range,
    summarize_raster_months,
)
from comparison_video import create_comparison_job, render_preview, comparison_summary, render_comparison_endcard  # noqa: E402


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.sources = tempfile.TemporaryDirectory()
        self.addCleanup(self.sources.cleanup)

    def attach_sources(self, output):
        import calendar
        receipts = []
        for year in output['years']:
            dates = [dt.date(year, month, day) for month in range(output['first_month'], output['last_month']+1)
                     for day in range(1, calendar.monthrange(year, month)[1]+1)]
            path = Path(self.sources.name) / f'{year}.tif'
            with rasterio.open(path, 'w', driver='GTiff', width=36, height=16, count=len(dates),
                dtype='float32', crs='EPSG:4326', transform=from_origin(-93, 2, .5, .5), nodata=-9999) as source:
                for index, day in enumerate(dates, 1):
                    source.write(np.full((16, 36), 15.+day.month, dtype='float32'), index)
                    source.set_band_description(index, day.isoformat())
            receipts.append({'tiff_path': str(path), 'start': dates[0].isoformat(), 'end': dates[-1].isoformat(), 'provider': 'TEST FIXTURE'})
        output['receipts'] = receipts
        return output

    def test_video_maqueta_renders_monthly_comparison(self):
        frame = pd.DataFrame([
            {"year": year, "month": month, "month_label": "Ene", "value": value,
             "units": "°C", "complete": True}
            for year, values in ((2023, [14.0, 14.5, 15.0]), (2024, [15.0, 15.2, 16.0]))
            for month, value in enumerate(values, start=1)
        ])
        output = {
            "mode": "provincia", "area": "Napo", "years": [2023, 2024],
            "first_month": 1, "last_month": 3, "parameter": "T2M",
            "source": "NASA POWER · clima",
        }
        self.attach_sources(output)
        image = render_preview(frame, output, {
            "title": "¿Cómo cambió la temperatura?", "subtitle": "Napo · comparación mensual",
            "variable": "Temperatura del aire", "units": "°C",
            "citation": "NASA POWER", "author": "Ecuador Vivo",
        })
        self.assertEqual(image.size, (1080, 1920))

    def test_video_maqueta_renders_provincial_ranking(self):
        frame = pd.DataFrame([
            {"year": 2024, "month": 1, "month_label": "Ene", "value": 2.0,
             "units": "mm/mes", "complete": True},
        ])
        ranking = pd.DataFrame([
            {"year": 2024, "area": f"Provincia {index:02d}", "value": float(25 - index), "units": "mm del periodo"}
            for index in range(1, 25)
        ])
        output = {
            "mode": "ranking", "area": "Ecuador", "years": [2024],
            "first_month": 1, "last_month": 1, "parameter": "PRECTOTCORR",
            "source": "NASA POWER · clima",
        }
        self.attach_sources(output)
        image = render_preview(frame, output, {
            "title": "¿Dónde llovió más?", "subtitle": "Ranking provincial",
            "variable": "Precipitación", "units": "mm del periodo",
            "citation": "NASA POWER", "author": "Ecuador Vivo",
        }, rank_frame=ranking)
        self.assertEqual(image.size, (1080, 1920))

    def test_comparison_export_saves_mp4_csv_and_receipt(self):
        frame = pd.DataFrame([
            {"year": year, "month": month, "month_label": "Ene", "value": value,
             "units": "°C", "complete": True}
            for year, values in ((2023, [14.0, 14.5]), (2024, [15.0, 15.2]))
            for month, value in enumerate(values, start=1)
        ])
        output = {
            "mode": "provincia", "area": "Napo", "years": [2023, 2024],
            "first_month": 1, "last_month": 2, "parameter": "T2M",
            "source": "NASA POWER · clima", "receipts": [],
        }
        with tempfile.TemporaryDirectory() as temporary:
            self.attach_sources(output)
            job = create_comparison_job(
                frame, output,
                {"title": "Temperatura en Napo", "subtitle": "Prueba audiovisual",
                 "variable": "Temperatura", "units": "°C", "duration": 6},
                jobs_root=Path(temporary),
            )
            receipt = json.loads((job / "receipt.json").read_text(encoding="utf-8"))
            self.assertTrue((job / "ecuador-vivo.mp4").is_file())
            self.assertTrue((job / "comparison.csv").is_file())
            self.assertEqual(receipt["render_type"], "climate_comparison")
            self.assertEqual(receipt["comparison"]["years"], [2023, 2024])

    def test_comparison_tools_are_inside_video_studio(self):
        from streamlit.testing.v1 import AppTest

        app = HERE / "app.py"
        at = AppTest.from_file(str(app), default_timeout=30).run()
        self.assertFalse(at.exception)
        selector = next(row for row in at.selectbox if row.label == 'Tipo de video')
        selector.set_value('Comparación climática').run()
        self.assertFalse(at.exception)
        self.assertEqual(at.radio(key='section').value, 'Editor')
        self.assertNotIn('Comparar para video', at.radio(key='section').options)
        self.assertEqual(at.segmented_control(key="climate_comparison_view").value, "Años y territorios")

    def test_prepared_comparison_reaches_design_and_endcard_without_palette_error(self):
        from streamlit.testing.v1 import AppTest
        from model import default_project
        frame = pd.DataFrame([
            {'year': year, 'month': month, 'month_label': ['Ene', 'Feb'][month-1], 'value': value,
             'area': 'Napo', 'units': '°C', 'complete': True, 'days_with_data': dt.date(year, 3, 1).day + 30 if month == 1 else 29,
             'days_expected': 31 if month == 1 else 29}
            for year in [2020, 2024] for month, value in [(1, 12.0), (2, 18.0)]
        ])
        output = {'frames': [frame], 'receipts': [], 'mode': 'provincia', 'area': 'Napo', 'years': [2020, 2024],
                  'first_month': 1, 'last_month': 2, 'parameter': 'T2M',
                  'source': 'NASA POWER · temperatura, lluvia, viento y humedad (~50–60 km)'}
        self.attach_sources(output)
        project = default_project()
        project['video_type'] = 'Comparación climática'
        at = AppTest.from_file(str(HERE / 'app.py'), default_timeout=30)
        at.session_state['project'] = project
        at.session_state['climate_comparison'] = output
        at.run()
        self.assertFalse(at.exception, [row.message for row in at.exception])
        at.segmented_control(key='studio_phase').set_value('Maqueta').run()
        self.assertTrue(any(row.label == 'Paleta' for row in at.selectbox))
        self.assertTrue(at.get('bidi_component'))
        self.assertFalse(at.get('imgs'))
        controls = next(row for row in at.segmented_control if row.label == 'Controles')
        controls.set_value('Textos y créditos').run()
        next(row for row in at.text_input if row.label == 'Autoría').set_value('Autor de prueba').run()
        self.assertEqual(at.session_state['project']['author'], 'Autor de prueba')
        next(row for row in at.segmented_control if row.label == 'Controles').set_value('Diseño').run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state['project']['comparison_design']['author'], 'Autor de prueba')
        at.segmented_control(key='studio_phase').set_value('Datos').run()
        next(row for row in at.selectbox if row.label == 'Variable').set_value('Precipitación corregida').run()
        self.assertFalse(at.exception)
        self.assertFalse(any(row.label == 'Generar video comparativo · MP4' for row in at.button))
        at.segmented_control(key='studio_phase').set_value('Exportar').run()
        self.assertFalse(any(row.label == 'Generar video comparativo · MP4' for row in at.button))
        at.segmented_control(key='studio_phase').set_value('Datos').run()
        next(row for row in at.selectbox if row.label == 'Tipo de video').set_value('Mapa temporal').run()
        self.assertFalse(at.exception)
        next(row for row in at.selectbox if row.label == 'Tipo de video').set_value('Comparación climática').run()
        self.assertFalse(at.exception)

    def test_comparison_closing_weights_temperature_and_sums_rain(self):
        frame = pd.DataFrame([{'year': 2024, 'month': month, 'value': value, 'complete': True, 'area': 'Napo'}
                              for month, value in [(1, 10.), (2, 20.)]])
        output = {'mode': 'provincia', 'area': 'Napo', 'years': [2024], 'first_month': 1, 'last_month': 2, 'parameter': 'T2M'}
        summary = comparison_summary(frame, output, {'units': '°C'})
        self.assertAlmostEqual(summary['period_values'][0]['value'], (10*31 + 20*29)/60)
        output['parameter'] = 'PRECTOTCORR'
        summary = comparison_summary(frame, output, {'units': 'mm/mes'})
        self.assertEqual(summary['period_values'][0]['value'], 30.)
        self.assertEqual(summary['aggregate_units'], 'mm')

    def test_comparison_closing_rejects_missing_or_duplicate_months(self):
        frame = pd.DataFrame([{'year': 2024, 'month': 1, 'value': 10., 'complete': True}])
        output = {'mode': 'nacional', 'area': 'Ecuador', 'years': [2024], 'first_month': 1, 'last_month': 2, 'parameter': 'T2M'}
        with self.assertRaises(ValueError):
            comparison_summary(frame, output, {'units': '°C'})
        with self.assertRaises(ValueError):
            comparison_summary(pd.concat([frame, frame]), output, {'units': '°C'})

    def test_manual_comparison_copy_does_not_restore_rain_factory_labels(self):
        from unittest.mock import patch
        frame = pd.DataFrame([{'year': 2024, 'month': 1, 'value': 15., 'complete': True}])
        output = {'mode': 'nacional', 'area': 'Ecuador', 'years': [2024], 'first_month': 1, 'last_month': 1, 'parameter': 'T2M'}
        with patch('endcard.compose_endcard') as compositor:
            _, summary = render_comparison_endcard(frame, output, {'units': '°C', 'endcard_auto_text': False,
                'endcard_subtitle': 'Mi comparación', 'endcard_copy': {'section_3': 'CÓMO SE CALCULÓ'}})
        project = compositor.call_args.args[0]
        self.assertTrue(project['endcard_auto_text'])
        self.assertEqual(summary['comparison_copy']['subtitle'], 'Mi comparación')
        self.assertEqual(summary['comparison_copy']['section_3'], 'CÓMO SE CALCULÓ')
        self.assertNotIn('CHIRPS v2', summary['comparison_copy']['footer'])

    def test_displayed_precipitation_units_match_temporal_aggregation(self):
        self.assertEqual(display_units("PRECTOTCORR"), "mm/mes")
        self.assertEqual(display_units("PRECTOTCORR", period_total=True), "mm del periodo")
        self.assertEqual(display_units("T2M"), "°C")

    def test_cpc_table_parser_maps_three_month_seasons_to_mid_month(self):
        frame = parse_cpc_index(
            "SEAS YR ANOM\nDJF 2024 1.2\nJFM 2024 1.3\nJAS 2024 0.8\n",
            "ANOM",
        )
        self.assertEqual(frame["date"].dt.month.tolist(), [1, 2, 8])
        self.assertEqual(frame["value"].tolist(), [1.2, 1.3, 0.8])

    def test_partial_year_range_ends_today_without_creating_future_dates(self):
        start, end = year_range(2026, 1, 12, today=dt.date(2026, 9, 30))
        self.assertEqual(start, dt.date(2026, 1, 1))
        self.assertEqual(end, dt.date(2026, 9, 30))

    def test_precipitation_accumulates_and_intensive_variables_average(self):
        transform = from_origin(-80, 2, 1, 1)
        with MemoryFile() as memory:
            with memory.open(driver="GTiff", width=2, height=2, count=3,
                             dtype="float32", crs="EPSG:4326", transform=transform,
                             nodata=-9999) as source:
                source.write(np.array([[1, 3], [5, 7]], dtype="float32"), 1)
                source.write(np.array([[2, 4], [6, 8]], dtype="float32"), 2)
                source.write(np.array([[3, 5], [7, 9]], dtype="float32"), 3)
                rain = _monthly_grid(source, [1, 2, 3], "PRECTOTCORR")
                chirps_rain = _monthly_grid(source, [1, 2, 3], "CHIRPS_PRECTOT")
                temp = _monthly_grid(source, [1, 2, 3], "T2M")
        np.testing.assert_allclose(rain, [[6, 12], [18, 24]])
        np.testing.assert_allclose(chirps_rain, [[6, 12], [18, 24]])
        np.testing.assert_allclose(temp, [[2, 4], [6, 8]])

    def test_monthly_grid_does_not_treat_missing_daily_pixel_as_zero(self):
        with MemoryFile() as memory:
            with memory.open(driver='GTiff', width=2, height=1, count=2, dtype='float32',
                             crs='EPSG:4326', transform=from_origin(-80, 2, 1, 1), nodata=-9999) as source:
                source.write(np.array([[1, 3]], dtype='float32'), 1)
                source.write(np.array([[-9999, 4]], dtype='float32'), 2)
                for parameter, expected in [('PRECTOTCORR', 7), ('T2M', 3.5)]:
                    grid = _monthly_grid(source, [1, 2], parameter)
                    self.assertTrue(np.isnan(grid[0, 0]))
                    self.assertEqual(grid[0, 1], expected)

    def test_current_partial_month_is_not_a_complete_month(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'daily.tif'
            with rasterio.open(target, 'w', driver='GTiff', width=1, height=1, count=7,
                               dtype='float32', crs='EPSG:4326', transform=from_origin(-78, 0, 1, 1)) as source:
                for index in range(1, 8):
                    source.write(np.array([[1.]], dtype='float32'), index)
                    source.set_band_description(index, f'2026-10-{index:02d}')
            with patch('climate_comparison.year_range', return_value=(dt.date(2026, 10, 1), dt.date(2026, 10, 7))), \
                 patch('climate_comparison._stats_for_features', return_value={'Napo': {'mean': 7.}}):
                result = summarize_raster_months(target, 'PRECTOTCORR', 2026, 10, 10, mode='provincia', area='Napo')
            self.assertFalse(result.iloc[0].complete)
            self.assertEqual(result.iloc[0].days_expected, 31)
            self.assertTrue(pd.isna(result.iloc[0].value))

    def test_duplicate_province_month_is_rejected(self):
        row = {'year': 2024, 'month': 1, 'area': 'Napo', 'value': 2.,
               'days_with_data': 31, 'days_expected': 31, 'complete': True}
        with self.assertRaises(ValueError):
            annual_rank([pd.DataFrame([row, row])], 'PRECTOTCORR', years_included=[2024], months_expected=[1])

    def test_period_mean_weights_months_by_number_of_days(self):
        import pandas as pd

        months = pd.DataFrame([
            {"year": 2024, "month": 1, "area": "Napo", "value": 10.0,
             "days_with_data": 31, "days_expected": 31, "complete": True},
            {"year": 2024, "month": 2, "area": "Napo", "value": 20.0,
             "days_with_data": 29, "days_expected": 29, "complete": True},
        ])
        result = annual_rank([months], "T2M", years_included=[2024], months_expected=[1, 2])
        expected = (10 * 31 + 20 * 29) / 60
        napo = result.loc[result.area == "Napo"].iloc[0]
        self.assertAlmostEqual(napo.value, expected)
        self.assertEqual(napo.units, "°C")
        self.assertIn("ponderada", napo.statistic)
        self.assertEqual(result.area.nunique(), 24)

    def test_period_total_refuses_to_sum_incomplete_month_coverage(self):
        import pandas as pd

        months = pd.DataFrame([
            {"year": 2024, "month": 1, "area": "Napo", "value": 10.0,
             "days_with_data": 31, "days_expected": 31, "complete": True},
        ])
        result = annual_rank([months], "PRECTOTCORR", years_included=[2024], months_expected=[1, 2])
        napo = result.loc[result.area == "Napo"].iloc[0]
        self.assertTrue(np.isnan(napo.value))
        self.assertFalse(napo.complete)
        self.assertEqual(napo.months_with_data, 1)

    def test_earth_engine_script_keeps_selected_layers_and_date(self):
        script = ee_climate_script(
            "2024-02-01", show_sst=False, show_anomaly=True, show_wind=False,
            show_air_temp=False, show_rain=False,
        )
        self.assertIn("var day = '2024-02-01';", script)
        self.assertIn("SST_anomaly_C", script)
        self.assertNotIn("ECMWF/ERA5/HOURLY", script)
        self.assertNotIn("Temperatura superficial del mar", script)

    def test_earth_engine_script_can_combine_continental_air_temperature_rain_and_wind(self):
        script = ee_climate_script(
            "2024-02-01", show_sst=False, show_anomaly=False,
            show_wind=True, show_air_temp=True, show_rain=True,
        )
        self.assertIn("UCSB-CHC/CHIRPS/V3/DAILY_RNL", script)
        self.assertIn("temperature_2m", script)
        self.assertIn("u_component_of_wind_10m", script)


if __name__ == "__main__":
    unittest.main()
