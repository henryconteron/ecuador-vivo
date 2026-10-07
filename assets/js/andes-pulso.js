/** A frozen, verifiable case. Never query the live earthquake service here. */
export const CASE_ID = "memoria-sismica-1900-2025";
export const CASE_BASE = `data/cases/${CASE_ID}/`;
export const SNAPSHOT_SHA256 = "8cf19180b19b9a9998f76f1feee9bf88b69d141287a9d213e3455f20c1b2d5c8";
export const PAGE_SIZE = 20;
export const STORY_REGISTRY = "data/cases/registry.json";

export function storyStatusLabel(status, language = "es") {
  const labels = {
    data_ready: { es: "datos preparados", en: "data prepared" },
    draft: { es: "borrador", en: "draft" },
    published: { es: "publicado", en: "published" },
  };
  return labels[status]?.[language] ?? (language === "en" ? "in preparation" : "en preparación");
}

function storyText(record, field, language) {
  return record[`${field}_${language}`] ?? record[`${field}_es`] ?? "";
}

function appendStoryFileLinks(parent, record, language) {
  const links = document.createElement("div");
  links.className = "case-story-links";
  for (const file of record.files ?? []) {
    const link = document.createElement("a");
    link.href = file.href;
    link.textContent = `${file[`label_${language}`] ?? file.label_es} ↗`;
    link.setAttribute("download", "");
    links.append(link);
  }
  parent.append(links);
}

function appendCaseVideo(parent, record, language) {
  const href = record.video?.href;
  if (typeof href !== "string" || !/^assets\/media\/andes-pulso\/[a-z0-9-]+\/ecuador-vivo\.mp4$/.test(href)) return;
  const wrap = document.createElement("div");
  wrap.className = "case-story-video-wrap";
  const video = document.createElement("video");
  video.className = "case-story-video";
  video.controls = true;
  video.playsInline = true;
  video.preload = "metadata";
  video.src = href;
  video.setAttribute("aria-label", language === "en" ? "Video and map animation for this case" : "Video y animación cartográfica del caso");
  const poster = record.video.poster;
  if (typeof poster === "string" && /^assets\/media\/andes-pulso\/[a-z0-9-]+\/poster\.png$/.test(poster)) video.poster = poster;
  wrap.append(video);
  parent.append(wrap);
}

function metricText(value, units, language = "es", digits = 2) {
  if (!Number.isFinite(value)) return "—";
  const locale = language === "en" ? "en-US" : "es-EC";
  const number = value.toLocaleString(locale, { maximumFractionDigits: digits });
  return `${number}${units ? ` ${units}` : ""}`;
}

function appendStoryEvidence(article, record, evidence, language) {
  const detail = document.createElement("details");
  detail.className = "case-story-evidence";
  const summaryLine = document.createElement("summary");
  summaryLine.textContent = language === "en" ? "Metrics shown in the video" : "Cifras que aparecen en el video";
  detail.append(summaryLine);
  const metrics = evidence.summary ?? {};
  const copy = evidence.display_copy ?? {};
  const unit = metrics.units ?? "";
  const aggregateUnit = metrics.aggregate_units ?? unit;
  const rows = [
    [copy.date_label ?? (language === "en" ? "Highlighted date" : "Fecha destacada"), metricText(metrics.peak_date_mean, unit, language), metrics.peak_date],
    [copy.period_label ?? (language === "en" ? "Highlighted period" : "Período destacado"), metricText(metrics.peak_month_value, aggregateUnit, language), metrics.peak_month],
    [(language === "en" ? "Period spatial mean" : "Promedio espacial del período"), metricText(metrics.mean_period, unit, language)],
    [Array.isArray(copy.maximum_labels) ? copy.maximum_labels.filter(Boolean).join(" ") : (language === "en" ? "Maximum" : "Máximo"), metricText(metrics.peak_pixel_value, unit, language), metrics.peak_pixel_date],
  ];
  const list = document.createElement("dl");
  list.className = "case-story-metrics";
  for (const [label, value, when] of rows) {
    if (value === "—") continue;
    const term = document.createElement("dt");
    term.textContent = label;
    const description = document.createElement("dd");
    description.textContent = [value, when].filter(Boolean).join(" · ");
    list.append(term, description);
  }
  detail.append(list);

  const ranking = metrics.province_rank ?? metrics.city_rank ?? [];
  if (ranking.length) {
    const caption = document.createElement("p");
    caption.className = "case-story-table-caption";
    caption.textContent = language === "en" ? "Provincial values used for the ranking" : "Valores provinciales usados en el ranking";
    const scroll = document.createElement("div");
    scroll.className = "case-story-table-scroll";
    const table = document.createElement("table");
    table.className = "case-story-metric-table";
    const head = document.createElement("thead");
    const header = document.createElement("tr");
    for (const label of [language === "en" ? "Rank" : "Puesto", language === "en" ? "Province" : "Provincia", language === "en" ? "Value" : "Valor"]) {
      const cell = document.createElement("th");
      cell.scope = "col";
      cell.textContent = label;
      header.append(cell);
    }
    head.append(header);
    const body = document.createElement("tbody");
    ranking.forEach((row, index) => {
      const tr = document.createElement("tr");
      for (const value of [String(index + 1), String(row.name ?? ""), metricText(row.value, metrics.city_rank_units ?? aggregateUnit, language, metrics.decimals ?? 1)]) {
        const cell = document.createElement("td");
        cell.textContent = value;
        tr.append(cell);
      }
      body.append(tr);
    });
    table.append(head, body);
    scroll.append(table);
    detail.append(caption, scroll);
  }
  if (metrics.scope) {
    const scope = document.createElement("p");
    scope.className = "case-story-scope";
    scope.textContent = metrics.scope;
    detail.append(scope);
  }
  const warnings = Array.isArray(metrics.warnings) ? metrics.warnings : [];
  if (warnings.length) {
    const warningList = document.createElement("ul");
    warningList.className = "case-story-warnings";
    for (const warning of warnings) {
      const item = document.createElement("li");
      item.textContent = warning;
      warningList.append(item);
    }
    detail.append(warningList);
  }
  article.append(detail);
}

