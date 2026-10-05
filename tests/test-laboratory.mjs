import assert from 'node:assert/strict';
import './test-georeference-audit.mjs';
import './test-prototypes.mjs';
import fs from 'node:fs';
import {laboratoryURL, PRESETS} from '../assets/js/laboratory.js';
import {selectGeology, exportSelection, loadGeology} from '../assets/js/geology-catalog.js';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
for(const preset of Object.keys(PRESETS)){
  const url=new URL(laboratoryURL(preset,'en'));
  assert.equal(url.origin,'https://web.geolibre.app');assert.equal(url.searchParams.get('lang'),'en');
  for(const data of url.searchParams.getAll('data'))assert.match(data,/^https:\/\/raw\.githubusercontent\.com\/henryconteron\/ecuador-vivo\/[a-f0-9]{40}\/data\//);
}
assert.throws(()=>laboratoryURL('__proto__'));assert.throws(()=>laboratoryURL('https://private.example'));
assert.equal(new URL(laboratoryURL('empty')).searchParams.has('data'),false);
const units=read('data/geology/tena-units.geojson').features,sheets=read('data/geology/tena-sheets.geojson').features;
assert.equal(selectGeology(sheets,{query:'poalo'}).length,1);
assert.equal(selectGeology(sheets,{status:'En revisión'}).length,1);
const subset=selectGeology(units,{unit:'Formación Napo'});assert.ok(subset.length>0 && subset.length<units.length);
const manifest=read('data/geology/manifest.json'), exported=exportSelection(subset,'units',manifest,{unit:'Formación Napo'});
assert.equal(exported.metadata.source,manifest.source);assert.deepEqual(exported.features,subset);
assert.equal(selectGeology(units,{query:'no-match-xyz'}).length,0);
const fetcher=async path=>{const bytes=fs.readFileSync(path);return {ok:true,json:async()=>JSON.parse(bytes),arrayBuffer:async()=>bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength)};};
assert.equal((await loadGeology(fetcher)).collections['tena-units'].features.length,56);
await assert.rejects(loadGeology(async path=>path.endsWith('.geojson')?{ok:true,arrayBuffer:async()=>new Uint8Array([1]).buffer}:fetcher(path)));
const lab=fs.readFileSync('laboratorio.html','utf8');assert.ok(!lab.includes('<iframe'),'external service is opt-in, not eagerly embedded');
assert.ok(!lab.includes('drive.google.com/drive/folders/'),'no private folder IDs in public HTML');
const labScript=fs.readFileSync('assets/js/laboratory.js','utf8');assert.match(labScript,/lab-stop'\)\.disabled=!active/,'close action must reflect the inactive state');
console.log('Laboratory: pinned public sources, opt-in embed, geology filters, exports and integrity passed.');
