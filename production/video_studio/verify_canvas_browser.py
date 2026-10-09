"""Optional real Chrome check of the exact inline editor, without extra packages."""
import ast
import base64
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
from html.parser import HTMLParser

from PIL import Image


def run():
    source = ast.parse(Path(__file__).with_name('layout_editor.py').read_text(encoding='utf-8'))
    constants = {node.targets[0].id: ast.literal_eval(node.value)
                 for node in source.body if isinstance(node, ast.Assign)
                 and isinstance(node.targets[0], ast.Name)
                 and node.targets[0].id in ('HTML', 'CSS', 'JS')}
    timeline_source = ast.parse(Path(__file__).with_name('studio_ui.py').read_text(encoding='utf-8'))
    timeline = {node.targets[0].id: ast.literal_eval(node.value)
                for node in timeline_source.body if isinstance(node, ast.Assign)
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id in ('TIMELINE_HTML', 'TIMELINE_JS')}
    png = io.BytesIO()
    Image.new('RGBA', (40, 20), '#00aabb').save(png, format='PNG')
    uri = 'data:image/png;base64,' + base64.b64encode(png.getvalue()).decode()
    layers = [dict(id=name, label=name, kind=kind, x=20, y=30, w=80, h=40,
                   z=index, src=uri, editable=True, content_editable=False,
                   hidden=False, locked=False, original={'w':80,'h':40})
              for index, (name, kind) in enumerate((('title','text'),('map','map')))]
    payload = dict(width=640, height=360, frame_width=640, frame_height=360,
                   scene='map', layers=layers, entries={}, icons=['pin'], background=uri)
    harness = r'''
const root=document.querySelector('#editor').attachShadow({mode:'open'});
root.innerHTML='<style>'+STYLE+'</style>'+HTML;
let saved=null;
const q=id=>root.querySelector('#'+id);
let checks=0;
const assert=(value,message)=>{checks++;if(!value)throw new Error(message)};
const report=value=>document.querySelector('#result').textContent=JSON.stringify(value);
window.addEventListener('error',e=>report({ok:false,error:e.message}));
try{
 mount({parentElement:root,data:DATA,setTriggerValue:(key,value)=>saved=structuredClone(value)});
 setTimeout(()=>{try{
  assert(q('layers').children.length===2,'layers inventory');
  assert(q('layers').querySelector('button').hasAttribute('aria-pressed'),'layer selection exposes pressed state');
  const stage=root.querySelector('.stage');
  const key=(name,shift=false)=>stage.dispatchEvent(new KeyboardEvent('keydown',{key:name,shiftKey:shift,bubbles:true}));
  key('ArrowRight');assert(q('x').value==='21','arrow precision');
  key('ArrowDown',true);assert(q('y').value==='40','shift arrows');
  q('name').value='Título editorial';q('name').dispatchEvent(new Event('change'));
  q('locked').checked=true;q('locked').dispatchEvent(new Event('change'));
  assert(q('layers').querySelector('[data-layer="title"] button[aria-label="Desbloquear title"]')?.getAttribute('aria-pressed')==='true'||q('layers').querySelector('[data-layer="title"] button[aria-label^="Desbloquear"]')?.getAttribute('aria-pressed')==='true','lock state exposed to assistive technology');
  key('ArrowRight');key('Delete');assert(q('x').value==='21' && q('delete').disabled,'lock guards');
  q('locked').checked=false;q('locked').dispatchEvent(new Event('change'));
  q('layerup').click();q('apply').click();assert(saved.entries.title.z===1,'layer reorder');
  q('undo').click();q('apply').click();assert(saved.entries.title.z===0,'undo');
  q('redo').click();q('apply').click();assert(saved.entries.title.z===1,'redo');
  assert(saved.entries.title.name==='Título editorial','saved name');
  q('zoom').value='200';q('zoom').dispatchEvent(new Event('change'));
  assert(Math.abs(stage.getBoundingClientRect().width-1280)<3,'zoom 200');
  q('zoom').value='fit';q('zoom').dispatchEvent(new Event('change'));
  assert(stage.getBoundingClientRect().width<=root.querySelector('.viewport').clientWidth+3,'fit');
  assert(document.documentElement.scrollWidth<=innerWidth+2,'page overflow');
  assert(DATA.layers[0].x===20 && DATA.layers[0].y===30,'input mutation');
  // Synthetic handler tests run the exact production JS. Pointer capture is
  // intentionally stubbed: untrusted PointerEvents have no active hardware ID
  // (https://www.w3.org/TR/pointerevents3/#dom-element-setpointercapture).
  // This harness does not certify hit testing or the Streamlit transport.
  const freeHost=document.createElement('div');document.body.append(freeHost);
  const freeRoot=freeHost.attachShadow({mode:'open'});
  freeRoot.innerHTML='<style>'+STYLE+'</style>'+HTML;
  const freeData=structuredClone(DATA);freeData.free_scene=true;
  freeData.safe_area={x:10,y:10,width:620,height:340};
  freeData.layers[0].font_size=20;freeData.layers[0].content_editable=true;
  freeData.layers[1].x=140;freeData.layers[1].kind='shape';
  freeData.layers.push({...freeData.layers[1],id:'locked',x:280,z:2,locked:true},
                       {...freeData.layers[1],id:'hidden',x:400,z:3,hidden:true});
  let freeSaved;
  const dispose=mount({parentElement:freeRoot,data:freeData,
    setTriggerValue:(key,value)=>freeSaved=structuredClone(value)});
  const fq=id=>freeRoot.querySelector('#'+id),freeStage=freeRoot.querySelector('.stage');
  freeStage.setPointerCapture=()=>{};
  fq('zoom').value='100';fq('zoom').dispatchEvent(new Event('change'));
  fq('snap').checked=false;
  const fkey=(key,extra={})=>freeStage.dispatchEvent(new KeyboardEvent('keydown',{key,bubbles:true,...extra}));
  const piece=id=>freeRoot.querySelector('.piece[data-id="'+id+'"]');
  const point=(target,type,x,y,extra={})=>{
    const rect=freeRoot.querySelector('.board').getBoundingClientRect();
    target.dispatchEvent(new PointerEvent(type,{clientX:rect.left+x,clientY:rect.top+y,
      pointerId:1,button:0,buttons:type==='pointerup'?0:1,bubbles:true,...extra}));
  };
  const apply=()=>{fq('apply').click();return freeSaved};
  point(piece('map'),'pointerdown',150,40,{shiftKey:true});
  assert(apply().selection.join(',')==='title,map','shift click multiselection');
  assert(fq('font').disabled && fq('x').disabled,'group inspector guards');
  fkey('ArrowRight');fkey('ArrowDown',{shiftKey:true});
  apply();assert(freeSaved.entries.title.x===21 && freeSaved.entries.map.x===141 &&
    freeSaved.entries.title.y===40 && freeSaved.entries.map.y===40,'group arrow geometry');
  fkey('z',{ctrlKey:true});fkey('z',{ctrlKey:true});
  const handle=freeRoot.querySelector('.handle');
  point(handle,'pointerdown',220,70);point(freeStage,'pointermove',320,90);point(freeStage,'pointerup',320,90);
  apply();assert(freeSaved.entries.title.w===120 && freeSaved.entries.title.h===60 &&
    freeSaved.entries.title.font_size===30 && freeSaved.entries.map.x===200,'group resize text and offsets');
  fkey('z',{ctrlKey:true});fkey('y',{ctrlKey:true});
  assert(apply().entries.title.font_size===30,'redo restores resized typography');
  fkey('z',{ctrlKey:true});
  point(piece('title'),'pointerdown',30,40);point(freeStage,'pointermove',60,70);fkey('Escape');
  assert(apply().selection.length===0 && !freeSaved.entries.title,'escape cancels geometry');
  point(freeStage,'pointerdown',5,5);point(freeStage,'pointermove',500,100);point(freeStage,'pointerup',500,100);
  assert(apply().selection.join(',')==='title,map','marquee excludes locked and hidden');
  fkey('Escape');fkey('a',{ctrlKey:true});
  assert(apply().selection.join(',')==='title,map','select all excludes locked and hidden');
  fkey('Delete');apply();
  assert(freeSaved.entries.title.deleted && freeSaved.entries.map.deleted &&
    !freeSaved.entries.locked && !freeSaved.entries.hidden,'group delete lock guards');
  fkey('z',{ctrlKey:true});assert(apply().selection.length===2,'undo restores group selection');
  for(const [key,action] of [['c','copy'],['v','paste'],['d','duplicate']]){
    fkey(key,{ctrlKey:true});assert(freeSaved.action===action && freeSaved.selection.length===2,'shortcut '+action);
  }
  fkey('Escape');point(piece('title'),'pointerdown',30,40);point(freeStage,'pointerup',30,40);
  point(handle,'pointerdown',100,70);point(freeStage,'pointermove',140,110);point(freeStage,'pointerup',140,110);
  apply();assert(freeSaved.entries.title.w===120 && freeSaved.entries.title.h===60 &&
    freeSaved.entries.title.font_size===30,'single text resize keeps typography ratio');
  assert(fq('text').maxLength===2000,'free scene text contract');
  fq('text').focus();fq('text').dispatchEvent(new KeyboardEvent('keydown',{key:'a',ctrlKey:true,bubbles:true}));
  assert(apply().selection.join(',')==='title','text shortcuts stay outside canvas');
  assert(freeData.layers[0].w===80 && freeData.layers[0].font_size===20,'free input immutable');
  const freeEntries=structuredClone(freeSaved.entries);
  fkey('z',{ctrlKey:true});
  assert(!fq('redo').disabled,'redo available before cancelled gesture');
  point(piece('title'),'pointerdown',30,40);point(freeStage,'pointermove',40,50);
  freeStage.dispatchEvent(new PointerEvent('pointercancel',{pointerId:1,bubbles:true}));
  assert(!fq('redo').disabled,'pointercancel preserves redo');
  point(freeStage,'pointerdown',5,5);point(freeStage,'pointermove',250,100);
  freeStage.dispatchEvent(new PointerEvent('pointercancel',{pointerId:1,bubbles:true}));
  assert(apply().selection.join(',')==='title','marquee cancel restores selection');
  fkey('a',{ctrlKey:true});
  point(handle,'pointerdown',220,70);point(freeStage,'pointermove',30,32);point(freeStage,'pointerup',30,32);
  apply();assert(freeSaved.entries.title.w===32 && freeSaved.entries.title.h===16 &&
    freeSaved.entries.title.font_size===8 && freeSaved.entries.map.w===32,'group shrink constrained by font minimum');
  fkey('z',{ctrlKey:true});
  point(handle,'pointerdown',220,70);point(freeStage,'pointermove',320,90);point(freeStage,'pointerup',320,90);
  apply();assert(freeSaved.entries.title.w===120 && freeSaved.entries.title.font_size===30,'resize after cancelled gestures');
  fq('object').value='map';fq('object').dispatchEvent(new Event('change'));
  fq('layerup').click();
  assert(!apply().entries.locked,'layer ordering preserves locked neighbor');
  const initialX=parseFloat(piece('map').style.left);
  for(let i=0;i<40;i++)fkey('ArrowRight');
  point(piece('map'),'pointerdown',initialX+45,40);
  freeStage.dispatchEvent(new PointerEvent('pointercancel',{pointerId:1,bubbles:true}));
  for(let i=0;i<40;i++)fkey('z',{ctrlKey:true});
  assert(parseFloat(piece('map').style.left)===initialX,'cancel at history limit preserves 40 undo steps');
  fq('object').value='title';fq('object').dispatchEvent(new Event('change'));
  const beforeDrag=parseFloat(piece('title').style.left);
  point(piece('title'),'pointerdown',beforeDrag+5,40);point(freeStage,'pointermove',beforeDrag+15,40);
  fkey('ArrowRight');
  freeStage.dispatchEvent(new PointerEvent('pointercancel',{pointerId:1,bubbles:true}));
  assert(parseFloat(piece('title').style.left)===beforeDrag+11,'keyboard finalizes active gesture before new edit');
  for(const [id,value] of [['font',8],['w',1],['h',100]]){
    fq(id).value=value;fq(id).dispatchEvent(new Event('input'));
  }
  point(handle,'pointerdown',50,130);point(freeStage,'pointermove',50.5,130);point(freeStage,'pointerup',50.5,130);
  apply();assert(freeSaved.entries.title.w===2 && freeSaved.entries.title.h===150 &&
    freeSaved.entries.title.font_size===12,'font uses resize factor before geometry rounding');
  const beforeCopy=parseFloat(piece('title').style.left);
  point(piece('title'),'pointerdown',beforeCopy+1,40);point(freeStage,'pointermove',beforeCopy+21,40);
  fkey('c',{ctrlKey:true});
  freeStage.dispatchEvent(new PointerEvent('pointercancel',{pointerId:1,bubbles:true}));
  assert(freeSaved.action==='copy' && freeSaved.entries.title.x===beforeCopy+20 &&
    parseFloat(piece('title').style.left)===beforeCopy+20,'clipboard finalizes active drag');
  dispose();
  assert(freeStage.onpointerdown===null && freeStage.onkeydown===null,'canvas cleanup');

  for(const [width,height] of [[160,160],[160,320],[320,160],[3840,160]]){
    const host=document.createElement('div');host.style.cssText='width:320px;max-width:100%';document.body.append(host);
    const sr=host.attachShadow({mode:'open'});sr.innerHTML='<style>'+STYLE+'</style>'+HTML;
    const small=structuredClone(DATA);small.free_scene=true;small.width=small.frame_width=width;small.height=small.frame_height=height;
    small.safe_area={x:6,y:6,width:width-12,height:height-12};small.layers[0].font_size=20;
    let emitted;const cleanup=mount({parentElement:sr,data:small,setTriggerValue:(key,value)=>emitted=structuredClone(value)});
    const sq=id=>sr.querySelector('#'+id),ss=sr.querySelector('.stage');sq('zoom').value='fit';sq('zoom').dispatchEvent(new Event('change'));
    assert(ss.getBoundingClientRect().width<=sr.querySelector('.viewport').clientWidth+2,'small profile fits width '+width+'x'+height);
    assert(ss.getBoundingClientRect().height<=innerHeight*.78+2,'small profile fits height '+width+'x'+height);
    assert(sr.querySelector('.handle').getBoundingClientRect().width>=23,'resize target remains usable at fit '+width+'x'+height);
    const target=sr.querySelector('.handle').getBoundingClientRect(),clip=sr.querySelector('.viewport').getBoundingClientRect();
    assert(Math.min(target.bottom,clip.bottom)-Math.max(target.top,clip.top)>=23,'resize target is not clipped vertically '+width+'x'+height);
    assert(sq('font').min==='8','free-scene font lower bound');
    sq('font').value='5';sq('font').dispatchEvent(new Event('input'));sq('apply').click();
    assert(emitted.entries.title.font_size===8,'free font input clamps to render minimum');
    sq('addtext').click();const added=Object.entries(emitted.entries).find(([id])=>id.startsWith('custom.'))[1];
    assert(added.x+added.w<=width&&added.y+added.h<=height&&added.font_size>=8,'small new text bounds');
    assert(document.documentElement.scrollWidth<=innerWidth+2,'narrow container does not overflow page');
    cleanup();host.remove();
  }

  const groupHost=document.createElement('div');document.body.append(groupHost);
  const groupRoot=groupHost.attachShadow({mode:'open'});groupRoot.innerHTML='<style>'+STYLE+'</style>'+HTML;
  const groupData=structuredClone(freeData);groupData.layers[0].group_id='group.persisted';groupData.layers[1].group_id='group.persisted';groupData.layers[3].group_id='group.persisted';
  let groupSaved;
  const groupDispose=mount({parentElement:groupRoot,data:groupData,setTriggerValue:(key,value)=>groupSaved=structuredClone(value)});
  const gq=id=>groupRoot.querySelector('#'+id),groupStage=groupRoot.querySelector('.stage');groupStage.setPointerCapture=()=>{};
  const gkey=(key,extra={})=>groupStage.dispatchEvent(new KeyboardEvent('keydown',{key,bubbles:true,...extra}));
  const gapply=()=>{gq('apply').click();return groupSaved};
  assert(gapply().selection.length===3,'persisted group restored including hidden member');
  gkey('ArrowRight');gapply();
  assert(groupSaved.entries.title.x===21&&groupSaved.entries.map.x===141&&groupSaved.entries.hidden.x===401,'persistent group moves hidden members');
  gkey('z',{ctrlKey:true});gkey('Escape');
  const gpoint=(type,x,y)=>{const rect=groupRoot.querySelector('.board').getBoundingClientRect(),scale=rect.width/groupData.width;groupStage.dispatchEvent(new PointerEvent(type,{clientX:rect.left+x*scale,clientY:rect.top+y*scale,pointerId:1,button:0,bubbles:true}))};
  gpoint('pointerdown',0,0);gpoint('pointermove',120,100);gpoint('pointerup',120,100);
  assert(gapply().selection.length===3,'marquee expands persistent membership');
  [...groupRoot.querySelectorAll('button')].find(b=>b.textContent==='Desagrupar selección').click();
  assert(groupSaved.action==='ungroup'&&groupSaved.selection.length===3,'ungroup command transport');
  groupDispose();groupHost.remove();
  const lockedGroupHost=document.createElement('div');document.body.append(lockedGroupHost);
  const lockedGroupRoot=lockedGroupHost.attachShadow({mode:'open'});lockedGroupRoot.innerHTML='<style>'+STYLE+'</style>'+HTML;
  groupData.layers[1].locked=true;let lockedGroupSaved;
  const lockedGroupDispose=mount({parentElement:lockedGroupRoot,data:groupData,setTriggerValue:(key,value)=>lockedGroupSaved=structuredClone(value)});
  lockedGroupRoot.querySelector('.stage').dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}));lockedGroupRoot.querySelector('#apply').click();
  assert(!Object.keys(lockedGroupSaved.entries).length,'locked member keeps persistent group stationary');
  assert(lockedGroupRoot.querySelector('#delete').disabled,'locked group delete guard');
  lockedGroupDispose();lockedGroupHost.remove();

  const recoveryHost=document.createElement('div');document.body.append(recoveryHost);
  const recoveryRoot=recoveryHost.attachShadow({mode:'open'});
  const recoveryData=structuredClone(freeData);recoveryData.recovery_key='evs-test-recovery-'+innerWidth;
  const remount=()=>{recoveryRoot.innerHTML='<style>'+STYLE+'</style>'+HTML;return mount({parentElement:recoveryRoot,data:recoveryData,setTriggerValue:()=>{}})};
  let recoveryDispose=remount();const rq=id=>recoveryRoot.querySelector('#'+id);
  recoveryRoot.querySelector('.stage').dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}));
  recoveryDispose();recoveryDispose=remount();
  assert(rq('x').value==='21','unapplied gesture restored after component navigation');
  assert(rq('pending').textContent.includes('pendientes'),'restored gesture remains explicitly pending');
  const recoveryStage=recoveryRoot.querySelector('.stage');recoveryStage.setPointerCapture=()=>{};
  const recoveryPoint=(target,type,x,y)=>{const rect=recoveryRoot.querySelector('.board').getBoundingClientRect(),scale=rect.width/recoveryData.width;target.dispatchEvent(new PointerEvent(type,{clientX:rect.left+x*scale,clientY:rect.top+y*scale,pointerId:1,button:0,bubbles:true}))};
  recoveryPoint(recoveryRoot.querySelector('.piece[data-id="title"]'),'pointerdown',30,40);
  recoveryPoint(recoveryStage,'pointermove',60,70);recoveryPoint(recoveryStage,'pointercancel',60,70);
  recoveryDispose();recoveryDispose=remount();assert(rq('x').value==='21','cancelled gesture does not replace recoverable state');
  recoveryDispose();recoveryData.recovery_key+='-revision2';recoveryDispose=remount();
  assert(rq('x').value==='20','new accepted revision excludes old pending gesture');
  const originalSet=Storage.prototype.setItem;Storage.prototype.setItem=()=>{throw new Error('storage unavailable')};
  try{recoveryRoot.querySelector('.stage').dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}));
    assert(rq('pending').textContent.includes('no se pudo'),'storage failure visible without blocking edits');
    assert(rq('x').value==='21','storage failure preserves live gesture');
  }finally{Storage.prototype.setItem=originalSet}
  recoveryDispose();sessionStorage.setItem(recoveryData.recovery_key,JSON.stringify({entries:{title:{x:'invalid'}}}));recoveryDispose=remount();
  assert(rq('x').value==='20'&&rq('pending').textContent.includes('no se pudo recuperar'),'malformed pending state preserves accepted geometry');
  recoveryDispose();recoveryHost.remove();sessionStorage.removeItem(recoveryData.recovery_key);sessionStorage.removeItem(recoveryData.recovery_key.replace('-revision2',''));

  const timelineHost=document.createElement('div');document.body.append(timelineHost);
  const timelineRoot=timelineHost.attachShadow({mode:'open'});timelineRoot.innerHTML=TIMELINE_HTML;
  let timelineSaved;
  const rows=[{id:'a',name:'Inicio',seconds:1/30,start_frame:0,end_frame:1,thumbnail:DATA.background},
    {id:'b',name:'Final',seconds:2/30,start_frame:1,end_frame:3,thumbnail:DATA.background}];
  mountTimeline({parentElement:timelineRoot,data:{rows,selected:'a',frame:0},
    setTriggerValue:(key,value)=>timelineSaved=structuredClone(value)});
  const tq=id=>timelineRoot.querySelector('#'+id),buttons=tq('scenes').querySelectorAll('button');
  assert(buttons.length===2 && buttons[0].getAttribute('aria-current')==='true','timeline inventory and selected');
  buttons[1].click();assert(timelineSaved.action==='select' && timelineSaved.id==='b','timeline select');
  buttons[1].dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowLeft',shiftKey:true,bubbles:true}));
  assert(timelineSaved.action==='reorder' && timelineSaved.order.join(',')==='b,a','timeline keyboard reorder');
  const transfer=new DataTransfer();
  buttons[0].dispatchEvent(new DragEvent('dragstart',{dataTransfer:transfer,bubbles:true}));
  buttons[1].dispatchEvent(new DragEvent('drop',{dataTransfer:transfer,bubbles:true,cancelable:true}));
  assert(timelineSaved.order.join(',')==='b,a','timeline drag reorder');
  assert(tq('playhead').max==='2','timeline last frame inclusive');
  for(const frame of [0,1,2]){
    tq('playhead').value=frame;tq('playhead').dispatchEvent(new Event('input'));
    tq('playhead').dispatchEvent(new Event('change'));
    assert(timelineSaved.action==='seek' && timelineSaved.frame===frame,'timeline seek '+frame);
  }
  assert(rows[0].id==='a' && rows[1].end_frame===3,'timeline input immutable');
  report({ok:true,width:innerWidth,checks,free_entries:freeEntries});
 }catch(error){report({ok:false,error:String(error)})}},250);
}catch(error){report({ok:false,error:String(error)})}
'''
    script = '\n'.join('const '+name+'='+json.dumps(value)+';' for name,value in
                       [('HTML',constants['HTML']),('STYLE',constants['CSS']),('DATA',payload),
                        ('TIMELINE_HTML',timeline['TIMELINE_HTML'])])
    script += constants['JS'].replace('export default function(component)', 'function mount(component)', 1)
    script += timeline['TIMELINE_JS'].replace('export default function(', 'function mountTimeline(', 1)
    script += harness
    html = '<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#04151e}#editor{display:block;width:100%}</style><div id="editor"></div><pre id="result"></pre><script>' + script.replace('</script', '<\\/script') + '</script>'
    candidates = [Path(os.environ.get('PROGRAMFILES','C:/Program Files'))/'Google/Chrome/Application/chrome.exe',
                  Path(os.environ.get('LOCALAPPDATA',''))/'Google/Chrome/Application/chrome.exe']
    chrome = next((path for path in candidates if path.is_file()), None)
    if chrome is None:
        raise RuntimeError('Chrome local no disponible para la verificación opcional.')
    with tempfile.TemporaryDirectory(prefix='studio-browser-') as directory:
        fixture = Path(directory)/'editor.html'
        fixture.write_text(html, encoding='utf-8')
        for width in (1440,768,500):
            command = [str(chrome),'--headless','--no-first-run','--no-default-browser-check',
                       '--disable-background-networking', '--disable-extensions',
                       '--user-data-dir='+str(Path(directory)/str(width)),
                       '--window-size='+str(width)+',1000', '--virtual-time-budget=1500',
                       '--dump-dom',fixture.as_uri()]
            completed = subprocess.run(command, capture_output=True, timeout=45,
                                       creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            class Result(HTMLParser):
                recording=False
                value=''
                def handle_starttag(self, tag, attrs):
                    if tag=='pre' and dict(attrs).get('id')=='result': self.recording=True
                def handle_endtag(self, tag):
                    if tag=='pre': self.recording=False
                def handle_data(self,data):
                    if self.recording: self.value+=data
            result=Result()
            result.feed(completed.stdout.decode('utf-8',errors='replace'))
            if not result.value:
                raise AssertionError('Chrome no produjo resultado: '+completed.stderr.decode(errors='replace')[-1000:])
            state=json.loads(result.value)
            print(json.dumps(state, ensure_ascii=True))
            if not state.get('ok'): raise AssertionError(state)


if __name__=='__main__':
    run()
