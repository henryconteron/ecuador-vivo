import unittest
import numpy as np
from tools.parcelas.radar_series import temporal_gaps, summarize_series


class RadarSeriesTests(unittest.TestCase):
    def test_large_gap_is_explicit_not_interpolated(self):
        gaps = temporal_gaps(["2020-12-23", "2021-01-04", "2025-03-08"])
        self.assertEqual(len(gaps), 1)
        self.assertGreater(gaps[0]["days"], 1400)

    def test_duplicate_and_unsorted_dates_are_rejected(self):
        for dates in (["2025-03-08", "2025-03-08"], ["2025-03-20", "2025-03-08"]):
            with self.subTest(dates=dates), self.assertRaises(ValueError):
                temporal_gaps(dates)

    def test_common_mask_applies_to_every_date(self):
        arrays = [np.array([[1., 2.]]), np.array([[2., np.nan]])]
        rows = summarize_series(arrays, np.array([[True, True]]))
        self.assertEqual(rows[0]["paired_centres"], 1)
        self.assertEqual(rows[0]["mean_linear"], 1)
        self.assertAlmostEqual(rows[1]["db_of_mean_linear"], 3.0102999566)

    def test_empty_support_is_not_zero(self):
        rows = summarize_series([np.zeros((1, 1))], np.ones((1, 1), dtype=bool))
        self.assertIsNone(rows[0]["db_of_mean_linear"])


if __name__ == "__main__":
    unittest.main()
