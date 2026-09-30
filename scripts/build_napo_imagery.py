"""Build a real Sentinel-2/MapBiomas visual comparison on one shared display grid.

Never infer classification accuracy, area change or causes from this comparison.
Reflectance and QA statistics are read from the exported raster, not a web image.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_receipt(receipt, config):
    for key in ["period", "bbox", "bands", "quality_band", "clear_threshold",
                "min_observations", "excluded_scl", "composite", "export_crs", "export_scale_m"]:
        if receipt.get(key) != config[key]:
            raise ValueError(f"Receipt mismatch: {key}")
    for key, value in {"schema_version": 1, "asset": config["source"]["asset"],
                       "quality_asset": config["source"]["quality_asset"],
                       "nominal_resolution_m": 10, "reflectance_scale": 0.0001,
                       "export_resampling": "nearest"}.items():
        if receipt.get(key) != value:
            raise ValueError(f"Receipt mismatch: {key}")
    ids, dates = receipt.get("scene_ids", []), receipt.get("acquired_ms", [])
    count = receipt.get("joined_count", 0)
    if not isinstance(count, int) or not 3 <= count <= 800 or not isinstance(receipt.get("source_count"), int) or receipt["source_count"] < count:
        raise ValueError("Invalid source scene counts")
    if len(ids) != count or len(set(ids)) != count or len(dates) != count or any(not isinstance(x, str) or not x for x in ids):
        raise ValueError("Missing/duplicate scene provenance")
    start, end = [datetime.fromisoformat(x).replace(tzinfo=timezone.utc).timestamp() * 1000 for x in config["period"]]
    if any(not isinstance(x, (int, float)) or not start <= x < end for x in dates):
        raise ValueError("Scene dates outside composition period")
    datetime.fromisoformat(receipt["export_requested_at"].replace("Z", "+00:00"))


def build_bundle(input_path, receipt_path, output_root, config, landcover):
    import numpy as np
    import rasterio
    from rasterio.features import geometry_mask
    from rasterio.transform import from_bounds
    from rasterio.warp import reproject, Resampling, transform_bounds, transform_geom
    from PIL import Image

    input_path, receipt_path, output_root = Path(input_path), Path(receipt_path), Path(output_root)
    document = json.loads(receipt_path.read_text(encoding="utf-8"))
    if document.get("type") != "FeatureCollection" or len(document.get("features", [])) != 1:
        raise ValueError("Expected one-feature Earth Engine receipt")
    receipt = json.loads(document["features"][0]["properties"]["receipt"])
    validate_receipt(receipt, config)
    if landcover.get("status") != "ready" or landcover["bbox"] != config["bbox"] or landcover["display_crs"] != "EPSG:3857":
        raise ValueError("Missing matching MapBiomas comparison")
    classification = next(row for row in landcover["images"] if row["year"] == 2024)
    class_path = output_root / classification["url"]
    if sha256(class_path) != classification["sha256"]:
        raise ValueError("MapBiomas preview checksum differs")
    with Image.open(class_path) as image:
        classes = np.array(image.convert("RGBA"))
    classified_display_pixels = int((classes[:, :, 3] > 0).sum())
    height, width = classes.shape[:2]
    if width * height > 5000000:
        raise ValueError("Comparison grid too large")
    bounds = landcover["display_bounds"]
    projected = transform_bounds("EPSG:4326", "EPSG:3857", bounds[0][1], bounds[0][0], bounds[1][1], bounds[1][0])
    destination_transform = from_bounds(*projected, width, height)
    west, south, east, north = config["bbox"]
    polygon = {"type": "Polygon", "coordinates": [[[west, south], [east, south], [east, north], [west, north], [west, south]]]}
    with rasterio.open(input_path) as src:
        if src.count != 4 or src.crs != rasterio.crs.CRS.from_string(config["export_crs"]) or src.nodata != 65535:
            raise ValueError("Expected four-band projected Sentinel export, NoData=65535")
        if src.width * src.height > 5000000 or any(dtype != "uint16" for dtype in src.dtypes):
            raise ValueError("Unexpected raster size/type")
        if list(src.descriptions) != config["bands"]:
            raise ValueError("Band order not verified by GeoTIFF descriptions")
        if not np.allclose([src.transform.a, src.transform.b, src.transform.d, src.transform.e], [30, 0, 0, -30], atol=1e-8):
            raise ValueError("Export sampling must be 30m, without rotation")
        extent = transform_bounds(src.crs, "EPSG:4326", *src.bounds)
        if extent[0] > west + 0.0004 or extent[1] > south + 0.0004 or extent[2] < east - 0.0004 or extent[3] < north - 0.0004:
            raise ValueError("Raster does not cover study window")
        data = src.read()
        inside = geometry_mask([transform_geom("EPSG:4326", src.crs, polygon)],
                              out_shape=(src.height, src.width), transform=src.transform, invert=True)
        count_valid = inside & (src.read_masks(4) > 0)
        counts = data[3]
        if np.any(counts[count_valid] > receipt["joined_count"]):
            raise ValueError("Impossible usable scene count")
        rgb_valid = inside & (src.read_masks()[:3] > 0).all(axis=0)
        valid = count_valid & (counts >= config["min_observations"]) & rgb_valid
        if np.any(rgb_valid & (~count_valid | (counts < config["min_observations"]))):
            raise ValueError("RGB includes pixels below the stated QA minimum")
        if not valid.any():
            raise ValueError("No usable optical pixels")
        display_valid = np.zeros((height, width), dtype="uint8")
        reproject(valid.astype("uint8"), display_valid, src_transform=src.transform, src_crs=src.crs,
                  dst_transform=destination_transform, dst_crs="EPSG:3857", resampling=Resampling.nearest)
        rgb = np.zeros((3, height, width), dtype="float32")
        for band in range(3):
            reproject(np.where(valid, data[band].astype("float32") * 0.0001, -9999), rgb[band],
                      src_transform=src.transform, src_crs=src.crs, dst_transform=destination_transform,
                      dst_crs="EPSG:3857", src_nodata=-9999, dst_nodata=0, resampling=Resampling.bilinear)
        paired = (display_valid > 0) & (classes[:, :, 3] > 0)
        if not paired.any():
            raise ValueError("No paired display pixels")
        stretch = config["display"]
        normalized = np.clip((rgb - stretch["reflectance_min"]) / (stretch["reflectance_max"] - stretch["reflectance_min"]), 0, 1)
        rendered = np.rint(255 * normalized ** (1 / stretch["gamma"])).astype("uint8").transpose(1, 2, 0)
        rgba = np.dstack([rendered, paired.astype("uint8") * 255])
        classes[:, :, 3] = paired.astype("uint8") * 255
        stats = {"window_pixels": int(inside.sum()), "usable_pixels": int(valid.sum()),
                 "counted_pixels": int(count_valid.sum()), "min_clear_scenes": int(counts[valid].min()),
                 "median_clear_scenes": float(np.median(counts[valid])), "max_clear_scenes": int(counts[valid].max()),
                 "paired_display_pixels": int(paired.sum()), "classified_display_pixels": classified_display_pixels}
        with tempfile.TemporaryDirectory(prefix="napo-imagery-", dir=output_root) as staging_name:
            staging = Path(staging_name)
            files = []
            for kind, array, name in [("observation", rgba, "napo-sentinel2-2024.webp"),
                                      ("classification", classes, "napo-mapbiomas-2024.png")]:
                temporary = staging / name
                if kind == "observation":
                    Image.fromarray(array).save(temporary, format="WEBP", quality=88, method=6)
                else:
                    Image.fromarray(array).save(temporary, optimize=True)
                files.append({"kind": kind, "url": f"assets/images/imagery/{name}", "sha256": sha256(temporary)})
            manifest = {"schema_version": 1, "status": "ready", "source": config["source"],
                        "period": config["period"], "bbox": config["bbox"], "scope": config["scope"],
                        "display_bounds": bounds, "display_crs": "EPSG:3857", "width": width, "height": height,
                        "display_sampling_m": 30, "reflectance_resampling": "bilinear", "mask_resampling": "nearest",
                        "display": stretch, "input_sha256": sha256(input_path), "receipt_sha256": sha256(receipt_path),
                        "classification_sha256": classification["sha256"], "receipt": receipt, "statistics": stats,
                        "images": files, "built_at": datetime.now(timezone.utc).isoformat()}
            for row in files:
                target = output_root / row["url"]
                target.parent.mkdir(parents=True, exist_ok=True)
                (staging / Path(row["url"]).name).replace(target)
            manifest_path = output_root / "data/imagery/napo-manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            temporary = staging / "manifest.json"
            temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            temporary.replace(manifest_path)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads((ROOT / "data/imagery/napo-config.json").read_text(encoding="utf-8"))
    landcover = json.loads((ROOT / "data/landcover/napo-manifest.json").read_text(encoding="utf-8"))
    try:
        manifest = build_bundle(args.input, args.receipt, ROOT, config, landcover)
    except (ValueError, KeyError, FileNotFoundError) as error:
        parser.exit(1, f"Build stopped: {error}\n")
    print(f'Ready: {manifest["receipt"]["joined_count"]} scenes; {manifest["statistics"]["usable_pixels"]} usable pixels')


if __name__ == "__main__":
    main()
