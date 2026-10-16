import assert from 'node:assert/strict';
import test from 'node:test';
import {rebuildLayer,rasterImageKey} from './src/layer-refresh.ts';
test('a palette change reuses all thirty layer objects but refreshes their images',()=>{
 const before=Array.from({length:30},(_,id)=>({id,type:'raster',representation_revision:'old',image:'old-'+id,bbox:[-80,-5,-75,2],presentation:{resampling:'bilinear'}}));
 const after=before.map(r=>({...r,representation_revision:'new',image:'new-'+r.id}));
 assert.equal(after.filter((r,i)=>rebuildLayer(before[i],r)).length,0);
 assert.ok(after.every((r,i)=>rasterImageKey(r)!==rasterImageKey(before[i])));
});
test('source kind and vector geometry revisions rebuild; raster extent/resampling only refresh the source',()=>{
 const raster={type:'raster',representation_revision:'a',image:'same',bbox:[0,0,1,1],presentation:{resampling:'nearest'}};
 assert.equal(rebuildLayer(undefined,raster),true);
 assert.equal(rebuildLayer(raster,{...raster,type:'vector'}),true);
 assert.equal(rebuildLayer({type:'vector',representation_revision:'a'},{type:'vector',representation_revision:'b'}),true);
 for(const next of [{...raster,bbox:[0,0,2,2]},{...raster,presentation:{resampling:'bilinear'}}]){
  assert.equal(rebuildLayer(raster,next),false);assert.notEqual(rasterImageKey(raster),rasterImageKey(next));
 }
 assert.equal(rasterImageKey(raster),rasterImageKey(structuredClone(raster)));
});
