/** Public catalogs are curated manifests; live providers never overwrite them. */
export const TOPICS = {earth:{es:"Tierra",en:"Earth"},water:{es:"Agua",en:"Water"},sky:{es:"Cielo",en:"Sky"},life:{es:"Vida",en:"Life"},risk:{es:"Riesgo",en:"Risk"}};
export const ACCESS = {file:{es:"Archivo de datos",en:"Data file"},derivative:{es:"Derivados y metadatos",en:"Derivatives and metadata"},service:{es:"Servicio externo",en:"External service"}};
export const localize = (value, lang = "es") => typeof value === "string" ? value : value?.[lang === "en" ? "en" : "es"] ?? "";
export const normalizeSearch = (value) => String(value ?? "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
export function filterRecords(records, {query = "", topic = "all", territory = "all", access = "all"} = {}) {
  const tokens = normalizeSearch(query).trim().split(/\s+/).filter(Boolean);
  return records.filter((record) => {
    const text = normalizeSearch(JSON.stringify([record.title, record.summary, record.publisher, record.authors, record.venue, record.scope, record.territories, record.topics.map((key) => TOPICS[key]), record.year, record.format, record.doi]));
    return (topic === "all" || record.topics.includes(topic)) && (territory === "all" || record.territories.includes(territory)) && (access === "all" || record.access === access) && tokens.every((token) => text.includes(token));
  });
}
export function safeHref(value) {
  if (typeof value !== "string" || !value || /[\u0000-\u0020\\]/.test(value)) return null;
  if (/^https:\/\//i.test(value)) { try { const url = new URL(value); return !url.username && !url.password ? value : null; } catch { return null; } }
  if (/^[a-z][a-z0-9+.-]*:/i.test(value) || value.startsWith("/") || value.split(/[/?#]/).includes("..")) return null;
  return value;
}
export function recordLinks(record) {
  return [record.source_url, record.url, record.viewer, record.method, record.reading, ...(record.files ?? []).map((file) => file.href)].filter(Boolean);
}

if (typeof document !== "undefined" && document.querySelector("[data-catalog-mode]")) bootCatalog();

async function bootCatalog() {
  const mode = document.body.dataset.catalogMode;
  const library = mode === "library";
  const dataPath = library ? "data/library/studies.json" : "data/catalog/datasets.json";
  const results = document.querySelector("#catalog-results");
  const detail = document.querySelector("#catalog-detail");
  const count = document.querySelector("#catalog-count");
  const search = document.querySelector("#catalog-search");
  const topic = document.querySelector("#topic-filter");
  const territory = document.querySelector("#territory-filter");
  const access = document.querySelector("#access-filter");
  let records = [];
  let selected = decodeHash();
  let lang = getLanguage();
  let citation = "";
  const say = (es, en) => lang === "en" ? en : es;
  const value = (text) => localize(text, lang);
  function getLanguage() { return (window.portalLanguage?.() ?? new URLSearchParams(location.search).get("lang") ?? document.documentElement.lang) === "en" ? "en" : "es"; }
  function decodeHash() { try { return decodeURIComponent(location.hash.slice(1)); } catch { return ""; } }
  const params = new URLSearchParams(location.search);
  search.value = params.get("q") ?? "";
  for (const [element, key] of [[topic,"tema"],[territory,"territorio"],[access,"acceso"]]) {
    if (element && [...element.options].some((option) => option.value === params.get(key))) element.value = params.get(key);
  }
  function node(tag, text, className) { const element = document.createElement(tag); if (text !== undefined) element.textContent = text; if (className) element.className = className; return element; }
  function link(href, label, className) {
    const element = node("a", label, className);
    const validated = safeHref(href);
    if (!validated) return node("span", label);
    if (validated.startsWith("https://")) { element.href = validated; element.target = "_blank"; element.rel = "noopener noreferrer"; }
    else { const url = new URL(validated, location.href); if (/\.html$/.test(url.pathname)) { url.searchParams.set("lang", lang); element.dataset.keepLang = ""; } element.href = url.href; }
    return element;
  }
  function synchronizeUrl() {
    const url = new URL(location.href);
    for (const [key,current] of [["q",search.value],["tema",topic.value],["territorio",territory.value],["acceso",access?.value ?? "all"]]) { if (!current || current === "all") url.searchParams.delete(key); else url.searchParams.set(key,current); }
    url.hash = selected;
    history.replaceState(null,"",url);
  }
  function fieldList(entries) {
    const dl = node("dl");
    for (const [label, content] of entries) { const row = node("div"); row.append(node("dt",label),node("dd",value(content))); dl.append(row); }
    return dl;
  }
  function showDetail(record) {
    detail.replaceChildren();
    if (!record) return;
    if (record.image && safeHref(record.image)) {
      const figure = node("figure"); const img = node("img"); img.src = record.image; img.alt = value(record.image_caption); img.loading = "lazy"; figure.append(img,node("figcaption",value(record.image_caption))); detail.append(figure);
    }
    detail.append(node("p",library ? `${value(record.type)} · ${record.year}` : `${record.publisher} · ${record.format}`,"eyebrow"));
    const heading = node("h2",value(record.title)); heading.id = "catalog-detail-title"; detail.setAttribute("aria-labelledby",heading.id); detail.append(heading,node("p",value(record.summary)));
    if (library) {
      detail.append(node("p", record.access === "open" ? say("Acceso abierto documentado · ", "Documented open access · ") + record.license : say("Acceso: consultar la fuente; esta ficha aún no documenta una licencia abierta.", "Access: consult the source; this record does not yet document an open license."), "catalog-warning"));
      detail.append(fieldList([[say("Autoría","Authors"),record.authors],[say("Publicación","Publication"),record.venue],[say("Territorio","Territory"),record.scope]]));
      detail.append(link(record.url,say("Leer la fuente original ↗","Read the original source ↗"),"button"));
      detail.append(node("h3",say("Qué respalda esta ficha","What this record supports")),node("p",value(record.verification),"catalog-warning"));
      detail.append(node("p",`${say("Comprobación documental","Documentary check")}: ${record.checked}`,"catalog-citation"));
      detail.append(link(record.reading,say("Dónde se utiliza en Ecuador Vivo →","Where Ecuador Vivo uses it →")));
    } else {
      detail.append(fieldList([[say("Acceso","Access"),ACCESS[record.access]],[say("Periodo","Period"),record.period],[say("Resolución","Resolution"),record.resolution],[say("Cobertura","Coverage"),record.scope],[say("Condiciones","Terms"),record.license]]));
      detail.append(link(record.viewer,say("Explorar en el visor →","Explore in the viewer →"),"button"));
      if (record.access === "service") detail.append(node("p",say("Servicio externo: el repositorio no conserva ni ofrece una descarga del conjunto numérico completo.","External service: this repository does not archive or offer a download of the complete numerical dataset."),"catalog-warning"));
      else {
        detail.append(node("h3",say("Archivos disponibles","Available files")));
        const files = node("ul",undefined,"catalog-files");
        for (const file of record.files) { const item = node("li"); const a = link(file.href,value(file.label)); a.setAttribute("download",""); item.append(a,node("small",file.kind === "metadata" ? say("Metadatos y procedencia; no confundir con observaciones.","Metadata and provenance; not the observations themselves.") : file.kind === "image" ? say("Imagen de visualización; no raster científico numérico.","Visualization image; not a numerical scientific raster.") : say("Datos; revisar formato, condiciones y método.","Data; check format, terms and method."))); files.append(item); }
        detail.append(files);
      }
      if (record.method) { const p = node("p"); p.append(link(record.method,say("Método y documentación ↗","Method and documentation ↗"))); detail.append(p); }
      const sourceParagraph = node("p"); sourceParagraph.append(link(record.source_url,say("Fuente del proveedor ↗","Provider source ↗"))); detail.append(sourceParagraph);
    }
    detail.append(node("h3",say("Antes de interpretar","Before interpreting")),node("p",value(record.limits),"catalog-warning"));
    if (record.related?.length) {
      detail.append(node("h3",library ? say("Datos relacionados","Related data") : say("Estudios relacionados","Related studies")));
      const ul = node("ul",undefined,"catalog-files");
      for (const id of record.related) { const li = node("li"); li.append(link(`${library?"datos":"biblioteca"}.html#${encodeURIComponent(id)}`,relatedLabels.get(id)?.[lang] ?? id)); ul.append(li); }
      detail.append(ul);
    }
    const citations = node("details"); citations.append(node("summary",say("Cita y procedencia","Citation and provenance")),node("p",record.citation,"catalog-citation"));
    const copy = node("button",say("Copiar cita","Copy citation"),"catalog-copy"); copy.type = "button";
    const status = node("p","","catalog-copy-status"); status.setAttribute("role","status"); citation = record.citation;
    copy.addEventListener("click",async()=>{ try { if (!navigator.clipboard?.writeText) throw new Error("Clipboard unavailable"); await navigator.clipboard.writeText(record.citation); status.textContent = say("Cita copiada.","Citation copied."); } catch { status.textContent = say("No se pudo copiar automáticamente. Selecciona el texto de la cita de arriba.","Could not copy automatically. Select the citation text above."); } });
    citations.append(copy,status); detail.append(citations);
  }
  const relatedLabels = new Map();
  function render() {
    search.placeholder = say("Napo, fallas, ríos…","Napo, faults, rivers…");
    document.title = `${library?say("Biblioteca de Ecuador","Ecuador Library"):say("Datos","Data")} · Ecuador Vivo`;
    const filtered = filterRecords(records,{query:search.value,topic:topic.value,territory:territory.value,access:access?.value ?? "all"});
    if (!filtered.some((record)=>record.id===selected)) selected = filtered[0]?.id ?? "";
    count.textContent = `${filtered.length} ${say("de","of")} ${records.length} ${library?say("estudios","studies"):say("conjuntos y servicios","datasets and services")}`;
    results.replaceChildren();
    if (!filtered.length) results.append(node("p",say("No hay fichas para esta combinación. Prueba otro tema o limpia los filtros; la cobertura del catálogo todavía es parcial.","No records match this combination. Try another topic or clear the filters; catalog coverage is still partial."),"catalog-empty"));
    for (const [index,record] of filtered.entries()) {
      const button = node("button",undefined,"catalog-card"); button.type = "button"; button.setAttribute("aria-pressed",String(record.id===selected)); button.setAttribute("aria-controls","catalog-detail");
      if (record.image && safeHref(record.image)) { const img = node("img",undefined,"catalog-thumb"); img.src = record.image; img.alt = ""; img.loading = "lazy"; button.append(img); }
      else { const block = node("span",String(index+1).padStart(2,"0"),"catalog-thumb catalog-no-image"); block.setAttribute("aria-hidden","true"); block.append(node("small",library?String(record.year):record.format)); button.append(block); }
      const text = node("span",undefined,"catalog-card-copy"); text.append(node("span",value(record.title),"catalog-card-title"),node("span",library?`${record.authors} · ${record.year}`:record.publisher,"catalog-card-source"));
      const tags = node("span",undefined,"catalog-tags"); for(const key of record.topics)tags.append(node("span",value(TOPICS[key]),`catalog-tag catalog-tag-${key}`));
      tags.append(node("span",library?value(record.type):value(ACCESS[record.access]),"catalog-tag catalog-tag-access")); text.append(tags); button.append(text,node("span","›","catalog-arrow"));
      button.addEventListener("click",()=>{ selected=record.id; render(); synchronizeUrl(); const current=[...results.querySelectorAll("button")].find((el)=>el.getAttribute("aria-pressed")==="true"); if (matchMedia("(max-width: 580px)").matches) { detail.focus({preventScroll:true}); detail.scrollIntoView({behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"instant":"smooth",block:"start"}); } else current?.focus({preventScroll:true}); });
      results.append(button);
    }
    showDetail(filtered.find((record)=>record.id===selected));
  }
  function filterChanged() { render(); synchronizeUrl(); }
  for(const el of [search,topic,territory,access].filter(Boolean)) el.addEventListener(el===search?"input":"change",filterChanged);
  document.querySelector("#catalog-reset").addEventListener("click",()=>{search.value="";topic.value="all";territory.value="all";if(access)access.value="all";filterChanged();search.focus();});
  window.addEventListener("portal:language",()=>{lang=getLanguage();render();});
  window.addEventListener("hashchange",()=>{const id=decodeHash();if(records.some(record=>record.id===id)){selected=id;search.value="";topic.value="all";territory.value="all";if(access)access.value="all";render();synchronizeUrl();}});
  try {
    const response = await fetch(dataPath); if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json(); if (!Array.isArray(payload.records)) throw new Error("Invalid catalog"); records=payload.records;
    try { const relatedResponse=await fetch(library?"data/catalog/datasets.json":"data/library/studies.json"); if(relatedResponse.ok){const related=await relatedResponse.json();for(const entry of related.records??[])relatedLabels.set(entry.id,typeof entry.title==="string"?{es:entry.title,en:entry.title}:entry.title);} } catch { /* Primary catalog remains usable if related labels are unavailable. */ }
    lang=getLanguage();render();
  } catch {
    count.textContent=""; results.replaceChildren(node("p",say("No se pudo cargar el catálogo. Recarga la página o consulta el archivo JSON directamente.","The catalog could not load. Reload the page or open the JSON file directly."),"catalog-error"),link(dataPath,say("Abrir catálogo JSON","Open JSON catalog")));
  }
}
