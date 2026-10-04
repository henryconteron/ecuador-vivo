/** Provincial 10 m display tiles; screening markers are not confirmed events. */
import {screenClip} from "./spectral-map.js?v=20260930-8";
import {orderedRiverCells, riverCellFromParam, adjacentRiverCell} from "./rivers-review.js?v=20261001-2";
import {mountRiverObservations} from "./rivers-observations.js?v=20261001-4";

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
    if (config.scene_selection?.mode === "frozen-inventory-acquisition-tile-latest-generation-v1") {
      const pinned = config.scene_selection.pinned_scene_ids;
      if (config.scene_selection.no_refill !== true || !hash(config.scene_selection.plan_sha256) || !hash(config.scene_selection.source_manifest_sha256)) throw new Error("Missing pinned plan provenance");
      if (!Array.isArray(pinned) || pinned.length !== 2 || !same(pinned[i], row.scene_ids)) throw new Error("Actual observations differ from pinned deduplicated plan");
      const groups = row.scene_ids.map(id => { const parts = id.split("_"); if (!/^\d{8}T\d{6}_\d{8}T\d{6}_T\d{2}[A-Z]{3}$/.test(id)) throw new Error("Malformed pinned scene ID"); return `${parts[0]}_${parts[2]}`; });
      if (new Set(groups).size !== groups.length) throw new Error("Repeated pass/tile in deduplicated plan");
    }
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
  if (manifest.candidate_status === "ready") {
    const s = manifest.screening, r = s?.count_receipt;
    if (s?.schema_version !== 1 || s.method !== "exact-count-fractions-local-8-connected-100px-1km-v1" || s.connectivity !== 8 || s.sampling_m !== 10 ||
        !hash(s.receipt_sha256) || !hash(s.builder_sha256) || s.rgb_receipt_sha256 !== manifest.receipt_sha256 || !Number.isFinite(Date.parse(s.built_at)) ||
        !Number.isSafeInteger(s.comparable_pixels) || s.comparable_pixels < 1 || s.comparable_pixels > config.max_pixels ||
        ![s.retained_pixels?.gain, s.retained_pixels?.loss].every(x => Number.isSafeInteger(x) && x >= 0) ||
        s.retained_pixels.gain + s.retained_pixels.loss > s.comparable_pixels ||
        !Array.isArray(s.input_chunks) || !s.input_chunks.length || s.input_chunks.length > 100 ||
        new Set(s.input_chunks.map(row => row.name)).size !== s.input_chunks.length ||
        s.input_chunks.some(row => typeof row.name !== "string" || !/^[\w.-]+\.tif$/.test(row.name) || !hash(row.sha256) || !Number.isSafeInteger(row.size_bytes) || row.size_bytes < 1) ||
        !same(s.count_bands, ["y2019_water_count", "y2019_valid_count", "y2024_water_count", "y2024_valid_count"]) ||
        s.count_encoding !== "exact-water-and-valid-observation-counts-zero-valid-is-nodata" || r?.product !== "water-observation-counts" ||
        r.count_dtype !== "uint8" || !same(r.count_bands, s.count_bands) || r.count_encoding !== s.count_encoding) throw new Error("Missing exact-count screening provenance");
    for (const key of Object.keys(config).filter(key => !["file_dimensions", "max_pixels", "attribution"].includes(key))) {
      if (!same(r[key], receipt[key])) throw new Error(`Screening/RGB method mismatch: ${key}`);
    }
    for (const key of ["scenes", "processing_block", "boundary"]) if (!same(r[key], receipt[key])) throw new Error(`Screening/RGB observations mismatch: ${key}`);
    if (!Number.isFinite(r.area_m2) || Math.abs(r.area_m2 - receipt.area_m2) > 1 || !Number.isFinite(Date.parse(r.export_requested_at))) throw new Error("Screening province/date mismatch");
  }
  return manifest;
}

