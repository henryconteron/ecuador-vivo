// Navigation changes visibility only: it never changes layer checkboxes or data.
const say=(es,en)=>document.documentElement.lang==='en'?en:es;
const sidebar=document.querySelector('.sidebar');
if(sidebar){
  const groups={layers:'.layer-panel',catalog:'.summary-grid,.filters,.catalog',sources:'.spatial-context,.source-network',guide:'.intro,.method-note'};
  const labels={layers:['Capas','Layers'],catalog:['Catálogo de fallas','Fault catalog'],sources:['Fuentes y aportes','Sources & contributions'],guide:['Guía','Guide']};
  const nav=document.createElement('nav');nav.className='workspace-nav';nav.setAttribute('aria-label','Panel / Panel');let active='layers';
  const buttons={};for(const id of Object.keys(groups)){const b=document.createElement('button');b.type='button';buttons[id]=b;b.addEventListener('click',()=>select(id));nav.append(b);}
  sidebar.querySelector('.system-explorer').after(nav);
  const note=document.createElement('p');note.className='workspace-empty';note.hidden=true;nav.after(note);
  function select(id){active=id;for(const [key,selector] of Object.entries(groups)){sidebar.querySelectorAll(selector).forEach(node=>node.toggleAttribute('data-workspace-hidden',key!==id));buttons[key].setAttribute('aria-pressed',String(key===id));}
    note.hidden=id!=='catalog'||sidebar.dataset.activeSystem==='earth';note.textContent=say('El catálogo de fallas corresponde a Tierra. Selecciona Tierra para consultarlo.','The fault catalog belongs to Earth. Select Earth to browse it.');
  }
  function update(){for(const id of Object.keys(groups))buttons[id].textContent=say(...labels[id]);select(active);}
  new MutationObserver(()=>{if(active==='catalog'&&sidebar.dataset.activeSystem!=='earth')select('layers');else update();}).observe(sidebar,{attributes:true,attributeFilter:['data-active-system']});
  window.addEventListener('atlas:languagechange',update);window.addEventListener('portal:language',update);update();
}
const learn=document.querySelector('[data-story-panel]');
if(learn){
  const bar=document.createElement('nav');bar.className='chapter-jump content-width';const label=document.createElement('label'),select=document.createElement('select');select.id='chapter-jump';label.htmlFor=select.id;bar.append(label,select);document.querySelector('.stories-cover').after(bar);
  const headings=[...document.querySelectorAll('[data-story-panel] h2')];headings.forEach((h,i)=>{if(!h.id)h.id='learning-chapter-'+i;});
  function update(){label.textContent=say('Ir directamente a un capítulo','Jump directly to a chapter');const previous=select.value;select.replaceChildren();const first=document.createElement('option');first.value='';first.textContent=say('Elige un capítulo…','Choose a chapter…');select.append(first);for(const h of headings){const option=document.createElement('option');option.value=h.id;option.textContent=h.textContent;select.append(option);}if([...select.options].some(o=>o.value===previous))select.value=previous;}
  select.addEventListener('change',()=>{if(!select.value)return;location.hash=select.value;const target=document.getElementById(select.value);target.tabIndex=-1;target.focus({preventScroll:true});});
  window.addEventListener('atlas:languagechange',update);window.addEventListener('portal:language',update);update();
}
