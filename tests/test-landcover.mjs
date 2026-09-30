import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import {classShares, formatClassShare, validateLandcoverManifest} from "../assets/js/map/landcover.js";
assert.equal(formatClassShare(0, "es"), "0%");
assert.equal(formatClassShare(0.0002, "es"), "<0,1%");
assert.equal(formatClassShare(0.03, "en"), "<0.1%");
assert.equal(formatClassShare(71.2, "es"), "71,2%");
assert.throws(() => formatClassShare(NaN, "en"));
assert.throws(() => formatClassShare(101, "en"));
const config = JSON.parse(fs.readFileSync("data/landcover/napo-config.json", "utf8"));
assert.equal(config.source.asset, "projects/mapbiomas-public/assets/ecuador/lulc/v1");
assert.deepEqual(config.years, [2000, 2024]);
assert.equal(new Set(config.legend.map(row => row.id)).size, config.legend.length);
assert.ok(config.legend.every(row => /^#[a-f0-9]{6}$/i.test(row.color) && row.es && row.en));
const exporter = fs.readFileSync("scripts/export_napo_landcover_gee.js", "utf8");
assert.ok(exporter.includes(config.source.asset));
assert.ok(exporter.includes(JSON.stringify(config.years).replaceAll(",", ", ")));
assert.ok(exporter.includes(JSON.stringify(config.bbox).replaceAll(",", ", ")));
assert.ok(exporter.includes("crsTransform: projection.transform"));
assert.ok(!exporter.includes(".getInfo("), "Exporter must not block the browser with synchronous requests");
// Simulate only the asynchronous control flow, not Earth Engine or real Napo data.
function exerciseExporter({counts = [1, 1], lookupFailure, metadataFailure, scale = 30, differentGrid = false} = {}) {
  const callbacks = [], tasks = [], messages = [];
  const grid = {crs: "EPSG:4326", transform: [0.0002695, 0, 0, 0, -0.0002695, 0]};
  const projection = {nominalScale: () => 30};
  const image = {select() { return this; }, rename() { return this; }, projection: () => projection,
    clip() { return this; }, unmask() { return this; }, toUint8() { return this; }};
  const Image = () => image; Image.cat = () => image;
  const ee = {
    Geometry: {Rectangle: () => ({})},
    ImageCollection: () => ({filter: () => ({size: () => 1, first: () => image})}),
    Filter: {eq: () => ({})}, Image,
    List: () => ({evaluate: callback => callbacks.push(() => callback(counts, lookupFailure))}),
    Dictionary: () => ({evaluate: callback => callbacks.push(() => callback({projection: grid,
      secondProjection: differentGrid ? {...grid, crs: "EPSG:3857"} : grid,
      nominalScale: scale}, metadataFailure))}),
    Feature: (geometry, properties) => ({geometry, properties}), FeatureCollection: rows => rows
  };
  vm.runInNewContext(exporter, {ee, print: (...args) => messages.push(args),
    Export: {image: {toDrive: args => tasks.push(args)}, table: {toDrive: args => tasks.push(args)}},
    Map: {centerObject() {}, addLayer() {}}});
  assert.equal(tasks.length, 0, "No task before asynchronous source validation");
  callbacks.shift()();
  assert.equal(tasks.length, 0, "No task before asynchronous grid validation");
  if (callbacks.length) callbacks.shift()();
  return {tasks, messages};
}
const successfulExport = exerciseExporter();
assert.equal(successfulExport.tasks.length, 2);
assert.deepEqual(Array.from(successfulExport.tasks[0].crsTransform), [0.0002695, 0, 0, 0, -0.0002695, 0]);
assert.deepEqual(JSON.parse(successfulExport.tasks[1].collection[0].properties.receipt).years, config.years);
for (const bad of [{counts: [0, 1]}, {counts: [2, 1]}, {counts: null}, {lookupFailure: "offline"},
  {metadataFailure: "offline"}, {scale: 100}, {scale: NaN}, {differentGrid: true}]) {
  const result = exerciseExporter(bad);
  assert.equal(result.tasks.length, 0);
  assert.ok(result.messages.length, "Failure must be explained in the console");
}
assert.equal(validateLandcoverManifest({schema_version: 1, status: "pending"}, config), null);

// Synthetic fixture exists only in tests; never shipped as a production raster.
const fixture = {schema_version: 1, status: "ready", source: config.source,
  years: config.years, bbox: config.bbox, scope: config.scope,
  display_crs: "EPSG:3857", display_resampling: "nearest", display_bounds: [[-1.12, -78.04], [-0.72, -77.55]],
  input_sha256: "a".repeat(64), receipt_sha256: "b".repeat(64),
  images: config.years.map(year => ({year, url: `assets/images/landcover/napo-v1-${year}.png`, sha256: "c".repeat(64)})),
  statistics: {common_observed_pixels: 4, window_pixels: 5, observed_pixels: [4, 5], changed_class_pixels: 1, classes: [{id: 3, pixels: [3, 2]}, {id: 21, pixels: [1, 2]}]}};
assert.equal(validateLandcoverManifest(fixture, config), fixture);
assert.deepEqual(classShares(fixture, 0).map(row => row.percent), [75, 25]);
assert.throws(() => classShares(fixture, 2));
for (const mutate of [
  x => { x.source.version = "Collection 4"; },
  x => { x.images[0].url = "https://untrusted.example/map.png"; },
  x => { x.images[0].url = "../secret.png"; },
  x => { x.statistics.classes[0].pixels[0] = 9; },
  x => { x.statistics.classes[0].id = 99; },
  x => { x.statistics.common_observed_pixels = 0; },
  x => { x.statistics.observed_pixels[0] = 0; },
  x => { x.display_resampling = "bilinear"; },
  x => { x.display_bounds[0][0] = NaN; },
]) {
  const invalid = structuredClone(fixture); mutate(invalid);
  assert.throws(() => validateLandcoverManifest(invalid, config));
}
console.log("Land-cover manifest, comparison, and shared export parameters passed.");
