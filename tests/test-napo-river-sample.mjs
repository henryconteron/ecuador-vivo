import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import {createHash} from "node:crypto";
import {prepareSample, stageRecipe, loadSampleSource} from "../scripts/prepare_napo_river_sample.mjs";
import {validateRiverManifest} from "../assets/js/map/rivers.js";
import {compareSamples} from "../scripts/promote_napo_river_sample.mjs";
const {manifestBytes: bytes, manifest, config} = loadSampleSource();
const template = fs.readFileSync("scripts/export_napo_rivers_gee.js", "utf8");
const original = structuredClone(manifest), recipe = stageRecipe(manifest, config, bytes, template);
assert.deepEqual(manifest, original, "Never mutate existing provenance");
assert.deepEqual(recipe, stageRecipe(manifest, config, bytes, template), "Deterministic recipe, no wall-clock timestamps");
assert.deepEqual(recipe.plan.years.map(row => row.selected_entries), [31, 32]);
assert.deepEqual(recipe.plan.years.map(row => row.distinct_utc_days), [17, 13]);
assert.equal(recipe.plan.years[0].decisions[0].retained, "20190621T153629_20190621T154333_T17MRU");
assert.deepEqual(recipe.plan.years[0].decisions[0].discarded, ["20190621T153629_20190621T153627_T17MRU"]);
for (const [i, row] of recipe.plan.years.entries()) {
  assert.ok(row.scene_ids.every(id => manifest.receipt.scenes[i].scene_ids.includes(id)), "No invented/replacement acquisitions");
  assert.equal(new Set(row.scene_ids.map(id => { const parts = id.split("_"); return `${parts[0]}_${parts[2]}`; })).size, row.selected_entries);
}
assert.equal(recipe.plan.status, "planned-not-exported-not-validated");
assert.throws(() => prepareSample(manifest, config, "unknown"));
assert.throws(() => stageRecipe(manifest, config, Buffer.from("{}"), template));
assert.throws(() => stageRecipe(manifest, config, bytes, template.replace("var exportMode = 'water-counts';", "")));

// Exercise the generated client gates, not a fake image result or GEE service.
const script = recipe.files["export_napo_rivers_pinned_gee.js"];
const provenance = {scenes: recipe.plan.years.map(row => ({year: row.year, period: row.period, joined_count: row.selected_entries,
  scene_ids: row.scene_ids, acquired_ms: row.acquired_ms})), boundary: manifest.receipt.boundary, area_m2: manifest.receipt.area_m2, bounds: manifest.receipt.bounds};
function runAudit(actual = provenance, boundaryCount = 1, source = script) {
  let tasks = 0; const messages = [];
  const chain = new Proxy({}, {get: (_, key) => key === "evaluate" ? callback => callback(boundaryCount, null) : () => chain});
  const imageCollection = () => chain; imageCollection.fromImages = () => chain;
  const context = vm.createContext({ee: {FeatureCollection: () => chain, Filter: {eq: () => chain, equals: () => chain},
    Projection: () => chain, Geometry: {Rectangle: () => chain}, ImageCollection: imageCollection, Image: () => chain,
    Join: {inner: () => chain}, Dictionary: () => ({evaluate: callback => callback(actual, null)})},
    print: (...args) => messages.push(args[0]), Export: {image: {toDrive: () => tasks++}, table: {toDrive: () => tasks++}}});
  vm.runInContext(source, context);
  assert.equal(tasks, 0); assert.equal(context.exportMode, "audit");
  return messages;
}
assert.ok(runAudit().some(message => message.startsWith("Audit only:")));
const changed = structuredClone(provenance); changed.scenes[0].acquired_ms[0] += 1;
assert.ok(runAudit(changed).some(message => message.startsWith("Pinned scene/QA inventory differs")));
const missing = structuredClone(provenance); missing.scenes[0].joined_count--; missing.scenes[0].scene_ids.pop(); missing.scenes[0].acquired_ms.pop();
assert.ok(runAudit(missing).some(message => message.startsWith("Pinned scene/QA inventory differs")));
assert.ok(runAudit(provenance, 0).some(message => message.startsWith("No unique Napo boundary")));
assert.ok(runAudit(provenance, 1, script.replace("var blockId = 7;", "var blockId = 6;")).some(message => message.startsWith("Pinned plan belongs")));
assert.ok(!script.includes(".median()") || script.indexOf("if (exportMode === 'audit')") < script.indexOf(".median()"));

