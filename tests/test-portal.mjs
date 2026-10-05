import assert from 'node:assert/strict';
import fs from 'node:fs';
import {filterRecords, safeHref, recordLinks} from '../assets/js/portal-catalog.js';
const datasets=JSON.parse(fs.readFileSync('data/catalog/datasets.json')).records;
const studies=JSON.parse(fs.readFileSync('data/library/studies.json')).records;
for(const records of [datasets,studies]) {
  assert.equal(new Set(records.map(r=>r.id)).size,records.length);
  for(const r of records) {
    assert.ok(r.topics.length && r.territories.includes('ecuador'),r.id);
    for(const href of [...recordLinks(r),r.image].filter(Boolean)) {
      assert.ok(safeHref(href),href);
      if(!href.startsWith('https://')) {
        const [file]=href.split(/[?#]/); assert.ok(fs.existsSync(file),href);
        if(href.includes('#')&&file.endsWith('.html')) assert.ok(fs.readFileSync(file,'utf8').includes('id="'+href.split('#')[1]+'"'),href);
      }
    }
  }
}
for(const r of datasets) for(const id of r.related??[]) assert.ok(studies.some(s=>s.id===id),id);
for(const r of studies) for(const id of r.related??[]) assert.ok(datasets.some(d=>d.id===id),id);
assert.ok(filterRecords(datasets,{query:'rios',territory:'napo'}).length);
assert.equal(filterRecords(datasets,{query:'absentrecord999'}).length,0);
for(const unsafe of ['javascript:alert(1)','//evil.test','../private','https://x:y@example.com','data:text/html,hi']) assert.equal(safeHref(unsafe),null);
for(const file of ['index.html','explore.html','learn.html','lecturas.html','rocks.html','rivers.html','datos.html','biblioteca.html','andes-pulso.html','geologia.html','laboratorio.html','georreferenciar.html','modelos.html']) {
  const html=fs.readFileSync(file,'utf8');
  const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
  assert.equal(new Set(ids).size,ids.length,file);
  for(const m of html.matchAll(/(?:href|src|poster)="([^"]+)"/g)) {
    const href=m[1].replaceAll('&amp;','&');
    if(/^(https?:|data:|mailto:)/.test(href)) continue;
    const [local]=href.split(/[?#]/);
    if(local) assert.ok(fs.existsSync(local),file+' -> '+local);
    else if(href.startsWith('#')) assert.ok(ids.includes(href.slice(1)),file+' -> '+href);
  }
}
console.log('Portal: resources, relationships, search and safe URLs passed.');
