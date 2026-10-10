"""Licensed small reference layers, admitted by canonical import transactions."""
import copy,hashlib,json
from pathlib import Path
from studio_sig_layers import add_geojson_layer,layer_command,workspace_for

ASSETS=Path(__file__).with_name('reference_data')
NAMES={'ecuador-national':'Ecuador · límite nacional','ecuador-provinces':'Ecuador · 24 provincias',
       'galapagos':'Galápagos · ubicación real','latin-america':'Latinoamérica · 20 países'}
EXTENTS={'Ecuador continental':[-81.5,-5.3,-75.,1.6],'Galápagos':[-92.3,-1.7,-88.9,2.],
         'Latinoamérica':[-118.,-57.,-33.,33.]}


def catalog():return json.loads((ASSETS/'manifest.json').read_text(encoding='utf-8'))


def reference(project,key):
    if key not in NAMES:raise ValueError('Capa de referencia desconocida.')
    parent='ecuador-provinces' if key=='galapagos' else key;meta=catalog()[parent]
    content=(ASSETS/(parent+'.geojson')).read_bytes()
    if hashlib.sha256(content).hexdigest()!=meta['sha256']:raise ValueError('La referencia cambió: no se utilizará.')
    if key=='galapagos':
        value=json.loads(content);value['features']=[f for f in value['features'] if f['properties']['shapeName']=='Galápagos']
        if len(value['features'])!=1:raise ValueError('La referencia no contiene la provincia Galápagos.')
        content=json.dumps(value,ensure_ascii=False,separators=(',',':')).encode('utf-8')
    candidate,lid=add_geojson_layer(project,content,NAMES[key],{'citation':meta['notes']+' '+
        ('Natural Earth v5.1.2.' if parent=='latin-america' else 'geoBoundaries, William & Mary; Runfola et al. (2020).')+
        ' Original SHA256: '+meta['original_sha256'], 'license':meta['license'],'url':meta['source_url']})
    # Presentation group and style do not modify the imported geometry.
    candidate=layer_command(candidate,{'action':'group','layer_id':lid,'group':'reference'})
    candidate=layer_command(candidate,{'action':'style','layer_id':lid,'style':{'fill':'#2d9387','stroke':'#b2e9dc','opacity':.3}})
    return candidate,lid


def initial_map(project):
    if workspace_for(project)['layers']:return copy.deepcopy(project)
    candidate=project
    for key in ('ecuador-national','ecuador-provinces','galapagos'):candidate,_=reference(candidate,key)
    candidate=layer_command(candidate,{'action':'basemap','value':'osm'})
    return layer_command(candidate,{'action':'view','bbox':EXTENTS['Ecuador continental']})


def reference_panel(session):
    import streamlit as st
    from studio_sig_workspace import notify
    with st.expander('Capas de referencia',expanded=not bool(workspace_for(session.project)['layers'])):
        for key,label in NAMES.items():
            if st.button(label,key='sig_reference_'+key,width='stretch'):
                try:
                    before=workspace_for(session.project)['view']
                    candidate,_=reference(session.project,key)
                    candidate=layer_command(candidate,{'action':'view','bbox':before['bbox']})
                    session.commit(candidate);notify(session,'Referencia incorporada; geometrías y atribución conservadas.');st.rerun()
                except (ValueError,OSError,KeyError,TypeError) as error:st.error(str(error))
        st.caption('Referencias cartográficas, no límites oficiales. Latinoamérica: 20 países soberanos; escala 1:110M.')
        with st.expander('Países y licencias'):
            st.write(', '.join(catalog()['latin-america']['countries']))
            st.caption('geoBoundaries: CC BY 4.0. Natural Earth: dominio público. No se redistribuyen fuentes personales.')
    with st.container(horizontal=True,gap='xsmall'):
        for label,box in EXTENTS.items():
            if st.button({'Ecuador continental':'Ecuador','Galápagos':'Galápagos','Latinoamérica':'LatAm'}[label],key='sig_extent_'+label,help='Encuadrar '+label):
                try:
                    candidate=session.project
                    if label=='Latinoamérica':candidate,_=reference(candidate,'latin-america')
                    session.commit(layer_command(candidate,{'action':'view','bbox':box}));st.rerun()
                except (ValueError,OSError,KeyError,TypeError) as error:st.error(str(error))
    with st.expander('Fuentes de datos'):
        st.markdown('**CHIRPS · Climate Hazards Center, UCSB**')
        st.caption('Precipitación · 50°S–50°N · v2: 1981–presente del proveedor · 0,05° · mm/día · dominio público. La fecha solicitada debe verificarse; no se garantiza disponibilidad reciente.')
        st.link_button('Datos y condiciones CHIRPS','https://chc.ucsb.edu/data/chirps')
        st.markdown('**NASA POWER**')
        st.caption('Meteorología regional diaria · precipitación, temperatura y viento · resolución/unidades según producto. Conector existente; consulta y descarga original distintas de un servicio de imagen.')
        st.link_button('Documentación POWER','https://power.larc.nasa.gov/docs/services/api/temporal/daily/')
        st.markdown('**INAMHI · Ecuador**')
        st.caption('Estaciones y observaciones diarias. Cobertura, parámetros y condiciones dependen de la estación; no equivalen a promedios provinciales.')
        st.link_button('Información pública INAMHI','https://www.inamhi.gob.ec/info-liberada/')
        st.caption('Descarga integrada con estimación, cancelación y incorporación automática: pendiente de conectar los adaptadores existentes. El ejemplo CHIRPS local se abre desde Inicio.')


