"""SIG workspace presentation over the canonical document and existing tools.

Only panel/tool preferences live here. Geographic selection/view, scientific
time, sources and durable history remain owned by their existing contracts.
"""
import base64
import copy
import html
import io
import json
from pathlib import Path
import streamlit as st
from studio_sig_layers import workspace_for,layer_command
from studio_geography import read_source,_features

TOOLS=['Propiedades','Datos','Análisis vectorial','Ráster y tiempo','Preparar timelapse','Serie para Studio','Ciencia','Mapa observado','Secuencia temporal','Publicar vista']
ASSETS=Path(__file__).with_name('sig_map_frontend')


def preferences(session):
    key=session.key+'_sig_ui'
    if key not in session.state:
        session.state[key]={'left':True,'right':True,'dock':False,
                            'tool':'Propiedades' if workspace_for(session.project)['layers'] else 'Datos'}
    ui=session.state[key]
    ui.setdefault('dock_height',200)
    ui.setdefault('time',bool(workspace_for(session.project).get('raster_time') or session.project.get('project_meta',{}).get('scientific_revision') or
        any('temporal_map' in r for r in session.project['studio']['media'].values())))
    ui.setdefault('compact',False)
    return ui


def presentation_event(session,message):
    """Untrusted UI hints never change the canonical document or its history."""
    if not isinstance(message,dict):raise ValueError('Evento visual inválido.')
    ui=preferences(session)
    if message.get('action')=='viewport':
        width=message.get('width')
        if type(width) not in (int,float) or not 240<=width<=20000:raise ValueError('Ancho visual inválido.')
        compact=width<=1000
        if compact!=ui['compact']:
            ui.update(compact=compact,left=not compact,right=not compact)
    elif message.get('action')=='close_panels':ui.update(left=False,right=False)
    elif message.get('action')=='import':choose_tool(session,'Datos')
    elif message.get('action')=='timelapse':choose_tool(session,'Preparar timelapse')
    elif message.get('action')=='send_series':choose_tool(session,'Serie para Studio')
    elif message.get('action')=='compare_series':
        time=workspace_for(session.project).get('raster_time')
        if message.get('version')!=session.version or not time or len(time['layers'])!=2 or type(message.get('compare')) is not bool:
            raise ValueError('La comparación cambió; revisa las dos observaciones.')
        candidate=layer_command(session.project,{'action':'raster_time','value':{**time,'compare':message['compare']}})
        candidate=layer_command(candidate,{'action':'raster_date','index':message.get('index')})
        if candidate!=session.project:session.commit(candidate)
    elif message.get('action')=='query_raster':
        from studio_sig_raster import query
        state=workspace_for(session.project);lid=message.get('layer_id')
        if message.get('version')!=session.version or lid not in state['layers'] or state['layers'][lid]['type']!='raster':
            raise ValueError('La capa cambió. Vuelve a consultar el mapa actualizado.')
        source=session.project['studio']['geography']['sources'][state['layers'][lid]['source_id']]
        session.state[session.key+'_sig_pixel']=query(source,message.get('lon'),message.get('lat'))
    else:raise ValueError('Acción visual desconocida.')


def notify(session,text,kind='info'):
    key=session.key+'_sig_messages'
    item={'tipo':kind,'mensaje':str(text)};messages=session.state.get(key,[])
    if not messages or messages[-1]!=item:session.state[key]=(messages+[item])[-20:]


def choose_tool(session,tool):
    ui=preferences(session);ui['tool']=tool;ui['right']=True
    session.state[session.key+'_sig_requested_tool']=tool
    if tool in ('Mapa observado','Secuencia temporal'):
        session.state.pop(session.key+'_sig_preparation_'+('observation' if tool=='Mapa observado' else 'sequence')+'_opened',None)


