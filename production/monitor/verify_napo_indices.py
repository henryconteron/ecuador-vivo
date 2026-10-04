"""Independent recalculation and optional authoritative COG pixel spot checks.

Technical verification is not field validation of water labels or river change.
Only anonymous, reviewed HTTPS Sentinel assets are accessed.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
from PIL import Image
import rasterio
from rasterio.windows import Window, bounds, from_bounds
from rasterio.warp import transform

from prepare_napo_ndwi import API, calibration, public_url, fetch_json
from prepare_napo_indices import ENV, BANDS, area_slices
from reel_napo_indices import load_evidence


def checked_ratio(green, infrared):
    """Float64 independent expression, not the preparation's ratio helper."""
    green, infrared = np.asarray(green, dtype="float64"), np.asarray(infrared, dtype="float64")
    if np.any(~np.isfinite(green) | ~np.isfinite(infrared) | (green < 0) | (infrared < 0) | (green + infrared <= 0)):
        raise ValueError("Invalid reflectance in a declared valid pixel")
    return (green - infrared) / (green + infrared)


def native_pixel(item, scene, array, grid, col, row):
    report = {}
    target_bounds = bounds(Window(col, row, 1, 1), grid["transform"])
    for band, key in enumerate(BANDS):
        asset = item["assets"][key]
        scale, offset = calibration(asset)
        if scene["radiometry"][key]["url"] != public_url(asset) or (scale, offset) != (scene["radiometry"][key]["scale"], scene["radiometry"][key]["offset"]):
            raise ValueError("Live asset calibration / location differs from saved evidence")
        if item["collection"] == "sentinel-2-l2a" and item["properties"].get("earthsearch:boa_offset_applied") and offset:
            raise ValueError("Ambiguous legacy calibration")
        with rasterio.open(public_url(asset)) as source:
            raw = from_bounds(*target_bounds, source.transform)
            numbers = [raw.col_off, raw.row_off, raw.width, raw.height]
            if not np.allclose(numbers, np.round(numbers), atol=1e-6):
                raise ValueError("Native spot check is not aligned")
            win = Window(*[int(round(number)) for number in numbers])
            size = 1 if key == "swir16" else 2
            if source.crs != grid["crs"] or source.res != ((20, 20) if size == 1 else (10, 10)) or (win.height, win.width) != (size, size):
                raise ValueError("Unexpected native sampling")
            dn = source.read(1, window=win)
        if np.any(dn == 0):
            raise ValueError("Example pixel contains native NoData")
        value = float((dn.astype("float32") * scale + offset).mean())
        saved = float(array[band, row, col])
        if abs(value - saved) > 1e-6:
            raise ValueError("Native reflectance does not reproduce the saved pixel: " + key)
        report[key] = {"native_dn": dn.tolist(), "scale": scale, "offset": offset,
                       "mean_reflectance": value, "saved_reflectance": saved, "absolute_error": abs(value - saved)}
    with rasterio.open(public_url(item["assets"]["scl"])) as source:
        raw = from_bounds(*target_bounds, source.transform)
        scl = int(source.read(1, window=Window(round(raw.col_off), round(raw.row_off), 1, 1))[0, 0])
    if scl != int(array[8, row, col]):
        raise ValueError("Native SCL spot check differs")
    report["scl"] = scl
    return report


