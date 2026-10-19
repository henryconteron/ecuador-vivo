"""Bounded public STAC discovery. No pixel downloads or compliance decisions."""
import argparse
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from pyproj import Geod
from shapely.geometry import shape
from shapely.geometry.polygon import orient

CATALOG = "https://stac.dataspace.copernicus.eu/v1"
COLLECTIONS = ("sentinel-1-grd", "sentinel-2-l2a")


def validate_parcel(document):
    if document.get("type") != "FeatureCollection" or len(document.get("features", [])) != 1:
        raise ValueError("Provide exactly one GeoJSON feature")
    crs = document.get("crs", {}).get("properties", {}).get("name")
    if crs and crs not in ("EPSG:4326", "urn:ogc:def:crs:OGC:1.3:CRS84"):
        raise ValueError("Coordinates must be WGS84 longitude/latitude")
    geometry = document["features"][0].get("geometry", {})
    if geometry.get("type") not in ("Polygon", "MultiPolygon"):
        raise ValueError("A point is not a parcel perimeter")
    polygons = [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
    for polygon in polygons:
        for ring in polygon:
            if len(ring) < 4 or ring[0] != ring[-1]:
                raise ValueError("Polygon rings must be closed")
    geom = shape(geometry)
    if geom.is_empty or not geom.is_valid or geom.has_z:
        raise ValueError("Invalid or non-2D polygon")
    west, south, east, north = geom.bounds
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90) or east - west > 1 or north - south > 1:
        raise ValueError("Invalid coordinates or extent exceeds pilot limit")
    parts = [geom] if geom.geom_type == "Polygon" else geom.geoms
    geod = Geod(ellps="WGS84")
    area = sum(abs(geod.geometry_area_perimeter(orient(part))[0]) for part in parts) / 10000
    if not 0 < area <= 100:
        raise ValueError("Pilot accepts at most 100 hectares")
    return {"bbox": list(geom.bounds), "area_ha": area}


def build_search_url(collection, bbox, start, end):
    if collection not in COLLECTIONS or not 0 < (date.fromisoformat(end) - date.fromisoformat(start)).days <= 366:
        raise ValueError("Invalid collection or interval; maximum 366 days, exclusive end")
    return CATALOG + "/search?" + urlencode({"collections": collection,
        "bbox": ",".join(map(str, bbox)), "datetime": f"{start}T00:00:00Z/{end}T00:00:00Z", "limit": 100})


def discover(collection, bbox, start, end, max_pages=5):
    url = build_search_url(collection, bbox, start, end)
    items, complete, visited = [], False, set()
    for _ in range(max_pages):
        if url in visited or not url.startswith(CATALOG + "/"):
            raise ValueError("Unsafe or repeated catalog pagination URL")
        visited.add(url)
        with urlopen(Request(url, headers={"User-Agent": "EcuadorVivo-parcel-pilot/0.1"}), timeout=45) as response:
            payload = response.read(12_000_001)
        if len(payload) > 12_000_000:
            raise ValueError("Catalog response exceeds 12 MB limit")
        page = json.loads(payload)
        if page.get("type") != "FeatureCollection":
            raise ValueError("Unexpected catalog response")
        # STAC interval endpoint may include midnight of the following day.
        items.extend(item for item in page["features"]
                     if start <= item["properties"]["datetime"][:10] < end)
        links = [link for link in page.get("links", []) if link.get("rel") == "next"]
        if not links:
            complete = True
            break
        if len(links) != 1 or links[0].get("method", "GET") != "GET":
            raise ValueError("Unsupported pagination contract; refusing incomplete silent result")
        url = links[0]["href"]
    return items, complete


def summarize_items(items):
    rows, groups, rejected, seen = [], {}, [], set()
    for item in items:
        key = (item.get("collection"), item["id"])
        if key in seen:
            continue
        seen.add(key)
        p = item.get("properties", {})
        row = {"id": item["id"], "collection": item.get("collection"),
               "datetime": p.get("datetime"), "scene_cloud_percent": p.get("eo:cloud_cover"),
               "platform": p.get("platform"), "mode": p.get("sar:instrument_mode"),
               "orbit_direction": p.get("sat:orbit_state"), "relative_orbit": p.get("sat:relative_orbit"),
               "polarizations": sorted(p.get("sar:polarizations", [])),
               "product_type": p.get("product:type"),
               "processing_level": p.get("processing:level"),
               "processing_version": p.get("processing:version"),
               "incidence_angle": p.get("view:incidence_angle"),
               "asset_keys": sorted(item.get("assets", {})),
               "estimated_product_bytes": p.get("_private", {}).get("product_size")}
        rows.append(row)
        if row["collection"] == "sentinel-1-grd":
            values = (row["mode"], row["orbit_direction"], row["relative_orbit"])
            if any(value is None for value in values) or not {"VV", "VH"}.issubset(row["polarizations"]):
                rejected.append(row["id"])
            else:
                group = "/".join(map(str, (*values, "+".join(row["polarizations"]))))
                groups.setdefault(group, []).append(row["id"])
    return {"analysis_status": "metadata_only_not_processed", "item_count": len(rows),
            "items": rows, "radar_groups": groups, "radar_unusable_metadata": rejected,
            "warning": "Cloud percentage is scene-wide, not parcel QA. Groups do not establish scientific comparability or deforestation."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parcel", type=Path)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True, help="Exclusive end date")
    parser.add_argument("--output", required=True, type=Path, help="New private local directory")
    args = parser.parse_args()
    raw = args.parcel.read_bytes()
    if len(raw) > 1_000_000:
        raise ValueError("Parcel exceeds 1 MB limit")
    parcel = validate_parcel(json.loads(raw))
    if args.output.exists():
        raise ValueError("Output already exists; originals will not be overwritten")
    result, complete = [], {}
    for collection in COLLECTIONS:
        items, finished = discover(collection, parcel["bbox"], args.start, args.end)
        result.extend(items)
        complete[collection] = finished
    summary = summarize_items(result)
    summary.update({"catalog": CATALOG, "queried_at": datetime.now(timezone.utc).isoformat(),
                    "start": args.start, "end_exclusive": args.end, "parcel": parcel,
                    "parcel_sha256": hashlib.sha256(raw).hexdigest(), "pagination_complete": complete})
    args.output.mkdir(parents=True)
    (args.output / "catalog-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    # Public discovery metadata, not signed URLs or downloaded imagery.
    (args.output / "catalog-items.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": result}), encoding="utf-8")
    print(json.dumps({"items": summary["item_count"], "radar_groups": len(summary["radar_groups"]),
                      "pagination_complete": complete, "status": summary["analysis_status"]}))


if __name__ == "__main__":
    main()
