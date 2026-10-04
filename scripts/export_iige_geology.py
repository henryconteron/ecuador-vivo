"""Freeze an IIGE spatial selection; keep whole intersecting polygons, not a clip.

Run manually, never silently refresh published evidence. Standard library only.
"""
import datetime
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://capas.geoenergia.gob.ec/arcgis/rest/services/"
BBOX = [-78.1, -1.2, -77.6, -0.7]


def fetch(url):
    with urllib.request.urlopen(url, timeout=60) as reply:
        data = reply.read()
    value = json.loads(data)
    if "error" in value:
        raise ValueError(value["error"])
    return value


def export():
    folder = ROOT / "data" / "geology"
    folder.mkdir(parents=True, exist_ok=True)
    records = []
    for service, name in [("Geologia_General", "tena-units"), ("Cartas_Geologicas_100K", "tena-sheets")]:
        endpoint = BASE + service + "/MapServer/0"
        query = dict(where="1=1", geometry=",".join(map(str, BBOX)), geometryType="esriGeometryEnvelope",
                     inSR=4326, spatialRel="esriSpatialRelIntersects")
        count = fetch(endpoint + "/query?" + urllib.parse.urlencode(dict(query, returnCountOnly="true", f="json")))["count"]
        url = endpoint + "/query?" + urllib.parse.urlencode(dict(query, outFields="*", outSR=4326, f="geojson"))
        collection = fetch(url)
        if collection.get("type") != "FeatureCollection" or len(collection["features"]) != count or count == 0 or collection.get("exceededTransferLimit"):
            raise ValueError("Incomplete or empty spatial selection")
        ids = [feature["properties"]["OBJECTID"] for feature in collection["features"]]
        if len(set(ids)) != count:
            raise ValueError("Duplicate IDs")
        # Deterministic UTF-8 LF serialization, not a claim of original response bytes.
        raw = (json.dumps(collection, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
        path = folder / (name + ".geojson")
        path.write_bytes(raw)
        records.append(dict(id=name, path=path.relative_to(ROOT).as_posix(), count=count, query=url,
                            sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw)))
    manifest = dict(source="Instituto de Investigación Geológico y Energético (IIGE)",
                    retrieved=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    terms="https://geoportal.geoenergia.gob.ec/", bbox=BBOX, crs="OGC:CRS84",
                    selection="Whole polygons intersecting the Tena–Archidona study window; not clipped, not a province boundary.",
                    map_scale="Geologia General: not established from service metadata. Sheet index: 1:100000 sheets, not geological units.",
                    status="source-snapshot-not-independently-validated", files=records)
    (folder / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    for row in records:
        print(row["id"], row["count"], row["bytes"], row["sha256"])


if __name__ == "__main__":
    export()
