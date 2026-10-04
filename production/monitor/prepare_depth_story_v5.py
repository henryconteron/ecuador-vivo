"""Freeze primary wave science and bind unchanged historical sources."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import requests
from prepare_depth_story_v4 import V4
from prepare_depth_episode import HASH,UA

V5=V4.parent/'v5'
SOURCES={
    'body_waves':'https://earthquake.usgs.gov/earthquakes/events/1906calif/18april/earthwaves.php',
    'wave_motion':'https://www.earthscope.org/what-is/seismology/',
    'p_s_materials':'https://pubs.usgs.gov/gip/earthq1/measure.html',
    'rayleigh_polarization':'https://service.earthscope.org/mustang/metrics/docs/1/desc/orientation_check/',
    'love_layered_medium':'https://arxiv.org/abs/2302.08173',
}


def prepare():
    (V5/'sources').mkdir(parents=True,exist_ok=True); records={}
    for key,url in SOURCES.items():
        path=V5/'sources'/f'{key}.html'
        if not path.exists():
            r=requests.get(url,headers=UA,timeout=45);r.raise_for_status();path.write_bytes(r.content)
        records[key]=dict(url=url,file=str(path.relative_to(V5)),sha256=sha256(path.read_bytes()).hexdigest())
    old=V4/'source_audit_v4.json'
    audit=dict(retrieved_utc=datetime.now(timezone.utc).isoformat(),catalog_sha256=HASH,sources=records,
        historical_evidence_file=str(old.relative_to(V5.parent)),historical_evidence_sha256=sha256(old.read_bytes()).hexdigest(),
        claims={'P':'longitudinal; faster than S in the same material; solid/liquid propagation',
                'S':'transverse; vertical or horizontal polarization; solids',
                'Love':'horizontal transverse surface mode; guiding layered medium assumed',
                'Rayleigh':'vertical-radial elliptical motion; ideal retrograde surface ellipse',
                'limits':'No event-specific wave identification from photographs or felt reports. No universal most-damaging wave. Exaggerated schematic motion, not an elastic/damage model.'})
    (V5/'source_audit_v5.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    print(V5.resolve())


if __name__=='__main__':prepare()
