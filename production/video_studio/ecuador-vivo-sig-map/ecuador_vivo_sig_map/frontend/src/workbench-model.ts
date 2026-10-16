/** Presentation state only: never included in the scientific project. */
export const TASKS=['map','data','analysis','time','output'] as const;
export type Task=typeof TASKS[number];
export type ProcessingTool={id:string;label:string;kind:string;group:string;summary:string;available:boolean;reason:string};
export function filterTools(tools:ProcessingTool[],query:string,kind:string){
 const normalize=(v:string)=>v.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase();
 const words=normalize(query).trim().split(/\s+/).filter(Boolean);
 return tools.filter(t=>(kind==='all'||t.kind===kind)&&words.every(w=>normalize(t.label+' '+t.group+' '+t.summary).includes(w)));
}
export type PanelSizes={left:number;right:number;dock:number};
export function floatingPosition(position:{x:number;y:number},host:{width:number;height:number},panel:{width:number;height:number}){
 if(![...Object.values(position),...Object.values(host),...Object.values(panel)].every(Number.isFinite))throw new Error('Invalid floating geometry');
 return {x:Math.max(0,Math.min(position.x,Math.max(0,host.width-panel.width))),y:Math.max(0,Math.min(position.y,Math.max(0,host.height-panel.height)))};
}
export function temporalWindow(count:number,index:number,span:number){
 if(![count,index,span].every(Number.isFinite))throw new Error('Invalid temporal window');
 count=Math.max(0,Math.floor(count));if(count<2)return {start:0,end:0};
 span=Math.max(2,Math.min(count,Math.floor(span)));index=Math.max(0,Math.min(count-1,Math.floor(index)));
 const start=Math.max(0,Math.min(count-span,index-Math.floor(span/2)));return {start,end:start+span-1};
}
export function resizeByKey(axis:keyof PanelSizes,key:string,current:number,shift=false){
 const min=axis==='left'?180:axis==='right'?240:100,max=axis==='left'?400:axis==='right'?420:300;
 const increase=axis==='dock'?'ArrowUp':axis==='right'?'ArrowLeft':'ArrowRight';
 const decrease=axis==='dock'?'ArrowDown':axis==='right'?'ArrowRight':'ArrowLeft';
 if(![increase,decrease,'Home','End'].includes(key))return undefined;
 const value=key==='Home'?min:key==='End'?max:current+(key===increase?1:-1)*(shift?16:4);
 return Math.max(min,Math.min(max,value));
}
export function visibleTask(value:unknown):Task {
 return TASKS.includes(value as Task)?value as Task:'map';
}
export function eventStatus(action:string,savedAt:string){
 const saving=['layer','series_visibility','series_style','series_palette','series_presentation','save','undo','redo','profile','basemap'];
 if(saving.includes(action))return 'Guardando…';
 if(['open','import','timelapse','navigate'].includes(action))return 'Abriendo…';
 return 'Guardado · '+savedAt;
}
export function panelSizes(width:number,preferred:PanelSizes,closed:{left?:boolean;right?:boolean}={}){
 if(!Number.isFinite(width)||width<0||!Object.values(preferred).every(Number.isFinite))throw new Error('Invalid panel geometry');
 const clamp=(n:number,min:number,max:number)=>Math.min(max,Math.max(min,n));
 const overlay=width<=760;
 let left=clamp(preferred.left,180,400),right=clamp(preferred.right,240,420);
 if(overlay){left=Math.min(width,left);right=Math.min(width,right)}
 else if(!closed.left&&!closed.right){
  const budget=width-260-12;
  left=Math.min(left,budget-240);right=Math.min(right,budget-left);
 }
 return {left,right,dock:clamp(preferred.dock,100,300),overlay};
}
