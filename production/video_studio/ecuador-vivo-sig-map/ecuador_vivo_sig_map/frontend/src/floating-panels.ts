/** Non-modal local windows. No source fetching, project edits or map recreation. */
import {floatingPosition} from './workbench-model';
export type WindowName='layers'|'reference'|'properties'|'table'|'toolbox';
const selectors:Record<WindowName,[string,string]>={layers:['sig-layers-window','sig-layers-view'],reference:['sig-reference-window','sig-reference-view'],properties:['sig-properties-window','sig-properties-view'],table:['sig-table-window','sig-attributes-view'],toolbox:['sig-toolbox-window','sig-toolbox-view']};
export class FloatingPanels{
 private observer:ResizeObserver;private z=12;private frame=0;private disposed=false;
 private positioned=new Set<WindowName>();
 constructor(private root:HTMLElement){
  const q=(id:string)=>root.querySelector<HTMLElement>('#'+id)!;
  const bring=(node:HTMLElement)=>node.style.zIndex=String(++this.z);
  this.observer=new ResizeObserver(()=>{cancelAnimationFrame(this.frame);this.frame=requestAnimationFrame(()=>{if(!this.disposed)this.clampAll()})});
  this.observer.observe(q('sig-geographic-map'));
  for(const [name,[id,trigger]] of Object.entries(selectors) as [WindowName,[string,string]][]){
   const node=q(id),handle=node.querySelector<HTMLElement>('[data-drag-window]')!;
   q(trigger).onclick=()=>this.toggle(name);node.onpointerdown=()=>bring(node);this.observer.observe(node);
   handle.title='Arrastra para mover. Flechas: mover; Ctrl + flechas: tamaño.';
   let origin:{x:number;y:number;left:number;top:number}|undefined;
   handle.onpointerdown=event=>{
    if(event.button!==0)return;event.preventDefault();event.stopPropagation();bring(node);handle.focus();
    origin={x:event.clientX,y:event.clientY,left:node.offsetLeft,top:node.offsetTop};handle.setPointerCapture(event.pointerId);
   };
   handle.onpointermove=event=>{if(origin){event.preventDefault();this.move(node,origin.left+event.clientX-origin.x,origin.top+event.clientY-origin.y)}};
   const finish=()=>{origin=undefined};handle.onpointerup=finish;handle.onpointercancel=finish;handle.onlostpointercapture=finish;
   handle.onkeydown=event=>{
    if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key))return;
    event.preventDefault();const step=event.shiftKey?32:8,dx=event.key==='ArrowRight'?step:event.key==='ArrowLeft'?-step:0,dy=event.key==='ArrowDown'?step:event.key==='ArrowUp'?-step:0;
    if(event.ctrlKey){node.style.width=Math.max(name==='table'?260:220,node.offsetWidth+dx)+'px';node.style.height=Math.max(name==='table'?140:110,node.offsetHeight+dy)+'px';node.classList.remove('sig-window-maximized');if(name==='table')q('sig-table-maximize').setAttribute('aria-pressed','false')}
    else this.move(node,node.offsetLeft+dx,node.offsetTop+dy);
   };
   node.onkeydown=event=>{if(event.key==='Escape'){event.stopPropagation();this.close(name)}};
  }
  for(const [id,name] of [['sig-toggle-layers','layers'],['sig-toggle-inspector','properties'],['sig-reference-close','reference'],['sig-toggle-dock','table'],['sig-toolbox-close','toolbox']] as [string,WindowName][])q(id).onclick=()=>this.close(name);
  q('sig-table-maximize').onclick=()=>{const node=q('sig-table-window');node.classList.toggle('sig-window-maximized');q('sig-table-maximize').setAttribute('aria-pressed',String(node.classList.contains('sig-window-maximized')));this.clampAll()};
 }
 private move(node:HTMLElement,x:number,y:number){
  const host=this.root.querySelector<HTMLElement>('.sig-shell-body')!;
  const position=floatingPosition({x,y},{width:host.clientWidth,height:host.clientHeight},{width:node.offsetWidth,height:node.offsetHeight});
  node.style.left=position.x+'px';node.style.top=position.y+'px';
 }
 private clampAll(){
  for(const [id] of Object.values(selectors)){const node=this.root.querySelector<HTMLElement>('#'+id)!;if(!node.hidden&&!node.classList.contains('sig-window-maximized'))this.move(node,node.offsetLeft,node.offsetTop)}
 }
 open(name:WindowName){
  const [id,trigger]=selectors[name],node=this.root.querySelector<HTMLElement>('#'+id)!,host=this.root.querySelector<HTMLElement>('.sig-shell-body')!;
  node.hidden=false;
  if(!this.positioned.has(name)){
   this.positioned.add(name);
   this.move(node,name==='properties'||name==='toolbox'?host.clientWidth-node.offsetWidth-16:16,name==='table'?host.clientHeight-node.offsetHeight-16:16);
  }else this.clampAll();
  node.style.zIndex=String(++this.z);this.root.querySelector('#'+trigger)!.setAttribute('aria-expanded','true');
  node.querySelector<HTMLElement>('[data-drag-window]')!.focus();
 }
 close(name:WindowName){
  const [id,trigger]=selectors[name];this.root.querySelector<HTMLElement>('#'+id)!.hidden=true;
  const button=this.root.querySelector<HTMLElement>('#'+trigger)!;button.setAttribute('aria-expanded','false');button.focus();
 }
 toggle(name:WindowName){const [id]=selectors[name];this.root.querySelector<HTMLElement>('#'+id)!.hidden?this.open(name):this.close(name)}
 reset(){for(const name of Object.keys(selectors) as WindowName[]){const node=this.root.querySelector<HTMLElement>('#'+selectors[name][0])!;node.hidden=true;node.removeAttribute('style');node.classList.remove('sig-window-maximized');this.root.querySelector('#'+selectors[name][1])!.setAttribute('aria-expanded','false')};this.positioned.clear();this.root.querySelector('#sig-table-maximize')!.setAttribute('aria-pressed','false')}
 dispose(){this.disposed=true;cancelAnimationFrame(this.frame);this.observer.disconnect()}
}
