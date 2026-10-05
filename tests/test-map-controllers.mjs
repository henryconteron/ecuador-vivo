import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

import { createEarthquakePanel } from "../assets/js/map/earthquake-panel.js";
import { createWmsLayerController } from "../assets/js/map/wms-layer.js";

function fakeLayer() {
  const handlers = new Map();
  return {
    on(event, handler) {
      handlers.set(event, handler);
      return this;
    },
    emit(event) {
      handlers.get(event)?.();
    },
    addTo(map) {
      map.layers.add(this);
      return this;
    },
  };
}

const map = {
  layers: new Set(),
  hasLayer(layer) {
    return this.layers.has(layer);
  },
  removeLayer(layer) {
    this.layers.delete(layer);
  },
};
const layer = fakeLayer();
const statusEl = { dataset: {}, textContent: "" };
const controller = createWmsLayerController(map, layer, {
  statusEl,
  dateEl: { value: "2026-10-05" },
  i18nPrefix: "precipitation",
  t: (key) => key,
  template: (key, values) => `${key}:${values.date}`,
});

controller.updateStatus();
assert.equal(statusEl.dataset.state, "off");
controller.activate();
assert.equal(statusEl.dataset.state, "loading");
layer.emit("load");
assert.equal(statusEl.dataset.state, "loaded");
layer.emit("tileerror");
layer.emit("tileerror");
assert.equal(statusEl.dataset.state, "error");
controller.deactivate();
layer.emit("tileerror");
layer.emit("tileerror");
assert.equal(statusEl.dataset.state, "off", "late errors must not revive an inactive layer");

const earthquakeElements = {
  earthquakeDays: { value: "7" },
  earthquakeMinimumMagnitude: { value: "4" },
  earthquakeDepthFilter: { value: "all" },
  earthquakeStatus: { dataset: {}, textContent: "" },
};
const earthquakePanel = createEarthquakePanel(
  {},
  {},
  earthquakeElements,
  {
    t: (key) => key,
    template: (key) => key,
    formatNumber: String,
    formatUtcDate: String,
    updateLegendVisibility() {},
    updateSourceCount() {},
    getSelectedPoint: () => null,
    renderPlaceExplanation() {},
  },
);
earthquakePanel.updateStatus();
assert.equal(earthquakeElements.earthquakeStatus.dataset.state, "loading");
assert.equal(earthquakeElements.earthquakeStatus.textContent, "earthquakes.loading");
assert.equal(earthquakePanel.hasData(), false);

const mapSource = await readFile(new URL("../assets/js/map.js", import.meta.url), "utf8");
assert.doesNotMatch(mapSource, /\bupdate(?:Precipitation|AirTemperature|CloudFraction|Flood|Thermal)Status\s*\(/);
assert.match(mapSource, /earthquakePanel\.updateStatus\(\)/);

console.log("Map controller tests passed.");
