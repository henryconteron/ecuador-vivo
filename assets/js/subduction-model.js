import {normalizeSnapshot,CASE_BASE,SNAPSHOT_SHA256} from './andes-pulso.js';
export const BOX={west:-83,east:-74.5,south:-5.5,north:2.5};
// Approximate local Cartesian display, in units of 450 km. Not a GIS reprojection.
export function hypocenterPoint(event){return {x:(event.longitude+78.75)*111*Math.cos(-1.5*Math.PI/180)/450,y:-(event.latitude+1.5)*111/450,z:-event.depth/450};}
export function conceptualDepth(longitude){const distance=Math.max(0,(longitude+80.5)*111);return .3*distance+.0007*distance*distance;}
export function selectHypocenters(events,{magnitude=6,to=2025,maxDepth=700}={}){
  return events.filter(e=>e.magnitude>=magnitude&&e.year<=to&&e.depth!==null&&Number.isFinite(e.depth)&&e.depth>=0&&e.depth<=maxDepth);
}
export async function loadHypocenters(fetcher=fetch){
  const response=await fetcher(CASE_BASE+'usgs_snapshot.geojson');if(!response.ok)throw new Error('snapshot');const bytes=await response.arrayBuffer();
  const sha=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(v=>v.toString(16).padStart(2,'0')).join('');if(sha!==SNAPSHOT_SHA256)throw new Error('integrity');
  return normalizeSnapshot(JSON.parse(new TextDecoder().decode(bytes)));
}
