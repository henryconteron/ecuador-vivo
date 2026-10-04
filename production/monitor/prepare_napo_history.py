"""Pin selected IG-EPN historical reports; never imply a complete catalog."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re

import requests

FOLDER = Path("artifacts/serie_memoria_sismica/01_napo")
REPORTS = [
    {"key": "1987", "url": "https://www.igepn.edu.ec/cayambe/762-hoy-se-recuerda-el-terremoto-del-reventador-de-1987",
     "checks": [r"5 de marzo de 1987", r"Ms\s*=\s*6,1", r"Ms\s*=\s*6,9"],
     "events": [{"date": "1987-03-05", "local_time": "20:54", "magnitude": 6.1, "type": "Ms", "depth_km": None, "latitude": None, "longitude": None},
                {"date": "1987-03-05", "local_time": "23:10", "magnitude": 6.9, "type": "Ms", "depth_km": None, "latitude": None, "longitude": None}]},
    {"key": "2023_006", "url": "https://www.igepn.edu.ec/servicios/noticias/2050-informe-sismico-especial-no-2023-006",
     "checks": [r"18 de junio de 2023", r"5\.3\s*MLv", r"0\.66", r"77\.61", r"2\.2\s*km"],
     "events": [{"date": "2023-06-18", "local_time": "04:10", "magnitude": 5.3, "type": "MLv", "depth_km": 2.2, "latitude": -.66, "longitude": -77.61}]},
    {"key": "2025_002", "url": "https://www.igepn.edu.ec/servicios/noticias/2207-informe-sismico-especial-no-2025-002",
     "checks": [r"31 de enero de 2025", r"5\.5\s*MLv", r"0\.88", r"78\.11", r"11\s*km"],
     "events": [{"date": "2025-01-31", "local_time": "18:02", "magnitude": 5.5, "type": "MLv", "depth_km": 11, "latitude": -.88, "longitude": -78.11}]},
    {"key": "2025_007", "url": "https://www.igepn.edu.ec/servicios/noticias/2249-informe-sismico-especial-no-2025-007",
     "checks": [r"16 de junio de 2025", r"4\.9\s*Mw", r"0\.89", r"78\.16", r"17\s*km"],
     "events": [{"date": "2025-06-16", "local_time": "21:46", "magnitude": 4.9, "type": "Mw", "depth_km": 17, "latitude": -.89, "longitude": -78.16}]},
    {"key": "2025_016", "url": "https://www.igepn.edu.ec/servicios/noticias/2318-informe-sismico-especial-no-2025-016",
     "checks": [r"19 de diciembre de 2025", r"4\.9\s*Mw", r"0\.700", r"78\.037", r"18\s*km"],
     "events": [{"date": "2025-12-19", "local_time": "16:59", "magnitude": 4.9, "type": "Mw", "depth_km": 18, "latitude": -.700, "longitude": -78.037}]},
]


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def verify_report(report, raw):
    parser = PlainText()
    parser.feed(raw.decode("utf-8"))
    content = re.sub(r"\s+", " ", " ".join(parser.parts))
    for pattern in report["checks"]:
        if not re.search(pattern, content):
            raise ValueError(f"Unverified report {report['key']}: {pattern}")
    return content


def load_history(folder):
    folder = Path(folder)
    manifest = json.loads((folder / "history_evidence.json").read_text(encoding="utf-8"))
    if len(manifest["reports"]) != len(REPORTS):
        raise ValueError("Unexpected number of historical reports")
    events = []
    for expected, saved in zip(REPORTS, manifest["reports"]):
        raw = (folder / saved["file"]).read_bytes()
        if sha256(raw).hexdigest() != saved["sha256"]:
            raise ValueError("Historical evidence hash mismatch")
        verify_report(expected, raw)
        if saved["events"] != expected["events"] or saved["url"] != expected["url"]:
            raise ValueError("Historical event values changed")
        events.extend(dict(row, source_url=saved["url"]) for row in saved["events"])
    return events


def fetch(report):
    response = requests.get(report["url"], timeout=45)
    response.raise_for_status()
    verify_report(report, response.content)
    return report, response.content


def main():
    FOLDER.mkdir(parents=True, exist_ok=True)
    reports = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        for report, raw in executor.map(fetch, REPORTS):
            filename = f"history_igepn_{report['key']}.html"
            (FOLDER / filename).write_bytes(raw)
            reports.append({"url": report["url"], "file": filename,
                            "sha256": sha256(raw).hexdigest(), "events": report["events"]})
    manifest = {"retrieved_utc": datetime.now(timezone.utc).isoformat(), "reports": reports,
                "selection": "1987 pair and four documented 2023–2025 cases; not exhaustive",
                "limits": ["1987 province boundaries differed from today's reference map.",
                           "No exact epicenters or depths supplied here for 1987; never invent them.",
                           "Magnitude types are heterogeneous; no ranking or energy comparison.",
                           "Coordinates/depths follow the identified report, not a unified catalog."]}
    (FOLDER / "history_evidence.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Verified {len(load_history(FOLDER))} historical cases in {len(reports)} official reports.")


if __name__ == "__main__":
    main()
