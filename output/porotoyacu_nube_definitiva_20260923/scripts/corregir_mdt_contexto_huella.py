"""Repair the visualization-only DTM using the definitive 1 m rasters.

The original observed Ground raster is never changed. The all-class raster is
used only to delimit the surveyed footprint; its elevations are not used to
estimate terrain. A distance-to-Ground raster accompanies the filled context.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image


QGIS_SITE = Path(r"C:\Program Files\QGIS 3.34.15\apps\Python312\Lib\site-packages")
GDAL_TRANSLATE = Path(r"C:\Program Files\QGIS 3.34.15\bin\gdal_translate.exe")
sys.path.append(str(QGIS_SITE))

from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator  # noqa: E402
from scipy.ndimage import distance_transform_edt, gaussian_filter  # noqa: E402


def write_geotiff(data: np.ndarray, template: Image.Image, dest: Path) -> None:
    pixel_width, pixel_height, _ = template.tag_v2[33550]
    _, _, _, xmin, ymax, _ = template.tag_v2[33922]
    xmax = xmin + data.shape[1] * pixel_width
    ymin = ymax - data.shape[0] * pixel_height
    with tempfile.TemporaryDirectory(prefix="porotoyacu_mdt_") as tmp:
        plain = Path(tmp) / "surface.tif"
        Image.fromarray(data.astype(np.float32), mode="F").save(plain)
        subprocess.run(
            [
                str(GDAL_TRANSLATE), "-of", "GTiff",
                "-co", "COMPRESS=DEFLATE", "-co", "PREDICTOR=3",
                "-co", "TILED=YES", "-a_srs", "EPSG:32718",
                "-a_ullr", str(xmin), str(ymax), str(xmax), str(ymin),
                "-a_nodata", "-9999", str(plain), str(dest),
            ],
            check=True,
        )


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    rasters = root / "rasters"
    ground_file = rasters / "MDT_ground_observado_1m.tif"
    all_file = rasters / "MDS_todas_clases_sin_ruido_1m.tif"
    with Image.open(ground_file) as src:
        ground = np.asarray(src).copy()
        geotags = src.copy()
        geotags.tag_v2 = src.tag_v2
    with Image.open(all_file) as src:
        all_classes = np.asarray(src)

    ground_valid = ground > -9000
    all_valid = all_classes > -9000
    if ground.shape != all_classes.shape or not np.all(all_valid[ground_valid]):
        raise ValueError("Ground and all-class raster footprints are inconsistent")

    # The 10 m buffer joins sparse all-class cells without filling unlimited
    # territory beyond actual cloud coverage. This includes the northern notch.
    footprint_distance = distance_transform_edt(~all_valid)
    footprint = footprint_distance <= 10.0
    ground_distance = distance_transform_edt(~ground_valid)

    rows, cols = np.indices(ground.shape)
    known_xy = np.column_stack((cols[ground_valid], rows[ground_valid]))
    known_z = ground[ground_valid].astype(np.float64)
    target_xy = np.column_stack((cols[footprint], rows[footprint]))
    linear = LinearNDInterpolator(known_xy, known_z, fill_value=np.nan)
    estimate = linear(target_xy)
    outside_hull = ~np.isfinite(estimate)
    if outside_hull.any():
        nearest = NearestNDInterpolator(known_xy, known_z)
        estimate[outside_hull] = nearest(target_xy[outside_hull])

    context = np.zeros(ground.shape, dtype=np.float32)
    context[footprint] = estimate.astype(np.float32)
    # Smooth only the contextual estimate. Restore all direct observations.
    weights = gaussian_filter(footprint.astype(np.float32), sigma=1.0)
    smoothed = gaussian_filter(context, sigma=1.0) / np.maximum(weights, 1e-6)
    context[footprint] = smoothed[footprint]
    context[ground_valid] = ground[ground_valid]
    context[~footprint] = -9999.0

    distance = np.full(ground.shape, -9999.0, dtype=np.float32)
    distance[footprint] = ground_distance[footprint].astype(np.float32)

    assert np.array_equal(context[ground_valid], ground[ground_valid])
    assert np.isfinite(context[footprint]).all()
    assert context[footprint].min() >= known_z.min() - 0.01
    assert context[footprint].max() <= known_z.max() + 0.01
    assert np.all(context[all_valid] > -9000)

    context_file = rasters / "MDT_contexto_continuo_huella_1m.tif"
    distance_file = rasters / "DISTANCIA_al_Ground_observado_1m.tif"
    write_geotiff(context, geotags, context_file)
    write_geotiff(distance, geotags, distance_file)
    shade = np.clip((context - 594.0) / 40.0, 0.0, 1.0)
    gray = (35 + shade * 190).astype(np.uint8)
    preview = np.repeat(gray[:, :, None], 3, axis=2)
    preview[~footprint] = 255
    Image.fromarray(preview, mode="RGB").save(rasters / "QA_vista_MDT_contexto_continuo_huella.png")

    stats = {
        "source_ground_raster": ground_file.name,
        "footprint_reference": all_file.name,
        "cell_size_m": 1,
        "all_class_footprint_buffer_m": 10,
        "method": "2D linear interpolation of observed Ground medians; nearest Ground outside their convex hull; Gaussian sigma 1 m only on estimates; direct Ground cells restored unchanged",
        "ground_observed_cells": int(ground_valid.sum()),
        "all_class_observed_cells": int(all_valid.sum()),
        "context_footprint_cells": int(footprint.sum()),
        "context_cells_over_60m_from_ground": int((footprint & (ground_distance > 60)).sum()),
        "context_cells_over_100m_from_ground": int((footprint & (ground_distance > 100)).sum()),
        "nearest_extrapolated_cells_outside_ground_convex_hull": int(outside_hull.sum()),
        "minimum_context_m": float(context[footprint].min()),
        "maximum_context_m": float(context[footprint].max()),
        "direct_ground_preserved_exactly": True,
        "limitation": "Visualization only. Interpolated/extrapolated cells are not measured terrain or valid for scarp-height estimates.",
    }
    (rasters / "QA_MDT_contexto_continuo_huella.json").write_text(
        json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
