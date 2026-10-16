import time
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

async def task(b,j):
    await b.call('Page.navigate',{'url':'http://127.0.0.1:8527'})
    await j.wait("document.querySelector('.st-key-home_help_panel summary')!==null",60)
    report={'checks':[]}
    for width,height in [(1920,1080),(1366,768)]:
        await b.call('Emulation.setDeviceMetricsOverride',{'width':width,'height':height,'deviceScaleFactor':1,'mobile':False})
        await j.wait('innerWidth==='+str(width));await b.shot('editor-inicio-'+str(width)+'.png')
    await j.click("document.querySelector('.st-key-home_help_panel summary')")
    await j.click("document.querySelector('.st-key-home_chirps_example button')")
    if not await j.wait("all().some(e=>e.id==='sig-map'&&e.dataset.rendered==='1')",90):
        print(await j.ev('return document.body.innerText'),flush=True);raise RuntimeError('SIG no abrió')
    for width,height in [(1366,768),(1920,1080)]:
        await b.call('Emulation.setDeviceMetricsOverride',{'width':width,'height':height,'deviceScaleFactor':1,'mobile':False})
        await j.wait('innerWidth==='+str(width));await b.shot('editor-sig-'+str(width)+'.png')
        report['checks'].append(await j.ev("const r=all().find(e=>e.id==='sig-map'),a=r.sigAdapter,m=all().find(e=>e.id==='sig-geographic-map').getBoundingClientRect();return {width:innerWidth,height:innerHeight,version:a.version,instance:r.dataset.instance,map:{x:m.x,y:m.y,width:m.width,height:m.height},layers:a.data.layers.map(l=>({name:l.name,type:l.type,visible:l.visible,date:l.date})),calendar:all().find(e=>e.id==='sig-raster-calendar').textContent,workspace:!!a.data.workspace,error:a.data.error}"))
    (ROOT/'tmp/editor-visual-start.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(report,ensure_ascii=False),flush=True)
