import assert from "node:assert/strict";
import fs from "node:fs";
import {comparisonCrop, loadSpectralPair, validateSpectralManifest} from "../assets/js/map/spectral.js";
const read = path => JSON.parse(fs.readFileSync(path, "utf8"));
const config = read("data/spectral/napo-config.json"), grid = read("data/landcover/napo-manifest.json");
const fields = ["years", "periods", "bbox", "optical_bands", "year_bands", "quality_band", "clear_threshold", "min_observations", "excluded_scl", "composite", "observation_mask", "index_formulas", "export_crs", "export_transform", "nodata"];
// Fictitious metadata fixture is validator input only, never a public image.
const fixture = {schema_version: 1, status: "ready",
  ...Object.fromEntries(["source", "years", "periods", "bbox", "scope", "display", "river_focus_bbox", "context_source"].map(key => [key, config[key]])),
  display_bounds: grid.display_bounds, grid_reference_sha256: grid.images.find(row => row.year === 2024).sha256,
  display_crs: "EPSG:3857", display_sampling_m: 30, width: 4, height: 4,
  reflectance_resampling: "bilinear", index_resampling: "nearest", mask_resampling: "nearest",
  input_sha256: "a".repeat(64), receipt_sha256: "b".repeat(64),
  receipt: {schema_version: 1, asset: config.source.asset, quality_asset: config.source.quality_asset,
    ...Object.fromEntries(fields.map(key => [key, config[key]])), reflectance_scale: 0.0001,
    export_resampling: "nearest", export_requested_at: "2026-09-30T00:00:00Z",
    scenes: config.years.map((year, index) => ({year, period: config.periods[index], source_count: 3, joined_count: 3,
      scene_ids: ["test-a", "test-b", "test-c"], acquired_ms: [1, 2, 3].map(day => Date.parse(`${year}-01-0${day}`))}))},
  statistics: {window_pixels: 16, common_pixels: 14, paired_display_pixels: 14,
    years: config.years.map(year => ({year, usable_pixels: 15, min_clear_scenes: 3, median_clear_scenes: 3, max_clear_scenes: 3}))},
  images: config.years.flatMap(year => ["rgb", "ndvi", "mndwi"].map(mode => ({year, mode,
    url: `assets/images/spectral/napo-${mode}-${year}.${mode === "rgb" ? "webp" : "png"}`, sha256: "c".repeat(64)}))),
};
assert.equal(validateSpectralManifest({schema_version: 1, status: "pending"}, config, grid), null);
assert.equal(validateSpectralManifest(fixture, config, grid), fixture);
for (const mutate of [
  m => {m.images[0].url = "https://untrusted.example/view.webp";}, m => {m.images[1].mode = "rgb";},
  m => {m.images[0].sha256 = "missing";}, m => {m.images.reverse();},
  m => {m.grid_reference_sha256 = "d".repeat(64);}, m => {m.display_bounds[0][0] += 0.01;},
  m => {m.display_sampling_m = 10;}, m => {m.mask_resampling = "bilinear";}, m => {m.index_resampling = "bilinear";},
  m => {m.receipt.scenes[0].source_count = 801;}, m => {m.receipt.scenes[0].scene_ids[0] = "test-b";},
  m => {m.receipt.scenes[0].acquired_ms[0] = Date.parse("2020-01-01");},
  m => {m.receipt.clear_threshold = 0.3;}, m => {m.receipt.index_formulas.mndwi = "wrong";},
  m => {m.receipt.export_requested_at = "2026-09-30T00:00:00";},
  m => {m.statistics.common_pixels = 16;}, m => {m.statistics.years[0].min_clear_scenes = 2;},
  m => {m.statistics.years[0].max_clear_scenes = 4;}, m => {m.statistics.paired_display_pixels = 17;},
]) {
  const invalid = structuredClone(fixture); mutate(invalid);
  assert.throws(() => validateSpectralManifest(invalid, config, grid));
}
const complete = comparisonCrop(grid.display_bounds, [grid.display_bounds[0][1], grid.display_bounds[0][0], grid.display_bounds[1][1], grid.display_bounds[1][0]]);
assert.deepEqual(complete, {left: 0, top: 0, width: 1, height: 1});
const crop = comparisonCrop(grid.display_bounds, config.river_focus_bbox);
assert.ok(crop.width < 1 && crop.height < 1 && crop.left > 0 && crop.top > 0);
assert.throws(() => comparisonCrop(grid.display_bounds, [-90, -1, -89, -0.8]));
assert.throws(() => comparisonCrop([[-90, -78], [90, -77]], config.river_focus_bbox));
const rows = [fixture.images[0], fixture.images[3]];
function mockImage({failure = false, badSize = false} = {}) {
  return () => ({naturalWidth: badSize ? 2 : 4, naturalHeight: 4,
    set src(value) {this.url = value; queueMicrotask(() => failure ? this.onerror() : this.onload());}});
}
const pair = await loadSpectralPair(rows, {width: 4, height: 4, createImage: mockImage()});
assert.equal(pair.length, 2); assert.ok(pair[0].url.includes("2019") && pair[1].url.includes("2024"));
assert.equal(await loadSpectralPair(rows, {width: 4, height: 4, isCurrent: () => false, createImage: mockImage()}), null);
for (const options of [{failure: true}, {badSize: true}]) {
  await assert.rejects(loadSpectralPair(rows, {width: 4, height: 4, createImage: mockImage(options)}));
}
await assert.rejects(loadSpectralPair([], {width: 4, height: 4}));
const markup = fs.readFileSync("explore.html", "utf8");
for (const id of ["spectral-launch", "spectral-dialog", "spectral-focus", "spectral-slider", "spectral-stage"]) {
  assert.equal([...markup.matchAll(new RegExp(`id="${id}"`, "g"))].length, 1);
}
assert.ok(markup.includes('data-system-content="life water"'));
assert.ok(fs.readFileSync("learn.html", "utf8").includes("lab=spectral"));
console.log("Spectral provenance, quality, Mercator crop and async pair loading passed.");
