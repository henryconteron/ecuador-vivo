import asyncio,json
from ux_browser import Browser,ROOT

async def run():
    b=await Browser().start()
    try:
        await b.call('Runtime.enable')
        await b.call('Page.navigate',{'url':'http://127.0.0.1:8512'})
        await b.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent.includes('5 · Estudio'))")
        await b.evaluate("all().find(e=>e.tagName==='BUTTON'&&e.textContent.includes('5 · Estudio')).click()")
        await b.wait("all().some(e=>e.id==='scene-duration')")
        metrics=[]
        for w,h in [(1920,1080),(1366,768),(768,1024)]:
            await b.size(w,h);await b.shot(f'after-shell-{w}.png')
            metrics.append(await b.evaluate("const rect=sel=>{const r=all().find(e=>e.matches(sel)).getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height}};return{width:innerWidth,height:innerHeight,canvas:rect('.stage'),workspace:rect('.evs'),left:rect('.layers-panel'),inspector:rect('.inspector'),timeline:rect('.timeline'),error:all().filter(e=>e.id==='workspace-status').map(e=>e.textContent),scrollWidth:document.documentElement.scrollWidth}"))
        print(json.dumps(metrics));(ROOT/'ux-redesign'/'shell.json').write_text(json.dumps(metrics,indent=2))
        errors=[e for e in b.events if e.get('method')=='Runtime.exceptionThrown'];print('JS_ERRORS',json.dumps(errors))
    finally:await b.close()
asyncio.run(run())