export function renderStoryCatalog(records, language = "es", container = document.getElementById("case-catalog")) {
  if (!container) return;
  container.replaceChildren();
  if (!Array.isArray(records) || !records.length) {
    const empty = document.createElement("p");
    empty.textContent = language === "en" ? "No stories are registered yet." : "Todavía no hay historias registradas.";
    container.append(empty);
    return;
  }
  for (const record of records) {
    const article = document.createElement("article");
    article.className = `case-story-card case-story-${record.kind ?? "general"}`;
    article.dataset.caseId = record.id ?? "";
    const header = document.createElement("div");
    header.className = "case-story-card-header";
    const kind = document.createElement("span");
    kind.className = "case-story-kind";
    kind.textContent = record.kind ?? "story";
    const status = document.createElement("span");
    status.className = "case-story-status";
    status.textContent = storyStatusLabel(record.status, language);
    header.append(kind, status);
    const title = document.createElement("h3");
    title.textContent = storyText(record, "title", language);
    const hook = document.createElement("p");
    hook.className = "case-story-hook";
    hook.textContent = storyText(record, "hook", language);
    const question = document.createElement("p");
    question.className = "case-story-question";
    question.textContent = storyText(record, "question", language);
    const facts = document.createElement("dl");
    facts.className = "case-story-facts";
    for (const [label, value] of [
      [language === "en" ? "Period" : "Periodo", storyText(record, "period", language)],
      [language === "en" ? "Sources" : "Fuentes", storyText(record, "sources", language)],
      [language === "en" ? "Territory" : "Territorio", (record.territories ?? []).join(" · ")],
    ]) {
      const term = document.createElement("dt");
      term.textContent = label;
      const detail = document.createElement("dd");
      detail.textContent = value;
      facts.append(term, detail);
    }
    const limits = document.createElement("p");
    limits.className = "case-story-limits";
    limits.textContent = `${language === "en" ? "Limit: " : "Límite: "}${storyText(record, "limits", language)}`;
    article.append(header, title, hook, question);
    appendCaseVideo(article, record, language);
    article.append(facts, limits);
    appendStoryFileLinks(article, record, language);
    container.append(article);
  }
}

