"""Launch composition over the canonical project; no illustrative fake projects."""
import base64
import copy
import html
import io
import json
import hashlib
from pathlib import Path
import streamlit as st
SOURCE_MTIME=Path(__file__).stat().st_mtime_ns


@st.cache_data(max_entries=1,show_spinner=False)
def reference_art():
    folder=Path(__file__).with_name('reference_data')
    content=(folder/'ecuador-national.geojson').read_bytes()
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    if hashlib.sha256(content).hexdigest()!=manifest['ecuador-national']['sha256']:raise ValueError('Referencia visual modificada.')
    geometry=json.loads(content)['features'][0]['geometry']
    polygons=geometry['coordinates'] if geometry['type']=='MultiPolygon' else [geometry['coordinates']]
    paths=[]
    for polygon in polygons:
        paths.append(' '.join('M'+' L'.join(f'{(float(x)+92)*20:.2f},{(2-float(y))*26:.2f}' for x,y,*_ in ring)+' Z' for ring in polygon))
    svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 350 190"><path d="'+' '.join(paths)+'" fill="#236b73" fill-rule="evenodd" stroke="#82e4ca" stroke-width="1"/></svg>'
    # An image preserves the validated SVG across Streamlit's HTML sanitization.
    return '<img src="data:image/svg+xml;base64,'+base64.b64encode(svg.encode('utf-8')).decode('ascii')+'" alt="Ecuador y Galápagos en ubicación real, referencia geoBoundaries"><small>geoBoundaries · CC BY 4.0</small>'


@st.cache_data(max_entries=12,show_spinner=False)
def thumbnail(path,modified):
    from studio_recovery import recover_snapshot
    from studio_timeline import PreparedTimeline
    from studio_media import AssetFrames
    from studio_cache import StudioPreviewCache
    project,_=recover_snapshot(Path(path))
    project=copy.deepcopy(project)
    scene=next((s for s in project['studio']['scenes'] if s['id'] in project['studio']['timeline'] and any(e.get('visible',True) and not e.get('editor_deleted') for e in s.get('elements',[]))),None)
    project['studio']['timeline']=[scene['id']] if scene else project['studio']['timeline'][:1]
    prepared=PreparedTimeline(project);cache=StudioPreviewCache()
    with AssetFrames(project['studio']['media'],cache=cache.media) as assets:
        return cache.for_timeline(prepared,assets).thumbnails()[0]['thumbnail']


def launch(document,recent_paths=()):
    st.html(Path(__file__).with_name('workspace_frontend')/'home.css')
    name=html.escape(str((document or {}).get('name','Proyecto sin título')))
    with st.container(key='ev_home_nav',horizontal=True,vertical_alignment='center'):
        st.html('<div class="home-brand"><span>EV</span><strong>Ecuador Vivo</strong></div>')
        st.button('Inicio',disabled=True,key='home_nav_current')
        if st.button('SIG',key='home_nav_sig'):
            st.session_state['section']='SIG';st.rerun()
        if st.button('Studio',key='home_nav_studio'):
            st.session_state['section']='Editor';st.session_state['studio_phase']='Estudio';st.rerun()
        st.html('<span class="home-project" title="'+name+'">'+name+'</span>')
    st.html('<header class="home-hero"><h1>¿Qué quieres crear hoy?</h1><p>Explora, analiza y compón. Tus datos y tu historia, en un proyecto compartido.</p></header>')
    with st.container(key='ev_home_entries'):
        left,right=st.columns(2,gap='medium')
        with left,st.container(key='ev_home_sig',border=True):
            st.html('<div class="home-entry-icon" aria-hidden="true">◇</div><h2>SIG</h2><p class="home-entry-copy">Explora datos geográficos, consulta tus capas y prepara mapas científicos.</p><div class="home-map-art">'+reference_art()+'</div>')
            if st.button('Abrir SIG',type='primary',key='home_sig',icon=':material/map:'):
                st.session_state['section']='SIG';st.rerun()
        with right,st.container(key='ev_home_studio',border=True):
            art='<i></i><i></i><i></i>'
            if recent_paths:
                try:art='<img src="'+thumbnail(str(recent_paths[0]),recent_paths[0].stat().st_mtime_ns)+'" alt="Composición real de una escena reciente">'
                except (ValueError,TypeError,KeyError,OSError):pass
            st.html('<div class="home-entry-icon" aria-hidden="true">▷</div><h2>Studio</h2><p class="home-entry-copy">Crea videos con mapas, textos, imágenes y escenas que puedes editar.</p><div class="home-film-art">'+art+'</div>')
            if st.button('Abrir Studio',type='primary',key='home_continue',icon=':material/movie:'):
                st.session_state['section']='Editor';st.session_state['studio_phase']='Estudio';st.rerun()


def recents(paths,open_project,validate_document):
    import json
    st.markdown('### Proyectos recientes')
    if not paths:
        st.info('Tu próximo proyecto empieza aquí. Crea uno en SIG o Studio, o abre una copia guardada.');return
    columns=st.columns(min(3,len(paths)),gap='small')
    for index,path in enumerate(paths[:3]):
        with columns[index],st.container(border=True,key='ev_home_recent_'+str(index)):
            try:
                data=json.loads(path.read_text(encoding='utf-8'))
                image=thumbnail(str(path),path.stat().st_mtime_ns)
                # Existing scientific renderer output, never a stock thumbnail.
                st.html('<img class="home-recent-image" src="'+image+'" alt="Miniatura de una escena del proyecto guardado">')
                st.markdown('**'+html.escape(str(data.get('name',path.stem)))+'**')
                st.caption(str(len(data.get('studio',{}).get('timeline',[])))+' escenas · copia guardada')
                if st.button('Abrir',key='home_recent_'+str(index),icon=':material/folder_open:'):
                    open_project(validate_document(data));st.session_state['section']='Editor';st.session_state['studio_phase']='Estudio';st.rerun()
            except (ValueError,TypeError,KeyError,OSError) as error:
                st.caption(path.stem);st.warning('Miniatura no disponible: '+str(error))

