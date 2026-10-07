import assert from "node:assert/strict";
import {validCustomSource} from "../assets/js/map/custom-sources.js";
const source = {id: "local-geology", type: "geojson", system: "earth", url: "data/geology/tena-units.geojson", title_es: "Geología", title_en: "Geology", citation: "IIGE · escala declarada"};
assert.equal(validCustomSource(source), true);
assert.equal(validCustomSource({...source, type: "wms", url: "https://example.org/wms", layers: "units"}), true);
assert.equal(validCustomSource({...source, type: "xyz", url: "https://example.org/{z}/{x}/{y}.png"}), true);
for (const invalid of [{url: "javascript:alert(1)"}, {url: "//example.org/data"}, {url: "data/../private.json"}, {system: "other"}, {id: "<script>"}, {type: "wms"}, {citation: ""}]) {
  assert.equal(validCustomSource({...source, ...invalid}), false);
}
console.log("Owner-managed map sources: types, scope, citations and safe URLs passed.");
