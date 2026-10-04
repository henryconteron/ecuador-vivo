"""Synthetic algorithm fixtures only; never exported as real river observations."""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
AVAILABLE = importlib.util.find_spec("numpy") is not None


@unittest.skipUnless(AVAILABLE, "Optional numpy required")
class FluvialScienceTests(unittest.TestCase):
    def setUp(self):
        import numpy as np
        import fluvial_science as science
        self.np, self.s = np, science

    def test_formulas_include_swir2_not_repeated_swir1(self):
        np, s = self.np, self.s
        b = np.array([[.1], [.2], [.15], [.1], [.05], [.025]], dtype=np.float32)
        v = s.signals(b)
        self.assertAlmostEqual(v["aweinsh"][0], 4 * (.2 - .05) - .25 * .1 - 2.75 * .025)
        self.assertAlmostEqual(v["aweish"][0], .1 + 2.5 * .2 - 1.5 * (.1 + .05) - .25 * .025)
        self.assertAlmostEqual(v["ndti"][0], (.15 - .2) / (.15 + .2))
        self.assertEqual(s.votes(b, np.array([True]), dict.fromkeys(s.METHODS, 0))[0], 4)
        self.assertEqual(s.votes(b, np.array([False]), dict.fromkeys(s.METHODS, 0))[0], -1)
        with self.assertRaises(ValueError): s.votes(b, np.array([True]), {})

    def test_nodata_not_dry_or_water_loss(self):
        np, s = self.np, self.s
        a = np.array([-1, 4, 0, 3, 0, 4]); b = np.array([0, 0, 4, 0, 0, 4])
        np.testing.assert_equal(s.transitions(a, b), [0, 3, 4, 5, 1, 2])
        frequency, count = s.presence_frequency(np.array([[1, 0, 0], [0, 0, 0]]), np.array([[True, False, True], [False, False, True]]))
        self.assertEqual(frequency[0], 1); self.assertTrue(np.isnan(frequency[1])); self.assertEqual(frequency[2], 0)
        np.testing.assert_equal(count, [1, 0, 2])
        with self.assertRaises(ValueError): s.presence_frequency(np.array([[3]]), np.array([[True]]))

    def test_minimum_distance_requires_all_independent_classes(self):
        np, s = self.np, self.s
        x = np.array([[.01] * 6, [.1] * 6, [.3] * 6, [.5] * 6])
        model = s.fit_minimum_distance(x, np.array(s.CLASSES))
        np.testing.assert_equal(s.classify_minimum_distance(x, model), [0, 1, 2, 3])
        with self.assertRaises(ValueError): s.fit_minimum_distance(x[:3], np.array(s.CLASSES[:3]))
        with self.assertRaises(ValueError): s.classify_minimum_distance(np.full((1, 6), np.nan), model)

    def test_metrics_do_not_hide_water_omission_in_overall_accuracy(self):
        np, s = self.np, self.s
        r = s.water_metrics(np.array([1, 1, 0, 0]), np.array([1, 0, 1, 0]))
        self.assertEqual(r["precision"], .5); self.assertEqual(r["recall"], .5); self.assertEqual(r["f1"], .5); self.assertEqual(r["iou"], 1 / 3)
        r = s.water_metrics(np.array([0, 0]), np.array([0, 0]))
        self.assertIsNone(r["f1"]); self.assertIsNone(r["recall"])

    @unittest.skipUnless(importlib.util.find_spec("rasterio"), "Optional rasterio required")
    def test_empty_references_are_not_published_as_validation(self):
        import evaluate_fluvial_methods as evaluator
        with self.assertRaises(ValueError): evaluator.read_references({"type": "FeatureCollection", "features": []}, {}, ROOT / "tmp")

    @unittest.skipUnless(importlib.util.find_spec("rasterio"), "Optional rasterio required")
    def test_held_out_metrics_and_qa_omissions_are_separate(self):
        import evaluate_fluvial_methods as evaluator
        np, s = self.np, self.s
        rows = [{"role": role, "class": label, "features": np.full(6, .01 + i * .1), "sample_id": f"{role}-{i}", "usable": True}
                for role in ["train", "test"] for i, label in enumerate(s.CLASSES)]
        rows.append({"role": "test", "class": "water_shallow", "features": np.full(6, -9999), "sample_id": "missing-water", "usable": False})
        report = evaluator.evaluate(rows)
        self.assertIsNone(report["winner"])
        self.assertEqual(report["methods"]["minimum_distance"]["test"]["f1"], 1)
        self.assertEqual(report["qa_coverage"]["test"]["water_shallow"], {"references": 2, "useful": 1})
        self.assertEqual(report["qa_missing_sample_ids"], ["missing-water"])
        rows[0]["usable"] = False
        with self.assertRaises(ValueError): evaluator.evaluate(rows)

    @unittest.skipUnless(importlib.util.find_spec("rasterio"), "Optional rasterio required")
    def test_independent_reference_contract_and_spatial_leakage(self):
        import copy
        import tempfile
        import hashlib
        import rasterio
        from rasterio.warp import transform
        from rasterio.transform import from_origin
        import evaluate_fluvial_methods as evaluator
        np, s = self.np, self.s
        with tempfile.TemporaryDirectory() as folder:
            raw = Path(folder); path = raw / "synthetic-test-only.tif"
            grid = from_origin(840000, 9896000, 20, 20)
            data = np.full((7, 40, 40), .1, dtype=np.float32); data[6] = 1
            with rasterio.open(path, "w", driver="GTiff", count=7, width=40, height=40, crs="EPSG:32717", transform=grid, dtype="float32") as ds:
                ds.write(data)
            date = "2019-07-11"
            scene = {"date": date, "native_file": path.name, "native_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "acquired_at": date + "T15:43:42Z"}
            manifest = {"config": {"scenes": [{"date": date}]}, "regions": [{"id": "test-only", "scenes": [scene]}]}
            document = {"type": "FeatureCollection", "features": []}
            for role, row in [("train", 2), ("test", 30)]:
                for col, label in enumerate(s.CLASSES, 2):
                    x, y = rasterio.transform.xy(grid, row, col)
                    lon, lat = transform("EPSG:32717", "EPSG:4326", [x], [y])
                    document["features"].append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon[0], lat[0]]},
                      "properties": {"sample_id": f"{role}-{col}", "group_id": role, "region": "test-only", "date": date,
                       "class": label, "role": role, "independent_reference": True, "reference_type": "drone",
                       "evidence_uri": "https://example.test/synthetic-fixture-not-evidence", "reference_acquired_at": scene["acquired_at"], "observer": "test fixture"}})
            rows = evaluator.read_references(document, manifest, raw)
            self.assertEqual(len(rows), 8)
            for mutate in [lambda d: d["features"][0]["properties"].update(independent_reference=False),
                           lambda d: d["features"][0]["properties"].update(reference_type="SCL"),
                           lambda d: d["features"][4]["properties"].update(group_id="train"),
                           lambda d: d["features"][0]["properties"].update(reference_acquired_at="2019-07-13T15:43:42Z"),
                           lambda d: d["features"][4].update(geometry=d["features"][0]["geometry"]),
                           lambda d: d["features"][0]["properties"].update(evidence_uri="javascript:bad")]:
                invalid = copy.deepcopy(document); mutate(invalid)
                with self.assertRaises(ValueError): evaluator.read_references(invalid, manifest, raw)

    @unittest.skipUnless(importlib.util.find_spec("rasterio"), "Optional rasterio required")
    def test_real_public_packs_match_native_arrays_when_local_sources_exist(self):
        import gzip
        import hashlib
        import json
        import rasterio
        from rasterio.warp import reproject, Resampling
        from affine import Affine
        np = self.np
        manifest = json.loads((ROOT / "data/fluvial/manifest.json").read_text(encoding="utf-8"))
        raw = ROOT / "data/raw/fluvial"
        if not all((raw / scene["native_file"]).exists() for region in manifest["regions"] for scene in region["scenes"]):
            self.skipTest("Ignored native source arrays not available; public packs are checked by JS in CI")
        for region in manifest["regions"]:
            for scene in region["scenes"]:
                path = raw / scene["native_file"]
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), scene["native_sha256"])
                displayed = np.frombuffer(gzip.decompress((ROOT / scene["url"]).read_bytes()), dtype="<f4").reshape(7, region["height"], region["width"])
                with rasterio.open(path) as ds:
                    self.assertEqual(ds.descriptions, ("B2", "B3", "B4", "B8", "B11", "B12", "valid"))
                    self.assertEqual(ds.res, (20, 20)); self.assertEqual(ds.crs.to_epsg(), 32717)
                    native = ds.read(); projected = np.full(displayed.shape, -9999, dtype=np.float32)
                    for band in range(7):
                        reproject(native[band], projected[band], src_transform=ds.transform, src_crs=ds.crs,
                                  dst_transform=Affine(*region["web_transform"]), dst_crs="EPSG:3857", src_nodata=-9999, dst_nodata=-9999, resampling=Resampling.nearest)
                mask = projected[6] == 1; projected[6] = mask.astype(np.float32); projected[:6, ~mask] = -9999
                np.testing.assert_array_equal(displayed, projected)


if __name__ == "__main__": unittest.main()
