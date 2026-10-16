"""Reusable explanatory scenes share the normal Studio document and renderer."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parent))
from studio_home import create_project
from studio_model import Element, validate_studio
from studio_resource_projects import (create_resource_project, insert_saved_resource,
                                      resource_files, resource_from_scene)


class ResourceProjectTests(unittest.TestCase):
    def test_blank_and_template_are_normal_single_scene_studio_projects(self):
        blank = create_resource_project('Mi explicación', {'id': 'tiktok'})
        template = create_resource_project('Lluvia', {'id': 'youtube'}, resource_id='rain_volume')
        for project in (blank, template):
            validate_studio(project['studio'])
            self.assertEqual(len(project['studio']['timeline']), 1)
            self.assertEqual(len(project['studio']['scenes']), 1)
            self.assertEqual(project['project_meta']['resource']['version'], 1)
        self.assertNotEqual(blank['project_meta']['id'], template['project_meta']['id'])
        self.assertEqual(template['studio']['scenes'][0]['resource']['id'], 'rain_volume')

    def test_capture_copies_only_selected_scene_without_audio_captions_or_science(self):
        source = create_resource_project('Origen', {'id': 'tiktok'}, resource_id='rain_volume')
        source['studio']['datasets'] = {'private': {'value': 99}}
        source['studio']['calculations'] = {'private': {'value': 99}}
        source['studio']['captions'] = {'enabled': False, 'cues': []}
        source['studio']['audio_tracks'] = []
        before = copy.deepcopy(source)
        result = resource_from_scene(source, source['studio']['timeline'][0], 'Reutilizable')
        self.assertEqual(source, before)
        self.assertEqual(result['studio']['datasets'], {})
        self.assertEqual(result['studio']['calculations'], {})
        self.assertNotIn('captions', result['studio'])
        self.assertNotIn('audio_tracks', result['studio'])
        self.assertNotEqual(result['project_meta']['id'], source['project_meta']['id'])
        self.assertEqual(result['name'], 'Reutilizable')

    def test_scientific_maps_are_not_silently_decoupled_from_their_data(self):
        project = create_resource_project('Origen', {'id': 'tiktok'})
        project['studio']['scenes'][0]['elements'].append(Element(id='test.map', type='map').to_dict())
        with self.assertRaisesRegex(ValueError, 'científicos'):
            resource_from_scene(project, project['studio']['timeline'][0], 'No es una ilustración')

    def test_insert_preserves_original_and_global_narration(self):
        target = create_project('free', {'id': 'youtube'}, name='Video')
        target['studio']['captions'] = {'enabled': False, 'cues': []}
        target['studio']['audio_tracks'] = []
        before = copy.deepcopy(target)
        resource = create_resource_project('Lluvia', {'id': 'tiktok'}, resource_id='rain_volume')
        result = insert_saved_resource(target, resource)
        validate_studio(result['studio'])
        self.assertEqual(target, before)
        self.assertEqual(result['studio']['timeline'][:-1], before['studio']['timeline'])
        self.assertEqual(result['studio']['audio_tracks'], before['studio']['audio_tracks'])
        self.assertEqual(result['studio']['captions'], before['studio']['captions'])
        self.assertEqual(result['studio']['output_profile'], {'id': 'youtube'})
        self.assertNotEqual(result['studio']['scenes'][-1]['id'], resource['studio']['scenes'][0]['id'])
        for element in result['studio']['scenes'][-1]['elements']:
            box = element['transform']
            self.assertGreaterEqual(box['x'], 0)
            self.assertLessEqual(box['x'] + box['width'], 1920)
            self.assertLessEqual(box['y'] + box['height'], 1080)

    def test_catalog_only_reads_tagged_files_and_ignores_backups_or_broken_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'projects'
            root.mkdir()
            resource = create_resource_project('Mi recurso', {'id': 'tiktok'})
            (root / 'recurso.json').write_text(json.dumps(resource), encoding='utf-8')
            (root / 'recurso.previous.json').write_text(json.dumps(resource), encoding='utf-8')
            (root / 'video.json').write_text(json.dumps(create_project('free', {'id': 'youtube'})), encoding='utf-8')
            (root / 'roto.json').write_text('{', encoding='utf-8')
            entries = resource_files(folder)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]['name'], 'Mi recurso')
            self.assertEqual(Path(entries[0]['path']).name, 'recurso.json')


if __name__ == '__main__':
    unittest.main()
