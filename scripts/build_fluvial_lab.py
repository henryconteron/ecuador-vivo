"""Fetch pinned free Sentinel-2 COG windows and publish numerical web packs.

20 m native UTM comparison; average aligned 2x2 10 m reflectance samples.
Optional --reuse uses previously verified native five-band crops, not JPEGs.
The public application loads one region/date at a time, verifies SHA-256, and
computes signals from float32 reflectance; it never measures PNG colours.
"""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

import numpy as np
import rasterio
from affine import Affine
from rasterio.windows import Window, from_bounds, bounds
from rasterio.warp import transform_bounds, reproject, Resampling
from fluvial_science import signals

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ("blue", "green", "red", "nir", "swir16", "swir22")
ENV = dict(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
           GDAL_HTTP_TIMEOUT="30", GDAL_HTTP_MAX_RETRY="2")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def item_for(scene, config, raw):
    path = raw / (scene["id"] + ".stac.json")
    if not path.exists():
        url = f'{config["api"]}/collections/{scene["collection"]}/items/{scene["id"]}'
        with urlopen(url, timeout=40) as response:
            item = json.load(response)
        save(path, item)
    item = json.loads(path.read_text(encoding="utf-8"))
    if item.get("id") != scene["id"] or item.get("collection") != scene["collection"] or not item["properties"]["datetime"].startswith(scene["date"]):
        raise ValueError("Pinned acquisition mismatch")
    return item, sha(path)


def asset_url(asset):
    url = asset["href"]
    if url.startswith("s3://"):
        bucket, key = url[5:].split("/", 1)
        url = f"https://{bucket}.s3.us-west-2.amazonaws.com/{key}"
    if not url.startswith("https://"):
        raise ValueError("Public HTTPS COG required")
    return url


def aligned_window(dataset, box):
    w = from_bounds(*box, dataset.transform)
    values = [w.col_off, w.row_off, w.width, w.height]
    if not np.allclose(values, np.round(values), atol=1e-6, rtol=0):
        raise ValueError("Input bands must align exactly")
    return Window(*[int(round(x)) for x in values])


