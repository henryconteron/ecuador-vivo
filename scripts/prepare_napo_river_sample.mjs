/** Stage a frozen deduplicated sample; never rewrite a published receipt/raster. */
import fs from "node:fs";
import path from "node:path";
import {createHash} from "node:crypto";
import {fileURLToPath} from "node:url";
import {validateRiverManifest} from "../assets/js/map/rivers.js";
import {summarizeRiverObservations} from "../assets/js/map/rivers-observations.js";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const sha = bytes => createHash("sha256").update(bytes).digest("hex");
const RULE = "frozen-inventory-acquisition-tile-latest-generation-v1";
const encode = value => `${JSON.stringify(value, null, 2)}\n`;

export function loadSampleSource(root = ROOT) {
  const publishedConfig = JSON.parse(fs.readFileSync(path.join(root, "data/rivers/napo-config.json"), "utf8"));
  const archived = publishedConfig.scene_selection?.mode === RULE;
  const prefix = archived ? "data/rivers/history/pre-dedup-" : "data/rivers/napo-";
  const manifestBytes = fs.readFileSync(path.join(root, `${prefix}manifest.json`));
  if (archived && sha(manifestBytes) !== publishedConfig.scene_selection.source_manifest_sha256) throw new Error("Original archived manifest fingerprint changed");
  return {manifestBytes, manifest: JSON.parse(manifestBytes), config: JSON.parse(fs.readFileSync(path.join(root, `${prefix}config.json`), "utf8"))};
}

export function prepareSample(manifest, config, manifestHash) {
  if (!/^[a-f0-9]{64}$/.test(manifestHash)) throw new Error("Missing original manifest fingerprint");
  if (!validateRiverManifest(manifest, config)) throw new Error("No verified RGB sample to deduplicate");
  const inventory = summarizeRiverObservations(manifest.receipt.scenes);
  const years = inventory.map((row, i) => {
    const groups = new Map();
    for (const record of row.records) {
      if (!groups.has(record.acquisition_tile)) groups.set(record.acquisition_tile, []);
      groups.get(record.acquisition_tile).push(record);
    }
    const retained = [], decisions = [];
    for (const [key, group] of groups) {
      // ID component 2 is provider generation time, not a quality/confidence rank.
      // Descending lexical order is chronological for its fixed UTC format.
      const ranked = [...group].sort((a, b) => a.id.split("_")[1] === b.id.split("_")[1] ?
        b.id.localeCompare(a.id) : (a.id.split("_")[1] < b.id.split("_")[1] ? 1 : -1));
      retained.push(ranked[0]);
      if (ranked.length > 1) decisions.push({acquisition_tile: key, retained: ranked[0].id, discarded: ranked.slice(1).map(record => record.id)});
    }
    retained.sort((a, b) => a.id.localeCompare(b.id));
    if (retained.length < config.min_observations) throw new Error("Deduplicated inventory below minimum; no script");
    return {year: row.year, period: [...config.periods[i]], original_entries: row.entries,
      selected_entries: retained.length, distinct_utc_days: new Set(retained.map(record => record.day)).size,
      scene_ids: retained.map(record => record.id), acquired_ms: retained.map(record => record.acquired_ms), decisions};
  });
  return {schema_version: 1, status: "planned-not-exported-not-validated", rule: RULE,
    source_manifest_sha256: manifestHash, source_rgb_receipt_sha256: manifest.receipt_sha256,
    processing_block: structuredClone(manifest.receipt.processing_block),
    no_refill: true, no_new_scenes: true, per_pixel_support_unknown_until_reexport: true,
    limitations: ["Latest generation ID is a reproducible choice, not proven better quality.",
      "Deduplicating a frozen sample does not balance months, seasons or river levels.",
      "Selected tile/pass groups are not independent days; pixel masks remain unknown.",
      "Existing RGB, counts and candidate cells are unchanged and unreviewed."], years};
}

function replaceOnce(source, original, replacement) {
  if (source.split(original).length !== 2) throw new Error("Exporter template changed: review adaptation before staging");
  return source.replace(original, replacement);
}

