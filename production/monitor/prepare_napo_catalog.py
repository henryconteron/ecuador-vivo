"""Pin a regional USGS 1900–2025 snapshot; do not merge it with IG-EPN cases."""
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import math
from pathlib import Path

import requests

FOLDER = Path("artifacts/serie_memoria_sismica/01_napo")
SERVICE = "https://earthquake.usgs.gov/fdsnws/event/1/"
# Regional window, NOT modern or historic Napo political boundaries.
# North edge includes the 1987 main event at 0.151 N.
REGION = (-78.8, -76.75, -1.65, .30)
PARAMS = {"starttime": "1900-01-01T00:00:00Z", "endtime": "2025-12-31T23:59:59.999Z",
          "minmagnitude": 4, "minlongitude": REGION[0], "maxlongitude": REGION[1],
          "minlatitude": REGION[2], "maxlatitude": REGION[3], "eventtype": "earthquake"}
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def normalize(features):
    rows = []
    identities = set()
    for feature in features:
        props, coords = feature["properties"], feature["geometry"]["coordinates"]
        identity = feature["id"]
        if identity in identities:
            raise ValueError("Duplicate USGS event ID")
        identities.add(identity)
        lon, lat, magnitude = float(coords[0]), float(coords[1]), float(props["mag"])
        if not all(math.isfinite(v) for v in (lon, lat, magnitude)):
            raise ValueError("Non-finite event parameters")
        if not REGION[0] <= lon <= REGION[1] or not REGION[2] <= lat <= REGION[3] or magnitude < 4:
            raise ValueError("Event outside the declared query")
        # Windows datetime.fromtimestamp fails for negative pre-1970 epochs.
        utc = EPOCH+timedelta(milliseconds=props["time"])
        if not 1900 <= utc.year <= 2025:
            raise ValueError("USGS event outside the declared period")
        depth = coords[2] if len(coords) > 2 else None
        depth = float(depth) if depth is not None else None
        if depth is not None and not math.isfinite(depth):
            depth = None
        rows.append({"id": identity, "source": "USGS", "utc_time": utc.isoformat(),
                     "local_time": utc.astimezone(timezone(timedelta(hours=-5))).isoformat(),
                     "year": utc.year, "magnitude": magnitude,
                     "magnitude_type": props.get("magType") or "N/D", "depth_km": depth,
                     "latitude": lat, "longitude": lon,
                     "source_url": props.get("url") or f"https://earthquake.usgs.gov/earthquakes/eventpage/{identity}"})
    return sorted(rows, key=lambda row: (row["utc_time"], row["id"]))


def load_catalog(folder):
    folder = Path(folder)
    raw = (folder / "usgs_napo_region_1900_2025.geojson").read_bytes()
    audit = json.loads((folder / "usgs_history_audit.json").read_text(encoding="utf-8"))
    if sha256(raw).hexdigest() != audit["sha256"] or audit["query"] != PARAMS:
        raise ValueError("USGS historical snapshot integrity/query mismatch")
    rows = normalize(json.loads(raw)["features"])
    if len(rows) != audit["expected_count"]:
        raise ValueError("USGS catalog count mismatch")
    return rows, audit


def main():
    response = requests.get(SERVICE+"count", params=PARAMS, timeout=45)
    response.raise_for_status()
    expected = int(response.text)
    if expected > 20000:
        raise ValueError("USGS single-query limit exceeded; pagination required")
    response = requests.get(SERVICE+"query", params=dict(PARAMS, format="geojson", orderby="time-asc"), timeout=45)
    response.raise_for_status()
    rows = normalize(response.json()["features"])
    if len(rows) != expected:
        raise ValueError("Catalog changed or returned incomplete")
    FOLDER.mkdir(parents=True, exist_ok=True)
    (FOLDER / "usgs_napo_region_1900_2025.geojson").write_bytes(response.content)
    audit = {"retrieved_utc": datetime.now(timezone.utc).isoformat(), "query": PARAMS,
             "query_url": response.url, "source": "USGS ComCat", "expected_count": expected,
             "sha256": sha256(response.content).hexdigest(), "region": REGION,
             "earliest_record": rows[0]["utc_time"] if rows else None,
             "magnitude_types": sorted({r["magnitude_type"] for r in rows}),
             "missing_depth": sum(r["depth_km"] is None for r in rows),
             "limits": ["Regional rectangle includes Napo and neighboring areas; not a province-only catalog.",
                        "Query starts in 1900; availability/completeness vary in time and magnitude.",
                        "No events in an interval means no matching catalog records, not no earthquakes.",
                        "Magnitude types retained as published; no homogenization or ranking.",
                        "Historical USGS map stops at 2025; IG-EPN 2026 is a separate selected-case scene.",
                        "Different source periods/selection thresholds cannot establish a rate trend.",
                        "No IG-EPN historical cases appended; no cross-source double counting."]}
    (FOLDER / "usgs_history_audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    load_catalog(FOLDER)
    print(json.dumps({"count": expected, "earliest": audit["earliest_record"], "types": audit["magnitude_types"],
                      "1987_main": [r for r in rows if r["id"] == "usp000330w"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