async function initStoryCatalog() {
  const container = document.getElementById("case-catalog");
  if (!container) return;
  let records;
  try {
    const response = await fetch(STORY_REGISTRY);
    if (!response.ok) throw new Error(`Registry HTTP ${response.status}`);
    const registry = await response.json();
    records = Array.isArray(registry.cases) ? registry.cases : [];
    window.__ecuadorVivoStoryRegistry = records;
  } catch (error) {
    console.error("Andes Pulso: story registry unavailable", error);
    container.textContent = "No se pudo cargar el catálogo; descarga el JSON para revisar las fichas.";
    return;
  }
  const language = window.portalLanguage?.() ?? (new URLSearchParams(location.search).get("lang") === "en" ? "en" : "es");
  renderStoryCatalog(records, language, container);
  for (const record of records) {
    const href = record.summary_href;
    if (typeof href !== "string" || !/^data\/cases\/[a-z0-9-]+\/summary\.json$/.test(href)) continue;
    try {
      const response = await fetch(href);
      if (!response.ok) continue;
      const evidence = await response.json();
      const article = [...container.querySelectorAll(".case-story-card")]
        .find((item) => item.dataset.caseId === record.id);
      if (article) appendStoryEvidence(article, record, evidence, language);
    } catch (error) {
      console.warn(`Andes Pulso: summary unavailable for ${record.id}`, error);
    }
  }
}

export function normalizeSnapshot(collection) {
  if (collection?.type !== "FeatureCollection" || !Array.isArray(collection.features)) {
    throw new Error("Invalid frozen catalog");
  }
  const ids = new Set();
  return collection.features.map((feature) => {
    const properties = feature.properties ?? {};
    const coordinates = feature.geometry?.coordinates ?? [];
    const id = String(feature.id ?? "");
    const [longitude, latitude, rawDepth] = coordinates;
    const magnitude = properties.mag;
    const time = properties.time;
    if (!id || ids.has(id) || feature.geometry?.type !== "Point"
      || !Number.isFinite(longitude) || !Number.isFinite(latitude)
      || longitude < -83 || longitude > -74.5 || latitude < -5.5 || latitude > 2.5
      || !Number.isFinite(magnitude) || magnitude < 4 || !Number.isFinite(time)
      || !Number.isFinite(new Date(time).getTime())) throw new Error("Invalid event in frozen catalog");
    ids.add(id);
    const year = new Date(time).getUTCFullYear();
    if (year < 1900 || year > 2025) throw new Error("Event outside frozen period");
    return {
      id, longitude, latitude, magnitude, time, year,
      depth: Number.isFinite(rawDepth) ? rawDepth : null,
      magnitudeType: String(properties.magType ?? ""),
      place: String(properties.place ?? ""),
    };
  }).sort((a, b) => b.time - a.time || a.id.localeCompare(b.id));
}

export function filterEvents(events, { from = 1900, to = 2025, magnitude = 4, search = "" } = {}) {
  const term = String(search).trim().toLocaleLowerCase();
  return events.filter((event) => event.year >= from && event.year <= to && event.magnitude >= magnitude
    && (!term || `${event.id} ${event.place}`.toLocaleLowerCase().includes(term)));
}

export function pageEvents(events, page = 0, size = PAGE_SIZE) {
  const pages = Math.max(1, Math.ceil(events.length / size));
  const selected = Math.max(0, Math.min(pages - 1, Math.trunc(page) || 0));
  return { rows: events.slice(selected * size, (selected + 1) * size), page: selected, pages };
}

export function depthGroup(depth) {
  if (!Number.isFinite(depth)) return "unknown";
  if (depth < 70) return "shallow";
  if (depth < 300) return "intermediate";
  return "deep";
}

export function summarizeEvents(events) {
  const summary = { count: events.length, shallow: 0, intermediate: 0, deep: 0, unknown: 0, maxDepth: null };
  for (const event of events) {
    summary[depthGroup(event.depth)] += 1;
    if (event.depth !== null && (summary.maxDepth === null || event.depth > summary.maxDepth)) summary.maxDepth = event.depth;
  }
  return summary;
}

export function eventURL(id) {
  return `https://earthquake.usgs.gov/earthquakes/eventpage/${encodeURIComponent(id)}`;
}

