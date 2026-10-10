"""Private sealed RGBA observations; no new project schema or raster engine."""
import datetime as dt
from bisect import bisect_right
import copy
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import re
import shutil
import uuid
from PIL import Image, ImageDraw
from rasterio.transform import from_bounds
from storyboard import MEDIA_ROOT
from model import frame_counts
from studio_map_layers import MapLayerPainter, _resolution
from studio_preparation import verify_sources
from studio_science import restored_snapshot

PNG_LIMIT = 100 * 1024 * 1024
MANIFEST_LIMIT = 8 * 1024 * 1024
BUNDLE_LIMIT = 1024 * 1024 * 1024
REPRESENTATION = 'rgba_observation_bundle'


def _bytes(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,allow_nan=False).encode('utf-8')


def _digest(content): return hashlib.sha256(content).hexdigest()


def legend_spec(settings):
    """Frozen display semantics; never derives statistics from rendered pixels."""
    keys=('kind','legend','units','classes') if settings['kind']=='categorical' else ('kind','legend','units','stops','palette')
    return copy.deepcopy({key:settings[key] for key in keys})


def paint_legend(settings):
    """Static RGBA auxiliary, using the exact raster colorizer and all labels."""
    import numpy as np
    from maqueta import colorize
    from studio_typography import studio_font
    spec=legend_spec(settings);font=studio_font(18)
    title=spec['legend']+(' · '+spec['units'] if spec['units'] else '')
    labels=([str(row['value'])+' · '+row['label'] for row in spec['classes']]
            if spec['kind']=='categorical' else [f'{v:g}' for v in spec['stops']])
    if not labels:raise ValueError('La leyenda necesita valores explícitos.')
    # Size follows complete labels, never truncates classes or crops units.
    width=max(640,math.ceil(font.getlength(title))+32,max(math.ceil(font.getlength(s))+72 for s in labels))
    height=64+32*len(labels)
    if width>8192 or height>8192 or width*height>40_000_000:raise ValueError('Leyenda completa superior al presupuesto.')
    image=Image.new('RGBA',(width,height));draw=ImageDraw.Draw(image)
    draw.text((16,8),title,font=font,fill='white')
    if spec['kind']=='continuous':
        with Image.fromarray(colorize(np.linspace(spec['stops'][0],spec['stops'][-1],width-32)[None,:],settings)).convert('RGBA') as bar:
            image.alpha_composite(bar.resize((width-32,20)),(16,36))
    for index,label in enumerate(labels):
        y=64+index*32
        value=spec['classes'][index]['value'] if spec['kind']=='categorical' else spec['stops'][index]
        color=tuple(int(v) for v in colorize(np.array([[value]]),settings)[0,0])
        draw.rectangle((16,y,36,y+20),fill=(*color,255))
        draw.text((48,y),label,font=font,fill='white')
    return image


def _root():
    media = Path(MEDIA_ROOT).resolve()
    root = (media/'map-bundles').resolve()
    if not root.is_relative_to(media): raise ValueError('Root de bundles fuera del almacenamiento interno.')
    return root


def _path(root, name):
    if not isinstance(name,str) or not re.fullmatch(r'[A-Za-z0-9_./-]{1,180}',name):
        raise ValueError('Ruta relativa de bundle inválida.')
    relative = PurePosixPath(name)
    if relative.is_absolute() or '..' in relative.parts or relative.as_posix() != name:
        raise ValueError('Ruta de bundle no confinada.')
    path = (root/name).resolve()
    if not path.is_relative_to(root.resolve()): raise ValueError('Enlace de bundle fuera de su directorio.')
    return path


def _read(path, limit):
    if not path.is_file() or path.stat().st_size > limit: raise ValueError('Archivo ausente o superior al presupuesto.')
    with path.open('rb') as stream: content = stream.read(limit+1)
    if len(content)>limit: raise ValueError('Archivo superior al presupuesto.')
    return content


