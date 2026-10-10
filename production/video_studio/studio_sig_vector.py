"""BYOD vector import and GEOS/PROJ operations in the canonical geography catalog.

Original files are immutable. CRS84 is an identified representation, not a claim
that CSV/OGR input coordinates were WGS84. All operations create new sources.
"""
import copy,csv,io,json,math,re,hashlib
from datetime import datetime,timezone
from pathlib import Path
import studio_geography as geo
from pyproj import CRS,Transformer
from shapely.geometry import shape,mapping
from shapely.ops import transform,unary_union
from shapely.strtree import STRtree


def crs(value):
    if not isinstance(value,str) or not value.strip():raise ValueError('CRS desconocido. Indica el CRS de origen; no se asumirá WGS84.')
    try:result=CRS.from_user_input(value)
    except Exception as error:raise ValueError('CRS no reconocido. Usa un código EPSG o WKT válido.') from error
    if len(result.axis_info)!=2:raise ValueError('Se requiere CRS horizontal 2D; no se descartan coordenadas verticales.')
    return result


def transform_for(source,target):
    return Transformer.from_crs(source,target,always_xy=True,allow_ballpark=False,only_best=True)


def stored_original(content,name,kind,source_crs,options):
    if not isinstance(content,bytes) or not 0<len(content)<=geo.SOURCE_LIMIT:raise ValueError('Archivo vacío o superior a 8 MiB.')
    digest=hashlib.sha256(content).hexdigest();path=geo.ROOT/'originals'/(digest+'.'+kind)
    path.parent.mkdir(parents=True,exist_ok=True)
    try:
        with path.open('xb') as stream:stream.write(content)
    except FileExistsError:
        if path.read_bytes()!=content:raise ValueError('El archivo original almacenado cambió.')
    result={'path':str(path),'sha256':digest,'bytes':len(content),'name':name,'format':kind,
            'native_crs':crs(source_crs).to_wkt(),'options':copy.deepcopy(options)}
    verify_origin(result);return result


