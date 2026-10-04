import assert from "node:assert/strict";

import {
  ATLAS_SYSTEMS,
  contentBelongsToSystem,
  normalizeAtlasSystem,
  selectedSystems,
  contentBelongsToSelection,
  createSystemScope,
} from "../assets/js/map/systems.js";
import { catalogForSystem } from "../assets/js/map/source-catalog.js";

assert.deepEqual(ATLAS_SYSTEMS, ["earth", "water", "sky", "life", "risk"]);
assert.equal(normalizeAtlasSystem("water"), "water");
assert.equal(normalizeAtlasSystem("unknown"), "earth");
assert.equal(contentBelongsToSystem("water sky", "sky"), true);
assert.equal(contentBelongsToSystem("water risk", "life"), false);
assert.deepEqual(selectedSystems("water", ["water", "earth", "invalid"]), ["water", "earth"]);
assert.equal(contentBelongsToSelection("earth", "water"), false);
assert.equal(contentBelongsToSelection("earth", "water", ["earth"]), true);
const controls = ["earth", "water sky", "life"].map(owners => ({
  checked: true, listeners: [],
  closest: () => ({dataset: {systemContent: owners}}),
  addEventListener(_name, fn) { this.listeners.push(fn); },
}));
const scope = createSystemScope(controls, control => control.listeners.forEach(fn => fn()));
scope("water"); assert.deepEqual(controls.map(c => c.checked), [false, true, false]);
scope("sky"); assert.deepEqual(controls.map(c => c.checked), [false, true, false]);
scope("earth"); assert.deepEqual(controls.map(c => c.checked), [true, false, false]);
scope("earth", ["life"], false); assert.equal(controls[2].checked, false); // combining exposes controls, not layers
controls[2].checked = true; controls[2].listeners.forEach(fn => fn());
scope("earth", ["life"], false); assert.equal(controls[2].checked, true);
scope("risk"); assert.deepEqual(controls.map(c => c.checked), [false, false, false]);
assert.deepEqual(
  catalogForSystem("es", "risk").map((source) => source.id),
  ["inamhi-services", "nasa-viirs-flood"],
);

console.log("Atlas system navigation tests passed.");