export function validateRiverCandidates(collection, manifest) {
  if (collection?.type !== "FeatureCollection" || !Array.isArray(collection.features) || collection.features.length !== manifest.candidate_count) throw new Error("Invalid screening count");
  const cells = new Set();
  if (manifest.screening && JSON.stringify(collection.metadata) !== JSON.stringify(manifest.screening)) throw new Error("Screening metadata changed");
  for (const feature of collection.features) {
    const p = feature.properties, c = feature.geometry?.coordinates;
    if (feature.geometry?.type !== "Point" || !Array.isArray(c) || c.length !== 2 || c.some(x => !Number.isFinite(x)) || c[0] < -79 || c[0] > -76 || c[1] < -2 || c[1] > 1 ||
        p?.kind !== "water-frequency-change-candidate" || p.status !== "unreviewed" || JSON.stringify(p.years) !== "[2019,2024]" || p.sampling_m !== 10 || p.screening_cell_m !== 1000 ||
        p.min_observations !== 10 || p.water_threshold !== 0.2 || p.change_threshold !== 0.5 || !Number.isSafeInteger(p.cell_id) || cells.has(p.cell_id) ||
        [p.gain_ha, p.loss_ha].some(x => !Number.isFinite(x) || x < 0 || x > 100.001) || p.gain_ha + p.loss_ha < 0.9999) throw new Error("Invalid screening cell");
    cells.add(p.cell_id);
    if (manifest.screening) {
      const x = 6378137 * c[0] * Math.PI / 180;
      const y = 6378137 * Math.log(Math.tan(Math.PI / 4 + c[1] * Math.PI / 360));
      const column = Math.floor(x / 1000), row = Math.floor(-y / 1000);
      if (p.cell_id !== column + row * 100000 || Math.abs(x - (column + 0.5) * 1000) > 0.01 || Math.abs(y + (row + 0.5) * 1000) > 0.01 ||
          !Number.isSafeInteger(p.comparable_pixels) || p.comparable_pixels > 10000 || p.comparable_pixels < Math.round((p.gain_ha + p.loss_ha) * 100)) throw new Error("Invalid cell centre/support");
    }
    if (manifest.display_bounds) {
      const [southwest, northeast] = manifest.display_bounds, margin = 0.015;
      if (c[0] < southwest[1] - margin || c[0] > northeast[1] + margin || c[1] < southwest[0] - margin || c[1] > northeast[0] + margin) throw new Error("Screening candidate outside displayed block");
    }
  }
  return collection;
}

