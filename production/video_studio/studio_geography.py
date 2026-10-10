"""BYOD GeoJSON polygon views in the existing Studio document and renderer.

Original bytes and attributes remain external and immutable. These angular
views are presentation products, never statistical domains or measurements.
"""
import copy
import hashlib
import io
import json
import math
from pathlib import Path
import re
from urllib.parse import urlsplit
import uuid
from collections import OrderedDict
import pickle
from threading import RLock
import numpy as np
from PIL import Image
from shapely.geometry import shape
from shapely.errors import GEOSException
from rasterio.features import geometry_mask
from rasterio.transform import from_bounds
from model import STORE

ROOT=STORE/'geography'
SOURCE_LIMIT=8*1024*1024
REGION_LIMIT=5000
COORDINATE_LIMIT=250_000
CRS='OGC:CRS84'
METHOD='angular_lonlat_pixel_center_v1'
REPRESENTATION_REVISION='geojson-features-v2'
SOURCE_CACHE_BYTES=64*1024*1024
SOURCE_CACHE_ENTRIES=8
_SOURCE_CACHE=OrderedDict()
_SOURCE_CACHE_LOCK=RLock()


def clear_source_cache():
    """Discard transient representations only; never touch source files."""
    with _SOURCE_CACHE_LOCK:_SOURCE_CACHE.clear()


def _hash(content):return hashlib.sha256(content).hexdigest()


def _id(prefix,value):
    return prefix+'.'+_hash(json.dumps(value,sort_keys=True,ensure_ascii=False,allow_nan=False).encode('utf-8'))


def _provenance(value):
    if not isinstance(value,dict) or set(value)!={'citation','license','url'}:
        raise ValueError('Registra citación, licencia/condiciones y URL pública de la fuente.')
    if any(not isinstance(v,str) or len(v)>1000 for v in value.values()):raise ValueError('Metadata de fuente inválida.')
    if not value['citation'].strip() or not value['license'].strip():raise ValueError('La procedencia y las condiciones de uso son obligatorias.')
    if value['url']:
        url=urlsplit(value['url'])
        if url.scheme not in ('https','http') or not url.hostname or url.username or url.password or url.query or url.fragment:
            raise ValueError('Usa una URL pública sin credenciales, query ni fragmentos; no se guardan tokens en el proyecto.')
    return copy.deepcopy(value)


