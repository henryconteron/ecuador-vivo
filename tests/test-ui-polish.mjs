import assert from "node:assert/strict";
import fs from "node:fs";

const atlasCss = fs.readFileSync("assets/css/styles.css", "utf8");
const portalCss = fs.readFileSync("assets/css/portal.css", "utf8");
const portalBridgeCss = fs.readFileSync("assets/css/portal-bridge.css", "utf8");
const laboratoryCss = fs.readFileSync("assets/css/laboratory.css", "utf8");
const laboratoryJs = fs.readFileSync("assets/js/laboratory.js", "utf8");
const exploreHtml = fs.readFileSync("explore.html", "utf8");

assert.match(exploreHtml, /family=DM\+Sans[^"']*Newsreader/);
assert.match(atlasCss, /"DM Sans"/);
assert.match(atlasCss, /"Newsreader"/);
assert.match(atlasCss, /\.switch-track/);
assert.match(atlasCss, /scrollbar-width:\s*thin/);
assert.match(atlasCss, /@media \(hover: hover\) and \(pointer: fine\)/);
assert.match(atlasCss, /@media \(prefers-reduced-motion: reduce\)/);
assert.doesNotMatch(atlasCss, /transition:\s*all\b/);
assert.doesNotMatch(portalCss, /transition:\s*all\b/);
assert.match(portalBridgeCss, /\.topbar \.main-nav::-webkit-scrollbar\{display:none\}/);

assert.match(laboratoryJs, /classList\.toggle\('lab-idle',!active\)/);
assert.match(laboratoryJs, /el\('lab-stop'\)\.disabled=!active/);
assert.match(laboratoryCss, /prefers-reduced-motion:reduce/);

console.log("UI polish: typography, motion, scrollbars and laboratory onboarding passed.");
