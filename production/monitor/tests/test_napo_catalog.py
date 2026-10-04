import unittest
from datetime import datetime, timezone
from pathlib import Path

from fault_blocks import DIP_RATIO, displacement
from prepare_napo_catalog import EPOCH, REGION, load_catalog, normalize
from reel_napo_catalog import SCENES, historical_year, camera, CatalogFaultDesign
from reel_napo_fault import ZOOM_EXTENT


def feature(identity="test", year=1927, depth=None, mag_type="mw"):
    utc = datetime(year, 6, 10, tzinfo=timezone.utc)
    return {"id": identity, "geometry": {"coordinates": [-77.8, -.99, depth]},
            "properties": {"time": (utc-EPOCH).total_seconds()*1000, "mag": 5,
                           "magType": mag_type}}


class CatalogAnimationTests(unittest.TestCase):
    def test_normal_and_reverse_are_parallel_to_plane(self):
        for kind, expected_sign in (("normal", -1), ("inversa", 1)):
            for phase in (.1, .5, 1):
                dx, dy, dz = displacement(kind, phase)
                self.assertEqual(dy, 0)
                self.assertGreater(dz*expected_sign, 0)
                self.assertAlmostEqual(dx+DIP_RATIO*dz, 0)

    def test_strike_slip_is_horizontal_and_clamped(self):
        for kind in ("normal", "inversa", "desgarre"):
            self.assertEqual(displacement(kind, -1), (0, 0, 0))
            self.assertEqual(displacement(kind, 2), displacement(kind, 1))
        dx, dy, dz = displacement("desgarre", 1)
        self.assertEqual((dx, dz), (0, 0))
        self.assertGreater(dy, 0)

    def test_pre_epoch_dates_types_and_missing_depth_are_preserved(self):
        row = normalize([feature()])[0]
        self.assertEqual(row["year"], 1927)
        self.assertEqual(row["magnitude_type"], "mw")
        self.assertIsNone(row["depth_km"])
        self.assertTrue(row["local_time"].endswith("-05:00"))

    def test_invalid_or_duplicate_records_fail(self):
        with self.assertRaises(ValueError):
            normalize([feature(), feature()])
        for year in (1899, 2026):
            with self.assertRaises(ValueError):
                normalize([feature(year=year)])
        outside = feature()
        outside["geometry"]["coordinates"][0] = -80
        with self.assertRaises(ValueError):
            normalize([outside])

    def test_timeline_and_camera_do_not_change_coordinates(self):
        years = [historical_year(t/30) for t in range(24*30)]
        self.assertEqual(years, sorted(years))
        self.assertEqual((years[0], years[-1]), (1900, 2025))
        self.assertEqual(historical_year(10.5), 1987)
        self.assertEqual(camera(0), REGION)
        for a, b in zip(camera(1), ZOOM_EXTENT):
            self.assertAlmostEqual(a, b)
        self.assertEqual([s[2] for s in SCENES][:5],
                         ["mapa_historico", "pregunta_2026", "mapa_2026", "zoom_tena", "que_es_falla"])
        self.assertTrue(all(a[1] == b[0] for a, b in zip(SCENES, SCENES[1:])))

    def test_pinned_history_and_current_have_distinct_periods(self):
        folder = Path(__file__).resolve().parents[1]/"artifacts/serie_memoria_sismica/01_napo"
        history, audit = load_catalog(folder)
        self.assertEqual(len(history), 347)
        self.assertEqual(min(r["year"] for r in history), 1927)
        self.assertEqual(len({r["id"] for r in history}), len(history))
        main = next(r for r in history if r["id"] == "usp000330w")
        self.assertEqual((main["magnitude"], main["magnitude_type"]), (7.2, "mw"))
        self.assertTrue(main["local_time"].startswith("1987-03-05"))
        design = CatalogFaultDesign(folder)
        self.assertTrue(all(r["utc_time"].startswith("2026-") for r in design.current))
        self.assertTrue(all(r["year"] <= 2025 for r in history))


if __name__ == "__main__":
    unittest.main()
