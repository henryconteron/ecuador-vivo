const REVISION = '4cf5742c52c58fff5edddbff0c603e9e5fb92ddf';
const PUBLIC_ROOT = `https://raw.githubusercontent.com/henryconteron/ecuador-vivo/${REVISION}/`;
export const PRESETS = Object.freeze({
  geology:['data/geology/tena-units.geojson','data/geology/tena-sheets.geojson'],
  faults:['data/geojson/fallas.geojson'],
  empty:[],
});
// Only public, version-pinned files. Never forward private/local file paths or arbitrary URL parameters.
export function laboratoryURL(preset, language='es') {
  if (!Object.hasOwn(PRESETS,preset)) throw new Error('Unknown laboratory preset');
  const url = new URL('https://web.geolibre.app/');
  url.searchParams.set('lang',language==='en'?'en':'es');
  url.searchParams.set('theme','dark');url.searchParams.set('welcome','0');
  PRESETS[preset].forEach(path=>url.searchParams.append('data',PUBLIC_ROOT+path));
  return url.href;
}
if(typeof document!=='undefined' && document.querySelector('#lab-start')) {
  const el=id=>document.getElementById(id);let active=false;
  const say=(es,en)=>document.documentElement.lang==='en'?en:es;
  function sync(){
    document.body.classList.toggle('lab-idle',!active);el('lab-stop').disabled=!active;
    const url=laboratoryURL(el('lab-preset').value,document.documentElement.lang);el('lab-external').href=url;
    if(!active)el('lab-status').textContent=say('GeoLibre no se ha cargado. Elige un conjunto y pulsa Abrir.','GeoLibre has not been loaded. Choose a dataset and click Open.');
  }
  el('lab-start').addEventListener('click',()=>{
    if(active && !window.confirm(say('Recargar el laboratorio puede perder trabajo no guardado dentro de GeoLibre. ¿Continuar?','Reloading the laboratory may lose unsaved work inside GeoLibre. Continue?')))return;
    const frame=document.createElement('iframe');frame.className='lab-frame';frame.title=say('Laboratorio externo GeoLibre','External GeoLibre laboratory');
    frame.referrerPolicy='no-referrer';frame.allow='fullscreen';frame.src=laboratoryURL(el('lab-preset').value,document.documentElement.lang);
    el('lab-host').replaceChildren(frame);active=true;document.body.classList.remove('lab-idle');el('lab-stop').disabled=false;
    el('lab-status').textContent=say('Solicitando GeoLibre. Si no aparece el mapa, ábrelo en otra pestaña.','Requesting GeoLibre. If the map does not appear, open it in another tab.');
    frame.addEventListener('load',()=>{el('lab-status').textContent=say('Página externa cargada. Comprueba en GeoLibre que las capas terminaron de cargar; este aviso no certifica sus datos.','External page loaded. Check within GeoLibre that layers finished loading; this notice does not certify its data.');});
  });
  el('lab-stop').addEventListener('click',()=>{
    if(active && !window.confirm(say('¿Cerrar? Guarda primero tu proyecto en GeoLibre para no perder cambios.','Close? Save your GeoLibre project first to avoid losing changes.')))return;
    el('lab-host').replaceChildren();active=false;sync();
  });
  el('lab-preset').addEventListener('change',sync);window.addEventListener('portal:language',sync);sync();
}
