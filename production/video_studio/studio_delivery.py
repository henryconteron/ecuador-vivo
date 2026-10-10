"""Bounded, expiring capability URLs for complete worker products only.

Public Starlette FileResponse supports byte ranges. No private Streamlit API.
https://www.starlette.io/responses/#fileresponse
"""
from collections import OrderedDict
from pathlib import Path
import threading
import time
import uuid
import copy
import hashlib
import json
import io
from starlette.responses import FileResponse, Response
from model import STORE

_files=OrderedDict();_lock=threading.Lock()
_rasters=OrderedDict()
_jobs=OrderedDict()
TTL=3600


def register_job_status(job):
    job=Path(job).resolve();root=(STORE/'jobs').resolve()
    if job.parent!=root or not job.name.startswith('studio-') or not (job/'request.json').is_file():raise ValueError('Trabajo de Studio desconocido.')
    with _lock:
        now=time.monotonic()
        for token,(existing,expires) in list(_jobs.items()):
            if expires<=now:_jobs.pop(token)
            elif existing==job:
                _jobs[token]=(job,now+TTL);return '/studio-status/'+token
        while len(_jobs)>=64:_jobs.popitem(last=False)
        token=uuid.uuid4().hex;_jobs[token]=(job,now+TTL);return '/studio-status/'+token


async def job_response(request):
    from jobs import read_json
    from starlette.responses import JSONResponse
    with _lock:
        record=_jobs.get(request.path_params.get('token',''))
        if not record or record[1]<=time.monotonic():return Response(status_code=404)
        job=record[0]
    status=read_json(job/'status.json',{})
    result={'job':status}
    if status.get('state')=='complete':
        try:result.update(movie_url=register_movie(job),receipt=read_json(job/'receipt.json'))
        except (ValueError,OSError):return Response('Producto incompleto.',status_code=409)
    return JSONResponse(result,headers={'Cache-Control':'private, no-store'})


def register_raster_display(source,scale):
    """Expiring presentation capability, not another source or time registry."""
    identity=hashlib.sha256(json.dumps([source,scale],sort_keys=True,allow_nan=False).encode()).hexdigest()
    with _lock:
        now=time.monotonic()
        for token,record in list(_rasters.items()):
            if record['expires']<=now:_rasters.pop(token)
            elif record['identity']==identity:
                record['expires']=now+TTL;return '/sig-display/'+token
        while len(_rasters)>=128:_rasters.popitem(last=False)
        token=uuid.uuid4().hex
        _rasters[token]={'identity':identity,'source':copy.deepcopy(source),'scale':copy.deepcopy(scale),'expires':now+TTL}
        return '/sig-display/'+token


async def raster_response(request):
    from starlette.concurrency import run_in_threadpool
    with _lock:
        record=_rasters.get(request.path_params.get('token',''))
        if not record or record['expires']<=time.monotonic():return Response(status_code=404)
        source,scale=record['source'],record['scale']
    def render():
        from studio_sig_raster import representation
        # Authorisation and content hash are checked on every request, including
        # warm render-cache hits. Native values/NoData remain in the original.
        image,_=representation(source,scale)
        try:
            buffer=io.BytesIO();image.save(buffer,format='PNG');return buffer.getvalue()
        finally:image.close()
    try:content=await run_in_threadpool(render)
    except (ValueError,TypeError,KeyError,OSError):return Response('La fuente cambió o no está autorizada. Vuelve a verificar la capa.',status_code=409)
    return Response(content,media_type='image/png',headers={'Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff',
        'X-Ecuador-Observation-Date':source.get('date') or '', 'X-Ecuador-Source-SHA256':source['sha256']})

def register_movie(job):
    job=Path(job).resolve();root=(STORE/'jobs').resolve()
    if job.parent!=root or not job.name.startswith('studio-'):raise ValueError('Producto fuera de jobs Studio.')
    path=job/'video.mp4'
    if not path.is_file() or not (job/'receipt.json').is_file():raise ValueError('Producto incompleto.')
    with _lock:
        now=time.monotonic()
        for token,(existing,expiry) in list(_files.items()):
            if expiry<=now:_files.pop(token)
            elif existing==path:
                _files[token]=(path,now+TTL);return '/studio-media/'+token
        while len(_files)>=64:_files.popitem(last=False)
        token=uuid.uuid4().hex;_files[token]=(path,now+TTL)
        return '/studio-media/'+token

async def movie_response(request):
    token=request.path_params.get('token','')
    with _lock:
        record=_files.get(token)
        if not record or record[1]<=time.monotonic():
            _files.pop(token,None);return Response(status_code=404)
        path=record[0]
    if not path.is_file():return Response(status_code=404)
    return FileResponse(path,media_type='video/mp4',filename='ecuador-vivo.mp4',
        content_disposition_type='attachment' if request.query_params.get('download') else 'inline',
        headers={'Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff'})
