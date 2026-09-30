"""Rebuild point-cloud evidence and publication figures from one frozen LAZ.

Only geometry (not elevations) is read from the historical 32-profile CSV.
The source cloud is never modified.  All output files are derived anew.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import laspy
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import LightSource, Normalize
import numpy as np
import pandas as pd
import rasterio
from rasterio.fill import fillnodata
from rasterio.transform import from_origin
from scipy.ndimage import distance_transform_edt, gaussian_filter, map_coordinates


GROUND = 2
NOISE = 7
REPRESENTATIVE = (32, 21, 18, 11, 4)
TRACE_M = 60.0
LENGTH_M = 180.0
MAX_SWATH_M = 7.5


def arguments():
    p = argparse.ArgumentParser()
    p.add_argument("--laz", type=Path, required=True)
    p.add_argument("--geometry-csv", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--chunk", type=int, default=1_000_000)
    return p.parse_args()


def sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def geometries(path: Path):
    table = pd.read_csv(
        path,
        usecols=["numero", "distancia_m", "x_utm18s", "y_utm18s"],
    )
    result = []
    for num, group in table.groupby("numero", sort=True):
        group = group.sort_values("distancia_m")
        a, b = group.iloc[0], group.iloc[-1]
        x0, y0 = float(a.x_utm18s), float(a.y_utm18s)
        x1, y1 = float(b.x_utm18s), float(b.y_utm18s)
        length = math.hypot(x1 - x0, y1 - y0)
        if not 179.0 <= length <= 181.0 or x1 <= x0:
            raise ValueError(f"P{num}: invalid west-to-east 180 m geometry ({length:.3f} m)")
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        result.append({
            "number": int(num), "name": f"P{num}", "x0": x0, "y0": y0,
            "x1": x1, "y1": y1, "ux": ux, "uy": uy, "length": length,
            "azimuth_deg": (math.degrees(math.atan2(x1-x0, y1-y0)) + 360) % 360,
            "trace_x": x0 + TRACE_M * ux, "trace_y": y0 + TRACE_M * uy,
            "xmin": min(x0, x1)-MAX_SWATH_M,
            "xmax": max(x0, x1)+MAX_SWATH_M,
            "ymin": min(y0, y1)-MAX_SWATH_M,
            "ymax": max(y0, y1)+MAX_SWATH_M,
        })
    if [g["number"] for g in result] != list(range(1, 33)):
        raise ValueError("Exactly 32 ordered profiles P1-P32 are required")
    return result


def extract_cloud(laz: Path, geoms, chunk_size: int):
    with laspy.open(laz) as reader:
        header = reader.header
        crs = header.parse_crs()
        if crs is None or crs.to_epsg() != 32718:
            raise ValueError(f"Expected EPSG:32718, found {crs}")
        xmin = math.floor(float(header.mins[0]))
        ymin = math.floor(float(header.mins[1]))
        xmax = math.ceil(float(header.maxs[0]))
        ymax = math.ceil(float(header.maxs[1]))
        width, height = xmax - xmin + 1, ymax - ymin + 1
        ncell = width * height
        dsm = np.full(ncell, -np.inf, dtype=np.float32)
        ground_idx, ground_z = [], []
        swaths = {g["number"]: [] for g in geoms}
        raw = {n: [] for n in REPRESENTATIVE}
        class_count = np.zeros(256, dtype=np.int64)
        total_read = 0

        for block in reader.chunk_iterator(chunk_size):
            x = np.asarray(block.x, dtype=np.float64)
            y = np.asarray(block.y, dtype=np.float64)
            z = np.asarray(block.z, dtype=np.float32)
            c = np.asarray(block.classification, dtype=np.uint8)
            total_read += len(x)
            class_count += np.bincount(c, minlength=256)
            col = np.floor(x - xmin).astype(np.int32)
            row = np.floor(y - ymin).astype(np.int32)
            np.clip(col, 0, width-1, out=col)
            np.clip(row, 0, height-1, out=row)
            flat = row.astype(np.int64)*width + col
            nonnoise = c != NOISE
            np.maximum.at(dsm, flat[nonnoise], z[nonnoise])
            isground = c == GROUND
            ground_idx.append(flat[isground].astype(np.int32))
            ground_z.append(z[isground])
            gx, gy, gz = x[isground], y[isground], z[isground]

            for geom in geoms:
                box = ((gx >= geom["xmin"]) & (gx <= geom["xmax"])
                       & (gy >= geom["ymin"]) & (gy <= geom["ymax"]))
                if box.any():
                    rx, ry = gx[box]-geom["x0"], gy[box]-geom["y0"]
                    along = rx*geom["ux"] + ry*geom["uy"]
                    across = np.abs(-rx*geom["uy"] + ry*geom["ux"])
                    good = ((along >= 0) & (along < LENGTH_M)
                            & (across <= MAX_SWATH_M))
                    if good.any():
                        swaths[geom["number"]].append(np.column_stack((
                            along[good], across[good], gz[box][good]
                        )).astype(np.float32))

                if geom["number"] not in raw:
                    continue
                # Raw 2 m corridor retains every non-noise LAS class.
                box = ((x >= geom["xmin"]) & (x <= geom["xmax"])
                       & (y >= geom["ymin"]) & (y <= geom["ymax"]))
                if not box.any():
                    continue
                rx, ry = x[box]-geom["x0"], y[box]-geom["y0"]
                along = rx*geom["ux"] + ry*geom["uy"]
                across = np.abs(-rx*geom["uy"] + ry*geom["ux"])
                good = ((along >= 0) & (along < LENGTH_M)
                        & (across <= 1.0) & (c[box] != NOISE))
                if good.any():
                    raw[geom["number"]].append(np.column_stack((
                        along[good], across[good], z[box][good], c[box][good]
                    )).astype(np.float32))
            print(f"Read {total_read:,}/{header.point_count:,} points", flush=True)

    if total_read != int(header.point_count):
        raise ValueError("LAZ point count differs from the header")
    idx = np.concatenate(ground_idx)
    gz = np.concatenate(ground_z)
    order = np.lexsort((gz, idx))
    sorted_idx, sorted_z = idx[order], gz[order]
    unique_idx, starts, counts = np.unique(sorted_idx, return_index=True, return_counts=True)
    lo = starts + (counts-1)//2
    hi = starts + counts//2
    median = (sorted_z[lo].astype(np.float64)+sorted_z[hi].astype(np.float64))/2
    dtm = np.full(ncell, np.nan, dtype=np.float32)
    dtm[unique_idx] = median.astype(np.float32)
    dsm[np.isneginf(dsm)] = np.nan
    swaths = {n: np.concatenate(parts) if parts else np.empty((0, 3), np.float32)
              for n, parts in swaths.items()}
    raw = {n: np.concatenate(parts) if parts else np.empty((0, 4), np.float32)
           for n, parts in raw.items()}
    return {
        "header": header, "xmin": xmin, "ymin": ymin, "width": width,
        "height": height, "dtm": dtm.reshape(height, width),
        "dsm": dsm.reshape(height, width), "class_count": class_count,
        "swaths": swaths, "raw": raw, "ground_cells": len(unique_idx),
    }


def write_raster(path, south_up, model, nodata=-9999.0):
    data = np.flipud(south_up).copy()
    data[~np.isfinite(data)] = nodata
    with rasterio.open(path, "w", driver="GTiff", height=model["height"],
                       width=model["width"], count=1, dtype="float32",
                       crs="EPSG:32718", nodata=nodata, compress="deflate",
                       transform=from_origin(model["xmin"],
                                             model["ymin"]+model["height"], 1, 1)) as dst:
        dst.write(data.astype(np.float32), 1)


def context_surface(array, max_distance=60):
    valid = np.isfinite(array)
    if not valid.any():
        raise ValueError("Surface has no data")
    distance = distance_transform_edt(~valid)
    # Rasterio's local inverse-distance fill avoids nearest-neighbour Voronoi
    # facets in the map. It remains a visualization surface, not measured DTM.
    filled = fillnodata(np.where(valid, array, 0).astype(np.float32),
                        mask=valid.astype(np.uint8),
                        max_search_distance=max_distance,
                        smoothing_iterations=2)
    smooth = gaussian_filter(filled, sigma=0.8)
    # Keep actual per-cell Ground medians without smoothing.
    smooth[valid] = array[valid]
    smooth[distance > max_distance] = np.nan
    return smooth


def sample_surface(surface, model, geom, step=0.5):
    s = np.arange(0, LENGTH_M+step/2, step)
    x = geom["x0"] + s*geom["ux"]
    y = geom["y0"] + s*geom["uy"]
    col = x-model["xmin"]-0.5
    row = y-model["ymin"]-0.5
    return s, map_coordinates(surface, [row, col], order=1, mode="nearest")


def ground_bins(points, halfwidth, step, minimum):
    centers = np.arange(step/2, LENGTH_M, step)
    med = np.full(len(centers), np.nan)
    q25 = med.copy(); q75 = med.copy()
    counts = np.zeros(len(centers), dtype=np.int32)
    subset = points[points[:, 1] <= halfwidth]
    if len(subset):
        index = np.floor(subset[:, 0] / step).astype(np.int32)
        for i in np.unique(index):
            vals = subset[index == i, 2]
            counts[i] = len(vals)
            if len(vals) >= minimum:
                med[i] = float(np.median(vals))
                q25[i], q75[i] = np.percentile(vals, (25, 75))
    return centers, counts, med, q25, q75


def max_gap(good, step):
    longest = current = 0
    for value in good:
        current = 0 if value else current+1
        longest = max(longest, current)
    return longest*step


def write_profiles(out, geoms, model, dtm_context, dsm_context):
    data = out / "datos"; data.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([{k: v for k, v in g.items() if k not in
                   ("xmin", "xmax", "ymin", "ymax")}
                  for g in geoms]).to_csv(data/"geometria_32_perfiles.csv", index=False)
    bin_rows, qc_rows, point_rows = [], [], []
    for g in geoms:
        n = g["number"]
        points = model["swaths"][n]
        for halfwidth in (2.5, 5.0, 7.5):
            centers, counts, med, q25, q75 = ground_bins(points, halfwidth, 1.0, 3)
            good = counts >= 3
            central = (centers >= 30) & (centers <= 100)
            search = (centers >= 30) & (centers <= 170)
            near_trace = (centers >= 40) & (centers <= 80)
            search_pct = 100*good[search].mean()
            search_gap = max_gap(good[search], 1.0)
            trace_pct = 100*good[near_trace].mean()
            if search_pct >= 80 and search_gap <= 10 and trace_pct >= 80:
                support_class = "A - high direct support"
            elif search_pct >= 60 and search_gap <= 20 and trace_pct >= 50:
                support_class = "B - moderate direct support"
            else:
                support_class = "C - insufficient direct support"
            qc_rows.append({
                "perfil": g["name"], "semiancho_faja_m": halfwidth,
                "n_ground_faja": int((points[:, 1] <= halfwidth).sum()),
                "bins_total": len(centers), "bins_validos_n_ge_3": int(good.sum()),
                "cobertura_total_pct": round(100*good.mean(), 3),
                "cobertura_30_100m_pct": round(100*good[central].mean(), 3),
                "hueco_max_total_m": max_gap(good, 1.0),
                "hueco_max_30_100m_m": max_gap(good[central], 1.0),
                "cobertura_30_170m_pct": round(search_pct, 3),
                "hueco_max_30_170m_m": search_gap,
                "cobertura_40_80m_pct": round(trace_pct, 3),
                "clase_soporte_directo": support_class,
            })
            for i, s in enumerate(centers):
                bin_rows.append((g["name"], halfwidth, s, counts[i],
                                 med[i], q25[i], q75[i]))
        if n in REPRESENTATIVE:
            for s, d, z, c in model["raw"][n]:
                point_rows.append((g["name"], float(s), float(d), float(z), int(c)))
    pd.DataFrame(bin_rows, columns=("perfil", "semiancho_faja_m", "distancia_m",
                                    "n_ground", "z_mediana_ground_m",
                                    "z_p25_ground_m", "z_p75_ground_m")).to_csv(
        data/"perfiles_ground_bins_1m.csv", index=False)
    pd.DataFrame(qc_rows).to_csv(data/"control_soporte_32_perfiles.csv", index=False)
    pd.DataFrame(point_rows, columns=("perfil", "distancia_m", "distancia_transversal_m",
                                      "z_m", "clase_las")).to_csv(
        data/"puntos_5_perfiles_representativos.csv", index=False)
    grid_rows = []
    for g in geoms:
        if g["number"] not in REPRESENTATIVE:
            continue
        s, z_dtm = sample_surface(dtm_context, model, g)
        _, z_dsm = sample_surface(dsm_context, model, g)
        for a, b, c in zip(s, z_dtm, z_dsm):
            grid_rows.append((g["name"], a, b, c))
    pd.DataFrame(grid_rows, columns=("perfil", "distancia_m", "dtm_contexto_m",
                                     "dsm_todas_clases_sin_ruido_m")).to_csv(
        data/"perfiles_raster_contexto_0p5m.csv", index=False)
    return pd.DataFrame(qc_rows)


def plot_profiles(out, geoms, model, dtm_context, dsm_context):
    figdir = out/"figuras"; figdir.mkdir(parents=True, exist_ok=True)
    # Metric 1:1 panel shape: 50 m elevation spans 50/180 of 180 m distance.
    fig, axes = plt.subplots(5, 1, figsize=(5.75, 9.5), sharex=True)
    fig.subplots_adjust(left=0.16, right=0.98, top=0.98, bottom=0.17, hspace=0.24)
    panels = "bcdef"
    for ax, n, letter in zip(axes, REPRESENTATIVE, panels):
        geom = geoms[n-1]
        raw = model["raw"][n]
        noground = raw[raw[:, 3] != GROUND]
        graw = raw[raw[:, 3] == GROUND]
        for points, color, alpha, size in ((noground, "#bdbdbd", 0.40, 2.0),
                                           (graw, "#1f5eb5", 0.72, 2.4)):
            if len(points):
                stride = max(1, len(points)//6000)
                ax.scatter(points[::stride, 0], points[::stride, 2], s=size,
                           c=color, alpha=alpha, rasterized=True, linewidths=0, zorder=1)
        x, _, med, _, _ = ground_bins(model["swaths"][n], 1.0, 0.5, 1)
        sample_x, dtm = sample_surface(dtm_context, model, geom)
        _, dsm = sample_surface(dsm_context, model, geom)
        ax.plot(sample_x, dtm, color="#666666", linestyle=(0, (3, 2)), lw=1.0, zorder=2)
        ax.plot(x, med, color="black", lw=1.45, zorder=3)
        ax.plot(sample_x, dsm, color="#ea8500", linestyle=(0, (5, 2)), lw=1.15, zorder=4)
        ax.axvline(TRACE_M, color="#d62728", linestyle=":", lw=1.0)
        ax.text(0.02, 0.90, f"({letter}) {geom['name']}", ha="left", va="top",
                transform=ax.transAxes, fontsize=9.5, fontweight="bold")
        ax.set(xlim=(0, 180), ylim=(595, 645), yticks=(595,605,615,625,635,645))
        ax.set_box_aspect(50/180)
        ax.tick_params(labelsize=7.7, pad=1.5, length=2.5)
        ax.grid(False)
    axes[2].set_ylabel("Elevation (m)", fontsize=9)
    axes[-1].set_xlabel("Distance along profile (m; W → E)", fontsize=9)
    axes[-1].set_xticks((0,45,90,135,180))
    handles = [
        Line2D([], [], marker="o", ls="", color="#bdbdbd", markersize=4.8,
               label="Non-ground points"),
        Line2D([], [], marker="o", ls="", color="#1f5eb5", markersize=4.8,
               label="Ground points"),
        Line2D([], [], color="#ea8500", ls=(0,(5,2)), label="DSM (all non-noise)"),
        Line2D([], [], color="black", lw=1.4, label="DTM (direct Ground support)"),
        Line2D([], [], color="#666666", ls=(0,(3,2)), label="DTM (interpolated context)"),
        Line2D([], [], color="#d62728", ls=":", label="Mapped lineament position"),
    ]
    legend = fig.legend(handles=handles, ncol=2, loc="lower center",
                        bbox_to_anchor=(0.5, 0.015), frameon=True,
                        title="Legend", title_fontsize=9, fontsize=7.5,
                        handlelength=2.2, columnspacing=1.5)
    legend.get_frame().set_linewidth(0.6)
    fig.savefig(figdir/"Figura_2b_perfiles_1x_NUBE_FINAL.pdf", bbox_inches="tight")
    fig.savefig(figdir/"Figura_2b_perfiles_1x_NUBE_FINAL.png", dpi=450,
                bbox_inches="tight")
    plt.close(fig)


def plot_map(out, geoms, model, dtm_context):
    figdir = out/"figuras"; figdir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.0, 8.4))
    fig.subplots_adjust(left=0.12, right=0.86, top=0.96, bottom=0.08)
    north_up = np.flipud(dtm_context)
    extent = (model["xmin"], model["xmin"]+model["width"],
              model["ymin"], model["ymin"]+model["height"])
    norm = Normalize(vmin=595, vmax=633)
    cmap = plt.get_cmap("viridis").copy()
    cmap.set_bad("white")
    relief = LightSource(azdeg=315, altdeg=45).hillshade(
        np.nan_to_num(north_up, nan=np.nanmedian(north_up)), vert_exag=1,
        dx=1, dy=1)
    colored = cmap(norm(np.ma.masked_invalid(north_up)))
    colored[..., :3] = 0.76*colored[..., :3] + 0.24*relief[..., None]
    colored[..., 3] = np.isfinite(north_up)
    ax.imshow(colored, extent=extent, interpolation="nearest")
    for g in geoms:
        ax.plot([g["x0"], g["x1"]], [g["y0"], g["y1"]], color="white",
                lw=0.9, path_effects=[], zorder=2)
        if g["number"] in REPRESENTATIVE:
            ax.text(g["x0"]+4, g["y0"]+3, g["name"], color="black", fontsize=8,
                    bbox=dict(facecolor="white", edgecolor="none", alpha=.9, pad=1),
                    zorder=4)
    trace = sorted(geoms, key=lambda g: g["trace_y"])
    ax.plot([g["trace_x"] for g in trace], [g["trace_y"] for g in trace],
            color="#d62728", lw=2.0, label="Local mapped lineament", zorder=3)
    ax.set_xlabel("Easting (m, EPSG:32718)", fontsize=9)
    ax.set_ylabel("Northing (m, EPSG:32718)", fontsize=9)
    ax.ticklabel_format(style="plain", useOffset=False)
    ax.tick_params(labelsize=7.5)
    ax.set_aspect("equal")
    ax.legend(loc="upper right", fontsize=8, framealpha=.9)
    fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax,
                 pad=.02, shrink=.75, label="Elevation (m)")
    fig.savefig(figdir/"Figura_2a_MDT_traza_32_perfiles_NUBE_FINAL.pdf", bbox_inches="tight")
    fig.savefig(figdir/"Figura_2a_MDT_traza_32_perfiles_NUBE_FINAL.png", dpi=450,
                bbox_inches="tight")
    plt.close(fig)


def plot_all_qc(out, model):
    figdir = out/"figuras"; figdir.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(8, 4, figsize=(14, 16), sharex=True, sharey=True)
    fig.subplots_adjust(left=.07, right=.98, bottom=.055, top=.97, hspace=.3, wspace=.14)
    for n, ax in enumerate(axes.flat, 1):
        points = model["swaths"][n]
        x, counts, med, q25, q75 = ground_bins(points, 5, 1, 3)
        ax.fill_between(x, q25, q75, where=np.isfinite(med), color="#a6bddb", alpha=.55)
        ax.plot(x, med, color="#0b3d79", lw=1.15)
        ax.axvline(TRACE_M, color="#d62728", ls=":", lw=.9)
        ax.text(.03, .88, f"P{n}  {np.mean(counts>=3)*100:.0f}%",
                transform=ax.transAxes, fontsize=8, ha="left", va="top")
        ax.set(xlim=(0,180), ylim=(592,645))
        ax.tick_params(labelsize=6.5)
    fig.supxlabel("Distance along profile (m; W → E)", fontsize=10)
    fig.supylabel("Direct Ground elevation (m)", fontsize=10)
    fig.savefig(figdir/"Figura_S1_32_perfiles_soporte_ground.pdf", bbox_inches="tight")
    fig.savefig(figdir/"Figura_S1_32_perfiles_soporte_ground.png", dpi=350,
                bbox_inches="tight")
    plt.close(fig)


def main():
    args = arguments()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    geoms = geometries(args.geometry_csv)
    model = extract_cloud(args.laz, geoms, args.chunk)
    if int(model["class_count"].sum()) != model["header"].point_count:
        raise ValueError("Class counts do not match LAZ header")
    rasters = out/"rasters"; rasters.mkdir(exist_ok=True)
    dtm_context = context_surface(model["dtm"])
    dsm_context = context_surface(model["dsm"])
    write_raster(rasters/"MDT_ground_observado_1m.tif", model["dtm"], model)
    write_raster(rasters/"MDT_contexto_interpolado_1m.tif", dtm_context, model)
    write_raster(rasters/"MDS_todas_clases_sin_ruido_1m.tif", model["dsm"], model)
    qc = write_profiles(out, geoms, model, dtm_context, dsm_context)
    plot_profiles(out, geoms, model, dtm_context, dsm_context)
    plot_map(out, geoms, model, dtm_context)
    plot_all_qc(out, model)
    manifest = {
        "source_laz": str(args.laz.resolve()),
        "source_sha256": sha256(args.laz),
        "source_bytes": args.laz.stat().st_size,
        "header_points": int(model["header"].point_count),
        "ground_points": int(model["class_count"][GROUND]),
        "class_counts": {str(i): int(v) for i,v in enumerate(model["class_count"]) if v},
        "crs": "EPSG:32718", "cell_m": 1.0,
        "geometry_csv": str(args.geometry_csv.resolve()),
        "geometry_sha256": sha256(args.geometry_csv),
        "ground_cells_1m": model["ground_cells"],
        "profile_swath_halfwidths_m": [2.5,5.0,7.5],
        "valid_swath_bin": "At least three Ground points in a 1 m bin; no gap filling",
        "figure_profile_aspect": "1:1 physical metric axis scaling (180 m x 50 m)",
        "representative_profiles": [f"P{n}" for n in REPRESENTATIVE],
        "caveat": "Context rasters are interpolated visualization aids, not direct observations.",
    }
    (out/"MANIFIESTO_NUBE_FINAL.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(qc[qc.semiancho_faja_m == 5.0].to_string(index=False))
    print(f"Completed: {out}")


if __name__ == "__main__":
    main()
