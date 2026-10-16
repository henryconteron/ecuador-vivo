"""Focused v1 measurements using the existing native Chrome test driver.

Run from the repository root with the Studio Python environment.
No scientific data preparation, broad suites, or unrelated processes.
"""
import asyncio
import hashlib
import importlib
import json
from pathlib import Path
import sys
import time

import psutil

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'tmp'), str(ROOT/'production/video_studio'),
               str(ROOT/'production/video_studio/workspace_checks')]
driver = importlib.import_module('sig-professional-browser')
from studio2_native_click import native_click

SELECTOR = 'div[data-testid="stElementContainer"][class*="st-key-free_studio_"][class*="_workspace"]'
FIXTURE = ROOT/'_local/video-studio/projects/borrador-studio-demo-fullhd-8escenas.json'
EVIDENCE = ROOT/'tmp/v1-usable-opacity.json'


def identity():
    listeners = {c.laddr.port:c.pid for c in psutil.net_connections(kind='tcp')
                 if c.status == 'LISTEN' and 8510 <= c.laddr.port <= 8527}
    process = psutil.Process(listeners[8527])
    assert '--server.fileWatcherType' in process.cmdline()
    assert 'ECUADOR_VIVO_DEVELOPMENT_RELOAD' not in process.environ()
    return {'listeners':listeners, 'pid':process.pid, 'created':process.create_time(),
            'command':process.cmdline(), 'cwd':process.cwd(),
            'fixture_sha256':hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            'app_sha256':hashlib.sha256((ROOT/'production/video_studio/app.py').read_bytes()).hexdigest()}


