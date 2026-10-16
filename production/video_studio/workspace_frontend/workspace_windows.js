/* Presentation only. No project mutations, server commands or document writes. */
function studioWindowState(saved={}){
 const current=saved.windowVersion===1;
 return {...saved,windowVersion:1,left:current&&saved.left===true,right:current&&saved.right===true,
  collapsed:current?saved.collapsed!==false:true,focusVideo:current&&saved.focusVideo===true,
  windowRects:current&&saved.windowRects&&typeof saved.windowRects==='object'?saved.windowRects:{}};
}
function studioWindowRect(saved,bounds,side){
 const finite=(value,fallback)=>Number.isFinite(value)?value:fallback;
 const bw=Math.max(1,finite(bounds.width,1200)),bh=Math.max(1,finite(bounds.height,700));
 const gap=Math.min(12,bw/20,bh/20),maxW=Math.max(1,bw-2*gap),maxH=Math.max(1,bh-2*gap);
 const clamp=(v,min,max)=>Math.max(min,Math.min(max,v));
 const width=clamp(finite(saved?.width,side==='left'?348:324),Math.min(260,maxW),maxW);
 const height=clamp(finite(saved?.height,484),Math.min(200,maxH),maxH);
 return {width,height,x:clamp(finite(saved?.x,side==='left'?gap:bw-width-gap),gap,bw-width-gap),
  y:clamp(finite(saved?.y,44),gap,bh-height-gap)};
}
function createStudioWindows({root,ui,save}){
 const q=id=>root.querySelector('#'+id),shell=root.querySelector('.evs'),host=root.querySelector('.workspace');
 const panels=Object.fromEntries(['left','right'].map(side=>[side,root.querySelector('[data-studio-window="'+side+'"]')]));
 const cleanups=[];let top=30,disposed=false;
 const listen=(el,type,fn)=>{el.addEventListener(type,fn);cleanups.push(()=>el.removeEventListener(type,fn))};
 const bounds=()=>({width:host.clientWidth||1200,height:host.clientHeight||700});
 const place=side=>{
  const rect=studioWindowRect(ui.windowRects[side],bounds(),side);ui.windowRects[side]=rect;
  Object.assign(panels[side].style,{left:rect.x+'px',top:rect.y+'px',width:rect.width+'px',height:rect.height+'px'});
 };
 const raise=side=>{panels[side].style.zIndex=String(++top)};
 function sync(){
  if(disposed)return;
  shell.classList.toggle('focus-video',!!ui.focusVideo);
  shell.classList.toggle('timeline-collapsed',!!ui.collapsed);
  for(const side of ['left','right']){
   place(side);panels[side].hidden=!ui[side]||ui.focusVideo;
   q('toggle-'+side).setAttribute('aria-expanded',String(!panels[side].hidden));
  }
  root.querySelectorAll?.('[data-tab]').forEach(button=>{
   button.setAttribute('aria-controls','studio-library');
   button.setAttribute('aria-expanded',String(!panels.left.hidden&&button.dataset.tab===ui.tab));
  });
  q('focus-mode').setAttribute('aria-pressed',String(!!ui.focusVideo));q('focus-exit').hidden=!ui.focusVideo;
  q('timeline-collapse').setAttribute('aria-expanded',String(!ui.collapsed));
  q('timeline-collapse').setAttribute('aria-label',ui.collapsed?'Desplegar montaje':'Recoger montaje');
  q('timeline-collapse').title=ui.collapsed?'Desplegar montaje':'Recoger montaje';
 }
 function open(side,focus=true){
  ui.focusVideo=false;ui[side]=true;
  if(bounds().width<=740)ui[side==='left'?'right':'left']=false;
  raise(side);sync();save();if(focus)panels[side].querySelector('[data-window-drag]').focus({preventScroll:true});
 }
 function close(side,restoreFocus=true){ui[side]=false;sync();save();if(restoreFocus)q('toggle-'+side).focus({preventScroll:true})}
 function focus(value){ui.focusVideo=!!value;sync();save();(value?q('focus-exit'):q('focus-mode')).focus({preventScroll:true})}
 for(const side of ['left','right']){
  const panel=panels[side],heading=panel.querySelector('[data-window-drag]'),handle=panel.querySelector('[data-window-resize]');
  listen(q('toggle-'+side),'click',()=>ui[side]&&!ui.focusVideo?close(side):open(side));
  listen(q('close-'+side),'click',()=>close(side));
  listen(panel,'pointerdown',()=>raise(side));
  for(const [control,resizing] of [[heading,false],[handle,true]]){
   let gesture=null;
   const finish=event=>{
    if(!gesture||event.pointerId!==gesture.id)return;
    try{control.releasePointerCapture(gesture.id)}catch{}
    gesture=null;panel.classList.toggle('window-moving',false);save();
   };
   listen(control,'pointerdown',event=>{
    if(event.button!==0||(!resizing&&event.target.closest?.('button,input,select,textarea')))return;
    event.preventDefault();raise(side);control.focus({preventScroll:true});
    gesture={id:event.pointerId,x:event.clientX,y:event.clientY,rect:{...ui.windowRects[side]}};
    control.setPointerCapture(event.pointerId);panel.classList.toggle('window-moving',true);
   });
   listen(control,'pointermove',event=>{
    if(!gesture||event.pointerId!==gesture.id)return;
    const dx=event.clientX-gesture.x,dy=event.clientY-gesture.y,r=gesture.rect;
    ui.windowRects[side]=resizing?{...r,width:r.width+dx,height:r.height+dy}:{...r,x:r.x+dx,y:r.y+dy};
    place(side);
   });
   listen(control,'pointerup',finish);listen(control,'pointercancel',finish);listen(control,'lostpointercapture',finish);
   listen(control,'keydown',event=>{
    if(event.target!==control||!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key))return;
    event.preventDefault();const step=event.shiftKey?10:1;
    const axis=['ArrowLeft','ArrowRight'].includes(event.key)?(resizing?'width':'x'):(resizing?'height':'y');
    ui.windowRects[side][axis]+=step*(['ArrowLeft','ArrowUp'].includes(event.key)?-1:1);
    place(side);save();
   });
   cleanups.push(()=>{if(gesture){try{control.releasePointerCapture(gesture.id)}catch{}gesture=null}});
  }
 }
 listen(q('focus-mode'),'click',()=>focus(!ui.focusVideo));listen(q('focus-exit'),'click',()=>focus(false));
 listen(q('timeline-collapse'),'click',()=>{ui.collapsed=!ui.collapsed;sync();save()});
 const view=root.ownerDocument?.defaultView;
 if(view)listen(view,'resize',sync);
 const observer=typeof ResizeObserver==='function'?new ResizeObserver(sync):null;observer?.observe(host);
 sync();
 return {open,close,focus,sync,dispose(){disposed=true;observer?.disconnect();cleanups.splice(0).forEach(fn=>fn())}};
}
