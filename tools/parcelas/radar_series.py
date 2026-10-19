"""Sparse radar observations with explicit gaps; no interpolation or EUDR decision."""
import argparse
from datetime import date
import json
from pathlib import Path

from affine import Affine
import numpy as np
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom
from shapely.geometry import shape

from tools.parcelas.catalog import validate_parcel
from tools.parcelas.radar_pair import read_export


def temporal_gaps(dates):
    parsed = [date.fromisoformat(value) for value in dates]
    if not parsed or any(after <= before for before, after in zip(parsed, parsed[1:])):
        raise ValueError("Dates must be unique and increasing")
    return [{"from": before.isoformat(), "to": after.isoformat(), "days": (after - before).days}
            for before, after in zip(parsed, parsed[1:]) if (after - before).days > 30]


def summarize_series(arrays, valid):
    common = valid.copy()
    for array in arrays:
        if array.shape != common.shape:
            raise ValueError("Raster shapes differ")
        common &= np.isfinite(array) & (array > 0)
    count = int(common.sum())
    rows = []
    for array in arrays:
        mean = float(array[common].astype("float64").mean()) if count else None
        rows.append({"paired_centres": count, "mean_linear": mean,
                     "db_of_mean_linear": float(10 * np.log10(mean)) if mean is not None else None})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Choose a new output directory")
    config = json.loads(args.manifest.read_text(encoding="utf-8"))
    expected = {"backscatter": "GAMMA0_TERRAIN", "dem": "COPERNICUS_30", "speckle": "NONE", "upsampling": "NEAREST", "units": "LINEAR_POWER"}
    if config["processing"] != expected or not 2 <= len(config["exports"]) <= 24:
        raise ValueError("Invalid processing contract or series length")
    exports = config["exports"]
    gaps = temporal_gaps([item["date"] for item in exports])
    parcel = json.loads((args.manifest.parent / config["parcel"]).read_text(encoding="utf-8"))
    validate_parcel(parcel)
    geometry = shape(parcel["features"][0]["geometry"])
    items = []
    for catalog in config["catalogs"]:
        items.extend(json.loads((args.manifest.parent / catalog).read_text(encoding="utf-8"))["features"])
    candidates, acquisition_keys = [], set()
    for export in exports:
        matches = {item["id"]: item for item in items if item.get("collection") == "sentinel-1-grd"
                   and item["properties"]["datetime"].startswith(export["date"])
                   and shape(item["geometry"]).covers(geometry)}
        if len(matches) != 1:
            raise ValueError("Expected one complete-coverage catalog candidate per date")
        item = next(iter(matches.values()))
        properties = item["properties"]
        fields = ("platform", "sar:instrument_mode", "sat:relative_orbit", "sat:orbit_state")
        key = tuple(properties.get(field) for field in fields)
        if None in key or not {"VV", "VH"}.issubset(properties.get("sar:polarizations", [])):
            raise ValueError("Insufficient acquisition metadata")
        acquisition_keys.add(key)
        candidates.append({"id": item["id"], "date": export["date"],
                           **{field: properties[field] for field in fields},
                           "scene_incidence_angle": properties.get("view:incidence_angle"),
                           "lineage_status": "unique_catalog_candidate_not_export_lineage_proof"})
    if len(acquisition_keys) != 1:
        raise ValueError("Do not mix platforms, relative orbits, modes or directions")
    layers = [read_export((args.manifest.parent / item["archive"]).resolve(), item["sha256"]) for item in exports]
    grids = [band["grid"] for layer in layers for band in layer.values()]
    if any(grid != grids[0] for grid in grids):
        raise ValueError("Series grid alignment must be exact")
    crs, transform, dimensions = grids[0]
    projected = transform_geom("EPSG:4326", crs, parcel["features"][0]["geometry"])
    common = geometry_mask([projected], dimensions, Affine(*transform[:6]), invert=True, all_touched=False)
    for layer in layers:
        for band in layer.values():
            common &= band["mask"] & np.isfinite(band["values"]) & (band["values"] > 0)
    results = {band: summarize_series([layer[band]["values"] for layer in layers], common) for band in ("VV", "VH")}
    report = {"status": "sparse_observation_diagnostic_not_deforestation", "processing": expected,
              "dates": [item["date"] for item in exports], "gaps_over_30_days": gaps,
              "common_centres_all_dates_and_bands": int(common.sum()), "results": results,
              "catalog_candidates": candidates, "interpolation": "none",
              "eudr_assessment": "not_performed", "history_of_crop_before_2021": "unknown"}
    args.output.mkdir(parents=True)
    (args.output / "radar-series.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = ["# Ecuador Vivo · observaciones radar históricas", "",
             "**Serie incompleta: no demuestra ausencia ni presencia de deforestación.**", "",
             "Porción de cacao CERSGIS 352, Ghana. Cultivo documentado en marzo de 2025; uso en 2020 desconocido.", "",
             "Gamma0 terreno, Copernicus DEM30, sin filtro speckle y NEAREST. Grillas idénticas.",
             "La cifra en dB es 10 log10 de la media en potencia lineal, no la media de los dB.", "",
             "| Fecha | Centros comunes | VV · dB de media | VH · dB de media |", "|---|---:|---:|---:|"]
    for index, item in enumerate(exports):
        values = [results[band][index]["db_of_mean_linear"] for band in ("VV", "VH")]
        labels = ["Sin soporte" if value is None else f"{value:.3f}" for value in values]
        lines.append(f"| {item['date']} | {int(common.sum())} | {labels[0]} | {labels[1]} |")
    lines.extend(["", "## Vacíos de observación", ""])
    lines.extend(f"- {gap['from']} a {gap['to']}: {gap['days']} días entre observaciones guardadas; sin interpolación." for gap in gaps)
    lines.extend(["", "## Límites", "", "- Igual satélite/órbita y una escena candidata con cobertura completa por fecha según catálogo; no prueba del linaje exacto de la exportación.",
                  "- dataMask acredita disponibilidad, no ausencia de sombra radar o layover.",
                  "- Humedad, fenología, speckle y procesamiento pueden cambiar la señal sin pérdida forestal.",
                  "- No hay línea base temporal validada, detector calibrado ni estimación de exactitud.",
                  "- La prueba en Ghana no valida resultados para Ecuador; estos polígonos no son linderos legales.",
                  "", "Fuente del polígono: CERSGIS (2025), https://doi.org/10.5281/zenodo.16579443 · CC BY 4.0."])
    (args.output / "INFORME.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"dates": report["dates"], "common_centres": int(common.sum()), "gaps": gaps}))


if __name__ == "__main__":
    main()
