"""One retained OpenLayers shell, canonical transactions and contextual tools."""
from pathlib import Path
import streamlit as st
from streamlit.errors import StreamlitAPIException
from studio_sig_layers import map_payload
from studio_sig_workspace import apply_requested_tool,notify
from studio_sig_shell import shell_payload,shell_event,shell_dialog

ASSETS=Path(__file__).with_name('sig_map_frontend')
_OL_COMPONENT=None

@st.fragment
def show_sig_map(session):
    global _OL_COMPONENT
    component_key=session.key+'_sig_map'
    def changed():
        message=st.session_state.get(component_key,{}).get('command')
        if not message:return
        try:
            if 'commands' in message:
                from studio_sig_protocol import apply_map_intents
                st.session_state[component_key+'_confirmation']=apply_map_intents(session,message)
            else:
                from studio_sig_layers import layer_command
                if message.get('version')!=session.version:raise ValueError('La vista cambió; repite el gesto sobre la versión actual.')
                candidate=layer_command(session.project,message)
                if candidate!=session.project:session.commit(candidate)
        except (ValueError,TypeError,KeyError,OSError) as error:
            notify(session,error,'error');st.session_state[component_key+'_error']=str(error)
            st.session_state[component_key+'_confirmation']={'client':message.get('client'),'sequence':message.get('sequence'),
                'version':session.version,'status':'rejected','error':str(error)}
        finally:st.session_state[component_key+'_ack']=st.session_state.get(component_key+'_ack',0)+1
    def ui_changed():
        message=st.session_state.get(component_key,{}).get('ui_event');prepared=False
        try:
            from studio_sig_protocol import prepare_ui_event
            event,confirmation=prepare_ui_event(session,message)
            if confirmation:st.session_state[component_key+'_confirmation']=confirmation
            prepared=True
            shell_event(session,event)
        except (ValueError,TypeError,KeyError,OSError) as error:
            notify(session,error,'error');st.session_state[component_key+'_error']=str(error)
            if not prepared and isinstance(message,dict) and isinstance(message.get('map_intents'),dict):
                envelope=message['map_intents']
                st.session_state[component_key+'_confirmation']={'client':envelope.get('client'),'sequence':envelope.get('sequence'),
                    'version':session.version,'status':'rejected','error':str(error)}
    apply_requested_tool(session)
    st.html(ASSETS/'workspace.css')
    try:
        from studio_sig_series import restore_downloaded_series
        if restore_downloaded_series(session):
            notify(session,'Se activó el control temporal de la descarga existente. No se descargaron datos nuevos; puedes deshacer este ajuste.')
        payload=map_payload(session.project)
        payload.update(version=session.version,ack=st.session_state.get(component_key+'_ack',0),
            error=st.session_state.pop(component_key+'_error',''),project_id=session.project.get('project_meta',{}).get('id',''),
            confirmation=st.session_state.get(component_key+'_confirmation'),
            workspace_layout={'dock_open':True,'dock_height':112,'time_height':64,'top_height':100,'temporal_preview':False},
            workspace=shell_payload(session,payload['layers']),pixel_result=session.state.get(session.key+'_sig_pixel'))
        from ecuador_vivo_sig_map import register,out
        if _OL_COMPONENT is None:_OL_COMPONENT=out
        with st.container(key='sig_integrated_shell'):
            try:_OL_COMPONENT(key=component_key,data=payload,on_command_change=changed,on_ui_event_change=ui_changed,width='stretch',height='content')
            except StreamlitAPIException as error:
                if 'is not registered' not in str(error):raise
                _OL_COMPONENT=register()
                _OL_COMPONENT(key=component_key,data=payload,on_command_change=changed,on_ui_event_change=ui_changed,width='stretch',height='content')
        shell_dialog(session)
    except (ValueError,TypeError,KeyError,OSError) as error:st.error('No se pudo abrir el mapa SIG: '+str(error))
