"""Recheck the frozen publication snapshot and official USGS live queries."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

import pandas as pd
from prepare_reel import audit_features, get
from reel_design import depth_counts, CREDIT


def audit(folder):
    folder=Path(folder)
    manifest=json.loads((folder/"manifest.json").read_text(encoding="utf-8"))
    snapshot=(folder/"usgs_snapshot.geojson").read_bytes()
    csv=(folder/"catalog.csv").read_bytes()
    assert sha256(snapshot).hexdigest()==manifest["snapshot_sha256"]
    assert sha256(csv).hexdigest()==manifest["csv_sha256"]
    saved,checks=audit_features(json.loads(snapshot)["features"],manifest["first"],manifest["last"],manifest["minimum"])
    rendered=pd.read_csv(folder/"catalog.csv")
    rendered.time=pd.to_datetime(rendered.time,utc=True,format="ISO8601")
    pd.testing.assert_frame_equal(saved,rendered,check_dtype=False,check_exact=True)
    counts=depth_counts(saved)
    assert len(saved)==manifest["exported_count"]==2661
    assert counts==dict(shallow=1752,intermediate=908,deep=0,unknown=1)
    assert float(saved.depth.max())==254
    assert (saved.depth.dropna()>=0).all()
    report=dict(checked_at_utc=datetime.now(timezone.utc).isoformat(),credit=CREDIT,
                snapshot_checks=checks,records=len(saved),depth_counts=counts,
                depth_max_km=float(saved.depth.max()),magnitude_types=saved.mag_type.value_counts().to_dict(),
                original_csv_sha256=manifest["csv_sha256"],snapshot_matches_rendered_csv=True)
    # Fresh official comparison; the film itself remains tied to the dated snapshot.
    fresh=[]
    count_raw,count_url=get("count",manifest["query"])
    current_count=int(count_raw)
    for offset in range(1,current_count+1,2000):
        payload,_=get("query",dict(manifest["query"],format="geojson",orderby="time-asc",limit=2000,offset=offset))
        fresh.extend(json.loads(payload)["features"])
    current,current_checks=audit_features(fresh,manifest["first"],manifest["last"],manifest["minimum"])
    assert len(current)==current_count
    # Ignore cosmetic place-name changes, but detect any change to scientific values.
    columns=["id","time","longitude","latitude","depth","magnitude","mag_type"]
    scientific_match=saved[columns].equals(current[columns])
    report["live_historical_check"]=dict(source=count_url,records=current_count,checks=current_checks,
                                           scientific_values_match_snapshot=scientific_match,
                                           depth_counts=depth_counts(current),depth_max_km=float(current.depth.max()))
    cutoff=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    params=dict(manifest["query"],starttime="2026-01-01T00:00:00Z",endtime=cutoff)
    raw,url=get("query",dict(params,format="geojson",orderby="time",limit=2000))
    events=json.loads(raw)["features"]
    ecuador=[event for event in events if "Ecuador" in (event["properties"].get("place") or "")]
    def summary(event):
        props=event["properties"]
        return dict(id=event["id"],time_utc=pd.to_datetime(props["time"],unit="ms",utc=True).isoformat(),
                    magnitude=props["mag"],magnitude_type=props["magType"],place=props["place"],
                    coordinates=event["geometry"]["coordinates"],source=props["url"])
    report["separate_2026_check"]=dict(source=url,cutoff_utc=cutoff,regional_records_returned=len(events),
                                      example_with_ecuador_place=summary(ecuador[0]) if ecuador else None,
                                      included_in_video=False,
                                      note="Regional rectangle and M >= 4; place label used only to choose an example, not a political-boundary count.")
    (folder/"publication_audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
    if not scientific_match:
        raise ValueError("Live scientific values changed: review before recommending publication.")
    return report


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder",type=Path)
    audit(parser.parse_args().folder)
