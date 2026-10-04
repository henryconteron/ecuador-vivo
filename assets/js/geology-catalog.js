import {validateLocalGeoJSON} from './map/local-data.js';

export const normalize = value => String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
export function selectGeology(features, {query = '', unit = '', status = ''} = {}) {
  return features.filter(({properties: p}) => (!unit || p.ENT_GEOL === unit) && (!status || p.ESTADO === status) &&
    normalize([p.ENT_GEOL,p.LITOLOGIA,p.LIT,p.NOMBRE,p.CD_IGM,p.OBJECTID].join(' ')).includes(normalize(query.trim())));
}
export function exportSelection(features, kind, manifest, filters) {
  return {type:'FeatureCollection', name:`ecuador-vivo-${kind}-selection`, metadata:{
    source:manifest.source, retrieved:manifest.retrieved, source_files:manifest.files,
    selection:'Whole source polygons matching attribute filters; not clipped.', filters,
    map_scale:manifest.map_scale, status:manifest.status, terms:manifest.terms,
  }, features};
}
export async function loadGeology(fetcher = fetch) {
  const response = await fetcher('data/geology/manifest.json');
  if (!response.ok) throw new Error('manifest');
  const manifest = await response.json(), collections = {};
  for (const id of ['tena-units','tena-sheets']) {
    const row = manifest.files?.find(f => f.id === id);
    if (!row || row.path !== `data/geology/${id}.geojson`) throw new Error('path');
    const reply = await fetcher(row.path); if (!reply.ok) throw new Error('snapshot');
    const bytes = await reply.arrayBuffer();
    const sha = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))].map(v=>v.toString(16).padStart(2,'0')).join('');
    if (bytes.byteLength !== row.bytes || sha !== row.sha256) throw new Error('integrity');
    const data = validateLocalGeoJSON(JSON.parse(new TextDecoder().decode(bytes)));
    if (data.features.length !== row.count) throw new Error('count');
    collections[id] = data;
  }
  return {manifest, collections};
}

if (typeof document !== 'undefined' && document.querySelector('#geology-catalog') && !window.L) {
  const status = document.getElementById('catalog-loading');
  status.removeAttribute('data-es'); status.removeAttribute('data-en');
  status.textContent = document.documentElement.lang === 'en'
    ? 'The map library could not load. Reload the page or download the source files below.'
    : 'No se pudo cargar el componente del mapa. Recarga la página o descarga los archivos de origen al pie.';
}
if (typeof document !== 'undefined' && document.querySelector('#geology-catalog') && window.L) {
  const el = id => document.getElementById(id), text = (es,en) => document.documentElement.lang === 'en' ? en : es;
  let bundle, results = [], selected;
  const map = window.L.map('catalog-map').setView([-1,-77.85],9);
  window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'}).addTo(map);
  const layer = window.L.geoJSON(null,{style:{color:'#447264',weight:2,fillOpacity:.25}, onEachFeature:(feature,item)=>item.on('click',()=>show(feature))}).addTo(map);
  const fields = ['OBJECTID','ENT_GEOL','LIT','LITOLOGIA','NOMBRE','CD_IGM','ESTADO','VERSIONES','AUTORES'];
  function show(feature) {
    selected = feature;
    el('record-title').textContent = feature.properties.ENT_GEOL || feature.properties.NOMBRE;
    el('record-fields').replaceChildren();
    for (const key of fields) {
      const value = feature.properties[key]; if (value === undefined || !String(value).trim()) continue;
      const dt=document.createElement('dt'),dd=document.createElement('dd'); dt.textContent=key;dd.textContent=String(value);el('record-fields').append(dt,dd);
    }
    layer.eachLayer(item=>item.setStyle({color:item.feature === feature?'#8d3b71':'#447264',weight:item.feature === feature?4:2}));
    el('record-note').textContent = text('Atributos originales del IIGE. Un límite dibujado no certifica su posición exacta en campo.','Original IIGE attributes. A mapped boundary does not certify its exact position in the field.');
  }
  function filters() { return {query:el('geology-search').value, unit:el('geology-kind').value==='units'?el('unit-filter').value:'',status:el('geology-kind').value==='sheets'?el('sheet-status').value:''}; }
  function render() {
    if (!bundle) return;
    const kind=el('geology-kind').value, sheets=kind==='sheets';
    el('unit-filter-wrap').hidden=sheets;el('sheet-status-wrap').hidden=!sheets;
    results=selectGeology(bundle.collections[`tena-${kind}`].features,filters());
    el('catalog-results').replaceChildren();layer.clearLayers();layer.addData({type:'FeatureCollection',features:results});
    el('catalog-count').textContent=text(`${results.length} de ${bundle.collections[`tena-${kind}`].features.length} registros`,`${results.length} of ${bundle.collections[`tena-${kind}`].features.length} records`);
    el('catalog-scale').textContent=sheets?text('Índice de hojas 1:100 000; no contiene la geología de las hojas.','1:100,000 sheet index; it does not contain the geology within the sheets.'):text('Escala de las unidades no documentada por el servicio.','Unit-map scale not documented by the service.');
    el('catalog-export').disabled=!results.length;el('catalog-fit').disabled=!results.length;
    for (const feature of results) {
      const li=document.createElement('li'), button=document.createElement('button');button.type='button';
      button.textContent=`${feature.properties.ENT_GEOL || feature.properties.NOMBRE} · ID ${feature.properties.OBJECTID}${sheets?' · '+feature.properties.ESTADO:''}`;
      button.addEventListener('click',()=>{show(feature);layer.eachLayer(item=>{if(item.feature===feature)map.fitBounds(item.getBounds(),{maxZoom:13});});});li.append(button);el('catalog-results').append(li);
    }
    if(results.length) show(results.find(f=>f===selected) || results[0]);
    else {el('record-title').textContent=text('Sin coincidencias','No matches');el('record-fields').replaceChildren();el('record-note').textContent='';}
  }
  for (const id of ['geology-kind','unit-filter','sheet-status']) el(id).addEventListener('change',render);
  el('geology-search').addEventListener('input',render);
  el('catalog-fit').addEventListener('click',()=>{if(results.length)map.fitBounds(layer.getBounds());});
  el('catalog-clear').addEventListener('click',()=>{el('geology-search').value='';el('unit-filter').value='';el('sheet-status').value='';render();});
  el('catalog-export').addEventListener('click',()=>{
    if(!bundle || !results.length)return;
    const a=document.createElement('a'), url=URL.createObjectURL(new Blob([JSON.stringify(exportSelection(results,el('geology-kind').value,bundle.manifest,filters()))],{type:'application/geo+json'}));
    a.href=url;a.download=`ecuador-vivo-${el('geology-kind').value}-selection.geojson`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
  window.addEventListener('portal:language',render);
  loadGeology().then(value=>{
    bundle=value;
    for(const [id,features,key] of [['unit-filter',value.collections['tena-units'].features,'ENT_GEOL'],['sheet-status',value.collections['tena-sheets'].features,'ESTADO']]) {
      [...new Set(features.map(f=>f.properties[key]))].sort().forEach(name=>{const option=document.createElement('option');option.value=option.textContent=name;el(id).append(option);});
    }
    el('catalog-loading').hidden=true;render();map.fitBounds(layer.getBounds());
  }).catch(()=>{el('catalog-loading').textContent=text('No se pudo comprobar la integridad de los datos. No se muestran resultados parciales.','Data integrity could not be verified. Partial results are not shown.');});
}
