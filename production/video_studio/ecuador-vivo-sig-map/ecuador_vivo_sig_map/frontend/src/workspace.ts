/** Workspace chrome only. OpenLayers retains map, sources and temporal clock. */
import {workbench,icon} from './workbench';
import {layerTree} from './layer-tree';
import {toolbox} from './toolbox';
import {eventStatus} from './workbench-model';
export function workspace(adapter:any){
 const root=adapter.root as HTMLElement,q=(id:string)=>root.querySelector('#'+id) as HTMLElement;
 if(!adapter.data.workspace)return;
 const data=adapter.data,w=data.workspace;
 const windows=workbench(adapter).panels;
 const el=(tag:string,text='',cls='')=>{const node=document.createElement(tag);node.textContent=text;if(cls)node.className=cls;return node};
 const event=(action:string,extra:any={})=>{q('sig-save-label').textContent=eventStatus(action,w.saved_at);adapter.uiEvent({action,...extra})};
 const tool=(name:string)=>event('tool',{tool:name});
 q('sig-home').onclick=()=>event('navigate',{section:'Inicio'});q('sig-studio').onclick=()=>event('navigate',{section:'Studio'});
 q('sig-resources').onclick=()=>event('navigate',{section:'Recursos'});
 q('sig-open').onclick=()=>event('open');q('sig-save').onclick=()=>event('save');
 q('sig-undo').onclick=()=>event('undo');q('sig-redo').onclick=()=>event('redo');
 (q('sig-undo') as HTMLButtonElement).disabled=!w.can_undo;(q('sig-redo') as HTMLButtonElement).disabled=!w.can_redo;
 q('sig-send-top').onclick=()=>q('sig-raster-send').click();
 (q('sig-send-top') as HTMLButtonElement).disabled=!data.raster_time;
 q('sig-add-data').onclick=()=>event('import');q('sig-import').onclick=()=>event('import');
 const showTools=(kind:string)=>{(q('sig-toolbox-kind') as HTMLSelectElement).value=kind;toolbox(adapter,event);windows.open('toolbox');q('sig-toolbox-search').focus()};
 q('sig-analysis').onclick=()=>showTools('vector');q('sig-raster-tools').onclick=()=>showTools('raster');
 q('sig-prepare').onclick=()=>{adapter.pausePlayback();event('timelapse')};
 const paletteAccess=q('sig-series-palette') as HTMLButtonElement;paletteAccess.disabled=!data.raster_time;
 paletteAccess.onclick=()=>{adapter.inspectorTab='style';workspace(adapter);windows.open('properties');q('sig-palette-choice')?.focus()};
 q('sig-science').onclick=()=>tool('Ciencia');
 q('sig-export-layer').onclick=()=>tool('Exportar capa');
 (q('sig-export-layer') as HTMLButtonElement).disabled=!data.active_layer;
 toolbox(adapter,event);
 q('sig-output-settings').onclick=()=>{windows.open('properties');q('sig-format').focus()};
 q('sig-results-view').onclick=()=>{adapter.dockTab='results';workspace(adapter);windows.open('table');q('sig-dock-tabs').querySelector<HTMLButtonElement>('[data-tab=results]')?.focus()};
 q('sig-processes').onclick=()=>event('tool',{tool:'Procesos'});
 q('sig-attributes-view').onclick=()=>{if(!q('sig-table-window').hidden&&adapter.dockTab==='attributes'){windows.close('table');return};adapter.dockTab='attributes';workspace(adapter);windows.open('table')};
 const time=data.raster_time,series=(time?.layers??[]).map((id:string)=>data.layers.find((l:any)=>l.id===id)).filter(Boolean);
 q('sig-series-context').textContent=series.length?`${series.length} fechas · ${series[0].units||'unidad sin declarar'} · escala compartida`:'Exploración geográfica · datos originales';
 q('sig-project-title').textContent=w.name;q('sig-project-title').title=w.name;
 const running=(w.jobs??[]).find((job:any)=>['queued','running'].includes(job.state));
 q('sig-save-label').textContent=data.error?'Error de guardado':running?running.kind+': '+running.message:'Guardado · '+w.saved_at;
 const base=q('sig-base') as HTMLSelectElement;base.value=data.basemap??'none';base.onchange=()=>event('basemap',{value:base.value});
 const format=q('sig-format') as HTMLSelectElement;
 if(!format.options.length){Object.entries(w.profiles).forEach(([id,label])=>{const option=el('option',String(label)) as HTMLOptionElement;option.value=id;format.append(option)});if(w.profile.id==='custom'){const option=el('option','Personalizado') as HTMLOptionElement;option.value='custom';format.append(option)}}
 format.value=w.profile.id;format.onchange=()=>{if(format.value==='custom')return;event('profile',{profile:{id:format.value}})};
 q('sig-format-dimensions').textContent=w.dimensions.join(' × ')+' px · 30 fps';
 q('sig-science-note').textContent=w.scientific_note;
 layerTree(adapter,event,()=>{adapter.inspectorTab='style';workspace(adapter);windows.open('properties')});
 const inspector=q('sig-inspector-content'),tab=adapter.inspectorTab??'style',active=data.layers.find((l:any)=>l.id===data.active_layer),key=JSON.stringify([active?.id,active?.style,active?.name,tab,w.source,w.export_presentation,time?.palette]);
 q('sig-inspector-tabs').querySelectorAll('button').forEach(b=>{b.classList.toggle('is-active',b.dataset.tab===tab);b.setAttribute('aria-pressed',String(b.dataset.tab===tab));b.onclick=()=>{adapter.inspectorTab=b.dataset.tab;inspector.dataset.key='';workspace(adapter)}});
 if(inspector.dataset.key!==key){inspector.dataset.key=key;inspector.replaceChildren();
  if(!active)inspector.append(el('p','Selecciona una capa del árbol para consultar sus propiedades.','sig-muted'));
  else {
   const field=(label:string,value:any)=>{const line=el('div','','sig-data-row');line.append(el('small',label),el('span',value===null||value===undefined?'No declarado':String(value)));inspector.append(line)};
   if(tab==='style'){
    inspector.append(el('p',active.type==='raster'?'La serie conserva una escala común entre fechas. Opacidad visual; los valores nativos no cambian.':'Colores y transparencia de la referencia.','sig-muted'));
    const form=el('form'),style={...active.style};
    if(data.raster_time?.layers.includes(active.id)){
     const label=el('label','Paleta compartida'),choice=el('select') as HTMLSelectElement;choice.id='sig-palette-choice';choice.name='palette';
     Object.entries(w.palettes??{}).forEach(([id,value]:[string,any])=>{const option=el('option',value.label) as HTMLOptionElement;option.value=id;choice.append(option)});
     choice.value=time.palette??'andes';const swatch=el('div','','sig-palette-swatch');swatch.setAttribute('aria-hidden','true');
     const paint=()=>{const colors=w.palettes?.[choice.value]?.colors;if(colors)swatch.style.background=`linear-gradient(90deg,${colors.join(',')})`};choice.onchange=paint;paint();label.append(choice);form.append(label,swatch);
    }
    for(const [name,label,type] of [['fill','Relleno','color'],['stroke','Límites','color'],['opacity','Opacidad','range']]){
     if(active.type==='raster'&&name!=='opacity')continue;const wrapper=el('label',label),input=el('input') as HTMLInputElement;input.name=name;input.type=type;input.value=String(style[name]);if(type==='range'){input.min='0';input.max='1';input.step='.05'}wrapper.append(input);form.append(wrapper);
    }
    const apply=el('button','Aplicar estilo','sig-primary') as HTMLButtonElement;apply.type='submit';form.append(apply);form.onsubmit=e=>{e.preventDefault();form.querySelectorAll('input').forEach(input=>style[input.name]=input.type==='range'?Number(input.value):input.value);if(data.raster_time?.layers.includes(active.id))event('series_style',{opacity:style.opacity,palette:form.querySelector<HTMLSelectElement>('[name=palette]')?.value});else event('layer',{command:{action:'style',layer_id:active.id,style}})};inspector.append(form);
    const fit=el('button','Ajustar vista a esta capa');fit.onclick=()=>q('sig-fit-layer').click();inspector.append(fit);
    if(active.scale){const tick=(value:number)=>Number(value.toPrecision(3)).toString();field('Escala común',tick(active.scale.stops[0])+' a '+tick(active.scale.stops.at(-1))+(active.scale.saturation?'+':'')+' '+active.units);if(active.scale.saturation)field('Saturación visual','Valores superiores conservados en datos y métricas');field('Vista SIG y Studio',w.export_presentation?.resampling==='bilinear'?'Suavizado visual; resolución original conservada':'Celdas nativas')}
    if(active.type==='raster'&&data.raster_time?.layers.includes(active.id)){
     const presentation=w.export_presentation;
     for(const [name,label] of [['resampling','Suavizar el mapa'],['borders','Contorno del territorio'],['provinces','Límites provinciales']]){
      const wrapper=el('label',label),input=el('input') as HTMLInputElement;input.type='checkbox';input.checked=name==='resampling'?presentation.resampling==='bilinear':presentation[name];input.onchange=()=>event('series_presentation',{presentation:{...presentation,[name]:name==='resampling'?(input.checked?'bilinear':'nearest'):input.checked}});wrapper.prepend(input);inspector.append(wrapper);
     }
     inspector.append(el('small','Se aplica aquí y al próximo envío a Studio. Los originales y cálculos no cambian.','sig-muted'));
    }
    const order=el('div','','sig-tool-actions');for(const [label,offset] of [['Subir',1],['Bajar',-1]]){const b=el('button',String(label));b.onclick=()=>event('layer',{command:{action:'order',layer_id:active.id,offset}});order.append(b)}inspector.append(order);
    const nameLabel=el('label','Nombre de la capa'),nameInput=el('input') as HTMLInputElement;nameInput.value=active.name;nameInput.maxLength=180;nameInput.onchange=()=>event('layer',{command:{action:'rename',layer_id:active.id,name:nameInput.value}});nameLabel.append(nameInput);inspector.append(nameLabel);
   }else if(tab==='data'){
    field('Tipo',active.type==='raster'?'Ráster geográfico':'Vector geográfico');field('Fecha',w.source.date);field('Variable',w.source.variable);field('Unidad',w.source.units);field('CRS nativo',w.source.native_crs_label??w.source.native_crs);field('NoData',w.source.raster?.nodata);field('SHA-256',w.source.sha256);
    const native=w.source.native_support;
    if(native){field('Grid original',native.shape[1]+' columnas × '+native.shape[0]+' filas');field('Paso de celda',native.step?native.step.map((v:number)=>Number(v.toPrecision(5))).join(' × ')+' '+native.unit:'Consulta las unidades de los ejes nativos');field('Banda',native.band);field('Calibración',`Valor físico = valor válido × ${native.scale} + ${native.offset}`);inspector.append(el('p','Estos valores describen el dato original, no los píxeles de tu pantalla. El suavizado no mejora la resolución de la medición.','sig-muted'))}
   }else{const p=w.source.provenance??{};Object.entries(p).forEach(([label,value])=>field(label,typeof value==='object'?JSON.stringify(value):value));if(!Object.keys(p).length)inspector.append(el('p','Sin procedencia declarada.','sig-muted'))}
  }
 }
 const selected=q('sig-selected-layer');selected.replaceChildren();
 if(active){selected.append(icon(active.type==='raster'?'raster':'vector'),el('strong',active.name),el('small',active.type==='raster'?(active.date||'Sin fecha')+' · '+(active.units||'Unidad no declarada'):'Capa vectorial · geometría original'))}
 else selected.append(el('p','Selecciona una capa para ver sus propiedades.','sig-muted'));
 const dock=q('sig-dock-content'),dockTab=adapter.dockTab??'attributes';q('sig-dock-tabs').querySelectorAll('button').forEach(b=>{b.classList.toggle('is-active',b.dataset.tab===dockTab);b.setAttribute('aria-pressed',String(b.dataset.tab===dockTab));b.onclick=()=>{adapter.dockTab=b.dataset.tab;workspace(adapter)}});dock.replaceChildren();
 const rows=dockTab==='attributes'?w.attributes.rows:dockTab==='results'?w.results:w.messages;
 if(!rows.length)dock.append(el('p',dockTab==='attributes'?(active?.type==='raster'?'Consulta el valor de la celda nativa haciendo clic en el mapa.':'Selecciona una capa vectorial para ver sus atributos.'):(dockTab==='results'?'Los recursos preparados aparecerán aquí.':'Sin errores registrados.'),'sig-muted'));
 else{const table=el('table'),cols=[...new Set(rows.flatMap((r:any)=>Object.keys(r)))].slice(0,8) as string[],head=el('tr');table.setAttribute('aria-label',dockTab==='attributes'?'Atributos de la capa':'Resultados o mensajes del proyecto');cols.forEach(c=>{const th=el('th',c);th.setAttribute('scope','col');head.append(th)});table.append(head);rows.forEach((r:any,i:number)=>{const tr=el('tr');cols.forEach((c,column)=>{const value=typeof r[c]==='object'?JSON.stringify(r[c]):String(r[c]??'Sin dato'),td=el('td');if(dockTab==='attributes'&&column===0){const button=el('button',value);button.title='Seleccionar entidad en el mapa';button.onclick=()=>event('layer',{command:{action:'select',layer_id:data.active_layer,region_id:w.attributes.ids[i]}});td.append(button)}else td.textContent=value;tr.append(td)});table.append(tr)});dock.append(table)}
 workbench(adapter);
}
