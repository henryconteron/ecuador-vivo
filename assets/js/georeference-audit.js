// Diagnostic affine fit only. No raster warping, reprojection or automatic certification.
export class AuditError extends Error { constructor(code) { super(code); this.code=code; } }
const fail=code=>{throw new AuditError(code);};
const mean=values=>values.reduce((a,b)=>a+b,0)/values.length;
const finite=value=>typeof value==='number' && Number.isFinite(value);
export function validateAudit(input) {
  if (!input || input.schema_version!==1 || !Array.isArray(input.points) || input.points.length<3 || input.points.length>200) fail('format');
  if (!['EPSG:32717','EPSG:32718'].includes(input.crs)) fail('crs');
  const raster=input.raster;
  if(!raster || !Number.isInteger(raster.width) || !Number.isInteger(raster.height) || raster.width<2 || raster.height<2 || raster.width>100000 || raster.height>100000) fail('raster');
  for(const key of ['title','source','license']) if(typeof input[key]!=='string' || !input[key].trim() || input[key].length>1000) fail('metadata');
  if(input.synthetic!==undefined && typeof input.synthetic!=='boolean') fail('format');
  if(input.pixel_convention!=='center-zero-based-y-down') fail('pixels');
  if(raster.sha256!==undefined && !/^[a-f0-9]{64}$/.test(raster.sha256)) fail('raster');
  const ids=new Set();
  for(const p of input.points) {
    if(!p || typeof p.id!=='string' || !p.id.trim() || p.id.length>80 || ids.has(p.id) || !['control','check'].includes(p.role)) fail('points');
    ids.add(p.id);
    if(!['pixel_x','pixel_y','easting','northing'].every(k=>finite(p[k]))) fail('numbers');
    if(p.pixel_x<0 || p.pixel_x>raster.width-1 || p.pixel_y<0 || p.pixel_y>raster.height-1) fail('bounds');
    if(p.easting<100000 || p.easting>900000 || p.northing<0 || p.northing>10000000) fail('coordinates');
  }
  for(let i=0;i<input.points.length;i++) for(let j=0;j<i;j++) {
    const a=input.points[i],b=input.points[j];
    if(Math.hypot(a.pixel_x-b.pixel_x,a.pixel_y-b.pixel_y)<1e-6 || Math.hypot(a.easting-b.easting,a.northing-b.northing)<.001) fail('duplicate');
  }
  if(input.points.filter(p=>p.role==='control').length<3) fail('controls');
  return input;
}
export function auditGeoreference(raw) {
  const input=validateAudit(raw), controls=input.points.filter(p=>p.role==='control');
  const cx=mean(controls.map(p=>p.pixel_x)),cy=mean(controls.map(p=>p.pixel_y));
  const sx=Math.sqrt(mean(controls.map(p=>(p.pixel_x-cx)**2))),sy=Math.sqrt(mean(controls.map(p=>(p.pixel_y-cy)**2)));
  if(sx===0 || sy===0) fail('collinear');
  const x=controls.map(p=>(p.pixel_x-cx)/sx),y=controls.map(p=>(p.pixel_y-cy)/sy);
  const correlation=mean(x.map((v,i)=>v*y[i])), det=1-correlation**2;
  if(det<1e-8) fail('collinear');
  // Center and normalize pixels before solving the two-variable least-squares fit.
  function fit(key) {
    const offset=mean(controls.map(p=>p[key]));
    const dx=mean(x.map((v,i)=>v*(controls[i][key]-offset))),dy=mean(y.map((v,i)=>v*(controls[i][key]-offset)));
    const ax=(dx-correlation*dy)/det,ay=(dy-correlation*dx)/det;
    return {offset,x:ax,y:ay};
  }
  const e=fit('easting'),n=fit('northing');
  const area=e.x*n.y-e.y*n.x, size=Math.hypot(e.x,n.x)*Math.hypot(e.y,n.y);
  if(!Number.isFinite(area) || !size || Math.abs(area)/size<1e-10) fail('singular');
  const rows=input.points.map(p=>{
    const px=(p.pixel_x-cx)/sx,py=(p.pixel_y-cy)/sy;
    const predicted_easting=e.offset+e.x*px+e.y*py,predicted_northing=n.offset+n.x*px+n.y*py;
    const dx=predicted_easting-p.easting,dy=predicted_northing-p.northing;
    return {...p,predicted_easting,predicted_northing,dx_m:dx,dy_m:dy,error_m:Math.hypot(dx,dy)};
  });
  function stats(role) {
    const group=rows.filter(p=>p.role===role);
    return group.length?{count:group.length,rmse_m:Math.sqrt(mean(group.map(p=>p.error_m**2))),max_error_m:Math.max(...group.map(p=>p.error_m))}:{count:0,rmse_m:null,max_error_m:null};
  }
  const checks=stats('check'), warnings=['not-certified','independence-not-verified'];
  if(controls.length===3) warnings.push('minimal-fit');
  if(!checks.count) warnings.push('no-checks'); else if(checks.count<3) warnings.push('few-checks');
  const extent=key=>Math.max(...controls.map(p=>p[key]))-Math.min(...controls.map(p=>p[key]));
  if(extent('pixel_x')/(input.raster.width-1)<.5 || extent('pixel_y')/(input.raster.height-1)<.5) warnings.push('limited-spread');
  if(!input.raster.sha256) warnings.push('unbound-image');
  return {schema_version:1,method:'affine-least-squares-v1',status:'diagnostic-only',synthetic:input.synthetic===true,
    input,transform:{pixel_center:[cx,cy],pixel_scale:[sx,sy],easting:e,northing:n},
    controls:stats('control'),checks,points:rows,warnings};
}
export function syntheticExample() {
  const make=(id,role,x,y,de=0,dn=0)=>({id,role,pixel_x:x,pixel_y:y,easting:180000+2*x+.1*y+de,northing:9900000+.05*x-2*y+dn});
  return {schema_version:1,title:'Demostración sintética / Synthetic demonstration',source:'Invented coordinates, not an Ecuadorian map',license:'CC0 synthetic test values',synthetic:true,crs:'EPSG:32718',pixel_convention:'center-zero-based-y-down',raster:{width:1000,height:1000},points:[
    make('C1','control',50,50),make('C2','control',950,50),make('C3','control',50,950),
    make('V1','check',300,300,12,16),make('V2','check',700,300,-12,16),make('V3','check',300,700,12,-16),make('V4','check',800,800,-12,-16)]};
}
