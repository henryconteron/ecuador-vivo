export const LANDCOVER_CONFIG_URL = "data/landcover/napo-config.json";
export const LANDCOVER_MANIFEST_URL = "data/landcover/napo-manifest.json";

export function validateLandcoverManifest(manifest, config) {
  if (manifest?.schema_version !== 1) throw new Error("Unsupported land-cover manifest");
  if (manifest.status === "pending") return null;
  if (manifest.status !== "ready") throw new Error("Invalid land-cover status");
  for (const key of ["source", "years", "bbox", "scope"]) {
    if (JSON.stringify(manifest[key]) !== JSON.stringify(config[key])) throw new Error(`Mismatch: ${key}`);
  }
  if (manifest.display_crs !== "EPSG:3857" || manifest.display_resampling !== "nearest") throw new Error("Unsafe display grid");
  const bounds = manifest.display_bounds;
  if (!Array.isArray(bounds) || bounds.length !== 2 || bounds.some(p => !Array.isArray(p) || p.length !== 2 || p.some(x => !Number.isFinite(x))) ||
      bounds[0][0] >= bounds[1][0] || bounds[0][1] >= bounds[1][1] ||
      bounds[0][0] < -90 || bounds[1][0] > 90 || bounds[0][1] < -180 || bounds[1][1] > 180) throw new Error("Invalid display extent");
  const extent = [bounds[0][1], bounds[0][0], bounds[1][1], bounds[1][0]];
  if (extent.some((value, index) => Math.abs(value - config.bbox[index]) > 0.002)) throw new Error("Display extent is outside the local subset");
  if (!/^[a-f0-9]{64}$/.test(manifest.input_sha256) || !/^[a-f0-9]{64}$/.test(manifest.receipt_sha256)) throw new Error("Missing input checksums");
  if (!Array.isArray(manifest.images) || manifest.images.length !== 2 || manifest.images.some((image, index) =>
    image.year !== config.years[index] || image.url !== `assets/images/landcover/napo-v1-${image.year}.png` || !/^[a-f0-9]{64}$/.test(image.sha256))) throw new Error("Invalid preview files");
  const stats = manifest.statistics;
  const validCount = n => Number.isSafeInteger(n) && n >= 0;
  if (!stats || !validCount(stats.common_observed_pixels) || stats.common_observed_pixels === 0 || !validCount(stats.window_pixels) ||
      stats.common_observed_pixels > stats.window_pixels || !validCount(stats.changed_class_pixels) || stats.changed_class_pixels > stats.common_observed_pixels) throw new Error("Invalid comparison counts");
  const ids = new Set(config.legend.filter(row => row.id !== 27).map(row => row.id));
  if (!Array.isArray(stats.classes) || stats.classes.length === 0 || new Set(stats.classes.map(row => row.id)).size !== stats.classes.length ||
      stats.classes.some(row => !ids.has(row.id) || !Array.isArray(row.pixels) || row.pixels.length !== 2 || row.pixels.some(n => !validCount(n)))) throw new Error("Unknown/invalid land-cover classes");
  for (let year = 0; year < 2; year++) {
    if (stats.classes.reduce((sum, row) => sum + row.pixels[year], 0) !== stats.common_observed_pixels) throw new Error("Comparison denominators differ");
  }
  if (!Array.isArray(stats.observed_pixels) || stats.observed_pixels.length !== 2 || stats.observed_pixels.some(n => !validCount(n) || n < stats.common_observed_pixels || n > stats.window_pixels)) throw new Error("Invalid observation coverage");
  return manifest;
}

export function classShares(manifest, yearIndex) {
  if (![0, 1].includes(yearIndex)) throw new Error("Invalid year index");
  return manifest.statistics.classes.map(row => ({id: row.id, percent: 100 * row.pixels[yearIndex] / manifest.statistics.common_observed_pixels}));
}

