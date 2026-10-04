"""Verify profiles and primary scientific sources without altering the published snapshot."""
from datetime import datetime, timezone
from hashlib import sha256
import json

from prepare_depth_episode import FOLDER, HASH, CASE_IDS, load_history, request

SOURCES={
    'depth_significance':'https://www.usgs.gov/faqs/what-depth-do-earthquakes-occur-what-significance-depth?items_per_page=6&page=1',
    'depth_classes':'https://www.usgs.gov/programs/earthquake-hazards/determining-depth-earthquake',
    'distance':'https://earthquake.usgs.gov/education/listen/distance.php',
    'coast':'https://www.igepn.edu.ec/1324-informe-sismico-especial-n-18-2016.html',
    'amazon':'https://www.igepn.edu.ec/cayambe/762-hoy-se-recuerda-el-terremoto-del-reventador-de-1987',
}


def audit():
    rows=load_history(); known=[r for r in rows if r['depth_km'] is not None]
    sources={}
    for key,url in SOURCES.items():
        response=request(url)
        path=FOLDER/f'source_v2_{key}.html'; path.write_bytes(response.content)
        sources[key]=dict(url=response.url,file=path.name,sha256=sha256(response.content).hexdigest())
    cases=[]
    for identity in CASE_IDS:
        row=next(r for r in rows if r['id']==identity)
        response=request('https://earthquake.usgs.gov/fdsnws/event/1/query',params={'format':'geojson','eventid':identity})
        raw=response.json()
        if raw['geometry']['coordinates']!=[row['longitude'],row['latitude'],row['depth_km']] or (raw['properties']['mag'],raw['properties']['magType'])!=(row['magnitude'],row['magnitude_type']):
            raise ValueError(f'Case revised by USGS: {identity}. Stop and reconcile sources.')
        path=FOLDER/f'{identity}_verified_v2.geojson'; path.write_bytes(response.content)
        cases.append(dict(id=identity,url=response.url,file=path.name,sha256=sha256(response.content).hexdigest()))
    result=dict(checked_at_utc=datetime.now(timezone.utc).isoformat(),catalog_sha256=HASH,
                regional_records=len(rows),profile_records=len(known),unknown_depth_count=len(rows)-len(known),
                maximum_selected_depth_km=max(r['depth_km'] for r in known),
                selected_deep_events=sum(r['depth_km']>=300 for r in known),sources=sources,cases=cases,
                hypothetical_depths_km=[500,150,10],hypothetical_epicentral_distance_km=40,
                scientific_limits=['Profiles are coordinate projections of all known-depth records, not geological slices.',
                                   'The 500 km example is hypothetical and absent from this selected catalog.',
                                   'Shared spatial scale, no intensity or damage prediction; wave motion has no physical time scale.',
                                   'Real cases differ in multiple variables and do not isolate depth.'])
    (FOLDER/'source_audit_v2.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=True,indent=2))


if __name__=='__main__':audit()