def apply_requested_tool(session):
    """Set widget state before drawing, including after returning from Studio."""
    key=session.key+'_sig_tool'
    requested=session.state.pop(session.key+'_sig_requested_tool',None)
    if requested is not None:session.state[key]=requested
    elif key not in session.state:session.state[key]=preferences(session)['tool']


def attribute_rows(project,layer_id):
    """Original property values, stable region IDs; no geometry or scientific edit."""
    state=workspace_for(project);layer=state['layers'].get(layer_id)
    if layer is None:return [],[]
    registry=project['studio']['geography'];sid=layer['source_id']
    if layer['type']=='raster':return [],[]
    features=_features(read_source(registry['sources'][sid]))
    regions=[(rid,r) for rid,r in registry['regions'].items() if r['source_id']==sid]
    return [rid for rid,_ in regions],[copy.deepcopy(features[r['feature_index']].get('properties') or {}) for _,r in regions]


def select_attribute(session,layer_id,ids,rows,version):
    if version!=session.version:raise ValueError('La selección cambió. Vuelve a elegir una fila de la tabla actual.')
    if not isinstance(rows,list) or len(rows)>1 or any(type(i) is not int or not 0<=i<len(ids) for i in rows):
        raise ValueError('Fila de atributos inválida; no se cambió el proyecto.')
    message={'action':'select','layer_id':layer_id,'region_id':ids[rows[0]]} if rows else {'action':'clear_selection'}
    candidate=layer_command(session.project,message)
    if candidate!=session.project:session.commit(candidate)


def open_copy(session,document):
    """Prepare and save a new working copy before replacing the current UI state."""
    from studio_project import validate_document,replace_document,workspace_key,source_projection
    from studio_workspace import WorkspaceSession
    validated=validate_document(document);temporary={}
    candidate=replace_document(temporary,validated)
    WorkspaceSession(temporary,workspace_key(candidate),source_projection(candidate),store=session.store,canonical=True)
    session.state.update(temporary)


