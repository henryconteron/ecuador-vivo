import json
import unittest
from pathlib import Path

import numpy as np

from seismology import (
    calcular_valor_b,
    estimar_mc_maxima_curvatura,
    evaluar_consistencia_buzamiento,
    vectorized_haversine,
)


class SeismologyTests(unittest.TestCase):
    def test_haversine_same_point_is_zero(self):
        result = vectorized_haversine(-0.2, -78.5, np.array([-0.2]), np.array([-78.5]))
        self.assertEqual(result[0], 0.0)

    def test_dip_consistency_rejects_vertical_and_accepts_geometry(self):
        self.assertIsNone(evaluar_consistencia_buzamiento(10, 0, 90))
        consistent, expected = evaluar_consistencia_buzamiento(10, 10, 45)
        self.assertTrue(consistent)
        self.assertEqual(round(expected, 6), 10.0)

    def test_mc_requires_minimum_sample(self):
        self.assertIsNone(estimar_mc_maxima_curvatura([2.0, 2.1, 2.2, 2.3]))

    def test_b_value_returns_finite_estimate(self):
        magnitudes = [2.5, 2.6, 2.7, 2.8, 3.0, 3.2, 3.5]
        b_value, error, sample_size = calcular_valor_b(magnitudes, 2.5)
        self.assertGreater(b_value, 0)
        self.assertGreaterEqual(error, 0)
        self.assertEqual(sample_size, len(magnitudes))

    def test_fault_catalog_is_present_and_valid(self):
        path = Path(__file__).parents[1] / "ecuador_active_faults.geojson"
        with path.open(encoding="utf-8") as handle:
            catalog = json.load(handle)
        self.assertEqual(catalog["type"], "FeatureCollection")
        self.assertGreater(len(catalog["features"]), 0)


if __name__ == "__main__":
    unittest.main()
