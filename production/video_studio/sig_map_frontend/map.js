export default function(component){
 const {data,parentElement,setTriggerValue}=component,root=parentElement.querySelector('#sig-map');
 const svg=root.querySelector('svg'),q=id=>root.querySelector('#'+id),ns='http://www.w3.org/2000/svg';
 let box=[...data.view.bbox],pending=false,drag=null;
 root.querySelectorAll('button').forEach(b=>b.disabled=false);
 root.dataset.version=String(data.version);root.dataset.active=data.active_layer||'';
 const status=text=>q('sig-map-status').textContent=text;
 function paintBox(){svg.setAttribute('viewBox',`${box[0]} ${-box[3]} ${box[2]-box[0]} ${box[3]-box[1]}`);root.dataset.bbox=JSON.stringify(box)}
 function send(action,values={}){if(pending)return;pending=true;status('Guardando vista…');root.querySelectorAll('button').forEach(b=>b.disabled=true);setTriggerValue('command',{action,...values,version:data.version})}
 function constrained(next){let w=Math.min(360,Math.max(.0001,next[2]-next[0])),h=Math.min(179.998,Math.max(.0001,next[3]-next[1]));let x=Math.min(180-w,Math.max(-180,next[0])),y=Math.min(89.999-h,Math.max(-89.999,next[1]));return [x,y,x+w,y+h]}
 function point(e){const p=svg.createSVGPoint();p.x=e.clientX;p.y=e.clientY;const xy=p.matrixTransform(svg.getScreenCTM().inverse());return [xy.x,-xy.y]}
 function zoom(factor,center){const c=center||[(box[0]+box[2])/2,(box[1]+box[3])/2];box=constrained([c[0]+(box[0]-c[0])*factor,c[1]+(box[1]-c[1])*factor,c[0]+(box[2]-c[0])*factor,c[1]+(box[3]-c[1])*factor]);paintBox();send('view',{bbox:box})}
 const fragment=document.createDocumentFragment();
 for(const layer of data.layers){
  if(!layer.visible)continue;
  const group=document.createElementNS(ns,'g');group.dataset.layer=layer.id;
  for(const feature of layer.features){
   const path=document.createElementNS(ns,'path'),polygons=feature.geometry.type==='Polygon'?[feature.geometry.coordinates]:feature.geometry.coordinates;
   const d=polygons.flatMap(poly=>poly.map(ring=>ring.map((p,i)=>(i?'L':'M')+p[0]+' '+(-p[1])).join(' ')+'Z')).join(' ');
   path.setAttribute('d',d);path.setAttribute('fill',layer.style.fill);path.setAttribute('stroke',layer.style.stroke);path.setAttribute('fill-opacity',layer.style.opacity);
   path.setAttribute('fill-rule','evenodd');path.setAttribute('stroke-width','1.5');path.setAttribute('vector-effect','non-scaling-stroke');
   path.classList.add('geo-feature');path.dataset.region=feature.region_id;path.dataset.layer=layer.id;
   if(data.active_layer===layer.id&&data.selection.includes(feature.region_id))path.classList.add('selected');
   group.appendChild(path);
  }
  fragment.appendChild(group);
 }
 svg.replaceChildren(fragment);paintBox();status(data.error||'Guardado');root.dataset.state=data.error?'error':'saved';
 q('sig-zoom-in').onclick=()=>zoom(.8);q('sig-zoom-out').onclick=()=>zoom(1.25);
 q('sig-fit-all').onclick=()=>send('fit_all');q('sig-fit-layer').onclick=()=>send('fit',{layer_id:data.active_layer});
 q('sig-fit-layer').disabled=!data.active_layer;q('sig-clear').onclick=()=>send('clear_selection');
 svg.onwheel=e=>{e.preventDefault();if(!pending)zoom(e.deltaY<0?.8:1.25,point(e))};
 svg.onpointerdown=e=>{if(e.button!==0||pending)return;drag={id:e.pointerId,start:point(e),box:[...box],x:e.clientX,y:e.clientY,target:e.target,changed:false};svg.setPointerCapture(e.pointerId)};
 svg.onpointermove=e=>{const p=point(e);q('sig-coordinate').textContent=`Lon ${p[0].toFixed(5)}° · Lat ${p[1].toFixed(5)}°`;if(!drag)return;
  if(Math.hypot(e.clientX-drag.x,e.clientY-drag.y)>4)drag.changed=true;
  if(drag.changed){const dx=p[0]-drag.start[0],dy=p[1]-drag.start[1];box=constrained([box[0]-dx,box[1]-dy,box[2]-dx,box[3]-dy]);paintBox()}};
 svg.onpointerup=e=>{if(!drag)return;const previous=drag;drag=null;svg.releasePointerCapture(e.pointerId);
  if(previous.changed)send('view',{bbox:box});else if(previous.target.dataset.region)send('select',{layer_id:previous.target.dataset.layer,region_id:previous.target.dataset.region});else send('clear_selection')};
 svg.onpointercancel=()=>{if(drag){box=drag.box;paintBox();drag=null}};
 svg.onkeydown=e=>{if(e.key==='+'||e.key==='='){e.preventDefault();zoom(.8)}else if(e.key==='-'){e.preventDefault();zoom(1.25)}else if(e.key==='Escape')send('clear_selection')};
}