def native(item, region, config, raw, reuse=None):
    path = raw / f'{item["id"]}-{region["id"]}.tif'
    # Rebuild every publication. Raw downloads are cached only with their provenance.
    with rasterio.open(asset_url(item["assets"]["swir16"])) as ds:
        if ds.crs.to_epsg() != 32717 or ds.res != (20, 20):
            raise ValueError("Native 20 m UTM 17S required")
        box = transform_bounds("EPSG:4326", ds.crs, *region["bbox"])
        requested = from_bounds(*box, ds.transform)
        left, top = np.floor([requested.col_off, requested.row_off]).astype(int)
        right, bottom = np.ceil([requested.col_off + requested.width, requested.row_off + requested.height]).astype(int)
        win = Window(left, top, right - left, bottom - top)
        grid = dict(crs=ds.crs, transform=ds.window_transform(win), width=int(win.width), height=int(win.height))
    box = bounds(Window(0, 0, grid["width"], grid["height"]), grid["transform"])
    parent = None; reused = None
    if reuse:
        pm = json.loads((reuse / "manifest.json").read_text(encoding="utf-8"))
        row = next(r for r in pm["scenes"] if r["id"] == item["id"])
        crop_path = reuse / row["crop_file"]
        if row["collection"] != item["collection"] or sha(crop_path) != row["crop_sha256"]:
            raise ValueError("Reused native source checksum mismatch")
        with rasterio.open(crop_path) as ds:
            w = aligned_window(ds, box)
            if ds.crs != grid["crs"] or ds.window_transform(w) != grid["transform"] or ds.count != 9 or ds.descriptions[:5] != ("red", "green", "blue", "nir", "swir16"):
                raise ValueError("Reused source grid or bands mismatch")
            reused = ds.read([3, 2, 1, 4, 5], window=w)
            reused[reused == -9999] = np.nan
        parent = {"manifest_sha256": sha(reuse / "manifest.json"), "crop_sha256": sha(crop_path), "crop_file": crop_path.name}
    optical, provenance = [], []
    for i, key in enumerate(ASSETS):
        asset = item["assets"][key]
        band = asset["raster:bands"][0]
        scale, offset = band["scale"], band.get("offset", 0)
        if not np.isfinite([scale, offset]).all() or scale <= 0:
            raise ValueError("Invalid radiometric calibration")
        if item["collection"] == "sentinel-2-l2a" and item["properties"].get("earthsearch:boa_offset_applied") and offset:
            raise ValueError("Ambiguous legacy BOA offset; use C1")
        resolution = 10 if i < 4 else 20
        if reused is not None and i < 5:
            old = row["radiometry"][key]
            if old["scale"] != scale or old["offset"] != offset or old["url"] != asset_url(asset):
                raise ValueError("Reused reflectance calibration mismatch")
            values = reused[i]
            raw_sha = old["raw_crop_array_sha256"]
        else:
            cache = raw / f'{item["id"]}-{region["id"]}-{key}.npy'
            with rasterio.open(asset_url(asset)) as ds:
                w = aligned_window(ds, box)
                if ds.crs != grid["crs"] or ds.res != (resolution, resolution) or ds.nodata != 0 or ds.window_transform(w) != grid["transform"] * Affine.scale(resolution / 20):
                    raise ValueError("Band resolution/registration/NoData mismatch")
                dn = np.load(cache) if cache.exists() else ds.read(1, window=w)
                if dn.shape != (grid["height"] * (20 // resolution), grid["width"] * (20 // resolution)):
                    raise ValueError("Cached crop shape mismatch")
                if not cache.exists(): np.save(cache, dn)
            raw_sha = hashlib.sha256(dn.tobytes()).hexdigest()
            values = dn.astype(np.float32) * scale + offset
            values[dn == 0] = np.nan
            if resolution == 10:
                h, w = values.shape
                values = values.reshape(h // 2, 2, w // 2, 2).mean(axis=(1, 3))
        optical.append(values)
        provenance.append({"band": config["bands"][i], "url": asset_url(asset), "scale": scale, "offset": offset,
                           "native_m": resolution, "aggregation": "aligned-2x2-mean" if resolution == 10 else "none",
                           "raw_array_sha256": raw_sha, "reused_parent_crop": bool(reused is not None and i < 5)})
    optical = np.stack(optical)
    with rasterio.open(asset_url(item["assets"]["scl"])) as ds:
        w = aligned_window(ds, box)
        if ds.crs != grid["crs"] or ds.res != (20, 20) or ds.window_transform(w) != grid["transform"]:
            raise ValueError("SCL registration mismatch")
        scl = ds.read(1, window=w)
    valid = np.isin(scl, config["accepted_scl"]) & np.all(np.isfinite(optical) & (optical >= 0), axis=0)
    valid &= np.all([np.isfinite(v) for v in signals(optical).values()], axis=0)
    optical[:, ~valid] = -9999
    output = np.concatenate([optical, valid[None].astype(np.float32)])
    with rasterio.open(path, "w", driver="GTiff", count=7, dtype="float32", nodata=-9999, compress="deflate", **grid) as ds:
        ds.write(output)
        for i, key in enumerate(config["bands"], 1): ds.set_band_description(i, key)
    return output, grid, {"native_file": path.name, "native_sha256": sha(path), "radiometry": provenance,
                          "scl_url": asset_url(item["assets"]["scl"]), "scl_raw_sha256": hashlib.sha256(scl.tobytes()).hexdigest(),
                          "reused_parent": parent}


def publish(config, reuse=None):
    raw = ROOT / "data/raw/fluvial"; raw.mkdir(parents=True, exist_ok=True)
    output = ROOT / "data/fluvial"; output.mkdir(parents=True, exist_ok=True)
    result = {"schema_version": 1, "status": "exploratory-not-field-validated", "built_at": datetime.now(timezone.utc).isoformat(),
              "config": config, "builder_sha256": sha(__file__), "science_sha256": sha(Path(__file__).with_name("fluvial_science.py")),
              "benchmark": {"status": "pending-independent-references", "winner": None}, "regions": []}
    with rasterio.Env(**ENV):
        for region in config["regions"]:
            record = {**region, "scenes": []}; template = None; useful = []
            for scene in config["scenes"]:
                print(region["id"], scene["date"], flush=True)
                item, stac_sha = item_for(scene, config, raw)
                data, grid, provenance = native(item, region, config, raw, reuse)
                if template is not None and grid != template: raise ValueError("Native date grids differ")
                template = grid
                if "width" not in record:
                    left, bottom, right, top = transform_bounds(grid["crs"], "EPSG:3857", *bounds(Window(0, 0, grid["width"], grid["height"]), grid["transform"]))
                    # Web grid uses native dimensions; actual web spacing is recorded, not called exactly 20 m.
                    web = Affine((right - left) / grid["width"], 0, left, 0, -(top - bottom) / grid["height"], top)
                    record.update(width=grid["width"], height=grid["height"], web_extent=[left, bottom, right, top],
                                  web_transform=list(web)[:6], native_transform=list(grid["transform"])[:6])
                converted = np.full(data.shape, -9999, dtype=np.float32)
                for i in range(7):
                    reproject(data[i], converted[i], src_transform=grid["transform"], src_crs=grid["crs"],
                              dst_transform=web, dst_crs="EPSG:3857", resampling=Resampling.nearest,
                              src_nodata=-9999, dst_nodata=-9999)
                mask = converted[6] == 1
                # Encode QA explicitly as exact binary values; invalid warp edges
                # never become valid zero reflectance or a dry-bed observation.
                converted[6] = mask.astype(np.float32)
                converted[:6, ~mask] = -9999
                pack = gzip.compress(converted.astype("<f4").tobytes(), compresslevel=9, mtime=0)
                path = output / f'{region["id"]}-{scene["date"]}.bin.gz'
                path.write_bytes(pack)
                # Give metadata its own public hash; native TIFFs remain local/ignored.
                metadata = output / f'{scene["id"]}.stac.json'; save(metadata, item)
                record["scenes"].append({**scene, "acquired_at": item["properties"]["datetime"], "stac_url": f'{config["api"]}/collections/{scene["collection"]}/items/{scene["id"]}',
                                         "stac_file": metadata.relative_to(ROOT).as_posix(), "stac_sha256": sha(metadata),
                                         "url": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "size_bytes": len(pack),
                                         "decoded_bytes": converted.nbytes, "native_usable_pixels": int(data[6].sum()),
                                         "web_usable_pixels": int(mask.sum()), **provenance})
                useful.append(mask)
            record["web_common_pixels"] = int(np.logical_and.reduce(useful).sum())
            result["regions"].append(record)
    save(output / "manifest.json", result)
    print("Published", sum(s["size_bytes"] for r in result["regions"] for s in r["scenes"]), "bytes", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reuse", type=Path, help="Optional verified aligned20m_v2 native source folder")
    args = parser.parse_args()
    publish(json.loads((ROOT / "data/fluvial/config.json").read_text(encoding="utf-8")), args.reuse)
