"""Fetch and freeze primary evidence for the revised story; preserve V1–V3."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import requests
from prepare_depth_episode import FOLDER, HASH, load_history, UA

V4 = FOLDER / 'v4'
SOURCES = {
    'bolivia_bulletin': 'https://pubs.usgs.gov/of/1995/0600a/report.pdf',
    'loreto_report': 'https://repositorio.igp.gob.pe/bitstream/20.500.12816/4846/1/Sismo_Lagunas_26_Mayo_2019_Region_Loreto.pdf',
    'loreto_ecuador': 'https://www.igepn.edu.ec/servicios/noticias/1734-informe-sismico-especial-n-12-2019',
    'pelileo': 'https://www.igepn.edu.ec/cayambe/805-terremoto-del-5-de-agosto-de-1949',
    'pedernales_intensity': 'https://www.igepn.edu.ec/1324-informe-sismico-especial-n-18-2016.html',
    'reventador_effects': 'https://www.igepn.edu.ec/cayambe/762-hoy-se-recuerda-el-terremoto-del-reventador-de-1987',
    'depth_science': 'https://www.usgs.gov/programs/earthquake-hazards/determining-depth-earthquake',
    'distance_science': 'https://earthquake.usgs.gov/education/listen/distance.php',
}


def freeze(key, url, suffix):
    path = V4 / 'sources' / (key + suffix)
    if not path.exists():
        response = requests.get(url, headers=UA, timeout=60)
        response.raise_for_status()
        if suffix == '.pdf' and not response.content.startswith(b'%PDF'):
            raise ValueError('Expected PDF, not an error document')
        path.write_bytes(response.content)
    return dict(url=url, file=str(path.relative_to(V4)), sha256=sha256(path.read_bytes()).hexdigest())


def prepare():
    (V4 / 'sources').mkdir(parents=True, exist_ok=True)
    sources = {key: freeze(key, url, '.pdf' if url.endswith('.pdf') else '.html') for key, url in SOURCES.items()}
    cases = {}
    for key, identity in [('bolivia', 'usp0006dzc'), ('pedernales', 'us20005j32'), ('reventador', 'usp000330w')]:
        url = 'https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&eventid=' + identity
        source = freeze(key, url, '.json')
        feature = json.loads((V4 / source['file']).read_bytes())
        p = feature['properties']; lon, lat, depth = feature['geometry']['coordinates']
        cases[key] = dict(id=identity, magnitude=p['mag'], magnitude_type=p['magType'], depth_km=depth,
                          longitude=lon, latitude=lat, provider='USGS', source=source)
    if cases['bolivia']['magnitude'] != 8.2 or abs(cases['bolivia']['depth_km'] - 631.3) > .01:
        raise ValueError('Review changed USGS Bolivia solution before rendering')
    cases['loreto'] = dict(id='IGP-Lagunas-2019', magnitude=8.0, magnitude_type='M (type not specified in parameter table)',
        depth_km=135, longitude=-75.55, latitude=-5.74, provider='IGP, report May 2019 pp. 5, 8',
        source=sources['loreto_report'], alternate_solution_note='USGS us60003sc0 publishes 122.57 km; do not mix solutions')
    cases['pelileo'] = dict(id='IG-EPN-Pelileo-1949', magnitude=6.8,
        magnitude_type='estimated from intensities, not labelled Mw', depth_km=None, depth_upper_exclusive_km=15,
        provider='IG-EPN historical review', source=sources['pelileo'])
    audit = dict(retrieved_utc=datetime.now(timezone.utc).isoformat(), catalog_sha256=HASH,
        opening_records=len(load_history()), additional_cases_outside_original_selection=['bolivia', 'loreto'],
        cases=cases, sources=sources, status='primary evidence; manually verify historical bulletin and report pages')
    (V4 / 'source_audit_v4.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
    print(V4.resolve())


if __name__ == '__main__': prepare()
