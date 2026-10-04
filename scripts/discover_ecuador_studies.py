"""Discover Crossref candidates. Never publish them into the reviewed library.

The public library is curated manually. CC metadata is a discovery signal,
not proof that the full text or every figure is reusable.
"""
import argparse
import datetime
import json
from pathlib import Path
import urllib.parse
import urllib.request

def select_candidates(items):
    records = {}
    for item in items:
        title = " ".join(item.get("title", []))
        if "ecuador" not in title.casefold() or not item.get("DOI"):
            continue
        licenses = [row.get("URL", "") for row in item.get("license", [])]
        if not any("creativecommons.org/licenses/" in url for url in licenses):
            continue
        records[item["DOI"]] = dict(doi=item["DOI"], title=title, url="https://doi.org/" + item["DOI"],
                                    licenses=licenses, status="candidate-needs-editorial-and-access-review")
    return sorted(records.values(), key=lambda row: row["doi"])

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("_local/library-candidates.json"))
    args = parser.parse_args()
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode({"query.title":"Ecuador geology hydrology climate", "filter":"type:journal-article,has-license:true", "rows":100, "sort":"published", "order":"desc"})
    with urllib.request.urlopen(url, timeout=60) as response:
        payload = json.load(response)
    result = dict(retrieved=datetime.datetime.now(datetime.timezone.utc).isoformat(), query=url,
                  coverage="One discovery page, title-matched Ecuador, incomplete and not peer-review verification",
                  candidates=select_candidates(payload["message"]["items"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(result['candidates'])} candidates saved for manual review; public library unchanged.")

if __name__ == "__main__":
    main()
