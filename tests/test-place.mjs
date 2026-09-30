import assert from "node:assert/strict";

import { distanceToGeometryKm, haversineKm, nearestFeature } from "../assets/js/map/place.js";
import { SOURCE_CATALOG } from "../assets/js/map/source-catalog.js";
import { activeSpatialContexts, normalizeRegionFocus, REGION_VIEWS, SPATIAL_CONTEXTS } from "../assets/js/map/spatial-context.js";

assert.ok(Math.abs(haversineKm([-78, 0], [-78, 1]) - 111.2) < 0.5);
assert.ok(distanceToGeometryKm([-78, 0], {
  type: "LineString",
  coordinates: [[-79, 0], [-77, 0]],
}) < 0.001);

const near = { type: "Feature", geometry: { type: "Point", coordinates: [-78, 0.1] } };
const far = { type: "Feature", geometry: { type: "Point", coordinates: [-75, 0] } };
assert.equal(nearestFeature([-78, 0], [far, near]).feature, near);
assert.ok(SOURCE_CATALOG.some((source) => source.id === "inamhi-services"));
assert.ok(SOURCE_CATALOG.every((source) => source.url.startsWith("https://")));
assert.equal(new Set(SOURCE_CATALOG.map(source => source.id)).size, SOURCE_CATALOG.length);
assert.equal(SOURCE_CATALOG.find(source => source.id === "mapbiomas-ecuador")?.status, "connected");
for (const id of ["chc-chirps3", "copernicus-era5-land", "copernicus-dem", "jrc-surface-water"]) {
  assert.equal(SOURCE_CATALOG.find(source => source.id === id)?.status, "candidate");
}
assert.equal(normalizeRegionFocus("napo"), "napo");
for (const invalid of [undefined, "__proto__", "toString", "Napo", "quito"]) assert.equal(normalizeRegionFocus(invalid), "ecuador");
assert.equal(REGION_VIEWS.napo.bounds.length, 2);
assert.deepEqual(activeSpatialContexts({}, "es"), []);
assert.deepEqual(activeSpatialContexts({ precipitation: false, flood: true, unknown: true }, "en").map(x => x.id), ["flood"]);
assert.match(activeSpatialContexts({ "air-temperature": true }, "es")[0].resolution, /111 km/);
assert.match(activeSpatialContexts({ faults: true }, "en", { demo: true })[0].resolution, /Synthetic/);
assert.match(activeSpatialContexts({ evidence: true }, "es", { demo: true })[0].limit, /no observación/);
for (const language of ["es", "en"]) {
  const all = activeSpatialContexts(Object.fromEntries(SPATIAL_CONTEXTS.map(x => [x.id, true])), language);
  assert.equal(all.length, 11);
  assert.ok(all.every(x => x.name && x.resolution && x.limit));
}

console.log("Place explainer and source catalog tests passed.");
