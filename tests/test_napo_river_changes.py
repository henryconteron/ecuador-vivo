"""Screening fixtures stay in temporary folders, never in public atlas data."""
import copy
import json
import math
from pathlib import Path
import tempfile
import unittest

import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import transform_bounds
from scripts import build_napo_river_changes as changes
from scripts import build_napo_rivers as rgb


class ChangeTests(unittest.TestCase):
    def test_components_diagonal_seams_and_holes(self):
        mask = np.zeros((25, 25), dtype=bool)
        mask[0:10, 0:10] = True
        mask[5, 5] = False
        mask[10, 10] = True  # 8-connectivity joins across the diagonal: 100.
        result = changes.retained_components(mask)
        self.assertEqual(int(result.sum()), 100)
        self.assertFalse(result[5, 5])
        mask[10, 10] = False
        self.assertFalse(changes.retained_components(mask).any())

    def test_exact_threshold_and_no_uint8_overflow(self):
        counts = np.zeros((4, 20, 20), dtype=np.uint8)
        counts[1] = counts[3] = 32
        counts[2] = 16  # exactly 0.5 frequency increase
        gain, loss, valid = changes.change_masks(counts, [32, 32])
        self.assertTrue(gain.all())
        self.assertFalse(loss.any())
        self.assertTrue(valid.all())
        counts[2] = 15
        self.assertFalse(changes.change_masks(counts, [32, 32])[0].any())
        counts[0] = 16
        counts[2] = 0
        self.assertTrue(changes.change_masks(counts, [32, 32])[1].all())
        counts[0] = 33
        with self.assertRaises(ValueError):
            changes.change_masks(counts, [32, 32])

    def test_zero_water_is_not_nodata(self):
        counts = np.zeros((4, 12, 12), dtype=np.uint8)
        counts[1] = counts[3] = 10
        gain, loss, valid = changes.change_masks(counts, [10, 10])
        self.assertFalse(gain.any() or loss.any())
        self.assertTrue(valid.all())
        counts[3] = 9
        with self.assertRaises(ValueError):
            changes.change_masks(counts, [10, 10])

    def test_fixed_cell_origin_and_area(self):
        mask = np.zeros((100, 100), dtype=bool)
        mask[0:10, 0:10] = True
        collection = changes.aggregate_cells(mask, np.zeros_like(mask), np.ones_like(mask), from_origin(-8669000, -111000, 10, 10))
        self.assertEqual(len(collection["features"]), 1)
        p = collection["features"][0]["properties"]
        self.assertEqual(p["gain_ha"], 1)
        self.assertEqual(p["cell_id"], -8669 + 111 * 100000)
        mask[0, 0] = False
        self.assertEqual(changes.aggregate_cells(mask, np.zeros_like(mask), np.ones_like(mask), from_origin(-8669000, -111000, 10, 10))["features"], [])

    def test_real_grid_pipeline_seam_and_failure_preserve_manifest(self):
        config = json.loads((rgb.ROOT / "data/rivers/napo-config.json").read_text(encoding="utf-8"))
        config["processing_grid"]["bbox"] = [-77.901, -1.01, -77.898, -1.007]
        receipt = copy.deepcopy(json.loads((rgb.ROOT / "data/rivers/napo-manifest.json").read_text(encoding="utf-8"))["receipt"])
        receipt["processing_grid"] = config["processing_grid"]
        receipt["processing_block"] = {"id": 7, "bbox": [-77.9, -1.01, -77.899, -1.009]}
        receipt["boundary"]["geometry"] = {"type": "Polygon", "coordinates": [[[-77.9, -1.01], [-77.899, -1.01], [-77.899, -1.009], [-77.9, -1.009], [-77.9, -1.01]]]}
        extent = transform_bounds("EPSG:4326", "EPSG:3857", *receipt["processing_block"]["bbox"])
        west, north = math.floor(extent[0] / 10) * 10, math.ceil(extent[3] / 10) * 10
        width, height = math.ceil((extent[2] - west) / 10), math.ceil((north - extent[1]) / 10)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            public = root / "data/rivers"
            public.mkdir(parents=True)
            tile = root / "assets/images/rivers/test-only.bin"
            tile.parent.mkdir(parents=True)
            tile.write_bytes(b"isolated fixture only")
            manifest = {"status": "ready", "config": config, "receipt": receipt, "receipt_sha256": "a" * 64,
                        "tiles": [{"url": "assets/images/rivers/test-only.bin", "sha256": rgb.digest(tile), "size_bytes": tile.stat().st_size}]}
            manifest_path = public / "napo-manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            count_receipt = copy.deepcopy(receipt)
            count_receipt.update(product="water-observation-counts", count_bands=changes.COUNT_BANDS, count_dtype="uint8", count_encoding=changes.ENCODING)
            receipt_path = root / "receipt.geojson"
            def write_receipt():
                receipt_path.write_text(json.dumps({"type": "FeatureCollection", "features": [{"properties": {"receipt": json.dumps(count_receipt)}}]}), encoding="utf-8")
            write_receipt()
            array = np.zeros((4, height, width), dtype=np.uint8)
            array[1] = array[3] = 10
            array[2] = 10
            paths = [root / "left.tif", root / "right.tif"]
            middle = width // 2
            for path, start, stop in [(paths[0], 0, middle), (paths[1], middle, width)]:
                with rasterio.open(path, "w", driver="GTiff", width=stop - start, height=height, count=4, dtype="uint8", crs="EPSG:3857", transform=from_origin(west + start * 10, north, 10, 10)) as dest:
                    dest.write(array[:, :, start:stop])
                    dest.descriptions = tuple(changes.COUNT_BANDS)
            result = changes.build_changes(paths, receipt_path, root, config)
            self.assertGreaterEqual(result["screening"]["retained_pixels"]["gain"], 100)  # each individual chunk <100
            self.assertEqual(result["tiles"], manifest["tiles"])
            self.assertEqual(result["candidate_status"], "ready")
            previous = manifest_path.read_bytes()
            previous_cells = (public / "napo-candidates.geojson").read_bytes()
            with self.assertRaises(ValueError):
                changes.build_changes(paths[:1], receipt_path, root, config)
            count_receipt["scenes"][0]["scene_ids"][0] = "different-scene"
            write_receipt()
            with self.assertRaises(ValueError):
                changes.build_changes(paths, receipt_path, root, config)
            self.assertEqual(manifest_path.read_bytes(), previous)
            self.assertEqual((public / "napo-candidates.geojson").read_bytes(), previous_cells)


if __name__ == "__main__":
    unittest.main()