def _png_content(root, item):
    content = _read(_path(root,item['path']),PNG_LIMIT)
    if len(content) != item['bytes'] or _digest(content) != item['sha256']:
        raise ValueError('PNG cartográfico cambiado o incompleto.')
    return content


def _decode_png(content,item,*,empty=False):
    try:
        with Image.open(io.BytesIO(content)) as image:
            if image.format != 'PNG' or image.mode != 'RGBA' or list(image.size) != item['size'] or image.width*image.height>40_000_000:
                raise ValueError('PNG cartográfico con modo o grid inesperado.')
            image.load()
            if empty:
                with image.getchannel('A') as alpha:
                    if alpha.getextrema() != (0,0):raise ValueError('Una capa sin cobertura debe permanecer transparente.')
            return image.copy()
    except (OSError,Image.DecompressionBombError) as error: raise ValueError('PNG cartográfico inválido.') from error


def _png(root,item,*,empty=False):
    with _decode_png(_png_content(root,item),item,empty=empty):pass


class BundleFrames:
    """Private lazy tiles; callers provide a source frame, not a second clock.

    Only metadata and thumbnail are verified in the constructor. Every tile
    request hashes current bytes even on a warm cache; returned images belong
    to the caller and never expose mutable cached pixels.
    """
    def __init__(self,record,*,cache_bytes=32*1024*1024,cache=None):
        from studio_cache import MediaCache
        if type(cache_bytes) is not int or not 0<=cache_bytes<=320_000_000:
            raise ValueError('Presupuesto de tiles fuera de 0–320 MB.')
        self.record=copy.deepcopy(record)
        self.manifest=read_bundle(self.record,verify_tiles=False)
        self.root=Path(self.record['manifest_path']).resolve().parent
        self.starts=[span['start_frame'] for span in self.manifest['intervals']]
        self.cache=cache if cache is not None else MediaCache(cache_bytes)
        self.owns_cache=cache is None;self.closed=False

    def at(self,source_frame,layer_ids=('continent','galapagos')):
        if self.closed:raise ValueError('Decoder de bundle cerrado.')
        if type(source_frame) is not int or not 0<=source_frame<self.manifest['total_frames']:
            raise ValueError('Fotograma fuente fuera del bundle.')
        if (not isinstance(layer_ids,(list,tuple)) or not layer_ids or any(not isinstance(lid,str) for lid in layer_ids)
                or len(set(layer_ids))!=len(layer_ids) or set(layer_ids)-(set(self.manifest['layers'])|set(self.manifest.get('auxiliaries',{})))):
            raise ValueError('Canales cartográficos inválidos.')
        if self.root.resolve()!=self.root or not self.root.is_relative_to(_root()):
            raise ValueError('Directorio de bundle cambiado o fuera del almacenamiento interno.')
        content=_read(_path(self.root,'manifest.json'),MANIFEST_LIMIT)
        if _digest(content)!=self.record['manifest_sha256']:raise ValueError('Manifiesto cartográfico cambiado.')
        position=bisect_right(self.starts,source_frame)-1
        span=self.manifest['intervals'][position]
        index=span['source_index'];images={}
        try:
            for lid in layer_ids:
                item=(self.manifest['auxiliaries'][lid] if lid in self.manifest.get('auxiliaries',{})
                      else self.manifest['observations'][position]['layers'][lid])
                content=_png_content(self.root,item)
                key=('map-tile',self.record['manifest_sha256'],'static' if lid in self.manifest.get('auxiliaries',{}) else index,lid,item['sha256'])
                image=self.cache.image(key)
                if image is None:
                    image=_decode_png(content,item,empty=item.get('state','covered')!='covered')
                    try:self.cache.remember_image(key,image)
                    except Exception:image.close();raise
                images[lid]=image
            from studio_temporal import bundle_observation
            return {'images':images,'observation':bundle_observation(self.manifest,source_frame,starts=self.starts),
                    'coverage':{lid:self.manifest['observations'][position]['layers'][lid]['state'] for lid in layer_ids if lid in self.manifest['layers']}}
        except Exception:
            for image in images.values():image.close()
            raise

    def close(self):
        if self.owns_cache:self.cache.clear()
        self.closed=True

    def __enter__(self):return self
    def __exit__(self,*args):self.close()


