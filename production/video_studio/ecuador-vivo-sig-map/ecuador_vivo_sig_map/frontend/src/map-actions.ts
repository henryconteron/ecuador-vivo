/** Own GIS interaction layer; never recalculates source data or exports sketches. */
import type Map from 'ol/Map.js';
import Draw from 'ol/interaction/Draw.js';
import VectorSource from 'ol/source/Vector.js';
import VectorLayer from 'ol/layer/Vector.js';
import {Fill,Stroke,Style,Circle} from 'ol/style.js';
import {unByKey} from 'ol/Observable.js';
import type {EventsKey} from 'ol/events.js';
import type Geometry from 'ol/geom/Geometry.js';
import {ExtentHistory,searchCommands,measureGeometry,commandFocusIndex,type MapCommand} from './map-interactions-model';
import {icon} from './workbench';

type Host={root:HTMLElement;map:Map;data:any;active:string;disposed:boolean;fit:(b:number[])=>void;cameraIntent:()=>void;pausePlayback:(commit?:boolean)=>void};
const COMMANDS:MapCommand[]=[
 {id:'sig-import',label:'Agregar datos',group:'Datos',keywords:'archivo importar geojson geotiff'},
 {id:'sig-toolbox-view',label:'Caja de herramientas',group:'Análisis',keywords:'procesos operaciones'},
 {id:'sig-analysis',label:'Análisis vectorial',group:'Análisis',keywords:'buffer recortar disolver centroide contornos'},
 {id:'sig-raster-tools',label:'Operaciones ráster',group:'Análisis',keywords:'diferencia media zonales comparar'},
 {id:'sig-science',label:'Fuentes científicas',group:'Datos',keywords:'clima datos observados'},
 {id:'sig-export-layer',label:'Exportar capa activa',group:'Salida',keywords:'geojson geotiff original'},
 {id:'sig-prepare',label:'Preparar serie temporal',group:'Tiempo',keywords:'clima timelapse fuente periodo'},
 {id:'sig-series-palette',label:'Paleta de la serie',group:'Tiempo',keywords:'color estilo'},
 {id:'sig-time-view',label:'Control temporal',group:'Tiempo',keywords:'fecha reproducir'},
 {id:'sig-layers-view',label:'Capas del proyecto',group:'Vista'},
 {id:'sig-reference-view',label:'Mapa de referencia',group:'Vista',keywords:'fondo osm'},
 {id:'sig-properties-view',label:'Propiedades de capa',group:'Vista',keywords:'simbolo opacidad'},
 {id:'sig-attributes-view',label:'Tabla de atributos',group:'Datos',keywords:'entidades campos'},
 {id:'sig-results-view',label:'Resultados y métricas',group:'Análisis'},
 {id:'sig-fit-all',label:'Ajustar todas las capas visibles',group:'Vista',keywords:'zoom extension'},
 {id:'sig-fit-layer',label:'Ajustar la capa activa',group:'Vista',keywords:'zoom extension'},
 {id:'sig-view-back',label:'Encuadre anterior',group:'Vista'},
 {id:'sig-view-forward',label:'Encuadre siguiente',group:'Vista'},
 {id:'sig-measure-length',label:'Medir distancia',group:'Medición',keywords:'longitud regla'},
 {id:'sig-measure-area',label:'Medir área',group:'Medición',keywords:'superficie poligono'},
 {id:'sig-measure-clear',label:'Salir de medición y borrar boceto',group:'Medición'},
 {id:'sig-output-settings',label:'Formato y encuadre del video',group:'Salida',keywords:'tiktok instagram youtube'},
 {id:'sig-send-top',label:'Enviar serie a Studio',group:'Salida'},
 {id:'sig-save',label:'Guardar proyecto',group:'Proyecto'},
 {id:'sig-open',label:'Abrir proyecto',group:'Proyecto'},
 {id:'sig-undo',label:'Deshacer cambio del proyecto',group:'Proyecto'},
 {id:'sig-redo',label:'Rehacer cambio del proyecto',group:'Proyecto'}
];
function element<K extends keyof HTMLElementTagNameMap>(tag:K,text='',cls=''){
 const node=document.createElement(tag);node.textContent=text;if(cls)node.className=cls;return node;
}
export class MapActions{
 private history=new ExtentHistory();private restoring=false;private project:string;
 private source=new VectorSource();private layer:VectorLayer;private draw?:Draw;private geometryKey?:EventsKey;
 private mode?:'LineString'|'Polygon';private toolbar:HTMLDivElement;private panel:HTMLDivElement;private result:HTMLOutputElement;
 private dialog:HTMLDialogElement;private search:HTMLInputElement;private list:HTMLDivElement;private launch:HTMLButtonElement;
 private returnFocus?:HTMLElement;
 constructor(private host:Host){
  this.project=host.data.project_id;this.history.record(host.data.view.bbox);
  this.layer=new VectorLayer({source:this.source,zIndex:10001,style:new Style({stroke:new Stroke({color:'#ffcf66',width:3}),fill:new Fill({color:'rgba(255,207,102,.16)'}),image:new Circle({radius:5,fill:new Fill({color:'#ffcf66'})})})});
  host.map.addLayer(this.layer);
  this.toolbar=element('div','','sig-local-tools');this.toolbar.setAttribute('role','toolbar');this.toolbar.setAttribute('aria-label','Navegación y medición local');
  const button=(id:string,label:string,glyph:string,action:()=>void)=>{
   const b=element('button');b.id=id;b.type='button';b.title=label;b.setAttribute('aria-label',label);b.append(icon(glyph));b.onclick=action;this.toolbar.append(b);return b;
  };
  button('sig-view-back','Encuadre anterior','undo',()=>this.navigate('back'));
  button('sig-view-forward','Encuadre siguiente','redo',()=>this.navigate('forward'));
  button('sig-measure-length','Medir distancia aproximada','ruler',()=>this.measure('LineString'));
  button('sig-measure-area','Medir área aproximada','area',()=>this.measure('Polygon'));
  this.launch=button('sig-command-search','Buscar comandos (Ctrl+K)','search',()=>this.openCommands());
  const label=element('span','Comandos');this.launch.append(label);
  host.root.querySelector('.sig-ribbon-navigation')!.append(this.toolbar);
  this.panel=element('div','','sig-measure-panel');this.panel.hidden=true;
  const heading=element('strong','Medición del mapa'),close=element('button','Salir');close.id='sig-measure-clear';close.type='button';close.onclick=()=>{this.stop();this.host.root.querySelector<HTMLElement>('#sig-geographic-map')?.focus()};
  const top=element('div','','sig-measure-heading');top.append(heading,close);
  this.result=element('output');this.result.setAttribute('aria-live','polite');
  this.panel.append(top,this.result,element('p','Clic para añadir puntos; doble clic para terminar. Escape cancela. La siguiente medición reemplaza el boceto.'),element('small','Aproximación esférica en WGS 84. Boceto local: no es un resultado analítico ni se exporta.'));
  host.root.querySelector('.sig-viewport')!.append(this.panel);
  this.dialog=element('dialog','','sig-command-dialog');this.dialog.setAttribute('aria-label','Buscar una herramienta del SIG');
  const head=element('div','','sig-command-heading'),title=element('strong','Herramientas del SIG'),cancel=element('button','Cerrar');cancel.type='button';cancel.onclick=()=>this.closeCommands();head.append(title,cancel);
  const searchLabel=element('label','Buscar por nombre o tarea');this.search=element('input');this.search.type='search';this.search.placeholder='Ej.: área, paleta, atributos…';this.search.autocomplete='off';searchLabel.append(this.search);
  this.list=element('div','','sig-command-list');this.dialog.append(head,searchLabel,this.list,element('small','↑ ↓ para recorrer · Enter para abrir · Escape para cerrar'));
  this.search.oninput=()=>this.paintCommands();
  this.dialog.addEventListener('keydown',this.commandKeys);this.dialog.addEventListener('cancel',()=>this.closeCommands());
  this.dialog.addEventListener('close',()=>{this.launch.setAttribute('aria-expanded','false');this.returnFocus?.focus()});
  this.launch.setAttribute('aria-haspopup','dialog');this.launch.setAttribute('aria-expanded','false');host.root.append(this.dialog);host.root.addEventListener('keydown',this.keys);
  this.sync();
 }
 get measuring(){return Boolean(this.mode)}
 private target(id:string){return this.host.root.querySelector<HTMLButtonElement>('#'+id)}
 record(box:number[]){if(!this.restoring)this.history.record(box);this.sync()}
 private navigate(direction:'back'|'forward'){
  const box=this.history[direction]();if(!box)return;
  this.restoring=true;try{this.host.fit(box);this.host.cameraIntent()}finally{this.restoring=false}this.sync();
 }
 sync(){
  if(this.project!==this.host.data.project_id){this.project=this.host.data.project_id;this.history.clear();this.history.record(this.host.data.view.bbox);this.stop()}
  this.target('sig-view-back')!.disabled=!this.history.canBack;this.target('sig-view-forward')!.disabled=!this.history.canForward;
  const unavailable=Boolean(this.host.data.temporal_preview);for(const id of ['sig-measure-length','sig-measure-area'])this.target(id)!.disabled=unavailable;
  if(unavailable&&this.mode)this.stop();
  if(this.dialog.open)this.paintCommands();
 }
 private measure(type:'LineString'|'Polygon'){
  if(this.host.data.temporal_preview)return;this.stop();this.host.pausePlayback();this.mode=type;
  this.panel.hidden=false;this.result.textContent=type==='Polygon'?'Dibuja el perímetro del área':'Dibuja el recorrido';
  this.target(type==='Polygon'?'sig-measure-area':'sig-measure-length')!.setAttribute('aria-pressed','true');
  this.host.root.querySelector<HTMLElement>('#sig-geographic-map')?.focus();
  this.draw=new Draw({source:this.source,type,stopClick:true});
  this.draw.on('drawstart',event=>{
   this.source.clear();if(this.geometryKey)unByKey(this.geometryKey);
   const geometry=event.feature.getGeometry()!;this.updateMeasure(geometry);this.geometryKey=geometry.on('change',()=>this.updateMeasure(geometry));
  });
  this.draw.on('drawend',()=>{if(this.geometryKey)unByKey(this.geometryKey);this.geometryKey=undefined;this.result.textContent+=' · terminado'});
  this.host.map.addInteraction(this.draw);
 }
 private updateMeasure(geometry:Geometry){
  const measure=measureGeometry(geometry),large=measure.kind==='area'?1e6:1000;
  const value=measure.value>=large?measure.value/large:measure.value;
  const unit=measure.value>=large?(measure.kind==='area'?'km²':'km'):measure.unit;
  this.result.textContent='≈ '+value.toLocaleString('es-EC',{maximumFractionDigits:2})+' '+unit;
 }
 private stop(){
  if(this.geometryKey)unByKey(this.geometryKey);this.geometryKey=undefined;
  if(this.draw){this.host.map.removeInteraction(this.draw);this.draw.abortDrawing();this.draw=undefined}
  this.source.clear();this.mode=undefined;this.panel.hidden=true;
  for(const id of ['sig-measure-length','sig-measure-area'])this.target(id)?.setAttribute('aria-pressed','false');
 }
 private openCommands(){
  this.returnFocus=(this.host.root.getRootNode() as ShadowRoot).activeElement as HTMLElement??this.launch;
  this.search.value='';this.paintCommands();this.dialog.showModal();this.launch.setAttribute('aria-expanded','true');this.search.focus();
 }
 private closeCommands(){if(this.dialog.open)this.dialog.close()}
 private paintCommands(){
  this.list.replaceChildren();
  for(const command of searchCommands(COMMANDS,this.search.value)){
   const target=this.target(command.id);if(!target||target.hidden||target.disabled)continue;
   const button=element('button');button.type='button';button.append(element('span',command.label),element('small',command.group));
   button.onclick=()=>{this.closeCommands();target.click()};this.list.append(button);
  }
  if(!this.list.children.length)this.list.append(element('p','No hay comandos disponibles con ese nombre en la vista actual.'));
 }
 private commandKeys=(event:KeyboardEvent)=>{
  const buttons=[...this.list.querySelectorAll('button')];if(!buttons.length)return;
  const active=(this.host.root.getRootNode() as ShadowRoot).activeElement;
  const index=buttons.indexOf(active as HTMLButtonElement);
  if(event.key==='ArrowDown'||event.key==='ArrowUp'){event.preventDefault();buttons[commandFocusIndex(index,buttons.length,event.key)].focus()}
  if(event.key==='Enter'&&active===this.search){event.preventDefault();buttons[0].click()}
 };
 private keys=(event:KeyboardEvent)=>{
  if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='k'){event.preventDefault();if(!this.dialog.open)this.openCommands();return}
  if(event.key==='Escape'&&this.mode&&!this.dialog.open){event.preventDefault();this.stop()}
 };
 dispose(){
  this.stop();this.closeCommands();this.host.root.removeEventListener('keydown',this.keys);this.dialog.removeEventListener('keydown',this.commandKeys);
  this.host.map.removeLayer(this.layer);this.layer.dispose();this.toolbar.remove();this.panel.remove();this.dialog.remove();
 }
}