def toolbar(session):
    from studio_project import request_studio_navigation
    from studio_home import project_files
    from studio_recovery import recover_snapshot
    ui=preferences(session)
    with st.container(key='sig_topbar',horizontal=True,vertical_alignment='center',gap='xsmall'):
        st.html('<div id="sig-brand"><svg viewBox="0 0 32 32" aria-hidden="true"><path d="M4 26 15 8l12 18M9 20l6-4 6 4M15 8l3-5"/></svg><strong>EV</strong><span>Ecuador Vivo</span></div>')
        if st.button('Inicio',key='sig_home',icon=':material/home:',help='Proyectos y recuperación'):
            session.state['section']='Inicio';st.rerun()
        st.button('SIG',key='sig_current_workspace',disabled=True,icon=':material/layers:')
        if st.button('Studio',key='sig_studio',icon=':material/movie:',help='Abrir editor; no envía recursos'):
            request_studio_navigation(session.state);st.rerun()
        name=html.escape(str(session.project.get('name','Proyecto sin título')),quote=True)
        st.html('<div id="sig-project-name" title="'+name+'">'+name+'</div>')
        with st.popover('Abrir',icon=':material/folder_open:',key='sig_open_menu'):
            with st.form('sig_open_form'):
                saved=st.selectbox('Proyecto guardado',[None]+project_files(session.store/'projects'),
                    format_func=lambda p:'Selecciona una copia…' if p is None else p.stem,key='sig_open_saved')
                upload=st.file_uploader('Proyecto JSON',type=['json'],key='sig_open_file')
                accepted=st.form_submit_button('Abrir copia en SIG',key='sig_open_copy')
            if accepted:
                try:
                    previous=False
                    if upload is None and saved is None:raise ValueError('Selecciona un proyecto guardado o un archivo JSON para abrir una copia.')
                    if upload is not None:document=json.loads(upload.getvalue())
                    else:document,previous=recover_snapshot(saved)
                    open_copy(session,document)
                    if previous:notify(session,'Se recuperó la versión anterior del archivo.','aviso')
                    st.rerun()
                except (ValueError,TypeError,KeyError,OSError) as error:st.error(str(error))
            st.caption('Se abre una copia de trabajo; el archivo elegido se conserva.')
        if st.button('Guardar',key='sig_save_project',icon=':material/save:'):
            try:session.commit(session.project,record=False);notify(session,'Proyecto guardado y confirmado.');st.rerun()
            except (ValueError,TypeError,KeyError,OSError) as error:notify(session,error,'error');st.error(str(error))
        if st.button('Datos',key='sig_add_data',icon=':material/add:'):
            choose_tool(session,'Datos');st.rerun()
        if st.button('Análisis',key='sig_analyze',icon=':material/functions:'):
            choose_tool(session,'Análisis vectorial');st.rerun()
        with st.popover('Exportar',icon=':material/file_download:',key='sig_export_menu'):
            st.download_button('Proyecto JSON',json.dumps(session.project,ensure_ascii=False,indent=2,allow_nan=False),
                file_name='ecuador-vivo-proyecto.json',mime='application/json',key='sig_export_json')
            if st.button('Video en Studio',key='sig_export_studio'):
                request_studio_navigation(session.state);st.rerun()
        for label,operation,stack in [('Deshacer','undo','history'),('Rehacer','redo','future')]:
            if st.button(label,key='sig_'+operation,icon=':material/'+operation+':',help=label,
                disabled=not session.state.get(session.key+'_workspace_'+stack)):
                session.dispatch({'action':operation,'version':session.version,'scene':session.selected});st.rerun()
    with st.container(key='sig_save_status',horizontal=True,gap='xsmall'):
        st.caption('Último guardado confirmado '+str(session.state.get(session.key+'_saved_at','al abrir')))
        job=session.state.get('science_job')
        if job:
            from studio_preparation import preparation_status
            try:
                state=preparation_status(job)
                st.caption('Revisión científica: '+str(state.get('message',state.get('state',''))))
            except (ValueError,TypeError,KeyError,OSError) as error:
                st.caption('Preparación científica no disponible; consulta Mensajes.')
                notify(session,error,'error')
        from studio_map_jobs import map_status
        jobs={str(session.state[k]) for k in session.state if k.startswith(session.key+'_sig_preparation_') and '_map_job' in k}
        for job in jobs:
            try:
                state=map_status(job)
                if state.get('state') in ('queued','running'):st.caption('Mapa: '+str(state.get('message','Preparando')))
            except (ValueError,TypeError,KeyError,OSError) as error:notify(session,error,'error')
        st.caption('Fuentes y resultados vinculados al proyecto')


def import_panel(session):
    from studio_sig_layers import add_geojson_layer
    st.markdown('**Incorporar datos**')
    from studio_sig_vector_ui import import_general
    if import_general(session):return
    st.caption('GeoJSON RFC7946 · puntos, líneas y polígonos · hasta 8 MiB')
    with st.form('sig_u1_import'):
        upload=st.file_uploader('Archivo GeoJSON',type=['geojson','json'],key='sig_u1_upload',max_upload_size=8)
        citation=st.text_input('Procedencia',key='sig_u1_citation',max_chars=1000)
        license=st.text_input('Licencia o condiciones',key='sig_u1_license',max_chars=1000)
        with st.expander('Referencia pública opcional'):
            url=st.text_input('URL pública sin credenciales (opcional)',key='sig_u1_url',max_chars=1000)
        accepted=st.form_submit_button('Añadir capa GeoJSON',key='sig_u1_import_submit')
    if accepted:
        try:
            if upload is None:raise ValueError('Selecciona un archivo GeoJSON.')
            candidate,_=add_geojson_layer(session.project,upload.getvalue(),upload.name,{'citation':citation,'license':license,'url':url})
            if candidate!=session.project:session.commit(candidate)
            choose_tool(session,'Propiedades');notify(session,'Capa incorporada al mapa y al catálogo.');st.rerun()
        except (ValueError,TypeError,KeyError,OSError) as error:notify(session,error,'error');st.error('No se añadió la capa: '+str(error))
    st.caption('Tus fuentes no se redistribuyen automáticamente. Conexiones avanzadas pendientes.')


