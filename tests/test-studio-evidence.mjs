import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {assetPath, validateEvidence, publicSourceURL} from '../assets/js/studio-evidence.js';
const id='studio-'+'a'.repeat(24);
assert.equal(assetPath(id,'maps/0001-continent.png'),`data/cases/studio/${id}/maps/0001-continent.png`);
for(const bad of ['../video.mp4','maps/../../private.png','https://elsewhere/a.png','maps/a.svg'])assert.throws(()=>assetPath(id,bad));
assert.throws(()=>assetPath('../escape','video.mp4'));
assert.equal(publicSourceURL('https://example.org/data'),'https://example.org/data');
for(const bad of ['javascript:alert(1)','http://example.org','https://user:pass@example.org','https://example.org?token=x'])assert.equal(publicSourceURL(bad),null);
const c={schema:'ecuador-vivo-evidence-v1',id,status:'reviewed',title:'T',variable:'Temperatura',units:'°C',
 observation_dates:['2024-09-01'],maps:[{date:'2024-09-01',channels:{continent:'maps/0000-continent.png'}}],
 files:{'maps/0000-continent.png':{sha256:'b'.repeat(64),bytes:100},'video.mp4':{sha256:'c'.repeat(64),bytes:100}},
 results:[],metrics_status:'not_calculated',sources:[],limitations:[],video:'video.mp4'};
assert.equal(validateEvidence(c,id),c);
assert.throws(()=>validateEvidence({...c,id:'different'},id));
assert.throws(()=>validateEvidence({...c,status:'draft'},id));
assert.throws(()=>validateEvidence({...c,observation_dates:['2024-09-02']},id));
assert.throws(()=>validateEvidence({...c,metrics_status:'linked_results'},id));
assert.throws(()=>validateEvidence({...c,maps:[{date:'2024-09-01',channels:{continent:'../private.png'}}]},id));
const html=readFileSync(new URL('../andes-pulso.html',import.meta.url),'utf8');
const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
assert.equal(ids.length,new Set(ids).size);
for(const control of ['studio-story','studio-date','studio-metric-list','studio-source-list','studio-limit-list','studio-map-pane','studio-video'])assert.ok(ids.includes(control),control);
assert.match(html,/<script src="assets\/js\/studio-evidence\.js" type="module">/);
assert.ok(!html.includes('autoplay'));
console.log('Studio evidence: confined assets, source links, dates and metric status verified.');
