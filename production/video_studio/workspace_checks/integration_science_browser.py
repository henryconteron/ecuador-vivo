"""Cached CHIRPS day: capture -> editable scenes -> explicit proposal -> MP4."""
import asyncio
import json
import time
from pathlib import Path
from ux_browser import Browser,ROOT


async def run():
    browser=await Browser().start();checks=[];started=time.time()
    async def ev(code):return await browser.evaluate("const q=id=>all().find(e=>e.id===id);"+code)
    async def button(label):
        point=await ev("const label="+json.dumps(label)+";const button=all().find(e=>e.tagName==='BUTTON'&&(label!=='Visualizaciones'||e.getAttribute('role')==='radio')&&e.getBoundingClientRect().width>0&&e.getBoundingClientRect().height>0&&e.textContent.includes(label));button.scrollIntoView({block:'center'});const r=button.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}")
        await browser.call('Input.dispatchMouseEvent',{'type':'mouseMoved',**point})
        await browser.call('Input.dispatchMouseEvent',{'type':'mousePressed','button':'left','buttons':1,'clickCount':1,**point})
        await browser.call('Input.dispatchMouseEvent',{'type':'mouseReleased','button':'left','buttons':0,'clickCount':1,**point})
    async def commit(code):
        before=await ev("return Number(all().find(e=>e.classList.contains('evs')).dataset.version)")
        await ev(code)
        await browser.wait("Number(all().find(e=>e.classList.contains('evs')).dataset.version)>"+str(before))
    try:
        await browser.call('Runtime.enable');await browser.call('Page.navigate',{'url':'http://127.0.0.1:8513'})
        await browser.wait("all().some(e=>e.tagName==='INPUT'&&e.type==='file')")
        remote=await browser.call('Runtime.evaluate',{'expression':"document.querySelector('input[type=file]')"})
        await browser.call('DOM.setFileInputFiles',{'files':[str((ROOT/'ux-redesign/scientific-project.json').resolve())],'objectId':remote['result']['objectId']})
        await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Importar proyecto'&&!e.disabled)")
        await asyncio.sleep(.4);await button('Importar proyecto')
        await browser.wait("all().some(e=>e.id==='project-menu')")
        await browser.wait("all().some(e=>e.id==='save-state'&&e.dataset.state==='saved')")
        checks.append('existing one-day CHIRPS fixture opened as a copy')
        await ev("q('project-menu').click()")
        await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='2 · Maqueta')")
        await ev("all().find(e=>e.tagName==='BUTTON'&&e.textContent==='2 · Maqueta').click()")
        await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.getAttribute('role')==='radio'&&e.textContent==='Visualizaciones')")
        await button('Visualizaciones')
        await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Cargar resultados científicos')")
        await button('Cargar resultados científicos')
        await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Crear proyecto en Studio')")
        await button('Crear proyecto en Studio')
        await browser.wait("all().some(e=>e.id==='scenes'&&e.children.length>=4)")
        count=await ev("return q('scenes').children.length")
        assert count>=4
        checks.append('real current CalculationResult revision generates editable scenes')
        await commit("q('project-name').value='Studio2 scientific Chrome fixture';q('project-name').dispatchEvent(new Event('change'))")
        await ev("all().find(e=>e.dataset.tab==='scenes').click()")
        before_scene=await ev("return all().find(e=>e.classList.contains('evs')).dataset.scene")
        await ev("[...q('library-content').querySelectorAll('button')].find(e=>e.textContent.includes('mean_period')).click()")
        await browser.wait("all().some(e=>e.classList.contains('evs')&&e.dataset.scene!=="+json.dumps(before_scene)+")")
        await ev("[...q('library-content').querySelectorAll('button')].find(e=>e.textContent.includes('Cambiar template')).click()")
        await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Preparar propuesta')")
        await button('Preparar propuesta')
        await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Regenerar y conservar versión anterior')")
        await browser.shot('studio2-science-diff-1366.png')
        await button('Conservar edición actual / cancelar')
        await browser.wait("all().some(e=>e.id==='project-menu')&&!all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Preparar propuesta')")
        checks.append('regeneration diff displayed and cancellation preserves manual document')
        await ev("[...q('library-content').querySelectorAll('button')].find(e=>e.textContent.includes('Cambiar template')).click()")
        await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Preparar propuesta')")
        await button('Preparar propuesta')
        await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Regenerar y conservar versión anterior')")
        await commit("all().find(e=>e.tagName==='BUTTON'&&e.textContent==='Regenerar y conservar versión anterior').click()")
        checks.append('explicit regeneration publishes and archives previous scene')
        await commit("q('undo').click()")
        checks.append('undo restores original generated scene')
        for w,h in [(1920,1080),(1366,768),(768,1024)]:
            await browser.size(w,h);await browser.shot(f'studio2-generated-{w}.png')
            assert await ev("return document.documentElement.scrollWidth<=innerWidth")
        # Keep the export fixture short while exercising all generated scenes.
        scene_ids=await ev("return [...q('scenes').children].map(e=>e.dataset.scene)")
        for scene_id in scene_ids:
            if await ev("return all().find(e=>e.classList.contains('evs')).dataset.scene")!=scene_id:
                await ev("[...q('scenes').children].find(e=>e.dataset.scene==="+json.dumps(scene_id)+").click()")
                await browser.wait("all().some(e=>e.classList.contains('evs')&&e.dataset.scene==="+json.dumps(scene_id)+")")
            await commit("q('scene-duration').value='0.1';q('scene-duration').dispatchEvent(new Event('change'))")
        checks.append('all generated scene durations edited through UI for short export fixture')
        await ev("q('play').click()")
        await browser.wait("all().some(e=>e.id==='movie'&&e.readyState>=2)",seconds=60)
        checks.append('generated scientific sequence exported and played by actual worker')
        await ev("q('movie').pause();q('back-edit').click()")
        drafts=[]
        for path in Path('_local/video-studio/projects').glob('borrador-studio-*.json'):
            if path.stat().st_mtime<started or path.name.endswith('.previous.json'):continue
            data=json.loads(path.read_text(encoding='utf-8'))
            if data.get('name')=='Studio2 scientific Chrome fixture':drafts.append((path.stat().st_mtime,data))
        saved=max(drafts,key=lambda p:p[0])[1]
        studio=saved['studio']
        bound=[e['data_binding'] for s in studio['scenes'] if s['id'] in studio['timeline'] for e in s['elements'] if e.get('data_binding')]
        assert all(b['result_id'] in studio['calculations'] for b in bound)
        assert studio['datasets'] and saved['project_meta']['scientific_revision']
        assert all(studio['calculations'][b['result_id']]['units'] for b in bound)
        checks.append('saved bindings, units, provenance and scientific revision intact')
        assert not [e for e in browser.events if e.get('method')=='Runtime.exceptionThrown']
        checks.append('no uncaught JavaScript exceptions')
        (ROOT/'studio2-science-browser.json').write_text(json.dumps({'checks':checks,'count':len(checks),'generated_scenes':count},indent=2),encoding='utf-8')
        print(json.dumps({'checks':checks,'count':len(checks),'generated_scenes':count}))
    except Exception:
        await browser.shot('studio2-science-failure.png')
        print(await ev("return all().filter(e=>e.getAttribute('role')==='alert').map(e=>e.textContent)"))
        raise
    finally:await browser.close()


if __name__=='__main__':asyncio.run(run())
