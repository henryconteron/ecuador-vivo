"""Launch composition over the canonical project; no illustrative fake projects."""
import base64
import copy
import html
import io
import json
import hashlib
import datetime as dt
import unicodedata
from pathlib import Path
import streamlit as st
SOURCE_MTIME=Path(__file__).stat().st_mtime_ns


def entry_icon(path):
    """Local vector artwork survives Streamlit's HTML sanitizer as an image."""
    svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><path d="'+path+'" fill="none" stroke="#58e4ce" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/></svg>'
    return '<div class="home-entry-icon" aria-hidden="true"><img alt="" src="data:image/svg+xml;base64,'+base64.b64encode(svg.encode('utf-8')).decode('ascii')+'"></div>'


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
    prepared=PreparedTimeline(project);cache=StudioPreviewCache()
    with AssetFrames(project['studio']['media'],cache=cache.media) as assets:
        view=cache.for_timeline(prepared,assets)
        return view._thumbnail(scene['id'] if scene else prepared.rows[0]['id'])


@st.cache_data(max_entries=8,show_spinner=False)
def _cover_bytes(path,modified):
    return Path(path).read_bytes()


def workspace_entries(document):
    """Decorative, bounded static art; never render a saved project on arrival."""
    entries=[('sig','SIG','Mapas y análisis','Explora capas, consulta valores y prepara series temporales.','Abrir SIG',':material/layers:','SIG'),
             ('studio','Studio','Montaje y narración','Compón escenas, ajusta tu voz y exporta el video final.','Abrir Studio',':material/movie:','Editor'),
             ('resources','Recursos','Diseños para explicar','Crea esquemas, anima elementos y guarda diseños reutilizables.','Abrir Recursos',':material/animation:','Recursos')]
    with st.container(key='ev_home_entries'):
        feature,companions=st.columns([1.35,1],gap='medium')
        def entry_content(entry,compact=False):
            slug,title,subtitle,description,label,icon,section=entry
            cover=Path(__file__).with_name('workspace_frontend')/'art'/(slug+'-cover.webp')
            def artwork():
                if cover.is_file():st.image(_cover_bytes(str(cover),cover.stat().st_mtime_ns),width='stretch',alt='')
            def actions():
                st.html('<div class="home-entry-title"><h2>'+title+'</h2><span>'+subtitle+'</span></div>')
                st.caption(description)
                if st.button(label,key={'sig':'home_sig','studio':'home_continue','resources':'home_resources'}[slug],
                             icon=icon,type='primary',width='stretch'):
                    _enter_workspace(document,section)
            with st.container(key='ev_home_'+slug,border=True):
                if compact:
                    picture,content=st.columns([.38,.62],gap='medium')
                    with picture:artwork()
                    with content:actions()
                else:
                    artwork();actions()
        with feature:entry_content(entries[1])
        with companions:
            entry_content(entries[0],True)
            entry_content(entries[2],True)


