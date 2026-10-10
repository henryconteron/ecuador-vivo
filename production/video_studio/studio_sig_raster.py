"""Windowed BYOD rasters in the canonical geography registry.

Native samples own science; bounded nearest-neighbour RGBA owns presentation.
No visual action edits originals, substitutes missing values, or aggregates dates.
"""
import copy,hashlib,io,json,math,re
from datetime import date,datetime,timezone
from pathlib import Path
from collections import OrderedDict
from threading import RLock
import numpy as np
import rasterio
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from rasterio.windows import Window
from rasterio.warp import transform_bounds,transform_geom
from rasterio.features import geometry_mask,geometry_window
from rasterio.errors import WindowError
from PIL import Image
import studio_geography as geo

LIMIT=32*1024*1024
PALETTE=['#effbfd','#80d7df','#16a7c7','#0878aa','#123875']
_CACHE=OrderedDict();_IMAGES=OrderedDict();_LOCK=RLock()


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def _values(dataset,band,window):
    value=dataset.read(band,window=window,masked=True).astype('float64')
    return np.where(np.ma.getmaskarray(value),np.nan,value.data*dataset.scales[band-1]+dataset.offsets[band-1])


def metadata(path,band):
    with rasterio.open(path) as ds:
        if ds.driver!='GTiff' or ds.crs is None:raise ValueError('GeoTIFF requiere un CRS declarado; no se asumirá WGS84.')
        if type(band) is not int or not 1<=band<=ds.count:raise ValueError('Banda ráster fuera del archivo.')
        if ds.width*ds.height>200_000_000:raise ValueError('Ráster superior al presupuesto de 200 millones de celdas.')
        bbox=list(transform_bounds(ds.crs,'EPSG:4326',*ds.bounds,densify_pts=21))
        from studio_sig_layers import _bbox
        _bbox(bbox)
        count=0;minimum=None;maximum=None;total=0.
        # Fixed windows bound memory even when a TIFF stores one enormous strip.
        for y in range(0,ds.height,512):
            for x in range(0,ds.width,512):
                values=_values(ds,band,Window(x,y,min(512,ds.width-x),min(512,ds.height-y)))
                valid=values[np.isfinite(values)]
                if valid.size:
                    count+=int(valid.size);total+=float(valid.sum())
                    minimum=float(valid.min()) if minimum is None else min(minimum,float(valid.min()))
                    maximum=float(valid.max()) if maximum is None else max(maximum,float(valid.max()))
        nodata=ds.nodatavals[band-1]
        return {'native_crs':ds.crs.to_wkt(),'bbox':bbox,'shape':[ds.height,ds.width],
            'transform':list(ds.transform),'band':band,'dtype':ds.dtypes[band-1],
            'nodata':'NaN' if nodata is not None and not math.isfinite(nodata) else nodata,
            'scale':ds.scales[band-1],'offset':ds.offsets[band-1],
            'statistics':{'valid':count,'cells':ds.width*ds.height,'coverage':count/(ds.width*ds.height),
                          'min':minimum,'max':maximum,'mean':total/count if count else None}}


