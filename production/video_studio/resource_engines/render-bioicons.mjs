import {Resvg} from '@resvg/resvg-js';import {readFile,writeFile} from 'node:fs/promises';
const folder=new URL('./artwork/',import.meta.url),catalog=JSON.parse(await readFile(new URL('catalog.json',folder),'utf8'));
for(const item of catalog.items){const svg=await readFile(new URL(item.original,folder));const png=new Resvg(svg,{fitTo:{mode:'width',value:1200},font:{loadSystemFonts:false}}).render().asPng();await writeFile(new URL(item.image,folder),png)}
console.log('Rendered',catalog.items.length,'scientific illustrations');
