// Controller unit tests with tiny in-memory nodes, not a browser or visual QA.
import assert from 'node:assert/strict';
import test from 'node:test';
import {readFile} from 'node:fs/promises';
import ts from 'typescript';
const source=await readFile(new URL('./src/floating-panels.ts',import.meta.url),'utf8');
const js=ts.transpileModule(source,{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ESNext}}).outputText.replace("'./workbench-model'",JSON.stringify(new URL('./src/workbench-model.ts',import.meta.url).href));
const {FloatingPanels}=await import('data:text/javascript;base64,'+Buffer.from(js).toString('base64'));
let active;
class Node{
 hidden=false;style={};attributes={};classes=new Set();handler;
 constructor(width=320,height=300){this.clientWidth=width;this.clientHeight=height}
 get offsetWidth(){return Number.parseFloat(this.style.width)||this.clientWidth}
 get offsetHeight(){return Number.parseFloat(this.style.height)||this.clientHeight}
 get offsetLeft(){return Number.parseFloat(this.style.left)||0}
 get offsetTop(){return Number.parseFloat(this.style.top)||0}
 classList={contains:key=>this.classes.has(key),remove:key=>this.classes.delete(key),toggle:key=>{this.classes.has(key)?this.classes.delete(key):this.classes.add(key);return this.classes.has(key)}};
 setAttribute(key,value){this.attributes[key]=value}
 removeAttribute(key){if(key==='style')this.style={}}
 querySelector(){return this.handler}
 focus(){active=this}
 setPointerCapture(){}
 click(){this.onclick?.()}
}
function fixture(){
 let observer;
 globalThis.ResizeObserver=class{constructor(callback){this.callback=callback;observer=this}observe(){}disconnect(){this.disconnected=true}};
 globalThis.requestAnimationFrame=()=>1;globalThis.cancelAnimationFrame=()=>{};
 const pairs=[['layers','sig-layers-window','sig-layers-view'],['reference','sig-reference-window','sig-reference-view'],['properties','sig-properties-window','sig-properties-view'],['table','sig-table-window','sig-attributes-view'],['toolbox','sig-toolbox-window','sig-toolbox-view']];
 const nodes=new Map([['.sig-shell-body',new Node(1000,600)],['#sig-geographic-map',new Node()]]);
 for(const [name,id,trigger] of pairs){const panel=new Node(name==='table'?820:320,300);panel.hidden=true;panel.handler=new Node();nodes.set('#'+id,panel);nodes.set('#'+trigger,new Node())}
 for(const id of ['sig-toggle-layers','sig-toggle-inspector','sig-reference-close','sig-toggle-dock','sig-show-panels','sig-table-maximize','sig-toolbox-close'])nodes.set('#'+id,new Node());
 const root={querySelector:selector=>nodes.get(selector)},windows=new FloatingPanels(root);
 return {nodes,windows,q:id=>nodes.get('#'+id),observer};
}
test('toolbar toggles windows locally and close restores focus',()=>{
 const {q,windows}=fixture();q('sig-layers-view').click();assert.equal(q('sig-layers-window').hidden,false);assert.equal(q('sig-layers-view').attributes['aria-expanded'],'true');
 assert.equal(active,q('sig-layers-window').handler);q('sig-toggle-layers').click();assert.equal(q('sig-layers-window').hidden,true);assert.equal(active,q('sig-layers-view'));windows.dispose();
});
test('keyboard and dragging clamp windows inside the map, cancelling ends drag',()=>{
 const {q,windows}=fixture();windows.open('properties');const panel=q('sig-properties-window'),title=panel.handler;
 const event={button:0,clientX:0,clientY:0,pointerId:1,preventDefault(){},stopPropagation(){}};
 title.onpointerdown(event);title.onpointermove({...event,clientX:1000,clientY:1000});assert.equal(panel.offsetLeft,680);assert.equal(panel.offsetTop,300);
 title.onpointercancel();title.onpointermove({...event,clientX:0,clientY:0});assert.equal(panel.offsetLeft,680);
 title.onkeydown({key:'ArrowLeft',preventDefault(){}});assert.equal(panel.offsetLeft,672);windows.dispose();
});
test('Escape dismisses only its window; reset and dispose release local state',()=>{
 const {q,windows,observer}=fixture();windows.open('layers');windows.open('table');q('sig-table-window').onkeydown({key:'Escape',stopPropagation(){}});
 assert.equal(q('sig-table-window').hidden,true);assert.equal(q('sig-layers-window').hidden,false);windows.reset();assert.equal(q('sig-layers-window').hidden,true);windows.dispose();assert.equal(observer.disconnected,true);
});
test('table can expand and restore without changing the other windows',()=>{
 const {q,windows}=fixture();windows.open('table');q('sig-table-maximize').click();assert.equal(q('sig-table-window').classList.contains('sig-window-maximized'),true);assert.equal(q('sig-table-maximize').attributes['aria-pressed'],'true');q('sig-table-maximize').click();assert.equal(q('sig-table-window').classList.contains('sig-window-maximized'),false);windows.dispose();
});
test('processing window opens at the right and Escape restores its trigger focus',()=>{
 const {q,windows}=fixture();q('sig-toolbox-view').click();assert.equal(q('sig-toolbox-window').hidden,false);assert.equal(q('sig-toolbox-window').offsetLeft,664);
 q('sig-toolbox-window').onkeydown({key:'Escape',stopPropagation(){}});assert.equal(q('sig-toolbox-window').hidden,true);assert.equal(active,q('sig-toolbox-view'));windows.dispose();
});
