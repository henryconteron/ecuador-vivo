import assert from "node:assert/strict";
import fs from "node:fs";
import crypto from "node:crypto";
import zlib from "node:zlib";
import {ratio, valuesAt, waterVotes, transition, pixelIndex, validateManifest, decodePack, WATER_METHODS, SIGNALS} from "../assets/js/fluvial-science.js";
import {COPY, normalizeView} from "../assets/js/fluvial-lab.js";

const config = JSON.parse(fs.readFileSync("data/fluvial/config.json", "utf8"));
const manifest = JSON.parse(fs.readFileSync("data/fluvial/manifest.json", "utf8"));
assert.equal(validateManifest(manifest, config), manifest);
assert.equal(manifest.benchmark.winner, null);
assert.equal(manifest.regions.length, 4);
assert.equal(manifest.regions[0].scenes.length, 3);
assert.deepEqual(Object.keys(COPY.es).sort(), Object.keys(COPY.en).sort());
for (const match of fs.readFileSync("rivers.html", "utf8").matchAll(/data-lab-text="([^"]+)"/g)) {
  assert.ok(COPY.es[match[1]] && COPY.en[match[1]], `Missing bilingual text: ${match[1]}`);
}
for (const signal of SIGNALS) assert.ok(COPY.es[signal + "Copy"] && COPY.en[signal + "Copy"]);
assert.equal(ratio(0, 0), NaN); assert.equal(ratio(-.1, .2), NaN); assert.equal(ratio(.3, .1), .49999999999999994);
const pack = {width: 1, height: 1, values: Float32Array.from([.1, .2, .15, .1, .05, .025, 1])};
const values = valuesAt(pack, 0);
assert.ok(Math.abs(values.aweinsh - (4 * (.2 - .05) - .25 * .1 - 2.75 * .025)) < 1e-6);
assert.ok(Math.abs(values.aweish - (.1 + 2.5 * .2 - 1.5 * (.1 + .05) - .25 * .025)) < 1e-6);
assert.ok(Math.abs(values.ndti - ((.15 - .2) / (.15 + .2))) < 1e-6);
assert.equal(waterVotes(values, config.thresholds), 4);
assert.equal(valuesAt(pack, -1), null); assert.equal(valuesAt(pack, 1), null);
assert.equal(valuesAt({...pack, values: Float32Array.from([.1, .2, .15, .1, .05, .025, 0])}, 0), null);
assert.equal(transition(-1, 4), 0); assert.equal(transition(4, 0), 3); assert.equal(transition(0, 4), 4); assert.equal(transition(3, 0), 5);
const grid = {width: 10, height: 10, web_extent: [0, 0, 100, 100]};
assert.equal(pixelIndex({x: 0, y: 100}, grid), 0); assert.equal(pixelIndex({x: 50, y: 50}, grid), 55);
assert.equal(pixelIndex({x: 100, y: 50}, grid), null); assert.equal(pixelIndex({x: 50, y: 0}, grid), null);
const view = normalizeView(new URLSearchParams("region=unknown&mode=wrong&from=2024-08-08&to=2024-08-08&ndwi=Infinity&mndwi=&split=nope"));
assert.equal(view.region, "tena"); assert.equal(view.mode, "rgb"); assert.equal(view.later, "2026-07-29"); assert.equal(view.thresholds.ndwi, 0); assert.equal(view.thresholds.mndwi, 0); assert.equal(view.split, 50);
for (const mutate of [m => m.status = "validated", m => m.benchmark.winner = "mndwi", m => m.regions[0].scenes[0].url = "../other.gz",
  m => m.regions[0].scenes[0].date = "2026-01-01", m => m.regions[0].scenes[0].radiometry[0].offset = NaN,
  m => m.regions[0].width = 9999999, m => m.regions[0].scenes[0].decoded_bytes += 4]) {
  const invalid = structuredClone(manifest); mutate(invalid); assert.throws(() => validateManifest(invalid, config));
}
// Verify every real numerical public pack, not colourized previews.
let bytesTotal = 0;
for (const region of manifest.regions) {
  const masks = [];
  for (const row of region.scenes) {
    const bytes = fs.readFileSync(row.url);
    assert.equal(crypto.createHash("sha256").update(bytes).digest("hex"), row.sha256);
    const input = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
    const decoded = await decodePack(input, row, region); const n = region.width * region.height;
    assert.equal(decoded.values.length, n * 7); bytesTotal += bytes.length;
    assert.equal(crypto.createHash("sha256").update(fs.readFileSync(row.stac_file)).digest("hex"), row.stac_sha256);
    const stac = JSON.parse(fs.readFileSync(row.stac_file, "utf8")); assert.equal(stac.id, row.id); assert.equal(stac.collection, row.collection);
    const mask = decoded.values.slice(n * 6); masks.push(mask);
    assert.equal(mask.reduce((a, b) => a + b, 0), row.web_usable_pixels);
    for (const pixel of [0, Math.floor(n / 2), n - 1]) {
      const v = valuesAt(decoded, pixel);
      if (mask[pixel] === 1) { assert.ok(v); for (const method of WATER_METHODS) assert.ok(Number.isFinite(v[method])); }
      else assert.equal(v, null);
    }
  }
  assert.equal(masks[0].reduce((sum, x, i) => sum + Number(x === 1 && masks[1][i] === 1 && masks[2][i] === 1), 0), region.web_common_pixels);
}
// Corruption, over-expansion and inconsistent quality must fail closed.
const region = {width: 1, height: 1};
const encoded = zlib.gzipSync(Buffer.from(pack.values.buffer));
const row = {size_bytes: encoded.length, decoded_bytes: 28, sha256: crypto.createHash("sha256").update(encoded).digest("hex")};
const asArray = buffer => buffer.buffer.slice(buffer.byteOffset, buffer.byteOffset + buffer.byteLength);
assert.equal((await decodePack(asArray(encoded), row, region)).values[6], 1);
await assert.rejects(() => decodePack(asArray(encoded), {...row, sha256: "a".repeat(64)}, region));
await assert.rejects(() => decodePack(asArray(encoded), {...row, decoded_bytes: 24}, region));
const bad = zlib.gzipSync(Buffer.from(Float32Array.from([.1, .2, .15, .1, .05, .025, 0]).buffer));
await assert.rejects(() => decodePack(asArray(bad), {...row, size_bytes: bad.length, sha256: crypto.createHash("sha256").update(bad).digest("hex")}, region));
console.log(`Fluvial bilingual UI, pinned scenes, numerical integrity, formulas and NoData passed (${bytesTotal} bytes).`);
