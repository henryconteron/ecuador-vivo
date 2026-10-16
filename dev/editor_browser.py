"""Native CDP test session, owned profile/process; no personal browser surfaces."""
import asyncio
import base64
import importlib
import json
from pathlib import Path
import psutil
import sys
import urllib.request
from tornado.websocket import websocket_connect

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'dev'),str(ROOT/'tmp'),str(ROOT/'production/video_studio/workspace_checks')]
from studio_v1_opacity import Journey
driver=importlib.import_module('sig-professional-browser')
META=ROOT/'tmp/editor-browser.json'

async def run():
    if '--start' in sys.argv:
        b=await driver.SigBrowser().start();p=psutil.Process(b.process.pid)
        port=next(int(a.split('=')[1]) for a in p.cmdline() if a.startswith('--remote-debugging-port='))
        meta={'pid':p.pid,'created':p.create_time(),'command':p.cmdline(),'port':port}
        META.write_text(json.dumps(meta,indent=2),encoding='utf8')
        await b.call('Page.navigate',{'url':'http://127.0.0.1:8527'})
    else:
        meta=json.loads(META.read_text(encoding='utf8'));p=psutil.Process(meta['pid'])
        assert p.create_time()==meta['created'] and p.cmdline()==meta['command']
        tabs=json.load(urllib.request.urlopen('http://127.0.0.1:'+str(meta['port'])+'/json'))
        b=driver.SigBrowser();b.ws=await websocket_connect(next(t['webSocketDebuggerUrl'] for t in tabs if t['type']=='page'));b.n=0;b.events=[]
    j=Journey(b,{})
    task=next((ROOT/a for a in sys.argv[1:] if a.endswith('.py')),None)
    if task:
        namespace={'ROOT':ROOT,'json':json,'asyncio':asyncio};exec(compile(task.read_text(encoding='utf8'),str(task),'exec'),namespace)
        await namespace['task'](b,j)
    else:
        if '--start' in sys.argv:await j.wait("document.querySelector('.st-key-home_help_panel summary')!==null")
        result=await j.ev("return {text:document.body.innerText.slice(-5000),errors:all().filter(e=>e.getAttribute('data-testid')==='stException').map(e=>e.textContent)}")
        print(json.dumps(result,ensure_ascii=False),flush=True)
    if '--close' in sys.argv:
        assert p.create_time()==meta['created'] and p.cmdline()==meta['command']
        p.terminate();p.wait(15);meta['closed']=True;META.write_text(json.dumps(meta,indent=2),encoding='utf8');print('Chrome cerrado PID '+str(meta['pid']))
    b.ws.close()

if __name__=='__main__':asyncio.run(run())
