import test from 'node:test';
import assert from 'node:assert/strict';
import {ObservationCache} from './src/observation-cache.ts';

test('repeated observations reuse a bounded display resource, never a scientific result', async () => {
 let calls=0; const cache=new ObservationCache({entries:3,bytes:30,ttl:30000});
 const load=async()=>({value:++calls,bytes:10,dispose(){}});
 assert.equal((await cache.get('date-and-source-a',load)).value,1);
 assert.equal((await cache.get('date-and-source-a',load)).value,1);
 assert.equal((await cache.get('date-and-source-b',load)).value,2);
 assert.equal(calls,2);cache.clear();
});
test('concurrent requests coalesce and failure does not poison subsequent requests',async()=>{
 const cache=new ObservationCache();let calls=0;
 const load=async()=>{calls++;return {value:7,bytes:1,dispose(){}}};
 await Promise.all([cache.get('x',load),cache.get('x',load)]);assert.equal(calls,1);
 await assert.rejects(cache.get('bad',async()=>{throw Error('bad date')}));
 assert.equal((await cache.get('bad',load)).value,7);cache.clear();
});
test('LRU eviction, byte limits and expiry release owned resources',async()=>{
 let now=0;const disposed=[];const cache=new ObservationCache({entries:2,bytes:20,ttl:10,now:()=>now});
 const load=k=>async()=>({value:k,bytes:10,dispose(){disposed.push(k)}});
 await cache.get('a',load('a'));await cache.get('b',load('b'));await cache.get('a',load('a'));
 await cache.get('c',load('c'));assert.deepEqual(disposed,['b']);assert.equal(cache.size,2);
 now=11;await cache.get('a',load('a'));assert.ok(disposed.includes('a'));
 cache.clear();assert.equal(cache.size,0);
});
test('clear during a pending load cannot admit stale data',async()=>{
 const cache=new ObservationCache();let done;let released=0;
 const pending=cache.get('old',()=>new Promise(resolve=>{done=resolve}));
 await Promise.resolve();cache.clear();done({value:'old',bytes:1,dispose(){released++}});
 await assert.rejects(pending,/cambió/);assert.equal(released,1);assert.equal(cache.size,0);
});
test('oversized resources are refused and released',async()=>{
 const cache=new ObservationCache({bytes:10});let released=0;
 await assert.rejects(cache.get('big',async()=>({value:1,bytes:11,dispose(){released++}})),/memoria/);
 assert.equal(released,1);assert.equal(cache.size,0);
});
