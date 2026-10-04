import json
import unittest
import wave
from hashlib import sha256
from PIL import ImageChops

from piedmont_animation import state, project, terrain_height, render_piedmont
from reel_depth_damage_v3 import narration_parts, timeline_for, DepthDesignV3, AUDIO, FPS
from reel_depth_damage_v2 import SCENES
from prepare_depth_episode import FOLDER


class ProvisionalDepthTests(unittest.TestCase):
    def test_all_words_preserved_and_original_script_not_changed(self):
        actual=' '.join(' '.join(narration_parts().values()).split())
        original=' '.join((FOLDER/'guion_elevenlabs_v2.txt').read_text(encoding='utf-8').split())
        self.assertEqual(actual,original)
        self.assertEqual(len(narration_parts()),11)

    def test_audio_never_cut_and_timeline_is_frame_aligned(self):
        lengths={name.replace('_',''):28 for _,_,name in SCENES}
        scenes=timeline_for(lengths)
        for start,end,name in scenes:
            self.assertGreaterEqual(end-start,28.9-1e-8)
            self.assertAlmostEqual(start*FPS,round(start*FPS))
            self.assertAlmostEqual(end*FPS,round(end*FPS))
        self.assertTrue(all(a[1]==b[0] for a,b in zip(scenes,scenes[1:])))

    def test_landslide_moves_down_then_along_channel_without_loop_reset(self):
        initial=state(0); slide=state(.7); flow=state(1)
        self.assertGreater(slide['center'][0],initial['center'][0])
        self.assertLess(terrain_height(*slide['center']),terrain_height(*initial['center']))
        self.assertGreater(flow['center'][1],slide['center'][1])
        self.assertEqual(state(2),flow)
        self.assertEqual(flow['scar'],1)
        self.assertEqual([state(q)['phase'] for q in (.1,.26,.56,.94)],[0,1,2,3])

    def test_terrain_within_diagram_not_phase_or_footer_text(self):
        for ix in range(25):
            for iy in range(19):
                x,y=ix/24,-.63+iy*.07
                px,py=project(x,y,terrain_height(x,y))
                self.assertTrue(0<px<840)
                self.assertTrue(115<py<530)

    def test_actual_mesh_motion_not_progress_bar(self):
        for q in (.1,.26,.56,.94):
            a=render_piedmont(q).crop((100,115,800,530))
            b=render_piedmont(q+.002).crop((100,115,800,530))
            self.assertIsNotNone(ImageChops.difference(a,b).getbbox())

    def test_all_scene_boundaries_fit(self):
        design=DepthDesignV3(SCENES)
        for start,end,name in SCENES:
            for t in (start,(start+end)/2,end-1/FPS):
                self.assertEqual(design.render(t).size,(1080,1920),name)

    @unittest.skipUnless((AUDIO/'timeline.json').exists(),'Generate local provisional speech first')
    def test_generated_narration_hashes_and_total_pcm_length(self):
        manifest=json.loads((AUDIO/'timeline.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['voice'],'Microsoft Helena Desktop (es-ES)')
        for part in manifest['segments']:
            self.assertEqual(sha256((AUDIO/part['file']).read_bytes()).hexdigest(),part['sha256'])
            self.assertLessEqual(part['speech_start']+part['speech_seconds'],part['end']-.54)
        with wave.open(str(AUDIO/'guion_completo_provisional.wav'),'rb') as audio:
            self.assertAlmostEqual(audio.getnframes()/audio.getframerate(),manifest['duration_seconds'],places=3)


if __name__=='__main__': unittest.main()
