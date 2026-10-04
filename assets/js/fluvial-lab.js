import {WATER_METHODS, SIGNALS, valuesAt, waterVotes, transition, pixelIndex, validateManifest, decodePack} from "./fluvial-science.js?v=20261002-1";

export const COPY = {
  es: {
    skip: "Ir al mapa", viewMap: "Ver mapa", back: "Volver al atlas", eyebrow: "Napo · laboratorio de cambios fluviales",
    title: "¿Desapareció el agua… o dejó de verla el satélite?",
    lead: "Una señal puede cambiar por agua poco profunda, sedimentos, sombras o por un cauce que se mueve. Compara cuatro detectores sobre las mismas escenas reales; observa primero, interpreta después.",
    scope: "Cuatro ventanas locales, no toda Napo ni sus cuencas. Tres escenas de julio/agosto: 2019, 2024 y 2026. No son una serie suficiente para medir sequías, caudal ni duración de periodos secos.",
    region: "Tramo de exploración", signal: "Qué quieres observar", earlier: "Antes", later: "Después", swipe: "Desliza para comparar fechas", fit: "Ver el tramo completo",
    agreement: "Coincidencia entre detectores", transition: "Cambios candidatos de agua", ndti: "Contraste rojo/verde · NDTI", red: "Reflectancia roja del agua candidata", ndvi: "Vegetación · NDVI", vegetationChange: "Diferencia de NDVI",
    thresholds: "Prueba la sensibilidad del detector", thresholdNote: "Umbrales exploratorios, no calibrados para Napo. Un cambio de umbral modifica el resultado, no el río. Coincidencia no significa exactitud.", reset: "Restablecer a cero",
    loading: "Verificando la procedencia…", fetching: "Cargando y verificando dos escenas numéricas…", error: "No se pudo verificar o cargar la comparación. Se retiraron ambas imágenes; vuelve a seleccionar un tramo para reintentar.",
    ready: "Píxeles útiles en ambas fechas", useful: "Disponibilidad de datos, no exactitud. Trama gris = sin datos comparables. Zoom no crea detalle menor de 20 m.",
    inspect: "Haz clic en la imagen para consultar valores numéricos de ambas fechas. No se miden desde los colores.", outside: "Fuera de la ventana disponible.", missing: "Sin observación útil; no significa seco.",
    pending: "Ganador local: pendiente. La clasificación multibanda y su evaluación requieren referencias independientes. SCL no se usa como verdad de campo.",
    readTitle: "Tres preguntas distintas, tres líneas de evidencia", candidate: "Exploratorio", needsEvidence: "Necesita contraste independiente",
    waterTitle: "¿Dónde vemos agua?", waterCopy: "Los detectores proponen agua superficial. Sus desacuerdos quedan visibles; los huecos no cuentan como cauce seco. Menor superficie de agua no es una medición de caudal.",
    sedimentTitle: "¿Cambió la señal del agua?", sedimentCopy: "NDTI y reflectancia roja ayudan a explorar cambios ópticos dentro del agua candidata. Sin calibración local no damos NTU, mg/L ni concentraciones de mercurio. Agua poco profunda y efectos atmosféricos también pueden alterar la señal.",
    miningTitle: "¿Qué produjo el cambio?", miningCopy: "Buscar terreno removido, pozas y pérdida de vegetación; revisar lluvia y nivel del río; comparar aguas arriba y abajo. Ni el color del agua ni NDVI identifican por sí solos minería, ilegalidad o su causa.",
    sources: "Fuentes, datos y reproducción", resolution: "Comparación a 20 m: B2/B3/B4/B8 se agregan desde 10 m; B11/B12 son nativas de 20 m. Ampliar no crea detalle. La máscara conservadora puede descartar agua real bajo sombras.",
    manifest: "Procedencia y SHA-256 (JSON)", method: "Método, evaluación y siguientes pasos",
    datesNote: "Las escenas se escogieron por cobertura útil local, no por magnitud de cambio. Julio/agosto no garantiza condiciones hidrológicas iguales. 2019 no es un estado prístino y 2026 no es una composición anual ni una imagen en vivo.",
    shared: "Enlace actualizado con tramo, fechas, señal y umbrales; puedes copiar la dirección del navegador.",
    rgbCopy: "Color real, ajuste fijo 0–0,3 y gamma 1,2. Sigue los bordes, barras de arena y vegetación; no interpretes la diferencia como erosión o minería confirmadas.",
    ndwiCopy: "NDWI = (B3 − B8)/(B3 + B8). Puede omitir agua turbia o poco profunda. Aquí también se compara a 20 m para no darle una ventaja de resolución frente a los otros métodos.",
    mndwiCopy: "MNDWI = (B3 − B11)/(B3 + B11). Destaca el contraste verde/SWIR; no está demostrado que sea el mejor detector de Napo.",
    aweinshCopy: "AWEInsh = 4(B3 − B11) − 0,25B8 − 2,75B12. Variante sin sombras: candidato a comparar, no ganador validado. No está normalizado a −1/+1.",
    aweishCopy: "AWEIsh = B2 + 2,5B3 − 1,5(B8 + B11) − 0,25B12. Variante diseñada para reducir confusión con sombras, no para recuperar todos los píxeles descartados por QA. No está normalizado.",
    agreementCopy: "Azul: los cuatro métodos proponen agua. Gris: ninguno. Ámbar: discrepan. Comparten bandas y errores: cuatro votos no son cuatro evidencias independientes ni una probabilidad de certeza.",
    transitionCopy: "Azul/coral: aparición/pérdida candidata de agua con acuerdo unánime en ambos extremos. Ámbar: algún detector discrepa. La pérdida candidata no confirma cauce seco, sedimentos expuestos, erosión ni minería.",
    ndtiCopy: "NDTI = (B4 − B3)/(B4 + B3), solo donde los cuatro métodos proponen agua. Contraste óptico rojo/verde, no una medida calibrada de turbidez ni contaminación. Esta máscara puede omitir agua real.",
    redCopy: "Reflectancia superficial B4, solo sobre agua candidata por los cuatro métodos. Relacionable con sedimentos mediante calibración local, no convertida aquí a mg/L o NTU. Fondo, atmósfera y píxeles mixtos afectan la señal.",
    ndviCopy: "NDVI = (B8 − B4)/(B8 + B4). Señal de verdor, no clasificación de bosque, terreno removido ni minería.",
    vegetationChangeCopy: "NDVI posterior menos NDVI anterior, solo sobre soporte común. No mide hectáreas deforestadas; fechas, humedad, inundación e iluminación también cambian la señal.",
    stableLand: "No-agua por los cuatro métodos, ambas fechas", stableWater: "Agua candidata, ambas fechas", loss: "Pérdida candidata", gain: "Aparición candidata", disputed: "Desacuerdo entre métodos", agreementWater: "4/4 proponen agua", agreementLand: "0/4 proponen agua", noData: "Trama gris: NoData, no cauce seco", votes: "detectores proponen agua", clipped: "Escala visual fija; valores fuera de rango saturan el color, no el dato numérico.",
    pageTitle: "Ríos bajo la lupa · Ecuador Vivo", reference: "Registro de adquisición", notWaterMask: "Fuera del agua candidata; no es NoData", inspectorTitle: "Consultar un píxel · valores numéricos", inspectCenter: "Consultar el centro visible",
    referenceNames: ["Sentinel-2: bandas y resolución · Copernicus / Google", "NDWI · McFeeters (1996)", "MNDWI · Xu (2006)", "AWEI · Feyisa et al. (2014)", "Comparación de detectores · Kirby et al. (2024)", "Agua poco profunda y cauces secos · Cavallo et al. (2025)", "Sedimentos y minería amazónica · Lobo et al. (2018)", "NDTI rojo/verde · Water (2025)", "Minería aluvial y sedimentos · Dethier et al. (2023)"],
  },
  en: {
    skip: "Skip to map", viewMap: "View map", back: "Back to atlas", eyebrow: "Napo · river-change laboratory",
    title: "Did the water disappear… or did the satellite stop seeing it?",
    lead: "Shallow water, sediment, shadows and a shifting channel can all change a signal. Compare four detectors on the same real acquisitions; observe first, interpret afterwards.",
    scope: "Four local windows, not all of Napo or its catchments. Three July/August acquisitions: 2019, 2024 and 2026. Not a sufficient time series to measure drought, discharge or dry-period duration.",
    region: "Exploration window", signal: "What to observe", earlier: "Earlier", later: "Later", swipe: "Slide to compare dates", fit: "Fit available window",
    agreement: "Detector agreement", transition: "Candidate water changes", ndti: "Red/green contrast · NDTI", red: "Red reflectance of candidate water", ndvi: "Vegetation · NDVI", vegetationChange: "NDVI difference",
    thresholds: "Test detector sensitivity", thresholdNote: "Exploratory thresholds, not calibrated for Napo. A threshold changes the result, not the river. Agreement does not mean accuracy.", reset: "Reset to zero",
    loading: "Verifying provenance…", fetching: "Loading and verifying two numerical acquisitions…", error: "The comparison could not be verified or loaded. Both images were removed; select a window again to retry.",
    ready: "Useful pixels on both dates", useful: "Data availability, not accuracy. Grey checkerboard = no comparable data. Zoom does not create detail below 20 m.",
    inspect: "Click an image to inspect numerical values on both dates. Values are not read from colours.", outside: "Outside the available window.", missing: "No useful observation; this does not mean dry.",
    pending: "Local winner: pending. Multiband classification and evaluation need independent references. SCL is not used as field truth.",
    readTitle: "Three different questions, three lines of evidence", candidate: "Exploratory", needsEvidence: "Needs independent evidence",
    waterTitle: "Where do we see water?", waterCopy: "Detectors propose surface water. Disagreements remain visible; missing observations do not count as dry riverbed. Water area is not a discharge measurement.",
    sedimentTitle: "Did the water signal change?", sedimentCopy: "NDTI and red reflectance help explore optical changes inside candidate water. Without local calibration we report no NTU, mg/L or mercury concentrations. Shallow water and atmospheric effects can also alter the signal.",
    miningTitle: "What caused the change?", miningCopy: "Look for disturbed ground, ponds and vegetation loss; check rainfall and river level; compare upstream and downstream. Water colour and NDVI alone do not identify mining, illegality or causation.",
    sources: "Sources, data and reproduction", resolution: "20 m comparison: B2/B3/B4/B8 are aggregated from 10 m; B11/B12 are native 20 m. Zoom does not add detail. Conservative QA may discard real shadowed water.",
    manifest: "Provenance and SHA-256 (JSON)", method: "Method, evaluation and next steps",
    datesNote: "Acquisitions were chosen for local useful coverage, not change magnitude. July/August does not ensure equal hydrological conditions. 2019 is not pristine; 2026 is neither an annual composite nor a live image.",
    shared: "The URL preserves window, dates, signal and thresholds; copy it to share your view.",
    rgbCopy: "True colour, fixed 0–0.3 stretch and gamma 1.2. Follow banks, sandbars and vegetation; differences are not confirmed erosion or mining.",
    ndwiCopy: "NDWI = (B3 − B8)/(B3 + B8). May miss turbid or shallow water. Compared at 20 m here to avoid a resolution advantage over the other methods.",
    mndwiCopy: "MNDWI = (B3 − B11)/(B3 + B11). Highlights green/SWIR contrast; it is not proven to be Napo's best detector.",
    aweinshCopy: "AWEInsh = 4(B3 − B11) − 0.25B8 − 2.75B12. Non-shadow variant: a comparison candidate, not a validated winner. Not normalized to −1/+1.",
    aweishCopy: "AWEIsh = B2 + 2.5B3 − 1.5(B8 + B11) − 0.25B12. Designed to reduce shadow confusion, not recover every QA-rejected pixel. Not normalized.",
    agreementCopy: "Blue: all four propose water. Grey: none. Amber: disagreement. Shared bands and errors mean four votes are not four independent pieces of evidence or a confidence probability.",
    transitionCopy: "Blue/coral: candidate gain/loss with unanimous agreement at both dates. Amber: a detector disagrees. Candidate loss does not confirm dry bed, exposed sediment, erosion or mining.",
    ndtiCopy: "NDTI = (B4 − B3)/(B4 + B3), only where all four methods propose water. Optical red/green contrast, not calibrated turbidity or contamination. The mask may miss real water.",
    redCopy: "B4 surface reflectance, only on four-method candidate water. May relate to sediment with local calibration; not converted to mg/L or NTU here. Bottom, atmosphere and mixed pixels affect the signal.",
    ndviCopy: "NDVI = (B8 − B4)/(B8 + B4). Greenness signal, not a forest, disturbed-ground or mining classification.",
    vegetationChangeCopy: "Later minus earlier NDVI, on common support only. Not hectares of deforestation; dates, moisture, flooding and illumination also affect the signal.",
    stableLand: "All methods non-water, both dates", stableWater: "Candidate water on both dates", loss: "Candidate loss", gain: "Candidate gain", disputed: "Detector disagreement", agreementWater: "4/4 propose water", agreementLand: "0/4 propose water", noData: "Grey checkerboard: NoData, not dry bed", votes: "detectors propose water", clipped: "Fixed display range; out-of-range values saturate colour, not the numerical data.",
    pageTitle: "Rivers under the lens · Ecuador Vivo", reference: "Acquisition record", notWaterMask: "Outside candidate water; not NoData", inspectorTitle: "Inspect a pixel · numerical values", inspectCenter: "Inspect visible centre",
    referenceNames: ["Sentinel-2: bands and resolution · Copernicus / Google", "NDWI · McFeeters (1996)", "MNDWI · Xu (2006)", "AWEI · Feyisa et al. (2014)", "Detector comparison · Kirby et al. (2024)", "Shallow water and dry beds · Cavallo et al. (2025)", "Amazon sediment and mining · Lobo et al. (2018)", "Red/green NDTI · Water (2025)", "Alluvial mining and sediment · Dethier et al. (2023)"],
  },
};

