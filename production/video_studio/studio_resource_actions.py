"""Explicit illustration library actions, reusing the normal snapshot store."""
from pathlib import Path
import uuid

GRAPHIC_ELEMENTS={
    'rectangle':'Rectángulo','rounded_rectangle':'Tarjeta','circle':'Círculo',
    'line':'Línea','divider':'Separador','marker':'Punto con borde',
    'panel':'Panel','pill_outline':'Etiqueta','play':'Reproducción',
    'icon.cloud':'Lluvia','icon.calendar':'Calendario','icon.thermometer':'Temperatura',
    'icon.wind':'Viento','icon.bars':'Comparación','icon.peak':'Variación',
    'icon.index':'Índice','icon.pin':'Ubicación','icon.database':'Fuente de datos',
    'icon.tiktok':'TikTok','icon.instagram':'Instagram','icon.mountain':'Relieve'}


def persist_resource(session,name,category='Mis recursos'):
    """Write a new owned resource copy; never overwrite the source video."""
    from studio_resource_projects import resource_from_scene
    from studio_timeline import PreparedTimeline
    from studio_media import AssetFrames
    from studio_recovery import save_snapshot
    candidate=resource_from_scene(session.project,session.selected,name,category)
    prepared=PreparedTimeline(candidate)
    with AssetFrames(candidate['studio']['media']) as assets:
        prepared.frame_at(0,assets=assets,authoring=True).close()
    root=session.store.resolve()
    folder=(root/'projects').resolve()
    if not folder.is_relative_to(root):raise ValueError('La biblioteca está fuera del almacenamiento del Studio.')
    destination=folder/('recurso-'+uuid.uuid4().hex+'.json')
    if destination.exists():raise ValueError('El destino ya existe; vuelve a intentar sin sobrescribirlo.')
    save_snapshot(destination,candidate)
    return destination


def show_save_resource(session,*,key):
    import streamlit as st
    scene=next(s for s in session.project['studio']['scenes'] if s['id']==session.selected)
    st.caption('Guarda una copia reutilizable de esta escena. Tu video, mapas, métricas, voz y subtítulos originales no se modifican.')
    with st.form(key+'_form'):
        name=st.text_input('Nombre del recurso',scene.get('name') or 'Mi recurso',max_chars=180)
        category=st.text_input('Categoría','Mis recursos',max_chars=80)
        save=st.form_submit_button('Guardar en Mis recursos',type='primary')
    if save:
        try:
            path=persist_resource(session,name,category)
            st.success('Guardado en Mis recursos. Puedes seguir editando esta escena o volver a la biblioteca.')
            st.caption(path.name)
        except (ValueError,TypeError,KeyError,OSError) as error:st.error(str(error))
    if st.button('Cerrar',key=key+'_close'):
        session.state.pop(session.key+'_dialog',None);st.rerun()
