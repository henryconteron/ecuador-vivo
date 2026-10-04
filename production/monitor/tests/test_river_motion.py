"""Verify explanatory motion and the distinction between diagrams and evidence."""
from pathlib import Path
import unittest
import numpy as np
from reel_river_motion import SCRIPT, FOLDER, Design, candidates, threshold_at, load_evidence
from reel_napo_ndwi import pieces, export


class RiverMotionTests(unittest.TestCase):
    def test_one_central_question_and_no_method_catalog(self):
        self.assertIn("¿Se está secando?", SCRIPT["hook"])
        self.assertNotIn("Jatunyacu", SCRIPT["hook"])
        self.assertIn("Con estas tres imágenes no podemos afirmarlo", SCRIPT["end"])
        self.assertIn("misma imagen, mismo día", SCRIPT["threshold"])
        self.assertNotIn("A W E I", " ".join(SCRIPT.values()))
        self.assertNotIn("N D T I", " ".join(SCRIPT.values()))
        self.assertLess(list(SCRIPT).index("level"),list(SCRIPT).index("index"))
        self.assertLess(list(SCRIPT).index("light"),list(SCRIPT).index("index"))
        for narration in SCRIPT.values():
            self.assertEqual(" ".join(pieces(narration)), narration)

    def test_threshold_is_bounded_monotone_and_nodata_stays_missing(self):
        ts=[threshold_at(t) for t in np.linspace(0,1,101)]
        self.assertEqual(ts[0],0)
        self.assertEqual(ts[-1],.2)
        self.assertTrue(all(a<=b for a,b in zip(ts,ts[1:])))
        a=np.array([[.4,.1,np.nan]])
        common=np.array([[True,True,False]])
        np.testing.assert_array_equal(candidates(a,common,.2),[[True,False,False]])

    def test_render_stride_rejects_bad_values_before_io(self):
        for stride in (0,4,-1,1.5):
            with self.assertRaises(ValueError):
                export(Path("absent"),render_stride=stride)

    def test_real_data_and_animations(self):
        if not (FOLDER/"motion_evidence.json").exists():
            self.skipTest("Local ignored evidence unavailable")
        m=load_evidence(FOLDER)
        d=Design(FOLDER,m)
        self.assertEqual(candidates(d.values,d.common,0).sum(),947)
        self.assertEqual(candidates(d.values,d.common,.2).sum(),681)
        last=candidates(d.values,d.common,0)
        for threshold in np.linspace(0,.2,15):
            now=candidates(d.values,d.common,threshold)
            self.assertFalse(np.any(now & ~last))
            last=now
        for kind,narration in SCRIPT.items():
            for phase in (.05,.35,.65,.95):
                for caption in pieces(narration):
                    self.assertEqual(d.render(kind,phase,caption,.5).size,(1080,1920))
            # Exclude captions/progress: the explanation itself must change.
            if kind not in ("comparefirst","comparerecent"):
                self.assertNotEqual(d.render(kind,.05,"",.5).tobytes(),d.render(kind,.95,"",.5).tobytes())

    def test_native_array_recipe_reproduces_if_geo_dependencies_present(self):
        if not (FOLDER/"motion_evidence.json").exists():
            self.skipTest("Local ignored evidence unavailable")
        try:
            from prepare_napo_methods import read_native, signals
            from affine import Affine
        except ModuleNotFoundError:
            self.skipTest("Optional geospatial dependencies unavailable")
        m=load_evidence(FOLDER)
        row=next(r for r in m["sources"] if r["region"]=="jatunyacu" and r["date"]=="2024-08-08")
        a,grid=read_native(FOLDER/row["local_file"])
        detail=m["regions"]["jatunyacu_detail"]
        target=Affine(*detail["transform"])
        x,y=(~grid)*(target.c,target.f)
        x,y=round(x),round(y)
        expected=signals(a[:6,y:y+detail["height"],x:x+detail["width"]])["mndwi"]
        with np.load(FOLDER/"threshold_values.npz",allow_pickle=False) as arrays:
            np.testing.assert_array_equal(arrays["values"],expected)


if __name__=="__main__":
    unittest.main()
