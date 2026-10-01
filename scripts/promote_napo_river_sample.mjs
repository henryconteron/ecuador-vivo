/** Verify, compare and optionally promote one real rebuilt sample. Never launch GEE tasks. */
import fs from "node:fs";
import path from "node:path";
import {createHash} from "node:crypto";
import {fileURLToPath} from "node:url";
import {validateRiverManifest, validateRiverCandidates} from "../assets/js/map/rivers.js";
import {summarizeRiverObservations} from "../assets/js/map/rivers-observations.js";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const sha = bytes => createHash("sha256").update(bytes).digest("hex");
const encode = value => `${JSON.stringify(value, null, 2)}\n`;
const read = (root, name) => fs.readFileSync(path.join(root, name));
const parse = (root, name) => JSON.parse(read(root, name));
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const FILES = ["data/rivers/napo-config.json", "data/rivers/napo-candidates.geojson", "data/rivers/napo-manifest.json"];

export function compareSamples(before, after, oldCells, newCells, plan, planHash) {
  validateRiverManifest(before, before.config); validateRiverManifest(after, after.config);
  validateRiverCandidates(oldCells, before); validateRiverCandidates(newCells, after);
  if (before.candidate_status !== "ready" || after.candidate_status !== "ready" ||
      after.config.scene_selection?.plan_sha256 !== planHash ||
      after.config.scene_selection.source_manifest_sha256 !== plan.source_manifest_sha256 ||
      !same(before.receipt.processing_block, after.receipt.processing_block) ||
      !same(before.receipt.boundary, after.receipt.boundary)) throw new Error("Not a paired, rebuilt sample of the same block");
  const expectedConfig = {...structuredClone(before.config), scene_selection: after.config.scene_selection};
  if (!same(expectedConfig, after.config)) throw new Error("Methods changed beyond the pinned scene selection");
  const oldInventory = summarizeRiverObservations(before.receipt.scenes), newInventory = summarizeRiverObservations(after.receipt.scenes);
  for (let i = 0; i < 2; i++) {
    if (!same(after.receipt.scenes[i].scene_ids, plan.years[i].scene_ids) ||
        !same(after.receipt.scenes[i].acquired_ms, plan.years[i].acquired_ms) ||
        after.receipt.scenes[i].scene_ids.some(id => !before.receipt.scenes[i].scene_ids.includes(id))) throw new Error("Rebuilt acquisitions differ from frozen plan");
  }
  const oldById = new Map(oldCells.features.map(f => [f.properties.cell_id, f.properties]));
  const newById = new Map(newCells.features.map(f => [f.properties.cell_id, f.properties]));
  const ids = [...new Set([...oldById.keys(), ...newById.keys()])].sort((a, b) => a - b);
  const oldTiles = new Map(before.tiles.map(row => [row.url, row.sha256])), newTiles = new Map(after.tiles.map(row => [row.url, row.sha256]));
  const metrics = manifest => ({comparable_pixels: manifest.screening.comparable_pixels,
    retained_pixels: manifest.screening.retained_pixels, candidate_cells: manifest.candidate_count,
    rgb_tiles: manifest.tiles.length, rgb_bytes: manifest.tiles.reduce((sum, row) => sum + row.size_bytes, 0)});
  return {schema_version: 1, status: "rebuilt-integrity-verified-unreviewed", plan_sha256: planHash,
    source_manifest_sha256: plan.source_manifest_sha256, processing_block: after.receipt.processing_block,
    before: metrics(before), after: metrics(after),
    rgb_tile_changes: {changed: [...newTiles].filter(([url, hash]) => oldTiles.has(url) && oldTiles.get(url) !== hash).length,
      added: [...newTiles.keys()].filter(url => !oldTiles.has(url)).length, removed: [...oldTiles.keys()].filter(url => !newTiles.has(url)).length},
    inventory: oldInventory.map((row, i) => ({year: row.year, before_files: row.entries, after_files: newInventory[i].entries,
      before_utc_days: row.days, after_utc_days: newInventory[i].days, remaining_pass_tile_variants: newInventory[i].variants.length})),
    cell_changes: ids.map(id => ({cell_id: id, status: !oldById.has(id) ? "added" : !newById.has(id) ? "removed" : "retained",
      before: oldById.has(id) ? {gain_ha: oldById.get(id).gain_ha, loss_ha: oldById.get(id).loss_ha, comparable_pixels: oldById.get(id).comparable_pixels} : null,
      after: newById.has(id) ? {gain_ha: newById.get(id).gain_ha, loss_ha: newById.get(id).loss_ha, comparable_pixels: newById.get(id).comparable_pixels} : null})),
    limitations: ["Technical integrity, not field or hydrological validation.", "Same-day/overlapping tiles may still not be independent observations.",
      "Annual samples are not seasonally matched; latest generation is not proven better quality.",
      "No mining, pollution or channel-migration cause is established; all cells remain unreviewed."]};
}

