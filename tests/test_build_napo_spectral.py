"""Synthetic test-only rasters stay in temporary folders, never public assets."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("spectral_builder", ROOT / "scripts/build_napo_spectral.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
CONFIG = json.loads((ROOT / "data/spectral/napo-config.json").read_text(encoding="utf-8"))
AVAILABLE = all(importlib.util.find_spec(module) for module in ["numpy", "rasterio", "PIL"])


def receipt_for(config):
    from datetime import datetime, timezone
    return {"schema_version": 1, "asset": config["source"]["asset"],
            "quality_asset": config["source"]["quality_asset"],
            **{key: config[key] for key in builder.RECEIPT_FIELDS},
            "reflectance_scale": 0.0001, "export_resampling": "nearest",
            "export_requested_at": "2026-09-30T00:00:00Z",
            "scenes": [{"year": year, "period": period, "source_count": 3, "joined_count": 3,
                        "scene_ids": [f"test-only-{year}-{letter}" for letter in "abc"],
                        "acquired_ms": [datetime.fromisoformat(period[0]).replace(tzinfo=timezone.utc).timestamp() * 1000] * 3}
                       for year, period in zip(config["years"], config["periods"])]}


class SpectralReceiptTests(unittest.TestCase):
    def test_provenance_and_quality_rejected_when_inconsistent(self):
        receipt = receipt_for(CONFIG)
        builder.validate_receipt(receipt, CONFIG)
        mutations = [lambda item: item.update(clear_threshold=0.3),
                     lambda item: item["scenes"][0].update(scene_ids=["same"] * 3),
                     lambda item: item["scenes"][1].update(acquired_ms=[1735689600000] * 3),
                     lambda item: item["scenes"][0].update(source_count=801),
                     lambda item: item["scenes"][0].update(joined_count=True),
                     lambda item: item.update(export_requested_at="2026-09-30T00:00:00")]
        for mutation in mutations:
            invalid = copy.deepcopy(receipt)
            mutation(invalid)
            with self.assertRaises(ValueError):
                builder.validate_receipt(invalid, CONFIG)


@unittest.skipUnless(AVAILABLE, "Install requirements-landcover.txt for spectral pipeline tests")
class SpectralRasterTests(unittest.TestCase):
    def fixture(self, root):
        import numpy as np
        import rasterio
        from rasterio.transform import from_origin
        from rasterio.warp import transform_bounds
        from PIL import Image
        config = copy.deepcopy(CONFIG)
        # Integer multiples of the global 30 m grid; only four by four fictitious cells.
        transform = from_origin(170010, 9900000, 30, 30)
        config["bbox"] = list(transform_bounds(config["export_crs"], "EPSG:4326", 170010, 9899880, 170130, 9900000))
        config["river_focus_bbox"] = config["bbox"]
        array = np.full((16, 4, 4), 0.1, dtype="float32")
        for base in (0, 8):
            array[base + 3] = 0.3
            array[base + 4] = 0.05
            array[base + 5] = 0.5
            array[base + 6] = (0.1 - 0.05) / (0.1 + 0.05)
            array[base + 7] = 3
            array[base + 3, 3, 3] = 0.1
            array[base + 4, 3, 3] = 0.1
            array[base + 5:base + 7, 3, 3] = 0  # true index zero must be opaque
            # Black RGB is valid data, with positive index denominators.
            array[base:base + 3, 2, 2] = 0
            array[base + 5, 2, 2] = 1
            array[base + 6, 2, 2] = -1
        array[:7, 0, 0] = -9999; array[7, 0, 0] = 2
        array[8:15, 0, 1] = -9999; array[15, 0, 1] = 2
        raster, receipt_path = root / "test-only.tif", root / "receipt.geojson"
        with rasterio.open(raster, "w", driver="GTiff", count=16, width=4, height=4,
                           dtype="float32", crs=config["export_crs"], transform=transform, nodata=-9999) as dst:
            dst.write(array)
            bands = [f"y{year}_{band}" for year in config["years"] for band in config["year_bands"]]
            for index, band in enumerate(bands, 1): dst.set_band_description(index, band)
        receipt_path.write_text(json.dumps({"type": "FeatureCollection", "features": [{"properties": {"receipt": json.dumps(receipt_for(config))}}]}), encoding="utf-8")
        grid = root / "grid.png"
        # Transparent reference proves its alpha is NOT used as an analysis mask.
        Image.fromarray(np.zeros((4, 4, 4), dtype="uint8")).save(grid)
        w, s, e, n = config["bbox"]
        landcover = {"status": "ready", "bbox": config["bbox"], "display_crs": "EPSG:3857",
                     "display_bounds": [[s, w], [n, e]],
                     "images": [{"year": 2024, "url": "grid.png", "sha256": builder.sha256(grid)}]}
        return config, landcover, raster, receipt_path, array

    def test_common_mask_zero_reflectance_and_six_views(self):
        import numpy as np
        from PIL import Image
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            config, landcover, raster, receipt_path, _ = self.fixture(root)
            manifest = builder.build_bundle(raster, receipt_path, root, config, landcover)
            self.assertEqual(manifest["statistics"]["window_pixels"], 16)
            self.assertEqual(manifest["statistics"]["common_pixels"], 14)
            self.assertEqual([item["usable_pixels"] for item in manifest["statistics"]["years"]], [15, 15])
            self.assertEqual(len(manifest["images"]), 6)
            alphas = []
            palettes = {}
            for row in manifest["images"]:
                with Image.open(root / row["url"]) as image:
                    alphas.append(np.array(image.convert("RGBA"))[:, :, 3])
                    if row["mode"] != "rgb":
                        self.assertEqual(image.mode, "P")
                        self.assertEqual(image.info["transparency"], 0)
                        self.assertEqual(np.array(image)[3, 3], 65)
                        self.assertEqual(alphas[-1][3, 3], 255)
                        if row["mode"] in palettes:
                            self.assertEqual(image.getpalette(), palettes[row["mode"]])
                        palettes[row["mode"]] = image.getpalette()
                self.assertEqual(builder.sha256(root / row["url"]), row["sha256"])
            for alpha in alphas[1:]: np.testing.assert_array_equal(alpha, alphas[0])
            self.assertEqual(alphas[0][2, 2], 255)
            self.assertIn(0, alphas[0])
            self.assertEqual(manifest["grid_reference_sha256"], landcover["images"][0]["sha256"])

    def test_invalid_rasters_and_receipt_preserve_published_bundle(self):
        import rasterio
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            config, landcover, raster, receipt_path, array = self.fixture(root)
            builder.build_bundle(raster, receipt_path, root, config, landcover)
            manifest_path = root / "data/spectral/napo-manifest.json"
            published = builder.sha256(manifest_path)
            for band, value, message in [(5, 0.7, "formula"), (7, 2.5, "integer"),
                                          (7, 2, "QA minimum"), (3, -0.01, "reflectance"),
                                          (6, -9999, "Index mask")]:
                changed = array.copy(); changed[band, 1, 1] = value
                with rasterio.open(raster, "r+") as dst: dst.write(changed)
                with self.subTest(band=band, value=value), self.assertRaisesRegex(ValueError, message):
                    builder.build_bundle(raster, receipt_path, root, config, landcover)
                self.assertEqual(builder.sha256(manifest_path), published)
            with rasterio.open(raster, "r+") as dst: dst.write(array)
            bad_grid = copy.deepcopy(landcover); bad_grid["images"][0]["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "checksum"):
                builder.build_bundle(raster, receipt_path, root, config, bad_grid)
            receipt_path.write_text('{"type":"FeatureCollection","features":[{}]}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Malformed"):
                builder.build_bundle(raster, receipt_path, root, config, landcover)
            self.assertEqual(builder.sha256(manifest_path), published)

    def test_zero_denominators_are_masked_and_grid_anchor_is_verified(self):
        import rasterio
        from affine import Affine
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            config, landcover, raster, receipt_path, array = self.fixture(root)
            # All-zero reflectance is not NoData, but neither ratio is defined here.
            array[:5, 1, 1] = 0
            array[5:7, 1, 1] = -9999
            with rasterio.open(raster, "r+") as dst: dst.write(array)
            manifest = builder.build_bundle(raster, receipt_path, root, config, landcover)
            self.assertEqual(manifest["statistics"]["common_pixels"], 13)
            array[5:7, 1, 1] = 0  # an invented numerical index is not acceptable
            with rasterio.open(raster, "r+") as dst: dst.write(array)
            with self.assertRaisesRegex(ValueError, "Index mask"):
                builder.build_bundle(raster, receipt_path, root, config, landcover)
            array[5:7, 1, 1] = -9999
            with rasterio.open(raster, "r+") as dst:
                dst.write(array)
                dst.transform = dst.transform * Affine.translation(0.5, 0)
            with self.assertRaisesRegex(ValueError, "anchored"):
                builder.build_bundle(raster, receipt_path, root, config, landcover)


if __name__ == "__main__":
    unittest.main()
