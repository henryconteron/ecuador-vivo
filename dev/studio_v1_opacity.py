"""Five-phase opacity measurement; findings never interrupt later phases."""
import asyncio
import hashlib
import importlib
import json
from pathlib import Path
import sys
import time
import psutil

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tmp'),str(ROOT/'production/video_studio'),str(ROOT/'production/video_studio/workspace_checks')]
driver=importlib.import_module('sig-professional-browser')
SELECTOR='div[data-testid="stElementContainer"][class*="st-key-free_studio_"][class*="_workspace"]'
PHASES=['autoguardado','arrastre','cambio_escena','reproduccion','retorno_preview']

class Journey:
    def __init__(self,b,report):self.b=b;self.report=report
    async def ev(self,js):return await self.b.evaluate(js)
    def elem(self,id):return 'all().find(e=>e.id==='+json.dumps(id)+')'
    async def wait(self,expr,seconds=35):
        # Wait for observed state on animation frames; no fixed sleeps.
        return await self.ev('return new Promise(resolve=>{const end=performance.now()+'+str(seconds*1000)+';function check(){try{if('+expr+'){resolve(true);return}}catch{}if(performance.now()>end){resolve(false);return}requestAnimationFrame(check)}check()})')
    async def click(self,expr):
        if not await self.wait('Boolean('+expr+') && !('+expr+').disabled'):
            raise RuntimeError('Unavailable native click: '+expr)
        point=await self.ev('const e='+expr+';e.scrollIntoView({block:"nearest"});const r=e.getBoundingClientRect();let hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);while(hit?.shadowRoot){const n=hit.shadowRoot.elementFromPoint(r.x+r.width/2,r.y+r.height/2);if(!n||n===hit)break;hit=n}return {x:r.x+r.width/2,y:r.y+r.height/2,correct:hit===e||e.contains(hit)}')
        if not point['correct']:raise RuntimeError('Native target obscured: '+expr)
        for kind in ('mouseMoved','mousePressed','mouseReleased'):
            await self.b.call('Input.dispatchMouseEvent',{'type':kind,'button':'left','buttons':int(kind=='mousePressed'),'clickCount':1,'x':point['x'],'y':point['y']})
    async def key(self,key,code=None,modifiers=0,vk=None):
        for kind in ('rawKeyDown','keyUp'):
            args={'type':kind,'key':key,'code':code or key,'modifiers':modifiers}
            if vk:args['windowsVirtualKeyCode']=vk
            await self.b.call('Input.dispatchKeyEvent',args)
    async def state(self):
        return await self.ev("const stage=all().find(e=>e.id==='canvas-stage');if(!stage)return null;const r=stage.getRootNode(),s=JSON.parse(r.__evsSignature);return {version:s[1],scene:s[2],frame:s[3],project:s[7],error:s[8],name:r.querySelector('#project-name').value,save:r.querySelector('#save-state').dataset.state,date:r.querySelector('#scientific-date').textContent,mode:r.querySelector('#canvas-mode').textContent}")
    async def settled(self,version):
        return await self.wait('all().some(e=>e.classList.contains("evs")&&+e.dataset.version>'+str(version)+')&&all().some(e=>e.id==="save-state"&&e.dataset.state==="saved")',45)
    async def phase(self,name):
        print('PHASE '+name,flush=True)
        await self.ev('window.v1Measure.phase='+json.dumps(name)+';return true')
    async def finish_phase(self,name):
        await self.wait('(window.v1Measure.counts['+json.dumps(name)+']||0)>=850',90)
    async def record(self,phase,operation):
        try:result=await operation();self.report['findings'].append({'phase':phase,'result':result})
        except Exception as error:self.report['findings'].append({'phase':phase,'error':repr(error)});print('FINDING '+phase+' '+repr(error),flush=True)
    async def open_copy(self):
        await self.b.call('Page.navigate',{'url':'http://127.0.0.1:8527'})
        await self.click("document.querySelector('.st-key-home_open_panel summary')")
        await self.click("document.querySelector('.st-key-home_saved button[aria-haspopup=listbox]')")
        # Use actual native search to make a virtualized select option visible.
        combo="all().find(e=>e.getAttribute('role')==='combobox'&&e.getAttribute('aria-expanded')==='true')"
        if await self.ev('return Boolean('+combo+')'):
            await self.click(combo);await self.b.call('Input.insertText',{'text':'borrador-studio-demo-fullhd-8escenas'})
        await self.click("all().find(e=>e.getAttribute('role')==='option'&&e.textContent.trim()==='borrador-studio-demo-fullhd-8escenas')")
        await self.click("document.querySelector('.st-key-home_open button')")
        if not await self.wait('all().some(e=>e.id==="canvas-stage"&&e.querySelector("img.piece")?.complete)',60):raise RuntimeError('Copy did not open')
        return await self.state()

