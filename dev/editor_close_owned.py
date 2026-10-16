"""Close only the recorded test process identities; preserve user listeners."""
import json
from pathlib import Path
import psutil

ROOT=Path(__file__).resolve().parents[1]
def listeners():
    return {str(c.laddr.port):c.pid for c in psutil.net_connections(kind='tcp')
            if c.status==psutil.CONN_LISTEN and 8510<=c.laddr.port<=8527}
before=listeners()
report={'before':before,'closed':[]}
for filename,kind in [('editor-browser.json','chrome'),('editor-server-studio.json','server')]:
    meta=json.loads((ROOT/'tmp'/filename).read_text(encoding='utf8'))
    p=psutil.Process(meta['pid'])
    assert p.create_time()==meta['created'], 'PID identity changed'
    assert p.cmdline()==meta['command'], 'Command identity changed'
    if kind=='server':
        assert before.get('8527')==p.pid
        assert Path(p.cwd()).resolve()==Path(meta['cwd']).resolve()
        assert Path(p.cwd()).resolve()==ROOT/'production/video_studio'
    else:
        assert '--remote-debugging-port=9236' in p.cmdline()
        assert '--user-data-dir='+str(ROOT/'tmp/sig-studio-chrome-fcbd0ce8') in p.cmdline()
    children=[(c,c.create_time()) for c in p.children(recursive=True)] if kind=='chrome' else []
    p.terminate()
    p.wait(15)
    for child,created in children:
        try:
            if child.create_time()==created and child.is_running():
                child.terminate();child.wait(10)
        except psutil.NoSuchProcess:pass
    report['closed'].append({'kind':kind,'pid':meta['pid'],'command':meta['command'],
                             'created':meta['created'],'cwd':meta.get('cwd'),
                             'verified_closed':not psutil.pid_exists(meta['pid'])})
report['after']=listeners()
report['user_ports_unchanged']={k:v for k,v in before.items() if k!='8527'}==report['after']
(ROOT/'tmp/editor-closure-processes.json').write_text(json.dumps(report,indent=2),encoding='utf8')
assert report['user_ports_unchanged'], 'User listener inventory changed'
print(json.dumps(report,indent=2))