def verify_origin(origin):
    if (not isinstance(origin,dict) or set(origin)!={'path','sha256','bytes','name','format','native_crs','options'}
            or origin['format'] not in ('csv','gpkg','fgb') or not re.fullmatch('[a-f0-9]{64}',str(origin['sha256']))
            or type(origin['bytes']) is not int or not 0<origin['bytes']<=geo.SOURCE_LIMIT
            or not isinstance(origin['name'],str) or not 0<len(origin['name'])<=180 or not isinstance(origin['options'],dict)):
        raise ValueError('Referencia de archivo original inválida.')
    crs(origin['native_crs']);path=Path(origin['path']).resolve()
    expected=(geo.ROOT/'originals'/(origin['sha256']+'.'+origin['format'])).resolve()
    if path!=expected or not path.is_relative_to(geo.ROOT.resolve()) or not path.is_file():raise ValueError('Original ausente o no autorizado.')
    if path.stat().st_size!=origin['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest()!=origin['sha256']:
        raise ValueError('El original aportado cambió; no se utilizará una representación en caché.')
    json.dumps(origin['options'],allow_nan=False)


def csv_rows(content,delimiter=','):
    if not isinstance(content,bytes) or not 0<len(content)<=geo.SOURCE_LIMIT:raise ValueError('CSV vacío o superior a 8 MiB.')
    if delimiter not in (',',';','\t'):raise ValueError('Separador CSV inválido.')
    try:reader=csv.DictReader(io.StringIO(content.decode('utf-8-sig')),delimiter=delimiter)
    except UnicodeError as error:raise ValueError('CSV debe estar codificado en UTF-8.') from error
    fields=reader.fieldnames
    if not fields or any(not k for k in fields) or len(set(fields))!=len(fields):raise ValueError('Cabecera CSV ausente o con columnas repetidas.')
    rows=[]
    for row in reader:
        if None in row or None in row.values():raise ValueError('CSV tiene filas con un número de columnas distinto de la cabecera.')
        rows.append(row)
        if len(rows)>geo.REGION_LIMIT:raise ValueError('CSV supera 5000 filas.')
    if not rows:raise ValueError('CSV sin filas de datos.')
    return fields,rows


def add_converted(project,features,content,name,provenance,kind,source_crs,options):
    from studio_sig_layers import add_geojson_layer
    # Conversion metadata participates in content identity and cannot be silently relabeled.
    metadata={'format':kind,'input_sha256':hashlib.sha256(content).hexdigest(),
              'native_crs':crs(source_crs).to_wkt(),'display_crs':'OGC:CRS84','options':options,'method':'PROJ always_xy, no ballpark'}
    document={'type':'FeatureCollection','features':features,'ecuador_vivo_import':metadata}
    data=json.dumps(document,ensure_ascii=False,allow_nan=False).encode('utf-8');geo.parse_geojson(data)
    origin=stored_original(content,name,kind,source_crs,options)
    result,lid=add_geojson_layer(project,data,name,provenance)
    source=result['studio']['geography']['sources'][result['studio']['geography']['map_workspace']['layers'][lid]['source_id']]
    if 'origin' in source and source['origin']!=origin:raise ValueError('Conversión existente con otro original.')
    source['origin']=origin;geo.validate_geography(result['studio']);return result,lid


def add_csv(project,content,name,provenance,*,x,y,source_crs,delimiter=','):
    fields,rows=csv_rows(content,delimiter);native=crs(source_crs)
    if x==y or x not in fields or y not in fields:raise ValueError('Elige dos columnas distintas para X e Y.')
    projector=transform_for(native,CRS.from_user_input('OGC:CRS84'));features=[]
    for i,row in enumerate(rows):
        try:
            a,b=float(row[x]),float(row[y])
            if not math.isfinite(a) or not math.isfinite(b):raise ValueError()
            lon,lat=projector.transform(a,b,errcheck=True)
        except Exception as error:raise ValueError(f'Fila {i+2}: coordenadas ausentes, no numéricas o incompatibles con el CRS. No se omitió ni sustituyó la fila.') from error
        features.append({'type':'Feature','id':i,'properties':{k:v if v!='' else None for k,v in row.items()},
                         'geometry':{'type':'Point','coordinates':[lon,lat]}})
    return add_converted(project,features,content,name,provenance,'csv',native.to_wkt(),{'x':x,'y':y,'delimiter':delimiter,'empty':'null','attributes':'text, original retained'})


def ogr_layers(content,kind):
    """Validate self-contained container before allowing GDAL to inspect bytes."""
    import pyogrio
    if not isinstance(content,bytes) or not 0<len(content)<=geo.SOURCE_LIMIT:
        raise ValueError('Archivo vacío o superior a 8 MiB.')
    if kind=='gpkg':
        # SQLite application_id is big endian at byte 68; reject arbitrary
        # SQLite, VRT/XML and mismatched extensions before GDAL auto-detection.
        valid=content[:16]==b'SQLite format 3\x00' and content[68:72]==b'GPKG'
    elif kind=='fgb':valid=content[:8]==b'fgb\x03fgb\x01'
    else:valid=False
    if not valid:raise ValueError('El contenido no corresponde a un GeoPackage o FlatGeobuf autónomo autorizado.')
    layers=pyogrio.list_layers(content)
    if not len(layers):raise ValueError('El archivo no contiene capas vectoriales.')
    return layers


def add_ogr(project,content,name,provenance,*,kind,source_crs='',layer=None):
    """Installed GDAL reader, restricted to self-contained GeoPackage/FlatGeobuf."""
    import geopandas as gpd
    if kind not in ('gpkg','fgb'):raise ValueError('Formato OGR no habilitado.')
    if len(content)>geo.SOURCE_LIMIT:raise ValueError('Archivo superior a 8 MiB.')
    try:
        layers=ogr_layers(content,kind)
        if layer is None and len(layers)!=1:raise ValueError('El GeoPackage contiene varias capas; selecciona una capa explícitamente.')
        selected=layer or str(layers[0][0])
        if selected not in layers[:,0]:raise ValueError('Capa OGR desconocida.')
        frame=gpd.read_file(content,engine='pyogrio',layer=selected,rows=geo.REGION_LIMIT+1)
        if not 0<len(frame)<=geo.REGION_LIMIT:raise ValueError('Capa vacía o superior a 5000 entidades.')
        native=crs(frame.crs.to_wkt() if frame.crs is not None else source_crs)
        if source_crs and not native.equals(crs(source_crs)):raise ValueError('El CRS declarado contradice los metadatos del archivo.')
        if frame.crs is None:frame=frame.set_crs(native)
        projector=transform_for(native,CRS.from_user_input('OGC:CRS84'))
        frame=frame.copy()
        frame.geometry=gpd.GeoSeries([transform(projector.transform,g) if g is not None else None for g in frame.geometry],index=frame.index,crs='OGC:CRS84')
        frame=frame.set_crs('OGC:CRS84',allow_override=True)
        features=json.loads(frame.to_json(drop_id=False,na='null'))['features']
    except (ValueError,TypeError) :raise
    except Exception as error:raise ValueError('No se pudo leer la capa OGR: '+str(error)) from error
    return add_converted(project,features,content,name,provenance,kind,native.to_wkt(),{'layer':selected,'reader':'GDAL/pyogrio'})


def layer_features(project,lid):
    from studio_sig_layers import workspace_for
    layer=workspace_for(project)['layers'].get(lid)
    if layer is None:raise ValueError('Selecciona una capa vectorial existente.')
    source=project['studio']['geography']['sources'][layer['source_id']]
    return source,copy.deepcopy(geo._features(geo.read_source(source)))


def validate_operation(operation,registry):
    if (not isinstance(operation,dict) or set(operation)!={'version','tool','inputs','parameters','units','processed_at','engine'}
            or operation['version']!=1 or operation['tool'] not in ('buffer','clip','intersection','dissolve','measure','calculate','filter','zonal')
            or not isinstance(operation['parameters'],dict) or not isinstance(operation['units'],str)
            or not isinstance(operation['inputs'],list) or not 1<=len(operation['inputs'])<=2):
        raise ValueError('Procedencia de operación vectorial inválida.')
    for value in operation['inputs']:
        if not isinstance(value,dict) or set(value)!={'source_id','sha256'}:raise ValueError('Entrada de operación inválida.')
        source=registry['sources'].get(value['source_id'])
        if source is None or source['sha256']!=value['sha256']:raise ValueError('Operación sin la fuente de entrada verificada.')
    datetime.fromisoformat(operation['processed_at']);json.dumps(operation,allow_nan=False)
    if operation['tool']=='zonal':
        inputs=[registry['sources'][v['source_id']] for v in operation['inputs']]
        if len(inputs)!=2 or inputs[0].get('type')!='raster' or inputs[1].get('type')=='raster':raise ValueError('Zonas requieren un ráster y polígonos de origen.')
        if operation['units']!=inputs[0]['units'] or operation['parameters']!={'band':inputs[0]['raster']['band'],'date':inputs[0]['date'],
            'method':'native pixel centres; coverage denominator clipped to raster footprint, not entire polygon'}:raise ValueError('Método zonal distinto de su fuente.')


def metric_projection(features,value):
    target=crs(value)
    if not target.is_projected or any(abs(a.unit_conversion_factor-1)>1e-12 for a in target.axis_info) or target.to_epsg()==3857:
        raise ValueError('Elige un CRS proyectado apropiado en metros; grados y Web Mercator no sirven para esta medida.')
    area=target.area_of_use
    if area:
        for f in features:
            a,b,c,d=shape(f['geometry']).bounds
            if not area.west<=a<=c<=area.east or not area.south<=b<=d<=area.north:
                raise ValueError('La capa está fuera del área de uso del CRS elegido. Selecciona una proyección adecuada.')
    return target,transform_for(CRS.from_user_input('OGC:CRS84'),target),transform_for(target,CRS.from_user_input('OGC:CRS84'))


def number(value):
    if value is None or isinstance(value,bool):raise ValueError('Valor ausente/no numérico; no se sustituye por cero.')
    try:value=float(value)
    except (ValueError,TypeError) as error:raise ValueError('Campo no numérico.') from error
    if not math.isfinite(value):raise ValueError('Valor no finito.')
    return value


def run_operation(project,lid,tool,parameters,*,other=None,name='Resultado vectorial'):
    if not isinstance(name,str) or not name.strip() or len(name)>172:raise ValueError('Nombre de resultado vacío o demasiado largo.')
    source,features=layer_features(project,lid);inputs=[source];params=copy.deepcopy(parameters);units='';output=[]
    if tool in ('calculate','filter') or tool=='dissolve' and params.get('field'):
        if not any(params.get('field') in (f.get('properties') or {}) for f in features):raise ValueError('El campo elegido no existe en la capa.')
    if tool=='calculate' and params.get('operator')=='divide' and number(params.get('constant'))==0:raise ValueError('No se permite dividir por cero.')
    if tool in ('clip','intersection'):
        mask_source,masks=layer_features(project,other);inputs.append(mask_source)
        if any(f['geometry']['type'] not in ('Polygon','MultiPolygon') for f in masks):raise ValueError('La capa de recorte/intersección debe contener polígonos.')
        mask_geometries=[shape(f['geometry']) for f in masks]
        if tool=='clip':mask=unary_union(mask_geometries)
        else:mask_index=STRtree(mask_geometries)
    if tool in ('buffer','measure'):
        target,to_metric,to_view=metric_projection(features,params.get('crs',''));params['crs']=target.to_wkt()
        units='m' if tool=='buffer' else 'm² / m'
    if tool=='buffer':params['quad_segs']=16
    params['geometry_method']='projected metric GEOS' if tool in ('buffer','measure') else 'planar GEOS in CRS84' if tool in ('clip','intersection','dissolve') else 'attribute operation; geometry unchanged'
    if tool=='dissolve':
        field=params.get('field');groups={}
        for f in features:
            value=(f.get('properties') or {}).get(field) if field else None;key=json.dumps(value,sort_keys=True)
            groups.setdefault(key,[]).append(f)
        for key,group in groups.items():
            geometry=unary_union([shape(f['geometry']) for f in group])
            output.append({'type':'Feature','properties':{field:json.loads(key)} if field else {},'geometry':mapping(geometry)})
    else:
        for i,f in enumerate(features):
            g=shape(f['geometry']);properties=f.get('properties') or {};f['properties']=properties;f.pop('bbox',None)
            if tool=='buffer':
                distance=number(params.get('distance'))
                if not 0<distance<=1_000_000:raise ValueError('Buffer requiere distancia positiva de hasta 1000000 m.')
                g=transform(to_view.transform,transform(to_metric.transform,g).buffer(distance,quad_segs=params['quad_segs']))
            elif tool=='clip':g=g.intersection(mask)
            elif tool=='intersection':
                for j in sorted(mask_index.query(g,predicate='intersects')):
                    m=masks[j];intersected=g.intersection(mask_geometries[j])
                    if intersected.is_empty:continue
                    if intersected.geom_type=='GeometryCollection':raise ValueError('Intersección con partes mixtas no soportada; no se descartaron partes.')
                    props=copy.deepcopy(properties)
                    for k,v in (m.get('properties') or {}).items():
                        key='ev_mask_'+k
                        if key in props:raise ValueError('Colisión de campos de intersección; no se sobrescribieron atributos.')
                        props[key]=v
                    output.append({'type':'Feature','id':f'{i}.{j}','geometry':mapping(intersected),'properties':props})
                    if len(output)>geo.REGION_LIMIT:raise ValueError('Intersección supera 5000 resultados. Filtra las entradas antes de operar; no se añadió un resultado parcial.')
                continue
            elif tool=='measure':
                if any(k in properties for k in ('ev_area_m2','ev_length_m')):raise ValueError('Los campos de medición ya existen; conserva o cambia la capa de entrada.')
                measured=transform(to_metric.transform,g)
                properties['ev_area_m2']=measured.area if g.geom_type in ('Polygon','MultiPolygon') else None
                properties['ev_length_m']=measured.length if g.geom_type not in ('Point','MultiPoint') else None
            elif tool=='calculate':
                field=params.get('field');out=params.get('output');operation=params.get('operator');constant=number(params.get('constant'))
                if not isinstance(out,str) or not re.fullmatch(r'[\w]{1,64}',out) or out in properties:raise ValueError('Elige un campo nuevo válido; no se sobrescriben atributos.')
                value=properties.get(field)
                if value is None:properties[out]=None
                else:
                    value=number(value)
                    if operation=='divide' and constant==0:raise ValueError('No se permite dividir por cero.')
                    ops={'add':lambda:value+constant,'subtract':lambda:value-constant,'multiply':lambda:value*constant,'divide':lambda:value/constant}
                    if operation not in ops:raise ValueError('Operador de cálculo desconocido.')
                    properties[out]=number(ops[operation]())
                units=params.get('units','')
                if not isinstance(units,str):raise ValueError('Unidades inválidas.')
            elif tool=='filter':
                value=properties.get(params.get('field'));operator=params.get('operator');reference=params.get('value')
                if operator=='missing':keep=value is None
                elif operator=='equals':keep=str(value)==str(reference) if value is not None else False
                elif operator=='contains':keep=str(reference).casefold() in str(value).casefold() if value is not None else False
                elif operator in ('greater','less'):keep=False if value is None else number(value)>number(reference) if operator=='greater' else number(value)<number(reference)
                else:raise ValueError('Filtro desconocido.')
                if not keep:continue
            else:raise ValueError('Operación vectorial desconocida.')
            if g.is_empty:continue
            if g.geom_type=='GeometryCollection':raise ValueError('La operación produjo una GeometryCollection; no se descartarán partes silenciosamente.')
            f['geometry']=mapping(g);output.append(f)
    if not output:raise ValueError('La operación no produjo entidades. No se añadió una capa vacía ni datos ficticios.')
    import shapely,pyproj
    recipe={'version':1,'tool':tool,'inputs':[{'source_id':s['id'],'sha256':s['sha256']} for s in inputs],
            'parameters':params,'units':units,'processed_at':datetime.now(timezone.utc).isoformat(),
            'engine':f'Shapely {shapely.__version__} / GEOS {shapely.geos_version_string}; PyProj {pyproj.__version__} / PROJ {pyproj.proj_version_str}; CRS84 representation'}
    data=json.dumps({'type':'FeatureCollection','features':output,'ecuador_vivo_operation':recipe},ensure_ascii=False,allow_nan=False).encode('utf-8')
    from studio_sig_layers import add_geojson_layer
    result,new_lid=add_geojson_layer(project,data,name+'.geojson',source['provenance'])
    registry=result['studio']['geography'];registry['sources'][registry['map_workspace']['layers'][new_lid]['source_id']]['operation']=recipe
    geo.validate_geography(result['studio']);return result,new_lid


def export_layer(project,lid):
    source,features=layer_features(project,lid)
    return json.dumps({'type':'FeatureCollection','features':features,
        'ecuador_vivo_provenance':source['provenance'],'ecuador_vivo_operation':source.get('operation')},
        ensure_ascii=False,allow_nan=False,indent=2).encode('utf-8')
