// Deterministic interaction tests, not a browser/visual acceptance substitute.
import {readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
import test from 'node:test';
const source=await readFile(new URL('./workspace_windows.js',import.meta.url),'utf8');
const {studioWindowRect,studioWindowState,createStudioWindows}=await import('data:text/javascript;base64,'+Buffer.from(source+'\nexport {studioWindowRect,studioWindowState,createStudioWindows};').toString('base64'));

test('new editor and old column preferences start with a clear video and compact montage',()=>{
 for(const old of [{},{left:true,right:true,collapsed:false}]){
  const state=studioWindowState(old);
  assert.equal(state.left,false);assert.equal(state.right,false);assert.equal(state.collapsed,true);
 }
 const saved=studioWindowState({windowVersion:1,left:true,right:false,collapsed:false,windowRects:{left:{x:11}}});
 assert.equal(saved.left,true);assert.equal(saved.collapsed,false);assert.equal(saved.windowRects.left.x,11);
});
test('windows remain within the editor after tiny screens, resizing and invalid saved positions',()=>{
 for(const bounds of [{width:1200,height:700},{width:360,height:400},{width:180,height:120}]){
  for(const saved of [null,{x:-500,y:9999,width:9999,height:9999},{x:NaN,y:Infinity,width:-1,height:0}]){
   const rect=studioWindowRect(saved,bounds,'right');
   for(const value of Object.values(rect))assert.ok(Number.isFinite(value));
   assert.ok(rect.x>=0&&rect.y>=0&&rect.width>0&&rect.height>0);
   assert.ok(rect.x+rect.width<=bounds.width&&rect.y+rect.height<=bounds.height);
  }
 }
});

class Element {
 constructor(){this.hidden=false;this.style={};this.dataset={};this.attrs={};this.handlers={};this.classes=new Set();this.classList={toggle:(name,on)=>on?this.classes.add(name):this.classes.delete(name)};this.clientWidth=1200;this.clientHeight=700;}
 setAttribute(k,v){this.attrs[k]=String(v)}
 addEventListener(k,fn){(this.handlers[k]??=[]).push(fn)}
 removeEventListener(k,fn){this.handlers[k]=this.handlers[k]?.filter(x=>x!==fn)}
 fire(k,values={}){for(const fn of this.handlers[k]||[])fn({target:this,button:0,pointerId:1,preventDefault(){},...values})}
 focus(){this.focused=true}setPointerCapture(){}releasePointerCapture(){}
 closest(){return null}
}
function fixture(width=1200){
 const host=new Element();host.clientWidth=width;
 const ids=Object.fromEntries(['toggle-left','toggle-right','close-left','close-right','focus-mode','focus-exit','timeline-collapse'].map(x=>[x,new Element()]));
 const panels={left:new Element(),right:new Element()};
 for(const panel of Object.values(panels)){
  panel.heading=new Element();panel.resize=new Element();
  panel.querySelector=s=>s==='[data-window-drag]'?panel.heading:panel.resize;
 }
 const root={querySelector:s=>s==='.evs'?host:s==='.workspace'?host:s.startsWith('#')?ids[s.slice(1)]:panels[s.includes('left')?'left':'right']};
 const ui=studioWindowState({});let saves=0;
 const windows=createStudioWindows({root,ui,save:()=>saves++});
 return {ui,windows,host,ids,panels,saves:()=>saves};
}
test('open/close, focus mode and montage only change local presentation',()=>{
 const f=fixture();assert.equal(f.panels.left.hidden,true);
 f.windows.open('left');assert.equal(f.panels.left.hidden,false);assert.equal(f.ids['toggle-left'].attrs['aria-expanded'],'true');
 f.windows.focus(true);assert.equal(f.panels.left.hidden,true);assert.ok(f.host.classes.has('focus-video'));
 f.windows.focus(false);assert.equal(f.panels.left.hidden,false);
 f.windows.close('left');assert.equal(f.panels.left.hidden,true);assert.equal(f.ids['toggle-left'].focused,true);
 f.ids['timeline-collapse'].fire('click');assert.equal(f.ui.collapsed,false);assert.ok(f.saves()>0);
 f.windows.dispose();
});
test('small editor opens one window at a time and disposal removes input handlers',()=>{
 const f=fixture(380);f.windows.open('left');f.windows.open('right');
 assert.equal(f.panels.left.hidden,true);assert.equal(f.panels.right.hidden,false);
 f.windows.dispose();const before=f.saves();f.ids['toggle-left'].fire('click');assert.equal(f.saves(),before);
});
test('pointer and keyboard move/resize persist rectangles without leaving the workspace',()=>{
 const f=fixture();f.windows.open('left');const before={...f.ui.windowRects.left};
 f.panels.left.heading.fire('pointerdown',{clientX:20,clientY:30});
 f.panels.left.heading.fire('pointermove',{clientX:90,clientY:80});
 f.panels.left.heading.fire('pointerup');assert.equal(f.ui.windowRects.left.x,before.x+70);
 f.panels.left.heading.fire('keydown',{key:'ArrowRight',shiftKey:true});assert.equal(f.ui.windowRects.left.x,before.x+80);
 const width=f.ui.windowRects.left.width;
 f.panels.left.resize.closest=()=>f.panels.left.resize;
 f.panels.left.resize.fire('pointerdown',{clientX:0,clientY:0});
 f.panels.left.resize.fire('pointermove',{clientX:20,clientY:10});
 f.panels.left.resize.fire('pointerup');assert.equal(f.ui.windowRects.left.width,width+20);
 f.panels.left.resize.fire('keydown',{key:'ArrowRight'});assert.equal(f.ui.windowRects.left.width,width+21);
 f.host.clientWidth=360;f.windows.sync();
 assert.ok(f.ui.windowRects.left.x+f.ui.windowRects.left.width<=360);
 f.windows.dispose();
});
