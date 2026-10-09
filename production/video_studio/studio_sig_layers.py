"""Canonical SIG layers/view over SIG-G1 sources; no duplicate datasets/science."""
import copy
import math
import re
from studio_geography import CRS,_registry,import_geojson,read_source,_features

METHOD='angular_lonlat_interactive_v1'
DEFAULT_STYLE={'fill':'#13bfd1','stroke':'#e4f4f9','opacity':.7}

def layer_id(source_id):return source_id.replace('source.','layer.',1)

def _bbox(box):
    if (not isinstance(box,list) or len(box)!=4 or any(type(v) not in (int,float) or not math.isfinite(v) for v in box)
            or not -180<=box[0]<box[2]<=180 or not -89.999<=box[1]<box[3]<=89.999):
        raise ValueError('Extensión de vista: lon/lat finitas, sin polos ni cruce del antimeridiano.')
    return box

def _fit(boxes):
    if not boxes:return [-180,-80,180,80]
    box=[min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes)]
    dx=max(.001,(box[2]-box[0])*.05);dy=max(.001,(box[3]-box[1])*.05)
    return [max(-180,box[0]-dx),max(-89.999,box[1]-dy),min(180,box[2]+dx),min(89.999,box[3]+dy)]

def _layer(source):
    return {'id':layer_id(source['id']),'source_id':source['id'],'type':'vector','native_crs':source['native_crs'],
            'name':source['name'],'visible':True,'style':copy.deepcopy(DEFAULT_STYLE)}

def workspace_for(project):
    registry=_registry(project)
    if 'map_workspace' in registry:return copy.deepcopy(registry['map_workspace'])
    layers={layer_id(sid):_layer(s) for sid,s in registry['sources'].items()}
    return {'version':1,'layers':layers,'order':list(layers),'active_layer':next(reversed(layers),None),
            'selection':[], 'view':{'display_crs':CRS,'method':METHOD,
                'bbox':_fit([r['bbox'] for r in registry['regions'].values()])}}

def validate_map_workspace(registry):
    state=registry.get('map_workspace')
    if state is None:return
    try:
        if (not isinstance(state,dict) or set(state)!={'version','layers','order','active_layer','selection','view'}
                or type(state['version']) is not int or state['version']!=1 or not isinstance(state['layers'],dict)):
            raise ValueError('Estado SIG de capas incompatible.')
        layers=state['layers'];order=state['order']
        if not isinstance(order,list) or any(not isinstance(v,str) for v in order) or len(set(order))!=len(order) or set(order)!=set(layers):
            raise ValueError('Orden SIG debe contener cada capa exactamente una vez.')
        for lid,layer in layers.items():
            sid=layer['source_id'];source=registry['sources'].get(sid)
            if (source is None or lid!=layer_id(sid) or layer['id']!=lid or layer['type']!='vector'
                    or layer['native_crs']!=source['native_crs'] or type(layer['visible']) is not bool
                    or not isinstance(layer['name'],str) or not 0<len(layer['name'])<=180):
                raise ValueError('Capa sin fuente válida, CRS o identidad coherentes.')
            style=layer['style']
            if (set(style)!={'fill','stroke','opacity'} or any(not isinstance(style[k],str) or not re.fullmatch('#[0-9a-fA-F]{6}',style[k]) for k in ('fill','stroke'))
                    or type(style['opacity']) not in (int,float) or not math.isfinite(style['opacity']) or not 0<=style['opacity']<=1):
                raise ValueError('Simbología SIG inválida.')
        active=state['active_layer']
        if active is not None and active not in layers or active is None and layers:raise ValueError('Capa activa SIG desconocida.')
        selection=state['selection']
        if (not isinstance(selection,list) or any(not isinstance(rid,str) for rid in selection) or len(set(selection))!=len(selection)
                or any(rid not in registry['regions'] or registry['regions'][rid]['source_id']!=layers[active]['source_id'] for rid in selection)
                or selection and not layers[active]['visible']):raise ValueError('Selección no pertenece a la capa activa visible.')
        view=state['view']
        if set(view)!={'display_crs','method','bbox'} or view['display_crs']!=CRS or view['method']!=METHOD:
            raise ValueError('CRS de vista SIG incompatible.')
        _bbox(view['bbox'])
    except (KeyError,TypeError,AttributeError) as error:raise ValueError('Contrato SIG de capas/vista incompleto.') from error