def verify(folder, live=False):
    folder = Path(folder)
    manifest = load_evidence(folder)
    arrays, reports, grid = [], [], None
    with rasterio.Env(**ENV):
        for scene in manifest["scenes"]:
            local = json.loads((folder / (scene["id"] + ".stac.json")).read_text(encoding="utf-8"))
            if local["id"] != scene["id"] or local["collection"] != scene["collection"] or local["properties"]["datetime"] != scene["acquired_at"]:
                raise ValueError("Saved acquisition does not match STAC")
            with rasterio.open(folder / scene["crop_file"]) as source:
                newgrid = dict(crs=source.crs, transform=source.transform, width=source.width, height=source.height)
                if source.count != 9 or source.res != (20, 20) or source.crs.to_epsg() != 32717:
                    raise ValueError("Unexpected scientific raster layout")
                array = source.read()
            if grid is not None and newgrid != grid:
                raise ValueError("Dates not aligned")
            grid = newgrid
            valid = array[7] == 1
            if not np.all(np.isin(array[8][valid], [4, 5, 6])) or not np.all(array[:7, ~valid] == -9999):
                raise ValueError("QA / NoData is inconsistent")
            differences = {}
            for key, band, infrared in (("ndwi", 5, 3), ("mndwi", 6, 4)):
                calculated = checked_ratio(array[1][valid], array[infrared][valid])
                difference = float(np.max(np.abs(calculated - array[band][valid])))
                if difference > 2e-6:
                    raise ValueError("Independent index recalculation failed")
                differences[key] = difference
            point_col, point_row = manifest["illustrative_pixel"]["grid_col_row"]
            if not valid[point_row, point_col]:
                raise ValueError("Illustrative location not usable in every date")
            row = {"id": scene["id"], "date": scene["acquired_at"], "independent_ratio_max_error": differences}
            if live:
                item = fetch_json(API + f"/collections/{scene['collection']}/items/{scene['id']}")
                if item["id"] != local["id"] or item["properties"]["datetime"] != local["properties"]["datetime"] or item["properties"].get("s2:product_uri") != local["properties"].get("s2:product_uri"):
                    raise ValueError("Live product differs from the saved acquisition")
                row["live_native_pixel"] = native_pixel(item, scene, array, grid, point_col, point_row)
            reports.append(row)
            arrays.append(array)
            print("Verified scientific scene:", scene["id"], flush=True)
    common = np.logical_and.reduce([array[7] == 1 for array in arrays])
    for area, properties in manifest["regions"].items():
        y, x, _ = area_slices(properties, grid)
        paired = common[y, x]
        if abs(float(paired.mean()) - properties["common_valid_fraction"]) > 1e-10:
            raise ValueError("Reported common support differs")
        for year in (2019, 2024, 2026):
            for mode in ("rgb", "ndwi", "mndwi"):
                with Image.open(folder / f"{area}_{year}_{mode}.png") as image:
                    alpha = np.asarray(image)[..., 3]
                if not np.array_equal(alpha, paired.astype("uint8") * 255):
                    raise ValueError("An image does not share the three-date support")
    point = manifest["illustrative_pixel"]
    col, row = point["grid_col_row"]
    for name, band in (("green", 1), ("nir", 3), ("swir", 4), ("ndwi", 5), ("mndwi", 6)):
        if abs(point[name] - float(arrays[1][band, row, col])) > 1e-8:
            raise ValueError("Narrated numeric example differs from source")
    easting, northing = grid["transform"] * (col + .5, row + .5)
    lon, lat = transform(grid["crs"], "EPSG:4326", [easting], [northing])
    if not np.allclose([lon[0], lat[0]], point["longitude_latitude"], atol=1e-9):
        raise ValueError("Example georeference is wrong")
    result = {"status": "passed_technical_checks_not_field_validation", "checked_at": datetime.now(timezone.utc).isoformat(),
              "manifest_sha256": sha256((folder / "manifest.json").read_bytes()).hexdigest(),
              "live_checks": live, "scenes": reports,
              "checks": ["source hashes", "STAC acquisition identity", "identical native 20 m grids",
                         "float64 independent recalculation", "all derived alpha masks", "numeric example and coordinates"],
              "not_verified": ["field water labels", "river migration or erosion magnitude", "matched discharge",
                               "mining cause", "pollutant concentration", "MNDWI classification accuracy superiority"]}
    (folder / "verification_scientific.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    print(json.dumps(verify(args.folder, args.live), ensure_ascii=False, indent=2), flush=True)
