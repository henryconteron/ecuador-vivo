/** Layer identity differs from a raster's replaceable presentation image. */
export function rebuildLayer(previous:any,next:any){
 return !previous||previous.type!==next.type||next.type!=='raster'&&previous.representation_revision!==next.representation_revision;
}
export function rasterImageKey(record:any){
 return JSON.stringify([record.image,record.bbox,record.presentation?.resampling]);
}
