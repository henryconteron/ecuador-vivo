"""Text fit and honest summaries for the reference-inspired social designs."""
import sys
from pathlib import Path
import unittest

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from editorial import comparison_findings, compose_temporal_closing, draw_header, text_box, compose_editorial, editorial_background, editorial_font
from comparison_video import comparison_summary
import pandas as pd


class EditorialTests(unittest.TestCase):
    def summary(self, parameter='T2M', values=(22.4, 22.35, 21.3)):
        output = dict(parameter=parameter, mode='nacional', area='Ecuador',
                      years=[2016, 2024, 2026], first_month=1, last_month=2)
        frame = pd.DataFrame([dict(year=year, month=month, area='Ecuador', value=value, complete=True)
                              for year, value in zip(output['years'], values) for month in (1, 2)])
        summary = comparison_summary(frame, output, {'units': '°C' if parameter == 'T2M' else 'mm/mes'})
        summary['findings'] = comparison_findings(summary)
        return summary

    def assert_fits(self, image):
        for entry in image.info['layout_boxes']:
            x0, y0, x1, y1 = entry['box']
            for left, top, right, bottom in entry['bounds']:
                self.assertGreaterEqual(left, x0-2, entry['text'])
                self.assertGreaterEqual(top, y0-1, entry['text'])
                self.assertLessEqual(right, x1+2, entry['text'])
                self.assertLessEqual(bottom, y1+1, entry['text'])

    def test_scientific_long_headline_has_no_brand_or_subtitle_overlap(self):
        image = Image.new('RGB', (1080, 1920))
        draw_header(image, {'title': '¿Cómo cambió la temperatura media del aire a 2 m?',
                            'subtitle': 'Misma escala · 3 años · Ecuador.'})
        self.assert_fits(image)

    def test_long_credits_and_sources_fit(self):
        summary = self.summary()
        summary['comparison_copy']['footer'] = 'NASA POWER · NASA / MERRA-2 · resolución regional aproximada de 50–60 km; límites geoBoundaries'
        image = compose_temporal_closing({'author': 'Henry P. Conteron Moreta',
                                         'tiktok': '@elgeocientifico', 'instagram': '@henry_conteron'}, summary)
        self.assertEqual(image.size, (1080, 1920))
        self.assert_fits(image)

    def test_findings_use_unrounded_difference_not_a_trend(self):
        summary = self.summary(values=(22.44, 22.4, 21.36))
        findings = comparison_findings(summary)
        self.assertIn('1.1 °C menor', findings[0]['body'])
        self.assertIn('Enero–febrero', findings[1]['body'])
        self.assertIn('NO ES UNA TENDENCIA', findings[2]['title'])
        self.assertNotIn('estabilidad', str(findings).lower())

    def test_rain_and_negative_temperature_fit_and_keep_units(self):
        for parameter, values in [('PRECTOTCORR', (9999., 8888., 4444.)), ('T2M', (-22., 1., -3.))]:
            summary = self.summary(parameter, values)
            image = compose_temporal_closing({}, summary)
            self.assert_fits(image)
            if parameter == 'PRECTOTCORR':
                self.assertEqual(summary['aggregate_units'], 'mm')
                self.assertIn('acumulado', summary['findings'][0]['body'])

    def test_text_box_does_not_drop_long_words(self):
        image = Image.new('RGB', (1080, 1920))
        text_box(image, 'Santo Domingo de los Tsáchilas', (20, 20, 250, 110), size=30, lines=2)
        self.assert_fits(image)

    def test_manual_findings_change_copy_not_calculations(self):
        from comparison_video import render_comparison_endcard
        frame = pd.DataFrame([dict(year=year, month=1, area='Ecuador', value=value, complete=True)
                              for year, value in [(2024, 20.), (2026, 21.)]])
        output = dict(parameter='T2M', mode='nacional', area='Ecuador', years=[2024, 2026], first_month=1, last_month=1)
        image, summary = render_comparison_endcard(frame, output, {'units': '°C', 'endcard_auto_text': False,
            'endcard_findings': [{'title': 'Mi explicación', 'body': 'Un grado más en esta ventana.'}]})
        self.assertEqual(summary['findings'][0]['title'], 'Mi explicación')
        self.assertEqual(summary['period_values'][1]['value'], 21.)
        self.assertTrue(any('texto manual' in text for text in summary['warnings']))
        self.assert_fits(image)

    def test_reference_artwork_is_not_globally_shrunk(self):
        image = editorial_background({})
        image.putpixel((100, 100), (255, 0, 0, 255))
        self.assertEqual(compose_editorial(image, {}).getpixel((100, 100)), (255, 0, 0))
        self.assertNotEqual(compose_editorial(image, {'editorial_margins': 'amplios'}).getpixel((100, 100)), (255, 0, 0))

    def test_bundled_condensed_display_font_is_used(self):
        selected = editorial_font(50, display=True)
        self.assertIn('BarlowCondensed-ExtraBold.ttf', str(selected.path))


if __name__ == '__main__':
    unittest.main()
