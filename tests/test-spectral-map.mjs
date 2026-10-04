import assert from "node:assert/strict";
import fs from "node:fs";
import {mountNapoSpectralMap, normalizeSpectralView, screenClip, validateSpectralExplorer} from "../assets/js/map/spectral-map.js";
const read = path => JSON.parse(fs.readFileSync(path, "utf8"));
const parent = read("data/spectral/napo-manifest.json"), settings = read("data/spectral/napo-explorer-config.json");
const extra = read("data/spectral/napo-explorer-manifest.json");
assert.equal(validateSpectralExplorer(extra, settings, parent), extra);
for (const mutate of [
  d => {d.parent_input_sha256 = "a".repeat(64);}, d => {d.parent_receipt_sha256 = "b".repeat(64);},
  d => {d.width += 1;}, d => {d.display_bounds[0][0] += 0.01;}, d => {d.resampling = "bilinear";},
  d => {d.config.ndmi_formula = "wrong";}, d => {d.common_pixels += 1;}, d => {d.ndmi_common_pixels = 0;},
  d => {d.ndmi_common_pixels = d.common_pixels + 1;}, d => {d.images.reverse();},
  d => {d.images[0].url = "https://untrusted.example/image.png";}, d => {d.images[4].year = 2024;},
  d => {d.images[1].sha256 = "none";},
]) {const invalid = structuredClone(extra); mutate(invalid); assert.throws(() => validateSpectralExplorer(invalid, settings, parent));}
const normalized = normalizeSpectralView(new URLSearchParams("view=spectral&signal=change&year=1800&split=500&compare=1"));
assert.deepEqual(normalized, {enabled: true, mode: "change", year: 2024, compare: false, position: 100, river: false});
assert.equal(normalizeSpectralView(new URLSearchParams("signal=unknown&split=no")).position, 50);
assert.equal(normalizeSpectralView(new URLSearchParams("signal=unknown")).mode, "rgb");
assert.equal(screenClip({left: 0, width: 100}, {left: 0, width: 100}, 50, "later"), "inset(0 0 0 50%)");
assert.equal(screenClip({left: -50, width: 200}, {left: 0, width: 100}, 50, "earlier"), "inset(0 50% 0 0)");
assert.equal(screenClip({left: -100, width: 100}, {left: 0, width: 100}, 50, "earlier"), "inset(0 0% 0 0)");
assert.equal(screenClip({left: 100, width: 100}, {left: 0, width: 100}, 50, "later"), "inset(0 0 0 0%)");

