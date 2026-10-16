"""Manage only this continuation's identified 8527 test server."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import psutil

ROOT=Path(__file__).resolve().parents[1]
META=ROOT/'tmp/resume-studio-server-identity.json'
LOG=ROOT/'tmp/resume-studio-processes.json'

if __name__=='__main__':
    prior=json.loads(META.read_text(encoding='utf-8-sig'))
    pid=prior.get('pid',prior.get('ProcessId'))
    owned=psutil.Process(pid)
    created=prior.get('created')
    if created is None:created=int(re.search(r'\d+',prior['CreationDate']).group())/1000
    assert abs(owned.create_time()-created)<.002,'Creation time differs'
    expected=['-X','utf8','-B','-m','streamlit','run','studio_server.py','--server.port','8527',
        '--server.address','127.0.0.1','--server.headless','true','--server.fileWatcherType','none',
        '--server.runOnSave','false','--client.toolbarMode','viewer']
    assert owned.cmdline()[1:]==expected,'Command differs'
    assert Path(owned.cwd()).resolve()==(ROOT/'production/video_studio').resolve(),'Working directory differs'
    children=owned.children(recursive=True)
    for child in children:
        assert child.cmdline()[1:]==expected or (child.name().lower()=='conhost.exe' and child.ppid()==owned.pid),'Unrecognized child'
    children=[child for child in children if child.name().lower()!='conhost.exe']
    record={'closed':[{'pid':p.pid,'created':p.create_time(),'command':p.cmdline()} for p in children+[owned]],
        'reason':sys.argv[1] if len(sys.argv)>1 else 'Load current assets between checks','time':time.time()}
    for p in children+[owned]:p.terminate()
    gone,alive=psutil.wait_procs(children+[owned],timeout=10)
    assert not alive,'Owned server did not exit'
    assert not any(c.status==psutil.CONN_LISTEN and c.laddr.port==8527 for c in psutil.net_connections('tcp'))
    env=os.environ.copy();env.pop('ECUADOR_VIVO_DEVELOPMENT_RELOAD',None)
    with (ROOT/'tmp/resume-studio-server-current.out.log').open('ab') as out, (ROOT/'tmp/resume-studio-server-current.err.log').open('ab') as err:
        process=subprocess.Popen([str(ROOT/'_local/video-studio/.venv/Scripts/python.exe'),*expected],
            cwd=ROOT/'production/video_studio',env=env,stdout=out,stderr=err,
            creationflags=subprocess.CREATE_NO_WINDOW)
    current=psutil.Process(process.pid)
    identity={'pid':current.pid,'created':current.create_time(),'command':current.cmdline(),'cwd':current.cwd(),'port':8527}
    META.write_text(json.dumps(identity,indent=2),encoding='utf8')
    record['started']=identity
    records=json.loads(LOG.read_text()) if LOG.exists() else []
    records.append(record);LOG.write_text(json.dumps(records,indent=2),encoding='utf8')
    print(json.dumps(identity))