export function stageRecipe(manifest, config, manifestBytes, template) {
  if (JSON.stringify(JSON.parse(manifestBytes.toString())) !== JSON.stringify(manifest)) throw new Error("Manifest bytes and parsed provenance differ");
  const plan = prepareSample(manifest, config, sha(manifestBytes));
  const planBytes = encode(plan), planHash = sha(planBytes);
  const selection = {mode: RULE, plan_sha256: planHash, source_manifest_sha256: plan.source_manifest_sha256,
    no_refill: true, pinned_scene_ids: plan.years.map(row => row.scene_ids)};
  const nextConfig = {...structuredClone(config), scene_selection: selection};
  let script = template.replaceAll("\r\n", "\n");
  script = replaceOnce(script, "var blockId = 7;", `var blockId = ${plan.processing_block.id};\nvar pinnedPlan = ${JSON.stringify(plan)};`);
  script = replaceOnce(script, "var exportMode = 'water-counts';", "var exportMode = 'audit'; // No export tasks until deliberately changed to 'rgb' or 'water-counts'.");
  script = replaceOnce(script, "var sceneSelection = {mode: 'quarter-cloud-ranked-per-block', max_per_quarter: 8};", `var sceneSelection = ${JSON.stringify(selection)};`);
  script = replaceOnce(script, "if (exportMode !== 'water-counts' && exportMode !== 'rgb')", "if (exportMode !== 'audit' && exportMode !== 'water-counts' && exportMode !== 'rgb')");
  script = replaceOnce(script, "  var province = boundary.geometry(), projection = ee.Projection(crs, crsTransform);", "  if (blockId !== pinnedPlan.processing_block.id) { print('Pinned plan belongs to another block; no tasks.'); return; }\n  var province = boundary.geometry(), projection = ee.Projection(crs, crsTransform);");
  const start = script.indexOf("    // merge() prefixes system:index.");
  const end = script.indexOf("    var quality = ee.ImageCollection(qualityAsset)", start);
  if (start < 0 || end < start) throw new Error("Missing source selection template");
  script = script.slice(0, start) + `    // Frozen selected sample, deduplicated locally without quarterly refill.\n    var optical = ee.ImageCollection.fromImages(pinnedPlan.years[i].scene_ids.map(function (id) {\n      return ee.Image(asset + '/' + id).set('source_scene_index', id);\n    }));\n` + script.slice(end);
  const gate = "    var observations = collections.map(function (collection) {";
  script = replaceOnce(script, gate, `    // Fail closed if any exact asset/QA join or acquisition time changed.\n    var matches = provenance.scenes.every(function (row, i) {\n      return JSON.stringify(row.scene_ids) === JSON.stringify(pinnedPlan.years[i].scene_ids) &&\n        JSON.stringify(row.acquired_ms) === JSON.stringify(pinnedPlan.years[i].acquired_ms);\n    });\n    if (!matches) { print('Pinned scene/QA inventory differs; no exports.', provenance); return; }\n    print('Verified frozen selection; pixel QA and hydrology are not validated.', pinnedPlan);\n    if (exportMode === 'audit') { print('Audit only: zero export tasks; no image calculation or map preview.'); return; }\n` + gate);
  script = replaceOnce(script, "var prefix = 'napo_block' + blockId +", `var prefix = 'napo_block' + blockId + '_dedup_${planHash.slice(0, 12)}' +`);
  script = `/* GENERATED by scripts/prepare_napo_river_sample.mjs.\n * Plan SHA-256: ${planHash}\n * Template SHA-256: ${sha(template)}\n * Planned only: does not replace the published bundle.\n * Default audit queries metadata/QA IDs, not zero-cost or validated pixel support.\n */\n` + script;
  return {plan, planHash, files: {"scene-plan.json": planBytes, "napo-config-next.json": encode(nextConfig), "export_napo_rivers_pinned_gee.js": script}};
}

function main(args) {
  if (args.includes("--help")) {
    console.log("node scripts/prepare_napo_river_sample.mjs [--check]\nStages only in tmp/rivers-next. --check validates the recipe without writing. No network, GEE task or publication."); return;
  }
  if (args.some(arg => arg !== "--check")) throw new Error("Unknown argument; use --help");
  const {manifestBytes, manifest, config} = loadSampleSource();
  const template = fs.readFileSync(path.join(ROOT, "scripts/export_napo_rivers_gee.js"), "utf8");
  const staged = stageRecipe(manifest, config, manifestBytes, template);
  console.log(`Planned block ${staged.plan.processing_block.id}: ${staged.plan.years.map(row => `${row.year}: ${row.original_entries} → ${row.selected_entries} files`).join("; ")}. Plan SHA-256 ${staged.planHash}`);
  if (args.includes("--check")) return;
  const output = path.join(ROOT, "tmp/rivers-next");
  // Refuse any path redirected by a symlink/junction outside this exact staging area.
  fs.mkdirSync(output, {recursive: true});
  if (fs.realpathSync(output).toLowerCase() !== output.toLowerCase()) throw new Error("Staging path redirected; refusing writes");
  for (const [name, content] of Object.entries(staged.files)) {
    const target = path.join(output, name);
    if (fs.existsSync(target)) {
      if (fs.readFileSync(target, "utf8") !== content) throw new Error(`Existing staging file differs; preserve/review it first: ${target}`);
    } else fs.writeFileSync(target, content, {flag: "wx"});
  }
  console.log(`Staged in ${output}; published files unchanged. Generated GEE script defaults to audit only.`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { main(process.argv.slice(2)); } catch (error) { console.error(error.message); process.exitCode = 1; }
}