def verify_source(source):
    try:
        if source['type']!='raster' or source['id']!='source.'+source['sha256'] or not re.fullmatch('[a-f0-9]{64}',source['sha256']):raise ValueError('Identidad ráster inválida.')
        path=Path(source['path']).resolve();expected=(geo.ROOT/'rasters'/(source['sha256']+'.tif')).resolve()
        if path!=expected or not path.is_relative_to(geo.ROOT.resolve()) or not path.is_file():raise ValueError('Ráster ausente o no autorizado.')
        if type(source['bytes']) is not int or not 0<source['bytes']<=LIMIT or path.stat().st_size!=source['bytes'] or digest(path)!=source['sha256']:
            raise ValueError('El ráster original cambió; tampoco se utilizará la caché caliente.')
        if not isinstance(source['name'],str) or not 0<len(source['name'])<=180:raise ValueError('Nombre ráster inválido.')
        geo._provenance(source['provenance'])
        if source['date'] is not None:date.fromisoformat(source['date'])
        if source['semantics'] not in ('precipitation','temperature','scalar'):raise ValueError('Significado ráster desconocido.')
        if any(not isinstance(source[k],str) or not 0<len(source[k])<=180 for k in ('variable','units')):raise ValueError('Declara variable y unidad.')
        # Cache may bypass metadata/statistics computation, never authorization or hash.
        with _LOCK:
            cache_key=(str(path),source['sha256'],source['raster']['band'])
            cached=_CACHE.get(cache_key)
            if cached is None:
                cached=metadata(path,source['raster']['band']);_CACHE[cache_key]=cached
                while len(_CACHE)>8:_CACHE.popitem(last=False)
            if source['raster']!=cached or source['native_crs']!=cached['native_crs']:raise ValueError('Metadatos ráster distintos del original.')
        operation=source.get('raster_operation')
        with rasterio.open(path) as ds:declared=ds.tags(ns='ecuador_vivo').get('operation')
        if (json.loads(declared) if declared else None)!=operation:raise ValueError('La receta del resultado difiere de la registrada en su GeoTIFF.')
        if operation is not None:
            if operation.get('tool') not in ('difference','mean','sum') or len(operation.get('inputs',[]))!=2:raise ValueError('Operación ráster inválida.')
        return path
    except (KeyError,TypeError,AttributeError) as error:raise ValueError('Referencia ráster incompleta.') from error


def add_raster(project,content,name,provenance,*,observed_date,variable,units,semantics='scalar',band=1):
    if not isinstance(content,bytes) or not 0<len(content)<=LIMIT:raise ValueError('GeoTIFF vacío o superior a 32 MiB.')
    if observed_date is not None:date.fromisoformat(observed_date)
    sha=hashlib.sha256(content).hexdigest();path=geo.ROOT/'rasters'/(sha+'.tif');path.parent.mkdir(parents=True,exist_ok=True)
    # Inspect before admitting the file/catalog entry. Original external references are forbidden.
    from rasterio.io import MemoryFile
    with MemoryFile(content) as memory:
        with memory.open() as ds:
            if ds.driver!='GTiff' or ds.crs is None:raise ValueError('GeoTIFF sin CRS explícito; no se añadió la capa.')
    try:
        with path.open('xb') as stream:stream.write(content)
    except FileExistsError:
        if digest(path)!=sha:raise ValueError('El original almacenado cambió.')
    meta=metadata(path,band)
    source={'id':'source.'+sha,'type':'raster','sha256':sha,'path':str(path),'bytes':len(content),'name':name,
        'native_crs':meta['native_crs'],'raster':meta,'date':observed_date,'variable':variable,'units':units,
        'semantics':semantics,'provenance':geo._provenance(provenance)}
    with rasterio.open(path) as ds:declared=ds.tags(ns='ecuador_vivo').get('operation')
    if declared:source['raster_operation']=json.loads(declared)
    verify_source(source)
    from studio_sig_layers import ensure_workspace,layer_id,_fit,DEFAULT_STYLE
    candidate=ensure_workspace(project);registry=candidate['studio']['geography'];sid=source['id'];lid=layer_id(sid)
    if sid in registry['sources'] and registry['sources'][sid]!=source:raise ValueError('Este original ya tiene otra declaración. No se sobrescribió.')
    registry['sources'][sid]=source;state=registry['map_workspace']
    if lid not in state['layers']:
        state['layers'][lid]={'id':lid,'source_id':sid,'type':'raster','native_crs':meta['native_crs'],
                            'name':name,'visible':True,'style':copy.deepcopy(DEFAULT_STYLE)}
        state['order'].append(lid)
    state.update(active_layer=lid,selection=[]);state['view']['bbox']=_fit([meta['bbox']])
    geo.validate_geography(candidate['studio']);return candidate,lid


