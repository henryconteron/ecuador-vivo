'''Ecuador Vivo local video studio.

Launch with:
    Abrir editor de videos.vbs

The approved Ecuador Vivo / Andes Pulso composition is available as:
    Maqueta Ecuador Vivo · aprobada
'''

import copy
import datetime as dt
import io
import importlib
import json
import os
from pathlib import Path
import sys
import uuid

import pandas as pd
import streamlit as st

# Streamlit reruns this file in the same Python process. During a hot reload,
# ``model`` can otherwise remain the old cached module and make a newly added
# constant (for example TEMPLATE_VERSION) look missing. Reload once here so
# app.py, render.py and jobs.py all use the same current project schema.
import model as _model
_model = importlib.reload(_model)
default_project = _model.default_project
upgrade_project = _model.upgrade_project
validate = _model.validate
timeline = _model.timeline
PALETTES = _model.PALETTES
STORE = _model.STORE
ROOT = _model.ROOT
TEMPLATE_VERSION = getattr(_model, 'TEMPLATE_VERSION', 1)

# Hot reload keeps imported modules in sys.modules. Reload the renderer graph
# as one unit: otherwise a previous render.py may still route the new
# ``maqueta`` layout to the older social renderer and raise KeyError('maqueta').
import data as _data
_data = importlib.reload(_data)
import variables as _variables
_variables = importlib.reload(_variables)
if 'layout_engine' in sys.modules:
    importlib.reload(sys.modules['layout_engine'])
if 'maqueta' in sys.modules:
    _maqueta = importlib.reload(sys.modules['maqueta'])
if 'endcard' in sys.modules:
    _endcard = importlib.reload(sys.modules['endcard'])
for module_name in ('editorial', 'comparison_maps'):
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
import render as _render
_render = importlib.reload(_render)
import social as _social
_social = importlib.reload(_social)
import jobs as _jobs
_jobs = importlib.reload(_jobs)
import publication as _publication
_publication = importlib.reload(_publication)
import providers as _providers
_providers = importlib.reload(_providers)
for module_name in ('storyboard', 'workspace', 'storyboard_ui', 'climate_comparison', 'comparison_video', 'climate_comparison_ui', 'spatial_csv_ui'):
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])

# CCv2 is registered once per module load, not on every interaction. Refresh
# its inline assets only when their source changed during local development.
_layout_module = sys.modules.get('layout_editor')
if _layout_module and getattr(_layout_module, 'SOURCE_MTIME', None) != Path(_layout_module.__file__).stat().st_mtime_ns:
    importlib.reload(_layout_module)

boundary = _data.boundary
load_values = _data.load_values
store_upload = _data.store_upload
inspect_file = _data.inspect_file
compose = _render.compose
guided_preview = _social.guided_preview
start_job = _jobs.start_job
read_json = _jobs.read_json
write_json = _jobs.write_json
statuses = _jobs.statuses
default_case_id = _publication.default_case_id
prepare_case = _publication.prepare_case
from endcard import compose_endcard, summary_for_project
detect_profile = _variables.detect_profile
resolve_aggregation = _variables.resolve_aggregation


# =============================================================================
# APP
# =============================================================================

st.set_page_config(
    page_title='Ecuador Vivo · Estudio de video',
    page_icon=':material/movie:',
    layout='wide'
)

st.session_state.setdefault('project', default_project())
st.session_state.setdefault('revision', 0)
st.session_state.setdefault('preview', None)
st.session_state.setdefault('endcard_preview', None)
st.session_state.setdefault('import_rows', [])
st.session_state.setdefault('active_job', None)
st.session_state.setdefault('section', 'Inicio')
# Retain navigation while its native radio is absent on home/Studio surfaces.
st.session_state.section = st.session_state.section
from studio_project import request_studio_navigation, consume_studio_navigation
consume_studio_navigation(st.session_state)

# Force a one-time migration when the renderer/template version changes.
# Streamlit preserves session_state across hot reloads, which otherwise leaves
# the old "La lluvia cambia" project active even after replacing the files.
if st.session_state.get('_ecuador_vivo_template_version') != TEMPLATE_VERSION:
    st.session_state.project = upgrade_project(st.session_state.project)
    st.session_state.preview = None
    st.session_state.endcard_preview = None
    st.session_state.revision += 1
    st.session_state['_ecuador_vivo_template_version'] = TEMPLATE_VERSION
    st.cache_data.clear()

# Provider downloads can be handed into the editor on the next rerun. Consume
# the queued project before the sidebar widget is created, as Streamlit does
# not allow changing a widget's value after it has been instantiated.
pending_provider_project = st.session_state.pop('_pending_provider_project', None)
pending_provider_section = st.session_state.pop('_pending_provider_section', None)
if pending_provider_project is not None:
    st.session_state.project = upgrade_project(pending_provider_project)
    st.session_state.preview = None
    st.session_state.endcard_preview = None
    st.session_state.import_rows = []
    st.session_state.revision += 1
if pending_provider_section:
    st.session_state.section = pending_provider_section
if st.session_state.section != 'Obtener datos':
    st.session_state.pop('science_acquisition', None)

p = upgrade_project(st.session_state.project)
revision = st.session_state.revision
from studio_project import synchronize_source, source_projection, workspace_key, replace_document, validate_document
synchronize_source(st.session_state, p)
p = st.session_state.project

# Included in the cached preview key so old PNGs can never survive a renderer
# update with the same project JSON.
RENDER_CACHE_VERSION = f'ecuador-vivo-maqueta-{TEMPLATE_VERSION}-visual-1'


# =============================================================================
# HELPERS
# =============================================================================

def replace_project(project):
    document = replace_document(st.session_state, upgrade_project(copy.deepcopy(project)))
    if 'studio' in project:
        request_studio_navigation(st.session_state)
    st.session_state.revision += 1
    st.session_state.preview = None
    st.session_state.endcard_preview = None
    st.session_state.import_rows = []
    st.session_state.pop('climate_comparison', None)
    stored = project.get('comparison_data')
    if stored:
        restored = copy.deepcopy(stored)
        restored['frames'] = [pd.DataFrame(rows) for rows in stored.get('frames', [])]
        st.session_state.climate_comparison = restored


@st.cache_data(max_entries=8, show_spinner=False)
def preview_bytes(project_json, index, render_cache_version):
    _ = render_cache_version
    project = json.loads(project_json)
    rows = validate(project)
    values, _ = load_values(project, rows[index])

    image = compose(
        project,
        values,
        boundary(),
        rows[index]['date'],
        index,
        len(rows)
    )
    from storyboard import format_preview
    image = format_preview(image, project)

    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()


@st.cache_data(max_entries=4, show_spinner=False)
def endcard_preview_bytes(project_json, render_cache_version):
    """Create the same data-driven closing card used by the worker."""
    _ = render_cache_version
    project = json.loads(project_json)
    rows = validate(project)
    summary = summary_for_project(project, rows, boundary())
    image = compose_endcard(project, summary)
    from storyboard import format_preview
    image = format_preview(image, project)
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()


@st.cache_data(max_entries=4, show_spinner=False)
def _editor_summary(scientific_json, file_versions):
    project = default_project()
    project.update(json.loads(scientific_json))
    return summary_for_project(project, timeline(project), boundary())


def editor_summary(settings):
    # Moving a text/icon must not reread hundreds of daily rasters. Only the
    # data/method identity participates in this cache. Local file changes
    # invalidate it; no scientific result is altered by presentation edits.
    fields = ('source', 'start', 'end', 'entries', 'bbox', 'scale', 'offset',
              'nodata', 'clip_ecuador', 'kind', 'variable', 'units', 'cadence',
              'endcard_aggregation', 'endcard_aggregation_mode', 'endcard_accumulated_units',
              '_scientific_revision_sha256')
    values = {key: settings[key] for key in fields if key in settings}
    return _editor_summary(json.dumps(values, sort_keys=True), _data.scientific_file_versions(settings))


def snapshot():
    return json.dumps(
        p,
        ensure_ascii=False,
        sort_keys=True
    )


def save_project():
    target = (
        STORE
        / 'projects'
        / (
            dt.datetime.now().strftime('%Y%m%d-%H%M%S')
            + '-'
            + uuid.uuid4().hex[:6]
            + '.json'
        )
    )
    write_json(target, synchronize_source(st.session_state, p))
    return target


def create_studio_from_snapshot(scientific_snapshot):
    from studio_science import generate_scientific_project
    from visualization_ui import scientific_identity
    if scientific_identity(p) != scientific_snapshot['scientific_identity']:
        raise ValueError('La fuente cambió; carga nuevamente los resultados.')
    document=synchronize_source(st.session_state,p)
    candidate=generate_scientific_project(document,scientific_snapshot,
        document['studio']['output_profile'],theme=document['studio'].get('theme','Ecuador Vivo'))
    replace_project(candidate)
    request_studio_navigation(st.session_state)
    st.rerun()


def rerun_project():
    st.session_state.revision += 1
    st.session_state.preview = None
    st.session_state.endcard_preview = None
    st.rerun()


