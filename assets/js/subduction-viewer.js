import {BOX,hypocenterPoint,selectHypocenters,loadHypocenters} from './subduction-model.js';
import {loadSlab2,slabSegments,slabNode} from './slab2.js';
import {projectPoint} from './terrain-model.js';
import {eventURL} from './andes-pulso.js';
const el=id=>document.getElementById(id),c=el('slab-canvas'),ctx=c.getContext('2d'),say=(es,en)=>document.documentElement.lang==='en'?en:es;
let events=[],loaded=false,failed=false,selected='',dots=[],drag=null,frame=0,listKey='';
let slab=null,segments=[],slabFailed=false;
const filters=()=>({magnitude:Number(el('slab-magnitude').value),to:Number(el('slab-year').value),maxDepth:Number(el('slab-depth').value)});
function draw(){
  frame=0;const rect=c.getBoundingClientRect();if(!rect.width||!ctx)return;const dpr=Math.min(devicePixelRatio||1,2);c.width=rect.width*dpr;c.height=rect.height*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);const w=rect.width,h=rect.height;
  ctx.fillStyle='#102b28';ctx.fillRect(0,0,w,h);const params={yaw:Number(el('slab-yaw').value)*Math.PI/180,pitch:Number(el('slab-pitch').value)*Math.PI/180,exaggeration:Number(el('slab-exaggeration').value)},scale=Math.min(w*.3,h*.3)/Math.max(1,params.exaggeration*.85);
  const screen=p=>{const q=projectPoint(p,params);return {x:w/2+q.x*scale,y:h*.33+q.y*scale,depth:q.depth};};
  const at=(longitude,latitude,depth=0)=>screen(hypocenterPoint({longitude,latitude,depth}));
  function path(points,color,fill=false){ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.strokeStyle=color;ctx.lineWidth=1.3;if(fill){ctx.closePath();ctx.fillStyle=color;ctx.fill();}else ctx.stroke();}
  const face=(west,east,color)=>path([at(west,BOX.south),at(east,BOX.south),at(east,BOX.north),at(west,BOX.north)],color,true);
  // Neutral sea-level reference, not a coastline or continental plate geometry.
  face(BOX.west,BOX.east,'#b7d1cc0b');
  if(el('slab-show-model').checked)for(const [a,b] of segments){
    const u=a.uncertainty,color=el('slab-color').value==='uncertainty'?(u===null?'#888888':u<10?'#8fd8c4':u<20?'#e6dc7c':'#ed8d74'):'#efae70aa';
    path([at(a.longitude,a.latitude,a.depth),at(b.longitude,b.latitude,b.depth)],color);
  }
  ctx.font='13px system-ui';ctx.fillStyle='#f1ede2';ctx.fillText(say('NAZCA · SUPERFICIE MODELADA SLAB2 (2018)','NAZCA · SLAB2 MODELED SURFACE (2018)'),12,24,w-24);
  ctx.fillText(say(`Profundidades del catálogo · escala vertical ×${params.exaggeration}`,`Catalog depths · vertical scale ×${params.exaggeration}`),12,45);
  ctx.fillText(el('slab-color').value==='uncertainty'?say('Malla: incertidumbre (km) · verde <10 / amarillo <20 / coral ≥20','Mesh: uncertainty (km) · green <10 / yellow <20 / coral ≥20'):say('Malla naranja: profundidad modelada · no es un volumen de placas','Orange mesh: modeled depth · not a plate volume'),12,65,w-24);
  for(const [label,lon,lat] of [['83° O/W',-83,BOX.south],['74.5° O/W',-74.5,BOX.north],['N',-78.75,BOX.north]]){const p=at(lon,lat);ctx.fillText(label,p.x-30,p.y-12);}
  for(const depth of [0,100,300,600]){const a=at(BOX.east,BOX.south,depth);ctx.fillStyle='#d4dfd5';ctx.fillText(`${depth} km`,a.x+6,a.y);}
  path([at(BOX.east,BOX.south,0),at(BOX.east,BOX.south,700)],'#d4dfd5');
  el('slab-model-status').textContent=slabFailed?say('Slab2 no pudo verificarse: superficie oculta, sin sustituto inventado.','Slab2 could not be verified: surface hidden, no invented fallback.'):slab?say('Slab2 verificado · 21 849 nodos con profundidad · paso nativo 0,05°. La separación de nodos no es la exactitud.','Verified Slab2 · 21,849 depth nodes · native spacing 0.05°. Node spacing is not accuracy.'):say('Comprobando Slab2…','Checking Slab2…');
  if(slab){const row=Number(el('slab-node-lat').value),col=Number(el('slab-node-lon').value),node=slabNode(slab,row,col);
    el('slab-node-info').textContent=`${slab.latitude[row].toFixed(2)}°, ${slab.longitude[col].toFixed(2)}° · `+(node?say(`profundidad modelada ${node.depth.toFixed(1)} km · incertidumbre publicada ${node.uncertainty===null?'—':node.uncertainty.toFixed(1)} km`,`modeled depth ${node.depth.toFixed(1)} km · published uncertainty ${node.uncertainty===null?'—':node.uncertainty.toFixed(1)} km`):say('Sin modelo en este nodo.','No model at this node.'));
    if(node&&el('slab-show-model').checked){const p=at(node.longitude,node.latitude,node.depth);ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.strokeRect(p.x-5,p.y-5,10,10);}
  }
  const visible=selectHypocenters(events,filters());dots=visible.map(event=>({...screen(hypocenterPoint(event)),event})).sort((a,b)=>a.depth-b.depth);
  for(const dot of dots){ctx.beginPath();ctx.arc(dot.x,dot.y,Math.max(3,(dot.event.magnitude-3)*1.35),0,Math.PI*2);ctx.fillStyle=dot.event.depth<70?'#f49b83':dot.event.depth<300?'#e6dc7c':'#8fc9ee';ctx.fill();if(dot.event.id===selected){ctx.strokeStyle='white';ctx.lineWidth=3;ctx.stroke();}}
  el('slab-year-value').textContent=el('slab-year').value;el('slab-depth-value').textContent=el('slab-depth').value;el('slab-exaggeration-value').textContent=el('slab-exaggeration').value;
  el('slab-status').textContent=failed?say('No se pudo verificar el catálogo. No se muestran sismos.','Catalog could not be verified. No earthquakes are shown.'):loaded?say(`${visible.length} hipocentros visibles de ${events.length} registros conservados. No es un catálogo completo ni en vivo.`,`${visible.length} visible hypocenters from ${events.length} preserved records. Not a complete or live catalog.`):say('Comprobando catálogo y SHA-256…','Checking catalog and SHA-256…');
  const picker=el('slab-event'),nextKey=JSON.stringify([filters(),events.length,document.documentElement.lang]);
  if(nextKey!==listKey){listKey=nextKey;picker.replaceChildren();const option=document.createElement('option');option.value='';option.textContent=say('Selecciona un sismo…','Select an earthquake…');picker.append(option);
    for(const event of visible){const o=document.createElement('option');o.value=event.id;o.textContent=`${new Date(event.time).toISOString().slice(0,10)} · M ${event.magnitude} · ${event.depth} km · ${event.id}`;picker.append(o);}}
  picker.value=visible.some(e=>e.id===selected)?selected:'';if(!picker.value){selected='';el('slab-record').textContent='';el('slab-event-link').hidden=true;}
}
const requestDraw=()=>{if(!frame)frame=requestAnimationFrame(draw);};
function show(id){selected=id;const event=events.find(e=>e.id===id);if(event){el('slab-record').textContent=`${new Date(event.time).toISOString()} · M ${event.magnitude} (${event.magnitudeType}) · ${event.depth} km · ${event.latitude}, ${event.longitude} · ${event.place}`;el('slab-event-link').href=eventURL(event.id);el('slab-event-link').hidden=false;}requestDraw();}
for(const id of ['slab-yaw','slab-pitch','slab-exaggeration','slab-magnitude','slab-year','slab-depth','slab-show-model','slab-color','slab-node-lat','slab-node-lon'])el(id).addEventListener('input',requestDraw);
el('slab-event').addEventListener('change',e=>show(e.target.value));
el('slab-reset').addEventListener('click',()=>{for(const [id,value] of Object.entries({'slab-yaw':25,'slab-pitch':30,'slab-exaggeration':1,'slab-magnitude':6,'slab-year':2025,'slab-depth':700,'slab-color':'surface','slab-node-lat':100,'slab-node-lon':100}))el(id).value=value;el('slab-show-model').checked=true;selected='';requestDraw();});
c.addEventListener('pointerdown',e=>{if(e.button!==0)return;drag={x:e.clientX,y:e.clientY,startX:e.clientX,startY:e.clientY,moved:false};c.setPointerCapture(e.pointerId);});
c.addEventListener('pointermove',e=>{if(!drag)return;drag.moved ||= Math.hypot(e.clientX-drag.startX,e.clientY-drag.startY)>4;el('slab-yaw').value=Math.max(-180,Math.min(180,Number(el('slab-yaw').value)+(e.clientX-drag.x)*.4));el('slab-pitch').value=Math.max(15,Math.min(80,Number(el('slab-pitch').value)+(e.clientY-drag.y)*.3));drag.x=e.clientX;drag.y=e.clientY;requestDraw();});
c.addEventListener('pointerup',e=>{if(drag&&!drag.moved){const r=c.getBoundingClientRect(),near=dots.map(d=>({...d,distance:Math.hypot(d.x-(e.clientX-r.left),d.y-(e.clientY-r.top))})).sort((a,b)=>a.distance-b.distance)[0];if(near&&near.distance<15)show(near.event.id);}drag=null;});
for(const type of ['pointercancel','lostpointercapture'])c.addEventListener(type,()=>{drag=null;});
new ResizeObserver(requestDraw).observe(c);window.addEventListener('portal:language',requestDraw);
loadHypocenters().then(value=>{events=value;loaded=true;requestDraw();}).catch(()=>{failed=true;requestDraw();});requestDraw();
loadSlab2().then(value=>{slab=value;segments=slabSegments(slab);el('slab-node-lat').disabled=false;el('slab-node-lon').disabled=false;requestDraw();}).catch(()=>{slabFailed=true;requestDraw();});
for(const button of document.querySelectorAll('[data-model-scene]'))button.addEventListener('click',()=>{for(const b of document.querySelectorAll('[data-model-scene]'))b.setAttribute('aria-pressed',String(b===button));for(const section of document.querySelectorAll('[data-scene-panel]'))section.hidden=section.dataset.scenePanel!==button.dataset.modelScene;});
