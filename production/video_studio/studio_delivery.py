"""Bounded, expiring capability URLs for complete worker products only.

Public Starlette FileResponse supports byte ranges. No private Streamlit API.
https://www.starlette.io/responses/#fileresponse
"""
from collections import OrderedDict
from pathlib import Path
import threading
import time
import uuid
from starlette.responses import FileResponse, Response
from model import STORE

_files=OrderedDict();_lock=threading.Lock()
TTL=3600

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
