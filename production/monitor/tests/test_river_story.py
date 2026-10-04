"""Verify the narrative promise is an actual rule change, not a fake event."""
import json
from pathlib import Path
import unittest

import numpy as np
from PIL import Image
from reel_river_story import SCRIPT, Design, FOLDER, load_evidence
from reel_napo_ndwi import pieces


class RiverStoryTests(unittest.TestCase):
    def test_universal_hook_then_ecuador_as_case(self):
        self.assertIn("de este mapa",SCRIPT["hook"])
        self.assertNotIn("Napo",SCRIPT["hook"])
        self.assertNotIn("Jatunyacu",SCRIPT["hook"])
        self.assertLess(list(SCRIPT).index("invisible"),list(SCRIPT).index("index"))
        self.assertGreater(list(SCRIPT).index("comparefirst"),list(SCRIPT).index("reveal"))
        self.assertIn("No del paisaje",SCRIPT["end"])
        self.assertIn("no es un análisis químico",SCRIPT["sediment"])

    def test_captions_preserve_original_narration(self):
        for value in SCRIPT.values():
            self.assertEqual(" ".join(pieces(value)),value)

    def test_demo_is_same_observation_and_nested_thresholds(self):
        if not (FOLDER/"manifest.json").exists():
            self.skipTest("Local evidence unavailable")
        load_evidence(FOLDER)
        report=json.loads((FOLDER/"hook_evidence.json").read_text(encoding="utf-8"))
        self.assertEqual(report["date"],"2024-08-08")
        with Image.open(FOLDER/"threshold_low.png") as im:
            low=np.array(im)
        with Image.open(FOLDER/"threshold_high.png") as im:
            high=np.array(im)
        np.testing.assert_array_equal(low[:,:,3],high[:,:,3])
        valid=low[:,:,3]==255
        a=valid & (low[:,:,2]==202)
        b=valid & (high[:,:,2]==202)
        self.assertFalse(np.any(b & ~a))
        self.assertGreater(int(a.sum()),int(b.sum()))
        self.assertEqual(report["candidate_pixels"],{"low":int(a.sum()),"high":int(b.sum())})

    def test_frame_safety_and_phase_cache(self):
        if not (FOLDER/"manifest.json").exists():
            self.skipTest("Local evidence unavailable")
        d=Design(FOLDER,load_evidence(FOLDER))
        for kind,value in SCRIPT.items():
            for phase in (.1,.6,.9):
                for caption in pieces(value):
                    self.assertEqual(d.render(kind,phase,caption,.5).size,(1080,1920))
        for kind in ("hook","reveal","index"):
            self.assertNotEqual(d.render(kind,.1,"Prueba",.5).tobytes(),d.render(kind,.9,"Prueba",.5).tobytes())
        self.assertEqual([Design.scene_year(k) for k in ("comparefirst","comparemiddle","comparerecent")],[2019,2024,2026])


if __name__=="__main__":
    unittest.main()
