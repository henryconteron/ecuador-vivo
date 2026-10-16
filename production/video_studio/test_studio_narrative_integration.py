"""One shared global clock for editable resources, narration and subtitles."""
import copy
import hashlib
import unittest

from studio_home import create_project
from studio_model import validate_studio
from studio_timeline import PreparedTimeline, frame_at


class NarrativeIntegrationTests(unittest.TestCase):
    def project(self):
        project = create_project('free', {'id': 'tiktok'})
        scene = next(s for s in project['studio']['scenes'] if s['id'] in project['studio']['timeline'])
        scene['duration'] = 2
        project['studio']['captions'] = {'enabled': True, 'cues': [
            {'id': 'cue.1', 'start': .5, 'end': 1, 'text': 'Un milímetro de lluvia.'}], 'style': {}}
        return project

    def test_captions_share_preview_and_authoring_pixels(self):
        project = self.project()
        before = copy.deepcopy(project)
        with_caption = frame_at(project, 15)
        self.assertEqual(with_caption.tobytes(), PreparedTimeline(project).frame_at(15).tobytes())
        self.assertEqual(with_caption.tobytes(), frame_at(project, 15, authoring=True).tobytes())
        no_caption = copy.deepcopy(project)
        no_caption['studio']['captions']['enabled'] = False
        self.assertNotEqual(hashlib.sha256(with_caption.tobytes()).hexdigest(),
                            hashlib.sha256(frame_at(no_caption, 15).tobytes()).hexdigest())
        self.assertEqual(frame_at(project, 30).tobytes(), frame_at(no_caption, 30).tobytes())
        self.assertEqual(project, before)

    def test_model_rejects_out_of_timeline_subtitle(self):
        project = self.project()
        project['studio']['captions']['cues'][0]['end'] = 3
        with self.assertRaises(ValueError): validate_studio(project['studio'])

    def test_model_rejects_orphan_audio_track(self):
        project = self.project()
        project['studio']['audio_tracks'] = [{'id': 'voice.1', 'asset_id': 'missing'}]
        with self.assertRaises(ValueError): validate_studio(project['studio'])

    def test_cached_canvas_updates_caption_without_creating_editable_scene_element(self):
        from studio_cache import StudioPreviewCache
        from studio_media import AssetFrames
        from studio_ui import canvas_payload
        project = self.project()
        cache = StudioPreviewCache()
        try:
            prepared = cache.prepare(project)
            sid = prepared.rows[0]['id']
            with AssetFrames({}) as assets:
                view = cache.for_timeline(prepared, assets)
                first = view.canvas(sid, canvas_payload, frame=15)
                self.assertIsNotNone(first['caption_overlay'])
                project['studio']['captions']['cues'][0]['text'] = 'Un litro por metro cuadrado.'
                changed = cache.for_timeline(cache.prepare(project), assets).canvas(sid, canvas_payload, frame=15)
                self.assertNotEqual(first['caption_overlay']['src'], changed['caption_overlay']['src'])
                hidden = cache.for_timeline(cache.prepare(project), assets).canvas(sid, canvas_payload, frame=30)
                self.assertIsNone(hidden['caption_overlay'])
                self.assertEqual(first['layers'], changed['layers'])
        finally:
            cache.clear()


if __name__ == '__main__': unittest.main()
