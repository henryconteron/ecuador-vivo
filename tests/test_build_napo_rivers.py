"""Small synthetic fixtures, isolated in temporary directories; never public data."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rivers_builder", ROOT / "scripts/build_napo_rivers.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class RiverBuilderTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / "data/rivers/napo-config.json").read_text(encoding="utf-8"))
        # Synthetic fixtures do not impersonate the pinned public acquisitions.
        self.config["scene_selection"] = {"mode": "quarter-cloud-ranked-per-block", "max_per_quarter": 8}
        # Tiny artificial provincial grid, ONLY in this isolated test fixture.
        self.config["processing_grid"]["bbox"] = [-77.901, -1.01, -77.898, -1.007]
        self.receipt = {key: copy.deepcopy(value) for key, value in self.config.items() if key not in ["file_dimensions", "max_pixels", "attribution"]}
        self.receipt.update({"processing_block": {"id": 7, "bbox": [-77.9, -1.01, -77.899, -1.009]}, "boundary": {"type": "Feature", "properties": {"shapeName": "Napo", "shapeGroup": "ECU"},
            "geometry": {"type": "Polygon", "coordinates": [[[-77.9, -1.01], [-77.899, -1.01], [-77.899, -1.009], [-77.9, -1.009], [-77.9, -1.01]]]}},
            "area_m2": 12750626696, "export_requested_at": "2026-09-30T18:00:00Z",
            "scenes": [{"year": year, "period": self.config["periods"][i], "joined_count": 10,
                        "scene_ids": [f"test-only-{year}-{day}" for day in range(10)],
                        "acquired_ms": [__import__("datetime").datetime(year, 1, day + 1, tzinfo=__import__("datetime").timezone.utc).timestamp() * 1000 for day in range(10)]}
                       for i, year in enumerate([2019, 2024])]})

    def test_receipt_and_candidate_fail_closed(self):
        builder.validate_receipt(self.receipt, self.config)
        for mutate in [lambda r: r.update(export_transform=[30, 0, 0, 0, -30, 0]),
                       lambda r: r["boundary"]["properties"].update(shapeName="Pastaza"),
                       lambda r: r["scenes"][0]["scene_ids"].pop(),
                       lambda r: r["processing_block"]["bbox"].__setitem__(0, -78),
                       lambda r: r["scenes"][1]["acquired_ms"].__setitem__(0, 0)]:
            invalid = copy.deepcopy(self.receipt)
            mutate(invalid)
            with self.assertRaises(ValueError):
                builder.validate_receipt(invalid, self.config)
        empty = {"type": "FeatureCollection", "features": []}
        self.assertEqual(builder.validate_candidates(empty), empty)
        with self.assertRaises(ValueError):
            builder.validate_candidates({"type": "FeatureCollection", "features": [{"geometry": {"type": "Point", "coordinates": [-77.8, -1.0]}, "properties": {"status": "confirmed"}}]})

    def test_pinned_receipt_rejects_substitution_and_repeated_pass_tile(self):
        config, receipt = copy.deepcopy(self.config), copy.deepcopy(self.receipt)
        for row in receipt["scenes"]:
            row["scene_ids"] = [f'{row["year"]}01{day + 1:02d}T153629_{row["year"]}01{day + 1:02d}T163629_T17MRU' for day in range(10)]
        config["scene_selection"] = {"mode": "frozen-inventory-acquisition-tile-latest-generation-v1", "no_refill": True,
            "plan_sha256": "a" * 64, "source_manifest_sha256": "b" * 64,
            "pinned_scene_ids": [list(row["scene_ids"]) for row in receipt["scenes"]]}
        receipt["scene_selection"] = copy.deepcopy(config["scene_selection"])
        builder.validate_receipt(receipt, config)
        substituted = copy.deepcopy(receipt)
        substituted["scenes"][0]["scene_ids"][0] = "wrong"
        with self.assertRaisesRegex(ValueError, "differ from pinned"):
            builder.validate_receipt(substituted, config)
        repeated = copy.deepcopy(receipt)
        repeated["scenes"][0]["scene_ids"][1] = repeated["scenes"][0]["scene_ids"][0].replace("T163629_", "T173629_")
        duplicate_config = copy.deepcopy(config)
        duplicate_config["scene_selection"]["pinned_scene_ids"][0] = list(repeated["scenes"][0]["scene_ids"])
        repeated["scene_selection"] = copy.deepcopy(duplicate_config["scene_selection"])
        with self.assertRaisesRegex(ValueError, "Repeated pass/tile"):
            builder.validate_receipt(repeated, duplicate_config)

    def test_pinned_cli_requires_isolated_staging_before_reading_inputs(self):
        config = copy.deepcopy(self.config)
        config["scene_selection"]["mode"] = "frozen-inventory-acquisition-tile-latest-generation-v1"
        with tempfile.TemporaryDirectory() as folder:
            config_path = Path(folder) / "fixture-config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            for script in ["build_napo_rivers.py", "build_napo_river_changes.py"]:
                result = subprocess.run([sys.executable, str(ROOT / "scripts" / script), "--inputs", "never-read.tif", "--receipt", "never-read.geojson", "--config", str(config_path)],
                    cwd=ROOT, capture_output=True, text=True, timeout=15)
                self.assertEqual(result.returncode, 1)
                self.assertIn("isolated --output-root under tmp/", result.stderr)

    def test_lossless_paired_pyramid_and_reject_upscaled_30m(self):
        import numpy as np
        import rasterio
        from rasterio.transform import from_origin
        from rasterio.warp import transform_bounds
        from PIL import Image
        bbox = [-77.9, -1.01, -77.899, -1.009]
        extent = transform_bounds("EPSG:4326", "EPSG:3857", *bbox)
        west, north = __import__("math").floor(extent[0] / 10) * 10, __import__("math").ceil(extent[3] / 10) * 10
        width, height = __import__("math").ceil((extent[2] - west) / 10), __import__("math").ceil((north - extent[1]) / 10)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source, receipt, cells = root / "fixture.tif", root / "receipt.geojson", root / "cells.geojson"
            receipt.write_text(json.dumps({"type": "FeatureCollection", "features": [{"properties": {"receipt": json.dumps(self.receipt)}}]}), encoding="utf-8")
            cells.write_text('{"type":"FeatureCollection","features":[]}', encoding="utf-8")
            array = np.zeros((8, height, width), dtype="uint8")
            array[[0, 1, 2, 4, 5, 6]] = 80
            array[[3, 7]] = 255
            array[:, 0, 0] = 0
            with rasterio.open(source, "w", driver="GTiff", width=width, height=height, count=8, dtype="uint8", crs="EPSG:3857", transform=from_origin(west, north, 10, 10)) as dest:
                dest.write(array)
                dest.descriptions = tuple(self.config["export_bands"])
            result = builder.build_bundle([source], receipt, cells, root / "public", self.config)
            self.assertEqual(result["candidate_count"], 0)
            self.assertEqual(result["sampling_m"], 10)
            self.assertTrue(result["tiles"])
            native = [row for row in result["tiles"] if "/13/" in row["url"]]
            for row in native:
                path = root / "public" / row["url"]
                self.assertEqual(builder.digest(path), row["sha256"])
                with Image.open(path) as image:
                    self.assertEqual(image.size, (512, 512))
                    pixels = np.asarray(image.convert("RGBA"))
                    self.assertTrue(np.isin(pixels[:, :, 3], [0, 255]).all())
                    self.assertTrue((pixels[pixels[:, :, 3] == 255, :3] == 80).all())
            manifest_path = root / "public/data/rivers/napo-manifest.json"
            previous = manifest_path.read_bytes()
            rgb_only = builder.build_bundle([source], receipt, None, root / "rgb-only", self.config)
            self.assertEqual(rgb_only["candidate_status"], "pending")
            self.assertIsNone(rgb_only["candidate_count"])
            self.assertIsNone(rgb_only["candidates_sha256"])
            self.assertFalse((root / "rgb-only/data/rivers/napo-candidates.geojson").exists())
            with rasterio.open(source, "r+") as dest:
                dest.transform = from_origin(west - 1000, north, 10, 10)
            with self.assertRaises(ValueError):
                builder.build_bundle([source], receipt, cells, root / "public", self.config)
            self.assertEqual(manifest_path.read_bytes(), previous)
            with rasterio.open(source, "r+") as dest:
                dest.transform = from_origin(west, north, 30, 30)
            with self.assertRaises(ValueError):
                builder.build_bundle([source], receipt, cells, root / "public", self.config)
            self.assertEqual(manifest_path.read_bytes(), previous)
            with self.assertRaises(ValueError):
                builder.build_bundle([], receipt, cells, root / "public", self.config)


if __name__ == "__main__":
    unittest.main()
