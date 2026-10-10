"""Project launch surface over the existing Studio document and renderer."""
import copy
import html
import json
from pathlib import Path
import streamlit as st
from model import STORE, default_project
from output_profiles import PRESETS, profile_for
from studio_editing import new_workspace
from studio_templates import TEMPLATES, TEMPLATE_BINDINGS, THEMES, template_scene
from studio_project import replace_document, validate_document
from studio_recovery import recover_snapshot
SOURCE_MTIME=Path(__file__).stat().st_mtime_ns


def project_files(folder):
    root=Path(folder).resolve()
    if not root.is_dir():return []
    files=[p for p in root.glob('*.json') if not p.name.endswith('.previous.json')
           and p.is_file() and p.resolve().is_relative_to(root)]
    return sorted(files,key=lambda p:p.stat().st_mtime_ns,reverse=True)[:100]


def create_project(mode, profile, *, template='blank', theme='Ecuador Vivo', name='Proyecto sin título'):
    if mode not in ('free','template'): raise ValueError('Modo de proyecto desconocido.')
    if not isinstance(name,str) or not name.strip() or len(name)>200: raise ValueError('Nombre de proyecto inválido.')
    if template in TEMPLATE_BINDINGS: raise ValueError('Esta plantilla necesita resultados científicos vinculados.')
    output=profile_for(profile)
    project=new_workspace(default_project())
    scene=template_scene('blank' if mode=='free' else template,output,theme=theme)
    project['studio']['scenes'].append(scene)
    project['studio']['timeline']=[scene['id']]
    project['studio']['output_profile']=copy.deepcopy(profile)
    project['studio']['theme']=theme
    project['name']=name.strip()
    project['endcard_enabled']=False
    project['project_meta']={'mode':'free'}
    # Identity allocation uses exactly the canonical document helper.
    return replace_document({},project)