async function initCase() {
  const byId = (id) => document.getElementById(id);
  const form = byId("case-filters");
  if (!form) return;
  let language = window.portalLanguage?.() ?? (new URLSearchParams(location.search).get("lang") === "en" ? "en" : "es");
  const t = (es, en) => language === "en" ? en : es;
  const number = (value, maximumFractionDigits = 2) => Number(value).toLocaleString(language === "en" ? "en-US" : "es-EC", { maximumFractionDigits });
  let allEvents = [];
  let filtered = [];
  let currentPage = 0;
  let integrity = "pending";
  let map = null;
  let eventLayer = null;
  let mapError = "";
  let loadFailed = false;
  const markers = new Map();
  const colours = { shallow: "#e8bd5d", intermediate: "#b04b63", deep: "#3e3459", unknown: "#838c90" };
  const textNode = (tag, text, className) => {
    const node = document.createElement(tag);
    node.textContent = text;
    if (className) node.className = className;
    return node;
  };

  function showStatus() {
    const status = byId("case-status");
    if (loadFailed) {
      status.textContent = t("No se pudo verificar o cargar la copia conservada. Puedes descargar los archivos originales abajo; no se sustituyeron por datos actuales.", "The preserved snapshot could not be loaded or verified. You can download the original files below; no live data were substituted.");
      status.className = "case-error";
      return;
    }
    const integrityText = integrity === "verified"
      ? t("Integridad SHA-256 comprobada.", "SHA-256 integrity checked.")
      : t("Este navegador no permite comprobar SHA-256; consulta el manifiesto descargable.", "This browser cannot check SHA-256; see the downloadable manifest.");
    status.textContent = `${number(filtered.length)} ${t("de", "of")} ${number(allEvents.length)} ${t("registros", "records")} · ${integrityText}${mapError ? ` ${mapError}` : ""}`;
    status.className = "";
  }

  function popup(event) {
    const content = document.createElement("div");
    content.append(textNode("strong", event.place || event.id));
    content.append(textNode("p", `${new Date(event.time).toISOString().replace("T", " ").slice(0, 19)} UTC`));
    content.append(textNode("p", `M ${number(event.magnitude)} (${event.magnitudeType || "—"}) · ${t("Profundidad", "Depth")}: ${event.depth === null ? t("sin dato", "unknown") : `${number(event.depth)} km`}`));
    const link = textNode("a", t("Ver registro USGS ↗", "Open USGS record ↗"));
    link.href = eventURL(event.id);
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    content.append(link);
    return content;
  }

  function initialiseMap() {
    if (!window.L) {
      mapError = t("El mapa no está disponible; la tabla y las descargas sí.", "The map is unavailable; the table and downloads still work.");
      byId("case-map").append(textNode("p", mapError, "case-map-unavailable"));
      return;
    }
    const L = window.L;
    map = L.map("case-map", { preferCanvas: true, scrollWheelZoom: false }).setView([-1.5, -78.75], 6);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> · USGS',
      maxZoom: 18,
    }).addTo(map);
    L.rectangle([[-5.5, -83], [2.5, -74.5]], { color: "#4c7462", weight: 2, dashArray: "7 5", fill: false, interactive: false }).addTo(map);
    eventLayer = L.layerGroup().addTo(map);
    map.fitBounds([[-5.5, -83], [2.5, -74.5]], { padding: [16, 16] });
  }

  function drawMap() {
    if (!map) return;
    eventLayer.clearLayers();
    markers.clear();
    for (const event of filtered) {
      const marker = window.L.circleMarker([event.latitude, event.longitude], {
        radius: Math.max(3, (event.magnitude - 3) * 1.8),
        color: "#153529", weight: .65, fillColor: colours[depthGroup(event.depth)], fillOpacity: .77,
      }).bindPopup(() => popup(event)).addTo(eventLayer);
      markers.set(event.id, marker);
    }
  }

  function drawTable() {
    const page = pageEvents(filtered, currentPage);
    currentPage = page.page;
    const body = byId("case-rows");
    body.replaceChildren();
    if (!page.rows.length) {
      const row = document.createElement("tr");
      const cell = textNode("td", t("No hay registros con estos filtros.", "No records match these filters."));
      cell.colSpan = 6;
      row.append(cell);
      body.append(row);
    }
    for (const event of page.rows) {
      const row = document.createElement("tr");
      const date = new Date(event.time).toISOString().replace("T", " ").slice(0, 19);
      for (const value of [date, number(event.magnitude), event.magnitudeType || "—", event.depth === null ? t("Sin dato", "Unknown") : number(event.depth), event.place || event.id]) row.append(textNode("td", value));
      const actions = document.createElement("td");
      if (map) {
        const zoom = textNode("button", t("Mapa", "Map"));
        zoom.type = "button";
        zoom.setAttribute("aria-label", `${t("Ver en el mapa", "Show on map")}: ${event.id}`);
        zoom.addEventListener("click", () => {
          map.setView([event.latitude, event.longitude], Math.max(map.getZoom(), 8));
          markers.get(event.id)?.openPopup();
          byId("case-map").scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "center" });
          byId("case-map").focus({ preventScroll: true });
        });
        actions.append(zoom);
      }
      const link = textNode("a", "USGS ↗");
      link.href = eventURL(event.id);
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.setAttribute("aria-label", `USGS: ${event.id}`);
      actions.append(link);
      row.append(actions);
      body.append(row);
    }
    byId("case-prev").disabled = currentPage === 0;
    byId("case-next").disabled = currentPage >= page.pages - 1;
    byId("case-page").textContent = `${t("Página", "Page")} ${currentPage + 1} ${t("de", "of")} ${page.pages}`;
  }

  function drawSummary() {
    const s = summarizeEvents(allEvents);
    byId("case-derived").textContent = t(
      `${number(s.count)} registros: ${number(s.shallow)} con profundidad menor de 70 km; ${number(s.intermediate)} entre 70 y menos de 300 km; ${number(s.deep)} de 300 km o más; ${number(s.unknown)} sin profundidad. Máxima profundidad registrada: ${number(s.maxDepth)} km. Estas cifras corresponden al catálogo completo conservado, no al filtro de la tabla.`,
      `${number(s.count)} records: ${number(s.shallow)} with depth below 70 km; ${number(s.intermediate)} from 70 to less than 300 km; ${number(s.deep)} at 300 km or deeper; ${number(s.unknown)} with unknown depth. Maximum recorded depth: ${number(s.maxDepth)} km. These figures describe the full preserved catalog, not the table filter.`,
    );
  }

  function applyFilters() {
    const from = Number(byId("case-from").value);
    const to = Number(byId("case-to").value);
    byId("case-to").setCustomValidity(from > to ? t("El año final debe ser igual o posterior al inicial.", "The end year must not precede the start year.") : "");
    if (!form.reportValidity()) return;
    filtered = filterEvents(allEvents, { from, to, magnitude: Number(byId("case-mag").value), search: byId("case-search").value });
    currentPage = 0;
    drawMap();
    drawTable();
    showStatus();
  }

  form.addEventListener("submit", (event) => { event.preventDefault(); applyFilters(); });
  // Clear custom validity as soon as either year changes, allowing resubmission.
  for (const id of ["case-from", "case-to"]) byId(id).addEventListener("input", () => byId("case-to").setCustomValidity(""));
  form.addEventListener("reset", () => { byId("case-to").setCustomValidity(""); setTimeout(applyFilters, 0); });
  byId("case-prev").addEventListener("click", () => { currentPage -= 1; drawTable(); });
  byId("case-next").addEventListener("click", () => { currentPage += 1; drawTable(); });
  window.addEventListener("portal:language", (event) => {
    language = event.detail?.lang === "en" ? "en" : "es";
    byId("case-video").setAttribute("aria-label", t("Memoria sísmica 1900–2025 · video narrado en español", "Seismic memory 1900–2025 · Spanish-language video"));
    byId("case-map").setAttribute("aria-label", t("Mapa de epicentros del catálogo conservado", "Epicenter map of the preserved catalog"));
    if (allEvents.length) { drawMap(); drawTable(); drawSummary(); showStatus(); }
    else if (loadFailed) showStatus();
    const storyRecords = window.__ecuadorVivoStoryRegistry;
    if (storyRecords) renderStoryCatalog(storyRecords, language);
  });

  try {
    const response = await fetch(`${CASE_BASE}usgs_snapshot.geojson`);
    if (!response.ok) throw new Error(`Snapshot HTTP ${response.status}`);
    const bytes = await response.arrayBuffer();
    if (globalThis.crypto?.subtle) {
      const digest = await globalThis.crypto.subtle.digest("SHA-256", bytes);
      const sha = [...new Uint8Array(digest)].map((value) => value.toString(16).padStart(2, "0")).join("");
      if (sha !== SNAPSHOT_SHA256) throw new Error("Snapshot checksum mismatch");
      integrity = "verified";
    } else integrity = "unavailable";
    allEvents = normalizeSnapshot(JSON.parse(new TextDecoder().decode(bytes)));
    if (allEvents.length !== 2661) throw new Error("Snapshot count mismatch");
    initialiseMap();
    applyFilters();
    drawSummary();
  } catch (error) {
    loadFailed = true;
    console.error("Andes Pulso: frozen catalog unavailable", error);
    showStatus();
    byId("case-derived").textContent = t("No se calcularon cifras: descarga el archivo original para comprobarlo.", "No figures were calculated: download the original file to check them.");
    for (const control of form.elements) control.disabled = true;
  }
}

if (typeof document !== "undefined") initCase();
if (typeof document !== "undefined") initStoryCatalog();
