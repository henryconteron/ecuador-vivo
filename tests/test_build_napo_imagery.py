import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("imagery_builder", ROOT / "scripts/build_napo_imagery.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
CONFIG = json.loads((ROOT / "data/imagery/napo-config.json").read_text(encoding="utf-8"))
AVAILABLE = all(importlib.util.find_spec(module) for module in ["numpy", "rasterio", "PIL"])


def receipt_for(config):
    return {"schema_version": 1, "asset": config["source"]["asset"], "quality_asset": config["source"]["quality_asset"],
            **{key: config[key] for key in ["period", "bbox", "bands", "quality_band", "clear_threshold", "min_observations", "excluded_scl", "composite", "export_crs", "export_scale_m"]},
            "nominal_resolution_m": 10, "reflectance_scale": 0.0001, "export_resampling": "nearest",
            "source_count": 3, "joined_count": 3, "scene_ids": ["test-a", "test-b", "test-c"],
            "acquired_ms": [1704067200000] * 3, "export_requested_at": "2026-09-30T00:00:00Z"}


class ImageryReceiptTests(unittest.TestCase):
    def test_quality_and_scene_provenance(self):
        receipt = receipt_for(CONFIG)
        builder.validate_receipt(receipt, CONFIG)
        for key, value in [("clear_threshold", 0.3), ("scene_ids", ["same"] * 3),
                           ("acquired_ms", [1735689600000] * 3), ("joined_count", 0), ("bands", ["B2", "B3", "B4"])]:
            invalid = copy.deepcopy(receipt); invalid[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                builder.validate_receipt(invalid, CONFIG)


@unittest.skipUnless(AVAILABLE, "Install requirements-landcover.txt for imagery pipeline tests")
class ImageryRasterTests(unittest.TestCase):
    def test_build_common_mask_and_dark_pixels(self):
        import numpy as np
        import rasterio
        from rasterio.transform import from_origin
        from rasterio.warp import transform_bounds
        from PIL import Image
        # All fictitious rasters are confined to this temporary directory.
        config = copy.deepcopy(CONFIG)
        transform = from_origin(170000, 9900000, 30, 30)
        config["bbox"] = list(transform_bounds(config["export_crs"], "EPSG:4326", 170000, 9899880, 170120, 9900000))
        w, s, e, n = config["bbox"]
        receipt = receipt_for(config)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            raster = root / "synthetic.tif"; receipt_path = root / "receipt.geojson"
            array = np.full((4, 4, 4), 1000, dtype="uint16")
            array[3] = 3
            array[:3, 0, 0] = 65535; array[3, 0, 0] = 2
            array[:3, 2, 2] = 0  # dark reflectance is data, not NoData
            with rasterio.open(raster, "w", driver="GTiff", count=4, width=4, height=4, dtype="uint16",
                               crs=config["export_crs"], transform=transform, nodata=65535) as dst:
                dst.write(array)
                for index, band in enumerate(config["bands"], 1): dst.set_band_description(index, band)
            receipt_path.write_text(json.dumps({"type": "FeatureCollection", "features": [{"properties": {"receipt": json.dumps(receipt)}}]}), encoding="utf-8")
            class_path = root / "classification.png"
            Image.fromarray(np.full((4, 4, 4), 255, dtype="uint8")).save(class_path)
            landcover = {"status": "ready", "bbox": config["bbox"], "display_crs": "EPSG:3857",
                         "display_bounds": [[s, w], [n, e]], "images": [{"year": 2024, "url": "classification.png", "sha256": builder.sha256(class_path)}]}
            manifest = builder.build_bundle(raster, receipt_path, root, config, landcover)
            self.assertEqual(manifest["statistics"]["window_pixels"], 16)
            self.assertEqual(manifest["statistics"]["usable_pixels"], 15)
            self.assertEqual(manifest["statistics"]["min_clear_scenes"], 3)
            with Image.open(root / manifest["images"][0]["url"]) as optical, Image.open(root / manifest["images"][1]["url"]) as classes:
                alpha = np.array(optical)[:, :, 3]
                np.testing.assert_array_equal(alpha, np.array(classes)[:, :, 3])
                self.assertIn(0, alpha)
                self.assertEqual(alpha[2, 2], 255)
            published_sha = builder.sha256(root / "data/imagery/napo-manifest.json")
            # Bad QA must not overwrite a valid published bundle.
            with rasterio.open(raster, "r+") as dst:
                array[3, 2, 2] = 1; dst.write(array)
            with self.assertRaisesRegex(ValueError, "below the stated QA minimum"):
                builder.build_bundle(raster, receipt_path, root, config, landcover)
            self.assertEqual(builder.sha256(root / "data/imagery/napo-manifest.json"), published_sha)


if __name__ == "__main__":
    unittest.main()
