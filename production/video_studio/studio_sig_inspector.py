"""Contextual presentation only; originals and commands keep their existing owner."""
import html
import streamlit as st
from studio_sig_layers import workspace_for
from studio_geography import region_feature


def layer_list(session, action, commit):
    state=workspace_for(session.project)
    from studio_sig_references import reference_panel
    reference_panel(session)
    query=st.text_input('Buscar capas',key=session.key+'_sig_layer_search',
                        placeholder='Buscar por nombre…',icon=':material/search:',persist_state='session')
    if st.button('Importar datos',key='sig_import_from_layers',icon=':material/upload:',width='stretch'):
        from studio_sig_workspace import choose_tool
        choose_tool(session,'Datos');st.rerun()
    if st.button('Preparar timelapse',key='sig_timelapse_from_layers',icon=':material/timelapse:',type='primary',width='stretch'):
        from studio_sig_workspace import choose_tool
        choose_tool(session,'Preparar timelapse');st.rerun()
    visible=[lid for lid in reversed(state['order']) if query.casefold() in state['layers'][lid]['name'].casefold()]
    st.caption(f"{len(state['layers'])} capas · arriba primero")
    if not visible:
        st.caption('No hay coincidencias.' if state['layers'] else 'Importa un archivo geográfico para comenzar. Tus fuentes conservan su procedencia.')
    def row(lid):
        layer=state['layers'][lid]
        source=session.project['studio']['geography']['sources'][layer['source_id']]
        with st.container(key='sig_layer_row_'+lid,gap=None):
            with st.container(horizontal=True,gap='xsmall',vertical_alignment='center'):
                widget='sig_visible_'+lid+'_'+str(session.version)
                def visibility(lid=lid,widget=widget):
                    try:commit({'action':'visibility','layer_id':lid,'visible':st.session_state[widget]})
                    except (ValueError,TypeError,KeyError,OSError) as error:
                        from studio_sig_workspace import notify
                        notify(session,error,'error')
                        st.session_state[session.key+'_sig_map_error']=str(error)
                st.checkbox('Visible '+layer['name'],value=layer['visible'],key=widget,
                            on_change=visibility,label_visibility='collapsed',help='Mostrar u ocultar '+layer['name'])
                fill=html.escape(layer['style']['fill'],quote=True)
                stroke=html.escape(layer['style']['stroke'],quote=True)
                st.html(f'<span class="sig-swatch" style="background:{fill};border-color:{stroke}" aria-label="Muestra del estilo"></span>')
                action(layer['name'],{'action':'active','layer_id':lid},'sig_active_'+lid,
                       type='primary' if lid==state['active_layer'] else 'secondary',
                       width='stretch',help=layer['name']+' · '+layer['native_crs'],wrap=False)
            source=session.project['studio']['geography']['sources'][layer['source_id']]
            kind='GEOTIFF' if layer['type']=='raster' else source.get('origin',{}).get('format','GeoJSON').upper()
            from pyproj import CRS
            native=CRS.from_user_input(layer['native_crs']).to_string()
            # Type/CRS remain in the contextual inspector and accessible tooltip.
    temporal=state.get('raster_time',{}).get('layers',[])
    for category,title in [('reference','Capas de referencia'),('files','Mis archivos'),('results','Resultados')]:
        ids=[lid for lid in visible if state['layers'][lid].get('group','results' if session.project['studio']['geography']['sources'][state['layers'][lid]['source_id']].get('operation') or session.project['studio']['geography']['sources'][state['layers'][lid]['source_id']].get('raster_operation') else 'files')==category]
        if not ids:continue
        group_container=st.container(key='sig_layer_group_files') if category=='files' else st.expander(title+' · '+str(len(ids)),expanded=True,key='sig_layer_group_'+category)
        with group_container:
            if category=='files':st.markdown('**'+title+' · '+str(len(ids))+'**')
            series=[lid for lid in ids if lid in temporal]
            if series:
                st.markdown('**Serie temporal**')
                selected=temporal[state['raster_time']['index']]
                if selected in series:row(selected)
                with st.expander(str(len(series))+' observaciones · consultar capas',key='sig_series_observations'):
                    for lid in series:
                        if lid!=selected:row(lid)
            for lid in ids:
                if lid not in series:row(lid)


