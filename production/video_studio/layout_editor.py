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
<div class="editor" lang="es">
 <div class="toolbar" role="group" aria-label="Herramientas del lienzo">
  <div class="tools" role="group" aria-label="Historial">
   <button type="button" id="undo">Deshacer</button><button type="button" id="redo">Rehacer</button>
  </div>
  <div class="tools" role="group" aria-label="Añadir elementos">
   <button type="button" id="addtext">Añadir texto</button><button type="button" id="addicon">Añadir icono</button>
  </div>
  <div class="tools view-tools" role="group" aria-label="Ayudas de edición">
   <label>Zoom<select id="zoom"><option value="fit">Ajustar</option><option value="25">25%</option><option value="50">50%</option><option value="75">75%</option><option value="100">100%</option><option value="125">125%</option><option value="150">150%</option><option value="200">200%</option></select></label>
   <label><input id="guides" type="checkbox" checked> Guías sociales</label>
   <label><input id="snap" type="checkbox" checked> Ajustar a 10 px</label>
  </div>
 </div>
 <div class="workspace">
  <aside class="layers-panel" aria-label="Capas de la escena">
   <h3>Capas</h3><div id="layers"></div>
   <div class="stack"><button type="button" id="layerup">Subir capa</button><button type="button" id="layerdown">Bajar capa</button></div>
  </aside>
  <div class="canvas-area">
   <div class="viewport"><div class="stage" tabindex="0" aria-label="Lienzo editable del video" aria-describedby="keyboard-help"><div class="board"></div></div></div>
   <p class="muted" id="keyboard-help">Mayús + clic: selección múltiple · Arrastra el fondo: seleccionar área · Ctrl+A: seleccionar · Flechas: mover · Supr: eliminar · Alt + arrastre: pan.</p>
  </div>
  <div class="inspector" role="group" aria-label="Propiedades del elemento">
   <div class="inspector-fields">
    <fieldset>
     <legend>Elemento seleccionado</legend>
     <label>Elemento<select id="object"></select></label>
     <label>Nombre de capa<input id="name" type="text" maxlength="180"></label>
     <label class="checkbox-label"><input id="locked" type="checkbox"> Bloquear elemento</label>
     <p id="hint">Selecciona y arrastra un elemento. La esquina inferior derecha cambia su tamaño.</p>
     <button type="button" id="delete" class="danger">Eliminar elemento</button>
    </fieldset>
    <fieldset>
     <legend>Posición y tamaño <span class="muted">· px</span></legend>
     <div class="coordinates">
      <label>X<input id="x" type="number" step="1"></label><label>Y<input id="y" type="number" step="1"></label>
      <label>Ancho<input id="w" type="number" min="1" step="1"></label><label>Alto<input id="h" type="number" min="1" step="1"></label>
     </div>
    </fieldset>
    <fieldset>
     <legend>Contenido y estilo</legend>
     <label>Texto<textarea id="text" rows="3" maxlength="500" aria-describedby="hint"></textarea></label>
     <div class="coordinates">
      <label>Tamaño de letra<input id="font" type="number" min="4" max="400"></label>
      <label>Color del texto<input id="color" type="color"></label>
     </div>
     <label>Icono<select id="icon"></select></label>
    </fieldset>
    <details>
     <summary>Organizar y recuperar</summary>
     <div class="detail-fields">
      <label class="checkbox-label"><input id="hidden" type="checkbox"> Ocultar elemento</label>
      <div class="stack"><button type="button" id="front">Al frente</button><button type="button" id="back">Al fondo</button></div>
      <label>Elementos eliminados<select id="deleted"></select></label>
      <button type="button" id="restore">Recuperar elemento</button>
      <button type="button" id="reset">Restaurar tarjeta</button>
     </div>
    </details>
   </div>
   <div class="inspector-actions">
    <p id="notice" role="status"></p>
    <p id="pending" role="status" aria-live="polite">Sin cambios por aplicar.</p>
    <button type="button" id="apply" class="primary">OK · aplicar y guardar</button>
    <button type="button" id="generate">Guardar e ir a exportar</button>
   </div>
  </div>
 </div>
 <p class="foot">Los mapas conservan su proporción. La distancia y el norte viajan con el mapa; la leyenda conserva sus valores. Las guías no se exportan.</p>
