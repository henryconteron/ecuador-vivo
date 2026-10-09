"""Optional real Chrome/Streamlit CCv2/worker integration, no extra packages.

Gestures are synthetic (capture is stubbed); the production JS, callbacks,
reruns, saved document, worker, receipt and pixel comparison are real.
"""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request


CANVAS_DRIVER = r'''
export default function(component){
 const dispose=mountCanvas(component),root=component.parentElement;
 const title=component.data.layers.find(r=>r.id==='title');
 if(title?.w===120){window.__studioTransportReady=true;return dispose}
 if(!title)return dispose;
 const timer=setTimeout(()=>{
  const q=id=>root.querySelector('#'+id),stage=root.querySelector('.stage');
  stage.setPointerCapture=()=>{};q('zoom').value='100';q('zoom').dispatchEvent(new Event('change'));q('snap').checked=false;
  const rect=root.querySelector('.board').getBoundingClientRect();
  const pointer=(target,type,x,y,extra={})=>target.dispatchEvent(new PointerEvent(type,{
    clientX:rect.left+x,clientY:rect.top+y,pointerId:1,button:0,bubbles:true,...extra}));
  pointer(root.querySelector('.piece[data-id="box"]'),'pointerdown',150,40);
  pointer(root.querySelector('.handle'),'pointerdown',220,70);
  pointer(stage,'pointermove',320,90);pointer(stage,'pointerup',320,90);
  q('apply').click();
 },400);
 return()=>{clearTimeout(timer);dispose?.()};
}
'''

TIMELINE_DRIVER = r'''
export default function(component){
 mountTimeline(component);const root=component.parentElement;
 const timer=setInterval(()=>{
  if(!window.__studioTransportReady)return;
  const buttons=root.querySelectorAll('#scenes button'),data=component.data;
  const step=window.__studioTransportStep||0;
  if(step===0&&data.selected==='red'){
   window.__studioTransportStep=1;buttons[1].click();
  }else if(step===1&&data.selected==='blue'&&data.rows[0].id==='red'){
   window.__studioTransportStep=2;
   buttons[1].dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowLeft',shiftKey:true,bubbles:true}));
  }else if(step===2&&data.rows[0].id==='blue'){
   window.__studioTransportStep=3;const seek=root.querySelector('#playhead');
   seek.value=5;seek.dispatchEvent(new Event('change'));
  }else if(step===3&&data.frame===5&&data.selected==='red'){
   window.__studioTransportStep=4;
   [...document.querySelectorAll('button')].find(b=>b.textContent.includes('Exportar timeline MP4'))?.click();
  }
 },300);
 return()=>clearInterval(timer);
}
'''

APP = '''
import copy
import json
from pathlib import Path
import sys
import time
sys.path.insert(0, SOURCE)
import streamlit as st
import imageio_ffmpeg
from PIL import Image
import layout_editor
import studio_ui
import studio_jobs
from studio_model import Element
from studio_timeline import frame_at
from test_studio_jobs import small_project
from jobs import read_json, write_json

studio_ui.STORE=studio_jobs.STORE=Path(OUTPUT)
layout_editor._COMPONENT=st.components.v2.component('studio_transport_canvas',
    html=layout_editor.HTML,css=layout_editor.CSS,
    js=layout_editor.JS.replace('export default function(component)','function mountCanvas(component)',1)+CANVAS_DRIVER)
studio_ui._TIMELINE=st.components.v2.component('studio_transport_timeline',
    html=studio_ui.TIMELINE_HTML,css=studio_ui.TIMELINE_CSS,
    js=studio_ui.TIMELINE_JS.replace('export default function(','function mountTimeline(',1)+TIMELINE_DRIVER)
project=small_project()
project['studio']['scenes'][0]['elements']=[
    Element(id='title',type='text',transform={'x':20,'y':30,'width':80,'height':40},
            style={'text':'A','font_size':20,'font_family':'Atkinson Hyperlegible'},z_index=0).to_dict(),
    Element(id='box',type='shape',transform={'x':140,'y':30,'width':80,'height':40},z_index=1).to_dict()]
# Use 640x360 so the group can scale by exactly 1.5 without clamping.
project['studio']['output_profile']={'id':'custom','width':640,'height':360}
for element in project['studio']['scenes'][0]['elements']: element['group_id']='group.transport'
before=copy.deepcopy(project)
studio_ui.show_studio(project,key='transport')
if st.session_state.get('transport_job'):
    job=Path(st.session_state['transport_job'])
    status=read_json(job/'status.json',{})
    if status.get('state') in ('queued','running'):
        time.sleep(.1);st.rerun()
    assert status['state']=='complete',status
    document=st.session_state['transport_document']
    title=document['studio']['scenes'][0]['elements'][0]
    box=document['studio']['scenes'][0]['elements'][1]
    assert title['transform']['width']==120 and title['transform']['height']==60
    assert title['style']['font_size']==30 and box['transform']['x']==200
    assert title['style']['font_family']=='Atkinson Hyperlegible'
    assert title['group_id']==box['group_id']=='group.transport'
    assert document['studio']['timeline']==['blue','red']
    assert st.session_state['transport_frame']==5
    assert document['studio']['calculations']==before['studio']['calculations']
    assert document['studio']['datasets']==before['studio']['datasets']
    receipt=read_json(job/'receipt.json');assert receipt['total_frames']==6
    assert receipt['calculations']==before['studio']['calculations']
    assert receipt['datasets']==before['studio']['datasets']
    reader=imageio_ffmpeg.read_frames(str(job/'video.mp4'),pix_fmt='rgb24')
    metadata=next(reader);frames=list(reader)
    assert metadata['size']==(640,360) and len(frames)==6
    for index,frame in enumerate(frames):
        actual=Image.frombytes('RGB',(640,360),frame)
        expected=frame_at(document,index).convert('RGB')
        difference=sum(abs(a-b) for a,b in zip(actual.tobytes(),expected.tobytes()))/(640*360*3)
        assert difference<5,(index,difference)
    write_json(Path(OUTPUT)/'verified.json',{'ok':True,'checks':17,'frames':6,
        'transport':'Chrome -> CCv2 -> production callbacks -> Studio worker',
        'timeline':document['studio']['timeline'],'font_size':title['style']['font_size']})
    st.success('CCv2 integration verified')
'''


