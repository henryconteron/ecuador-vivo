"""Download a reproducible USGS snapshot and independently audit it for a Reel.

Uses stdlib HTTP and pandas; runnable with the bundled analysis Python.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen, Request

import pandas as pd

SERVICE = "https://earthquake.usgs.gov/fdsnws/event/1/"
BOUNDS = dict(minlatitude=-5.5, maxlatitude=2.5, minlongitude=-83, maxlongitude=-74.5)


def get(path, params):
    url = SERVICE + path + "?" + urlencode(params)
    with urlopen(Request(url, headers={"User-Agent": "AndesPulso/1.0 (educational catalog visualization)"}), timeout=60) as response:
        return response.read(), url


def audit_features(features, first, last, minimum):
    rows=[]
    for f in features:
        p=f["properties"]
        lon,lat,depth=f["geometry"]["coordinates"]
        rows.append(dict(id=f["id"],time=pd.to_datetime(p["time"],unit="ms",utc=True),
                         longitude=lon,latitude=lat,depth=depth,magnitude=p["mag"],
                         mag_type=p.get("magType") or "N/D",place=p.get("place") or "N/D"))
    df=pd.DataFrame(rows)
    if df.empty:
        raise ValueError("Empty catalog: no publication will be rendered.")
    checks={
        "unique_ids": bool(df.id.notna().all() and df.id.is_unique),
        "valid_utc_dates": bool(df.time.notna().all() and df.time.dt.year.between(first,last).all()),
        "within_regional_window": bool(df.longitude.between(-83,-74.5).all() and df.latitude.between(-5.5,2.5).all()),
        "valid_magnitudes": bool(df.magnitude.between(minimum,10).all()),
        "depth_unknown_or_within_service_range": bool((df.depth.isna() | df.depth.between(-100,1000)).all()),
    }
    if not all(checks.values()):
        raise ValueError(f"Audit failed: {checks}")
    return df.sort_values(["time","id"]).reset_index(drop=True),checks


def prepare(output,first=1900,last=2025,minimum=4):
    now=datetime.now(timezone.utc)
    if not 1900<=first<=last<now.year:
        raise ValueError("Use completed calendar years only.")
    params=dict(BOUNDS,starttime=f"{first}-01-01T00:00:00Z",endtime=f"{last}-12-31T23:59:59.999Z",
                minmagnitude=minimum,eventtype="earthquake")
    raw_count,count_url=get("count",params)
    expected=int(raw_count)
    if expected>6000:
        raise ValueError("Too many events; narrow the query. Never silently truncate.")
    features=[]
    urls=[]
    for offset in range(1,expected+1,2000):
        payload,url=get("query",dict(params,format="geojson",orderby="time-asc",limit=2000,offset=offset))
        features.extend(json.loads(payload)["features"])
        urls.append(url)
    after_count,_=get("count",params)
    if len(features)!=expected or int(after_count)!=expected:
        raise ValueError("Catalog changed or a page is incomplete. Retry the download.")
    df,checks=audit_features(features,first,last,minimum)
    # Cross-check two well-documented events against independent single-event API requests.
    spotchecks=[]
    for event_id in ["official19060131153610_30","us20005j32"]:
        row=df.loc[df.id==event_id]
        if len(row)!=1:
            raise ValueError(f"Reference event absent or duplicated: {event_id}")
        raw,url=get("query",dict(format="geojson",eventid=event_id))
        detail=json.loads(raw)
        p=detail["properties"]
        coords=detail["geometry"]["coordinates"]
        record=row.iloc[0]
        if record.magnitude!=p["mag"] or list(record[["longitude","latitude","depth"]])!=coords or record.time!=pd.to_datetime(p["time"],unit="ms",utc=True):
            raise ValueError(f"Reference event changed: {event_id}")
        spotchecks.append(dict(id=event_id,date_utc=record.time.isoformat(),magnitude=float(record.magnitude),
                              magnitude_type=record.mag_type,longitude=float(record.longitude),latitude=float(record.latitude),
                              depth_km=float(record.depth),source=url))
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    snapshot=json.dumps(dict(type="FeatureCollection",features=features),ensure_ascii=False).encode()
    (output/"usgs_snapshot.geojson").write_bytes(snapshot)
    csv=df.to_csv(index=False).encode("utf-8")
    (output/"catalog.csv").write_bytes(csv)
    manifest=dict(source=SERVICE,query=params,downloaded_at_utc=now.isoformat(),count_url=count_url,page_urls=urls,
                  reported_count=expected,exported_count=len(df),checks=checks,spotchecks=spotchecks,
                  unknown_depth_count=int(df.depth.isna().sum()),negative_depth_count=int((df.depth<0).sum()),
                  magnitude_types=df.mag_type.value_counts().to_dict(),earliest_utc=df.time.min().isoformat(),
                  latest_utc=df.time.max().isoformat(),snapshot_sha256=sha256(snapshot).hexdigest(),csv_sha256=sha256(csv).hexdigest(),
                  first=first,last=last,minimum=minimum,
                  limitations=["Regional rectangle, not Ecuador-only or a political-boundary selection; excludes Galápagos.",
                               "Historical catalog is incomplete; annual counts are not comparable without completeness analysis.",
                               "Original USGS magnitude types retained, not homogenized to Mw.",
                               "Historical locations, depths and magnitudes are estimates that can be revised.",
                               "No intensity, damage, fault assignment or prediction is inferred."])
    (output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(dict(records=len(df),unknown_depth=manifest["unknown_depth_count"],checks=checks,spotchecks=spotchecks),ensure_ascii=False,indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path)
    args=parser.parse_args()
    prepare(args.output)
