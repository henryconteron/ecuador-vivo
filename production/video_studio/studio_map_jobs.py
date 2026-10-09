"""Private cartographic bridge: existing data loader/compositor, no new science."""
import datetime as dt
import os
import math
from pathlib import Path
import subprocess
import sys
import time
import traceback
import uuid

import imageio_ffmpeg

from model import STORE, validate, frame_counts
from jobs import write_json, read_json, sha256
from studio_project import source_projection
from studio_science import restored_snapshot, _hash
from studio_editing import snapshot_revision
from studio_preparation import job_path, preparation_status, verify_sources
from studio_temporal import validate_resource

ROOT = STORE / 'temporal-map-preparations'


def start_map_job(project, duration, *, representation='opaque_prerendered_map', layer_sizes=None,source_index=None):
    if representation not in ('opaque_prerendered_map','rgba_observation_bundle'):
        raise ValueError('Representación cartográfica desconocida.')
    if layer_sizes is not None and (representation!='rgba_observation_bundle' or not isinstance(layer_sizes,dict)
            or set(layer_sizes)-{'continent_size','galapagos_size'}):
        raise ValueError('Resoluciones de capa no admitidas.')
    snapshot = restored_snapshot(project)
    if snapshot is None: raise ValueError('Prepara una revisión científica antes de generar el mapa.')
    if source_index is not None and (representation!='rgba_observation_bundle' or type(source_index) is not int
                                    or not 0<=source_index<len(snapshot['source_records'])):
        raise ValueError('Selecciona una observación existente para el mapa RGBA.')
    source = source_projection(project)
    if source_index is not None and (type(duration) not in (int,float) or not math.isfinite(duration) or not 1/30<=duration<=7200):
        raise ValueError('La observación necesita de uno a 216000 fotogramas a 30 FPS.')
    # Validate the complete scientific source without imposing its full-series
    # playback duration on the explicitly selected observation.
    source['duration'] = duration if source_index is None else max(duration,len(snapshot['source_records'])/30)
    validate(source)
    job = ROOT / uuid.uuid4().hex
    job.mkdir(parents=True)
    request = {'project':project, 'duration':duration}
    if representation=='rgba_observation_bundle': request.update(representation=representation,layer_sizes=layer_sizes or {})
    if source_index is not None:request['source_index']=source_index
    write_json(job/'request.json', request)
    write_json(job/'status.json', {'state':'queued','progress':0,'message':'Mapa temporal en cola','updated':time.time()})
    try:
        with (job/'worker.log').open('w',encoding='utf-8') as log:
            process = subprocess.Popen([sys.executable,str(Path(__file__).resolve()),str(job)],
                stdin=subprocess.DEVNULL,stdout=log,stderr=log,close_fds=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        write_json(job/'process.json', {'pid':process.pid})
    except Exception as error:
        write_json(job/'status.json', {'state':'failed','progress':0,'message':str(error),'updated':time.time()})
        raise
    return job


def map_status(job, *, root=None): return preparation_status(job, root=root or ROOT)


def execute(job, *, root=None):
    job = job_path(job, root or ROOT)
    progress = 0
    writer = None
    def check():
        if (job/'cancel.request').exists(): raise InterruptedError('Mapa cancelado; el proyecto activo se conserva.')
    def status(state, message, **extra):
        write_json(job/'status.json', {'state':state,'message':message,'progress':progress,
                   'updated':time.time(),'pid':os.getpid(),**extra})
    try:
        from data import boundary, load_values
        from render import compose
        from studio_media import import_asset
        check()
        request = read_json(job/'request.json')
        project = request['project']
        if request.get('representation')=='rgba_observation_bundle':
            from studio_map_bundles import prepare_bundle
            sizes = request.get('layer_sizes',{})
            if not isinstance(sizes,dict) or set(sizes)-{'continent_size','galapagos_size'}:
                raise ValueError('Resoluciones de capa no admitidas.')
            def bundle_progress(done,total,message):
                nonlocal progress
                check();progress=.05+.9*done/total;status('running',message)
            status('running','Preparando bundle RGBA privado')
            record=prepare_bundle(project,request['duration'],**sizes,progress=bundle_progress,
                                  cancelled=lambda:(job/'cancel.request').exists(),source_index=request.get('source_index'))
            check();write_json(job/'bundle-resource.json',record);check()
            progress=1
            status('complete','Bundle RGBA privado verificado; aún no publicado',bundle_resource_sha256=_hash(record))
            return
        if request.get('representation','opaque_prerendered_map')!='opaque_prerendered_map':
            raise ValueError('Representación cartográfica desconocida.')
        if 'source_index' in request:raise ValueError('El mapa opaco no admite una selección RGBA.')
        snapshot = restored_snapshot(project)
        if snapshot is None: raise ValueError('Revisión científica ausente.')
        source = source_projection(project)
        source['duration'] = request['duration']
        rows = validate(source)
        counts = frame_counts(len(rows), source['duration'])
        records = snapshot['source_records']
        if len(records) != len(rows) or any(r['date'] != s['date'] or r['band'] != s['band'] for r,s in zip(rows,records)):
            raise ValueError('Las fechas y bandas no coinciden con la revisión científica.')
        status('running','Verificando revisión científica y originales')
        verify_sources(project, snapshot, cancelled=lambda:(job/'cancel.request').exists())
        shape = boundary()
        # Freeze the cartographic source configuration; compose may upgrade its private copy.
        settings = source_projection(source)
        intervals = []
        cursor = 0
        partial = job/'mapa-prerenderizado.mp4'
        for index, (row, record, count) in enumerate(zip(rows, records, counts)):
            check()
            status('running',f'{index+1}/{len(rows)} · componiendo {row["date"]}')
            values, metadata = load_values(source, row)
            if (str(Path(metadata['path']).resolve()) != str(Path(record['file']).resolve())
                    or sha256(metadata['path']) != record['sha256']):
                raise ValueError('Los datos del fotograma no coinciden con la revisión.')
            frame = compose(source, values, shape, row['date'], index, len(rows)).convert('RGB')
            if writer is None:
                resolution = list(frame.size)
                writer = imageio_ffmpeg.write_frames(str(partial), frame.size, fps=30,
                    codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',macro_block_size=1,
                    output_params=['-crf',str(source['crf']),'-preset','fast','-movflags','+faststart'])
                writer.send(None)
                # A single internal thumbnail, never one library entry per date.
                with frame.copy() as thumbnail:
                    thumbnail.thumbnail((240,426)); thumbnail.save(job/'thumbnail.png')
            pixels = frame.tobytes()
            for number in range(count):
                check()
                writer.send(pixels)
                if number % 30 == 0:
                    progress = .05 + .85*(cursor+number+1)/sum(counts)
                    status('running',f'{index+1}/{len(rows)} · {row["date"]}')
            intervals.append({'date':row['date'],'source_index':index,'start_frame':cursor,'end_frame':cursor+count})
            cursor += count
            frame.close()
        writer.close(); writer = None
        check()
        verify_sources(project, snapshot, cancelled=lambda:(job/'cancel.request').exists())
        progress = .95
        status('running','Verificando producto y guardando calendario')
        record = import_asset(partial.read_bytes(), 'Mapa '+source['variable']+' · '+rows[0]['date']+' — '+rows[-1]['date']+'.mp4')
        if record['size'] != resolution or abs(record['duration']-cursor/30) > 1/30:
            raise ValueError('El producto codificado no coincide con el reloj solicitado.')
        record['duration'] = cursor/30
        manifest = {'version':1,'renderer':'render.compose','representation':'opaque_prerendered_map',
            'scientific_revision':snapshot_revision(snapshot),'scientific_identity':snapshot['scientific_identity'],
            'source':source['source'],'citation':source.get('citation',''),'source_url':source.get('source_url'),
            'variable':source['variable'],'units':source['units'],'region':source['bbox'],
            'cartographic_settings':settings,'source_records':records,'intervals':intervals,
            'fps':30,'total_frames':cursor,'duration':cursor/30,'resolution':resolution,
            'generated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'state':'ready',
            'video_sha256':record['sha256'],'temporal_interpolation':False,
            'nodata':{'override':source.get('nodata'),'rule':'existing data.load_values native masks; no imputation'},
            'rules':{'fit':'contain','trim':'integer CFR frames','loop':'repeat selected frames and their dates',
                     'after_end':'hold last frame and date','overlays':'baked into existing compositor',
                     'galapagos':'existing editorial inset; not independently editable'}}
        record['temporal_map'] = manifest
        record['temporal_manifest_sha256'] = _hash(manifest)
        validate_resource(record)
        write_json(job/'resource.json', record)
        check()
        progress = 1
        status('complete','Mapa y calendario listos para insertar',resource_sha256=_hash(record))
    except InterruptedError as error: status('cancelled',str(error))
    except Exception as error:
        traceback.print_exc(); status('failed',f'{type(error).__name__}: {error}')
    finally:
        if writer is not None: writer.close()


def read_resource(job, *, root=None):
    job = job_path(job, root or ROOT)
    state = map_status(job, root=root)
    if state.get('state') != 'complete' or (job/'cancel.request').exists():
        raise ValueError('No hay un mapa completo publicable.')
    path = job/'resource.json'
    if path.stat().st_size > 4_000_000: raise ValueError('Manifiesto superior a 4 MB.')
    record = read_json(path)
    if not isinstance(record,dict) or _hash(record) != state.get('resource_sha256'):
        raise ValueError('El producto cartográfico cambió; vuelve a generarlo.')
    validate_resource(record)
    from studio_media import AssetFrames
    with AssetFrames({'map':record}): pass
    return record


def read_bundle_resource(job, *, root=None):
    """Private v2 product only; AssetFrames/v1 publication remain unchanged."""
    from studio_map_bundles import read_bundle
    job=job_path(job,root or ROOT)
    state=map_status(job,root=root)
    if state.get('state')!='complete' or (job/'cancel.request').exists():
        raise ValueError('No hay un bundle completo publicable.')
    path=job/'bundle-resource.json'
    if not path.is_file() or path.stat().st_size>4_000_000: raise ValueError('Header privado ausente o demasiado grande.')
    record=read_json(path)
    if not isinstance(record,dict) or _hash(record)!=state.get('bundle_resource_sha256'):
        raise ValueError('El header del bundle cambió.')
    read_bundle(record)
    return record


if __name__=='__main__': execute(sys.argv[1])
