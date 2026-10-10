import type {FrontendRendererArgs} from '@streamlit/component-v2-lib';
import Map from 'ol/Map.js';
import View from 'ol/View.js';
import GeoJSON from 'ol/format/GeoJSON.js';
import VectorSource from 'ol/source/Vector.js';
import VectorLayer from 'ol/layer/Vector.js';
import ImageLayer from 'ol/layer/Image.js';
import ImageStatic from 'ol/source/ImageStatic.js';
import TileLayer from 'ol/layer/Tile.js';
import OSM from 'ol/source/OSM.js';
import {getRenderPixel} from 'ol/render.js';
import WebGLVector from 'ol/layer/WebGLVector.js';
import {defaults as interactions} from 'ol/interaction/defaults.js';
import DragPan from 'ol/interaction/DragPan.js';
import {Fill, Stroke, Style, Circle as CircleStyle} from 'ol/style.js';
import {asArray} from 'ol/color.js';
import 'ol/ol.css';
import './map.css';

// SDK objects are transient presentation resources, never a project document.
const instances = new WeakMap<object, Adapter>();
type Intent = {sequence: number; action: string; [key: string]: unknown};
type Data = {version:number; layers:any[]; view:{bbox:number[]}; active_layer:string;
 selection:string[]; confirmation?:any; error?:string; project_id:string;basemap?:string;raster_time?:any;pixel_result?:any;output_frame?:any;
 workspace_layout?:{dock_open:boolean;dock_height?:number;time_height?:number;top_height?:number;temporal_preview:boolean};temporal_preview?:{image:string;caption:string}};
