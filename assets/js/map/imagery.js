/** Real observations and model output, never a synthetic production fallback. */
import {validateLandcoverManifest} from "./landcover.js?v=20260930-4";
export function comparisonPosition(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? Math.min(100, Math.max(0, parsed)) : 50;
}

export function validateImageryManifest(manifest, config, landcover) {
  if (manifest?.schema_version !== 1) throw new Error("Unsupported imagery manifest");
  if (manifest.status === "pending") return null;
  if (manifest.status !== "ready") throw new Error("Invalid imagery status");
  for (const key of ["source", "period", "bbox", "scope", "display"]) {
    if (JSON.stringify(manifest[key]) !== JSON.stringify(config[key])) throw new Error(`Imagery mismatch: ${key}`);
  }
  if (landcover?.status !== "ready" || JSON.stringify(landcover.bbox) !== JSON.stringify(config.bbox) ||
      JSON.stringify(manifest.display_bounds) !== JSON.stringify(landcover.display_bounds) ||
      manifest.classification_sha256 !== landcover.images.find(row => row.year === 2024)?.sha256) throw new Error("Classification has changed; rebuild comparison");
  if (manifest.display_crs !== "EPSG:3857" || manifest.display_sampling_m !== 30 ||
      manifest.reflectance_resampling !== "bilinear" || manifest.mask_resampling !== "nearest" ||
      !Number.isSafeInteger(manifest.width) || manifest.width <= 0 || !Number.isSafeInteger(manifest.height) ||
      manifest.height <= 0 || manifest.width * manifest.height > 5000000) throw new Error("Invalid imagery display grid");
  const digest = x => typeof x === "string" && /^[a-f0-9]{64}$/.test(x);
  if (!digest(manifest.input_sha256) || !digest(manifest.receipt_sha256)) throw new Error("Missing imagery input checksums");
  const paths = ["assets/images/imagery/napo-sentinel2-2024.webp", "assets/images/imagery/napo-mapbiomas-2024.png"];
  if (!Array.isArray(manifest.images) || manifest.images.length !== 2 || manifest.images.some((row, index) =>
    row.kind !== ["observation", "classification"][index] || row.url !== paths[index] || !digest(row.sha256))) throw new Error("Invalid comparison images");
  const receipt = manifest.receipt;
  if (!receipt || receipt.schema_version !== 1 || receipt.asset !== config.source.asset || receipt.quality_asset !== config.source.quality_asset ||
      receipt.nominal_resolution_m !== 10 || receipt.reflectance_scale !== 0.0001 || receipt.export_resampling !== "nearest") throw new Error("Invalid imagery provenance");
  for (const key of ["period", "bbox", "bands", "quality_band", "clear_threshold", "min_observations", "excluded_scl", "composite", "export_crs", "export_scale_m"]) {
    if (JSON.stringify(receipt[key]) !== JSON.stringify(config[key])) throw new Error(`Receipt mismatch: ${key}`);
  }
  const count = receipt.joined_count, start = Date.parse(config.period[0]), end = Date.parse(config.period[1]);
  if (!Number.isSafeInteger(count) || count < config.min_observations || count > 800 ||
      !Number.isSafeInteger(receipt.source_count) || receipt.source_count < count ||
      !Array.isArray(receipt.scene_ids) || receipt.scene_ids.length !== count || new Set(receipt.scene_ids).size !== count ||
      receipt.scene_ids.some(id => typeof id !== "string" || !id) || !Array.isArray(receipt.acquired_ms) || receipt.acquired_ms.length !== count ||
      receipt.acquired_ms.some(ms => !Number.isFinite(ms) || ms < start || ms >= end) || !Number.isFinite(Date.parse(receipt.export_requested_at))) throw new Error("Missing source scenes/dates");
  const stats = manifest.statistics, integer = n => Number.isSafeInteger(n) && n > 0;
  if (!stats || !["window_pixels", "usable_pixels", "counted_pixels", "paired_display_pixels", "classified_display_pixels"].every(key => integer(stats[key])) ||
      stats.usable_pixels > stats.counted_pixels || stats.counted_pixels > stats.window_pixels ||
      stats.paired_display_pixels > stats.classified_display_pixels || stats.classified_display_pixels > manifest.width * manifest.height ||
      !integer(stats.min_clear_scenes) || !integer(stats.max_clear_scenes) || !Number.isFinite(stats.median_clear_scenes) ||
      stats.min_clear_scenes < config.min_observations || stats.min_clear_scenes > stats.median_clear_scenes ||
      stats.median_clear_scenes > stats.max_clear_scenes || stats.max_clear_scenes > count) throw new Error("Impossible imagery quality statistics");
  return manifest;
}

