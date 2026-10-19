"""Check installed SNAP operators and anonymous manifest access, not SAR accuracy."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


def inspect_graph(path):
    root = ET.parse(path).getroot()
    nodes, seen = [], set()
    for node in root.findall("node"):
        node_id = node.attrib["id"]
        if node_id in seen:
            raise ValueError("Duplicate graph node")
        for source in node.findall("sources/*"):
            if source.attrib.get("refid") not in seen:
                raise ValueError("Missing or out-of-order graph dependency")
        seen.add(node_id)
        nodes.append({"id": node_id, "operator": node.findtext("operator"),
                      "parameters": [child.tag for child in node.findall("parameters/*")]})
    if not nodes:
        raise ValueError("Empty graph")
    return nodes


def missing_parameters(parameters, help_text):
    documented = set(re.findall(r"<([A-Za-z][\w]*)>", help_text))
    return sorted(set(parameters) - documented)


def manifest_access(href):
    parsed = urlparse(href)
    if parsed.scheme != "https" or parsed.hostname != "download.dataspace.copernicus.eu":
        raise ValueError("Only the official CDSE download host is allowed")
    try:
        request = Request(href, headers={"Range": "bytes=0-1023", "User-Agent": "EcuadorVivo-parcel-pilot/0.1"})
        with urlopen(request, timeout=30) as response:
            prefix = response.read(1024)
            return {"http_status": response.status, "sample_bytes": len(prefix),
                    "appears_xml": prefix.lstrip().startswith(b"<"),
                    "status": "response_received_not_product_downloaded"}
    except HTTPError as error:
        return {"http_status": error.code, "status": "authentication_required" if error.code == 401 else "http_error"}
    except (URLError, TimeoutError) as error:
        return {"status": "network_error", "error_type": type(error).__name__}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gpt", type=Path, default=Path("C:/Program Files/esa-snap/bin/gpt.exe"))
    parser.add_argument("--graph", type=Path, default=Path("tools/parcelas/sentinel1-grd-diagnostic.xml"))
    parser.add_argument("--items", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Output exists; choose a new directory")
    if not args.gpt.is_file():
        raise ValueError("SNAP GPT executable not found")
    nodes = inspect_graph(args.graph)
    args.output.mkdir(parents=True)
    checks = []
    for node in nodes:
        try:
            process = subprocess.run([str(args.gpt), node["operator"], "-h"],
                                     capture_output=True, text=True, encoding="utf-8",
                                     errors="replace", timeout=75)
            help_text = process.stdout + process.stderr
            (args.output / (node["id"] + "-help.txt")).write_text(help_text, encoding="utf-8")
            missing = missing_parameters(node["parameters"], help_text)
            checks.append({**node, "return_code": process.returncode, "unknown_parameters": missing,
                           "status": "names_checked_not_values" if process.returncode == 0 and not missing else "needs_review"})
        except subprocess.TimeoutExpired:
            checks.append({**node, "status": "help_timeout"})
        print(node["operator"], checks[-1]["status"], flush=True)
    items = json.loads(args.items.read_text(encoding="utf-8"))["features"]
    item = next(item for item in items if item.get("collection") == "sentinel-1-grd")
    href = item["assets"]["safe_manifest"]["alternate"]["https"]["href"]
    report = {"created_at": datetime.now(timezone.utc).isoformat(), "operators": checks,
              "probe_item_id": item["id"], "manifest_access": manifest_access(href),
              "processing_status": "not_executed", "reader_compatibility": "not_tested",
              "warning": "Parameter-name checks do not validate values, graph execution or scientific suitability."}
    (args.output / "preflight.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["manifest_access"]))


if __name__ == "__main__":
    main()
