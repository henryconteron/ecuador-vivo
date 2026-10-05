import assert from "node:assert/strict";

import { createStationPanel, createStationPopup } from "../assets/js/map/station-panel.js";

function createDocumentStub() {
  return {
    createElement(tagName) {
      return {
        tagName,
        children: [],
        textContent: "",
        append(...children) {
          this.children.push(...children);
        },
      };
    },
  };
}

const popup = createStationPopup(
  {
    properties: {
      categoria: "HIDROLOGICA",
      codigo: "H001",
      nombre: "Río de prueba",
      altitud_m: 510,
      canton: "Tena",
      provincia: "Napo",
    },
  },
  {
    t: (key) => key,
    template: (key, values) => `${key}:${values.altitude}`,
    formatNumber: String,
    documentObject: createDocumentStub(),
  },
);
assert.equal(popup.className, "station-popup");
assert.equal(popup.children[0].textContent, "stations.hydrological");
assert.equal(popup.children[1].textContent, "H001");
assert.equal(popup.children.at(-1).rel, "noopener noreferrer");

function createHarness(loadSnapshot) {
  const layers = new Set();
  const callbacks = { legend: 0, sources: 0, place: 0 };
  const map = {
    layers,
    attributionControl: {
      values: [],
      addAttribution(value) {
        this.values.push(value);
      },
    },
    hasLayer(layer) {
      return layers.has(layer);
    },
    removeLayer(layer) {
      layers.delete(layer);
    },
  };
  const layer = {
    features: [],
    addTo(targetMap) {
      targetMap.layers.add(this);
      return this;
    },
    clearLayers() {
      this.features = [];
    },
    addData(collection) {
      this.features = collection.features;
    },
  };
  const elements = {
    stationStatus: { dataset: {}, textContent: "" },
    stationRetrievedAt: { dateTime: "", textContent: "" },
    stationCategory: { value: "all", disabled: true },
    stationToggle: { checked: false, disabled: true },
  };
  const panel = createStationPanel(map, layer, elements, {
    t: (key) => key,
    template: (key, values) => `${key}:${Object.values(values).join("/")}`,
    formatUtcDate: (value) => `date:${value}`,
    loadSnapshot,
    updateLegendVisibility: () => { callbacks.legend += 1; },
    updateSourceCount: () => { callbacks.sources += 1; },
    getSelectedPoint: () => null,
    renderPlaceExplanation: () => { callbacks.place += 1; },
  });
  return { callbacks, elements, layer, map, panel };
}

const features = [
  { properties: { categoria: "METEOROLOGICA" } },
  { properties: { categoria: "HIDROLOGICA" } },
];
const success = createHarness(async () => ({
  features,
  metadata: { retrievedAt: "2026-10-05T12:00:00Z" },
}));

await success.panel.load();
assert.equal(success.panel.state, "loaded");
assert.equal(success.elements.stationToggle.disabled, false);
assert.equal(success.panel.visibleCatalog.length, 2);
assert.equal(success.elements.stationRetrievedAt.dateTime, "2026-10-05T12:00:00Z");
assert.equal(success.map.attributionControl.values.length, 1);

success.elements.stationCategory.value = "hydrological";
success.panel.render();
assert.equal(success.panel.visibleCatalog.length, 1);
assert.equal(success.layer.features.length, 1);

success.panel.setActive(true);
assert.equal(success.map.hasLayer(success.layer), true);
assert.equal(success.elements.stationCategory.disabled, false);
assert.equal(success.elements.stationStatus.dataset.state, "loaded");
success.panel.setActive(false);
assert.equal(success.map.hasLayer(success.layer), false);
assert.equal(success.elements.stationCategory.disabled, true);

const failure = createHarness(async () => {
  throw new Error("offline");
});
const originalConsoleError = console.error;
console.error = () => {};
try {
  await failure.panel.load();
} finally {
  console.error = originalConsoleError;
}
assert.equal(failure.panel.state, "error");
assert.equal(failure.elements.stationToggle.disabled, true);
assert.equal(failure.elements.stationToggle.checked, false);
assert.equal(failure.layer.features.length, 0);

console.log("Station panel tests passed.");
