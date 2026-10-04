"""Preserve v4 observations; add a real threshold demonstration for story v5."""
import argparse
from pathlib import Path
import json

import numpy as np
from PIL import Image
from rasterio.windows import Window, from_bounds, transform as window_transform

from prepare_napo_methods import checked_copy, digest, read_native, signals, categorical
from reel_napo_methods import FOLDER as PREVIOUS, load_evidence

FOLDER = Path("artifacts/rios_historia_v5")


def prepare(source=PREVIOUS, folder=FOLDER):
    source, folder = Path(source), Path(folder)
    if source.resolve() == folder.resolve():
        raise ValueError("Keep previous video evidence unchanged")
    m = load_evidence(source)
    folder.mkdir(parents=True, exist_ok=True)
    files = {"manifest.json": digest(source / "manifest.json"),
             "source_manifest.json": m["source_manifest_sha256"], **m["images_sha256"]}
    for row in m["sources"]:
        files[row["local_file"]] = row["native_sha256"]
        files[row["id"] + ".stac.json"] = row["stac_sha256"]
    for name, expected in files.items():
        checked_copy(source / name, folder / name, expected)
    # Compute from calibrated native arrays, never from screenshot colours.
    row = next(r for r in m["sources"] if r["region"] == "jatunyacu" and r["date"] == "2024-08-08")
    a, grid = read_native(source / row["local_file"])
    detail = m["regions"]["jatunyacu_detail"]
    from affine import Affine
    target_grid = Affine(*detail["transform"])
    x, y = (~grid) * (target_grid.c, target_grid.f)
    if not np.allclose([x,y], np.round([x,y]), atol=1e-7):
        raise ValueError("Detail must align exactly")
    x, y = int(round(x)), int(round(y))
    w, h = detail["width"], detail["height"]
    if x < 0 or y < 0 or x+w > a.shape[2] or y+h > a.shape[1]:
        raise ValueError("Detail must stay inside native evidence")
    values = signals(a[:6, y:y+h, x:x+w])["mndwi"]
    with Image.open(source / "jatunyacu_detail_2024_mndwi.png") as image:
        common = np.asarray(image)[:, :, 3] == 255
    if common.shape != values.shape or not np.isfinite(values[common]).all():
        raise ValueError("Common support mismatch")
    products, counts = {}, {}
    for label, threshold in (("low", 0.0), ("high", 0.2)):
        candidate = values > threshold
        count = int((candidate & common).sum())
        name = f"threshold_{label}.png"
        Image.fromarray(categorical(candidate.astype("uint8"), [(35,57,55),(54,174,202)], common)).save(folder / name)
        products[name] = digest(folder / name)
        counts[label] = count
    if counts["low"] <= counts["high"]:
        raise ValueError("Threshold demonstration has no visible candidate change")
    evidence = {"status": "editorial-threshold-demonstration-not-water-validation", "date": "2024-08-08",
                "method": "mndwi", "thresholds": {"low":0, "high":0.2},
                "candidate_pixels": counts, "support_pixels": int(common.sum()),
                "native_source_sha256": row["native_sha256"],
                "source_manifest_sha256": digest(source / "manifest.json"),
                "images_sha256": products, "meaning": "detector changes, not observed water volume",
                "builder_sha256": digest(Path(__file__))}
    (folder / "hook_evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2)+"\n",encoding="utf-8")
    print(json.dumps(counts), flush=True)
    return evidence


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=PREVIOUS)
    parser.add_argument("--folder", type=Path, default=FOLDER)
    args=parser.parse_args()
    prepare(args.source,args.folder)
