"""Satellite provenance, old identity, editorial scope and actual timing checks."""
from hashlib import sha256
import json
import unittest
import numpy as np
from PIL import Image
import reel_river_satellite_story as story

class SatelliteStoryTests(unittest.TestCase):
    def test_case_and_method_scope(self):
        ids=[b[0] for b in story.BEATS]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(ids[:3],['docepair','doceevent','docestudy'])
        words=' '.join(b[1] for b in story.BEATS)
        for value in ('Landsat','Fundão','Rudorff','rojo e infrarrojo cercano','mediciones de caudal y turbidez','No son la misma herramienta','No trasladamos esa conclusión al Jatunyacu'):
            self.assertIn(value,words)
        self.assertNotIn('Colorado',words)
        self.assertNotIn('Nilo',words)
        self.assertNotIn('sin tocar el campo',words)

    def test_both_real_panels_are_visible(self):
        d=story.Design()
        with Image.open(story.FOLDER/'sources/Brazil-Dam2.jpg') as source:
            for i,tag in enumerate(('before','after')):
                expected=source.crop(story.CROPS[tag]).convert('RGB').resize((960,540),Image.Resampling.LANCZOS)
                self.assertEqual(expected.tobytes(),d.dope[tag].tobytes())
                # Test an unobstructed region of BOTH panels in every opening shot.
                for beat in story.BEATS[:3]:
                    y=285+i*580
                    observed=d.render(beat,.2).crop((60,y+65,460,y+230))
                    self.assertEqual(observed.tobytes(),expected.crop((0,65,400,230)).tobytes())

    def test_native_data_and_layout(self):
        d=story.Design()
        self.assertEqual(d.native.size,d.values.shape[::-1])
        self.assertEqual(int(story.motion.candidates(d.values,d.common,0).sum()),947)
        self.assertEqual(int(story.motion.candidates(d.values,d.common,.2).sum()),681)
        for beat in story.BEATS:
            for t in (0,.4,1):
                self.assertEqual(d.render(beat,t,'Las dos imágenes son observaciones reales.').size,(1080,1920))
        for sid in ('docepair','sedimentlight','twoquestions','response','contrast','rulemove','zoom','levelv9','middle','time'):
            beat=next(b for b in story.BEATS if b[0]==sid)
            self.assertNotEqual(d.render(beat,.1).tobytes(),d.render(beat,.8).tobytes())

    def test_voice_and_previous_modules_unchanged(self):
        old_folder,old_beats=story.previous.FOLDER,story.previous.BEATS
        scenes=story.plan()
        self.assertEqual(story.previous.FOLDER,old_folder)
        self.assertIs(story.previous.BEATS,old_beats)
        d=story.Design()
        cursor=0
        for beat,scene in zip(story.BEATS,scenes):
            self.assertEqual(scene['start_frame'],cursor)
            self.assertGreater(scene['frames']/story.FPS,scene['audio_seconds'])
            timing=json.loads((story.FOLDER/f'times_{beat[0]}.json').read_text(encoding='utf-8'))
            self.assertGreaterEqual(len(timing['words']),len(beat[1].split())*.85)
            for cue in scene['cues']:
                d.render(beat,.6,cue['text'])
                self.assertLessEqual(cue['end'],scene['frames']/story.FPS)
            cursor+=scene['frames']

    def test_sources_and_previous_renders(self):
        m=json.loads((story.FOLDER/'sources_manifest.json').read_text(encoding='utf-8'))
        self.assertTrue(m['satellite_only'])
        self.assertEqual(m['images'][0]['dates'],['2015-09-11','2015-11-30'])
        for path,digest in m['previous_renders'].items():
            self.assertEqual(sha256(story.Path(path).read_bytes()).hexdigest(),digest)

if __name__=='__main__':unittest.main()
