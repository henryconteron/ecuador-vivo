"""Real Sentinel-2 scene crops for an educational Napo NDWI reel.

Public HTTPS COGs only: no account, payment, GEE export or annual composite.
The STAC asset's scale/offset is authoritative; do not guess it from the year.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
from PIL import Image
import requests
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject, transform_bounds
from rasterio.windows import Window, from_bounds

API = "https://earth-search.aws.element84.com/v1"
COLLECTION = "sentinel-2-l2a"
FOLDER = Path("artifacts/rios_napo_ndwi_2026")
BBOX = (-77.94, -1.095, -77.64, -.94)
SCENES = ((COLLECTION, "S2B_17MRU_20190711_0_L2A"),
          ("sentinel-2-c1-l2a", "S2C_T17MRU_20260729T153626_L2A"))
REGIONS = {
    "tena": {"name": "Tena · entorno urbano", "bbox": [-77.84, -1.025, -77.78, -.965]},
    "jatunyacu": {"name": "Jatunyacu · tramo inferior", "bbox": [-77.865, -1.095, -77.805, -1.035]},
    "napo": {"name": "Napo · aguas abajo de Puerto Napo", "bbox": [-77.775, -1.07, -77.715, -1.01]},
    "misahualli": {"name": "Entorno de Puerto Misahuallí", "bbox": [-77.695, -1.06, -77.64, -1.005]},
}
ACCEPTED_SCL = (4, 5, 6)  # Vegetation, not vegetated, water; not a verified water mask.
ASSETS = ("red", "green", "blue", "nir")
SOURCES = {
    "catalog": "https://github.com/Element84/earth-search/blob/main/README.md",
    "ndwi": "https://doi.org/10.1080/01431169608948714",
    "bands": "https://custom-scripts.sentinel-hub.com/custom-scripts/sentinel-2/ndwi/",
    "sentinel_terms": "https://dataspace.copernicus.eu/explore-data/collections/sentinel-data/sentinel-2",
    "external_context_not_our_results": "https://www.maapprogram.org/mining-ecuador-napo/",
}


def json_save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ratio(green, nir):
    green, nir = np.asarray(green, dtype="float32"), np.asarray(nir, dtype="float32")
    total = green + nir
    valid = np.isfinite(green) & np.isfinite(nir) & (green >= 0) & (nir >= 0) & (total > 0)
    result = np.full(green.shape, np.nan, dtype="float32")
    np.divide(green - nir, total, out=result, where=valid)
    return result, valid


def calibration(asset):
    bands = asset.get("raster:bands", [])
    if len(bands) != 1 or bands[0].get("nodata") != 0:
        raise ValueError("Missing or unexpected STAC radiometry / NoData")
    scale, offset = bands[0].get("scale"), bands[0].get("offset", 0)
    if scale != .0001 or not np.isfinite(offset) or offset not in (0, -.1):
        raise ValueError("Unreviewed reflectance calibration")
    return scale, offset


def usable(scl, optical):
    return np.isin(scl, ACCEPTED_SCL) & np.all(np.isfinite(optical) & (optical >= 0), axis=0)


def fetch_json(url, **params):
    response = requests.get(url, params=params, timeout=45)
    response.raise_for_status()
    return response.json()


def audit_catalog(folder):
    folder.mkdir(parents=True, exist_ok=True)
    searches = []
    for period in ("2019-07-01T00:00:00Z/2019-07-31T23:59:59Z",
                   "2026-09-01T00:00:00Z/2026-10-02T23:59:59Z"):
        result = fetch_json(API + "/search", collections=COLLECTION, bbox=",".join(map(str, BBOX)),
                            datetime=period, limit=100, sortby="-properties.datetime")
        searches.append({"period": period, "response": result})
        rows = [item for item in result["features"] if "17MRU" in item["id"]]
        print([(r["id"], r["properties"]["eo:cloud_cover"]) for r in rows], flush=True)
    json_save(folder / "catalog_searches.json", {"api": API, "bbox": BBOX, "retrieved_at": datetime.now(timezone.utc).isoformat(),
                                               "searches": searches, "note": "Search page only; cloud percentage is tile-wide, not local QA."})


def public_url(asset):
    url = asset["href"]
    if not url.startswith(("https://sentinel-cogs.s3.us-west-2.amazonaws.com/",
                           "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/")) or not url.endswith(".tif"):
        raise ValueError("Only reviewed anonymous HTTPS COGs are supported; no requester-pays assets")
    return url


def quality_audit(folder):
    """Rank local SCL support, never confuse tile-wide cloud with local quality."""
    result = fetch_json(API + "/search", collections=COLLECTION, bbox=",".join(map(str, BBOX)),
                        datetime="2026-01-01T00:00:00Z/2026-10-02T23:59:59Z", limit=100,
                        sortby="properties.eo:cloud_cover")
    # Low-cloud plus six most recent candidates: tile cloud alone is not a ranking of river quality.
    candidates = [item for item in result["features"] if "17MRU" in item["id"]][:10]
    recent = fetch_json(API + "/search", collections=COLLECTION, bbox=",".join(map(str, BBOX)),
                        datetime="2026-09-01T00:00:00Z/2026-10-02T23:59:59Z", limit=100,
                        sortby="-properties.datetime")
    known = {item["id"] for item in candidates}
    candidates += [item for item in [r for r in recent["features"] if "17MRU" in r["id"]][:6] if item["id"] not in known]
    reports = []
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
                      GDAL_HTTP_TIMEOUT="30", GDAL_HTTP_MAX_RETRY="1"):
        for item in candidates:
            fractions = {}
            with rasterio.open(public_url(item["assets"]["scl"])) as source:
                window = crop_window(BBOX, source)
                data = source.read(1, window=window)
                class GridSource:
                    crs = source.crs
                    transform = source.window_transform(window)
                for key, area in REGIONS.items():
                    local = crop_window(area["bbox"], GridSource)
                    crop = data[int(local.row_off):int(local.row_off + local.height),
                                int(local.col_off):int(local.col_off + local.width)]
                    fractions[key] = float(np.isin(crop, ACCEPTED_SCL).mean())
            row = {"id": item["id"], "date": item["properties"]["datetime"],
                   "tile_cloud": item["properties"]["eo:cloud_cover"], "scl_usable_fraction": fractions}
            reports.append(row)
            print(row, flush=True)
            json_save(folder / (item["id"] + ".stac.json"), item)
    json_save(folder / "quality_search.json", {"search": result, "recent_search": recent, "candidates": reports,
                                               "method": "10 low tile-cloud plus 6 most recent MRU candidates, unique IDs; local SCL only; not definitive pixel QA"})


def crop_window(bounds, source):
    west, south, east, north = transform_bounds("EPSG:4326", source.crs, *bounds)
    raw = from_bounds(west, south, east, north, source.transform)
    start_x, start_y = int(np.floor(raw.col_off)), int(np.floor(raw.row_off))
    stop_x, stop_y = int(np.ceil(raw.col_off + raw.width)), int(np.ceil(raw.row_off + raw.height))
    return Window(start_x, start_y, stop_x - start_x, stop_y - start_y)


def crop_scene(item, folder, template=None):
    if item["collection"] == COLLECTION and item["properties"].get("earthsearch:boa_offset_applied") is True:
        if any(calibration(item["assets"][key])[1] != 0 for key in ASSETS):
            raise ValueError("Ambiguous already-applied legacy BOA offset; use Collection 1, not a silent override")
    with rasterio.open(public_url(item["assets"]["green"])) as source:
        if source.crs.to_epsg() != 32717 or source.res != (10, 10):
            raise ValueError("Unexpected native scene grid")
        window = crop_window(BBOX, source)
        grid = {"crs": source.crs, "transform": source.window_transform(window),
                "height": int(window.height), "width": int(window.width)}
    if template is not None and grid != template:
        raise ValueError("Dates do not share an identical native grid")
    optical, radiometry, raw_hashes = [], {}, {}
    for key in ASSETS:
        asset = item["assets"][key]
        scale, offset = calibration(asset)
        with rasterio.open(public_url(asset)) as source:
            if source.crs != grid["crs"] or source.res != (10, 10) or source.nodata != 0:
                raise ValueError("Unexpected optical CRS, resolution or NoData")
            if source.window_transform(window) != grid["transform"]:
                raise ValueError("Optical bands are not aligned")
            dn = source.read(1, window=window)
        raw_hashes[key] = sha256(dn.tobytes()).hexdigest()
        reflectance = dn.astype("float32") * scale + offset
        reflectance[dn == 0] = np.nan
        optical.append(reflectance)
        radiometry[key] = {"formula": "DN * scale + offset", "scale": scale, "offset": offset,
                          "url": public_url(asset), "nodata": 0}
        print(item["id"], key, "cropped", dn.shape, flush=True)
    optical = np.stack(optical)
    with rasterio.open(public_url(item["assets"]["scl"])) as source:
        if source.res != (20, 20) or source.crs != grid["crs"]:
            raise ValueError("SCL must be native 20 m in the same CRS")
        scl_window = crop_window(BBOX, source)
        scl_raw = source.read(1, window=scl_window)
        scl = np.zeros((grid["height"], grid["width"]), dtype="uint8")
        reproject(scl_raw, scl, src_transform=source.window_transform(scl_window), src_crs=source.crs,
                  dst_transform=grid["transform"], dst_crs=grid["crs"], resampling=Resampling.nearest,
                  src_nodata=0, dst_nodata=0)
    ndwi, denominator_mask = ratio(optical[1], optical[3])
    valid = usable(scl, optical) & denominator_mask
    output = np.concatenate([optical, ndwi[None], valid[None].astype("float32"), scl[None].astype("float32")])
    output[:5, ~valid] = -9999
    output[~np.isfinite(output)] = -9999
    path = folder / (item["id"] + "_crop.tif")
    with rasterio.open(path, "w", driver="GTiff", count=7, dtype="float32", nodata=-9999,
                       compress="deflate", **grid) as destination:
        destination.write(output)
        for band, name in enumerate((*ASSETS, "NDWI", "usable", "SCL"), 1):
            destination.set_band_description(band, name)
    row = {"id": item["id"], "collection": item["collection"], "acquired_at": item["properties"]["datetime"],
           "tile_cloud_percent": item["properties"]["eo:cloud_cover"], "radiometry": radiometry,
           "crop_file": path.name, "crop_sha256": sha256(path.read_bytes()).hexdigest(),
           "raw_optical_crop_array_sha256": raw_hashes, "valid_fraction": float(valid.mean())}
    return grid, row, output


def verify_c1_calibration(item, folder):
    """Direct aligned pixel comparison with the already-corrected legacy COG.

    Never use ambiguous legacy STAC offsets for the scientific export. Check
    four small native-band windows, record the evidence, then use C1 metadata.
    """
    legacy = fetch_json(API + f"/collections/{COLLECTION}/items/S2C_17MRU_20260729_0_L2A")
    json_save(folder / (legacy["id"] + ".stac.json"), legacy)
    if legacy["properties"].get("earthsearch:boa_offset_applied") is not True:
        raise ValueError("Calibration audit legacy flag changed")
    if legacy["properties"]["s2:product_uri"] != item["properties"]["s2:product_uri"]:
        raise ValueError("Calibration audit must compare the exact same product")
    window = Window(5500, 1000, 12, 12)
    report = {"legacy_id": legacy["id"], "c1_id": item["id"], "product_uri": item["properties"]["s2:product_uri"],
              "native_window": [5500, 1000, 12, 12], "bands": {}}
    for key in ASSETS:
        with rasterio.open(public_url(legacy["assets"][key])) as source:
            previous = source.read(1, window=window).astype("int32")
            original_transform, original_crs = source.transform, source.crs
        with rasterio.open(public_url(item["assets"][key])) as source:
            if source.crs != original_crs or source.transform != original_transform:
                raise ValueError("Calibration audit grids differ")
            current = source.read(1, window=window).astype("int32")
        differences = np.unique(current - previous)
        if not np.array_equal(differences, [1000]) or np.any(previous == 0):
            raise ValueError("Unexpected C1 / legacy pixel difference; review calibration")
        scale, offset = calibration(item["assets"][key])
        if not np.allclose(current * scale + offset, previous * .0001, atol=1e-7):
            raise ValueError("C1 asset calibration does not reproduce corrected reflectance")
        report["bands"][key] = {"c1_minus_legacy_dn": differences.tolist(), "scale": scale, "offset": offset,
                                "c1_array_sha256": sha256(current.tobytes()).hexdigest(),
                                "legacy_array_sha256": sha256(previous.tobytes()).hexdigest()}
    report["status"] = "passed; metadata offset applied once to uncorrected C1; legacy not used for 2026 export"
    json_save(folder / "calibration_audit.json", report)
    return report


def color_ndwi(index, valid):
    # Quantized visualization only, not source values or a classified water mask.
    stops = np.array([[116, 70, 46], [220, 199, 157], [242, 237, 212], [47, 141, 184], [7, 61, 105]])
    scaled = np.clip((index + 1) * 2, 0, 4)
    rgb = np.stack([np.interp(scaled, np.arange(5), stops[:, c]) for c in range(3)], axis=-1).astype("uint8")
    return np.dstack([rgb, valid.astype("uint8") * 255])


def views(folder, arrays, grid):
    common = (arrays[0][5] == 1) & (arrays[1][5] == 1)
    reports = {}
    for key, area in REGIONS.items():
        class GridSource:
            crs = grid["crs"]
            transform = grid["transform"]
        window = crop_window(area["bbox"], GridSource)
        y = slice(int(window.row_off), int(window.row_off + window.height))
        x = slice(int(window.col_off), int(window.col_off + window.width))
        paired = common[y, x]
        reports[key] = {**area, "width": paired.shape[1], "height": paired.shape[0],
                        "common_valid_fraction": float(paired.mean()),
                        "usable_2019": float((arrays[0][5, y, x] == 1).mean()),
                        "usable_2026": float((arrays[1][5, y, x] == 1).mean()),
                        "native_bounds": list(rasterio.windows.bounds(window, grid["transform"]))}
        for year, array in zip((2019, 2026), arrays):
            rgb = np.clip(np.maximum(array[:3, y, x], 0) / .3, 0, 1) ** (1 / 1.2)
            rgba = np.dstack([(rgb.transpose(1, 2, 0) * 255).astype("uint8"), paired.astype("uint8") * 255])
            Image.fromarray(rgba).save(folder / f"{key}_{year}_rgb.png")
            Image.fromarray(color_ndwi(array[4, y, x], paired)).save(folder / f"{key}_{year}_ndwi.png")
        print(key, "common usable:", round(paired.mean() * 100, 1), "%", flush=True)
    return reports


def build(folder):
    folder.mkdir(parents=True, exist_ok=True)
    items, rows, arrays, grid = [], [], [], None
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
                      GDAL_HTTP_TIMEOUT="30", GDAL_HTTP_MAX_RETRY="2", GDAL_HTTP_RETRY_DELAY="1"):
        for collection, identifier in SCENES:
            path = folder / (identifier + ".stac.json")
            item = json.loads(path.read_text(encoding="utf-8")) if path.exists() else fetch_json(API + f"/collections/{collection}/items/{identifier}")
            if item["id"] != identifier or item["collection"] != collection:
                raise ValueError("Unexpected source item")
            json_save(path, item)
            items.append(item)
            if collection == "sentinel-2-c1-l2a":
                radiometry_audit = verify_c1_calibration(item, folder)
            # Reuse checksum-verified source crops; the C1 radiometry audit still runs above.
            old_manifest = folder / "manifest.json"
            old_rows = json.loads(old_manifest.read_text(encoding="utf-8"))["scenes"] if old_manifest.exists() else []
            cached = next((r for r in old_rows if r["id"] == identifier), None)
            if cached and cached.get("collection") == collection and sha256((folder / cached["crop_file"]).read_bytes()).hexdigest() == cached["crop_sha256"]:
                with rasterio.open(folder / cached["crop_file"]) as source:
                    cached_grid = {"crs": source.crs, "transform": source.transform, "height": source.height, "width": source.width}
                    array = source.read()
                if grid is not None and grid != cached_grid:
                    raise ValueError("Cached grid mismatch")
                grid, row = cached_grid, {**cached, "collection": collection}
            else:
                grid, row, array = crop_scene(item, folder, grid)
            rows.append(row)
            arrays.append(array)
    regions = views(folder, arrays, grid)
    files = {p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(folder.glob("*.png"))}
    manifest = {"schema_version": 1, "status": "educational_preview_not_validated_channel_change",
                "dates": [r["acquired_at"] for r in rows], "bbox": BBOX, "api": API,
                "collections": [r["collection"] for r in rows], "calibration_audit": radiometry_audit,
                "formula": "(B3-B8)/(B3+B8)", "composite": "none; one acquisition per year",
                "grid": {**grid, "crs": str(grid["crs"]), "transform": list(grid["transform"])[:6]},
                "qa": {"accepted_scl": ACCEPTED_SCL, "scl_native_metres": 20, "resampling": "nearest",
                       "cloud_score_plus": False, "nonnegative_joint_optical": True,
                       "common_valid_support": True, "visual_review_required": True},
                "scenes": rows, "regions": regions, "images_sha256": files, "sources": SOURCES,
                "limits": ["same calendar month does not ensure same discharge, weather or season state; dates differ by 18 calendar days",
                           "10 m pixels mix water, banks and vegetation; narrow streams may be unresolved",
                           "SCL filtering does not guarantee cloud/shadow-free observations",
                           "no mining, pollution, hectares, river migration or causation inferred",
                           "four editorial crops, not all rivers of the province"],
                "attribution": "Contains modified Copernicus Sentinel data (2019, 2026); processed by Henry Conteron; distributed via Element 84 Earth Search / AWS open data."}
    json_save(folder / "manifest.json", manifest)
    print("Source-pinned educational crops ready:", folder.resolve(), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, default=FOLDER)
    parser.add_argument("--audit", action="store_true", help="Search metadata only; no pixel products")
    parser.add_argument("--quality-audit", action="store_true", help="Inspect local SCL support for ten bounded candidates")
    args = parser.parse_args()
    if args.audit:
        audit_catalog(args.folder)
    elif args.quality_audit:
        quality_audit(args.folder)
    else:
        build(args.folder)