// Test-only DOM/Leaflet doubles: lifecycle, stale loads and failures, not scientific observations.
const markup = fs.readFileSync("explore.html", "utf8");
class Element {
  constructor() {this.style = {}; this.dataset = {}; this.handlers = {}; this.attributes = {}; this.checked = false; this.value = "";}
  addEventListener(name, callback) {this.handlers[name] = callback;}
  setAttribute(name, value) {this.attributes[name] = value;}
  async fire(name) {this.handlers[name]?.(); await new Promise(resolve => setImmediate(resolve));}
}
const nodes = new Map([...markup.matchAll(/id="(spectral-map-[^"]+)"/g)].map(match => [match[1], new Element()]));
nodes.get("spectral-map-opacity").value = "100";
const years = [2019, 2024].map(year => Object.assign(new Element(), {dataset: {spectralMapYear: String(year)}}));
const areas = ["window", "river"].map(area => Object.assign(new Element(), {dataset: {spectralMapArea: area}}));
globalThis.document = {getElementById: id => nodes.get(id), querySelectorAll: selector => selector.includes("year") ? years : areas};
let href = "http://localhost/?system=water&view=spectral&signal=rgb&compare=1&area=jatunyacu";
const windowHandlers = {};
globalThis.window = {location: {get href() {return href;}, get search() {return new URL(href).search;}},
  history: {replaceState: (_state, _title, url) => {href = url.href;}},
  addEventListener: (name, callback) => {windowHandlers[name] = callback;}, matchMedia: () => ({matches: false})};
globalThis.fetch = async path => ({ok: true, json: async () => read(path)});
let pendingLoads = [], deferImages = false, failImages = false;
globalThis.Image = class {
  naturalWidth = parent.width; naturalHeight = parent.height;
  set src(value) {this.url = value; const complete = () => failImages ? this.onerror() : this.onload();
    if (deferImages) pendingLoads.push(complete); else queueMicrotask(complete);}
  get src() {return this.url;}
};
const layers = new Set(), events = {}, element = {getBoundingClientRect: () => ({left: 0, width: 100}), scrollIntoView() {}};
const map = {createPane() {}, getPane: () => ({style: {}}), getContainer: () => element,
  removeLayer: layer => {layers.delete(layer);}, hasLayer: layer => layers.has(layer),
  getBounds: () => ({intersects: () => true}), getZoom: () => 13, fitBounds() {},
  on: (names, callback) => {for (const name of names.split(" ")) (events[name] ??= []).push(callback);}};
let overlayFailure = false;
const makeLayer = () => {
  const handlers = {}, image = {style: {}, getBoundingClientRect: () => ({left: 0, width: 100})};
  return {on: (event, callback) => {handlers[event] = callback;}, getElement: () => image,
    setOpacity(value) {this.opacity = value;}, addTo() {layers.add(this); queueMicrotask(() => handlers[overlayFailure ? "error" : "load"]?.()); return this;}};
};
const L = {imageOverlay: makeLayer, rectangle: makeLayer};
let controller, changes = 0;
controller = mountNapoSpectralMap({L, map, t: key => key, language: () => "es", onChange: () => {changes++;}, focus() {}});
await new Promise(resolve => setImmediate(resolve));
assert.equal(controller.isActive(), true);
assert.equal(layers.size, 3); // two years and an extent outline
assert.equal(nodes.get("spectral-map-toolbar").hidden, false);
assert.equal(nodes.get("spectral-map-divider").hidden, false);
nodes.get("spectral-map-split").value = "100"; await nodes.get("spectral-map-split").fire("input");
assert.equal([...layers][0].getElement().style.clipPath, "inset(0 0% 0 0)");
assert.equal([...layers][1].getElement().style.clipPath, "inset(0 0 0 100%)");
assert.equal(new URL(href).searchParams.get("split"), "100");
nodes.get("spectral-map-time").value = "2019"; await nodes.get("spectral-map-time").fire("change");
assert.equal(layers.size, 2); assert.equal(nodes.get("spectral-map-divider").hidden, true);
assert.equal(nodes.get("spectral-map-title").textContent, "spectral.rgb · 2019");
nodes.get("spectral-map-time").value = "compare"; await nodes.get("spectral-map-time").fire("change");
assert.equal(layers.size, 3); assert.equal(nodes.get("spectral-map-compare").checked, true);
nodes.get("spectral-map-mode").value = "change"; await nodes.get("spectral-map-mode").fire("change");
assert.equal(controller.isActive(), true); assert.equal(layers.size, 2);
assert.equal(nodes.get("spectral-map-divider").hidden, true);
assert.equal(nodes.get("spectral-map-compare").disabled, true);
assert.equal(nodes.get("spectral-map-time").disabled, true);
assert.ok(years.every(year => year.disabled));
nodes.get("spectral-map-opacity").value = "45"; await nodes.get("spectral-map-opacity").fire("input");
assert.equal([...layers][0].opacity, 0.45);
deferImages = true;
nodes.get("spectral-map-mode").value = "ndmi"; await nodes.get("spectral-map-mode").fire("change");
assert.equal(controller.isActive(), false); assert.equal(layers.size, 0);
await nodes.get("spectral-map-hide").fire("click");
for (const complete of pendingLoads) complete(); pendingLoads = [];
await new Promise(resolve => setImmediate(resolve));
assert.equal(layers.size, 0); assert.equal(nodes.get("spectral-map-toolbar").hidden, true);
deferImages = false; failImages = true;
nodes.get("spectral-map-toggle").checked = true; await nodes.get("spectral-map-toggle").fire("change");
assert.equal(layers.size, 0); assert.equal(nodes.get("spectral-map-toggle").checked, false);
assert.equal(nodes.get("spectral-map-status").textContent, "spectralMap.error");
failImages = false; overlayFailure = true;
controller.activate(); await new Promise(resolve => setImmediate(resolve));
assert.equal(controller.isActive(), false); assert.equal(layers.size, 0);
overlayFailure = false; controller.activate(); await new Promise(resolve => setImmediate(resolve));
assert.equal(controller.isActive(), true);
await nodes.get("spectral-map-hide").fire("click");
assert.equal(new URL(href).searchParams.has("view"), false);
assert.equal(controller.isActive(), false); assert.ok(changes > 5);
assert.ok(markup.includes('data-legend-layer="spectral-map"'));
console.log("Spectral map: provenance, screen-space clipping, years, failures, stale loads and hide lifecycle passed.");