export function mountNapoRivers({L, map, t, language, onChange, onActivate, focus}) {
  const find = id => document.getElementById(id);
  const observations = mountRiverObservations({t, language});
  const toggle = find("rivers-toggle"), signals = find("rivers-signals"), time = find("rivers-time"), split = find("rivers-split");
  const toolbar = find("rivers-toolbar"), divider = find("rivers-divider");
  const cellSelect = find("rivers-cell"), cellPrevious = find("rivers-previous"), cellNext = find("rivers-next"), cellInspect = find("rivers-inspect");
  let manifest, candidates, layers = [], markers, cellOutline, state = "loading", active = false, failed = false, popupVisible = false;
  let cells = [], selectedCell = null, optionLanguage;
  const cellLayers = new Map();
  const params = new URLSearchParams(window.location.search);
  time.value = params.get("view") === "rivers" && ["2019", "2024"].includes(params.get("year")) ? params.get("year") : "compare";
  const initialSplit = Number(params.get("split"));
  split.value = params.has("split") && Number.isFinite(initialSplit) ? String(Math.max(0, Math.min(100, initialSplit))) : "50";
  const number = value => new Intl.NumberFormat(language(), {maximumFractionDigits: 1}).format(value);
  const areaNumber = value => new Intl.NumberFormat(language(), {maximumFractionDigits: 2}).format(value);
  map.createPane("napo-rivers"); map.getPane("napo-rivers").style.zIndex = "310";
  map.getPane("napo-rivers").style.pointerEvents = "none";
  function syncUrl() {
    const url = new URL(window.location.href);
    if (active) {
      url.searchParams.set("view", "rivers"); url.searchParams.set("year", time.value); url.searchParams.set("split", split.value);
      url.searchParams.delete("signal"); url.searchParams.delete("compare"); url.searchParams.delete("area"); url.searchParams.delete("lab");
      if (signals.checked && selectedCell !== null) url.searchParams.set("cell", String(selectedCell));
      else url.searchParams.delete("cell");
    } else if (url.searchParams.get("view") === "rivers") for (const key of ["view", "year", "split", "cell"]) url.searchParams.delete(key);
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
    toolbar.hidden = !active; divider.hidden = !active || time.value !== "compare" || popupVisible;
    find("rivers-swipe").hidden = time.value !== "compare";
    find("rivers-status").textContent = t(`rivers.${state}`);
    find("rivers-scope").textContent = `${manifest ? `${t("rivers.block")} ${manifest.receipt.processing_block.id} / 0–8 · ` : ""}${t(map.getZoom() > 14 ? "rivers.zoomLimit" : "rivers.scope")}`;
    find("rivers-count").textContent = candidates ? `${number(manifest.candidate_count)} · ${t("rivers.unreviewed")}` : t("rivers.awaitingSignals");
    find("rivers-legend-year").textContent = time.value === "compare" ? "2019 ↔ 2024" : time.value;
    find("rivers-marker-legend").hidden = !active || !signals.checked || !manifest?.candidate_count;
    cellSelect.disabled = cellPrevious.disabled = cellNext.disabled = !active || !cells.length;
    cellInspect.disabled = !active || selectedCell === null;
    if (optionLanguage !== language() || cellSelect.options.length !== cells.length + 1) {
      cellSelect.replaceChildren();
      const placeholder = document.createElement("option"); placeholder.value = ""; placeholder.textContent = t("rivers.chooseCell"); cellSelect.append(placeholder);
      for (const cell of cells) {
        const p = cell.properties, option = document.createElement("option");
        option.value = String(p.cell_id); option.textContent = `${p.cell_id} · ${areaNumber(p.gain_ha + p.loss_ha)} ha`;
        cellSelect.append(option);
      }
      optionLanguage = language();
    }
    cellSelect.value = selectedCell === null ? "" : String(selectedCell);
    find("rivers-cell-position").textContent = selectedCell === null ? t("rivers.cellOrder") : `${cells.findIndex(cell => cell.properties.cell_id === selectedCell) + 1} / ${cells.length} · ${t("rivers.notReviewed")}`;
    clip();
  }
  function clear() {
    layers.forEach(layer => map.removeLayer(layer)); layers = [];
    if (markers) map.removeLayer(markers);
    markers = undefined;
    cellLayers.clear();
    popupVisible = false;
    if (cellOutline) map.removeLayer(cellOutline); cellOutline = undefined;
  }
  function renderMarkers() {
    if (cellOutline) map.removeLayer(cellOutline); cellOutline = undefined;
    if (markers) map.removeLayer(markers);
    markers = undefined;
    cellLayers.clear();
    if (!active || !signals.checked || !candidates) { render(); onChange(); return; }
    markers = L.geoJSON(candidates, {pointToLayer: (_, latlng) => L.circleMarker(latlng, {radius: 7, color: "#ffb15f", fillColor: "#171e20", fillOpacity: 0.9, weight: 2}),
      onEachFeature: (feature, layer) => {
        const p = feature.properties, card = document.createElement("div");
        const title = document.createElement("strong"), copy = document.createElement("p"), counts = document.createElement("p"), support = document.createElement("p"), caution = document.createElement("p"), link = document.createElement("a"), zoom = document.createElement("button");
        title.textContent = `${t("rivers.candidateTitle")} · ${p.cell_id}`; copy.textContent = t("rivers.candidateCopy");
        counts.textContent = `2019 ↔ 2024 · ${t("rivers.gain")}: ${areaNumber(p.gain_ha)} ha · ${t("rivers.loss")}: ${areaNumber(p.loss_ha)} ha`;
        caution.textContent = t("rivers.caution"); link.textContent = t("rivers.method");
        support.textContent = `${t("rivers.support")}: ${number(p.comparable_pixels / 100)}% · ${t("rivers.minimumSupport")}`;
        zoom.type = "button"; zoom.textContent = t("rivers.inspectCell");
        const centre = L.CRS.EPSG3857.project(layer.getLatLng());
        const bounds = L.latLngBounds(L.CRS.EPSG3857.unproject(L.point(centre.x - 500, centre.y - 500)), L.CRS.EPSG3857.unproject(L.point(centre.x + 500, centre.y + 500)));
        cellLayers.set(p.cell_id, {layer, bounds});
        zoom.addEventListener("click", () => inspectCell(p.cell_id));
        link.href = "https://github.com/henryconteron/ecuador-vivo/blob/main/documentation/napo-rivers.md"; link.target = "_blank"; link.rel = "noopener noreferrer";
        card.append(title, copy, counts, support, caution, zoom, link);
        layer.bindPopup(card, {maxHeight: 260, autoPanPaddingTopLeft: [16, 100], autoPanPaddingBottomRight: [16, 65]});
        layer.on("add", () => {
          const element = layer.getElement();
          if (!element) return;
          element.setAttribute("role", "button"); element.setAttribute("tabindex", "0");
          element.setAttribute("aria-label", `${t("rivers.candidateTitle")} · ${p.cell_id}`);
          element.addEventListener("keydown", event => {
            if (event.key === "Enter" || event.key === " ") { event.preventDefault(); event.stopPropagation(); layer.openPopup(); }
            if (event.key === "Escape") { event.stopPropagation(); layer.closePopup(); }
          });
        });
        layer.on("popupopen", () => {
          selectedCell = p.cell_id; popupVisible = true; syncUrl(); render();
          if (cellOutline) map.removeLayer(cellOutline);
          cellOutline = L.rectangle(bounds, {color: "#ffb15f", weight: 1, dashArray: "5 5", fill: false, interactive: false}).addTo(map);
        });
        layer.on("popupclose", () => { if (cellOutline) map.removeLayer(cellOutline); cellOutline = undefined; popupVisible = false; render(); });
      }}).addTo(map);
    render(); onChange();
  }
  function inspectCell(id) {
    if (!active || riverCellFromParam(String(id), cells) === null) return;
    selectedCell = id;
    if (!signals.checked) { signals.checked = true; renderMarkers(); }
    const entry = cellLayers.get(id);
    if (!entry) return;
    map.closePopup(); map.stop();
    map.fitBounds(entry.bounds, {padding: [45, 45], maxZoom: 14, animate: false});
    entry.layer.openPopup(); syncUrl(); render();
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
    if (!active) selectedCell = null;
    if (active) { onActivate(); focus(); if (fit) map.fitBounds(manifest.display_bounds, {padding: [20, 20]}); }
    state = manifest ? active ? "visible" : "ready" : state;
    syncUrl(); draw();
  }
  toggle.addEventListener("change", () => setEnabled(toggle.checked, true));
  find("rivers-hide").addEventListener("click", () => setEnabled(false));
  find("rivers-fit").addEventListener("click", () => map.fitBounds(manifest.display_bounds, {padding: [20, 20]}));
  signals.addEventListener("change", () => { if (!signals.checked) selectedCell = null; syncUrl(); renderMarkers(); });
  cellSelect.addEventListener("change", () => {
    const id = riverCellFromParam(cellSelect.value, cells);
    if (id !== null) inspectCell(id);
    else { selectedCell = null; map.closePopup(); syncUrl(); render(); }
  });
  cellPrevious.addEventListener("click", () => inspectCell(adjacentRiverCell(cells, selectedCell, -1)));
  cellNext.addEventListener("click", () => inspectCell(adjacentRiverCell(cells, selectedCell, 1)));
  cellInspect.addEventListener("click", () => inspectCell(selectedCell));
  time.addEventListener("change", () => { syncUrl(); draw(); });
  split.addEventListener("input", () => { clip(); syncUrl(); });
  window.addEventListener("popstate", () => {
    const current = new URLSearchParams(window.location.search);
    if (current.get("view") === "rivers") {
      time.value = ["2019", "2024"].includes(current.get("year")) ? current.get("year") : "compare";
      const value = Number(current.get("split"));
      split.value = current.has("split") && Number.isFinite(value) ? String(Math.max(0, Math.min(100, value))) : "50";
      setEnabled(true);
      const id = riverCellFromParam(current.get("cell"), cells);
      selectedCell = id;
      if (id !== null) inspectCell(id);
      else { syncUrl(); render(); }
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
        cells = orderedRiverCells(candidates);
      }
      state = manifest ? "ready" : "pending";
      observations.setManifest(manifest);
    } catch { manifest = undefined; observations.setManifest(null); state = "error"; }
    render(); onChange();
    if (manifest && params.get("view") === "rivers") {
      const id = riverCellFromParam(params.get("cell"), cells);
      setEnabled(true, id === null);
      if (id !== null) inspectCell(id);
    }
  }
  render(); void load();
  return {render: () => { render(); observations.render(); if (markers) renderMarkers(); }, setEnabled,
    isActive: () => active, context: () => ({id: "rivers", name: t("rivers.title"), resolution: "Sentinel-2 · 10 m · 2019 / 2024", limit: t("rivers.caution")})};
}
