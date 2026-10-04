"""Prepare a standalone, checksum-audited river video from native observations.

Optional local hand-off of six-band crops, not screenshots or web-reprojected
images. All output lives in a new ignored artifact folder; no old video changes.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image
import rasterio
from rasterio.windows import Window, from_bounds
from rasterio.warp import transform_bounds

from prepare_napo_ndwi import color_ndwi

FOLDER = Path("artifacts/rios_napo_metodos_v4")
METHODS = ("ndwi", "mndwi", "aweinsh", "aweish")
DATES = ("2019-07-11", "2024-08-08", "2026-07-29")
BANDS = ("B2", "B3", "B4", "B8", "B11", "B12", "valid")
FORMULAS = {"ndwi": "(B3-B8)/(B3+B8)", "mndwi": "(B3-B11)/(B3+B11)",
            "aweinsh": "4*(B3-B11)-0.25*B8-2.75*B12",
            "aweish": "B2+2.5*B3-1.5*(B8+B11)-0.25*B12",
            "ndti": "(B4-B3)/(B4+B3)", "ndvi": "(B8-B4)/(B8+B4)"}
DETAIL = [-77.842, -1.092, -77.808, -1.058]
CHANGE_COLORS = [(0, 0, 0), (45, 64, 62), (47, 141, 184),
                 (226, 112, 89), (112, 215, 168), (255, 207, 118)]


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ratio(a, b):
    good = np.isfinite(a) & np.isfinite(b) & (a >= 0) & (b >= 0) & (a + b > 0)
    result = np.full(a.shape, np.nan, dtype="float32")
    np.divide(a - b, a + b, out=result, where=good)
    return result


def signals(bands):
    blue, green, red, nir, swir1, swir2 = bands
    return {"ndwi": ratio(green, nir), "mndwi": ratio(green, swir1),
            "aweinsh": 4 * (green - swir1) - .25 * nir - 2.75 * swir2,
            "aweish": blue + 2.5 * green - 1.5 * (nir + swir1) - .25 * swir2,
            "ndti": ratio(red, green), "ndvi": ratio(nir, red)}


def agreement(values, common, threshold=0):
    # Exploratory threshold; shared bands mean shared errors, NOT confidence.
    count = np.sum([values[key] > threshold for key in METHODS], axis=0)
    return np.where(common, count, -1).astype("int8")


def transitions(before, after):
    if before.shape != after.shape:
        raise ValueError("Change requires aligned grids")
    result = np.zeros(before.shape, dtype="uint8")
    common = (before >= 0) & (after >= 0)
    result[common] = 5
    result[common & (before == 0) & (after == 0)] = 1
    result[common & (before == 4) & (after == 4)] = 2
    result[common & (before == 4) & (after == 0)] = 3
    result[common & (before == 0) & (after == 4)] = 4
    return result


def categorical(values, colors, valid):
    return np.dstack([np.array(colors, dtype="uint8")[np.maximum(values, 0)], valid.astype("uint8") * 255])


def signal_color(values, valid, colors):
    scaled = np.clip((np.nan_to_num(values) + 1) * 2, 0, 4)
    stops = np.asarray(colors)
    rgb = np.stack([np.interp(scaled, np.arange(5), stops[:, c]) for c in range(3)], axis=-1).astype("uint8")
    return np.dstack([rgb, valid.astype("uint8")*255])


def checked_copy(source, target, expected):
    if digest(source) != expected:
        raise ValueError("Source checksum mismatch: " + source.name)
    if target.exists() and digest(target) != expected:
        raise ValueError("Conflicting artifact; use another output folder: " + target.name)
    shutil.copy2(source, target)


def read_native(path):
    with rasterio.open(path) as ds:
        if ds.crs.to_epsg() != 32717 or ds.res != (20, 20) or ds.descriptions != BANDS:
            raise ValueError("Expected calibrated six-band native 20 m UTM crop")
        array = ds.read()
        if not np.isin(array[6], [0, 1]).all():
            raise ValueError("QA must be exactly binary")
        array[:6][array[:6] == ds.nodata] = np.nan
        return array, ds.transform


def prepare(source_root, folder=FOLDER):
    source_root, folder = Path(source_root), Path(folder)
    parent_path = source_root / "data/fluvial/manifest.json"
    parent = json.loads(parent_path.read_text(encoding="utf-8"))
    config = parent["config"]
    if config["bands"] != list(BANDS) or config["formulas"] != FORMULAS or config["sampling_m"] != 20:
        raise ValueError("Unreviewed source recipe")
    if config["threshold_status"] != "exploratory-not-locally-calibrated":
        raise ValueError("Unexpected threshold claims")
    folder.mkdir(parents=True, exist_ok=True)
    checked_copy(parent_path, folder / "source_manifest.json", digest(parent_path))
    regions, sources, images = {}, [], {}
    for region in parent["regions"]:
        arrays, grid = [], None
        if tuple(row["date"] for row in region["scenes"]) != DATES:
            raise ValueError("Unexpected source acquisitions")
        for row in region["scenes"]:
            native = source_root / "data/raw/fluvial" / row["native_file"]
            target = folder / row["native_file"]
            checked_copy(native, target, row["native_sha256"])
            checked_copy(source_root / row["stac_file"], folder / (row["id"] + ".stac.json"), row["stac_sha256"])
            item = json.loads((folder / (row["id"] + ".stac.json")).read_text(encoding="utf-8"))
            if item["id"] != row["id"] or item["collection"] != row["collection"] or not item["properties"]["datetime"].startswith(row["date"]):
                raise ValueError("Acquisition identity mismatch")
            array, transform = read_native(target)
            current = (array.shape, tuple(transform))
            if grid is not None and current != grid:
                raise ValueError("Dates not on identical native grid")
            grid = current
            if not np.allclose(tuple(transform)[:6], region["native_transform"], rtol=0, atol=1e-8):
                raise ValueError("Parent native grid mismatch")
            arrays.append(array)
            sources.append({**row, "region": region["id"], "local_file": target.name})
        windows = [(region["id"], region["name"], region["bbox"], arrays, transform)]
        if region["id"] == "jatunyacu":
            box = transform_bounds("EPSG:4326", "EPSG:32717", *DETAIL)
            requested = from_bounds(*box, transform)
            left, top = np.floor([requested.col_off, requested.row_off]).astype(int)
            right, bottom = np.ceil([requested.col_off + requested.width, requested.row_off + requested.height]).astype(int)
            if left < 0 or top < 0 or right > arrays[0].shape[2] or bottom > arrays[0].shape[1]:
                raise ValueError("Detail outside source")
            cut = [a[:, top:bottom, left:right] for a in arrays]
            windows.append(("jatunyacu_detail", "Jatunyacu · detalle", DETAIL, cut,
                            rasterio.windows.transform(Window(left, top, right-left, bottom-top), transform)))
        for key, name, bbox, cut, transform in windows:
            values = [signals(a[:6]) for a in cut]
            common = np.all([a[6] == 1 for a in cut], axis=0)
            common &= np.all([np.all(np.isfinite(a[:6]) & (a[:6] >= 0), axis=0) for a in cut], axis=0)
            common &= np.all([np.all([np.isfinite(v) for v in s.values()], axis=0) for s in values], axis=0)
            if common.mean() < .55:
                raise ValueError("Too little useful common support")
            votes = [agreement(s, common) for s in values]
            regions[key] = {"name": name, "bbox": bbox, "width": common.shape[1], "height": common.shape[0],
                            "transform": list(transform)[:6], "common_valid_fraction": float(common.mean())}
            for i, (date, a, sig, count) in enumerate(zip(DATES, cut, values, votes)):
                year = int(date[:4])
                rgb = (np.clip(np.nan_to_num(a[[2, 1, 0]]) / .3, 0, 1) ** (1/1.2) * 255).astype("uint8")
                views = {"rgb": np.dstack([rgb.transpose(1, 2, 0), common.astype("uint8")*255])}
                for mode in FORMULAS:
                    views[mode] = color_ndwi(np.nan_to_num(sig[mode]), common)
                # Different questions get different palettes: green is verdor;
                # red-green sediment contrast never inherits the water-blue cue.
                views["ndvi"] = signal_color(sig["ndvi"], common,
                    [(64,82,100), (169,159,139), (239,231,203), (136,174,95), (24,100,61)])
                views["ndti"] = signal_color(sig["ndti"], common,
                    [(44,87,112), (139,169,164), (239,231,203), (211,160,94), (132,70,39)])
                # Grey = not unanimous candidate water, NOT missing observations.
                for mode in ("ndti",):
                    views[mode][common & (count != 4), :3] = [91, 100, 98]
                views["agreement"] = categorical(np.where(count == 4, 2, np.where(count == 0, 0, 1)),
                                                  [(45,64,62), (255,207,118), (47,141,184)], common)
                if i:
                    views["change"] = categorical(transitions(votes[i-1], count), CHANGE_COLORS, common)
                for mode, view in views.items():
                    filename = f"{key}_{year}_{mode}.png"
                    Image.fromarray(view).save(folder / filename)
                    images[filename] = digest(folder / filename)
    manifest = {"recipe": "native20m_methods_video_v4", "dates": list(DATES), "bands": list(BANDS),
                "formulas": FORMULAS, "source_manifest_sha256": digest(parent_path), "sources": sources,
                "regions": regions, "images_sha256": images, "sampling_m": 20,
                "qa": "six-band QA and finite signals; exact common support of all three dates",
                "thresholds": {key: 0 for key in METHODS}, "threshold_status": "exploratory-not-locally-calibrated",
                "winner": None, "classification": "candidate agreement only; not independent truth",
                "benchmark": "not run; independent reference labels unavailable",
                "ndti": "red-green contrast only in unanimous candidate water; not NTU or concentration",
                "awei_display": "fixed editorial -1/+1 clipping; AWEI is not normalized",
                "rgb_display": "reflectance 0/.3 gamma1.2; identical dates; no generated river imagery",
                "palettes": {"ndvi": "fixed bluegrey-neutral-green; higher means greener contrast",
                             "ndti": "fixed bluegrey-neutral-brown; higher red-green contrast, not calibrated turbidity"},
                "references": config["references"], "builder_sha256": digest(Path(__file__))}
    save(folder / "manifest.json", manifest)
    print(f"Prepared {len(images)} real observation views in {folder}", flush=True)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True, help="Local native-crop hand-off directory; read only")
    parser.add_argument("--folder", type=Path, default=FOLDER)
    args = parser.parse_args()
    prepare(args.source_root, args.folder)
