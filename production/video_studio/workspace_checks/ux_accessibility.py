import asyncio,json
from ux_browser import Browser,ROOT
checks=[]
async def run():
 b=await Browser().start()
 async def ev(code):return await b.evaluate("const q=id=>all().find(e=>e.id===id);"+code)
 async def check(expression,label):
  assert await ev('return '+expression),label;checks.append(label)
 async def version():return int(await ev("return all().find(e=>e.classList.contains('evs')).dataset.version"))
 async def commit(code):
  v=await version();await ev(code);await b.wait("Number(all().find(e=>e.classList.contains('evs')).dataset.version)>"+str(v));await asyncio.sleep(.2)
 try:
  await b.call('Runtime.enable');await b.call('Page.navigate',{'url':'http://127.0.0.1:8512'})
  await b.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent.includes('5 · Estudio'))");await ev("all().find(e=>e.tagName==='BUTTON'&&e.textContent.includes('5 · Estudio')).click()")
  await b.wait("all().some(e=>e.id==='scene-duration')");await b.size(1366,768)
  await check("all().find(e=>e.classList.contains('evs')).querySelectorAll('button').length>20",'integrated tools mounted')
  await check("all().find(e=>e.classList.contains('evs')).querySelectorAll('button').values().every(e=>!e.getClientRects().length||!!(e.getAttribute('aria-label')||e.textContent.trim()))",'all visible buttons named')
  await ev("q('layers').querySelector('button').focus()")
  await b.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Tab','code':'Tab','windowsVirtualKeyCode':9})
  await b.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Tab','code':'Tab','windowsVirtualKeyCode':9})
  await check("getComputedStyle(q('layers').getRootNode().activeElement).outlineStyle!=='none'",'keyboard focus visible')
  await ev("q('layers').querySelector('button').click()")
  await check("q('layers').querySelector('button').getAttribute('aria-pressed')==='true'",'selection accessible state')
  await check("all().filter(e=>e.classList.contains('handle')).length===1",'one current resize handle')
  await ev("q('zoom').value='200';q('zoom').dispatchEvent(new Event('change'))")
  await check("all().find(e=>e.classList.contains('stage')).getBoundingClientRect().width>1000",'200 percent zoom')
  vp=await ev("const r=all().find(e=>e.classList.contains('viewport')).getBoundingClientRect();return{x:r.x+r.width/2,y:r.y+r.height/2}")
  for args in [{'type':'mousePressed','x':vp['x'],'y':vp['y'],'button':'left','clickCount':1,'modifiers':1},{'type':'mouseMoved','x':vp['x']-80,'y':vp['y']-40,'buttons':1,'modifiers':1},{'type':'mouseReleased','x':vp['x']-80,'y':vp['y']-40,'button':'left','clickCount':1,'modifiers':1}]:await b.call('Input.dispatchMouseEvent',args)
  await check("all().find(e=>e.classList.contains('viewport')).scrollLeft>0",'real Alt drag pan')
  await ev("q('zoom').value='fit';q('zoom').dispatchEvent(new Event('change'))")
  await check("all().find(e=>e.classList.contains('stage')).getBoundingClientRect().height<=all().find(e=>e.classList.contains('viewport')).clientHeight",'fit viewport')
  await ev("q('guides').checked=false;q('guides').dispatchEvent(new Event('change'))")
  await check("getComputedStyle(all().find(e=>e.classList.contains('guide'))).display==='none'",'guides toggle')
  await ev("q('guides').checked=true;q('guides').dispatchEvent(new Event('change'))")
  await ev("q('canvas-stage').focus()")
  for i in range(2):
   v=await version();await b.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'ArrowRight','code':'ArrowRight','windowsVirtualKeyCode':39});await b.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'ArrowRight','code':'ArrowRight','windowsVirtualKeyCode':39});await b.wait("Number(all().find(e=>e.classList.contains('evs')).dataset.version)>"+str(v));await asyncio.sleep(.3)
  await check("q('canvas-stage').getRootNode().activeElement===q('canvas-stage')",'stage focus survives consecutive autosaves')
  await ev("const d=[...all().find(e=>e.classList.contains('inspector')).querySelectorAll('details')].find(e=>e.textContent.includes('Animación'));d.open=true")
  await commit("q('font-family').value='Lora';q('font-family').dispatchEvent(new Event('change'))")
  await check("[...all().find(e=>e.classList.contains('inspector')).querySelectorAll('details')].find(e=>e.querySelector('summary').textContent==='Animación').open",'inspector sections survive rerun')
  await ev("q('locked').checked=true;q('locked').dispatchEvent(new Event('change'))")
  await asyncio.sleep(.7)
  await ev("q('layers').querySelectorAll('.layer-row')[0].querySelectorAll('button')[2].click()")
  await asyncio.sleep(.7)
  for profile,ratio in [('youtube',16/9),('instagram_square',1),('tiktok',9/16)]:
   await ev("q('format').click();q('dialog-body').querySelector('select').value="+json.dumps(profile))
   await commit("[...q('dialog-body').querySelectorAll('button')].find(e=>e.textContent.includes('Adaptar')).click()")
   await check("Math.abs(all().find(e=>e.classList.contains('stage')).getBoundingClientRect().width/all().find(e=>e.classList.contains('stage')).getBoundingClientRect().height-"+str(ratio)+")<.02",'native ratio '+profile)
  await ev("q('timeline-collapse').click()")
  await check("getComputedStyle(all().find(e=>e.classList.contains('timeline-content'))).display==='none'",'timeline collapse')
  await ev("q('timeline-collapse').click()")
  for w,h in [(1920,1080),(1366,768),(768,1024)]:
   await b.size(w,h);await b.shot(f'after-final-{w}.png')
   await check("document.documentElement.scrollWidth===innerWidth",'no horizontal overflow '+str(w))
   await check("all().find(e=>e.classList.contains('timeline')).getBoundingClientRect().bottom<=innerHeight",'timeline inside viewport '+str(w))
   if w>1000:await check("all().filter(e=>e.matches('.layers-panel,.inspector,.stage')).every(e=>e.getBoundingClientRect().height>0&&e.getBoundingClientRect().bottom<=innerHeight)",'five visible regions '+str(w))
   else:
    await ev("q('toggle-right').click()");await check("all().find(e=>e.classList.contains('inspector')).getBoundingClientRect().width>0",'narrow inspector drawer');await ev("q('close-right').click();q('toggle-left').click()");await check("all().find(e=>e.classList.contains('layers-panel')).getBoundingClientRect().width>0",'narrow resources drawer');await ev("q('close-left').click()")
  errors=[e for e in b.events if e.get('method')=='Runtime.exceptionThrown'];assert not errors,errors
  (ROOT/'ux-redesign'/'accessibility.json').write_text(json.dumps({'checks':checks,'count':len(checks)},indent=2));print(json.dumps({'checks':checks,'count':len(checks)}))
 except Exception:
  await b.shot('debug-accessibility-failure.png');print('FAILED',checks,await ev("return q('workspace-status')?.textContent"),flush=True);raise
 finally:await b.close()
asyncio.run(run())
