import assert from 'node:assert/strict';
import test from 'node:test';
import {floatingPosition,temporalWindow} from './src/workbench-model.ts';

test('floating windows stay reachable inside their actual host',()=>{
 assert.deepEqual(floatingPosition({x:-40,y:900}, {width:1000,height:600}, {width:320,height:260}),{x:0,y:340});
 assert.deepEqual(floatingPosition({x:900,y:400}, {width:320,height:220}, {width:500,height:300}),{x:0,y:0});
});
test('invalid floating coordinates cannot propagate to CSS',()=>{
 assert.throws(()=>floatingPosition({x:NaN,y:1},{width:100,height:100},{width:50,height:50}));
});
test('timeline zoom retains actual observation indices, not invented dates',()=>{
 assert.deepEqual(temporalWindow(30,12,8),{start:8,end:15});
 assert.deepEqual(temporalWindow(30,29,8),{start:22,end:29});
 assert.deepEqual(temporalWindow(30,0,8),{start:0,end:7});
 assert.deepEqual(temporalWindow(30,12,100),{start:0,end:29});
});
test('empty, single and malformed temporal ranges are safe',()=>{
 assert.deepEqual(temporalWindow(0,0,8),{start:0,end:0});
 assert.deepEqual(temporalWindow(1,0,8),{start:0,end:0});
 assert.deepEqual(temporalWindow(2,1,8),{start:0,end:1});
 assert.throws(()=>temporalWindow(30,NaN,8));
});
