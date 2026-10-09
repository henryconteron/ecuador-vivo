"""Isolated real Chrome: BYOD GeoJSON -> region/view -> shared Studio."""
import asyncio
import json
from pathlib import Path
import time
from integration_sig_browser import SigBrowser,ROOT


async def run():
    browser=await SigBrowser().start();checks=[];started=time.time()
    async def ev(code):return await browser.evaluate(code)
    def button(label):return "all().find(e=>e.tagName==='BUTTON'&&e.textContent.trim().endsWith("+json.dumps(label)+"))"
    async def click(expression,scroll=True):
        await browser.wait('Boolean('+expression+')');await asyncio.sleep(.3)
        point=await ev('const e='+expression+';'+("e.scrollIntoView({block:'center',behavior:'instant'});" if scroll else '')+"const r=e.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}")
        for kind in ('mouseMoved','mousePressed','mouseReleased'):
            await browser.call('Input.dispatchMouseEvent',{'type':kind,'button':'left','buttons':1 if kind=='mousePressed' else 0,'clickCount':1,**point})
        await asyncio.sleep(.5)
    async def text(label,value):
        expression="all().find(e=>e.tagName==='LABEL'&&e.textContent==="+json.dumps(label)+")?.closest('[data-testid=stTextInput]')?.querySelector('input')"
        await click(expression)
        for kind in ('rawKeyDown','keyUp'):
            await browser.call('Input.dispatchKeyEvent',{'type':kind,'key':'a','code':'KeyA','modifiers':2,'windowsVirtualKeyCode':65})
        await browser.call('Input.insertText',{'text':value})
        for kind in ('keyDown','keyUp'):await browser.call('Input.dispatchKeyEvent',{'type':kind,'key':'Tab','code':'Tab'})
    async def upload(label,path):
        await browser.wait("all().some(e=>e.getAttribute('data-testid')==='stFileUploader'&&e.textContent.includes("+json.dumps(label)+"))")
        remote=await browser.call('Runtime.evaluate',{'expression':"[...document.querySelectorAll('[data-testid=stFileUploader]')].find(e=>e.textContent.includes("+json.dumps(label)+")).querySelector('input[type=file]')"})
        await browser.call('DOM.setFileInputFiles',{'files':[str(path.resolve())],'objectId':remote['result']['objectId']})
        await asyncio.sleep(.8)
    async def navigate(label):
        await click("all().find(e=>e.id==='project-menu')");await click(button(label))
    async def select_multipart():
        await click("all().find(e=>e.tagName==='LABEL'&&e.textContent==='Región GeoJSON')?.closest('[data-testid=stSelectbox]')?.querySelector('button[aria-haspopup=listbox]')")
        await click("all().find(e=>e.getAttribute('role')==='option'&&e.textContent.startsWith('Multipart'))",scroll=False)
        await browser.wait("all().some(e=>e.tagName==='LABEL'&&e.textContent==='Región GeoJSON'&&e.closest('[data-testid=stSelectbox]').querySelector('input')?.value.startsWith('Multipart'))")
    async def layouts(prefix):
        for w,h in [(1920,1080),(1366,768),(768,1024)]:
            await browser.size(w,h);assert await ev('return document.documentElement.scrollWidth<=innerWidth')
            if prefix=='brazil':
                await browser.wait("all().some(e=>e.tagName==='IMG'&&e.closest('[data-testid=stImage]'))")
                delta=await ev("const r=all().find(e=>e.tagName==='IMG'&&e.closest('[data-testid=stImage]')).getBoundingClientRect();return r.y+r.height/2-innerHeight/2")
                await browser.call('Input.dispatchMouseEvent',{'type':'mouseWheel','x':w/2,'y':h/2,'deltaX':0,'deltaY':delta})
                await asyncio.sleep(.5)
            await browser.shot(f'sig-g1-{prefix}-{w}.png')
        await browser.size(1920,1080)
    try:
        await browser.call('Page.navigate',{'url':'http://127.0.0.1:8516'})
        await upload('Importar proyecto JSON',ROOT/'sig-g1-browser-project.json')
        await browser.wait('!'+button('Importar proyecto')+'.disabled')
        await click(button('Importar proyecto'))
        await browser.wait("all().some(e=>e.id==='project-name'&&e.value==='Prueba SIG GeoJSON')")
        await navigate('Abrir SIG')
        await upload('Importar GeoJSON',ROOT/'sig-g1-synthetic.geojson')
        await text('Procedencia del GeoJSON','Synthetic test, no real administrative borders')
        await text('Licencia o condiciones de uso','CC0 synthetic test')
        await click(button('Importar capa al proyecto'))
        await browser.wait("all().some(e=>e.tagName==='LABEL'&&e.textContent==='Región GeoJSON')")
        assert await ev("return document.body.textContent.includes('OGC:CRS84')&&document.body.textContent.includes('Brasil')")
        await layouts('brazil')
        checks.append('GeoJSON real importado: Brasil fuera de ECU, CRS lon/lat y procedencia; tres tamaños sin overflow')
        await select_multipart();await click(button('Guardar vista geográfica'))
        await browser.wait('Boolean('+button('Enviar vista a Studio')+')')
        checks.append('Región multipart seleccionada por ID y vista RGBA persistida')
        await click(button('Enviar vista a Studio'))
        await browser.wait("all().some(e=>e.id==='scenes'&&e.children.length===2)")
        await layouts('studio')
        await navigate('Abrir SIG');await select_multipart();await click(button('Enviar vista a Studio'))
        await browser.wait("all().some(e=>e.id==='scenes'&&e.children.length===2)")
        checks.append('Mapa/título/procedencia reales en Studio; reenviar conserva escena sin duplicar')
        await click("all().find(e=>e.id==='export')");await click(button('Exportar MP4'))
        await browser.wait("all().some(e=>e.id==='movie'&&e.readyState>=2)",120)
        await click("all().find(e=>e.id==='play')")
        await browser.wait("all().some(e=>e.id==='movie'&&e.currentTime>0&&e.videoWidth===320)")
        checks.append('MP4 real 320x180 exportado y reproducido con vista fuera de Ecuador')
        drafts=[p for p in Path('_local/video-studio/projects').glob('borrador-studio-*.json') if p.stat().st_mtime>=started and not p.name.endswith('.previous.json')]
        path,document=next((p,json.loads(p.read_text(encoding='utf-8'))) for p in sorted(drafts,key=lambda p:p.stat().st_mtime,reverse=True)
            if json.loads(p.read_text(encoding='utf-8')).get('studio',{}).get('geography',{}).get('views'))
        registry=document['studio']['geography'];source=next(iter(registry['sources'].values()))
        assert Path(source['path']).read_bytes()==(ROOT/'sig-g1-synthetic.geojson').read_bytes()
        assert len(registry['regions'])==3 and len(registry['views'])==1
        assert document['studio']['calculations']=={} and document['studio']['datasets']=={}
        await navigate('Volver al inicio');await upload('Importar proyecto JSON',path)
        await browser.wait('!'+button('Importar proyecto')+'.disabled');await click(button('Importar proyecto'))
        await browser.wait("all().some(e=>e.id==='scenes'&&e.children.length===2)")
        await navigate('Abrir SIG');await select_multipart()
        await browser.wait('Boolean('+button('Enviar vista a Studio')+')')
        checks.append('Abrir copia recupera regiones/vista/atributos y bytes originales; no depende de límites ECU')
        receipts=[json.loads(p.read_text(encoding='utf-8')) for p in Path('_local/video-studio/jobs').glob('*/receipt.json') if p.stat().st_mtime>=started]
        receipt=next(r for r in receipts if r.get('geographic_views'))
        view=next(iter(registry['views'].values()))
        assert receipt['geographic_views'][0]['region_id']==view['region_id']
        assert receipt['geographic_views'][0]['source_sha256']==source['sha256']
        assert receipt['geographic_views'][0]['visibility'] and all(receipt['geographic_views'][0]['visibility'].values())
        assert not [e for e in browser.events if e.get('method')=='Runtime.exceptionThrown']
        checks.append('Receipt conserva ID/revisión/hash/CRS/geometría/transform editorial; sin excepciones JS')
        report={'checks':checks,'count':len(checks),'elapsed_seconds':time.time()-started,'draft':str(path),'geography':registry,'receipt_geographic_views':receipt['geographic_views']}
        (ROOT/'sig-g1-browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(report,ensure_ascii=False),flush=True)
    except Exception:
        await browser.shot('sig-g1-failure.png')
        print(await ev("return all().filter(e=>e.getAttribute('role')==='alert').map(e=>e.textContent)"),flush=True)
        raise
    finally:await browser.close()


if __name__=='__main__':asyncio.run(run())