SAMPLER="""
window.v1Measure={phase:'autoguardado',samples:[],counts:{},stopped:false};
function effective(e){let o=1,n=e;const chain=[];for(let i=0;i<40&&n;i++){const css=getComputedStyle(n),opacity=Number(css.opacity);o*=opacity;chain.push({tag:n.tagName,cls:String(n.className),testid:n.getAttribute('data-testid'),stale:n.getAttribute('data-stale'),opacity});n=n.parentElement||n.getRootNode()?.host}return {opacity:o,chain}}
function sample(){const m=window.v1Measure;if(m.stopped)return;if((m.counts[m.phase]||0)>=1500){requestAnimationFrame(sample);return}const nodes=all();const stage=nodes.find(e=>e.id==='canvas-stage'),board=stage?.querySelector('.board'),movie=nodes.find(e=>e.id==='movie');const mode=nodes.find(e=>e.id==='canvas-mode')?.textContent;
const playing=mode?.startsWith('PREVIEW')&&!nodes.find(e=>e.id==='movie')?.hidden;
const target=playing?movie:board,host=document.querySelector(HOST_SELECTOR);
const value=effective(target),maps=[...(board?.querySelectorAll('img.piece')||[])].filter(e=>e.alt.startsWith('Región SIG'));
const outside=[...document.querySelectorAll('[data-stale="true"]')].filter(e=>e!==host).map(e=>{const r=e.getBoundingClientRect(),v=effective(e),c=getComputedStyle(e);return {cls:e.className,testid:e.getAttribute('data-testid'),text:(e.innerText||'').trim().slice(0,220),visible:r.width>0&&r.height>0&&r.bottom>0&&r.top<innerHeight&&c.display!=='none'&&c.visibility!=='hidden',editor:e.contains(host)||host?.contains(e)||!!e.closest('[class*="free_studio"]'),opacity:v.opacity,ancestors:v.chain}});
m.samples.push({t:performance.now(),phase:m.phase,opacity:value.opacity,ancestors:value.chain,stale:value.chain.some(a=>a.stale==='true'),staleElsewhere:outside,ready:maps.filter(e=>e.complete&&e.naturalWidth>0).length,videoReady:playing?movie?.readyState:null,mode,date:nodes.find(e=>e.id==='scientific-date')?.textContent});m.counts[m.phase]=(m.counts[m.phase]||0)+1;requestAnimationFrame(sample)}requestAnimationFrame(sample);return true
"""

def summarize(samples):
    out={}
    for phase in sorted({s['phase'] for s in samples}):
        rows=[s for s in samples if s['phase']==phase];stale=[s for s in rows if s['stale']]
        windows=[];start=None;last=None
        for s in rows:
            if s['stale'] and start is None:start=s['t']
            if not s['stale'] and start is not None:windows.append({'start_ms':start,'end_ms':s['t'],'duration_ms':s['t']-start});start=None
            last=s['t']
        if start is not None:windows.append({'start_ms':start,'end_ms':last,'duration_ms':last-start,'open_at_phase_end':True})
        out[phase]={'samples':len(rows),'stale_samples':len(stale),'minimum':min(s['opacity'] for s in rows),
                    'stale_minimum':min((s['opacity'] for s in stale),default=None),'stale_windows':windows,'total_stale_ms':sum(w['duration_ms'] for w in windows)}
    return out

async def download_samples(j):
    # A whole 4250-row reply exceeds Tornado's default 10 MB CDP limit.
    length=await j.ev('window.v1Measure.stopped=true;return window.v1Measure.samples.length')
    rows=[]
    for offset in range(0,length,100):
        rows.extend(await j.ev('return window.v1Measure.samples.slice('+str(offset)+','+str(offset+100)+')'))
    return rows

