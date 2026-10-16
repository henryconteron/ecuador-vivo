import {filterTools,type ProcessingTool} from './workbench-model';
/** Discovery only. Execution remains in validated Python forms. */
export function toolbox(adapter:any,event:(action:string,extra:any)=>void){
 const root=adapter.root as HTMLElement,q=(id:string)=>root.querySelector<HTMLElement>('#'+id)!;
 const search=q('sig-toolbox-search') as HTMLInputElement,kind=q('sig-toolbox-kind') as HTMLSelectElement,list=q('sig-toolbox-list');
 const tools=adapter.data.workspace.tools as ProcessingTool[]??[];
 const key=JSON.stringify([tools,search.value,kind.value]);
 const paint=()=>{
  list.replaceChildren();const matches=filterTools(adapter.data.workspace.tools??[],search.value,kind.value);
  q('sig-toolbox-count').textContent=matches.length+(matches.length===1?' herramienta':' herramientas');
  const groups=new Map<string,ProcessingTool[]>();for(const tool of matches){if(!groups.has(tool.group))groups.set(tool.group,[]);groups.get(tool.group)!.push(tool)}
  for(const [name,items] of groups){
   const group=document.createElement('section'),title=document.createElement('h3');title.textContent=name;group.append(title);
   for(const tool of items){
    const row=document.createElement('div'),button=document.createElement('button'),summary=document.createElement('small');
    row.className='sig-processing-tool';button.type='button';button.textContent=tool.label;button.disabled=!tool.available;
    summary.textContent=tool.available?tool.summary:tool.reason;summary.id='sig-tool-help-'+tool.id;
    button.setAttribute('aria-describedby',summary.id);button.title=summary.textContent;
    button.onclick=()=>{adapter.pausePlayback();q('sig-toolbox-close').click();event('operation',{operation:tool.id})};row.append(button,summary);group.append(row);
   }
   list.append(group);
  }
  if(!matches.length){const p=document.createElement('p');p.textContent='No hay herramientas con ese nombre. Prueba «contornos», «campo» o «ráster».';list.append(p)}
  list.dataset.key=JSON.stringify([adapter.data.workspace.tools,search.value,kind.value]);
 };
 search.oninput=paint;kind.onchange=paint;if(list.dataset.key!==key)paint();
}
