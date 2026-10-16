"""Compact OpenLayers presentation over the shared project."""
import copy
import json
import streamlit as st
from studio_sig_layers import workspace_for,layer_command
from studio_sig_workspace import preferences,choose_tool,attribute_rows,notify


def result_rows(project):
    """Present the linked immutable calculations, without reading source pixels."""
    studio=project['studio'];rows=[]
    from studio_support import matching_results
    for rid in matching_results(project):
        result=studio.get('calculations',{}).get(rid)
        if not result:continue
        provenance=result['provenance'];period=provenance.get('period',{})
        value=result.get('value')
        rows.append({'Resultado':result['variable'],
            'Valor':round(value,2) if value is not None else f"{len(result.get('rows',[]))} filas",
            'Unidad':result['units'],'Periodo':f"{period.get('start','')} — {period.get('end','')}",
            'Método':provenance.get('method','No declarado'),'ID':rid,
            'Procedencia':provenance.get('source_records_ref','No declarada'),
            'Advertencias':'; '.join(provenance.get('warnings',[])) or 'Sin advertencias'})
    return rows or [{'Resultado':r.get('name',aid),'Tipo':r.get('representation',r.get('type',''))}
                   for aid,r in studio['media'].items()]


def shell_payload(session,layer_records=None):
    project=session.project;state=workspace_for(project);registry=project['studio'].get('geography',{'sources':{},'regions':{}})
    active=state['layers'].get(state['active_layer']);source=registry['sources'].get(active['source_id'],{}) if active else {}
    ids,rows=attribute_rows(project,state['active_layer'])
    from output_profiles import PRESETS,profile_for
    profile=profile_for(project['studio']['output_profile'])
    jobs=[]
    if session.state.get('science_job'):
        from studio_preparation import preparation_status
        try:jobs.append({'kind':'Ciencia',**preparation_status(session.state['science_job'])})
        except (ValueError,TypeError,KeyError,OSError) as error:notify(session,error,'error')
    from studio_map_jobs import map_status
    for key in list(session.state):
        if key.startswith(session.key+'_sig_preparation_') and '_map_job' in key:
            try:jobs.append({'kind':'Mapa',**map_status(session.state[key])})
            except (ValueError,TypeError,KeyError,OSError) as error:notify(session,error,'error')
    from studio_territory import options_for
    from pyproj import CRS
    source=copy.deepcopy(source)
    if source.get('native_crs'):source['native_crs_label']=CRS.from_user_input(source['native_crs']).to_string()
    from studio_support import grid_info
    from studio_sig_palette import PALETTES
    source['native_support']=grid_info(source)
    from studio_sig_tool_catalog import tool_catalog
    return {'name':project.get('name','Proyecto sin título'),'saved_at':session.state.get(session.key+'_saved_at','al abrir'),
        'export_presentation':options_for(project),'palettes':PALETTES,'tools':tool_catalog(project,layer_records),
        'can_undo':bool(session.state.get(session.key+'_workspace_history')),'can_redo':bool(session.state.get(session.key+'_workspace_future')),
        'profile':project['studio']['output_profile'],'dimensions':[profile.width,profile.height],
        'profiles':{pid:label for pid,(label,_,_) in PRESETS.items()},'source':copy.deepcopy(source),
        'attributes':{'ids':ids,'rows':rows[:100]},'messages':session.state.get(session.key+'_sig_messages',[]),'jobs':jobs,
        'results':result_rows(project),
        'scientific_note':'Vista EPSG:4326 · datos nativos y NoData conservados · escala común de la serie'}


