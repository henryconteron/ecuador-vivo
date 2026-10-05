import assert from "node:assert/strict";

import {
  filterFaultCatalog,
  hasCatalogFilters,
  sortFaultCatalog,
} from "../assets/js/map/fault-catalog.js";
import { movementOf } from "../assets/js/map/symbology.js";
import { normalize } from "../assets/js/map/utils.js";

const features = [
  {
    properties: {
      nombre: "Falla Quito",
      nombre_en: "Quito fault",
      provincia: "Pichincha",
      tipo_movimiento: "inversa",
      catalog_id: "EC-01",
    },
  },
  {
    properties: {
      nombre: "Sistema Pallatanga",
      provincia: "Chimborazo",
      tipo_movimiento: "dextral",
      fuente: "GEM GAF-DB",
    },
  },
];

const dependencies = { normalize, movementOf };

assert.equal(filterFaultCatalog(features, {}, dependencies).length, 2);
assert.deepEqual(
  filterFaultCatalog(features, { query: "pichincha" }, dependencies),
  [features[0]],
);
assert.deepEqual(
  filterFaultCatalog(features, { query: "quito fault" }, dependencies),
  [features[0]],
  "English names must remain searchable from the Spanish interface",
);
assert.deepEqual(
  filterFaultCatalog(features, { query: "gem", movement: "dextral" }, dependencies),
  [features[1]],
);
assert.equal(filterFaultCatalog(features, { movement: "normal" }, dependencies).length, 0);

assert.equal(hasCatalogFilters(), false);
assert.equal(hasCatalogFilters({ query: "  " }), false);
assert.equal(hasCatalogFilters({ movement: "dextral" }), true);

const sorted = sortFaultCatalog(features, {
  localizedProperty: (feature, property) => feature.properties[property],
  locale: "es",
});
assert.deepEqual(sorted, [features[0], features[1]]);
assert.deepEqual(features[0].properties.nombre, "Falla Quito", "sorting must not mutate the input");

console.log("Fault catalog tests passed.");
