export function validateLocalGeoJSON(value) {
  if (!value || value.type !== "FeatureCollection" || !Array.isArray(value.features) || !value.features.length || value.features.length > 5000 || value.crs) throw new Error("collection");
  let points = 0;
  function position(p) {
    if (!Array.isArray(p) || p.length < 2 || p.length > 3 || !p.every(Number.isFinite) || Math.abs(p[0]) > 180 || Math.abs(p[1]) > 85.051129 || ++points > 100000) throw new Error("coordinates");
  }
  function line(ps, min = 2) { if (!Array.isArray(ps) || ps.length < min) throw new Error("line"); ps.forEach(position); }
  function polygon(rings) {
    if (!Array.isArray(rings) || !rings.length) throw new Error("polygon");
    rings.forEach(r => { line(r, 4); if (r[0][0] !== r.at(-1)[0] || r[0][1] !== r.at(-1)[1]) throw new Error("ring"); });
  }
  for (const feature of value.features) {
    if (feature?.type !== "Feature" || !feature.geometry || feature.crs || feature.geometry.crs) throw new Error("feature");
    const {type, coordinates: c} = feature.geometry;
    if (type === "Point") position(c);
    else if (type === "MultiPoint") line(c, 1);
    else if (type === "LineString") line(c);
    else if (type === "MultiLineString") { if (!Array.isArray(c) || !c.length) throw new Error("lines"); c.forEach(x => line(x)); }
    else if (type === "Polygon") polygon(c);
    else if (type === "MultiPolygon") { if (!Array.isArray(c) || !c.length) throw new Error("polygons"); c.forEach(polygon); }
    else throw new Error("geometry");
    if (feature.properties !== null && (typeof feature.properties !== "object" || Array.isArray(feature.properties))) throw new Error("properties");
  }
  return value;
}

export function mountLocalData({L, map, language, owner, allowed, onChange}) {
  const file = document.querySelector("#local-file"), toggle = document.querySelector("#local-toggle"), status = document.querySelector("#local-status");
  const label = toggle.closest("[data-system-content]"), legend = document.querySelector("#local-legend");
  let layer, name = "", count = 0, state = "empty", request = 0;
  const say = (es, en) => language() === "en" ? en : es;
  function render() {
    status.textContent = state === "error" ? say("Archivo no válido. Usa GeoJSON WGS84 (longitud, latitud), hasta 10 MB, 5000 entidades y 100000 vértices; sin GeometryCollection.", "Invalid file. Use WGS84 GeoJSON (longitude, latitude), up to 10 MB, 5000 features and 100000 vertices; no GeometryCollection.") : state === "loading" ? say("Leyendo el archivo local…", "Reading local file…") : layer ? `${name} · ${count} · ${say("aporte local no verificado", "unverified local contribution")}` : say("No hay archivos cargados. Nada se publica al seleccionar un archivo.", "No files loaded. Selecting a file publishes nothing.");
    legend.hidden = !layer || !map.hasLayer(layer);
    legend.textContent = `${say("Capa local · no verificada", "Local layer · unverified")}: ${name}`;
  }
  toggle.addEventListener("change", () => { if (!layer) return; if (toggle.checked && allowed(label.dataset.systemContent)) layer.addTo(map); else { toggle.checked = false; layer.remove(); } render(); onChange(); });
  document.querySelector("#local-opacity").addEventListener("input", event => { layer?.setStyle({opacity: Number(event.target.value), fillOpacity: Number(event.target.value) * .35}); });
  document.querySelector("#local-fit").addEventListener("click", () => { if (layer) map.fitBounds(layer.getBounds(), {maxZoom: 13}); });
  document.querySelector("#local-remove").addEventListener("click", () => { ++request; layer?.remove(); layer = undefined; name = ""; count = 0; state = "empty"; file.value = ""; toggle.checked = false; toggle.disabled = true; toggle.dispatchEvent(new Event("change")); render(); onChange(); });
  file.addEventListener("change", async () => {
    const input = file.files[0]; if (!input) return;
    const ticket = ++request, selectedOwner = owner(); state = "loading"; render();
    try {
      if (input.size > 10 * 1024 * 1024) throw new Error("size");
      const collection = validateLocalGeoJSON(JSON.parse(await input.text()));
      if (ticket !== request) return;
      const next = L.geoJSON(collection, {style: {color: "#ce5cdb", weight: 3, fillOpacity: .25},
        pointToLayer: (_feature, latlng) => L.circleMarker(latlng, {radius: 6, color: "#ce5cdb", fillOpacity: .65}),
        onEachFeature: (feature, item) => { const box = document.createElement("div"); const heading = document.createElement("strong"); heading.textContent = say("Aporte local · no verificado", "Local contribution · unverified"); box.append(heading);
          Object.entries(feature.properties || {}).slice(0, 12).forEach(([key, value]) => { const p = document.createElement("p"); p.textContent = `${key.slice(0,80)}: ${String(value).slice(0,400)}`; box.append(p); }); item.bindPopup(box); }});
      layer?.remove(); layer = next; name = input.name; count = collection.features.length; state = "ready";
      label.dataset.systemContent = selectedOwner; toggle.disabled = false; toggle.checked = allowed(selectedOwner);
      document.querySelector("#local-opacity").value = "1";
      toggle.dispatchEvent(new Event("change")); render(); onChange();
    } catch { if (ticket === request) { state = "error"; render(); } }
  });
  window.addEventListener("atlas:languagechange", render); render();
  return {isActive: () => Boolean(layer && map.hasLayer(layer))};
}
