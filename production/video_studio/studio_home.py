"""Project launch surface over the existing Studio document and renderer."""
import copy
import json
from pathlib import Path
import streamlit as st
from model import STORE, default_project
from output_profiles import PRESETS, profile_for
SOURCE_MTIME=Path(__file__).stat().st_mtime_ns


def project_files(folder):
    root=Path(folder).resolve()
    if not root.is_dir():return []
    files=[p for p in root.glob('*.json') if not p.name.endswith('.previous.json')
           and p.is_file() and p.resolve().is_relative_to(root)]
    return sorted(files,key=lambda p:p.stat().st_mtime_ns,reverse=True)


def create_project(mode, profile, *, template='blank', theme='Ecuador Vivo', name='Proyecto sin título'):
    from studio_editing import new_workspace
    from studio_templates import TEMPLATE_BINDINGS, template_scene
    from studio_project import replace_document
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
    from studio_home_visual import launch,recents,workspace_entries
    from studio_project import validate_document
    saved_paths=project_files(store/'projects')
    launch(document,show_entries=False)
    with st.container(key='ev_home_actions',horizontal=True,vertical_alignment='center'):
        if st.button('Crear proyecto',key='home_free',type='primary',icon=':material/add:'):
            st.session_state['home_mode']='free'
        if st.button('Abrir proyecto',key='home_open_saved',icon=':material/folder_open:'):
            st.session_state['home_mode']='open'
        if st.button('Usar plantilla',key='home_template',icon=':material/dashboard:'):
            st.session_state['home_mode']='template'
        if st.button('Desde datos',key='home_scientific',icon=':material/database:'):
            st.session_state['home_mode']='scientific'
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
            show_scientific_assistant(document or st.session_state.get('project_document'),open_project)
        except (ValueError,TypeError,KeyError,OSError) as error: st.error(str(error))
    elif mode in ('free','template'):
        from studio_templates import TEMPLATES,TEMPLATE_BINDINGS,THEMES
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
    elif mode=='open':
        st.subheader('Abrir un proyecto guardado')
        options={str(path):path for path in saved_paths}
        chosen=st.selectbox('Proyectos locales',[None,*options],format_func=lambda value:'Selecciona un proyecto…' if value is None else options[value].stem,key='home_open_choice')
        if st.button('Abrir selección',key='home_open_selection',disabled=chosen is None,type='primary'):
            try:
                from studio_recovery import recover_snapshot
                project,_=recover_snapshot(options[chosen]);open_project(validate_document(project))
                st.session_state.pop('home_mode',None)
                st.session_state['section']='Editor';st.session_state['studio_phase']='Estudio';st.rerun()
            except (ValueError,TypeError,KeyError,OSError) as error:st.error(str(error))
        st.caption('También puedes importar una copia JSON desde otra carpeta.')
        upload=st.file_uploader('Importar proyecto JSON',type=['json'],key='home_import_file')
        if st.button('Importar proyecto',disabled=upload is None,key='home_import'):
            try:
                from studio_recovery import save_snapshot
                import uuid
                project=validate_document(json.loads(upload.getvalue()))
                save_snapshot(store/'projects'/('importado-'+uuid.uuid4().hex[:12]+'.json'),project)
                open_project(project)
                st.session_state['section']='Editor';st.session_state['studio_phase']='Estudio';st.rerun()
            except (ValueError,TypeError,KeyError,OSError) as error:st.error(str(error))
        st.caption('Abrir crea una copia de trabajo. Los archivos originales se conservan. El JSON referencia recursos locales; no incluye los archivos multimedia.')
    if mode and st.button('Cerrar configuración',key='home_cancel_create'):
        st.session_state.pop('home_mode',None);st.rerun()
    workspace_entries(document)
    recents(saved_paths,open_project,validate_document)
    with st.expander('Ayuda y ejemplo científico',expanded=False,key='home_help_panel',on_change='rerun'):
        if st.button('Abrir ejemplo real · CHIRPS 1–3 enero 2024',key='home_chirps_example',icon=':material/calendar_month:'):
            try:
                from studio_sig_references import local_chirps_example
                with st.spinner('Verificando originales locales…'):project=local_chirps_example()
                open_project(project);st.session_state.pop('_pending_studio_navigation',None)
                st.session_state['section']='SIG';st.rerun()
            except (ValueError,OSError,KeyError,TypeError) as error:st.error(str(error))
        st.caption('Ejemplo local real; no se descarga al abrir Inicio.')
        st.markdown('1. Explora e importa datos en SIG.\n2. Prepara el mapa temporal y envíalo a Studio.\n3. Añade Recursos, tu voz y subtítulos.\n4. Revisa y exporta el video.')
