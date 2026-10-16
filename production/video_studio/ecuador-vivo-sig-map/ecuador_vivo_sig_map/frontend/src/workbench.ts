/** Local workbench geometry and task chrome; no project transactions. */
import {visibleTask,type Task} from './workbench-model';
import {FloatingPanels} from './floating-panels';
type Host={root:HTMLElement;map:{updateSize:()=>void};updateMapHeight:()=>void;disposed:boolean;workbenchCleanup?:()=>void};
const instances=new WeakMap<HTMLElement,Workbench>();
const NS='http://www.w3.org/2000/svg';
const paths:Record<string,string>={
 home:'M3 11 12 3 21 11M6 9v12h12V9M10 21v-7h4v7',
 folder:'M3 7h7l2 3h9v11H3ZM3 7V4h7l2 3',
 save:'M4 3h13l4 4v14H4ZM8 3v6h9V3M8 21v-8h9v8',
 undo:'M9 5 4 10l5 5M4 10h10a6 6 0 0 1 0 12',
 redo:'M15 5 20 10l-5 5M20 10h-10a6 6 0 0 0 0 12',
 layers:'m3 7 9-4 9 4-9 4ZM3 12l9 4 9-4M3 17l9 4 9-4',
 settings:'M4 6h16M4 12h16M4 18h16M8 3v6M16 9v6M10 15v6',
 add:'M12 4v16M4 12h16',
 raster:'M4 4h16v16H4ZM4 9h16M4 15h16M9 4v16M15 4v16',
 vector:'M5 5h3v3H5ZM16 5h3v3h-3ZM10 16h3v3h-3ZM8 7h8M7 8l4 8M17 8l-4 8',
 calendar:'M4 6h16v15H4ZM8 3v6M16 3v6M4 11h16M8 15h2M14 15h2',
 chart:'M4 3v18h17M8 17v-5M13 17V8M18 17V5',
 frame:'M3 3h7M3 3v7M21 3h-7M21 3v7M3 21h7M3 21v-7M21 21h-7M21 21v-7',
 film:'M4 3h16v18H4ZM4 8h16M4 16h16M8 3v18M16 3v18',
 arrow:'M4 12h15M13 5l7 7-7 7',
 close:'M6 6l12 12M18 6 6 18',
 globe:'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0ZM3 12h18M12 3c-6 5-6 13 0 18 6-5 6-13 0-18',
 table:'M3 4h18v16H3ZM3 9h18M3 14h18M9 4v16',
 previous:'m15 5-7 7 7 7M5 5v14',next:'m9 5 7 7-7 7M19 5v14',
 zoomIn:'M17 10a7 7 0 1 1-14 0 7 7 0 0 1 14 0ZM15 15l6 6M6 10h8M10 6v8',zoomOut:'M17 10a7 7 0 1 1-14 0 7 7 0 0 1 14 0ZM15 15l6 6M6 10h8',
 play:'m8 4 12 8-12 8Z',pause:'M7 4v16M17 4v16',
 search:'M17 10a7 7 0 1 1-14 0 7 7 0 0 1 14 0ZM15 15l6 6',
 ruler:'m3 15 12-12 6 6-12 12ZM7 11l3 3M10 8l3 3M13 5l3 3',
 area:'M4 4h16v16H4ZM4 10l6-6M4 16 16 4M8 20 20 8M14 20l6-6'
};
export function icon(name:string){
 const svg=document.createElementNS(NS,'svg');svg.setAttribute('viewBox','0 0 24 24');svg.setAttribute('aria-hidden','true');svg.classList.add('sig-icon');
 const path=document.createElementNS(NS,'path');path.setAttribute('d',paths[name]??paths.layers);svg.append(path);return svg;
}
class Workbench{
 task:Task='map';panels:FloatingPanels;observer:ResizeObserver;lastWidth=0;frame=0;
 constructor(public host:Host){
  const root=host.root,q=(id:string)=>root.querySelector<HTMLElement>('#'+id)!;
  const buttons:Record<string,string>={
   'sig-home':'home','sig-studio':'film','sig-resources':'layers','sig-open':'folder','sig-save':'save','sig-undo':'undo','sig-redo':'redo','sig-send-top':'arrow',
   'sig-add-data':'add','sig-import':'add','sig-properties-view':'settings','sig-analysis':'vector','sig-raster-tools':'raster','sig-results-view':'chart','sig-processes':'settings',
   'sig-prepare':'calendar','sig-series-palette':'settings','sig-output-settings':'frame','sig-layout-reset':'layers','sig-toggle-layers':'close','sig-toggle-inspector':'close',
   'sig-fit-all':'frame','sig-fit-layer':'raster','sig-clear':'close','sig-layers-view':'layers','sig-reference-view':'globe','sig-attributes-view':'table',
   'sig-time-view':'calendar','sig-reference-close':'close','sig-toggle-dock':'close','sig-table-maximize':'frame','sig-time-prev':'previous','sig-time-next':'next',
   'sig-time-zoom-in':'zoomIn','sig-time-zoom-out':'zoomOut','sig-time-settings':'settings','sig-time-close':'close',
   'sig-toolbox-view':'settings','sig-toolbox-close':'close','sig-science':'chart','sig-export-layer':'folder'};
  for(const [id,name] of Object.entries(buttons)){
   const button=q(id),label=document.createElement('span');label.textContent=button.textContent;
   button.replaceChildren(icon(name),label);button.title=button.getAttribute('aria-label')||label.textContent||'';
  }
  root.querySelectorAll<HTMLButtonElement>('[data-workbench-task]').forEach(button=>{
   button.onclick=()=>{this.task=visibleTask(button.dataset.workbenchTask);this.sync()};
   button.onkeydown=event=>{
    if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;
    event.preventDefault();const tabs=[...root.querySelectorAll<HTMLButtonElement>('[data-workbench-task]')];let index=tabs.indexOf(button);
    index=event.key==='Home'?0:event.key==='End'?tabs.length-1:(index+(event.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;
    tabs[index].click();tabs[index].focus();
   };
  });
  this.panels=new FloatingPanels(root);
  q('sig-layout-reset').onclick=()=>{this.panels.reset();this.sync()};
  this.observer=new ResizeObserver(()=>{const width=Math.round(root.getBoundingClientRect().width);if(width===this.lastWidth)return;this.lastWidth=width;this.sync()});this.observer.observe(root);
  host.workbenchCleanup=()=>{cancelAnimationFrame(this.frame);this.observer.disconnect();this.panels.dispose();instances.delete(root)};
 }
 sync(){
  const {host}=this;if(host.disposed)return;
  const root=host.root,width=root.getBoundingClientRect().width||window.innerWidth;
  root.dataset.task=this.task;root.classList.toggle('sig-narrow',width<=760);
  root.querySelectorAll<HTMLButtonElement>('[data-workbench-task]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.workbenchTask===this.task)));
  root.querySelectorAll<HTMLElement>('[data-task-group]').forEach(group=>group.hidden=group.dataset.taskGroup!==this.task);
  cancelAnimationFrame(this.frame);this.frame=requestAnimationFrame(()=>{if(!host.disposed){host.updateMapHeight();host.map.updateSize()}});
 }
}
export function workbench(host:Host){let item=instances.get(host.root);if(!item){item=new Workbench(host);instances.set(host.root,item)}item.sync();return item}
