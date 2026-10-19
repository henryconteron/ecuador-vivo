import unittest
import numpy as np
from tools.parcelas.radar_pair import paired_statistics


class RadarPairTests(unittest.TestCase):
    def test_double_power_is_three_db_not_six(self):
        result = paired_statistics(np.ones((2, 2)), np.full((2, 2), 2.), np.ones((2, 2), dtype=bool))
        self.assertAlmostEqual(result["ratio_of_means_db"], 3.0102999566)
        self.assertEqual(result["paired_pixel_centres"], 4)

    def test_nodata_and_nonpositive_do_not_become_zero_db(self):
        result = paired_statistics(np.array([[1., 0., np.nan, 4.]]),
                                   np.array([[1., 2., 2., 1.]]), np.array([[True, True, True, False]]))
        self.assertEqual(result["paired_pixel_centres"], 1)
        self.assertEqual(result["ratio_of_means_db"], 0)

    def test_empty_support_has_no_statistic(self):
        result = paired_statistics(np.zeros((1, 1)), np.ones((1, 1)), np.ones((1, 1), dtype=bool))
        self.assertIsNone(result["ratio_of_means_db"])

    def test_misaligned_shapes_rejected(self):
        with self.assertRaises(ValueError):
            paired_statistics(np.ones((1, 1)), np.ones((2, 1)), np.ones((1, 1), dtype=bool))


if __name__ == "__main__":
    unittest.main()
