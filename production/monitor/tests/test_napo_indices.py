"""Offline scientific and frame checks for the three-date index video."""
import json
import re
from pathlib import Path
import tempfile
import unittest

import numpy as np
from reel_napo_indices import active_year, load_evidence, SCRIPT, YEARS
from reel_napo_ndwi import pieces

try:
    from prepare_napo_indices import aggregate_2x2, indices, proxy_diagnostic, crop
    GEO = True
except ModuleNotFoundError as error:
    if error.name != "rasterio":
        raise
    GEO = False


@unittest.skipUnless(GEO, "Optional rasterio for geospatial math")
class RiverIndicesMathTests(unittest.TestCase):
    def test_mean_not_fake_upsampled_swir(self):
        values = np.array([[.1, .2, .5, .5], [.3, .4, .5, .5]], dtype="float32")
        np.testing.assert_allclose(aggregate_2x2(values), [[.25, .5]])
        values[0, 0] = np.nan
        self.assertTrue(np.isnan(aggregate_2x2(values)[0, 0]))
        with self.assertRaises(ValueError):
            aggregate_2x2(np.ones((3, 2)))

    def test_aggregate_reflectance_before_index(self):
        green = np.array([[.1, .3], [.1, .3]])
        nir = np.array([[.01, .2], [.01, .2]])
        ndwi, _, _ = indices(aggregate_2x2(green), aggregate_2x2(nir), [[.05]])
        expected = (.2 - .105) / (.2 + .105)
        self.assertAlmostEqual(float(ndwi[0, 0]), expected, places=6)

    def test_two_actual_band_contrasts_not_water_amount(self):
        ndwi, mndwi, valid = indices([.1053], [.0642], [.0457])
        self.assertAlmostEqual(float(ndwi[0]), .2424778761, places=5)
        self.assertAlmostEqual(float(mndwi[0]), .3947019868, places=5)
        self.assertTrue(valid[0])

    def test_joint_support_excludes_either_invalid_index(self):
        _, _, valid = indices([.1, .1, 0], [.05, -.05, 0], [-.1, .05, 0])
        self.assertFalse(valid.any())

    def test_proxy_is_not_independent_accuracy(self):
        array = np.ones((9, 1, 2), dtype="float32")
        array[8] = [[6, 5]]
        array[5] = [[.2, -.1]]
        array[6] = [[.4, -.2]]
        report = proxy_diagnostic(array, np.ones((1, 2), dtype=bool))
        self.assertIn("scl_water_proxy", report["ndwi"])
        self.assertNotIn("accuracy", report)
        self.assertEqual(report["mndwi"]["scl_vegetation_proxy"]["pixels"], 0)

    def test_ambiguous_legacy_offset_rejected_before_network(self):
        asset = {"raster:bands": [{"scale": .0001, "offset": -.1, "nodata": 0}]}
        item = {"collection": "sentinel-2-l2a", "properties": {"earthsearch:boa_offset_applied": True},
                "assets": {key: asset for key in ("red", "green", "blue", "nir", "swir16")}}
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            crop(item, None)


class RiverIndicesVideoTests(unittest.TestCase):
    def test_2024_is_visible_longer_and_all_three_dates_occur(self):
        self.assertEqual(YEARS, (2019, 2024, 2026))
        self.assertEqual([active_year(f) for f in (.1, .25, .5, .64, .65, .99)],
                         [2019, 2024, 2024, 2024, 2026, 2026])

    def test_script_explains_indices_and_limits(self):
        self.assertIn("dividido por su suma", SCRIPT["ndwi"])
        self.assertIn("onda corta", SCRIPT["mndwi"])
        self.assertIn("no podemos declarar un ganador por exactitud", SCRIPT["choice"])
        self.assertIn("Ocho de agosto", SCRIPT["comparemiddle"])
        self.assertIn("No significa más agua", SCRIPT["pixel"])
        self.assertIn("no hemos igualado", SCRIPT["quality"])
        self.assertIn("mide mercurio", SCRIPT["limits"])

    def test_comparison_date_follows_narration_chapter_not_caption_estimate(self):
        from reel_napo_indices import Design
        self.assertEqual([Design.scene_year(kind) for kind in ("comparefirst", "comparemiddle", "comparerecent")], list(YEARS))
        self.assertIsNone(Design.scene_year("ndwi"))

    def test_installed_voice_segment_names_are_safe_lowercase_letters(self):
        self.assertTrue(all(re.fullmatch("[a-z]+", kind) for kind in SCRIPT))

    def test_caption_chunks_do_not_drop_narration(self):
        for value in SCRIPT.values():
            self.assertEqual(" ".join(pieces(value)), value)

    def test_unreviewed_dates_rejected_before_source_loading(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            (folder / "manifest.json").write_text(json.dumps({"recipe": "other"}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Wrong reviewed"):
                load_evidence(folder)

    def test_local_evidence_all_caption_frames_when_available(self):
        # Optional integration evidence; normal clone does not need large artifacts.
        from reel_napo_indices import FOLDER, Design
        if not (FOLDER / "manifest.json").exists():
            self.skipTest("Local ignored scientific artifacts not downloaded")
        evidence = load_evidence(FOLDER)
        design = Design(FOLDER, evidence)
        for kind, narration in SCRIPT.items():
            for fraction in (.1, .5, .9):
                for caption in pieces(narration):
                    image = design.render(kind, fraction, caption, .5)
                    self.assertEqual(image.size, (1080, 1920))


if __name__ == "__main__":
    unittest.main()
