// Build-time inventory; notices ship with the optional editor assets.
import {readFile,readdir,writeFile,mkdir} from 'node:fs/promises';import path from 'node:path';import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
const out=path.resolve(here,'../ecuador-vivo-scientific-tools/ecuador_vivo_scientific_tools/frontend/build/notices');await mkdir(out,{recursive:true});
const modules=path.join(here,'node_modules'),records=[];
async function visit(dir){
 for(const entry of await readdir(dir,{withFileTypes:true})){
  if(entry.name.startsWith('.'))continue;const target=path.join(dir,entry.name);
  if(entry.name.startsWith('@')&&entry.isDirectory()){await visit(target);continue}
  if(!entry.isDirectory())continue;
  let pkg;try{pkg=JSON.parse(await readFile(path.join(target,'package.json'),'utf8'))}catch{continue}
  const licenseFiles=(await readdir(target)).filter(name=>/^(licen[cs]e|copying|notice)(\.|$)/i.test(name));
  const notice=[];for(const file of licenseFiles){try{notice.push(file+'\n'+await readFile(path.join(target,file),'utf8'))}catch{}}
  const filename=pkg.name.replaceAll('/','__').replaceAll('@','')+'.txt';
  if(notice.length)await writeFile(path.join(out,filename),notice.join('\n\n'));
  records.push({name:pkg.name,version:pkg.version,license:pkg.license||'Revisar paquete',notice:notice.length?filename:null});
 }
}
await visit(modules);await writeFile(path.join(out,'inventory.json'),JSON.stringify(records,null,2));console.log('Notices inventoried:',records.length);