def launch(document,recent_paths=(),*,show_entries=True):
    st.html(Path(__file__).with_name('workspace_frontend')/'surfaces.css')
    st.html(Path(__file__).with_name('workspace_frontend')/'home.css')
    name=html.escape(str(document.get('name','Proyecto sin título') if document else 'Sin proyecto abierto'))
    with st.container(key='ev_home_nav',horizontal=True,vertical_alignment='center'):
        mark=Path(__file__).resolve().parents[2]/'assets/images/ecuador-vivo-mark.svg'
        brand_image='data:image/svg+xml;base64,'+base64.b64encode(_cover_bytes(str(mark),mark.stat().st_mtime_ns)).decode('ascii')
        st.html('<div class="home-brand"><img src="'+brand_image+'" alt="" width="44" height="44"><strong>Ecuador Vivo</strong></div>')
        st.button('Inicio',disabled=True,key='home_nav_current')
        if st.button('SIG',key='home_nav_sig'):
            _enter_workspace(document,'SIG')
        if st.button('Studio',key='home_nav_studio'):
            _enter_workspace(document,'Editor')
        if st.button('Recursos',key='home_nav_resources'):
            st.session_state['section']='Recursos';st.rerun()
        st.html('<span class="home-project" title="'+name+'">'+name+'</span>')
        if document and st.button('Cerrar proyecto',key='home_close_project',icon=':material/close:'):
            st.session_state['project']=None
            st.session_state['project_document']=None
            st.session_state.pop('_pending_studio_navigation',None)
            st.session_state.pop('home_mode',None)
            st.session_state['section']='Inicio'
            st.rerun()
    art=Path(__file__).resolve().parents[2]/'assets/images/expedicion/andes-hero.webp'
    image='data:image/webp;base64,'+base64.b64encode(_cover_bytes(str(art),art.stat().st_mtime_ns)).decode('ascii')
    font=Path(__file__).with_name('assets')/'fonts'/'Lora-Variable.ttf'
    face='data:font/ttf;base64,'+base64.b64encode(_cover_bytes(str(font),font.stat().st_mtime_ns)).decode('ascii')
    st.html('<style>@font-face{font-family:EVLora;src:url("'+face+'");font-weight:400 700;font-display:swap}</style>')
    st.html('<header class="home-hero expedition-desk"><img class="desk-landscape" src="'+image+'" alt="" width="1600" height="800"><div><span class="desk-eyebrow">ECUADOR VIVO / MESA DE PRODUCCIÓN</span><h1>Del territorio<br>a la historia.</h1><p>Explora su ciencia. Diseña una explicación.<br>Cuenta una historia que merezca ser vista.</p></div><aside><strong>Un país por descubrir.</strong>SIG · Studio · Recursos<br>Un mismo proyecto, de principio a fin.</aside><small>Ilustración conceptual · no representa observaciones ni cartografía.</small></header>')
    if show_entries:workspace_entries(document)


def _enter_workspace(document,section):
    if section=='Recursos':
        st.session_state['section']='Recursos';st.rerun()
    if document:
        st.session_state['section']=section
        if section=='Editor':st.session_state['studio_phase']='Estudio'
    else:
        from studio_home import create_project
        from studio_project import replace_document
        candidate=create_project('free',{'id':'youtube' if section=='SIG' else 'tiktok'},
                                 name='Mapa sin título' if section=='SIG' else 'Video sin título')
        if section=='SIG':
            from studio_sig_references import initial_map
            with st.spinner('Abriendo mapa de referencia…'):candidate=initial_map(candidate)
        replace_document(st.session_state,candidate)
        st.session_state.pop('_pending_studio_navigation',None)
        st.session_state.pop('home_mode',None)
        st.session_state['section']=section
        if section=='Editor':st.session_state['studio_phase']='Estudio'
    st.rerun()


@st.cache_data(max_entries=512,show_spinner=False)
def project_summary(path,modified,size):
    """Read light metadata, never calculate science or render media for listing."""
    from studio_recovery import MAX_BYTES
    if size>MAX_BYTES:raise ValueError('El proyecto supera el presupuesto de 64 MiB.')
    data=json.loads(Path(path).read_text(encoding='utf-8-sig'))
    if not isinstance(data,dict):raise ValueError('El proyecto debe ser un objeto JSON.')
    studio=data.get('studio',{})
    if not isinstance(studio,dict):raise ValueError('Estructura Studio inválida.')
    return {'name':str(data.get('name') or Path(path).stem),
        'scenes':len(studio.get('timeline',[])),
        'variable':str(data.get('variable') or ''),
        'start':str(data.get('start') or ''),'end':str(data.get('end') or '')}


def _search_text(value):
    return ''.join(c for c in unicodedata.normalize('NFKD',value.casefold()) if not unicodedata.combining(c))