def parse_geojson(content):
    if not isinstance(content,bytes) or not 0<len(content)<=SOURCE_LIMIT:raise ValueError('GeoJSON: archivo vacío o superior a 8 MiB.')
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise ValueError('GeoJSON contiene claves duplicadas.')
            result[key]=value
        return result
    def nonfinite(value):raise ValueError('GeoJSON contiene números no finitos.')
    try:
        document=json.loads(content.decode('utf-8'),object_pairs_hook=pairs,parse_constant=nonfinite)
    except (UnicodeError,json.JSONDecodeError,RecursionError) as error:raise ValueError('GeoJSON UTF-8/JSON inválido.') from error
    try:json.dumps(document,allow_nan=False)
    except (ValueError,TypeError,RecursionError) as error:raise ValueError('GeoJSON y metadata deben ser JSON finito.') from error
    if not isinstance(document,dict) or 'crs' in document:raise ValueError('Solo GeoJSON RFC7946: lon/lat WGS84 sin un CRS legacy.')
    kind=document.get('type')
    features=document.get('features') if kind=='FeatureCollection' else [document] if kind=='Feature' else None
    if not isinstance(features,list) or not 0<len(features)<=REGION_LIMIT:raise ValueError('Importa Feature o FeatureCollection de hasta 5000 regiones.')
    identifiers=set();points=0;bounds=[]
    for feature in features:
        if not isinstance(feature,dict) or feature.get('type')!='Feature' or 'crs' in feature:
            raise ValueError('Feature GeoJSON inválido o CRS no soportado.')
        if 'properties' not in feature or feature['properties'] is not None and not isinstance(feature['properties'],dict):
            raise ValueError('properties debe ser un objeto JSON o null.')
        if 'id' in feature:
            fid=feature['id']
            if type(fid) not in (str,int,float) or isinstance(fid,str) and len(fid)>180 or isinstance(fid,(int,float)) and not math.isfinite(fid):
                raise ValueError('ID GeoJSON inválido.')
            key=('string',fid) if isinstance(fid,str) else ('number',fid)
            if key in identifiers:raise ValueError('IDs GeoJSON duplicados.')
            identifiers.add(key)
        geometry=feature.get('geometry')
        if not isinstance(geometry,dict) or 'crs' in geometry or geometry.get('type') not in ('Point','MultiPoint','LineString','MultiLineString','Polygon','MultiPolygon'):
            raise ValueError('Importa puntos, líneas o polígonos 2D; GeometryCollection no está soportado.')
        def positions(value):
            if not isinstance(value,list) or not value:raise ValueError('Coordenadas ausentes.')
            if all(not isinstance(v,list) for v in value):
                if len(value)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in value):
                    raise ValueError('Se requieren posiciones 2D finitas, sin coordenada Z ni booleanos.')
                yield value
            else:
                for child in value:yield from positions(child)
        coordinates=list(positions(geometry.get('coordinates')));points+=len(coordinates)
        if points>COORDINATE_LIMIT:raise ValueError('GeoJSON superior a 250000 posiciones.')
        if any(not -180<=p[0]<=180 or not -90<p[1]<90 for p in coordinates):
            raise ValueError('Coordenadas fuera de lon/lat WGS84 o polos no soportados; comprueba CRS y ejes.')
        polygons=[geometry.get('coordinates')] if geometry['type']=='Polygon' else geometry.get('coordinates') if geometry['type']=='MultiPolygon' else []
        for polygon in polygons:
            if not isinstance(polygon,list) or not polygon:raise ValueError('Anillos ausentes.')
            for ring in polygon:
                if not isinstance(ring,list) or len(ring)<4 or ring[0]!=ring[-1]:raise ValueError('Anillo debe estar cerrado y contener al menos cuatro posiciones.')
                for point in ring:
                    if (not isinstance(point,list) or len(point)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in point)
                            or not -180<=point[0]<=180 or not -90<=point[1]<=90):
                        raise ValueError('Se requieren posiciones 2D lon/lat WGS84 finitas, sin swap de ejes.')
                    if abs(point[1])==90:raise ValueError('Polos no soportados en esta vista angular.')
                if any(abs(a[0]-b[0])>180 for a,b in zip(ring,ring[1:])):raise ValueError('Cruce del antimeridiano no soportado en este corte.')
        try:geometry_shape=shape(geometry)
        except (TypeError,ValueError,GEOSException) as error:raise ValueError('Geometría GeoJSON inválida.') from error
        if (geometry_shape.is_empty or not geometry_shape.is_valid or
                geometry['type'] in ('Polygon','MultiPolygon') and geometry_shape.area<=0 or
                geometry['type'] in ('LineString','MultiLineString') and geometry_shape.length<=0):
            raise ValueError('Geometría inválida, vacía o degenerada; no se repara automáticamente.')
        lines=[geometry['coordinates']] if geometry['type']=='LineString' else geometry['coordinates'] if geometry['type']=='MultiLineString' else []
        if any(abs(a[0]-b[0])>180 for line in lines for a,b in zip(line,line[1:])):
            raise ValueError('Cruce del antimeridiano no soportado.')
        if geometry_shape.bounds[2]-geometry_shape.bounds[0]>180:raise ValueError('Extensión angular superior a 180 grados no soportada.')
        box=list(geometry_shape.bounds);bounds.append(box)
        for item in (feature,geometry):
            if 'bbox' in item and (not isinstance(item['bbox'],list) or len(item['bbox'])!=4
                    or any(type(v) not in (int,float) or not math.isfinite(v) for v in item['bbox']) or item['bbox']!=box):
                raise ValueError('BBox declarado no coincide con la geometría 2D.')
    combined=[min(b[0] for b in bounds),min(b[1] for b in bounds),max(b[2] for b in bounds),max(b[3] for b in bounds)]
    if kind=='FeatureCollection' and 'bbox' in document and (not isinstance(document['bbox'],list) or len(document['bbox'])!=4
            or any(type(v) not in (int,float) or not math.isfinite(v) for v in document['bbox']) or document['bbox']!=combined):
        raise ValueError('BBox de colección distinto de sus geometrías.')
    return document


def _features(document):return document['features'] if document['type']=='FeatureCollection' else [document]


def _region(source_id,index,feature):
    return {'id':_id('region',[source_id,index]),'source_id':source_id,'feature_index':index,
        'feature_id':copy.deepcopy(feature.get('id')),'bbox':list(shape(feature['geometry']).bounds)}


def _registry(project):
    return project['studio'].get('geography',{'version':1,'sources':{},'regions':{},'views':{}})