def _artifact(item, path, size):
    if (not isinstance(item,dict) or item.get('path') != path or item.get('size') != size
            or type(item.get('bytes')) is not int or not 0<item['bytes']<=PNG_LIMIT
            or not re.fullmatch('[0-9a-f]{64}',str(item.get('sha256'))) or item.get('mode')!='RGBA'):
        raise ValueError('Descriptor PNG cartográfico inválido.')


def _schema(manifest):
    from maqueta import GALAPAGOS_BOX
    if manifest.get('source_scope') not in (None,'canonical_geography'):
        raise ValueError('Ámbito de fuentes cartográficas desconocido.')
    if manifest.get('source_scope')=='canonical_geography':
        from studio_temporal import _hash
        binding=manifest['geographic_binding']
        if (manifest['scientific_identity']!=_hash(binding) or manifest['scientific_revision']!=_hash([binding,manifest['source_records']])
                or binding['basemap_included'] is not False or binding['bbox']!=manifest['region']):
            raise ValueError('Bundle sin su vínculo geográfico verificable.')
    total=manifest.get('total_frames')
    if (type(manifest.get('version')) is not int or manifest['version']!=2 or manifest.get('representation')!=REPRESENTATION
            or type(manifest.get('fps')) is not int or manifest['fps']!=30
            or type(total) is not int or not 1<=total<=216000 or type(manifest.get('duration')) not in (int,float) or manifest.get('duration')!=total/30
            or manifest.get('state')!='ready' or manifest.get('temporal_interpolation') is not False):
        raise ValueError('Reloj o representación de bundle incompatible.')
    for key in ('scientific_revision','scientific_identity'):
        if not re.fullmatch('[0-9a-f]{64}',str(manifest.get(key))): raise ValueError('Identidad científica inválida.')
    settings=manifest['cartographic_settings']
    if any(manifest.get(k)!=settings.get(k) for k in ('source','variable','units')) or manifest['region']!=settings['bbox']:
        raise ValueError('Descripción de bundle distinta de sus parámetros.')
    layers=manifest['layers']
    if set(layers)!={'continent','galapagos'}: raise ValueError('La pareja cartográfica está incompleta.')
    for lid,grid in layers.items():
        box=grid['bbox']
        if (not isinstance(box,list) or len(box)!=4 or any(type(v) not in (int,float) or not math.isfinite(v) for v in box)
                or not box[0]<box[2] or not box[1]<box[3]): raise ValueError('BBox inválido.')
        size=_resolution(grid['size'],box)
        if (grid['id']!=lid or grid['crs']!='EPSG:4326' or grid['transform']!=list(from_bounds(*box,*size))
                or box!=(manifest['region'] if lid=='continent' else list(GALAPAGOS_BOX))):
            raise ValueError('Grid cartográfico cambiado.')
    if sum(math.prod(g['size']) for g in layers.values())>80_000_000: raise ValueError('Pareja superior a 80 MP.')
    records,intervals,observations=manifest['source_records'],manifest['intervals'],manifest['observations']
    if not isinstance(records,list) or not records or not isinstance(intervals,list) or not intervals or len(intervals)!=len(observations):
        raise ValueError('Bundle sin correspondencia de observaciones.')
    selection=manifest.get('observation_selection')
    if selection is None:
        indices=list(range(len(records)))
    else:
        if (not isinstance(selection,dict) or set(selection)!={'mode','source_index'}
                or selection['mode']!='single_observation' or type(selection['source_index']) is not int
                or not 0<=selection['source_index']<len(records)):
            raise ValueError('Selección de observación inválida.')
        indices=[selection['source_index']]
    if len(indices)!=len(observations):raise ValueError('La selección no coincide con las observaciones.')
    previous=None
    for source in records:
        date=dt.date.fromisoformat(source['date'])
        if (previous is not None and date<=previous or type(source['band']) is not int or source['band']<1
                or not isinstance(source['file'],str) or not re.fullmatch('[0-9a-f]{64}',str(source.get('sha256')))):
            raise ValueError('Registro científico completo inválido.')
        previous=date
    cursor=0;previous=None
    for i,(source_index,span,obs) in enumerate(zip(indices,intervals,observations)):
        source=records[source_index]
        date=dt.date.fromisoformat(source['date'])
        if (type(span['source_index']) is not int or span['source_index']!=source_index or type(obs['source_index']) is not int or obs['source_index']!=source_index
                or source['date']!=span['date'] or source['date']!=obs['date'] or previous is not None and date<=previous
                or type(span['start_frame']) is not int or span['start_frame']!=cursor
                or type(span['end_frame']) is not int or not cursor<span['end_frame']<=total
                or type(source['band']) is not int or source['band']<1 or not isinstance(source['file'],str)
                or not re.fullmatch('[0-9a-f]{64}',str(source.get('sha256'))) or set(obs['layers'])!=set(layers)):
            raise ValueError('Fuente, fecha, banda o intervalo incoherentes.')
        for lid,item in obs['layers'].items():
            _artifact(item,f'observations/{i:06d}/{lid}.png',layers[lid]['size'])
            if (item.get('state') not in ('covered','no_coverage','disabled') or type(item.get('data_pixels')) is not int
                    or not 0<=item['data_pixels']<=math.prod(item['size']) or (item['state']=='covered')!=(item['data_pixels']>0)
                    or (item['state']=='disabled') != (lid=='galapagos' and not settings.get('show_galapagos',True))):
                raise ValueError('Estado de cobertura cartográfica inválido.')
        cursor=span['end_frame'];previous=date
    if cursor!=total: raise ValueError('Calendario incompleto.')
    _artifact(manifest['thumbnail'],'thumbnail.png',[480,320])
    auxiliaries=manifest.get('auxiliaries',{})
    if auxiliaries:
        if set(auxiliaries)!={'legend_static'}:raise ValueError('Auxiliares cartográficos desconocidos.')
        legend=auxiliaries['legend_static'];size=legend['size']
        if (not isinstance(size,list) or len(size)!=2 or any(type(n) is not int or not 1<=n<=8192 for n in size)
                or math.prod(size)>40_000_000 or legend.get('spec')!=legend_spec(settings)):
            raise ValueError('La leyenda no corresponde a los valores y unidades del mapa.')
        _artifact(legend,'legend.png',size)


