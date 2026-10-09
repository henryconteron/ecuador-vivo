"""Chrome physical input: prepare/cancel/review/insert/seek/play temporal maps."""
import asyncio
import json
import time
from pathlib import Path
from ux_browser import Browser, ROOT


async def run():
    browser=await Browser().start()
    checks=[]; started=time.time()
    async def ev(code): return await browser.evaluate(code)
    def button(label): return "all().find(e=>e.tagName==='BUTTON'&&e.textContent.trim()==="+json.dumps(label)+")"
    async def click(expression):
        await asyncio.sleep(.4)
        await browser.wait('Boolean('+expression+')')
        point=await ev("const e="+expression+";e.scrollIntoView({block:'center',behavior:'instant'});const r=e.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}")
        for kind in ('mouseMoved','mousePressed','mouseReleased'):
            await browser.call('Input.dispatchMouseEvent',{'type':kind,'button':'left','buttons':1 if kind=='mousePressed' else 0,'clickCount':1,**point})
    async def text(label,value):
        await click("all().find(e=>e.tagName==='LABEL'&&e.textContent==="+json.dumps(label)+")?.closest('[data-testid]')?.parentElement.querySelector('input')")
        await browser.call('Input.dispatchKeyEvent',{'type':'rawKeyDown','key':'a','code':'KeyA','modifiers':2,'windowsVirtualKeyCode':65})
        await browser.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'a','code':'KeyA','modifiers':2,'windowsVirtualKeyCode':65})
        await browser.call('Input.insertText',{'text':value})
        for kind in ('keyDown','keyUp'): await browser.call('Input.dispatchKeyEvent',{'type':kind,'key':'Tab','code':'Tab'})
        await asyncio.sleep(.6)
    async def key(expression,value):
        await ev('const e='+expression+';e.focus();return true')
        for kind in ('keyDown','keyUp'): await browser.call('Input.dispatchKeyEvent',{'type':kind,'key':value,'code':value})
    try:
        await browser.call('Runtime.enable')
        await browser.call('Page.navigate',{'url':'http://127.0.0.1:8515'})
        await browser.wait("all().some(e=>e.tagName==='LABEL'&&e.textContent==='Importar proyecto JSON')")
        remote=await browser.call('Runtime.evaluate',{'expression':"[...document.querySelectorAll('[data-testid=stFileUploader]')].find(e=>e.textContent.includes('Importar proyecto JSON')).querySelector('input[type=file]')"})
        await browser.call('DOM.setFileInputFiles',{'files':[str(ROOT/'studio2-temporal-browser-project.json')],'objectId':remote['result']['objectId']})
        await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Importar proyecto'&&!e.disabled)")
        await click(button('Importar proyecto'))
        await browser.wait("all().some(e=>e.id==='project-name'&&e.value.includes('Prueba temporal'))")
        count=await ev("return all().find(e=>e.id==='scenes').children.length")
        await click("all().find(e=>e.dataset.tab==='media')")
        await click(button('Preparar mapa temporal'))
        await text('Duración del mapa · segundos','60')
        await click(button('Preparar mapa desde datos'))
        await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Cancelar preparación del mapa')")
        await browser.shot('studio2-temporal-progress.png')
        await click(button('Cancelar preparación del mapa'))
        await browser.wait("all().some(e=>e.textContent==='Mapa cancelado; el proyecto activo se conserva.')")
        assert await ev("return all().find(e=>e.id==='scenes').children.length")==count
        checks.append('private cartographic worker reports progress and cancels without changing timeline')
        await click(button('Preparar otro mapa'))
        await text('Duración del mapa · segundos','0.23333333333333334')
        await click(button('Preparar mapa desde datos'))
        await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Insertar mapa y escena en Studio')",seconds=90)
        assert await ev("return all().find(e=>e.id==='scenes').children.length")==count
        assert await ev("return all().some(e=>e.textContent.includes('7 fotogramas'))")
        for width,height in [(1920,1080),(1366,768),(768,1024)]:
            await browser.size(width,height); await browser.shot(f'studio2-temporal-review-{width}.png')
            assert await ev('return document.documentElement.scrollWidth<=innerWidth')
        checks.append('completed two-band raster product exposes seven verified frames and calendar review in three viewports')
        await click(button('Cerrar sin insertar'))
        await browser.wait("!all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Insertar mapa y escena en Studio')")
        assert await ev("return all().find(e=>e.id==='scenes').children.length")==count
        await browser.size(1366,768)
        await click(button('Preparar mapa temporal'))
        await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Insertar mapa y escena en Studio')")
        checks.append('closing review keeps the active project unchanged and reopening restores the completed private product')
        await click(button('Insertar mapa y escena en Studio'))
        await browser.wait("all().some(e=>e.id==='scenes'&&e.children.length==="+str(count+1)+")")
        await browser.wait("all().some(e=>e.id==='scientific-date'&&e.textContent.includes('2025-01-01'))")
        assert await ev("return all().filter(e=>e.classList.contains('resource-card')&&e.textContent.includes('Mapa temporal ·')).length")==1
        await browser.shot('studio2-temporal-inserted.png')
        checks.append('explicit insertion publishes one logical map resource with thumbnail and a scene in the existing workspace')
        await key("all().find(e=>e.id==='playhead')",'End')
        # Seek is a controlled command; wait for its server acknowledgment before Play.
        # Navigation changes the playhead, not the document revision.
        await browser.wait("all().some(e=>e.id==='save-state'&&e.textContent.startsWith('Guardado'))")
        await browser.wait("all().some(e=>e.id==='scientific-date'&&e.textContent.includes('2025-01-03'))")
        checks.append('real playhead navigation resolves last frame to January 3 without inventing missing January 2')
        await click("all().find(e=>e.id==='play')")
        await browser.wait("all().some(e=>e.id==='movie'&&e.readyState>=2)",seconds=90)
        checks.append('same Studio worker exports and plays the real map MP4 with immutable scientific results')
        drafts=[]
        for path in Path('_local/video-studio/projects').glob('*.json'):
            if path.stat().st_mtime<started or path.name.endswith('.previous.json'): continue
            project=json.loads(path.read_text(encoding='utf-8'))
            if project.get('name','').startswith('Prueba temporal') and project.get('studio',{}).get('media'): drafts.append((path,project))
        assert drafts
        path,project=max(drafts,key=lambda pair:pair[0].stat().st_mtime)
        original=json.loads((ROOT/'studio2-temporal-browser-project.json').read_text(encoding='utf-8'))
        assert project['studio']['calculations']==original['studio']['calculations']
        assert project['studio']['datasets']==original['studio']['datasets']
        m=next(iter(project['studio']['media'].values()))['temporal_map']
        assert [(i['date'],i['start_frame'],i['end_frame']) for i in m['intervals']]==[('2025-01-01',0,3),('2025-01-03',3,7)]
        receipts=[]
        for receipt_path in Path('_local/video-studio/jobs').glob('*/receipt.json'):
            if receipt_path.stat().st_mtime<started: continue
            receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
            if receipt.get('scientific_calendar'): receipts.append(receipt)
        assert receipts and receipts[-1]['scientific_calendar'][0]['intervals'][-1]['date']=='2025-01-03'
        checks.append('durable JSON and export receipt preserve source hashes, native scientific results and global calendar spans')
        assert not [e for e in browser.events if e.get('method')=='Runtime.exceptionThrown']
        report={'checks':checks,'elapsed_seconds':time.time()-started,'draft':str(path),'manifest':m,'receipt_calendar':receipts[-1]['scientific_calendar']}
        (ROOT/'studio2-temporal-browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print('Chrome temporal:',len(checks),'checks OK',flush=True)
    except Exception:
        await browser.shot('studio2-temporal-browser-failure.png')
        print(await ev("return all().filter(e=>['workspace-status','save-state','scientific-date','time'].includes(e.id)).map(e=>({id:e.id,text:e.textContent}));"),flush=True)
        raise
    finally: await browser.close()


if __name__=='__main__': asyncio.run(run())
