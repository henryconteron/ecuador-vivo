"""Build aligned, traceable Sentinel-2 RGB/NDVI/MNDWI year comparisons.

Indices are checked against native reflectance. They are not mining, water-quality
or land-cover labels. The MapBiomas preview supplies only the display grid.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_FIELDS = ["years", "periods", "bbox", "optical_bands", "year_bands",
                  "quality_band", "clear_threshold", "min_observations", "excluded_scl",
                  "composite", "observation_mask", "index_formulas", "export_crs",
                  "export_transform", "nodata"]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_receipt(receipt, config):
    """Reject incomplete or contradictory export provenance before publishing."""
    if not isinstance(receipt, dict):
        raise ValueError("Receipt must be an object")
    for key in RECEIPT_FIELDS:
        if receipt.get(key) != config[key]:
            raise ValueError(f"Receipt mismatch: {key}")
    expected = {"schema_version": 1, "asset": config["source"]["asset"],
                "quality_asset": config["source"]["quality_asset"],
                "reflectance_scale": 0.0001, "export_resampling": "nearest"}
    for key, value in expected.items():
        if receipt.get(key) != value:
            raise ValueError(f"Receipt mismatch: {key}")
    scenes = receipt.get("scenes")
    if not isinstance(scenes, list) or len(scenes) != len(config["years"]):
        raise ValueError("Missing per-year scene provenance")
    for position, scene in enumerate(scenes):
        if not isinstance(scene, dict) or scene.get("year") != config["years"][position] or scene.get("period") != config["periods"][position]:
            raise ValueError("Scene year/period mismatch")
        joined, source = scene.get("joined_count"), scene.get("source_count")
        if type(joined) is not int or type(source) is not int or not 3 <= joined <= source <= 800:
            raise ValueError("Invalid source scene counts")
        ids, dates = scene.get("scene_ids"), scene.get("acquired_ms")
        if not isinstance(ids, list) or len(ids) != joined or any(not isinstance(item, str) or not item for item in ids) or len(set(ids)) != joined:
            raise ValueError("Missing/duplicate scene provenance")
        if not isinstance(dates, list) or len(dates) != joined:
            raise ValueError("Missing scene dates")
        start, end = [datetime.fromisoformat(value).replace(tzinfo=timezone.utc).timestamp() * 1000 for value in scene["period"]]
        if any(type(value) not in (int, float) or not math.isfinite(value) or not start <= value < end for value in dates):
            raise ValueError("Scene dates outside composition period")
    try:
        requested = datetime.fromisoformat(receipt["export_requested_at"].replace("Z", "+00:00"))
    except (KeyError, TypeError, AttributeError, ValueError) as error:
        raise ValueError("Invalid export timestamp") from error
    if requested.tzinfo is None:
        raise ValueError("Export timestamp needs a timezone")


def _read_receipt(path, config):
    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(document, dict) or document.get("type") != "FeatureCollection" or len(document.get("features", [])) != 1:
            raise ValueError("Expected one-feature Earth Engine receipt")
        encoded = document["features"][0]["properties"]["receipt"]
        if not isinstance(encoded, str):
            raise ValueError("Receipt property must contain JSON text")
        receipt = json.loads(encoded)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
        raise ValueError("Malformed Earth Engine receipt") from error
    validate_receipt(receipt, config)
    return receipt


def _safe_asset(root, relative):
    path = (root / relative).resolve()
    if Path(relative).is_absolute() or not path.is_relative_to(root.resolve()):
        raise ValueError("Grid reference must stay inside output root")
    return path


def _index_colors(values, display):
    import numpy as np
    colors = np.array([[int(color[position:position + 2], 16) for position in (1, 3, 5)]
                       for color in display["palette"]], dtype="float32")
    if colors.shape != (3, 3) or display["min"] != -1 or display["max"] != 1:
        raise ValueError("Indices require a fixed three-color [-1, 0, 1] scale")
    normalized = np.clip(values, -1, 1) + 1
    lower = np.minimum(normalized.astype("int32"), 1)
    fraction = (normalized - lower)[..., None]
    return np.rint(colors[lower] * (1 - fraction) + colors[lower + 1] * fraction).astype("uint8")


def _indexed_image(values, paired, display):
    """Fixed palette, nearest 1/64 visual bins; native indices remain untouched."""
    import numpy as np
    from PIL import Image
    levels = display.get("levels")
    if type(levels) is not int or levels != 129:
        raise ValueError("Index previews require the fixed 129-level palette")
    # 0 exclusively means transparent NoData; valid zero is opaque entry 65.
    codes = 1 + np.rint((np.clip(values, -1, 1) + 1) * ((levels - 1) / 2)).astype("uint8")
    codes[~paired] = 0
    image = Image.fromarray(codes).convert("P")
    palette = np.zeros((256, 3), dtype="uint8")
    palette[1:levels + 1] = _index_colors(np.linspace(-1, 1, levels), display)
    image.putpalette(palette.flatten().tolist())
    image.info["transparency"] = 0
    return image


def build_bundle(input_path, receipt_path, output_root, config, landcover):
    import numpy as np
    import rasterio
    from rasterio.features import geometry_mask
    from rasterio.transform import from_bounds
    from rasterio.warp import reproject, Resampling, transform_bounds, transform_geom
    from PIL import Image

    input_path, receipt_path, output_root = Path(input_path), Path(receipt_path), Path(output_root)
    receipt = _read_receipt(receipt_path, config)
    if landcover.get("status") != "ready" or landcover.get("bbox") != config["bbox"] or landcover.get("display_crs") != "EPSG:3857":
        raise ValueError("Missing matching ready display grid")
    references = [row for row in landcover.get("images", []) if row.get("year") == 2024]
    if len(references) != 1:
        raise ValueError("Missing unique 2024 display-grid reference")
    reference = references[0]
    grid_path = _safe_asset(output_root, reference["url"])
    if sha256(grid_path) != reference["sha256"]:
        raise ValueError("Display-grid reference checksum differs")
    with Image.open(grid_path) as grid_image:
        width, height = grid_image.size
    if not 0 < width * height <= 5000000:
        raise ValueError("Display grid too large/empty")
    # Its colors and alpha are deliberately never read: this is not a land-cover mask.
    bounds = landcover["display_bounds"]
    try:
        south, west = bounds[0]
        north, east = bounds[1]
        if not all(math.isfinite(value) for value in [west, south, east, north]) or not west < east or not south < north:
            raise ValueError("Invalid display bounds")
        if any(abs(a - b) > 0.002 for a, b in zip([west, south, east, north], config["bbox"])):
            raise ValueError("Display bounds differ from study window")
    except (TypeError, IndexError) as error:
        raise ValueError("Invalid display bounds") from error
    projected = transform_bounds("EPSG:4326", "EPSG:3857", west, south, east, north)
    destination_transform = from_bounds(*projected, width, height)
    west, south, east, north = config["bbox"]
    polygon = {"type": "Polygon", "coordinates": [[[west, south], [east, south], [east, north], [west, north], [west, south]]]}
    expected_bands = [f"y{year}_{band}" for year in config["years"] for band in config["year_bands"]]
    with rasterio.open(input_path) as src:
        if src.count != 16 or src.crs != rasterio.crs.CRS.from_string(config["export_crs"]) or src.nodata != config["nodata"]:
            raise ValueError("Expected 16-band projected Sentinel export, NoData=-9999")
        if not 0 < src.width * src.height <= 5000000 or any(dtype != "float32" for dtype in src.dtypes):
            raise ValueError("Unexpected raster size/type")
        if list(src.descriptions) != expected_bands:
            raise ValueError("Band order not verified by GeoTIFF descriptions")
        a, b, c, d, e, f = config["export_transform"]
        if not np.allclose([src.transform.a, src.transform.b, src.transform.d, src.transform.e], [a, b, d, e], atol=1e-8, rtol=0):
            raise ValueError("Export sampling must match the 30m grid")
        offset = [(src.transform.c - c) / a, (src.transform.f - f) / e]
        if not np.allclose(offset, np.rint(offset), atol=1e-7, rtol=0):
            raise ValueError("Raster origin is not anchored to export grid")
        extent = transform_bounds(src.crs, "EPSG:4326", *src.bounds)
        if extent[0] > west + 0.0004 or extent[1] > south + 0.0004 or extent[2] < east - 0.0004 or extent[3] < north - 0.0004:
            raise ValueError("Raster does not cover study window")
        if any(abs(value - limit) > 0.02 for value, limit in zip(extent, config["bbox"])):
            raise ValueError("Raster extent is inconsistent with study window")
        data, masks = src.read(), src.read_masks() > 0
        inside = geometry_mask([transform_geom("EPSG:4326", src.crs, polygon)],
                               out_shape=(src.height, src.width), transform=src.transform, invert=True)
        year_valid, year_stats = [], []
        for position, year in enumerate(config["years"]):
            base = position * 8
            optical = data[base:base + 5]
            optical_masks = masks[base:base + 5]
            if np.any(inside & np.any(optical_masks != optical_masks[0], axis=0)):
                raise ValueError("Five optical bands do not share a joint mask")
            optical_valid = inside & optical_masks.all(axis=0)
            if np.any(~np.isfinite(optical[:, optical_valid])) or np.any(optical[:, optical_valid] < 0) or np.any(optical[:, optical_valid] > 6.5535):
                raise ValueError("Invalid scaled optical reflectance")
            counts = data[base + 7]
            count_valid = inside & masks[base + 7]
            observed_counts = counts[count_valid]
            if np.any(~np.isfinite(observed_counts)) or np.any(observed_counts < 0) or np.any(observed_counts > receipt["scenes"][position]["joined_count"]) or np.any(observed_counts != np.rint(observed_counts)):
                raise ValueError("Invalid integer usable scene count")
            if np.any(optical_valid & (~count_valid | (counts < config["min_observations"]))):
                raise ValueError("Optical pixels below the stated QA minimum")
            for index, first, second in [(5, 3, 0), (6, 1, 4)]:
                denominator = optical[first] + optical[second]
                expected_valid = optical_valid & (denominator > 0)
                actual_valid = inside & masks[base + index]
                if not np.array_equal(expected_valid, actual_valid):
                    raise ValueError("Index mask disagrees with positive-denominator reflectance")
                expected = (optical[first][expected_valid] - optical[second][expected_valid]) / denominator[expected_valid]
                actual = data[base + index][expected_valid]
                if np.any(~np.isfinite(actual)) or not np.allclose(actual, expected, atol=1e-5, rtol=0):
                    raise ValueError("Index formula does not match native median reflectance")
            valid = optical_valid & masks[base + 5] & masks[base + 6]
            if not valid.any():
                raise ValueError(f"No usable optical/index pixels for {year}")
            year_valid.append(valid)
            year_stats.append({"year": year, "usable_pixels": int(valid.sum()),
                               "min_clear_scenes": int(counts[valid].min()),
                               "median_clear_scenes": float(np.median(counts[valid])),
                               "max_clear_scenes": int(counts[valid].max())})
        common = np.logical_and.reduce(year_valid)
        if not common.any():
            raise ValueError("No common-support pixels between years")
        display_valid = np.zeros((height, width), dtype="uint8")
        reproject(common.astype("uint8"), display_valid, src_transform=src.transform, src_crs=src.crs,
                  dst_transform=destination_transform, dst_crs="EPSG:3857", resampling=Resampling.nearest)
        paired = display_valid > 0
        if not paired.any():
            raise ValueError("No paired display pixels")
        alpha = paired.astype("uint8") * 255
        stats = {"window_pixels": int(inside.sum()), "common_pixels": int(common.sum()),
                 "paired_display_pixels": int(paired.sum()), "years": year_stats}
        output_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="napo-spectral-", dir=output_root) as staging_name:
            staging, files = Path(staging_name), []
            for position, year in enumerate(config["years"]):
                for mode, indices in [("rgb", [0, 1, 2]), ("ndvi", [5]), ("mndwi", [6])]:
                    sampled = np.zeros((len(indices), height, width), dtype="float32")
                    for output_band, source_band in enumerate(indices):
                        reproject(np.where(common, data[position * 8 + source_band], config["nodata"]), sampled[output_band],
                                  src_transform=src.transform, src_crs=src.crs, dst_transform=destination_transform,
                                  dst_crs="EPSG:3857", src_nodata=config["nodata"], dst_nodata=0,
                                  resampling=Resampling.bilinear if mode == "rgb" else Resampling.nearest)
                    if mode == "rgb":
                        stretch = config["display"]["rgb"]
                        normalized = np.clip((sampled - stretch["reflectance_min"]) / (stretch["reflectance_max"] - stretch["reflectance_min"]), 0, 1)
                        colors = np.rint(255 * normalized ** (1 / stretch["gamma"])).astype("uint8").transpose(1, 2, 0)
                    name = f"napo-{mode}-{year}.{'webp' if mode == 'rgb' else 'png'}"
                    temporary = staging / name
                    if mode == "rgb":
                        image = Image.fromarray(np.dstack([colors, alpha]))
                        image.save(temporary, format="WEBP", quality=88, method=6)
                    else:
                        image = _indexed_image(sampled[0], paired, config["display"][mode])
                        image.save(temporary, optimize=True, transparency=0)
                    files.append({"year": year, "mode": mode, "url": f"assets/images/spectral/{name}", "sha256": sha256(temporary)})
            manifest = {"schema_version": 1, "status": "ready", "source": config["source"],
                        "years": config["years"], "periods": config["periods"], "bbox": config["bbox"],
                        "scope": config["scope"], "river_focus_bbox": config["river_focus_bbox"],
                        "context_source": config["context_source"], "display": config["display"],
                        "display_bounds": bounds, "display_crs": "EPSG:3857", "display_sampling_m": 30,
                        "width": width, "height": height, "reflectance_resampling": "bilinear",
                        "index_resampling": "nearest", "mask_resampling": "nearest",
                        "input_sha256": sha256(input_path), "receipt_sha256": sha256(receipt_path),
                        "grid_reference_sha256": reference["sha256"], "receipt": receipt,
                        "statistics": stats, "images": files, "built_at": datetime.now(timezone.utc).isoformat()}
            # All validation/rendering succeeds before replacing any public bundle files.
            manifest_file = staging / "manifest.json"
            manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            for row in files:
                target = output_root / row["url"]
                target.parent.mkdir(parents=True, exist_ok=True)
                (staging / Path(row["url"]).name).replace(target)
            target = output_root / "data/spectral/napo-manifest.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            manifest_file.replace(target)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads((ROOT / "data/spectral/napo-config.json").read_text(encoding="utf-8"))
    landcover = json.loads((ROOT / "data/landcover/napo-manifest.json").read_text(encoding="utf-8"))
    try:
        manifest = build_bundle(args.input, args.receipt, ROOT, config, landcover)
    except (ValueError, KeyError, FileNotFoundError) as error:
        parser.exit(1, f"Build stopped: {error}\n")
    print(f'Ready: {manifest["statistics"]["common_pixels"]} common native pixels; six aligned views')


if __name__ == "__main__":
    main()
