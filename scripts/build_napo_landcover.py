"""Validate an actual MapBiomas export and build small, georeferenced web previews.

Statistics use common observed pixels on the NATIVE grid, never the PNG display.
No area/deforestation/causal claims are inferred from classification transitions.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def read_receipt(path):
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    if document.get("type") != "FeatureCollection" or len(document.get("features", [])) != 1:
        raise ValueError("Expected the one-feature Earth Engine receipt GeoJSON")
    return json.loads(document["features"][0]["properties"]["receipt"])


def validate_receipt(receipt, config):
    expected = {
        "schema_version": 1, "asset": config["source"]["asset"],
        "version": config["source"]["version"], "years": config["years"],
        "bbox": config["bbox"], "license": config["source"]["license"],
        "source_url": config["source"]["url"], "nominal_resolution_m": 30,
        "band_order": [f"classification_{year}" for year in config["years"]],
    }
    for key, value in expected.items():
        if receipt.get(key) != value:
            raise ValueError(f"Receipt mismatch: {key}")
    if not receipt.get("crs") or len(receipt.get("crs_transform", [])) != 6:
        raise ValueError("Missing native CRS/grid in receipt")
    if not 25 <= receipt.get("native_scale_m", 0) <= 35:
        raise ValueError("Unexpected native sampling in receipt")
    datetime.fromisoformat(receipt["export_requested_at"].replace("Z", "+00:00"))


def summarize(before, after, valid_before, valid_after, legend):
    import numpy as np
    ids = {row["id"] for row in legend}
    for values, valid in [(before, valid_before), (after, valid_after)]:
        unknown = set(int(x) for x in np.unique(values[valid])) - ids - {0}
        if unknown:
            raise ValueError(f"Unknown classification codes: {sorted(unknown)}")
    observed_before = valid_before & (before != 0) & (before != 27)
    observed_after = valid_after & (after != 0) & (after != 27)
    paired = observed_before & observed_after
    total = int(paired.sum())
    if total == 0:
        raise ValueError("No common observed pixels; cannot compare years")
    classes = []
    for row in legend:
        if row["id"] == 27:
            continue
        counts = [int(((values == row["id"]) & paired).sum()) for values in [before, after]]
        if any(counts):
            classes.append({"id": row["id"], "pixels": counts})
    codes, counts = np.unique(before[paired].astype("uint16") * 100 + after[paired], return_counts=True)
    transitions = [{"from": int(code // 100), "to": int(code % 100), "pixels": int(count)}
                   for code, count in zip(codes, counts) if code // 100 != code % 100]
    transitions.sort(key=lambda row: (-row["pixels"], row["from"], row["to"]))
    return {"common_observed_pixels": total,
            "observed_pixels": [int(observed_before.sum()), int(observed_after.sum())],
            "classes": classes, "changed_class_pixels": int((paired & (before != after)).sum()),
            "top_transitions": transitions[:10]}, [observed_before, observed_after]


def build_bundle(input_path, receipt_path, output_root, config):
    import numpy as np
    from PIL import Image
    import rasterio
    from rasterio.features import geometry_mask
    from rasterio.warp import calculate_default_transform, reproject, Resampling, transform_bounds, transform_geom
    from rasterio.transform import array_bounds

    input_path, output_root = Path(input_path), Path(output_root)
    receipt = read_receipt(receipt_path)
    validate_receipt(receipt, config)
    west, south, east, north = config["bbox"]
    polygon = {"type": "Polygon", "coordinates": [[[west, south], [east, south],
                [east, north], [west, north], [west, south]]]}
    with rasterio.open(input_path) as src:
        if src.count != 2 or src.crs is None or src.width * src.height > 25000000:
            raise ValueError("Expected a small two-band georeferenced export")
        if src.nodata != 0:
            raise ValueError("Expected explicit NoData=0, as configured in the exporter")
        if any(dtype != "uint8" for dtype in src.dtypes):
            raise ValueError("Expected uint8 categorical bands, not RGB or float data")
        if any(src.descriptions) and list(src.descriptions) != receipt["band_order"]:
            raise ValueError("Band descriptions differ from receipt year order")
        if src.crs != rasterio.crs.CRS.from_string(receipt["crs"]):
            raise ValueError("Export CRS differs from native receipt")
        # Cropping changes the origin by whole pixels, but not resolution/rotation.
        native = receipt["crs_transform"]
        if not np.allclose([src.transform.a, src.transform.b, src.transform.d, src.transform.e],
                           [native[0], native[1], native[3], native[4]], rtol=0, atol=1e-10):
            raise ValueError("Pixel grid differs from export receipt")
        offset = ~rasterio.Affine(*native) * (src.transform.c, src.transform.f)
        if not np.allclose(offset, np.rint(offset), atol=1e-5, rtol=0):
            raise ValueError("Shifted native pixel alignment")
        bounds = transform_bounds(src.crs, "EPSG:4326", *src.bounds)
        if bounds[0] > west + 1e-6 or bounds[1] > south + 1e-6 or bounds[2] < east - 1e-6 or bounds[3] < north - 1e-6:
            raise ValueError("Raster does not cover the configured study window")
        inside = geometry_mask([transform_geom("EPSG:4326", src.crs, polygon)],
                               out_shape=(src.height, src.width), transform=src.transform,
                               invert=True, all_touched=False)
        values = src.read()
        valid = [inside & (src.read_masks(band) > 0) for band in [1, 2]]
        stats, observed = summarize(values[0], values[1], *valid, config["legend"])
        stats["window_pixels"] = int(inside.sum())
        dst_transform, width, height = calculate_default_transform(src.crs, "EPSG:3857", src.width,
                src.height, *src.bounds, resolution=30)
        if width * height > 12000000:
            raise ValueError("Display export exceeds 12 million pixels")
        display_bounds = transform_bounds("EPSG:3857", "EPSG:4326", *array_bounds(height, width, dst_transform))
        native_grid = {"crs": str(src.crs), "transform": list(src.transform)[:6],
                       "width": src.width, "height": src.height,
                       "band_order_verification": "geotiff-descriptions" if any(src.descriptions) else "receipt-declaration"}
        output_root.mkdir(parents=True, exist_ok=True)
        # Complete validation/rendering before replacing any public artifact.
        with tempfile.TemporaryDirectory(prefix="napo-build-", dir=output_root) as staging_name:
            staging = Path(staging_name)
            images = []
            for band, year in enumerate(config["years"]):
                display = np.zeros((height, width), dtype="uint8")
                reproject(np.where(observed[band], values[band], 0), display,
                          src_transform=src.transform, src_crs=src.crs,
                          dst_transform=dst_transform, dst_crs="EPSG:3857",
                          src_nodata=0, dst_nodata=0, resampling=Resampling.nearest)
                rgba = np.zeros((height, width, 4), dtype="uint8")
                for row in config["legend"]:
                    if row["id"] == 27:
                        continue
                    color = row["color"].lstrip("#")
                    rgba[display == row["id"]] = [int(color[i:i+2], 16) for i in [0, 2, 4]] + [255]
                relative = f"assets/images/landcover/napo-v1-{year}.png"
                temporary = staging / f"{year}.png"
                Image.fromarray(rgba).save(temporary, optimize=True)
                images.append({"year": year, "url": relative,
                               "sha256": hashlib.sha256(temporary.read_bytes()).hexdigest()})
            manifest = {"schema_version": 1, "status": "ready", "source": config["source"],
                "years": config["years"], "bbox": config["bbox"], "scope": config["scope"],
                "display_bounds": [[display_bounds[1], display_bounds[0]], [display_bounds[3], display_bounds[2]]],
                "display_crs": "EPSG:3857", "display_resampling": "nearest",
                "built_at": datetime.now(timezone.utc).isoformat(),
                "input_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
                "receipt_sha256": hashlib.sha256(Path(receipt_path).read_bytes()).hexdigest(),
                "receipt": receipt, "native_grid": native_grid, "statistics": stats, "images": images}
            for image in images:
                destination = output_root / image["url"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                (staging / f'{image["year"]}.png').replace(destination)
            manifest_path = output_root / "data/landcover/napo-manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            temporary_manifest = staging / "manifest.json"
            temporary_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            temporary_manifest.replace(manifest_path)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Actual two-band native GeoTIFF")
    parser.add_argument("--receipt", required=True, type=Path, help="Earth Engine receipt GeoJSON")
    args = parser.parse_args()
    config = json.loads((ROOT / "data/landcover/napo-config.json").read_text(encoding="utf-8"))
    try:
        manifest = build_bundle(args.input, args.receipt, ROOT, config)
    except (ValueError, KeyError, FileNotFoundError) as error:
        parser.exit(1, f"Build stopped: {error}\n")
    print(f'Ready: {manifest["years"]}, {manifest["statistics"]["common_observed_pixels"]} common observed pixels')


if __name__ == "__main__":
    main()
