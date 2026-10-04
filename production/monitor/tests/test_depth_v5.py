import json
import math
import unittest
from hashlib import sha256
import numpy as np
from PIL import ImageChops,ImageDraw
from seismic_gpu import displacement,SeismicGPU,front_radius
from reel_depth_damage_v5 import AUDIO,SCRIPT,NAMES,DepthDesignV5,narration_parts,FPS
from prepare_depth_story_v5 import V5
from export_video import font


class WavePhysicsTests(unittest.TestCase):
    def test_p_longitudinal_and_s_transverse(self):
        pts=np.array([[1,0,0],[2,-1,1]],float)
        p=displacement('p',pts,.7);s=displacement('s',pts,.7)
        self.assertTrue(np.allclose(p[:,1:],0));self.assertTrue(np.allclose(s[:,[0,2]],0))
        self.assertGreater(np.abs(p[:,0]).max(),0);self.assertGreater(np.abs(s[:,1]).max(),0)

    def test_love_horizontal_transverse_and_surface_envelope(self):
        pts=np.array([[1,0,0],[1,-1,0]])
        u=displacement('love',pts,.7)
        self.assertTrue(np.allclose(u[:,:2],0))
        self.assertGreater(abs(u[0,2]),abs(u[1,2]))

    def test_rayleigh_ellipse_is_retrograde_at_surface(self):
        times=np.linspace(0,2*math.pi/2.1,201)
        u=np.array([displacement('rayleigh',[[0,0,0]],t)[0] for t in times])
        self.assertTrue(np.allclose(u[:,2],0))
        self.assertTrue(np.allclose((u[:,0]/.28)**2+(u[:,1]/.40)**2,1))
        area=np.sum(u[:-1,0]*u[1:,1]-u[1:,0]*u[:-1,1])
        self.assertGreater(area,0,'Counterclockwise x/up-y ellipse for +x propagation')

    def test_wave_advances_but_material_returns(self):
        for kind in ('p','s','love','rayleigh'):
            self.assertTrue(np.allclose(displacement(kind,[[0,0,0]],0),displacement(kind,[[0,0,0]],2*math.pi/2.1)))
            self.assertTrue(np.allclose(displacement(kind,[[0,0,0]],.3),displacement(kind,[[.4,0,0]],.7)))

    def test_depth_diagram_can_reach_surface_not_permanent_deep_rings(self):
        for speed in (1.1,.65):
            radii=[front_radius(t,speed) for t in np.linspace(0,14,100)]
            self.assertGreater(max(radii),631.3/700*5.6)


class WaveStoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((AUDIO/'timeline.json').read_text(encoding='utf-8'));cls.design=DepthDesignV5(cls.manifest)

    def test_all_script_words_captioned_and_nothing_cut(self):
        parts=narration_parts();m=self.manifest
        self.assertEqual(list(parts),list(NAMES));self.assertEqual(m['script_sha256'],sha256(SCRIPT.read_bytes()).hexdigest())
        for name,text in parts.items():
            shown=' '.join(c['text'] for c in m['captions'] if c['scene']==name)
            self.assertEqual(' '.join(shown.split()),' '.join(text.split()))
        for part in m['segments']:
            self.assertLessEqual(part['speech_start']+part['speech_seconds'],part['end']-.69)
            self.assertAlmostEqual(part['end']*FPS,round(part['end']*FPS))

    def test_captions_fit_reserved_box(self):
        d=ImageDraw.Draw(self.design.render(0))
        for cue in self.manifest['captions']:
            lines=[];line=''
            for word in cue['text'].split():
                trial=(line+' '+word).strip()
                if d.textlength(trial,font=font(35))>790 and line:lines.append(line);line=word
                else:line=trial
            lines.append(line)
            self.assertLessEqual(len(lines),3,cue['text'])
            self.assertTrue(all(d.textlength(line,font=font(35))<=790 for line in lines))

    def test_scene_boundaries_and_midpoints_fit(self):
        for start,end,name in self.manifest['scenes']:
            for second in (start,(start+end)/2,end-1/FPS):self.assertEqual(self.design.render(second).size,(1080,1920),name)

    def test_gpu_geometry_moves_without_progress_or_text(self):
        for name in ('p','s','love','rayleigh'):
            a=self.design.gpu.wave(name,1,camera_seconds=0)[0]
            b=self.design.gpu.wave(name,1+1/FPS,camera_seconds=0)[0]
            self.assertIsNotNone(ImageChops.difference(a.crop((80,150,810,760)),b.crop((80,150,810,760))).getbbox(),name)

    def test_depth_scale_is_visible_monotonic_and_geometry_bound(self):
        gpu=self.design.gpu
        for t in (0,7,15,23):
            _,anchors=gpu.depth(631.3,t)
            ys=[anchors[d][1] for d in (0,70,300,700)]
            self.assertTrue(all(a<b for a,b in zip(ys,ys[1:])))
            for depth in (0,70,300,700):
                x,y=anchors[depth]
                self.assertTrue(90<x<800 and 0<y<830)
                self.assertTrue(np.allclose((x,y),gpu.screen((-3,-depth/700*5.6,1.8))))

    def test_preserved_science_and_no_wave_damage_attribution(self):
        p=narration_parts()
        self.assertIn('ambas nacen durante la ruptura',p['s'])
        self.assertIn('No hay una onda que siempre explique todo el daño',p['rayleigh'])
        self.assertIn('Si lo demás es comparable',p['pedernales'])
        self.assertIn('reporte preliminar',p['sentido'])
        self.assertEqual(self.design.evidence['cases']['loreto']['depth_km'],135)
        self.assertIsNone(self.design.evidence['cases']['pelileo']['depth_km'])


if __name__=='__main__':unittest.main()