/** Modular UI; no remote account, API keys, or synthetic production fallback. */
export function mountNapoLandcover({ L, map, t, language, onChange, focus }) {
  const toggle = document.querySelector("#landcover-toggle");
  const years = document.querySelector("#landcover-years");
  const status = document.querySelector("#landcover-status");
  const summary = document.querySelector("#landcover-summary");
  const table = document.querySelector("#landcover-table-body");
  const legend = document.querySelector("#landcover-legend");
  const source = document.querySelector("#landcover-source");
  let config, manifest, overlay, selected = 1, state = "loading";
  map.createPane("land-cover");
  map.getPane("land-cover").style.zIndex = "270";
  map.getPane("land-cover").style.pointerEvents = "none";
  const number = value => new Intl.NumberFormat(language(), {maximumFractionDigits: 1}).format(value);

  function render() {
    status.textContent = t(`landcover.${state}`);
    toggle.disabled = !manifest;
    years.hidden = !manifest;
    summary.hidden = !manifest;
    if (!manifest) return;
    years.querySelectorAll("button").forEach((button, index) => button.setAttribute("aria-pressed", String(index === selected)));
    document.querySelector("#landcover-completeness").textContent = `${number(100 * manifest.statistics.common_observed_pixels / manifest.statistics.window_pixels)}% · ${t("landcover.commonCoverage")}`;
    document.querySelector("#landcover-change").textContent = `${number(100 * manifest.statistics.changed_class_pixels / manifest.statistics.common_observed_pixels)}% · ${t("landcover.changedClasses")}`;
    table.replaceChildren();
    legend.replaceChildren();
    const before = classShares(manifest, 0), after = classShares(manifest, 1);
    manifest.statistics.classes.forEach((row, index) => {
      const item = config.legend.find(entry => entry.id === row.id);
      const tr = document.createElement("tr");
      [item[language() === "en" ? "en" : "es"], `${number(before[index].percent)}%`, `${number(after[index].percent)}%`].forEach(text => {
        const cell = document.createElement("td"); cell.textContent = text; tr.append(cell);
      });
      table.append(tr);
      if (row.pixels[selected] > 0) {
        const entry = document.createElement("span"), color = document.createElement("i"), label = document.createElement("span");
        color.style.backgroundColor = item.color;
        label.textContent = item[language() === "en" ? "en" : "es"];
        entry.append(color, label); legend.append(entry);
      }
    });
    document.querySelector("#landcover-legend-year").textContent = `${t("landcover.title")} · ${config.years[selected]}`;
  }

  function setOverlay() {
    if (overlay) map.removeLayer(overlay);
    overlay = undefined;
    if (!toggle.checked || !manifest) { state = manifest ? "ready" : state; render(); onChange(); return; }
    state = "imageLoading";
    overlay = L.imageOverlay(manifest.images[selected].url, manifest.display_bounds, {
      pane: "land-cover", opacity: 0.8,
      attribution: 'Land cover: <a href="https://developers.google.com/earth-engine/datasets/catalog/projects_mapbiomas-public_assets_ecuador_lulc_v1" target="_blank" rel="noopener noreferrer">MapBiomas Ecuador V1</a> (CC-BY-4.0)',
      className: "categorical-overlay"
    });
    const requested = overlay;
    overlay.on("load", () => { if (overlay === requested) { state = "visible"; render(); } });
    overlay.on("error", () => {
      if (overlay !== requested) return;
      map.removeLayer(overlay); overlay = undefined; toggle.checked = false;
      state = "imageError"; render(); onChange();
    });
    overlay.addTo(map);
    render(); onChange();
  }
  toggle.addEventListener("change", () => { if (toggle.checked) focus(); setOverlay(); });
  years.querySelectorAll("button").forEach((button, index) => button.addEventListener("click", () => { selected = index; setOverlay(); }));
  async function load() {
    try {
      const responses = await Promise.all([LANDCOVER_CONFIG_URL, LANDCOVER_MANIFEST_URL].map(url => fetch(url, {cache: "no-store"})));
      if (responses.some(response => !response.ok)) throw new Error("Missing land-cover bundle");
      const documents = await Promise.all(responses.map(response => response.json()));
      config = documents[0];
      if (!Array.isArray(config.legend) || config.legend.some(row => !/^#[a-f0-9]{6}$/i.test(row.color) || !row.es || !row.en)) throw new Error("Invalid legend");
      manifest = validateLandcoverManifest(documents[1], config);
      source.href = config.source.url;
      state = manifest ? "ready" : "pending";
    } catch { state = "error"; manifest = undefined; }
    render(); onChange();
  }
  render();
  void load();
  return {
    render,
    isActive: () => Boolean(overlay && map.hasLayer(overlay)),
    context: () => ({id: "landcover", name: t("landcover.title"), resolution: `MapBiomas V1 · 30 m · ${config.years[selected]}`, limit: t("landcover.caution")})
  };
}
