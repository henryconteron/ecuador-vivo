/** Georeferenced explorer. Display colours are not a pixel-measurement API. */
import {loadSpectralPair, validateSpectralManifest} from "./spectral.js";
import {comparisonPosition} from "./imagery.js";

export const SPECTRAL_MODES = Object.freeze(["rgb", "ndvi", "mndwi", "ndmi", "change", "quality"]);
export function normalizeSpectralView(params) {
  const mode = SPECTRAL_MODES.includes(params.get("signal")) ? params.get("signal") : "rgb";
  return {enabled: params.get("view") === "spectral", mode,
    year: params.get("year") === "2019" ? 2019 : 2024,
    compare: mode !== "change" && params.get("compare") !== "0",
    position: params.has("split") ? comparisonPosition(params.get("split")) : 50,
    river: params.get("area") === "jatunyacu"};
}

export function validateSpectralExplorer(document, settings, parent) {
  const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  if (!parent || document?.schema_version !== 1 || document.status !== "ready" || settings?.schema_version !== 1 ||
      !same(document.config, settings) || settings.derivation !== "native-float32-before-nearest-display-resampling" ||
      settings.ndmi_formula !== "(B8-B11)/(B8+B11)" || settings.change_formula !== "NDVI_2024-NDVI_2019" || settings.quality_band !== "clear_count" ||
      settings.ndmi_source !== "https://www.usgs.gov/landsat-missions/normalized-difference-moisture-index") throw new Error("Unknown spectral derivation");
  for (const mode of ["ndmi", "change", "quality"]) {
    const row = settings.display[mode], range = {ndmi: [-1, 1], change: [-2, 2], quality: [0, 80]}[mode];
    if (row?.min !== range[0] || row.max !== range[1] || row.levels !== 129 || !Array.isArray(row.palette) || row.palette.length !== 3 ||
        row.palette.some(value => !/^#[a-f0-9]{6}$/i.test(value))) throw new Error("Unknown explorer colour scale");
  }
  if (document.parent_input_sha256 !== parent.input_sha256 || document.parent_receipt_sha256 !== parent.receipt_sha256 ||
      !same(document.display_bounds, parent.display_bounds) || document.width !== parent.width || document.height !== parent.height ||
      document.display_crs !== "EPSG:3857" || document.resampling !== "nearest" || document.common_pixels !== parent.statistics.common_pixels ||
      !Number.isSafeInteger(document.ndmi_common_pixels) || document.ndmi_common_pixels <= 0 || document.ndmi_common_pixels > document.common_pixels) throw new Error("Explorer source/grid has changed");
  const expected = [["ndmi", 2019], ["ndmi", 2024], ["quality", 2019], ["quality", 2024], ["change", null]];
  if (!Array.isArray(document.images) || document.images.length !== 5 || document.images.some((row, index) =>
    row.mode !== expected[index][0] || row.year !== expected[index][1] ||
    row.url !== `assets/images/spectral/napo-${row.mode}-${row.year ?? "2019-2024"}.png` || !/^[a-f0-9]{64}$/.test(row.sha256))) throw new Error("Invalid explorer images");
  return document;
}

/** Cut in screen space, recalculated on pan/zoom; never move either year independently. */
export function screenClip(imageRect, mapRect, position, side) {
  if (!Number.isFinite(imageRect.width) || imageRect.width <= 0) return "inset(0 0 0 0)";
  const cut = comparisonPosition(100 * (mapRect.left + mapRect.width * comparisonPosition(position) / 100 - imageRect.left) / imageRect.width);
  return side === "earlier" ? `inset(0 ${100 - cut}% 0 0)` : `inset(0 0 0 ${cut}%)`;
}

export function mountNapoSpectralMap({L, map, t, language, onChange, onActivate = () => {}, canActivate = () => true, focus}) {
  const find = id => document.getElementById(id);
  const toggle = find("spectral-map-toggle"), controls = find("spectral-map-settings"), toolbar = find("spectral-map-toolbar");
  const modeSelect = find("spectral-map-mode"), quickSelect = find("spectral-map-quick-mode");
  const compareToggle = find("spectral-map-compare"), slider = find("spectral-map-split"), opacity = find("spectral-map-opacity");
  const timeSelect = find("spectral-map-time");
  const divider = find("spectral-map-divider"), years = [...document.querySelectorAll("[data-spectral-map-year]")];
  let view = normalizeSpectralView(new URLSearchParams(window.location.search));
  let config, manifest, extended, settings, state = "loading", overlays = [], outline, epoch = 0;
  const number = value => new Intl.NumberFormat(language(), {maximumFractionDigits: 1}).format(value);
  map.createPane("napo-spectral");
  map.getPane("napo-spectral").style.zIndex = "300";
  map.getPane("napo-spectral").style.pointerEvents = "none";
  function clip() {
    const mapRect = map.getContainer().getBoundingClientRect();
    overlays.forEach((layer, index) => {
      const image = layer.getElement();
      if (image) image.style.clipPath = view.compare ? screenClip(image.getBoundingClientRect(), mapRect, view.position, index === 0 ? "earlier" : "later") : "none";
    });
    divider.style.left = `${view.position}%`;
  }
  function clear() {
    for (const layer of overlays) map.removeLayer(layer);
    overlays = [];
    if (outline) map.removeLayer(outline);
    outline = undefined;
  }
  function syncUrl() {
    const url = new URL(window.location.href);
    for (const key of ["view", "signal", "year", "compare", "split", "area"]) url.searchParams.delete(key);
    if (toggle.checked) {
      url.searchParams.delete("lab");
      url.searchParams.set("view", "spectral"); url.searchParams.set("signal", view.mode);
      url.searchParams.set("year", String(view.year)); url.searchParams.set("compare", view.compare ? "1" : "0");
      url.searchParams.set("split", String(view.position));
      if (view.river) url.searchParams.set("area", "jatunyacu");
    }
    window.history.replaceState(window.history.state, "", url);
  }
  function render() {
    toggle.disabled = !manifest;
    controls.hidden = !manifest || !toggle.checked;
    const active = state === "visible" && overlays.some(layer => map.hasLayer(layer));
    toolbar.hidden = !active; divider.hidden = !active || !view.compare;
    const status = !manifest ? `spectral.${state}` : `spectralMap.${state === "visible" ? "visible" : state === "imageLoading" ? "loading" : state === "imageError" ? "error" : "off"}`;
    find("spectral-map-status").textContent = t(status);
    modeSelect.value = quickSelect.value = view.mode;
    compareToggle.checked = view.compare; compareToggle.disabled = view.mode === "change";
    timeSelect.value = view.compare || view.mode === "change" ? "compare" : String(view.year); timeSelect.disabled = view.mode === "change";
    slider.value = String(view.position);
    slider.setAttribute("aria-valuetext", `2019 ${number(view.position)}%, 2024 ${number(100 - view.position)}%`);
    find("spectral-map-compare-controls").hidden = !view.compare;
    find("spectral-map-title").textContent = `${t(`spectral.${view.mode}`)} · ${view.mode === "change" || view.compare ? "2019 ↔ 2024" : view.year}`;
    find("spectral-map-opacity-value").textContent = `${opacity.value}%`;
    find("spectral-map-copy").textContent = t(`spectral.${view.mode}Copy`);
    years.forEach(button => { button.disabled = view.compare || view.mode === "change"; button.setAttribute("aria-pressed", String(Number(button.dataset.spectralMapYear) === view.year)); });
    find("spectral-map-legend-title").textContent = find("spectral-map-title").textContent;
    find("spectral-map-legend-scale").hidden = view.mode === "rgb";
    find("spectral-map-legend-note").textContent = t(view.mode === "rgb" ? "spectralMap.rgbLegend" : view.mode === "quality" ? "spectralMap.qualityLegend" : view.mode === "change" ? "spectralMap.changeLegend" : "spectral.scale");
    if (manifest && view.mode !== "rgb") {
      const display = (config.display[view.mode] ?? settings.display[view.mode]);
      find("spectral-map-gradient").style.background = `linear-gradient(90deg, ${display.palette.join(", ")})`;
      find("spectral-map-min").textContent = number(display.min);
      find("spectral-map-mid").textContent = number((display.min + display.max) / 2);
      find("spectral-map-max").textContent = number(display.max);
    }
    const outside = manifest && !map.getBounds().intersects(manifest.display_bounds);
    const compact = window.matchMedia("(max-width: 30rem)").matches;
    find("spectral-map-scope").textContent = compact
      ? t(outside ? "spectralMap.compactOutside" : map.getZoom() > 13 ? "spectralMap.compactZoom" : "spectralMap.compactScope")
      : t(outside ? "spectralMap.outside" : map.getZoom() > 13 ? "spectralMap.zoomLimit" : "spectralMap.scope");
    clip();
  }
  async function draw() {
    const current = ++epoch;
    clear();
    state = manifest ? "ready" : state; render(); onChange();
    if (!toggle.checked || !manifest) return;
    state = "imageLoading"; render();
    const requestedMode = view.mode;
    const rows = requestedMode === "change" ? [extended.images.at(-1), extended.images.at(-1)] :
      [2019, 2024].map(year => [...manifest.images, ...extended.images].find(row => row.year === year && row.mode === requestedMode));
    try {
      const images = await loadSpectralPair(rows, {width: manifest.width, height: manifest.height, isCurrent: () => current === epoch && toggle.checked});
      if (!images) return;
      const shown = view.compare ? images : [images[view.year === 2019 ? 0 : 1]];
      let loaded = 0;
      overlays = shown.map(image => {
        const layer = L.imageOverlay(image.src, manifest.display_bounds, {pane: "napo-spectral", opacity: Number(opacity.value) / 100,
          className: requestedMode === "rgb" ? "spectral-rgb-overlay" : "categorical-overlay",
          attribution: 'Modified Copernicus Sentinel-2 (2019, 2024) · <a href="https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_CLOUD_SCORE_PLUS_V1_S2_HARMONIZED" target="_blank" rel="noopener noreferrer">Cloud Score+</a>'});
        layer.on("load", () => {
          if (current !== epoch) return;
          loaded += 1; clip();
          if (loaded === shown.length) { state = "visible"; render(); onChange(); }
        });
        layer.on("error", () => { if (current === epoch) fail(); });
        return layer;
      });
      for (const layer of overlays) layer.addTo(map);
      outline = L.rectangle(manifest.display_bounds, {pane: "napo-spectral", interactive: false, fill: false, color: "#bce6da", weight: 1, dashArray: "5 5"}).addTo(map);
      clip();
    } catch { if (current === epoch) fail(); }
  }
  function fail() {
    ++epoch; clear(); toggle.checked = false; state = "imageError"; syncUrl(); render(); onChange();
  }
  function goToArea(river) {
    view.river = river; focus();
    const bbox = river ? config.river_focus_bbox : config.bbox;
    map.fitBounds([[bbox[1], bbox[0]], [bbox[3], bbox[2]]], {padding: [24, 24], maxZoom: river ? 13 : 11});
    if (window.matchMedia("(max-width: 64rem)").matches) map.getContainer().scrollIntoView({block: "start"});
  }
  function activate({mode = view.mode, river = view.river} = {}) {
    if (!manifest || !canActivate()) return false;
    view.mode = SPECTRAL_MODES.includes(mode) ? mode : "rgb";
    if (view.mode === "change") view.compare = false;
    onActivate(); toggle.checked = true; goToArea(river); syncUrl(); void draw();
    return true;
  }
  toggle.addEventListener("change", () => { if (toggle.checked) { onActivate(); goToArea(view.river); } syncUrl(); void draw(); });
  find("spectral-map-hide").addEventListener("click", () => { toggle.checked = false; syncUrl(); void draw(); });
  for (const select of [modeSelect, quickSelect]) select.addEventListener("change", () => {
    view.mode = select.value; if (view.mode === "change") view.compare = false; syncUrl(); void draw();
  });
  compareToggle.addEventListener("change", () => { view.compare = compareToggle.checked && view.mode !== "change"; syncUrl(); void draw(); });
  timeSelect.addEventListener("change", () => {
    view.compare = timeSelect.value === "compare" && view.mode !== "change";
    if (!view.compare) view.year = timeSelect.value === "2019" ? 2019 : 2024;
    syncUrl(); void draw();
  });
  years.forEach(button => button.addEventListener("click", () => { view.year = Number(button.dataset.spectralMapYear); syncUrl(); void draw(); }));
  slider.addEventListener("input", () => { view.position = comparisonPosition(slider.value); clip(); syncUrl(); render(); });
  opacity.addEventListener("input", () => { overlays.forEach(layer => layer.setOpacity(Number(opacity.value) / 100)); render(); });
  document.querySelectorAll("[data-spectral-map-area]").forEach(button => button.addEventListener("click", () => { goToArea(button.dataset.spectralMapArea === "river"); syncUrl(); render(); }));
  map.on("move zoom zoomend resize viewreset", () => { clip(); });
  let clipFrame;
  map.on("zoomstart", () => {
    const animate = () => { clip(); clipFrame = requestAnimationFrame(animate); };
    if (overlays.length) clipFrame = requestAnimationFrame(animate);
  });
  map.on("zoomend", () => { if (clipFrame) cancelAnimationFrame(clipFrame); clipFrame = undefined; clip(); });
  map.on("moveend zoomend", render);
  window.addEventListener("popstate", () => {
    view = normalizeSpectralView(new URLSearchParams(window.location.search)); toggle.checked = Boolean(manifest && view.enabled && canActivate()); void draw();
  });
  async function load() {
    try {
      const urls = ["data/spectral/napo-config.json", "data/spectral/napo-manifest.json", "data/landcover/napo-manifest.json", "data/spectral/napo-explorer-config.json", "data/spectral/napo-explorer-manifest.json"];
      const responses = await Promise.all(urls.map(url => fetch(url, {cache: "no-store"})));
      if (responses.some(response => !response.ok)) throw new Error("Missing explorer bundle");
      const [primaryConfig, primary, grid, extraConfig, extra] = await Promise.all(responses.map(response => response.json()));
      config = primaryConfig; settings = extraConfig; manifest = validateSpectralManifest(primary, config, grid);
      if (manifest) extended = validateSpectralExplorer(extra, settings, manifest);
      state = manifest ? "ready" : "pending";
    } catch (error) { console.warn("Spectral explorer bundle could not be validated", error); manifest = undefined; state = "error"; }
    render(); onChange();
    if (manifest && view.enabled) activate();
  }
  render(); void load();
  return {render, activate, deactivate: () => { toggle.checked = false; syncUrl(); void draw(); }, isReady: () => Boolean(manifest), isActive: () => state === "visible" && overlays.some(layer => map.hasLayer(layer)),
    context: () => ({id: "spectral-map", name: t("spectralMap.title"), resolution: `Sentinel-2 · 10 / 20 m → 30 m · ${view.compare || view.mode === "change" ? "2019 / 2024" : view.year}`, limit: t("spectralMap.zoomLimit")})};
}
