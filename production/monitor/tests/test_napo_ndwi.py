"""Offline NDWI math, radiometry and display tests; no network or invented maps."""
import unittest
import numpy as np
from PIL import Image

from reel_napo_ndwi import fit_map, pieces, timestamp, SCRIPT

try:
    from prepare_napo_ndwi import ratio, calibration, usable, color_ndwi, crop_scene
    GEO_AVAILABLE = True
except ModuleNotFoundError as error:
    if error.name != "rasterio":
        raise
    GEO_AVAILABLE = False


@unittest.skipUnless(GEO_AVAILABLE, "Optional rasterio needed for preparation math tests")
class NDWIMathTests(unittest.TestCase):
    def test_ratio_uses_green_nir_reflectance_not_rgb_colors(self):
        result, mask = ratio([.2, .1], [.1, .3])
        np.testing.assert_allclose(result, [1 / 3, -.5], atol=1e-6)
        self.assertTrue(mask.all())

    def test_no_zero_negative_or_nonfinite_denominator_invented(self):
        result, mask = ratio([0, -.1, np.nan, .2], [0, .2, .1, -.1])
        self.assertFalse(mask.any())
        self.assertTrue(np.isnan(result).all())

    def test_metadata_offset_applied_once_after_scale(self):
        asset = {"raster:bands": [{"scale": .0001, "offset": -.1, "nodata": 0}]}
        scale, offset = calibration(asset)
        self.assertAlmostEqual(1500 * scale + offset, .05)
        with self.assertRaises(ValueError):
            calibration({})
        with self.assertRaises(ValueError):
            calibration({"raster:bands": [{"scale": 1, "offset": 0, "nodata": 0}]})

    def test_scl_qa_not_a_water_classification(self):
        scl = np.arange(12).reshape(3, 4)
        optical = np.ones((4, 3, 4), dtype="float32")
        expected = np.isin(scl, [4, 5, 6])
        np.testing.assert_array_equal(usable(scl, optical), expected)
        optical[0, 1, 0] = np.nan
        self.assertFalse(usable(scl, optical)[1, 0])

    def test_nodata_is_transparent_not_a_zero_index(self):
        data = np.array([[-1, 0, 1]], dtype="float32")
        result = color_ndwi(data, np.array([[True, False, True]]))
        self.assertEqual(result.shape, (1, 3, 4))
        np.testing.assert_array_equal(result[0, :, 3], [255, 0, 255])
        np.testing.assert_array_equal(result[0, 2, :3], [7, 61, 105])

    def test_ambiguous_already_corrected_legacy_offset_fails_before_io(self):
        asset = {"raster:bands": [{"scale": .0001, "offset": -.1, "nodata": 0}]}
        item = {"collection": "sentinel-2-l2a", "properties": {"earthsearch:boa_offset_applied": True},
                "assets": {name: asset for name in ("red", "green", "blue", "nir")}}
        with self.assertRaisesRegex(ValueError, "Ambiguous already-applied"):
            crop_scene(item, None)


class NDWIVideoTests(unittest.TestCase):
    def test_map_aspect_is_not_stretched_and_nodata_not_filled(self):
        source = Image.new("RGBA", (400, 200), (255, 0, 0, 255))
        source.putpixel((200, 100), (0, 0, 0, 0))
        target, factor = fit_map(source)
        self.assertEqual(target.size, (840, 840))
        self.assertEqual(factor, 2.1)
        self.assertNotEqual(target.getpixel((420, 420)), (255, 0, 0))
        self.assertEqual(target.getpixel((420, 211)), (255, 0, 0))

    def test_caption_chunks_preserve_all_narration(self):
        for value in SCRIPT.values():
            self.assertEqual(" ".join(pieces(value)), value)
            self.assertTrue(all(len(piece.split()) <= 19 for piece in pieces(value)))

    def test_captions_have_real_srt_time_format(self):
        self.assertEqual(timestamp(61.25), "00:01:01,250")

    def test_script_keeps_current_dates_and_scientific_limits(self):
        self.assertIn("julio", SCRIPT["hook"])
        self.assertIn("veintiséis", SCRIPT["hook"])
        self.assertIn("once de julio", SCRIPT["compare"])
        self.assertIn("no mide mercurio", SCRIPT["limits"])
        self.assertIn("no garantiza el mismo caudal", SCRIPT["napo"])
        self.assertEqual(list(SCRIPT)[0], "hook")


if __name__ == "__main__":
    unittest.main()
