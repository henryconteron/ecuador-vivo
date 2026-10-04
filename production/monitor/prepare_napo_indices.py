"""Three real acquisitions, fair NDWI/MNDWI comparison on native SWIR 20 m grid.

Standalone v2; keeps the previous 2019/2026 preview unchanged. No water
classification, invented detail, paid APIs, or attribution of mining causes.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
from PIL import Image
import rasterio
from affine import Affine
from rasterio.windows import from_bounds, bounds
from rasterio.warp import transform

from prepare_napo_ndwi import (API, BBOX, REGIONS, ACCEPTED_SCL, calibration,
                              ratio, public_url, fetch_json, crop_window,
                              color_ndwi, json_save, SOURCES)

FOLDER = Path("artifacts/rios_napo_indices_v2")
C1 = "sentinel-2-c1-l2a"
SCENES = (("sentinel-2-l2a", "S2B_17MRU_20190711_0_L2A"),
          (C1, "S2A_T17MRU_20240808T153803_L2A"),
          (C1, "S2C_T17MRU_20260729T153626_L2A"))
BANDS = ("red", "green", "blue", "nir", "swir16")
# Fixed editorial detail, chosen from river location, not index change magnitude.
REGIONS = {**REGIONS, "jatunyacu_detail": {
    "name": "Jatunyacu · detalle del tramo inferior",
    "bbox": [-77.842, -1.092, -77.808, -1.058]}}
FORMULAS = {"ndwi": "(B3-B8)/(B3+B8)", "mndwi": "(B3-B11)/(B3+B11)"}
ENV = dict(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
           GDAL_HTTP_TIMEOUT="30", GDAL_HTTP_MAX_RETRY="2", GDAL_HTTP_RETRY_DELAY="1")


def aggregate_2x2(values):
    """Mean of all four reflectance samples; any NoData invalidates the block."""
    values = np.asarray(values, dtype="float32")
    if values.ndim != 2 or any(size % 2 for size in values.shape):
        raise ValueError("Exact aligned 2x2 aggregation requires even 2D dimensions")
    h, w = values.shape
    return values.reshape(h // 2, 2, w // 2, 2).mean(axis=(1, 3))


def indices(green, nir, swir):
    ndwi, nvalid = ratio(green, nir)
    mndwi, mvalid = ratio(green, swir)
    return ndwi, mndwi, nvalid & mvalid


def area_slices(area, grid):
    class Grid:
        crs = grid["crs"]
        transform = grid["transform"]
    window = crop_window(area["bbox"], Grid)
    return (slice(int(window.row_off), int(window.row_off + window.height)),
            slice(int(window.col_off), int(window.col_off + window.width)), window)


def audit_2024(folder):
    """All returned MRU candidates in June-August, not dramatic-change selection."""
    folder.mkdir(parents=True, exist_ok=True)
    response = fetch_json(API + "/search", collections=C1, bbox=",".join(map(str, BBOX)),
                          datetime="2024-06-01T00:00:00Z/2024-08-31T23:59:59Z", limit=100,
                          sortby="properties.eo:cloud_cover")
    candidates = [item for item in response["features"] if "T17MRU" in item["id"]]
    # Ranking by local usable coverage, not tile-wide cloud or channel differences.
    reports = []
    with rasterio.Env(**ENV):
        for item in candidates:
            metadata = folder / (item["id"] + ".stac.json")
            json_save(metadata, item)
            fractions = {}
            with rasterio.open(public_url(item["assets"]["scl"])) as source:
                win = crop_window(BBOX, source)
                data = source.read(1, window=win)
                grid = dict(crs=source.crs, transform=source.window_transform(win))
                for key, area in REGIONS.items():
                    y, x, _ = area_slices(area, grid)
                    fractions[key] = float(np.isin(data[y, x], ACCEPTED_SCL).mean())
            row = {"id": item["id"], "date": item["properties"]["datetime"],
                   "tile_cloud": item["properties"]["eo:cloud_cover"], "local_scl": fractions}
            reports.append(row)
            print(row, flush=True)
            json_save(folder / "selection_2024.json", {
                "retrieved_at": datetime.now(timezone.utc).isoformat(), "search": response,
                "candidates": reports, "complete": len(reports) == len(candidates),
                "scope": "MRU items on returned June-August page; not exhaustive annual survey",
                "criterion": "local SCL support and proximity to July; no river-change metric used"})


def crop(item, folder, template=None):
    if item["collection"] == "sentinel-2-l2a" and item["properties"].get("earthsearch:boa_offset_applied"):
        if any(calibration(item["assets"][key])[1] != 0 for key in BANDS):
            raise ValueError("Ambiguous already-applied legacy BOA offset")
    with rasterio.open(public_url(item["assets"]["swir16"])) as source:
        if source.res != (20, 20) or source.crs.to_epsg() != 32717:
            raise ValueError("Expected native B11 20 m EPSG:32717")
        window = crop_window(BBOX, source)
        grid = dict(crs=source.crs, transform=source.window_transform(window),
                    height=int(window.height), width=int(window.width))
    if template is not None and grid != template:
        raise ValueError("Three acquisition grids must be identical")
    optical, radiometry, raw_hashes = [], {}, {}
    for key in BANDS:
        asset = item["assets"][key]
        scale, offset = calibration(asset)
        with rasterio.open(public_url(asset)) as source:
            target_bounds = bounds(rasterio.windows.Window(0, 0, grid["width"], grid["height"]), grid["transform"])
            raw_window = from_bounds(*target_bounds, transform=source.transform)
            # Round only after confirming the requested bounds align exactly.
            numbers = [raw_window.col_off, raw_window.row_off, raw_window.width, raw_window.height]
            if not np.allclose(numbers, np.round(numbers), atol=1e-6):
                raise ValueError("Band is not exactly aligned with the 20 m grid")
            win = rasterio.windows.Window(*map(lambda v: int(round(v)), numbers))
            resolution = 20 if key == "swir16" else 10
            expected_transform = grid["transform"] * Affine.scale(resolution / 20)
            if source.crs != grid["crs"] or source.res != (resolution, resolution) or source.nodata != 0 or source.window_transform(win) != expected_transform:
                raise ValueError("Unreviewed band alignment / NoData")
            dn = source.read(1, window=win)
        raw_hashes[key] = sha256(dn.tobytes()).hexdigest()
        reflectance = dn.astype("float32") * scale + offset
        reflectance[dn == 0] = np.nan
        if resolution == 10:
            reflectance = aggregate_2x2(reflectance)
        optical.append(reflectance)
        radiometry[key] = {"scale": scale, "offset": offset, "formula": "DN * scale + offset",
                          "native_metres": resolution, "aggregation": "aligned 2x2 mean" if resolution == 10 else "none",
                          "url": public_url(asset), "raw_crop_array_sha256": raw_hashes[key]}
        print(item["id"], key, "20 m reflectance", reflectance.shape, flush=True)
    optical = np.stack(optical)
    with rasterio.open(public_url(item["assets"]["scl"])) as source:
        if source.crs != grid["crs"] or source.res != (20, 20) or source.window_transform(window) != grid["transform"]:
            raise ValueError("SCL native grid differs")
        scl = source.read(1, window=window)
    ndwi, mndwi, mask = indices(optical[1], optical[3], optical[4])
    valid = mask & np.isin(scl, ACCEPTED_SCL) & np.all(np.isfinite(optical) & (optical >= 0), axis=0)
    output = np.concatenate([optical, ndwi[None], mndwi[None], valid[None].astype("float32"), scl[None].astype("float32")])
    output[:7, ~valid] = -9999
    output[~np.isfinite(output)] = -9999
    path = folder / (item["id"] + "_indices20m.tif")
    with rasterio.open(path, "w", driver="GTiff", count=9, dtype="float32", nodata=-9999, compress="deflate", **grid) as destination:
        destination.write(output)
        for band, name in enumerate((*BANDS, "NDWI", "MNDWI", "usable", "SCL"), 1):
            destination.set_band_description(band, name)
    return grid, output, {"id": item["id"], "collection": item["collection"],
                          "acquired_at": item["properties"]["datetime"], "radiometry": radiometry,
                          "crop_file": path.name, "crop_sha256": sha256(path.read_bytes()).hexdigest()}


def proxy_diagnostic(array, paired):
    """SCL groups are correlated proxies, NOT independent accuracy labels."""
    report = {}
    for mode, band in (("ndwi", 5), ("mndwi", 6)):
        report[mode] = {}
        for label, code in (("scl_water_proxy", 6), ("scl_bare_proxy", 5), ("scl_vegetation_proxy", 4)):
            values = array[band][paired & (array[8] == code)]
            report[mode][label] = {"pixels": int(values.size), "median": float(np.median(values)) if values.size else None,
                                   "p10_p90": np.quantile(values, [.1, .9]).tolist() if values.size else None}
    return report


def example_pixel(arrays, grid, common):
    """Visually inspected river-location pixel; NOT a ground-truth water label."""
    _, _, window = area_slices(REGIONS["jatunyacu_detail"], grid)
    x, y = 133, 133
    row, col = int(window.row_off) + y, int(window.col_off) + x
    if not common[row, col]:
        raise ValueError("Illustrative pixel is outside the three-date valid support")
    values = arrays[1][:, row, col]
    easting, northing = grid["transform"] * (col + .5, row + .5)
    lon, lat = transform(grid["crs"], "EPSG:4326", [easting], [northing])
    return {"acquired_at": "2024-08-08", "region": "jatunyacu_detail", "local_col_row": [x, y],
            "grid_col_row": [col, row], "longitude_latitude": [lon[0], lat[0]],
            "green": float(values[1]), "nir": float(values[3]), "swir": float(values[4]),
            "ndwi": float(values[5]), "mndwi": float(values[6]), "scl": int(values[8]),
            "meaning": "Real reflectance example at visually inspected river location; SCL=6 proxy; possibly mixed, not verified water",
            "caveat": "Higher MNDWI than NDWI is not more water; different band contrasts"}


def build(folder):
    folder.mkdir(parents=True, exist_ok=True)
    old_path = folder / "manifest.json"
    old = json.loads(old_path.read_text(encoding="utf-8")) if old_path.exists() else {}
    grid, arrays, rows = None, [], []
    with rasterio.Env(**ENV):
        for collection, identifier in SCENES:
            if identifier == "SELECT_AFTER_LOCAL_QA":
                raise ValueError("Pin the reviewed 2024 candidate first")
            path = folder / (identifier + ".stac.json")
            item = json.loads(path.read_text(encoding="utf-8")) if path.exists() else fetch_json(API + f"/collections/{collection}/items/{identifier}")
            if item["id"] != identifier or item["collection"] != collection:
                raise ValueError("Wrong pinned acquisition")
            json_save(path, item)
            cached = next((row for row in old.get("scenes", []) if row["id"] == identifier), None)
            if cached and old.get("recipe") == "aligned20m_v2" and sha256((folder / cached["crop_file"]).read_bytes()).hexdigest() == cached["crop_sha256"]:
                with rasterio.open(folder / cached["crop_file"]) as source:
                    newgrid = dict(crs=source.crs, transform=source.transform, width=source.width, height=source.height)
                    array = source.read()
                if grid is not None and grid != newgrid:
                    raise ValueError("Cached grid differs")
                grid, row = newgrid, cached
            else:
                grid, array, row = crop(item, folder, grid)
            arrays.append(array)
            rows.append(row)
    common = np.logical_and.reduce([array[7] == 1 for array in arrays])
    reports = {}
    for key, area in REGIONS.items():
        y, x, window = area_slices(area, grid)
        paired = common[y, x]
        reports[key] = {**area, "width": paired.shape[1], "height": paired.shape[0],
                        "common_valid_fraction": float(paired.mean()), "native_bounds": list(bounds(window, grid["transform"])),
                        "diagnostic_caveat": "SCL correlated proxies, not ground truth or accuracy",
                        "proxy_diagnostics": {str(year): proxy_diagnostic(array[:, y, x], paired) for year, array in zip((2019, 2024, 2026), arrays)}}
        for year, array in zip((2019, 2024, 2026), arrays):
            rgb = (np.clip(array[:3, y, x] / .3, 0, 1) ** (1 / 1.2)).transpose(1, 2, 0)
            Image.fromarray(np.dstack([(rgb * 255).astype("uint8"), paired.astype("uint8") * 255])).save(folder / f"{key}_{year}_rgb.png")
            for mode, band in (("ndwi", 5), ("mndwi", 6)):
                Image.fromarray(color_ndwi(array[band, y, x], paired)).save(folder / f"{key}_{year}_{mode}.png")
        print(key, "three-date common", round(paired.mean() * 100, 1), "%", flush=True)
    manifest = {"schema_version": 2, "recipe": "aligned20m_v2", "status": "educational_preview_not_validated_channel_change",
                "dates": [row["acquired_at"] for row in rows], "scenes": rows, "formulas": FORMULAS,
                "bbox": BBOX, "grid": {**grid, "crs": str(grid["crs"]), "transform": list(grid["transform"])[:6]},
                "qa": {"accepted_scl": ACCEPTED_SCL, "common_valid_support": True, "all_three_dates_and_both_indices": True,
                       "all_five_bands_finite_nonnegative": True, "native_scl_metres": 20},
                "display": {"rgb_min_max": [0, .3], "gamma": 1.2, "index_min_max": [-1, 1], "same_palette_both_indices_all_dates": True},
                "regions": reports, "composite": "none; individual acquisitions, not atlas annual medians",
                "illustrative_pixel": example_pixel(arrays, grid, common),
                "images_sha256": {p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(folder.glob("*.png"))},
                "sources": {**SOURCES, "mndwi": "https://doi.org/10.1080/01431160600589179"},
                "limits": ["SCL is imperfect; clouds/shadows/haze and negative reflectance are masked, not filled",
                           "20 m comparison: B3 and B8 averaged from 10 m before ratios; B11 native 20 m",
                           "No validated water threshold, no area or migration estimate, no mining attribution",
                           "Dates do not have matched discharge, recent rainfall or seasonal river state",
                           "SCL diagnostic proxies cannot establish independent classification accuracy"]}
    json_save(old_path, manifest)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, default=FOLDER)
    parser.add_argument("--audit-2024", action="store_true")
    args = parser.parse_args()
    audit_2024(args.folder) if args.audit_2024 else build(args.folder)
