/** Short-lived display resources only. Native queries and export still verify originals. */
type Resource<T>={value:T;bytes:number;dispose:()=>void};
type Options={entries?:number;bytes?:number;ttl?:number;now?:()=>number};
export class ObservationCache<T=unknown>{
 private values=new Map<string,Resource<T>&{expires:number}>();
 private pending=new Map<string,Promise<Resource<T>>>();
 private generation=0;
 private options:Required<Options>;
 hits=0;misses=0;
 constructor(options:Options={}){
  this.options={entries:4,bytes:24*1024*1024,ttl:30000,now:()=>performance.now(),...options};
 }
 get size(){return this.values.size}
 get bytes(){return [...this.values.values()].reduce((n,r)=>n+r.bytes,0)}
 async get(key:string,load:()=>Promise<Resource<T>>):Promise<Resource<T>>{
  const cached=this.values.get(key);
  if(cached&&cached.expires>this.options.now()){
   this.hits++;this.values.delete(key);this.values.set(key,cached);return cached;
  }
  if(cached){cached.dispose();this.values.delete(key)}
  const waiting=this.pending.get(key);if(waiting)return waiting;
  const generation=this.generation;this.misses++;
  const promise=Promise.resolve().then(load).then(resource=>{
   if(generation!==this.generation){resource.dispose();throw Error('La representación cambió durante la carga.')}
   if(!Number.isFinite(resource.bytes)||resource.bytes<0||resource.bytes>this.options.bytes){
    resource.dispose();throw Error('La observación supera el límite de memoria de presentación.');
   }
   while(this.values.size>=this.options.entries||this.bytes+resource.bytes>this.options.bytes){
    const first=this.values.keys().next().value;if(first===undefined)break;
    this.values.get(first)!.dispose();this.values.delete(first);
   }
   this.values.set(key,{...resource,expires:this.options.now()+this.options.ttl});return resource;
  }).finally(()=>{if(this.pending.get(key)===promise)this.pending.delete(key)});
  this.pending.set(key,promise);return promise;
 }
 clear(){
  this.generation++;for(const resource of this.values.values())resource.dispose();
  this.values.clear();this.pending.clear();
 }
}
