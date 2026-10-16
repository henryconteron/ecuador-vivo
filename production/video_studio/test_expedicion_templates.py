"""Editable scientific explanations stay in Studio and outside data registries."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


class ExpeditionTemplateTests(unittest.TestCase):
    def test_small_custom_canvas_does_not_break_the_template_library(self):
        from studio_expedicion_templates import illustrated_templates
        self.assertEqual(illustrated_templates({'id':'custom','width':160,'height':160}),[])

    def test_template_is_in_the_scientific_library_with_real_preview_and_source(self):
        from studio_scientific_library import scientific_templates
        entry = next(row for row in scientific_templates({'id': 'tiktok'})
                     if row['id'] == 'expedition.water_cycle')
        self.assertEqual(entry['name'], 'Expedición · Ciclo del agua')
        self.assertTrue(entry['preview'].startswith('data:image/png;base64,'))
        self.assertEqual(entry['sources'][0]['url'],
                         'https://www.usgs.gov/special-topics/water-science-school/water-cycle')
        self.assertIn('conceptual', entry['note'])

    def test_image_labels_arrows_sources_and_credits_remain_independent_elements(self):
        from studio_expedicion_templates import create_scientific_template
        from studio_model import validate_studio
        with tempfile.TemporaryDirectory() as folder, patch('storyboard.MEDIA_ROOT', Path(folder)):
            for preset in ('tiktok', 'youtube'):
                project = create_scientific_template('expedition.water_cycle', {'id': preset})
                validate_studio(json.loads(json.dumps(project))['studio'])
                scene = project['studio']['scenes'][0]
                self.assertTrue(scene['resource']['illustrative'])
                self.assertEqual(scene['resource']['id'], 'expedition.water_cycle')
                self.assertEqual(sum(e['type'] == 'image' for e in scene['elements']), 1)
                self.assertEqual(sum(e.get('resource_role', '').endswith('_arrow_shaft')
                                     for e in scene['elements']), 5)
                content = ' '.join(e['style'].get('text', '') for e in scene['elements'])
                for value in ('Condensación', 'Precipitación', 'Evapotranspiración',
                              'Escorrentía', 'Infiltración', 'Henry P. Conteron Moreta',
                              'Ilustración conceptual', 'USGS'):
                    self.assertIn(value, content)
                self.assertTrue(all(not e['locked'] for e in scene['elements']))
                self.assertTrue(all(not e.get('data_binding') and not e.get('temporal_binding')
                                    for e in scene['elements']))
                self.assertEqual(project['studio']['calculations'], {})

    def test_default_only_affects_new_resource_drafts_not_existing_or_canonical_video(self):
        from studio_resource_workbench import resource_draft, RESOURCE_KEY
        from studio_home import create_project
        from studio_resource_projects import create_resource_project
        video = create_project('free', {'id': 'tiktok'}, name='Mi vídeo')
        before = copy.deepcopy(video)
        old = create_resource_project('Mi explicación', {'id': 'youtube'}, resource_id='rain_volume')
        state = {RESOURCE_KEY + '_source': old}
        self.assertIs(resource_draft(state, video), old)
        with tempfile.TemporaryDirectory() as folder, patch('storyboard.MEDIA_ROOT', Path(folder)):
            fresh = resource_draft({}, video)
            self.assertEqual(fresh['studio']['scenes'][0]['resource']['id'], 'expedition.water_cycle')
            supplied = resource_draft({}, old)
            self.assertEqual(supplied, old)
            self.assertIsNot(supplied, old)
        self.assertEqual(video, before)

    def test_explicit_template_open_uses_existing_command_and_does_not_change_video(self):
        from studio_resource_workbench import resource_draft, resource_command
        from studio_workspace import WorkspaceSession
        from studio_home import create_project
        video = create_project('free', {'id': 'tiktok'}, name='Mi vídeo')
        before = copy.deepcopy(video)
        with tempfile.TemporaryDirectory() as folder, patch('storyboard.MEDIA_ROOT', Path(folder) / 'media'):
            state = {'project_document': video}
            session = WorkspaceSession(state, 'resources', resource_draft(state, video), store=folder)
            resource_command(session, {'action': 'resource_open', 'resource_id': 'expedition.water_cycle',
                                      'version': session.version, 'scene': session.selected})
            self.assertEqual(session.project['studio']['scenes'][0]['resource']['id'], 'expedition.water_cycle')
            self.assertEqual(video, before)

    def test_both_video_formats_render_real_art_and_all_editable_objects_fit(self):
        from studio_expedicion_templates import create_scientific_template
        from studio_timeline import PreparedTimeline
        from output_profiles import profile_for
        with tempfile.TemporaryDirectory() as folder, patch('storyboard.MEDIA_ROOT', Path(folder)):
            for preset in ('tiktok', 'youtube'):
                project = create_scientific_template('expedition.water_cycle', {'id': preset})
                profile = profile_for({'id': preset})
                for element in project['studio']['scenes'][0]['elements']:
                    box = element['transform']
                    self.assertGreaterEqual(box['x'], 0)
                    self.assertGreaterEqual(box['y'], 0)
                    self.assertLessEqual(box['x'] + box['width'], profile.width)
                    self.assertLessEqual(box['y'] + box['height'], profile.height)
                image = PreparedTimeline(project, preview_max_side=600).frame_at(90)
                self.assertEqual(max(image.size), 600)
                self.assertGreater(len(image.getcolors(image.width * image.height)), 1000)
                image.close()


if __name__ == '__main__':
    unittest.main()
