/** Presentation grouping only: no source, calendar or numeric data is changed. */
export function seriesTree(layers:any[],time?:{layers:string[];index:number}){
 const byId=new Map(layers.map(layer=>[layer.id,layer]));
 const observations=(time?.layers??[]).map(id=>byId.get(id)).filter(Boolean);
 const ids=new Set(observations.map(layer=>layer.id)),others=layers.filter(layer=>!ids.has(layer.id));
 const variables=[...new Set(observations.map(layer=>layer.variable).filter(Boolean))];
 const visible=observations.length>0&&observations.every(layer=>layer.visible);
 return {observations,others,count:observations.length,logicalCount:others.length+Number(observations.length>0),
  name:variables.length===1?String(variables[0]):'Serie temporal',visible,
  mixed:observations.some(layer=>layer.visible)&&!visible,
  current:byId.get(time?.layers[time.index])??observations[0]};
}
