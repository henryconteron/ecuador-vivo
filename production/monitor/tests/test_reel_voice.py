import math
import unittest

from reel_voice import FPS, timeline
from reel_design import closing_card


class VoiceReelTests(unittest.TestCase):
    def setUp(self):
        self.cues=dict(scope_start=14.30,archive_complete=31.31,guide_start=47.22,
                       depth_start=65.57,profile_start=81.17,action_start=105.17,end_start=118.28)
        self.duration=121.156

    def test_map_first_complete_period_and_full_narration(self):
        plan=timeline(1900,2025,self.cues,self.duration)
        self.assertEqual(plan[0][:2],("year",1900))
        self.assertEqual([year for kind,year,_ in plan if kind=="year"],list(range(1900,2026)))
        self.assertEqual([kind for kind,_,_ in plan if kind!="year"],
                         ["hold","guide","depth","profile","action","end"])
        self.assertTrue(all(frames>0 for _,_,frames in plan))
        self.assertEqual(sum(frames for _,_,frames in plan),math.ceil((self.duration+5)*FPS))
        self.assertEqual(sum(frames for kind,_,frames in plan if kind=="year"),round(self.cues["archive_complete"]*FPS))

    def test_bad_cues_cannot_cut_or_reverse_narration(self):
        for key,value in [("scope_start",0),("scope_start",32),("guide_start",30),
                          ("guide_start",31.311),("end_start",122),("depth_start",float("nan"))]:
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):
                timeline(1900,2025,dict(self.cues,**{key:value}),self.duration)
        with self.assertRaises(ValueError):
            timeline(2025,1900,self.cues,self.duration)
        with self.assertRaises(ValueError):
            timeline(1900,2025,self.cues,self.duration,tail=-1)

    def test_new_closing_fits_canvas(self):
        image=closing_card(dict(exported_count=2661,minimum=4,downloaded_at_utc="2026-10-02"),tagline=True)
        self.assertEqual(image.size,(1080,1920))


if __name__=="__main__":
    unittest.main()