def restore_maqueta_style():
    defaults = default_project()

    for key in (
        'background',
        'text',
        'accent',
        'palette',
        'stops',
        'title_gradient_1',
        'title_gradient_2',
        'show_galapagos',
        'show_provinces',
        'show_play_button',
    ):
        p[key] = copy.deepcopy(defaults[key])

    p['layout'] = 'maqueta'
    rerun_project()


@st.cache_data(ttl=1800, show_spinner=False)
def cached_inamhi_stations():
    return _providers.inamhi_stations()


@st.cache_data(ttl=1800, show_spinner=False)
def cached_inamhi_parameters(station_id):
    return _providers.inamhi_parameters(station_id)


def _queue_provider_project(result, provider):
    """Use a downloaded gridded time series without losing the visual template."""
    candidate = copy.deepcopy(p)
    candidate.update(
        source='local',
        entries=copy.deepcopy(result['entries']),
        start=result['start'],
        end=result['end'],
        cadence='Diaria',
        scale=1.0,
        offset=0.0,
        nodata=-9999.0,
        clip_ecuador=True,
        endcard_aggregation_mode='auto',
        endcard_rank_mode='provinces',
        citation=result['citation'],
        source_url=result['source_url'],
        resolution_note=result['resolution_note'],
        note=result['note'],
        endcard_footer=result.get('endcard_footer', result['citation']),
        endcard_footer_2=result.get(
            'endcard_footer_2',
            'Ecuador continental · límites: geoBoundaries'
        ),
        endcard_subtitle=(
            f"Así cambió {result['variable'].lower()} en Ecuador "
            f"durante {result['start'][:4]}."
        ),
        endcard_enabled=bool(result.get('endcard_enabled', False)),
        show_galapagos=bool(result.get('show_galapagos', False)),
        bbox=list(result.get('map_bbox', _providers.ECUADOR_MAP_BBOX)),
    )
    for key in ('variable', 'units', 'legend', 'title', 'description', 'kind'):
        if result.get(key) is not None:
            candidate[key] = result[key]
    if result.get('stops'):
        candidate['stops'] = list(result['stops'])
    if result.get('palette'):
        candidate['palette'] = list(result['palette'])
    if result.get('endcard_aggregation'):
        candidate['endcard_aggregation'] = result['endcard_aggregation']
    if result.get('accumulated_units'):
        candidate['endcard_accumulated_units'] = result['accumulated_units']
    candidate['endcard_title'] = 'MÉTRICAS DEL PERÍODO'
    candidate['endcard_section_2_note'] = (
        'Provincias · promedio espacial · ranking 1–12'
    )
    candidate['endcard_section_3'] = 'PROVINCIAS 13–24'
    candidate['endcard_section_3_note'] = 'Continuación del ranking.'
    candidate['endcard_auto_text'] = True
    candidate['scale_note'] = result.get(
        'scale_note', result['resolution_note']
    )
    candidate['name'] = (
        f"{provider} · {result['variable']} · "
        f"{result['start']}–{result['end']}"
    )
    candidate['title'] = result.get(
        'title', result['variable'].upper() + ' EN ECUADOR'
    )
    candidate['description'] = result.get(
        'description',
        f"Evolución diaria · {result['start']} a {result['end']}."
    )
    candidate['endcard_footer'] = result.get(
        'endcard_footer',
        f"{provider} · {result['resolution_note']}"
    )
    validate(candidate)
    if st.session_state.pop('science_acquisition',False):
        st.session_state['_pending_scientific_source'] = candidate
        st.session_state['home_mode'] = 'scientific'
        st.session_state['_pending_provider_section'] = 'Inicio'
        st.rerun()
    st.session_state._pending_provider_project = candidate
    st.session_state._pending_provider_section = 'Editor'
    st.rerun()


# =============================================================================
# SIDEBAR
# =============================================================================

# Studio owns a bounded viewport. Route before the legacy sidebar/forms, while
# retaining every earlier phase and the same source project/revision.
if st.session_state.section == 'Inicio':
    from studio_home import show_home
    show_home(replace_project,document=st.session_state.project_document)
    st.stop()
if st.session_state.section == 'SIG':
    from studio_sig import show_sig
    try: show_sig(p)
    except (ValueError,TypeError,KeyError,OSError) as error: st.error('No se pudo abrir SIG: '+str(error))
    st.stop()
if st.session_state.get('section','Editor')=='Editor' and st.session_state.get('studio_phase')=='Estudio':
    from studio_workspace import show_workspace
    document = synchronize_source(st.session_state, p)
    show_workspace(p,key=workspace_key(document),snapshot=st.session_state.get(f'visualizations_{revision}_snapshot'),canonical=True)
    st.stop()

with st.sidebar:
    st.markdown('**ECUADOR VIVO**')

    st.caption(
        'ESTUDIO DE VIDEO · LOCAL'
    )

    if st.session_state.section == 'Comparar para video':
        st.session_state.section = 'Editor'
        p['video_type'] = 'Comparación climática'
    section = st.radio(
        'Espacio de trabajo',
        [
            'Inicio',
            'Editor',
            'Obtener datos',
            'Exportaciones',
            'Cómo usarlo'
        ],
        key='section'
    )

    st.divider()

    st.header(
        'Tus proyectos'
    )

    projects = sorted(
        (STORE / 'projects').glob('*.json'),
        reverse=True
    )

    chosen = st.selectbox(
        'Abrir un proyecto guardado',
        [None] + projects,
        format_func=lambda f:
            'Selecciona…'
            if f is None
            else (
                read_json(f, {}).get('name', f.stem)
                + ' · '
                + f.stem[:15]
            )
    )

    if st.button(
        'Abrir proyecto',
        disabled=chosen is None,
        icon=':material/folder_open:'
    ):
        candidate = read_json(chosen)
        try:
            validate_document(candidate)
            replace_project(candidate)
            st.rerun()
        except (
            ValueError,
            TypeError,
            KeyError
        ) as error:
            st.error(
                f'No se pudo abrir: {error}'
            )

    if st.button(
        'Nuevo proyecto',
        icon=':material/add:',
        width='stretch',
    ):
        replace_project(
            default_project()
        )
        st.rerun()

    with st.expander(
        'Importar proyecto JSON'
    ):
        restored = st.file_uploader(
            'Proyecto exportado',
            type=['json'],
            key='restore_file'
        )

        if st.button(
            'Restaurar ajustes',
            disabled=restored is None
        ):
            try:
                candidate = json.loads(
                    restored.getvalue()
                )
                validate_document(candidate)
                replace_project(candidate)
                st.rerun()
            except (
                ValueError,
                TypeError,
                KeyError
            ) as error:
                st.error(
                    f'No se pudo restaurar: {error}'
                )

    st.caption(
        'Los proyectos y videos permanecen en tu computadora.'
    )


# =============================================================================
# HELP
# =============================================================================

if section == 'Cómo usarlo':

    st.title('Del dato al video')

    st.markdown(
        '''
1. En **Obtener datos**, descarga un período de CHIRPS v3 o NASA POWER y
   envíalo directamente al **Editor**; para INAMHI puedes consultar y descargar
   observaciones diarias de una estación.
2. En **Editor**, elige **Mapa temporal**, **Comparación climática** o **CSV geográfico**.
3. En **Datos**, prepara y revisa las fechas, unidades, cálculos o coordenadas.
4. En **Maqueta**, ajusta el mapa y las métricas en el mismo lienzo: mueve,
   redimensiona, añade o elimina textos e iconos. **Eliminar elemento** quita
   la capa del diseño; **Recuperar elemento** permite volver a ponerla.
   Las cifras calculadas no se sustituyen por valores escritos manualmente.
5. Pulsa **OK · aplicar y guardar** antes de cambiar de tarjeta o de apartado.
   Los cambios se dibujan aquí; no hay otra vista previa que actualizar.
6. En **Montaje**, elige el formato (redes o YouTube), el orden y los tiempos.
   También puedes añadir imágenes, clips y tarjetas explicativas.
7. En **Exportar**, guarda el proyecto y pulsa **Generar video**.

### Maqueta Ecuador Vivo
La plantilla aprobada conserva la estructura visual:
- cabecera Ecuador Vivo / Andes Pulso;
- contador temporal;
- mapa principal;
- Galápagos opcional;
- límites provinciales opcionales;
- leyenda;
- fuente, autoría y redes.

El lienzo y la exportación utilizan las mismas capas y el mismo dibujado.
Las guías de seguridad y el borde de selección no aparecen en el MP4.

### Datos
**CHIRPS v3:** precipitación diaria en mm/día, 0,05° (~5,6 km). Sus productos
diarios satelitales y de reanálisis distribuyen acumulados pentadales en días;
el día es una etiqueta coherente, no una ventana de observación uniforme.

**NASA POWER:** campos meteorológicos diarios y gratuitos; descarga nacional
regional en GeoTIFF y CSV. Su grilla nativa es mucho más gruesa que CHIRPS: el
remuestreo de pantalla no añade detalle. Las métricas provinciales quedan
desactivadas por defecto para evitar darles una precisión que no tienen.

**INAMHI:** observaciones diarias de estaciones meteorológicas/hidrológicas.
El editor conserva cada estación como punto y reporta fechas faltantes; no
convierte una estación en promedio provincial ni inventa una superficie.
El endpoint del visor puede limitar el histórico disponible. Si un período
no aparece, el panel enlaza el acceso oficial para solicitarlo.

**GeoTIFF:** una banda seleccionada por fecha. Revisa unidades, escala,
desplazamiento, NoData y preparación científica antes de importar.

### Duración
Todas las fechas aparecen por lo menos un cuadro. Para 366 días, una duración
de alrededor de **26 s** reproduce el ritmo corto de la pieza anual.
'''
    )

    st.code(
        str(STORE),
        language=None
    )

    st.stop()


