/* Scientific collection UI over canonical commands; authored strings stay text. */
function scientificSearch(items,query='',category='Todos',favorites=null){
 const normalize=s=>String(s).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
 const term=normalize(query.trim());
 return items.filter(item=>(category==='Todos'||item.category===category)&&(!favorites||favorites.includes(item.id))&&normalize([item.name,item.category,item.summary].join(' ')).includes(term));
}
function renderScientificLibrary({body,tab,data,ui,save,send,el,button,field,card,svg}){
 const config={objects:['Objetos científicos','Arrastra una pieza al lienzo o pulsa su miniatura.'],templates:['Explicaciones editables','Abrir conserva tu recurso anterior en los borradores.'],saved:['Mis recursos','Abrir crea una copia editable; el archivo original se conserva.'],engines:['Herramientas especializadas','Componentes locales: instalación e integración son estados diferentes.']};
 const section=tab.replace('science_','');
 if(!config[section])return false;
 body.className='scientific-collection';
 body.append(el('p',config[section][1],'panel-note'));
 if(section==='engines'){
  for(const tool of data.resource_engines||[]){
   const row=el('div','','engine-item');row.append(el('strong',tool.name),el('span',tool.version||'No instalado'),el('small',tool.status));
   if(tool.url){const link=el('a','Documentación');link.href=tool.url;link.target='_blank';link.rel='noopener noreferrer';row.append(link)}body.append(row);
   if(tool.tool&&tool.version)button('Abrir editor',()=>send('resource_tool',{tool:tool.tool}),row);
  }
  body.append(el('p','Los dibujos y modelos de terceros mantienen sus licencias. BioRender es una referencia de interfaz, no contenido incluido.','source-info'));
  return true;
 }
 const items=section==='templates'?(data.explanation_catalog||[]).map(r=>({...r,type:'template'})):section==='saved'?(data.saved_resources||[]).map(r=>({...r,id:r.path,type:'saved',summary:'Diseño guardado'})):(data.scientific_objects||[]);
 const controls=el('div','','collection-search');body.append(controls);
 const search=field(controls,'Buscar objetos o conceptos',ui.scienceSearch||'',{id:'science-search'});
 search.placeholder='Nubes, temperatura, células…';
 const filters=el('div','','collection-filters');body.append(filters);
 const category=field(filters,'Tema',ui.scienceCategory||'Todos',{options:['Todos',...new Set(items.map(r=>r.category))]});
 if(![...category.options].some(o=>o.value===category.value))category.value='Todos';
 const only=field(filters,'Solo favoritos',!!ui.scienceFavoritesOnly,{type:'checkbox'});
 const grid=el('div','','scientific-grid');body.append(grid);const count=el('p','','panel-note');body.append(count);
 function paint(){
  ui.scienceSearch=search.value;ui.scienceCategory=category.value;ui.scienceFavoritesOnly=only.checked;save();grid.replaceChildren();
  const selected=scientificSearch(items,search.value,category.value,only.checked?(ui.scienceFavorites||[]):null);
  count.textContent=selected.length+' recursos disponibles';
  if(!selected.length){grid.append(el('p','No hay coincidencias. Cambia el tema o la búsqueda.','empty-state'));return}
  for(const item of selected){
   const tile=el('div','','scientific-tile'),action=button('',()=>insert(item),tile);action.className='scientific-object';action.title=item.summary||item.name;
   if(item.preview){const image=el('img');image.src=item.preview;image.alt='';image.loading='lazy';action.append(image)}else action.append(svg(item.icon||'shape'));
   action.append(el('strong',item.name),el('small',item.category));
   const favorite=button('',()=>{const list=ui.scienceFavorites||[];ui.scienceFavorites=list.includes(item.id)?list.filter(id=>id!==item.id):[...list,item.id];paint()},tile);
   favorite.className='scientific-favorite';favorite.textContent=(ui.scienceFavorites||[]).includes(item.id)?'★':'☆';favorite.setAttribute('aria-label','Favorito: '+item.name);favorite.setAttribute('aria-pressed',String((ui.scienceFavorites||[]).includes(item.id)));
   if(item.type==='shape'){action.draggable=true;action.addEventListener('dragstart',event=>event.dataTransfer.setData('application/x-ecuador-resource',JSON.stringify({shape:item.shape,name:item.name})));}
   grid.append(tile);
  }
 }
 function insert(item){
  if(item.type==='template')send('resource_open',{resource_id:item.id});
  else if(item.type==='saved')send('resource_open',{path:item.id});
  else if(item.type==='asset')send('resource_asset',{resource_id:item.id});
  else send('add_element',{kind:'shape',shape:item.shape,name:item.name});
 }
 search.oninput=paint;category.onchange=paint;only.onchange=paint;paint();
 return true;
}