def local_chirps_example():
    """Read three cached originals, crop native cells; no download or aggregation."""
    import rasterio
    from rasterio.windows import from_bounds,Window
    from rasterio.io import MemoryFile
    from data import rain_path,ROOT
    from studio_home import create_project
    from studio_sig_raster import add_raster,digest
    from studio_sig_timelapse import configure
    receipts=list((ROOT/'_local/climate-studio').glob('*/download-receipt.json'))
    verified={}
    for path in receipts:
        value=json.loads(path.read_text(encoding='utf-8'))
        for entry in value.get('files',[]):
            if 'sha256' in entry and 'source_url' in entry:verified[(entry.get('date'),entry['source_url'])]=entry['sha256']
    project=initial_map(create_project('free',{'id':'youtube'},name='CHIRPS v2 · ejemplo real · 1–3 enero 2024'))
    from studio_workspace_commands import workspace_command
    project=workspace_command(project,project['studio']['timeline'][0],{'action':'scene_properties','duration':.2})
    layers=[]
    for day in ('2024-01-01','2024-01-02','2024-01-03'):
        path,url=rain_path(day,allow_download=False);sha=digest(path)
        if verified.get((day,url))!=sha:raise ValueError('El original CHIRPS no coincide con su recibo local: '+day)
        with rasterio.open('/vsigzip/'+path.resolve().as_posix()) as ds:
            win=from_bounds(-81.5,-5.2,-75.,1.8,ds.transform).round_offsets().round_lengths()
            win=win.intersection(Window(0,0,ds.width,ds.height));profile=ds.profile.copy()
            # UCSB CHIRPS FAQ defines bad values as -9999 even when the old
            # TIFF omits the tag. Declare the provider mask in this derivative;
            # raw cell values and cached original bytes remain unchanged.
            profile.update(width=int(win.width),height=int(win.height),transform=ds.window_transform(win),compress='deflate',nodata=-9999.)
            with MemoryFile() as memory:
                with memory.open(**profile) as out:
                    out.write(ds.read(window=win));out.scales=ds.scales;out.offsets=ds.offsets
                    out.update_tags(original_sha256=sha,original_url=url,native_window=json.dumps(win.flatten()),
                        provider_nodata=-9999,provider_nodata_definition='https://wiki.chc.ucsb.edu/index.php?title=CHIRPS_FAQ')
                content=memory.read()
        project,lid=add_raster(project,content,'CHIRPS v2 · '+day+'.tif',
            {'citation':'CHIRPS v2 daily · Climate Hazards Center, UCSB · recorte nativo, sin remuestreo; NoData=-9999 según CHIRPS FAQ · original gzip SHA256 '+sha,
             'url':url,'license':'Dominio público CHIRPS; https://chc.ucsb.edu/data/chirps'},observed_date=day,
             variable='Precipitación diaria CHIRPS v2',units='mm/día',semantics='precipitation')
        layers.append(lid)
    project=configure(project,layers,duration=3.,cadence='daily')
    return layer_command(project,{'action':'view','bbox':EXTENTS['Ecuador continental']})