// Future receipts must agree with the pinned list; never relabel old outputs.
const nextConfig = JSON.parse(recipe.files["napo-config-next.json"]);
const next = structuredClone(manifest); next.config = nextConfig; next.receipt.scene_selection = nextConfig.scene_selection;
next.receipt.scenes = provenance.scenes; next.candidate_status = "pending"; next.candidate_count = null; next.candidates_sha256 = null; delete next.screening;
assert.equal(validateRiverManifest(next, nextConfig), next);
const wrong = structuredClone(next); wrong.receipt.scenes[0].scene_ids[0] = "wrong";
assert.throws(() => validateRiverManifest(wrong, nextConfig));
const repeated = structuredClone(next), repeatedConfig = structuredClone(nextConfig);
repeated.receipt.scenes[0].scene_ids[1] = repeated.receipt.scenes[0].scene_ids[0].replace(/_\d{8}T\d{6}_/, "_20190107T235959_");
repeatedConfig.scene_selection.pinned_scene_ids[0] = [...repeated.receipt.scenes[0].scene_ids];
repeated.config = repeatedConfig; repeated.receipt.scene_selection = repeatedConfig.scene_selection;
assert.throws(() => validateRiverManifest(repeated, repeatedConfig), /Repeated pass/);
// Isolated comparison fixture: never written as a rebuilt scientific product.
const oldCandidatePath = config.scene_selection.mode === "quarter-cloud-ranked-per-block" &&
  JSON.parse(fs.readFileSync("data/rivers/napo-config.json", "utf8")).scene_selection.mode === config.scene_selection.mode ?
  "data/rivers/napo-candidates.geojson" : "data/rivers/history/pre-dedup-candidates.geojson";
const baselineCells = JSON.parse(fs.readFileSync(oldCandidatePath, "utf8"));
const comparisonFixture = structuredClone(manifest);
comparisonFixture.config = nextConfig;
comparisonFixture.receipt.scene_selection = nextConfig.scene_selection;
comparisonFixture.receipt.scenes = provenance.scenes;
comparisonFixture.screening.count_receipt.scene_selection = nextConfig.scene_selection;
comparisonFixture.screening.count_receipt.scenes = provenance.scenes;
const fixtureCells = structuredClone(baselineCells); fixtureCells.metadata = comparisonFixture.screening;
assert.deepEqual(compareSamples(manifest, comparisonFixture, baselineCells, fixtureCells, recipe.plan, recipe.planHash).inventory.map(row => row.after_files), [31, 32]);
const changedPlan = structuredClone(recipe.plan); changedPlan.years[0].acquired_ms[0]++;
assert.throws(() => compareSamples(manifest, comparisonFixture, baselineCells, fixtureCells, changedPlan, recipe.planHash));
assert.throws(() => compareSamples(manifest, comparisonFixture, baselineCells, fixtureCells, recipe.plan, "a".repeat(64)));
const published = JSON.parse(fs.readFileSync("data/rivers/napo-manifest.json", "utf8"));
if (published.config.scene_selection?.mode === nextConfig.scene_selection.mode) {
  const oldCells = JSON.parse(fs.readFileSync("data/rivers/history/pre-dedup-candidates.geojson", "utf8"));
  const cells = JSON.parse(fs.readFileSync("data/rivers/napo-candidates.geojson", "utf8"));
  const comparison = compareSamples(manifest, published, oldCells, cells, recipe.plan, recipe.planHash);
  comparison.rebuilt_manifest_sha256 = createHash("sha256").update(fs.readFileSync("data/rivers/napo-manifest.json")).digest("hex");
  assert.deepEqual(JSON.parse(fs.readFileSync("data/rivers/history/sample-comparison.json", "utf8")), comparison, "Published comparison must agree with both actual receipts/results");
  assert.equal(createHash("sha256").update(fs.readFileSync("data/rivers/history/scene-plan.json")).digest("hex"), recipe.planHash);
  assert.equal(comparison.status, "rebuilt-integrity-verified-unreviewed");
  assert.deepEqual(comparison.inventory.map(row => row.after_files), [31, 32]);
  const altered = structuredClone(recipe.plan); altered.years[0].acquired_ms[0]++;
  assert.throws(() => compareSamples(manifest, published, oldCells, cells, altered, recipe.planHash));
  assert.throws(() => compareSamples(manifest, published, oldCells, cells, recipe.plan, "a".repeat(64)));
}
console.log("Frozen Napo sample: deterministic deduplication, pinned receipt guards and zero-task audit gates passed (not a live GEE validation).");
