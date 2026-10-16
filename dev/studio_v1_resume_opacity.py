"""Recover retained samples from our verified Chrome after oversized CDP reply."""
import asyncio
import json
from pathlib import Path
import sys
import urllib.request
import psutil
from tornado.websocket import websocket_connect
from studio_v1_opacity import Journey, SAMPLER, SELECTOR, PHASES, summarize, driver, ROOT
from studio_v1_measure import identity

async def download(j):
    length=await j.ev('window.v1Measure.stopped=true;return window.v1Measure.samples.length')
    rows=[]
    for offset in range(0,length,100):
        rows.extend(await j.ev('return window.v1Measure.samples.slice('+str(offset)+','+str(offset+100)+')'))
    return rows

async def run():
    latest=json.loads((ROOT/'tmp/v1-definitive-latest.json').read_text(encoding='utf-8'))
    report=json.loads(Path(latest['evidence']).read_text(encoding='utf-8'))
    saved=report['chrome'];chrome=psutil.Process(saved['pid'])
    assert chrome.create_time()==saved['created'] and chrome.cmdline()==saved['command']
    assert '--headless=new' in chrome.cmdline()
    assert Path(saved['profile']).resolve().is_relative_to(ROOT/'tmp')
    report['server_before']['listeners']={int(k):v for k,v in report['server_before']['listeners'].items()}
    before=identity();assert before==report['server_before']
    port=next(a.split('=',1)[1] for a in chrome.cmdline() if a.startswith('--remote-debugging-port='))
    tabs=json.load(urllib.request.urlopen('http://127.0.0.1:'+port+'/json'))
    b=driver.SigBrowser();b.n=0;b.events=[]
    b.ws=await websocket_connect(next(t['webSocketDebuggerUrl'] for t in tabs if t['type']=='page'))
    j=Journey(b,report);tag=Path(latest['evidence']).stem.rsplit('-',1)[1]
    target=ROOT/f'tmp/v1-definitive-opacity-{tag}-recovered.json'
    report['transport_recovery']={'original_error':report.pop('error',None),'same_chrome_pid':chrome.pid,'chunk_size':100,'repeated_gestures':False}
    try:
        samples=await download(j);report['samples']=samples
        report['by_phase']=summarize(samples)
        report['summary']={'samples':len(samples),'minimum':min(s['opacity'] for s in samples),'stale_samples':sum(s['stale'] for s in samples),'without_decoded_map':sum(s['ready']==0 for s in samples)}
        report['dominant_stale_phase']=max(report['by_phase'],key=lambda p:report['by_phase'][p]['total_stale_ms'])
        outside={}
        for s in samples:
            for e in s['staleElsewhere']:
                key=json.dumps([e['cls'],e['testid'],e['text']],ensure_ascii=False)
                if key not in outside:outside[key]={**e,'samples':0,'minimum':1}
                outside[key]['samples']+=1;outside[key]['minimum']=min(outside[key]['minimum'],e['opacity'])
        report['stale_elsewhere']=list(outside.values())
        await b.shot('v1-definitive-opacity-'+tag+'.png');report['screenshot']='tmp/ux-redesign/v1-definitive-opacity-'+tag+'.png'
        report['css_off']=await j.ev("window.v1HostStyles=[...document.querySelectorAll('style')].filter(e=>e.textContent.includes('st-key-free_studio_')&&e.textContent.includes('opacity'));window.v1HostStyles.forEach(e=>e.sheet.disabled=true);return {disabled:window.v1HostStyles.length}")
        await j.ev(SAMPLER.replace('HOST_SELECTOR',json.dumps(SELECTOR)))
        await j.phase('contraste_sin_css')
        current=await j.state();await j.click(j.elem('project-name'));await j.key('a','KeyA',2,65)
        await b.call('Input.insertText',{'text':current['name']+' · contraste'})
        await j.key('Enter');await j.key('Tab');await j.settled(current['version'])
        await j.wait('window.v1Measure.samples.some(s=>s.stale)&&window.v1Measure.samples.some(s=>s.opacity<.99)',20)
        contrast=await download(j)
        await j.ev('window.v1HostStyles.forEach(e=>{if(e.sheet)e.sheet.disabled=false});return true')
        report['contrast']={'samples':contrast,'by_phase':summarize(contrast),'minimum':min((s['opacity'] for s in contrast),default=None),'stale_samples':sum(s['stale'] for s in contrast)}
        report['server_after']=identity();stable=report['server_after']==before;report['environment_unchanged']=stable
        visible_faded=[e for e in report['stale_elsewhere'] if e['visible'] and e['editor'] and e['minimum']<.99]
        report['visible_editor_stale_below_099']=visible_faded
        report['status']='PASS' if stable and len(samples)>=4000 and report['summary']['minimum']>=.99 and report['summary']['stale_samples']>0 and report['summary']['without_decoded_map']==0 and all(p in report['by_phase'] for p in PHASES) and report['contrast']['stale_samples']>0 and report['contrast']['minimum']<.99 and not visible_faded else 'FAIL'
    except Exception as error:report['status']='FAIL';report['error']=repr(error)
    finally:
        try:await b.call('Browser.close');b.ws.close();chrome.wait(timeout=15);report['chrome_closed']=True;report.pop('chrome_close_error',None)
        except Exception as error:report['chrome_close_error']=repr(error)
        target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        latest['evidence']=str(target);(ROOT/'tmp/v1-definitive-latest.json').write_text(json.dumps(latest,indent=2),encoding='utf-8')
        print(json.dumps({k:v for k,v in report.items() if k in ('status','error','summary','by_phase','dominant_stale_phase','stale_elsewhere','chrome_closed')},ensure_ascii=False),flush=True)
        print('EVIDENCE '+str(target),flush=True)

if __name__=='__main__':asyncio.run(run())
