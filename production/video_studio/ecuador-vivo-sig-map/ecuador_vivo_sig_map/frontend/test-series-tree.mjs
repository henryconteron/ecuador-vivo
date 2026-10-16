import test from 'node:test';
import assert from 'node:assert/strict';
import {seriesTree} from './src/series-tree-model.ts';
test('temporal observations form one logical layer without losing dates or other layers',()=>{
 const layers=[{id:'ref',visible:true},{id:'a',variable:'Temperatura',date:'2026-09-01',visible:true},{id:'b',variable:'Temperatura',date:'2026-09-03',visible:false}];
 const before=JSON.stringify(layers),model=seriesTree(layers,{layers:['a','b'],index:1});
 assert.equal(model.name,'Temperatura');assert.equal(model.count,2);assert.equal(model.logicalCount,2);
 assert.equal(model.current.id,'b');assert.equal(model.mixed,true);assert.equal(model.visible,false);
 assert.deepEqual(model.observations.map(l=>l.date),['2026-09-01','2026-09-03']);assert.deepEqual(model.others,[layers[0]]);
 assert.equal(JSON.stringify(layers),before);
});
test('missing calendar entries never invent observations and absent series keeps normal layers',()=>{
 const layers=[{id:'a',visible:true}];
 assert.equal(seriesTree(layers).logicalCount,1);assert.equal(seriesTree(layers).count,0);
 const model=seriesTree(layers,{layers:['missing','a'],index:0});
 assert.equal(model.count,1);assert.equal(model.current.id,'a');assert.equal(model.logicalCount,1);
});
