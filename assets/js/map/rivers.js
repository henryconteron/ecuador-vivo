/** Provincial 10 m display tiles; screening markers are not confirmed events. */
import {screenClip} from "./spectral-map.js?v=20260930-8";

export function validateRiverManifest(manifest, config) {
  if (manifest?.schema_version !== 1) throw new Error("Unknown river bundle");
  if (manifest.status === "pending") return null;
  const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  const hash = value => typeof value === "string" && /^[a-f0-9]{64}$/.test(value);
  if (manifest.status !== "ready" || !same(manifest.config, config) || config.scope !== "province-napo-incremental-blocks-not-entire-river-basin" ||
      config.method !== "joint-four-band-qa-annual-median-rgb-scene-level-ndwi-frequency" ||
      !same(config.export_transform, [10, 0, 0, 0, -10, 0]) || config.export_crs !== "EPSG:3857" ||
      !same(config.years, [2019, 2024]) || manifest.sampling_m !== 10 || manifest.resampling !== "nearest" || manifest.tile_format !== "lossless-webp" ||
      manifest.tile_size !== 512 || manifest.zoom_offset !== -1 || manifest.min_native_zoom !== 9 || manifest.max_native_zoom !== 14 ||
      !hash(manifest.receipt_sha256) || !["pending", "ready"].includes(manifest.candidate_status) ||
      (manifest.candidate_status === "ready" ? !hash(manifest.candidates_sha256) : manifest.candidates_sha256 !== null || manifest.candidate_count !== null)) throw new Error("Invalid provincial provenance/grid");
  const receipt = manifest.receipt;
  for (const key of ["schema_version", "asset", "quality_asset", "boundary_asset", "boundary_filter", "years", "periods", "bands", "clear_threshold",
    "min_observations", "excluded_scl", "water_formula", "water_threshold", "change_threshold", "water_frequency_min", "min_connected_pixels",
    "screening_cell_m", "min_cell_change_ha", "export_crs", "export_transform", "export_bands", "display", "method", "scope", "rgb_min_observations", "scene_selection", "processing_grid"]) {
    if (!same(receipt?.[key], config[key])) throw new Error(`River receipt mismatch: ${key}`);
  }
  if (!Number.isSafeInteger(receipt.processing_block?.id) || receipt.processing_block.id < 0 || receipt.processing_block.id > 8 ||
      !Array.isArray(receipt.processing_block.bbox) || receipt.processing_block.bbox.length !== 4 || receipt.processing_block.bbox.some(x => !Number.isFinite(x)) ||
      manifest.coverage?.kind !== "processing-block" || manifest.coverage.total_blocks !== 9 || !same(manifest.coverage.block_ids, [receipt.processing_block.id])) throw new Error("Missing incremental coverage");
  const grid = config.processing_grid, block = receipt.processing_block;
  const dx = (grid.bbox[2] - grid.bbox[0]) / grid.columns, dy = (grid.bbox[3] - grid.bbox[1]) / grid.rows;
  const left = grid.bbox[0] + (block.id % grid.columns) * dx, top = grid.bbox[3] - Math.floor(block.id / grid.columns) * dy;
  if ([left, top - dy, left + dx, top].some((value, i) => Math.abs(value - block.bbox[i]) > 1e-9)) throw new Error("Processing block differs from grid");
  if (receipt.boundary?.properties?.shapeName !== "Napo" || receipt.boundary?.properties?.shapeGroup !== "ECU" ||
      !["Polygon", "MultiPolygon"].includes(receipt.boundary?.geometry?.type) || !Number.isFinite(Date.parse(receipt.export_requested_at))) throw new Error("Missing actual Napo boundary");
  if (!Array.isArray(receipt.scenes) || receipt.scenes.length !== 2) throw new Error("Missing scene inventories");
  receipt.scenes.forEach((row, i) => {
    if (row.year !== config.years[i] || !same(row.period, config.periods[i]) || !Number.isSafeInteger(row.joined_count) || row.joined_count < 10 || row.joined_count > 32 ||
        !Array.isArray(row.scene_ids) || row.scene_ids.length !== row.joined_count || new Set(row.scene_ids).size !== row.joined_count || row.scene_ids.some(id => typeof id !== "string" || !id) ||
        !Array.isArray(row.acquired_ms) || row.acquired_ms.length !== row.joined_count || row.acquired_ms.some(ms => !Number.isFinite(ms) || ms < Date.parse(row.period[0]) || ms >= Date.parse(row.period[1]))) throw new Error("Invalid acquisition dates/IDs");
  });
  const b = manifest.display_bounds;
  if (!Array.isArray(b) || b.length !== 2 || b.some(row => !Array.isArray(row) || row.length !== 2 || row.some(value => !Number.isFinite(value))) ||
      b[0][0] >= b[1][0] || b[0][1] >= b[1][1] || b[0][0] < -2 || b[1][0] > 1 || b[0][1] < -79 || b[1][1] > -76 ||
      (manifest.candidate_status === "ready" && (!Number.isSafeInteger(manifest.candidate_count) || manifest.candidate_count < 0 || manifest.candidate_count > 20000)) ||
      !Array.isArray(manifest.input_chunks) || !manifest.input_chunks.length || manifest.input_chunks.some(row => !hash(row.sha256)) ||
      !Array.isArray(manifest.tiles) || !manifest.tiles.length || manifest.tiles.length > 20000) throw new Error("Invalid river extent/assets");
  if (!same([b[0][1], b[0][0], b[1][1], b[1][0]], receipt.processing_block.bbox)) throw new Error("Wrong displayed block");
  const urls = new Set();
  for (const row of manifest.tiles) {
    const match = /^assets\/images\/rivers\/(2019|2024)\/(\d+)\/(\d+)\/(\d+)\.webp$/.exec(row.url);
    if (!match || Number(match[2]) < 8 || Number(match[2]) > 13 || Number(match[3]) >= 2 ** Number(match[2]) || Number(match[4]) >= 2 ** Number(match[2]) ||
        !hash(row.sha256) || !Number.isSafeInteger(row.size_bytes) || row.size_bytes <= 0 || urls.has(row.url)) throw new Error("Invalid tile inventory");
    urls.add(row.url);
  }
  for (const url of urls) if (!urls.has(url.replace(/\/(2019|2024)\//, (_, year) => `/${year === "2019" ? "2024" : "2019"}/`))) throw new Error("Unpaired provincial tile");
  return manifest;
}

export function validateRiverCandidates(collection, manifest) {
  if (collection?.type !== "FeatureCollection" || !Array.isArray(collection.features) || collection.features.length !== manifest.candidate_count) throw new Error("Invalid screening count");
  const cells = new Set();
  for (const feature of collection.features) {
    const p = feature.properties, c = feature.geometry?.coordinates;
    if (feature.geometry?.type !== "Point" || !Array.isArray(c) || c.length !== 2 || c.some(x => !Number.isFinite(x)) || c[0] < -79 || c[0] > -76 || c[1] < -2 || c[1] > 1 ||
        p?.kind !== "water-frequency-change-candidate" || p.status !== "unreviewed" || JSON.stringify(p.years) !== "[2019,2024]" || p.sampling_m !== 10 || p.screening_cell_m !== 1000 ||
        p.min_observations !== 10 || p.water_threshold !== 0.2 || p.change_threshold !== 0.5 || !Number.isSafeInteger(p.cell_id) || cells.has(p.cell_id) ||
        [p.gain_ha, p.loss_ha].some(x => !Number.isFinite(x) || x < 0 || x > 100.001) || p.gain_ha + p.loss_ha < 0.9999) throw new Error("Invalid screening cell");
    cells.add(p.cell_id);
    if (manifest.display_bounds) {
      const [southwest, northeast] = manifest.display_bounds, margin = 0.015;
      if (c[0] < southwest[1] - margin || c[0] > northeast[1] + margin || c[1] < southwest[0] - margin || c[1] > northeast[0] + margin) throw new Error("Screening candidate outside displayed block");
    }
  }
  return collection;
}

export function mountNapoRivers({L, map, t, language, onChange, onActivate, focus}) {
  const find = id => document.getElementById(id);
  const toggle = find("rivers-toggle"), signals = find("rivers-signals"), time = find("rivers-time"), split = find("rivers-split");
  const toolbar = find("rivers-toolbar"), divider = find("rivers-divider");
  let manifest, candidates, layers = [], markers, state = "loading", active = false, failed = false;
  const params = new URLSearchParams(window.location.search);
  time.value = params.get("view") === "rivers" && ["2019", "2024"].includes(params.get("year")) ? params.get("year") : "compare";
  const initialSplit = Number(params.get("split"));
  split.value = params.has("split") && Number.isFinite(initialSplit) ? String(Math.max(0, Math.min(100, initialSplit))) : "50";
  const number = value => new Intl.NumberFormat(language(), {maximumFractionDigits: 1}).format(value);
  map.createPane("napo-rivers"); map.getPane("napo-rivers").style.zIndex = "310";
  map.getPane("napo-rivers").style.pointerEvents = "none";
  function syncUrl() {
    const url = new URL(window.location.href);
    if (active) {
      url.searchParams.set("view", "rivers"); url.searchParams.set("year", time.value); url.searchParams.set("split", split.value);
      url.searchParams.delete("signal"); url.searchParams.delete("compare"); url.searchParams.delete("area"); url.searchParams.delete("lab");
    } else if (url.searchParams.get("view") === "rivers") for (const key of ["view", "year", "split"]) url.searchParams.delete(key);
    window.history.replaceState(window.history.state, "", url);
  }
  function clip() {
    const rect = map.getContainer().getBoundingClientRect();
    layers.forEach((layer, i) => layer.getContainer()?.querySelectorAll("img").forEach(image => {
      image.style.clipPath = time.value === "compare" ? screenClip(image.getBoundingClientRect(), rect, Number(split.value), i === 0 ? "earlier" : "later") : "none";
    }));
    divider.style.left = `${split.value}%`;
  }
  function render() {
    toggle.disabled = !manifest; signals.disabled = !manifest || !active || !candidates;
    toolbar.hidden = !active; divider.hidden = !active || time.value !== "compare";
    find("rivers-swipe").hidden = time.value !== "compare";
    find("rivers-status").textContent = t(`rivers.${state}`);
    find("rivers-scope").textContent = `${manifest ? `${t("rivers.block")} ${manifest.receipt.processing_block.id} / 0–8 · ` : ""}${t(map.getZoom() > 14 ? "rivers.zoomLimit" : "rivers.scope")}`;
    find("rivers-count").textContent = candidates ? `${number(manifest.candidate_count)} · ${t("rivers.unreviewed")}` : t("rivers.awaitingSignals");
    find("rivers-legend-year").textContent = time.value === "compare" ? "2019 ↔ 2024" : time.value;
    find("rivers-marker-legend").hidden = !active || !signals.checked || !manifest?.candidate_count;
    clip();
  }
  function clear() {
    layers.forEach(layer => map.removeLayer(layer)); layers = [];
    if (markers) map.removeLayer(markers);
    markers = undefined;
  }
  function renderMarkers() {
    if (markers) map.removeLayer(markers);
    markers = undefined;
    if (!active || !signals.checked || !candidates) return;
    markers = L.geoJSON(candidates, {pointToLayer: (_, latlng) => L.circleMarker(latlng, {radius: 7, color: "#ffb15f", fillColor: "#171e20", fillOpacity: 0.9, weight: 2}),
      onEachFeature: (feature, layer) => {
        const p = feature.properties, card = document.createElement("div");
        const title = document.createElement("strong"), copy = document.createElement("p"), counts = document.createElement("p"), caution = document.createElement("p"), link = document.createElement("a");
        title.textContent = t("rivers.candidateTitle"); copy.textContent = t("rivers.candidateCopy");
        counts.textContent = `2019 ↔ 2024 · ${t("rivers.gain")}: ${number(p.gain_ha)} ha · ${t("rivers.loss")}: ${number(p.loss_ha)} ha`;
        caution.textContent = t("rivers.caution"); link.textContent = t("rivers.method");
        link.href = "https://github.com/henryconteron/fallas-ecuador/blob/main/documentation/napo-rivers.md"; link.target = "_blank"; link.rel = "noopener noreferrer";
        card.append(title, copy, counts, caution, link); layer.bindPopup(card);
      }}).addTo(map);
    render(); onChange();
  }
  function draw() {
    clear(); failed = false;
    if (!active || !manifest) { render(); onChange(); return; }
    const requested = time.value === "compare" ? [2019, 2024] : [Number(time.value)];
    layers = requested.map(year => {
      const layer = L.tileLayer(`assets/images/rivers/${year}/{z}/{x}/{y}.webp?v=${manifest.receipt_sha256.slice(0, 12)}`, {
        pane: "napo-rivers", tileSize: 512, zoomOffset: -1, minNativeZoom: 9, maxNativeZoom: 14, minZoom: 0, maxZoom: 19,
        bounds: manifest.display_bounds, noWrap: true, attribution: 'Modified Copernicus Sentinel data (2019, 2024) · Cloud Score+ · geoBoundaries v6'});
      layer.on("tileload", clip);
      layer.on("tileerror", () => {
        if (failed || !layers.includes(layer)) return;
        failed = true; active = false; toggle.checked = false; state = "error"; clear(); syncUrl(); render(); onChange();
      });
      return layer;
    });
    layers.forEach(layer => layer.addTo(map)); state = "visible"; renderMarkers(); render(); onChange();
  }
  function setEnabled(enabled, fit = false) {
    active = Boolean(enabled && manifest); toggle.checked = active;
    if (active) { onActivate(); focus(); if (fit) map.fitBounds(manifest.display_bounds, {padding: [20, 20]}); }
    state = manifest ? active ? "visible" : "ready" : state;
    syncUrl(); draw();
  }
  toggle.addEventListener("change", () => setEnabled(toggle.checked, true));
  find("rivers-hide").addEventListener("click", () => setEnabled(false));
  find("rivers-fit").addEventListener("click", () => map.fitBounds(manifest.display_bounds, {padding: [20, 20]}));
  signals.addEventListener("change", renderMarkers);
  time.addEventListener("change", () => { syncUrl(); draw(); });
  split.addEventListener("input", () => { clip(); syncUrl(); });
  window.addEventListener("popstate", () => {
    const current = new URLSearchParams(window.location.search);
    if (current.get("view") === "rivers") {
      time.value = ["2019", "2024"].includes(current.get("year")) ? current.get("year") : "compare";
      const value = Number(current.get("split"));
      split.value = current.has("split") && Number.isFinite(value) ? String(Math.max(0, Math.min(100, value))) : "50";
      setEnabled(true);
    } else if (active) setEnabled(false);
  });
  map.on("move zoom zoomend resize viewreset", clip); map.on("zoomend", render);
  let frame;
  map.on("zoomstart", () => { const animate = () => { clip(); frame = requestAnimationFrame(animate); }; if (active) frame = requestAnimationFrame(animate); });
  map.on("zoomend", () => { if (frame) cancelAnimationFrame(frame); frame = undefined; });
  async function load() {
    try {
      const replies = await Promise.all(["data/rivers/napo-config.json", "data/rivers/napo-manifest.json"].map(url => fetch(url, {cache: "no-store"})));
      if (replies.some(reply => !reply.ok)) throw new Error("Missing provincial bundle");
      const [config, document] = await Promise.all(replies.map(reply => reply.json()));
      manifest = validateRiverManifest(document, config);
      if (manifest?.candidate_status === "ready") {
        const reply = await fetch("data/rivers/napo-candidates.geojson", {cache: "no-store"});
        if (!reply.ok) throw new Error("Missing screening observations");
        const bytes = await reply.arrayBuffer();
        const hash = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", bytes)), x => x.toString(16).padStart(2, "0")).join("");
        if (hash !== manifest.candidates_sha256) throw new Error("Screening observations changed");
        candidates = validateRiverCandidates(JSON.parse(new TextDecoder().decode(bytes)), manifest);
      }
      state = manifest ? "ready" : "pending";
    } catch { manifest = undefined; state = "error"; }
    render(); onChange();
    if (manifest && params.get("view") === "rivers") setEnabled(true, true);
  }
  render(); void load();
  return {render: () => { render(); if (markers) renderMarkers(); }, setEnabled,
    isActive: () => active, context: () => ({id: "rivers", name: t("rivers.title"), resolution: "Sentinel-2 · 10 m · 2019 / 2024", limit: t("rivers.caution")})};
}
