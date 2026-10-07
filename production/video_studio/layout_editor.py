"""Private local drag/resize editor. Inline CCv2; no npm/CDN or extra service."""
import copy
import datetime as dt
import uuid
from pathlib import Path

import streamlit as st
from streamlit.errors import StreamlitAPIException

from jobs import write_json
from model import STORE
from layout_engine import ICONS, clean_layout

HTML = """
<div class="editor">
 <div class="toolbar">
  <button id="undo">Deshacer</button><button id="redo">Rehacer</button>
  <label><input id="guides" type="checkbox" checked> Guías sociales</label>
  <label><input id="snap" type="checkbox" checked> Ajustar a 10 px</label>
  <button id="reset">Restaurar tarjeta</button>
  <button id="addtext">Añadir texto</button><button id="addicon">Añadir icono</button>
  <button id="delete">Eliminar elemento</button>
 </div>
 <div class="workspace">
  <div class="stage" tabindex="0" aria-label="Lienzo editable del video"><div class="board"></div></div>
  <div class="inspector">
   <label>Elemento<select id="object"></select></label>
   <div class="coordinates">
    <label>X<input id="x" type="number" step="1"></label><label>Y<input id="y" type="number" step="1"></label>
    <label>Ancho<input id="w" type="number" min="1" step="1"></label><label>Alto<input id="h" type="number" min="1" step="1"></label>
   </div>
   <label>Tamaño de letra<input id="font" type="number" min="4" max="400"></label>
   <label>Texto<textarea id="text" rows="4" maxlength="500"></textarea></label>
   <label>Color del texto<input id="color" type="color"></label>
   <label>Icono<select id="icon"></select></label>
   <label><input id="hidden" type="checkbox"> Ocultar elemento</label>
   <label>Elementos eliminados<select id="deleted"></select></label>
   <button id="restore">Recuperar elemento</button>
   <div class="stack"><button id="front">Al frente</button><button id="back">Al fondo</button></div>
   <p id="hint">Selecciona y arrastra un elemento. La esquina inferior derecha cambia su tamaño.</p>
   <p id="notice"></p>
   <p id="pending" role="status">Sin cambios por aplicar.</p>
   <button id="apply" class="primary">OK · aplicar y guardar</button>
   <button id="generate">Guardar e ir a exportar</button>
  </div>
 </div>
 <p class="foot">Los mapas conservan su proporción. La distancia y el norte viajan con el mapa; la leyenda conserva sus valores. Las guías no se exportan.</p>
</div>
"""

CSS = """
.editor{font-family:var(--st-font);color:var(--st-text-color);width:100%}
.toolbar,.stack{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:12px}
button,input,select,textarea{font:inherit;box-sizing:border-box;color:var(--st-text-color);background:var(--st-secondary-background-color);border:1px solid #527180;border-radius:7px;padding:8px}
button{cursor:pointer}button:disabled,input:disabled,textarea:disabled,select:disabled{opacity:.4;cursor:default}
.workspace{display:grid;grid-template-columns:minmax(230px,440px) minmax(230px,320px);gap:18px;justify-content:center;align-items:start}
.stage{position:relative;overflow:hidden;outline:none;background:#071721;border:1px solid #527180;touch-action:none;width:100%;max-width:calc(74vh * var(--frame-ratio));justify-self:center;box-sizing:border-box}
.board{position:absolute;top:0;left:0;width:1080px;height:1920px;transform-origin:top left}
.piece{position:absolute;object-fit:fill;user-select:none;touch-action:none;-webkit-user-drag:none}
.selected{position:absolute;box-sizing:border-box;border:3px solid #fff45c;pointer-events:none}
.handle{position:absolute;bottom:-12px;right:-12px;width:24px;height:24px;background:#fff45c;border:2px solid #071721;pointer-events:auto;cursor:nwse-resize}
.guide{position:absolute;box-sizing:border-box;border:3px dashed #f5c24a;pointer-events:none;opacity:.65}
.inspector{display:flex;flex-direction:column;gap:10px;max-height:74vh;overflow:auto;padding-right:6px;min-width:0}.inspector label{display:flex;flex-direction:column;gap:4px;font-size:13px;min-width:0}
.inspector input,.inspector select,.inspector textarea{width:100%;min-width:0}.inspector input[type=checkbox]{width:auto}
.inspector label:has(input[type=checkbox]),.toolbar label{display:block}
.coordinates{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:8px}.coordinates input{width:100%}
.primary{background:#164e59;border-color:#55e2cb;font-weight:600}
p{font-size:13px;line-height:1.4;margin:4px 0}.foot{margin-top:12px;color:#a6bdc7}#notice,#pending{color:#f5c24a}
@media(max-width:650px){.workspace{grid-template-columns:minmax(0,1fr)}.stage{max-width:100%}.inspector{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);max-height:none;overflow:visible}.inspector p,.inspector .primary,.inspector .coordinates{grid-column:1/-1}}
"""