def tools_panel(session):
    ui=preferences(session)
    tool=st.selectbox('Herramienta',TOOLS,key=session.key+'_sig_tool',
        persist_state='session',label_visibility='collapsed')
    previous=ui['tool'];ui['tool']=tool
    if tool!=previous:
        # A new explicit tool choice may reopen its preparation; a rerun cannot.
        session.state.pop(session.key+'_sig_preparation_'+('observation' if tool=='Mapa observado' else 'sequence')+'_opened',None)
    if tool=='Datos':import_panel(session);return
    if tool=='Análisis vectorial':
        from studio_sig_vector_ui import analysis_panel
        analysis_panel(session);return
    if tool=='Ráster y tiempo':
        from studio_sig_raster_ui import analysis_panel
        analysis_panel(session);return
    if tool=='Preparar timelapse':
        from studio_sig_raster_ui import timelapse_panel
        timelapse_panel(session);return
    if tool=='Serie para Studio':
        from studio_sig_raster_ui import series_review
        series_review(session);return
    if tool=='Propiedades':return # Existing properties are rendered by the map surface.
    if tool=='Publicar vista':
        from studio_geographic_ui import show_geography
        show_geography(session,show_import=False);return
    from studio_science import restored_snapshot
    snapshot=restored_snapshot(session.project)
    if tool=='Ciencia':
        from studio_scientific_ui import show_scientific_assistant
        from studio_sig import merge_scientific_proposal
        def accept(proposal):
            candidate,selected=merge_scientific_proposal(session.project,proposal)
            if candidate!=session.project:session.commit(candidate)
            session.state[session.key+'_selected']=selected
            notify(session,'Resultados científicos incorporados al proyecto compartido.')
        show_scientific_assistant(session.project,accept,publish_label='Enviar resultados a Studio',
                                  shared_profile=session.project['studio']['output_profile']);return
    if snapshot is None:
        st.info('Prepara o abre una revisión científica antes de crear el mapa.');return
    # SIG preparation keys are isolated from Studio's dialog dispatcher.
    key=session.key+'_sig_preparation';structured=tool=='Mapa observado'
    key+='_'+('observation' if structured else 'sequence')
    if session.state.get(key+'_opened') and key+'_dialog' not in session.state:
        choose_tool(session,'Propiedades');st.rerun()
    session.state[key+'_opened']=True
    session.state.setdefault(key+'_dialog','observation_layers' if structured else 'temporal_map')
    from studio_map_ui import show_map_dialog
    from studio_sig import send_map
    if structured:
        dates=[r['date'] for r in snapshot['source_records']]
        date=st.selectbox('Fecha observada',dates,key=session.key+'_sig_observed_date',persist_state='session')
        index=dates.index(date)
        def publish(candidate):
            session.commit(candidate);session.state[session.key+'_selected']=candidate['studio']['timeline'][-1]
            from studio_project import request_studio_navigation
            request_studio_navigation(session.state)
        show_map_dialog(session,key,publish_label='Enviar capas a Studio',publisher=publish,
                        representation='rgba_observation_bundle',source_index=index)
    else:
        show_map_dialog(session,key,publish_label='Enviar mapa a Studio',publisher=lambda record:send_map(session,record))
    if key+'_dialog' not in session.state:choose_tool(session,'Propiedades');st.rerun()


