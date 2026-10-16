"""Isolated Chrome, native UI clicks and read-only DOM/state inspection."""
import asyncio,base64,importlib,json,os,subprocess,sys
from pathlib import Path
import psutil
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'dev'),str(ROOT/'tmp'),str(ROOT/'production/video_studio/workspace_checks')]
driver=importlib.import_module('sig-professional-browser')
from studio_v1_opacity import Journey


async def run():
    latest=json.loads((ROOT/'tmp/sig-presentation-review/latest-final.json').read_text(encoding='utf-8'))
    if len(sys.argv)>1:
        folder=Path(sys.argv[1]).resolve()
        latest={'folder':str(folder),'project':str(ROOT/'_local/video-studio/projects'/('andes-pulso-temperatura-septiembre-2026-'+folder.name.removeprefix('final-')+'.json'))}
    out=Path(latest['folder']);used={c.laddr.port for c in psutil.net_connections(kind='tcp') if c.status=='LISTEN'}
    saved=out/'server.json';reuse=False
    if saved.is_file():
        meta=json.loads(saved.read_text(encoding='utf-8'))
        try:
            previous=psutil.Process(meta['pid'])
            reuse=previous.create_time()==meta['created'] and previous.cmdline()==meta['command'] and previous.cwd()==meta['cwd'] and meta['port'] in used
        except psutil.Error:pass
    port=meta['port'] if reuse else next(p for p in range(8534,8550) if p not in used)
    command=[str(ROOT/'_local/video-studio/.venv/Scripts/python.exe'),'-X','utf8','-m','streamlit','run','studio_server.py',
        '--server.port',str(port),'--server.address','127.0.0.1','--server.headless','true','--server.fileWatcherType','none',
        '--server.runOnSave','false','--browser.gatherUsageStats','false']
    env=os.environ.copy();env.pop('ECUADOR_VIVO_DEVELOPMENT_RELOAD',None)
    if not reuse:
        with (out/'server.out.log').open('ab') as log,(out/'server.err.log').open('ab') as err:
            process=subprocess.Popen(command,cwd=ROOT/'production/video_studio',env=env,stdout=log,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
        owned=psutil.Process(process.pid)
        saved.write_text(json.dumps({'pid':owned.pid,'created':owned.create_time(),'command':owned.cmdline(),'cwd':owned.cwd(),'port':port}),encoding='utf-8')
    b=await driver.SigBrowser().start();j=Journey(b,{})
    async def click(expr):
        assert await j.wait('Boolean('+expr+')&&!('+expr+').disabled',55),expr
        point=await j.ev('const r=('+expr+').getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}')
        for kind in ('mouseMoved','mousePressed','mouseReleased'):
            await b.call('Input.dispatchMouseEvent',{'type':kind,'button':'left','buttons':int(kind=='mousePressed'),'clickCount':1,**point})
    async def shot(name):
        image=await b.call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})
        (out/(name+'.png')).write_bytes(base64.b64decode(image['data']))
    report={'url':f'http://127.0.0.1:{port}/','project':latest['project'],'checks':[]}
    try:
        await b.call('Network.enable');await b.size(1920,1080)
        await b.call('Page.navigate',{'url':report['url']})
        ready=False
        for _ in range(220):
            try:ready=await j.ev("return Boolean(document.querySelector('.st-key-home_recent_0 button'))")
            except RuntimeError:pass # First navigation replaces the execution context.
            if ready:break
            await asyncio.sleep(.25)
        assert ready,'Home did not initialize after navigation'
        await click("document.querySelector('.st-key-home_recent_0 button')")
        assert await j.wait("all().some(e=>e.id==='project-name'&&e.value.includes('Septiembre 2026'))",60)
        assert await j.wait("all().some(e=>e.id==='canvas-stage'&&e.querySelector('img.piece')?.complete)",60)
        for w,h in ((1920,1080),(1366,768)):
            await b.size(w,h);await shot('studio-'+str(w))
        await b.size(1920,1080);await click("all().find(e=>e.id==='nav-sig')")
        assert await j.wait("all().some(e=>e.id==='sig-map'&&e.sigAdapter&&e.sigAdapter.displayedIndex===0)",60)
        assert await j.wait("all().some(e=>e.id==='sig-island-inset'&&!e.hidden&&e.querySelector('img')?.complete)",30)
        for w,h in ((1920,1080),(1366,768)):
            await b.size(w,h);await shot('sig-'+str(w))
            report['checks'].append(await j.ev("const a=all().find(e=>e.id==='sig-map').sigAdapter,r=[...a.layers.values()].find(e=>e.record.visible).record;return {viewport:[innerWidth,innerHeight],scrollWidth:document.documentElement.scrollWidth,presentation:r.presentation,palette:r.scale.palette,bbox:r.bbox,date:r.date,interpolation:[...a.layers.values()].find(e=>e.source)?.source.getInterpolate?.(),errors:all().filter(e=>e.getAttribute('data-testid')==='stException').map(e=>e.textContent)}"))
        await b.size(1920,1080);await click("all().find(e=>e.id==='sig-raster-play')")
        assert await j.wait("all().some(e=>e.id==='sig-map'&&e.sigAdapter.displayedIndex>=2)",45)
        await shot('sig-playing')
        report['playback']=await j.ev("const a=all().find(e=>e.id==='sig-map').sigAdapter;return {index:a.displayedIndex,date:all().find(e=>e.id==='sig-raster-calendar').textContent,insetVisible:!all().find(e=>e.id==='sig-island-inset').hidden,notice:a.notice}")
        await click("all().find(e=>e.id==='sig-raster-play')")
        report['console_errors']=[e for e in b.events if e.get('method')=='Runtime.exceptionThrown']
        report['failed_map_responses']=[e['params']['response'] for e in b.events if e.get('method')=='Network.responseReceived' and '/sig-display/' in e['params']['response']['url'] and e['params']['response']['status']!=200]
        assert all(r['scrollWidth']<=r['viewport'][0] and not r['errors'] for r in report['checks'])
        assert not report['console_errors'] and not report['failed_map_responses']
        (out/'browser-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(report,ensure_ascii=False),flush=True)
    except Exception:
        await shot('browser-failure')
        print(await j.ev("return {text:document.body.innerText,errors:all().filter(e=>e.getAttribute('data-testid')==='stException').map(e=>e.textContent)}"),flush=True)
        raise
    finally:
        await b.call('Browser.close');b.ws.close()


if __name__=='__main__':asyncio.run(run())
