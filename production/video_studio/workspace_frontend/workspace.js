// CCv2 controlled data + trigger commands; never interpolate authored content as HTML.
// https://docs.streamlit.io/develop/api-reference/custom-components/st.components.v2.component
export default function(component){
 const {parentElement:root,data,setTriggerValue}=component;
 // CCv2 can call the renderer again with the same ShadowRoot on data changes.
 // Dispose the previous controller before mounting the next controlled snapshot.
 root.__evsDispose?.();
 const q=id=>root.querySelector('#'+id),shell=root.querySelector('.evs');
 shell.dataset.version=String(data.version);shell.dataset.scene=data.scene;
 const paths={undo:'M8 4 3 9l5 5M3 9h10a6 6 0 0 1 0 12',redo:'m16 4 5 5-5 5M21 9H11a6 6 0 0 0 0 12',play:'m8 4 13 8-13 8Z',pause:'M8 4v16M16 4v16',layers:'m12 3 10 5-10 5L2 8Zm-10 9 10 5 10-5M2 16l10 5 10-5',settings:'M4 5h16M4 12h16M4 19h16M8 2v6M16 9v6M10 16v6',menu:'M4 5h16M4 12h16M4 19h16',plus:'M12 4v16M4 12h16',copy:'M9 9h12v12H9ZM3 15V3h12',trash:'M3 6h18M9 6V3h6v3M6 6l1 15h10l1-15M10 10v7M14 10v7',up:'m5 14 7-7 7 7',down:'m5 10 7 7 7-7',group:'M3 3h18v18H3ZM7 7h4v4H7ZM13 13h4v4h-4Z',ungroup:'M3 8V3h5M16 3h5v5M21 16v5h-5M8 21H3v-5M7 7h4v4H7ZM13 13h4v4h-4Z',eye:'M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Zm10-3a3 3 0 1 0 0 6 3 3 0 0 0 0-6',hidden:'m3 3 18 18M2 12s4-7 10-7c6 0 10 7 10 7-1 2-2 3-4 4M6 6 2 12s4 7 10 7c2 0 4-1 5-2',lock:'M6 10h12v11H6ZM8 10V7a4 4 0 0 1 8 0v3',unlock:'M6 10h12v11H6ZM8 10V7a4 4 0 0 1 8 0',text:'M3 4h18M12 4v17M8 21h8',image:'M3 3h18v18H3ZM3 17l6-6 4 4 3-3 5 5M16 7h.01',video:'M3 6h13v12H3Zm13 4 5-3v10l-5-3',chart:'M4 3v18h17M8 17v-6M13 17V7M18 17V4',shape:'M4 4h16v16H4Z',audio:'M3 10v4h4l5 5V5l-5 5ZM16 8a6 6 0 0 1 0 8M19 5a10 10 0 0 1 0 14',mute:'M3 10v4h4l5 5V5l-5 5ZM16 9l5 6M21 9l-5 6',folder:'M3 5h7l2 3h9v12H3Z'};
 const svg=kind=>{const el=document.createElementNS('http://www.w3.org/2000/svg','svg');el.setAttribute('viewBox','0 0 24 24');el.setAttribute('aria-hidden','true');const path=document.createElementNS(el.namespaceURI,'path');path.setAttribute('d',paths[kind]||paths.shape);el.append(path);return el};
 for(const [id,icon] of Object.entries({undo:'undo',redo:'redo',play:'play','project-menu':'menu','toggle-left':'layers','toggle-right':'settings',layerup:'up',layerdown:'down',group:'group',ungroup:'ungroup',delete:'trash','scene-add':'plus','scene-duplicate':'copy','scene-remove':'trash','timeline-collapse':'down'}))q(id).replaceChildren(svg(icon));
 let ui={tab:'layers',zoom:'fit',guides:true,snap:true,ids:[],selected:null,timeZoom:100,left:false,right:false,collapsed:false,mode:'edit',movieTime:0};
 try{Object.assign(ui,JSON.parse(sessionStorage.getItem(data.ui_key)||'{}'))}catch{}
 if(ui.scene!==data.scene){ui.ids=[];ui.selected=null;if(ui.mode==='movie')ui.mode='edit'}ui.scene=data.scene;
 let disposed=false,busy=false,saveTimer=null,pollTimer=null,contextKey=null,movieReady=false;
 const saveUi=()=>{try{sessionStorage.setItem(data.ui_key,JSON.stringify(ui))}catch{q('workspace-status').textContent='No se pudieron conservar las preferencias por pestaña.'}};
 const state=()=>component.canvasApi?.state()||{entries:{},ids:[],selected:null};
 const status=text=>q('workspace-status').textContent=text;
 function send(action,values={}){
  if(disposed||busy)return;
  if(q('workspace-dialog').open)q('workspace-dialog').close();
  clearTimeout(saveTimer);const s=state();ui.ids=s.ids;ui.selected=s.selected;saveUi();
  busy=true;q('save-state').textContent='Guardando…';q('save-state').dataset.state='dirty';
  setTriggerValue('command',{action,scene:data.scene,version:data.version,entries:s.entries,ids:s.ids,...values,nonce:Date.now()});
 }
 let failedEntries=null;
 const autosave=()=>{clearTimeout(saveTimer);if(data.error&&failedEntries===JSON.stringify(state().entries))return;if(!disposed&&!busy&&component.canvasApi?.hasPending())saveTimer=setTimeout(()=>{if(!component.canvasApi.isGesture())send('canvas');else autosave()},350)};
 component.onPending=dirty=>{if(disposed)return;q('save-state').textContent=dirty?'Cambios pendientes':'Guardado'+(data.saved_at?' · '+data.saved_at:'');q('save-state').dataset.state=dirty?'dirty':'saved';if(dirty)autosave()};
 component.onPaint=()=>{q('undo').disabled=!data.can_undo&&!component.canvasApi?.hasPending();q('redo').disabled=!data.can_redo};
 const disposeCanvas=mountCanvas({...component,setTriggerValue:(name,message)=>{
  if(name==='applied')send(({apply:'canvas',generate:'export'}[message.action]||message.action),{entries:message.entries,ids:message.selection});
 },get onPending(){return component.onPending},get onSelection(){return component.onSelection},get onPaint(){return component.onPaint},
 set canvasApi(value){component.canvasApi=value}});
 const stage=root.querySelector('.stage'),viewport=root.querySelector('.viewport');
 q('zoom').value=ui.zoom;q('guides').checked=ui.guides;q('snap').checked=ui.snap;
 const oldZoom=q('zoom').onchange;q('zoom').onchange=()=>{ui.zoom=q('zoom').value;oldZoom();saveUi()};
 const oldGuides=q('guides').onchange;q('guides').onchange=()=>{ui.guides=q('guides').checked;oldGuides();saveUi()};q('snap').onchange=()=>{ui.snap=q('snap').checked;saveUi()};
 // Existing controller creates legacy convenience buttons; workspace has one compact action per capability.
 [...q('addtext').parentElement.children].filter(e=>e.tagName==='BUTTON'&&!e.id).forEach(e=>e.remove());
 q('addtext').onclick=()=>send('add_element',{kind:'text'});q('addshape').onclick=()=>send('add_element',{kind:'shape'});
 q('group').onclick=()=>send('group');q('ungroup').onclick=()=>send('ungroup');q('duplicate-selection').onclick=()=>send('duplicate');
 const localUndo=q('undo').onclick,localRedo=q('redo').onclick;
 q('undo').onclick=()=>{if(component.canvasApi.hasPending()){localUndo();autosave()}else send('undo')};
 q('redo').onclick=()=>{if(data.can_redo)send('redo');else localRedo()};
 const finish=stage.onpointerup;stage.onpointerup=e=>{finish(e);if(component.canvasApi.hasPending())send('canvas')};
 root.addEventListener('change',autosave);
 q('project-name').value=data.project.name||'Proyecto sin título';q('project-name').onchange=()=>send('rename',{name:q('project-name').value});
 q('scene-label').textContent=data.scene_data.name;
 const profile=data.project.studio.output_profile;
 q('format').textContent=data.profiles[profile.id]||'Personalizado';q('resolution').textContent=data.frame_width+' × '+data.frame_height+' · 30 FPS';
 q('scene-remove').disabled=data.rows.length===1;
 for(const [id,action] of Object.entries({'scene-add':'scene_add','scene-duplicate':'scene_duplicate','scene-remove':'scene_delete'}))q(id).onclick=()=>send(action);
 function togglePanel(side){
  if(innerWidth<=1000){ui[side]=!ui[side];ui[side==='left'?'right':'left']=false}
  else ui[side]=!ui[side];applyPanels();saveUi();
 }
 function applyPanels(){
  shell.classList.toggle('left-open',innerWidth<=1000&&ui.left);shell.classList.toggle('right-open',innerWidth<=1000&&ui.right);
  shell.classList.toggle('left-collapsed',innerWidth>1000&&ui.left);shell.classList.toggle('right-collapsed',innerWidth>1000&&ui.right);
  shell.classList.toggle('timeline-collapsed',!!ui.collapsed);
  q('toggle-left').setAttribute('aria-expanded',String(innerWidth>1000?!ui.left:ui.left));q('toggle-right').setAttribute('aria-expanded',String(innerWidth>1000?!ui.right:ui.right));
 }
 q('toggle-left').onclick=()=>togglePanel('left');q('toggle-right').onclick=()=>togglePanel('right');
 q('close-left').onclick=()=>{ui.left=false;applyPanels();saveUi()};q('close-right').onclick=()=>{ui.right=false;applyPanels();saveUi()};
 q('timeline-collapse').onclick=()=>{ui.collapsed=!ui.collapsed;applyPanels();saveUi();q('timeline-collapse').setAttribute('aria-label',ui.collapsed?'Expandir timeline':'Colapsar timeline')};
 window.addEventListener('resize',applyPanels);applyPanels();
 const el=(tag,text='',className='')=>{const e=document.createElement(tag);if(text)e.textContent=text;if(className)e.className=className;return e};
 const button=(text,fn,container,icon)=>{const b=el('button',text);b.type='button';b.onclick=fn;if(icon)b.prepend(svg(icon));container?.append(b);return b};
 function field(container,label,value,{type='text',options=null,min,max,step,onchange,id}={}){
  const wrap=el('label',label),input=el(options?'select':type==='textarea'?'textarea':'input');
  if(options){for(const [key,text] of Array.isArray(options)?options.map(v=>[v,v]):Object.entries(options)){const opt=el('option',text);opt.value=key;input.append(opt)}input.value=value??''}
  else if(type==='textarea'){input.rows=3;input.value=value??''}
  else{input.type=type;if(type==='checkbox'){input.checked=!!value;wrap.className='checkbox-label'}else input.value=value??''}
  if(min!==undefined)input.min=min;if(max!==undefined)input.max=max;if(step!==undefined)input.step=step;
  if(id)input.id=id;input.onchange=()=>onchange?.(type==='checkbox'?input.checked:type==='number'||type==='range'?Number(input.value):input.value);
  wrap.append(input);container.append(wrap);return input;
 }
 function section(container,title,open=true){const details=el('details');details.open=open;details.append(el('summary',title));container.append(details);return details}
 function card(container,title,subtitle,fn,{thumbnail,icon='shape',selected=false}={}){
  const b=button('',fn,container);b.className='resource-card';b.setAttribute('aria-current',String(selected));
  if(thumbnail){const image=el('img');image.src=thumbnail;image.alt='';b.append(image)}else b.append(svg(icon));
  const text=el('span',title);if(subtitle)text.append(el('small',subtitle));b.append(text);return b;
 }
 const dialog=q('workspace-dialog');let returnFocus=null;
 function openDialog(title,build){returnFocus=root.activeElement;q('dialog-title').textContent=title;q('dialog-body').replaceChildren();build(q('dialog-body'));dialog.showModal()}
 q('dialog-close').onclick=()=>dialog.close();dialog.addEventListener('close',()=>returnFocus?.focus());
 function download(content,name,type='application/json'){const url=URL.createObjectURL(new Blob([content],{type}));const a=el('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
 function formatDialog(){openDialog('Formato del proyecto',body=>{
  const choice=field(body,'Perfil de salida',profile.id,{options:{...data.profiles,custom:'Personalizado'}});
  const w=field(body,'Ancho · px',data.frame_width,{type:'number',min:160,max:3840,step:2});const h=field(body,'Alto · px',data.frame_height,{type:'number',min:160,max:3840,step:2});
  const custom=()=>{w.disabled=h.disabled=choice.value!=='custom'};choice.onchange=custom;custom();
  body.append(el('p','Adaptar conserva los elementos y reorganiza las regiones de templates. 30 FPS.','panel-note'));
  button('Adaptar escenas',()=>send('profile',{profile:choice.value==='custom'?{id:'custom',width:Number(w.value),height:Number(h.value)}:{id:choice.value}}),body);
 })}
 q('format').onclick=formatDialog;
 function projectDialog(){openDialog('Proyecto y espacios de trabajo',body=>{
  button('Nuevo proyecto · escena vacía',()=>send('project_new'),body,'plus');
  button('Descargar proyecto JSON',()=>download(JSON.stringify(data.project,null,2),'ecuador-vivo-proyecto.json'),body,'folder');
  button('Abrir proyecto JSON',()=>{dialog.close();send('import_project')},body,'folder');
  for(const [phase,label] of Object.entries({Inicio:'Volver al inicio',SIG:'Abrir SIG',Datos:'1 · Datos',Maqueta:'2 · Maqueta',Montaje:'3 · Montaje',Exportar:'4 · Exportar · montaje anterior'}))button(label,()=>send('navigate',{phase}),body);
  const recover=field(body,'Borradores guardados','',{options:{'':'Selecciona una copia',...Object.fromEntries(data.recovery.map(r=>[r.path,r.name]))}});
  button('Abrir copia recuperada',()=>{if(recover.value)send('recover',{path:recover.value})},body);
  body.append(el('p','Abrir una copia conserva el archivo original y empieza otro historial.','panel-note'));
 })}
 q('project-menu').onclick=projectDialog;
 q('help').onclick=()=>openDialog('Atajos y ayudas',body=>{
  for(const line of ['Mayús + clic: selección múltiple · Ctrl+A: todos','Flechas: mover 1 px · Mayús + flechas: 10 px','Arrastre de esquina: resize · Alt + arrastre: pan','Supr: eliminar · Escape: cancelar gesto o seleccionar escena','Ctrl+Z / Ctrl+Mayús+Z: historial · Ctrl+D: duplicar','Ctrl+C / Ctrl+V: copiar y pegar · Ctrl+G: agrupar','Espacio: reproducir/pausar · Guías y selección no se exportan'])body.append(el('p',line));
 });
 const tabLabels={scenes:'Escenas',layers:'Capas',media:'Multimedia',data:'Datos científicos',visuals:'Visualizaciones',templates:'Templates',project:'Recursos del proyecto'};
 const rememberDetails=()=>{ui.detailsFor=state().ids.join('|');ui.details=Object.fromEntries([...root.querySelector('.inspector').querySelectorAll('details')].map(d=>[d.querySelector('summary')?.textContent,d.open]));ui.inspectorScroll=root.querySelector('.inspector-fields').scrollTop};
 const restoreDetails=key=>{if(ui.detailsFor===key){root.querySelector('.inspector').querySelectorAll('details').forEach(d=>{const name=d.querySelector('summary')?.textContent;if(ui.details?.[name]!==undefined)d.open=ui.details[name]});root.querySelector('.inspector-fields').scrollTop=ui.inspectorScroll||0}if(ui.draftVersion===data.version&&ui.draftFor===key){q('context-fields').querySelectorAll('input,select,textarea').forEach(input=>{const name=input.closest('label')?.firstChild?.textContent;if(ui.draftControls?.[name]!==undefined){if(input.type==='checkbox')input.checked=ui.draftControls[name];else input.value=ui.draftControls[name]}})}};
 function library(tab){
  ui.tab=tab;saveUi();q('resource-title').textContent=tabLabels[tab];q('layer-content').hidden=tab!=='layers';q('library-content').hidden=tab==='layers';
  root.querySelectorAll('[data-tab]').forEach(b=>b.setAttribute('aria-current',String(b.dataset.tab===tab)));
  const body=q('library-content');body.replaceChildren();
  if(tab==='scenes'){
   data.rows.forEach((r,i)=>card(body,(i+1)+' · '+r.name,r.seconds.toFixed(2)+' s',()=>send('select',{id:r.id}),{thumbnail:r.thumbnail,selected:r.id===data.scene}));
   button('Añadir escena',()=>send('scene_add'),body,'plus');
   button('Cambiar template / regenerar escena',()=>send('regenerate'),body,'settings');
   if(data.project.project_meta?.scientific_revision)button('Regenerar estructura científica',()=>send('regenerate_structure'),body,'settings');
  }else if(tab==='media'){
   button('Importar multimedia',()=>send('upload'),body,'plus');
   if(data.project.project_meta?.scientific_revision)button('Preparar mapa temporal',()=>send('temporal_map'),body,'video');
   if(data.project.project_meta?.scientific_revision)button('Preparar capas cartográficas',()=>send('temporal_layers'),body,'image');
   const asMap=field(body,'Insertar imágenes como mapa',false,{type:'checkbox'});
   const assets=Object.entries(data.project.studio.media);
   if(!assets.length)body.append(el('p','Importa imágenes y videos locales para añadirlos al canvas.','empty-state'));
   assets.forEach(([id,a])=>{
    if(a.kind==='temporal_map'){
     const resource=card(body,a.name,'Mapa de capas · '+a.variable+' · '+a.period.join(' — ')+' · '+a.units+' · revisar e insertar',()=>send('review_map_layers',{asset_id:id}),{icon:'image'});
     resource.setAttribute('aria-label','Revisar e insertar capas: '+a.name);
     return;
    }
    const m=a.temporal_map;
    const subtitle=m?'Mapa temporal · '+m.source+' · '+m.variable+' · '+m.intervals[0].date+' — '+m.intervals.at(-1).date+' · '+m.duration.toFixed(3)+' s · '+m.resolution.join(' × ')+' · listo · generado '+m.generated_at:a.kind+' · '+(a.size||[]).join(' × ');
    card(body,a.name,subtitle,()=>send('add_element',{kind:a.kind==='video'?'video':asMap.checked?'map':'image',asset_id:id,name:a.name}),{thumbnail:data.map_thumbnails?.[id],icon:a.kind==='video'?'video':'image'});
   });
  }else if(tab==='data'){
   button('Vincular revisión cargada',()=>send('attach'),body,'chart').disabled=!data.can_attach;
   const results=Object.entries(data.project.studio.calculations);
   if(!results.length)body.append(el('p','Carga resultados en Maqueta → Visualizaciones y vincula la revisión aquí. El diseño no recalcula ciencia.','empty-state'));
   results.forEach(([id,r])=>{const s=section(body,r.variable||id);s.append(el('p',id+' · '+(r.units||'Unidad no declarada')));s.append(el('p','Fuente: '+JSON.stringify(r.provenance||{}),'source-info'));});
  }else if(tab==='visuals'){
   const results=Object.entries(data.project.studio.calculations);
   if(!results.length){body.append(el('p','Vincula un CalculationResult para crear métricas, series, rankings y comparaciones.','empty-state'));button('Ver datos científicos',()=>library('data'),body);return}
   const form=el('div','','resource-section');body.append(form);
   const result=field(form,'Resultado',results[0][0],{options:Object.fromEntries(results.map(([id,r])=>[id,(r.variable||id)+' · '+r.units]))});
   const kind=field(form,'Representación','metric',{options:['metric']});
   const update=()=>{const r=data.project.studio.calculations[result.value];kind.replaceChildren();('rows'in r?['horizontal_bar','vertical_bar','dot','lollipop','line','ranking','comparison']:['metric']).forEach(k=>{const opt=el('option',k);opt.value=k;kind.append(opt)})};result.onchange=update;update();
   const palette=field(form,'Paleta','Earth',{options:Object.keys(data.palettes)});
   button('Añadir visualización',()=>send('add_element',{kind:kind.value==='metric'?'metric':'chart',result_id:result.value,visualization:kind.value,palette:palette.value}),form,'plus');
  }else if(tab==='templates'){
   const theme=field(body,'Tema',data.project.studio.theme||data.themes[0],{options:data.themes});
   const typography=field(body,'Tipografía',data.typography[0],{options:data.typography});
   for(const [id,name] of Object.entries(data.templates))card(body,name,'Escena editable',()=>{
    if(data.template_bindings[id]||id==='image_caption'){
     openDialog(name,content=>{
      let rid=null,asset=null;
      if(data.template_bindings[id])rid=field(content,'Resultado vinculado','',{options:{'':'Sin vincular · placeholder editable',...Object.fromEntries((data.template_results[id]||[]).map(r=>[r,r]))}});
      if(id==='image_caption')asset=field(content,'Imagen','',{options:{'':'Sin imagen · placeholder editable',...Object.fromEntries(Object.entries(data.project.studio.media).filter(([,r])=>r.kind==='image').map(([r,a])=>[r,a.name]))}});
      button('Añadir template',()=>{const bindings={};if(rid?.value){const [key,field]=data.template_bindings[id];bindings[key]={result_id:rid.value,field}}send('template',{template:id,theme:theme.value,typography:typography.value,bindings,asset_id:asset?.value||null})},content);
     });
    }else send('template',{template:id,theme:theme.value,typography:typography.value});
   },{icon:id==='image_caption'?'image':'chart'});
  }else if(tab==='project'){
   button('Guardar proyecto JSON',()=>download(JSON.stringify(data.project,null,2),'ecuador-vivo-proyecto.json'),body,'folder');button('Borradores y navegación',projectDialog,body,'folder');
   data.project.studio.scenes.filter(s=>!data.project.studio.timeline.includes(s.id)&&s.renderer!=='legacy').forEach(s=>card(body,s.name,'Escena recuperable',()=>send('scene_recover',{id:s.id}),{icon:'copy'}));
   body.append(el('p',Object.keys(data.project.studio.media).length+' recursos · '+Object.keys(data.project.studio.calculations).length+' resultados · '+data.project.studio.scenes.length+' escenas conservadas.','panel-note'));
  }
 }
 root.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>library(b.dataset.tab));library(ui.tab in tabLabels?ui.tab:'layers');
 function decorateLayers(){
  const kinds={text:'Texto',source:'Fuente',shape:'Forma',map:'Mapa',image:'Imagen',video:'Video',metric:'Métrica',chart:'Visualización',ranking:'Ranking',logo:'Logo',background:'Fondo'};
  const defaults={title:'Título',body:'Contenido',source:'Fuentes y créditos',metric:'Métrica',ranking:'Ranking','map.placeholder':'Mapa',context:'Contexto'};
  const readable=e=>e?(e.name===e.id&&defaults[e.id]?defaults[e.id]:e.name||kinds[e.type]||e.id):'';
  root.querySelectorAll('.group-heading').forEach(e=>e.remove());let previousGroup=null;
  q('layers').querySelectorAll('.layer-row').forEach(row=>{
   const element=data.scene_data.elements.find(e=>e.id===row.dataset.layer);
   if(element?.group_id){row.dataset.group=element.group_id;if(previousGroup!==element.group_id){const heading=el('div','Grupo · '+data.scene_data.elements.filter(e=>e.group_id===element.group_id&&!e.editor_deleted).length+' elementos','group-heading');heading.prepend(svg('group'));row.before(heading)}previousGroup=element.group_id}else previousGroup=null;
   const buttons=row.querySelectorAll('button');if(buttons.length<3)return;
   buttons[0].replaceChildren(svg({source:'text',metric:'chart',ranking:'chart',map:'image',logo:'image'}[element?.type]||element?.type),document.createTextNode(readable(element)));buttons[0].title=readable(element);
   buttons[1].replaceChildren(svg(buttons[1].getAttribute('aria-pressed')==='true'?'hidden':'eye'));
   buttons[2].replaceChildren(svg(buttons[2].getAttribute('aria-pressed')==='true'?'lock':'unlock'));
  });
  [...q('object').options].forEach(option=>{const e=data.scene_data.elements.find(e=>e.id===option.value);if(e)option.textContent=readable(e)+' · '+(kinds[e.type]||'Elemento')});
 }
 // Observe structural updates only; our decoration must not recursively observe its own mutations.
 const originalLayers=q('layers');let decorating=false;
 const monitored=new MutationObserver(()=>{if(decorating)return;decorating=true;monitored.disconnect();decorateLayers();monitored.observe(originalLayers,{childList:true});decorating=false});
 decorateLayers();monitored.observe(originalLayers,{childList:true});
 function inspector(ids,selected){
  ui.ids=ids;ui.selected=selected;saveUi();
  q('group').disabled=ids.length<2;q('ungroup').disabled=!ids.some(id=>data.scene_data.elements.find(e=>e.id===id)?.group_id);
  const elements=data.scene_data.elements.filter(e=>ids.includes(e.id)),element=elements.find(e=>e.id===selected)||elements[0];
  const key=ids.join('|');if(key===contextKey)return;contextKey=key;
  const body=q('context-fields');body.replaceChildren();q('selection-common').hidden=!element;
  q('text-properties').hidden=!element||ids.length!==1||!['text','source'].includes(element.type);
  q('recovery-fields').hidden=!element;q('inspector-title').textContent=!element?'Escena':ids.length>1?'Grupo · '+ids.length+' elementos':({text:'Texto',source:'Fuente',video:'Video',image:'Imagen',map:'Mapa',chart:'Visualización',metric:'Métrica',shape:'Forma'}[element.type]||'Elemento');
  if(!element){
   q('hint').textContent=data.scene_data.elements.length?'Selecciona un elemento en las capas o en el canvas.':'Escena vacía. Añade texto, formas, multimedia o un template.';
   const s=section(body,'Escena');field(s,'Nombre',data.scene_data.name,{id:'scene-name',onchange:name=>send('scene_properties',{name})});
   field(s,'Duración · segundos',data.scene_data.duration,{type:'number',min:1/30,max:7200,step:1/30,id:'scene-duration',onchange:duration=>send('scene_properties',{duration})});
   field(s,'Fondo',data.scene_data.background,{type:'color',id:'scene-background',onchange:background=>send('scene_properties',{background})});
   button('Formato del proyecto',formatDialog,s);button('Elegir template',()=>library('templates'),s);
   const design=section(body,'Identidad visual',false);
   field(design,'Tema',data.project.studio.theme||data.themes[0],{options:data.themes,onchange:theme=>send('design',{theme})});
   field(design,'Tipografía',data.typography[0],{options:data.typography,onchange:typography=>send('design',{typography})});
   for(const [role,label] of Object.entries(data.font_roles))field(design,'Familia · '+label,'',{options:{'':'Conservar actual',...Object.fromEntries(data.font_families.map(f=>[f,f]))},onchange:family=>{if(family)send('design',{font_roles:{[role]:family}})}});
   restoreDetails(key);return;
  }
  const style=element.style||{},visual=['metric','ranking','chart'].includes(element.type),target=visual?style.visualization?.style||{}:style;
  const properties=style=>send('properties',{style});
  if(ids.length===1){
   if(['text','source','metric','ranking','chart'].includes(element.type)){
    const typography=section(body,'Tipografía',true);
    field(typography,'Familia',target.font_family||'Barlow Condensed',{options:data.font_families,id:'font-family',onchange:font_family=>properties(visual?{visualization:{...style.visualization,style:{...target,font_family}}}:{font_family})});
    field(typography,'Rol',element.typography_role||(['source'].includes(element.type)?'source':visual?'data':'body'),{options:data.font_roles,onchange:typography_role=>send('properties',{typography_role})});
    if(!visual){field(typography,'Destacado',!!style.bold,{type:'checkbox',onchange:bold=>properties({bold})});field(typography,'Alineación',style.alignment||'left',{options:{left:'Izquierda',center:'Centro',right:'Derecha'},onchange:alignment=>properties({alignment})})}
   }
   if(element.temporal_binding){
    const linked=section(body,'Referencia científica');
    linked.append(el('p',element.temporal_binding.instance_id+' · '+element.temporal_binding.channel,'source-info'));
   }
   if(['image','logo','video','map'].includes(element.type)&&!element.temporal_binding){
    const media=section(body,'Recurso y encuadre');
    const compatible=Object.entries(data.project.studio.media).filter(([,a])=>(a.kind==='video')===(element.type==='video'));
    field(media,'Recurso',style.asset_id,{options:Object.fromEntries(compatible.map(([id,a])=>[id,a.name])),onchange:asset_id=>properties({asset_id})});
    const temporal=data.project.studio.media[style.asset_id]?.temporal_map;
    if(element.type!=='map'&&!temporal)field(media,'Encuadre',style.fit||'contain',{options:{contain:'Completo · contain',cover:'Rellenar · cover'},onchange:fit=>properties({fit})});
    if(temporal){media.append(el('p','Mapa prerenderizado · encuadre completo · revisión '+temporal.scientific_revision.slice(0,16),'panel-note'));button('Actualizar mapa desde datos',()=>send('temporal_map'),media,'video')}
    if(element.type==='video'){
     const audio=section(body,'Video y audio'),a=data.project.studio.media[style.asset_id];
     field(audio,'Trim in · segundos',style.trim_in||0,{type:'number',min:0,max:a?.duration||7200,step:1/30,id:'trim-in',onchange:trim_in=>properties({trim_in})});
     field(audio,'Trim out · segundos',style.trim_out??a?.duration,{type:'number',min:0,max:a?.duration||7200,step:1/30,id:'trim-out',onchange:trim_out=>properties({trim_out})});
     field(audio,'Repetir clip',!!style.loop,{type:'checkbox',onchange:loop=>properties({loop})});field(audio,'Silenciar',style.mute??true,{type:'checkbox',id:'clip-mute',onchange:mute=>properties({mute})});
     field(audio,'Volumen · 1 = original',style.volume??1,{type:'number',min:0,max:2,step:.05,id:'clip-volume',onchange:volume=>properties({volume})});
     audio.append(el('p','Mezcla por clip con limitador de picos. Escucha el resultado con Reproducir.','panel-note'));
    }
   }
   if(['shape','background'].includes(element.type)){
    const appearance=section(body,'Forma');field(appearance,'Relleno',style.fill||'#13bfd1',{type:'color',onchange:fill=>properties({fill})});
    field(appearance,'Forma',style.shape||'rectangle',{options:['rectangle','rounded_rectangle','circle','line','divider'],onchange:shape=>properties({shape})});
   }
   if(visual){
    const v=section(body,'Visualización');const binding=element.data_binding,r=data.project.studio.calculations[binding?.result_id]||{};
    field(v,'Binding',binding?.result_id,{options:Object.fromEntries(Object.entries(data.project.studio.calculations).filter(([,r])=>('rows'in r)===('rows'in data.project.studio.calculations[binding?.result_id])).map(([id,r])=>[id,(r.variable||id)+' · '+r.units])),onchange:result_id=>send('properties',{data_binding:{result_id,field:binding.field}})});
    const updateVisual=(key,value)=>properties({visualization:{...style.visualization,style:{...target,[key]:value}}});
    field(v,'Tipo',style.visualization?.kind||'metric',{options:'rows'in r?['horizontal_bar','vertical_bar','dot','lollipop','line','ranking','comparison']:['metric'],onchange:kind=>properties({visualization:{...style.visualization,kind}})});
    for(const [key,label,fallback] of [['color','Tinta','#13bfd1'],['background','Fondo','#04151e'],['text','Texto','#f0f5f8']])field(v,label,target[key]||fallback,{type:'color',onchange:value=>updateVisual(key,value)});
    const scale=section(body,'Escala de datos',false),current=target.color_scale;
    const palette=field(scale,'Paleta',current?.palette||'',{options:{'':'Tinta uniforme',...Object.fromEntries(Object.entries(data.palettes).map(([p,s])=>[p,p+' · '+s.type]))}});
    const domainMin=field(scale,'Dominio mínimo',current?.domain?.[0]??0,{type:'number',step:'any'}),domainMax=field(scale,'Dominio máximo',current?.domain?.[1]??100,{type:'number',step:'any'}),center=field(scale,'Centro explícito',current?.center??0,{type:'number',step:'any'});
    const categories=field(scale,'Categorías · una por línea',(current?.categories||[]).join('\n'),{type:'textarea'}),colors=field(scale,'Colores hex · uno por línea',(current?.colors||[]).join('\n'),{type:'textarea'});
    button('Aplicar escala',()=>{const next={...target};if(!palette.value)delete next.color_scale;else{const p=data.palettes[palette.value];next.color_scale={palette:palette.value,...(p.type==='categorical'?{categories:categories.value.split('\n').filter(Boolean)}:{domain:[Number(domainMin.value),Number(domainMax.value)]}),...(p.type==='diverging'?{center:Number(center.value)}:{}),...(colors.value.trim()?{colors:colors.value.split('\n').filter(Boolean)}:{})}}properties({visualization:{...style.visualization,style:next}})},scale);
    const provenance=section(body,'Unidades y fuentes',false);provenance.append(el('p',(r.variable||'')+' · '+(r.units||'Unidad no declarada'),'source-info'));provenance.append(el('p',JSON.stringify(r.provenance||{},null,2),'source-info'));
   }
  }
  const appearance=section(body,'Composición',ids.length>1);field(appearance,'Opacidad',style.opacity??1,{type:'number',min:0,max:1,step:.05,onchange:opacity=>properties({opacity})});
  if(ids.length===1&&['image','video','logo','map','shape','background'].includes(element.type))field(appearance,'Rotación · grados',element.transform.rotation||0,{type:'number',min:-360,max:360,step:1,onchange:rotation=>send('properties',{rotation})});
  const animation=section(body,'Animación',false),a=element.animation||{},modes={none:'Ninguna',fade:'Fundido',slide:'Deslizar',scale:'Escala',wipe:'Barrido'};
  const incoming=field(animation,'Entrada',a.in||'none',{options:modes}),outgoing=field(animation,'Salida',a.out||'none',{options:modes});
  const duration=field(animation,'Duración · segundos',a.duration||0,{type:'number',min:0,max:300,step:.1}),delay=field(animation,'Retraso · segundos',a.delay||0,{type:'number',min:0,max:300,step:.1});
  for(const input of [incoming,outgoing,duration,delay])input.onchange=()=>send('properties',{animation:{in:incoming.value,out:outgoing.value,duration:Number(duration.value),delay:Number(delay.value)}});
  if(elements.some(e=>e.locked)){body.querySelectorAll('input,select,textarea,button').forEach(e=>e.disabled=true)}
  restoreDetails(key);
 }
 component.onSelection=inspector;
 const desiredIds=[...ui.ids],desiredSelected=ui.selected;
 component.canvasApi.choose(desiredSelected&&data.scene_data.elements.some(e=>e.id===desiredSelected)?desiredSelected:null);
 if(desiredIds.length>1)for(const id of desiredIds){if(id!==desiredSelected&&!state().ids.includes(id))component.canvasApi.choose(id,true)}
 component.canvasApi.resizeView();
 const total=data.rows.at(-1).end_frame;q('total').textContent=data.rows.length+' escenas · '+(total/30).toFixed(2)+' s';q('playhead').max=total-1;q('playhead').value=data.frame;
 function timePosition(frame){const row=data.rows.find(r=>r.start_frame<=frame&&frame<r.end_frame)||data.rows.at(-1);const card=[...q('scenes').children].find(b=>b.dataset.scene===row.id);return card?card.offsetLeft-q('scenes').offsetLeft+(frame-row.start_frame)/row.frames*card.offsetWidth:0}
 let updateCalendar=()=>{};
 function clock(frame){frame=Math.max(0,Math.min(total-1,frame));q('time').textContent=(frame/30).toFixed(2)+' / '+(total/30).toFixed(2)+' s';q('timeline-playhead').style.left=(q('scenes').offsetLeft+timePosition(frame))+'px';[...q('scenes').children].forEach(b=>b.dataset.playing=String(ui.mode==='movie'&&data.rows.some(r=>r.id===b.dataset.scene&&r.start_frame<=frame&&frame<r.end_frame)));updateCalendar(frame)}clock(data.frame);
 let dragged=null;
 function timeline(){
  q('scenes').replaceChildren();q('time-ruler').replaceChildren();const zoom=Number(q('time-zoom').value)/100,width=Math.max(1,q('scenes').clientWidth);
  data.rows.forEach((r,i)=>{
   const b=button('',()=>send('select',{id:r.id}),q('scenes'));b.draggable=true;b.dataset.scene=r.id;b.setAttribute('aria-current',String(r.id===data.scene));b.setAttribute('aria-label',(i+1)+' · '+r.name+' · '+r.seconds.toFixed(2)+' segundos');
   b.style.width=Math.max(100,(width-(data.rows.length-1)*4)*r.frames/total*zoom)+'px';b.title=r.name+' · '+r.seconds.toFixed(2)+' s';
   const image=el('img');image.src=r.thumbnail;image.alt='';b.append(image,el('span',(i+1)+' · '+r.name),el('small',r.seconds.toFixed(2)+' s'));
   b.ondragstart=e=>{dragged=r.id;e.dataTransfer.setData('text/plain',r.id)};b.ondragover=e=>e.preventDefault();
   const reorder=index=>{const order=data.rows.map(r=>r.id);order.splice(order.indexOf(r.id),1);order.splice(index,0,r.id);send('reorder',{order})};
   b.ondrop=e=>{e.preventDefault();if(dragged&&dragged!==r.id){const order=data.rows.map(r=>r.id);order.splice(order.indexOf(dragged),1);order.splice(i,0,dragged);send('reorder',{order})}};
   b.onkeydown=e=>{if(e.shiftKey&&['ArrowLeft','ArrowRight'].includes(e.key)){e.preventDefault();const to=i+(e.key==='ArrowLeft'?-1:1);if(to>=0&&to<data.rows.length)reorder(to)}};
  });
  // The ruler follows actual card geometry, including zoom and minimum card
  // widths. Short scenes stay legible without misrepresenting the playhead.
  q('time-ruler').style.width=Math.max(width,timePosition(total))+'px';
  for(let i=0;i<=4;i++){const tick=el('span',(total/30*i/4).toFixed(1)+' s');tick.style.left=timePosition(total*i/4)+'px';tick.style.transform=i===0?'none':i===4?'translateX(-100%)':'translateX(-50%)';q('time-ruler').append(tick)};
  clock(Number(q('playhead').value));
 }
 q('time-zoom').value=ui.timeZoom;q('time-zoom').oninput=()=>{ui.timeZoom=Number(q('time-zoom').value);timeline();saveUi()};timeline();
 let timelineFrame=null;const timelineObserver=new ResizeObserver(()=>{if(timelineFrame!==null)cancelAnimationFrame(timelineFrame);timelineFrame=requestAnimationFrame(()=>{timelineFrame=null;timeline()})});timelineObserver.observe(q('scenes'));
 q('tracks').replaceChildren();const videoElements=data.scene_data.elements.filter(e=>e.type==='video'&&e.visible&&!e.editor_deleted);
 if(videoElements.length)videoElements.forEach(e=>{const chip=el('span',e.name||'Video','track-chip');chip.prepend(svg(e.style.mute??true?'mute':'audio'));chip.title='Video real · trim '+(e.style.trim_in||0)+' s · volumen '+(e.style.volume??1)+' · '+((e.style.mute??true)?'silenciado':'audio activo');q('tracks').append(chip)});
 else q('tracks').append(el('span',data.scene_data.elements.filter(e=>e.visible&&!e.editor_deleted).length+' elementos de escena · duración común'));
 const observation=el('span','','track-chip');observation.id='scientific-date';q('tracks').append(observation);
 function calendar(frame){
  const dates=(data.scientific_calendar||[]).flatMap(c=>c.intervals.filter(i=>i.start_frame<=frame&&frame<i.end_frame).map(i=>i.date));
  observation.textContent=dates.length?'Fecha científica · '+[...new Set(dates)].join(' / '):'';observation.hidden=!dates.length;
 }
 updateCalendar=calendar;calendar(data.frame);
 q('playhead').oninput=()=>clock(Number(q('playhead').value));q('playhead').onchange=()=>{
  const frame=Number(q('playhead').value);
  if(movieReady&&ui.mode==='movie'){q('movie').currentTime=frame/30;clock(frame)}else{ui.mode='frame';saveUi();send('seek',{frame})}
 };
 function editMode(){ui.mode='edit';saveUi();q('movie').pause();root.querySelector('.preview-surface').hidden=true;viewport.hidden=false;q('canvas-mode').textContent='EDICIÓN';q('play').replaceChildren(svg('play'));q('play').setAttribute('aria-label','Reproducir');component.canvasApi.resizeView()}
 q('back-edit').onclick=editMode;
 const movie=q('movie');q('frame-preview').src=data.preview;
 function movieMode(autoplay=false){
  ui.mode='movie';saveUi();root.querySelector('.preview-surface').hidden=false;viewport.hidden=true;movie.hidden=false;q('frame-preview').hidden=true;q('canvas-mode').textContent='PREVIEW · MISMO MP4 DE EXPORTACIÓN';
  if(autoplay)movie.play().catch(()=>status('Preview listo. Pulsa reproducir en el video para escuchar audio.'));
 }
 movie.ontimeupdate=()=>{ui.movieTime=movie.currentTime;const frame=Math.min(total-1,Math.floor(movie.currentTime*30+1e-7));q('playhead').value=frame;clock(frame)};
 movie.onplay=()=>{q('play').replaceChildren(svg('pause'));q('play').setAttribute('aria-label','Pausar')};movie.onpause=()=>{q('play').replaceChildren(svg('play'));q('play').setAttribute('aria-label','Reproducir')};
 movie.onloadedmetadata=()=>{movie.currentTime=Math.min(ui.movieTime||data.frame/30,movie.duration);if(ui.mode==='movie')movieMode(true)};
 movie.onerror=()=>{movieReady=false;status('Reproducción integrada no disponible con este arranque. Abre el preview nativo.');q('play').onclick=()=>send('native_preview');q('play').setAttribute('title','Abrir preview audiovisual nativo');};
 if(data.movie_url){movieReady=true;movie.src=data.movie_url;if(ui.mode==='movie')movieMode(false)}
 else if(ui.mode==='frame'){
  root.querySelector('.preview-surface').hidden=false;viewport.hidden=true;movie.hidden=true;q('frame-preview').hidden=false;q('canvas-mode').textContent='CUADRO · '+(data.frame/30).toFixed(2)+' s';
 }else if(ui.mode==='movie'&&!['queued','running'].includes(data.job.state)){ui.mode='edit';editMode()}
 q('play').onclick=()=>{if(movieReady){if(ui.mode!=='movie')movieMode(true);else if(movie.paused)movie.play().catch(()=>{});else movie.pause()}else{ui.mode='movie';saveUi();send('play')}};
 q('export').onclick=()=>openDialog('Exportación del proyecto',body=>{
  body.append(el('p',data.frame_width+' × '+data.frame_height+' px · 30 FPS · '+(total/30).toFixed(2)+' s · '+data.rows.length+' escenas'));
  if(data.movie_url&&!data.job_stale){const a=el('a','Descargar video MP4');a.href=data.movie_url+'?download=1';a.download='ecuador-vivo.mp4';body.append(a);button('Abrir preview nativo / descarga alternativa',()=>send('native_preview'),body);button('Ver comprobante JSON',()=>download(JSON.stringify(data.receipt,null,2),'ecuador-vivo-receipt.json'),body)}
  else button(['queued','running'].includes(data.job.state)?'Exportación en curso':'Exportar MP4',()=>{dialog.close();send('export')},body).disabled=['queued','running'].includes(data.job.state);
  button('Descargar proyecto JSON',()=>download(JSON.stringify(data.project,null,2),'ecuador-vivo-proyecto.json'),body);
  const png=el('a','Descargar cuadro PNG · '+(data.frame/30).toFixed(2)+' s');png.href=data.preview;png.download='ecuador-vivo-cuadro-'+data.frame+'.png';body.append(png);
  if(['queued','running'].includes(data.job.state))button('Cancelar exportación',()=>send('cancel'),body);
  body.append(el('p','Preview audiovisual y descarga utilizan exactamente el mismo archivo del worker.','panel-note'));
 });
 if(data.error){status('Cambio no aplicado: '+data.error);q('workspace-status').setAttribute('role','alert');shell.dataset.error='true'}else{q('workspace-status').setAttribute('role','status');delete shell.dataset.error}
 if(!data.error){if(data.notice)status(data.notice);else if(data.job_stale)status('El documento cambió. Prepara una nueva reproducción/exportación.');
 else if(['queued','running'].includes(data.job.state)){status((data.job.message||'Preparando reproducción')+' · '+Math.round((data.job.progress||0)*100)+'%')}
 else if(data.job.state==='failed')status('Exportación fallida: '+data.job.message);else if(data.job.state==='complete')status('MP4 listo · preview y exportación comparten el mismo archivo.');else status('Autosave activo · los cambios de diseño conservan datos, unidades y fuentes.');}
 if(['queued','running'].includes(data.job.state))pollTimer=setTimeout(()=>send('status'),1000);
 q('save-state').textContent=data.error?'Cambio no aplicado':'Guardado'+(data.saved_at?' · '+data.saved_at:'');q('save-state').dataset.state=data.error?'dirty':'saved';
 if(data.error)failedEntries=JSON.stringify(state().entries);
 if(component.canvasApi.hasPending()&&!data.error){component.onPending(true);autosave()}
 function keyboard(e){
  if(['INPUT','SELECT','TEXTAREA'].includes(e.composedPath()[0]?.tagName)||dialog.open)return;
  if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='g'){e.preventDefault();send(e.shiftKey?'ungroup':'group');return}
  if(e.code==='Space'){e.preventDefault();q('play').click();return}
  if(e.key==='Escape'){if(ui.left||ui.right){ui.left=ui.right=false;applyPanels();saveUi()}return}
  if(e.target!==stage&&(e.ctrlKey||e.metaKey)&&['z','y'].includes(e.key.toLowerCase())){e.preventDefault();q(e.key.toLowerCase()==='y'||e.shiftKey?'redo':'undo').click()}
 }
 root.addEventListener('keydown',keyboard);
 // Restore keyboard focus after an accepted rerun, including textarea cursor.
 if(ui.focus){const active=(ui.focus.id?q(ui.focus.id):null)||[...q('context-fields').querySelectorAll('input,select,textarea')].find(e=>e.closest('label')?.firstChild?.textContent===ui.focus.label);if(active){active.focus({preventScroll:true});if(ui.focus.start!==null&&active.setSelectionRange&&['text','textarea'].includes(active.type))active.setSelectionRange(ui.focus.start,ui.focus.end)}}
 const dispose=()=>{
  if(disposed)return;
  disposed=true;clearTimeout(saveTimer);clearTimeout(pollTimer);monitored.disconnect();timelineObserver.disconnect();if(timelineFrame!==null)cancelAnimationFrame(timelineFrame);
  const active=root.activeElement;ui.focus=active?{id:active.id||'',label:active.closest?.('label')?.firstChild?.textContent,start:active.selectionStart??null,end:active.selectionEnd??null}:null;
  ui.draftVersion=data.version;ui.draftFor=state().ids.join('|');ui.draftControls=Object.fromEntries([...q('context-fields').querySelectorAll('input,select,textarea')].map(input=>[input.closest('label')?.firstChild?.textContent,input.type==='checkbox'?input.checked:input.value]));
  rememberDetails();
  ui.movieTime=movie.currentTime||ui.movieTime;ui.ids=state().ids;ui.selected=state().selected;saveUi();
  movie.pause();movie.removeAttribute('src');movie.load();root.removeEventListener('change',autosave);root.removeEventListener('keydown',keyboard);window.removeEventListener('resize',applyPanels);disposeCanvas?.();
 };
 root.__evsDispose=dispose;
 return dispose;
}
