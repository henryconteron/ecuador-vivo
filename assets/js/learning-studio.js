import {lessons} from './learning-lessons.js';
import {waterBudget,airParcel} from './learning-science.js';
const el=id=>document.getElementById(id),ids=Object.keys(lessons),say=(es,en)=>document.documentElement.lang==='en'?en:es;
const text=value=>value[document.documentElement.lang==='en'?'en':'es'];
const params=new URLSearchParams(location.search);let current=ids.includes(params.get('story'))?params.get('story'):'earth';
const textOnly=params.get('view')==='text';
const states=Object.fromEntries(ids.map(id=>[id,{progress:0,fault:'normal',impervious:0,wet:false,moist:true}]));
let saved={};try{saved=JSON.parse(localStorage.getItem('ev-learning-v1')||'{}')||{};}catch{/* Private browsing remains usable. */}
const completed=new Set(Array.isArray(saved.completed)?saved.completed.filter(id=>ids.includes(id)):[]),explored=new Set(completed),answers={};
el('learning-note').value=typeof saved.note==='string'?saved.note.slice(0,4000):'';
let world=null,worldFailed=false,playing=false,raf=0,lastTime=0,drag=null,view={yaw:.65,pitch:.5,distance:8.4};
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
function persist(){try{localStorage.setItem('ev-learning-v1',JSON.stringify({completed:[...completed],note:el('learning-note').value}));}catch{el('notebook-status').textContent=say('El navegador no permite guardar. Puedes descargar tu cuaderno.','This browser cannot save progress. You can download your notebook.');}}
function progress(){el('journey-count').textContent=`${completed.size} / 3`;el('journey-progress').value=completed.size;}
function playbackLabel(){el('play-process').textContent=playing?say('Ⅱ Pausar','Ⅱ Pause'):say('▶ Reproducir','▶ Play');el('play-process').disabled=reduced.matches;el('play-process').title=reduced.matches?say('Movimiento reducido: usa Antes, Durante y Después.','Reduced motion: use Before, During and After.') : '';}
function stop(){playing=false;cancelAnimationFrame(raf);playbackLabel();}
function renderFeedback(){const i=answers[current];el('challenge-feedback').textContent=i===undefined?'':text(lessons[current].feedback[i]);el('next-lesson').hidden=i!==lessons[current].correct||current==='sky';el('challenge-answers').querySelectorAll('button').forEach((b,n)=>{b.disabled=!explored.has(current);b.setAttribute('aria-pressed',String(i===n));});el('challenge-gate').hidden=explored.has(current);}
function updateExperiment(){
  const s=states[current],lesson=lessons[current];el('experiment-time').value=s.progress;el('time-value').textContent=`${Math.round(s.progress)} %`;
  const beat=text(lesson.beats[s.progress<25?0:s.progress<75?1:2]);if(el('observation').textContent!==beat)el('observation').textContent=beat;
  if(s.progress>=70&&!explored.has(current)){explored.add(current);renderFeedback();}
  let caption='';
  if(current==='earth')caption=s.fault==='strike'?say('Franja superficial blanca: observa su separación lateral.','White surface marker: watch its sideways offset.'):say('Bloque móvil = techo · franja blanca = capa guía.','Moving block = hanging wall · white band = marker layer.');
  if(current==='water'){const b=waterBudget(s.impervious/100,s.wet);el('runoff-value').textContent=String(b.runoff);el('infiltration-value').textContent=String(b.infiltration);el('impervious-value').textContent=`${s.impervious} %`;caption=say('Azul: escorrentía · turquesa: infiltración · gris: suelo sellado.','Blue: runoff · turquoise: infiltration · gray: sealed ground.');}
  if(current==='sky')caption=airParcel(s.progress/100,s.moist).condensed?say('Condensación representada. Nube ≠ lluvia asegurada.','Condensation shown. Cloud ≠ guaranteed rain.'):say('Parcela aún sin condensación en este recorrido.','Parcel not yet condensed along this path.');
  el('world-caption').textContent=caption;
  world?.set(current,s);
}
function render(){
  const lesson=lessons[current];
  const state=states[current];el('fault-kind').value=state.fault;el('impervious').value=state.impervious;el('soil-wet').value=state.wet?'wet':'dry';el('air-moisture').value=state.moist?'moist':'dry';
  for(const field of ['tag','title','hook','goal','task','why','limit'])el('lesson-'+field).textContent=text(lesson[field]);
  el('guide-number').textContent=lesson.number;el('challenge-title').textContent=text(lesson.question);
  el('lesson-source').textContent=lesson.source.title;el('lesson-source').href=lesson.source.url;
  el('lesson-atlas').href=`explore.html?system=${lesson.atlas}&lang=${document.documentElement.lang}`;
  const [reading,hash]=lesson.reading.split('#');el('lesson-reading').href=`${reading}?lang=${document.documentElement.lang}#${hash}`;
  document.querySelectorAll('[data-lesson]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.lesson===current)));
  document.querySelectorAll('[data-controls]').forEach(e=>e.hidden=e.dataset.controls!==current);el('water-balance').hidden=current!=='water';
  el('challenge-answers').replaceChildren();lesson.answers.forEach((answer,i)=>{const b=document.createElement('button');b.type='button';b.textContent=text(answer);b.addEventListener('click',()=>{answers[current]=i;if(i===lesson.correct){completed.add(current);persist();progress();}renderFeedback();});el('challenge-answers').append(b);});
  canvas.hidden=textOnly;canvas.parentElement.dataset.textOnly=String(textOnly);el('render-status').hidden=!!world;el('render-status').textContent=textOnly?say('Modo sin 3D: experimenta con los controles y lee los cambios debajo. No se carga el motor gráfico.','Text mode: experiment with the controls and read the changes below. The graphics engine is not loaded.'):worldFailed?say('El 3D no está disponible. Los controles, descripciones, balance y retos siguen funcionando. Prueba recargar en un navegador con WebGL2.','3D is unavailable. Controls, descriptions, balance and challenges still work. Try reloading in a WebGL2 browser.'):say('Preparando el modelo 3D…','Preparing the 3D model…');
  el('text-mode-link').href=`learn.html?story=${current}&lang=${document.documentElement.lang}${textOnly?'':'&view=text'}#studio`;el('text-mode-link').textContent=textOnly?say('Activar modelos 3D','Enable 3D models'):say('Usar modo ligero sin 3D','Use lightweight text mode');
  renderFeedback();progress();playbackLabel();updateExperiment();
}
function select(id,navigate=true){if(!ids.includes(id))return;stop();current=id;render();if(navigate){const url=new URL(location.href);url.searchParams.set('story',id);url.hash='studio';history.pushState(null,'',url);el('lesson-title').focus({preventScroll:true});}}
document.querySelectorAll('[data-lesson]').forEach(b=>b.addEventListener('click',()=>select(b.dataset.lesson)));
window.addEventListener('popstate',()=>{const id=new URLSearchParams(location.search).get('story');select(ids.includes(id)?id:'earth',false);});
el('experiment-time').addEventListener('input',e=>{stop();states[current].progress=Number(e.target.value);updateExperiment();});
document.querySelectorAll('[data-step]').forEach(b=>b.addEventListener('click',()=>{stop();states[current].progress=Number(b.dataset.step);updateExperiment();}));
for(const [id,key,convert] of [['fault-kind','fault',v=>v],['impervious','impervious',Number],['soil-wet','wet',v=>v==='wet'],['air-moisture','moist',v=>v==='moist']])el(id).addEventListener('input',e=>{states[current][key]=convert(e.target.value);updateExperiment();});
el('reset-experiment').addEventListener('click',()=>{stop();states[current]={progress:0,fault:'normal',impervious:0,wet:false,moist:true};el('fault-kind').value='normal';el('impervious').value='0';el('soil-wet').value='dry';el('air-moisture').value='moist';updateExperiment();});
el('play-process').addEventListener('click',()=>{if(playing){stop();return;}if(reduced.matches)return;if(states[current].progress>=100)states[current].progress=0;playing=true;lastTime=performance.now();playbackLabel();const tick=now=>{if(!playing)return;states[current].progress=Math.min(100,states[current].progress+(now-lastTime)/65);lastTime=now;updateExperiment();if(states[current].progress>=100)stop();else raf=requestAnimationFrame(tick);};raf=requestAnimationFrame(tick);});
document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});reduced.addEventListener('change',stop);
el('next-lesson').addEventListener('click',()=>{select(ids[ids.indexOf(current)+1]);el('studio').scrollIntoView({behavior:'auto',block:'start'});});
el('learning-note').addEventListener('input',persist);
el('clear-progress').addEventListener('click',()=>{completed.clear();explored.clear();ids.forEach(id=>{delete answers[id];states[id].progress=0;});stop();persist();render();});
el('download-notebook').addEventListener('click',()=>{const lines=['# Ecuador Vivo · '+say('Mi cuaderno','My notebook'),''];for(const id of ids){const l=lessons[id];lines.push(`## ${text(l.title)}`,`${say('Reto resuelto','Challenge solved')}: ${completed.has(id)?say('sí','yes'):say('todavía no','not yet')}`,text(l.limit),`${l.source.title}: ${l.source.url}`,'');}lines.push('## '+say('Mi observación','My observation'),el('learning-note').value);const url=URL.createObjectURL(new Blob([lines.join('\n\n')],{type:'text/markdown;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download='ecuador-vivo-mi-cuaderno.md';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);el('notebook-status').textContent=say('Cuaderno preparado para descarga; no se envió a ningún servidor.','Notebook prepared for download; nothing was sent to a server.');});
function setView(){world?.view(view.yaw,view.pitch,view.distance);}
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{view.yaw=b.dataset.view==='oblique'?.65:0;view.pitch=b.dataset.view==='top'?1.46:b.dataset.view==='front'?.08:.5;setView();}));
for(const [id,delta] of [['zoom-in',-.6],['zoom-out',.6]])el(id).addEventListener('click',()=>{view.distance=Math.max(5.5,Math.min(12,view.distance+delta));setView();});
const canvas=el('learning-canvas');canvas.addEventListener('pointerdown',e=>{if(e.button!==0)return;drag={x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);});canvas.addEventListener('pointermove',e=>{if(!drag)return;view.yaw-=(e.clientX-drag.x)*.007;view.pitch=Math.max(.08,Math.min(1.46,view.pitch+(e.clientY-drag.y)*.006));drag={x:e.clientX,y:e.clientY};setView();});for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,()=>drag=null);
canvas.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key))return;e.preventDefault();view.yaw+=e.key==='ArrowLeft'?-.12:e.key==='ArrowRight'?.12:0;view.pitch=Math.max(.08,Math.min(1.46,view.pitch+(e.key==='ArrowUp'?.12:e.key==='ArrowDown'?-.12:0)));setView();});
canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();stop();world=null;worldFailed=true;render();});
new ResizeObserver(()=>world?.paint()).observe(canvas);window.addEventListener('portal:language',render);
render();if(!textOnly)import('./learning-world.js').then(module=>{world=module.createLearningWorld(canvas);render();}).catch(()=>{worldFailed=true;render();});