# =============================================================================
# DATA PROVIDERS
# =============================================================================

if section == 'Obtener datos':
    st.title('Obtener datos')
    st.caption(
        'Descarga desde fuentes originales, conserva el recibo de procedencia '
        'y manda las grillas compatibles directo al editor.'
    )
    source_name = st.selectbox(
        'Fuente de datos',
        ['CHIRPS v3 · lluvia', 'NASA POWER · clima', 'INAMHI · estaciones'],
        key='provider_source',
    )

    if source_name.startswith('CHIRPS'):
        st.header('Precipitación diaria en rejilla')
        st.markdown(
            'CHIRPS v3 ofrece lluvia estimada con resolución de **0,05°**. '
            'Elige un producto y descarga hasta **31 días por paquete**; cada '
            'GeoTIFF se recorta en el equipo para incluir Ecuador continental y '
            'Galápagos. El manifiesto conserva la URL fuente y la huella SHA-256 '
            'del archivo recortado; no descarga el GeoTIFF global completo.'
        )
        product_labels = {
            key: value['label'] for key, value in _providers.CHIRPS_PRODUCTS.items()
        }
        product = st.selectbox(
            'Producto', list(product_labels),
            format_func=product_labels.get,
            index=0,
            key='provider_chirps_product',
        )
        product_info = _providers.CHIRPS_PRODUCTS[product]
        today = dt.date.today()
        default_end = today - dt.timedelta(days=7)
        default_start = default_end - dt.timedelta(days=6)
        period = st.date_input(
            'Período (máximo 31 días)',
            value=(default_start, default_end),
            min_value=product_info['minimum_date'],
            max_value=today,
            key=f'provider_chirps_period_{product}',
        )
        st.info(product_info['method'] + ' La versión preliminar puede revisarse cuando salga la final.')
        chirps_dates = period if isinstance(period, (tuple, list)) else (period,)
        if len(chirps_dates) == 2:
            first, last = chirps_dates
            signature = f'{product}|{first}|{last}'
            if st.button('Descargar y preparar serie', type='primary', key='download_chirps'):
                progress = st.progress(0, text='Conectando con CHIRPS…')

                def chirps_progress(index, total, date_label):
                    progress.progress(
                        index / total,
                        text=f'Día {index} de {total} · {date_label}',
                    )

                try:
                    result = _providers.download_chirps_v3(
                        first, last, product, progress=chirps_progress
                    )
                    result['_signature'] = signature
                    st.session_state.provider_chirps_result = result
                    progress.progress(1.0, text='Serie preparada para el editor.')
                    st.rerun()
                except Exception as error:
                    st.error(f'No se pudo descargar CHIRPS: {error}')
            else:
                result = st.session_state.get('provider_chirps_result')
                if result and result.get('_signature') == signature:
                    st.success(
                        f"{result['count']} días listos · "
                        f"{result['start']} a {result['end']} · {result['resolution_note']}"
                    )
                    st.caption(
                        f"Crédito sugerido: {result['citation']}. "
                        'El paquete incluye GeoTIFF diarios y metadata.json.'
                    )
                    c1, c2 = st.columns(2)
                    c1.download_button(
                        'Descargar paquete GeoTIFF + recibo',
                        Path(result['zip_path']).read_bytes(),
                        file_name=Path(result['zip_path']).name,
                        mime='application/zip',
                        key='download_chirps_zip',
                    )
                    c2.download_button(
                        'Descargar manifiesto',
                        Path(result['manifest_path']).read_bytes(),
                        file_name='metadata-chirps-v3.json',
                        mime='application/json',
                        key='download_chirps_manifest',
                    )
                    if st.button(
                        'Usar esta serie en el editor',
                        type='primary',
                        key='use_chirps_in_editor',
                    ):
                        _queue_provider_project({
                            **result,
                            'endcard_enabled': True,
                            'endcard_aggregation': 'sum',
                            'accumulated_units': 'mm',
                            'show_galapagos': True,
                            'legend': 'LLUVIA DIARIA',
                            'title': 'LLUVIA EN ECUADOR',
                            'variable': 'Precipitación diaria CHIRPS v3',
                            'description': f"Lluvia día a día · {first:%d %b %Y} a {last:%d %b %Y}.",
                            'endcard_footer': f"CHIRPS v3 · 0,05° · {product.upper()}",
                            'endcard_footer_2': 'Ecuador + Galápagos · límites: geoBoundaries',
                            'map_bbox': _providers.ECUADOR_MAP_BBOX,
                        }, 'CHIRPS v3')
        else:
            st.caption('Selecciona fecha inicial y final para habilitar la descarga.')

        st.caption('Fuente oficial: https://chc.ucsb.edu/data/chirps3')

    elif source_name.startswith('NASA'):
        st.header('Clima diario en una grilla regional')
        st.markdown(
            'NASA POWER permite descargar series regionales para una variable '
            'por solicitud. El paquete contiene el CSV original, GeoTIFF '
            'multibanda y manifiesto. El grid meteorológico es de escala '
            'regional (~50–60 km); no es adecuado para inferir diferencias '
            'finas entre provincias o barrios.'
        )
        parameter = st.selectbox(
            'Variable', list(_providers.POWER_VARIABLES),
            format_func=lambda code: (
                f"{_providers.POWER_VARIABLES[code]['label']} "
                f"({_providers.POWER_VARIABLES[code]['units']})"
            ),
            key='provider_power_parameter',
        )
        today = dt.date.today()
        default_end = today - dt.timedelta(days=14)
        default_start = default_end - dt.timedelta(days=6)
        period = st.date_input(
            'Período (máximo 366 días por descarga)',
            value=(default_start, default_end),
            min_value=dt.date(1981, 1, 1),
            max_value=today,
            key='provider_power_period',
        )
        st.caption(
            'Los valores meteorológicos regionales de POWER provienen de '
            'productos de modelado/reanálisis; no son observaciones de '
            'estaciones INAMHI. La API regional acepta una variable por pedido.'
        )
        power_dates = period if isinstance(period, (tuple, list)) else (period,)
        if len(power_dates) == 2:
            first, last = power_dates
            signature = f'{parameter}|{first}|{last}'
            if st.button('Descargar campo y preparar video', type='primary', key='download_power'):
                progress = st.progress(0, text='Consultando NASA POWER…')
                try:
                    result = _providers.download_power_regional(
                        first, last, parameter,
                        progress=lambda index, total, label: progress.progress(
                            index / max(total, 1),
                            text=f'Preparando banda {index} de {total} · {label}',
                        ),
                    )
                    result.update(
                        endcard_enabled=False,
                        show_galapagos=False,
                        endcard_footer=(
                            f"NASA POWER · {parameter} · grilla regional"
                        ),
                        endcard_footer_2=(
                            'Resolución gruesa · no interpretar como estación local'
                        ),
                        map_bbox=_providers.ECUADOR_MAP_BBOX,
                    )
                    result['_signature'] = signature
                    st.session_state.provider_power_result = result
                    progress.progress(1.0, text='Campo listo para el editor.')
                    st.rerun()
                except Exception as error:
                    st.error(f'No se pudo descargar NASA POWER: {error}')
            else:
                result = st.session_state.get('provider_power_result')
                if result and result.get('_signature') == signature:
                    st.success(
                        f"{result['count']} fechas · {result['start']} a {result['end']} · "
                        f"grid {result['manifest']['spatial_resolution_degrees']['latitude']:.3g}° × "
                        f"{result['manifest']['spatial_resolution_degrees']['longitude']:.3g}°"
                    )
                    if result['missing_dates']:
                        st.warning(
                            f"La fuente no devolvió {len(result['missing_dates'])} fecha(s): "
                            + ', '.join(result['missing_dates'][:8])
                        )
                        st.warning(
                            'No enviaré esta serie a un video diario mientras tenga '
                            'fechas ausentes: eso comprimiría el tiempo. Descarga el '
                            'paquete para revisarlo o elige un período sin huecos.'
                        )
                    st.caption(
                        'Se enviará al editor con la tarjeta de métricas finales '
                        'apagada por defecto: la grilla es demasiado gruesa para '
                        'un ranking provincial defendible.'
                    )
                    c1, c2 = st.columns(2)
                    c1.download_button(
                        'Descargar paquete CSV + GeoTIFF',
                        Path(result['zip_path']).read_bytes(),
                        file_name=Path(result['zip_path']).name,
                        mime='application/zip',
                        key='download_power_zip',
                    )
                    c2.download_button(
                        'Descargar metadata',
                        Path(result['manifest_path']).read_bytes(),
                        file_name='metadata-nasa-power.json',
                        mime='application/json',
                        key='download_power_manifest',
                    )
                    if st.button(
                        'Usar esta serie en el editor',
                        type='primary',
                        key='use_power_in_editor',
                        disabled=bool(result['missing_dates']),
                    ):
                        _queue_provider_project({
                            **result,
                            'title': result['title'],
                            'description': (
                                f"Evolución diaria de {result['parameter_name'].lower()} · "
                                f"{first:%d %b %Y} a {last:%d %b %Y}."
                            ),
                            'legend': result['legend'],
                            'map_bbox': _providers.ECUADOR_MAP_BBOX,
                        }, 'NASA POWER')
        else:
            st.caption('Selecciona fecha inicial y final para habilitar la descarga.')

        st.caption('Documentación oficial: https://power.larc.nasa.gov/docs/services/api/temporal/daily/')

    else:
        st.header('Observaciones de estaciones INAMHI')
        st.markdown(
            'Este conector consulta el catálogo del visor diario y permite '
            'descargar la serie CSV de una estación junto con su procedencia. '
            'Empieza en **Napo** para facilitar tu uso en Tena y Archidona.'
        )
        try:
            stations = cached_inamhi_stations()
        except Exception as error:
            stations = []
            st.error(f'No se pudo consultar el catálogo de estaciones: {error}')
            st.link_button('Abrir visor oficial de INAMHI', _providers.INAMHI_VIEWER_URL)
        if stations:
            provinces = sorted({row['province'] for row in stations if row['province']})
            preferred = 'Napo' if 'Napo' in provinces else (provinces[0] if provinces else 'Todas')
            province_options = ['Todas'] + provinces
            province = st.selectbox(
                'Provincia', province_options,
                index=province_options.index(preferred),
                key='provider_inamhi_province',
            )
            filtered_stations = [
                row for row in stations
                if province == 'Todas' or row['province'] == province
            ]
            selected_station = st.selectbox(
                'Estación', filtered_stations,
                format_func=lambda row: ' · '.join(
                    part for part in (
                        row.get('code'), row.get('name'), row.get('canton'), row.get('province')
                    ) if part
                ) or str(row['id']),
                key='provider_inamhi_station',
            )
            try:
                parameters = cached_inamhi_parameters(selected_station['id'])
            except Exception as error:
                parameters = []
                st.error(f'No se pudo consultar el catálogo de variables: {error}')
            if parameters:
                parameter = st.selectbox(
                    'Variable/estadístico disponible', parameters,
                    format_func=lambda row: ' · '.join(
                        part for part in (
                            row['name'], row['statistic'], row['units'], row['code']
                        ) if part
                    ),
                    key=f"provider_inamhi_parameter_{selected_station['id']}",
                )
                today = dt.date.today()
                default_end = today - dt.timedelta(days=1)
                default_start = default_end - dt.timedelta(days=29)
                period = st.date_input(
                    'Período (máximo 31 días)',
                    value=(default_start, default_end),
                    min_value=dt.date(1981, 1, 1),
                    max_value=today,
                    key=f"provider_inamhi_period_{selected_station['id']}",
                )
                st.info(
                    'La estación es una medición puntual. El CSV no representa '
                    'el promedio de Napo ni genera por sí solo un campo continuo '
                    'para el mapa; no se interpolan valores.'
                )
                inamhi_dates = period if isinstance(period, (tuple, list)) else (period,)
                if len(inamhi_dates) == 2:
                    first, last = inamhi_dates
                    signature = f"{selected_station['id']}|{parameter['code']}|{first}|{last}"
                    if st.button('Consultar y preparar datos INAMHI', type='primary', key='download_inamhi'):
                        try:
                            result = _providers.download_inamhi_daily(
                                selected_station, parameter, first, last
                            )
                            result['_signature'] = signature
                            st.session_state.provider_inamhi_result = result
                            st.rerun()
                        except Exception as error:
                            st.error(f'No se pudo obtener la serie INAMHI: {error}')
                    else:
                        result = st.session_state.get('provider_inamhi_result')
                        if result and result.get('_signature') == signature:
                            st.success(
                                f"{result['count']} observaciones dentro del período · "
                                f"{result['start']} a {result['end']}"
                            )
                            if result['returned_date_span_before_filter']:
                                returned = result['returned_date_span_before_filter']
                                if returned['start'] != result['start'] or returned['end'] != result['end']:
                                    st.warning(
                                        'El visor respondió con una ventana diferente a la pedida '
                                        f"({returned['start']}–{returned['end']}); solo se conservaron "
                                        'filas dentro de tu período. Revisa posibles huecos.'
                                    )
                            if result['missing_dates']:
                                st.warning(
                                    f"Faltan {len(result['missing_dates'])} días de la estación: "
                                    + ', '.join(result['missing_dates'][:12])
                                )
                            st.dataframe(
                                pd.DataFrame(result['rows']),
                                hide_index=True,
                                use_container_width=True,
                            )
                            c1, c2, c3 = st.columns(3)
                            c1.download_button(
                                'Descargar CSV', Path(result['csv_path']).read_bytes(),
                                file_name=Path(result['csv_path']).name,
                                mime='text/csv', key='download_inamhi_csv',
                            )
                            c2.download_button(
                                'Descargar paquete + recibo', Path(result['zip_path']).read_bytes(),
                                file_name=Path(result['zip_path']).name,
                                mime='application/zip', key='download_inamhi_zip',
                            )
                            c3.download_button(
                                'Descargar metadata', Path(result['manifest_path']).read_bytes(),
                                file_name='metadata-inamhi.json',
                                mime='application/json', key='download_inamhi_manifest',
                            )
                            st.caption(
                                'INAMHI informa acceso público gratuito; su API no '
                                'devuelve una licencia explícita ni una bandera de QC. '
                                'El manifiesto conserva esa limitación y el crédito.'
                            )
                else:
                    st.caption('Selecciona fecha inicial y final para consultar los datos.')
            else:
                st.warning('Esta estación no muestra variables diarias en el catálogo público actual.')
            st.link_button('Abrir visor diario oficial', _providers.INAMHI_VIEWER_URL)
            st.link_button('Acceso/solicitud oficial de datos históricos', _providers.INAMHI_PUBLIC_ACCESS_URL)
            st.markdown(
                'Si el visor no cubre el periodo histórico, INAMHI recibe '
                'solicitudes en [datos@inamhi.gob.ec](mailto:datos@inamhi.gob.ec).'
            )
        else:
            st.warning('El catálogo no respondió con estaciones. Vuelve a intentarlo o abre el visor oficial.')

    st.divider()
    st.header('Otras fuentes ecuatorianas')
    st.caption(
        'Son portales institucionales reales, pero todavía no están conectados '
        'como descargas de un clic. El siguiente paso es implementar cada '
        'conector con su API/servicio y licencia verificados.'
    )
    source_cards = [
        ('IGM · cartografía y servicios geográficos',
         'Geoportal nacional; publica cartografía, escalas, metadatos y servicios WMS/WFS/WMTS.',
         'https://www.geoportaligm.gob.ec/geoportal-igm/'),
        ('IIGE · geología y energía',
         'Geoportal geológico con metadatos y servicios WMS/WCS; requiere respetar la licencia de descarga y atribuir la fecha.',
         'https://geoportal.geoenergia.gob.ec/'),
        ('IG-EPN · sismos y volcanes',
         'Catálogos sísmicos y registros descargables; cada producto tiene su propio formulario/condiciones.',
         'https://igepn.edu.ec/catalogos-sismicos/formulario-catalogos-sismicos'),
        ('INOCAR · océano y mareas',
         'Consultas de mareas por puerto/fecha y productos oceanográficos; no se asume una API estable.',
         'https://www.inocar.mil.ec/mareas/form_mareas.php'),
        ('IEDG · índice geoespacial del Ecuador',
         'Entrada nacional a geoportales institucionales y servicios publicados por organismos públicos.',
         'https://www.iedg.gob.ec/servicios/geoportales/'),
        ('Datos Abiertos Ecuador',
         'Catálogo transversal; los formatos y la disponibilidad dependen de cada conjunto de datos.',
         'https://www.datosabiertos.gob.ec/'),
    ]
    for offset in range(0, len(source_cards), 2):
        columns = st.columns(2)
        for column, card in zip(columns, source_cards[offset:offset + 2]):
            with column.container(border=True):
                st.markdown(f"**{card[0]}**")
                st.caption(card[1])
                st.link_button('Abrir portal oficial', card[2], use_container_width=True)

    st.stop()


