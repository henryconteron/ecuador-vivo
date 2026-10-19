"""Export a minimal, explicitly selected public snapshot; never copy credentials or inventories."""
import csv
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '_local/parcelas/parcelas-campo-ecuador/observaciones'
TARGET = ROOT / 'data/casos/parcelas-sentinel'

def main():
    result = SOURCE / 'resultado'
    manifest = json.loads((result / 'huellas.json').read_text(encoding='utf-8'))
    if set(manifest) != {'INFORME.md', 'evidencia.json', 'RF05.png', 'RF06.png'}:
        raise ValueError('Unexpected local report manifest')
    for name, digest in manifest.items():
        if hashlib.sha256((result / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Local report integrity failed')
    evidence = json.loads((result / 'evidencia.json').read_text(encoding='utf-8'))
    plan = json.loads((SOURCE / 'plan.json').read_text(encoding='utf-8'))
    if hashlib.sha256((SOURCE / 'plan.json').read_bytes()).hexdigest() != evidence['plan_sha256']:
        raise ValueError('Plan integrity failed')
    observations = []
    for row in evidence['observations']:
        folder = SOURCE / row['key']
        if folder.parent != SOURCE or folder.name != row['key']:
            raise ValueError('Unsafe source path')
        if hashlib.sha256((folder / 'response.tar').read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Source integrity failed')
        observations.append({key: row[key] for key in ('key', 'plot_id', 'sensor', 'date', 'product', 'sha256', 'lineage_status')})
        observations[-1]['request_sha256'] = hashlib.sha256((folder / 'request.json').read_bytes()).hexdigest()
    snapshot = {
        'title': 'Qué puede ver un satélite en una parcela de media hectárea',
        'published': '2026-10-19', 'author': 'Henry P. Conteron Moreta',
        'status': evidence['status'], 'plan_sha256': evidence['plan_sha256'],
        'study_reference': 'https://zenodo.org/records/6813783',
        'boundary_license': 'ReforesTree, CC BY 4.0; original valid research polygons, not cadastral boundaries',
        'satellite_credit': 'Contains modified Copernicus Sentinel data (2020, 2025)',
        'plots': evidence['plots'], 'observations': observations,
        'processing': {'epsg': 32717, 'context_m': [200, 200], 'optical_step_m': 10,
            'radar_step_m': 20, 'radar_platform': 'Sentinel-1A', 'relative_orbit': 40,
            'direction': 'DESCENDING', 'backscatter': 'GAMMA0_TERRAIN',
            'optical_valid_SCL': [4, 5, 6], 'resampling': 'NEAREST',
            'speckle_filter': 'NONE', 'dem': 'COPERNICUS_30'},
        'limits': ['No observations before 2020 in this experiment',
            'No independent validation of forest loss or conversion date',
            'Two periods are not a continuous time series',
            'Centres and fully contained cells are not independent samples',
            'No EUDR compliance conclusion; no area declared deforested'],
    }
    TARGET.mkdir(parents=True, exist_ok=True)
    (TARGET / 'evidencia-publica.json').write_text(json.dumps(snapshot, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8', newline='\n')
    with (TARGET / 'escenas.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(observations[0]), lineterminator='\n')
        writer.writeheader(); writer.writerows(observations)
    with (TARGET / 'metricas.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['plot_id', 'period', 'sensor', 'support', 'value', 'unit'], lineterminator='\n')
        writer.writeheader()
        for plot in snapshot['plots']:
            writer.writerows({'plot_id': plot['plot_id'], **m} for m in plot['measurements'])
    for name in ('RF05.png', 'RF06.png'):
        shutil.copyfile(result / name, TARGET / name)
    (TARGET / 'INFORME.md').write_text((result / 'INFORME.md').read_text(encoding='utf-8'), encoding='utf-8', newline='\n')
    (TARGET / 'huellas-publicas.json').write_text(json.dumps({p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in TARGET.iterdir() if p.is_file() and p.name != 'huellas-publicas.json'}, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('Public snapshot exported: no credentials, landholder names, raw inventory or videos.')

if __name__ == '__main__':
    main()
