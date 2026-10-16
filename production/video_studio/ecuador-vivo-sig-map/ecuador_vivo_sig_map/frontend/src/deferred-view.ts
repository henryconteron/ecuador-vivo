/** Only unsent camera states coalesce. Numbered protocol intents are immutable. */
export class DeferredView{
 private latest?:number[];private accepted?:number[];private timer?:ReturnType<typeof setTimeout>;private disposed=false;
 private accept:(box:number[],force:boolean)=>boolean;private delay:number;
 private schedule:typeof setTimeout;private cancelTimer:typeof clearTimeout;
 constructor(accept:(box:number[],force:boolean)=>boolean,delay=400,
  schedule:typeof setTimeout=setTimeout,cancelTimer:typeof clearTimeout=clearTimeout){
  this.accept=accept;this.delay=delay;
  // Browser timers require a Window/undefined receiver, not this model instance.
  this.schedule=(...args)=>schedule(...args);this.cancelTimer=(...args)=>cancelTimer(...args);
 }
 get pending(){return Boolean(this.latest)}
 get ready(){return this.pending&&this.timer===undefined}
 reconcile(box:number[]){
  if(!this.pending&&this.accepted&&!this.accepted.every((v,i)=>Math.abs(v-box[i])<1e-7))this.accepted=undefined;
 }
 update(box:number[]){
  if(this.disposed)return;
  if(box.length!==4||!box.every(Number.isFinite)||box[0]>=box[2]||box[1]>=box[3])throw new Error('Encuadre inválido');
  if(this.accepted?.every((v,i)=>Math.abs(v-box[i])<1e-7)){
   if(this.timer!==undefined)this.cancelTimer(this.timer);this.timer=undefined;this.latest=undefined;return;
  }
  this.latest=[...box];
  if(this.timer!==undefined)this.cancelTimer(this.timer);
  this.timer=this.schedule(()=>{this.timer=undefined;this.flush()},this.delay);
 }
 flush(force=false){
  if(this.timer!==undefined){this.cancelTimer(this.timer);this.timer=undefined}
  if(this.disposed||!this.latest)return;
  const box=this.latest;
  if(this.accepted?.every((v,i)=>Math.abs(v-box[i])<1e-7)||this.accept([...box],force)){
   this.accepted=box;this.latest=undefined;
  }
 }
 cancel(){if(this.timer!==undefined)this.cancelTimer(this.timer);this.timer=undefined;this.latest=undefined;this.accepted=undefined}
 dispose(){this.cancel();this.disposed=true}
}
