import assert from "node:assert/strict";
import fs from "node:fs";

const markup = fs.readFileSync("learn.html", "utf8");
const learnScript = fs.readFileSync("assets/js/learn.js", "utf8");

for (const story of ["earth", "water", "sky"]) {
  assert.match(markup, new RegExp(`id="choice-${story}"[^>]*role="tab"[^>]*aria-controls="story-${story}"`), `Missing accessible story choice: ${story}`);
  assert.match(markup, new RegExp(`id="story-${story}"[^>]*role="tabpanel"[^>]*aria-labelledby="choice-${story}"[^>]*data-story-panel="${story}"`), `Missing story panel: ${story}`);
  const tourLink = [...markup.matchAll(/<a\b[^>]*data-story-map[^>]*>/g)].some((match) =>
    match[0].includes(`href="./?system=${story}&amp;tour=${story}"`));
  assert.ok(tourLink, `Missing guided atlas link: ${story}`);
}

const allIds = [...markup.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1]);
assert.equal(new Set(allIds).size, allIds.length, "Story sections must have unique IDs");
for (const match of markup.matchAll(/href="#([^"]+)"/g)) {
  assert.ok(allIds.includes(match[1]), `Missing in-page destination: #${match[1]}`);
}

assert.equal((markup.match(/data-learning-check/g) ?? []).length, 2, "Water and Sky each need an exercise");
assert.equal((markup.match(/data-check-choice=/g) ?? []).length, 6, "Each new exercise needs three choices");
assert.equal((markup.match(/data-check-feedback role="status"/g) ?? []).length, 2, "Exercise feedback must be announced accessibly");
assert.match(markup, /data-lab-answer="unknown"/, "Field lab must allow insufficient evidence");
const labMarkup = markup.slice(markup.indexOf('id="laboratorio"'), markup.indexOf('class="earth-map-mission'));
assert.ok(!labMarkup.includes("<svg"), "Field lab must use attributed scientific figures, not generic vector scenes");
for (const match of learnScript.matchAll(/image: "(papers\/[^"]+)"/g)) {
  assert.ok(fs.existsSync(`assets/images/education/${match[1]}`), `Missing lab figure: ${match[1]}`);
}
for (const match of markup.matchAll(/<a\b[^>]*target="_blank"[^>]*>/g)) {
  assert.match(match[0], /rel="[^"]*noopener[^"]*"/, "External links must include noopener");
}
const assetPaths = new Set();

for (const match of markup.matchAll(/(?:src|href)="(assets\/[^"?]+)(?:\?[^\"]*)?"/g)) {
  assetPaths.add(match[1]);
}

for (const match of markup.matchAll(/srcset="([^"]+)"/g)) {
  for (const candidate of match[1].split(",")) {
    const source = candidate.trim().split(/\s+/)[0];
    if (source.startsWith("assets/")) assetPaths.add(source);
  }
}

for (const assetPath of assetPaths) {
  assert.ok(fs.existsSync(assetPath), `Missing local resource referenced by learn.html: ${assetPath}`);
}

const images = [...markup.matchAll(/<img\b[^>]*>/g)].map((match) => match[0]);
assert.ok(images.length > 0, "learn.html should contain educational images");
for (const image of images) {
  assert.match(image, /\balt="[^"]*"/, `Image is missing alternative text: ${image}`);
}

const bibliographyIds = new Set(
  [...markup.matchAll(/\bid="(ref-[^"]+)"/g)].map((match) => match[1]),
);
const citedIds = [...markup.matchAll(/href="#(ref-[^"]+)"/g)].map((match) => match[1]);
assert.ok(citedIds.length >= 5, "The educational story should visibly connect figures and claims to references");
for (const citedId of citedIds) {
  assert.ok(bibliographyIds.has(citedId), `Citation target #${citedId} is missing from the bibliography`);
}

for (const chapter of ["observar", "fundamentos", "sismo", "paleosismologia", "caso-ecuador", "laboratorio"]) {
  assert.match(markup, new RegExp(`data-story-section="${chapter}"`), `Missing story chapter: ${chapter}`);
  assert.match(markup, new RegExp(`data-story-link="${chapter}"`), `Missing story navigation link: ${chapter}`);
}

console.log(`Learn content tests passed for ${assetPaths.size} local resources and ${citedIds.length} citations.`);