def run():
    candidates=[Path(os.environ.get('PROGRAMFILES','C:/Program Files'))/'Google/Chrome/Application/chrome.exe',
                Path(os.environ.get('LOCALAPPDATA',''))/'Google/Chrome/Application/chrome.exe']
    chrome=next((p for p in candidates if p.is_file()),None)
    if chrome is None: raise RuntimeError('Chrome local no disponible.')
    with socket.socket() as listener:
        listener.bind(('127.0.0.1',0));port=listener.getsockname()[1]
    with tempfile.TemporaryDirectory(prefix='studio-transport-') as directory:
        folder=Path(directory)
        app=folder/'app.py'
        constants=dict(SOURCE=str(Path(__file__).resolve().parent),OUTPUT=str(folder),
                       CANVAS_DRIVER=CANVAS_DRIVER,TIMELINE_DRIVER=TIMELINE_DRIVER)
        app.write_text('\n'.join(f'{key}={value!r}' for key,value in constants.items())+APP,encoding='utf-8')
        with (folder/'server.log').open('w',encoding='utf-8') as log:
            server=subprocess.Popen([sys.executable,'-m','streamlit','run',str(app),
                '--server.address','127.0.0.1','--server.port',str(port),'--server.headless','true',
                '--browser.gatherUsageStats','false','--server.fileWatcherType','none'],
                stdout=log,stderr=log,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            try:
                deadline=time.monotonic()+20
                while time.monotonic()<deadline:
                    try:
                        with urllib.request.urlopen(f'http://127.0.0.1:{port}/_stcore/health',timeout=1) as health:
                            if health.status==200: break
                    except OSError: time.sleep(.1)
                else: raise AssertionError('Servidor Streamlit no inició.')
                # Virtual time can finish before Python handles the WebSocket.
                # Keep Chrome alive on wall time until the backend verifies it.
                browser=subprocess.Popen([str(chrome),'--headless','--no-first-run','--no-default-browser-check',
                    '--disable-background-networking','--disable-extensions','--user-data-dir='+str(folder/'chrome'),
                    '--remote-debugging-port=0','--window-size=1440,1000',f'http://127.0.0.1:{port}/'],
                    stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                try:
                    marker=folder/'verified.json';deadline=time.monotonic()+45
                    while not marker.is_file() and time.monotonic()<deadline: time.sleep(.1)
                    if not marker.is_file():
                        raise AssertionError('CCv2 no terminó: '+(folder/'server.log').read_text(encoding='utf-8')[-6000:])
                finally:
                    browser.terminate();browser.wait(timeout=10)
                result=json.loads(marker.read_text(encoding='utf-8'));print(json.dumps(result,ensure_ascii=True))
                return result
            finally:
                server.terminate();server.wait(timeout=10)


if __name__=='__main__': run()
