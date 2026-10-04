"""Preserve earlier episodes and prepare audited continuous MNDWI demonstration."""
import argparse
import json
from pathlib import Path

import numpy as np
from affine import Affine
from PIL import Image

from prepare_river_story import prepare
from prepare_napo_methods import digest, read_native, signals

FOLDER = Path("artifacts/rios_historia_v6")


def build(folder=FOLDER):
    folder = Path(folder)
    prepare(folder=folder)
    m = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    row = next(r for r in m["sources"] if r["region"] == "jatunyacu" and r["date"] == "2024-08-08")
    a, grid = read_native(folder / row["local_file"])
    detail = m["regions"]["jatunyacu_detail"]
    x, y = (~grid) * (Affine(*detail["transform"]).c, Affine(*detail["transform"]).f)
    if not np.allclose([x, y], np.round([x, y]), atol=1e-7):
        raise ValueError("Unaligned native demonstration")
    x, y = int(round(x)), int(round(y))
    h, w = detail["height"], detail["width"]
    if min(x, y) < 0 or y+h > a.shape[1] or x+w > a.shape[2]:
        raise ValueError("Demonstration is outside native evidence")
    values = signals(a[:6, y:y+h, x:x+w])["mndwi"]
    with Image.open(folder / "jatunyacu_detail_2024_mndwi.png") as im:
        common = np.asarray(im)[:, :, 3] == 255
    if values.shape != common.shape or not np.isfinite(values[common]).all():
        raise ValueError("Invalid common support")
    np.savez_compressed(folder / "threshold_values.npz", values=values, common=common)
    report = {
        "status": "exploratory-threshold-demonstration-not-local-validation",
        "date": "2024-08-08", "formula": "(B3-B11)/(B3+B11)",
        "threshold_range": [0, 0.2], "support_pixels": int(common.sum()),
        "candidate_pixels": {"low": int((common & (values > 0)).sum()),
                             "high": int((common & (values > .2)).sum())},
        "array_sha256": digest(folder / "threshold_values.npz"),
        "manifest_sha256": digest(folder / "manifest.json"),
        "native_source_sha256": row["native_sha256"],
        "builder_sha256": digest(Path(__file__)),
        "diagrams": "Original qualitative teaching diagrams; not site reconstructions or measured spectra",
    }
    (folder / "motion_evidence.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, default=FOLDER)
    build(parser.parse_args().folder)