def _verified_source(record):
    if (not isinstance(record,dict) or record.get('native_crs')!=CRS or type(record.get('bytes')) is not int
            or not 0<record['bytes']<=SOURCE_LIMIT or not re.fullmatch('[0-9a-f]{64}',str(record.get('sha256')))):
        raise ValueError('Referencia geográfica inválida.')
    _provenance(record.get('provenance'))
    if not isinstance(record.get('name'),str) or len(record['name'])>180:raise ValueError('Nombre de fuente inválido.')
    expected=(ROOT/'sources'/ (record['sha256']+'.geojson')).resolve()
    path=Path(record.get('path','')).resolve()
    if path!=expected or not expected.is_relative_to(ROOT.resolve()) or not path.is_file() or path.stat().st_size!=record['bytes']:
        raise ValueError('Fuente ausente, cambiada o fuera del almacenamiento geográfico interno.')
    with path.open('rb') as stream:content=stream.read(SOURCE_LIMIT+1)
    if len(content)!=record['bytes'] or _hash(content)!=record['sha256']:raise ValueError('Los bytes GeoJSON originales cambiaron.')
    if 'origin' in record:
        from studio_sig_vector import verify_origin
        verify_origin(record['origin'])
    # Metadata, confinement and every original byte are checked BEFORE cache lookup.
    # Size/mtime alone is not an integrity check. Limits are part of parser revision.
    key=(str(ROOT.resolve()),record['sha256'],REPRESENTATION_REVISION,SOURCE_LIMIT,REGION_LIMIT,COORDINATE_LIMIT)
    with _SOURCE_CACHE_LOCK:
        cached=_SOURCE_CACHE.get(key)
        if cached is not None:
            _SOURCE_CACHE.move_to_end(key)
            return pickle.loads(cached)
    document=parse_geojson(content);sid='source.'+record['sha256']
    regions={}
    for index,feature in enumerate(_features(document)):
        region=_region(sid,index,feature);regions[region['id']]=region
    # Pickle contains only our validated in-memory primitives, never external input.
    # A new copy on each read prevents callers poisoning the shared cache.
    cached=pickle.dumps((document,regions),protocol=5)
    with _SOURCE_CACHE_LOCK:
        if len(cached)<=SOURCE_CACHE_BYTES and SOURCE_CACHE_ENTRIES>0:
            _SOURCE_CACHE[key]=cached;_SOURCE_CACHE.move_to_end(key)
            while len(_SOURCE_CACHE)>SOURCE_CACHE_ENTRIES or sum(map(len,_SOURCE_CACHE.values()))>SOURCE_CACHE_BYTES:
                _SOURCE_CACHE.popitem(last=False)
    return document,regions


def read_source(record):return _verified_source(record)[0]


def validate_geography(studio):
    registry=studio.get('geography')
    if registry is None:return
    if (not isinstance(registry,dict) or type(registry.get('version')) is not int or registry['version']!=1
            or not {'version','sources','regions','views'}<=set(registry)
            or set(registry)-{'version','sources','regions','views','map_workspace'}):
        raise ValueError('Registro geográfico incompatible.')
    if any(not isinstance(registry[k],dict) for k in ('sources','regions','views')):raise ValueError('Registros geográficos deben usar IDs.')
    if len(registry['sources'])>50 or len(registry['regions'])>REGION_LIMIT or len(registry['views'])>100:
        raise ValueError('Registro geográfico superior al presupuesto.')
    expected_regions={};used=0
    for sid,source in registry['sources'].items():
        if not isinstance(source,dict) or sid!='source.'+str(source.get('sha256')) or source.get('id')!=sid:raise ValueError('Identidad de fuente inválida.')
        if source.get('type')=='raster':
            from studio_sig_raster import verify_source
            verify_source(source);used+=source['bytes']
            if used>256*1024*1024:raise ValueError('Fuentes superiores al presupuesto de 256 MiB.')
            for entry in source.get('raster_operation',{}).get('inputs',[]):
                original=registry['sources'].get(entry.get('source_id'))
                if original is None or original.get('sha256')!=entry.get('sha256') or original.get('date')!=entry.get('date'):
                    raise ValueError('Operación ráster sin sus entradas originales.')
            continue
        document,regions=_verified_source(source);used+=source['bytes']
        if 'origin' in source:
            metadata=document.get('ecuador_vivo_import',{})
            if any(metadata.get(key)!=source['origin'][other] for key,other in
                   [('format','format'),('input_sha256','sha256'),('native_crs','native_crs'),('options','options')]):
                raise ValueError('La representación no corresponde al original y su conversión declarada.')
        if used>256*1024*1024:raise ValueError('Fuentes del proyecto superiores a 256 MiB.')
        expected_regions.update(regions)
        if 'operation' in source:
            from studio_sig_vector import validate_operation
            validate_operation(source['operation'],registry)
            if document.get('ecuador_vivo_operation')!=source['operation']:raise ValueError('Los parámetros de la operación cambiaron.')
    if registry['regions']!=expected_regions:raise ValueError('Regiones distintas de sus geometrías originales.')
    for vid,view in registry['views'].items():
        if not isinstance(view,dict) or view.get('id')!=vid or view.get('region_id') not in expected_regions or view.get('display_crs')!=CRS or view.get('method')!=METHOD:
            raise ValueError('Vista geográfica inválida.')
        bbox,size=_view_grid(expected_regions[view['region_id']]['bbox'])
        if view.get('bbox')!=bbox or view.get('size')!=size or vid!=_id('view',[view['region_id'],bbox,size,METHOD]):
            raise ValueError('Grid de vista cambiado.')
        asset=studio['media'].get(view.get('asset_id'))
        if not isinstance(asset,dict) or asset.get('kind')!='image' or asset.get('sha256')!=view.get('image_sha256') or asset.get('size')!=size:
            raise ValueError('Vista sin su asset de imagen verificado.')
    for scene in studio['scenes']:
        vid=scene.get('generation',{}).get('geographic_view_id')
        if vid is not None and vid not in registry['views']:raise ValueError('Escena vinculada a una vista geográfica inexistente.')
    from studio_sig_layers import validate_map_workspace
    validate_map_workspace(registry)


