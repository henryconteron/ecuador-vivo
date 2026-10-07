/** Optional owner-configured cartography. No HTML from external sources is injected. */
const SYSTEMS = new Set(["earth", "water", "sky", "life", "risk"]);
export function validCustomSource(source) {
  return Boolean(source && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(source.id)
    && SYSTEMS.has(source.system) && ["geojson", "wms", "xyz"].includes(source.type)
    && typeof source.url === "string" && /^(https:\/\/|data\/)/.test(source.url)
    && !/[\s\\<>"']/.test(source.url) && !source.url.startsWith("data/../")
    && source.title_es && source.title_en && source.citation
    && (source.type !== "wms" || source.layers));
}

function escaped(value) {
  return String(value).replace(/[&<>"']/g, char => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"})[char]);
}

export function mountCustomSources({L, map, sources = [], language, allowed, onChange}) {
  const panel = document.querySelector(".layer-panel");
  const legend = document.querySelector(".legend");
  const entries = [];
  if (!panel || !legend) return {sync() {}, activeCount: () => 0};
  for (const source of sources.slice(0, 20).filter(validCustomSource)) {
    if (source.enabled === false || entries.some(entry => entry.source.id === source.id)) continue;
    const card = document.createElement("article");
    card.className = "now-layer-card";
    card.dataset.systemContent = source.system;
    const label = document.createElement("label");
    label.className = "layer-switch";
    const title = document.createElement("strong");
    const toggle = document.createElement("input");
    toggle.type = "checkbox";
    const status = document.createElement("small");
    const citation = document.createElement("small");
    citation.textContent = source.citation;
    label.append(title, toggle);
    card.append(label, citation, status);
    panel.append(card);
    const key = document.createElement("section");
    key.className = "legend-section";
    key.hidden = true;
    key.style.borderLeft = `4px solid ${/^#[a-f\d]{6}$/i.test(source.color) ? source.color : "#55e2cb"}`;
    const keyTitle = document.createElement("strong");
    const keyNote = document.createElement("small");
    keyNote.textContent = source.citation;
    key.append(keyTitle, keyNote);
    legend.append(key);
    const entry = {source, card, toggle, title, key, keyTitle, layer: null, pending: null};
    entries.push(entry);
    const attribution = escaped(source.citation);
    const color = /^#[a-f\d]{6}$/i.test(source.color) ? source.color : "#55e2cb";
    toggle.addEventListener("change", async () => {
      if (!toggle.checked || !allowed(source.system)) {
        toggle.checked = false;
        entry.pending?.abort();
        if (entry.layer) map.removeLayer(entry.layer);
        key.hidden = true;
        onChange();
        return;
      }
      status.textContent = language() === "en" ? "Loading…" : "Cargando…";
      try {
        if (!entry.layer) {
          if (source.type === "wms") entry.layer = L.tileLayer.wms(source.url, {
            layers: source.layers, format: "image/png", transparent: true, attribution,
          });
          else if (source.type === "xyz") entry.layer = L.tileLayer(source.url, {attribution});
          else {
            const request = new AbortController();
            entry.pending = request;
            const response = await fetch(source.url, {signal: request.signal});
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            if (data.type !== "FeatureCollection" || !Array.isArray(data.features) || data.features.length > 50000) throw new Error("GeoJSON: FeatureCollection / max. 50000");
            if (!toggle.checked || !allowed(source.system)) return;
            entry.layer = L.geoJSON(data, {
              style: {color, weight: 2, fillOpacity: 0.18}, attribution,
              pointToLayer: (_feature, latlng) => L.circleMarker(latlng, {color, fillColor: color, radius: 5, fillOpacity: 0.8}),
            });
          }
          entry.layer.on("tileerror", () => {
            status.textContent = language() === "en" ? "Service/tile error" : "Error de servicio/tesela";
          });
        }
        if (!toggle.checked || !allowed(source.system)) return;
        entry.layer.addTo(map);
        key.hidden = false;
        status.textContent = language() === "en" ? "Source enabled" : "Fuente activada";
      } catch (error) {
        if (error.name === "AbortError") return;
        toggle.checked = false;
        key.hidden = true;
        status.textContent = language() === "en" ? "Unavailable: check URL and CORS" : "No disponible: revisa URL y CORS";
      } finally {
        onChange();
      }
    });
  }
  return {
    sync() {
      entries.forEach(entry => {
        entry.title.textContent = language() === "en" ? entry.source.title_en : entry.source.title_es;
        entry.keyTitle.textContent = entry.title.textContent;
        entry.card.hidden = !allowed(entry.source.system);
        if (entry.card.hidden && entry.toggle.checked) {
          entry.toggle.checked = false;
          entry.pending?.abort();
          if (entry.layer) map.removeLayer(entry.layer);
          entry.key.hidden = true;
        }
      });
    },
    activeCount: () => entries.filter(entry => entry.layer && map.hasLayer(entry.layer)).length,
  };
}