export function normalizeView(params) {
  const regions = ["tena", "jatunyacu", "napo", "misahualli"];
  const earlier = ["2019-07-11", "2024-08-08"].includes(params.get("from")) ? params.get("from") : "2019-07-11";
  let later = ["2024-08-08", "2026-07-29"].includes(params.get("to")) ? params.get("to") : "2024-08-08";
  if (earlier >= later) later = "2026-07-29";
  const thresholds = Object.fromEntries(WATER_METHODS.map(key => {
    const raw = params.get(key), value = raw?.trim() ? Number(raw) : 0;
    return [key, Number.isFinite(value) && Math.abs(value) <= 1 ? value : 0];
  }));
  const split = params.get("split")?.trim() ? Number(params.get("split")) : 50;
  return {region: regions.includes(params.get("region")) ? params.get("region") : "tena",
    mode: SIGNALS.includes(params.get("mode")) ? params.get("mode") : "rgb", earlier, later, thresholds,
    split: Number.isFinite(split) ? Math.max(0, Math.min(100, split)) : 50};
}

if (typeof document !== "undefined") mountLab();
function mountLab() {
  const find = id => document.getElementById(id);
  const params = new URLSearchParams(location.search); let view = normalizeView(params), lang = params.get("lang") === "en" ? "en" : "es";
  try { if (!params.has("lang") && localStorage.getItem("atlas-language") === "en") lang = "en"; } catch { /* Optional preference. */ }
  const t = key => COPY[lang][key], locale = () => lang === "es" ? "es-EC" : "en-GB";
  const number = (x, digits = 3) => new Intl.NumberFormat(locale(), {maximumFractionDigits: digits}).format(x);
  const date = value => new Intl.DateTimeFormat(locale(), {day: "2-digit", month: "short", year: "numeric", timeZone: "UTC"}).format(new Date(value + "T12:00:00Z"));
  let manifest, region, packs, overlays = [], epoch = 0, state = "loading", lastPoint;
  const cache = new Map();
  if (!window.L) { find("lab-status").textContent = t("error"); return; }
  const map = L.map("fluvial-map", {maxZoom: 19, minZoom: 8, zoomSnap: .25}).setView([-1.0, -77.81], 13);
  // No basemap imagery behind gaps: checkerboard makes missing support explicit.
  L.control.scale({imperial: false}).addTo(map);
  map.createPane("fluvial-data"); map.getPane("fluvial-data").style.zIndex = "300"; map.getPane("fluvial-data").style.pointerEvents = "none";
  function syncURL() {
    const url = new URL(location.href);
    url.search = "";
    for (const [key, value] of Object.entries({lang, region: view.region, mode: view.mode, from: view.earlier, to: view.later, split: view.split, ...view.thresholds})) url.searchParams.set(key, String(value));
    history.replaceState(history.state, "", url);
  }
  function clear() { overlays.forEach(layer => map.removeLayer(layer)); overlays = []; find("lab-cut").hidden = true; }
  function clip() {
    const rect = map.getContainer().getBoundingClientRect();
    overlays.forEach((layer, i) => {
      const image = layer.getElement(); if (!image) return;
      const bounds = image.getBoundingClientRect();
      const cut = Math.max(0, Math.min(100, 100 * (rect.left + rect.width * view.split / 100 - bounds.left) / bounds.width));
      image.style.clipPath = overlays.length === 2 ? i === 0 ? `inset(0 ${100 - cut}% 0 0)` : `inset(0 0 0 ${cut}%)` : "none";
    });
    find("lab-cut").style.left = view.split + "%";
  }
  const ranges = {ndwi: [-1, 1], mndwi: [-1, 1], aweinsh: [-1, 1], aweish: [-1, 1], ndti: [-1, 1], red: [0, .3], ndvi: [-1, 1], vegetationChange: [-2, 2]};
  const colours = [[160, 103, 56], [236, 223, 175], [40, 127, 192]];
  const categorical = [[0, 0, 0, 0], [64, 78, 81, 255], [61, 138, 153, 255], [240, 109, 96, 255], [82, 180, 238, 255], [224, 175, 80, 255]];
  function gradient(value, low, high) {
    const f = Math.max(0, Math.min(1, (value - low) / (high - low))), side = f <= .5 ? 0 : 1, weight = side === 0 ? f * 2 : (f - .5) * 2;
    return [...colours[side].map((x, i) => Math.round(x + weight * (colours[side + 1][i] - x))), 255];
  }
  function imageFor(side, stats) {
    const canvas = document.createElement("canvas"); canvas.width = region.width; canvas.height = region.height;
    const context = canvas.getContext("2d"), image = context.createImageData(canvas.width, canvas.height), n = canvas.width * canvas.height;
    for (let index = 0; index < n; index++) {
      const a = valuesAt(packs[0], index), b = valuesAt(packs[1], index);
      if (!a || !b) continue; // Exactly the same paired support for every mode/date.
      if (side === 0) stats.common++;
      const selected = side === 0 ? a : b, votes = waterVotes(selected, view.thresholds);
      let colour;
      if (view.mode === "rgb") colour = [selected.red, selected.green, selected.blue].map(v => Math.round(255 * Math.pow(Math.max(0, Math.min(1, v / .3)), 1 / 1.2))).concat(255);
      else if (view.mode === "agreement") colour = votes === 4 ? categorical[4] : votes === 0 ? categorical[1] : categorical[5];
      else if (view.mode === "transition") {
        const code = transition(waterVotes(a, view.thresholds), waterVotes(b, view.thresholds)); colour = categorical[code]; stats.transitions[code]++;
      } else if (view.mode === "ndti" || view.mode === "red") {
        colour = votes === 4 ? gradient(selected[view.mode], ...ranges[view.mode]) : categorical[1];
      } else {
        const value = view.mode === "vegetationChange" ? b.ndvi - a.ndvi : selected[view.mode];
        colour = gradient(value, ...ranges[view.mode]);
      }
      image.data.set(colour, index * 4);
    }
    context.putImageData(image, 0, 0); return canvas.toDataURL("image/png");
  }
  function legend() {
    const box = find("lab-legend"); box.replaceChildren();
    const title = document.createElement("strong"); title.textContent = find("lab-mode").selectedOptions[0].textContent; box.append(title);
    const swatch = (colour, text) => {
      const p = document.createElement("p"), span = document.createElement("span"); span.className = "swatch"; span.style.background = `rgb(${colour.slice(0, 3).join(",")})`;
      p.append(span, document.createTextNode(text)); box.append(p);
    };
    if (view.mode === "transition") ["stableLand", "stableWater", "loss", "gain", "disputed"].forEach((key, i) => swatch(categorical[i + 1], t(key)));
    else if (view.mode === "agreement") { swatch(categorical[4], t("agreementWater")); swatch(categorical[1], t("agreementLand")); swatch(categorical[5], t("disputed")); }
    else if (view.mode !== "rgb") {
      const scale = document.createElement("div"); scale.className = "legend-scale";
      const ticks = document.createElement("div"); ticks.className = "ticks";
      const [low, high] = ranges[view.mode]; for (const v of [low, (low + high) / 2, high]) { const span = document.createElement("span"); span.textContent = number(v); ticks.append(span); }
      box.append(scale, ticks);
      if (["ndti", "red"].includes(view.mode)) swatch(categorical[1], t("notWaterMask"));
      if (["aweinsh", "aweish", "red"].includes(view.mode)) { const note = document.createElement("p"); note.textContent = t("clipped"); box.append(note); }
    }
    const note = document.createElement("p"); note.textContent = t("noData"); box.append(note);
  }
  function draw() {
    clear();
    find("lab-explanation").textContent = t(view.mode + "Copy");
    if (!packs || state !== "ready") return;
    const single = ["transition", "vegetationChange"].includes(view.mode), stats = {common: 0, transitions: Array(6).fill(0)};
    const [left, bottom, right, top] = region.web_extent;
    const sw = L.CRS.EPSG3857.unproject(L.point(left, bottom)), ne = L.CRS.EPSG3857.unproject(L.point(right, top));
    for (const side of single ? [0] : [0, 1]) {
      const layer = L.imageOverlay(imageFor(side, stats), L.latLngBounds(sw, ne), {pane: "fluvial-data", className: "lab-overlay", attribution: "Modified Copernicus Sentinel data · Earth Search / Element 84"});
      layer.on("load", clip); layer.addTo(map); overlays.push(layer);
    }
    find("lab-split").disabled = single; find("lab-cut").hidden = single;
    find("lab-date-a").textContent = single ? `${date(view.earlier)} → ${date(view.later)}` : date(view.earlier);
    find("lab-date-b").hidden = single; find("lab-date-b").textContent = date(view.later);
    find("lab-status").textContent = `${t("ready")}: ${number(100 * stats.common / (region.width * region.height), 1)}%. ${t("useful")}`;
    find("lab-explanation").textContent = t(view.mode + "Copy");
    legend(); clip(); if (lastPoint) inspect(lastPoint);
  }
  function fit() {
    if (!region) return;
    const [left, bottom, right, top] = region.web_extent;
    map.fitBounds([L.CRS.EPSG3857.unproject(L.point(left, bottom)), L.CRS.EPSG3857.unproject(L.point(right, top))], {padding: [25, 25], animate: false});
  }
  async function getPack(row, selectedRegion) {
    if (!cache.has(row.url)) {
      const promise = fetch(row.url).then(response => { if (!response.ok) throw new Error("Missing numerical pack"); return response.arrayBuffer(); }).then(bytes => decodePack(bytes, row, selectedRegion));
      cache.set(row.url, promise);
      promise.catch(() => cache.delete(row.url));
    }
    const pack = await cache.get(row.url);
    while (cache.size > 4) cache.delete(cache.keys().next().value);
    return pack;
  }
  async function loadView(shouldFit = false) {
    if (!manifest) return;
    const current = ++epoch; clear(); packs = undefined; lastPoint = undefined; state = "fetching";
    region = manifest.regions.find(row => row.id === view.region);
    find("lab-status").textContent = t("fetching"); find("lab-inspector").textContent = t("inspect");
    find("lab-legend").replaceChildren(); find("lab-date-a").textContent = ""; find("lab-date-b").textContent = "";
    if (shouldFit) fit();
    const selectedRegion = region, requestedDates = [view.earlier, view.later];
    try {
      const result = await Promise.all(requestedDates.map(date => getPack(selectedRegion.scenes.find(row => row.date === date), selectedRegion)));
      if (current !== epoch) return;
      packs = result; state = "ready"; draw();
    } catch {
      if (current !== epoch) return;
      state = "error"; packs = undefined; clear(); find("lab-status").textContent = t("error");
    }
  }
  function inspect(latlng) {
    if (!packs || state !== "ready") return;
    const index = pixelIndex(L.CRS.EPSG3857.project(latlng), region);
    if (index === null) { find("lab-inspector").textContent = t("outside"); return; }
    lastPoint = latlng;
    find("lab-inspector-panel").open = true;
    const lines = [`${number(latlng.lat, 5)}, ${number(latlng.lng, 5)}`];
    for (const [i, pack] of packs.entries()) {
      const v = valuesAt(pack, index); lines.push(date(i === 0 ? view.earlier : view.later));
      if (!v) { lines.push(t("missing")); continue; }
      const votes = waterVotes(v, view.thresholds);
      lines.push(`NDWI ${number(v.ndwi)} · MNDWI ${number(v.mndwi)}`, `AWEInsh ${number(v.aweinsh)} · AWEIsh ${number(v.aweish)}`,
        votes === 4 ? `NDTI ${number(v.ndti)} · B4 ${number(v.red)}` : `NDTI / B4: ${t("notWaterMask")}`,
        `NDVI ${number(v.ndvi)} · ${votes}/4 ${t("votes")}`);
    }
    find("lab-inspector").textContent = lines.join("\n");
  }
  function text() {
    document.documentElement.lang = lang; document.title = t("pageTitle");
    document.querySelector('meta[name="description"]').content = t("scope");
    document.querySelectorAll("[data-lab-text]").forEach(el => el.textContent = t(el.dataset.labText));
    find("lab-language").textContent = lang === "es" ? "EN" : "ES"; find("lab-language").setAttribute("aria-label", lang === "es" ? "Switch to English" : "Cambiar a español");
    find("fluvial-map").setAttribute("aria-label", t("title"));
    document.querySelector(".workbench").setAttribute("aria-label", t("eyebrow"));
    for (const id of ["lab-earlier", "lab-later"]) [...find(id).options].forEach(option => option.textContent = date(option.value));
    if (state === "ready") draw(); else find("lab-status").textContent = t(state);
    if (manifest) {
      const list = find("lab-sources"); list.replaceChildren();
      for (const row of [...manifest.config.references.map((row, i) => ({...row, title: t("referenceNames")[i]})), ...manifest.config.scenes.map(row => ({title: `${t("reference")} · ${date(row.date)} · ${row.id}`, url: `${manifest.config.api}/collections/${row.collection}/items/${row.id}`}))]) {
        const li = document.createElement("li"), a = document.createElement("a"); a.href = row.url; a.textContent = row.title; a.target = "_blank"; a.rel = "noopener noreferrer"; li.append(a); list.append(li);
      }
    }
  }
  function controls() {
    find("lab-region").value = view.region; find("lab-mode").value = view.mode; find("lab-earlier").value = view.earlier; find("lab-later").value = view.later; find("lab-split").value = String(view.split);
    for (const key of WATER_METHODS) find("threshold-" + key).value = String(view.thresholds[key]);
  }
  for (const key of WATER_METHODS) {
    const label = document.createElement("label"), span = document.createElement("span"), input = document.createElement("input");
    span.textContent = key.toUpperCase(); input.type = "number"; input.min = "-1"; input.max = "1"; input.step = ".01"; input.id = "threshold-" + key;
    label.append(span, input); find("lab-thresholds").append(label);
    input.addEventListener("change", () => {
      const raw = input.value.trim(), value = raw ? Number(raw) : NaN;
      if (!Number.isFinite(value) || Math.abs(value) > 1) { input.value = String(view.thresholds[key]); return; }
      view.thresholds[key] = value; syncURL(); draw();
    });
  }
  find("lab-region").addEventListener("change", () => { view.region = find("lab-region").value; syncURL(); void loadView(true); });
  find("lab-mode").addEventListener("change", () => { view.mode = find("lab-mode").value; syncURL(); if (state === "error") void loadView(); else draw(); });
  for (const id of ["lab-earlier", "lab-later"]) find(id).addEventListener("change", () => {
    view.earlier = find("lab-earlier").value; view.later = find("lab-later").value;
    if (view.earlier >= view.later) { if (id === "lab-earlier") view.later = "2026-07-29"; else view.earlier = "2019-07-11"; }
    controls(); syncURL(); void loadView();
  });
  find("lab-split").addEventListener("input", () => { view.split = Number(find("lab-split").value); syncURL(); clip(); });
  find("lab-reset").addEventListener("click", () => { view.thresholds = Object.fromEntries(WATER_METHODS.map(key => [key, 0])); controls(); syncURL(); draw(); });
  find("lab-fit").addEventListener("click", fit);
  find("lab-inspect-center").addEventListener("click", () => inspect(map.getCenter()));
  find("lab-language").addEventListener("click", () => { lang = lang === "es" ? "en" : "es"; try { localStorage.setItem("atlas-language", lang); } catch { /* Optional. */ } syncURL(); text(); });
  map.on("click", event => inspect(event.latlng)); map.on("move zoom resize viewreset", clip);
  let frame; map.on("zoomstart", () => { const animate = () => { clip(); frame = requestAnimationFrame(animate); }; frame = requestAnimationFrame(animate); });
  map.on("zoomend", () => { cancelAnimationFrame(frame); clip(); });
  window.addEventListener("popstate", () => { const params = new URLSearchParams(location.search); view = normalizeView(params); lang = params.get("lang") === "en" ? "en" : "es"; controls(); text(); void loadView(true); });
  controls(); text();
  (async () => {
    try {
      const replies = await Promise.all(["data/fluvial/config.json", "data/fluvial/manifest.json"].map(url => fetch(url, {cache: "no-store"})));
      if (replies.some(r => !r.ok)) throw new Error("Missing provenance");
      const [config, data] = await Promise.all(replies.map(r => r.json())); manifest = validateManifest(data, config); text(); await loadView(true);
    } catch { state = "error"; find("lab-status").textContent = t("error"); }
  })();
}