def import_geojson(project,content,name,provenance):
    document=parse_geojson(content);provenance=_provenance(provenance)
    if not isinstance(name,str) or not name.strip() or len(name)>180:raise ValueError('Nombre de archivo inválido.')
    digest=_hash(content);sid='source.'+digest;registry=_registry(project)
    if sid in registry['sources']:
        if registry['sources'][sid]['provenance']!=provenance:raise ValueError('La fuente existente conserva su procedencia; no la sobrescribas en un reintento.')
        read_source(registry['sources'][sid])
        return copy.deepcopy(project),_id('region',[sid,0])
    root=ROOT.resolve();destination=root/'sources'/(digest+'.geojson')
    if not destination.resolve().is_relative_to(root):raise ValueError('Almacenamiento geográfico no confinado.')
    destination.parent.mkdir(parents=True,exist_ok=True)
    try:
        with destination.open('xb') as stream:stream.write(content)
    except FileExistsError:
        with destination.open('rb') as stream:existing=stream.read(SOURCE_LIMIT+1)
        if existing!=content:raise ValueError('El recurso inmutable de origen cambió.')
    result=copy.deepcopy(project);registry=result['studio'].setdefault('geography',copy.deepcopy(registry))
    registry['sources'][sid]={'id':sid,'path':str(destination),'sha256':digest,'bytes':len(content),'name':name,
        'native_crs':CRS,'provenance':provenance}
    for index,feature in enumerate(_features(document)):
        region=_region(sid,index,feature);registry['regions'][region['id']]=region
    validate_geography(result['studio'])
    return result,_id('region',[sid,0])


def region_feature(project,region_id):
    registry=_registry(project);region=registry['regions'].get(region_id)
    if region is None:raise ValueError('Región geográfica desconocida.')
    document=read_source(registry['sources'][region['source_id']]);feature=_features(document)[region['feature_index']]
    if region!=_region(region['source_id'],region['feature_index'],feature):raise ValueError('Identidad de región cambiada.')
    return feature


def _view_grid(box):
    dx,dy=box[2]-box[0],box[3]-box[1]
    box=[max(-180,box[0]-.05*dx),max(-90,box[1]-.05*dy),min(180,box[2]+.05*dx),min(90,box[3]+.05*dy)]
    scale=min(1000/(box[2]-box[0]),800/(box[3]-box[1]))
    size=[max(1,round((box[2]-box[0])*scale)),max(1,round((box[3]-box[1])*scale))]
    return box,size


def render_region(project,region_id):
    from maqueta import projector,iter_polygons,outline_layer
    feature=region_feature(project,region_id)
    if feature['geometry']['type'] not in ('Polygon','MultiPolygon'):
        raise ValueError('La vista editorial G1 admite polígonos. Un punto o línea no sustituye un dominio de estadísticas zonales.')
    box,size=_view_grid(_registry(project)['regions'][region_id]['bbox'])
    width,height=size
    mask=geometry_mask([feature['geometry']],out_shape=(height,width),transform=from_bounds(*box,width,height),invert=True)
    image=Image.new('RGBA',(width,height),'#13bfd1')
    with Image.fromarray(mask.astype(np.uint8)*255) as alpha:image.putalpha(alpha)
    xy=projector(box,width,height)
    rings=[[xy(*point) for point in ring] for polygon in iter_polygons({'features':[feature]}) for ring in polygon]
    with outline_layer((width,height),[(rings,(228,244,249,255),1.5)]) as outline:image.alpha_composite(outline)
    return image,box