export function mountNapoImagery({t, language}) {
  const launch = document.querySelector("#imagery-launch"), status = document.querySelector("#imagery-status");
  const dialog = document.querySelector("#imagery-dialog"), stage = document.querySelector("#imagery-stage");
  const slider = document.querySelector("#imagery-slider"), observation = document.querySelector("#imagery-observation");
  const classification = document.querySelector("#imagery-classification"), divider = document.querySelector("#imagery-divider");
  let manifest, landcoverConfig, landcoverManifest, state = "loading", loaded = 0, failed = false;
  const number = n => new Intl.NumberFormat(language(), {maximumFractionDigits: 1}).format(n);
  function move() {
    const value = comparisonPosition(slider.value);
    classification.style.clipPath = `inset(0 0 0 ${value}%)`;
    divider.style.left = `${value}%`;
    document.querySelector("#imagery-position").textContent = `${number(value)}% · ${t("imagery.observation")}`;
    slider.setAttribute("aria-valuetext", `${number(value)}% ${t("imagery.observation")}, ${number(100 - value)}% ${t("imagery.classification")}`);
  }
  function render() {
    status.textContent = t(`imagery.${state}`);
    launch.disabled = !manifest;
    document.querySelector("#imagery-image-status").textContent = t(`imagery.${failed ? "imageError" : loaded === 2 ? "imageReady" : "imageLoading"}`);
    if (manifest) {
      const s = manifest.statistics;
      document.querySelector("#imagery-scenes").textContent = `${number(manifest.receipt.joined_count)} / ${number(manifest.receipt.source_count)} · ${t("imagery.scenes")}`;
      document.querySelector("#imagery-quality").textContent = `${number(100 * s.usable_pixels / s.window_pixels)}% · ${t("imagery.coverage")}`;
      document.querySelector("#imagery-counts").textContent = `${number(s.min_clear_scenes)} / ${number(s.median_clear_scenes)} / ${number(s.max_clear_scenes)} · ${t("imagery.counts")}`;
      document.querySelector("#imagery-paired").textContent = `${number(100 * s.paired_display_pixels / s.classified_display_pixels)}% · ${t("imagery.paired")}`;
      const legend = document.querySelector("#imagery-legend");
      legend.replaceChildren();
      for (const row of landcoverManifest.statistics.classes.filter(row => row.pixels[1] > 0)) {
        const item = landcoverConfig.legend.find(item => item.id === row.id);
        const entry = document.createElement("span"), swatch = document.createElement("i"), label = document.createElement("span");
        swatch.style.backgroundColor = item.color;
        label.textContent = item[language() === "en" ? "en" : "es"];
        entry.append(swatch, label); legend.append(entry);
      }
    }
    move();
  }
  function loadImages() {
    loaded = 0; failed = false; stage.hidden = true; slider.disabled = true;
    for (const [index, image] of [observation, classification].entries()) {
      image.onload = () => {
        if (failed) return;
        if (image.naturalWidth !== manifest.width || image.naturalHeight !== manifest.height) { image.onerror(); return; }
        loaded += 1;
        if (loaded === 2) { stage.hidden = false; slider.disabled = false; }
        render();
      };
      image.onerror = () => { failed = true; stage.hidden = true; slider.disabled = true; render(); };
      image.src = `${manifest.images[index].url}?sha=${manifest.images[index].sha256.slice(0, 12)}`;
    }
    render();
  }
  slider.addEventListener("input", move);
  function movePointer(event) {
    const bounds = stage.getBoundingClientRect();
    if (bounds.width <= 0 || slider.disabled) return;
    slider.value = String(Math.round(comparisonPosition(100 * (event.clientX - bounds.left) / bounds.width)));
    move();
  }
  stage.addEventListener("pointerdown", event => {
    if (event.button !== 0 || slider.disabled) return;
    event.preventDefault();
    stage.setPointerCapture(event.pointerId);
    slider.focus({preventScroll: true}); movePointer(event);
  });
  stage.addEventListener("pointermove", event => { if (stage.hasPointerCapture(event.pointerId)) movePointer(event); });
  stage.addEventListener("pointerup", event => { if (stage.hasPointerCapture(event.pointerId)) stage.releasePointerCapture(event.pointerId); });
  launch.addEventListener("click", () => {
    if (!manifest) return;
    dialog.showModal();
    if (loaded !== 2 || failed) loadImages();
  });
  document.querySelector("#imagery-close").addEventListener("click", () => dialog.close());
  dialog.addEventListener("close", () => launch.focus());
  async function load() {
    try {
      const responses = await Promise.all(["data/imagery/napo-config.json", "data/imagery/napo-manifest.json", "data/landcover/napo-manifest.json", "data/landcover/napo-config.json"].map(url => fetch(url, {cache: "no-store"})));
      if (responses.some(response => !response.ok)) throw new Error("Missing imagery bundle");
      const [config, document, landcover, classes] = await Promise.all(responses.map(response => response.json()));
      landcoverConfig = classes;
      landcoverManifest = validateLandcoverManifest(landcover, classes);
      if (!landcoverManifest || !Array.isArray(classes.legend) || classes.legend.some(row => !/^#[a-f0-9]{6}$/i.test(row.color) || !row.es || !row.en)) throw new Error("Invalid classification legend");
      manifest = validateImageryManifest(document, config, landcover);
      state = manifest ? "ready" : "pending";
      if (manifest) stage.style.aspectRatio = `${manifest.width} / ${manifest.height}`;
    } catch { manifest = undefined; state = "error"; }
    render();
    if (manifest && new URLSearchParams(window.location.search).get("lab") === "imagery") launch.click();
  }
  render(); void load();
  return {render};
}
