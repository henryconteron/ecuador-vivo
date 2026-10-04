import json
import unittest
import wave
from hashlib import sha256
from PIL import ImageChops
from prepare_depth_story_v4 import V4
from reel_depth_damage_v4 import SCRIPT, AUDIO, NAMES, FPS, narration_parts, timeline_for, DepthDesignV4
from depth_story_3d import render_source, render_relocation, render_piedmont_orbit, camera_point


class RealCasesStoryTests(unittest.TestCase):
    def test_original_opening_and_complete_script(self):
        old=SCRIPT.parent.parent/'guion_elevenlabs_v2.txt'
        self.assertEqual(narration_parts()['pregunta'],old.read_text(encoding='utf-8').strip().split('\n\n')[0])
        self.assertEqual(list(narration_parts()),list(NAMES))
        self.assertIn('Profundo no significa inofensivo.',narration_parts()['bolivia'])

    def test_primary_solutions_not_mixed_or_historical_precision_invented(self):
        audit=json.loads((V4/'source_audit_v4.json').read_text(encoding='utf-8'))
        cases=audit['cases']
        self.assertEqual(cases['bolivia']['depth_km'],631.3)
        self.assertEqual(cases['loreto']['depth_km'],135)
        self.assertEqual((cases['loreto']['longitude'],cases['loreto']['latitude']),(-75.55,-5.74))
        self.assertIsNone(cases['pelileo']['depth_km'])
        self.assertEqual(cases['pelileo']['depth_upper_exclusive_km'],15)
        self.assertEqual(audit['additional_cases_outside_original_selection'],['bolivia','loreto'])

    def test_audio_never_cut_and_frame_aligned(self):
        scenes=timeline_for(dict.fromkeys(NAMES,25))
        for start,end,_ in scenes:
            self.assertGreaterEqual(end-start,26.15-1e-8)
            self.assertAlmostEqual(start*FPS,round(start*FPS))
            self.assertAlmostEqual(end*FPS,round(end*FPS))
        self.assertTrue(all(a[1]==b[0] for a,b in zip(scenes,scenes[1:])))

    def test_3d_actual_motion_not_progress_or_text(self):
        for depth in (20.59,135,631.3):
            a=render_source(depth,3).crop((70,105,810,590))
            b=render_source(depth,3+1/FPS).crop((70,105,810,590))
            self.assertIsNotNone(ImageChops.difference(a,b).getbbox())
        for fn,a,b in [(render_relocation,3,3+1/FPS),(render_piedmont_orbit,.5,.502),(render_piedmont_orbit,.93,.932)]:
            self.assertIsNotNone(ImageChops.difference(fn(a).crop((20,130,820,580)),fn(b).crop((20,130,820,580))).getbbox())

    def test_depth_order_same_camera_and_no_negative_depth(self):
        for seconds in (0,6,12,25):
            ys=[camera_point(0,0,z,seconds)[1] for z in (0,20.59,135,631.3,700)]
            self.assertEqual(ys,sorted(ys))

    def test_scene_boundaries_fit_and_sources_match_hashes(self):
        manifest=json.loads((AUDIO/'timeline.json').read_text(encoding='utf-8'))
        design=DepthDesignV4(manifest['scenes'],manifest.get('cues'))
        for a,b,name in design.scenes:
            for t in (a,(a+b)/2,b-1/FPS): self.assertEqual(design.render(t).size,(1080,1920),name)
        self.assertEqual(manifest['script_sha256'],sha256(SCRIPT.read_bytes()).hexdigest())
        for part in manifest['segments']:
            self.assertEqual(sha256((AUDIO/part['file']).read_bytes()).hexdigest(),part['sha256'])
            self.assertLess(part['speech_start']+part['speech_seconds'],part['end']-.79)

    def test_reported_intensity_scales_kept_distinct(self):
        parts=narration_parts()
        self.assertIn('Mercalli Modificada',parts['loreto'])
        self.assertIn('informe preliminar',parts['sentido'])
        self.assertIn('escala europea',parts['sentido'])

    def test_word_cues_are_real_and_within_speech(self):
        manifest=json.loads((AUDIO/'timeline.json').read_text(encoding='utf-8'))
        for scene,cues in manifest['cues'].items():
            segment=next(p for p in manifest['segments'] if p['scene']==scene)
            for cue in cues.values(): self.assertTrue(.35<=cue<=segment['speech_seconds']+.35)
        self.assertLess(manifest['cues']['pedernales']['El Instituto'],manifest['cues']['pedernales']['Esta fotografía'])
        marks=json.loads((AUDIO/'word_marks.json').read_text(encoding='utf-8-sig'))
        for segment in manifest['segments']:
            self.assertLess(marks[segment['scene']][-1]['Seconds'],segment['speech_seconds'])
            with wave.open(str(AUDIO/segment['file'])) as audio: self.assertEqual(audio.getframerate(),16000)


if __name__=='__main__': unittest.main()
