/** Numerical reflectance, not display colours. Keep in sync with fluvial_science.py. */
export const WATER_METHODS = Object.freeze(["ndwi", "mndwi", "aweinsh", "aweish"]);
export const SIGNALS = Object.freeze(["rgb", ...WATER_METHODS, "agreement", "transition", "ndti", "red", "ndvi", "vegetationChange"]);
export function ratio(a, b) {
  return Number.isFinite(a) && Number.isFinite(b) && a >= 0 && b >= 0 && a + b > 0 ? (a - b) / (a + b) : NaN;
}
export function valuesAt(pack, index) {
  const n = pack.width * pack.height;
  if (!Number.isInteger(index) || index < 0 || index >= n || pack.values[6 * n + index] !== 1) return null;
  const [blue, green, red, nir, swir1, swir2] = Array.from({length: 6}, (_, band) => pack.values[band * n + index]);
  if (![blue, green, red, nir, swir1, swir2].every(value => Number.isFinite(value) && value >= 0)) return null;
  const result = {blue, green, red, nir, swir1, swir2, ndwi: ratio(green, nir), mndwi: ratio(green, swir1),
    aweinsh: 4 * (green - swir1) - .25 * nir - 2.75 * swir2,
    aweish: blue + 2.5 * green - 1.5 * (nir + swir1) - .25 * swir2,
    ndti: ratio(red, green), ndvi: ratio(nir, red)};
  return Object.values(result).every(Number.isFinite) ? result : null;
}
export function waterVotes(values, thresholds) {
  if (!values || !WATER_METHODS.every(key => Number.isFinite(values[key]))) return -1;
  if (!WATER_METHODS.every(key => Number.isFinite(thresholds[key]))) throw new Error("Invalid thresholds");
  return WATER_METHODS.reduce((count, key) => count + Number(values[key] > thresholds[key]), 0);
}
export function transition(a, b) {
  if (a < 0 || b < 0) return 0;
  if (a === 0 && b === 0) return 1;
  if (a === 4 && b === 4) return 2;
  if (a === 4 && b === 0) return 3;
  if (a === 0 && b === 4) return 4;
  return 5;
}
export function pixelIndex(point, region) {
  if (!Number.isFinite(point.x) || !Number.isFinite(point.y)) return null;
  const [left, bottom, right, top] = region.web_extent;
  if (point.x < left || point.x >= right || point.y <= bottom || point.y > top) return null;
  const x = Math.floor((point.x - left) / (right - left) * region.width);
  const y = Math.floor((top - point.y) / (top - bottom) * region.height);
  return y * region.width + x;
}
export function validateManifest(manifest, config) {
  const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  if (manifest?.schema_version !== 1 || manifest.status !== "exploratory-not-field-validated" || !same(manifest.config, config) ||
      config.sampling_m !== 20 || config.display_crs !== "EPSG:3857" || config.encoding !== "band-major-float32-little-endian-gzip" ||
      !same(config.bands, ["B2", "B3", "B4", "B8", "B11", "B12", "valid"]) ||
      config.scope !== "four-editorial-windows-not-province-or-basin" || config.native_crs !== "EPSG:32717" || config.resampling !== "nearest" ||
      config.api !== "https://earth-search.aws.element84.com/v1" || !same(config.accepted_scl, [4, 5, 6]) ||
      config.threshold_status !== "exploratory-not-locally-calibrated" ||
      config.formulas?.aweinsh !== "4*(B3-B11)-0.25*B8-2.75*B12" || config.formulas?.aweish !== "B2+2.5*B3-1.5*(B8+B11)-0.25*B12" ||
      manifest.benchmark?.winner !== null || manifest.benchmark.status !== "pending-independent-references" ||
      !Array.isArray(manifest.regions) || manifest.regions.length !== config.regions.length) throw new Error("Invalid fluvial provenance");
  for (const [i, region] of manifest.regions.entries()) {
    if (region.id !== config.regions[i].id || !same(region.bbox, config.regions[i].bbox) ||
        !Number.isSafeInteger(region.width) || !Number.isSafeInteger(region.height) || region.width <= 0 || region.height <= 0 || region.width * region.height > 500000 ||
        !Array.isArray(region.web_extent) || region.web_extent.length !== 4 || !region.web_extent.every(Number.isFinite) ||
        region.web_extent[0] >= region.web_extent[2] || region.web_extent[1] >= region.web_extent[3] ||
        !Number.isSafeInteger(region.web_common_pixels) || region.web_common_pixels < 0 || region.web_common_pixels > region.width * region.height ||
        !Array.isArray(region.scenes) || region.scenes.length !== config.scenes.length) throw new Error("Invalid region grid");
    for (const [j, row] of region.scenes.entries()) {
      const pinned = config.scenes[j];
      if (row.id !== pinned.id || row.collection !== pinned.collection || row.date !== pinned.date || !row.acquired_at?.startsWith(pinned.date) ||
          row.url !== `data/fluvial/${region.id}-${row.date}.bin.gz` || !/^[a-f0-9]{64}$/.test(row.sha256) ||
          row.decoded_bytes !== region.width * region.height * 7 * 4 || !Number.isSafeInteger(row.size_bytes) || row.size_bytes <= 0 || row.size_bytes > row.decoded_bytes + 1000 ||
          !Array.isArray(row.radiometry) || row.radiometry.length !== 6 || row.radiometry.some((band, k) => band.band !== config.bands[k] ||
            !Number.isFinite(band.scale) || !Number.isFinite(band.offset) || band.scale <= 0 || band.native_m !== (k < 4 ? 10 : 20))) throw new Error("Invalid dated numerical pack");
    }
  }
  return manifest;
}
export async function decodePack(bytes, row, region) {
  if (bytes.byteLength !== row.size_bytes) throw new Error("Incomplete download");
  const digest = [...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))].map(value => value.toString(16).padStart(2, "0")).join("");
  if (digest !== row.sha256) throw new Error("Changed numerical data");
  const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"));
  const reader = stream.getReader(); const chunks = []; let total = 0;
  while (true) {
    const {value, done} = await reader.read(); if (done) break;
    total += value.byteLength;
    if (total > row.decoded_bytes) { await reader.cancel(); throw new Error("Oversized pack"); }
    chunks.push(value);
  }
  if (total !== row.decoded_bytes) throw new Error("Incomplete numerical grid");
  const raw = new Uint8Array(total); let offset = 0;
  for (const chunk of chunks) { raw.set(chunk, offset); offset += chunk.byteLength; }
  const view = new DataView(raw.buffer), values = new Float32Array(total / 4), n = region.width * region.height;
  for (let i = 0; i < values.length; i++) values[i] = view.getFloat32(i * 4, true);
  for (let i = 0; i < n; i++) {
    const usable = values[6 * n + i];
    if (usable !== 0 && usable !== 1) throw new Error("Invalid QA");
    for (let band = 0; band < 6; band++) {
      const value = values[band * n + i];
      if (usable ? !Number.isFinite(value) || value < 0 : value !== -9999) throw new Error("QA/NoData mismatch");
    }
  }
  return {width: region.width, height: region.height, values};
}
