/** Presentation-only helpers. No project mutation or analytical results. */
import type Geometry from 'ol/geom/Geometry.js';
import {getLength,getArea} from 'ol/sphere.js';

export type Box=[number,number,number,number];
export class ExtentHistory{
 private items:Box[]=[];private index=-1;private limit:number;
 constructor(limit=40){this.limit=Math.max(2,Math.floor(limit))}
 get canBack(){return this.index>0}
 get canForward(){return this.index>=0&&this.index<this.items.length-1}
 record(box:number[]){
  if(box.length!==4||!box.every(Number.isFinite)||box[0]>=box[2]||box[1]>=box[3])throw new Error('Encuadre inválido');
  if(this.items[this.index]?.every((v,i)=>Math.abs(v-box[i])<1e-7))return;
  this.items=this.items.slice(0,this.index+1);this.items.push([...box] as Box);
  if(this.items.length>this.limit)this.items.shift();this.index=this.items.length-1;
 }
 back(){if(this.canBack)return [...this.items[--this.index]] as Box}
 forward(){if(this.canForward)return [...this.items[++this.index]] as Box}
 clear(){this.items=[];this.index=-1}
}
export type MapCommand={id:string;label:string;group:string;keywords?:string};
const normalized=(value:string)=>value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase();
export function searchCommands<T extends MapCommand>(commands:T[],query:string):T[]{
 const words=normalized(query).trim().split(/\s+/).filter(Boolean);
 return commands.filter(c=>words.every(word=>normalized(c.label+' '+c.group+' '+(c.keywords??'')).includes(word)));
}
export function commandFocusIndex(current:number,count:number,key:'ArrowDown'|'ArrowUp'){
 if(count===0)return -1;
 if(current<0)return key==='ArrowDown'?0:count-1;
 return (current+(key==='ArrowDown'?1:-1)+count)%count;
}
export function measureGeometry(geometry:Geometry){
 const area=geometry.getType()==='Polygon';
 return {kind:area?'area':'length',value:area?getArea(geometry,{projection:'EPSG:4326'}):getLength(geometry,{projection:'EPSG:4326'}),unit:area?'m²':'m'};
}
