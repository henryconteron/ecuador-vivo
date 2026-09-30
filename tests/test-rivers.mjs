import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import {validateRiverManifest, validateRiverCandidates} from "../assets/js/map/rivers.js";
const config = JSON.parse(fs.readFileSync("data/rivers/napo-config.json", "utf8"));
assert.equal(validateRiverManifest({schema_version: 1, status: "pending"}, config), null);
assert.throws(() => validateRiverManifest({schema_version: 1, status: "ready"}, config));
const manifest = {candidate_count: 1};
const row = {geometry: {type: "Point", coordinates: [-77.8, -1.0]}, properties: {kind: "water-frequency-change-candidate", status: "unreviewed", years: [2019, 2024],
  sampling_m: 10, screening_cell_m: 1000, min_observations: 10, water_threshold: 0.2, change_threshold: 0.5, cell_id: 123, gain_ha: 1.1, loss_ha: 0}};
const collection = {type: "FeatureCollection", features: [row]};
// These objects are validation fixtures only, never written to public files.
const dx = (config.processing_grid.bbox[2] - config.processing_grid.bbox[0]) / 3, dy = (config.processing_grid.bbox[3] - config.processing_grid.bbox[1]) / 3;
const left = config.processing_grid.bbox[0] + dx, top = config.processing_grid.bbox[3] - 2 * dy;
const receipt = {...config, processing_block: {id: 7, bbox: [left, top - dy, left + dx, top]}, boundary: {properties: {shapeName: "Napo", shapeGroup: "ECU"}, geometry: {type: "Polygon"}}, export_requested_at: "2026-09-30T18:00:00Z",
  scenes: config.years.map((year, i) => ({year, period: config.periods[i], joined_count: 10, scene_ids: Array.from({length: 10}, (_, n) => `test-${year}-${n}`),
    acquired_ms: Array.from({length: 10}, () => Date.parse(config.periods[i][0]))}))};
const ready = {schema_version: 1, status: "ready", config, receipt, sampling_m: 10, resampling: "nearest", tile_format: "lossless-webp", tile_size: 512,
  zoom_offset: -1, min_native_zoom: 9, max_native_zoom: 14, receipt_sha256: "a".repeat(64), candidates_sha256: "b".repeat(64), candidate_status: "ready",
  display_bounds: [[top - dy, left], [top, left + dx]], coverage: {kind: "processing-block", block_ids: [7], total_blocks: 9}, candidate_count: 1, input_chunks: [{name: "test-only.tif", sha256: "c".repeat(64)}],
  tiles: [2019, 2024].map(year => ({url: `assets/images/rivers/${year}/13/2330/4100.webp`, sha256: "d".repeat(64), size_bytes: 123}))};
assert.equal(validateRiverManifest(ready, config), ready);
const rgbOnly = {...ready, candidate_status: "pending", candidate_count: null, candidates_sha256: null};
assert.equal(validateRiverManifest(rgbOnly, config), rgbOnly);
for (const mutate of [m => m.sampling_m = 30, m => m.receipt.scenes[0].acquired_ms[0] = 0, m => m.tiles.pop(), m => m.tiles[0].url = "../wrong.webp",
  m => m.tile_format = "lossy-webp", m => m.display_bounds[0][1] = -80, m => m.candidate_status = "confirmed"]) {
  const invalid = structuredClone(ready); mutate(invalid); assert.throws(() => validateRiverManifest(invalid, config));
}
assert.throws(() => validateRiverManifest({...rgbOnly, candidate_count: 0}, config));
assert.equal(validateRiverCandidates(collection, manifest), collection);
assert.equal(validateRiverCandidates(collection, ready), collection);
assert.throws(() => validateRiverCandidates(collection, {...ready, display_bounds: [[-0.5, -78.4], [-0.3, -78.2]]}));
for (const mutate of [r => r.properties.status = "confirmed", r => r.properties.gain_ha = NaN, r => r.properties.sampling_m = 30, r => r.geometry.coordinates[0] = 0]) {
  const invalid = structuredClone(collection); mutate(invalid.features[0]); assert.throws(() => validateRiverCandidates(invalid, manifest));
}
assert.throws(() => validateRiverCandidates({...collection, features: [row, row]}, {candidate_count: 2}));
const code = fs.readFileSync("scripts/export_napo_rivers_gee.js", "utf8");
const chain = new Proxy({}, {get: (_, key) => key === "evaluate" ? callback => callback(0, null) : () => chain});
const context = vm.createContext({ee: {FeatureCollection: () => chain, Filter: {eq: () => chain}}, print() {}});
vm.runInContext(code, context);
for (const [variable, key] of [["asset", "asset"], ["qualityAsset", "quality_asset"], ["boundaryAsset", "boundary_asset"], ["boundaryFilter", "boundary_filter"],
  ["years", "years"], ["periods", "periods"], ["bands", "bands"], ["excludedScl", "excluded_scl"], ["crs", "export_crs"], ["crsTransform", "export_transform"],
  ["exportBands", "export_bands"], ["display", "display"], ["threshold", "clear_threshold"], ["minObservations", "min_observations"],
  ["waterThreshold", "water_threshold"], ["changeThreshold", "change_threshold"], ["waterFrequencyMin", "water_frequency_min"], ["rgbMinObservations", "rgb_min_observations"],
  ["processingGrid", "processing_grid"], ["sceneSelection", "scene_selection"],
  ["minConnectedPixels", "min_connected_pixels"], ["cellSize", "screening_cell_m"], ["minCellChangeHa", "min_cell_change_ha"], ["fileDimensions", "file_dimensions"], ["maxPixels", "max_pixels"]]) {
  assert.deepEqual(JSON.parse(JSON.stringify(context[variable])), config[key], variable);
}
assert.ok(!code.includes(".getInfo(") && !code.includes(".normalizedDifference("));
assert.ok(code.includes("size !== 1") && code.includes(".toByte()") && code.includes(".sum()"));
assert.ok(!code.includes(".reduceToVectors(") && !code.includes(".connectedPixelCount("));
assert.equal(context.exportMode, "water-counts");
assert.deepEqual(JSON.parse(JSON.stringify(context.countBands)), ["y2019_water_count", "y2019_valid_count", "y2024_water_count", "y2024_valid_count"]);
// Earth Engine merge() rewrites system:index: QA must join the original ID.
assert.ok(code.includes("image.set('source_scene_index', image.get('system:index'))"));
assert.ok(code.includes("leftField: 'source_scene_index', rightField: 'system:index'"));
assert.ok(code.includes("aggregate_array('source_scene_index')"));
console.log("Provincial river settings, native grid, pending state and screening integrity passed.");