def show_home(open_project, *, store=None, document=None):
    store=Path(store or STORE)
    from studio_home_visual import launch,recents
    recent_paths=project_files(store/'projects')[:3]
    launch(document,recent_paths)
    st.markdown('### Empieza con una idea')
    columns=st.columns(3)
    choices=[('free','Proyecto libre','Grabaciones, imágenes, títulos y composición.','home_free'),
             ('template','Desde plantilla','Un diseño editable para empezar a contar.','home_template'),
             ('scientific','Desde datos científicos','Preparar fuentes y resultados verificables.','home_scientific')]
    for column,(mode,title,description,key) in zip(columns,choices):
        with column,st.container(border=True,key='ev_home_choice_'+mode):
            st.markdown('**'+title+'**');st.caption(description)
            if st.button('Elegir '+title.lower(),key=key,width='stretch'):
                st.session_state['home_mode']=mode
    recents(recent_paths,open_project,validate_document)
    with st.expander('Ayuda y ejemplo científico',expanded=False,key='home_help_panel',on_change='rerun'):
        if st.button('Abrir ejemplo real · CHIRPS 1–3 enero 2024',key='home_chirps_example',icon=':material/calendar_month:'):
            try:
                from studio_sig_references import local_chirps_example
                with st.spinner('Verificando originales locales…'):project=local_chirps_example()
                open_project(project);st.session_state.pop('_pending_studio_navigation',None)
                st.session_state['section']='SIG';st.rerun()
            except (ValueError,OSError,KeyError,TypeError) as error:st.error(str(error))
        st.caption('Tres observaciones ambientales reales disponibles en la caché personal. No se incluyen en la distribución pública.')
        st.markdown('1. Importa y consulta tus datos en SIG.\n2. Preparar timelapse: revisa fechas, periodo, duración y encuadre.\n3. Enviar a Studio: revisa el recurso y confirma.\n4. Edita la escena, guarda y exporta el MP4.')
    mode=st.session_state.get('home_mode')
    if mode=='gis':
        st.subheader('Proyecto SIG')
        name=st.text_input('Nombre del proyecto','Proyecto SIG sin título',key='home_sig_name',max_chars=200)
        st.caption('Importa, consulta y analiza datos sin preparar un video. Studio estará disponible en el mismo proyecto.')
        if st.button('Crear proyecto SIG',type='primary',key='home_create_sig'):
            try:
                from studio_sig_references import initial_map
                open_project(initial_map(create_project('free',{'id':'youtube'},name=name)))
                st.session_state.pop('home_mode',None)
                # replace_project queues Studio for legacy consumers. This
                # explicit SIG destination must survive the next app rerun.
                st.session_state.pop('_pending_studio_navigation',None)
                st.session_state['section']='SIG';st.rerun()
            except (ValueError,TypeError,KeyError,OSError) as error:st.error(str(error))
    elif mode=='scientific':
        from studio_scientific_ui import show_scientific_assistant
        try:
            show_scientific_assistant(document or st.session_state.get('project_document',default_project()),open_project)
        except (ValueError,TypeError,KeyError,OSError) as error: st.error(str(error))
    elif mode in ('free','template'):
        with st.container(border=True):
            st.subheader('Configura tu proyecto')
            name=st.text_input('Nombre del proyecto','Proyecto sin título',key='home_name',max_chars=200)
            profile_id=st.selectbox('Formato de salida',list(PRESETS)+['custom'],format_func=lambda k:PRESETS[k][0] if k in PRESETS else 'Personalizado',key='home_profile')
            profile={'id':profile_id}
            if profile_id=='custom':
                width=st.number_input('Ancho · px',160,3840,1920,2,key='home_width')
                height=st.number_input('Alto · px',160,3840,1080,2,key='home_height')
                profile.update(width=width,height=height)
            st.caption('30 FPS · perfiles y límites del motor actual; puedes cambiar el formato dentro del Studio.')
            template='blank'
            if mode=='template':
                templates=[k for k in TEMPLATES if k not in TEMPLATE_BINDINGS]
                template=st.selectbox('Plantilla inicial',templates,index=templates.index('cover'),format_func=lambda k:TEMPLATES[k],key='home_initial_template')
                st.caption('Los diseños de métricas y gráficos requieren resultados y se eligen en Studio.')
            theme=st.selectbox('Estilo',list(THEMES),key='home_theme')
            if st.button('Crear proyecto SIG',key='home_create_sig',icon=':material/layers:'):
                try:
                    project=create_project(mode,profile,template=template,theme=theme,name=name)
                    from studio_sig_references import initial_map
                    project=initial_map(project)
                    open_project(project)
                    st.session_state.pop('home_mode',None)
                    st.session_state.pop('_pending_studio_navigation',None)
                    st.session_state['section']='SIG';st.rerun()
                except (ValueError,TypeError,KeyError,OSError) as error:st.error(str(error))
            if st.button('Crear proyecto en Studio',type='primary',key='home_create'):
                try:
                    project=create_project(mode,profile,template=template,theme=theme,name=name)
                    open_project(project)
                    st.session_state.pop('home_mode',None)
                    st.session_state['section']='Editor';st.session_state['studio_phase']='Estudio';st.rerun()
                except (ValueError,TypeError,KeyError,OSError) as error:st.error(str(error))
    with st.expander('Abrir e importar un proyecto',expanded=False,key='home_open_panel',on_change='rerun'):
        with st.container(horizontal=True):
            chosen=st.selectbox('Proyecto guardado',[None]+project_files(store/'projects'),format_func=lambda p:'Selecciona una copia…' if p is None else p.stem,key='home_saved')
            if st.button('Abrir copia',disabled=chosen is None,key='home_open'):
                try:
                    project,previous=recover_snapshot(chosen)
                    open_project(validate_document(project))
                    st.session_state['section']='Editor';st.session_state['studio_phase']='Estudio';st.rerun()
                except (ValueError,TypeError,KeyError,OSError) as error:st.error(str(error))
        upload=st.file_uploader('Importar proyecto JSON',type=['json'],key='home_import_file')
        if st.button('Importar proyecto',disabled=upload is None,key='home_import'):
            try:
                open_project(validate_document(json.loads(upload.getvalue())))
                st.session_state['section']='Editor';st.session_state['studio_phase']='Estudio';st.rerun()
            except (ValueError,TypeError,KeyError,OSError) as error:st.error(str(error))
        st.caption('Abrir crea una copia de trabajo. Los archivos originales se conservan. El JSON referencia recursos locales; no incluye los archivos multimedia.')
