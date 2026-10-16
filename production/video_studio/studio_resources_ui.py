"""Resource gallery over existing Studio scenes, with explicit insertion only."""
from io import BytesIO
import base64
import html
from pathlib import Path
import streamlit as st

from output_profiles import PRESETS, profile_for
from studio_resources import MINT, RESOURCE_CATALOG, insert_resource, resource_scene
from studio_resource_projects import create_resource_project,resource_files,load_resource,insert_saved_resource,is_resource


@st.cache_data(max_entries=24, ttl=900, show_spinner=False)
def _preview(resource_id, definition, duration, title, accent, second):
    profile = profile_for(definition)
    scene = resource_scene(resource_id, profile, duration=duration, title=title, accent=accent)
    from studio_timeline import PreparedTimeline
    project = create_resource_project(title or 'Recurso', definition)
    project['studio']['scenes'] = [scene]
    project['studio']['timeline'] = [scene['id']]
    prepared = PreparedTimeline(project, preview_max_side=600)
    frame = min(round(second * 30), prepared.total_frames - 1)
    image = prepared.frame_at(frame)
    try:
        stream = BytesIO()
        image.convert('RGB').save(stream, format='PNG')
        return stream.getvalue()
    finally:
        image.close()


@st.cache_data(max_entries=48,ttl=900,show_spinner=False)
def _template_thumbnail(resource_id,definition):
    from studio_timeline import PreparedTimeline
    entry=next(item for item in RESOURCE_CATALOG if item['id']==resource_id)
    project=create_resource_project(entry['name'],definition,resource_id=resource_id)
    prepared=PreparedTimeline(project,preview_max_side=280)
    image=prepared.frame_at(min(90,prepared.total_frames-1))
    stream=BytesIO()
    try:image.convert('RGB').save(stream,format='PNG');return stream.getvalue()
    finally:image.close()


def _blank_resource(project,on_change,key):
    st.subheader('Un lienzo para tu explicación')
    st.caption('Texto, formas, imágenes y animaciones. Podrás mover y redimensionar cada elemento en el editor visual.')
    with st.form(key+'_blank_form'):
        name=st.text_input('Nombre del diseño','Mi recurso',max_chars=180,key=key+'_blank_name')
        selected=st.selectbox('Formato del recurso',list(PRESETS),format_func=lambda pid:PRESETS[pid][0],key=key+'_blank_profile')
        duration=st.number_input('Duración de la animación · segundos',1.,120.,6.,.5,key=key+'_blank_duration')
        create=st.form_submit_button('Crear y abrir lienzo',type='primary',key=key+'_blank_create')
    if create:
        try:on_change(create_resource_project(name,{'id':selected},duration=duration))
        except (ValueError,TypeError,KeyError,OSError) as error:st.error(str(error))
    if project:st.caption('Crear un recurso abre un diseño independiente; el proyecto anterior no se convierte ni se borra.')


def _saved_resources(project,on_change,key,store):
    entries=resource_files(store)
    search=st.text_input('Buscar en mis recursos',key=key+'_saved_search',placeholder='Nombre o categoría…')
    entries=[entry for entry in entries if search.casefold() in (entry['name']+' '+entry['category']).casefold()]
    if not entries:
        st.info('Todavía no hay diseños guardados que coincidan. Crea uno y pulsa Guardar recurso en el lienzo.')
        return
    options={entry['path']:entry for entry in entries}
    selected=st.selectbox('Mis recursos',list(options),format_func=lambda path:options[path]['name']+' · '+options[path]['category'],key=key+'_saved_choice')
    entry=options[selected]
    st.caption('Diseño local reutilizable. Abrir y editar conserva el original; añadir crea una escena independiente en el video actual.')
    with st.container(horizontal=True):
        opened=st.button('Abrir y editar recurso',key=key+'_saved_edit',icon=':material/edit:')
        inserted=st.button('Añadir al proyecto actual',key=key+'_saved_insert',disabled=project is None or is_resource(project),type='primary',icon=':material/add:')
    if opened or inserted:
        try:
            resource=load_resource(selected,store)
            on_change(insert_saved_resource(project,resource) if inserted else resource)
        except (ValueError,TypeError,KeyError,OSError) as error:st.error(str(error))
    if project is None or is_resource(project):
        st.caption('Para añadirlo a un video, abre primero ese proyecto desde Inicio y vuelve a Mis recursos.')
    show=st.toggle('Ver diseño guardado',value=False,key=key+'_saved_preview')
    if show:
        try:
            from studio_timeline import PreparedTimeline
            from studio_media import AssetFrames
            resource=load_resource(selected,store)
            prepared=PreparedTimeline(resource,preview_max_side=600)
            with AssetFrames(resource['studio']['media']) as assets:
                image=prepared.frame_at(min(90,prepared.total_frames-1),assets=assets)
                try:st.image(image,width='content',alt='Diseño guardado: '+entry['name'])
                finally:image.close()
        except (ValueError,TypeError,KeyError,OSError) as error:st.error(str(error))


