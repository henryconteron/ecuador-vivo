import time
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

async def task(b,j):
    report={'status':'RUNNING','checks':[],'started':time.time(),'reloads':0}
    path=ROOT/'tmp/editor-sig-journey.json'
    async def state():
        return await j.ev("const r=all().find(e=>e.id==='sig-map'),a=r.sigAdapter;return {version:a.version,instance:r.dataset.instance,builds:a.builds,index:a.data.raster_time.index,displayed:a.displayedIndex,date:all().find(e=>e.id==='sig-raster-calendar').textContent,profile:a.data.workspace.profile,layers:a.data.layers.map(l=>({id:l.id,name:l.name,type:l.type,visible:l.visible,style:l.style})),error:a.data.error}")
    async def saved(previous):
        assert await j.wait("all().some(e=>e.id==='sig-map'&&e.sigAdapter.version>"+str(previous['version'])+"&&e.dataset.state==='saved')",40)
        current=await state();assert not current['error'];assert current['instance']==previous['instance'];return current
    def button(text):return "all().find(e=>e.tagName==='BUTTON'&&e.textContent.trim()==="+json.dumps(text)+")"
    try:
        initial=await state();report['initial']=initial
        for ident in ['sig-toggle-layers','sig-toggle-inspector']:
            await j.click(j.elem(ident));await j.click(j.elem(ident))
        await j.click(j.elem('sig-layer-search'));await b.call('Input.insertText',{'text':'provincias'})
        assert await j.ev("return all().find(e=>e.id==='sig-layer-tree').querySelectorAll('.sig-layer-row:not([hidden])').length===1")
        await j.key('a','KeyA',2,65);await j.key('Backspace',vk=8);await j.key('Tab')
        assert (await state())['version']==initial['version'];report['checks'].append({'operation':'panels_search_preserve_project','state':await state()})
        await j.click(j.elem('sig-raster-play'))
        assert await j.wait("all().find(e=>e.id==='sig-raster-calendar').textContent!=='"+initial['date']+"'",10)
        playing=await state();await j.click(j.elem('sig-raster-play'))
        assert await j.wait("all().find(e=>e.id==='sig-raster-play').textContent==='Reproducir fechas'",5)
        report['checks'].append({'operation':'play_pause','playing':playing,'paused':await state()})
        before=await state();await j.click(j.elem('sig-raster-date'));await j.key('End',vk=35);await j.key('Tab')
        assert await j.wait("all().find(e=>e.id==='sig-raster-calendar').textContent==='2024-01-03'",35)
        report['checks'].append({'operation':'seek','state':await state()})
        before=await state();layer=next(l for l in before['layers'] if '24 provincias' in l['name'])
        await j.click("all().find(e=>e.tagName==='BUTTON'&&e.dataset.layer==="+json.dumps(layer['id'])+")");before=await saved(before)
        opacity="all().find(e=>e.id==='sig-inspector-content').querySelector('input[name=opacity]')"
        await j.click(opacity);await j.key('ArrowLeft',vk=37);await j.key('Tab');await j.click(button('Aplicar estilo'));styled=await saved(before)
        report['checks'].append({'operation':'style','before':before,'after':styled})
        check="all().find(e=>e.id==='sig-layer-tree').querySelector('[data-layer=\""+layer['id']+"\"] input')"
        await j.click(check);hidden=await saved(styled);await j.click(check);shown=await saved(hidden)
        report['checks'].append({'operation':'visibility','hidden':hidden,'shown':shown})
        await j.click(j.elem('sig-format'));await j.key('Home',vk=36);await j.key('Enter',vk=13);vertical=await saved(shown)
        assert vertical['profile']['id']=='tiktok';report['checks'].append({'operation':'vertical','state':vertical});await b.shot('editor-sig-vertical-1920.png')
        await j.click(j.elem('sig-save'));report['checks'].append({'operation':'save','state':await saved(vertical)})
        await j.click(j.elem('sig-send-top'));await j.click("document.querySelector('.st-key-sig_series_prepare button')")
        await j.click(button('Enviar serie a Studio'))
        assert await j.wait("all().some(e=>e.id==='canvas-stage'&&e.querySelector('img.piece')?.naturalWidth>0)",90)
        report['studio']=await j.state();report['checks'].append({'operation':'send_studio','state':report['studio']});report['status']='PASS'
        for width,height in [(1920,1080),(1366,768)]:
            await b.call('Emulation.setDeviceMetricsOverride',{'width':width,'height':height,'deviceScaleFactor':1,'mobile':False});await j.wait('innerWidth==='+str(width));await b.shot('editor-studio-'+str(width)+'.png')
    except Exception as error:
        report['status']='FAIL';report['error']=repr(error);report['visible']=await j.ev("return all().filter(e=>e.tagName==='BUTTON'||e.getAttribute('data-testid')==='stException').map(e=>e.textContent).slice(-60)");await b.shot('editor-journey-failure.png');raise
    finally:
        path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'status':report['status'],'error':report.get('error'),'checks':[c['operation'] for c in report['checks']]},ensure_ascii=False),flush=True)
