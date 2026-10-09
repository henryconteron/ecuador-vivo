"""Real isolated Chrome: direct Studio, SIG map preparation and shared project."""
import asyncio
import json
from pathlib import Path
import subprocess
import time
import urllib.request
import uuid
from tornado.websocket import websocket_connect
from ux_browser import Browser, ROOT, CHROME


class SigBrowser(Browser):
    async def start(self):
        self.process = subprocess.Popen([str(CHROME),'--headless=new','--no-first-run',
            '--no-default-browser-check','--remote-debugging-port=9224',
            f'--user-data-dir={ROOT / ("sig-studio-chrome-"+uuid.uuid4().hex[:8])}',
            '--window-size=1920,1080','about:blank'],creationflags=subprocess.CREATE_NO_WINDOW)
        for _ in range(60):
            try:
                tabs=json.load(urllib.request.urlopen('http://127.0.0.1:9224/json'));break
            except OSError: await asyncio.sleep(.25)
        self.ws=await websocket_connect(next(t['webSocketDebuggerUrl'] for t in tabs if t['type']=='page'))
        self.n=0;self.events=[]
        await self.call('Page.enable');await self.call('Runtime.enable')
        return self


async def run():
    browser=await SigBrowser().start(); checks=[]; started=time.time()
    async def ev(code): return await browser.evaluate(code)
    def button(label): return "all().find(e=>e.tagName==='BUTTON'&&e.textContent.trim().endsWith("+json.dumps(label)+"))"
    async def click(expression, scroll=True):
        await browser.wait('Boolean('+expression+')');await asyncio.sleep(.3)
        point=await ev('const e='+expression+';'+("e.scrollIntoView({block:'center',behavior:'instant'});" if scroll else '')+"const r=e.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}")
        for kind in ('mouseMoved','mousePressed','mouseReleased'):
            await browser.call('Input.dispatchMouseEvent',{'type':kind,'button':'left','buttons':1 if kind=='mousePressed' else 0,'clickCount':1,**point})
        await asyncio.sleep(.5)
    async def text(expression,value):
        await click(expression)
        for kind in ('rawKeyDown','keyUp'):
            await browser.call('Input.dispatchKeyEvent',{'type':kind,'key':'a','code':'KeyA','modifiers':2,'windowsVirtualKeyCode':65})
        await browser.call('Input.insertText',{'text':value})
        for kind in ('keyDown','keyUp'): await browser.call('Input.dispatchKeyEvent',{'type':kind,'key':'Tab','code':'Tab'})
        await asyncio.sleep(.7)
    async def navigate(label):
        await click("all().find(e=>e.id==='project-menu')")
        await click(button(label))
    async def layouts(prefix):
        for w,h in [(1920,1080),(1366,768),(768,1024)]:
            await browser.size(w,h)
            assert await ev('return document.documentElement.scrollWidth<=innerWidth')
            await browser.shot(f'sig-studio-{prefix}-{w}.png')
        await browser.size(1920,1080)
    try:
        await browser.call('Page.navigate',{'url':'http://127.0.0.1:8516'})
        await click(button('Elegir proyecto libre'))
        await click("all().find(e=>e.tagName==='LABEL'&&e.textContent==='Formato de salida')?.closest('[data-testid=stSelectbox]')?.querySelector('button[aria-haspopup=listbox]')")
        await browser.wait("all().some(e=>e.getAttribute('role')==='option'&&e.textContent.trim()==='YouTube')")
        await click("all().find(e=>e.getAttribute('role')==='option'&&e.textContent.trim()==='YouTube')", scroll=False)
        await browser.wait("all().some(e=>e.tagName==='LABEL'&&e.textContent==='Formato de salida'&&(e.closest('[data-testid=stSelectbox]').querySelector('input')?.value==='YouTube'||e.closest('[data-testid=stSelectbox]').textContent.includes('YouTube')))")
        await click(button('Crear proyecto en Studio'))
        await browser.wait("all().some(e=>e.id==='project-name')")
        await browser.wait("all().some(e=>e.id==='resolution'&&e.textContent.includes('1920'))")
        await click("all().find(e=>e.id==='addtext')")
        await browser.wait("all().some(e=>e.id==='undo'&&!e.disabled)")
        checks.append('Studio directo YouTube sin SIG; texto editable y autosave')
        await navigate('Abrir SIG')
        await browser.wait("all().some(e=>e.tagName==='H1'&&e.textContent.includes('SIG'))")
        await layouts('free-sig')
        await click(button('Abrir Studio'))
        await browser.wait("all().some(e=>e.id==='undo'&&!e.disabled)")
        checks.append('SIG/Studio conserva escena libre e historial; tres tamaños SIG')
        await navigate('Volver al inicio')
        await browser.wait("all().some(e=>e.tagName==='LABEL'&&e.textContent==='Importar proyecto JSON')")
        remote=await browser.call('Runtime.evaluate',{'expression':"[...document.querySelectorAll('[data-testid=stFileUploader]')].find(e=>e.textContent.includes('Importar proyecto JSON')).querySelector('input[type=file]')"})
        await browser.call('DOM.setFileInputFiles',{'files':[str(ROOT/'studio2-temporal-browser-project.json')],'objectId':remote['result']['objectId']})
        await browser.wait('!'+button('Importar proyecto')+'.disabled')
        await click(button('Importar proyecto'))
        await browser.wait("all().some(e=>e.id==='project-name'&&e.value.includes('Prueba temporal'))")
        before=await ev("return all().find(e=>e.id==='scenes').children.length")
        await navigate('Abrir SIG')
        await click(button('Preparar mapa temporal'))
        await click(button('Preparar mapa desde datos'))
        await browser.wait('Boolean('+button('Enviar mapa a Studio')+')',120)
        await layouts('map-review')
        await click(button('Enviar mapa a Studio'))
        await browser.wait("all().some(e=>e.id==='scenes'&&e.children.length==="+str(before+1)+")")
        checks.append('SIG prepara mapa real 4a y lo envía con escena al documento compartido')
        await navigate('Abrir SIG')
        await browser.wait("all().some(e=>e.tagName==='LABEL'&&e.textContent==='Mapas del proyecto')")
        assert await ev("return document.body.textContent.includes('2025-01-01')")
        await click(button('Enviar mapa a Studio'))
        await browser.wait("all().some(e=>e.id==='scenes'&&e.children.length==="+str(before+1)+")")
        checks.append('Volver a SIG mantiene mapa/fechas; reenviar reutiliza escena sin duplicarla')
        await layouts('inserted')
        await click("all().find(e=>e.id==='export')")
        await click(button('Exportar MP4'))
        await browser.wait("all().some(e=>e.id==='movie'&&e.getAttribute('src'))",120)
        await browser.wait("all().some(e=>e.id==='movie'&&e.readyState>=2)")
        await click("all().find(e=>e.id==='play')")
        await browser.wait("all().some(e=>e.id==='movie'&&e.currentTime>0&&e.videoWidth>0)")
        checks.append('MP4 real exportado y reproducido en Studio; tres tamaños sin overflow')
        projects=Path('_local/video-studio/projects')
        drafts=[p for p in projects.glob('borrador-studio-*.json') if p.stat().st_mtime>=started and not p.name.endswith('.previous.json')]
        candidates=[(p,json.loads(p.read_text(encoding='utf-8'))) for p in drafts]
        path,document=next((p,d) for p,d in candidates if d.get('name','').startswith('Prueba temporal') and d['studio']['media'])
        original=json.loads((ROOT/'studio2-temporal-browser-project.json').read_text(encoding='utf-8'))
        assert document['studio']['calculations']==original['studio']['calculations']
        assert document['studio']['datasets']==original['studio']['datasets']
        assert len(document['studio']['timeline'])==len(original['studio']['timeline'])+1
        receipts=[]
        for p in Path('_local/video-studio/jobs').glob('*/receipt.json'):
            if p.stat().st_mtime>=started:
                r=json.loads(p.read_text(encoding='utf-8'))
                if r.get('scientific_calendar'): receipts.append(r)
        assert receipts and receipts[-1]['scientific_calendar'][0]['intervals'][-1]['date']=='2025-01-03'
        assert not [e for e in browser.events if e.get('method')=='Runtime.exceptionThrown']
        checks.append('Autosave, hashes, cálculos y calendario de exportación intactos; sin excepciones JS')
        report={'checks':checks,'count':len(checks),'draft':str(path),'elapsed_seconds':time.time()-started,'receipt_calendar':receipts[-1]['scientific_calendar']}
        (ROOT/'sig-studio-first-browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(report,ensure_ascii=False),flush=True)
    except Exception:
        await browser.shot('sig-studio-first-failure.png')
        print(await ev("return all().filter(e=>e.getAttribute('role')==='alert').map(e=>e.textContent)"),flush=True)
        raise
    finally: await browser.close()


if __name__=='__main__': asyncio.run(run())