</div>
"""

CSS = """
.editor{--muted:var(--st-gray-text-color,#b3c7cd);--focus:var(--st-primary-color);--line:var(--st-border-color);font-family:var(--st-font);font-size:1rem;line-height:1.5;color:var(--st-text-color);width:100%;container-type:inline-size}
*,*::before,*::after{box-sizing:border-box}
.toolbar,.tools,.stack{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.toolbar{gap:16px;padding:12px 0;margin-bottom:16px;border-block:1px solid var(--line)}
.view-tools{margin-left:auto;gap:12px}
.toolbar label,.checkbox-label{display:flex;align-items:center;gap:8px;min-height:44px;font-size:.875rem}
button,input,select,textarea{font:inherit;color:var(--st-text-color);background:var(--st-secondary-background-color);border:1px solid var(--line);border-radius:var(--st-button-radius,6px);padding:8px 12px;min-height:44px;max-width:100%}
button{cursor:pointer;font-size:.875rem;font-weight:600;line-height:1.4}
button:hover:not(:disabled){border-color:var(--focus)}
:is(button,input,select,textarea,summary,.stage):focus-visible{outline:3px solid var(--focus);outline-offset:3px}
button:disabled,input:disabled,textarea:disabled,select:disabled{opacity:.5;cursor:not-allowed}
input[type=checkbox]{min-height:auto;width:18px;height:18px;margin:0;accent-color:var(--focus);flex-shrink:0}
textarea{resize:vertical;line-height:1.5}
.workspace{display:grid;grid-template-columns:minmax(140px,190px) minmax(0,1fr) minmax(260px,300px);gap:16px;align-items:start}
.layers-panel{min-width:0;border:1px solid var(--line);padding:12px;border-radius:var(--st-base-radius,6px)}
.layers-panel h3{font-size:.875rem;margin:0 0 8px;font-weight:600}
#layers{max-height:58vh;overflow:auto;margin-bottom:12px}
.layer-row{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:4px;margin-bottom:4px}
.layer-row button{padding:4px;font-size:.75rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.layer-row[aria-current=true]{outline:2px solid var(--focus);outline-offset:-2px}
.viewport{width:100%;max-height:78vh;overflow:auto;scrollbar-gutter:stable}
.canvas-area{display:flex;flex-direction:column;align-items:center;gap:12px;min-width:0;padding:16px;background:var(--st-secondary-background-color);border-radius:var(--st-base-radius,6px)}
.stage{position:relative;overflow:hidden;background:var(--st-background-color);border:1px solid var(--line);touch-action:none;box-sizing:border-box;margin:auto}
.board{position:absolute;top:0;left:0;width:1080px;height:1920px;transform-origin:top left}
.piece{position:absolute;object-fit:fill;user-select:none;touch-action:none;-webkit-user-drag:none}
.selected{position:absolute;box-sizing:border-box;border:3px solid #fff45c;pointer-events:none}
.piece.multi-selected{outline:2px solid #fff45c;outline-offset:-2px}
.marquee{position:absolute;border:2px dashed #fff45c;background:#fff45c22;pointer-events:none;z-index:5100}
.handle{position:absolute;bottom:-12px;right:-12px;width:24px;height:24px;background:#fff45c;border:2px solid #071721;pointer-events:auto;cursor:nwse-resize}
.guide{position:absolute;box-sizing:border-box;border:3px dashed #f5c24a;pointer-events:none;opacity:.65}
.inspector{min-width:0;border:1px solid var(--line);border-radius:var(--st-base-radius,6px);overflow:hidden}
.inspector-fields{display:flex;flex-direction:column;gap:16px;max-height:52vh;overflow:auto;scrollbar-gutter:stable;padding:16px}
fieldset{border:0;margin:0;padding:0;min-width:0;display:flex;flex-direction:column;gap:12px}
legend{font-weight:600;font-size:.875rem;margin-bottom:12px;padding:0}
.inspector label{display:flex;flex-direction:column;gap:4px;font-size:.875rem;min-width:0}
.inspector input,.inspector select,.inspector textarea{width:100%;min-width:0}
.inspector input[type=color]{padding:4px;cursor:pointer}
.inspector .checkbox-label{flex-direction:row}
.inspector input[type=checkbox]{width:18px}
.coordinates{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px}
details{border-top:1px solid var(--line);padding-top:8px}
summary{cursor:pointer;font-size:.875rem;font-weight:600;min-height:44px;padding:12px 0}
.detail-fields{display:flex;flex-direction:column;gap:12px;padding-top:8px}
.stack button{flex:1}
.danger{color:var(--st-red-text-color);border-color:var(--st-border-color)}
.inspector-actions{display:flex;flex-direction:column;gap:8px;padding:16px;border-top:1px solid var(--line);background:var(--st-secondary-background-color)}
.primary{background:var(--st-primary-color);color:#ffffff;border-color:var(--st-primary-color)}
.primary:hover:not(:disabled){outline:1px solid var(--st-text-color)}
p{font-size:.875rem;line-height:1.5;margin:0;overflow-wrap:anywhere}
.muted,#hint,.foot{color:var(--muted)}
.foot{margin-top:16px;max-width:85ch}
#notice:empty{display:none}
#notice{color:var(--st-yellow-text-color)}
#pending{font-weight:500}
@container(max-width:720px){.workspace{grid-template-columns:minmax(0,1fr);gap:16px}.view-tools{margin-left:0}.inspector-fields{max-height:none;overflow:visible}.canvas-area{padding:12px}}
@container(min-width:721px) and (max-width:1040px){.workspace{grid-template-columns:minmax(0,1fr) minmax(260px,300px)}.layers-panel{grid-column:1 / -1}#layers{max-height:160px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}}
@media(max-width:720px){.workspace{grid-template-columns:minmax(0,1fr);gap:16px}.view-tools{margin-left:0}.inspector-fields{max-height:none;overflow:visible}}
"""

JS = """
export default function(component){
 const {parentElement:root,data,setTriggerValue}=component;
 const q=id=>root.querySelector('#'+id), board=root.querySelector('.board'), stage=root.querySelector('.stage');
 const layers=structuredClone(data.layers), entries=structuredClone(data.entries||{});
 const originalEntries=JSON.stringify(entries);
 let recoveryWarning='';
 const pending=()=>{const dirty=JSON.stringify(entries)!==originalEntries;q('pending').textContent=(dirty?(data.workspace_mode?'Cambios pendientes · guardado automático':'Cambios pendientes: pulsa OK para confirmar el diseño.'):'Sin cambios por aplicar.')+recoveryWarning;component.onPending?.(dirty)};
 let selected=layers.find(x=>x.editable)?.id, selection=new Set(selected?[selected]:[]), scale=1, history=[], future=[], drag=null, pan=null, marquee=null;
 const authorW=data.width||1080, authorH=data.height||1920, viewport=root.querySelector('.viewport');
 board.style.width=authorW+'px';board.style.height=authorH+'px';
 const frameW=data.frame_width||1080, frameH=data.frame_height||1920;
 const fit=Math.min(frameW/authorW,frameH/authorH);
 stage.style.background=data.frame_background||'#04151e';
 stage.style.aspectRatio=frameW+'/'+frameH;
 stage.style.setProperty('--frame-ratio',String(frameW/frameH));
 q('guides').disabled=frameW/frameH!==1080/1920;
 if(q('guides').disabled)q('guides').checked=false;
 const imgs=new Map();
 // Reconcile pixel surfaces across controlled snapshots; do not blank the board.
 const generation=board.dataset.generation=String(Number(board.dataset.generation||0)+1);
 const pixelTasks=[],pixelUpdates=[];
 const setPixels=(element,src)=>{if(element.getAttribute('src')===src)return;const next=new Image();next.src=src;pixelTasks.push(next.decode().then(()=>{pixelUpdates.push([element,src])}))};
 const bg=board.querySelector('img[data-background]')||document.createElement('img');bg.dataset.background='true';setPixels(bg,data.background);bg.alt='';bg.style.cssText='position:absolute;pointer-events:none';bg.style.width=authorW+'px';bg.style.height=authorH+'px';if(!bg.isConnected)board.append(bg);
 const retained=new Set(layers.map(row=>row.id));
 layers.forEach(row=>{const el=[...board.querySelectorAll('.piece')].find(el=>el.dataset.id===row.id)||document.createElement('img');setPixels(el,row.src);el.className='piece';el.alt=row.label;el.draggable=false;el.dataset.id=row.id;el.style.pointerEvents=row.editable?'auto':'none';imgs.set(row.id,el)});
 Promise.all(pixelTasks).then(()=>{
  if(board.dataset.generation!==generation)return;
  // The scientific date/background and cartographic pieces change together.
  // Keep the previous composition during decode, including a scene switch.
  for(const [element,src] of pixelUpdates)element.src=src;
  board.querySelectorAll('.piece').forEach(el=>{if(!retained.has(el.dataset.id))el.remove()});
  for(const element of imgs.values())if(!element.isConnected)board.append(element);
  component.onPixels?.();
 }).catch(()=>{if(board.dataset.generation===generation)q('notice').textContent='No se pudo decodificar la composición; se conserva el último cuadro válido.'});
 const guide=document.createElement('div');guide.className='guide';guide.setAttribute('aria-hidden','true');guide.style.cssText='left:60px;top:190px;width:900px;height:1330px';board.append(guide);
 const box=document.createElement('div');box.className='selected';box.setAttribute('aria-hidden','true');const handle=document.createElement('div');handle.className='handle';box.append(handle);board.append(box);
 function choices(){
  q('object').innerHTML='';q('deleted').innerHTML='';
  layers.filter(x=>x.editable).forEach(row=>{const o=document.createElement('option');o.value=row.id;o.textContent=row.label+' · '+row.kind;(row.deleted?q('deleted'):q('object')).append(o)});
  if(!layers.some(x=>x.id===selected&&!x.deleted))selected=layers.find(x=>x.editable&&!x.deleted)?.id;
  q('restore').disabled=!q('deleted').options.length;
  q('layers').replaceChildren();
  [...layers].filter(row=>!row.deleted).sort((a,b)=>b.z-a.z).forEach(row=>{
   const item=document.createElement('div');item.className='layer-row';item.dataset.layer=row.id;
   const select=document.createElement('button');select.type='button';select.textContent=row.label;select.title=row.label;select.disabled=!row.editable;
   select.setAttribute('aria-pressed',String(selection.has(row.id)));select.onclick=e=>{choose(row.id,e.shiftKey);paint();inspect()};item.append(select);
   for(const [field,on,off] of [['hidden','Ver','Ocultar'],['locked','Desbloquear','Bloquear']]){
    const button=document.createElement('button');button.type='button';button.textContent=row[field]?on:off;button.title=button.textContent+' '+row.label;button.setAttribute('aria-label',button.title);button.disabled=!row.editable;
    button.setAttribute('aria-pressed',String(!!row[field]));
    if(field==='hidden'&&row.locked)button.disabled=true;
    button.onclick=()=>{remember();row[field]=!row[field];mark(row);choices();paint();inspect()};item.append(button);
   }
   q('layers').append(item);
  });
 }
 choices();
 q('icon').innerHTML=''; ['Original',...data.icons].forEach(label=>{const o=document.createElement('option');o.value=label;o.textContent=label;q('icon').append(o)});
 const current=()=>layers.find(x=>x.id===selected&&!x.deleted);
 function choose(id,extend=false){const row=layers.find(r=>r.id===id),members=data.free_scene&&row?.group_id?layers.filter(r=>r.group_id===row.group_id&&!r.deleted).map(r=>r.id):id?[id]:[];const remove=extend&&selection.has(id);if(!extend)selection.clear();members.forEach(member=>remove?selection.delete(member):selection.add(member));selected=selection.has(id)?id:[...selection].at(-1)}
 const selectedRows=()=>layers.filter(row=>selection.has(row.id)&&row.editable&&!row.deleted&&(!row.hidden||data.free_scene&&row.group_id));
 const movable=()=>selectedRows().filter(row=>!row.locked&&(!data.free_scene||!row.group_id||!layers.some(r=>r.group_id===row.group_id&&r.locked&&!r.deleted)));
 if(data.free_scene)choose(selected);
 const snapshot=()=>({layers:structuredClone(layers),entries:structuredClone(entries),selection:[...selection],selected});
 function persistPending(){if(!data.free_scene||!data.recovery_key||drag||marquee)return;try{if(JSON.stringify(entries)===originalEntries)sessionStorage.removeItem(data.recovery_key);else sessionStorage.setItem(data.recovery_key,JSON.stringify({entries,selection:[...selection],selected}));recoveryWarning=''}catch(error){recoveryWarning=' La copia por pestaña no se pudo guardar; aplica OK para guardar en disco.'}pending()}
 function validPending(saved){if(!saved||!saved.entries||Array.isArray(saved.entries)||typeof saved.entries!=='object'||!Array.isArray(saved.selection)||saved.selection.some(id=>typeof id!=='string'||!layers.some(r=>r.id===id)))return false;return Object.entries(saved.entries).every(([id,value])=>layers.some(r=>r.id===id)&&value&&typeof value==='object'&&!Array.isArray(value)&&Object.entries(value).every(([field,v])=>['x','y','w','h','z','font_size'].includes(field)?typeof v==='number'&&Number.isFinite(v)&&(!['w','h'].includes(field)||v>=1)&&(field!=='font_size'||v>=8&&v<=400):['hidden','deleted','locked'].includes(field)?typeof v==='boolean':['name','text','color','icon'].includes(field)?typeof v==='string'&&v.length<=(field==='text'?2000:180):false))}
 const remember=()=>{history.push(snapshot());if(history.length>40)history.shift();future=[]};
 const hydrate=state=>{layers.splice(0,layers.length,...structuredClone(state.layers));Object.keys(entries).forEach(k=>delete entries[k]);Object.assign(entries,structuredClone(state.entries));selection=new Set(state.selection||[]);selected=state.selected;choices();paint();inspect();pending();persistPending()};
 const clamp=row=>{if(row.kind==='map'||row.kind==='icon'){const factor=Math.min(1,authorW/Math.max(1,row.w),authorH/Math.max(1,row.h));row.w*=factor;row.h*=factor}row.w=Math.max(1,Math.min(authorW,Math.round(row.w)));row.h=Math.max(1,Math.min(authorH,Math.round(row.h)));row.x=Math.max(0,Math.min(authorW-row.w,Math.round(row.x)));row.y=Math.max(0,Math.min(authorH-row.h,Math.round(row.y)))};
 const mark=row=>{entries[row.id]={...(entries[row.id]||{}),x:row.x,y:row.y,w:row.w,h:row.h,z:row.z,hidden:row.hidden,deleted:!!row.deleted,locked:!!row.locked,name:row.label};if(row.font_size){if(data.free_scene&&row.original.font_size===row.font_size)delete entries[row.id].font_size;else entries[row.id].font_size=row.font_size}if(row.content_editable&&row.changedText!==undefined)entries[row.id].text=row.changedText;if(row.changedColor)entries[row.id].color=row.changedColor;if(row.changedIcon&&row.changedIcon!=='Original')entries[row.id].icon=row.changedIcon;pending();persistPending()};
 function paint(){
  if(data.free_scene){for(const id of [...selection]){const group=layers.find(r=>r.id===id)?.group_id;if(group)layers.filter(r=>r.group_id===group&&!r.deleted).forEach(r=>selection.add(r.id))}}
  layers.forEach(row=>{const el=imgs.get(row.id);Object.assign(el.style,{display:row.deleted||row.hidden?'none':'block',left:row.x+'px',top:row.y+'px',width:row.w+'px',height:row.h+'px',zIndex:String(Math.round(row.z)+100),cursor:row.editable?'move':'default'})});
  selection=new Set([...selection].filter(id=>layers.some(row=>row.id===id&&!row.deleted)));if(!selection.has(selected))selected=[...selection].at(-1);
  layers.forEach(row=>imgs.get(row.id).classList.toggle('multi-selected',selection.has(row.id)));
  const rows=selectedRows(),row=current();box.style.display=rows.length?'block':'none';if(rows.length){const left=Math.min(...rows.map(r=>r.x)),top=Math.min(...rows.map(r=>r.y)),right=Math.max(...rows.map(r=>r.x+r.w)),bottom=Math.max(...rows.map(r=>r.y+r.h));Object.assign(box.style,{left:left+'px',top:top+'px',width:(right-left)+'px',height:(bottom-top)+'px',zIndex:'5000'});handle.style.display=rows.some(r=>r.locked)?'none':'block'}
  if(data.free_scene){handle.style.display=rows.length&&!rows.some(r=>r.locked)?'block':'none';if(rows.length)Object.assign(handle.style,{left:(Math.max(...rows.map(r=>r.x+r.w))*scale+parseFloat(board.style.left||'0')-12)+'px',top:(Math.max(...rows.map(r=>r.y+r.h))*scale+parseFloat(board.style.top||'0')-12)+'px',right:'auto',bottom:'auto',width:'24px',height:'24px',borderWidth:'2px',zIndex:'5001'})}
  guide.style.zIndex='4999';guide.style.display=q('guides').checked?'block':'none';
  q('undo').disabled=!history.length;q('redo').disabled=!future.length;
  q('delete').disabled=!movable().length;
  ['layerup','layerdown'].forEach(id=>q(id).disabled=!current()||!!current()?.locked);
  q('layers').querySelectorAll('.layer-row').forEach(item=>{item.setAttribute('aria-current',String(selection.has(item.dataset.layer)));item.querySelector('button').setAttribute('aria-pressed',String(selection.has(item.dataset.layer)))});
  const small=layers.filter(x=>x.editable&&!x.hidden&&!x.deleted&&x.kind==='text'&&x.font_size&&x.font_size<20).length;
  q('notice').textContent=small?small+' textos tienen menos de 20 px: revisa su legibilidad.':'';
 }
 function inspect(){const row=current();if(!row){['x','y','w','h','font','text','color','icon','hidden','front','back'].forEach(k=>q(k).disabled=true);q('hint').textContent='No quedan elementos seleccionables. Recupera un elemento o añade texto.';return}['x','y','w','h','hidden','front','back'].forEach(k=>q(k).disabled=false);q('object').value=selected;['x','y','w','h'].forEach(k=>q(k).value=row[k]);q('font').disabled=!row.font_size;q('font').value=row.font_size||'';q('text').disabled=!row.content_editable;q('text').value=row.changedText??entries[row.id]?.text??row.text??'';q('color').disabled=row.kind!=='text';q('color').value=/^#[0-9a-f]{6}$/i.test(row.changedColor||row.color)?(row.changedColor||row.color):'#ffffff';q('icon').disabled=row.kind!=='icon';q('icon').value=row.changedIcon||entries[row.id]?.icon||'Original';q('hidden').checked=!!row.hidden;q('hint').textContent=row.kind==='map'?'Arrastra el mapa completo; al ampliar, se amplían también su norte y distancia.':!row.content_editable&&row.kind==='text'?'Cifra/fecha vinculada a datos. Puedes moverla, ajustar letra/color o quitarla del diseño, pero no cambiar su valor.':'Arrastra o ajusta las medidas. OK redibuja el texto en este mismo lienzo.'}
 const inspectBase=inspect;
 q('hint').setAttribute('role','status');q('hint').setAttribute('aria-live','polite');stage.setAttribute('aria-keyshortcuts','ArrowLeft ArrowRight ArrowUp ArrowDown Delete Control+a Control+z Control+y');
 inspect=()=>{inspectBase();const row=current();q('name').disabled=!row;q('locked').disabled=!row;q('name').value=row?.label||'';q('locked').checked=!!row?.locked;if(row?.locked){['x','y','w','h','font','text','color','icon','hidden','front','back'].forEach(id=>q(id).disabled=true);q('hint').textContent='Elemento bloqueado. Desbloquéalo para editarlo.'}if(selection.size>1){['x','y','w','h','font','text','color','icon','hidden','front','back','name','locked','layerup','layerdown'].forEach(id=>q(id).disabled=true);q('hint').textContent=selection.size+' elementos seleccionados. Arrastra o usa flechas para mover juntos; esquina para escalar. Los bloqueados permanecen fijos.'}};
 q('name').onchange=()=>{const row=current();if(!row)return;remember();row.label=q('name').value;mark(row);choices();paint();inspect()};
 q('locked').onchange=()=>{const row=current();if(!row)return;remember();row.locked=q('locked').checked;mark(row);choices();paint();inspect()};
 function reorder(direction){const row=current();if(!row||row.locked)return;const ordered=[...layers].filter(x=>x.editable&&!x.deleted).sort((a,b)=>a.z-b.z);const index=ordered.indexOf(row),next=index+direction;if(next<0||next>=ordered.length||ordered[next].locked)return;remember();const other=ordered[next],z=row.z;row.z=other.z;other.z=z;mark(row);mark(other);choices();paint();inspect()}
 q('layerup').onclick=()=>reorder(1);q('layerdown').onclick=()=>reorder(-1);
 q('delete').onclick=()=>{const rows=movable();if(!rows.length)return;remember();rows.forEach(row=>{row.deleted=true;mark(row)});choose(null);choices();paint();inspect()};
 q('restore').onclick=()=>{const row=layers.find(x=>x.id===q('deleted').value);if(!row)return;remember();row.deleted=false;row.hidden=false;mark(row);choose(row.id);choices();paint();inspect()};
 q('object').onchange=()=>{choose(q('object').value);paint();inspect()};
 ['x','y','w','h'].forEach(k=>q(k).oninput=()=>{if(q(k).value==='')return;const value=Number(q(k).value);if(!Number.isFinite(value))return;const row=current();remember();const ratio=row.original.w/row.original.h;row[k]=value;if(row.kind==='map'||row.kind==='icon'){if(k==='w')row.h=row.w/ratio;if(k==='h')row.w=row.h*ratio}clamp(row);mark(row);paint();inspect()});
 q('font').oninput=()=>{if(q('font').value==='')return;const value=Number(q('font').value);if(!Number.isFinite(value))return;const row=current();remember();const n=data.free_scene?Math.round(Math.max(8,Math.min(400,value))):Math.max(4,Math.min(400,value));const factor=n/row.font_size;row.w*=factor;row.h*=factor;row.font_size=n;clamp(row);mark(row);paint();inspect()};
 q('text').oninput=()=>{const row=current();if(!row.content_editable)return;remember();row.changedText=q('text').value;mark(row)};
 q('color').onchange=()=>{const row=current();remember();row.changedColor=q('color').value;mark(row)};
 q('icon').onchange=()=>{const row=current();remember();row.changedIcon=q('icon').value;if(row.changedIcon==='Original')delete entries[row.id]?.icon;mark(row)};
 q('hidden').onchange=()=>{const row=current();remember();row.hidden=q('hidden').checked;mark(row);paint()};
 q('front').onclick=()=>{const row=current();remember();row.z=Math.min(3800,Math.max(...layers.map(x=>x.z))+1);mark(row);paint()};
 q('back').onclick=()=>{const row=current();remember();row.z=Math.max(-3800,Math.min(...layers.map(x=>x.z))-1);mark(row);paint()};
 q('undo').onclick=()=>{if(!history.length)return;future.push(snapshot());hydrate(history.pop())};
 q('redo').onclick=()=>{if(!future.length)return;history.push(snapshot());hydrate(future.pop())};
 q('guides').onchange=paint;
 function localPoint(e){const rect=board.getBoundingClientRect();return{x:(e.clientX-rect.left)/scale,y:(e.clientY-rect.top)/scale}}
 function moveTogether(rows,dx,dy){if(!rows.length)return;dx=Math.max(-Math.min(...rows.map(r=>r.x)),Math.min(authorW-Math.max(...rows.map(r=>r.x+r.w)),dx));dy=Math.max(-Math.min(...rows.map(r=>r.y)),Math.min(authorH-Math.max(...rows.map(r=>r.y+r.h)),dy));rows.forEach(before=>{const row=layers.find(r=>r.id===before.id);row.x=Math.round(before.x+dx);row.y=Math.round(before.y+dy);mark(row)})}
 const marqueeBox=document.createElement('div');marqueeBox.className='marquee';marqueeBox.style.display='none';board.append(marqueeBox);
 function cancelGesture(){if(drag)hydrate(drag.before);if(marquee)hydrate(marquee.before);drag=null;pan=null;marquee=null;marqueeBox.style.display='none';persistPending()}
 function finishGesture(){if(drag){if(JSON.stringify(layers)!==JSON.stringify(drag.before.layers)){history.push(drag.before);if(history.length>40)history.shift();future=[]}else hydrate(drag.before)}drag=null;pan=null;marquee=null;marqueeBox.style.display='none';paint();persistPending()}
 function resizeFactor(rows,wanted,limit){const fonts=data.free_scene?rows.filter(r=>r.font_size).map(r=>r.font_size):[];const minimum=Math.max(.05,...fonts.map(n=>8/n)),maximum=Math.min(limit,...fonts.map(n=>400/n));return Math.max(minimum,Math.min(wanted,maximum))}
 stage.onpointerdown=e=>{if(e.altKey||e.button===1){pan={x:e.clientX,y:e.clientY,left:viewport.scrollLeft,top:viewport.scrollTop};stage.setPointerCapture(e.pointerId);e.preventDefault();return}const resize=e.target===handle,id=resize?selected:e.target.dataset.id;stage.focus({preventScroll:true});if(!id){const p=localPoint(e);marquee={...p,base:e.shiftKey?[...selection]:[],before:snapshot()};if(!e.shiftKey)choose(null);stage.setPointerCapture(e.pointerId);paint();inspect();e.preventDefault();return}const row=layers.find(x=>x.id===id);if(!row?.editable)return;if(e.shiftKey&&!resize){choose(id,true);paint();inspect();e.preventDefault();return}if(!selection.has(id))choose(id);paint();inspect();if(row.locked||resize&&selectedRows().some(r=>r.locked))return;drag={x:e.clientX,y:e.clientY,rows:structuredClone(movable()),resize,before:snapshot()};stage.setPointerCapture(e.pointerId);e.preventDefault()};
 stage.onpointermove=e=>{
  if(pan){viewport.scrollLeft=pan.left+pan.x-e.clientX;viewport.scrollTop=pan.top+pan.y-e.clientY;return}
  if(marquee){const p=localPoint(e),x=Math.min(p.x,marquee.x),y=Math.min(p.y,marquee.y),w=Math.abs(p.x-marquee.x),h=Math.abs(p.y-marquee.y);Object.assign(marqueeBox.style,{display:'block',left:x+'px',top:y+'px',width:w+'px',height:h+'px'});selection=new Set([...marquee.base,...layers.filter(r=>r.editable&&!r.deleted&&!r.hidden&&!r.locked&&r.x<x+w&&r.x+r.w>x&&r.y<y+h&&r.y+r.h>y).map(r=>r.id)]);selected=[...selection].at(-1);paint();inspect();return}
  if(!drag)return;let dx=(e.clientX-drag.x)/scale,dy=(e.clientY-drag.y)/scale;
  if(e.shiftKey&&!drag.resize){if(Math.abs(dx)>Math.abs(dy))dy=0;else dx=0}
  const snap=v=>q('snap').checked?Math.round(v/10)*10:v;
  if(drag.resize&&drag.rows.length>1){
   const x=Math.min(...drag.rows.map(r=>r.x)),y=Math.min(...drag.rows.map(r=>r.y)),w=Math.max(...drag.rows.map(r=>r.x+r.w))-x,h=Math.max(...drag.rows.map(r=>r.y+r.h))-y;
   const factor=resizeFactor(drag.rows,Math.min((w+dx)/w,(h+dy)/h),Math.min((authorW-x)/w,(authorH-y)/h));
   drag.rows.forEach(before=>{const row=layers.find(r=>r.id===before.id);row.x=x+(before.x-x)*factor;row.y=y+(before.y-y)*factor;row.w=before.w*factor;row.h=before.h*factor;if(data.free_scene&&before.font_size)row.font_size=Math.max(8,Math.min(400,Math.round(before.font_size*factor)));clamp(row);mark(row)})
  }else if(drag.resize){
   const before=drag.rows[0],row=current();row.w=Math.max(1,snap(before.w+dx));row.h=Math.max(1,snap(before.h+dy));
   if(data.free_scene&&row.kind==='text'&&before.font_size){const factor=resizeFactor([before],row.w/before.w,Math.min((authorW-row.x)/before.w,(authorH-row.y)/before.h));row.w=before.w*factor;row.h=before.h*factor;row.font_size=Math.round(before.font_size*factor)}
   else if(row.kind==='map'||row.kind==='icon')row.h=row.w*before.h/before.w;
   clamp(row);mark(row)
  }else moveTogether(drag.rows,snap(dx),snap(dy));paint();inspect()
 };
 stage.onpointerup=finishGesture;stage.onpointercancel=cancelGesture;
 stage.onkeydown=e=>{if(e.key!=='Escape'&&(drag||marquee))finishGesture();if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='a'){e.preventDefault();selection=new Set(layers.filter(r=>r.editable&&!r.hidden&&!r.deleted&&!r.locked).map(r=>r.id));selected=[...selection].at(-1);paint();inspect();return}if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='z'){e.preventDefault();q(e.shiftKey?'redo':'undo').click();return}if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='y'){e.preventDefault();q('redo').click();return}if(e.key==='Escape'){cancelGesture();choose(null);paint();inspect();return}if(e.key==='Delete'||e.key==='Backspace'){e.preventDefault();q('delete').click();return}const moves={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]};if(!moves[e.key]||!movable().length)return;e.preventDefault();const rows=structuredClone(movable());remember();moveTogether(rows,moves[e.key][0]*(e.shiftKey?10:1),moves[e.key][1]*(e.shiftKey?10:1));paint();inspect()};
 const submit=action=>{if(drag||marquee)finishGesture();persistPending();setTriggerValue('applied',{scene:data.scene,entries,selection:[...selection],action,nonce:Date.now()})};
 q('apply').onclick=()=>submit('apply');q('generate').onclick=()=>submit('generate');
 q('reset').onclick=()=>setTriggerValue('applied',{scene:data.scene,entries:{},action:'reset',nonce:Date.now()});
 q('addtext').onclick=()=>{entries['custom.'+Date.now()]={text:'Tu texto',font_size:40,color:'#ffffff',x:100,y:100,w:500,h:120,z:3500};submit('apply')};
 q('addicon').onclick=()=>{entries['custom.'+Date.now()]={icon:'pin',x:100,y:100,w:88,h:88,z:3500};submit('apply')};
 if(data.free_scene){q('text').maxLength=2000;q('font').min=8;viewport.style.padding='12px';stage.style.overflow='visible';board.style.overflow='hidden';stage.append(handle)}
 if(data.free_scene)q('addtext').onclick=()=>{entries['custom.'+Date.now()]={text:'Tu texto',font_size:Math.min(40,Math.round(authorW*.1)),color:'#ffffff',x:20,y:20,w:Math.min(500,authorW-40),h:Math.min(120,authorH-40),z:3500};submit('apply')};
 if(data.free_scene){q('addicon').hidden=true;q('reset').hidden=true;q('guides').checked=true;q('guides').disabled=false;q('guides').parentElement.lastChild.textContent=' Márgenes orientativos';const area=data.safe_area;Object.assign(guide.style,{left:area.x+'px',top:area.y+'px',width:area.width+'px',height:area.height+'px'});root.querySelector('.foot').textContent='Edición de escenas libres. Mayús + clic y selección por área amplían la selección. Flechas mueven; posición y tamaño también se editan con los campos numéricos. Aplica OK para confirmar el diseño; preview y export usan el mismo render.';q('generate').textContent='Guardar y revisar exportación';const duplicate=document.createElement('button');duplicate.type='button';duplicate.textContent='Duplicar selección';duplicate.onclick=()=>submit('duplicate');q('addtext').after(duplicate);const keyboard=stage.onkeydown;stage.onkeydown=e=>{const action={c:'copy',v:'paste',d:'duplicate'}[e.key.toLowerCase()];if((e.ctrlKey||e.metaKey)&&action){e.preventDefault();submit(action);return}keyboard(e)}}
 function resizeView(){const padding=data.free_scene?24:0;const available=Math.max(1,Math.min(viewport.clientWidth-padding,((data.workspace_mode?viewport.clientHeight:window.innerHeight*.78)-padding)*frameW/frameH));const outer=q('zoom').value==='fit'?available/frameW:Number(q('zoom').value)/100;scale=outer*fit;stage.style.width=(frameW*outer)+'px';stage.style.height=(frameH*outer)+'px';board.style.transform='scale('+scale+')';board.style.left=((frameW-authorW*fit)/2*outer)+'px';board.style.top=((frameH-authorH*fit)/2*outer)+'px';if(data.free_scene)paint();else if(scale>0)Object.assign(handle.style,{width:(24/scale)+'px',height:(24/scale)+'px',right:(-12/scale)+'px',bottom:(-12/scale)+'px',borderWidth:(2/scale)+'px'})}
 q('zoom').onchange=resizeView;
 let viewFrame=null;
 const observer=new ResizeObserver(()=>{if(viewFrame!==null)cancelAnimationFrame(viewFrame);viewFrame=requestAnimationFrame(()=>{viewFrame=null;resizeView()})});observer.observe(viewport);
 if(data.free_scene){for(const [label,action] of [['Agrupar selección','group'],['Desagrupar selección','ungroup']]){const button=document.createElement('button');button.type='button';button.textContent=label;button.onclick=()=>submit(action);q('addtext').after(button)}}
 if(data.free_scene&&data.recovery_key){try{const raw=sessionStorage.getItem(data.recovery_key);if(raw){const saved=JSON.parse(raw);if(!validPending(saved))throw new Error('invalid pending state');Object.assign(entries,saved.entries);layers.forEach(row=>{const value=entries[row.id];if(!value)return;for(const field of ['x','y','w','h','z','hidden','deleted','locked','font_size'])if(value[field]!==undefined)row[field]=value[field];if(value.name!==undefined)row.label=value.name;if(value.text!==undefined)row.changedText=value.text;if(value.color!==undefined)row.changedColor=value.color;clamp(row)});selection=new Set(saved.selection||[]);selected=saved.selected;choices()}}catch(error){recoveryWarning=' La copia por pestaña no se pudo recuperar; el diseño guardado permanece disponible.'}}
 if(data.workspace_mode){
  const baseInspect=inspect;inspect=()=>{baseInspect();component.onSelection?.([...selection],selected)};
  const basePaint=paint;paint=()=>{basePaint();component.onPaint?.()};
  component.canvasApi={state:()=>({entries:structuredClone(entries),ids:[...selection],selected}),
   choose:(id,extend=false)=>{choose(id,extend);paint();inspect()},resizeView,
   isGesture:()=>!!(drag||marquee),hasPending:()=>JSON.stringify(entries)!==originalEntries};
 }
 paint();inspect();pending();return()=>{cancelGesture();observer.disconnect();if(viewFrame!==null)cancelAnimationFrame(viewFrame);stage.onpointerdown=null;stage.onpointermove=null;stage.onpointerup=null;stage.onpointercancel=null;stage.onkeydown=null;if(data.workspace_mode){handle.remove();box.remove();guide.remove();marqueeBox.remove()}};
}
"""

_COMPONENT = st.components.v2.component('ecuador_vivo_layout_editor', html=HTML, css=CSS, js=JS)
SOURCE_MTIME = Path(__file__).stat().st_mtime_ns


def mount_canvas(payload, *, key, on_applied_change):
    """Reuse the exact legacy canvas for Studio scenes, including browser tests."""
    global _COMPONENT
    try:
        return _COMPONENT(key=key,data=payload,on_applied_change=on_applied_change,width='stretch',height='content')
    except StreamlitAPIException as error:
        if 'is not registered' not in str(error): raise
        _COMPONENT=st.components.v2.component('ecuador_vivo_layout_editor',html=HTML,css=CSS,js=JS)
        return _COMPONENT(key=key,data=payload,on_applied_change=on_applied_change,width='stretch',height='content')


def show_layout_editor(config, render_map, render_endcard=None, *, project, persist, key):
    """Draw the authoring canvas; commit validated layers before the next rerun.

    ``persist`` assigns the layout to the caller's design. The shortcut saves
    the draft and navigates to Exportar, without starting an export itself.
    """
    st.header('Diseña tu maqueta')
    st.caption('Selecciona en el lienzo y ajusta sus propiedades. OK guarda el diseño que usará el video.')
    names = ['Mapa']+(['Métricas'] if render_endcard else [])
    card = st.segmented_control('Tarjeta que quieres editar', names, default='Mapa', key=key+'_card', wrap=True)
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
        st.caption('Diseño guardado en borrador. Se aplicará al video; los datos y sus fuentes se conservan.')
    if st.session_state.get(key+'_error'):
        st.error(st.session_state.pop(key+'_error'))
    return st.session_state.pop(generation_key, False)
