"""Derive unreviewed 1 km screening cells from real, exact 10 m water counts.

No resampling, RGB classification, hole filling, mining attribution or synthetic
public observations. The RGB bundle is preserved. Counts must match its scenes.
"""
import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile

try:  # CLI and unittest/module imports.
    from .build_napo_rivers import ROOT, digest, validate_receipt, validate_candidates
except ImportError:
    from build_napo_rivers import ROOT, digest, validate_receipt, validate_candidates

COUNT_BANDS = [f"y{year}_{kind}_count" for year in [2019, 2024] for kind in ["water", "valid"]]
ENCODING = "exact-water-and-valid-observation-counts-zero-valid-is-nodata"
METHOD = "exact-count-fractions-local-8-connected-100px-1km-v1"


def retained_components(mask, minimum=100):
    import numpy as np
    from scipy.ndimage import label
    labels, _ = label(mask, structure=np.ones((3, 3), dtype=np.uint8))
    sizes = np.bincount(labels.ravel())
    keep = sizes >= minimum
    keep[0] = False  # Background must never become a candidate or fill holes.
    return keep[labels]


def change_masks(counts, maximum_counts, inside=None):
    import numpy as np
    if counts.ndim != 3 or counts.shape[0] != 4 or counts.dtype != np.uint8:
        raise ValueError("Expected four uint8 count bands")
    w0, v0, w1, v1 = counts.astype(np.int32)
    if np.any(w0 > v0) or np.any(w1 > v1) or np.any(v0 > maximum_counts[0]) or np.any(v1 > maximum_counts[1]):
        raise ValueError("Water/valid counts exceed acquisition inventory")
    valid = (v0 >= 10) & (v1 >= 10)
    if inside is not None:
        valid &= inside
    if not valid.any():
        raise ValueError("No comparable observation support; not an observed empty result")
    # Exact fractions: avoid uint8 overflow and rounding near the 0.5 threshold.
    difference = w1 * v0 - w0 * v1
    context = (2 * w0 >= v0) | (2 * w1 >= v1)
    gain = retained_components(valid & context & (2 * difference >= v0 * v1))
    loss = retained_components(valid & context & (-2 * difference >= v0 * v1))
    return gain, loss, valid


def aggregate_cells(gain, loss, valid, transform):
    import numpy as np
    from rasterio.warp import transform as project
    cells = {}
    for key, mask in [("gain_pixels", gain), ("loss_pixels", loss)]:
        rows, columns = np.nonzero(mask)
        xs = np.floor((transform.c + (columns + 0.5) * 10) / 1000).astype(np.int64)
        ys = np.floor((-transform.f + (rows + 0.5) * 10) / 1000).astype(np.int64)
        pairs, totals = np.unique(np.stack([xs, ys], axis=1), axis=0, return_counts=True)
        for pair, total in zip(pairs, totals):
            cell = cells.setdefault(tuple(int(x) for x in pair), {"gain_pixels": 0, "loss_pixels": 0})
            cell[key] = int(total)
    features = []
    for (x, y), counts in sorted(cells.items()):
        if sum(counts.values()) < 100:
            continue
        lon, lat = project("EPSG:3857", "EPSG:4326", [(x + 0.5) * 1000], [-(y + 0.5) * 1000])
        features.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon[0], lat[0]]},
                         "properties": {"cell_id": x + y * 100000, "kind": "water-frequency-change-candidate", "status": "unreviewed",
                            "years": [2019, 2024], "sampling_m": 10, "screening_cell_m": 1000, "min_observations": 10,
                            "water_threshold": 0.2, "change_threshold": 0.5,
                            "gain_ha": counts["gain_pixels"] / 100, "loss_ha": counts["loss_pixels"] / 100,
                            "warning": "Cell centroid, not a river location or cause. Review clouds, shadows, seasons and water level."}})
    return validate_candidates({"type": "FeatureCollection", "features": features})


