"""GeoTIFF tools within the existing inspector and temporal strip."""
import json
import streamlit as st
from studio_sig_layers import workspace_for,layer_command
from studio_sig_raster import add_raster,calculate,zonal,settings
from studio_sig_workspace import choose_tool,notify,preferences


def import_panel(session):
    upload=st.file_uploader('Archivo GeoTIFF',type=['tif','tiff'],max_upload_size=32,key='sig_raster_upload')
    st.caption('CRS del archivo obligatorio. Original intacto; vista limitada a 512 px, vecino más próximo. Consulta de valores nativos.')
    with st.form('sig_raster_import'):
        observed=st.text_input('Fecha observada (AAAA-MM-DD)',key='sig_raster_date',help='Fecha real del producto. Deja vacío para una capa estática, como un DEM; no se infiere del nombre.')
        variable=st.text_input('Variable',key='sig_raster_variable')
        units=st.text_input('Unidades',key='sig_raster_units')
        semantics=st.selectbox('Significado',['scalar','precipitation','temperature'],format_func=lambda v:{'scalar':'Escalar sin agregación temporal','precipitation':'Precipitación','temperature':'Temperatura'}[v],key='sig_raster_semantics')
        band=st.number_input('Banda',min_value=1,max_value=100,value=1,key='sig_raster_band')
        citation=st.text_input('Procedencia',key='sig_raster_citation')
        license=st.text_input('Licencia o condiciones',key='sig_raster_license')
        accept=st.form_submit_button('Incorporar GeoTIFF',key='sig_raster_submit')
    if accept:
        try:
            if upload is None:raise ValueError('Selecciona un GeoTIFF.')
            candidate,_=add_raster(session.project,upload.getvalue(),upload.name,{'citation':citation,'license':license,'url':''},
                observed_date=observed.strip() or None,variable=variable,units=units,semantics=semantics,band=int(band))
            session.commit(candidate);choose_tool(session,'Propiedades');notify(session,'GeoTIFF incorporado, con máscara, CRS y valores nativos.');st.rerun()
        except (ValueError,TypeError,KeyError,OSError) as error:st.error('No se incorporó el ráster: '+str(error))


def inspector(session,layer,source,commit):
    from pyproj import CRS
    st.markdown('**'+layer['name']+'**');st.caption('GeoTIFF · '+source['variable']+' · '+source['units'])
    section=st.segmented_control('Propiedades ráster',['Estilo','Datos','Procedencia'],default='Datos',key=session.key+'_raster_inspector',persist_state='session')
    if section=='Estilo':
        with st.form('sig_raster_style'):
            opacity=st.slider('Opacidad',0.,1.,float(layer['style']['opacity']),.05,key='sig_raster_opacity')
            st.caption('Paleta continua azul. La comparación utiliza un único rango de valores nativos de ambas fechas.')
            if st.form_submit_button('Aplicar opacidad'):
                commit({'action':'style','layer_id':layer['id'],'style':{**layer['style'],'opacity':opacity}});st.rerun()
        for label,offset in [('Subir',1),('Bajar',-1)]:
            if st.button(label,key='sig_raster_order_'+str(offset)):commit({'action':'order','layer_id':layer['id'],'offset':offset});st.rerun()
        if st.button('Quitar capa de la vista',key='sig_raster_remove'):commit({'action':'remove','layer_id':layer['id']});st.rerun()
    elif section=='Datos':
        st.write('Fecha: '+(source['date'] or 'Producto derivado; consulta las fechas de entrada'))
        stats=source['raster']['statistics'];st.caption(f"Cobertura finita: {stats['valid']}/{stats['cells']} celdas ({stats['coverage']:.1%})")
        st.table([{'Estadística':k,'Valor':v,'Unidad':source['units']} for k,v in stats.items() if k in ('min','max','mean')],alt='Estadísticas nativas, no calculadas desde píxeles de pantalla')
        pixel=session.state.get(session.key+'_sig_pixel')
        if pixel and pixel['source_sha256']==source['sha256']:
            st.markdown('**Consulta en el mapa**')
            st.write('Sin dato' if pixel['value'] is None else f"{pixel['value']:g} {pixel['units']}")
            st.caption(f"Fila {pixel['row']} · columna {pixel['column']} · {pixel['status']}")
        else:st.caption('Haz clic en el mapa para consultar una celda de la capa activa.')
    else:
        st.write(source['provenance']['citation']);st.caption(source['provenance']['license'])
        st.write('CRS nativo: '+CRS.from_wkt(source['native_crs']).to_string())
        st.caption('La representación EPSG:4326 no modifica originales, resolución ni resultados científicos.')
        with st.expander('Hash, máscara y parámetros nativos'):st.json(source)
    if st.button('Comparar o calcular',key='sig_raster_tools'):choose_tool(session,'Ráster y tiempo');st.rerun()
    from pathlib import Path
    st.download_button('Descargar GeoTIFF original',Path(source['path']).read_bytes(),file_name=source['name'],key='sig_raster_export')


