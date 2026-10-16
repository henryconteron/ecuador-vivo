"""Isolated local visual review; never touches the user's browser or servers."""
import asyncio
import base64
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import psutil

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tmp/editorial-design-20261011'
sys.path[:0]=[str(ROOT/'dev'),str(ROOT/'tmp'),str(ROOT/'production/video_studio/workspace_checks')]
from studio_v1_opacity import Journey
driver=importlib.import_module('sig-professional-browser')


async def run():
    port=8532
    used={c.laddr.port for c in psutil.net_connections(kind='tcp') if c.status=='LISTEN'}
    if '--restart' in sys.argv and port in used:
        meta=json.loads((OUT/'server.json').read_text(encoding='utf-8'))
        owned=psutil.Process(meta['pid'])
        assert owned.create_time()==meta['created'] and owned.cmdline()==meta['command'] and owned.cwd()==meta['cwd']
        owned.terminate();owned.wait(12);used.remove(port)
    if port not in used:
        command=[str(ROOT/'_local/video-studio/.venv/Scripts/python.exe'),'-X','utf8','-m','streamlit','run','studio_server.py',
            '--server.port',str(port),'--server.address','127.0.0.1','--server.headless','true','--server.fileWatcherType','none',
            '--server.runOnSave','false','--browser.gatherUsageStats','false']
        env=os.environ.copy();env.pop('ECUADOR_VIVO_DEVELOPMENT_RELOAD',None)
        with (OUT/'server.out.log').open('ab') as out,(OUT/'server.err.log').open('ab') as err:
            process=subprocess.Popen(command,cwd=ROOT/'production/video_studio',env=env,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
        p=psutil.Process(process.pid)
        (OUT/'server.json').write_text(json.dumps({'pid':p.pid,'created':p.create_time(),'command':p.cmdline(),'cwd':p.cwd(),'port':port},indent=2),encoding='utf-8')
    b=await driver.SigBrowser().start();j=Journey(b,{})
    async def shot(name):
        result=await b.call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})
        (OUT/(name+'.png')).write_bytes(base64.b64decode(result['data']))
    report=[]
    try:
        await b.call('Page.navigate',{'url':f'http://127.0.0.1:{port}'})
        ready=False
        for _ in range(220):
            try:ready=await j.ev("return document.querySelector('.st-key-home_recent_0 button')!==null")
            except RuntimeError:ready=False  # Initial navigation replaces the JS context.
            if ready:break
            await asyncio.sleep(.25)
        assert ready,'Home did not finish initial navigation'
        for w,h in ((1920,1080),(1366,768)):
            await b.size(w,h);await shot('inicio-'+str(w))
        await j.click("document.querySelector('.st-key-home_recent_0 button')")
        assert await j.wait("all().some(e=>e.id==='canvas-stage'&&e.querySelector('img.piece')?.complete)",55)
        assert await j.wait("all().some(e=>e.id==='project-name'&&e.value.includes('diseño editorial'))",10)
        for w,h in ((1920,1080),(1366,768)):
            await b.size(w,h);await shot('studio-mapa-'+str(w))
            report.append(await j.ev("const e=all().find(e=>e.id==='canvas-stage'),r=e.getBoundingClientRect();return {viewport:[innerWidth,innerHeight],scrollWidth:document.documentElement.scrollWidth,canvas:{x:r.x,y:r.y,width:r.width,height:r.height},errors:all().filter(e=>e.getAttribute('data-testid')==='stException').map(e=>e.textContent)}"))
        await b.size(1920,1080)
        await j.click("all().find(e=>e.id==='scenes').querySelectorAll('button')[1]")
        assert await j.wait("all().some(e=>e.id==='scene-label'&&e.textContent.includes('Métricas'))",35)
        assert await j.wait("all().some(e=>e.id==='workspace-status'&&e.textContent.includes('actualizada'))",55)
        await shot('studio-metricas-1920')
        await j.click("all().find(e=>e.id==='nav-sig')")
        if not await j.wait("all().some(e=>e.id==='sig-map'&&e.sigAdapter)",45):
            await shot('sig-error')
            print(await j.ev('return {text:document.body.innerText,errors:all().filter(e=>e.getAttribute("data-testid")==="stException").map(e=>e.textContent)}'))
            raise RuntimeError('SIG did not initialize')
        await shot('sig-1920')
        report.append(await j.ev("const e=all().find(e=>e.id==='sig-map');return {sig:e.sigAdapter.version,errors:all().filter(e=>e.getAttribute('data-testid')==='stException').map(e=>e.textContent)}"))
        print(json.dumps(report,ensure_ascii=False))
        (OUT/'browser-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    finally:
        await b.call('Browser.close');b.ws.close()


if __name__=='__main__':asyncio.run(run())