async def run():
    before = identity()
    b = await driver.SigBrowser().start()
    clicks = []
    report = {'status':'RUNNING', 'server_before':before, 'selector':SELECTOR,
              'css_file':'production/video_studio/workspace_frontend/host.css',
              'driver':'existing tmp/sig-professional-browser.py / SigBrowser',
              'server_restarts_during_measurement':0, 'steps':[]}

    def elem(ident):
        return 'all().find(e=>e.id==='+json.dumps(ident)+')'

    async def ev(code):
        return await b.evaluate(code)

    async def click(expr):
        await b.wait('Boolean('+expr+') && !('+expr+').disabled', 30)
        await native_click(b, expr, clicks, wait_saved=False)

    async def phase(name):
        await ev('window.v1Measure.phase='+json.dumps(name)+';return true')
        print('PHASE '+name, flush=True)

    async def set_name(value):
        previous = (await state())['version']
        await click(elem('project-name'))
        for kind in ('keyDown','keyUp'):
            await b.call('Input.dispatchKeyEvent',{'type':kind,'key':'a','code':'KeyA','modifiers':2,'windowsVirtualKeyCode':65})
        await b.call('Input.insertText',{'text':value})
        for kind in ('keyDown','keyUp'):
            await b.call('Input.dispatchKeyEvent',{'type':kind,'key':'Tab','code':'Tab'})
        await b.wait('JSON.parse(all().find(e=>e.id==="canvas-stage").getRootNode().__evsSignature)[7].name==='+json.dumps(value),45)
        return await committed(previous)

    async def state():
        return await ev("const root=all().find(e=>e.id==='canvas-stage').getRootNode();const p=JSON.parse(root.__evsSignature);return {version:p[1],scene:p[2],frame:p[3],project:p[7],error:p[8],save:root.querySelector('#save-state').dataset.state,mode:root.querySelector('#canvas-mode').textContent,date:root.querySelector('#scientific-date').textContent}")

    async def committed(previous):
        await b.wait("all().some(e=>e.classList.contains('evs')&&+e.dataset.version>"+str(previous)+") && all().some(e=>e.id==='save-state'&&e.dataset.state==='saved')", 45)
        result = await state()
        assert not result['error'], result
        return result

    async def drag(expr,dx,dy):
        point = await ev('const r='+expr+'.getBoundingClientRect();return {x:r.x+r.width*.4,y:r.y+r.height*.4}')
        await b.call('Input.dispatchMouseEvent', {'type':'mousePressed','button':'left','buttons':1,'clickCount':1,**point})
        for i in range(1,9):
            await b.call('Input.dispatchMouseEvent', {'type':'mouseMoved','button':'left','buttons':1,
                'x':point['x']+dx*i/8,'y':point['y']+dy*i/8})
        await b.call('Input.dispatchMouseEvent', {'type':'mouseReleased','button':'left','buttons':0,'clickCount':1,
            'x':point['x']+dx,'y':point['y']+dy})

    try:
        await b.size(1920,1080)
        await b.call('Page.navigate', {'url':'http://127.0.0.1:8527'})
        await click("document.querySelector('.st-key-home_open_panel summary')")
        await click("document.querySelector('.st-key-home_saved button[aria-haspopup=listbox]')")
        await click("all().find(e=>e.getAttribute('role')==='option'&&e.textContent.trim()==='borrador-studio-demo-fullhd-8escenas')")
        await click("document.querySelector('.st-key-home_open button')")
        await b.wait("all().some(e=>e.id==='canvas-stage'&&e.querySelector('img.piece')?.complete)",45)
        host = await ev('const e=document.querySelector('+json.dumps(SELECTOR)+');return {cls:e?.className,opacity:e?getComputedStyle(e).opacity:null,transition:e?getComputedStyle(e).transition:null,matches:document.querySelectorAll('+json.dumps(SELECTOR)+').length}')
        assert host['matches'] == 1 and host['opacity'] == '1' and host['transition'].startswith('none'), host
        report['host'] = host
        initial = await state()
        assert len(initial['project']['studio']['timeline']) == 8 and initial['version'] == 0
        await ev("""window.v1Measure={phase:'autoguardado',samples:[],stopped:false};
        function sample(){const m=window.v1Measure;if(m.stopped)return;const nodes=all();const stage=nodes.find(e=>e.id==='canvas-stage');const board=stage?.querySelector('.board');const movie=nodes.find(e=>e.id==='movie');const mode=nodes.find(e=>e.id==='canvas-mode')?.textContent;
        const playing=mode?.startsWith('PREVIEW');const target=playing?movie:board;
        const maps=[...(board?.querySelectorAll('img.piece')||[])].filter(e=>e.alt.startsWith('Región SIG'));
        const ready=maps.filter(e=>e.complete&&e.naturalWidth>0).length;
        let opacity=1,n=target;const ancestors=[];for(let i=0;i<40&&n;i++){const o=Number(getComputedStyle(n).opacity);opacity*=o;ancestors.push({tag:n.tagName,cls:String(n.className),opacity:o,stale:n.getAttribute('data-stale')});n=n.parentElement||n.getRootNode()?.host}
        m.samples.push({t:performance.now(),phase:m.phase,mode,opacity,ready,stale:ancestors.some(a=>a.stale==='true'),staleElsewhere:document.querySelectorAll('[data-stale="true"]').length,videoReady:playing?movie?.readyState:null,date:nodes.find(e=>e.id==='scientific-date')?.textContent,ancestors});
        requestAnimationFrame(sample)}requestAnimationFrame(sample);return true""")
        # A real property change, acknowledged by a document version increment.
        name = initial['project']['name']
        saved = await set_name(name+' · medición v1')
        report['steps'].append({'phase':'autoguardado','version':saved['version']})
        await phase('arrastre')
        await click("all().find(e=>e.tagName==='BUTTON'&&e.closest('.layer-row')&&e.textContent.startsWith('Región SIG'))")
        await drag(elem('canvas-stage')+'.querySelector(\'.piece[alt^="Región SIG"]\')',16,8)
        moved = await committed(saved['version'])
        report['steps'].append({'phase':'arrastre','version':moved['version']})
        # Restore the fixture presentation before using its verified cached MP4.
        await click(elem('undo')); reverted = await committed(moved['version'])
        restored = await set_name(name)
        assert restored['project'] == initial['project']
        await phase('cambio_escena')
        scene = restored['scene']
        await click(elem('scenes')+'.children[1]')
        await b.wait("all().some(e=>e.classList.contains('evs')&&e.dataset.scene!=="+json.dumps(scene)+")",45)
        await click(elem('scenes')+'.children[0]')
        await b.wait("all().some(e=>e.classList.contains('evs')&&e.dataset.scene==="+json.dumps(scene)+")",45)
        report['steps'].append({'phase':'cambio_escena','scene':scene})
        await phase('reproduccion')
        await click(elem('play'))
        await b.wait("all().some(e=>e.id==='movie'&&e.readyState>=2&&!e.paused&&e.currentTime>1)",90)
        await b.wait("all().some(e=>e.id==='movie'&&e.currentTime>4)",45)
        report['steps'].append({'phase':'reproduccion','state':await state()})
        await phase('retorno_preview')
        await click(elem('back-edit'))
        await b.wait("all().some(e=>e.id==='canvas-mode'&&e.textContent==='EDICIÓN')",30)
        report['steps'].append({'phase':'retorno_preview','state':await state()})
        # Wait on the actual sample count, never use a timed sleep as a pass signal.
        await b.wait('window.v1Measure.samples.length>=4100',120)
        samples = await ev('window.v1Measure.stopped=true;return window.v1Measure.samples')
        report['samples'] = samples
        report['summary'] = {'samples':len(samples),'minimum':min(s['opacity'] for s in samples),
            'below_099':sum(s['opacity']<.99 for s in samples),'without_decoded_map':sum(s['ready']==0 for s in samples),
            'phases':{phase:sum(s['phase']==phase for s in samples) for phase in sorted({s['phase'] for s in samples})}}
        stale = [s for s in samples if s['stale']]
        report['summary']['stale_samples'] = len(stale)
        report['summary']['stale_effective_opacity_minimum'] = min((s['opacity'] for s in stale),default=None)
        report['summary']['stale_effective_opacity_maximum'] = max((s['opacity'] for s in stale),default=None)
        report['summary']['stale_by_phase'] = {phase:sum(s['phase']==phase for s in stale) for phase in report['summary']['phases']}
        report['other_containers'] = await ev('return [...document.querySelectorAll("div[data-testid=stElementContainer]")].filter(e=>!e.matches('+json.dumps(SELECTOR)+')).map(e=>({cls:e.className,opacity:getComputedStyle(e).opacity,transition:getComputedStyle(e).transition,matches:e.matches('+json.dumps(SELECTOR)+')}))')
        report['server_after'] = identity()
        assert report['server_after'] == before, 'Server, other listeners, fixture or source changed during measurement'
        assert len(samples)>=4000 and report['summary']['minimum']>=.99 and report['summary']['without_decoded_map']==0, report['summary']
        assert stale, 'No samples with data-stale=true on the rendered map ancestry; measurement invalid'
        assert all(report['summary']['phases'].values())
        assert all(not c['matches'] for c in report['other_containers'])
        report['status']='PASS'
        await b.shot('v1-usable-opacity.png')
    except Exception as error:
        report['status']='FAIL';report['error']=repr(error)
        try:
            report['partial_samples']=await ev('if(window.v1Measure){window.v1Measure.stopped=true;return window.v1Measure.samples}return []')
            partial=report['partial_samples']
            stale=[s for s in partial if s.get('stale')]
            report['partial_summary']={'samples':len(partial),'minimum':min((s['opacity'] for s in partial),default=None),'stale_samples':len(stale),'stale_minimum':min((s['opacity'] for s in stale),default=None),'phases':{p:sum(s['phase']==p for s in partial) for p in sorted({s['phase'] for s in partial})}}
            report['failure_state']=await state()
            await b.shot('v1-usable-opacity-failure.png')
        except Exception as inspection_error:
            report['inspection_error']=repr(inspection_error)
        raise
    finally:
        report['clicks']=clicks
        EVIDENCE.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({k:v for k,v in report.items() if k in ('status','error','summary','host')},ensure_ascii=False),flush=True)
        await b.call('Browser.close')
        b.ws.close()


if __name__ == '__main__':
    from studio_v1_opacity import run as measure_opacity
    asyncio.run(measure_opacity())
