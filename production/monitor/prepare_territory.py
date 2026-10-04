"""Pin public IG-EPN case evidence and reference province boundaries.

These are individual bulletins, never a complete catalog or hazard ranking.
"""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

import requests

CHANNEL = "https://t.me/s/SismosVolcanesIGEPN"
BOUNDARIES = "https://www.geoboundaries.org/api/current/gbOpen/ECU/ADM1/"
CASE_ID = "igepn2026lsvn"


class BulletinParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.messages = []
        self.current = None
        self.text_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("data-post"):
            self.current = {"post": attrs["data-post"], "text": ""}
            self.messages.append(self.current)
        if tag == "div" and "tgme_widget_message_text" in attrs.get("class", "").split():
            self.text_depth = 1
        elif self.text_depth and tag == "div":
            self.text_depth += 1
        if self.text_depth and tag == "br":
            self.current["text"] += "\n"

    def handle_endtag(self, tag):
        if self.text_depth and tag == "div":
            self.text_depth -= 1

    def handle_data(self, data):
        if self.text_depth and self.current is not None:
            self.current["text"] += data


def parse_bulletin(message):
    text = message["text"]
    status = re.search(r"\[(PRELIMINAR|REVISADO)\]", text)
    event = re.search(r"Evento:\s*(igepn\d{4}[a-z]+)", text)
    time = re.search(r"Ocurrido:\s*(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)", text)
    magnitude = re.search(r"Mag\.:\s*(\d+(?:\.\d+)?)([A-Za-z]+)", text)
    depth = re.search(r"Prof\.:\s*(\d+(?:\.\d+)?)\s*km", text)
    latitude = re.search(r"Lat\.:\s*(\d+(?:\.\d+)?)\s*°?\s*([NS])", text)
    longitude = re.search(r"Long\.:\s*(\d+(?:\.\d+)?)\s*°?\s*([EW])", text)
    if not all((status, event, time, magnitude, depth, latitude, longitude)):
        raise ValueError("Incomplete official bulletin; do not invent missing values")
    local = datetime.fromisoformat(time.group(1)).replace(tzinfo=timezone(timedelta(hours=-5)))
    return {"id": event.group(1), "status": status.group(1), "local_time": local.isoformat(),
            "utc_time": local.astimezone(timezone.utc).isoformat(),
            "magnitude": float(magnitude.group(1)), "magnitude_type": magnitude.group(2),
            "depth_km": float(depth.group(1)),
            "latitude": float(latitude.group(1)) * (-1 if latitude.group(2) == "S" else 1),
            "longitude": float(longitude.group(1)) * (-1 if longitude.group(2) == "W" else 1),
            "source_url": "https://t.me/" + message["post"], "source_text": text.strip()}


def fetch_case():
    response = requests.get(CHANNEL, params={"q": CASE_ID}, timeout=30)
    response.raise_for_status()
    parser = BulletinParser()
    parser.feed(response.content.decode("utf-8"))
    rows = [parse_bulletin(message) for message in parser.messages if CASE_ID in message["text"]]
    if len(rows) != 2 or {row["status"] for row in rows} != {"PRELIMINAR", "REVISADO"}:
        raise ValueError("Expected exactly two versions of the same official event")
    if any(row["id"] != CASE_ID or row["local_time"][:10] != "2026-06-16" for row in rows):
        raise ValueError("Unexpected event identity/date")
    rows.sort(key=lambda row: row["status"] == "REVISADO")
    return response.content, rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("artifacts/serie_memoria_sismica/01_napo"))
    args = parser.parse_args()
    folder = args.output
    folder.mkdir(parents=True, exist_ok=True)
    raw, rows = fetch_case()
    (folder / "igepn_official_case.html").write_bytes(raw)
    (folder / "igepn_2026_case.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    response = requests.get(BOUNDARIES, timeout=30)
    response.raise_for_status()
    metadata = response.json()
    response = requests.get(metadata["simplifiedGeometryGeoJSON"], timeout=30)
    response.raise_for_status()
    geometry = response.json()
    if len(geometry["features"]) != 24 or not any(f["properties"]["shapeName"] == "Napo" for f in geometry["features"]):
        raise ValueError("Expected 24 provinces including Napo")
    (folder / "ecuador_adm1_reference.geojson").write_bytes(response.content)
    audit = {"retrieved_utc": datetime.now(timezone.utc).isoformat(), "official_channel_url": CHANNEL,
             "case_id": CASE_ID, "bulletin_urls": [row["source_url"] for row in rows],
             "evidence_sha256": hashlib.sha256(raw).hexdigest(), "boundary_metadata": metadata,
             "boundary_sha256": hashlib.sha256(response.content).hexdigest(),
             "limitations": ["Two bulletin versions of ONE earthquake, not two earthquakes.",
                             "Individual case, not a complete 2026 catalog.",
                             "M is the published type; do not relabel as MLv or Mw.",
                             "Boundary reference represents 2011, not a certified current cadastral layer.",
                             "The 1987 province of Napo had different administrative extent."]}
    (folder / "source_audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    print("Evidence and map reference saved:", folder.resolve())


if __name__ == "__main__":
    main()
