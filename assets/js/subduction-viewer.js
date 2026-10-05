import {BOX,hypocenterPoint,conceptualDepth,selectHypocenters,loadHypocenters} from './subduction-model.js';
import {projectPoint} from './terrain-model.js';
import {eventURL} from './andes-pulso.js';
const el=id=>document.getElementById(id),c=el('slab-canvas'),ctx=c.getContext('2d'),say=(es,en)=>document.documentElement.lang==='en'?en:es;
let events=[],loaded=false,failed=false,selected='',dots=[],drag=null,frame=0,listKey='';
const filters=()=>({magnitude:Number(el('slab-magnitude').value),to:Number(el('slab-year').value),maxDepth:Number(el('slab-depth').value)});
function draw(){
  frame=0;const rect=c.getBoundingClientRect();if(!rect.width||!ctx)return;const dpr=Math.min(devicePixelRatio||1,2);c.width=rect.width*dpr;c.height=rect.height*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);const w=rect.width,h=rect.height;
  ctx.fillStyle='#102b28';ctx.fillRect(0,0,w,h);const params={yaw:Number(el('slab-yaw').value)*Math.PI/180,pitch:Number(el('slab-pitch').value)*Math.PI/180,exaggeration:Number(el('slab-exaggeration').value)},scale=Math.min(w*.3,h*.3)/Math.max(1,params.exaggeration*.85);
  const screen=p=>{const q=projectPoint(p,params);return {x:w/2+q.x*scale,y:h*.33+q.y*scale,depth:q.depth};};
  const at=(longitude,latitude,depth=0)=>screen(hypocenterPoint({longitude,latitude,depth}));
  function path(points,color,fill=false){ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.strokeStyle=color;ctx.lineWidth=1.3;if(fill){ctx.closePath();ctx.fillStyle=color;ctx.fill();}else ctx.stroke();}
  const face=(west,east,color)=>path([at(west,BOX.south),at(east,BOX.south),at(east,BOX.north),at(west,BOX.north)],color,true);
  face(BOX.west,-80.5,'#51adbe22');face(-80.5,BOX.east,'#c6df7e22');
  if(el('slab-show-model').checked){for(let lat=-5.5;lat<=2.5;lat+=.5){const line=[];for(let lon=-83;lon<=-74.5;lon+=.125)line.push(at(lon,lat,conceptualDepth(lon)));path(line,'#efae7090');}for(let lon=-83;lon<=-74.5;lon+=.5)path([at(lon,BOX.south,conceptualDepth(lon)),at(lon,BOX.north,conceptualDepth(lon))],'#efae7070');}
  ctx.font='13px system-ui';ctx.fillStyle='#f1ede2';ctx.fillText(say('NAZCA → SUDAMÉRICA · GEOMETRÍA CONCEPTUAL','NAZCA → SOUTH AMERICA · CONCEPTUAL GEOMETRY'),12,24);
  ctx.fillText(say(`Profundidades del catálogo · escala vertical ×${params.exaggeration}`,`Catalog depths · vertical scale ×${params.exaggeration}`),12,45);
  for(const [label,lon] of [['Nazca',-82],['Sudamérica / South America',-77]]){const p=at(lon,0);ctx.fillText(label,p.x-30,p.y-12);}
  for(const depth of [0,100,300,600]){const a=at(BOX.east,BOX.south,depth);ctx.fillStyle='#d4dfd5';ctx.fillText(`${depth} km`,a.x+6,a.y);}
  path([at(BOX.east,BOX.south,0),at(BOX.east,BOX.south,700)],'#d4dfd5');
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
for(const id of ['slab-yaw','slab-pitch','slab-exaggeration','slab-magnitude','slab-year','slab-depth','slab-show-model'])el(id).addEventListener('input',requestDraw);
el('slab-event').addEventListener('change',e=>show(e.target.value));
el('slab-reset').addEventListener('click',()=>{for(const [id,value] of Object.entries({'slab-yaw':25,'slab-pitch':30,'slab-exaggeration':1,'slab-magnitude':6,'slab-year':2025,'slab-depth':700}))el(id).value=value;el('slab-show-model').checked=true;selected='';requestDraw();});
c.addEventListener('pointerdown',e=>{if(e.button!==0)return;drag={x:e.clientX,y:e.clientY,startX:e.clientX,startY:e.clientY,moved:false};c.setPointerCapture(e.pointerId);});
c.addEventListener('pointermove',e=>{if(!drag)return;drag.moved ||= Math.hypot(e.clientX-drag.startX,e.clientY-drag.startY)>4;el('slab-yaw').value=Math.max(-180,Math.min(180,Number(el('slab-yaw').value)+(e.clientX-drag.x)*.4));el('slab-pitch').value=Math.max(15,Math.min(80,Number(el('slab-pitch').value)+(e.clientY-drag.y)*.3));drag.x=e.clientX;drag.y=e.clientY;requestDraw();});
c.addEventListener('pointerup',e=>{if(drag&&!drag.moved){const r=c.getBoundingClientRect(),near=dots.map(d=>({...d,distance:Math.hypot(d.x-(e.clientX-r.left),d.y-(e.clientY-r.top))})).sort((a,b)=>a.distance-b.distance)[0];if(near&&near.distance<15)show(near.event.id);}drag=null;});
for(const type of ['pointercancel','lostpointercapture'])c.addEventListener(type,()=>{drag=null;});
new ResizeObserver(requestDraw).observe(c);window.addEventListener('portal:language',requestDraw);
loadHypocenters().then(value=>{events=value;loaded=true;requestDraw();}).catch(()=>{failed=true;requestDraw();});requestDraw();
for(const button of document.querySelectorAll('[data-model-scene]'))button.addEventListener('click',()=>{for(const b of document.querySelectorAll('[data-model-scene]'))b.setAttribute('aria-pressed',String(b===button));for(const section of document.querySelectorAll('[data-scene-panel]'))section.hidden=section.dataset.scenePanel!==button.dataset.modelScene;});
