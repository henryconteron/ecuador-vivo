// Synthetic, dimensionless QA mesh; never an Ecuadorian DEM or subsurface model.
export function terrainHeight(x,y){return .12+.34*Math.exp(-((x+.4)**2*5+y*y*2))+.24*Math.exp(-((x-.5)**2*8+(y-.3)**2*4))-.09*Math.exp(-((x-.18*Math.sin(y*4))**2*45))+.025*Math.sin(x*9+y*4);}
export function createTerrain(size=37){
  if(!Number.isInteger(size)||size<3||size>80)throw new Error('Invalid grid');
  return Array.from({length:size},(_,j)=>Array.from({length:size},(_,i)=>{const x=i/(size-1)*2-1,y=j/(size-1)*2-1;return {x,y,z:terrainHeight(x,y)};}));
}
export function projectPoint(p,{yaw,pitch,exaggeration}){
  const x=p.x*Math.cos(yaw)-p.y*Math.sin(yaw),y=p.x*Math.sin(yaw)+p.y*Math.cos(yaw),z=p.z*exaggeration;
  return {x,y:y*Math.sin(pitch)-z*Math.cos(pitch),depth:y*Math.cos(pitch)+z*Math.sin(pitch)};
}
export function sectionProfile(grid,row){if(!Number.isInteger(row)||row<0||row>=grid.length)throw new Error('Invalid row');return grid[row].map(p=>({...p}));}
export function modelState(values={}){
  const bound=(key,min,max,fallback)=>Number.isFinite(Number(values[key]))&&values[key]!==null?Math.min(max,Math.max(min,Number(values[key]))):fallback;
  return {yaw:bound('yaw',-180,180,35),pitch:bound('pitch',15,80,40),exaggeration:bound('exaggeration',1,4,1),zoom:bound('zoom',.6,1.6,1),section:Math.round(bound('section',0,36,18))};
}