# =============================================================================
# JOBS
# =============================================================================

@st.fragment(run_every=3)
def jobs_panel():

    all_jobs = statuses()

    if not all_jobs:
        st.info(
            'Todavía no has exportado desde este editor.'
        )
        return

    selected = st.selectbox(
        'Exportación',
        [
            str(folder)
            for folder, _ in all_jobs
        ],
        format_func=lambda value:
            read_json(
                Path(value) / 'project.json',
                {}
            ).get(
                'name',
                Path(value).name
            )
            + ' · '
            + Path(value).name
    )

    folder = Path(selected)

    state = read_json(
        folder / 'status.json',
        {}
    )

    st.progress(
        min(
            1.0,
            max(
                0.0,
                state.get(
                    'progress',
                    0.0
                )
            )
        ),
        text=state.get(
            'message',
            'Preparando…'
        )
    )

    active = (
        state.get('state')
        in (
            'queued',
            'running'
        )
    )

    if active:

        st.caption(
            'El trabajo continúa en segundo plano. Puedes volver al editor.'
        )

        if st.button(
            'Cancelar esta exportación',
            key='cancel_' + folder.name,
            icon=':material/stop:'
        ):
            (
                folder
                / 'cancel.request'
            ).touch()

            st.info(
                'Cancelación solicitada.'
            )

    elif state.get('state') == 'complete':

        from job_products import published_movie
        try:
            movie = published_movie(folder)
        except (ValueError, OSError, TypeError) as error:
            st.error('No se pudo localizar el MP4 publicado: ' + str(error))
            return
        if movie is None:
            st.info('El trabajo todavía no ha publicado su MP4.')
            return

        st.success(
            'MP4 terminado · conserva la maqueta y la configuración del proyecto.'
        )

        with st.container(
            width=400
        ):
            st.video(
                str(
                    movie
                ),
                alt='Video cartográfico exportado desde Ecuador Vivo'
            )

        with st.container(
            horizontal=True
        ):

            st.download_button(
                'Descargar MP4',
                data=lambda:
                    (
                        movie
                    ).read_bytes(),
                file_name=(
                    'ecuador-vivo-'
                    + folder.name
                    + '.mp4'
                ),
                mime='video/mp4',
                icon=':material/download:'
            )

            st.download_button(
                'Recibo de fuentes',
                (
                    folder
                    / 'receipt.json'
                ).read_bytes(),
                file_name='receipt.json',
                mime='application/json'
            )

            if st.button(
                'Abrir carpeta',
                key='open_' + folder.name,
                icon=':material/folder:'
            ):
                os.startfile(folder)

        comparison_table = folder / 'comparison.csv'
        if comparison_table.is_file():
            st.download_button(
                'Datos comparados · CSV',
                comparison_table.read_bytes(),
                file_name='ecuador-vivo-comparacion.csv',
                mime='text/csv',
                key='comparison_csv_' + folder.name,
            )
        comparison_rank = folder / 'ranking-provincias.csv'
        if comparison_rank.is_file():
            st.download_button(
                'Ranking provincial · CSV',
                comparison_rank.read_bytes(),
                file_name='ecuador-vivo-ranking-provincias.csv',
                mime='text/csv',
                key='comparison_rank_' + folder.name,
            )

        job_project = read_json(folder / 'project.json', {})
        job_receipt = read_json(folder / 'receipt.json', {})
        if job_receipt.get('endcard', {}).get('enabled'):
            st.divider()
            st.subheader('Preparar ficha para Andes Pulso')
            st.caption(
                'Copia el MP4, las métricas calculadas, las fuentes y el recibo '
                'al proyecto web como borrador. No publica ni hace commit.'
            )
            case_id = st.text_input(
                'Identificador del caso',
                value=default_case_id(job_project),
                max_chars=72,
                key='case_id_' + folder.name,
                help='Se puede editar; usa minúsculas y guiones, por ejemplo lluvia-ecuador-2024.',
            )
            if st.button(
                'Preparar borrador en Andes Pulso',
                type='primary',
                key='prepare_case_' + folder.name,
                icon=':material/library_add:',
            ):
                try:
                    record = prepare_case(folder, case_id.strip())
                    st.success(
                        f'Ficha «{record["id"]}» creada como borrador. '
                        'MP4 y datos ya están en la carpeta del proyecto web.'
                    )
                    st.code(
                        'data/cases/' + record['id']
                        + '\nassets/media/andes-pulso/' + record['id']
                        + '\nRevisa data/cases/registry.json antes de publicar.',
                        language=None,
                    )
                except Exception as error:
                    st.error(f'No se pudo preparar la ficha: {error}')

    else:

        st.warning(
            state.get(
                'message',
                'El trabajo no terminó.'
            )
        )

    st.caption(
        str(folder)
    )