def build_changes(inputs, receipt_path, output_root, config):
    import numpy as np
    import rasterio
    from rasterio.features import geometry_mask
    from rasterio.transform import from_origin
    from rasterio.warp import transform_geom
    from shapely.geometry import shape, mapping, box
    from shapely.ops import unary_union

    if any(config[key] != expected for key, expected in {"min_observations": 10, "water_threshold": 0.2,
           "change_threshold": 0.5, "water_frequency_min": 0.5, "min_connected_pixels": 100,
           "screening_cell_m": 1000, "min_cell_change_ha": 1}.items()):
        raise ValueError("Unsupported screening thresholds")
    inputs = sorted(Path(path) for path in inputs)
    if not inputs or len(inputs) > 100 or len(set(path.resolve() for path in inputs)) != len(inputs):
        raise ValueError("Expected unique real count chunks")
    receipt_path, output_root = Path(receipt_path), Path(output_root)
    document = json.loads(receipt_path.read_text(encoding="utf-8"))
    if document.get("type") != "FeatureCollection" or len(document.get("features", [])) != 1:
        raise ValueError("Expected one-feature count receipt")
    receipt = json.loads(document["features"][0]["properties"]["receipt"])
    validate_receipt(receipt, config)
    if receipt.get("product") != "water-observation-counts" or receipt.get("count_bands") != COUNT_BANDS or receipt.get("count_dtype") != "uint8" or receipt.get("count_encoding") != ENCODING:
        raise ValueError("Missing exact-count product provenance")
    public = output_root / "data/rivers"
    manifest_path = public / "napo-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "ready" or manifest.get("config") != config:
        raise ValueError("Matching verified RGB bundle required")
    validate_receipt(manifest["receipt"], config)
    for key in ["scenes", "processing_block", "boundary", "area_m2"]:
        if receipt[key] != manifest["receipt"][key]:
            raise ValueError(f"Count/RGB observations differ: {key}")
    if not manifest.get("tiles"):
        raise ValueError("Missing RGB tile inventory")
    for tile in manifest["tiles"]:
        relative = Path(tile["url"])
        target = (output_root / relative).resolve()
        if not target.is_relative_to((output_root / "assets/images/rivers").resolve()) or not target.is_file() or target.stat().st_size != tile["size_bytes"] or digest(target) != tile["sha256"]:
            raise ValueError("RGB tiles changed; screening publication stopped")
    bbox = receipt["processing_block"]["bbox"]
    footprint = shape(receipt["boundary"]["geometry"]).intersection(box(*bbox))
    if footprint.is_empty:
        raise ValueError("Block does not intersect Napo")
    required = shape(transform_geom("EPSG:4326", "EPSG:3857", mapping(footprint)))
    with ExitStack() as stack:
        sources = [stack.enter_context(rasterio.open(path)) for path in inputs]
        rectangles = []
        for source in sources:
            t = source.transform
            if source.crs != rasterio.crs.CRS.from_string("EPSG:3857") or source.count != 4 or any(dtype != "uint8" for dtype in source.dtypes) or list(source.descriptions) != COUNT_BANDS:
                raise ValueError("Expected actual four-band uint8 counts")
            if not np.allclose([t.a, t.b, t.d, t.e], [10, 0, 0, -10], atol=1e-8, rtol=0) or not np.allclose([t.c / 10, t.f / 10], np.rint([t.c / 10, t.f / 10]), atol=1e-7, rtol=0):
                raise ValueError("Native count grid/alignment differs")
            if source.width > 4096 or source.height > 4096:
                raise ValueError("Oversized count chunk")
            rectangle = box(*source.bounds)
            if any(rectangle.intersection(previous).area > 0.01 for previous in rectangles):
                raise ValueError("Overlapping count chunks")
            if not box(*required.bounds).buffer(20).covers(rectangle):
                # Exterior padding in a rectangular GEE block is permitted;
                # arbitrary distant chunks are not.
                block_projected = shape(transform_geom("EPSG:4326", "EPSG:3857", mapping(box(*bbox))))
                if not block_projected.buffer(20).covers(rectangle):
                    raise ValueError("Count chunk outside processing block")
            rectangles.append(rectangle)
        if not unary_union(rectangles).buffer(0.01).covers(required):
            raise ValueError("Incomplete count chunks inside Napo")
        west, south, east, north = unary_union(rectangles).bounds
        width, height = round((east - west) / 10), round((north - south) / 10)
        if width * height > config["max_pixels"]:
            raise ValueError("Count mosaic exceeds local pixel limit")
        t = from_origin(west, north, 10, 10)
        counts = np.zeros((4, height, width), dtype=np.uint8)
        for source in sources:
            x, y = round((source.bounds.left - west) / 10), round((north - source.bounds.top) / 10)
            counts[:, y:y + source.height, x:x + source.width] = source.read()
        # Exact grid placement joins components across 4096 px chunk seams.
        # Provincial/block edges still truncate components: documented limit.
        inside = geometry_mask([mapping(required)], out_shape=(height, width), transform=t, invert=True)
        gain, loss, valid = change_masks(counts, [row["joined_count"] for row in receipt["scenes"]], inside)
        collection = aggregate_cells(gain, loss, valid, t)
        support = int(valid.sum())
        retained = {"gain": int(gain.sum()), "loss": int(loss.sum())}
    metadata = {"schema_version": 1, "method": METHOD, "connectivity": 8, "sampling_m": 10,
                "count_bands": COUNT_BANDS, "count_encoding": ENCODING, "count_receipt": receipt,
                "receipt_sha256": digest(receipt_path), "rgb_receipt_sha256": manifest["receipt_sha256"],
                "input_chunks": [{"name": path.name, "sha256": digest(path), "size_bytes": path.stat().st_size} for path in inputs],
                "comparable_pixels": support, "retained_pixels": retained,
                "builder_sha256": digest(Path(__file__)), "built_at": datetime.now(timezone.utc).isoformat()}
    collection["metadata"] = metadata
    # All validation completes before either public file is replaced. The
    # manifest is last: a interrupted write fails closed via SHA, never displays
    # data paired with the wrong manifest. Existing RGB assets are untouched.
    with tempfile.TemporaryDirectory(prefix="napo-screening-", dir=public) as folder:
        stage = Path(folder)
        candidate_path = stage / "candidates.geojson"
        candidate_path.write_text(json.dumps(collection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest.update(candidate_status="ready", candidate_count=len(collection["features"]),
                        candidates_sha256=digest(candidate_path), screening=metadata)
        staged_manifest = stage / "manifest.json"
        staged_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        candidate_path.replace(public / "napo-candidates.geojson")
        staged_manifest.replace(manifest_path)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", nargs="+", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads((ROOT / "data/rivers/napo-config.json").read_text(encoding="utf-8"))
    try:
        result = build_changes(args.inputs, args.receipt, ROOT, config)
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"Screening stopped: {error}\n")
    print(f'Unreviewed cells: {result["candidate_count"]}; comparable pixels: {result["screening"]["comparable_pixels"]}')


if __name__ == "__main__":
    main()
