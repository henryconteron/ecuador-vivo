import assert from 'node:assert/strict';
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {faultMotion,waterBudget,infiltrationTokens,airParcel} from '../assets/js/learning-science.js';
import {lessons} from '../assets/js/learning-lessons.js';
for(const progress of [0,.1,.5,1]){
  const normal=faultMotion('normal',progress),reverse=faultMotion('reverse',progress),strike=faultMotion('strike',progress);
  assert.ok(normal.y<=0&&reverse.y>=0);assert.ok(Math.abs(normal.y+Math.sqrt(3)*normal.x)<1e-12,'motion stays on dipping fault plane');
  assert.equal(strike.y,0);assert.equal(strike.x,0);assert.equal(normal.y+reverse.y,0);
}
assert.equal(faultMotion('normal',2).y,faultMotion('normal',1).y);
for(const wet of [true,false]){let previous=-1;for(let impervious=0;impervious<=1;impervious+=.05){const b=waterBudget(impervious,wet);assert.equal(b.runoff+b.infiltration,b.rain);assert.ok(b.runoff>=previous);previous=b.runoff;}}
assert.deepEqual(waterBudget(0,false),{rain:100,infiltration:60,runoff:40});assert.equal(waterBudget(1,true).infiltration,0);
for(const wet of [true,false])for(let p=0;p<=100;p+=5){const tokens=infiltrationTokens(p/100,wet);assert.equal(tokens.size,waterBudget(p/100,wet).infiltration);for(const i of tokens)assert.ok(((i%10)*.4+.2)/4>=p/100-1e-9,'never infiltrate through sealed ground');}
assert.equal(airParcel(0,true).condensed,false);assert.equal(airParcel(1,true).condensed,true);assert.equal(airParcel(1,false).condensed,false);
for(const lesson of Object.values(lessons)){
 for(const field of ['tag','title','hook','goal','task','why','limit','question'])for(const lang of ['es','en'])assert.ok(lesson[field][lang].length>10);
 for(const array of ['beats','answers','feedback']){assert.equal(lesson[array].length,3);for(const pair of lesson[array])assert.ok(pair.es&&pair.en);}
 assert.ok(Number.isInteger(lesson.correct)&&lesson.correct>=0&&lesson.correct<3);assert.match(lesson.source.url,/^https:\/\/(www\.usgs\.gov|forecast\.weather\.gov)\//);
}
const html=fs.readFileSync('learn.html','utf8');assert.ok(!html.includes('<img'),'the new experience uses live geometry rather than article images');
for(const id of ['learning-canvas','experiment-time','challenge-feedback','learning-note','download-notebook'])assert.ok(html.includes(`id="${id}"`));
const script=fs.readFileSync('assets/js/learning-studio.js','utf8');assert.match(script,/prefers-reduced-motion/);assert.match(script,/visibilitychange/);assert.match(script,/worldFailed/);assert.ok(!/fetch\(|XMLHttpRequest/.test(script),'notes must not be sent to a server');
assert.ok(fs.existsSync('assets/vendor/three-r180/LICENSE'));
for(const file of ['learning-studio','learning-world','learning-legacy'])execFileSync(process.execPath,['--check',`assets/js/${file}.js`]);
console.log('Learning studio: bilingual lessons, fault kinematics, closed teaching water balance, cloud contrast, motion preferences and private notes passed.');
