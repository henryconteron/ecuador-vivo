import assert from "node:assert/strict";
import fs from "node:fs";
import {comparisonPosition, validateImageryManifest} from "../assets/js/map/imagery.js";
const config = JSON.parse(fs.readFileSync("data/imagery/napo-config.json", "utf8"));
const landcover = JSON.parse(fs.readFileSync("data/landcover/napo-manifest.json", "utf8"));
const exporter = fs.readFileSync("scripts/export_napo_imagery_gee.js", "utf8");
for (const value of [config.source.asset, config.source.quality_asset, JSON.stringify(config.bbox).replaceAll(",", ", "),
  JSON.stringify(config.excluded_scl).replaceAll(",", ", ")]) assert.ok(exporter.includes(value));
assert.ok(exporter.includes("var threshold = 0.65;") && config.clear_threshold === 0.65);
assert.ok(exporter.includes("var minObservations = 3;") && config.min_observations === 3);
assert.ok(exporter.includes("var scale = 30;") && config.export_scale_m === 30);
assert.ok(exporter.includes(".evaluate(") && !exporter.includes(".getInfo("));
assert.ok(exporter.includes("unmask(65535)") && exporter.includes("noData: 65535"));
assert.deepEqual(config.period, ["2024-01-01", "2025-01-01"]);
for (const [input, expected] of [["0", 0], ["50", 50], [100, 100], [-2, 0], [110, 100], [NaN, 50]]) assert.equal(comparisonPosition(input), expected);
assert.equal(validateImageryManifest({schema_version: 1, status: "pending"}, config, landcover), null);
// Tiny fictitious metadata fixture for validation tests only; never a published image.
const receipt = {schema_version: 1, asset: config.source.asset, quality_asset: config.source.quality_asset,
  ...Object.fromEntries(["period", "bbox", "bands", "quality_band", "clear_threshold", "min_observations", "excluded_scl", "composite", "export_crs", "export_scale_m"].map(key => [key, config[key]])),
  nominal_resolution_m: 10, reflectance_scale: 0.0001, export_resampling: "nearest", source_count: 4, joined_count: 3,
  scene_ids: ["test-a", "test-b", "test-c"], acquired_ms: [1, 2, 3].map(day => Date.parse(`2024-01-0${day}`)), export_requested_at: "2026-09-30T00:00:00Z"};
const fixture = {schema_version: 1, status: "ready", source: config.source, period: config.period, bbox: config.bbox, scope: config.scope,
  display: config.display, display_bounds: landcover.display_bounds, classification_sha256: landcover.images[1].sha256,
  display_crs: "EPSG:3857", display_sampling_m: 30, reflectance_resampling: "bilinear", mask_resampling: "nearest", width: 4, height: 4,
  input_sha256: "a".repeat(64), receipt_sha256: "b".repeat(64), receipt,
  images: [{kind: "observation", url: "assets/images/imagery/napo-sentinel2-2024.webp", sha256: "c".repeat(64)},
    {kind: "classification", url: "assets/images/imagery/napo-mapbiomas-2024.png", sha256: "d".repeat(64)}],
  statistics: {window_pixels: 16, usable_pixels: 15, counted_pixels: 16, paired_display_pixels: 15, classified_display_pixels: 16,
    min_clear_scenes: 3, median_clear_scenes: 3, max_clear_scenes: 3}};
assert.equal(validateImageryManifest(fixture, config, landcover), fixture);
for (const mutate of [
  m => {m.images[0].url = "https://untrusted.example/image.webp";},
  m => {m.images[0].sha256 = "missing";},
  m => {m.classification_sha256 = "e".repeat(64);},
  m => {m.display_bounds[0][0] += 0.01;},
  m => {m.display_sampling_m = 10;},
  m => {m.mask_resampling = "bilinear";},
  m => {m.receipt.scene_ids[1] = m.receipt.scene_ids[0];},
  m => {m.receipt.acquired_ms[0] = Date.parse("2025-01-01");},
  m => {m.receipt.clear_threshold = 0.3;},
  m => {m.statistics.usable_pixels = 20;},
  m => {m.statistics.max_clear_scenes = 4;},
  m => {m.statistics.min_clear_scenes = 2;},
  m => {m.statistics.paired_display_pixels = 17;},
]) { const invalid = structuredClone(fixture); mutate(invalid); assert.throws(() => validateImageryManifest(invalid, config, landcover)); }
console.log("Imagery provenance, quality, shared grid and slider validation passed.");
