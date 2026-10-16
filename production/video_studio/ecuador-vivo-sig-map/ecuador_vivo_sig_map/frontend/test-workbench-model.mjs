import assert from 'node:assert/strict';
import test from 'node:test';
import {panelSizes, TASKS, visibleTask, resizeByKey, eventStatus} from './src/workbench-model.ts';
test('desktop panes respect their bounds and reserve useful map space',()=>{
 const large=panelSizes(1440,{left:999,right:999,dock:999});
 assert.equal(large.left,400);assert.equal(large.right,420);assert.equal(large.dock,300);
 const compact=panelSizes(800,{left:400,right:420,dock:160});
 assert.ok(800-compact.left-compact.right-12>=260);
 assert.ok(compact.left>=180);assert.ok(compact.right>=240);
});
test('small hosts use overlay panes rather than squeezing the map',()=>{
 const result=panelSizes(340,{left:270,right:310,dock:160});
 assert.equal(result.overlay,true);assert.ok(result.left<=340);assert.ok(result.right<=340);
});
test('a hidden panel gives its width back to the map and the remaining panel',()=>{
 const result=panelSizes(800,{left:400,right:420,dock:160},{left:true});
 assert.equal(result.right,420);assert.ok(800-result.right-6>=260);
});
test('invalid geometry cannot become CSS NaN or infinite layout',()=>{
 for(const width of [NaN,Infinity,-1])assert.throws(()=>panelSizes(width,{left:270,right:310,dock:160}));
 assert.throws(()=>panelSizes(1200,{left:NaN,right:310,dock:160}));
});
test('task choice affects only visible commands and keeps a safe default',()=>{
 assert.deepEqual(TASKS,['map','data','analysis','time','output']);
 assert.equal(visibleTask('not-a-tool'),'map');assert.equal(visibleTask('time'),'time');
});
test('divider keyboard direction follows the visible panel, with bounded endpoints',()=>{
 assert.equal(resizeByKey('left','ArrowRight',260),264);
 assert.equal(resizeByKey('right','ArrowLeft',300),304);
 assert.equal(resizeByKey('dock','ArrowUp',160,true),176);
 assert.equal(resizeByKey('right','Home',300),240);assert.equal(resizeByKey('right','End',300),420);
 assert.equal(resizeByKey('left','ArrowLeft',180),180);
 assert.equal(resizeByKey('dock','Tab',160),undefined);
});
test('routine tool changes do not leave a false opening spinner',()=>{
 assert.equal(eventStatus('tool','14:05:00'),'Guardado · 14:05:00');
 assert.equal(eventStatus('navigate','14:05:00'),'Abriendo…');
 assert.equal(eventStatus('series_palette','14:05:00'),'Guardando…');
});