def query(source,lon,lat):
    path=verify_source(source)
    if any(type(v) not in (float,int) or not math.isfinite(v) for v in (lon,lat)) or not -180<=lon<=180 or not -90<=lat<=90:raise ValueError('Coordenada de consulta inválida.')
    from studio_sig_vector import transform_for,crs
    with rasterio.open(path) as ds:
        x,y=transform_for(crs('EPSG:4326'),crs(ds.crs.to_wkt())).transform(lon,lat,errcheck=True)
        row,col=ds.index(x,y)
        value=None
        if 0<=row<ds.height and 0<=col<ds.width:
            raw=_values(ds,source['raster']['band'],Window(col,row,1,1))[0,0]
            if np.isfinite(raw):value=float(raw)
        return {'value':value,'status':'Sin dato / fuera de cobertura' if value is None else 'Observación nativa',
            'row':row,'column':col,'date':source['date'],'units':source['units'],'variable':source['variable'],
            'longitude':lon,'latitude':lat,'source_sha256':source['sha256']}


def compatible(sources,*,grid=False):
    if not 2<=len(sources)<=32:raise ValueError('Selecciona entre 2 y 32 rásteres.')
    for s in sources:verify_source(s)
    if any(sources[0][k]!=s[k] for s in sources[1:] for k in ('variable','units','semantics')):raise ValueError('Variable, unidad y significado deben coincidir; no se impone una escala común a datos distintos.')
    if grid and any(sources[0]['raster'][k]!=s['raster'][k] for s in sources[1:] for k in ('native_crs','shape','transform')):
        raise ValueError('CRS, alineación y resolución distintos. No se remuestrea automáticamente para calcular.')


def settings(sources):
    if len(sources)>1:compatible(sources)
    valid=[s['raster']['statistics'] for s in sources if s['raster']['statistics']['valid']]
    if not valid:return None
    lo=min(s['min'] for s in valid);hi=max(s['max'] for s in valid)
    if lo==hi:hi=lo+max(1.,abs(lo)*.01)
    return {'kind':'continuous','legend':sources[0]['variable'],'units':sources[0]['units'],
            'stops':np.linspace(lo,hi,len(PALETTE)).tolist(),'palette':PALETTE}


def representation(source,scale,size=512,box=None):
    if type(size) is not int or not 1<=size<=3840:raise ValueError('Representación: entre 1 y 3840 píxeles por lado.')
    path=verify_source(source);box=source['raster']['bbox'] if box is None else box;w,h=size,max(1,round(size*(box[3]-box[1])/(box[2]-box[0])))
    cache_key=(str(path),source['sha256'],source['raster']['band'],json.dumps(scale,sort_keys=True),tuple(box),size)
    with _LOCK:cached=_IMAGES.get(cache_key)
    if cached is not None:
        with Image.open(io.BytesIO(cached)) as image:return image.copy(),box
    if h>size:w=max(1,round(size*size/h));h=size
    if scale is None:return Image.new('RGBA',(w,h)),box
    from rasterio.transform import from_bounds
    from maqueta import paint_raster_layer
    with rasterio.open(path) as ds:
        from rasterio.enums import ColorInterp
        has_alpha=ColorInterp.alpha in ds.colorinterp
        with WarpedVRT(ds,crs='EPSG:4326',transform=from_bounds(*box,w,h),width=w,height=h,
                       resampling=Resampling.nearest,add_alpha=not has_alpha) as vrt:
            values=vrt.read(source['raster']['band'],masked=True).astype('float64')
            alpha_index=vrt.colorinterp.index(ColorInterp.alpha)+1
            alpha=vrt.read(alpha_index)>0
            values=np.where(alpha & ~np.ma.getmaskarray(values),values.data*source['raster']['scale']+source['raster']['offset'],np.nan)
    with Image.new('L',(w,h),255) as mask:
        image=paint_raster_layer(values,scale,mask)
    buffer=io.BytesIO();image.save(buffer,format='PNG')
    with _LOCK:
        _IMAGES[cache_key]=buffer.getvalue()
        while len(_IMAGES)>8 or sum(len(v) for v in _IMAGES.values())>8*1024*1024:_IMAGES.popitem(last=False)
    return image,box


