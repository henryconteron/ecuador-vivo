import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("napo_builder", ROOT / "scripts/build_napo_landcover.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
CONFIG = json.loads((ROOT / "data/landcover/napo-config.json").read_text(encoding="utf-8"))
AVAILABLE = all(importlib.util.find_spec(module) for module in ["numpy", "rasterio", "PIL"])


@unittest.skipUnless(AVAILABLE, "Install requirements-landcover.txt for raster pipeline tests")
class NapoLandcoverTests(unittest.TestCase):
    def test_common_mask_and_unknown_codes(self):
        import numpy as np
        before = np.array([[3, 3, 27], [21, 0, 3]], dtype="uint8")
        after = np.array([[3, 21, 3], [21, 3, 27]], dtype="uint8")
        valid = np.ones(before.shape, dtype=bool)
        stats, _ = builder.summarize(before, after, valid, valid, CONFIG["legend"])
        self.assertEqual(stats["common_observed_pixels"], 3)
        self.assertEqual(stats["observed_pixels"], [4, 5])
        self.assertEqual(stats["changed_class_pixels"], 1)
        self.assertEqual(stats["top_transitions"], [{"from": 3, "to": 21, "pixels": 1}])
        for index in [0, 1]:
            self.assertEqual(sum(row["pixels"][index] for row in stats["classes"]), 3)
        before[0, 0] = 99
        with self.assertRaisesRegex(ValueError, "Unknown classification"):
            builder.summarize(before, after, valid, valid, CONFIG["legend"])

    def test_end_to_end_and_receipt_rejection(self):
        import numpy as np
        import rasterio
        from rasterio.transform import from_origin
        from PIL import Image
        # Tiny SYNTHETIC test window; always isolated in a temporary directory.
        config = copy.deepcopy(CONFIG)
        resolution = 30 / 111319.49079327358
        config["bbox"] = [-78, -resolution * 4, -78 + resolution * 4, 0]
        transform = from_origin(-78, 0, resolution, resolution)
        receipt = {"schema_version": 1, "asset": config["source"]["asset"], "version": "V1.0",
                   "years": config["years"], "bbox": config["bbox"], "license": "CC-BY-4.0",
                   "source_url": config["source"]["url"], "nominal_resolution_m": 30, "native_scale_m": 30,
                   "crs": "EPSG:4326", "crs_transform": list(transform)[:6],
                   "band_order": ["classification_2000", "classification_2024"], "export_requested_at": "2026-09-30T00:00:00Z"}
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            raster = base / "synthetic.tif"
            receipt_path = base / "receipt.geojson"
            def write_receipt():
                receipt_path.write_text(json.dumps({"type": "FeatureCollection", "features": [{"properties": {"receipt": json.dumps(receipt)}}]}), encoding="utf-8")
            with rasterio.open(raster, "w", driver="GTiff", width=4, height=4, count=2,
                               dtype="uint8", crs="EPSG:4326", transform=transform, nodata=0) as src:
                before = np.full((4, 4), 3, dtype="uint8")
                after = before.copy(); after[0, 0] = 21; after[3, 3] = 27
                src.write(before, 1); src.write(after, 2)
            write_receipt()
            manifest = builder.build_bundle(raster, receipt_path, base / "output", config)
            self.assertEqual(manifest["statistics"]["common_observed_pixels"], 15)
            self.assertEqual(manifest["statistics"]["changed_class_pixels"], 1)
            self.assertEqual(manifest["display_resampling"], "nearest")
            with Image.open(base / "output" / manifest["images"][1]["url"]) as image:
                self.assertEqual(image.mode, "RGBA")
                self.assertIn(0, np.array(image)[:, :, 3])
            receipt["version"] = "Collection 4"
            write_receipt()
            with self.assertRaisesRegex(ValueError, "Receipt mismatch"):
                builder.build_bundle(raster, receipt_path, base / "wrong-output", config)
            self.assertFalse((base / "wrong-output").exists())


if __name__ == "__main__":
    unittest.main()
