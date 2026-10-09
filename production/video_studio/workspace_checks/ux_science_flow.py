import asyncio,json
from pathlib import Path
from ux_browser import Browser,ROOT
checks=[]
async def run():
 b=await Browser().start()
 async def ev(code):return await b.evaluate("const q=id=>all().find(e=>e.id===id);"+code)
 async def version():return int(await ev("return all().find(e=>e.classList.contains('evs')).dataset.version"))
 async def commit(code):
  v=await version();await ev(code);await b.wait("Number(all().find(e=>e.classList.contains('evs')).dataset.version)>"+str(v));await asyncio.sleep(.2)
 try:
  await b.call('Runtime.enable');await b.call('Page.navigate',{'url':'http://127.0.0.1:8512'})
  await b.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent.includes('5 · Estudio'))");await ev("all().find(e=>e.tagName==='BUTTON'&&e.textContent.includes('5 · Estudio')).click()")
  await b.wait("all().some(e=>e.id==='scene-duration')");await b.size(1366,768)
  await ev("q('project-menu').click();[...q('dialog-body').querySelectorAll('button')].find(e=>e.textContent==='Abrir proyecto JSON').click()")
  await b.wait("all().some(e=>e.tagName==='INPUT'&&e.type==='file')")
  remote=await b.call('Runtime.evaluate',{'expression':"document.querySelector('input[type=file]')"})
  await b.call('DOM.setFileInputFiles',{'files':[str((ROOT/'ux-redesign'/'scientific-project.json').resolve())],'objectId':remote['result']['objectId']})
  await b.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent==='Importar'&&!e.disabled)");await asyncio.sleep(1)
  await commit("all().find(e=>e.tagName==='BUTTON'&&e.textContent==='Importar').click()")
  checks.append('import existing science snapshot')
  await ev("all().find(e=>e.dataset.tab==='data').click()")
  assert await ev("return q('library-content').querySelectorAll('details').length===6");checks.append('six real CalculationResult exposed')
  await ev("all().find(e=>e.dataset.tab==='layers').click();[...q('layers').querySelectorAll('.layer-row')].find(e=>e.dataset.layer==='metric').querySelector('button').click()")
  assert await ev("return q('inspector-title').textContent==='Métrica'");checks.append('scientific contextual inspector')
  await ev("[...q('context-fields').querySelectorAll('summary')].find(e=>e.textContent.includes('Unidades y fuentes')).click()")
  assert await ev("return q('context-fields').textContent.includes('mm/día')&&q('context-fields').textContent.includes('spatial_operation')");checks.append('units provenance accessible')
  await commit("const label=[...q('context-fields').querySelectorAll('label')].find(e=>e.firstChild.textContent==='Tinta');const input=label.querySelector('input');input.value='#71dcc8';input.dispatchEvent(new Event('change'))")
  checks.append('scientific appearance edited without recalculation')
  await commit("q('font-family').value='Atkinson Hyperlegible';q('font-family').dispatchEvent(new Event('change'))")
  await b.shot('after-science-1366.png')
  await ev("q('play').click()")
  await b.wait("all().some(e=>e.id==='movie'&&e.readyState>=2)",seconds=90);checks.append('science project worker playback')
  await ev("q('movie').pause();q('back-edit').click();q('project-menu').click()")
  choice=await ev("return q('dialog-body').querySelector('select').options[1].value")
  await ev("q('dialog-body').querySelector('select').value="+json.dumps(choice))
  await commit("[...q('dialog-body').querySelectorAll('button')].find(e=>e.textContent==='Abrir copia recuperada').click()")
  checks.append('recover scientific autosave copy')
  assert await ev("return q('save-state').dataset.state==='saved'&&q('workspace-status').getAttribute('role')==='status'&&q('workspace-status').textContent.startsWith('Copia recuperada')");checks.append('successful recovery announced without false error')
  for w,h in [(1920,1080),(1366,768),(768,1024)]:
   await b.size(w,h);await b.shot(f'after-science-{w}.png')
  original=json.loads((ROOT/'ux-redesign'/'scientific-project.json').read_text(encoding='utf-8'))
  snapshots=[]
  for path in Path('_local/video-studio/projects').glob('borrador-studio-*.json'):
   p=json.loads(path.read_text(encoding='utf-8'))
   if p.get('name')==original['name']:snapshots.append((path.stat().st_mtime,p))
  accepted=max(snapshots,key=lambda row:row[0])[1]
  assert accepted['studio']['calculations']==original['studio']['calculations'];assert accepted['studio']['datasets']==original['studio']['datasets'];checks.append('saved scientific registries identical')
  assert not [e for e in b.events if e.get('method')=='Runtime.exceptionThrown']
  (ROOT/'ux-redesign'/'science-flow.json').write_text(json.dumps({'checks':checks,'count':len(checks)},indent=2));print(json.dumps({'checks':checks,'count':len(checks)}))
 except Exception:
  await b.shot('debug-science-failure.png');print('FAILED',checks,await ev("return q('workspace-status')?.textContent"),flush=True);raise
 finally:await b.close()
asyncio.run(run())
