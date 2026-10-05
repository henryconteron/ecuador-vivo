import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {loadSlab2,slabNode,slabSegments,SLAB_SHA256} from '../assets/js/slab2.js';
const bytes=fs.readFileSync('data/slab2/ecuador.json');
const manifest=JSON.parse(fs.readFileSync('data/slab2/manifest.json','utf8'));
assert.equal(createHash('sha256').update(bytes).digest('hex'),SLAB_SHA256);
assert.equal(manifest.output.sha256,SLAB_SHA256);assert.equal(manifest.output.bytes,bytes.length);
const grid=await loadSlab2(async()=>({ok:true,arrayBuffer:async()=>bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.length)}));
assert.equal(grid.latitude.length,161);assert.equal(grid.longitude.length,171);
assert.equal(grid.latitude[0],-5.5);assert.equal(grid.latitude.at(-1),2.5);
assert.equal(grid.longitude[0],-83);assert.equal(grid.longitude.at(-1),-74.5);
for(const axis of [grid.latitude,grid.longitude])for(let i=1;i<axis.length;i++)assert.ok(Math.abs(axis[i]-axis[i-1]-.05)<1e-9);
let count=0,holes=0;
for(let r=0;r<161;r++){assert.equal(grid.depth_km[r].length,171);assert.equal(grid.uncertainty_km[r].length,171);for(let c=0;c<171;c++){
  const p=slabNode(grid,r,c);if(!p){holes++;continue;}count++;assert.ok(p.depth>0&&p.depth<700);assert.ok(p.uncertainty===null||p.uncertainty>=0);
}}
assert.equal(count,21849);assert.ok(holes>0);assert.equal(manifest.finite_depth_nodes,count);
const segments=slabSegments(grid);assert.ok(segments.length>1000);
for(const [a,b] of segments)assert.ok(Math.abs(Math.abs(a.longitude-b.longitude)+Math.abs(a.latitude-b.latitude)-.05)<1e-9,'connect native adjacent nodes only');
const gaps={latitude:[0],longitude:[0,1,2],depth_km:[[10,null,30]],uncertainty_km:[[2,null,3]]};
assert.deepEqual(slabSegments(gaps,1),[]);assert.equal(slabNode(gaps,0,1),null);assert.equal(slabNode(gaps,1,0),null);
assert.throws(()=>slabSegments(grid,0));
await assert.rejects(loadSlab2(async()=>({ok:false})));
await assert.rejects(loadSlab2(async()=>({ok:true,arrayBuffer:async()=>new Uint8Array([1]).buffer})));
const viewer=fs.readFileSync('assets/js/subduction-viewer.js','utf8');assert.ok(!viewer.includes('conceptualDepth'));
console.log('Slab2: pinned integrity, 21849 native nodes, depth sign, missing data, uncertainty and no gap bridging passed.');