def show_resources(project,on_change,*,key='resource_library',store=None):
    from model import STORE
    st.html(Path(__file__).with_name('workspace_frontend')/'surfaces.css')
    st.html(Path(__file__).with_name('workspace_frontend')/'resources.css')
    with st.container(key='ev_resources_library'):
        from studio_home_visual import _cover_bytes
        cover=Path(__file__).with_name('workspace_frontend')/'art/resources-cover.webp'
        art=('<img alt="" src="data:image/webp;base64,'+base64.b64encode(_cover_bytes(str(cover),cover.stat().st_mtime_ns)).decode('ascii')+'">') if cover.is_file() else ''
        st.html('<header class="resource-hero"><div><h1>Haz visible tu explicación.</h1><p>Esquemas, animaciones y escenas 3D para contar lo que un mapa no alcanza a explicar. Crea aquí; compón en Studio.</p></div>'+art+'</header>')
        view=st.segmented_control('Biblioteca',['templates','3d','saved','blank'],default='templates',
            format_func=lambda value:{'templates':'Plantillas','3d':'Estudio 3D','saved':'Mis recursos','blank':'Crear desde cero'}[value],key=key+'_view') or 'templates'
        if view=='3d':
            from studio_blender_ui import show_blender_ui
            show_blender_ui(project,on_change,key=key+'_blender',store=store);return
        if view=='blank':_blank_resource(project,on_change,key);return
        if view=='saved':_saved_resources(project,on_change,key,Path(store or STORE));return
        definition=project['studio']['output_profile'] if project else {'id':'tiktok'}
        st.html('<div class="resource-section-heading"><h2>Diseños para empezar</h2><span>Ilustraciones editables, no observaciones científicas.</span></div>')
        with st.container(key='ev_resources_grid'):
            for start in range(0,len(RESOURCE_CATALOG),3):
                for column,entry in zip(st.columns(3,gap='small'),RESOURCE_CATALOG[start:start+3]):
                    with column,st.container(border=True,key='ev_resource_card_'+entry['id']):
                        try:
                            st.image(_template_thumbnail(entry['id'],definition),width='stretch',alt='')
                        except (ValueError,TypeError,KeyError,OSError):
                            st.caption('Plantilla disponible en un formato de mayor tamaño.')
                        st.html('<div class="resource-card-title"><span>'+html.escape(entry['name'])+'</span><small>'+html.escape(entry['category'])+'</small></div>')
                        st.caption(entry['summary'])
                        def choose(rid=entry['id']):
                            st.session_state[key+'_category']='Todos'
                            st.session_state[key+'_choice']=rid
                        st.button('Usar este diseño',key=key+'_card_'+entry['id'],on_click=choose,width='stretch')
        st.html('<div class="resource-section-heading"><h2>Prepara tu recurso</h2><span>Elige el contenido y comprueba su animación.</span></div>')
        with st.container(key='ev_resource_configuration'):
            _show_template_controls(project,on_change,key=key)