def make_view(project,region_id):
    from studio_media import import_asset
    image,box=render_region(project,region_id);size=list(image.size);stream=io.BytesIO()
    try:image.save(stream,format='PNG')
    finally:image.close()
    vid=_id('view',[region_id,box,size,METHOD]);record=import_asset(stream.getvalue(),'geojson-view.png');aid='geographic.'+record['sha256']
    result=copy.deepcopy(project);registry=result['studio']['geography']
    previous=result['studio']['media'].get(aid)
    if previous is not None and previous!=record:raise ValueError('Asset geográfico inmutable cambiado.')
    result['studio']['media'][aid]=record
    registry['views'][vid]={'id':vid,'region_id':region_id,'asset_id':aid,'display_crs':CRS,'method':METHOD,
        'bbox':box,'size':size,'image_sha256':record['sha256']}
    validate_geography(result['studio']);return result,vid


def attach_view(project,view_id,*,duration=6):
    from studio_model import Scene,Element
    from studio_timeline import PreparedTimeline
    from output_profiles import profile_for
    registry=_registry(project);view=registry['views'].get(view_id)
    if view is None:raise ValueError('Guarda una vista real antes de enviarla a Studio.')
    validate_geography(project['studio'])
    result=copy.deepcopy(project);studio=result['studio']
    scene=next((s for s in studio['scenes'] if s.get('generation',{}).get('geographic_view_id')==view_id),None)
    if scene is None:
        profile=profile_for(studio['output_profile']);w,h=profile.width,profile.height
        feature=region_feature(project,view['region_id']);properties=feature.get('properties') or {}
        label=str(properties.get('name') or 'Región '+view['region_id'][-8:])[:140]
        source=registry['sources'][registry['regions'][view['region_id']]['source_id']]
        credit='GeoJSON · WGS84 lon/lat · '+source['provenance']['citation']+' · '+source['provenance']['license']
        if len(credit)>2000:raise ValueError('La procedencia visible excede 2000 caracteres; no se truncará silenciosamente.')
        scene=Scene(id='scene.'+uuid.uuid4().hex,name=label,duration=duration,elements=[
            Element(id='element.'+uuid.uuid4().hex,type='map',name='Mapa vectorial · vista angular',
                transform={'x':w*.06,'y':h*.16,'width':w*.88,'height':h*.67},style={'asset_id':view['asset_id'],'fit':'contain'}).to_dict(),
            Element(id='element.'+uuid.uuid4().hex,type='text',name='Título',
                transform={'x':w*.06,'y':h*.02,'width':w*.88,'height':h*.12},style={'text':label,'font_size':max(8,min(60,round(h*.05)))}).to_dict(),
            Element(id='element.'+uuid.uuid4().hex,type='source',name='Procedencia GeoJSON',
                transform={'x':w*.06,'y':h*.86,'width':w*.88,'height':h*.12},style={'text':credit,'font_size':max(8,min(32,round(h*.025)))}).to_dict()
            ]).to_dict()
        scene['generation']={'geographic_view_id':view_id};studio['scenes'].append(scene)
    studio['timeline']=[sid for sid in studio['timeline'] if next(s for s in studio['scenes'] if s['id']==sid).get('renderer','studio')=='studio']
    if scene['id'] not in studio['timeline']:studio['timeline'].append(scene['id'])
    PreparedTimeline(result);return result,scene['id']


def geographic_receipt(project):
    registry=_registry(project);active=set(project['studio']['timeline']);items=[]
    for scene in project['studio']['scenes']:
        vid=scene.get('generation',{}).get('geographic_view_id')
        if scene['id'] not in active or vid is None:continue
        view=registry['views'][vid];region=registry['regions'][view['region_id']];source=registry['sources'][region['source_id']]
        bound=[e for e in scene['elements'] if e.get('style',{}).get('asset_id')==view['asset_id'] and not e.get('editor_deleted')]
        if not bound:continue
        items.append({'scene_id':scene['id'],**copy.deepcopy(view),'source_id':source['id'],'source_sha256':source['sha256'],
            'native_crs':source['native_crs'],'region_bbox':region['bbox'],'provenance':copy.deepcopy(source['provenance']),
            'transforms':{e['id']:copy.deepcopy(e['transform']) for e in bound},
            'visibility':{e['id']:e.get('visible',True) for e in bound}})
    return items
