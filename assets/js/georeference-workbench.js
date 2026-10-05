import {auditGeoreference,syntheticExample} from './georeference-audit.js';
const el=id=>document.getElementById(id), say=(es,en)=>document.documentElement.lang==='en'?en:es;
const messages={
  format:['JSON incompatible: versión 1 y entre 3 y 200 puntos.','Unsupported JSON: version 1 and 3–200 points required.'],
  crs:['Solo WGS 84 / UTM 17S o 18S: EPSG:32717 o EPSG:32718. No se reproyectan coordenadas.','Only WGS 84 / UTM 17S or 18S: EPSG:32717 or EPSG:32718. Coordinates are not reprojected.'],
  raster:['Revisa dimensiones de imagen y SHA-256 opcional.','Check image dimensions and optional SHA-256.'],
  metadata:['Completa título, fuente y condiciones de uso.','Provide title, source and usage terms.'],
  pixels:['Convención requerida: center-zero-based-y-down.','Required convention: center-zero-based-y-down.'],
  points:['Cada punto necesita ID único y rol control o check.','Each point needs a unique ID and control or check role.'],
  numbers:['Las coordenadas deben ser números finitos, no texto.','Coordinates must be finite numbers, not text.'],
  bounds:['Hay puntos fuera de las dimensiones de la imagen.','Some points are outside the image dimensions.'],
  coordinates:['Coordenadas fuera del rango UTM admitido. No introduzcas grados.','Coordinates outside the supported UTM range. Do not enter degrees.'],
  duplicate:['Hay posiciones repetidas. Un punto de ajuste no puede reutilizarse como comprobación.','Repeated positions. A fitting point cannot be reused as a check point.'],
  controls:['Se requieren al menos tres puntos de ajuste.','At least three fitting points are required.'],
  collinear:['Puntos de ajuste alineados o casi alineados: no permiten un ajuste estable.','Fitting points are collinear or nearly collinear: no stable fit is possible.'],
  singular:['La transformación colapsa el plano; revisa las coordenadas de destino.','The transformation collapses the plane; check target coordinates.'],
  file:['No se pudo leer el JSON, o supera 256 KB.','Could not read JSON, or it exceeds 256 KB.'],
  'not-certified':['Un error pequeño no certifica precisión cartográfica ni validez geológica.','Small errors do not certify cartographic accuracy or geological validity.'],
  'independence-not-verified':['Los roles los declara quien carga los datos. La herramienta no verifica la independencia ni la calidad de la referencia.','Roles are user-declared. The tool does not verify independence or reference quality.'],
  'minimal-fit':['Solo tres puntos de ajuste: pueden dar residuo cero sin detectar errores.','Only three fitting points: zero residual can hide errors.'],
  'no-checks':['Sin puntos de comprobación: el error fuera del ajuste no está evaluado.','No check points: out-of-fit error is not evaluated.'],
  'few-checks':['Menos de tres comprobaciones: diagnóstico muy limitado, no una prueba de exactitud.','Fewer than three checks: a very limited diagnostic, not an accuracy test.'],
  'limited-spread':['Los controles cubren menos de la mitad de algún eje de la imagen. Revisa la distribución; este aviso no mide cobertura completa.','Controls span less than half of an image axis. Review distribution; this warning does not measure full coverage.'],
  'unbound-image':['No hay SHA-256 de la imagen: el informe no queda vinculado a un archivo concreto.','No image SHA-256: the report is not bound to a specific file.']
};
let report=null,errorCode=null,revision=0;
const message=code=>say(...(messages[code]||messages.file));
function reset(){report=null;errorCode=null;el('audit-results').hidden=true;el('audit-export').disabled=true;el('audit-status').textContent='';}
function render(){
  if(errorCode){el('audit-status').textContent=message(errorCode);return;}
  if(!report)return;
  el('audit-status').textContent=report.synthetic?say('EJEMPLO SINTÉTICO · no representa una hoja real.','SYNTHETIC EXAMPLE · not a real map sheet.'):say('Diagnóstico calculado · no es una certificación.','Diagnostic computed · not a certification.');
  el('audit-results').hidden=false;el('audit-export').disabled=false;
  const metric=group=>group.rmse_m===null?say('No evaluado','Not evaluated'):`${group.rmse_m.toFixed(2)} m · n=${group.count}`;
  el('audit-fit').textContent=metric(report.controls);el('audit-check').textContent=metric(report.checks);
  el('audit-warnings').replaceChildren();
  for(const code of report.warnings){const li=document.createElement('li');li.textContent=message(code);el('audit-warnings').append(li);}
  el('audit-rows').replaceChildren();
  for(const row of report.points){const tr=document.createElement('tr');for(const value of [row.id,row.role==='control'?say('Ajuste','Fit'):say('Comprobación','Check'),row.dx_m.toFixed(2),row.dy_m.toFixed(2),row.error_m.toFixed(2)]) {const td=document.createElement('td');td.textContent=value;tr.append(td);}el('audit-rows').append(tr);}
}
function run(){reset();try{if(new TextEncoder().encode(el('audit-json').value).length>262144)throw new Error('file');report=auditGeoreference(JSON.parse(el('audit-json').value));}catch(e){errorCode=e.code||'file';}render();if(report){el('audit-results').focus({preventScroll:true});el('audit-results').scrollIntoView({block:'start'});}}
function save(value,name){const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
el('audit-demo').addEventListener('click',()=>{revision++;el('audit-file').value='';el('audit-json').value=JSON.stringify(syntheticExample(),null,2);run();});
el('audit-run').addEventListener('click',run);
el('audit-template').addEventListener('click',()=>save(syntheticExample(),'ecuador-vivo-synthetic-gcp-example.json'));
el('audit-export').addEventListener('click',()=>{if(report)save(report,'ecuador-vivo-georeference-diagnostic.json');});
el('audit-json').addEventListener('input',()=>{revision++;reset();});
el('audit-clear').addEventListener('click',()=>{revision++;el('audit-json').value='';el('audit-file').value='';reset();});
el('audit-file').addEventListener('change',async()=>{
  const token=++revision,file=el('audit-file').files[0];reset();el('audit-json').value='';if(!file)return;
  try {if(file.size>262144)throw new Error('size');const value=await file.text();if(token!==revision)return;el('audit-json').value=value;run();}
  catch {if(token===revision){errorCode='file';render();}}
});
window.addEventListener('portal:language',render);
