import unittest
import numpy as np
from tools.parcelas.optical_quality import summarize_scl


class OpticalQualityTests(unittest.TestCase):
    def test_clouds_and_missing_are_not_clear(self):
        result = summarize_scl(np.array([[4, 5, 6, 9, 0, 7]], dtype="uint8"),
                               np.ones((1, 6), dtype=bool), np.array([[1, 1, 1, 1, 0, 1]], dtype=bool))
        self.assertEqual(result["pixel_centres_in_parcel"], 6)
        self.assertEqual(result["clear_fraction"], .5)
        self.assertEqual(result["missing_fraction"], 1 / 6)

    def test_outside_pixels_do_not_affect_result(self):
        result = summarize_scl(np.array([[4, 9]]), np.array([[True, False]]), np.ones((1, 2), dtype=bool))
        self.assertEqual(result["clear_fraction"], 1)

    def test_no_pixel_centres_reports_insufficient_support(self):
        result = summarize_scl(np.array([[4]]), np.array([[False]]), np.array([[True]]))
        self.assertIsNone(result["clear_fraction"])
        self.assertEqual(result["status"], "insufficient_spatial_support")


if __name__ == "__main__":
    unittest.main()
