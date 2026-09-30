"""Figure 2b sized for a 100 mm-wide column in the QGIS composition.

All observations and elevations are unchanged. The compact legend uses short
labels that must be expanded in the manuscript caption.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
matplotlib.rcParams["path.simplify"] = False
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

os.add_dll_directory(r"C:\Program Files\QGIS 3.34.15\bin")
from osgeo import gdal

from replot_perfiles_2b_agisoft import DEM, profile_medians, sample_dem


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datos"
FIGS = ROOT / "figuras"
ORDER = (32, 21, 18, 11, 4)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--journal-full-width", action="store_true")
    args = parser.parse_args()
    points = pd.read_csv(DATA / "puntos_5_perfiles_representativos.csv")
    context = pd.read_csv(DATA / "perfiles_raster_contexto_0p5m.csv")
    geometry = pd.read_csv(DATA / "geometria_32_perfiles.csv").set_index("number")
    dataset = gdal.Open(str(DEM))
    transform = dataset.GetGeoTransform()
    dem = dataset.ReadAsArray().astype(np.float32)
    dem[dem == dataset.GetRasterBand(1).GetNoDataValue()] = np.nan

    # 100 mm is for the current right column. The full-width alternative is
    # journal-page scale and avoids reducing the five panels beside the map.
    if args.journal_full_width:
        fig, axes = plt.subplots(5, 1, figsize=(6.89, 9.84), sharex=True)
        fig.subplots_adjust(left=0.12, right=0.98, top=0.988, bottom=0.12,
                            hspace=0.18)
    else:
        fig, axes = plt.subplots(5, 1, figsize=(3.94, 7.50), sharex=True)
        fig.subplots_adjust(left=0.18, right=0.955, top=0.988, bottom=0.175,
                            hspace=0.20)
    for ax, number, letter in zip(axes, ORDER, "bcdef"):
        name = f"P{number}"
        raw = points.loc[points.perfil.eq(name)]
        grid = context.loc[context.perfil.eq(name)].sort_values("distancia_m")
        x_fill, z_fill = sample_dem(dem, transform, geometry.loc[number])
        x_direct, z_direct = profile_medians(raw)
        other = raw.loc[raw.clase_las.ne(2)]
        ground = raw.loc[raw.clase_las.eq(2)]

        for group, color, opacity, size, zorder in (
            (other, "#bdbdbd", 0.20, 1.5, 1),
            (ground, "#1f5eb5", 0.78, 2.2, 3),
        ):
            stride = max(1, len(group) // 6000)
            ax.scatter(group.distancia_m.to_numpy()[::stride],
                       group.z_m.to_numpy()[::stride], s=size, c=color,
                       alpha=opacity, rasterized=False, linewidths=0,
                       zorder=zorder)

        ax.plot(grid.distancia_m, grid.dsm_todas_clases_sin_ruido_m,
                color="#d98a24", linestyle=(0, (5, 2)), lw=1.05,
                alpha=0.62, zorder=2)
        ax.plot(x_fill, z_fill, color="#545454", linestyle=(0, (3, 2)),
                lw=1.35, zorder=4)
        ax.plot(x_direct, z_direct, color="black", lw=1.75, zorder=5)
        ax.axvline(60, color="#d62728", linestyle=":", lw=1.0, zorder=0)
        ax.text(0.02, 0.92, f"({letter}) {name}", transform=ax.transAxes,
                ha="left", va="top", fontsize=10.0, fontweight="bold")
        ax.set_xlim(0, 180)
        ax.set_ylim(595, 645)
        ax.set_yticks((595, 605, 615, 625, 635, 645))
        ax.tick_params(axis="both", which="major", labelsize=9.0,
                       pad=1.5, length=2.5)
        ax.grid(False)

    axes[2].set_ylabel("Elevation (m)", fontsize=9.4)
    axes[-1].set_xticks((0, 60, 120, 180))
    axes[-1].set_xlabel("Distance (m; W → E)", fontsize=9.4, labelpad=3)
    handles = [
        Line2D([], [], color="black", lw=1.75, label="Ground DTM"),
        Line2D([], [], marker="o", ls="", color="#1f5eb5", markersize=4.3,
               label="Ground points"),
        Line2D([], [], color="#d98a24", ls=(0, (5, 2)), lw=1.05,
               label="DSM"),
        Line2D([], [], color="#545454", ls=(0, (3, 2)), lw=1.35,
               label="Filled DTM"),
        Line2D([], [], marker="o", ls="", color="#bdbdbd", markersize=4.3,
               label="Other points"),
        Line2D([], [], color="#d62728", ls=":", label="Lineament"),
    ]
    legend = fig.legend(handles=handles, ncol=2, loc="lower center",
                        bbox_to_anchor=(0.5, 0.020 if args.journal_full_width else 0.030), frameon=False,
                        fontsize=8.7, handlelength=2.2,
                        columnspacing=1.2, handletextpad=0.5)
    legend.get_frame().set_linewidth(0)

    FIGS.mkdir(parents=True, exist_ok=True)
    stem = ("Figura_perfiles_ancho_revista_175mm" if args.journal_full_width
            else "Figura_2b_perfiles_columna_100mm")
    fig.savefig(FIGS / f"{stem}.pdf", dpi=900)
    fig.savefig(FIGS / f"{stem}.png", dpi=900)
    plt.close(fig)
    print(FIGS / f"{stem}.pdf")


if __name__ == "__main__":
    main()