def analysis_panel(session):
    state=workspace_for(session.project);registry=session.project['studio']['geography']
    rasters=[lid for lid in state['order'] if state['layers'][lid]['type']=='raster']
    if not rasters:st.info('Importa al menos un GeoTIFF con fecha y unidades.');return
    name=lambda lid:state['layers'][lid]['name']
    tool=st.selectbox('Operación ráster',['Comparar fechas','Diferencia B − A','Media de dos observaciones','Estadísticas zonales'],key='sig_raster_tool')
    with st.form('sig_raster_operation'):
        first=st.selectbox('Ráster A',rasters,format_func=name,key='sig_raster_first')
        if tool=='Estadísticas zonales':
            vectors=[lid for lid in state['order'] if state['layers'][lid]['type']=='vector']
            if not vectors:st.info('Importa polígonos para definir las zonas.');return
            second=st.selectbox('Zonas vectoriales',vectors,format_func=name,key='sig_raster_zones')
            st.caption('Centros de píxel nativo. Cobertura referida a la intersección del polígono con la extensión del ráster; no mide áreas ni representa capitales.')
        else:
            second=st.selectbox('Ráster B',rasters,index=min(1,len(rasters)-1),format_func=name,key='sig_raster_second')
            st.caption('Misma variable y unidad. Los cálculos requieren cuadrículas alineadas. La media es de dos observaciones, no un promedio anual.')
        accept=st.form_submit_button('Aplicar operación',key='sig_raster_run')
    if accept:
        try:
            if tool=='Comparar fechas':
                ids=sorted([first,second],key=lambda lid:registry['sources'][state['layers'][lid]['source_id']]['date'] or '')
                candidate=layer_command(session.project,{'action':'raster_time','value':{'layers':ids,'index':0,'compare':True}})
                candidate=layer_command(candidate,{'action':'raster_date','index':0})
                session.commit(candidate);preferences(session)['time']=True;choose_tool(session,'Propiedades');st.rerun()
            elif tool=='Estadísticas zonales':
                from studio_sig_raster import zonal_layer
                candidate,_=zonal_layer(session.project,first,second)
                session.commit(candidate);choose_tool(session,'Propiedades');preferences(session)['dock']=True;st.rerun()
            else:
                candidate,_=calculate(session.project,[first,second],'difference' if tool.startswith('Diferencia') else 'mean',tool+'.tif')
                session.commit(candidate);choose_tool(session,'Propiedades');st.rerun()
        except (ValueError,TypeError,KeyError,OSError) as error:st.error('No se aplicó la operación: '+str(error))


def time_strip(session):
    state=workspace_for(session.project);time=state['raster_time'];registry=session.project['studio']['geography']
    sources=[registry['sources'][state['layers'][lid]['source_id']] for lid in time['layers']]
    with st.container(key='sig_time',gap='small'):
        with st.container(horizontal=True,gap='xsmall'):
            current=st.selectbox('Fecha geográfica',list(range(len(sources))),index=time['index'],format_func=lambda i:sources[i]['date'],key='sig_geographic_date_'+str(session.version))
            compare=st.checkbox('Comparar ambas fechas',value=time['compare'],disabled=len(sources)!=2,key='sig_geographic_compare_'+str(session.version))
            if current!=time['index'] or compare!=time['compare']:
                candidate=layer_command(session.project,{'action':'raster_time','value':{**time,'compare':compare}})
                session.commit(layer_command(candidate,{'action':'raster_date','index':current}));st.rerun()
        scale=settings(sources)
        st.caption(f"Escala común {scale['stops'][0]:g} — {scale['stops'][-1]:g} {sources[0]['units']} · fechas observadas, sin interpolación" if scale else 'Ambas fechas sin cobertura; sin escala numérica inventada.')
        with st.container(horizontal=True,gap='xsmall'):
            if st.button('Enviar a Studio',key='sig_series_review',type='primary'):
                choose_tool(session,'Serie para Studio');st.rerun()
            if st.button('Ajustar timelapse',key='sig_adjust_timelapse'):
                choose_tool(session,'Preparar timelapse');st.rerun()
            if st.button('Cerrar serie',key='sig_close_raster_time'):
                import copy
                candidate=copy.deepcopy(session.project);candidate['studio']['geography']['map_workspace'].pop('raster_time')
                session.commit(candidate);st.rerun()
        duration=time.get('duration',3.)
        st.caption(f"{len(sources)} observaciones · {duration:g} s de video · igual tiempo por observación · mapa base excluido de Studio")