def ensure_workspace(project):
    from studio_geography import validate_geography
    result=copy.deepcopy(project)
    registry=result['studio'].setdefault('geography',{'version':1,'sources':{},'regions':{},'views':{}})
    registry.setdefault('map_workspace',workspace_for(result))
    validate_geography(result['studio'])
    return result

def add_geojson_layer(project,content,name,provenance):
    result,rid=import_geojson(project,content,name,provenance)
    result=ensure_workspace(result);registry=result['studio']['geography'];state=registry['map_workspace']
    sid=registry['regions'][rid]['source_id'];lid=layer_id(sid)
    if lid not in state['layers']:
        state['layers'][lid]=_layer(registry['sources'][sid]);state['order'].append(lid)
    state['active_layer']=lid;state['selection']=[]
    state['view']['bbox']=_fit([r['bbox'] for r in registry['regions'].values() if r['source_id']==sid])
    validate_map_workspace(registry)
    return result,lid

def layer_command(project,message):
    """Pure reversible presentation command; sources, attributes and science untouched."""
    result=ensure_workspace(project);registry=result['studio']['geography'];state=registry['map_workspace']
    action=message.get('action');lid=message.get('layer_id',state['active_layer']);layer=state['layers'].get(lid)
    if action not in ('view','fit_all','clear_selection') and layer is None:raise ValueError('Selecciona una capa existente.')
    if action=='active':state['active_layer']=lid;state['selection']=[]
    elif action=='visibility':
        layer['visible']=message['visible']
        if lid==state['active_layer'] and not layer['visible']:state['selection']=[]
    elif action=='style':layer['style']=copy.deepcopy(message['style'])
    elif action=='order':
        index=state['order'].index(lid);offset=message.get('offset')
        if type(offset) is not int or offset not in (-1,1):raise ValueError('Orden: subir o bajar una posición.')
        target=index+offset
        if 0<=target<len(state['order']):state['order'][index],state['order'][target]=state['order'][target],state['order'][index]
    elif action=='remove':
        state['order'].remove(lid);state['layers'].pop(lid)
        if state['active_layer']==lid:state['active_layer']=next(reversed(state['order']),None);state['selection']=[]
    elif action=='select':state['active_layer']=lid;state['selection']=[message['region_id']]
    elif action=='clear_selection':state['selection']=[]
    elif action=='view':state['view']['bbox']=copy.deepcopy(message['bbox'])
    elif action in ('fit','fit_all'):
        sources={layer['source_id']} if action=='fit' else {v['source_id'] for v in state['layers'].values() if v['visible']}
        state['view']['bbox']=_fit([r['bbox'] for r in registry['regions'].values() if r['source_id'] in sources])
    else:raise ValueError('Acción SIG desconocida.')
    validate_map_workspace(registry)
    return result

def map_payload(project):
    """Verified geometries for display only; canonical dataset references remain compact."""
    from studio_geography import validate_geography
    validate_geography(project['studio']);state=workspace_for(project);registry=_registry(project);sources={};layers=[]
    for lid in state['order']:
        layer=state['layers'][lid];sid=layer['source_id']
        if sid not in sources:sources[sid]=_features(read_source(registry['sources'][sid]))
        features=[{'region_id':rid,'geometry':sources[sid][r['feature_index']]['geometry']}
                  for rid,r in registry['regions'].items() if r['source_id']==sid]
        layers.append({**layer,'features':features})
    return {'view':state['view'],'layers':layers,'selection':state['selection'],'active_layer':state['active_layer']}