def verify_series_binding(project,manifest):
    """Bind a sealed audiovisual product to authorized canonical native sources."""
    from studio_temporal import _hash
    from studio_sig_layers import _bbox
    binding=manifest['geographic_binding']
    if not {'sources','bbox','scale','method','basemap_included'}<=set(binding) or set(binding)-{'sources','bbox','scale','opacity','method','basemap_included','output_profile','cadence'} or binding['method']!='GDAL nearest, finite native mask, RGBA' or binding['basemap_included'] is not False:
        raise ValueError('Vínculo geográfico o exclusión del mapa base inválidos.')
    opacity=binding.get('opacity',1.)
    if type(opacity) not in (int,float) or not 0<=opacity<=1:raise ValueError('Opacidad de presentación inválida.')
    _bbox(binding['bbox'])
    if 'output_profile' in binding:
        from output_profiles import profile_for
        profile_for(binding['output_profile'])
        if binding.get('cadence') not in ('daily','monthly','irregular'):raise ValueError('Cadencia del recurso inválida.')
    sources=[];registry=project['studio'].get('geography',{}).get('sources',{})
    for entry in binding['sources']:
        source=registry.get(entry.get('id'))
        if source is None or entry!={'id':source['id'],'metadata_sha256':_hash(source)}:
            raise ValueError('Fuentes o declaración científica diferentes del recurso revisado.')
        verify_source(source);sources.append(source)
    compatible(sources)
    records=[{'file':s['path'],'date':s['date'],'band':s['raster']['band'],'sha256':s['sha256'],'source_url':s['provenance'].get('url','')} for s in sources]
    if (records!=manifest['source_records'] or binding['scale']!=settings(sources)
            or manifest['scientific_identity']!=_hash(binding) or manifest['scientific_revision']!=_hash([binding,records])
            or manifest['region']!=binding['bbox']
            or manifest['source']!='local' or manifest['variable']!=sources[0]['variable'] or manifest['units']!=sources[0]['units']
            or [o['native_crs'] for o in manifest['observations']]!=[s['native_crs'] for s in sources]
            or any(manifest['cartographic_settings'].get(k)!=v for k,v in binding['scale'].items())):
        raise ValueError('Fechas, escala, grid o revisión distintos de los originales.')
    return sources


def calculate(project,lids,tool,name):
    if len(lids)!=2:raise ValueError('Este cálculo requiere exactamente dos rásteres; no es una agregación temporal.')
    registry=project['studio']['geography'];state=registry['map_workspace']
    sources=[registry['sources'][state['layers'][lid]['source_id']] for lid in lids];compatible(sources,grid=True)
    if tool not in ('difference','mean','sum'):raise ValueError('Cálculo no admitido.')
    if tool=='sum':raise ValueError('Acumulados requieren intervalos y unidades verificadas. Usa diferencia o media de las observaciones; no se suman temperaturas.')
    operation={'tool':tool,'inputs':[{'source_id':s['id'],'sha256':s['sha256'],'date':s['date']} for s in sources],
        'method':'native aligned grid, intersection of finite masks; difference=B-A' if tool=='difference' else 'arithmetic mean of two observations, intersection of finite masks; not period-weighted',
        'units':sources[0]['units'],'processed_at':datetime.now(timezone.utc).isoformat()}
    with rasterio.open(verify_source(sources[0])) as a,rasterio.open(verify_source(sources[1])) as b:
        profile=a.profile.copy();profile.update(count=1,dtype='float64',nodata=float('nan'),compress='deflate')
        from rasterio.io import MemoryFile
        with MemoryFile() as memory:
            with memory.open(**profile) as out:
                out.update_tags(ns='ecuador_vivo',operation=json.dumps(operation,sort_keys=True,allow_nan=False))
                for y in range(0,a.height,512):
                    for x in range(0,a.width,512):
                        win=Window(x,y,min(512,a.width-x),min(512,a.height-y));v1=_values(a,sources[0]['raster']['band'],win);v2=_values(b,sources[1]['raster']['band'],win)
                        out.write(v2-v1 if tool=='difference' else (v1+v2)/2,1,window=win)
            content=memory.read()
    result,lid=add_raster(project,content,name,{'citation':'Derivado de '+', '.join(s['name'] for s in sources),
        'license':'Conserva las condiciones de ambas fuentes; no autoriza redistribución.','url':''},
        observed_date=None,variable=sources[0]['variable'],units=sources[0]['units'],semantics=sources[0]['semantics'])
    geo.validate_geography(result['studio']);return result,lid