def temporal_strip(session):
    """Resolve actual published observations using the existing CFR/calendar."""
    from studio_science import restored_snapshot
    maps={aid:r for aid,r in session.project['studio']['media'].items() if 'temporal_map' in r}
    preview=None
    ui=preferences(session)
    state=workspace_for(session.project)
    if state.get('raster_time'):
        # One CCv2 transport owns the date slider and playback; preparation and
        # publication still use the existing contextual tools and transactions.
        return None
    with st.container(key='sig_time',gap='xsmall'):
        with st.container(horizontal=True,gap='xsmall',vertical_alignment='center'):
            if st.button('Ocultar tiempo' if ui['time'] else 'Tiempo',key='sig_toggle_time',icon=':material/calendar_month:',
                         help='Mostrar u ocultar el calendario; conserva la fecha seleccionada'):
                ui['time']=not ui['time'];st.rerun()
            if not ui['time']:st.caption('Sin recurso temporal seleccionado' if not maps else f'{len(maps)} recursos temporales disponibles')
        if not ui['time']:return None
        with st.container(horizontal=True,gap='xsmall',vertical_alignment='center'):
            aid=st.selectbox('Vista temporal',[None]+list(maps),format_func=lambda k:'Mapa SIG' if k is None else maps[k]['name'],
                key=session.key+'_sig_temporal_asset',persist_state='session',label_visibility='collapsed')
            if st.button('Mapa observado',key='sig_prepare_layers',help='Preparar y revisar una observación real'):
                choose_tool(session,'Mapa observado');st.rerun()
            if st.button('Preparar secuencia',key='sig_prepare_map',help='Preparación cartográfica existente'):
                choose_tool(session,'Secuencia temporal');st.rerun()
        if aid is not None:
            from studio_media import AssetFrames
            from studio_temporal import observation,validate_resource
            record=maps[aid];validate_resource(record)
            total=record['temporal_map']['total_frames']
            frame=st.slider('Fotograma observado',0,total-1,0,key=session.key+'_sig_map_frame_'+record['temporal_manifest_sha256'][:16],
                label_visibility='collapsed',persist_state='session') if total>1 else 0
            current=observation(record,{},frame)
            with AssetFrames({aid:record},cache=session.cache.media) as assets:
                image=assets.at(frame/30,[{'id':'sig.preview','type':'video','style':{'asset_id':aid}}])['video.sig.preview']
                buffer=io.BytesIO();image.save(buffer,format='PNG')
            caption=current['date']+' · '+record['temporal_map']['units']+' · '+record['temporal_map']['citation']
            preview={'image':'data:image/png;base64,'+base64.b64encode(buffer.getvalue()).decode(),'caption':caption}
            with st.container(horizontal=True,gap='xsmall'):
                st.caption('Observación '+caption)
                if st.button('Enviar mapa a Studio',key='sig_send_map'):
                    from studio_sig import send_map
                    send_map(session,record);st.rerun()
            st.caption('Vista prerenderizada; no es una capa ráster georreferenciada. Reproducción continua en Studio.')
        else:
            snapshot=restored_snapshot(session.project)
            st.caption('Tiempo: '+(str(session.project.get('start',''))+' — '+str(session.project.get('end',''))+' · revisión disponible'
                if snapshot else 'sin capa temporal. Reproducción universal de capas pendiente.'))
    return preview