if section == 'Exportaciones':

    st.title('Tus exportaciones')

    jobs_panel()

    st.stop()


# =============================================================================
# EDITOR
# =============================================================================

st.title('Editor de video')
st.caption('Datos verificables. Mapas que cuentan una historia.')

video_types = ['Mapa temporal', 'Comparación climática', 'CSV geográfico']
video_type = st.selectbox(
    'Tipo de video', video_types,
    index=video_types.index(p.get('video_type', 'Mapa temporal')),
    key=f'video_type_{revision}',
    help='La maqueta, los controles y el cierre se adaptan al tipo seleccionado.',
    width=440,
)
p['video_type'] = video_type
st.session_state.project = p
from workspace import navigation, export_check, authoring_config
phase = navigation()
if phase == 'Estudio':
    from studio_workspace import show_workspace
    document = synchronize_source(st.session_state, p)
    show_workspace(p,key=workspace_key(document),snapshot=st.session_state.get(f'visualizations_{revision}_snapshot'),canonical=True)
    st.stop()
if phase == 'Montaje':
    from storyboard_ui import show_storyboard
    show_storyboard(p, key=f'story_{revision}', always_open=True)
    st.caption('El formato y la secuencia se aplican al tipo de video seleccionado. La composición se ajusta solo en Maqueta.')
if video_type == 'Comparación climática':
    from climate_comparison_ui import render_embedded
    render_embedded(p, phase=phase)
    st.stop()
if video_type == 'CSV geográfico':
    from spatial_csv_ui import show_spatial_csv
    show_spatial_csv(p, phase=phase)
    st.stop()

