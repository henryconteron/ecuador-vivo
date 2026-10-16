"""One bounded real-data UI flow. Run: python dev/editor_browser.py dev/editor_smoke.py"""
import copy
import time
import psutil
import sys
from pathlib import Path
from editor_visual_start import task as start
from editor_sig_journey import task as sig

SAMPLER="""
window.editorMeasure={samples:[],stopped:false};function sample(){const m=window.editorMeasure;if(m.stopped||m.samples.length>=16000)return;
 const nodes=all(),stage=nodes.find(e=>e.id==='canvas-stage'),root=stage?.getRootNode(),movie=root?.querySelector('#movie'),mode=root?.querySelector('#canvas-mode')?.textContent;
 const target=mode?.includes('VISUALIZACIÓN')?movie:stage?.querySelector('.board');let opacity=1,n=target,stale=false;
 while(n){opacity*=Number(getComputedStyle(n).opacity);stale||=n.getAttribute?.('data-stale')==='true';n=n.parentElement||n.getRootNode()?.host}
 if(target){const images=[...stage.querySelectorAll('img.piece')].filter(e=>e.alt.startsWith('Región SIG'));m.samples.push({t:performance.now(),mode,opacity,stale,maps:images.length,decoded:images.filter(e=>e.complete&&e.naturalWidth>0).length,mounts:root.__evsMounts,date:root.querySelector('#scientific-date').textContent})}requestAnimationFrame(sample)}requestAnimationFrame(sample);return true
"""

