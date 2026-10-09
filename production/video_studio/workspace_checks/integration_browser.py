"""Studio 2.0 home/create/navigation, real Chrome against local port 8513."""
import asyncio
import json
from ux_browser import Browser, ROOT


async def run():
    browser=await Browser().start();checks=[]
    async def ev(code):return await browser.evaluate("const q=id=>all().find(e=>e.id===id);"+code)
    async def commit(code):
        before=await ev("return Number(all().find(e=>e.classList.contains('evs')).dataset.version)")
        await ev(code)
        await browser.wait("Number(all().find(e=>e.classList.contains('evs')).dataset.version)>"+str(before))
    try:
        await browser.call('Runtime.enable')
        await browser.call('Page.navigate',{'url':'http://127.0.0.1:8513'})
        await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent.includes('Crear proyecto'))")
        checks.append('new sessions open home without cartographic forms')
        for w,h in [(1920,1080),(1366,768),(768,1024)]:
            await browser.size(w,h)
            assert await ev("return document.documentElement.scrollWidth<=innerWidth")
            await browser.shot(f'studio2-home-{w}.png')
        checks.append('home in three sizes without global horizontal overflow')
        await ev("all().find(e=>e.tagName==='BUTTON'&&e.textContent==='Elegir proyecto libre').click()")
        await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Crear proyecto en Studio')")
        # Native Streamlit selectbox exposes its current value through an input.
        point=await ev("const label=all().find(e=>e.tagName==='LABEL'&&e.textContent==='Formato de salida');const select=label.closest('[data-testid=stSelectbox]').querySelector('button[aria-haspopup=listbox]');select.scrollIntoView({block:'center'});const r=select.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}")
        await browser.call('Input.dispatchMouseEvent',{'type':'mousePressed','button':'left','clickCount':1,**point})
        await browser.call('Input.dispatchMouseEvent',{'type':'mouseReleased','button':'left','clickCount':1,**point})
        await browser.wait("all().some(e=>e.getAttribute('role')==='option'&&e.textContent.includes('YouTube'))")
        await ev("all().find(e=>e.getAttribute('role')==='option'&&e.textContent.trim()==='YouTube').click()")
        await ev("all().find(e=>e.tagName==='BUTTON'&&e.textContent==='Crear proyecto en Studio').click()")
        await browser.wait("all().some(e=>e.id==='project-name')")
        assert await ev("return q('resolution').textContent.includes('1920')")
        checks.append('free YouTube project created directly into Studio')
        await commit("q('addtext').click()")
        await commit("q('project-name').value='Studio2 free Chrome fixture';q('project-name').dispatchEvent(new Event('change'))")
        checks.append('free scene edited and autosaved')
        await ev("q('project-menu').click();[...q('dialog-body').querySelectorAll('button')].find(e=>e.textContent==='Volver al inicio').click()")
        await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent.includes('Continuar en Studio'))")
        await ev("all().find(e=>e.tagName==='BUTTON'&&e.textContent.includes('Continuar en Studio')).click()")
        await browser.wait("all().some(e=>e.id==='project-name')")
        assert await ev("return q('project-name').value==='Studio2 free Chrome fixture'&&!q('undo').disabled")
        checks.append('home round trip preserves document and history')
        for w,h in [(1920,1080),(1366,768),(768,1024)]:
            await browser.size(w,h)
            assert await ev("return document.documentElement.scrollWidth<=innerWidth")
            await browser.shot(f'studio2-free-{w}.png')
        checks.append('free workspace in three requested sizes')
        assert not [event for event in browser.events if event.get('method')=='Runtime.exceptionThrown']
        checks.append('no uncaught JavaScript exceptions')
        (ROOT/'studio2-home-browser.json').write_text(json.dumps({'checks':checks,'count':len(checks)},indent=2),encoding='utf-8')
        print(json.dumps({'checks':checks,'count':len(checks)}))
    except Exception:
        await browser.shot('studio2-home-failure.png')
        print(await ev("return all().filter(e=>e.getAttribute('role')==='alert').map(e=>e.textContent)"))
        raise
    finally:await browser.close()


if __name__=='__main__':asyncio.run(run())
