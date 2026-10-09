"""Additive project contracts, independent of Streamlit or network access."""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from studio_model import migrate_project, validate_studio, Element, Scene, DataBinding
from model import default_project, validate


class StudioModelTests(unittest.TestCase):
    def test_legacy_export_rejects_free_scenes_instead_of_silently_ignoring_them(self):
        migrated = migrate_project(default_project())
        validate(copy.deepcopy(migrated))
        migrated['studio']['scenes'] = [Scene(id='free', elements=[
            Element(id='e',type='text',style={'text':'Debe salir en el video'})]).to_dict()]
        migrated['studio']['timeline'] = ['free']
        before = copy.deepcopy(migrated)
        with self.assertRaisesRegex(ValueError,'Studio'):
            validate(migrated)
        self.assertEqual(migrated,before)

    def test_legacy_export_cannot_ignore_changed_studio_timing_or_order(self):
        migrated=migrate_project(default_project())
        for change in (lambda model:model['timeline'].reverse(),
                       lambda model:model['scenes'][0].update(duration=3)):
            candidate=copy.deepcopy(migrated)
            change(candidate['studio'])
            before=copy.deepcopy(candidate)
            with self.assertRaisesRegex(ValueError,'Studio'): validate(candidate)
            self.assertEqual(candidate,before)

    def test_invalid_timeline_items_raise_validation_error(self):
        studio = migrate_project(default_project())['studio']
        for invalid in ([{'scene':'legacy.map'}], [None], [[]]):
            candidate = copy.deepcopy(studio)
            candidate['timeline'] = invalid
            with self.assertRaises(ValueError): validate_studio(candidate)

    def test_migration_preserves_every_legacy_and_unknown_field_without_mutation(self):
        original = default_project()
        original.update(visual_layout={'map': {'custom.a': {'x': 37, 'text': 'Mi diseño'}}},
                        map={'my': ['extension']}, scenes={'custom': 'older extension'},
                        delivery={'format': 'Cuadrado · publicaciones · 1:1'},
                        calculations=['legacy extension'], extra={'nested': [1]})
        before = copy.deepcopy(original)
        migrated = migrate_project(original)
        self.assertEqual(original, before)
        for key, value in before.items():
            self.assertEqual(migrated[key], value)
        self.assertEqual(migrated['schema_version'], 1)
        migrated['extra']['nested'].append(2)
        self.assertEqual(original['extra']['nested'], [1])

    def test_migration_is_deterministic_idempotent_and_json_roundtrips(self):
        original = default_project()
        first = migrate_project(original)
        self.assertEqual(first, migrate_project(original))
        self.assertEqual(first, migrate_project(first))
        self.assertEqual(first, json.loads(json.dumps(first)))

    def test_legacy_scenes_reproduce_storyboard_order_and_frame_exact_durations(self):
        original = default_project()
        original['storyboard'] = {'enabled': True, 'cards': [
            {'id': 'intro', 'kind': 'text', 'duration': 2},
            {'id': 'm', 'kind': 'map', 'duration': 10},
            {'id': 'e', 'kind': 'endcard', 'duration': 3}]}
        migrated = migrate_project(original)['studio']
        self.assertEqual(migrated['timeline'], ['legacy.intro', 'legacy.m', 'legacy.e'])
        self.assertEqual(sum(scene['duration'] for scene in migrated['scenes']), 15)
        self.assertTrue(all(scene['renderer'] == 'legacy' for scene in migrated['scenes']))
        self.assertTrue(all(not scene['elements'] for scene in migrated['scenes']))

    def test_versions_are_strict_and_future_schema_rejected_before_upgrade(self):
        for version in (2, True, 1.5, '1', None):
            original = default_project()
            original['schema_version'] = version
            before = copy.deepcopy(original)
            with self.assertRaises(ValueError):
                migrate_project(original)
            with self.assertRaises(ValueError):
                validate(original)
            self.assertEqual(original, before)

    def test_partial_or_unknown_studio_namespace_is_rejected_without_overwrite(self):
        for namespace in ({'custom_extension': [1]}, {'scenes': []},
                          {'timeline': []}, None):
            original = default_project()
            original['studio'] = namespace
            before = copy.deepcopy(original)
            with self.assertRaises(ValueError):
                migrate_project(original)
            self.assertEqual(original, before)

    def test_scene_and_element_contracts_support_editable_independent_styles(self):
        element = Element(id='title', type='text', name='Título',
                          transform={'x': 20, 'y': 30, 'width': 300, 'height': 80},
                          style={'text': 'Una historia', 'color': '#ffffff'})
        scene = Scene(id='intro', name='Portada', duration=2, elements=[element])
        payload = scene.to_dict()
        self.assertEqual(payload['elements'][0]['transform']['x'], 20)
        self.assertEqual(payload['elements'][0]['type'], 'text')
        self.assertEqual(payload['renderer'], 'studio')

    def test_invalid_geometry_animation_or_bindings_do_not_execute_expressions(self):
        for transform in ({'width': -1}, {'x': float('nan')}, {'rotation': float('inf')}):
            with self.assertRaises(ValueError):
                Element(id='e', type='text', transform=transform).to_dict()
        for field in ('__import__("os")', '../../file', 'a.b', '{{eval}}'):
            with self.assertRaises(ValueError):
                DataBinding(result_id='r', field=field).to_dict()

    def test_references_duplicates_and_legacy_content_are_rejected(self):
        migrated = migrate_project(default_project())
        for mutate in (
            lambda s: s['timeline'].append('missing'),
            lambda s: s['scenes'].append(copy.deepcopy(s['scenes'][0])),
            lambda s: s['scenes'][0]['elements'].append(Element(id='e', type='text').to_dict()),
        ):
            invalid = copy.deepcopy(migrated['studio'])
            mutate(invalid)
            with self.assertRaises(ValueError):
                validate_studio(invalid)

    def test_editing_a_design_does_not_change_calculations_or_datasets(self):
        migrated = migrate_project(default_project())
        studio = migrated['studio']
        studio['calculations'] = {'rain': {'value': 132.4, 'units': 'mm'}}
        studio['datasets'] = {'chirps': {'sha256': 'original'}}
        binding = DataBinding(result_id='rain', field='value').to_dict()
        studio['scenes'] = [Scene(id='s', duration=2, elements=[
            Element(id='kpi', type='metric', data_binding=binding)]).to_dict()]
        studio['timeline'] = ['s']
        before = copy.deepcopy((studio['calculations'], studio['datasets']))
        studio['scenes'][0]['elements'][0]['transform']['x'] = 100
        studio['scenes'][0]['elements'][0]['style'] = {'color': '#ff0000'}
        validate_studio(studio)
        self.assertEqual((studio['calculations'], studio['datasets']), before)
        studio['scenes'][0]['elements'][0]['data_binding']['result_id'] = 'missing'
        with self.assertRaises(ValueError):
            validate_studio(studio)


if __name__ == '__main__':
    unittest.main()
