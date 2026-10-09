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
    st.html('''<style>
      .evs-home-brand{display:flex;align-items:center;gap:14px;color:#edf3f5}
      .evs-home-mark{border:1px solid #82e4ca;border-radius:10px;padding:12px;color:#82e4ca;font-weight:700}
      .evs-home-brand h1{margin:0;font-size:1.8rem;letter-spacing:-.04em}
      .evs-home-brand p{margin:2px 0;color:#afc0c9}
      .evs-home-intro{max-width:780px;margin:28px 0 20px}
      .evs-home-intro h2{margin:0;font-size:2.4rem;line-height:1.2}
      .evs-home-intro p{color:#afc0c9;line-height:1.6}
      @media(max-width:800px){.evs-home-intro h2{font-size:1.8rem}}
      </style><div class="evs-home-brand"><span class="evs-home-mark">EV</span>
      <div><h1>Ecuador Vivo</h1><p>SIG y Studio · un proyecto compartido</p></div></div>
      <div class="evs-home-intro"><h2>Tu próxima historia empieza aquí.</h2>
      <p>Abre SIG para preparar mapas y resultados, o entra directamente en Studio para crear un video.
      Ambos espacios conservan el mismo proyecto.</p></div>''')
    with st.container(horizontal=True):
        if st.button('Crear proyecto',type='primary',icon=':material/add:',key='home_new'):
            st.session_state['home_mode']='free'
        if st.button('Continuar en Studio',icon=':material/movie:',key='home_continue'):
            st.session_state['section']='Editor';st.session_state['studio_phase']='Estudio';st.rerun()
        if st.button('Crear/abrir mapa · SIG',icon=':material/map:',key='home_sig'):
            st.session_state['section']='SIG';st.rerun()
        if st.button('Datos científicos',icon=':material/science:',key='home_data'):
            st.session_state['section']='Obtener datos';st.rerun()
        if st.button('Montaje anterior',icon=':material/history:',key='home_legacy'):
            st.session_state['section']='Editor';st.session_state['studio_phase']='Datos';st.rerun()
    st.subheader('Crear con un punto de partida')
    columns=st.columns(3)
    choices=[('free','Proyecto libre','Grabaciones, imágenes, títulos y composición.','home_free'),
             ('template','Desde plantilla','Un diseño editable para empezar a contar.','home_template'),
             ('scientific','Desde datos científicos','Preparar fuentes y resultados verificables.','home_scientific')]
    for column,(mode,title,description,key) in zip(columns,choices):
        with column,st.container(border=True):
            st.markdown('**'+title+'**');st.caption(description)
            if st.button('Elegir '+title.lower(),key=key,width='stretch'):
                st.session_state['home_mode']=mode
    mode=st.session_state.get('home_mode')
    if mode=='scientific':
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
            if st.button('Crear proyecto en Studio',type='primary',key='home_create'):
                try:
                    project=create_project(mode,profile,template=template,theme=theme,name=name)
                    open_project(project)
                    st.session_state.pop('home_mode',None)
                    st.session_state['section']='Editor';st.session_state['studio_phase']='Estudio';st.rerun()
                except (ValueError,TypeError,KeyError,OSError) as error:st.error(str(error))
    st.divider()
    st.subheader('Abrir y recuperar')
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
    recent=project_files(store/'projects')[:6]
    if recent:
        st.subheader('Proyectos recientes')
        for index,path in enumerate(recent):
            try:
                data=json.loads(path.read_text(encoding='utf-8'))
                if not isinstance(data,dict) or not isinstance(data.get('studio',{}),dict):
                    raise ValueError('Documento de proyecto inválido.')
                studio=data.get('studio',{})
                name=data.get('name',path.stem)
                label='Studio · '+str(len(studio.get('timeline',[])))+' escenas' if studio else 'Montaje anterior'
                with st.container(border=True):
                    st.markdown('**'+html.escape(str(name))+'**')
                    st.caption(label+' · '+path.name)
                    if st.button('Abrir',key='home_recent_'+str(index)):
                        open_project(validate_document(data))
                        st.session_state['section']='Editor';st.session_state['studio_phase']='Estudio';st.rerun()
            except (ValueError,TypeError,KeyError,OSError) as error:
                st.warning(path.name+': '+str(error))
