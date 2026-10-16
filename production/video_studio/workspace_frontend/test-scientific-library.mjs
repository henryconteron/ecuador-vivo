import test from 'node:test';import assert from 'node:assert/strict';import {readFile} from 'node:fs/promises';
const source=await readFile(new URL('./resource_workspace.js',import.meta.url),'utf8');
const {scientificSearch}=await import('data:text/javascript;base64,'+Buffer.from(source+'\nexport {scientificSearch}').toString('base64'));
const items=[{id:'a',name:'Células',category:'Biología'},{id:'b',name:'Temperatura',category:'Clima'}];
test('science search handles accents, themes and favorites without changing its data',()=>{
 assert.equal(scientificSearch(items,'celulas')[0].id,'a');assert.equal(scientificSearch(items,'','Clima')[0].id,'b');
 assert.equal(scientificSearch(items,'','Todos',['a'])[0].id,'a');assert.equal(scientificSearch(items,'unknown').length,0);assert.equal(items.length,2);
});
