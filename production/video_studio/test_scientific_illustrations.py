"""Approved artwork is illustrative, portable, and never changes scientific data."""
import base64
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image


class ScientificIllustrationsTests(unittest.TestCase):
    def test_expedicion_catalog_has_real_previews_and_honest_provenance(self):
        from studio_scientific_library import scientific_objects
        entries = {row['id']: row for row in scientific_objects()}
        for identifier in ('expedicion.andes', 'expedicion.agua'):
            row = entries[identifier]
            self.assertEqual(row['type'], 'asset')
            self.assertEqual(row['collection'], 'expedicion')
            self.assertEqual(row['author'], 'Henry P. Conteron Moreta')
            self.assertNotEqual(row['license'], 'CC0')
            self.assertEqual(row['generated_by'], 'OpenAI image_gen')
            self.assertFalse(row['observational_data'])
            self.assertIn('conceptual', row['summary'])
            prefix, data = row['preview'].split(',', 1)
            self.assertEqual(prefix, 'data:image/webp;base64')
            with Image.open(io.BytesIO(base64.b64decode(data))) as image:
                self.assertGreater(image.width, 500)
        with Image.open(io.BytesIO(base64.b64decode(entries['expedicion.agua']['preview'].split(',', 1)[1]))) as image:
            self.assertIn('A', image.getbands())
            self.assertEqual(image.getchannel('A').getextrema()[0], 0)

    def test_insert_is_editable_image_and_keeps_canonical_video_unchanged(self):
        from studio_scientific_library import insert_bioicon
        from studio_home import create_project
        from studio_resource_workbench import resource_draft
        from studio_resource_projects import resource_from_scene, insert_saved_resource
        from studio_model import validate_studio
        video = create_project('free', {'id': 'tiktok'}, name='Mi vídeo')
        before_video = copy.deepcopy(video)
        draft = resource_draft({}, video)
        before_draft = copy.deepcopy(draft)
        scene_id = draft['studio']['timeline'][0]
        with tempfile.TemporaryDirectory() as folder, patch('storyboard.MEDIA_ROOT', Path(folder)):
            edited = insert_bioicon(draft, scene_id, 'expedicion.agua')
            self.assertEqual(video, before_video)
            self.assertEqual(draft, before_draft)
            element = edited['studio']['scenes'][0]['elements'][-1]
            self.assertEqual(element['type'], 'image')
            self.assertGreater(element['transform']['width'], 0)
            self.assertFalse(element.get('data_binding'))
            self.assertFalse(element['scientific_provenance']['observational_data'])
            self.assertEqual(element['scientific_provenance']['generated_by'], 'OpenAI image_gen')
            resource = resource_from_scene(edited, scene_id, 'Cuenca ilustrada')
            target = insert_saved_resource(video, resource)
            validate_studio(json.loads(json.dumps(target))['studio'])
            self.assertEqual(video, before_video)
            self.assertEqual(target['studio']['calculations'], video['studio']['calculations'])
            self.assertEqual(target['studio']['scenes'][-1]['elements'][-1]['scientific_provenance'],
                             element['scientific_provenance'])

    def test_unknown_and_tampered_artwork_are_rejected_before_import(self):
        from studio_scientific_library import insert_bioicon, scientific_objects
        from studio_resource_projects import create_resource_project
        project = create_resource_project('Figura', {'id': 'youtube'})
        scene_id = project['studio']['timeline'][0]
        with patch('studio_media.import_asset') as imported:
            with self.assertRaises(ValueError):
                insert_bioicon(project, scene_id, 'unknown')
            row = next(row for row in scientific_objects() if row['id'] == 'expedicion.agua')
            with patch('studio_scientific_library.scientific_objects', return_value=[{**row, 'sha256': '0' * 64}]):
                with self.assertRaises(ValueError):
                    insert_bioicon(project, scene_id, row['id'])
            self.assertFalse(imported.called)

    def test_new_webp_art_and_existing_bioicons_render_through_the_same_pipeline(self):
        from studio_scientific_library import insert_bioicon, scientific_objects
        from studio_resource_projects import create_resource_project
        from studio_timeline import PreparedTimeline
        existing = next(row['id'] for row in scientific_objects() if row.get('collection') == 'bioicons')
        with tempfile.TemporaryDirectory() as folder, patch('storyboard.MEDIA_ROOT', Path(folder)):
            for preset in ('tiktok', 'youtube'):
                for identifier in ('expedicion.andes', 'expedicion.agua', existing):
                    with self.subTest(preset=preset, identifier=identifier):
                        project = create_resource_project('Figura', {'id': preset})
                        edited = insert_bioicon(project, project['studio']['timeline'][0], identifier)
                        frame = PreparedTimeline(edited, preview_max_side=280).frame_at(0)
                        self.assertEqual(max(frame.size), 280)
                        # Existing monochrome line icons legitimately have few
                        # colors; every asset still has visible nonblank detail.
                        minimum = 100 if identifier.startswith('expedicion.') else 10
                        self.assertGreater(len(frame.getcolors(frame.width * frame.height)), minimum)
                        frame.close()

    def test_catalog_paths_cannot_leave_their_explicit_collection(self):
        from studio_scientific_library import _catalog_assets
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'catalog'
            root.mkdir()
            outside = Path(folder) / 'outside.webp'
            outside.write_bytes(b'not an image')
            catalog = {'items': [{'id': 'escape', 'type': 'asset', 'original': '../outside.webp',
                                  'image': '../outside.webp',
                                  'sha256': hashlib.sha256(outside.read_bytes()).hexdigest()}]}
            (root / 'catalog.json').write_text(json.dumps(catalog), encoding='utf8')
            self.assertEqual(_catalog_assets(root, 'test'), [])


if __name__ == '__main__':
    unittest.main()
