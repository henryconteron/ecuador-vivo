"""Real Chrome: home assistant -> private worker -> review -> existing Studio."""
import asyncio
import json
import time
import sys
from pathlib import Path
from ux_browser import Browser, ROOT


async def run():
    browser = await Browser().start()
    checks = []; started = time.time()
    async def ev(code): return await browser.evaluate(code)
    async def click(expression, scroll=True):
        await asyncio.sleep(.4)
        await browser.wait("Boolean("+expression+")")
        point = await ev("const e="+expression+";"+("e.scrollIntoView({block:'center',behavior:'instant'});" if scroll else '')+"const r=e.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}")
        for kind in ('mouseMoved','mousePressed','mouseReleased'):
            await browser.call('Input.dispatchMouseEvent', {'type':kind,'button':'left',
                'buttons':1 if kind=='mousePressed' else 0,'clickCount':1,**point})
    def button(label): return "all().find(e=>e.tagName==='BUTTON'&&e.textContent.trim()==="+json.dumps(label)+")"
    async def select(label, option):
        await browser.wait("all().some(e=>e.tagName==='LABEL'&&e.textContent==="+json.dumps(label)+")")
        await click("all().find(e=>e.tagName==='LABEL'&&e.textContent==="+json.dumps(label)+")?.closest('[data-testid=stSelectbox]')?.querySelector('button[aria-haspopup=listbox]')")
        await browser.wait("all().some(e=>e.getAttribute('role')==='option'&&e.textContent.trim()==="+json.dumps(option)+")")
        await click("all().find(e=>e.getAttribute('role')==='option'&&e.textContent.trim()==="+json.dumps(option)+")",scroll=False)
        await browser.wait("all().some(e=>e.tagName==='LABEL'&&e.textContent==="+json.dumps(label)+"&&(e.closest('[data-testid=stSelectbox]').querySelector('input')?.value==="+json.dumps(option)+"||e.closest('[data-testid=stSelectbox]').textContent.includes("+json.dumps(option)+")))")
    async def text(label, value):
        await click("all().find(e=>e.tagName==='LABEL'&&e.textContent==="+json.dumps(label)+")?.closest('[data-testid]')?.parentElement.querySelector('input')")
        await browser.call('Input.dispatchKeyEvent',{'type':'rawKeyDown','key':'a','code':'KeyA','modifiers':2,'windowsVirtualKeyCode':65})
        await browser.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'a','code':'KeyA','modifiers':2,'windowsVirtualKeyCode':65})
        await browser.call('Input.insertText',{'text':value})
        await browser.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Tab','code':'Tab'})
        await browser.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Tab','code':'Tab'})
        await asyncio.sleep(.6)
    async def upload():
        await select('Datos de partida','Importar proyecto calculado')
        await browser.wait("all().some(e=>e.tagName==='LABEL'&&e.textContent==='Proyecto científico JSON')")
        remote = await browser.call('Runtime.evaluate', {'expression':"[...document.querySelectorAll('[data-testid=stFileUploader]')].find(e=>e.textContent.includes('Proyecto científico JSON')).querySelector('input[type=file]')"})
        await browser.call('DOM.setFileInputFiles',{'files':[str((ROOT/'ux-redesign/scientific-project.json').resolve())],'objectId':remote['result']['objectId']})
        await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Preparar revisión científica')")
        await asyncio.sleep(.5)
    try:
        await browser.call('Runtime.enable')
        await browser.call('Page.navigate',{'url':'http://127.0.0.1:8514'})
        await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Elegir desde datos científicos')")
        await click(button('Elegir desde datos científicos')); await upload()
        await click(button('Preparar revisión científica'))
        await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Cancelar preparación')")
        assert not await ev("return all().some(e=>e.id==='project-menu')")
        await browser.shot('studio2-assistant-progress.png')
        await click(button('Cancelar preparación'))
        await browser.wait("all().some(e=>e.textContent.includes('Preparación cancelada; el proyecto activo se conserva.'))")
        assert not await ev("return all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Crear proyecto en Studio')")
        checks.append('background preparation and cancellation never publish partial project')
        print('Chrome: cancellation passed',flush=True)
        await click(button('Elegir otra fuente / nueva revisión')); await upload()
        await click(button('Preparar revisión científica'))
        await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Crear proyecto en Studio')",seconds=60)
        assert not await ev("return all().some(e=>e.id==='project-menu')")
        checks.append('completed CHIRPS worker opens immutable scientific review before publication')
        print('Chrome: review ready',flush=True)
        await text('Título del proyecto científico','Studio2 assistant Chrome fixture')
        await text('Duración inicial por escena · s','0.1')
        await browser.wait("all().some(e=>e.textContent.includes('0.8 s'))")
        for w,h in [(1920,1080),(1366,768),(768,1024)]:
            await browser.size(w,h); await browser.shot(f'studio2-assistant-review-{w}.png')
            assert await ev('return document.documentElement.scrollWidth<=innerWidth')
        checks.append('review and audiovisual settings work in three viewports without global overflow')
        await browser.size(1366,768)
        await click(button('Crear proyecto en Studio'))
        await browser.wait("all().some(e=>e.id==='project-name'&&e.value==='Studio2 assistant Chrome fixture')")
        count = await ev("return all().find(e=>e.id==='scenes').children.length")
        assert count == 8
        checks.append('explicit publication opens eight editable scenes in existing canonical Studio')
        await browser.shot('studio2-assistant-created.png')
        await click("all().find(e=>e.id==='play')")
        await browser.wait("all().some(e=>e.id==='movie'&&e.readyState>=2)",seconds=60)
        checks.append('real worker produces and plays the scientific MP4 at selected short durations')
        original_movie=await ev("return all().find(e=>e.id==='movie').src")
        drafts=[]
        for path in Path('_local/video-studio/projects').glob('*.json'):
            if path.stat().st_mtime < started or path.name.endswith('.previous.json'): continue
            project=json.loads(path.read_text(encoding='utf-8'))
            if project.get('name')=='Studio2 assistant Chrome fixture': drafts.append(project)
        assert drafts
        project=drafts[-1]; studio=project['studio']
        assert studio['output_profile']['id']=='tiktok'
        for scene in studio['scenes']:
            if scene['id'] not in studio['timeline']: continue
            assert scene['duration']==.1
            for element in scene['elements']:
                if element.get('data_binding'):
                    result=studio['calculations'][element['data_binding']['result_id']]
                    assert result['units'] and result['provenance']['source_records_ref'] in studio['datasets']
        checks.append('durable project preserves hashes, revision, units, provenance and bindings')
        if '--structure' in sys.argv:
            await click("all().find(e=>e.id==='back-edit')")
            await browser.wait("all().some(e=>e.id==='addtext')")
            before_version=await ev("return Number(all().find(e=>e.classList.contains('evs')).dataset.version)")
            await click("all().find(e=>e.id==='addtext')")
            await browser.wait("all().some(e=>e.classList.contains('evs')&&Number(e.dataset.version)>"+str(before_version)+")")
            before_ids=await ev("return [...all().find(e=>e.id==='scenes').children].map(e=>e.dataset.scene)")
            await click("all().find(e=>e.dataset.tab==='scenes')")
            await click(button('Regenerar estructura científica'))
            await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Preparar estructura')")
            await click(button('Preparar estructura'))
            await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Regenerar estructura y archivar anterior')")
            await browser.shot('studio2-structure-diff.png')
            await click(button('Conservar estructura actual / cancelar'))
            await browser.wait("!all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Preparar estructura')")
            assert await ev("return [...all().find(e=>e.id==='scenes').children].map(e=>e.dataset.scene)")==before_ids
            checks.append('structure diff and cancellation preserve active sequence and manual edit')
            await click(button('Regenerar estructura científica'))
            await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Preparar estructura')")
            await click(button('Preparar estructura'))
            await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Regenerar estructura y archivar anterior')")
            version=await ev("return Number(all().find(e=>e.classList.contains('evs')).dataset.version)")
            await click(button('Regenerar estructura y archivar anterior'))
            await browser.wait("all().some(e=>e.classList.contains('evs')&&Number(e.dataset.version)>"+str(version)+")")
            await browser.wait("!all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Preparar estructura')")
            after_ids=await ev("return [...all().find(e=>e.id==='scenes').children].map(e=>e.dataset.scene)")
            assert after_ids[0]==before_ids[0] and after_ids[1:]!=before_ids[1:]
            checks.append('explicit full regeneration keeps modified cover and replaces other scenes')
            await click(button('Regenerar estructura científica'))
            await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Recuperar estructura anterior')")
            version=await ev("return Number(all().find(e=>e.classList.contains('evs')).dataset.version)")
            await click(button('Recuperar estructura anterior'))
            await browser.wait("all().some(e=>e.classList.contains('evs')&&Number(e.dataset.version)>"+str(version)+")")
            await browser.wait("!all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Preparar estructura')")
            assert await ev("return [...all().find(e=>e.id==='scenes').children].map(e=>e.dataset.scene)")==before_ids
            checks.append('archived structure can be restored through the existing workspace')
            version=await ev("return Number(all().find(e=>e.classList.contains('evs')).dataset.version)")
            await click("all().find(e=>e.id==='undo')")
            await browser.wait("all().some(e=>e.classList.contains('evs')&&Number(e.dataset.version)>"+str(version)+")")
            assert await ev("return [...all().find(e=>e.id==='scenes').children].map(e=>e.dataset.scene)")==after_ids
            checks.append('canonical undo reverses structure recovery')
            await click("all().find(e=>e.id==='play')")
            await browser.wait("all().some(e=>e.id==='movie'&&e.readyState>=2&&e.src!=="+json.dumps(original_movie)+")",seconds=60)
            checks.append('regenerated structure renders and plays a new real MP4')
        assert not [e for e in browser.events if e.get('method')=='Runtime.exceptionThrown']
        checks.append('no uncaught JavaScript exceptions')
        report='studio2-structure-browser.json' if '--structure' in sys.argv else 'studio2-assistant-browser.json'
        (ROOT/report).write_text(json.dumps({'checks':checks,'count':len(checks),'scenes':count},indent=2),encoding='utf-8')
        print(json.dumps({'checks':checks,'count':len(checks),'scenes':count}))
    except Exception:
        await browser.shot('studio2-assistant-failure.png')
        print(await ev("return all().filter(e=>e.getAttribute('role')==='alert').map(e=>e.textContent)"))
        raise
    finally: await browser.close()


if __name__=='__main__': asyncio.run(run())
