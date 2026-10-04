"""Pin city locations and a second reviewed IG-EPN bulletin for the fault reel."""
from datetime import datetime, timezone
from hashlib import sha256
import io
import json
from pathlib import Path
import zipfile

import requests

from prepare_territory import BulletinParser, parse_bulletin, CHANNEL

FOLDER = Path("artifacts/serie_memoria_sismica/01_napo")
CITY_SOURCE = "https://download.geonames.org/export/dump/EC.zip"
CITY_IDS = {"3650721": "Tena", "3658314": "El Chaco", "3660573": "Archidona", "10343870": "Baeza"}
SECOND_CASE = "igepn2026qghw"


def parse_cities(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        content = archive.read("EC.txt").decode("utf-8")
    cities = []
    for line in content.splitlines():
        fields = line.split("\t")
        if fields[0] not in CITY_IDS:
            continue
        if fields[1] != CITY_IDS[fields[0]] or fields[6] != "P" or fields[8] != "EC" or fields[10] != "23":
            raise ValueError("Unexpected city identity / feature class / country / province")
        cities.append({"id": fields[0], "name": fields[1], "latitude": float(fields[4]),
                       "longitude": float(fields[5]), "feature_code": fields[7],
                       "source_url": f"https://www.geonames.org/{fields[0]}/"})
    if len(cities) != 4:
        raise ValueError("Expected four populated-place locations, not canton centroids")
    return sorted(cities, key=lambda row: row["name"])


def parse_reviewed(raw):
    parser = BulletinParser()
    parser.feed(raw.decode("utf-8"))
    rows = [parse_bulletin(m) for m in parser.messages if SECOND_CASE in m["text"]]
    reviewed = [r for r in rows if r["status"] == "REVISADO"]
    if len(reviewed) != 1 or reviewed[0]["local_time"][:10] != "2026-08-19":
        raise ValueError("Expected one identified reviewed bulletin for August 19")
    return reviewed[0]


def load_fault_evidence(folder):
    folder = Path(folder)
    audit = json.loads((folder / "fault_episode_evidence.json").read_text(encoding="utf-8"))
    city_raw = (folder / "geonames_ec_reference.zip").read_bytes()
    case_raw = (folder / "igepn_2026_second_case.html").read_bytes()
    if sha256(city_raw).hexdigest() != audit["city_sha256"] or sha256(case_raw).hexdigest() != audit["second_case_sha256"]:
        raise ValueError("Fault-episode source evidence hash mismatch")
    cities, second = parse_cities(city_raw), parse_reviewed(case_raw)
    if cities != audit["cities"] or second != audit["second_case"]:
        raise ValueError("Fault-episode values differ from source evidence")
    return cities, second


def main():
    FOLDER.mkdir(parents=True, exist_ok=True)
    response = requests.get(CITY_SOURCE, timeout=45)
    response.raise_for_status()
    city_raw = response.content
    cities = parse_cities(city_raw)
    response = requests.get(CHANNEL, params={"q": SECOND_CASE}, timeout=45)
    response.raise_for_status()
    case_raw = response.content
    second = parse_reviewed(case_raw)
    (FOLDER / "geonames_ec_reference.zip").write_bytes(city_raw)
    (FOLDER / "igepn_2026_second_case.html").write_bytes(case_raw)
    audit = {"retrieved_utc": datetime.now(timezone.utc).isoformat(),
             "city_source": CITY_SOURCE, "city_license": "GeoNames CC BY 4.0; attribution required",
             "city_sha256": sha256(city_raw).hexdigest(), "cities": cities,
             "second_case_sha256": sha256(case_raw).hexdigest(), "second_case": second,
             "limits": ["Selected 2026 cases, not all events or a live catalog.",
                        "City points are gazetteer locations, not boundaries or damage observations.",
                        "August depth follows identified Telegram bulletin (3.0 km); web table reports 3.2 km. Depth is not shown in V4 map.",
                        "No fault trace or fault assignment for 2026 is provided by these bulletins."]}
    (FOLDER / "fault_episode_evidence.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    load_fault_evidence(FOLDER)
    print("Verified four city locations and second reviewed 2026 bulletin:", second["source_url"])


if __name__ == "__main__":
    main()