def recents(paths,open_project,validate_document):
    """Searchable, paginated catalogue; an unavailable thumbnail never blocks open."""
    from studio_recovery import recover_snapshot
    st.html('<div class="home-catalog-heading"><h2>Tus proyectos</h2><span>Tu mesa de trabajo, lista para continuar.</span></div>')
    if not paths:
        st.info('Tu próximo proyecto empieza aquí. Crea uno en SIG o Studio, o abre una copia guardada.');return
    search=st.text_input('Buscar proyectos',placeholder='Nombre, variable o archivo…',key='home_project_search')
    with st.container(horizontal=True,vertical_alignment='center'):
        order=st.selectbox('Ordenar proyectos',['Más recientes','Nombre'],key='home_project_order')
        show_images=st.checkbox('Mostrar miniaturas',value=False,key='home_project_thumbnails',help='Opcional: solo se dibujan los proyectos de esta página.')
    entries=[]
    for path in paths:
        try:
            stat=path.stat()
            summary=project_summary(str(path),stat.st_mtime_ns,stat.st_size)
            entry={'path':path,'modified':stat.st_mtime,**summary}
        except (ValueError,TypeError,KeyError,OSError) as error:
            entry={'path':path,'name':path.stem,'modified':0,'error':str(error)}
        if not search.strip() or _search_text(search.strip()) in _search_text(' '.join(str(entry.get(k,'')) for k in ('name','variable','path'))):
            entries.append(entry)
    if order=='Nombre':entries.sort(key=lambda item:_search_text(item['name']))
    count=len(entries)
    st.caption(f'{count} de {len(paths)} proyectos · carpeta local · originales conservados al abrir')
    if not count:
        st.info('No hay proyectos que coincidan con la búsqueda. Prueba otro nombre.');return
    page_size=12
    pages=(count+page_size-1)//page_size
    page_key='home_project_page_'+hashlib.sha256((search+'|'+order+'|'+str(pages)).encode()).hexdigest()[:12]
    page=st.selectbox('Página',range(1,pages+1),format_func=lambda value:f'{value} de {pages}',key=page_key) if pages>1 else 1
    visible=entries[(page-1)*page_size:page*page_size]
    for offset in range(0,len(visible),3):
        columns=st.columns(min(3,len(visible)-offset),gap='small')
        for column,entry in zip(columns,visible[offset:offset+3]):
            path=entry['path']
            identifier=hashlib.sha256(str(path.resolve()).encode()).hexdigest()[:16]
            with column,st.container(border=True,key='ev_home_recent_'+identifier):
                st.markdown('**'+html.escape(entry['name'])+'**')
                if 'error' in entry:
                    st.warning('Revisar archivo: '+entry['error'])
                else:
                    modified=dt.datetime.fromtimestamp(entry['modified']).strftime('%d/%m/%Y · %H:%M')
                    st.caption(f"{entry['scenes']} escenas · {modified}")
                    if entry['variable']:st.caption(entry['variable']+' · '+entry['start']+' → '+entry['end'])
                if show_images:
                    try:
                        image=thumbnail(str(path),path.stat().st_mtime_ns)
                        st.html('<img class="home-recent-image" src="'+image+'" alt="Miniatura de una escena del proyecto guardado">')
                    except (ValueError,TypeError,KeyError,OSError,IndexError):
                        st.caption('Miniatura no disponible; puedes abrir el proyecto para revisar sus recursos.')
                if st.button('Abrir proyecto',key='home_project_open_'+identifier,icon=':material/folder_open:',width='stretch',help=path.name):
                    try:
                        data,previous=recover_snapshot(path)
                        open_project(validate_document(data))
                        if previous:st.session_state['home_recovered_previous']=path.name
                        st.session_state['section']='Editor';st.session_state['studio_phase']='Estudio';st.rerun()
                    except (ValueError,TypeError,KeyError,OSError) as error:
                        st.error('No se pudo abrir el proyecto: '+str(error))

