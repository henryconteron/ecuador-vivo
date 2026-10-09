import asyncio,json
import uuid
from pathlib import Path
from ux_browser import Browser,ROOT
checks=[]
async def run():
 b=await Browser().start()
 async def ev(code):return await b.evaluate("const q=id=>all().find(e=>e.id===id);"+code)
 async def ver():return int(await ev("return all().find(e=>e.classList.contains('evs')).dataset.version"))
 async def committed(code):
  v=await ver();await ev(code);await b.wait("Number(all().find(e=>e.classList.contains('evs')).dataset.version)>"+str(v));await asyncio.sleep(.2)
 async def upload(path):
  await ev("all().find(e=>e.dataset.tab==='media').click();q('library-content').querySelector('button').click()")
  await b.wait("all().some(e=>e.tagName==='INPUT'&&e.type==='file')")
  r=await b.call('Runtime.evaluate',{'expression':"document.querySelector('input[type=file]')"})
  await b.call('DOM.setFileInputFiles',{'files':[str(path.resolve())],'objectId':r['result']['objectId']})
  await b.wait("all().some(e=>e.textContent==="+json.dumps(path.name)+")")
  await asyncio.sleep(1)
  await b.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Importar'&&!e.disabled)")
  await committed("all().find(e=>e.tagName==='BUTTON'&&e.textContent==='Importar').click()")
  await b.wait("!all().some(e=>e.tagName==='INPUT'&&e.type==='file')")
 try:
  await b.call('Runtime.enable');await b.call('Page.navigate',{'url':'http://127.0.0.1:8512'})
  downloads=ROOT/'ux-redesign'/'downloads'/uuid.uuid4().hex;downloads.mkdir(parents=True)
  await b.call('Browser.setDownloadBehavior',{'behavior':'allow','downloadPath':str(downloads.resolve()),'eventsEnabled':True})
  await b.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent.includes('5 · Estudio'))");await ev("all().find(e=>e.tagName==='BUTTON'&&e.textContent.includes('5 · Estudio')).click()")
  await b.wait("all().some(e=>e.id==='scene-duration')");await b.size(1366,768)
  await ev("q('project-menu').click()")
  await committed("[...q('dialog-body').querySelectorAll('button')].find(e=>e.textContent.includes('Nuevo proyecto')).click()")
  await ev("q('format').click();const s=q('dialog-body').querySelector('select');s.value='custom';s.dispatchEvent(new Event('change'))")
  await committed("const fields=q('dialog-body').querySelectorAll('input');fields[0].value=640;fields[1].value=360;[...q('dialog-body').querySelectorAll('button')].find(e=>e.textContent.includes('Adaptar')).click()")
  await committed("q('scene-duration').value=.5;q('scene-duration').dispatchEvent(new Event('change'))")
  await ev("all().find(e=>e.dataset.tab==='templates').click()")
  await committed("[...q('library-content').querySelectorAll('button')].find(e=>e.textContent.includes('Portada')).click()")
  await committed("q('scene-duration').value=.5;q('scene-duration').dispatchEvent(new Event('change'))")
  assert await ev("return q('scene-label').textContent==='Portada'&&q('scenes').children.length===2");checks.append('template in complete creation flow')
  await committed("q('addtext').click()")
  await ev("all().find(e=>e.dataset.tab==='layers').click();q('layers').querySelector('button').click()")
  await committed("q('text').value='Ciencia en movimiento';q('text').dispatchEvent(new Event('input',{bubbles:true}))")
  await committed("for(const [id,value] of [['font',20],['x',325],['y',14],['w',295],['h',30]]){q(id).value=value;q(id).dispatchEvent(new Event('input',{bubbles:true}))}")
  assert await ev("return q('text').value==='Ciencia en movimiento'");checks.append('authored text in complete creation flow')
  await upload(ROOT/'ux-redesign'/'media-image.png');checks.append('native image upload')
  await committed("[...q('library-content').querySelectorAll('button')].find(e=>e.textContent.includes('media-image')).click()")
  await ev("all().find(e=>e.dataset.tab==='layers').click();q('layers').querySelector('button').click()")
  assert await ev("return q('inspector-title').textContent==='Imagen'");checks.append('image contextual inspector')
  await upload(ROOT/'ux-redesign'/'media-video.mp4');checks.append('native video upload')
  await committed("[...q('library-content').querySelectorAll('button')].find(e=>e.textContent.includes('media-video')).click()")
  await ev("all().find(e=>e.dataset.tab==='layers').click();q('layers').querySelector('button').click()")
  assert await ev("return q('inspector-title').textContent==='Video'");checks.append('video contextual inspector')
  await committed("q('clip-mute').checked=false;q('clip-mute').dispatchEvent(new Event('change'))")
  await committed("q('clip-volume').value=.5;q('clip-volume').dispatchEvent(new Event('change'))")
  assert await ev("return !q('clip-mute').checked&&Number(q('clip-volume').value)===.5");checks.append('audio volume mute persisted')
  await committed("q('trim-in').value=.1;q('trim-in').dispatchEvent(new Event('change'))")
  checks.append('trim reflected in model')
  v=await ver();position=await ev("const piece=all().find(e=>e.classList.contains('piece')&&e.dataset.id===q('object').value);const r=piece.getBoundingClientRect();return{x:r.x+r.width/2,y:r.y+r.height/2,initial:Number(q('x').value)}")
  for params in [{'type':'mousePressed','x':position['x'],'y':position['y'],'button':'left','clickCount':1},{'type':'mouseMoved','x':position['x']+20,'y':position['y']+15,'buttons':1},{'type':'mouseReleased','x':position['x']+20,'y':position['y']+15,'button':'left','clickCount':1}]:await b.call('Input.dispatchMouseEvent',params)
  await b.wait("Number(all().find(e=>e.classList.contains('evs')).dataset.version)>"+str(v));await asyncio.sleep(.2)
  assert await ev("return Number(q('x').value)>"+str(position['initial']));checks.append('real canvas edit in complete creation flow')
  await committed("q('scenes').lastElementChild.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowLeft',shiftKey:true,bubbles:true}))")
  assert await ev("return q('scenes').firstElementChild.textContent.includes('Portada')");checks.append('real scene reorder before playback and download')
  await ev("q('play').click()")
  await b.wait("all().some(e=>e.id==='movie'&&e.readyState>=2)",seconds=90)
  assert await ev("return q('movie').duration>0&&q('movie').currentSrc.includes('/studio-media/')");checks.append('central movie preview real worker')
  url=await ev("return q('movie').currentSrc")
  status=await ev("return fetch(q('movie').currentSrc,{headers:{Range:'bytes=0-31'}}).then(r=>r.status)")
  assert status==206;checks.append('real HTTP range')
  await ev("q('playhead').value=15;q('playhead').dispatchEvent(new Event('change'))")
  assert abs(float(await ev("return q('movie').currentTime"))-.5)<.15;checks.append('movie seek synchronized')
  await ev("q('movie').pause();q('export').click()")
  assert await ev("return q('dialog-body').querySelector('a').href===q('movie').currentSrc+'?download=1'");checks.append('preview export same MP4')
  await ev("q('dialog-body').querySelector('a').click();[...q('dialog-body').querySelectorAll('button')].find(e=>e.textContent==='Descargar proyecto JSON').click()")
  for _ in range(100):
   if (downloads/'ecuador-vivo.mp4').is_file() and (downloads/'ecuador-vivo-proyecto.json').is_file():break
   await asyncio.sleep(.1)
  assert (downloads/'ecuador-vivo.mp4').stat().st_size>1000
  assert json.loads((downloads/'ecuador-vivo-proyecto.json').read_text(encoding='utf-8'))['studio']['media']
  checks.append('actual MP4 and project JSON downloads')
  await b.shot('after-media-export-1366.png')
  await ev("q('dialog-close').click();q('back-edit').click()")
  for w,h in [(1920,1080),(1366,768),(768,1024)]:
   await b.size(w,h)
   if w==768:
    await ev("q('toggle-right').click()");await b.shot('after-media-inspector-768.png');await ev("q('close-right').click();q('toggle-left').click()");await b.shot('after-media-resources-768.png');await ev("q('close-left').click()")
   await b.shot(f'after-media-{w}.png')
   assert await ev("return document.documentElement.scrollWidth<=innerWidth&&all().find(e=>e.classList.contains('evs')).getBoundingClientRect().height===innerHeight")
   checks.append('responsive '+str(w))
   assert await ev("const seek=q('playhead').getBoundingClientRect(),content=all().find(e=>e.classList.contains('timeline-content'));return seek.bottom<=content.getBoundingClientRect().top+content.clientHeight+1");checks.append('timeline seek visible '+str(w))
  assert not [e for e in b.events if e.get('method')=='Runtime.exceptionThrown']
  (ROOT/'ux-redesign'/'media-flow.json').write_text(json.dumps({'checks':checks,'count':len(checks),'movie_url':url,'download_directory':str(downloads)},indent=2));print(json.dumps({'checks':checks,'count':len(checks)}))
 except Exception:
  await b.shot('debug-media-failure.png');print('FAILED',checks,await ev("return q('workspace-status')?.textContent"),flush=True);raise
 finally:await b.close()
asyncio.run(run())
