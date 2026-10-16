import {seriesTree} from './series-tree-model';
/** One logical temporal layer; individual observations are populated on demand. */
export function layerTree(adapter:any,event:(action:string,extra?:any)=>void,properties:()=>void){
 const data=adapter.data,root=adapter.root as HTMLElement,tree=root.querySelector<HTMLElement>('#sig-layer-tree')!;
 const search=root.querySelector<HTMLInputElement>('#sig-layer-search')!,model=seriesTree(data.layers,data.raster_time);
 const el=(tag:string,text='',cls='')=>{const node=document.createElement(tag);node.textContent=text;if(cls)node.className=cls;return node};
 const swatch=(layer:any)=>{const node=el('i','','sig-layer-swatch');node.setAttribute('aria-hidden','true');const palette=layer.scale?.palette;
  node.style.background=layer.type==='raster'&&Array.isArray(palette)&&palette.every((c:string)=>/^#[a-f0-9]{6}$/i.test(c))?`linear-gradient(135deg,${palette.join(',')})`:layer.style?.fill||'#718a96';return node};
 const row=(layer:any)=>{const node=el('div','','sig-layer-row');node.dataset.layer=layer.id;
  const check=el('input') as HTMLInputElement;check.type='checkbox';check.checked=layer.visible;check.setAttribute('aria-label','Visibilidad · '+layer.name);
  check.onchange=()=>event('layer',{command:{action:'visibility',layer_id:layer.id,visible:check.checked}});
  const choose=el('button') as HTMLButtonElement;choose.type='button';choose.append(el('span',layer.name),el('small',layer.date?layer.date+' · '+(layer.units||'Sin unidad'):layer.type==='raster'?'Ráster':'Referencia · vector'));
  choose.title=layer.name;choose.onclick=()=>{adapter.pausePlayback(false);event('layer',{command:{action:'active',layer_id:layer.id}})};choose.ondblclick=properties;
  node.append(swatch(layer),check,choose);return node;
 };
 const key=JSON.stringify([data.layers.map((l:any)=>[l.id,l.name,l.variable,l.date,l.group,l.visible,l.style,l.scale?.palette]),data.raster_time?.layers]);
 const count=root.querySelector<HTMLElement>('#sig-layer-count')!;
 count.textContent=String(model.logicalCount)+(model.count?' · '+model.count+' fechas':'');count.title='Capas lógicas; las observaciones conservan sus registros originales';
 if(tree.dataset.key!==key){
  const expanded=new Map([...tree.querySelectorAll('details')].map(d=>[d.dataset.group,d.open]));
  tree.replaceChildren();tree.dataset.key=key;
  if(model.count){
   const card=el('section','','sig-series-layer');card.setAttribute('aria-label','Capa temporal · '+model.name);
   const logical=el('div','','sig-layer-row sig-logical-series');logical.dataset.series='true';
   const check=el('input') as HTMLInputElement;check.type='checkbox';check.checked=model.visible;check.indeterminate=model.mixed;check.setAttribute('aria-label','Visibilidad de toda la serie · '+model.name);
   check.onchange=()=>{adapter.pausePlayback(false);event('series_visibility',{visible:check.checked})};
   const choose=el('button') as HTMLButtonElement;choose.type='button';choose.append(el('span',model.name),el('small','','sig-series-current'));
   choose.onclick=()=>{adapter.pausePlayback(false);const time=adapter.data.raster_time;event('layer',{command:{action:'active',layer_id:time.layers[time.index]}});root.querySelector<HTMLButtonElement>('#sig-time-view')?.click()};
   choose.ondblclick=properties;logical.append(swatch(model.current),check,choose);card.append(logical);
   const dates=el('details','','sig-series-dates') as HTMLDetailsElement;dates.dataset.group='temporal-observations';dates.open=expanded.get('temporal-observations')??false;
   dates.append(el('summary','Observaciones · '+model.count));const list=el('div','','sig-observation-list');dates.append(list);
   const populate=()=>{if(!list.childElementCount)model.observations.forEach(layer=>list.append(row(layer)))};
   dates.ontoggle=()=>{if(dates.open){populate();highlight()}};
   if(dates.open||search.value)populate();card.append(dates);tree.append(card);
   (tree as any).populateObservations=populate;
  }else (tree as any).populateObservations=undefined;
  const groups=new Map<string,any[]>();model.others.forEach(layer=>{const name=layer.group||(layer.type==='raster'?'Series y datos':'Referencias geográficas');if(!groups.has(name))groups.set(name,[]);groups.get(name)!.push(layer)});
  [...groups].sort(([a],[b])=>Number(a==='reference')-Number(b==='reference')).forEach(([name,layers])=>{
   const group=el('details') as HTMLDetailsElement;group.dataset.group=name;group.open=expanded.get(name)??(name!=='reference'||!data.raster_time||window.innerHeight>=900);
   const names:Record<string,string>={reference:'Referencias geográficas',files:'Mis archivos',results:'Resultados'};
   group.append(el('summary',(names[name]??name)+' · '+layers.length));layers.forEach(layer=>group.append(row(layer)));tree.append(group);
  });
 }
 const highlight=()=>{tree.querySelectorAll<HTMLElement>('.sig-layer-row').forEach(node=>node.classList.toggle('is-active',node.dataset.series?model.observations.some(l=>l.id===adapter.data.active_layer):node.dataset.layer===adapter.data.active_layer))};
 const current=tree.querySelector('.sig-series-current');if(current)current.textContent=(model.current?.date||'Sin fecha')+' · '+model.count+' fechas · '+(model.current?.units||'Sin unidad');
 const filter=()=>{const query=search.value.toLocaleLowerCase().trim();if(query)(tree as any).populateObservations?.();
  tree.querySelectorAll<HTMLElement>('.sig-layer-row').forEach(node=>node.hidden=!(node.textContent??'').toLocaleLowerCase().includes(query));
  tree.querySelectorAll<HTMLDetailsElement>('details').forEach(group=>{group.hidden=query?![...group.querySelectorAll<HTMLElement>('.sig-layer-row')].some(node=>!node.hidden):false;if(query)group.open=true});highlight();
 };
 search.oninput=filter;filter();
}