def temporal_controls(step):
    with st.container(
        border=True
    ):

        if step == 'Datos':

            st.header(
                'Fuente y periodo'
            )

            choice = st.selectbox(
                'Origen',
                [
                    'Lluvia CHIRPS · automática',
                    'Mis archivos GeoTIFF'
                ],
                index=(
                    0
                    if p['source'] == 'chirps'
                    else 1
                ),
                key=f'source_{revision}'
            )

            source = (
                'chirps'
                if choice.startswith('Lluvia')
                else 'local'
            )

            if source != p['source']:

                p['source'] = source

                if source == 'chirps':

                    defaults = default_project()

                    for key in (
                        'kind',
                        'variable',
                        'citation',
                        'source_url',
                        'units',
                        'legend',
                        'note',
                        'resolution_note',
                        'scale',
                        'offset',
                        'stops',
                        'palette',
                        'cadence',
                        'bbox',
                        'clip_ecuador',
                        'endcard_aggregation',
                        'endcard_accumulated_units',
                    ):
                        p[key] = copy.deepcopy(
                            defaults[key]
                        )

                else:

                    p.update(
                        citation='',
                        source_url='',
                        resolution_note=(
                            'Resolución y calidad: según el archivo fuente'
                        ),
                        note=(
                            'Serie importada · revisar calidad y fechas'
                        ),
                        cadence='Por observación',
                        # The compositor only draws the inset when the source
                        # actually covers it; leave the option on for global
                        # GeoTIFFs instead of assuming every import is continental.
                        show_galapagos=True,
                        # Safer initial choice for unknown imported rasters:
                        # intensive variables must never be added through time.
                        endcard_aggregation='mean',
                        endcard_footer=(
                            'Fuente y resolución: según el GeoTIFF importado'
                        ),
                        endcard_footer_2='Cobertura según el encuadre seleccionado',
                        endcard_subtitle=(
                            'Resumen de la variable durante el período seleccionado.'
                        ),
                        endcard_section_1='MÉTRICAS DEL PERÍODO',
                        endcard_section_2='¿DÓNDE FUE MAYOR?',
                        endcard_section_2_note=(
                            'Provincias · promedio espacial · ranking 1–12'
                        ),
                        endcard_section_3='PROVINCIAS 13–24',
                    )

                rerun_project()

            if source == 'chirps':

                dates = st.columns(2)

                p['start'] = str(
                    dates[0].date_input(
                        'Desde',
                        dt.date.fromisoformat(
                            p['start']
                        ),
                        min_value=dt.date(
                            1981,
                            1,
                            1
                        ),
                        key=f'start_{revision}'
                    )
                )

                p['end'] = str(
                    dates[1].date_input(
                        'Hasta',
                        dt.date.fromisoformat(
                            p['end']
                        ),
                        key=f'end_{revision}'
                    )
                )

                st.caption(
                    'Lluvia diaria · mm/día · resolución original ≈ 5,6 km.'
                )

            else:

                st.caption(
                    'Carga TIFF numéricos y georreferenciados. '
                    'Una banda seleccionada por fecha.'
                )

                files = st.file_uploader(
                    'GeoTIFF de tu variable',
                    type=[
                        'tif',
                        'tiff'
                    ],
                    accept_multiple_files=True,
                    key=f'files_{revision}'
                )

                if st.button(
                    'Leer archivos',
                    disabled=not files,
                    key='read_files'
                ):

                    try:

                        imported = []

                        with st.spinner(
                            'Leyendo bandas y fechas…'
                        ):

                            for file in files:

                                path = store_upload(
                                    file.name,
                                    file.getvalue()
                                )

                                imported.extend(
                                    inspect_file(
                                        path,
                                        file.name
                                    )
                                )

                        st.session_state.import_rows = imported

                    except Exception as error:

                        st.error(
                            str(error)
                        )

                if st.session_state.import_rows:

                    table = pd.DataFrame(
                        st.session_state.import_rows
                    ).drop(
                        columns='path'
                    )

                    edited = st.data_editor(
                        table,
                        hide_index=True,
                        disabled=[
                            'archivo',
                            'banda',
                            'nombre_banda'
                        ],
                        key=f'import_table_{revision}'
                    )

                    if st.button(
                        'Usar esta serie',
                        key='apply_series'
                    ):

                        try:

                            entries = []

                            for i, row in edited.iterrows():

                                if row['usar']:

                                    date = str(
                                        dt.date.fromisoformat(
                                            str(
                                                row['fecha']
                                            ).strip()
                                        )
                                    )

                                    entries.append({
                                        'date': date,
                                        'band': int(
                                            row['banda']
                                        ),
                                        'path': (
                                            st.session_state
                                            .import_rows[i]['path']
                                        )
                                    })

                            candidate = copy.deepcopy(
                                p
                            )

                            candidate[
                                'entries'
                            ] = entries

                            timeline(
                                candidate
                            )

                            p[
                                'entries'
                            ] = entries

                            st.success(
                                f'{len(entries)} observaciones listas.'
                            )

                        except (
                            ValueError,
                            TypeError
                        ) as error:

                            st.error(
                                f'Revisa la selección: {error}'
                            )

                p['variable'] = st.text_input(
                    'Nombre de la variable',
                    p['variable'],
                    key=f'var_{revision}'
                )

                p['kind'] = st.selectbox(
                    'Tipo de dato',
                    [
                        'continuous',
                        'categorical'
                    ],
                    index=(
                        0
                        if p['kind'] == 'continuous'
                        else 1
                    ),
                    format_func=lambda value:
                        (
                            'Continuo: temperatura, lluvia, índices'
                            if value == 'continuous'
                            else 'Categorías: coberturas, usos del suelo'
                        ),
                    key=f'kind_{revision}'
                )

                p['cadence'] = st.selectbox(
                    'Cada mapa representa',
                    [
                        'Diaria',
                        'Mensual',
                        'Anual',
                        'Por observación'
                    ],
                    index=[
                        'Diaria',
                        'Mensual',
                        'Anual',
                        'Por observación'
                    ].index(
                        p['cadence']
                    ),
                    key=f'cadence_{revision}'
                )

                with st.expander(
                    'Unidades y conversión'
                ):

                    p['units'] = st.text_input(
                        'Unidades finales',
                        p['units'],
                        key=f'units_{revision}'
                    )

                    p['scale'] = st.number_input(
                        'Factor: valor × factor + desplazamiento',
                        value=float(
                            p['scale']
                        ),
                        format='%.6f',
                        key=f'scale_{revision}'
                    )

                    p['offset'] = st.number_input(
                        'Desplazamiento',
                        value=float(
                            p['offset']
                        ),
                        format='%.6f',
                        key=f'offset_{revision}'
                    )

                    nodata = st.text_input(
                        'NoData adicional',
                        (
                            ''
                            if p['nodata'] is None
                            else str(
                                p['nodata']
                            )
                        ),
                        key=f'nodata_{revision}'
                    )

                    try:
                        p['nodata'] = (
                            float(nodata)
                            if nodata.strip()
                            else None
                        )
                    except ValueError:
                        st.error(
                            'NoData debe ser numérico.'
                        )

        elif step == 'Diseño':

            st.subheader(
                'Maqueta y apariencia'
            )

            modes = {
                'maqueta':
                    'Maqueta Ecuador Vivo · aprobada',
                'social':
                    'Redes sociales · flexible',
                'conservative':
                    'Márgenes amplios',
                'original':
                    'Diseño clásico',
            }

            p['layout'] = st.selectbox(
                'Distribución',
                list(modes),
                index=list(modes).index(
                    p['layout']
                ),
                format_func=modes.get,
                key=f'layout_{revision}'
            )

            if p['layout'] == 'maqueta':
                st.success(
                    'Esta es la maqueta aprobada. '
                    'Lienzo y MP4 usan la misma composición.'
                )

            p['name'] = st.text_input(
                'Nombre del proyecto',
                p['name'],
                max_chars=100,
                key=f'name_{revision}'
            )

            p['title'] = st.text_input(
                'Título principal',
                p['title'],
                max_chars=100,
                help=(
                    'La primera palabra se destaca con degradado '
                    'en la maqueta aprobada.'
                ),
                key=f'title_{revision}'
            )

            p['description'] = st.text_input(
                'Descripción / subtítulo',
                p['description'],
                max_chars=150,
                key=f'desc_{revision}'
            )

            p['legend'] = st.text_input(
                'Título de la leyenda',
                p['legend'],
                max_chars=90,
                key=f'legend_{revision}'
            )

            colors = st.columns(3)

            p['background'] = colors[0].color_picker(
                'Fondo',
                p['background'],
                key=f'bg_{revision}'
            )

            p['text'] = colors[1].color_picker(
                'Texto',
                p['text'],
                key=f'fg_{revision}'
            )

            p['accent'] = colors[2].color_picker(
                'Acento',
                p['accent'],
                key=f'accent_{revision}'
            )

            if p['layout'] == 'maqueta':

                gradient_cols = st.columns(2)

                p['title_gradient_1'] = (
                    gradient_cols[0].color_picker(
                        'Inicio del degradado',
                        p['title_gradient_1'],
                        key=f'gradient1_{revision}'
                    )
                )

                p['title_gradient_2'] = (
                    gradient_cols[1].color_picker(
                        'Final del degradado',
                        p['title_gradient_2'],
                        key=f'gradient2_{revision}'
                    )
                )

                st.markdown(
                    '#### Elementos de la maqueta'
                )

                options = st.columns(3)

                p['show_galapagos'] = options[0].toggle(
                    'Galápagos',
                    p['show_galapagos'],
                    key=f'gal_{revision}'
                )

                p['show_provinces'] = options[1].toggle(
                    'Provincias',
                    p['show_provinces'],
                    key=f'prov_{revision}'
                )

                p['show_play_button'] = options[2].toggle(
                    'Símbolo ▶',
                    p['show_play_button'],
                    key=f'play_{revision}'
                )

                st.caption(
                    'Galápagos usa la misma fecha y escala de la capa. El recuadro '
                    'solo aparece si el ráster realmente cubre las islas; las áreas '
                    'sin cobertura quedan transparentes y 0 sigue siendo un dato válido.'
                )

                if st.button(
                    'Restaurar estilo Ecuador Vivo',
                    icon=':material/restart_alt:'
                ):
                    restore_maqueta_style()

            if p['kind'] == 'continuous':

                palette_name = st.selectbox(
                    'Paleta de partida',
                    list(PALETTES),
                    index=(
                        list(PALETTES).index(
                            'Ecuador Vivo · maqueta'
                        )
                        if 'Ecuador Vivo · maqueta' in PALETTES
                        else 0
                    ),
                    key=f'palette_{revision}'
                )

                if st.button(
                    'Aplicar paleta',
                    key='apply_palette'
                ):

                    p['palette'] = list(
                        PALETTES[
                            palette_name
                        ]
                    )

                    if len(
                        p['stops']
                    ) != len(
                        p['palette']
                    ):

                        lo = p['stops'][0]
                        hi = p['stops'][-1]

                        p['stops'] = [
                            lo
                            + (
                                hi
                                - lo
                            )
                            * i
                            / (
                                len(
                                    p['palette']
                                )
                                - 1
                            )
                            for i in range(
                                len(
                                    p['palette']
                                )
                            )
                        ]

                    rerun_project()

                with st.expander(
                    'Editar valores y colores de la escala',
                    expanded=True
                ):

                    table = st.data_editor(
                        pd.DataFrame({
                            'valor':
                                p['stops'],
                            'color':
                                p['palette']
                        }),
                        hide_index=True,
                        num_rows='dynamic',
                        key=f'colors_{revision}'
                    )

                    if st.button(
                        'Aplicar escala',
                        key='apply_scale'
                    ):

                        try:

                            candidate = copy.deepcopy(
                                p
                            )

                            candidate[
                                'stops'
                            ] = [
                                float(value)
                                for value
                                in table[
                                    'valor'
                                ]
                            ]

                            candidate[
                                'palette'
                            ] = list(
                                table[
                                    'color'
                                ]
                            )

                            validate(
                                candidate
                            )

                            p.update(
                                stops=candidate[
                                    'stops'
                                ],
                                palette=candidate[
                                    'palette'
                                ]
                            )

                            st.success(
                                'Escala aplicada.'
                            )

                        except (
                            ValueError,
                            TypeError
                        ) as error:

                            st.error(
                                str(error)
                            )

            else:

                classes = st.data_editor(
                    pd.DataFrame(
                        p['classes']
                    ),
                    num_rows='dynamic',
                    hide_index=True,
                    key=f'classes_{revision}'
                )

                if st.button(
                    'Aplicar clases',
                    key='apply_classes'
                ):

                    candidate = copy.deepcopy(
                        p
                    )

                    candidate[
                        'classes'
                    ] = classes.to_dict(
                        'records'
                    )

                    try:

                        validate(
                            candidate
                        )

                        p[
                            'classes'
                        ] = candidate[
                            'classes'
                        ]

                        st.success(
                            'Clases guardadas.'
                        )

                    except (
                        ValueError,
                        TypeError
                    ) as error:

                        st.error(
                            str(error)
                        )

        elif step == 'Cierre final':

            st.subheader(
                'Tarjeta final de métricas'
            )

            categorical_endcard = p['kind'] == 'categorical'
            profile = detect_profile(p)
            unsupported_endcard = (
                p['kind'] == 'continuous' and not profile['supported']
            )
            if categorical_endcard:
                # A ranked numerical endcard would falsely imply arithmetic
                # meaning for land-cover or other class codes.
                p['endcard_enabled'] = False
                st.info(
                    'Las capas categóricas no usan este cierre numérico. '
                    'Desactívalo o prepara un cierre de clases específico.'
                )
            elif unsupported_endcard:
                p['endcard_enabled'] = False
                st.warning(
                    'Las direcciones no se pueden resumir con un promedio '
                    'aritmético. Importa componentes u/v o una serie con '
                    'media circular ya calculada para usar un cierre.'
                )

            p['endcard_enabled'] = st.toggle(
                'Añadir el cierre al final del video',
                p.get('endcard_enabled', True),
                key=f'endcard_enabled_{revision}',
                disabled=(categorical_endcard or unsupported_endcard),
            )

            if p['endcard_enabled']:
                aggregation_mode = st.radio(
                    'Regla temporal',
                    ['auto', 'manual'],
                    index=(0 if p.get('endcard_aggregation_mode', 'auto') == 'auto'
                           else 1),
                    horizontal=True,
                    format_func=lambda value: (
                        'Automática · recomendada'
                        if value == 'auto' else 'Revisar manualmente'
                    ),
                    key=f'endcard_aggregation_mode_{revision}',
                    help=(
                        'Automática detecta si la variable representa una '
                        'cantidad por intervalo (se acumula) o una magnitud '
                        'intensiva como °C o NDWI (se promedia).'
                    ),
                )
                p['endcard_aggregation_mode'] = aggregation_mode
                if aggregation_mode == 'auto':
                    effective_aggregation, profile = resolve_aggregation(p)
                    # Keep the saved value aligned with the applied value, so
                    # the receipt remains legible even outside the editor.
                    p['endcard_aggregation'] = effective_aggregation
                    st.info(
                        f'Aplicado automáticamente: **'
                        f'{"acumular" if effective_aggregation == "sum" else "promediar"}'
                        f'** ({profile["kind"]}).'
                    )
                else:
                    options = ['mean'] if profile['intensive'] else ['sum', 'mean']
                    selected = p.get('endcard_aggregation', profile['aggregation'])
                    if selected not in options:
                        selected = profile['aggregation']
                    aggregation = st.segmented_control(
                        'Cómo se combinan las fechas',
                        options,
                        default=selected,
                        format_func=lambda value: (
                            'Acumular · cantidad por intervalo'
                            if value == 'sum' else 'Promediar · variable intensiva'
                        ),
                        key=f'endcard_aggregation_{revision}',
                    )
                    if aggregation is not None:
                        p['endcard_aggregation'] = aggregation
                    effective_aggregation, profile = resolve_aggregation(p)

                for warning in profile['warnings']:
                    st.warning(warning)

                if effective_aggregation == 'sum':
                    p['endcard_accumulated_units'] = st.text_input(
                        'Unidades tras acumular',
                        p.get('endcard_accumulated_units', ''),
                        max_chars=40,
                        key=f'endcard_accumulated_units_{revision}',
                        help=(
                            'Ejemplo: CHIRPS entra en mm/día y su total '
                            'anual o mensual se expresa en mm.'
                        ),
                    )
                else:
                    st.caption(
                        'Las métricas y el ranking usarán el promedio '
                        'temporal y conservarán las unidades del mapa.'
                    )

                p['endcard_auto_text'] = st.toggle(
                    'Adaptar títulos y etiquetas al tipo de dato automáticamente',
                    p.get('endcard_auto_text', True),
                    key=f'endcard_auto_text_{revision}',
                    help=(
                        'Cambia encabezados, descripciones de las cuatro cifras, '
                        'unidades y pie según la variable y su frecuencia. '
                        'Desactívalo para escribir cada texto manualmente.'
                    ),
                )
                if p['endcard_auto_text']:
                    st.caption(
                        'El cierre usará la variable, unidades, fechas, fuente y '
                        'estadísticas calculadas para completar los textos. '
                        'Puedes desactivar esta opción para personalizar cada línea.'
                    )
                else:
                    p['endcard_title'] = st.text_input(
                        'Título del cierre', p['endcard_title'], max_chars=80,
                        key=f'endcard_title_{revision}'
                    )
                    p['endcard_subtitle'] = st.text_input(
                        'Subtítulo del cierre', p['endcard_subtitle'], max_chars=150,
                        key=f'endcard_subtitle_{revision}'
                    )
                    c1, c2 = st.columns(2)
                    p['endcard_section_1'] = c1.text_input(
                        'Bloque 1', p['endcard_section_1'], max_chars=60,
                        key=f'endcard_section1_{revision}'
                    )
                    p['endcard_section_1_note'] = c2.text_input(
                        'Nota del bloque 1', p['endcard_section_1_note'],
                        max_chars=120, key=f'endcard_section1note_{revision}'
                    )
                    c3, c4 = st.columns(2)
                    p['endcard_section_2'] = c3.text_input(
                        'Ranking 1–12', p['endcard_section_2'], max_chars=60,
                        key=f'endcard_section2_{revision}'
                    )
                    p['endcard_section_2_note'] = c4.text_input(
                        'Nota del ranking 1–12', p['endcard_section_2_note'],
                        max_chars=120, key=f'endcard_section2note_{revision}'
                    )
                    c5, c6 = st.columns(2)
                    p['endcard_section_3'] = c5.text_input(
                        'Ranking 13–24', p['endcard_section_3'], max_chars=60,
                        key=f'endcard_section3_{revision}'
                    )
                    p['endcard_section_3_note'] = c6.text_input(
                        'Nota del ranking 13–24', p['endcard_section_3_note'],
                        max_chars=120, key=f'endcard_section3note_{revision}'
                    )
                    p['endcard_footer'] = st.text_input(
                        'Texto técnico del pie', p['endcard_footer'], max_chars=150,
                        key=f'endcard_footer_{revision}'
                    )
                    p['endcard_footer_2'] = st.text_input(
                        'Cobertura geográfica del pie', p['endcard_footer_2'],
                        max_chars=150, key=f'endcard_footer2_{revision}'
                    )
                    st.caption('Etiquetas de las cifras y del eje del ranking')
                    d1, d2 = st.columns(2)
                    p['endcard_date_metric_label'] = d1.text_input(
                        'Cifra 1 · fecha destacada',
                        p['endcard_date_metric_label'], max_chars=80,
                        key=f'endcard_date_metric_{revision}'
                    )
                    p['endcard_period_metric_label'] = d2.text_input(
                        'Cifra 2 · período destacado',
                        p['endcard_period_metric_label'], max_chars=80,
                        key=f'endcard_period_metric_{revision}'
                    )
                    d3, d4 = st.columns(2)
                    p['endcard_average_metric_label'] = d3.text_input(
                        'Cifra 3 · promedio',
                        p['endcard_average_metric_label'], max_chars=80,
                        key=f'endcard_average_metric_{revision}'
                    )
                    p['endcard_maximum_metric_label'] = d4.text_input(
                        'Cifra 4 · máximo',
                        p['endcard_maximum_metric_label'], max_chars=80,
                        key=f'endcard_maximum_metric_{revision}'
                    )
                    p['endcard_rank_axis_label'] = st.text_input(
                        'Texto del eje del ranking (vacío = automático)',
                        p['endcard_rank_axis_label'], max_chars=120,
                        key=f'endcard_rank_axis_{revision}'
                    )
            else:
                st.info('El video terminará en la última fecha del mapa.')

        elif step == 'Textos y créditos':

            st.subheader(
                'Tu firma, tus palabras'
            )

            p['brand'] = st.text_input(
                'Marca en la cabecera',
                p['brand'],
                max_chars=120,
                key=f'brand_{revision}'
            )

            p['author'] = st.text_input(
                'Autoría',
                p['author'],
                max_chars=120,
                key=f'author_{revision}'
            )

            p['credits'] = st.text_input(
                'Cargo / crédito breve',
                p['credits'],
                max_chars=120,
                key=f'credits_{revision}'
            )

            social = st.columns(2)

            p['tiktok'] = social[0].text_input(
                'TikTok',
                p.get('tiktok', '@elgeocientifico'),
                max_chars=60,
                key=f'tiktok_{revision}'
            )

            p['instagram'] = social[1].text_input(
                'Instagram',
                p.get('instagram', '@henry_conteron'),
                max_chars=60,
                key=f'instagram_{revision}'
            )

            with st.expander(
                'Fuente científica y límites',
                expanded=True
            ):

                p['citation'] = st.text_input(
                    'Fuente científica visible',
                    p['citation'],
                    max_chars=180,
                    key=f'credit_source_{revision}'
                )

                p['source_url'] = st.text_input(
                    'Enlace de la fuente',
                    p['source_url'],
                    key=f'credit_url_{revision}'
                )

                p['boundary_note'] = st.text_input(
                    'Crédito geográfico',
                    p['boundary_note'],
                    max_chars=180,
                    placeholder=(
                        'Automático: Ecuador continental · Límites: geoBoundaries'
                    ),
                    key=f'boundary_note_{revision}'
                )

                p['units'] = st.text_input(
                    'Unidades en la leyenda',
                    p['units'],
                    max_chars=40,
                    key=f'credit_units_{revision}'
                )

                p['resolution_note'] = st.text_input(
                    'Nota de resolución',
                    p['resolution_note'],
                    max_chars=180,
                    key=f'credit_resolution_{revision}'
                )

            with st.expander(
                'Fecha, contador y ciudades'
            ):

                p['date_format'] = st.selectbox(
                    'Formato de fecha diaria',
                    [
                        'DD / MM / AAAA',
                        'AAAA-MM-DD',
                        'MM / DD / AAAA'
                    ],
                    index=[
                        'DD / MM / AAAA',
                        'AAAA-MM-DD',
                        'MM / DD / AAAA'
                    ].index(
                        p['date_format']
                    ),
                    key=f'date_format_{revision}'
                )

                p['counter_label'] = st.text_input(
                    'Palabra del contador',
                    p['counter_label'],
                    max_chars=30,
                    placeholder=(
                        'Automático: DÍA, MES, AÑO u OBS.'
                    ),
                    key=f'counter_{revision}'
                )

                for city in p['cities']:

                    p['city_labels'][city] = st.text_input(
                        f'Etiqueta de {city}',
                        p['city_labels'].get(
                            city,
                            city
                        ),
                        max_chars=60,
                        key=f'city_label_{city}_{revision}'
                    )

        else:

            st.subheader(
                'Encuadre y ritmo'
            )

            region = st.selectbox(
                'Encuadre rápido',
                [
                    'Actual',
                    'Ecuador continental',
                    'Tena y Archidona'
                ],
                key=f'region_{revision}'
            )

            if st.button(
                'Aplicar encuadre',
                disabled=(
                    region == 'Actual'
                )
            ):

                if region == (
                    'Ecuador continental'
                ):
                    p['bbox'] = [
                        -81.5,
                        -5.2,
                        -75.0,
                        1.8
                    ]
                    p['clip_ecuador'] = True
                    p['show_galapagos'] = True

                else:
                    p['bbox'] = [
                        -78.04,
                        -1.12,
                        -77.55,
                        -0.72
                    ]
                    p['show_galapagos'] = False

                rerun_project()

            with st.expander(
                'Límites del mapa'
            ):

                coords = st.columns(2)

                for i, label in enumerate(
                    [
                        'Oeste',
                        'Sur',
                        'Este',
                        'Norte'
                    ]
                ):

                    p['bbox'][i] = (
                        coords[
                            i % 2
                        ].number_input(
                            label,
                            value=float(
                                p['bbox'][i]
                            ),
                            format='%.4f',
                            key=f'bbox_{i}_{revision}'
                        )
                    )

            p['clip_ecuador'] = st.toggle(
                'Recortar datos a Ecuador',
                p['clip_ecuador'],
                key=f'clip_{revision}'
            )

            p['cities'] = st.multiselect(
                'Ciudades de referencia',
                [
                    'Quito',
                    'Guayaquil',
                    'Cuenca',
                    'Tena',
                    'Archidona'
                ],
                p['cities'],
                key=f'cities_{revision}'
            )