def read_bundle(record, *, verify_tiles=True):
    """Verify the sealed package one PNG at a time, without loading any raster."""
    if not isinstance(record,dict) or record.get('kind')!='temporal_map' or record.get('representation')!=REPRESENTATION:
        raise ValueError('Header privado de bundle inválido.')
    if not isinstance(record.get('manifest_path'),str): raise ValueError('Ruta de manifiesto inválida.')
    path=Path(record['manifest_path']).resolve();root=path.parent
    if path.name!='manifest.json' or not root.is_relative_to(_root()) or root==_root():
        raise ValueError('Manifiesto fuera del almacenamiento interno.')
    content=_read(path,MANIFEST_LIMIT)
    if _digest(content)!=record.get('manifest_sha256'): raise ValueError('Manifiesto cartográfico cambiado.')
    def pairs(items):
        result={}
        for key,value in items:
            if key in result: raise ValueError('Clave JSON duplicada.')
            result[key]=value
        return result
    def nonfinite(value): raise ValueError('Manifiesto no finito: '+value)
    manifest=json.loads(content.decode('utf-8'),object_pairs_hook=pairs,parse_constant=nonfinite)
    try:
        if not isinstance(manifest,dict): raise ValueError('El manifiesto debe ser un objeto JSON.')
        _schema(manifest)
        if any(record.get(k)!=manifest[k] for k in ('scientific_revision','scientific_identity','fps','total_frames','duration','variable','units','state')):
            raise ValueError('Header y manifiesto no coinciden.')
        if (record.get('period')!=[manifest['observations'][0]['date'],manifest['observations'][-1]['date']]
                or any(record.get(k)!=manifest[k] for k in ('source','citation','generated_at','thumbnail'))
                or record.get('layers')!={lid:{'name':g['name'],'size':g['size']} for lid,g in manifest['layers'].items()}):
            raise ValueError('Metadata compacta distinta del bundle.')
        if record.get('source_dataset')!='sources.'+manifest['scientific_revision']:
            raise ValueError('Referencia de procedencia inválida.')
        size=len(content)+manifest['thumbnail']['bytes']+sum(item['bytes'] for obs in manifest['observations'] for item in obs['layers'].values())+sum(item['bytes'] for item in manifest.get('auxiliaries',{}).values())
        if size>BUNDLE_LIMIT or record.get('bytes')!=size: raise ValueError('Bundle superior al presupuesto o tamaño incorrecto.')
        # Validate every relative path even when the future decoder requests metadata only.
        for obs in manifest['observations']:
            for item in obs['layers'].values():
                _path(root,item['path'])
                if verify_tiles: _png(root,item,empty=item['state']!='covered')
        _png(root,manifest['thumbnail'])
        for item in manifest.get('auxiliaries',{}).values():
            _path(root,item['path'])
            if verify_tiles:_png(root,item)
    except (KeyError,TypeError,IndexError,AttributeError) as error: raise ValueError('Estructura de bundle incompleta.') from error
    return manifest


