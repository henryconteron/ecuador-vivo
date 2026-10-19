"""Read tiny native SCL windows; report parcel support, never land-use change."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import urlencode, urlparse
from urllib.request import urlopen

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom
from rasterio.windows import Window, from_bounds
from shapely.geometry import shape

from tools.parcelas.catalog import validate_parcel


def summarize_scl(values, inside, observed):
    total = int(inside.sum())
    if not total:
        return {"pixel_centres_in_parcel": 0, "clear_fraction": None,
                "status": "insufficient_spatial_support"}
    valid = inside & observed & (values != 0)
    classes = {str(code): int(((values == code) & valid).sum()) for code in range(1, 12)}
    clear = sum(classes[str(code)] for code in (4, 5, 6))
    return {"pixel_centres_in_parcel": total, "scl_counts": classes,
            "missing_fraction": float((inside & ~valid).sum()) / total,
            "clear_fraction": clear / total, "status": "quality_only_not_landcover",
            "clear_classes": [4, 5, 6],
            "warning": "Pixel-centre fractions at native SCL resolution, not exact area fractions or proof of cocoa/forest."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parcel", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    document = json.loads(args.parcel.read_text(encoding="utf-8"))
    parcel = validate_parcel(document)
    if args.output.exists():
        raise ValueError("Choose a new output directory")
    # Deliberately scoped to the approved reference date, two scenes only.
    url = "https://earth-search.aws.element84.com/v1/search?" + urlencode({
        "collections": "sentinel-2-l2a", "bbox": ",".join(map(str, parcel["bbox"])),
        "datetime": "2025-03-01T00:00:00Z/2025-03-31T23:59:59Z", "limit": 20})
    with urlopen(url, timeout=30) as response:
        raw = response.read(4_000_001)
    if len(raw) > 4_000_000:
        raise ValueError("Metadata size limit exceeded")
    page = json.loads(raw)
    items = sorted(page["features"], key=lambda item: item["properties"].get("eo:cloud_cover", 100))[:2]
    if not items:
        raise ValueError("No optical candidates in reference period")
    args.output.mkdir(parents=True)
    reports = []
    for item in items:
        href = item["assets"]["scl"]["href"]
        if urlparse(href).hostname != "sentinel-cogs.s3.us-west-2.amazonaws.com" or not href.startswith("https://"):
            raise ValueError("Unexpected public SCL asset host")
        with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", GDAL_HTTP_TIMEOUT="30",
                          GDAL_HTTP_MAX_RETRY="1", VSI_CACHE=False, GDAL_CACHEMAX=32_000_000):
            with rasterio.open(href) as source:
                geometry = transform_geom("EPSG:4326", source.crs, document["features"][0]["geometry"])
                bounds = shape(geometry).bounds
                window = from_bounds(*bounds, source.transform)
                col, row = int(np.floor(window.col_off)), int(np.floor(window.row_off))
                right, bottom = int(np.ceil(window.col_off + window.width)), int(np.ceil(window.row_off + window.height))
                window = Window(col, row, right - col, bottom - row).intersection(Window(0, 0, source.width, source.height))
                if window.width * window.height > 100_000:
                    raise ValueError("SCL window exceeds pilot limit")
                values = source.read(1, window=window, masked=True)
                transform = source.window_transform(window)
                inside = geometry_mask([geometry], values.shape, transform, invert=True, all_touched=False)
                report = summarize_scl(values.data, inside, ~np.ma.getmaskarray(values))
                report.update({"item_id": item["id"], "date": item["properties"]["datetime"],
                               "scene_cloud_percent": item["properties"].get("eo:cloud_cover"),
                               "source_asset": href, "crs": source.crs.to_string(),
                               "native_pixel_size": list(source.res), "transform": list(transform)[:6],
                               "window_shape": list(values.shape)})
                filename = f"scene-{len(reports) + 1}-scl.tif"
                with rasterio.open(args.output / filename, "w", driver="GTiff", height=values.shape[0],
                                   width=values.shape[1], count=1, dtype="uint8", crs=source.crs,
                                   transform=transform, nodata=0, compress="deflate") as target:
                    target.write(np.where(inside & ~np.ma.getmaskarray(values), values.data, 0).astype("uint8"), 1)
                report["local_raster"] = filename
        reports.append(report)
        print(item["id"], report["clear_fraction"], flush=True)
    result = {"created_at": datetime.now(timezone.utc).isoformat(), "reports": reports,
              "selection": "two lowest scene-cloud candidates from first page, not best parcel observations",
              "catalog_has_more": any(link.get("rel") == "next" for link in page.get("links", [])),
              "scientific_status": "quality_diagnostic_only_no_deforestation_assessment"}
    (args.output / "optical-quality.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (args.output / "source-items.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": items}), encoding="utf-8")


if __name__ == "__main__":
    main()
