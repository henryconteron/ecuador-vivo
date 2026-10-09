"""SIG-U1 native panels and angular interactive map in the canonical project."""
from pathlib import Path
import streamlit as st
from streamlit.errors import StreamlitAPIException
from studio_sig_layers import add_geojson_layer,layer_command,workspace_for,map_payload
from studio_geography import region_feature

ASSETS=Path(__file__).with_name('sig_map_frontend')
_COMPONENT=None

def _register():
    return st.components.v2.component('ecuador_vivo_sig_map',html=(ASSETS/'map.html').read_text(encoding='utf-8'),
        css=(ASSETS/'map.css').read_text(encoding='utf-8'),js=(ASSETS/'map.js').read_text(encoding='utf-8'))

def show_sig_map(session):
    global _COMPONENT
    component_key=session.key+'_sig_map'
    def commit(message):
        candidate=layer_command(session.project,message)
        if candidate!=session.project:session.commit(candidate)
    def changed():
        message=st.session_state.get(component_key,{}).get('command')
        if not message:return
        try:
            if message.get('version')!=session.version:raise ValueError('La vista cambió; vuelve a seleccionar sobre el mapa actualizado.')
            commit(message)
        except (ValueError,TypeError,KeyError,OSError) as error:st.session_state[component_key+'_error']=str(error)
        finally:st.session_state[component_key+'_ack']=st.session_state.get(component_key+'_ack',0)+1
    with st.expander('Añadir datos propios · GeoJSON',expanded=not workspace_for(session.project)['layers']):
        st.caption('Polygon/MultiPolygon 2D RFC7946 · WGS84 lon/lat · hasta 8 MiB. Conserva bytes/atributos originales. BYOD: declara procedencia y permisos; no se redistribuyen automáticamente.')
        with st.form('sig_u1_import'):
            upload=st.file_uploader('Archivo GeoJSON',type=['geojson','json'],key='sig_u1_upload',max_upload_size=8)
            citation=st.text_input('Procedencia',key='sig_u1_citation',max_chars=1000)
            license=st.text_input('Licencia o condiciones',key='sig_u1_license',max_chars=1000)
            url=st.text_input('URL pública sin credenciales (opcional)',key='sig_u1_url',max_chars=1000)
            accepted=st.form_submit_button('Añadir capa GeoJSON',key='sig_u1_import_submit')
        if accepted:
            try:
                if upload is None:raise ValueError('Selecciona un archivo GeoJSON.')
                candidate,_=add_geojson_layer(session.project,upload.getvalue(),upload.name,{'citation':citation,'license':license,'url':url})
                if candidate!=session.project:session.commit(candidate)
                st.rerun()
            except (ValueError,TypeError,KeyError,OSError) as error:st.error('No se añadió la capa: '+str(error))
    try:
        state=workspace_for(session.project);layers=state['layers']
        st.subheader('Mapa SIG')
        left,center,right=st.columns([.22,.55,.23])
        def action(label,msg,key,**options):
            if st.button(label,key=key,**options):
                try:commit(msg);st.rerun()
                except (ValueError,TypeError,KeyError,OSError) as error:st.error(str(error))
        with left:
            st.markdown('**Capas · arriba primero**')
            if not layers:st.info('Añade un GeoJSON para comenzar.')
            for lid in reversed(state['order']):
                layer=layers[lid]
                action(layer['name'],{'action':'active','layer_id':lid},'sig_active_'+lid,type='primary' if lid==state['active_layer'] else 'secondary',width='stretch')
                widget='sig_visible_'+lid+'_'+str(session.version)
                def visibility(lid=lid,widget=widget):
                    try:commit({'action':'visibility','layer_id':lid,'visible':st.session_state[widget]})
                    except (ValueError,TypeError,KeyError,OSError) as error:st.session_state[component_key+'_error']=str(error)
                st.checkbox('Visible',value=layer['visible'],key=widget,on_change=visibility)
            if st.button('Guardar proyecto SIG',key='sig_save_project'):
                session.commit(session.project,record=False)
                st.rerun()
            st.caption('Guardado automático · '+str(st.session_state.get(session.key+'_saved_at','sin cambios')))
        with center:
            payload=map_payload(session.project);payload.update(version=session.version,ack=st.session_state.get(component_key+'_ack',0),error=st.session_state.pop(component_key+'_error',''))
            if _COMPONENT is None:_COMPONENT=_register()
            try:_COMPONENT(key=component_key,data=payload,on_command_change=changed,width='stretch',height='content')
            except StreamlitAPIException as error:
                if 'is not registered' not in str(error):raise
                _COMPONENT=_register();_COMPONENT(key=component_key,data=payload,on_command_change=changed,width='stretch',height='content')
        with right:
            st.markdown('**Propiedades**')
            active=layers.get(state['active_layer'])
            if active:
                lid=active['id'];source=session.project['studio']['geography']['sources'][active['source_id']]
                st.write(active['name']);st.caption('Vector · '+active['native_crs'])
                with st.form('sig_style_'+lid+'_'+str(session.version)):
                    fill=st.color_picker('Relleno',active['style']['fill'])
                    stroke=st.color_picker('Contorno',active['style']['stroke'])
                    opacity=st.slider('Opacidad',0.,1.,float(active['style']['opacity']),.05)
                    if st.form_submit_button('Aplicar estilo'):
                        commit({'action':'style','layer_id':lid,'style':{'fill':fill,'stroke':stroke,'opacity':opacity}});st.rerun()
                with st.container(horizontal=True):
                    action('Subir',{'action':'order','layer_id':lid,'offset':1},'sig_up')
                    action('Bajar',{'action':'order','layer_id':lid,'offset':-1},'sig_down')
                action('Quitar capa de la vista',{'action':'remove','layer_id':lid},'sig_remove')
                with st.expander('Fuente y procedencia'):
                    st.json({k:source[k] for k in ('id','name','sha256','bytes','native_crs','provenance')})
                if state['selection']:
                    rid=state['selection'][0];feature=region_feature(session.project,rid)
                    st.markdown('**Entidad seleccionada**');st.caption(rid)
                    st.json(feature.get('properties') or {})
            else:st.caption('Selecciona una capa o entidad del mapa.')
        st.caption('Vista angular OGC:CRS84: el estilo y encuadre no cambian geometrías, atributos ni resultados científicos. Tabla ligada, medición métrica, filtros, otros CRS y ráster SIG universal corresponden a cortes posteriores.')
    except (ValueError,TypeError,KeyError,OSError) as error:st.error('No se pudo abrir el mapa SIG: '+str(error))
