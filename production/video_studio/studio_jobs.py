"""Separate free-scene job route. Legacy jobs and validation remain intact."""
import datetime as dt
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
import uuid
import hashlib
import json
import copy
import shutil
from jobs import write_json, read_json
from model import STORE
from studio_timeline import validate_export, export_movie


def _document_hash(project):
    return hashlib.sha256(json.dumps(project,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def _presentation_hash(project):
    value=copy.deepcopy(project)
    # These two canonical authoring fields are not read by the renderer.
    # Scientific revisions, provenance, source hashes and every style stay keyed.
    value.get('project_meta',{}).pop('id',None)
    value.get('project_meta',{}).pop('revision',None)
    if value.get('project_meta')=={}:value.pop('project_meta')
    return _document_hash(value)


def start_studio_job(project):
    validate_export(project)
    # Reopening an identical, validated document may reuse its complete product.
    # No incomplete worker or changed input/receipt/hash is accepted as a cache hit.
    identity=_document_hash(project);presentation=_presentation_hash(project)
    candidates=sorted((STORE/'jobs').glob('studio-*'),key=lambda path:path.stat().st_mtime,reverse=True)[:32]
    for previous in candidates:
        try:
            if read_json(previous/'status.json',{}).get('state')!='complete':continue
            receipt=read_json(previous/'receipt.json',{})
            original=read_json(previous/'request.json',{})
            if receipt.get('project_sha256')!=_document_hash(original) or _presentation_hash(original)!=presentation:continue
            movie=previous/'video.mp4'
            with movie.open('rb') as stream:video_hash=hashlib.file_digest(stream,'sha256').hexdigest()
            if video_hash!=receipt.get('video_sha256'):continue
        except (ValueError,TypeError,OSError):continue
        from studio_media import AssetFrames
        with AssetFrames(project['studio']['media']):pass
        if original==project:return previous
        # A copy/undo has its own document identity: issue a new coherent receipt,
        # explicitly naming the reused product, rather than returning an old receipt.
        cached=STORE/'jobs'/('studio-'+dt.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8])
        cached.mkdir(parents=True)
        write_json(cached/'request.json',project)
        write_json(cached/'status.json',{'state':'queued','progress':0,'message':'Verificando render reutilizable','updated':time.time()})
        try:
            partial=cached/'.video.studio-partial.mp4';shutil.copyfile(movie,partial)
            with partial.open('rb') as stream:
                if hashlib.file_digest(stream,'sha256').hexdigest()!=video_hash:raise ValueError('El render almacenado cambió durante la copia.')
            receipt=copy.deepcopy(receipt);receipt['project_sha256']=identity
            receipt['render_cache']={'source_job':previous.name,'source_project_sha256':_document_hash(original),
                'method':'identical presentation; only canonical document id/revision excluded'}
            write_json(cached/'project.json',project);write_json(cached/'receipt.json',receipt)
            os.replace(partial,cached/'video.mp4')
            write_json(cached/'status.json',{'state':'complete','progress':1,'message':'Render reutilizado · documento y recursos verificados','updated':time.time()})
        except Exception as error:
            write_json(cached/'status.json',{'state':'failed','message':str(error),'updated':time.time()});raise
        return cached
    job=STORE/'jobs'/('studio-'+dt.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8])
    job.mkdir(parents=True)
    write_json(job/'request.json',project)
    write_json(job/'status.json',{'state':'queued','progress':0,'message':'Preparando escenas Studio','updated':time.time()})
    with (job/'worker.log').open('w',encoding='utf-8') as log:
        try:
            subprocess.Popen([sys.executable,str(Path(__file__).resolve()),str(job)],stdin=subprocess.DEVNULL,
                stdout=log,stderr=log,close_fds=True,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        except Exception as error:
            write_json(job/'status.json',{'state':'failed','message':str(error),'updated':time.time()})
            raise
    return job


def execute(job):
    job=Path(job)
    def status(state,message,progress=0):
        write_json(job/'status.json',dict(state=state,message=message,progress=progress,pid=os.getpid(),updated=time.time()))
    try:
        project=read_json(job/'request.json')
        status('running','Componiendo escenas')
        export_movie(project,job/'video.mp4',progress=lambda value:status('running','Componiendo escenas',value),
                     cancelled=lambda:(job/'cancel.request').exists())
        status('complete','Video Studio terminado',1)
    except InterruptedError as error: status('cancelled',str(error))
    except Exception as error:
        traceback.print_exc();status('failed',f'{type(error).__name__}: {error}')


if __name__=='__main__': execute(sys.argv[1])
