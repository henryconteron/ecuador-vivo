/* Preserved Studio evidence. No live queries, inferred statistics or interpolation. */
const ID = /^studio-[a-f0-9]{24}$/;
const MAP = /^maps\/\d{4}-[a-zA-Z0-9_-]{1,32}\.png$/;
const SHA = /^[a-f0-9]{64}$/;
export function assetPath(id, name) {
  if (!ID.test(id) || (name !== 'case.json' && name !== 'video.mp4' && !MAP.test(name))) throw new Error('Invalid evidence path');
  return `data/cases/studio/${id}/${name}`;
}
export function publicSourceURL(raw) {
  try {
    const url = new URL(raw);
    return url.protocol === 'https:' && !url.username && !url.password && !url.search && !url.hash ? url.href : null;
  } catch { return null; }
}
export function validateEvidence(caseData, id) {
  const c = caseData;
  if (c?.schema !== 'ecuador-vivo-evidence-v1' || c.id !== id || !ID.test(id) || c.status !== 'reviewed' || c.video !== 'video.mp4') throw new Error('Unreviewed case');
  if (!Array.isArray(c.maps) || !Array.isArray(c.observation_dates) || !c.maps.length || c.maps.length > 1000 || c.maps.length !== c.observation_dates.length) throw new Error('Incomplete calendar');
  if (new Set(c.observation_dates).size !== c.observation_dates.length) throw new Error('Duplicate date');
  for (let i = 0; i < c.maps.length; i++) {
    const map = c.maps[i], date = c.observation_dates[i];
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || map.date !== date || (i && date <= c.observation_dates[i - 1])) throw new Error('Different map date');
    if (!map.channels || Object.keys(map.channels).length > 3 || !Object.keys(map.channels).length) throw new Error('Invalid channels');
    for (const name of Object.values(map.channels)) {
      assetPath(id, name);
      const file = c.files?.[name];
      if (!file || !SHA.test(file.sha256) || !Number.isInteger(file.bytes) || file.bytes <= 0 || file.bytes > 8 * 1024 * 1024) throw new Error('Invalid map inventory');
    }
  }
  if (!Array.isArray(c.results) || !['linked_results', 'not_calculated'].includes(c.metrics_status) || Boolean(c.results.length) !== (c.metrics_status === 'linked_results')) throw new Error('Invalid metric status');
  if (![c.title, c.variable, c.units].every(v => typeof v === 'string' && v.length <= 300) || !Array.isArray(c.sources) || !Array.isArray(c.limitations)) throw new Error('Invalid case labels');
  return c;
}

