import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const document = {
  body: { dataset: { page: "map" } },
  documentElement: { lang: "es" },
  querySelector: () => null,
  querySelectorAll: () => [],
  title: "",
};

const storage = new Map();
const window = { dispatchEvent: () => {} };
const context = vm.createContext({
  CustomEvent: class CustomEvent {},
  document,
  localStorage: {
    getItem: (key) => storage.get(key) ?? null,
    setItem: (key, value) => storage.set(key, value),
  },
  window,
});

vm.runInContext(fs.readFileSync("assets/js/i18n.js", "utf8"), context);

const markup = ["index.html", "learn.html"]
  .map((file) => fs.readFileSync(file, "utf8"))
  .join("\n");
const runtimeSource = ["assets/js/learn.js", "assets/js/map.js", "assets/js/map/landcover.js", "assets/js/map/imagery.js", "assets/js/map/spectral.js", "assets/js/map/spectral-map.js", "assets/js/map/rivers.js"]
  .map((file) => fs.readFileSync(file, "utf8"))
  .join("\n");
const keys = [
  ...new Set([
    "popup.referenceScope",
    "popup.referenceScope.individual",
    "popup.referenceScope.catalogOnly",
    "map.collapse", "spectralMap.compactScope", "spectralMap.compactOutside", "spectralMap.compactZoom",
    ...["loading", "pending", "ready", "visible", "error"].map(state => `rivers.${state}`),
    ...["loading", "pending", "error", "ready", "imageLoading", "visible", "imageError"].map(state => `landcover.${state}`),
    ...["loading", "pending", "error", "ready", "imageLoading", "imageReady", "imageError"].map(state => `imagery.${state}`),
    ...["loading", "pending", "error", "ready", "imageLoading", "imageReady", "imageError", "riverScope", "windowScope"].map(state => `spectral.${state}`),
    ...["rgb", "ndvi", "mndwi"].flatMap(mode => ["Copy", "Alt"].map(field => `spectral.${mode}${field}`)),
    ...["rgb", "ndvi", "mndwi", "ndmi", "quality", "change"].flatMap(mode => [`spectral.${mode}`, `spectral.${mode}Copy`]),
    ...["loading", "visible", "error", "off"].map(state => `spectralMap.${state}`),
    ...[...markup.matchAll(/data-i18n(?:-[a-z-]+)?="([^"]+)"/g)].map(
      (match) => match[1],
    ),
    ...[...runtimeSource.matchAll(/\bt\("([^"]+)"\)/g)].map(
      (match) => match[1],
    ),
    ...["earth", "water", "sky", "life", "risk"].flatMap((system) =>
      ["Eyebrow", "Title", "Copy", "Layers", "Note"].map(
        (field) => `systems.${system}${field}`,
      ),
    ),
    ...["off", "loading", "loaded", "error"].map((state) => `basins.${state}`),
    ...["placeLabel", "placeLoading", "placeUnavailable", "placeOutside", "placeDetail"].map(
      (field) => `basins.${field}`,
    ),
    ...["ready", "visible", "altitude", "transmitting", "placeLabel"].map(
      (field) => `stations.${field}`,
    ),
    ...["off", "loading", "loaded", "error", "placeLabel", "placeActive", "placeDetail"].map(
      (field) => `airTemperature.${field}`,
    ),
    ...["off", "loading", "loaded", "error", "placeLabel", "placeActive", "placeDetail"].map(
      (field) => `cloudFraction.${field}`,
    ),
    ...["normal", "reverse", "strike"].flatMap((scenario) =>
      ["kicker", "question", "clue", "imageAlt", "explanation"].map(
        (field) => `lab.scenario.${scenario}.${field}`,
      ),
    ),
  ]),
];

for (const language of ["es", "en"]) {
  window.atlasI18n.setLanguage(language);
  for (const key of keys) {
    assert.notEqual(
      window.atlasI18n.t(key),
      key,
      `Missing ${language} translation for ${key}`,
    );
  }
}

console.log(`i18n tests passed for ${keys.length} markup keys.`);
