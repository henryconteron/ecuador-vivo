"""Build a provincial RGB tile pyramid and unreviewed water-screening cells.

Inputs must be actual matching GEE exports. Never upscale the previous 30 m
raster, sharpen it, infer mining, or publish test fixtures as observations.
"""
import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
WORLD = 20037508.342789244


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tile_bounds(z, x, y):
    size = 2 * WORLD / 2 ** z
    west, north = -WORLD + x * size, WORLD - y * size
    return west, north - size, west + size, north


def validate_receipt(receipt, config):
    for key in ["schema_version", "asset", "quality_asset", "boundary_asset", "boundary_filter", "years", "periods", "bands",
                "clear_threshold", "min_observations", "excluded_scl", "water_formula", "water_threshold", "change_threshold",
                "water_frequency_min", "min_connected_pixels", "screening_cell_m", "min_cell_change_ha", "export_crs",
                "export_transform", "export_bands", "display", "method", "scope"]:
        if receipt.get(key) != config[key]:
            raise ValueError(f"Provincial receipt mismatch: {key}")
    for key in ["rgb_min_observations", "scene_selection", "processing_grid"]:
        if receipt.get(key) != config[key]:
            raise ValueError(f"Block method mismatch: {key}")
    block = receipt.get("processing_block", {})
    if type(block.get("id")) is not int or not 0 <= block["id"] < 9 or not isinstance(block.get("bbox"), list) or len(block["bbox"]) != 4:
        raise ValueError("Missing processing block")
    grid = config["processing_grid"]
    west, south, east, north = grid["bbox"]
    dx, dy = (east - west) / grid["columns"], (north - south) / grid["rows"]
    left, top = west + (block["id"] % grid["columns"]) * dx, north - (block["id"] // grid["columns"]) * dy
    expected = [left, top - dy, left + dx, top]
    if any(type(value) not in (int, float) or not math.isfinite(value) or abs(value - target) > 1e-9 for value, target in zip(block["bbox"], expected)):
        raise ValueError("Processing block does not match provincial grid")
    boundary = receipt.get("boundary", {})
    if boundary.get("type") != "Feature" or boundary.get("geometry", {}).get("type") not in ("Polygon", "MultiPolygon") or any(
        boundary.get("properties", {}).get(key) != value for key, value in config["boundary_filter"].items()
    ):
        raise ValueError("Missing actual Napo province boundary")
    datetime.fromisoformat(receipt["export_requested_at"].replace("Z", "+00:00"))
    if not isinstance(receipt.get("area_m2"), (int, float)) or not 1e9 < receipt["area_m2"] < 3e10:
        raise ValueError("Unexpected Napo province area")
    scenes = receipt.get("scenes", [])
    if len(scenes) != 2:
        raise ValueError("Missing both acquisition inventories")
    for i, row in enumerate(scenes):
        count = row.get("joined_count")
        if row.get("year") != config["years"][i] or row.get("period") != config["periods"][i] or type(count) is not int or not 10 <= count <= 32:
            raise ValueError("Invalid year/scene count")
        ids, dates = row.get("scene_ids", []), row.get("acquired_ms", [])
        start, end = [datetime.fromisoformat(x).replace(tzinfo=timezone.utc).timestamp() * 1000 for x in row["period"]]
        if len(ids) != count or len(set(ids)) != count or any(not isinstance(x, str) or not x for x in ids) or len(dates) != count or any(
            not isinstance(x, (float, int)) or not math.isfinite(x) or not start <= x < end for x in dates
        ):
            raise ValueError("Invalid acquisition IDs/times")


def validate_candidates(collection):
    if collection.get("type") != "FeatureCollection" or not isinstance(collection.get("features"), list) or len(collection["features"]) > 20000:
        raise ValueError("Invalid screening collection")
    seen = set()
    for feature in collection["features"]:
        p, geometry = feature.get("properties", {}), feature.get("geometry", {})
        point = geometry.get("coordinates", [])
        if geometry.get("type") != "Point" or len(point) != 2 or any(not isinstance(x, (int, float)) or not math.isfinite(x) for x in point) or not -79 < point[0] < -76 or not -2 < point[1] < 1:
            raise ValueError("Screening centroid outside provincial envelope")
        if p.get("kind") != "water-frequency-change-candidate" or p.get("status") != "unreviewed" or p.get("years") != [2019, 2024] or p.get("sampling_m") != 10 or p.get("screening_cell_m") != 1000 or p.get("min_observations") != 10 or p.get("water_threshold") != 0.2 or p.get("change_threshold") != 0.5:
            raise ValueError("Screening method has changed")
        areas = [p.get("gain_ha"), p.get("loss_ha")]
        if any(not isinstance(x, (int, float)) or not math.isfinite(x) or not 0 <= x <= 100.001 for x in areas) or sum(areas) < 0.9999:
            raise ValueError("Invalid screening area")
        cell = p.get("cell_id")
        if type(cell) is not int or cell in seen:
            raise ValueError("Missing/duplicate screening cell")
        seen.add(cell)
    return collection


def build_bundle(inputs, receipt_path, candidates_path, output_root, config):
    import numpy as np
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.transform import from_bounds
    from rasterio.warp import reproject, transform_bounds, transform_geom
    from shapely.geometry import shape, mapping, box
    from PIL import Image

    inputs = sorted(Path(path) for path in inputs)
    if not inputs or len(inputs) > 100 or len(set(inputs)) != len(inputs):
        raise ValueError("Expected unique real provincial raster chunks")
    receipt_path, output_root = map(Path, (receipt_path, output_root))
    candidates_path = Path(candidates_path) if candidates_path is not None else None
    document = json.loads(receipt_path.read_text(encoding="utf-8"))
    if document.get("type") != "FeatureCollection" or len(document.get("features", [])) != 1:
        raise ValueError("Expected one-feature acquisition receipt")
    receipt = json.loads(document["features"][0]["properties"]["receipt"])
    validate_receipt(receipt, config)
    candidates = validate_candidates(json.loads(candidates_path.read_text(encoding="utf-8"))) if candidates_path else None
    bbox = receipt["processing_block"]["bbox"]
    projected = transform_bounds("EPSG:4326", "EPSG:3857", *bbox)
    if candidates is not None:
        from shapely.geometry import Point
        # A clipped boundary cell's centroid can be outside by at most one cell;
        # reject candidates from another block/province rather than mixing data.
        province = shape(receipt["boundary"]["geometry"])
        tolerance = 0.015  # Conservative ~1.7 km allowance for 1 km edge cells.
        for feature in candidates["features"]:
            point = feature["geometry"]["coordinates"]
            if not bbox[0] - tolerance <= point[0] <= bbox[2] + tolerance or not bbox[1] - tolerance <= point[1] <= bbox[3] + tolerance or not province.buffer(tolerance).covers(Point(*point)):
                raise ValueError("Screening candidate outside processing coverage")
    with ExitStack() as stack:
        sources = [stack.enter_context(rasterio.open(path)) for path in inputs]
        for source in sources:
            if source.crs != rasterio.crs.CRS.from_string("EPSG:3857") or source.count != 8 or any(dtype != "uint8" for dtype in source.dtypes) or list(source.descriptions) != config["export_bands"]:
                raise ValueError("Expected actual eight-band byte RGB/alpha export")
            if not np.allclose([source.transform.a, source.transform.b, source.transform.d, source.transform.e], [10, 0, 0, -10], atol=1e-8, rtol=0) or not np.allclose([source.transform.c / 10, source.transform.f / 10], np.rint([source.transform.c / 10, source.transform.f / 10]), atol=1e-7, rtol=0):
                raise ValueError("Native 10 m grid/alignment differs")
            if source.width * source.height > 4096 ** 2:
                raise ValueError("Oversized source chunk")
        # Require complete coverage of the block's actual provincial footprint.
        # GEE skipEmptyTiles may omit a chunk wholly outside that footprint.
        # Never accept a missing chunk within Napo; exterior web tiles remain
        # transparent and are generated below, not fabricated observations.
        rectangles = [shape({"type": "Polygon", "coordinates": [[
            [s.bounds.left, s.bounds.bottom], [s.bounds.right, s.bounds.bottom],
            [s.bounds.right, s.bounds.top], [s.bounds.left, s.bounds.top], [s.bounds.left, s.bounds.bottom]
        ]]}) for s in sources]
        from shapely.ops import unary_union
        footprint = shape(receipt["boundary"]["geometry"]).intersection(box(*bbox))
        if footprint.is_empty:
            raise ValueError("Processing block does not intersect Napo")
        required = shape(transform_geom("EPSG:4326", "EPSG:3857", mapping(footprint)))
        if not unary_union(rectangles).buffer(0.01).covers(required):
            raise ValueError("Incomplete provincial source chunks")
        output_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="napo-rivers-", dir=output_root) as folder:
            staging = Path(folder)
            fingerprints = []
            for z in range(8, 14):
                size = 2 * WORLD / 2 ** z
                x0, x1 = math.floor((projected[0] + WORLD) / size), math.floor((projected[2] + WORLD) / size)
                y0, y1 = math.floor((WORLD - projected[3]) / size), math.floor((WORLD - projected[1]) / size)
                for x in range(x0, x1 + 1):
                    for y in range(y0, y1 + 1):
                        bounds = tile_bounds(z, x, y)
                        transform = from_bounds(*bounds, 512, 512)
                        rgba = np.zeros((8, 512, 512), dtype="uint8")
                        for source in sources:
                            if not rectangles[sources.index(source)].intersects(box(*bounds)):
                                continue
                            # Nearest preserves the exported 8-bit display, alpha,
                            # and aligned pixels; never blur categorical support.
                            sampled = np.zeros_like(rgba)
                            for band in range(8):
                                reproject(rasterio.band(source, band + 1), sampled[band], src_transform=source.transform,
                                          src_crs=source.crs, dst_transform=transform, dst_crs="EPSG:3857", resampling=Resampling.nearest)
                            if not np.isin(sampled[[3, 7]], [0, 255]).all() or not np.array_equal(sampled[3], sampled[7]):
                                raise ValueError("Paired alpha changed or is not binary")
                            valid = sampled[3] == 255
                            rgba[:, valid] = sampled[:, valid]
                        for i, year in enumerate([2019, 2024]):
                            relative = f"assets/images/rivers/{year}/{z}/{x}/{y}.webp"
                            target = staging / relative
                            target.parent.mkdir(parents=True, exist_ok=True)
                            Image.fromarray(rgba[i * 4:i * 4 + 4].transpose(1, 2, 0)).save(target, format="WEBP", lossless=True, method=4)
                            fingerprints.append({"url": relative, "sha256": digest(target), "size_bytes": target.stat().st_size})
            manifest = {"schema_version": 1, "status": "ready", "config": config, "receipt": receipt,
                        "input_chunks": [{"name": path.name, "sha256": digest(path)} for path in inputs],
                        "receipt_sha256": digest(receipt_path), "candidates_sha256": digest(candidates_path) if candidates_path else None,
                        "display_bounds": [[bbox[1], bbox[0]], [bbox[3], bbox[2]]],
                        "tile_size": 512, "zoom_offset": -1, "min_native_zoom": 9, "max_native_zoom": 14,
                        "tile_format": "lossless-webp", "resampling": "nearest", "sampling_m": 10,
                        "candidate_status": "ready" if candidates is not None else "pending",
                        "candidate_count": len(candidates["features"]) if candidates is not None else None, "tiles": fingerprints,
                        "coverage": {"kind": "processing-block", "block_ids": [receipt["processing_block"]["id"]], "total_blocks": 9},
                        "built_at": datetime.now(timezone.utc).isoformat()}
            for row in fingerprints:
                destination = output_root / row["url"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                (staging / row["url"]).replace(destination)
            public = output_root / "data/rivers"
            public.mkdir(parents=True, exist_ok=True)
            # Preserve exact observed GeoJSON bytes for integrity checking.
            if candidates_path:
                (staging / "candidates.geojson").write_bytes(candidates_path.read_bytes())
                (staging / "candidates.geojson").replace(public / "napo-candidates.geojson")
            (staging / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            (staging / "manifest.json").replace(public / "napo-manifest.json")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", nargs="+", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--candidates", type=Path, help="Optional actual screening export; omitted means explicitly pending, not zero candidates")
    args = parser.parse_args()
    config = json.loads((ROOT / "data/rivers/napo-config.json").read_text(encoding="utf-8"))
    try:
        result = build_bundle(args.inputs, args.receipt, args.candidates, ROOT, config)
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"Provincial build stopped: {error}\n")
    print(f'Ready: {len(result["tiles"])} lossless tiles; screening {result["candidate_status"]}, count {result["candidate_count"]}')


if __name__ == "__main__":
    main()