async function init() {
  const q = id => document.getElementById(id);
  if (!q('studio-stories')) return;
  const t = (es, en) => window.portalLanguage?.() === 'en' ? en : es;
  let current = null, generation = 0, urls = [], controller;
  const text = (id, value) => { q(id).textContent = value; };
  const release = () => { urls.forEach(url => URL.revokeObjectURL(url)); urls = []; };
  const node = (tag, value) => { const n = document.createElement(tag); if (value != null) n.textContent = String(value); return n; };
  const link = (label, href) => { const a = node('a', label); a.href = href; a.download = ''; return a; };

  async function showMap() {
    if (!current) return;
    const c = current, index = Number(q('studio-date').value), observation = c.maps[index], token = ++generation;
    controller?.abort(); controller = new AbortController();
    const signal = controller.signal, nextURLs = [];
    q('studio-map-pane').setAttribute('aria-busy', 'true');
    text('studio-map-status', t('Cargando la observación elegida…', 'Loading the selected observation…'));
    try {
      const settled = await Promise.allSettled(Object.entries(observation.channels).map(async ([channel, name]) => {
        const figure = node('figure'); figure.className = channel === 'galapagos' ? 'studio-inset' : 'studio-main-map';
        const caption = node('figcaption', channel === 'galapagos' ? t('Galápagos · reubicado', 'Galápagos · repositioned') : `${c.variable} · ${observation.date}`);
        figure.append(caption);
        const coverage = observation.coverage?.[channel]?.state;
        if (coverage === 'disabled') return null;
        if (coverage === 'no_coverage') { figure.append(node('p', t('Sin cobertura verificable en esta fecha. No equivale a cero.', 'No verified coverage on this date. This is not zero.'))); return figure; }
        const response = await fetch(assetPath(c.id, name), {signal});
        if (!response.ok) throw new Error('Map unavailable');
        const bytes = await response.arrayBuffer(), record = c.files[name];
        if (bytes.byteLength !== record.bytes || !globalThis.crypto?.subtle) throw new Error('Cannot verify map');
        const digest = await crypto.subtle.digest('SHA-256', bytes);
        const sha = Array.from(new Uint8Array(digest), v => v.toString(16).padStart(2, '0')).join('');
        if (sha !== record.sha256) throw new Error('Map changed');
        const url = URL.createObjectURL(new Blob([bytes], {type:'image/png'})); nextURLs.push(url);
        const image = node('img'); image.src = url; image.alt = `${c.variable} · ${observation.date} · ${channel}`;
        await image.decode(); figure.append(image); return figure;
      }));
      const failure = settled.find(item => item.status === 'rejected');
      if (failure) throw failure.reason;
      const figures = settled.map(item => item.value).filter(Boolean);
      if (token !== generation) { nextURLs.forEach(url => URL.revokeObjectURL(url)); return; }
      release(); urls = nextURLs;
      q('studio-map-pane').classList.toggle('studio-single-map', figures.length === 1);
      q('studio-map-pane').replaceChildren(...figures);
      text('studio-observed-date', observation.date);
      text('studio-map-status', t('Imagen y fecha verificadas · sin interpolación temporal.', 'Image and date verified · no temporal interpolation.'));
    } catch (error) {
      nextURLs.forEach(url => URL.revokeObjectURL(url));
      if (token === generation && error.name !== 'AbortError') {
        q('studio-map-pane').replaceChildren(); release();
        text('studio-observed-date', '—');
        text('studio-map-status', t('No se pudo verificar esta observación. Descarga la evidencia para comprobarla.', 'This observation could not be verified. Download the evidence to inspect it.'));
      }
    } finally { if (token === generation) q('studio-map-pane').setAttribute('aria-busy', 'false'); }
  }

  function details() {
    const c = current;
    if (!c) return;
    text('studio-case-title', c.title);
    text('studio-case-period', `${c.observation_dates[0]} — ${c.observation_dates.at(-1)} · ${c.maps.length} ${t('observaciones', 'observations')} · ${c.units}`);
    text('studio-map-method', t('Representación conservada del video. Suavizar no añade resolución. Los cálculos se realizan con las fuentes nativas.', 'Preserved video representation. Smoothing does not add resolution. Calculations use native sources.'));
    const scale = c.scale, legend = q('studio-map-legend'); legend.replaceChildren();
    if (scale?.palette?.length && scale.palette.every(color => /^#[a-f0-9]{6}$/i.test(color)) && scale.stops?.length === scale.palette.length && scale.stops.every(Number.isFinite)) {
      legend.append(node('strong', `${scale.legend || c.variable} · ${c.units}`));
      const bar = node('div'); bar.className = 'studio-legend-bar'; bar.style.background = `linear-gradient(to right,${scale.palette.join(',')})`;
      const ticks = node('div'); ticks.className = 'studio-legend-ticks';
      scale.stops.forEach(value => ticks.append(node('span', new Intl.NumberFormat(window.portalLanguage?.() || 'es', {maximumFractionDigits:1}).format(value))));
      legend.append(bar, ticks); if (scale.saturation) legend.append(node('small', scale.saturation));
    }
    const resultList = q('studio-metric-list'); resultList.replaceChildren();
    if (!c.results.length) resultList.append(node('p', t('Esta serie no incluye métricas agregadas verificadas. No se usan cifras de otro video.', 'This series has no verified aggregate metrics. Figures from another video are not used.')));
    for (const result of c.results) {
      const box = node('details'); box.append(node('summary', `${result.variable || result.id} · ${result.units || ''}`));
      if (Number.isFinite(result.value)) box.append(node('p', `${result.value} ${result.units || ''}`));
      const json = node('pre', JSON.stringify({rows:result.rows, method:result.method}, null, 2)); box.append(json); resultList.append(box);
    }
    const sourceList = q('studio-source-list'); sourceList.replaceChildren();
    for (const source of c.sources) {
      const item = node('li'); item.append(node('strong', `${source.date} · ${source.citation || t('Fuente por revisar', 'Source needs review')}`));
      item.append(node('p', source.license || t('Condiciones no declaradas', 'Terms not declared')));
      const url = publicSourceURL(source.url);
      if (url) { const a = node('a', t('Fuente original ↗', 'Original source ↗')); a.href = url; a.target = '_blank'; a.rel = 'noopener noreferrer'; item.append(a); }
      item.append(node('code', `SHA-256: ${source.sha256}`)); sourceList.append(item);
    }
    q('studio-limit-list').replaceChildren(...c.limitations.map(value => node('li', value)));
    q('studio-downloads').replaceChildren(link(t('Método, cifras y huellas · JSON', 'Method, figures and hashes · JSON'), assetPath(c.id, 'case.json')), link(t('Video final · MP4', 'Final video · MP4'), assetPath(c.id, 'video.mp4')));
    text('studio-author', c.author || t('Autoría en los créditos del video.', 'Authorship in the video credits.'));
  }

  async function selectCase() {
    const id = q('studio-story').value, token = ++generation;
    controller?.abort(); release(); current = null; q('studio-case-view').hidden = true;
    q('studio-video').pause(); q('studio-video').removeAttribute('src'); q('studio-video').load();
    try {
      const reply = await fetch(assetPath(id, 'case.json'));
      if (!reply.ok) throw new Error('Case unavailable');
      const c = validateEvidence(await reply.json(), id);
      if (token !== generation) return;
      current = c; q('studio-date').max = String(c.maps.length - 1); q('studio-date').value = '0';
      q('studio-date').disabled = c.maps.length === 1;
      q('studio-video').src = assetPath(id, c.video); q('studio-video').load();
      q('studio-case-view').hidden = false; details(); await showMap();
    } catch { if (token === generation) text('studio-stories-status', t('El caso no está disponible o no ha sido revisado.', 'The case is unavailable or has not been reviewed.')); }
  }
  try {
    const response = await fetch('data/cases/studio-index.json');
    if (!response.ok) throw new Error('Index unavailable');
    const index = await response.json();
    if (index.schema_version !== 1 || !Array.isArray(index.cases)) throw new Error('Invalid index');
    const cases = index.cases.filter(c => ID.test(c.id) && c.status === 'reviewed');
    if (!cases.length) {
      text('studio-stories-status', t('Las nuevas historias aparecerán después de revisar el video, sus datos y sus derechos. Los borradores privados no se muestran aquí.', 'New stories will appear after video, data and rights review. Private drafts are not shown here.')); return;
    }
    q('studio-story-picker').hidden = false;
    q('studio-story').replaceChildren(...cases.map(c => {const option = node('option', c.title); option.value = c.id; return option;}));
    text('studio-stories-status', t('Video, mapa y método de una misma versión.', 'Video, map and method from the same version.'));
    q('studio-story').addEventListener('change', selectCase);
    q('studio-date').addEventListener('input', showMap);
    document.addEventListener('portal:language', details);
    await selectCase();
  } catch { text('studio-stories-status', t('No se pudo cargar el catálogo de Studio. El caso sísmico y sus descargas siguen disponibles más abajo.', 'The Studio catalog could not be loaded. The seismic case and its downloads remain available below.')); }
}
if (typeof document !== 'undefined') init();