def prepare_geographic_bundle(project,duration=3.):
    """Canonical GeoTIFF provider adapter for the existing sealed RGBA contract.

    The primary channel is a universal region. The Ecuador inset is explicitly
    disabled, never fabricated. Decoder, calendar, legend and renderer are shared.
    """
    from studio_sig_layers import workspace_for
    from studio_sig_raster import verify_source,compatible,settings,representation,verify_series_binding
    from studio_temporal import _hash
    import numpy as np
    state=workspace_for(project);time=state.get('raster_time')
    if not time:raise ValueError('Configura y revisa las fechas geográficas antes de preparar la serie.')
    if type(duration) not in (int,float) or not math.isfinite(duration) or not .1<=duration<=120:raise ValueError('Duración de comprobación: de 0,1 a 120 segundos.')
    sources=[project['studio']['geography']['sources'][state['layers'][lid]['source_id']] for lid in time['layers']]
    compatible(sources)
    opacities=[state['layers'][lid]['style']['opacity'] for lid in time['layers']]
    if any(v!=opacities[0] for v in opacities):raise ValueError('La serie utiliza una opacidad común. Iguala la opacidad de sus fechas antes de enviarla; no se alterarán sus datos.')
    from studio_sig_timelapse import output_frame,gaps
    frame=output_frame(project);box=frame['bbox'];scale=settings(sources)
    if scale is None:raise ValueError('Ambas fechas carecen de datos finitos. No se puede preparar una leyenda numérica verificable.')
    binding={'sources':[{'id':s['id'],'metadata_sha256':_hash(s)} for s in sources],
        'bbox':box,'scale':scale,'opacity':opacities[0],'method':'GDAL nearest, finite native mask, RGBA','basemap_included':False}
    if 'duration' in time:binding.update(output_profile=copy.deepcopy(project['studio']['output_profile']),cadence=time.get('cadence','irregular'))
    records=[{'file':s['path'],'date':s['date'],'band':s['raster']['band'],'sha256':s['sha256'],'source_url':s['provenance'].get('url','')} for s in sources]
    identity=_hash(binding);revision=_hash([binding,records]);counts=frame_counts(len(sources),duration);total=sum(counts)
    cartography={**scale,'source':'local','variable':sources[0]['variable'],'bbox':box,'show_galapagos':False,
        'citation':' | '.join(dict.fromkeys(s['provenance']['citation'] for s in sources)),'source_url':None}
    destination=_root()/uuid.uuid4().hex;destination.mkdir(parents=True)
    used=0
    def save(image,name):
        nonlocal used
        path=_path(destination,name);path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as stream:image.save(stream,format='PNG')
        content=_read(path,PNG_LIMIT);used+=len(content)
        if used>BUNDLE_LIMIT:raise ValueError('Bundle superior al presupuesto.')
        return {'path':name,'sha256':_digest(content),'bytes':len(content),'size':list(image.size),'mode':'RGBA'}
    from maqueta import GALAPAGOS_BOX
    observations=[];intervals=[];cursor=0;specs={}
    with Image.new('RGBA',(480,320)) as thumbnail:
        for index,(source,count) in enumerate(zip(sources,counts)):
            image,_=representation(source,scale,size=max(frame['map_width'],frame['map_height']),box=box)
            try:
                if not specs:
                    for lid,bbox,size in [('continent',box,image.size),('galapagos',list(GALAPAGOS_BOX),(34,37))]:
                        specs[lid]={'id':lid,'name':'Región SIG · '+source['variable'] if lid=='continent' else 'Inset desactivado',
                            'bbox':bbox,'crs':'EPSG:4326','size':list(size),'transform':list(from_bounds(*bbox,*size))}
                pixels=int((np.asarray(image.getchannel('A'))>0).sum());tiles={}
                tile=save(image,f'observations/{index:06d}/continent.png')
                tile.update(state='covered' if pixels else 'no_coverage',data_pixels=pixels,borders_painted=False,provinces_painted=False);tiles['continent']=tile
                with Image.new('RGBA',(34,37)) as inset:
                    tile=save(inset,f'observations/{index:06d}/galapagos.png');tile.update(state='disabled',data_pixels=0,borders_painted=False,provinces_painted=False);tiles['galapagos']=tile
                if index==0:
                    with image.copy() as thumb:
                        thumb.thumbnail((480,320));thumbnail.alpha_composite(thumb,((480-thumb.width)//2,(320-thumb.height)//2))
                observations.append({'source_index':index,'date':source['date'],'native_crs':source['native_crs'],'layers':tiles})
                intervals.append({'date':source['date'],'source_index':index,'start_frame':cursor,'end_frame':cursor+count});cursor+=count
            finally:image.close()
        thumb=save(thumbnail,'thumbnail.png')
    with paint_legend(cartography) as legend:
        auxiliary=save(legend,'legend.png');auxiliary['spec']=legend_spec(cartography)
    manifest={'version':2,'representation':REPRESENTATION,'state':'ready','renderer':'shared RGBA colorizer / GDAL nearest',
        'source_scope':'canonical_geography','geographic_binding':binding,'scientific_revision':revision,'scientific_identity':identity,
        'source':'local','variable':sources[0]['variable'],'units':sources[0]['units'],'region':box,'citation':cartography['citation'],
        'source_url':None,'cartographic_settings':cartography,'layers':specs,'source_records':records,'observations':observations,'intervals':intervals,
        'fps':30,'total_frames':total,'duration':total/30,'generated_at':dt.datetime.now(dt.timezone.utc).isoformat(),
        'temporal_interpolation':False,'nodata':{'override':None,'rule':'native mask AND finite samples'},
        'rules':{'alpha':'native mask AND finite samples'},'warnings':['Inset Ecuador desactivado; región universal de la vista SIG.',
            'Igual tiempo por observación real; sin interpolación ni relleno de fechas.']+
            [f"Intervalos ausentes: {gap['missing_intervals']} entre {gap['after']} y {gap['before']}." for gap in gaps([s['date'] for s in sources],time.get('cadence','irregular'))],
        'thumbnail':thumb,'auxiliaries':{'legend_static':auxiliary}}
    _schema(manifest);verify_series_binding(project,manifest);content=_bytes(manifest)
    with (destination/'manifest.json').open('xb') as stream:stream.write(content)
    record={'kind':'temporal_map','representation':REPRESENTATION,'name':'Serie SIG '+sources[0]['variable']+' · '+sources[0]['date']+' — '+sources[-1]['date'],
        'manifest_path':str(destination/'manifest.json'),'manifest_sha256':_digest(content),'bytes':used+len(content),
        'source_dataset':'sources.'+revision,'period':[sources[0]['date'],sources[-1]['date']],
        'layers':{lid:{'name':g['name'],'size':g['size']} for lid,g in specs.items()},
        **{k:manifest[k] for k in ('source','citation','generated_at','thumbnail','scientific_revision','scientific_identity','fps','total_frames','duration','variable','units','state')}}
    read_bundle(record);verify_series_binding(project,manifest);return record


def observed_native_crs(observation,source,provider):
    """Recover CHIRPS CRS omitted by the legacy loader, from source metadata."""
    native=observation.get('native_crs')
    if native is not None or provider!='chirps':return native
    import gzip
    from rasterio.io import MemoryFile
    with MemoryFile(gzip.decompress(Path(source['file']).read_bytes())) as memory:
        with memory.open() as raster:
            if not raster.crs:raise ValueError('La observación CHIRPS no declara su CRS nativo.')
            return str(raster.crs)


def prepare_bundle(project,duration,*,continent_size=None,galapagos_size=None,progress=None,cancelled=None,source_index=None):
    """Paint observations through the existing painter; return only a verified header."""
    def check():
        if cancelled and cancelled(): raise InterruptedError('Bundle cancelado; proyecto activo intacto.')
    check()
    if type(duration) not in (int,float) or not math.isfinite(duration) or not 0<duration<=7200:
        raise ValueError('Duración del bundle: más de cero y hasta 7200 segundos.')
    snapshot=restored_snapshot(project)
    if snapshot is None:raise ValueError('Revisión científica ausente.')
    records=snapshot['source_records']
    if source_index is not None and (type(source_index) is not int or not 0<=source_index<len(records)):
        raise ValueError('Índice de observación fuera de la revisión científica.')
    indices=list(range(len(records))) if source_index is None else [source_index]
    painter=MapLayerPainter(project,continent_size=continent_size,galapagos_size=galapagos_size)
    settings=painter.cartographic_settings
    counts=frame_counts(len(indices),duration)
    if any(n<1 for n in counts): raise ValueError('Cada observación necesita al menos un fotograma.')
    total=sum(counts)
    if not 1<=total<=216000: raise ValueError('Duración de bundle fuera del límite.')
    root=_root();root.mkdir(parents=True,exist_ok=True)
    destination=root/uuid.uuid4().hex;destination.mkdir()
    used=0
    def save(image,name):
        nonlocal used
        check()
        if shutil.disk_usage(destination).free < image.width*image.height*4+MANIFEST_LIMIT:
            raise ValueError('Espacio libre insuficiente para preparar el bundle.')
        path=_path(destination,name);path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as stream: image.save(stream,format='PNG')
        content=_read(path,PNG_LIMIT);used+=len(content)
        if used>BUNDLE_LIMIT: raise ValueError('Bundle superior al presupuesto.')
        return {'path':name,'sha256':_digest(content),'bytes':len(content),'size':list(image.size),'mode':'RGBA'}
    observations=[];intervals=[];cursor=0;rules=None;warnings=set();thumbnail=Image.new('RGBA',(480,320))
    try:
        for index,(scientific_index,count) in enumerate(zip(indices,counts)):
            source=records[scientific_index]
            check()
            if progress: progress(index,len(indices),'Pintando '+source['date'])
            pair=painter.render_observation(scientific_index)
            try:
                observation=pair['observation']
                tiles={}
                for lid,tile in pair['layers'].items():
                    item=save(tile['image'],f'observations/{index:06d}/{lid}.png')
                    item.update({k:tile[k] for k in ('state','data_pixels','borders_painted','provinces_painted')})
                    tiles[lid]=item
                    if index==0:
                        with tile['image'].copy() as preview:
                            preview.thumbnail((230,300))
                            thumbnail.alpha_composite(preview,((0 if lid=='continent' else 240)+(240-preview.width)//2,(320-preview.height)//2))
                observations.append({'source_index':scientific_index,'date':observation['date'],
                    'native_crs':observed_native_crs(observation,source,settings['source']),'layers':tiles})
                intervals.append({'date':source['date'],'source_index':scientific_index,'start_frame':cursor,'end_frame':cursor+count})
                cursor+=count;rules=pair['rules'];warnings.update(pair['warnings'])
            finally:
                for tile in pair['layers'].values(): tile['image'].close()
            if progress: progress(index+1,len(indices),'Observación verificada '+source['date'])
        check();verify_sources(project,snapshot,cancelled=cancelled)
        thumb=save(thumbnail,'thumbnail.png')
    finally: thumbnail.close()
    with paint_legend(settings) as image:
        legend=save(image,'legend.png');legend['spec']=legend_spec(settings)
    manifest={'version':2,'representation':REPRESENTATION,'state':'ready','renderer':'maqueta shared MapLayerPainter',
        'scientific_revision':project['project_meta']['scientific_revision'],'scientific_identity':snapshot['scientific_identity'],
        'source':settings['source'],'variable':settings['variable'],'units':settings['units'],'region':settings['bbox'],
        'citation':settings.get('citation',''),'source_url':settings.get('source_url'),'cartographic_settings':settings,
        'layers':painter.layer_specs,'source_records':records,'observations':observations,'intervals':intervals,
        'fps':30,'total_frames':total,'duration':total/30,'generated_at':dt.datetime.now(dt.timezone.utc).isoformat(),
        'temporal_interpolation':False,'nodata':{'override':settings.get('nodata'),'rule':rules['alpha']},
        'rules':rules,'warnings':sorted(warnings),'thumbnail':thumb,'auxiliaries':{'legend_static':legend}}
    if source_index is not None:manifest['observation_selection']={'mode':'single_observation','source_index':source_index}
    _schema(manifest);content=_bytes(manifest)
    if len(content)>MANIFEST_LIMIT or used+len(content)>BUNDLE_LIMIT: raise ValueError('Manifiesto o bundle superior al presupuesto.')
    check()
    with (destination/'manifest.json').open('xb') as stream: stream.write(content)
    record={'kind':'temporal_map','representation':REPRESENTATION,'name':('Observación RGBA ' if source_index is not None else 'Mapa RGBA ')+settings['variable']+' · '+observations[0]['date']+' — '+observations[-1]['date'],
        'manifest_path':str(destination/'manifest.json'),'manifest_sha256':_digest(content),'bytes':used+len(content),
        'source_dataset':'sources.'+manifest['scientific_revision'],
        'period':[observations[0]['date'],observations[-1]['date']],
        'layers':{lid:{'name':g['name'],'size':g['size']} for lid,g in manifest['layers'].items()},
        **{k:manifest[k] for k in ('source','citation','generated_at','thumbnail')},
        **{k:manifest[k] for k in ('scientific_revision','scientific_identity','fps','total_frames','duration','variable','units','state')}}
    if progress: progress(len(indices),len(indices),'Verificando y sellando bundle privado')
    check();read_bundle(record);verify_sources(project,snapshot,cancelled=cancelled);check()
    return record
