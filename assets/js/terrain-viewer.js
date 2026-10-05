import {createTerrain,projectPoint,sectionProfile,modelState} from './terrain-model.js';
const grid=createTerrain(),el=id=>document.getElementById(id),canvas=el('terrain-canvas'),profile=el('terrain-profile');
const ctx=canvas.getContext('2d'),pc=profile.getContext('2d'),keys=['yaw','pitch','exaggeration','zoom','section'];
let state=modelState(),drag=null,frame=0;
const say=(es,en)=>document.documentElement.lang==='en'?en:es;
function size(c){const r=c.getBoundingClientRect(),ratio=Math.min(devicePixelRatio||1,2);c.width=Math.round(r.width*ratio);c.height=Math.round(r.height*ratio);return {w:r.width,h:r.height,ratio};}
function draw(){
  frame=0;if(!ctx||!pc){el('terrain-status').textContent=say('Tu navegador no dispone de Canvas. Consulta la descripción y los datos del ejemplo.','Canvas is unavailable. Read the description and example data.');return;}
  const {w,h,ratio}=size(canvas);ctx.setTransform(ratio,0,0,ratio,0,0);ctx.clearRect(0,0,w,h);ctx.fillStyle='#102b28';ctx.fillRect(0,0,w,h);
  const params={yaw:state.yaw*Math.PI/180,pitch:state.pitch*Math.PI/180,exaggeration:state.exaggeration},scale=Math.min(w*.29,h*.3)*state.zoom;
  const project=p=>{const q=projectPoint(p,params);return {...q,x:w/2+q.x*scale,y:h*.62+q.y*scale};};
  const triangles=[];
  for(let j=0;j<grid.length-1;j++)for(let i=0;i<grid.length-1;i++)for(const points of [[grid[j][i],grid[j][i+1],grid[j+1][i]],[grid[j+1][i],grid[j][i+1],grid[j+1][i+1]]]){
    const vertices=points.map(project),height=points.reduce((s,p)=>s+p.z,0)/3;
    triangles.push({vertices,depth:vertices.reduce((s,p)=>s+p.depth,0)/3,height});
  }
  triangles.sort((a,b)=>a.depth-b.depth);
  for(const {vertices,height} of triangles){ctx.beginPath();vertices.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.closePath();ctx.fillStyle=`hsl(${145-height*115} 29% ${35+height*90}%)`;ctx.fill();if(el('terrain-wire').checked){ctx.strokeStyle='#102b2855';ctx.lineWidth=.4;ctx.stroke();}}
  // Section trace is an overlay, deliberately visible through the mesh.
  const line=sectionProfile(grid,state.section);ctx.beginPath();line.map(project).forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.strokeStyle='#ffb69a';ctx.lineWidth=3;ctx.stroke();
  ctx.fillStyle='#f1ede2';ctx.font='13px system-ui';ctx.fillText(say('BORRADOR · MALLA SINTÉTICA','DRAFT · SYNTHETIC MESH'),16,26);ctx.fillText(say(`Exageración vertical ${state.exaggeration.toFixed(1)}×`,`Vertical exaggeration ${state.exaggeration.toFixed(1)}×`),16,48);
  const s=size(profile);pc.setTransform(s.ratio,0,0,s.ratio,0,0);pc.clearRect(0,0,s.w,s.h);pc.strokeStyle='#52645e';pc.lineWidth=1;pc.beginPath();pc.moveTo(35,16);pc.lineTo(35,s.h-28);pc.lineTo(s.w-16,s.h-28);pc.stroke();
  const pp=p=>({x:35+(p.x+1)/2*(s.w-51),y:s.h-28-p.z/.65*(s.h-48)});
  pc.beginPath();line.map(pp).forEach((p,i)=>i?pc.lineTo(p.x,p.y):pc.moveTo(p.x,p.y));pc.strokeStyle='#a84d2b';pc.lineWidth=3;pc.stroke();pc.fillStyle='#102b28';pc.font='12px system-ui';pc.fillText('x: −1',35,s.h-7);pc.fillText('x: +1',s.w-55,s.h-7);pc.fillText('z',12,22);
  el('terrain-status').textContent=say(`Malla de ${grid.length} × ${grid.length} puntos. Perfil y=${line[0].y.toFixed(2)}; altura original entre ${Math.min(...line.map(p=>p.z)).toFixed(3)} y ${Math.max(...line.map(p=>p.z)).toFixed(3)} unidades abstractas.`,`Mesh: ${grid.length} × ${grid.length} points. Profile y=${line[0].y.toFixed(2)}; original height ${Math.min(...line.map(p=>p.z)).toFixed(3)} to ${Math.max(...line.map(p=>p.z)).toFixed(3)} abstract units.`);
  for(const key of keys){el('terrain-'+key).value=state[key];el('value-'+key).textContent=String(state[key]);}
}
const requestDraw=()=>{if(!frame)frame=requestAnimationFrame(draw);};
for(const key of keys)el('terrain-'+key).addEventListener('input',e=>{state=modelState({...state,[key]:Number(e.target.value)});requestDraw();});
el('terrain-wire').addEventListener('change',requestDraw);
el('terrain-reset').addEventListener('click',()=>{state=modelState();el('terrain-wire').checked=false;requestDraw();});
canvas.addEventListener('pointerdown',e=>{if(e.button!==0)return;drag={x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);});
canvas.addEventListener('pointermove',e=>{if(!drag)return;state=modelState({...state,yaw:state.yaw+(e.clientX-drag.x)*.4,pitch:state.pitch+(e.clientY-drag.y)*.25});drag={x:e.clientX,y:e.clientY};requestDraw();});
for(const name of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(name,()=>{drag=null;});
canvas.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key))return;e.preventDefault();state=modelState({...state,yaw:state.yaw+(e.key==='ArrowLeft'?-5:e.key==='ArrowRight'?5:0),pitch:state.pitch+(e.key==='ArrowUp'?5:e.key==='ArrowDown'?-5:0)});requestDraw();});
el('terrain-export').addEventListener('click',()=>{const data={status:'synthetic-draft-not-ecuador',units:'dimensionless',crs:null,state,grid,profile:sectionProfile(grid,state.section)};const url=URL.createObjectURL(new Blob([JSON.stringify(data)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='ecuador-vivo-3d-synthetic-draft.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
new ResizeObserver(requestDraw).observe(canvas);window.addEventListener('portal:language',requestDraw);requestDraw();