JS = """
export default function(component){
 const {parentElement:root,data,setTriggerValue}=component;
 const q=id=>root.querySelector('#'+id), board=root.querySelector('.board'), stage=root.querySelector('.stage');
 const layers=structuredClone(data.layers), entries=structuredClone(data.entries||{});
 const originalEntries=JSON.stringify(entries);
 const pending=()=>q('pending').textContent=JSON.stringify(entries)===originalEntries?'Sin cambios por aplicar.':'Cambios pendientes: pulsa OK antes de salir de esta tarjeta.';
 let selected=layers.find(x=>x.editable)?.id, scale=1, history=[], future=[], drag=null;
 const frameW=data.frame_width||1080, frameH=data.frame_height||1920;
 const fit=Math.min(frameW/1080,frameH/1920);
 stage.style.background=data.frame_background||'#04151e';
 stage.style.aspectRatio=frameW+'/'+frameH;
 stage.style.setProperty('--frame-ratio',String(frameW/frameH));
 q('guides').disabled=frameW/frameH!==1080/1920;
 if(q('guides').disabled)q('guides').checked=false;
 const imgs=new Map();
 board.innerHTML='';
 const bg=document.createElement('img');bg.src=data.background;bg.style.cssText='position:absolute;width:1080px;height:1920px;pointer-events:none';board.append(bg);
 layers.forEach(row=>{const el=document.createElement('img');el.src=row.src;el.className='piece';el.alt=row.label;el.draggable=false;el.dataset.id=row.id;el.style.pointerEvents=row.editable?'auto':'none';imgs.set(row.id,el);board.append(el)});
 const guide=document.createElement('div');guide.className='guide';guide.style.cssText='left:60px;top:190px;width:900px;height:1330px';board.append(guide);
 const box=document.createElement('div');box.className='selected';const handle=document.createElement('div');handle.className='handle';box.append(handle);board.append(box);
 function choices(){
  q('object').innerHTML='';q('deleted').innerHTML='';
  layers.filter(x=>x.editable).forEach(row=>{const o=document.createElement('option');o.value=row.id;o.textContent=row.label+' · '+row.kind;(row.deleted?q('deleted'):q('object')).append(o)});
  if(!layers.some(x=>x.id===selected&&!x.deleted))selected=layers.find(x=>x.editable&&!x.deleted)?.id;
  q('restore').disabled=!q('deleted').options.length;
 }
 choices();
 q('icon').innerHTML=''; ['Original',...data.icons].forEach(label=>{const o=document.createElement('option');o.value=label;o.textContent=label;q('icon').append(o)});
 const current=()=>layers.find(x=>x.id===selected&&!x.deleted);
 const remember=()=>{history.push({layers:structuredClone(layers),entries:structuredClone(entries)});if(history.length>40)history.shift();future=[]};
 const hydrate=state=>{layers.splice(0,layers.length,...structuredClone(state.layers));Object.keys(entries).forEach(k=>delete entries[k]);Object.assign(entries,structuredClone(state.entries));choices();paint();inspect();pending()};
 const clamp=row=>{if(row.kind==='map'||row.kind==='icon'){const factor=Math.min(1,1080/Math.max(1,row.w),1920/Math.max(1,row.h));row.w*=factor;row.h*=factor}row.w=Math.max(1,Math.min(1080,Math.round(row.w)));row.h=Math.max(1,Math.min(1920,Math.round(row.h)));row.x=Math.max(0,Math.min(1080-row.w,Math.round(row.x)));row.y=Math.max(0,Math.min(1920-row.h,Math.round(row.y)))};
 const mark=row=>{entries[row.id]={...(entries[row.id]||{}),x:row.x,y:row.y,w:row.w,h:row.h,z:row.z,hidden:row.hidden,deleted:!!row.deleted};if(row.font_size)entries[row.id].font_size=row.font_size;if(row.content_editable&&row.changedText!==undefined)entries[row.id].text=row.changedText;if(row.changedColor)entries[row.id].color=row.changedColor;if(row.changedIcon&&row.changedIcon!=='Original')entries[row.id].icon=row.changedIcon;pending()};
 function paint(){
  layers.forEach(row=>{const el=imgs.get(row.id);Object.assign(el.style,{display:row.deleted||row.hidden?'none':'block',left:row.x+'px',top:row.y+'px',width:row.w+'px',height:row.h+'px',zIndex:String(Math.round(row.z)+100),cursor:row.editable?'move':'default'})});
  const row=current();box.style.display=row?'block':'none';if(row)Object.assign(box.style,{left:row.x+'px',top:row.y+'px',width:row.w+'px',height:row.h+'px',zIndex:'5000'});
  guide.style.zIndex='4999';guide.style.display=q('guides').checked?'block':'none';
  q('undo').disabled=!history.length;q('redo').disabled=!future.length;
  q('delete').disabled=!current();
  const small=layers.filter(x=>x.editable&&!x.hidden&&!x.deleted&&x.kind==='text'&&x.font_size&&x.font_size<20).length;
  q('notice').textContent=small?small+' textos tienen menos de 20 px: revisa su legibilidad.':'';
 }
 function inspect(){const row=current();if(!row){['x','y','w','h','font','text','color','icon','hidden','front','back'].forEach(k=>q(k).disabled=true);q('hint').textContent='No quedan elementos seleccionables. Recupera un elemento o añade texto.';return}['x','y','w','h','hidden','front','back'].forEach(k=>q(k).disabled=false);q('object').value=selected;['x','y','w','h'].forEach(k=>q(k).value=row[k]);q('font').disabled=!row.font_size;q('font').value=row.font_size||'';q('text').disabled=!row.content_editable;q('text').value=row.changedText??entries[row.id]?.text??row.text??'';q('color').disabled=row.kind!=='text';q('color').value=/^#[0-9a-f]{6}$/i.test(row.changedColor||row.color)?(row.changedColor||row.color):'#ffffff';q('icon').disabled=row.kind!=='icon';q('icon').value=row.changedIcon||entries[row.id]?.icon||'Original';q('hidden').checked=!!row.hidden;q('hint').textContent=row.kind==='map'?'Arrastra el mapa completo; al ampliar, se amplían también su norte y distancia.':!row.content_editable&&row.kind==='text'?'Cifra/fecha vinculada a datos. Puedes moverla, ajustar letra/color o quitarla del diseño, pero no cambiar su valor.':'Arrastra o ajusta las medidas. OK redibuja el texto en este mismo lienzo.'}
 q('delete').onclick=()=>{const row=current();if(!row)return;remember();row.deleted=true;mark(row);choices();paint();inspect()};
 q('restore').onclick=()=>{const row=layers.find(x=>x.id===q('deleted').value);if(!row)return;remember();row.deleted=false;row.hidden=false;mark(row);selected=row.id;choices();paint();inspect()};
 q('object').onchange=()=>{selected=q('object').value;paint();inspect()};
 ['x','y','w','h'].forEach(k=>q(k).oninput=()=>{if(q(k).value==='')return;const value=Number(q(k).value);if(!Number.isFinite(value))return;const row=current();remember();const ratio=row.original.w/row.original.h;row[k]=value;if(row.kind==='map'||row.kind==='icon'){if(k==='w')row.h=row.w/ratio;if(k==='h')row.w=row.h*ratio}clamp(row);mark(row);paint();inspect()});
 q('font').oninput=()=>{if(q('font').value==='')return;const row=current();remember();const n=Math.max(4,Math.min(400,Number(q('font').value)));if(!Number.isFinite(n))return;const factor=n/row.font_size;row.w*=factor;row.h*=factor;row.font_size=n;clamp(row);mark(row);paint();inspect()};
 q('text').oninput=()=>{const row=current();if(!row.content_editable)return;remember();row.changedText=q('text').value;mark(row)};
 q('color').onchange=()=>{const row=current();remember();row.changedColor=q('color').value;mark(row)};
 q('icon').onchange=()=>{const row=current();remember();row.changedIcon=q('icon').value;if(row.changedIcon==='Original')delete entries[row.id]?.icon;mark(row)};
 q('hidden').onchange=()=>{const row=current();remember();row.hidden=q('hidden').checked;mark(row);paint()};
 q('front').onclick=()=>{const row=current();remember();row.z=Math.min(3800,Math.max(...layers.map(x=>x.z))+1);mark(row);paint()};
 q('back').onclick=()=>{const row=current();remember();row.z=Math.max(-3800,Math.min(...layers.map(x=>x.z))-1);mark(row);paint()};
 q('undo').onclick=()=>{if(!history.length)return;future.push({layers:structuredClone(layers),entries:structuredClone(entries)});hydrate(history.pop())};
 q('redo').onclick=()=>{if(!future.length)return;history.push({layers:structuredClone(layers),entries:structuredClone(entries)});hydrate(future.pop())};
 q('guides').onchange=paint;
 stage.onpointerdown=e=>{const resize=e.target===handle;const id=resize?selected:e.target.dataset.id;if(!id)return;const row=layers.find(x=>x.id===id);if(!row?.editable)return;selected=id;remember();drag={x:e.clientX,y:e.clientY,row:structuredClone(row),resize};stage.setPointerCapture(e.pointerId);stage.focus();paint();inspect();e.preventDefault()};
 stage.onpointermove=e=>{if(!drag)return;const row=current(), dx=(e.clientX-drag.x)/scale,dy=(e.clientY-drag.y)/scale;const snap=v=>q('snap').checked?Math.round(v/10)*10:v;if(drag.resize){row.w=Math.max(1,snap(drag.row.w+dx));row.h=Math.max(1,snap(drag.row.h+dy));if(row.kind==='map'||row.kind==='icon')row.h=row.w*drag.row.h/drag.row.w}else{row.x=snap(drag.row.x+dx);row.y=snap(drag.row.y+dy)}clamp(row);mark(row);paint();inspect()};
 stage.onpointerup=()=>{drag=null};stage.onpointercancel=()=>{drag=null};
 stage.onkeydown=e=>{if(e.ctrlKey&&e.key==='z'){e.preventDefault();q('undo').click();return}if(e.key==='Delete'||e.key==='Backspace'){e.preventDefault();q('delete').click();return}const moves={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]};if(!moves[e.key]||!current())return;e.preventDefault();const row=current();remember();row.x+=moves[e.key][0]*(e.shiftKey?10:1);row.y+=moves[e.key][1]*(e.shiftKey?10:1);clamp(row);mark(row);paint();inspect()};
 const submit=action=>setTriggerValue('applied',{scene:data.scene,entries,action,nonce:Date.now()});
 q('apply').onclick=()=>submit('apply');q('generate').onclick=()=>submit('generate');
 q('reset').onclick=()=>setTriggerValue('applied',{scene:data.scene,entries:{},action:'reset',nonce:Date.now()});
 q('addtext').onclick=()=>{entries['custom.'+Date.now()]={text:'Tu texto',font_size:40,color:'#ffffff',x:100,y:100,w:500,h:120,z:3500};submit('apply')};
 q('addicon').onclick=()=>{entries['custom.'+Date.now()]={icon:'pin',x:100,y:100,w:88,h:88,z:3500};submit('apply')};
 const observer=new ResizeObserver(()=>{const outer=stage.clientWidth/frameW;scale=outer*fit;board.style.transform='scale('+scale+')';board.style.left=((frameW-1080*fit)/2*outer)+'px';board.style.top=((frameH-1920*fit)/2*outer)+'px';stage.style.height=(frameH*outer)+'px'});observer.observe(stage);
 paint();inspect();pending();return()=>{observer.disconnect();stage.onpointerdown=null;stage.onpointermove=null;stage.onpointerup=null;stage.onpointercancel=null;stage.onkeydown=null};
}
"""

