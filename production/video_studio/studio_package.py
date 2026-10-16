"""Local editorial handoff from a completed Studio product; no publication."""
import csv,hashlib,io,json,os,zipfile
from pathlib import Path


def prepare_package(job,project):
    transfer=project.get('studio',{}).get('sig_transfer')
    if not transfer or not set(transfer.get('scene_ids',[])).intersection(project['studio'].get('timeline',[])):return None
    job=Path(job);target=job/'andes-pulso.zip'
    if target.exists():return target
    snapshot=project['studio']['datasets'][transfer['science_dataset']]
    receipt=json.loads((job/'receipt.json').read_text(encoding='utf-8'))
    with (job/'video.mp4').open('rb') as stream:
        if hashlib.file_digest(stream,'sha256').hexdigest()!=receipt['video_sha256']:
            raise ValueError('El video cambió antes de preparar el paquete local.')
    def encoded(value):return json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)
    def table(rows,fields):
        stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore')
        writer.writeheader();writer.writerows(rows);return stream.getvalue()
    partial=job/'.andes-pulso.partial.zip'
    try:
        with zipfile.ZipFile(partial,'x',compression=zipfile.ZIP_DEFLATED) as archive:
            for name in ('video.mp4','project.json','receipt.json'):archive.write(job/name,name)
            archive.writestr('resultados.json',encoded(snapshot))
            archive.writestr('provincias.csv',table(snapshot['summary']['province_rank'],['name','value','days','coverage','spatial_coverage','observed_subtotal']))
            archive.writestr('medias-diarias.csv',table(snapshot['method']['daily'],['date','mean','maximum','coverage','galapagos_available']))
            archive.writestr('metodos-y-cobertura.json',encoded({k:v for k,v in snapshot['method'].items() if k!='daily'}))
            archive.writestr('fuentes.json',encoded(snapshot['source_records']))
            archive.writestr('LEEME.txt','Paquete local Andes Pulso. No publicado.\n'
                'project.json conserva elementos editables, cálculos y referencias locales selladas.\n'
                'Reabrir en este entorno con los originales y bundles referenciados; el ZIP no duplica los rásteres.\n'
                'CSV: valores vacíos significan ausencia, nunca cero. Unidades y método en resultados.json.\n'
                'Suma de medias diarias no es volumen nacional ni máximo acumulado de celda.\n'
                'Suavizado exclusivamente visual; resolución original conservada.\n')
        os.replace(partial,target)
    finally:partial.unlink(missing_ok=True)
    return target