def _show_template_controls(project, on_change, *, key='resource_library'):
    """Browse without a project; create or mutate only after pressing Insert.

    The host owns save, revision, undo/redo and Studio navigation. ``on_change``
    receives the complete copied document through that existing mechanism.
    """
    chooser, canvas = st.columns([.42, .58], gap='large')
    with chooser:
        categories = ['Todos'] + list(dict.fromkeys(item['category'] for item in RESOURCE_CATALOG))
        category = st.selectbox('Tipo de recurso', categories, key=key + '_category')
        choices = [item for item in RESOURCE_CATALOG if category == 'Todos' or item['category'] == category]
        by_id = {item['id']: item for item in choices}
        resource_id = st.selectbox('Recurso', list(by_id), format_func=lambda item: by_id[item]['name'], key=key + '_choice')
        entry = by_id[resource_id]
        st.markdown('**' + entry['name'] + '**')
        st.caption(entry['summary'])
        title = st.text_input('Título del recurso', entry['name'], max_chars=180, key=key + '_title_' + resource_id)
        duration = st.number_input('Duración · segundos', 1.0, 120.0, 6.0, .5, key=key + '_duration')
        accent = st.color_picker('Color de acento', MINT, key=key + '_accent')
        if project is None:
            profile_id = st.selectbox('Formato del nuevo proyecto', list(PRESETS),
                                      format_func=lambda item: PRESETS[item][0], key=key + '_profile')
            definition = {'id': profile_id}
            st.caption('No hay proyecto abierto. Solo se creará uno cuando confirmes la inserción.')
        else:
            definition = project['studio']['output_profile']
            output = profile_for(definition)
            st.caption(f"Proyecto actual · {output.name} · {output.width} × {output.height} px")
        preview_duration = duration
        if st.button('Editar diseño en el lienzo',key=key+'_edit_template',icon=':material/edit:',width='stretch'):
            try:
                candidate=create_resource_project(title,definition,resource_id=resource_id,duration=duration)
                if accent!=MINT:
                    for element in candidate['studio']['scenes'][0]['elements']:
                        style=element.get('style',{})
                        for field in ('fill','color'):
                            if style.get(field)==MINT:style[field]=accent
                on_change(candidate)
            except (ValueError,TypeError,KeyError,OSError) as error:st.error(str(error))
        mode = 'scene'
        scene_id = None
        if project is not None:
            mode = st.segmented_control('Insertar como', ['scene', 'overlay'], default='scene',
                                        format_func=lambda item: 'Escena nueva' if item == 'scene' else 'Superposición',
                                        key=key + '_mode') or 'scene'
            if mode == 'overlay':
                by_scene = {scene['id']: scene for scene in project['studio']['scenes']
                            if scene['id'] in project['studio']['timeline'] and scene.get('renderer', 'studio') == 'studio'}
                if by_scene:
                    scene_id = st.selectbox('Escena de destino', list(by_scene),
                                            format_func=lambda item: by_scene[item]['name'], key=key + '_target')
                    preview_duration = by_scene[scene_id]['duration']
                    st.caption(f'Conserva el mapa y la duración de destino: {preview_duration:g} s. La duración de arriba solo se usa para una escena nueva.')
                    st.caption('Puedes mover o eliminar las partes después en Studio.')
                else:
                    st.warning('No hay una escena Studio editable para superponer. Elige escena nueva.')
        if st.button('Crear proyecto y añadir' if project is None else 'Añadir a Studio',
                     icon=':material/add:', type='primary', width='stretch', key=key + '_insert',
                     disabled=(mode == 'overlay' and scene_id is None)):
            try:
                base = project
                if base is None:
                    base = create_resource_project(title.strip() or entry['name'],definition)
                updated = insert_resource(base, resource_id, duration=duration, title=title, accent=accent,
                                          mode=mode, scene_id=scene_id)
                if project is None:
                    # Keep the blank in the recovery scene registry, not in playback.
                    updated['studio']['timeline'] = [updated['studio']['timeline'][-1]]
                on_change(updated)
                st.success('Recurso añadido. Sus textos, formas y animaciones son editables en Studio.')
            except (ValueError, TypeError, KeyError, OSError) as error:
                st.error(str(error))
        with st.expander('Qué explica y qué no'):
            st.caption(entry['note'])
            st.caption('No contiene observaciones ni resultados inventados. Las formas no tienen escala física o geográfica salvo indicación expresa.')
            for source in entry['sources']:
                if source['url']:
                    st.markdown('[' + source['title'] + '](' + source['url'] + ')')
                else:
                    st.caption(source['title'])
    with canvas:
        st.subheader('Así se incorpora al video')
        second = st.slider('Momento de la animación · segundos', 0.0, float(preview_duration), min(3.0, float(preview_duration)), .1,
                           key=key + '_moment_' + str(preview_duration))
        try:
            preview = _preview(resource_id, definition, preview_duration, title, accent, second)
            st.image(preview, width='content', alt='Esquema ilustrativo: ' + entry['name'])
        except (ValueError, TypeError, KeyError, OSError) as error:
            st.error('No se puede representar el recurso: ' + str(error))
        st.caption('La vista usa el mismo render que el MP4. En Studio podrás mover, agrupar, ocultar o eliminar cada elemento.')