# =============================================================================
# ONE TEMPORAL WORKSPACE — no duplicate preview column
# =============================================================================

if phase == 'Datos':
    temporal_controls('Datos')
    st.info('Después de elegir y validar las fuentes, abre Maqueta para editar el diseño.')
elif phase == 'Maqueta':
    surface = st.segmented_control('Superficie de trabajo', ['Lienzo de mapa', 'Visualizaciones'],
        default='Lienzo de mapa', key=f'work_surface_{revision}')
    if surface == 'Visualizaciones':
        from visualization_ui import show_visualizations
        show_visualizations(p, editor_summary, key=f'visualizations_{revision}',on_create_studio=create_studio_from_snapshot)
        st.stop()
    # Optional template controls are not a second preview/editor.
    with st.expander('Configuración de la plantilla y créditos'):
        control = st.segmented_control('Configuración',
            ['Diseño', 'Cierre final', 'Textos y créditos', 'Encuadre'],
            default='Diseño', key='step', persist_state='session')
        temporal_controls('Mapa y tiempo' if control == 'Encuadre' else control)

    try:
        rows = validate(p)
        with st.expander('Fecha de trabajo del lienzo'):
            index = st.slider('Fecha del mapa en el lienzo', 1, len(rows), 1,
                key=f'preview_index_{revision}', persist_state='session') - 1 if len(rows) > 1 else 0
            st.caption(rows[index]['date'])
        if p['layout'] == 'maqueta':
            from layout_editor import show_layout_editor
            p['visual_layout'] = authoring_config(p)['visual_layout']
            def render_editable_map(settings):
                editable_rows = validate(settings)
                values, _ = load_values(settings, editable_rows[index])
                return compose(settings, values, boundary(), editable_rows[index]['date'], index, len(editable_rows))
            def render_editable_endcard(settings):
                return compose_endcard(settings, editor_summary(settings))
            def persist_visual_layout(layout):
                p['visual_layout'] = layout
            show_layout_editor(p, render_editable_map,
                render_editable_endcard if p.get('endcard_enabled', True) else None,
                project=p, persist=persist_visual_layout, key=f'normal_visual_{revision}')
        else:
            st.info('Este estilo antiguo no tiene capas editables. En Configuración selecciona Maqueta Ecuador Vivo para mover o eliminar elementos.')
            st.image(preview_bytes(snapshot(), index, RENDER_CACHE_VERSION), width=450,
                alt='Estilo antiguo no editable; cambia a Maqueta Ecuador Vivo para editar capas')
    except (ValueError, KeyError, TypeError, OSError) as error:
        st.warning(f'No se pudo abrir la maqueta: {error}')