def inspector(session,action,commit):
    state=workspace_for(session.project)
    active=state['layers'].get(state['active_layer'])
    if active is None:
        st.caption('Selecciona una capa para consultar estilo, datos y procedencia.');return
    source=session.project['studio']['geography']['sources'][active['source_id']]
    if active['type']=='raster':
        from studio_sig_raster_ui import inspector
        inspector(session,active,source,commit);return
    from studio_sig_vector import layer_features
    _,features=layer_features(session.project,active['id'])
    types=', '.join(dict.fromkeys(f['geometry']['type'] for f in features))
    lid=active['id']
    name=html.escape(active['name'],quote=True)
    st.html(f'<div class="sig-layer-title" title="{name}"><strong>{name}</strong><small>Vector · {html.escape(types)}</small></div>')
    tab_key=session.key+'_sig_inspector_tab'
    if tab_key in session.state and session.state[tab_key] is None:
        session.state[tab_key]=session.state.get(tab_key+'_last','Estilo')
    def retain_section():
        value=session.state[tab_key]
        if value is None:session.state[tab_key]=session.state.get(tab_key+'_last','Estilo')
        else:session.state[tab_key+'_last']=value
    section=st.segmented_control('Propiedades de capa',['Estilo','Datos','Procedencia'],default='Estilo',
        key=tab_key,selection_mode='single',persist_state='session',width='stretch',on_change=retain_section)
    if section=='Estilo':
        group=st.selectbox('Grupo',['reference','files','results'],index=['reference','files','results'].index(active.get('group','files')),
            format_func=lambda v:{'reference':'Capas de referencia','files':'Mis archivos','results':'Resultados'}[v],key='sig_layer_group_'+lid+'_'+str(session.version))
        if group!=active.get('group','files'):commit({'action':'group','layer_id':lid,'group':group});st.rerun()
        with st.form('sig_style_'+lid+'_'+str(session.version)):
            fill=st.color_picker('Relleno',active['style']['fill'])
            stroke=st.color_picker('Contorno',active['style']['stroke'])
            opacity=st.slider('Opacidad',0.,1.,float(active['style']['opacity']),.05)
            if st.form_submit_button('Aplicar estilo',width='stretch'):
                commit({'action':'style','layer_id':lid,'style':{'fill':fill,'stroke':stroke,'opacity':opacity}});st.rerun()
        with st.container(horizontal=True,gap='xsmall'):
            action('Subir',{'action':'order','layer_id':lid,'offset':1},'sig_up',icon=':material/arrow_upward:')
            action('Bajar',{'action':'order','layer_id':lid,'offset':-1},'sig_down',icon=':material/arrow_downward:')
        with st.popover('Acciones de capa',icon=':material/more_horiz:',key='sig_layer_actions'):
            with st.form('sig_rename_'+lid):
                new_name=st.text_input('Nombre de capa',value=active['name'],key='sig_rename_name')
                if st.form_submit_button('Renombrar'):
                    commit({'action':'rename','layer_id':lid,'name':new_name});st.rerun()
            st.caption('Solo se retira la representación de la vista. Fuente y resultados se conservan.')
            action('Quitar capa de la vista',{'action':'remove','layer_id':lid},'sig_remove')
            from studio_sig_vector_ui import export_controls
            export_controls(session,lid)
    elif section=='Datos':
        from studio_sig_workspace import attribute_rows
        ids,rows=attribute_rows(session.project,lid)
        st.caption(f'{len(ids)} entidades · atributos originales de solo lectura')
        selected=state['selection']
        if selected:
            feature=region_feature(session.project,selected[0])
            st.markdown('**Entidad seleccionada**')
            st.table([{'Campo':key,'Valor':str(value) if value is not None else 'Sin dato (null)'}
                      for key,value in (feature.get('properties') or {}).items()],
                     alt='Campos de la entidad seleccionada, incluidos cero, negativos y datos ausentes')
        else:st.caption('Identifica una entidad en el mapa o selecciona una fila en Atributos.')
        st.caption('Campos: '+(', '.join(dict.fromkeys(key for row in rows for key in row)) or 'sin campos'))
        with st.expander('Detalles avanzados',key='sig_entity_advanced',on_change='rerun') as advanced:
            if advanced.open:
                st.json({'selection':selected,'layer_id':lid})
    else:
        provenance=source['provenance']
        st.markdown('**Fuente**');st.write(source['name'])
        st.markdown('**Procedencia**');st.write(provenance['citation'])
        st.markdown('**Condiciones de uso**');st.write(provenance['license'])
        st.caption('Los datos aportados no se redistribuyen automáticamente.')
        st.markdown('**Referencia espacial**')
        origin=source.get('origin')
        if origin:
            from pyproj import CRS
            st.write('Archivo original: '+CRS.from_wkt(origin['native_crs']).name)
            st.caption('Representación normalizada: CRS84 · PROJ x/y. Original '+origin['format'].upper()+' intacto.')
        else:st.write('Origen: '+source['native_crs'])
        st.caption('Vista EPSG:4326 · x longitud / y latitud. Original intacto.')
        if source.get('operation'):
            operation=source['operation'];st.markdown('**Resultado derivado**')
            st.write(operation['tool']+' · '+operation['processed_at']);st.caption('Unidades: '+(operation['units'] or 'sin unidad declarada'))
            with st.expander('Parámetros de la operación'):st.json(operation)
        boxes=[r['bbox'] for r in session.project['studio']['geography']['regions'].values() if r['source_id']==active['source_id']]
        if boxes:
            extent=[min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes)]
            st.markdown('**Cobertura de las entidades**')
            st.caption(f'{len(boxes)} entidades · lon {extent[0]:.4f} a {extent[2]:.4f}° · lat {extent[1]:.4f} a {extent[3]:.4f}°')
        if provenance.get('url'):st.link_button('Consultar fuente',provenance['url'])
        with st.expander('Identidad y detalles avanzados',key='sig_source_advanced',on_change='rerun') as advanced:
            if advanced.open:st.json({k:source[k] for k in ('id','sha256','bytes','native_crs')})
