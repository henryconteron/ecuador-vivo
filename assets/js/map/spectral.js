/** Two measured annual composites; colours are signals, never causal labels. */
import {comparisonPosition} from "./imagery.js?v=20260930-6";

const MODES = ["rgb", "ndvi", "mndwi"];
const RECEIPT_KEYS = ["years", "periods", "bbox", "optical_bands", "year_bands", "quality_band", "clear_threshold", "min_observations", "excluded_scl", "composite", "observation_mask", "index_formulas", "export_crs", "export_transform", "nodata"];
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const digest = value => typeof value === "string" && /^[a-f0-9]{64}$/.test(value);
const positiveInteger = value => Number.isSafeInteger(value) && value > 0;

/** Fractions in the display projection, not linear latitude fractions. */
export function comparisonCrop(bounds, bbox) {
  if (!Array.isArray(bounds) || bounds.length !== 2 || bounds.some(row => !Array.isArray(row) || row.length !== 2 || row.some(x => !Number.isFinite(x))) ||
      !Array.isArray(bbox) || bbox.length !== 4 || bbox.some(x => !Number.isFinite(x))) throw new Error("Invalid comparison extent");
  const [[south, west], [north, east]] = bounds;
  const [cropWest, cropSouth, cropEast, cropNorth] = bbox;
  if (south >= north || west >= east || south <= -85 || north >= 85 || west < -180 || east > 180 ||
      cropWest < west || cropEast > east || cropSouth < south || cropNorth > north || cropWest >= cropEast || cropSouth >= cropNorth) throw new Error("Crop outside comparison grid");
  const mercatorY = latitude => Math.log(Math.tan(Math.PI / 4 + latitude * Math.PI / 360));
  const gridHeight = mercatorY(north) - mercatorY(south);
  return {
    left: (cropWest - west) / (east - west),
    top: (mercatorY(north) - mercatorY(cropNorth)) / gridHeight,
    width: (cropEast - cropWest) / (east - west),
    height: (mercatorY(cropNorth) - mercatorY(cropSouth)) / gridHeight,
  };
}

