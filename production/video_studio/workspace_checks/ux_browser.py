"""Task-local real Chrome CDP, using installed Tornado; no added dependency."""
import asyncio, base64, json, subprocess, sys, time, urllib.request
from pathlib import Path
from tornado.websocket import websocket_connect

ROOT=Path(__file__).resolve().parents[3]/'tmp'
CHROME=Path('C:/Program Files/Google/Chrome/Application/chrome.exe')
DEEP="""function all(r=document){return [...r.querySelectorAll('*')].flatMap(e=>[e,...(e.shadowRoot?all(e.shadowRoot):[])])};"""
class Browser:
    async def start(self):
        self.process=subprocess.Popen([str(CHROME),'--headless=new','--no-first-run','--no-default-browser-check','--remote-debugging-port=9223',f'--user-data-dir={ROOT / "ux-redesign-chrome"}','--window-size=1920,1080','about:blank'],creationflags=subprocess.CREATE_NO_WINDOW)
        for _ in range(60):
            try:
                tabs=json.load(urllib.request.urlopen('http://127.0.0.1:9223/json'));break
            except OSError: await asyncio.sleep(.25)
        self.ws=await websocket_connect(next(t['webSocketDebuggerUrl'] for t in tabs if t['type']=='page'))
        self.n=0;self.events=[]
        await self.call('Page.enable')
        return self
    async def call(self, method, params=None):
        self.n+=1; ident=self.n
        await self.ws.write_message(json.dumps({'id':ident,'method':method,'params':params or {}}))
        while True:
            raw=await self.ws.read_message()
            value=json.loads(raw)
            if 'method' in value:self.events.append(value)
            if value.get('id')==ident:
                if 'error' in value: raise RuntimeError(value['error'])
                return value.get('result',{})
    async def evaluate(self, code):
        r=await self.call('Runtime.evaluate',{'expression':'(()=>{'+DEEP+code+'})()','returnByValue':True,'awaitPromise':True})
        if 'exceptionDetails' in r: raise RuntimeError(r['exceptionDetails'])
        return r.get('result',{}).get('value')
    async def wait(self, expression, seconds=60):
        until=time.monotonic()+seconds
        while time.monotonic()<until:
            if await self.evaluate('return '+expression): return
            await asyncio.sleep(.25)
        raise TimeoutError(expression)
    async def size(self,w,h):
        await self.call('Emulation.setDeviceMetricsOverride',{'width':w,'height':h,'deviceScaleFactor':1,'mobile':False})
        await asyncio.sleep(.6)
    async def shot(self,name):
        result=await self.call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})
        (ROOT/'ux-redesign').mkdir(exist_ok=True)
        (ROOT/'ux-redesign'/name).write_bytes(base64.b64decode(result['data']))
    async def close(self):
        self.ws.close(); self.process.terminate()

async def before():
    b=await Browser().start()
    try:
        await b.call('Page.navigate',{'url':'http://127.0.0.1:8512'})
        await b.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent.includes('5 · Estudio'))")
        await b.evaluate("all().find(e=>e.tagName==='BUTTON'&&e.textContent.includes('5 · Estudio')).click()")
        await b.wait("all().some(e=>e.id==='apply')")
        metrics=[]
        for w,h in [(1920,1080),(1366,768),(768,1024)]:
            await b.size(w,h)
            await b.evaluate('window.scrollTo(0,0)')
            await b.shot(f'before-{w}.png')
            metrics.append(await b.evaluate("const s=all().find(e=>e.classList.contains('stage'));const r=s.getBoundingClientRect();return {width:innerWidth,height:innerHeight,scrollHeight:document.documentElement.scrollHeight,canvas:{x:r.x,y:r.y,width:r.width,height:r.height}}"))
        (ROOT/'ux-redesign'/'before.json').write_text(json.dumps(metrics,indent=2))
        print(json.dumps(metrics))
    finally: await b.close()
if __name__=='__main__':asyncio.run(before())
