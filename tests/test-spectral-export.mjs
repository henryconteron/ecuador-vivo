import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
const source = fs.readFileSync("scripts/export_napo_spectral_gee.js", "utf8");
const config = JSON.parse(fs.readFileSync("data/spectral/napo-config.json", "utf8"));
assert.ok(source.includes(".evaluate(") && !source.includes(".getInfo("));
assert.ok(!source.includes(".normalizedDifference("));
assert.ok(source.includes(".unmask(-9999)") && source.includes("noData: -9999"));
// ES5-like execution fixture tests client-side task gating, not server computation.
function run(metadata, failure) {
  const exports = [], output = [];
  const chain = new Proxy({}, {get: () => () => chain});
  const dictionary = value => ({evaluate: callback => callback(metadata, failure), value});
  const image = () => chain; image.cat = () => chain;
  const context = vm.createContext({
    ee: {Geometry: {Rectangle: () => chain}, ImageCollection: () => chain, Image: image,
      Feature: () => chain, FeatureCollection: () => chain, Dictionary: dictionary,
      Join: {inner: () => chain}, Filter: {equals: () => chain}, Reducer: {min: () => chain}},
    Export: {image: {toDrive: params => exports.push(params)}, table: {toDrive: params => exports.push(params)}},
    Map: {centerObject() {}, addLayer() {}}, print: (...args) => output.push(args),
  });
  vm.runInContext("Number.isInteger = undefined;", context);
  vm.runInContext(source, context);
  return {exports, output, context};
}
const metadata = {scenes: config.years.map((year, index) => ({year, period: config.periods[index],
  source_count: 3, joined_count: 3, scene_ids: ["test-a", "test-b", "test-c"],
  acquired_ms: [1, 2, 3].map(day => Date.parse(`${year}-01-0${day}`))}))};
const result = run(metadata);
assert.equal(result.exports.length, 2);
const {context} = result;
for (const [variable, key] of [["asset", "source"], ["qualityAsset", "quality_asset"]]) {
  assert.equal(context[variable], key === "source" ? config.source.asset : config.source[key]);
}
for (const [variable, key] of [["years", "years"], ["periods", "periods"], ["bbox", "bbox"],
  ["opticalBands", "optical_bands"], ["yearBands", "year_bands"], ["excludedScl", "excluded_scl"], ["crsTransform", "export_transform"]]) {
  assert.deepEqual(JSON.parse(JSON.stringify(context[variable])), config[key]);
}
assert.equal(context.threshold, config.clear_threshold);
assert.equal(context.minObservations, config.min_observations);
assert.equal(context.crs, config.export_crs);
assert.deepEqual(JSON.parse(JSON.stringify(result.exports[0].crsTransform)), config.export_transform);
assert.equal(result.exports[0].folder, "EcuadorVivo");
for (const invalid of [null, {scenes: []}, ...[
  m => {m.scenes[0].joined_count = 2;}, m => {m.scenes[0].source_count = 801;},
  m => {m.scenes[1].year = 2025;}, m => {m.scenes[1].scene_ids.pop();},
  m => {m.scenes[0].joined_count = NaN;}, m => {m.scenes[0].source_count = 2;},
  m => {m.scenes[0].scene_ids[0] = m.scenes[0].scene_ids[1];},
  m => {m.scenes[0].acquired_ms[0] = Date.parse("2020-01-01");},
  m => {m.scenes[0].period[1] = "2019-12-01";},
].map(mutate => {const copy = structuredClone(metadata); mutate(copy); return copy;})]) {
  assert.equal(run(invalid).exports.length, 0);
}
assert.equal(run(null, "test-only network failure").exports.length, 0);
console.log("Spectral export config, async failure gating and ES5 compatibility passed.");
