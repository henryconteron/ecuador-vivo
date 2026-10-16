"""Native project-name, persisted draft, geometry and calendar verification."""
import asyncio
import copy
import json
from pathlib import Path
import sys
import time
import psutil
from studio_v1_opacity import Journey, driver, ROOT
from studio_v1_measure import identity

def disk_state(identifier):
    matches=[]
    for p in (ROOT/'_local/video-studio/projects').glob('borrador-studio-*.json'):
        if p.name.endswith('.previous.json'):continue
        try:d=json.loads(p.read_text(encoding='utf-8'))
        except (OSError,ValueError):continue
        if d.get('project_meta',{}).get('id')==identifier:matches.append((p,d))
    p,d=max(matches,key=lambda item:item[0].stat().st_mtime_ns)
    return {'path':str(p.relative_to(ROOT)),'name':d['name'],'revision':d['project_meta']['revision'],'project':d}

async def run():
    before=identity();tag=str(time.time_ns());b=await driver.SigBrowser().start();chrome=psutil.Process(b.process.pid)
    report={'status':'RUNNING','server_before':before,'events':[],'chrome_pid':chrome.pid,'chrome_command':chrome.cmdline(),'server_restarts_during_measurement':0}
    j=Journey(b,report)
    async def snapshot(label):
        ui=await j.state();disk=disk_state(ui['project']['project_meta']['id'])
        result={'gesture':label,'ui':{'name':ui['name'],'version':ui['version'],'document_name':ui['project']['name'],'document_revision':ui['project']['project_meta']['revision'],'date':ui['date'],'frame':ui['frame']},'disk':disk}
        report['events'].append(result);return ui,result
    try:
        await b.call('Emulation.setDeviceMetricsOverride',{'width':1920,'height':1080,'deviceScaleFactor':1,'mobile':False})
        initial=await j.open_copy();ui,first=await snapshot('open_copy');report['copy_name']=ui['name'];report['draft']=first['disk']['path']
        expected='Studio v1 · nombre verificado '+tag[-8:];report['expected_name']=expected
        await j.click(j.elem('project-name'));await j.key('a','KeyA',2,65)
        await b.call('Input.insertText',{'text':expected});await snapshot('insertText_before_commit')
        await j.key('Enter');await j.key('Tab');await j.settled(initial['version'])
        renamed,renamed_record=await snapshot('enter_and_blur')
        report['rename_ok']=renamed['name']==expected and renamed['project']['name']==expected and renamed_record['disk']['name']==expected
        await j.click(j.elem('project-name'));await j.key('a','KeyA',2,65)
        await b.call('Input.insertText',{'text':initial['name']});await j.key('Enter');await j.key('Tab');await j.settled(renamed['version'])
        await snapshot('restore_name_for_cached_preview')
        # Fresh copy supplies the requested minimum Undo/Redo reproduction.
        await j.click(j.elem('nav-home'))
        await j.open_copy();start,_=await snapshot('undo_copy_open')
        await j.click("all().find(e=>e.tagName==='BUTTON'&&e.closest('.layer-row')&&e.textContent.startsWith('Región SIG'))")
        def transform(s):
            scene=next(c for c in s['project']['studio']['scenes'] if c['id']==s['scene'])
            return next(e['transform'] for e in scene['elements'] if e.get('temporal_binding',{}).get('channel')=='continent')
        report['transforms']={'before':transform(start)}
        point=await j.ev('const r='+j.elem('canvas-stage')+'.querySelector(\'.piece[alt^="Región SIG"]\').getBoundingClientRect();return {x:r.x+r.width*.4,y:r.y+r.height*.4}')
        await b.call('Input.dispatchMouseEvent',{'type':'mousePressed','button':'left','buttons':1,'clickCount':1,**point})
        for step in range(1,9):await b.call('Input.dispatchMouseEvent',{'type':'mouseMoved','button':'left','buttons':1,'x':point['x']+16*step/8,'y':point['y']+8*step/8})
        await b.call('Input.dispatchMouseEvent',{'type':'mouseReleased','button':'left','buttons':0,'clickCount':1,'x':point['x']+16,'y':point['y']+8})
        await j.settled(start['version']);moved,_=await snapshot('drag');report['transforms']['after_drag']=transform(moved)
        await j.click(j.elem('undo'));await j.settled(moved['version']);undone,_=await snapshot('undo');report['transforms']['after_undo']=transform(undone)
        await j.click(j.elem('redo'));await j.settled(undone['version']);redone,_=await snapshot('redo');report['transforms']['after_redo']=transform(redone)
        report['undo_redo_ok']=report['transforms']['before']!=report['transforms']['after_drag'] and report['transforms']['after_undo']==report['transforms']['before'] and report['transforms']['after_redo']==report['transforms']['after_drag']
        await j.click(j.elem('undo'));await j.settled(redone['version'])
        await j.click(j.elem('play'));playing=await j.wait('all().some(e=>e.id==="movie"&&!e.paused&&e.readyState>=2&&e.currentTime>1.5)',600)
        await j.click(j.elem('back-edit'));returned,_=await snapshot('return_from_preview')
        date=await j.ev('return all().find(e=>e.id==="canvas-stage").getRootNode().__evsSignature')
        report['calendar']={'playing':playing,'canvas_frame':returned['frame'],'label':returned['date'],'expected':'Fecha científica · 2024-01-01'}
        report['calendar_ok']=returned['frame']==0 and returned['date']==report['calendar']['expected']
        report['server_after']=identity();report['environment_unchanged']=before==report['server_after']
        report['status']='PASS' if report['rename_ok'] and report['undo_redo_ok'] and report['calendar_ok'] and report['environment_unchanged'] else 'FAIL'
        await b.shot('v1-definitive-editing-'+tag+'.png');report['screenshot']='tmp/ux-redesign/v1-definitive-editing-'+tag+'.png'
    except Exception as error:report['status']='FAIL';report['error']=repr(error)
    finally:
        await b.call('Browser.close');b.ws.close();chrome.wait(timeout=15);report['chrome_closed']=True
        path=ROOT/f'tmp/v1-definitive-editing-{tag}.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({k:v for k,v in report.items() if k in ('status','error','rename_ok','undo_redo_ok','calendar_ok','transforms','calendar','chrome_pid','chrome_closed','draft')},ensure_ascii=False),flush=True)
        print('EVIDENCE '+str(path),flush=True)

if __name__=='__main__':asyncio.run(run())
