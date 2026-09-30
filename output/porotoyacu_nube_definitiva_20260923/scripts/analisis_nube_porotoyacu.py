#!/usr/bin/env python3
"""Analisis reproducible de la nube clasificada de Porotoyacu.

Lee LAZ/LAS por bloques para no cargar toda la nube en memoria. Produce:
  - inventario y estadisticas globales (CSV, JSON y Markdown),
  - conteo por clase,
  - densidad total y Ground sobre una cuadricula comun,
  - retencion Ground y mascara de soporte directo,
  - GeoTIFFs para QGIS,
  - una figura cientifica de cuatro paneles (PNG y PDF), y
  - una comparacion global antes/despues (PNG y PDF).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

import laspy
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch
from matplotlib.ticker import ScalarFormatter
from rasterio.transform import from_origin
import rasterio


CLASS_NAMES = {
    0: "Created / never classified",
    1: "Unclassified",
    2: "Ground",
    3: "Low vegetation",
    4: "Medium vegetation",
    5: "High vegetation",
    6: "Building",
    7: "Low point / noise",
    8: "Reserved / model key-point",
    9: "Water",
    10: "Rail",
    11: "Road surface",
    12: "Reserved / overlap",
    13: "Wire guard",
    14: "Wire conductor",
    15: "Transmission tower",
    16: "Wire connector",
    17: "Bridge deck",
    18: "High noise",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analiza densidad y retencion Ground de una nube LAS/LAZ clasificada."
    )
    parser.add_argument("laz", type=Path, help="Archivo LAS/LAZ clasificado")
    parser.add_argument(
        "--salida", type=Path, default=Path("resultados_porotoyacu"),
        help="Carpeta de resultados",
    )
    parser.add_argument(
        "--celda", type=float, default=2.0,
        help="Tamano de celda en metros (predeterminado: 2)",
    )
    parser.add_argument(
        "--clase-ground", type=int, default=2,
        help="Codigo LAS de Ground (predeterminado: 2)",
    )
    parser.add_argument(
        "--area-declarada-km2", type=float, default=0.36,
        help="Area indicada en el manuscrito; use 0 para omitirla",
    )
    parser.add_argument(
        "--puntos-esperados", type=int, default=13_610_808,
        help="Conteo mostrado por Metashape; use 0 para omitir la comprobacion",
    )
    parser.add_argument(
        "--chunk", type=int, default=1_000_000,
        help="Puntos leidos por bloque",
    )
    return parser.parse_args()


def safe_percentiles(values: np.ndarray) -> dict[str, float]:
    if values.size == 0:
        return {k: float("nan") for k in ("p25", "p50", "p75", "p95", "p99")}
    p = np.percentile(values, [25, 50, 75, 95, 99])
    return dict(zip(("p25", "p50", "p75", "p95", "p99"), map(float, p)))


def scalar_formatter(ax: plt.Axes) -> None:
    fmt = ScalarFormatter(useOffset=False)
    fmt.set_scientific(False)
    ax.xaxis.set_major_formatter(fmt)
    ax.yaxis.set_major_formatter(fmt)


def write_geotiff(
    path: Path,
    array_south_up: np.ndarray,
    xmin: float,
    ymax: float,
    cell: float,
    crs,
    nodata,
    dtype: str,
) -> None:
    data = np.flipud(array_south_up).astype(dtype, copy=False)
    profile = {
        "driver": "GTiff",
        "height": data.shape[0],
        "width": data.shape[1],
        "count": 1,
        "dtype": dtype,
        "transform": from_origin(xmin, ymax, cell, cell),
        "crs": crs,
        "nodata": nodata,
        "compress": "deflate",
        "predictor": 2 if np.issubdtype(data.dtype, np.floating) else 1,
        "tiled": True,
    }
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(data, 1)


def main() -> int:
    args = parse_args()
    laz_path = args.laz.resolve()
    out_dir = args.salida.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not laz_path.is_file():
        raise FileNotFoundError(f"No se encontro: {laz_path}")
    if args.celda <= 0:
        raise ValueError("--celda debe ser mayor que cero")

    print(f"Leyendo encabezado: {laz_path}")
    with laspy.open(laz_path) as reader:
        header = reader.header
        total_header = int(header.point_count)
        mins = np.asarray(header.mins, dtype=float)
        maxs = np.asarray(header.maxs, dtype=float)
        try:
            crs = header.parse_crs()
        except Exception:
            crs = None

        xmin, ymin, zmin = mins
        xmax, ymax, zmax = maxs
        ncols = max(1, int(math.ceil((xmax - xmin) / args.celda)))
        nrows = max(1, int(math.ceil((ymax - ymin) / args.celda)))
        ncells = nrows * ncols

        all_counts = np.zeros(ncells, dtype=np.uint32)
        ground_counts = np.zeros(ncells, dtype=np.uint32)
        class_counts = np.zeros(256, dtype=np.int64)

        total_read = 0
        ground_read = 0
        z_sum = 0.0
        z_sum2 = 0.0
        zg_sum = 0.0
        zg_sum2 = 0.0

        print(
            f"Puntos declarados: {total_header:,}; cuadricula: "
            f"{ncols} x {nrows} celdas de {args.celda:g} m"
        )
        for block_number, points in enumerate(
            reader.chunk_iterator(args.chunk), start=1
        ):
            x = np.asarray(points.x, dtype=np.float64)
            y = np.asarray(points.y, dtype=np.float64)
            z = np.asarray(points.z, dtype=np.float64)
            classes = np.asarray(points.classification, dtype=np.uint8)

            cols = np.floor((x - xmin) / args.celda).astype(np.int64)
            rows = np.floor((y - ymin) / args.celda).astype(np.int64)
            np.clip(cols, 0, ncols - 1, out=cols)
            np.clip(rows, 0, nrows - 1, out=rows)
            flat = rows * ncols + cols

            all_counts += np.bincount(flat, minlength=ncells).astype(np.uint32)
            class_counts += np.bincount(classes, minlength=256)

            ground_mask = classes == args.clase_ground
            ground_n = int(np.count_nonzero(ground_mask))
            if ground_n:
                ground_counts += np.bincount(
                    flat[ground_mask], minlength=ncells
                ).astype(np.uint32)
                zg = z[ground_mask]
                zg_sum += float(np.sum(zg, dtype=np.float64))
                zg_sum2 += float(np.dot(zg, zg))

            n = len(points)
            total_read += n
            ground_read += ground_n
            z_sum += float(np.sum(z, dtype=np.float64))
            z_sum2 += float(np.dot(z, z))
            print(
                f"  bloque {block_number:02d}: {total_read:,}/{total_header:,} puntos",
                end="\r",
                flush=True,
            )

    print()
    all_grid = all_counts.reshape(nrows, ncols)
    ground_grid = ground_counts.reshape(nrows, ncols)
    support_all = all_grid > 0
    support_ground = ground_grid > 0
    cell_area = args.celda**2
    density_all = all_grid.astype(np.float64) / cell_area
    density_ground = ground_grid.astype(np.float64) / cell_area
    retention = np.full((nrows, ncols), np.nan, dtype=np.float64)
    retention[support_all] = (
        100.0 * ground_grid[support_all] / all_grid[support_all]
    )

    occupied_cells = int(np.count_nonzero(support_all))
    ground_cells = int(np.count_nonzero(support_ground))
    support_area_m2 = occupied_cells * cell_area
    n_removed = total_read - ground_read
    retention_global = 100.0 * ground_read / total_read if total_read else float("nan")
    removed_global = 100.0 - retention_global
    ground_support_pct = 100.0 * ground_cells / occupied_cells if occupied_cells else float("nan")

    mean_z = z_sum / total_read if total_read else float("nan")
    std_z = math.sqrt(max(0.0, z_sum2 / total_read - mean_z**2)) if total_read else float("nan")
    mean_zg = zg_sum / ground_read if ground_read else float("nan")
    std_zg = math.sqrt(max(0.0, zg_sum2 / ground_read - mean_zg**2)) if ground_read else float("nan")

    all_local = density_all[support_all]
    ground_local = density_ground[support_all]  # incluye ceros Ground
    all_pct = safe_percentiles(all_local)
    ground_pct = safe_percentiles(ground_local)

    crs_text = crs.to_string() if crs is not None else "No identificado"
    epsg = crs.to_epsg() if crs is not None else None
    is_metric_projected = bool(
        crs is not None and getattr(crs, "is_projected", False)
    )
    warnings: list[str] = []
    if total_read != total_header:
        warnings.append(
            f"Se leyeron {total_read:,} puntos, pero el encabezado declara {total_header:,}."
        )
    if args.puntos_esperados and total_header != args.puntos_esperados:
        diff = total_header - args.puntos_esperados
        warnings.append(
            f"El LAZ contiene {total_header:,} puntos y Metashape mostraba "
            f"{args.puntos_esperados:,}: diferencia {diff:+,} "
            f"({100.0 * diff / args.puntos_esperados:+.4f}%)."
        )
    if not is_metric_projected:
        warnings.append(
            "El CRS no parece proyectado; las densidades no pueden interpretarse como puntos/m2."
        )
    if epsg is not None and epsg != 32718:
        warnings.append(f"Se esperaba EPSG:32718, pero el archivo reporta EPSG:{epsg}.")

    summary = {
        "archivo": str(laz_path),
        "tamano_bytes": laz_path.stat().st_size,
        "formato_las": str(header.version),
        "formato_punto": int(header.point_format.id),
        "crs": crs_text,
        "epsg": epsg,
        "xmin_m": float(xmin),
        "xmax_m": float(xmax),
        "ymin_m": float(ymin),
        "ymax_m": float(ymax),
        "zmin_m": float(zmin),
        "zmax_m": float(zmax),
        "ancho_m": float(xmax - xmin),
        "alto_m": float(ymax - ymin),
        "puntos_total": int(total_read),
        "puntos_ground": int(ground_read),
        "puntos_no_ground": int(n_removed),
        "retencion_ground_pct": retention_global,
        "exclusion_no_ground_pct": removed_global,
        "celda_m": args.celda,
        "celdas_soporte_total": occupied_cells,
        "area_soporte_celdas_m2": support_area_m2,
        "densidad_total_sobre_soporte_pts_m2": total_read / support_area_m2,
        "densidad_ground_sobre_mismo_soporte_pts_m2": ground_read / support_area_m2,
        "celdas_con_ground": ground_cells,
        "cobertura_directa_ground_pct": ground_support_pct,
        "elevacion_total_media_m": mean_z,
        "elevacion_total_sd_m": std_z,
        "elevacion_ground_media_m": mean_zg,
        "elevacion_ground_sd_m": std_zg,
        "densidad_local_total_pts_m2": all_pct,
        "densidad_local_ground_pts_m2": ground_pct,
        "advertencias": warnings,
    }
    if args.area_declarada_km2 > 0:
        declared_m2 = args.area_declarada_km2 * 1_000_000.0
        summary.update(
            {
                "area_declarada_km2": args.area_declarada_km2,
                "densidad_total_area_declarada_pts_m2": total_read / declared_m2,
                "densidad_ground_area_declarada_pts_m2": ground_read / declared_m2,
            }
        )

    with (out_dir / "resumen_global.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    with (out_dir / "resumen_global.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as f:
        writer = csv.writer(f)
        writer.writerow(["metrica", "valor"])
        for key, value in summary.items():
            if isinstance(value, (dict, list)):
                writer.writerow([key, json.dumps(value, ensure_ascii=False)])
            else:
                writer.writerow([key, value])

    with (out_dir / "conteo_por_clase.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as f:
        writer = csv.writer(f)
        writer.writerow(["codigo_clase", "nombre_clase", "puntos", "porcentaje_total"])
        for code in np.flatnonzero(class_counts):
            count = int(class_counts[code])
            writer.writerow(
                [
                    int(code),
                    CLASS_NAMES.get(int(code), f"Clase {int(code)}"),
                    count,
                    100.0 * count / total_read,
                ]
            )

    # Rasters: fuera de la huella = nodata; los ceros Ground dentro de la huella son validos.
    nodata_float = -9999.0
    d_all_out = np.where(support_all, density_all, nodata_float).astype(np.float32)
    d_ground_out = np.where(support_all, density_ground, nodata_float).astype(np.float32)
    retention_out = np.where(support_all, retention, nodata_float).astype(np.float32)
    support_code = np.full((nrows, ncols), 255, dtype=np.uint8)
    support_code[support_all] = 1
    support_code[support_ground] = 2

    write_geotiff(
        out_dir / "densidad_total_pts_m2.tif", d_all_out, xmin, ymax,
        args.celda, crs, nodata_float, "float32"
    )
    write_geotiff(
        out_dir / "densidad_ground_pts_m2.tif", d_ground_out, xmin, ymax,
        args.celda, crs, nodata_float, "float32"
    )
    write_geotiff(
        out_dir / "retencion_ground_pct.tif", retention_out, xmin, ymax,
        args.celda, crs, nodata_float, "float32"
    )
    write_geotiff(
        out_dir / "soporte_ground.tif", support_code, xmin, ymax,
        args.celda, crs, 255, "uint8"
    )

    # Figura de cuatro paneles.
    plot_all = np.where(support_all, density_all, np.nan)
    plot_ground = np.where(support_all, density_ground, np.nan)
    vmax = float(np.percentile(all_local, 99)) if all_local.size else 1.0
    if vmax <= 0:
        vmax = 1.0
    extent = (xmin, xmin + ncols * args.celda, ymin, ymin + nrows * args.celda)

    fig, axes = plt.subplots(2, 2, figsize=(11.4, 12.4), constrained_layout=True)
    im0 = axes[0, 0].imshow(
        plot_all, origin="lower", extent=extent, cmap="viridis", vmin=0, vmax=vmax
    )
    axes[0, 0].set_title("A  All reconstructed points")
    axes[0, 1].imshow(
        plot_ground, origin="lower", extent=extent, cmap="viridis", vmin=0, vmax=vmax
    )
    axes[0, 1].set_title("B  Ground-classified points")
    im2 = axes[1, 0].imshow(
        retention, origin="lower", extent=extent, cmap="cividis", vmin=0, vmax=100
    )
    axes[1, 0].set_title("C  Ground-point retention")

    support_plot = np.where(support_code == 255, np.nan, support_code.astype(float))
    cmap_support = ListedColormap(["#e69f00", "#0072b2"])
    norm_support = BoundaryNorm([0.5, 1.5, 2.5], cmap_support.N)
    axes[1, 1].imshow(
        support_plot, origin="lower", extent=extent, cmap=cmap_support, norm=norm_support
    )
    axes[1, 1].set_title("D  Direct Ground support")
    axes[1, 1].legend(
        handles=[
            Patch(facecolor="#e69f00", label="All points, no Ground"),
            Patch(facecolor="#0072b2", label="Ground present"),
        ],
        loc="lower left", frameon=True, fontsize=8,
    )

    for ax in axes.flat:
        ax.set_xlabel("Easting (m), WGS 84 / UTM 18S")
        ax.set_ylabel("Northing (m)")
        ax.set_aspect("equal")
        scalar_formatter(ax)
    cb_density = fig.colorbar(im0, ax=axes[0, :], shrink=0.84, pad=0.02)
    cb_density.set_label(f"Point density (points/m²); shared scale, P99={vmax:.1f}")
    cb_ret = fig.colorbar(im2, ax=axes[1, 0], shrink=0.84, pad=0.02)
    cb_ret.set_label("Ground / all points (%)")
    fig.suptitle(
        f"Porotoyacu point-cloud validation | {args.celda:g} x {args.celda:g} m cells",
        fontsize=15,
    )
    fig.savefig(out_dir / "figura_validacion_nube_4_paneles.png", dpi=300)
    fig.savefig(out_dir / "figura_validacion_nube_4_paneles.pdf")
    plt.close(fig)

    # Comparacion global sobre exactamente la misma huella espacial.
    global_densities = [total_read / support_area_m2, ground_read / support_area_m2]
    fig, ax = plt.subplots(figsize=(6.8, 5.2), constrained_layout=True)
    bars = ax.bar(
        ["All reconstructed\npoints", "Ground-classified\npoints"],
        global_densities,
        color=["#6c757d", "#0072b2"],
        width=0.62,
    )
    ax.bar_label(bars, fmt="%.2f points/m²", padding=4, fontsize=10)
    ax.set_ylabel("Mean density over the same all-point support (points/m²)")
    ax.set_title(f"Ground retention = {retention_global:.2f}%")
    ax.set_ylim(0, max(global_densities) * 1.22 if max(global_densities) > 0 else 1)
    ax.grid(axis="y", alpha=0.25)
    fig.savefig(out_dir / "figura_comparacion_densidad_global.png", dpi=300)
    fig.savefig(out_dir / "figura_comparacion_densidad_global.pdf")
    plt.close(fig)

    lines = [
        "# Resultados de validacion de la nube de Porotoyacu",
        "",
        f"- Archivo: `{laz_path.name}`",
        f"- CRS: {crs_text}",
        f"- Puntos totales: {total_read:,}",
        f"- Puntos Ground (clase {args.clase_ground}): {ground_read:,}",
        f"- Puntos no Ground: {n_removed:,}",
        f"- Retencion Ground: {retention_global:.4f}%",
        f"- Exclusion para el DTM: {removed_global:.4f}%",
        f"- Tamano de celda: {args.celda:g} m",
        f"- Area de soporte por celdas ocupadas: {support_area_m2 / 1e6:.6f} km2",
        f"- Densidad total sobre esa misma area: {total_read / support_area_m2:.4f} puntos/m2",
        f"- Densidad Ground sobre esa misma area: {ground_read / support_area_m2:.4f} puntos/m2",
        f"- Celdas de la huella con al menos un punto Ground: {ground_support_pct:.4f}%",
        "",
        "## Percentiles de densidad local sobre celdas de la huella total",
        "",
        "| Conjunto | P25 | P50 | P75 | P95 | P99 |",
        "|---|---:|---:|---:|---:|---:|",
        "| All | " + " | ".join(f"{all_pct[k]:.3f}" for k in ("p25", "p50", "p75", "p95", "p99")) + " |",
        "| Ground | " + " | ".join(f"{ground_pct[k]:.3f}" for k in ("p25", "p50", "p75", "p95", "p99")) + " |",
        "",
        "## Advertencias",
        "",
    ]
    lines.extend([f"- {w}" for w in warnings] or ["- Ninguna."])
    lines.extend(
        [
            "",
            "## Texto base para Results (revisar antes de incorporar)",
            "",
            (
                "The classified SfM point cloud contained "
                f"{total_read:,} points, of which {ground_read:,} ({retention_global:.2f}%) "
                "were retained as Ground for DTM generation. Using a common "
                f"{args.celda:g} x {args.celda:g} m grid and the all-point support as the "
                f"reference footprint, mean density decreased from {total_read / support_area_m2:.2f} "
                f"to {ground_read / support_area_m2:.2f} points/m2 after classification. "
                f"Direct Ground observations occurred in {ground_support_pct:.2f}% of occupied cells; "
                "the remaining cells therefore lacked direct terrain support at this analysis scale."
            ),
            "",
            "Nota: `no Ground` significa excluido de la entrada del DTM; no implica necesariamente "
            "que cada punto haya sido vegetacion.",
        ]
    )
    (out_dir / "informe_resultados.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\nANALISIS TERMINADO")
    print(f"Resultados: {out_dir}")
    print(f"Total: {total_read:,}; Ground: {ground_read:,} ({retention_global:.4f}%)")
    for warning in warnings:
        print(f"ADVERTENCIA: {warning}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise

