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


def analysis_panel(session,*,show_heading=True):
    state=workspace_for(session.project);registry=session.project['studio'].get('geography',{'sources':{}})
    rasters=[lid for lid in state['order'] if state['layers'][lid]['type']=='raster']
    if not rasters:st.info('Importa al menos un GeoTIFF con fecha y unidades.');return
    name=lambda lid:state['layers'][lid]['name']
    from studio_sig_tool_catalog import RASTER_TOOLS
    tool=st.selectbox('Operación ráster',[item['label'] for item in RASTER_TOOLS],key='sig_raster_tool')
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
        accept=st.form_submit_button('Aplicar comparación' if tool=='Comparar fechas' else 'Calcular en segundo plano',key='sig_raster_run')
    if accept:
        try:
            if tool=='Comparar fechas':
                ids=sorted([first,second],key=lambda lid:registry['sources'][state['layers'][lid]['source_id']]['date'] or '')
                candidate=layer_command(session.project,{'action':'raster_time','value':{'layers':ids,'index':0,'compare':True}})
                candidate=layer_command(candidate,{'action':'raster_date','index':0})
                session.commit(candidate);preferences(session)['time']=True;choose_tool(session,'Propiedades');st.rerun()
            elif tool=='Estadísticas zonales':
                from studio_sig_analysis_ui import queue
                queue(session,{'kind':'raster','layers':[first,second],'tool':'zonal','name':'Estadísticas zonales'});st.rerun()
            else:
                from studio_sig_analysis_ui import queue
                queue(session,{'kind':'raster','layers':[first,second],'tool':'difference' if tool.startswith('Diferencia') else 'mean','name':tool+'.tif'});st.rerun()
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


def timelapse_panel(session,*,show_heading=True):
    from output_profiles import PRESETS,profile_for
    from studio_sig_timelapse import configure,gaps
    if show_heading:st.markdown('**Preparar timelapse**')
    st.caption('Fuente → variable → fechas → territorio → formato → Studio. Sin rellenar fechas ni alterar datos originales.')
    from studio_sig_series_ui import acquire_panel
    from studio_sig_series import series_groups
    acquire_panel(session)
    state=workspace_for(session.project);registry=session.project['studio'].get('geography',{'sources':{}});previous=state.get('raster_time',{})
    groups=series_groups(session.project)
    if not groups:st.info('Todavía no hay observaciones fechadas. Descarga una serie o importa tus GeoTIFF desde el selector de fuente. Los DEM y otras capas estáticas no se animan.');return
    # Dependent choices must rerun immediately, outside the atomic apply form.
    imported=set(session.state.get(session.key+'_series_imported',previous.get('layers',[])))
    import hashlib
    inventory=hashlib.sha256(str([(g['id'],len(g['layers'])) for g in groups]).encode()).hexdigest()[:12]
    origins=list(dict.fromkeys(g['source'] for g in groups))
    preferred=next((g for g in groups if imported.intersection(g['layers'])),groups[0])
    origin=st.selectbox('Fuente y producto disponibles',origins,index=origins.index(preferred['source']),key=session.key+'_series_origin_'+inventory)
    candidates=[g for g in groups if g['source']==origin]
    gid=st.selectbox('Variable y unidad',list(range(len(candidates))),index=candidates.index(preferred) if preferred in candidates else 0,
        format_func=lambda i:candidates[i]['variable']+' · '+candidates[i]['units'],key=session.key+'_series_variable_'+origin+'_'+inventory)
    group=candidates[gid];signature=group['id'];rasters=group['layers']
    from datetime import date
    lo=date.fromisoformat(group['dates'][0]);hi=date.fromisoformat(group['dates'][-1])
    period=st.date_input('Periodo a animar',value=(lo,hi),min_value=lo,max_value=hi,key=session.key+'_series_period_'+signature)
    if len(period)!=2:st.info('Selecciona también la fecha final.');return
    rasters=[lid for lid in rasters if period[0].isoformat()<=registry['sources'][state['layers'][lid]['source_id']]['date']<=period[1].isoformat()]
    if len(rasters)<2:st.info('El periodo seleccionado necesita al menos dos observaciones reales. Amplía las fechas o incorpora más datos.');return
    if len(rasters)>3600:st.warning('Este video admite como máximo 3600 observaciones en 120 segundos. Reduce el periodo; no se descartarán fechas automáticamente.');return
    current=session.project['studio']['output_profile'];pid=current['id']
    from studio_territory import options_for,province_names
    presentation=options_for(session.project)
    territories=['ecuador','continent','galapagos','province','view']
    territory=st.selectbox('Territorio de salida',territories,index=territories.index(presentation['territory']),
        format_func=lambda value:{'ecuador':'Ecuador continental + Galápagos','continent':'Solo Ecuador continental','galapagos':'Solo Galápagos','province':'Una provincia','view':'Región de la vista SIG'}[value],key='sig_export_territory')
    province=None
    if territory=='province':
        names=province_names();province=st.selectbox('Provincia',names,index=names.index(presentation.get('province','Napo')),key='sig_export_province')
    st.caption(f"{len(rasters)} observaciones disponibles · {group['variable']} · {group['units']} · una escala común. No se mezclarán otros productos ni variables.")
    with st.form('sig_timelapse_plan'):
        selected_previous=[lid for lid in previous.get('layers',[]) if lid in rasters]
        ids=st.multiselect('Observaciones',rasters,default=selected_previous or rasters,
            format_func=lambda lid:registry['sources'][state['layers'][lid]['source_id']]['date']+' · '+state['layers'][lid]['name'],key='sig_timelapse_layers_'+signature+'_'+str(period))
        default_cadence=previous.get('cadence','irregular') if selected_previous else ('daily' if imported.intersection(rasters) else 'irregular')
        cadence=st.selectbox('Cadencia científica',['daily','monthly','irregular'],index=['daily','monthly','irregular'].index(default_cadence),
            format_func=lambda v:{'daily':'Diaria','monthly':'Mensual','irregular':'Otra / irregular'}[v],key='sig_timelapse_cadence_'+signature,
            help='Cadencia declarada de las observaciones seleccionadas. No agrega datos ni cambia el intervalo o las unidades originales del producto.')
        import math
        minimum=max(.1,math.ceil(len(rasters)/3)/10)
        duration=st.number_input('Duración del video (s)',min_value=minimum,max_value=120.,value=min(120.,max(minimum,float(previous.get('duration',max(3.,len(rasters)/10))))),step=.1,key='sig_timelapse_duration_'+signature+'_'+str(len(rasters)))
        resampling=st.selectbox('Presentación',['nearest','bilinear'],index=['nearest','bilinear'].index(presentation['resampling']),
            format_func=lambda value:'Celdas nativas' if value=='nearest' else 'Suavizado visual',key='sig_export_resampling')
        borders=st.checkbox('Contorno del territorio',value=presentation['borders'],key='sig_export_borders')
        provinces=st.checkbox('Límites provinciales',value=presentation['provinces'],key='sig_export_provinces')
        st.caption('Suavizado visual; resolución original conservada. Los cálculos y las descargas usan las celdas originales. La navegación SIG sigue libre.')
        options=list(PRESETS)+['custom']
        selected=st.selectbox('Formato de salida',options,index=options.index(pid) if pid in options else 0,
            format_func=lambda v:(f'{PRESETS[v][0]} · {PRESETS[v][1]} × {PRESETS[v][2]}' if v in PRESETS else 'Dimensiones personalizadas'),key='sig_timelapse_profile')
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
            options={'territory':territory,'resampling':resampling,'borders':borders,'provinces':provinces}
            if province:options['province']=province
            candidate=configure(session.project,ids,duration=duration,cadence=cadence,profile=profile,safe_guides=guides,
                presentation=options)
            session.commit(candidate);preferences(session)['time']=True;choose_tool(session,'Propiedades');st.rerun()
        except (ValueError,KeyError,TypeError,OSError) as error:st.error('No se configuró la serie: '+str(error))
    if previous:
        dates=[registry['sources'][state['layers'][lid]['source_id']]['date'] for lid in previous['layers']]
        holes=gaps(dates,previous.get('cadence','irregular'))
        if holes:st.warning('Hay intervalos sin observación; no se interpolarán.');st.table(holes)
        st.caption('El marco turquesa indica la ventana geográfica enviada; título, fecha, leyenda y créditos se añaden como elementos editables en Studio.')
        if session.project['studio'].get('sig_transfer') or session.project['studio'].get('sig_map_transfer'):
            st.info('Studio conserva la última serie enviada con sus propios datos. Aplica esta preparación y pulsa Enviar a Studio para actualizar el video; cambiar la selección del SIG no reemplaza un video ya armado.')


def series_review(session):
    from studio_map_bundles import prepare_geographic_bundle
    from studio_map_ui import show_layer_review
    key=session.key+'_sig_series';record=session.state.get(key+'_record')
    if record is None:
        st.markdown('**Preparar serie para Studio**')
        time=workspace_for(session.project).get('raster_time')
        if not time:st.info('Prepara primero el timelapse en el mapa.');return
        st.caption(f"{len(time['layers'])} observaciones reales · RGBA · fecha protegida · escala común · originales vinculados.")
        st.caption('Se usa el territorio de salida elegido y la opacidad común de las fechas. El mapa base se excluye. Galápagos sin cobertura verificable queda transparente.')
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
        session.state.pop(session.key+'_sig_dialog',None)
        from studio_project import request_studio_navigation
        request_studio_navigation(session.state)
    show_layer_review(session,key,record,publish_label='Enviar serie a Studio',publisher=publish)
