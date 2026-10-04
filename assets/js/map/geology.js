import {validateLocalGeoJSON} from "./local-data.js";
const BASE = "https://capas.geoenergia.gob.ec/arcgis/services/Geologia_General/MapServer/WMSServer";
export function mountGeology({L, map, language, onChange}) {
  const get = id => document.getElementById(id);
  const national = get("geology-toggle"), snapshot = get("geology-local-toggle"), sheets = get("geology-sheets-toggle");
  const say = (es, en) => language() === "en" ? en : es;
  let units, index, loaded = false, failed = false, serviceError = false;
  const palette = ["#d9b781", "#96bc8e", "#d5a6b3", "#99bfd0", "#beb28b", "#c8b6db", "#8cbeb2", "#e0c956", "#c39070", "#91a58b", "#b1b5cd", "#dbaf79"];
  map.createPane("geology"); map.getPane("geology").style.zIndex = 270;
  const regional = L.tileLayer.wms(BASE, {layers: "0", format: "image/png", transparent: true, version: "1.3.0", pane: "geology", opacity: .65, attribution: "Geología: IIGE · servicio externo"});
  function render() {
    get("geology-status").textContent = failed ? say("No se pudo verificar la copia local. No se muestran datos incompletos.", "Local snapshot could not be verified. Incomplete data is not shown.") : loaded ? say("Copia IIGE verificada: 56 polígonos y 4 hojas intersectan la ventana Tena–Archidona. Escala de las unidades no documentada en el servicio.", "Verified IIGE snapshot: 56 polygons and 4 map sheets intersect the Tena–Archidona window. Unit-map scale is not documented by the service.") : say("Verificando la copia IIGE…", "Verifying IIGE snapshot…");
    get("geology-service-status").textContent = serviceError ? say("El servicio IIGE no responde; capa retirada. Puedes usar la copia local.", "IIGE service unavailable; layer removed. You can use the local snapshot.") : national.checked ? say("Servicio regional IIGE activo; las zonas vacías no prueban ausencia de geología.", "Regional IIGE service active; empty areas do not imply absence of geology.") : "";
    get("geology-legend").hidden = !(national.checked || snapshot.checked || sheets.checked);
    get("geology-legend-units").hidden = !snapshot.checked;
    get("geology-legend-service").hidden = !national.checked;
    get("geology-legend-sheets").hidden = !sheets.checked;
  }
  regional.on("tileerror", () => { if (!national.checked) return; regional.remove(); national.checked = false; serviceError = true; render(); onChange(); });
  national.addEventListener("change", () => { serviceError = false; if (national.checked) regional.addTo(map); else regional.remove(); render(); onChange(); });
  for (const [control, layer] of [[snapshot, () => units], [sheets, () => index]]) control.addEventListener("change", () => { if (control.checked) layer()?.addTo(map); else layer()?.remove(); render(); onChange(); });
  get("geology-opacity").addEventListener("input", event => { const opacity = Number(event.target.value); regional.setOpacity(opacity); units?.setStyle({fillOpacity: opacity, opacity}); });
  get("geology-focus").addEventListener("click", () => map.fitBounds([[-1.2,-78.1],[-.7,-77.6]]));
  function popup(feature, layer) { const box = document.createElement("div");
    for (const key of ["ENT_GEOL", "LIT", "LITOLOGIA", "NOMBRE", "ESTADO", "VERSIONES", "AUTORES", "OBJECTID"]) {
      const value = feature.properties[key]; if (value === undefined || !String(value).trim()) continue;
      const row = document.createElement("p"); row.textContent = `${key}: ${value}`; box.append(row);
    }
    const credit = document.createElement("small"); credit.textContent = "IIGE · 2026-10-04 · atributos originales en español / original Spanish attributes"; box.append(credit); layer.bindPopup(box);
  }
  async function load() {
    try {
      const response = await fetch("data/geology/manifest.json"); if (!response.ok) throw new Error("manifest");
      const manifest = await response.json(); const collections = [];
      for (const name of ["tena-units", "tena-sheets"]) {
        const row = manifest.files.find(file => file.id === name);
        if (!row || row.path !== `data/geology/${name}.geojson`) throw new Error("path");
        const reply = await fetch(row.path); if (!reply.ok) throw new Error("snapshot"); const bytes = await reply.arrayBuffer();
        const sha = [...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))].map(x => x.toString(16).padStart(2, "0")).join("");
        if (sha !== row.sha256 || bytes.byteLength !== row.bytes) throw new Error("integrity");
        const data = validateLocalGeoJSON(JSON.parse(new TextDecoder().decode(bytes))); if (data.features.length !== row.count) throw new Error("count"); collections.push(data);
      }
      const names = [...new Set(collections[0].features.map(f => f.properties.ENT_GEOL))].sort();
      const color = feature => palette[names.indexOf(feature.properties.ENT_GEOL) % palette.length];
      units = L.geoJSON(collections[0], {pane: "geology", style: feature => ({color: color(feature), weight: 1, fillOpacity: .65}), onEachFeature: popup, attribution: "IIGE · selección descargada 2026-10-04"});
      index = L.geoJSON(collections[1], {style: {color: "#f5be45", weight: 2, dashArray: "5 5", fill: false}, onEachFeature: popup});
      const legend = get("geology-legend-units"); names.forEach((name, i) => { const row = document.createElement("div"), swatch = document.createElement("i"); swatch.style.backgroundColor = palette[i % palette.length]; row.append(swatch, document.createTextNode(name)); legend.append(row); });
      loaded = true; snapshot.disabled = false; sheets.disabled = false;
    } catch { failed = true; } render(); onChange();
  }
  window.addEventListener("atlas:languagechange", render); render(); void load();
  return {isActive: () => national.checked || snapshot.checked || sheets.checked};
}
