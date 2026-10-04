"""Methods, honest narrative limits, and all generated caption safe areas."""
import json
from pathlib import Path
import re
import tempfile
import unittest

import numpy as np
from reel_napo_methods import Design, FOLDER, SCRIPT, load_evidence
from reel_napo_ndwi import pieces

try:
    from prepare_napo_methods import signals, agreement, transitions, read_native
    GEO = True
except ModuleNotFoundError as error:
    if error.name != "rasterio":
        raise
    GEO = False


@unittest.skipUnless(GEO, "Optional rasterio pipeline")
class MethodsMathTests(unittest.TestCase):
    def test_awei_uses_swir_two_not_repeated_swir_one(self):
        b = np.array([[.02], [.1], [.09], [.03], [.01], [.005]], dtype="float32")
        s = signals(b)
        self.assertAlmostEqual(float(s["aweinsh"][0]), 4*(.1-.01)-.25*.03-2.75*.005, places=6)
        self.assertAlmostEqual(float(s["aweish"][0]), .02+2.5*.1-1.5*(.03+.01)-.25*.005, places=6)
        self.assertAlmostEqual(float(s["ndti"][0]), (.09-.1)/(.09+.1), places=6)

    def test_missing_is_never_dry_or_candidate_loss(self):
        vals = {k: np.array([1, -1, 1]) for k in ("ndwi", "mndwi", "aweinsh", "aweish")}
        count = agreement(vals, np.array([True, True, False]))
        np.testing.assert_array_equal(count, [4, 0, -1])
        np.testing.assert_array_equal(transitions(count, np.array([0, 4, 0])), [3, 4, 0])

    def test_disagreement_is_not_sediment(self):
        np.testing.assert_array_equal(transitions(np.array([4, 3, 0, -1]), np.array([2, 0, 4, 4])), [5, 5, 4, 0])

    def test_native_band_read_masks_nodata_when_artifacts_exist(self):
        if not (FOLDER / "manifest.json").exists():
            self.skipTest("Local ignored observations unavailable")
        m = load_evidence(FOLDER)
        for s in m["sources"]:
            a, grid = read_native(FOLDER / s["local_file"])
            sig = signals(a[:6])
            valid = a[6] == 1
            self.assertEqual(abs(grid.a), 20)
            self.assertTrue(np.all(np.isfinite(a[:6, valid])))
            for k in sig:
                self.assertTrue(np.isfinite(sig[k][valid]).all())


class MethodsVideoTests(unittest.TestCase):
    def test_three_dates_tied_to_narration_not_estimated_captions(self):
        self.assertEqual([Design.scene_year(k) for k in ("comparefirst", "comparemiddle", "comparerecent")], [2019,2024,2026])
        self.assertIn("Detengámonos en 2024", __import__("reel_napo_methods").TITLES["comparemiddle"][0])

    def test_original_narrative_distinguishes_three_questions(self):
        self.assertIn("Son tres problemas distintos", SCRIPT["questions"])
        self.assertIn("no significa más agua", SCRIPT["reveal"])
        self.assertIn("no nos cuentan todo", SCRIPT["comparerecent"])
        self.assertIn("umbral exploratorio", SCRIPT["agreement"])
        self.assertIn("comparten bandas", SCRIPT["agreement"])
        self.assertIn("No significa automáticamente", SCRIPT["change"])
        self.assertIn("Una nube tampoco cuenta", SCRIPT["dry"])
        self.assertIn("no una concentración", SCRIPT["sediment"])
        self.assertIn("No trasladamos su resultado", SCRIPT["validation"])

    def test_segments_safe_and_captions_lossless(self):
        for k, s in SCRIPT.items():
            self.assertTrue(re.fullmatch("[a-z]+", k))
            self.assertEqual(" ".join(pieces(s)), s)

    def test_bad_recipe_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "manifest.json").write_text(json.dumps({"recipe":"other"}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_evidence(p)

    def test_all_caption_frames_and_metadata_if_present(self):
        if not (FOLDER / "manifest.json").exists():
            self.skipTest("Local ignored observations unavailable")
        m = load_evidence(FOLDER)
        self.assertIsNone(m["winner"])
        d = Design(FOLDER, m)
        for kind, narration in SCRIPT.items():
            for fraction in (.1,.5,.9):
                for caption in pieces(narration):
                    self.assertEqual(d.render(kind, fraction, caption, .5).size, (1080,1920))
        if (FOLDER / "video_metadata.json").exists():
            video = json.loads((FOLDER / "video_metadata.json").read_text())
            self.assertEqual(video["full_decode"], "passed")
            self.assertEqual([s["kind"] for s in video["scenes"]], list(SCRIPT))


if __name__ == "__main__":
    unittest.main()