async def task(b,j):
    report={'status':'RUNNING','checks':[],'started':time.time(),'server_restarts':0,'page_reloads_during_measurement':0}
    path=ROOT/'tmp/editor-smoke.json'
    before=json.loads((ROOT/'tmp/editor-server-studio.json').read_text());report['server']=before
    async def checkpoint():path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    async def state():return await j.state()
    async def settled(old):
        assert await j.settled(old['version']);value=await state();assert not value['error'];return value
    async def fill(expr,value):
        await j.click(expr);await j.key('a','KeyA',2,65);await b.call('Input.insertText',{'text':str(value)});await j.key('Tab')
    async def pixels():
        assert await j.wait("all().some(e=>e.id==='canvas-stage'&&[...e.querySelectorAll('img.piece')].some(i=>i.alt.startsWith('Región SIG')&&i.complete&&i.naturalWidth>0))&&!all().some(e=>e.id==='workspace-status'&&e.textContent.includes('actualizando'))",60)
    def button(text):return "all().find(e=>e.tagName==='BUTTON'&&e.textContent.trim()==="+json.dumps(text)+")"
    def draft(project):
        for file in (ROOT/'_local/video-studio/projects').glob('borrador-studio-*.json'):
            if file.name.endswith('.previous.json'):continue
            try:value=json.loads(file.read_text(encoding='utf8'))
            except (OSError,ValueError):continue
            if value.get('project_meta',{}).get('id')==project['project_meta']['id']:return {'path':str(file.relative_to(ROOT)),'name':value['name'],'revision':value['project_meta']['revision'],'project':value}
        raise RuntimeError('No se encontró el borrador guardado')
    try:
        if '--resume-sig' not in sys.argv:await start(b,j)
        await sig(b,j);await pixels()
        report['checks'].append({'operation':'complete_sig','evidence':'tmp/editor-sig-journey.json'})
        old=await state();blank=old['project']['studio']['timeline'][0]
        await j.click("all().find(e=>e.id==='scenes').querySelector('[data-scene=\""+blank+"\"]')")
        assert await j.wait("JSON.parse(all().find(e=>e.id==='canvas-stage').getRootNode().__evsSignature)[2]==="+json.dumps(blank),30)
        await j.click(j.elem('scene-remove'));old=await settled(old);await pixels()
        assert len(old['project']['studio']['timeline'])==1
        await j.ev(SAMPLER)
        original_mounts=await j.ev("return all().find(e=>e.id==='canvas-stage').getRootNode().__evsMounts")
        name='Ecuador Vivo · cierre editor · CHIRPS real'
        started=time.perf_counter();await fill(j.elem('project-name'),name);renamed=await settled(old)
        report['checks'].append({'operation':'rename','ui_name':renamed['name'],'signal_name':renamed['project']['name'],'ui_revision':renamed['project']['project_meta']['revision'],'disk':draft(renamed['project']),'confirm_ms':(time.perf_counter()-started)*1000});assert renamed['name']==name==draft(renamed['project'])['name'];await checkpoint()
        scene=next(s for s in renamed['project']['studio']['scenes'] if s['id']==renamed['scene']);title=next(e for e in scene['elements'] if e['name']=='Variable y unidades');eid=title['id']
        await j.click("all().find(e=>e.id==='layers').querySelector('[data-layer=\""+eid+"\"] button')")
        await j.click(j.elem('locked'));unlocked=await settled(renamed);await pixels()
        text='LLUVIA DIARIA EN ECUADOR\nCHIRPS v2 · 1–3 enero 2024 · mm/día'
        started=time.perf_counter();await fill(j.elem('text'),text);edited=await settled(unlocked);await pixels()
        scene=next(s for s in edited['project']['studio']['scenes'] if s['id']==edited['scene']);assert next(e for e in scene['elements'] if e['id']==eid)['style']['text']==text
        report['checks'].append({'operation':'text','confirm_ms':(time.perf_counter()-started)*1000,'state':edited});await checkpoint()
        transform=copy.deepcopy(next(e for e in scene['elements'] if e['id']==eid)['transform'])
        point=await j.ev("const i=all().find(e=>e.id==='canvas-stage').querySelector('img[data-id=\""+eid+"\"]'),r=i.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}")
        started=time.perf_counter()
        for kind,dx,dy in [('mouseMoved',0,0),('mousePressed',0,0),('mouseMoved',5,6),('mouseReleased',5,6)]:await b.call('Input.dispatchMouseEvent',{'type':kind,'button':'left','buttons':int(kind in ('mousePressed','mouseMoved') and (kind=='mousePressed' or dx>0)),'clickCount':1,'x':point['x']+dx,'y':point['y']+dy})
        moved=await settled(edited);moved_scene=next(s for s in moved['project']['studio']['scenes'] if s['id']==moved['scene']);after=next(e for e in moved_scene['elements'] if e['id']==eid)['transform'];assert after!=transform
        report['checks'].append({'operation':'drag','before':transform,'after':after,'confirm_ms':(time.perf_counter()-started)*1000});await checkpoint()
        await j.click(j.elem('undo'));undone=await settled(moved);restored=next(e for s in undone['project']['studio']['scenes'] for e in s['elements'] if e['id']==eid)['transform'];assert restored==transform
        await j.click(j.elem('redo'));redone=await settled(undone);restored=next(e for s in redone['project']['studio']['scenes'] for e in s['elements'] if e['id']==eid)['transform'];assert restored==after
        mounts=await j.ev("return all().find(e=>e.id==='canvas-stage').getRootNode().__evsMounts");assert mounts==original_mounts
        report['checks'].append({'operation':'undo_redo','before':transform,'undo':transform,'redo':restored,'controller_mounts_before':original_mounts,'controller_mounts_after':mounts});await pixels();await b.shot('editor-studio-vertical-final-1366.png');await checkpoint()
        started=time.perf_counter();await j.click(j.elem('play'))
        assert await j.wait("all().some(e=>e.id==='movie'&&e.readyState>=2)",180)
        preview_ms=(time.perf_counter()-started)*1000;report['preview_ms']=preview_ms
        preview=await j.ev("const s=all().find(e=>e.id==='canvas-stage').getRootNode();return {mode:s.querySelector('#canvas-mode').textContent,width:s.querySelector('#movie').videoWidth,height:s.querySelector('#movie').videoHeight,url:s.querySelector('#movie').getAttribute('src')}");assert max(preview['width'],preview['height'])<=640;assert 'PREVISUALIZACIÓN' in preview['mode'];report['checks'].append({'operation':'preview','measurement':preview,'ms':preview_ms});await checkpoint()
        await j.click(j.elem('playhead'));await j.key('End',vk=35);await j.key('Tab');assert await j.wait("all().find(e=>e.id==='scientific-date').textContent.includes('2024-01-03')",20)
        report['checks'].append({'operation':'movie_seek','date':await j.ev("return all().find(e=>e.id==='scientific-date').textContent")})
        await j.click(j.elem('back-edit'));returned=await state();assert returned['date'].endswith('2024-01-01');report['checks'].append({'operation':'back_edit','state':returned})
        await j.click(j.elem('playhead'));await j.key('End',vk=35);await j.key('Tab');assert await j.wait("all().find(e=>e.id==='canvas-mode').textContent.startsWith('CUADRO')&&all().find(e=>e.id==='scientific-date').textContent.includes('2024-01-03')",60)
        await j.click(j.elem('back-edit'));assert (await state())['date'].endswith('2024-01-03');report['checks'].append({'operation':'editor_seek_and_return','state':await state()});await checkpoint()
        old=await state();text='LLUVIA DIARIA · ECUADOR\nCHIRPS v2 · 1–3 enero 2024 · mm/día'
        await fill(j.elem('text'),text);new=await settled(old);await pixels()
        assert await j.ev("return all().find(e=>e.id==='workspace-status').textContent.includes('El documento cambió')")
        report['checks'].append({'operation':'content_invalidates_preview','state':new});await checkpoint()
        await j.click(j.elem('export'));started=time.perf_counter();await j.click(button('Exportar MP4'))
        assert await j.wait("all().some(e=>e.id==='workspace-status'&&e.textContent.startsWith('Exportación final lista'))",300)
        report['final_ms']=(time.perf_counter()-started)*1000;report['checks'].append({'operation':'final_export','ms':report['final_ms'],'dimensions':[1080,1920]});await checkpoint()
        await j.click(j.elem('nav-home'));assert await j.wait("document.querySelector('.st-key-home_open_panel summary')!==null")
        await j.click("document.querySelector('.st-key-home_open_panel summary')");await j.click("document.querySelector('.st-key-home_saved button[aria-haspopup=listbox]')")
        saved_path=Path(draft(new['project'])['path']).stem
        combo="all().find(e=>e.getAttribute('role')==='combobox'&&e.getAttribute('aria-expanded')==='true')"
        if await j.ev('return Boolean('+combo+')'):await j.click(combo);await b.call('Input.insertText',{'text':saved_path})
        await j.click("all().find(e=>e.getAttribute('role')==='option'&&e.textContent.trim()==="+json.dumps(saved_path)+")");await j.click("document.querySelector('.st-key-home_open button')");await pixels()
        reopened=await state();assert reopened['name']==new['name'];current=next(e for s in reopened['project']['studio']['scenes'] for e in s['elements'] if e['id']==eid);assert current['transform']==after and current['style']['text']==text
        report['checks'].append({'operation':'reopen','state':reopened});report['final_draft']=draft(reopened['project']);report['status']='PASS'
        for width,height in [(1366,768),(1920,1080)]:
            await b.call('Emulation.setDeviceMetricsOverride',{'width':width,'height':height,'deviceScaleFactor':1,'mobile':False});await j.wait('innerWidth==='+str(width));await b.shot('editor-studio-final-'+str(width)+'.png')
        current=psutil.Process(before['pid']);assert current.create_time()==before['created'] and current.cmdline()==before['command'];report['server_identity_preserved']=True
    except Exception as error:
        report['status']='FAIL';report['error']=repr(error);report['state']=await state();report['visible']=await j.ev("return all().filter(e=>e.tagName==='BUTTON'||e.getAttribute('data-testid')==='stException').map(e=>e.textContent).slice(-45)");await b.shot('editor-smoke-failure.png');raise
    finally:
        count=await j.ev('if(!window.editorMeasure)return 0;window.editorMeasure.stopped=true;return window.editorMeasure.samples.length')
        samples=[]
        for offset in range(0,count,250):samples.extend(await j.ev('return window.editorMeasure.samples.slice('+str(offset)+','+str(offset+250)+')'))
        if samples:
            stale=[s for s in samples if s['stale']];report['stability']={'samples':len(samples),'stale_samples':len(stale),'minimum_opacity':min(s['opacity'] for s in samples),'stale_minimum_opacity':min((s['opacity'] for s in stale),default=None),'missing_maps_edit':sum(s['mode']=='EDICIÓN' and s['decoded']==0 for s in samples)}
            (ROOT/'tmp/editor-stability.json').write_text(json.dumps(samples,ensure_ascii=False),encoding='utf8')
        await checkpoint();print(json.dumps({'status':report['status'],'error':report.get('error'),'preview_ms':report.get('preview_ms'),'final_ms':report.get('final_ms'),'checks':[c['operation'] for c in report['checks']],'stability':report.get('stability')},ensure_ascii=False),flush=True)
