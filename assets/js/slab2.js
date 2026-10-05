// Native Slab2 nodes. A null stays a hole: never fill or extrapolate it.
export const SLAB_SHA256='526dbb73b063a1fcf2125850481de0dbc0dac56d80d3d94e5644457cf0d28388';
export function slabNode(grid,row,col){
  const depth=grid.depth_km[row]?.[col];
  if(depth===null||!Number.isFinite(depth))return null;
  return {longitude:grid.longitude[col],latitude:grid.latitude[row],depth,uncertainty:grid.uncertainty_km[row][col]};
}
export function slabSegments(grid,stride=4){
  if(!Number.isInteger(stride)||stride<1)throw new Error('stride');
  const segments=[];
  for(let r=0;r<grid.latitude.length;r++)for(let c=0;c<grid.longitude.length;c++){
    const a=slabNode(grid,r,c);if(!a)continue;
    if(r%stride===0){const b=slabNode(grid,r,c+1);if(b)segments.push([a,b]);}
    if(c%stride===0){const b=slabNode(grid,r+1,c);if(b)segments.push([a,b]);}
  }
  return segments;
}
export async function loadSlab2(fetcher=fetch){
  const response=await fetcher('data/slab2/ecuador.json');if(!response.ok)throw new Error('Slab2 unavailable');
  const bytes=await response.arrayBuffer();
  const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(n=>n.toString(16).padStart(2,'0')).join('');
  if(hash!==SLAB_SHA256)throw new Error('Slab2 integrity');
  return JSON.parse(new TextDecoder().decode(bytes));
}