def shell_event(session,message):
    if not isinstance(message,dict):raise ValueError('Evento SIG inválido.')
    action=message.get('action')
    if action=='operation':
        if message.get('version')!=session.version:raise ValueError('La capa cambió; selecciona la operación de nuevo.')
        from studio_sig_tool_catalog import launch_operation
        launch_operation(session,message.get('operation'));return
    if action=='send_series':
        from studio_sig_transfer import transfer_series
        from studio_project import request_studio_navigation
        with st.spinner('Preparando serie temporal y elementos editables…'):
            candidate=transfer_series(session.project)
        session.commit(candidate);session.state[session.key+'_selected']=candidate['studio']['timeline'][-1]
        request_studio_navigation(session.state);st.rerun();return
    if action in ('import','timelapse','send_series','tool','open'):
        tool={'import':'Datos','timelapse':'Preparar timelapse','send_series':'Serie para Studio'}.get(action,message.get('tool','Propiedades'))
        from studio_sig_workspace import TOOLS
        if tool not in TOOLS:raise ValueError('Herramienta desconocida.')
        choose_tool(session,tool);session.state[session.key+'_sig_dialog']='open' if action=='open' else 'tools';return
    if action=='navigate':
        if message.get('section') not in ('Inicio','Studio','Recursos'):raise ValueError('Destino desconocido.')
        if message['section']=='Studio':
            from studio_project import request_studio_navigation
            request_studio_navigation(session.state)
        else:session.state['section']=message['section']
        st.rerun();return
    if action in ('layer','series_visibility','series_style','series_palette','series_presentation','save','undo','redo','profile','basemap'):
        if message.get('version')!=session.version:raise ValueError('El proyecto cambió; repite el gesto sobre la vista actual.')
        if action=='layer':
            command=message.get('command',{})
            if command.get('action') not in ('active','visibility','style','rename','order','fit','remove','select'):raise ValueError('Comando de capa desconocido.')
            if command.get('action')=='active':
                from studio_sig_series import select_observation
                candidate=select_observation(session.project,command.get('layer_id'))
            else:candidate=layer_command(session.project,command)
        elif action=='series_visibility':
            from studio_sig_layers import series_visibility_command
            candidate=series_visibility_command(session.project,message.get('visible'))
        elif action=='series_palette':
            from studio_sig_palette import change_palette
            candidate=change_palette(session.project,message.get('palette'))
        elif action=='series_presentation':
            from studio_territory import validate
            time=workspace_for(session.project).get('raster_time')
            if not time:raise ValueError('No hay serie temporal.')
            options=validate(message.get('presentation'))
            candidate=layer_command(session.project,{'action':'raster_time','value':{**time,'presentation':options}})
        elif action=='series_style':
            from studio_sig_layers import series_style_command
            candidate=series_style_command(session.project,message['opacity'])
            if 'palette' in message:
                from studio_sig_palette import change_palette
                candidate=change_palette(candidate,message['palette'])
        elif action=='basemap':candidate=layer_command(session.project,{'action':'basemap','value':message['value']})
        elif action=='profile':
            from studio_workspace_commands import workspace_command
            candidate=workspace_command(session.project,session.selected,{'action':'profile','profile':message['profile']})
        elif action in ('undo','redo'):
            session.dispatch({'action':action,'version':session.version,'scene':session.selected});return
        else:candidate=session.project
        if candidate!=session.project or action=='save':session.commit(candidate,record=action!='save')
        return
    from studio_sig_workspace import presentation_event
    presentation_event(session,message)


def shell_dialog(session):
    mode=session.state.get(session.key+'_sig_dialog')
    if not mode:return
    if mode=='tools' and preferences(session)['tool']=='Propiedades':
        session.state.pop(session.key+'_sig_dialog',None);return
    def close():session.state.pop(session.key+'_sig_dialog',None)
    if mode=='tools':
        tool_window(session)
        return
    @st.dialog('Abrir proyecto',width='small',on_dismiss=close)
    def content():
        if mode=='open':
            from studio_home import project_files
            from studio_recovery import recover_snapshot
            from studio_sig_workspace import open_copy
            with st.form('sig_shell_open'):
                path=st.selectbox('Proyecto guardado',[None]+project_files(session.store/'projects'),format_func=lambda p:p.stem if p else 'Selecciona un proyecto…')
                upload=st.file_uploader('Proyecto JSON',type=['json']);accepted=st.form_submit_button('Abrir copia en SIG')
            if accepted:
                try:
                    if not path and not upload:raise ValueError('Selecciona un proyecto.')
                    document=json.loads(upload.getvalue()) if upload else recover_snapshot(path)[0]
                    close();open_copy(session,document);st.rerun()
                except (ValueError,TypeError,KeyError,OSError) as error:st.error(str(error))
        if st.button('Volver al mapa',key='sig_shell_close'):close();st.rerun()
    content()


@st.fragment
def tool_window(session):
    """Contextual non-modal pane: form edits do not rerun the map fragment."""
    from studio_sig_workspace import tools_panel
    if session.state.get(session.key+'_sig_dialog')!='tools':return
    tool=preferences(session)['tool']
    if tool=='Propiedades':return
    def close_tool():session.state.pop(session.key+'_sig_dialog',None)
    with st.container(key='sig_tool_window',gap='small'):
        with st.container(horizontal=True,vertical_alignment='center',gap='small'):
            st.markdown('### '+tool)
            st.button('Cerrar',key='sig_tool_close',icon=':material/close:',help='Cerrar herramienta y conservar el mapa',on_click=close_tool)
        if tool=='Datos':
            from studio_sig_references import reference_panel
            with st.expander('Límites y referencias predefinidas'):reference_panel(session)
        tools_panel(session,fixed_tool=tool)
