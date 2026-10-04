import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {validateLocalGeoJSON} from '../assets/js/map/local-data.js';
const manifest=JSON.parse(fs.readFileSync('data/geology/manifest.json'));
assert.deepEqual(manifest.bbox,[-78.1,-1.2,-77.6,-.7]);
assert.equal(manifest.status,'source-snapshot-not-independently-validated');
assert.match(manifest.map_scale,/not established/);
for(const row of manifest.files){
  const bytes=fs.readFileSync(row.path);
  assert.equal(bytes.length,row.bytes);
  assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),row.sha256);
  const fc=validateLocalGeoJSON(JSON.parse(bytes));
  assert.equal(fc.features.length,row.count);
  assert.equal(new Set(fc.features.map(f=>f.properties.OBJECTID)).size,row.count);
}
const sheets=JSON.parse(fs.readFileSync('data/geology/tena-sheets.geojson'));
assert.equal(sheets.features.find(f=>f.properties.NOMBRE==='TENA').properties.ESTADO,'En revisión');
const good={type:'FeatureCollection',features:[{type:'Feature',geometry:{type:'Point',coordinates:[-77.8,-1]},properties:{name:'<img src=x onerror=alert(1)>'}}]};
assert.equal(validateLocalGeoJSON(good),good); // text is preserved, never interpreted as HTML
for(const mutate of [v=>v.crs={},v=>v.features=[],v=>v.features[0].geometry.coordinates=[500000,9800000],v=>v.features[0].geometry.coordinates=[NaN,1],v=>v.features[0].geometry.type='GeometryCollection',v=>v.features[0].geometry={type:'Polygon',coordinates:[[[0,0],[1,1],[2,1],[3,2]]]}]){
  const value=structuredClone(good);mutate(value);assert.throws(()=>validateLocalGeoJSON(value));
}
const source=fs.readFileSync('assets/js/map/local-data.js','utf8');
assert.ok(!source.includes('innerHTML'));
assert.ok(!/\bfetch\s*\(/.test(source),'local file must not be transmitted');
assert.ok(source.includes('input.size > 10 * 1024 * 1024'));
console.log('Geology: IIGE snapshots, provenance, sheet status and local-file safety passed.');
