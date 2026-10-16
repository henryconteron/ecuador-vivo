import assert from 'node:assert/strict';
import test from 'node:test';
import {DeferredView} from './src/deferred-view.ts';

function clock(){
 let next=0;const jobs=new Map();
 return {schedule:fn=>{jobs.set(++next,fn);return next},cancel:id=>jobs.delete(id),
  tick:()=>{const pending=[...jobs.values()];jobs.clear();pending.forEach(fn=>fn())},get count(){return jobs.size}};
}
test('a burst keeps only its final camera and schedules one durable request',()=>{
 const c=clock(),saved=[];const view=new DeferredView(box=>{saved.push(box);return true},400,c.schedule,c.cancel);
 for(let i=0;i<8;i++)view.update([i,0,i+1,1]);
 assert.equal(saved.length,0);assert.equal(c.count,1);assert.equal(view.pending,true);
 c.tick();assert.deepEqual(saved,[[7,0,8,1]]);assert.equal(view.pending,false);
});
test('backpressure retains the latest camera until acknowledgement; UI can force a flush',()=>{
 const c=clock(),saved=[];let blocked=true;
 const view=new DeferredView((box,force)=>{if(blocked&&!force)return false;saved.push({box,force});return true},400,c.schedule,c.cancel);
 view.update([0,0,1,1]);c.tick();assert.equal(view.pending,true);assert.equal(saved.length,0);
 view.update([1,0,2,1]);blocked=false;view.flush();assert.deepEqual(saved[0].box,[1,0,2,1]);
 blocked=true;view.update([2,0,3,1]);view.flush(true);assert.equal(saved[1].force,true);assert.equal(c.count,0);
});
test('cancel, duplicate cameras and disposal do not cause delayed writes',()=>{
 const c=clock(),saved=[];const view=new DeferredView(box=>{saved.push(box);return true},400,c.schedule,c.cancel);
 const box=[0,0,1,1];view.update(box);box[0]=99;c.tick();assert.deepEqual(saved[0],[0,0,1,1]);
 view.update([0,0,1,1]);c.tick();assert.equal(saved.length,1);
 view.update([1,0,2,1]);view.cancel();c.tick();assert.equal(view.pending,false);assert.equal(saved.length,1);
 view.update([2,0,3,1]);view.dispose();c.tick();assert.equal(saved.length,1);
});
test('an unrelated hydrate cannot end the debounce and undo permits saving a former view again',()=>{
 const c=clock(),saved=[];const view=new DeferredView(box=>{saved.push(box);return true},400,c.schedule,c.cancel);
 view.update([0,0,1,1]);assert.equal(view.ready,false);view.reconcile([2,0,3,1]);c.tick();
 view.reconcile([2,0,3,1]);view.update([0,0,1,1]);c.tick();assert.equal(saved.length,2);
});
test('browser timer functions are never invoked with the DeferredView as their receiver',()=>{
 let job;const schedule=function(fn){assert.equal(this,undefined);job=fn;return 1};
 const cancel=function(){assert.equal(this,undefined)};
 const view=new DeferredView(()=>true,400,schedule,cancel);
 view.update([0,0,1,1]);view.update([1,0,2,1]);job();assert.equal(view.pending,false);
});
