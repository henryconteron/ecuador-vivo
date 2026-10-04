"""Pin the published USGS snapshot and verify the next educational episode."""
from datetime import datetime, timezone, timedelta
from hashlib import sha256
from html import unescape
import json
from pathlib import Path
import re

import requests

ROOT = Path(__file__).resolve().parent
FOLDER = ROOT / "artifacts/serie_memoria_sismica/00_profundidad_danos"
SNAPSHOT = ROOT / "artifacts/reel_ecuador_1900_2025_v6"
HASH = "8cf19180b19b9a9998f76f1feee9bf88b69d141287a9d213e3455f20c1b2d5c8"
CASE_IDS = ("us20005j32", "usb000s27f", "usp000330w")
UA = {"User-Agent": "AndesPulsoResearch/1.0 (educational earthquake video; Python requests)"}
PHOTOS = {
    "pedernales": "TERREMOTO CANTÓN PEDERNALES (26443597791).jpg",
    "quito": "ZONA DEL DERRUMBE EN EL RÍO MONJAS (14898089101).jpg",
}
SOURCES = {
    "depth": "https://www.usgs.gov/faqs/what-depth-do-earthquakes-occur-what-significance-depth",
    "classification": "https://www.usgs.gov/programs/earthquake-hazards/determining-depth-earthquake",
    "coast": "https://www.igepn.edu.ec/1324-informe-sismico-especial-n-18-2016.html",
    "amazon": "https://www.igepn.edu.ec/cayambe/762-hoy-se-recuerda-el-terremoto-del-reventador-de-1987",
}


def rows_from_snapshot(payload):
    rows = []
    for f in payload["features"]:
        p = f["properties"]
        lon, lat, depth = f["geometry"]["coordinates"]
        utc = datetime(1970, 1, 1, tzinfo=timezone.utc)+timedelta(milliseconds=p["time"])
        if not (-83 <= lon <= -74.5 and -5.5 <= lat <= 2.5 and 1900 <= utc.year <= 2025 and p["mag"] >= 4):
            raise ValueError(f"Out-of-scope record {f['id']}")
        if depth is not None and not (0 <= depth <= 700):
            raise ValueError("Unexpected depth")
        rows.append(dict(id=f["id"], longitude=lon, latitude=lat, depth_km=depth,
                         magnitude=p["mag"], magnitude_type=p["magType"], year=utc.year,
                         utc_time=utc.isoformat(), local_time=utc.astimezone(timezone(timedelta(hours=-5))).isoformat(),
                         url=p["url"]))
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate IDs")
    return sorted(rows, key=lambda r: r["utc_time"])


def load_history():
    raw = (SNAPSHOT / "usgs_snapshot.geojson").read_bytes()
    if sha256(raw).hexdigest() != HASH:
        raise ValueError("Published snapshot changed; do not silently replace it")
    rows = rows_from_snapshot(json.loads(raw))
    if len(rows) != 2661:
        raise ValueError("Published regional selection must have 2661 records")
    return rows


def request(url, **kwargs):
    r = requests.get(url, headers=UA, timeout=45, **kwargs)
    r.raise_for_status()
    return r


def prepare(rights_only=False):
    FOLDER.mkdir(parents=True, exist_ok=True)
    history = load_history()
    cases = [next(r for r in history if r["id"] == identity) for identity in CASE_IDS]
    for row in cases:
        r = request("https://earthquake.usgs.gov/fdsnws/event/1/query", params={"format": "geojson", "eventid": row["id"]})
        raw = r.json()
        coords, props = raw["geometry"]["coordinates"], raw["properties"]
        if coords != [row["longitude"], row["latitude"], row["depth_km"]] or props["mag"] != row["magnitude"] or props["magType"] != row["magnitude_type"]:
            raise ValueError(f"USGS case revised: {row['id']}; review explicitly")
        (FOLDER/f"{row['id']}_verified.geojson").write_bytes(r.content)
    for key, url in SOURCES.items():
        (FOLDER/f"source_{key}.html").write_bytes(request(url).content)
    media = {}
    for key, title in PHOTOS.items():
        url = "https://commons.wikimedia.org/wiki/File:"+requests.utils.quote(title.replace(" ", "_"), safe="()")
        r = request(url)
        (FOLDER/f"rights_{key}.html").write_bytes(r.content)
        if "https://creativecommons.org/licenses/by-sa/2.0" not in r.text:
            raise ValueError("Expected CC BY-SA 2.0 not found")
        match = re.search(r'class="fullMedia".*?<a href="([^"]+)"', r.text, re.S)
        if not match:
            raise ValueError("Original photograph link missing")
        commons_original = unescape(match[1]).split("?")[0]
        photo_id = re.search(r'\((\d+)\)', title)[1]
        source_photo = f'https://www.flickr.com/photos/agenciaandes_ec/{photo_id}/'
        embed = request('https://www.flickr.com/services/oembed/', params={'url':source_photo, 'format':'json'})
        (FOLDER/f'rights_{key}_flickr.json').write_bytes(embed.content)
        photo_meta = embed.json()
        if photo_meta.get('license') != 'CC BY-SA 2.0':
            raise ValueError('Current original-provider license differs; review before reuse')
        original = photo_meta['url']
        photo_path = FOLDER/f"archive_{key}.jpg"
        if not rights_only and not photo_path.exists():
            photo_path.write_bytes(request(original).content)
        photo = photo_path.read_bytes() if photo_path.exists() else None
        body = re.sub(r'<script.*?</script>', '', r.text, flags=re.S)
        plain = unescape(re.sub(r"<[^>]+>", " ", body))
        start = plain.find('Description', plain.find('Summary'))
        media[key] = dict(title=title, source_page=url, original_provider=source_photo,
                          original_url=original, commons_original_url=commons_original,
                          photographer='Micaela Ayala V. / ANDES' if key=='pedernales' else 'Luis Astudillo C. / ANDES',
                          photographed_at_local='2016-04-18 10:52' if key=='pedernales' else '2014-08-12 17:35',
                          license="CC BY-SA 2.0", license_url="https://creativecommons.org/licenses/by-sa/2.0/",
                          sha256=sha256(photo).hexdigest() if photo else None, sha256_rights=sha256(r.content).hexdigest(),
                          modifications="Aspect-preserving resizing only; no crop, retouch or fabricated motion.",
                          evidence_text=plain[start:start+6500])
    audit = dict(checked_at_utc=datetime.now(timezone.utc).isoformat(), snapshot_sha256=HASH,
                 history_count=len(history), first_available=history[0]["utc_time"], cases=cases,
                 sources=SOURCES, media=media, limitation="Regional rectangle, not Ecuador-only; excludes Galápagos; incomplete historical coverage; original magnitude types retained.")
    (FOLDER/"evidence.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k:v for k,v in audit.items() if k!='media'}, ensure_ascii=True, indent=2))
    print('Verified media:', ', '.join(media))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rights-only', action='store_true')
    prepare(parser.parse_args().rights_only)