function verifiedBundle(root) {
  const resolvedRoot = fs.realpathSync(root).toLowerCase();
  for (const name of FILES) if (!fs.realpathSync(path.join(root, name)).toLowerCase().startsWith(`${resolvedRoot}${path.sep}`)) throw new Error("Redirected provenance path");
  const manifest = parse(root, FILES[2]), config = parse(root, FILES[0]);
  if (!validateRiverManifest(manifest, config) || manifest.candidate_status !== "ready") throw new Error("Real paired RGB/count bundle required");
  for (const row of manifest.tiles) {
    const bytes = read(root, row.url);
    if (sha(bytes) !== row.sha256 || bytes.length !== row.size_bytes) throw new Error(`Tile changed: ${row.url}`);
    if (!fs.realpathSync(path.join(root, row.url)).toLowerCase().startsWith(`${fs.realpathSync(root).toLowerCase()}${path.sep}`)) throw new Error("Redirected tile path");
  }
  const bytes = read(root, FILES[1]);
  if (sha(bytes) !== manifest.candidates_sha256) throw new Error("Candidate checksum changed");
  const cells = validateRiverCandidates(JSON.parse(bytes), manifest);
  return {manifest, config, cells};
}

function preserve(target, bytes) {
  fs.mkdirSync(path.dirname(target), {recursive: true});
  if (!fs.realpathSync(path.dirname(target)).toLowerCase().startsWith(`${fs.realpathSync(ROOT).toLowerCase()}${path.sep}`)) throw new Error("Redirected archive/backup directory");
  if (fs.existsSync(target)) {
    if (sha(fs.readFileSync(target)) !== sha(bytes)) throw new Error(`Backup/archive differs; refusing overwrite: ${target}`);
  } else fs.writeFileSync(target, bytes, {flag: "wx"});
}

function main(args) {
  if (args.includes("--help")) {
    console.log("node scripts/promote_napo_river_sample.mjs [--apply]\nDefault: verify/compare tmp/rivers-next/rebuilt without modifying published files. --apply preserves the original bundle, archives provenance and promotes manifest last."); return;
  }
  if (args.some(arg => arg !== "--apply") || args.length > 1) throw new Error("Unknown arguments; use --help");
  const staging = path.join(ROOT, "tmp/rivers-next/rebuilt"), recipeRoot = path.join(ROOT, "tmp/rivers-next");
  if (fs.realpathSync(staging).toLowerCase() !== staging.toLowerCase()) throw new Error("Redirected staging directory");
  const planBytes = read(recipeRoot, "scene-plan.json"), plan = JSON.parse(planBytes), planHash = sha(planBytes);
  const after = verifiedBundle(staging), currentBytes = read(ROOT, FILES[2]);
  if (sha(currentBytes) === sha(read(staging, FILES[2]))) {
    verifiedBundle(ROOT); // Same manifest alone does not guarantee unchanged assets/config.
    console.log("The verified rebuilt bundle is already integrated; no writes."); return;
  }
  if (sha(currentBytes) !== plan.source_manifest_sha256) throw new Error("Published source changed; stop and review before promotion");
  const before = verifiedBundle(ROOT), report = compareSamples(before.manifest, after.manifest, before.cells, after.cells, plan, planHash);
  report.rebuilt_manifest_sha256 = sha(read(staging, FILES[2]));
  console.log(JSON.stringify(report, null, 2));
  if (!args.includes("--apply")) { console.log("Verification only: published bundle unchanged."); return; }
  // Back up every original byte before replacing anything. No delete or rollback-by-reset.
  const backup = path.join(recipeRoot, "original-bundle");
  for (const name of [...FILES, ...before.manifest.tiles.map(row => row.url)]) preserve(path.join(backup, name), read(ROOT, name));
  const history = path.join(ROOT, "data/rivers/history");
  preserve(path.join(history, "pre-dedup-manifest.json"), currentBytes);
  preserve(path.join(history, "pre-dedup-config.json"), read(ROOT, FILES[0]));
  preserve(path.join(history, "pre-dedup-candidates.geojson"), read(ROOT, FILES[1]));
  preserve(path.join(history, "scene-plan.json"), planBytes);
  preserve(path.join(history, "sample-comparison.json"), Buffer.from(encode(report)));
  for (const row of after.manifest.tiles) {
    const target = path.join(ROOT, row.url); fs.mkdirSync(path.dirname(target), {recursive: true});
    if (!fs.realpathSync(path.dirname(target)).toLowerCase().startsWith(`${fs.realpathSync(ROOT).toLowerCase()}${path.sep}`)) throw new Error("Redirected destination");
    fs.copyFileSync(path.join(staging, row.url), target);
  }
  // Fail closed through SHA checks during any interruption; the manifest is last.
  for (const name of FILES) fs.copyFileSync(path.join(staging, name), path.join(ROOT, name));
  verifiedBundle(ROOT);
  console.log("Verified paired sample integrated locally. Original images recoverable under tmp/rivers-next/original-bundle. No commit or push.");
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { main(process.argv.slice(2)); } catch (error) { console.error(error.message); process.exitCode = 1; }
}