def zonal_layer(project,raster_id,zones_id):
    """Persist the zonal result using the existing derived vector recipe contract."""
    from studio_sig_layers import workspace_for,add_geojson_layer
    from studio_sig_vector import layer_features
    from datetime import datetime,timezone
    state=workspace_for(project)
    source=project['studio']['geography']['sources'][state['layers'][raster_id]['source_id']]
    zones,features=layer_features(project,zones_id)
    rows=zonal(source,features)
    for feature,row in zip(features,rows):feature['properties']=row
    recipe={'version':1,'tool':'zonal','inputs':[{'source_id':s['id'],'sha256':s['sha256']} for s in (source,zones)],
        'parameters':{'band':source['raster']['band'],'date':source['date'],'method':rows[0]['method']},
        'units':source['units'],'processed_at':datetime.now(timezone.utc).isoformat(),
        'engine':'Rasterio '+rasterio.__version__+' / GDAL '+rasterio.__gdal_version__+'; native finite mask, pixel centres'}
    data=json.dumps({'type':'FeatureCollection','features':features,'ecuador_vivo_operation':recipe},ensure_ascii=False,allow_nan=False).encode('utf-8')
    candidate,lid=add_geojson_layer(project,data,'Zonas · '+source['variable'],
        {'citation':'Estadísticas zonales de '+source['name'],'license':'Condiciones de las fuentes de entrada; no autoriza redistribución.','url':''})
    registry=candidate['studio']['geography'];registry['sources'][registry['map_workspace']['layers'][lid]['source_id']]['operation']=recipe
    geo.validate_geography(candidate['studio']);return candidate,lid


def zonal(source,features):
    """Polygon pixel-centre statistics, windowed native data, explicit coverage."""
    path=verify_source(source);rows=[]
    with rasterio.open(path) as ds:
        for feature in features:
            geom=feature['geometry']
            if geom['type'] not in ('Polygon','MultiPolygon'):raise ValueError('Estadísticas zonales requieren polígonos; no se sustituyen por capitales.')
            from studio_sig_vector import transform_for,crs
            from shapely.geometry import shape,mapping
            from shapely.ops import transform
            geom=mapping(transform(transform_for(crs('EPSG:4326'),crs(ds.crs.to_wkt())).transform,shape(geom)))
            count=0;cells=0;total=0.;lo=None;hi=None
            try:window=geometry_window(ds,[geom]).round_offsets().round_lengths()
            except WindowError:window=None
            if window is not None:
                for y in range(int(window.row_off),int(window.row_off+window.height),512):
                    for x in range(int(window.col_off),int(window.col_off+window.width),512):
                        win=Window(x,y,min(512,int(window.col_off+window.width)-x),min(512,int(window.row_off+window.height)-y))
                        values=_values(ds,source['raster']['band'],win)
                        mask=geometry_mask([geom],values.shape,ds.window_transform(win),invert=True,all_touched=False)
                        cells+=int(mask.sum());v=values[mask & np.isfinite(values)]
                        if v.size:
                            count+=int(v.size);total+=float(v.sum());lo=float(v.min()) if lo is None else min(lo,float(v.min()));hi=float(v.max()) if hi is None else max(hi,float(v.max()))
            rows.append({**copy.deepcopy(feature.get('properties') or {}),'valid_cells':count,'domain_cells_in_raster':cells,
                'coverage_within_raster':count/cells if cells else None,'mean':total/count if count else None,'min':lo,'max':hi,
                'units':source['units'],'date':source['date'],'method':'native pixel centres; coverage denominator clipped to raster footprint, not entire polygon'})
    return rows
