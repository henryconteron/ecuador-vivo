import assert from 'node:assert/strict';
import test from 'node:test';
import {ExtentHistory, searchCommands, measureGeometry, commandFocusIndex} from './src/map-interactions-model.ts';
import LineString from 'ol/geom/LineString.js';
import Polygon from 'ol/geom/Polygon.js';

test('view history restores copies and discards the forward branch on new navigation',()=>{
 const h=new ExtentHistory(4);h.record([-82,-6,-75,2]);h.record([-81,-5,-76,1]);h.record([-80,-4,-77,0]);
 const previous=h.back();assert.deepEqual(previous,[-81,-5,-76,1]);previous[0]=9;
 assert.deepEqual(h.forward(),[-80,-4,-77,0]);h.back();h.record([-79,-3,-78,-1]);
 assert.equal(h.canForward,false);assert.deepEqual(h.back(),[-81,-5,-76,1]);
});
test('duplicate views do not crowd bounded history; invalid views cannot enter it',()=>{
 const h=new ExtentHistory(3);h.record([0,0,1,1]);h.record([0,0,1,1]);assert.equal(h.canBack,false);
 for(let i=1;i<6;i++)h.record([i,0,i+1,1]);
 assert.deepEqual(h.back(),[4,0,5,1]);assert.deepEqual(h.back(),[3,0,4,1]);assert.equal(h.back(),undefined);
 assert.throws(()=>h.record([NaN,0,1,1]));assert.throws(()=>h.record([1,0,0,1]));
 h.clear();assert.equal(h.canBack,false);assert.equal(h.canForward,false);
});
test('search normalizes Spanish accents and requires every query term',()=>{
 const commands=[{id:'a',label:'Análisis vectorial',group:'Análisis',keywords:'buffer disolver'},
 {id:'b',label:'Tabla de atributos',group:'Datos',keywords:'entidades'}];
 assert.equal(searchCommands(commands,'analisis buffer')[0].id,'a');
 assert.equal(searchCommands(commands,'TABLA')[0].id,'b');
 assert.deepEqual(searchCommands(commands,'vectorial tabla'),[]);assert.equal(searchCommands(commands,'').length,2);
});
test('command keyboard starts at the correct end and wraps in both directions',()=>{
 assert.equal(commandFocusIndex(-1,4,'ArrowDown'),0);
 assert.equal(commandFocusIndex(-1,4,'ArrowUp'),3);
 assert.equal(commandFocusIndex(3,4,'ArrowDown'),0);
 assert.equal(commandFocusIndex(0,4,'ArrowUp'),3);
 assert.equal(commandFocusIndex(-1,1,'ArrowUp'),0);
 assert.equal(commandFocusIndex(-1,0,'ArrowDown'),-1);
});
test('measurement uses geographic spherical metres, not raw degrees',()=>{
 const length=measureGeometry(new LineString([[0,0],[1,0]]));
 assert.equal(length.kind,'length');assert.ok(Math.abs(length.value-111195)<2);assert.equal(length.unit,'m');
 const area=measureGeometry(new Polygon([[[0,0],[1,0],[1,1],[0,1],[0,0]]]));
 assert.equal(area.kind,'area');assert.ok(Math.abs(area.value/1e6-12363.7)<2);assert.equal(area.unit,'m²');
});
