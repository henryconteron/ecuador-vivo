"""Replot Figure 2b from saved final-cloud profile data and the Agisoft DEM.

Raw observations and the 1 m DSM remain unchanged. Only the gray contextual
terrain curve is resampled from the exported 0.196717 m Metashape DEM.
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from scipy.ndimage import map_coordinates

os.add_dll_directory(r"C:\Program Files\QGIS 3.34.15\bin")
from osgeo import gdal


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datos"
FIGS = ROOT / "figuras"
DEM = Path(
    r"C:\Users\JHONY CONTERON\Downloads\Perimetral 1-20260831T211605Z-1-001"
    r"\ENTREGA_Q2_NUBE_DEFINITIVA_20260923\rasters"
    r"\MDT_contexto_Extrapolado_19.7cmpix.tif"
)
ORDER = (32, 21, 18, 11, 4)
MAX_DISTANCE = 180.0


def profile_medians(raw: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    step = 0.5
    centers = np.arange(step / 2, MAX_DISTANCE, step)
    values = np.full(centers.size, np.nan)
    ground = raw.loc[raw.clase_las.eq(2)]
    idx = np.floor(ground.distancia_m.to_numpy() / step).astype(int)
    z = ground.z_m.to_numpy()
    for i in np.unique(idx):
        if 0 <= i < len(values):
            values[i] = np.median(z[idx == i])
    return centers, values


def sample_dem(dem: np.ndarray, transform, geom: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    distance = np.arange(0, MAX_DISTANCE + 0.25, 0.5)
    x = geom.x0 + distance * geom.ux
    y = geom.y0 + distance * geom.uy
    col = (x - transform[0]) / transform[1] - 0.5
    row = (y - transform[3]) / transform[5] - 0.5
    z = map_coordinates(dem, [row, col], order=1, mode="constant", cval=np.nan)
    return distance, z


def main() -> None:
    points = pd.read_csv(DATA / "puntos_5_perfiles_representativos.csv")
    context = pd.read_csv(DATA / "perfiles_raster_contexto_0p5m.csv")
    geometry = pd.read_csv(DATA / "geometria_32_perfiles.csv").set_index("number")

    raster = gdal.Open(str(DEM))
    if raster is None or raster.RasterCount != 1:
        raise ValueError("Cannot read the Agisoft DEM")
    transform = raster.GetGeoTransform()
    if not np.isclose(abs(transform[1]), 0.196717, atol=1e-6):
        raise ValueError(f"Unexpected pixel size: {transform[1]}")
    dem = raster.ReadAsArray().astype(np.float32)
    dem[dem == raster.GetRasterBand(1).GetNoDataValue()] = np.nan

    # Modest 6% horizontal reduction; original y limits and panel height stay.
    fig, axes = plt.subplots(5, 1, figsize=(5.40, 9.50), sharex=True)
    fig.subplots_adjust(left=0.17, right=0.985, top=0.985, bottom=0.17, hspace=0.25)
    panels = "bcdef"
    rows = []
    for ax, number, letter in zip(axes, ORDER, panels):
        label = f"P{number}"
        raw = points.loc[points.perfil.eq(label)]
        grid = context.loc[context.perfil.eq(label)].sort_values("distancia_m")
        geom = geometry.loc[number]
        x_dem, z_dem = sample_dem(dem, transform, geom)
        x_direct, z_direct = profile_medians(raw)

        # Observations and DSM stay behind the two terrain interpretations.
        other = raw.loc[raw.clase_las.ne(2)]
        ground = raw.loc[raw.clase_las.eq(2)]
        for selected, color, opacity, size, level in (
            (other, "#bdbdbd", 0.28, 1.8, 1),
            (ground, "#1f5eb5", 0.72, 2.3, 3),
        ):
            stride = max(1, len(selected) // 6000)
            ax.scatter(selected.distancia_m.to_numpy()[::stride],
                       selected.z_m.to_numpy()[::stride], s=size, c=color,
                       alpha=opacity, rasterized=True, linewidths=0, zorder=level)
        ax.plot(grid.distancia_m, grid.dsm_todas_clases_sin_ruido_m,
                color="#d98a24", linestyle=(0, (5, 2)), lw=1.0,
                alpha=0.72, zorder=2)
        ax.plot(x_dem, z_dem, color="#595959", linestyle=(0, (3, 2)),
                lw=1.25, zorder=4)
        ax.plot(x_direct, z_direct, color="black", lw=1.65, zorder=5)
        ax.axvline(60, color="#d62728", linestyle=":", lw=1.0, zorder=0)
        ax.text(0.02, 0.90, f"({letter}) {label}", ha="left", va="top",
                transform=ax.transAxes, fontsize=9.5, fontweight="bold")
        ax.set(xlim=(0, 180), ylim=(595, 645), yticks=(595, 605, 615, 625, 635, 645))
        ax.tick_params(labelsize=7.7, pad=1.5, length=2.5)
        ax.grid(False)

        rows.extend((label, float(x), float(z)) for x, z in zip(x_dem, z_dem))

    axes[2].set_ylabel("Elevation (m)", fontsize=9)
    axes[-1].set_xlabel("Distance along profile (m; W → E)", fontsize=9)
    axes[-1].set_xticks((0, 45, 90, 135, 180))

    # Matplotlib fills two-column legends down columns: first row is terrain.
    handles = [
        Line2D([], [], color="black", lw=1.65, label="DTM (direct Ground support)"),
        Line2D([], [], marker="o", ls="", color="#1f5eb5", markersize=4.7,
               label="Ground points"),
        Line2D([], [], color="#d98a24", ls=(0, (5, 2)), lw=1.0,
               label="DSM (all non-noise)"),
        Line2D([], [], color="#595959", ls=(0, (3, 2)), lw=1.25,
               label="DTM (interpolated/extrapolated)"),
        Line2D([], [], marker="o", ls="", color="#bdbdbd", markersize=4.7,
               label="Non-ground points"),
        Line2D([], [], color="#d62728", ls=":", label="Mapped lineament position"),
    ]
    legend = fig.legend(handles=handles, ncol=2, loc="lower center",
                        bbox_to_anchor=(0.5, 0.012), frameon=True,
                        title="Legend", title_fontsize=9, fontsize=7.2,
                        handlelength=2.2, columnspacing=1.2)
    legend.get_frame().set_linewidth(0.6)

    FIGS.mkdir(parents=True, exist_ok=True)
    name = "Figura_2b_perfiles_0197m_terreno_prioritario"
    fig.savefig(FIGS / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIGS / f"{name}.png", dpi=450, bbox_inches="tight")
    pd.DataFrame(rows, columns=("perfil", "distancia_m", "dtm_agisoft_m")).to_csv(
        DATA / "perfiles_mdt_agisoft_0197m_muestreo_0p5m.csv", index=False
    )
    print(FIGS / f"{name}.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
