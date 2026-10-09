"""Explicit contracts for the integrated editor; no scientific reads."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from studio_editing import new_workspace, edit_scene, patch_canvas, timeline_rows
from studio_templates import template_scene, THEMES
from output_profiles import profile_for


class StudioEditingTests(unittest.TestCase):
    def setUp(self):
        self.original = {'duration': 2, 'endcard_duration': 1, 'visual_layout': {'map': {'a': {'x': 12}}},
                         'unknown': {'keep': True}}
        self.project = new_workspace(self.original)

    def test_workspace_preserves_original_and_legacy_scenes(self):
        self.assertNotIn('studio', self.original)
        self.assertEqual(self.project['visual_layout'], self.original['visual_layout'])
        studio = self.project['studio']
        self.assertEqual(studio['legacy_timeline'], ['legacy.map', 'legacy.endcard'])
        self.assertEqual(len(studio['scenes']), 3)
        self.assertEqual(len(studio['timeline']), 1)
        self.assertEqual(new_workspace(self.project), self.project)

    def test_scene_commands_are_pure_and_duration_is_frame_exact(self):
        first = self.project['studio']['timeline'][0]
        before = copy.deepcopy(self.project)
        duplicate = edit_scene(self.project, 'duplicate', first)
        second = duplicate['studio']['timeline'][1]
        changed = edit_scene(duplicate, 'update', second, name='Contexto', duration=.11)
        self.assertEqual(self.project, before)
        rows = timeline_rows(changed['studio'])
        self.assertEqual(rows[1]['frames'], 3)
        self.assertEqual(rows[1]['name'], 'Contexto')
        reordered = edit_scene(changed, 'reorder', order=[second, first])
        self.assertEqual(reordered['studio']['timeline'], [second, first])
        deleted = edit_scene(reordered, 'delete', second)
        self.assertEqual(deleted['studio']['timeline'], [first])
        with self.assertRaises(ValueError): edit_scene(deleted, 'delete', first)
        with self.assertRaises(ValueError): edit_scene(changed, 'reorder', order=[first])

    def test_mixed_timeline_separation_preserves_all_references_and_data(self):
        free=self.project['studio']['timeline'][0]
        self.project['studio']['timeline']=['legacy.map',free,'legacy.endcard']
        before=copy.deepcopy(self.project)
        separated=edit_scene(self.project,'separate_timeline')
        self.assertEqual(separated['studio']['timeline'],[free])
        self.assertEqual(separated['studio']['legacy_timeline'],['legacy.map','legacy.endcard'])
        for key in ('scenes','calculations','datasets','media'):
            self.assertEqual(separated['studio'][key],before['studio'][key])
        self.assertEqual(self.project,before)
        self.assertEqual(edit_scene(separated,'separate_timeline'),separated)
        self.project['studio']['timeline']=['legacy.map']
        self.assertEqual(edit_scene(self.project,'separate_timeline')['studio']['timeline'],[free])


    def test_canvas_patch_preserves_bindings_and_scientific_registry(self):
        studio = self.project['studio']
        scene = next(s for s in studio['scenes'] if s['id'] == studio['timeline'][0])
        scene['elements'][0]['data_binding'] = {'result_id': 'rain', 'field': 'value'}
        studio['calculations']['rain'] = {'value': 132.4, 'units': 'mm'}
        before = copy.deepcopy(studio['calculations'])
        eid = scene['elements'][0]['id']
        changed = patch_canvas(self.project, scene['id'], {eid: {'x': 50, 'y': 80, 'w': 700, 'h': 100,
                               'font_size': 40, 'color': '#aabbcc', 'name': 'Título', 'text': 'fraude'}})
        element = next(s for s in changed['studio']['scenes'] if s['id'] == scene['id'])['elements'][0]
        self.assertNotEqual(element['style']['text'], 'fraude')
        self.assertEqual(element['data_binding'], scene['elements'][0]['data_binding'])
        self.assertEqual(changed['studio']['calculations'], before)
        self.assertEqual(element['transform']['x'], 50)
        with self.assertRaises(ValueError): patch_canvas(self.project, scene['id'], {'unknown': {'x': 1}})
        with self.assertRaises(ValueError): patch_canvas(self.project, scene['id'], {eid: {'x': float('nan')}})

    def test_locked_elements_reject_changes_and_deleted_are_recoverable(self):
        sid = self.project['studio']['timeline'][0]
        eid = self.project['studio']['scenes'][-1]['elements'][0]['id']
        locked = patch_canvas(self.project, sid, {eid: {'locked': True}})
        with self.assertRaises(ValueError): patch_canvas(locked, sid, {eid: {'x': 1}})
        unlocked = patch_canvas(locked, sid, {eid: {'locked': False}})
        deleted = patch_canvas(unlocked, sid, {eid: {'deleted': True}})
        self.assertTrue(deleted['studio']['scenes'][-1]['elements'][0]['editor_deleted'])
        self.assertFalse(deleted['studio']['scenes'][-1]['elements'][0]['visible'])
        recovered = patch_canvas(deleted, sid, {eid: {'deleted': False, 'hidden': False}})
        self.assertTrue(recovered['studio']['scenes'][-1]['elements'][0]['visible'])

    def test_templates_reflow_and_themes_never_touch_data(self):
        for identifier in ('tiktok', 'instagram_portrait', 'instagram_square', 'youtube'):
            profile = profile_for({'id': identifier})
            for template in ('cover', 'map_metric', 'map_ranking', 'closing', 'blank'):
                for theme in THEMES:
                    scene = template_scene(template, profile, theme=theme,
                        bindings={'metric': {'result_id': 'rain', 'field': 'value'},
                                  'ranking': {'result_id': 'provinces', 'field': 'rows'}})
                    for element in scene['elements']:
                        t = element['transform']
                        self.assertGreater(t['width'], 0)
                        self.assertLessEqual(t['x'] + t['width'], profile.width)
                        self.assertLessEqual(t['y'] + t['height'], profile.height)
        tall = template_scene('map_metric', profile_for({'id': 'tiktok'}))['elements']
        wide = template_scene('map_metric', profile_for({'id': 'youtube'}))['elements']
        self.assertGreater(tall[1]['transform']['height']/tall[1]['transform']['width'],
                           wide[1]['transform']['height']/wide[1]['transform']['width'])


if __name__ == '__main__': unittest.main()
