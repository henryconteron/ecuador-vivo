// Teaching models, not calibrated simulations or Ecuador observations.
export const clamp01=value=>Math.max(0,Math.min(1,Number(value)||0));
export function faultMotion(type,progress){
  const t=clamp01(progress),slip=.8*t;
  if(type==='strike')return {x:0,y:0,z:slip};
  const sign=type==='reverse'?-1:1;
  return {x:sign*slip*.5,y:-sign*slip*Math.sqrt(3)/2,z:0};
}
export function waterBudget(impervious,wet=false){
  const rain=100,infiltration=Math.round((wet?20:60)*(1-clamp01(impervious)));
  return {rain,infiltration,runoff:rain-infiltration};
}
export function infiltrationTokens(impervious,wet=false){
  const fraction=clamp01(impervious),count=waterBudget(fraction,wet).infiltration;
  return new Set(Array.from({length:100},(_,i)=>i).filter(i=>((i%10)*.4+.2)/4>=fraction-1e-9).slice(0,count));
}
export function airParcel(progress,moist=true){
  const t=clamp01(progress),x=-2+2*t,height=1.4*Math.exp(-x*x/.85);
  // Thresholds chosen for a qualitative contrast, not an atmospheric calculation.
  return {x,height,condensed:moist&&height>=.65};
}
