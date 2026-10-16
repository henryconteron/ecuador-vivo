"""Own tool descriptors shared by discovery and existing execution forms."""
import json
from collections import Counter
from studio_sig_layers import workspace_for

def descriptor(id,label,group,summary,kind='vector'):
    return {'id':id,'label':label,'group':group,'summary':summary,'kind':kind}

VECTOR_TOOLS=(
    descriptor('buffer','Buffer','Proximidad','Crea zonas a una distancia en metros.'),
    descriptor('clip','Recortar','Superposición','Conserva lo que cae dentro de otra capa poligonal.'),
    descriptor('intersection','Intersección','Superposición','Cruza geometrías y conserva atributos de ambas capas.'),
    descriptor('dissolve','Disolver','Geometría','Une entidades por campo o en un solo conjunto.'),
    descriptor('centroid','Centroides','Geometría','Centro geométrico por entidad; puede quedar fuera de un polígono.'),
    descriptor('point_on_surface','Puntos interiores','Geometría','Un punto dentro de cada polígono; útil para etiquetas.'),
    descriptor('convex_hull','Envolvente convexa','Geometría','Envolvente por entidad, no una envolvente de toda la capa.'),
    descriptor('boundary','Extraer contornos','Geometría','Bordes exteriores e interiores de cada polígono.'),
    descriptor('measure','Superficie y longitud','Medición','Añade área y longitud con un CRS métrico apropiado.'),
    descriptor('calculate','Calcular campo','Atributos','Aritmética por entidad; conserva valores ausentes.'),
    descriptor('filter','Filtrar entidades','Atributos','Genera una capa derivada según una condición.'),
)
RASTER_TOOLS=(
    descriptor('raster_compare','Comparar fechas','Ráster','Compara dos observaciones de la misma variable.','raster'),
    descriptor('raster_difference','Diferencia B − A','Ráster','Resta celdas nativas alineadas, no colores de pantalla.','raster'),
    descriptor('raster_mean','Media de dos observaciones','Ráster','Promedio de dos entradas compatibles, no promedio anual.','raster'),
    descriptor('raster_zonal','Estadísticas zonales','Ráster','Resume valores nativos dentro de polígonos.','raster'),
)

def tool_catalog(project,layer_records=None):
    state=workspace_for(project);active=state['layers'].get(state['active_layer'])
    vectors=[layer for layer in state['layers'].values() if layer['type']=='vector']
    rasters=[layer for layer in state['layers'].values() if layer['type']=='raster']
    records={r['id']:r for r in layer_records} if layer_records is not None else {}
    def polygon(layer):
        record=records.get(layer['id'])
        return None if record is None else bool(record.get('features')) and all(f['geometry']['type'] in ('Polygon','MultiPolygon') for f in record['features'])
    polygons=[layer for layer in vectors if polygon(layer) is not False]
    sources=project['studio'].get('geography',{}).get('sources',{})
    signatures=[];grids=[]
    for layer in rasters:
        source=sources[layer['source_id']];signature=[source.get(k) for k in ('variable','units','semantics')]
        signatures.append(json.dumps(signature,sort_keys=True))
        grids.append(json.dumps(signature+[source['raster'].get(k) for k in ('native_crs','shape','transform')],sort_keys=True))
    result=[]
    for tool in (*VECTOR_TOOLS,*RASTER_TOOLS):
        reason=''
        if tool['kind']=='vector':
            if not active or active['type']!='vector':reason='Selecciona una capa vectorial.'
            elif tool['id']=='boundary' and polygon(active) is False:reason='Selecciona una capa de polígonos para extraer contornos.'
            elif tool['id'] in ('clip','intersection') and not any(layer['id']!=active['id'] for layer in polygons):reason='Añade otra capa vectorial poligonal.'
        elif not rasters:reason='Incorpora un GeoTIFF.'
        elif tool['id']=='raster_zonal' and not polygons:reason='Incorpora polígonos para definir las zonas.'
        elif tool['id']!='raster_zonal' and len(rasters)<2:reason='Se necesitan dos observaciones ráster.'
        elif tool['id']!='raster_zonal' and max(Counter(signatures if tool['id']=='raster_compare' else grids).values(),default=0)<2:
            reason='Se necesitan dos entradas compatibles: variable, unidad y significado; para calcular, también la cuadrícula.'
        result.append({**tool,'available':not reason,'reason':reason})
    return result

def launch_operation(session,id):
    tool=next((tool for tool in tool_catalog(session.project) if tool['id']==id),None)
    if tool is None:raise ValueError('Operación desconocida.')
    if not tool['available']:raise ValueError(tool['reason'])
    from studio_sig_workspace import choose_tool
    if tool['kind']=='vector':
        session.state[session.key+'_vector_operation']=tool['label']
        session.state.pop('sig_analysis_name',None)
        choose_tool(session,'Análisis vectorial')
    else:
        session.state['sig_raster_tool']=tool['label'];choose_tool(session,'Ráster y tiempo')
    session.state[session.key+'_sig_dialog']='tools'
