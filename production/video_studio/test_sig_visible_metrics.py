"""SIG publication must expose scientific values and their meaning in pixels.

Only synthetic immutable revisions are used. Presentation must not read rasters.
"""
import base64
import copy
import io
import unittest
from unittest.mock import patch

from PIL import Image, ImageChops

from output_profiles import profile_for
from studio_editing import snapshot_revision
from studio_home import create_project
from studio_preparation import create_from_review
from studio_render import render_scene
from studio_science import generate_scientific_project
from studio_sig import merge_scientific_proposal
from studio_templates import template_scene
from studio_timeline import PreparedTimeline
from studio_ui import canvas_payload
from test_studio_science import scientific_fixture
from visualizations import VisualizationSpec, visualization_geometry


class SigVisibleMetricsTests(unittest.TestCase):
    def test_valid_numeric_value_and_units_reach_render_canvas_and_preview_pixels(self):
        source, snapshot = scientific_fixture()
        original = copy.deepcopy((source, snapshot))
        profile = profile_for({'id': 'youtube'})
        with patch('data.load_values', side_effect=AssertionError('Presentation read a raster')):
            proposal = generate_scientific_project(source, snapshot, {'id': 'youtube'})
            project, _ = merge_scientific_proposal(create_project('free', {'id': 'youtube'}), proposal)
            scene = next(s for s in project['studio']['scenes']
                         if s.get('generation', {}).get('role') == 'metric')
            metric = next(e for e in scene['elements'] if e['type'] == 'metric')
            registry = project['studio']['calculations']
            rid = metric['data_binding']['result_id']
            self.assertEqual(registry[rid]['value'], 3.)
            self.assertEqual(registry[rid]['units'], 'mm/day')
            self.assertTrue(metric['visible'])
            self.assertGreater(scene['duration'], 0)
            spec = VisualizationSpec(binding=metric['data_binding'], **metric['style']['visualization'])
            box = metric['transform']
            size = (box['width'], box['height'])
            geometry = visualization_geometry(spec, registry, size)
            self.assertEqual(geometry['value_label'], '3 mm/day')
            self.assertEqual(geometry['value'], 3.)

            image = render_scene(scene, profile, registry)
            tile = next(row['image'] for row in image.info['visual_scene'].items if row['id'] == metric['id'])
            # The central band contains the numeral and unit, excluding the
            # title. Foreground must exist there; a layer name proves nothing.
            center = (0, round(size[1]*.3), size[0], round(size[1]*.7))
            plain = Image.new('RGB', tile.size, scene['background'])
            self.assertIsNotNone(ImageChops.difference(tile.convert('RGB'), plain).crop(center).getbbox())
            for field, replacement in (('value', 42.75), ('units', 'kg/m²')):
                modified = copy.deepcopy(registry)
                modified[rid][field] = replacement
                variant = render_scene(scene, profile, modified)
                changed = next(r['image'] for r in variant.info['visual_scene'].items if r['id'] == metric['id'])
                self.assertIsNotNone(ImageChops.difference(tile.convert('RGB'), changed.convert('RGB')).crop(center).getbbox(),
                                     'The painted numeral/unit must respond to its bound value, not just its title.')

            payload = canvas_payload(image, scene, profile)
            layer = next(r for r in payload['layers'] if r['id'] == metric['id'])
            self.assertFalse(layer['hidden'])
            self.assertFalse(layer['deleted'])
            with Image.open(io.BytesIO(base64.b64decode(layer['src'].split(',', 1)[1]))) as decoded:
                self.assertEqual(decoded.convert('RGBA').tobytes(), tile.convert('RGBA').tobytes())
            prepared = PreparedTimeline(project)
            row = next(r for r in prepared.rows if r['id'] == scene['id'])
            self.assertEqual(prepared.frame_at(row['start_frame']).tobytes(), image.tobytes())
        self.assertEqual((source, snapshot), original)

    def test_null_metric_renders_sin_datos_and_never_a_zero(self):
        registry = {'missing': {'id': 'missing', 'value': None, 'units': 'mm',
                                'variable': 'Rain', 'provenance': {'fixture': True}}}
        profile = profile_for({'id': 'youtube'})
        scene = template_scene('metric_focus', profile,
                               bindings={'metric': {'result_id': 'missing', 'field': 'value'}})
        element = next(e for e in scene['elements'] if e['type'] == 'metric')
        spec = VisualizationSpec(binding=element['data_binding'], **element['style']['visualization'])
        size = (element['transform']['width'], element['transform']['height'])
        self.assertEqual(visualization_geometry(spec, registry, size)['value_label'], 'Sin datos')
        missing = render_scene(scene, profile, registry)
        zero = copy.deepcopy(registry); zero['missing']['value'] = 0.
        zero_image = render_scene(scene, profile, zero)
        box = element['transform']
        center = (box['x'], round(box['y']+box['height']*.3),
                  box['x']+box['width'], round(box['y']+box['height']*.7))
        self.assertIsNotNone(ImageChops.difference(missing.convert('RGB'), zero_image.convert('RGB')).crop(center).getbbox())
        self.assertIsNone(registry['missing']['value'])

    def test_selection_without_any_valid_result_is_rejected_before_publication(self):
        source, snapshot = scientific_fixture()
        review = {'source': source, 'snapshot': snapshot, 'revision': snapshot_revision(snapshot)}
        original = copy.deepcopy(review)
        with patch('studio_preparation.verify_sources'), patch('data.load_values', side_effect=AssertionError('Presentation recalculated')):
            with self.assertRaisesRegex(ValueError, r'(?i)(sin datos|ausent|válid|valor|disponible)'):
                create_from_review(review, {'id': 'youtube'}, selected=['missing'])
        self.assertEqual(review, original)

    def test_metric_scene_titles_distinguish_period_mean_from_pixel_peak(self):
        source, snapshot = scientific_fixture()
        mean = copy.deepcopy(snapshot['results']['mean']); mean['id'] = 'mean_period'
        peak = copy.deepcopy(mean); peak['id'] = 'peak_pixel_value'; peak['value'] = 17.
        snapshot['results'] = {'mean_period': mean, 'peak_pixel_value': peak}
        original = copy.deepcopy(snapshot)
        project = generate_scientific_project(source, snapshot, {'id': 'youtube'})
        scenes = [s for s in project['studio']['scenes'] if s.get('generation', {}).get('role') == 'metric']
        self.assertEqual(len(scenes), 2)
        titles = [next(e['style']['text'] for e in s['elements'] if e['id'] == 'title') for s in scenes]
        self.assertNotEqual(titles[0], titles[1],
                            'Mean over the period and peak pixel require distinct visible scientific meanings.')
        self.assertTrue(all('Rain' in title for title in titles))
        self.assertEqual(snapshot, original)


if __name__ == '__main__':
    unittest.main()