async def run():
    from studio_v1_measure import identity
    before=identity();started=time.time();tag=str(time.time_ns());evidence=ROOT/f'tmp/v1-definitive-opacity-{tag}.json'
    b=await driver.SigBrowser().start();chrome=psutil.Process(b.process.pid)
    report={'status':'RUNNING','server_before':before,'server_restarts_during_measurement':0,'findings':[],
            'chrome':{'pid':chrome.pid,'created':chrome.create_time(),'command':chrome.cmdline(),'profile':next(a.split('=',1)[1] for a in chrome.cmdline() if a.startswith('--user-data-dir='))},'selector':SELECTOR}
    j=Journey(b,report)
    try:
        await b.call('Emulation.setDeviceMetricsOverride',{'width':1920,'height':1080,'deviceScaleFactor':1,'mobile':False})
        initial=await j.open_copy();report['initial']=initial
        report['copies']=[{'name':initial['name'],'drafts':[str(p.relative_to(ROOT)) for p in (ROOT/'_local/video-studio/projects').glob('borrador-studio-*.json') if not p.name.endswith('.previous.json') and p.stat().st_mtime>=started]}]
        await j.ev(SAMPLER.replace('HOST_SELECTOR',json.dumps(SELECTOR)))
        async def rename():
            value=initial['name']+' · opacidad';await j.click(j.elem('project-name'))
            await j.key('a','KeyA',2,65);await b.call('Input.insertText',{'text':value})
            typed=await j.state();await j.key('Enter');await j.key('Tab')
            acknowledged=await j.settled(initial['version']);after=await j.state()
            return {'expected':value,'typed':typed['name'],'acknowledged':acknowledged,'after':after}
        await j.record('autoguardado',rename)
        await j.finish_phase('autoguardado')
        await j.phase('arrastre')
        async def drag():
            await j.click("all().find(e=>e.tagName==='BUTTON'&&e.closest('.layer-row')&&e.textContent.startsWith('Región SIG'))")
            before_drag=await j.state();expr=j.elem('canvas-stage')+'.querySelector(\'.piece[alt^="Región SIG"]\')'
            point=await j.ev('const r='+expr+'.getBoundingClientRect();return {x:r.x+r.width*.4,y:r.y+r.height*.4}')
            await b.call('Input.dispatchMouseEvent',{'type':'mousePressed','button':'left','buttons':1,'clickCount':1,**point})
            for step in range(1,9):await b.call('Input.dispatchMouseEvent',{'type':'mouseMoved','button':'left','buttons':1,'x':point['x']+16*step/8,'y':point['y']+8*step/8})
            await b.call('Input.dispatchMouseEvent',{'type':'mouseReleased','button':'left','buttons':0,'clickCount':1,'x':point['x']+16,'y':point['y']+8})
            ack=await j.settled(before_drag['version']);moved=await j.state()
            # Restore presentation through the UI, only to avoid another render.
            if await j.ev('return !'+j.elem('undo')+'.disabled'):
                await j.click(j.elem('undo'));await j.settled(moved['version'])
            return {'before':before_drag,'moved':moved,'acknowledged':ack,'restored':await j.state()}
        await j.record('arrastre',drag)
        await j.finish_phase('arrastre')
        await j.phase('cambio_escena')
        async def scenes():
            current=await j.state();await j.click(j.elem('scenes')+'.children[1]')
            first=await j.wait('all().some(e=>e.classList.contains("evs")&&e.dataset.scene!=='+json.dumps(current['scene'])+')',45)
            middle=await j.state();await j.click(j.elem('scenes')+'.children[0]')
            second=await j.wait('all().some(e=>e.classList.contains("evs")&&e.dataset.scene==='+json.dumps(current['scene'])+')',45)
            return {'first_changed':first,'second_changed':second,'middle':middle,'after':await j.state()}
        await j.record('cambio_escena',scenes)
        await j.finish_phase('cambio_escena')
        await j.phase('reproduccion')
        async def playback():
            await j.click(j.elem('play'))
            ready=await j.wait('all().some(e=>e.id==="movie"&&e.readyState>=2&&!e.paused&&e.currentTime>4)',600)
            return {'playing':ready,'after':await j.state(),'movie':await j.ev('const e='+j.elem('movie')+';return {readyState:e.readyState,time:e.currentTime,src:e.currentSrc,width:e.videoWidth,height:e.videoHeight}')}
        await j.record('reproduccion',playback)
        await j.finish_phase('reproduccion')
        await j.phase('retorno_preview')
        async def back():
            await j.click(j.elem('back-edit'));ready=await j.wait('all().some(e=>e.id==="canvas-mode"&&e.textContent==="EDICIÓN")')
            return {'editing':ready,'after':await j.state()}
        await j.record('retorno_preview',back)
        await j.finish_phase('retorno_preview')
        await j.wait('window.v1Measure.samples.length>=4200',120)
        samples=await download_samples(j);report['samples']=samples
        report['by_phase']=summarize(samples)
        report['summary']={'samples':len(samples),'minimum':min(s['opacity'] for s in samples),'stale_samples':sum(s['stale'] for s in samples),'without_decoded_map':sum(s['ready']==0 for s in samples)}
        report['dominant_stale_phase']=max(report['by_phase'],key=lambda p:report['by_phase'][p]['total_stale_ms'])
        # Identify every stale element outside the workspace, not just a count.
        outside={}
        for s in samples:
            for e in s['staleElsewhere']:
                key=json.dumps([e['cls'],e['testid'],e['text']],ensure_ascii=False)
                if key not in outside:outside[key]={**e,'samples':0,'minimum':1}
                outside[key]['samples']+=1;outside[key]['minimum']=min(outside[key]['minimum'],e['opacity'])
        report['stale_elsewhere']=list(outside.values())
        await b.shot('v1-definitive-opacity-'+tag+'.png')
        report['screenshot']='tmp/ux-redesign/v1-definitive-opacity-'+tag+'.png'
        # Short CSS-off contrast on the same running server and same page.
        report['css_off']=await j.ev("const selector="+json.dumps(SELECTOR)+";window.v1HostStyles=[...document.querySelectorAll('style')].filter(e=>e.textContent.includes('st-key-free_studio_')&&e.textContent.includes('opacity'));window.v1HostStyles.forEach(e=>e.sheet.disabled=true);return {disabled:window.v1HostStyles.length,hostOpacity:getComputedStyle(document.querySelector(selector)).opacity}")
        await j.ev(SAMPLER.replace('HOST_SELECTOR',json.dumps(SELECTOR)))
        await j.phase('contraste_sin_css');await j.record('contraste_sin_css',rename)
        await j.wait('window.v1Measure.samples.some(s=>s.stale)&&window.v1Measure.samples.some(s=>s.opacity<.99)',20)
        contrast=await j.ev('window.v1Measure.stopped=true;const result=window.v1Measure.samples;window.v1HostStyles.forEach(e=>e.sheet.disabled=false);return result')
        report['contrast']={'samples':contrast,'by_phase':summarize(contrast),'minimum':min((s['opacity'] for s in contrast),default=None),'stale_samples':sum(s['stale'] for s in contrast)}
        report['server_after']=identity()
        stable=before==report['server_after'];report['environment_unchanged']=stable
        visible_faded=[e for e in report['stale_elsewhere'] if e['visible'] and e['editor'] and e['minimum']<.99]
        report['visible_editor_stale_below_099']=visible_faded
        report['status']='PASS' if stable and len(samples)>=4000 and report['summary']['minimum']>=.99 and report['summary']['stale_samples']>0 and report['summary']['without_decoded_map']==0 and all(p in report['by_phase'] for p in PHASES) and report['contrast']['stale_samples']>0 and report['contrast']['minimum']<.99 and not visible_faded else 'FAIL'
    except Exception as error:
        report['status']='FAIL';report['error']=repr(error)
        try:report['partial_samples']=await download_samples(j);await b.shot('v1-definitive-opacity-failure-'+tag+'.png')
        except Exception as inspection:report['inspection_error']=repr(inspection)
    finally:
        try:await b.call('Browser.close');b.ws.close();chrome.wait(timeout=15);report['chrome_closed']=True
        except Exception as error:report['chrome_close_error']=repr(error)
        evidence.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        (ROOT/'tmp/v1-definitive-latest.json').write_text(json.dumps({'evidence':str(evidence),'server_before':before,'chrome':report['chrome']},indent=2),encoding='utf-8')
        print(json.dumps({k:v for k,v in report.items() if k in ('status','error','summary','by_phase','dominant_stale_phase','stale_elsewhere','chrome_closed')},ensure_ascii=False),flush=True)
        print('EVIDENCE '+str(evidence),flush=True)

if __name__=='__main__':asyncio.run(run())