_COMPONENT = st.components.v2.component('ecuador_vivo_layout_editor', html=HTML, css=CSS, js=JS)
SOURCE_MTIME = Path(__file__).stat().st_mtime_ns


def show_layout_editor(config, render_map, render_endcard=None, *, project, persist, key):
    """Draw the authoring canvas; commit validated layers before the next rerun.

    ``persist`` assigns the layout to the caller's design. The shortcut saves
    the draft and navigates to Exportar, without starting an export itself.
    """
    st.subheader('Lienzo de la maqueta')
    st.caption('Mueve, redimensiona, añade o elimina elementos aquí. OK aplica y guarda el diseño; no necesitas otra vista previa.')
    names = ['Mapa']+(['Métricas'] if render_endcard else [])
    card = st.segmented_control('Tarjeta que quieres editar', names, default='Mapa', key=key+'_card')
    scene_name = 'endcard' if card == 'Métricas' else 'map'
    generation_key = key+'_generate'
    capture = {**config, '_layout_capture': True}
    image = render_endcard(capture) if scene_name == 'endcard' else render_map(capture)
    scene = image.info.get('visual_scene')
    if not scene:
        st.warning('Este estilo no tiene capas editables. Selecciona Maqueta Ecuador Vivo.')
        return False
    component_key = key+'_canvas_'+scene_name

    def applied():
        state = st.session_state.get(component_key, {})
        message = state.get('applied')
        if not message or message.get('scene') != scene_name:
            return
        try:
            layout = copy.deepcopy(config.get('visual_layout', {}))
            layout[scene_name] = message['entries']
            layout['full_canvas'] = True
            layout = clean_layout(layout)
            allowed = {row['id'] for row in scene.items if row['editable']}
            unknown = {name for name in layout[scene_name] if name not in allowed and not name.startswith('custom.')}
            if unknown:
                raise ValueError('La maqueta contiene elementos que no pertenecen a esta tarjeta.')
            persist(layout)
            draft_key = f'_layout_draft_{st.session_state.get("revision", 0)}'
            if draft_key not in st.session_state:
                st.session_state[draft_key] = str(STORE/'projects'/('borrador-maqueta-'+dt.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6]+'.json'))
            target = Path(st.session_state[draft_key])
            write_json(target, project)
            st.session_state[key+'_saved'] = str(target)
            if message.get('action') == 'generate':
                st.session_state['studio_phase'] = 'Exportar'
        except (ValueError, KeyError, TypeError) as error:
            st.session_state[key+'_error'] = str(error)

    payload = {**scene.payload(), 'entries': scene.overrides, 'icons': list(ICONS)}
    from storyboard import dimensions
    payload['frame_width'], payload['frame_height'] = dimensions(config)
    payload['frame_background'] = config.get('delivery', {}).get('background', config.get('background', '#04151e'))
    st.caption(f'{payload["frame_width"]} × {payload["frame_height"]} px · el lienzo muestra el formato de salida.')
    global _COMPONENT
    try:
        _COMPONENT(key=component_key, data=payload, on_applied_change=applied, width='stretch', height='content')
    except StreamlitAPIException as error:
        # Headless tests/new runtimes have their own registry, but Python's
        # module cache can survive them. Register once on that transition;
        # never re-register on each normal user interaction.
        if 'is not registered' not in str(error):
            raise
        _COMPONENT = st.components.v2.component('ecuador_vivo_layout_editor', html=HTML, css=CSS, js=JS)
        _COMPONENT(key=component_key, data=payload, on_applied_change=applied, width='stretch', height='content')
    from workspace import download_artwork
    download_artwork(image, config, key=key+'_png')
    with st.expander('Ayuda del lienzo'):
        st.caption('Selecciona cualquier texto y pulsa Eliminar elemento (o Supr en el lienzo). Deshacer funciona durante la edición; Recuperar elemento también después de guardar. Quitar una cifra del diseño no cambia los cálculos ni las fuentes.')
        st.caption('Aplica con OK antes de cambiar de fecha, tarjeta o apartado. Los textos, colores e iconos se redibujan al aplicar. Las medidas son coordenadas de la maqueta base (1080 × 1920); el formato final se elige en Montaje.')
    if st.session_state.get(key+'_saved'):
        st.caption('Distribución guardada. Este lienzo y el video usan las mismas capas. Exportar conserva los datos y fuentes, incluso si quitas sus rótulos del diseño.')
    if st.session_state.get(key+'_error'):
        st.error(st.session_state.pop(key+'_error'))
    return st.session_state.pop(generation_key, False)
