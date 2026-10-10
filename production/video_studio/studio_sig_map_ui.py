"""Viewport SIG workspace; retained map and canonical transaction boundary."""
from pathlib import Path
import streamlit as st
from streamlit.errors import StreamlitAPIException
from studio_sig_layers import add_geojson_layer,layer_command,workspace_for,map_payload
from studio_sig_inspector import layer_list,inspector
from studio_sig_workspace import preferences,toolbar,choose_tool,apply_requested_tool,tools_panel,temporal_strip,bottom_panel,notify,presentation_event

ASSETS=Path(__file__).with_name('sig_map_frontend')
_COMPONENT=None
_OL_COMPONENT=None

def _register():
    return st.components.v2.component('ecuador_vivo_sig_map',html=(ASSETS/'map.html').read_text(encoding='utf-8'),
        css=(ASSETS/'map.css').read_text(encoding='utf-8'),js=(ASSETS/'map.js').read_text(encoding='utf-8'))

@st.fragment
def show_sig_map(session):
    global _COMPONENT,_OL_COMPONENT
    component_key=session.key+'_sig_map'
    def commit(message):
        candidate=layer_command(session.project,message)
        if candidate!=session.project:session.commit(candidate)
    def changed():
        message=st.session_state.get(component_key,{}).get('command')
        if not message:return
        try:
            if 'commands' in message:
                from studio_sig_protocol import apply_map_intents
                st.session_state[component_key+'_confirmation']=apply_map_intents(session,message)
            else:
                if message.get('version')!=session.version:raise ValueError('La vista cambió; vuelve a seleccionar sobre el mapa actualizado.')
                commit(message)
        except (ValueError,TypeError,KeyError,OSError) as error:
            notify(session,error,'error')
            st.session_state[component_key+'_error']=str(error)
            if isinstance(message,dict) and 'commands' in message:
                st.session_state[component_key+'_confirmation']={'client':message.get('client'),
                    'sequence':message.get('sequence'),'version':session.version,'status':'rejected','error':str(error)}
        finally:st.session_state[component_key+'_ack']=st.session_state.get(component_key+'_ack',0)+1
    def ui_changed():
        try:presentation_event(session,st.session_state.get(component_key,{}).get('ui_event'))
        except (ValueError,TypeError) as error:notify(session,error,'error')
    ui=preferences(session)
    apply_requested_tool(session)
    st.html(ASSETS/'workspace.css')
    dock=ui['dock_height'] if ui['dock'] else 0
    time_height=72 if workspace_for(session.project).get('raster_time') else (152 if ui['time'] else 36)
    top=88 if ui['compact'] else 56
    st.html('<style>.st-key-sig_shell{--sig-dock:'+str(dock)+'px;--sig-time:'+str(time_height)+'px;--sig-top:'+str(top)+'px;'+
        ('' if ui['left'] else '--sig-left:44px;')+('' if ui['right'] else '--sig-right:44px;')+'}</style>')
    try:
        state=workspace_for(session.project);layers=state['layers']
        engine_key=session.key+'_sig_engine'
        engine=st.session_state.get(engine_key,'OpenLayers · WebGL / Canvas')
        if not engine.startswith('OpenLayers') and any(l['type']=='raster' for l in layers.values()):
            engine='OpenLayers · WebGL / Canvas'
            notify(session,'Las capas GeoTIFF requieren OpenLayers; SVG conserva únicamente la compatibilidad vectorial.')
        st.session_state[engine_key]=engine
        shell=st.container(key='sig_shell',gap='xsmall')
        with shell:
            toolbar(session)
            body=st.container(key='sig_body')
            with body:left,center,right=st.columns([.22,.55,.23],gap='xsmall')
        def action(label,msg,key,**options):
            if st.button(label,key=key,**options):
                try:
                    commit(msg)
                    if msg['action']=='active':choose_tool(session,'Propiedades')
                    st.rerun()
                except (ValueError,TypeError,KeyError,OSError) as error:st.error(str(error))
        with left,st.container(key='sig_left',gap='xsmall'):
            if st.button('Fuentes y capas' if ui['left'] else 'Capas',key='sig_toggle_left',icon=':material/layers:',
                         help='Cerrar capas' if ui['left'] else 'Abrir capas',width='stretch'):
                ui['left']=not ui['left']
                if ui['compact'] and ui['left']:ui['right']=False
                st.rerun()
            if ui['left']:layer_list(session,action,commit)
        with center,st.container(key='sig_center',gap='xsmall'):
            map_slot=st.container(key='sig_map_slot')
            preview=temporal_strip(session)
            payload=map_payload(session.project);payload.update(version=session.version,ack=st.session_state.get(component_key+'_ack',0),error=st.session_state.pop(component_key+'_error',''),
                project_id=session.project.get('project_meta',{}).get('id',''),confirmation=st.session_state.get(component_key+'_confirmation'),workspace_layout={'dock_open':ui['dock'],'dock_height':dock,'time_height':time_height,'top_height':top,'temporal_preview':bool(preview)},temporal_preview=preview)
            payload['pixel_result']=session.state.get(session.key+'_sig_pixel')
            with map_slot:
                if engine.startswith('OpenLayers'):
                    try:from ecuador_vivo_sig_map import register,out
                    except ImportError:
                        st.error('Falta el adaptador local OpenLayers en este entorno. Instala production/video_studio/ecuador-vivo-sig-map con el Python de Studio, o elige SVG compatible.');return
                    if _OL_COMPONENT is None:_OL_COMPONENT=out
                    renderer=_OL_COMPONENT
                else:
                    if _COMPONENT is None:_COMPONENT=_register()
                    renderer=_COMPONENT
                try:renderer(key=component_key,data=payload,on_command_change=changed,on_ui_event_change=ui_changed,width='stretch',height='content')
                except StreamlitAPIException as error:
                    if 'is not registered' not in str(error):raise
                    if engine.startswith('OpenLayers'):_OL_COMPONENT=register();renderer=_OL_COMPONENT
                    else:_COMPONENT=_register();renderer=_COMPONENT
                    renderer(key=component_key,data=payload,on_command_change=changed,on_ui_event_change=ui_changed,width='stretch',height='content')
        with right,st.container(key='sig_right',gap='xsmall'):
            if st.button('Propiedades' if ui['right'] else 'Inspector',key='sig_toggle_right',icon=':material/tune:',
                         help='Cerrar inspector' if ui['right'] else 'Abrir inspector',width='stretch'):
                ui['right']=not ui['right']
                if ui['compact'] and ui['right']:ui['left']=False
                st.rerun()
            if ui['right']:tools_panel(session)
            if ui['right'] and ui['tool']=='Propiedades':inspector(session,action,commit)
            if ui['right']:
                with st.expander('Visor y referencia espacial'):
                    basemap=st.selectbox('Mapa base',['none','osm'],index=0 if state.get('basemap','none')=='none' else 1,
                        format_func=lambda v:'Sin mapa base' if v=='none' else 'OpenStreetMap · conexión a Internet',key=session.key+'_basemap_'+str(session.version))
                    if basemap!=state.get('basemap','none'):commit({'action':'basemap','value':basemap});st.rerun()
                    st.selectbox('Visor SIG',['OpenLayers · WebGL / Canvas','SVG compatible'],key=engine_key,persist_state='session')
                    st.caption('Vista EPSG:4326 · el CRS nativo figura en cada capa. La vista no modifica los originales.')
        with shell:bottom_panel(session)
    except (ValueError,TypeError,KeyError,OSError) as error:st.error('No se pudo abrir el mapa SIG: '+str(error))