def bottom_panel(session):
    ui=preferences(session)
    with st.container(key='sig_dock',gap='xsmall'):
        with st.container(key='sig_dock_header',horizontal=True,gap='xsmall',vertical_alignment='center'):
            if st.button('Cerrar panel inferior' if ui['dock'] else 'Atributos, resultados y mensajes',
                     key='sig_toggle_dock',icon=':material/expand_more:' if ui['dock'] else ':material/expand_less:'):
                ui['dock']=not ui['dock'];st.rerun()
            if ui['dock']:
                with st.popover('Altura',icon=':material/height:',key='sig_dock_size'):
                    height=st.select_slider('Altura del panel',[160,200,280],value=ui['dock_height'],
                        key=session.key+'_sig_dock_height',persist_state='session')
                    if height!=ui['dock_height']:ui['dock_height']=height;st.rerun()
        if not ui['dock']:return
        tabs=st.tabs(['Atributos','Resultados','Mensajes'],key=session.key+'_sig_dock_tab',on_change='rerun')
        with tabs[0]:
            if tabs[0].open:
                state=workspace_for(session.project);lid=state['active_layer'];ids,rows=attribute_rows(session.project,lid)
                if not ids:st.caption('Selecciona una capa para consultar sus atributos.')
                else:
                    import pandas as pd
                    # JSON dictionaries/lists remain available in properties; display serialization is explicit.
                    display=[{k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in row.items()} for row in rows]
                    df=pd.DataFrame(display,index=ids)
                    if not len(df.columns):
                        from studio_sig_vector import layer_features
                        df['Geometría']=[f['geometry']['type'] for f in layer_features(session.project,lid)[1]]
                    selected=[ids.index(rid) for rid in state['selection'] if rid in ids]
                    table_key=session.key+'_sig_attributes_'+lid+'_'+str(session.version)
                    version=session.version
                    def selected_row():
                        try:select_attribute(session,lid,ids,session.state[table_key]['selection']['rows'],version)
                        except (ValueError,TypeError,KeyError,OSError) as error:notify(session,error,'error')
                    st.caption(state['layers'][lid]['name']+f' · {len(ids)} entidades · consulta sin modificar originales')
                    st.dataframe(df,height=max(80,ui['dock_height']-60),hide_index=True,selection_mode='single-row',on_select=selected_row,
                        selection_default={'selection':{'rows':selected}},key=table_key,
                        alt='Atributos originales de la capa activa; selección vinculada al mapa',placeholder='null')
        with tabs[1]:
            if tabs[1].open:
                registry=session.project['studio'].get('geography',{})
                state=workspace_for(session.project)
                derived=[]
                for sid,source in registry.get('sources',{}).items():
                    operation=source.get('operation',source.get('raster_operation'))
                    if operation:
                        layers=[layer['name'] for layer in state['layers'].values() if layer['source_id']==sid]
                        derived.append({'Resultado':source['name'],'Operación':operation['tool'],
                            'Unidad':operation['units'] or 'No declarada','Fecha de procesamiento':operation['processed_at'],
                            'Capas en la vista':', '.join(layers) or 'Retirada de la vista; fuente conservada',
                            'Fuentes de entrada':len(operation['inputs'])})
                if derived:
                    st.dataframe(derived,height=max(80,ui['dock_height']-60),hide_index=True,
                        alt='Capas derivadas y operaciones verificadas del proyecto')
                from studio_science import restored_snapshot
                snapshot=restored_snapshot(session.project)
                if snapshot:
                    st.dataframe([{'Resultado':rid,'Variable':r['variable'],'Unidad':r['units'],
                        'Valor':r.get('value'),'Estado':'Disponible' if r.get('value') is not None else 'Sin valor escalar',
                        'Filas':len(r.get('rows',[]))} for rid,r in snapshot['results'].items()],height=145,
                        hide_index=True,alt='Resultados numéricos y unidades de la revisión científica',placeholder='null')
                elif not derived:st.caption('No hay resultados aún. Ejecuta una operación vectorial o prepara una revisión científica.')
                media=[{'Recurso':r.get('name',aid),'Tipo':r.get('representation',r.get('type','')),'Referencia':aid}
                       for aid,r in session.project['studio']['media'].items() if 'temporal_map' in r or 'manifest_path' in r]
                if media:st.dataframe(media,height=100,hide_index=True,alt='Recursos cartográficos existentes de las operaciones')
        with tabs[2]:
            if tabs[2].open:
                messages=session.state.get(session.key+'_sig_messages',[])
                st.caption('Los gestos se confirman después del guardado durable. Los errores conservan el proyecto.')
                if messages:st.dataframe(messages,height=150,hide_index=True,alt='Mensajes y errores del espacio SIG')
                else:st.caption('Sin errores registrados en este espacio de trabajo.')
