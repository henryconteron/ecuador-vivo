const state={posts:[],topic:"Todos",query:"",sort:"newest"};
const grid=document.querySelector("#feed-grid");
const template=document.querySelector("#card-template");
const filters=document.querySelector("#topic-filters");
const escapeText=(value)=>String(value??"").trim();

function labelForStatus(value){return value==="reviewed"?"Revisado":"Automático";}
function prettyDate(value){if(!value)return"Fecha no disponible";return new Intl.DateTimeFormat("es-EC",{year:"numeric",month:"short",day:"numeric",timeZone:"UTC"}).format(new Date(value+"T00:00:00Z"));}
function filteredPosts(){
  const q=state.query.toLocaleLowerCase("es");
  const items=state.posts.filter(post=>{
    const matchesTopic=state.topic==="Todos"||post.topic===state.topic;
    const haystack=[post.title,...(post.authors||[]),post.topic,post.venue,post.abstract_original,post.abstract,post.explanation_es,post.application].join(" ").toLocaleLowerCase("es");
    return matchesTopic&&(!q||haystack.includes(q));
  });
  return items.sort((a,b)=>state.sort==="title"?a.title.localeCompare(b.title,"es"):state.sort==="oldest"?a.published.localeCompare(b.published):b.published.localeCompare(a.published));
}
function render(){
  const posts=filteredPosts();grid.replaceChildren();
  posts.forEach(post=>{
    const node=template.content.cloneNode(true);
    node.querySelector(".topic").textContent=escapeText(post.topic);
    node.querySelector(".status").textContent=labelForStatus(post.status);
    node.querySelector("h3").textContent=escapeText(post.title);
    node.querySelector(".authors").textContent=(post.authors||[]).slice(0,4).join(", ")+(post.authors?.length>4?" et al.":"");
    const original=escapeText(post.abstract_original||post.abstract);
    node.querySelector(".abstract").textContent=original||"Abstract no disponible en los metadatos abiertos. Consulta la fuente original.";
    node.querySelector(".abstract-label").textContent=original?"ABSTRACT ORIGINAL · IDIOMA DE LA FUENTE":"ABSTRACT NO DISPONIBLE";
    const explanation=escapeText(post.explanation_es);const application=escapeText(post.application);
    const editorial=node.querySelector(".editorial");
    if(explanation||application){editorial.hidden=false;editorial.querySelector(".explanation").textContent=explanation||"Pendiente de revisión editorial.";editorial.querySelector(".application").textContent=application||"Pendiente de revisión editorial.";}
    node.querySelector(".date").textContent=prettyDate(post.published);
    node.querySelector(".venue").textContent=escapeText(post.venue)||"Fuente académica";
    const link=node.querySelector(".card-link");link.href=post.url;link.setAttribute("aria-label",`Abrir fuente: ${post.title}`);
    grid.append(node);
  });
  document.querySelector("#results-summary").textContent=`${posts.length} de ${state.posts.length} publicaciones`;
  document.querySelector("#empty-state").hidden=posts.length!==0;
}
function renderFilters(){
  const topics=["Todos",...new Set(state.posts.map(post=>post.topic).filter(Boolean))];
  topics.forEach(topic=>{
    const button=document.createElement("button");button.className="chip";button.textContent=topic;
    button.classList.toggle("active",topic===state.topic);
    button.addEventListener("click",()=>{state.topic=topic;[...filters.children].forEach(x=>x.classList.toggle("active",x.textContent===topic));render();});
    filters.append(button);
  });
}
async function init(){
  try{
    const response=await fetch("data/posts.json",{cache:"no-store"});if(!response.ok)throw new Error("No se pudo cargar el catálogo");
    const data=await response.json();state.posts=Array.isArray(data.posts)?data.posts:[];
    document.querySelector("#total-count").textContent=state.posts.length;
    document.querySelector("#last-update").textContent=`Actualizado: ${prettyDate(data.updated)}`;
    renderFilters();render();
  }catch(error){grid.innerHTML=`<p>No fue posible cargar el feed. <a href="https://github.com/henryconteron/feed-geologico/issues">Reportar problema</a>.</p>`;console.error(error);}
}
document.querySelector("#search").addEventListener("input",event=>{state.query=event.target.value.trim();render();});
document.querySelector("#sort").addEventListener("change",event=>{state.sort=event.target.value;render();});
document.querySelector("#clear-filters").addEventListener("click",()=>{state.topic="Todos";state.query="";document.querySelector("#search").value="";renderFilters();filters.replaceChildren();renderFilters();render();});
init();
