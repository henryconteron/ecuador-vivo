"""Diagnostic paired radar statistics, not a deforestation detector."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

import numpy as np
from rasterio.features import geometry_mask
from rasterio.io import MemoryFile
from rasterio.warp import transform_geom

from tools.parcelas.catalog import validate_parcel


def paired_statistics(before, after, valid):
    if before.shape != after.shape or before.shape != valid.shape:
        raise ValueError("Arrays must share the same grid shape")
    keep = valid & np.isfinite(before) & np.isfinite(after) & (before > 0) & (after > 0)
    count = int(keep.sum())
    if not count:
        return {"paired_pixel_centres": 0, "ratio_of_means_db": None}
    first, second = before[keep].astype("float64"), after[keep].astype("float64")
    return {"paired_pixel_centres": count, "before_mean_linear": float(first.mean()),
            "after_mean_linear": float(second.mean()),
            "ratio_of_means_db": float(10 * np.log10(second.mean() / first.mean())),
            "median_pixel_log_ratio_db": float(np.median(10 * np.log10(second / first)))}


def read_export(path, expected_sha):
    if path.stat().st_size > 5_000_000:
        raise ValueError("Diagnostic archive exceeds 5 MB limit")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha:
        raise ValueError("Archive checksum mismatch")
    layers = {}
    with zipfile.ZipFile(path) as archive:
        if len(archive.infolist()) != 2:
            raise ValueError("Expected exactly two polarization files")
        for member in archive.infolist():
            if member.file_size > 10_000_000:
                raise ValueError("Unpacked raster exceeds safety limit")
            matches = [band for band in ("VV", "VH") if member.filename.endswith(f"_{band}_(Raw).tiff")]
            if len(matches) != 1 or matches[0] in layers:
                raise ValueError("Unknown or duplicate polarization filename")
            with MemoryFile(archive.read(member)) as memory:
                with memory.open() as source:
                    if source.count != 2 or source.dtypes != ("float32", "float32") or not source.crs:
                        raise ValueError("Expected float32 values + explicit dataMask and CRS")
                    if source.width * source.height > 100_000:
                        raise ValueError("Raster exceeds diagnostic pixel limit")
                    values, mask = source.read()
                    if not np.isin(mask, [0, 1]).all():
                        raise ValueError("Invalid dataMask")
                    layers[matches[0]] = {"values": values, "mask": mask == 1,
                        "grid": (source.crs.to_string(), tuple(source.transform), source.shape)}
    return layers


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Output exists; choose a new directory")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest["processing"] != {"backscatter": "GAMMA0_TERRAIN", "dem": "COPERNICUS_30", "speckle": "NONE", "upsampling": "NEAREST", "units": "LINEAR_POWER"}:
        raise ValueError("Unverified processing contract")
    parcel_path = (args.manifest.parent / manifest["parcel"]).resolve()
    parcel = json.loads(parcel_path.read_text(encoding="utf-8"))
    validate_parcel(parcel)
    exports = manifest["exports"]
    if len(exports) != 2 or exports[0]["date"] >= exports[1]["date"]:
        raise ValueError("Two exports in chronological order required")
    layers = [read_export((args.manifest.parent / item["archive"]).resolve(), item["sha256"]) for item in exports]
    grids = [layer["grid"] for export in layers for layer in export.values()]
    if any(grid != grids[0] for grid in grids):
        raise ValueError("CRS, transform and raster shape must match exactly")
    crs, transform, dimensions = grids[0]
    from affine import Affine
    geometry = transform_geom("EPSG:4326", crs, parcel["features"][0]["geometry"])
    inside = geometry_mask([geometry], dimensions, Affine(*transform[:6]), invert=True, all_touched=False)
    common = inside.copy()
    for export in layers:
        for band in export.values():
            common &= band["mask"] & np.isfinite(band["values"]) & (band["values"] > 0)
    statistics = {band: paired_statistics(layers[0][band]["values"], layers[1][band]["values"], common) for band in ("VV", "VH")}
    result = {"status": "two_date_numeric_diagnostic_not_deforestation", "processing": manifest["processing"],
              "exports": exports, "grid": {"crs": crs, "transform": transform, "shape": dimensions},
              "pixel_centres_in_parcel": int(inside.sum()), "statistics": statistics,
              "limitations": ["Two dates are not a validated temporal baseline.",
                "Noise, moisture, phenology and processing can change backscatter without deforestation.",
                "dataMask does not establish absence of radar shadow/layover.",
                "Browser processing settings were observed in the UI, not independently reproduced in SNAP.",
                "Scene lineage, acquisition geometry and radiometric comparability still require verification."]}
    args.output.mkdir(parents=True)
    (args.output / "radar-pair.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    lines = ["# Ecuador Vivo · comparación radar diagnóstica", "", "**No demuestra deforestación ni cumplimiento EUDR.**", "",
             f"Fechas: {exports[0]['date']} y {exports[1]['date']}. Grillas idénticas, gamma0 terreno; potencia lineal.", "",
             "| Banda | Centros válidos comunes | Cambio de la media, en dB |", "|---|---:|---:|"]
    for band, values in statistics.items():
        change = values["ratio_of_means_db"]
        label = "Sin soporte" if change is None else f"{change:+.3f}"
        lines.append(f"| {band} | {values['paired_pixel_centres']} | {label} |")
    lines.extend(["", "Cambio = 10 log10(media posterior / media anterior), no porcentaje de pérdida forestal.", "", *["- " + warning for warning in result["limitations"]]])
    (args.output / "INFORME.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(statistics))


if __name__ == "__main__":
    main()