type Args = FrontendRendererArgs<any,Data>;
const constrained = (box:number[]) => {
 const w=Math.min(360,Math.max(.0001,box[2]-box[0])),h=Math.min(179.998,Math.max(.0001,box[3]-box[1]));
 const x=Math.min(180-w,Math.max(-180,box[0])),y=Math.min(89.999-h,Math.max(-89.999,box[1]));
 return [x,y,x+w,y+h];
};
class Adapter {
 root:HTMLElement; map:Map; args:Args; data:Data; layers=new globalThis.Map<string,any>();
 highlight=new VectorSource(); overlay:VectorLayer; client=crypto.randomUUID().replaceAll('-','');
 sequence=0; confirmed=0; pending:Intent[]=[]; version:number; muted=0; builds=0; mode='WebGL'; notice='';
 active:string; selection:string[]; timer:any; disposed=false; initialized=false; cameraDirty=false;
 compact?:boolean;
 basemap?:TileLayer; playTimer?:ReturnType<typeof setInterval>; swipe=.5;
 displayedIndex?:number;
 playbackIndex?:number; playbackBusy=false; playbackGeneration=0;
 viewportObserver:ResizeObserver; lastSize=''; layoutFitPending=false;
 resize=()=>{const compact=window.innerWidth<=1000;if(compact!==this.compact){this.compact=compact;this.args.setTriggerValue('ui_event',{action:'viewport',width:window.innerWidth})}};
 constructor(args:Args) {
  this.args=args;this.data=args.data;this.version=args.data.version;
  this.root=args.parentElement.querySelector('#sig-map') as HTMLElement;
  this.root.dataset.instance=this.client;
  this.active=args.data.active_layer;this.selection=[...args.data.selection];
  this.overlay=new VectorLayer({source:this.highlight,style:new Style({
   fill:new Fill({color:'rgba(255,207,102,.25)'}),stroke:new Stroke({color:'#ffcf66',width:3}),
   image:new CircleStyle({radius:9,fill:new Fill({color:'#ffcf66'}),stroke:new Stroke({color:'#07231e',width:2})})}),zIndex:10000});
  this.map=new Map({target:this.q('sig-geographic-map'),controls:[],layers:[this.overlay],
   interactions:interactions({dragPan:false,doubleClickZoom:false,altShiftDragRotate:false,pinchRotate:false,zoomDuration:0}).extend([new DragPan()]),
   view:new View({projection:'EPSG:4326',center:[-78,-2],zoom:5,enableRotation:false,
    extent:[-180,-89.999,180,89.999],showFullExtent:true,multiWorld:false,constrainResolution:false,
    minResolution:.0000001,maxResolution:3})});
  // Read-only inspection seam for real Chrome tests; it does not publish state.
  Object.defineProperty(this.root,'sigAdapter',{value:this,configurable:true});
  this.map.on('pointerdrag',()=>{this.cameraDirty=true});
  this.q('sig-geographic-map').addEventListener('wheel',()=>{this.cameraDirty=true},{passive:true});
  this.q('sig-geographic-map').addEventListener('keydown',event=>{
   if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','-','='].includes(event.key))this.cameraDirty=true;
  });
  this.map.on('moveend',()=>{if(!this.muted&&!this.disposed&&this.initialized&&this.cameraDirty){this.cameraDirty=false;this.cameraIntent()}});
  this.map.on('change:size',()=>{if(!this.initialized)this.bootLayout()});
  this.map.on('rendercomplete',()=>{this.root.dataset.rendered='1'});
  // The output guide depends on the geographic view, not on completion of
  // remote basemap tiles. Draw it even when a tile is slow or unavailable.
  this.map.on('postrender',()=>this.paintFrame());
  this.map.on('click',event=>{
   let selected=this.active;
   const time=this.data.raster_time;
   if(time&&!time.compare&&this.displayedIndex!==undefined)selected=time.layers[this.displayedIndex];
   if(time?.compare)selected=time.layers[event.pixel[0]<(this.map.getSize()?.[0]||1)*this.swipe?0:1];
   const layer=this.layers.get(selected);
   if(layer?.record.type==='raster'){
    if(layer.record.visible){this.q('sig-raster-query').textContent='Consultando celda nativa…';this.args.setTriggerValue('ui_event',{action:'query_raster',version:this.version,layer_id:selected,lon:event.coordinate[0],lat:event.coordinate[1]})}
    return;
   }
   const feature=layer?.record.visible?this.map.forEachFeatureAtPixel(event.pixel,f=>f,
    {layerFilter:l=>l===layer.layer,hitTolerance:3}):undefined;
   this.selection=feature?[String(feature.getId())]:[];this.paintSelection();
   this.intent(feature?'select':'clear_selection',feature?{layer_id:this.active,region_id:String(feature.getId())}:{});
  });
  this.map.on('pointermove',event=>{const c=event.coordinate;this.q('sig-coordinate').textContent=`Lon ${c[0].toFixed(5)}° · Lat ${c[1].toFixed(5)}°`});
  this.root.addEventListener('webglcontextlost',this.contextLost,true);
  this.q('sig-zoom-in').onclick=()=>this.zoom(.8);
  this.q('sig-zoom-out').onclick=()=>this.zoom(1.25);
  this.q('sig-fit-all').onclick=()=>this.fitVisible();
  this.q('sig-fit-layer').onclick=()=>this.fitVisible(this.active);
  this.q('sig-clear').onclick=()=>{this.selection=[];this.paintSelection();this.intent('clear_selection',{})};
  this.q('sig-empty-import').onclick=()=>this.args.setTriggerValue('ui_event',{action:'import'});
  this.q('sig-raster-play').onclick=()=>{
   if(this.playTimer){this.pausePlayback();return}
   this.playbackIndex=this.displayedIndex??this.data.raster_time.index;
   this.q('sig-raster-play').textContent='Pausar';this.playTimer=setInterval(()=>{
    if(!this.data.raster_time||this.pending.length)return;
    const index=((this.playbackIndex??this.data.raster_time.index)+1)%this.data.raster_time.layers.length;
    // Keep the confirmed observation visible while the next native source is
    // resolved. Never display a newer date over the old raster optimistically.
    this.showObservation(index);
   },Math.max(100,(this.data.raster_time?.duration??3)*1000/(this.data.raster_time?.layers.length??2)));
  };
  (this.q('sig-raster-date') as HTMLInputElement).onchange=event=>{this.pausePlayback(false);this.intent('raster_date',{index:Number((event.target as HTMLInputElement).value)})};
  this.q('sig-raster-configure').onclick=()=>{this.pausePlayback();this.args.setTriggerValue('ui_event',{action:'timelapse'})};
  (this.q('sig-raster-compare') as HTMLInputElement).onchange=event=>{
   const index=this.displayedIndex??this.data.raster_time.index;this.pausePlayback(false);
   this.args.setTriggerValue('ui_event',{action:'compare_series',version:this.version,index,compare:(event.target as HTMLInputElement).checked});
  };
  this.q('sig-raster-send').onclick=()=>{this.pausePlayback();this.args.setTriggerValue('ui_event',{action:'send_series'})};
  (this.q('sig-raster-swipe') as unknown as HTMLInputElement).oninput=event=>{this.swipe=Number((event.target as HTMLInputElement).value)/100;this.map.render()};
  window.addEventListener('resize',this.resize);
  this.q('sig-retry').onclick=()=>{if(this.pending.length)this.transmit()};
  this.q('sig-discard').onclick=()=>{this.pending=[];this.sequence=this.confirmed;
   this.data={...this.data,confirmation:undefined,error:''};this.hydrate(this.data,true)};
  this.hydrate(args.data,true);
  this.bootLayout();
  this.resize();
  this.viewportObserver=new ResizeObserver(()=>{
   const element=this.q('sig-geographic-map'),size=`${element.clientWidth}:${element.clientHeight}`;
   if(size===this.lastSize)return;this.lastSize=size;this.layoutFitPending=true;
   requestAnimationFrame(()=>this.fitLayout());
  });
  this.viewportObserver.observe(this.q('sig-geographic-map'));
 }
 q(id:string){return this.root.querySelector('#'+id) as HTMLElement & {disabled?:boolean}}
 pausePlayback(persist=true){
  clearInterval(this.playTimer);this.playTimer=undefined;this.playbackGeneration++;this.playbackBusy=false;
  const index=this.displayedIndex;this.playbackIndex=undefined;this.q('sig-raster-play').textContent='Reproducir fechas';
  if(persist&&index!==undefined&&index!==this.data.raster_time?.index)this.intent('raster_date',{index});
  this.paintStatus();
 }
 async showObservation(index:number){
  if(this.playbackBusy||!this.data.raster_time)return;
  const entry=this.layers.get(this.data.raster_time.layers[index]);if(!entry?.record.playback_url)return;
  const requestedUrl=entry.record.playback_url;
  const generation=++this.playbackGeneration;this.playbackBusy=true;
  try{
   const response=await fetch(requestedUrl,{cache:'no-store'});if(!response.ok)throw new Error('Fuente no disponible o modificada');
   if(response.headers.get('X-Ecuador-Observation-Date')!==entry.record.date)throw new Error('Fecha de representación incompatible');
   const blob=await response.blob();const url=URL.createObjectURL(blob),image=new Image();image.src=url;
   try{
    await image.decode();
    if(this.disposed||generation!==this.playbackGeneration||entry.record.playback_url!==requestedUrl||!this.layers.has(entry.record.id))return;
    // Source loading/decoding completes while the old layer remains visible.
    const source=new ImageStatic({url,imageExtent:entry.record.bbox,projection:'EPSG:4326',interpolate:false});
    const wrapper=source.getImage(entry.record.bbox,this.map.getView().getResolution()||1,1,this.map.getView().getProjection())!;
    await new Promise<void>((resolve,reject)=>{wrapper.addEventListener('change',()=>{if(wrapper.getState()===2)resolve();if(wrapper.getState()===3)reject(new Error('Imagen no decodificada'))});wrapper.load()});
    if(generation!==this.playbackGeneration){source.dispose();return}
    const previous=entry.source;entry.source=source;entry.layer.setSource(source);previous?.dispose();
    this.playbackIndex=this.displayedIndex=index;this.paintRasters();this.map.render();
    this.status('Reproducción local · la fecha se confirma al pausar','playing');
   }finally{URL.revokeObjectURL(url)}
  }catch(error){this.notice='No se cargó la observación; se conserva el último cuadro válido. '+String(error);this.pausePlayback(false);this.paintStatus()}
  finally{if(generation===this.playbackGeneration)this.playbackBusy=false}
 }
 status(text:string,state:string){this.q('sig-map-status').textContent=text;this.root.dataset.state=state}
 makeLayer(source:VectorSource,style:any) {
  if(this.mode==='WebGL') {
   try {
    const probe=document.createElement('canvas');const gl=probe.getContext('webgl');
    if(!gl)throw new Error('WebGL no disponible');gl.getExtension('WEBGL_lose_context')?.loseContext();
    const layer=new WebGLVector({source,style:{'fill-color':['var','fill'],'stroke-color':['var','stroke'],'stroke-width':1.5,
      'circle-radius':6,'circle-fill-color':['var','fill'],'circle-stroke-color':['var','stroke'],'circle-stroke-width':1.5},
      variables:this.variables(style)});
    layer.getRenderer();return layer;
   } catch(error){this.mode='Canvas';this.notice='WebGL no disponible: respaldo Canvas; rendimiento inferior.'}
  }
  return new VectorLayer({source,style:this.canvasStyle(style)});
 }
 variables(style:any){const fill=asArray(style.fill),stroke=asArray(style.stroke);return {fill:`rgba(${fill[0]},${fill[1]},${fill[2]},${style.opacity})`,stroke:`rgba(${stroke[0]},${stroke[1]},${stroke[2]},${style.opacity})`}}
 canvasStyle(style:any){const c=asArray(style.fill).slice(),s=asArray(style.stroke).slice();c[3]=s[3]=style.opacity;return new Style({fill:new Fill({color:c}),stroke:new Stroke({color:s,width:1.5}),image:new CircleStyle({radius:6,fill:new Fill({color:c}),stroke:new Stroke({color:s,width:1.5})})})}
 contextLost=(event:Event)=>{
  event.preventDefault();this.mode='Canvas';this.notice='Contexto WebGL perdido: respaldo Canvas; rendimiento inferior.';
  for(const entry of this.layers.values()) {
   if(entry.record.type==='raster')continue;
   this.map.removeLayer(entry.layer);entry.layer.dispose();entry.layer=this.makeLayer(entry.source,entry.record.style);
   this.map.addLayer(entry.layer);entry.layer.setVisible(entry.record.visible);entry.layer.setZIndex(entry.order);
  }
  this.paintStatus();
 };
 hydrate(data:Data,force=false) {
  if(data.version<this.version)return; // Ignore late responses, including their camera.
  if(this.playTimer&&JSON.stringify(data.raster_time?.layers)!==JSON.stringify(this.data.raster_time?.layers))this.pausePlayback(false);
  this.data=data;this.version=data.version;
  this.root.classList.toggle('sig-has-raster-time',Boolean(data.raster_time));
  if(data.basemap==='osm'&&!this.basemap){this.basemap=new TileLayer({source:new OSM({crossOrigin:'anonymous',maxZoom:16}),zIndex:-100});this.map.addLayer(this.basemap)}
  this.basemap?.setVisible(data.basemap==='osm');this.q('sig-basemap-credit').hidden=data.basemap!=='osm';
  this.q('sig-raster-controls').hidden=!data.raster_time;
  if(!data.raster_time&&this.playTimer){clearInterval(this.playTimer);this.playTimer=undefined;this.q('sig-raster-play').textContent='Reproducir fechas'}
  const pixel=data.pixel_result;
  if(pixel)this.q('sig-raster-query').textContent=`${pixel.date||'Resultado'} · ${pixel.value===null?'Sin dato':pixel.value+' '+pixel.units} · fila ${pixel.row}, col ${pixel.column}`;
  this.root.classList.toggle('sig-workspace',Boolean(data.workspace_layout));
  const layout=data.workspace_layout;
  this.root.style.setProperty('--sig-map-height',`max(140px, calc(100dvh - ${(layout?.top_height??56)+(layout?.time_height??36)+(layout?.dock_height??0)+106}px))`);
  const preview=this.q('sig-temporal-preview');preview.hidden=!data.temporal_preview;
  if(data.temporal_preview){
   const img=preview.querySelector('img')!;
   if(img.src!==data.temporal_preview.image)img.src=data.temporal_preview.image;
   preview.querySelector('figcaption')!.textContent=data.temporal_preview.caption;
  }
  this.q('sig-geographic-map').toggleAttribute('inert',Boolean(data.temporal_preview));
  this.q('sig-coordinate').hidden=Boolean(data.temporal_preview);
  const empty=!data.layers.length&&!data.temporal_preview;
  this.q('sig-empty').hidden=!empty;
  this.paintLegend();
  for(const id of ['sig-zoom-in','sig-zoom-out','sig-fit-all','sig-fit-layer','sig-clear'])this.q(id).hidden=Boolean(data.temporal_preview);
  const ack=data.confirmation;
  if(ack?.client===this.client&&ack.status==='saved'){
   this.confirmed=Math.max(this.confirmed,ack.sequence);this.pending=this.pending.filter(c=>c.sequence>this.confirmed);
  }
  const wanted=new Set(data.layers.map(l=>l.id));
  for(const [id,entry] of this.layers)if(!wanted.has(id)){this.map.removeLayer(entry.layer);entry.layer.dispose();this.layers.delete(id)}
  data.layers.forEach((record,order)=>{
   let entry=this.layers.get(record.id);
   if(!entry||entry.revision!==record.representation_revision) {
    this.root.dataset.rendered='0';
    if(entry){this.map.removeLayer(entry.layer);entry.layer.dispose()}
    if(record.type==='raster') {
     const source=undefined;
     const layer=new ImageLayer({source,opacity:record.style.opacity});
     layer.on('prerender',event=>{
      const time=this.data.raster_time,position=time?.layers.indexOf(record.id);
      if(!time?.compare||position<0)return;
      const ctx=event.context as CanvasRenderingContext2D;ctx.save();ctx.beginPath();
      const size=this.map.getSize()!,left=position===0?0:this.swipe*size[0],right=position===0?this.swipe*size[0]:size[0];
      const points=[[left,0],[right,0],[right,size[1]],[left,size[1]]].map(p=>getRenderPixel(event,p));
      ctx.moveTo(points[0][0],points[0][1]);for(const p of points.slice(1))ctx.lineTo(p[0],p[1]);ctx.closePath();ctx.clip();
     });
     layer.on('postrender',event=>{const time=this.data.raster_time;if(time?.compare&&time.layers.includes(record.id))(event.context as CanvasRenderingContext2D).restore()});
     entry={source,layer,revision:record.representation_revision,record,order};
    } else {
    const features=new GeoJSON().readFeatures({type:'FeatureCollection',features:record.features.map((f:any)=>
      ({type:'Feature',id:f.region_id,geometry:f.geometry,properties:{}}))},
      {dataProjection:'EPSG:4326',featureProjection:'EPSG:4326'});
    const source=new VectorSource({features,wrapX:false});
    entry={source,layer:this.makeLayer(source,record.style),revision:record.representation_revision,record,order};
    }
    this.layers.set(record.id,entry);this.map.addLayer(entry.layer);this.builds++;
   }
   if(record.type==='raster'&&record.image&&entry.loadedImage!==record.image&&entry.loadingImage!==record.image)this.prepareRaster(entry,record);
   if(JSON.stringify(entry.record.style)!==JSON.stringify(record.style)) {
    if(record.type==='raster')entry.layer.setOpacity(record.style.opacity);
    else if(entry.layer instanceof WebGLVector)entry.layer.updateStyleVariables(this.variables(record.style));
    else entry.layer.setStyle(this.canvasStyle(record.style));
   }
   entry.record=record;entry.order=order;entry.layer.setVisible(record.visible);entry.layer.setZIndex(order);
  });
  if(!this.pending.length||force) {
   this.active=data.active_layer;this.selection=[...data.selection];
   // A confirmed local camera already has the desired view. Avoid reset during a new gesture.
   if(force||!this.cameraDirty&&(ack?.client!==this.client||ack?.version!==data.version))this.fit(data.view.bbox);
  }
  this.paintRasters();this.paintSelection();this.paintStatus();
  this.root.dataset.version=String(this.version);this.root.dataset.builds=String(this.builds);
  this.root.dataset.features=String([...this.layers.values()].reduce((n,e)=>n+(e.source?.getFeatures?.().length||0),0));
  this.root.dataset.selection=JSON.stringify(this.selection);this.root.dataset.active=this.active||'';
  this.q('sig-fit-layer').disabled=!this.active;
  this.map.updateSize();
  requestAnimationFrame(()=>{if(!this.disposed)this.map.updateSize()});
  this.fitLayout();
 }
 prepareRaster(entry:any,record:any){
  const token=entry.loadToken=(entry.loadToken||0)+1;entry.loadingImage=record.image;
  const source=new ImageStatic({url:record.image,imageExtent:record.bbox,projection:'EPSG:4326',interpolate:false});
  const image=source.getImage(record.bbox,this.map.getView().getResolution()||1,1,this.map.getView().getProjection())!;
  const finish=()=>{
   if(image.getState()!==2&&image.getState()!==3)return;
   if(this.disposed||entry.loadToken!==token||!this.layers.has(record.id)){source.dispose();return}
   entry.loadingImage=null;
   if(image.getState()===3){source.dispose();this.notice='No se pudo cargar la observación. Se conserva el último cuadro válido.';this.paintStatus();return}
   const previous=entry.source;entry.source=source;entry.loadedImage=record.image;entry.layer.setSource(source);previous?.dispose();
   this.paintRasters();this.map.render();
  };
  image.addEventListener('change',finish);image.load();finish();
 }
 fitLayout(){
  if(this.disposed||!this.initialized||!this.layoutFitPending||this.cameraDirty||this.pending.length)return;
  this.map.updateSize();this.fit(this.data.view.bbox);this.layoutFitPending=false;
 }
 paintStatus() {
  this.root.dataset.engine='OpenLayers '+this.mode;this.q('sig-engine').textContent='OpenLayers 10.11.0 · '+this.mode+' · vista EPSG:4326'+(this.data.layers.some(l=>l.type==='raster')?' · ráster Canvas RGBA':'');
  const rejected=this.data.confirmation?.client===this.client&&this.data.confirmation?.status==='rejected';
  this.q('sig-retry').hidden=this.q('sig-discard').hidden=!rejected;
  this.q('sig-notice').textContent=this.notice;
  if(!this.initialized)this.status('Cargando mapa…','loading');
  else if(rejected)this.status(this.data.confirmation.error+' · Gestos conservados: reintentar o descartar.','error');
  else if(this.pending.length)this.status('Guardando vista… puedes seguir navegando','pending');
  else this.status(this.data.error||'Guardado',this.data.error?'error':'saved');
 }
 paintRasters(){const time=this.data.raster_time;
  if(time&&this.playbackIndex===undefined){
   const targets=(time.compare?time.layers:[time.layers[time.index]]).map((id:string)=>this.layers.get(id));
   if(targets.every((e:any)=>e?.source&&e.loadedImage===e.record.image))this.displayedIndex=time.index;
  }else if(!time)this.displayedIndex=undefined;
  for(const entry of this.layers.values()){
   if(entry.record.type!=='raster')continue;
   const index=time?.layers.indexOf(entry.record.id)??-1;
   entry.layer.setVisible(entry.record.visible&&Boolean(entry.source)&&(index<0||time.compare||index===this.displayedIndex));
  }
  if(time){const records=time.layers.map((id:string)=>this.layers.get(id)?.record);
   this.q('sig-raster-calendar').textContent=time.compare?`${records[0]?.date} | ${records[1]?.date}`:records[this.displayedIndex??time.index]?.date;
   const slider=this.q('sig-raster-date') as HTMLInputElement;slider.max=String(time.layers.length-1);slider.value=String(this.displayedIndex??time.index);
   this.q('sig-raster-summary').textContent=`${time.layers.length} observaciones · ${time.duration??3} s de video · sin interpolación`;
   const compare=this.q('sig-raster-compare') as HTMLInputElement;compare.closest('label')!.hidden=time.layers.length!==2;compare.checked=Boolean(time.compare);compare.disabled=this.pending.length>0;
   (this.q('sig-raster-swipe') as unknown as HTMLInputElement).disabled=!time.compare;
   this.q('sig-raster-swipe').closest('label')!.hidden=!time.compare;
  }
  // Keep only the displayed and requested observations: bounded decoded cache.
  if(time&&!time.compare)for(const [id,e] of this.layers){if(time.layers.includes(id)&&!([time.layers[time.index],time.layers[this.displayedIndex??time.index]]).includes(id)&&e.source){e.layer.setSource(undefined);e.source.dispose();e.source=undefined;e.loadedImage=null}}
  this.paintLegend();
 }
 paintLegend(){
  const data=this.data,time=data.raster_time,legend=this.q('sig-legend');legend.replaceChildren();
  for(const record of data.layers.filter(l=>l.visible&&(!time?.layers.includes(l.id)||time.compare||l.id===time.layers[this.displayedIndex??time.index]))){
   const row=document.createElement('div'),swatch=document.createElement('span'),label=document.createElement('span');
   swatch.style.backgroundColor=record.style.fill;swatch.style.borderColor=record.style.stroke;swatch.style.opacity=String(record.style.opacity);
   label.textContent=record.name;label.title=record.name;
   if(record.type==='raster'){
    const scale=record.scale;label.textContent+=scale?` · ${Number(scale.stops[0]).toPrecision(5)} — ${Number(scale.stops.at(-1)).toPrecision(5)} ${record.units}`:' · Sin cobertura';
    if(scale){swatch.style.backgroundImage=`linear-gradient(90deg, ${scale.palette.join(',')})`;swatch.style.width='48px'}
   }
   row.append(swatch,label);legend.append(row);
  }
  legend.hidden=!legend.childElementCount||Boolean(data.temporal_preview);
 }
 paintFrame(){const frame=this.data.output_frame,element=this.q('sig-output-frame');element.hidden=!frame;
  if(!frame)return;
  const a=this.map.getPixelFromCoordinate([frame.bbox[0],frame.bbox[3]]),b=this.map.getPixelFromCoordinate([frame.bbox[2],frame.bbox[1]]);
  if(!a||!b)return;
  Object.assign(element.style,{left:a[0]+'px',top:a[1]+'px',width:(b[0]-a[0])+'px',height:(b[1]-a[1])+'px'});
  element.querySelector('span')!.textContent=`${frame.width} × ${frame.height} · ventana del mapa`;
  const guides=this.q('sig-safe-guides');guides.hidden=!frame.safe_guides;guides.style.inset=(frame.margin_fraction*100)+'%';
 }
 paintSelection(){this.highlight.clear();const entry=this.layers.get(this.active);const source=entry?.record.visible&&entry.record.type!=='raster'?entry.source:undefined;
  for(const id of this.selection){const feature=source?.getFeatureById(id);if(feature)this.highlight.addFeature(feature.clone())}
  this.root.dataset.selection=JSON.stringify(this.selection);
 }
 bootLayout(){if(this.disposed||this.initialized)return;
  const size=this.map.getSize();
  if(!size||size[0]<10||size[1]<10){cancelAnimationFrame(this.timer);this.timer=requestAnimationFrame(()=>{this.map.updateSize();this.bootLayout()});return}
  this.initialized=true;this.fit(this.data.view.bbox);this.paintStatus();
 }
 fit(box:number[]){this.root.dataset.bbox=JSON.stringify(box);
  const size=this.map.getSize();if(!size||size[0]<10||size[1]<10)return;
  this.muted++;this.map.getView().fit(box,{size,duration:0});
  try{this.map.renderSync()}catch(error){this.contextLost(new Event('webglcontextlost',{cancelable:true}));this.map.renderSync()}
  queueMicrotask(()=>this.muted=Math.max(0,this.muted-1));this.root.dataset.bbox=JSON.stringify(box)}
 fitVisible(id?:string){const entries=[...this.layers.values()].filter(e=>e.record.visible&&(!id||e.record.id===id));
  if(!entries.length)return;
  const extents=entries.map(e=>e.record.bbox||e.source.getExtent());let box=[Math.min(...extents.map(b=>b[0])),Math.min(...extents.map(b=>b[1])),Math.max(...extents.map(b=>b[2])),Math.max(...extents.map(b=>b[3]))];
  const dx=Math.max(.001,(box[2]-box[0])*.05),dy=Math.max(.001,(box[3]-box[1])*.05);
  this.fit(constrained([box[0]-dx,box[1]-dy,box[2]+dx,box[3]+dy]));this.cameraIntent();
 }
 zoom(factor:number){this.cameraDirty=true;const view=this.map.getView();view.setResolution((view.getResolution()||1)*factor)}
 cameraIntent(){const box=constrained(this.map.getView().calculateExtent(this.map.getSize()));
  this.root.dataset.bbox=JSON.stringify(box);this.intent('view',{bbox:box})}
 intent(action:string,values:object){this.pending.push({sequence:++this.sequence,action,...values});
  this.paintStatus();this.transmit();}
 transmit(){if(!this.pending.length)return;
  this.args.setTriggerValue('command',{client:this.client,sequence:this.sequence,version:this.version,commands:this.pending});}
 dispose(){this.disposed=true;clearInterval(this.playTimer);cancelAnimationFrame(this.timer);this.viewportObserver.disconnect();window.removeEventListener('resize',this.resize);this.root.removeEventListener('webglcontextlost',this.contextLost,true);
  this.map.setTarget(undefined);for(const entry of this.layers.values())entry.layer.dispose();this.map.dispose();}
}
export default function(args:Args) {
 let adapter=instances.get(args.parentElement);
 if(!adapter){adapter=new Adapter(args);instances.set(args.parentElement,adapter)}
 else {adapter.args=args;adapter.hydrate(args.data)}
 return ()=>{setTimeout(()=>{if(!adapter!.root.isConnected){adapter!.dispose();instances.delete(args.parentElement)}},0)};
}
