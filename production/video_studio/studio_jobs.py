"""Separate free-scene job route. Legacy jobs and validation remain intact."""
import datetime as dt
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
import uuid
from jobs import write_json, read_json
from model import STORE
from studio_timeline import validate_export, export_movie


def start_studio_job(project):
    validate_export(project)
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