export function validateSpectralManifest(manifest, config, grid) {
  if (manifest?.schema_version !== 1) throw new Error("Unsupported spectral manifest");
  if (manifest.status === "pending") return null;
  if (manifest.status !== "ready" || config?.schema_version !== 1 || !same(config.years, [2019, 2024])) throw new Error("Invalid spectral status or years");
  for (const key of ["source", "years", "periods", "bbox", "scope", "display", "river_focus_bbox", "context_source"]) {
    if (!same(manifest[key], config[key])) throw new Error(`Spectral mismatch: ${key}`);
  }
  if (grid?.status !== "ready" || !same(grid.bbox, config.bbox) || !same(manifest.display_bounds, grid.display_bounds) ||
      manifest.grid_reference_sha256 !== grid.images?.find(row => row.year === 2024)?.sha256 || !digest(manifest.grid_reference_sha256)) throw new Error("Display reference changed; rebuild spectral views");
  comparisonCrop(manifest.display_bounds, config.bbox);
  comparisonCrop(manifest.display_bounds, config.river_focus_bbox);
  if (manifest.display_crs !== "EPSG:3857" || manifest.display_sampling_m !== 30 || manifest.reflectance_resampling !== "bilinear" ||
      manifest.index_resampling !== "nearest" || manifest.mask_resampling !== "nearest" || !positiveInteger(manifest.width) || !positiveInteger(manifest.height) ||
      manifest.width * manifest.height > 5000000 || !digest(manifest.input_sha256) || !digest(manifest.receipt_sha256)) throw new Error("Invalid spectral display grid or checksums");
  for (const mode of ["ndvi", "mndwi"]) {
    const display = config.display?.[mode];
    if (display?.min !== -1 || display.max !== 1 || display.levels !== 129 || !Array.isArray(display.palette) || display.palette.length !== 3 || display.palette.some(colour => !/^#[a-f0-9]{6}$/i.test(colour))) throw new Error("Invalid spectral scale");
  }
  const expected = config.years.flatMap(year => MODES.map(mode => ({year, mode, url: `assets/images/spectral/napo-${mode}-${year}.${mode === "rgb" ? "webp" : "png"}`})));
  if (!Array.isArray(manifest.images) || manifest.images.length !== expected.length || manifest.images.some((row, index) =>
    row.year !== expected[index].year || row.mode !== expected[index].mode || row.url !== expected[index].url || !digest(row.sha256))) throw new Error("Invalid spectral image bundle");
  const receipt = manifest.receipt;
  if (!receipt || receipt.schema_version !== 1 || receipt.asset !== config.source.asset || receipt.quality_asset !== config.source.quality_asset ||
      receipt.reflectance_scale !== 0.0001 || receipt.export_resampling !== "nearest" || !Number.isFinite(Date.parse(receipt.export_requested_at)) ||
      !/(Z|[+-]\d{2}:\d{2})$/.test(receipt.export_requested_at)) throw new Error("Invalid spectral provenance");
  for (const key of RECEIPT_KEYS) if (!same(receipt[key], config[key])) throw new Error(`Spectral receipt mismatch: ${key}`);
  if (!Array.isArray(receipt.scenes) || receipt.scenes.length !== 2) throw new Error("Missing annual scene inventories");
  for (const [index, scenes] of receipt.scenes.entries()) {
    const period = config.periods[index], count = scenes.joined_count;
    const start = Date.parse(period[0]), end = Date.parse(period[1]);
    if (scenes.year !== config.years[index] || !same(scenes.period, period) || !positiveInteger(count) || count < config.min_observations || count > 800 ||
        !Number.isSafeInteger(scenes.source_count) || scenes.source_count < count || scenes.source_count > 800 || !Array.isArray(scenes.scene_ids) || scenes.scene_ids.length !== count ||
        new Set(scenes.scene_ids).size !== count || scenes.scene_ids.some(id => typeof id !== "string" || !id) ||
        !Array.isArray(scenes.acquired_ms) || scenes.acquired_ms.length !== count || scenes.acquired_ms.some(ms => !Number.isFinite(ms) || ms < start || ms >= end)) throw new Error("Invalid source scenes or acquisition dates");
  }
  const stats = manifest.statistics;
  if (!stats || !positiveInteger(stats.window_pixels) || stats.window_pixels > 5000000 || !positiveInteger(stats.common_pixels) || stats.common_pixels > stats.window_pixels ||
      !positiveInteger(stats.paired_display_pixels) || stats.paired_display_pixels > manifest.width * manifest.height || !Array.isArray(stats.years) || stats.years.length !== 2) throw new Error("Invalid common support statistics");
  for (const [index, year] of stats.years.entries()) {
    if (year.year !== config.years[index] || !positiveInteger(year.usable_pixels) || year.usable_pixels > stats.window_pixels || year.usable_pixels < stats.common_pixels ||
        !positiveInteger(year.min_clear_scenes) || !positiveInteger(year.max_clear_scenes) || !Number.isFinite(year.median_clear_scenes) ||
        year.min_clear_scenes < config.min_observations || year.min_clear_scenes > year.median_clear_scenes || year.median_clear_scenes > year.max_clear_scenes ||
        year.max_clear_scenes > receipt.scenes[index].joined_count) throw new Error("Impossible annual quality statistics");
  }
  return manifest;
}

/** Decode a complete, same-sized pair before publishing either side. */
export async function loadSpectralPair(rows, {width, height, isCurrent = () => true, createImage = () => new Image()}) {
  if (!Array.isArray(rows) || rows.length !== 2) throw new Error("A year pair is required");
  const images = await Promise.all(rows.map(row => new Promise((resolve, reject) => {
    const image = createImage();
    image.decoding = "async"; image.draggable = false;
    image.onload = () => image.naturalWidth === width && image.naturalHeight === height ? resolve(image) : reject(new Error("Spectral image dimensions differ"));
    image.onerror = () => reject(new Error("Spectral image unavailable"));
    image.src = `${row.url}?sha=${row.sha256.slice(0, 12)}`;
  })));
  return isCurrent() ? images : null;
}

export function mountNapoSpectral({t, language}) {
  const launch = document.querySelector("#spectral-launch"), dialog = document.querySelector("#spectral-dialog");
  if (!launch || !dialog) return {render() {}};
  const stage = document.querySelector("#spectral-stage"), slider = document.querySelector("#spectral-slider");
  const planes = [document.querySelector("#spectral-earlier"), document.querySelector("#spectral-later")];
  const focus = document.querySelector("#spectral-focus"), modeButtons = [...document.querySelectorAll("[data-spectral-mode]")];
  let config, manifest, state = "loading", mode = "rgb", imageState = "imageLoading", epoch = 0, activeImages = [];
  const number = value => new Intl.NumberFormat(language(), {maximumFractionDigits: 1}).format(value);
  function move() {
    const value = comparisonPosition(slider.value);
    planes[1].style.clipPath = `inset(0 0 0 ${value}%)`;
    document.querySelector("#spectral-divider").style.left = `${value}%`;
    document.querySelector("#spectral-position").textContent = `2019 ${number(value)}% · 2024 ${number(100 - value)}%`;
    slider.setAttribute("aria-valuetext", `${number(value)}% 2019, ${number(100 - value)}% 2024`);
  }
  function crop() {
    if (!manifest) return;
    const box = focus.value === "river" ? comparisonCrop(manifest.display_bounds, config.river_focus_bbox) : {left: 0, top: 0, width: 1, height: 1};
    stage.style.aspectRatio = `${manifest.width * box.width} / ${manifest.height * box.height}`;
    for (const image of activeImages) {
      image.style.width = `${100 / box.width}%`; image.style.height = `${100 / box.height}%`;
      image.style.left = `${-100 * box.left / box.width}%`; image.style.top = `${-100 * box.top / box.height}%`;
    }
    document.querySelector("#spectral-focus-note").textContent = t(`spectral.${focus.value === "river" ? "riverScope" : "windowScope"}`);
  }
  function render() {
    document.querySelector("#spectral-status").textContent = t(`spectral.${state}`);
    document.querySelector("#spectral-image-status").textContent = t(`spectral.${imageState}`);
    launch.disabled = !manifest;
    modeButtons.forEach(button => { button.setAttribute("aria-pressed", String(button.dataset.spectralMode === mode)); button.disabled = !manifest; });
    document.querySelector("#spectral-mode-copy").textContent = t(`spectral.${mode}Copy`);
    document.querySelector("#spectral-formula").textContent = mode === "rgb" ? t("spectral.rgbFormula") : mode === "ndvi" ? "NDVI = (B8 − B4) / (B8 + B4)" : "MNDWI = (B3 − B11) / (B3 + B11)";
    const legend = document.querySelector("#spectral-legend");
    legend.hidden = mode === "rgb";
    if (manifest && mode !== "rgb") document.querySelector("#spectral-gradient").style.background = `linear-gradient(90deg, ${config.display[mode].palette.join(", ")})`;
    for (const [index, image] of activeImages.entries()) image.alt = `${t(`spectral.${mode}Alt`)} · ${[2019, 2024][index]}`;
    if (manifest) {
      const stats = manifest.statistics;
      document.querySelector("#spectral-common").textContent = `${number(100 * stats.common_pixels / stats.window_pixels)}% · ${t("spectral.commonCoverage")}`;
      for (const [index, year] of stats.years.entries()) {
        const scenes = manifest.receipt.scenes[index];
        document.querySelector(`#spectral-quality-${year.year}`).textContent = `${year.year} · ${number(scenes.joined_count)} / ${number(scenes.source_count)} ${t("spectral.scenes")}; ${number(100 * year.usable_pixels / stats.window_pixels)}% ${t("spectral.coverage")}; ${number(year.min_clear_scenes)} / ${number(year.median_clear_scenes)} / ${number(year.max_clear_scenes)} ${t("spectral.counts")}`;
      }
    }
    crop(); move();
  }
  async function loadMode() {
    const current = ++epoch;
    stage.hidden = true; slider.disabled = true; imageState = "imageLoading"; activeImages = [];
    render();
    try {
      const rows = config.years.map(year => manifest.images.find(row => row.year === year && row.mode === mode));
      const images = await loadSpectralPair(rows, {width: manifest.width, height: manifest.height, isCurrent: () => current === epoch});
      if (!images) return;
      activeImages = images;
      planes.forEach((plane, index) => plane.replaceChildren(images[index]));
      imageState = "imageReady"; crop(); render(); stage.hidden = false; slider.disabled = false;
    } catch {
      if (current !== epoch) return;
      imageState = "imageError"; stage.hidden = true; slider.disabled = true; render();
    }
  }
  slider.addEventListener("input", move);
  function pointer(event) {
    const bounds = stage.getBoundingClientRect();
    if (bounds.width <= 0 || slider.disabled) return;
    slider.value = String(Math.round(comparisonPosition(100 * (event.clientX - bounds.left) / bounds.width))); move();
  }
  stage.addEventListener("pointerdown", event => {
    if (event.button !== 0 || slider.disabled) return;
    event.preventDefault(); stage.setPointerCapture(event.pointerId); slider.focus({preventScroll: true}); pointer(event);
  });
  stage.addEventListener("pointermove", event => { if (stage.hasPointerCapture(event.pointerId)) pointer(event); });
  stage.addEventListener("pointerup", event => { if (stage.hasPointerCapture(event.pointerId)) stage.releasePointerCapture(event.pointerId); });
  modeButtons.forEach(button => button.addEventListener("click", () => {
    if (!manifest || button.dataset.spectralMode === mode && imageState === "imageReady") return;
    mode = button.dataset.spectralMode; void loadMode();
  }));
  focus.addEventListener("change", crop);
  launch.addEventListener("click", () => {
    if (!manifest) return;
    dialog.showModal();
    if (imageState !== "imageReady") void loadMode();
  });
  document.querySelector("#spectral-close").addEventListener("click", () => dialog.close());
  dialog.addEventListener("close", () => launch.focus());
  async function load() {
    try {
      const responses = await Promise.all(["data/spectral/napo-config.json", "data/spectral/napo-manifest.json", "data/landcover/napo-manifest.json"].map(url => fetch(url, {cache: "no-store"})));
      if (responses.some(response => !response.ok)) throw new Error("Missing spectral bundle");
      const [settings, receipt, grid] = await Promise.all(responses.map(response => response.json()));
      config = settings; manifest = validateSpectralManifest(receipt, config, grid); state = manifest ? "ready" : "pending";
    } catch { manifest = undefined; state = "error"; }
    render();
    if (manifest && new URLSearchParams(window.location.search).get("lab") === "spectral") launch.click();
  }
  render(); void load();
  return {render};
}