elif phase == 'Montaje':
    if not p.get('storyboard', {}).get('enabled'):
        # This is the only default timing control. Custom cards own their
        # times in Montaje and never compete with a second duration widget.
        p['duration'] = st.number_input('Duración del mapa · segundos',
            min_value=max(1/30, len(timeline(p))/30), max_value=3600.,
            value=max(float(p['duration']), len(timeline(p))/30), key=f'map_seconds_{revision}')
        if p.get('endcard_enabled', True):
            p['endcard_duration'] = st.number_input('Duración de métricas · segundos',
                min_value=1., max_value=30., value=float(p.get('endcard_duration', 6.)),
                key=f'metric_seconds_{revision}')
else:
    try:
        from storyboard import base_timing
        config = base_timing(copy.deepcopy(p))
        rows = validate(config)
        def export_map(settings):
            values, _ = load_values(settings, rows[0])
            return compose(settings, values, boundary(), rows[0]['date'], 0, len(rows))
        def export_endcard(settings):
            return compose_endcard(settings, editor_summary(settings))
        ready = export_check(config, export_map,
            export_endcard if config.get('endcard_enabled', True) else None)
    except (ValueError, KeyError, TypeError, OSError) as error:
        ready = False
        st.error(str(error))
    active = [state for _, state in statuses() if state.get('state') in ('queued', 'running')]
    if st.button('Generar video', type='primary', icon=':material/movie:',
        key='render_button', disabled=not ready or bool(active)):
        try:
            folder = start_job(copy.deepcopy(p))
            st.session_state.active_job = str(folder)
            st.success('Exportación iniciada. Revisa Exportaciones en la barra lateral.')
        except Exception as error:
            st.error(f'No se pudo iniciar: {error}')
    if active:
        st.caption('Hay una exportación activa. Puedes seguir diseñando mientras termina.')
    with st.container(horizontal=True):
        if st.button('Guardar proyecto', icon=':material/save:', key='save_project'):
            target = save_project()
            st.success(f'Proyecto guardado: {target.name}')
        st.download_button('Descargar proyecto JSON', json.dumps(synchronize_source(st.session_state,p),ensure_ascii=False,sort_keys=True),
            file_name='ecuador-vivo-proyecto.json', mime='application/json')
