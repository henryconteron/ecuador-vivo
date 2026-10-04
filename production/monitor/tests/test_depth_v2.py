import unittest
import json
from hashlib import sha256

from PIL import ImageChops

from depth_animation import project_block, path_length, HORIZONTAL_DISTANCE, DEPTH_SCALE
from reel_depth_damage_v2 import DepthDesignV2, SCENES, DURATION, profile_position, PROFILE_BOXES
from prepare_depth_episode import FOLDER, HASH


class ProfilesAndDepthTests(unittest.TestCase):
    def test_opening_then_deep_intermediate_shallow_then_cases(self):
        self.assertEqual([s[2] for s in SCENES[:7]],['pregunta_cortes','leer_cortes','profundo','intermedio','superficial','comparacion','pedernales'])
        self.assertEqual(SCENES[0][0],0)
        self.assertEqual(SCENES[-1][1],DURATION)
        self.assertTrue(all(a[1]==b[0] for a,b in zip(SCENES,SCENES[1:])))

    def test_profile_axes_are_original_unstretched_coordinates(self):
        for i,lower,upper in [(0,-83,-74.5),(1,-5.5,2.5)]:
            box=PROFILE_BOXES[i]
            self.assertEqual(profile_position(lower,0,i),box[:2])
            self.assertEqual(profile_position(upper,300,i),box[2:])
            self.assertGreater(profile_position(lower,150,i)[1],profile_position(lower,70,i)[1])

    def test_selection_has_no_deep_class_and_missing_depth_is_not_zero(self):
        design=DepthDesignV2()
        self.assertEqual(len(design.known),2660)
        self.assertEqual(design.maximum,254)
        self.assertEqual(sum(r['depth_km']>=300 for r in design.known),0)
        self.assertEqual(len(design.rows)-len(design.known),1)

    def test_same_city_and_scale_for_all_three_hypothetical_sources(self):
        city=project_block(HORIZONTAL_DISTANCE,0,0)
        epicenter=project_block(0,0,0)
        self.assertEqual(HORIZONTAL_DISTANCE,40)
        previous=0
        for depth in (10,150,500):
            focus=project_block(0,0,depth)
            self.assertEqual(focus[0],epicenter[0])
            self.assertAlmostEqual(focus[1]-epicenter[1],depth*DEPTH_SCALE)
            self.assertGreater(path_length(depth),previous);previous=path_length(depth)
            self.assertEqual(city,project_block(40,0,0))

    def test_all_scene_boundaries_fit_and_motion_is_inside_diagrams(self):
        design=DepthDesignV2()
        for start,end,name in SCENES:
            for t in (start,start+.5,(start+end)/2,end-1/30):
                self.assertEqual(design.render(t).size,(1080,1920),name)
        for t,box in [(17,PROFILE_BOXES[0]),(38,(120,530,915,1240)),(58,(120,530,915,1240)),(70,(120,530,915,1240))]:
            a,b=design.render(t).crop(box),design.render(t+1/30).crop(box)
            self.assertIsNotNone(ImageChops.difference(a,b).getbbox())

    def test_primary_source_audit_is_pinned_and_deep_example_is_not_catalog_data(self):
        audit=json.loads((FOLDER/'source_audit_v2.json').read_text(encoding='utf-8'))
        self.assertEqual(audit['catalog_sha256'],HASH)
        self.assertEqual((audit['regional_records'],audit['profile_records'],audit['maximum_selected_depth_km'],audit['selected_deep_events']),(2661,2660,254,0))
        self.assertEqual(audit['hypothetical_depths_km'],[500,150,10])
        for record in list(audit['sources'].values())+audit['cases']:
            self.assertEqual(sha256((FOLDER/record['file']).read_bytes()).hexdigest(),record['sha256'])

    def test_new_script_and_captions_keep_scientific_limits(self):
        script=(FOLDER/'guion_elevenlabs_v2.txt').read_text(encoding='utf-8')
        self.assertTrue(script.startswith('En el video anterior vimos estos cortes'))
        self.assertIn('no un evento de este catálogo',script)
        self.assertIn('No estamos viendo capas de roca',script)
        self.assertIn('Profundo no significa inofensivo',script)
        self.assertLessEqual(len(script.split()),370)
        for name in ('descripcion_instagram_v2_borrador.txt','descripcion_tiktok_v2_borrador.txt'):
            text=(FOLDER/name).read_text(encoding='utf-8')
            self.assertLessEqual(len(text),2200)
            self.assertIn('254 km',text)
            self.assertIn('CC BY-SA 2.0',text)


if __name__=='__main__':unittest.main()