def timelapse_panel(session):
    from output_profiles import PRESETS,profile_for
    from studio_sig_timelapse import configure,gaps
    state=workspace_for(session.project);registry=session.project['studio']['geography'];previous=state.get('raster_time',{})
    rasters=[lid for lid in state['order'] if state['layers'][lid]['type']=='raster' and registry['sources'][state['layers'][lid]['source_id']]['date'] is not None]
    st.markdown('**Preparar timelapse**')
    st.caption('Capas geográficas consultables. Inicio y final se eligen mediante las observaciones incluidas; no se rellenan huecos.')
    if len(rasters)<2:st.info('Añade al menos dos GeoTIFF con fechas. Las capas estáticas permanecen en el mapa.');return
    current=session.project['studio']['output_profile'];pid=current['id']
    with st.form('sig_timelapse_plan'):
        ids=st.multiselect('Observaciones',rasters,default=previous.get('layers',rasters[:32]),
            format_func=lambda lid:registry['sources'][state['layers'][lid]['source_id']]['date']+' · '+state['layers'][lid]['name'],key='sig_timelapse_layers')
        cadence=st.selectbox('Cadencia científica',['daily','monthly','irregular'],index=['daily','monthly','irregular'].index(previous.get('cadence','irregular')),
            format_func=lambda v:{'daily':'Diaria','monthly':'Mensual','irregular':'Otra / irregular'}[v],key='sig_timelapse_cadence',
            help='Cadencia declarada de las observaciones seleccionadas. No agrega datos ni cambia el intervalo o las unidades originales del producto.')
        duration=st.number_input('Duración del video (s)',min_value=.1,max_value=120.,value=float(previous.get('duration',3.)),step=.1,key='sig_timelapse_duration')
        options=['youtube','tiktok','instagram_square','custom']
        selected=st.selectbox('Formato de salida',options,index=options.index(pid) if pid in options else 0,
            format_func=lambda v:{'youtube':'Horizontal 16:9 · YouTube','tiktok':'Vertical 9:16 · Reels / Shorts / TikTok','instagram_square':'Cuadrado 1:1','custom':'Dimensiones personalizadas'}[v],key='sig_timelapse_profile')
        # Always visible: forms submit atomically, so changing a selector cannot
        # silently submit stale dimensions or force an intermediate rerun.
        w=st.number_input('Ancho personalizado (px)',160,3840,int(profile_for(current).width),2,key='sig_timelapse_width')
        h=st.number_input('Alto personalizado (px)',160,3840,int(profile_for(current).height),2,key='sig_timelapse_height')
        guides=st.checkbox('Guías editoriales de seguridad',value=previous.get('safe_guides',True),key='sig_timelapse_guides')
        st.caption('Cambiar el formato adapta las escenas existentes mediante el comando de Studio. No mejora la resolución científica; deshacer conserva el diseño anterior.')
        accepted=st.form_submit_button('Aplicar timelapse y encuadre',type='primary',key='sig_timelapse_apply')
    if accepted:
        try:
            profile={'id':selected}
            if selected=='custom':profile.update(width=int(w),height=int(h))
            candidate=configure(session.project,ids,duration=duration,cadence=cadence,profile=profile,safe_guides=guides)
            session.commit(candidate);preferences(session)['time']=True;choose_tool(session,'Propiedades');st.rerun()
        except (ValueError,KeyError,TypeError,OSError) as error:st.error('No se configuró la serie: '+str(error))
    if previous:
        dates=[registry['sources'][state['layers'][lid]['source_id']]['date'] for lid in previous['layers']]
        holes=gaps(dates,previous.get('cadence','irregular'))
        if holes:st.warning('Hay intervalos sin observación; no se interpolarán.');st.table(holes)
        st.caption('El marco turquesa indica la ventana geográfica enviada; título, fecha, leyenda y créditos se añaden como elementos editables en Studio.')


def series_review(session):
    from studio_map_bundles import prepare_geographic_bundle
    from studio_map_ui import show_layer_review
    key=session.key+'_sig_series';record=session.state.get(key+'_record')
    if record is None:
        st.markdown('**Preparar serie para Studio**')
        time=workspace_for(session.project).get('raster_time')
        if not time:st.info('Prepara primero el timelapse en el mapa.');return
        st.caption(f"{len(time['layers'])} observaciones reales · RGBA · fecha protegida · escala común · originales vinculados.")
        st.caption('Se conserva la extensión y la opacidad común de ambas capas. Si difieren, iguálalas antes de preparar.')
        duration=st.number_input('Duración del video de comprobación (s)',min_value=.1,max_value=120.,value=float(time.get('duration',3.)),step=.1,key='sig_series_duration')
        if st.button('Preparar y revisar serie',key='sig_series_prepare'):
            try:
                session.state[key+'_record']=prepare_geographic_bundle(session.project,duration)
                session.state[key+'_dialog']='map_layers';st.rerun()
            except (ValueError,TypeError,KeyError,OSError) as error:st.error('No se preparó la serie: '+str(error))
        return
    if key+'_dialog' not in session.state:
        session.state.pop(key+'_record',None);choose_tool(session,'Propiedades');st.rerun()
    def publish(candidate):
        session.commit(candidate);session.state[session.key+'_selected']=candidate['studio']['timeline'][-1]
        session.state.pop(key+'_record',None)
        from studio_project import request_studio_navigation
        request_studio_navigation(session.state)
    show_layer_review(session,key,record,publish_label='Enviar serie a Studio',publisher=publish)
