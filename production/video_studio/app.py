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
if 'maqueta' in sys.modules:
    _maqueta = importlib.reload(sys.modules['maqueta'])
if 'endcard' in sys.modules:
    _endcard = importlib.reload(sys.modules['endcard'])
import render as _render
_render = importlib.reload(_render)
import social as _social
_social = importlib.reload(_social)
import jobs as _jobs
_jobs = importlib.reload(_jobs)

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
from endcard import compose_endcard, summary_for_project


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

p = upgrade_project(st.session_state.project)
revision = st.session_state.revision

# Included in the cached preview key so old PNGs can never survive a renderer
# update with the same project JSON.
RENDER_CACHE_VERSION = f'ecuador-vivo-maqueta-{TEMPLATE_VERSION}-3'


# =============================================================================
# HELPERS
# =============================================================================

def replace_project(project):
    st.session_state.project = upgrade_project(project)
    st.session_state.revision += 1
    st.session_state.preview = None
    st.session_state.endcard_preview = None
    st.session_state.import_rows = []


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
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()


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
    write_json(target, p)
    return target


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


# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.title('Ecuador Vivo')

    st.caption(
        'ESTUDIO DE VIDEO · LOCAL'
    )

    section = st.radio(
        'Espacio de trabajo',
        [
            'Editor',
            'Exportaciones',
            'Cómo usarlo'
        ],
        key='section'
    )

    st.caption(
        'Una maqueta, tus datos y tu historia.'
    )

    st.subheader(
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
            validate(candidate)
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
        'Nueva maqueta Ecuador Vivo',
        icon=':material/add:'
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
                validate(candidate)
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
1. En **Datos**, elige CHIRPS o importa tus GeoTIFF.
2. En **Diseño**, usa **Maqueta Ecuador Vivo · aprobada** y cambia título,
   subtítulo, colores y escala.
3. En **Textos y créditos**, cambia marca, autoría, fuente, TikTok e Instagram.
4. En **Mapa y tiempo**, elige ciudades, fechas, duración y resolución.
5. Pulsa **Actualizar vista previa**.
6. Cuando se vea como quieres, pulsa **Generar video**.

### Maqueta Ecuador Vivo
La plantilla aprobada conserva la estructura visual:
- cabecera Ecuador Vivo / Andes Pulso;
- contador temporal;
- mapa principal;
- Galápagos opcional;
- límites provinciales opcionales;
- leyenda;
- fuente, autoría y redes.

La vista previa y la exportación utilizan el mismo renderer. Lo que ves en la
vista previa es la composición que se envía al MP4.

### Datos
**CHIRPS:** lluvia diaria en mm/día. No se inventan días intermedios.

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

        st.success(
            'MP4 terminado · conserva la maqueta y la configuración del proyecto.'
        )

        with st.container(
            width=400
        ):
            st.video(
                str(
                    folder
                    / 'ecuador-vivo.mp4'
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
                        folder
                        / 'ecuador-vivo.mp4'
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

st.title('Cuenta una historia con tus mapas')

st.caption(
    'La maqueta de Ecuador Vivo, ahora editable. '
    'Datos reales · vista previa · MP4 vertical.'
)

left, right = st.columns(
    [
        1.25,
        1
    ],
    gap='large'
)


# =============================================================================
# LEFT CONTROLS
# =============================================================================

with left:

    step = st.segmented_control(
        'Controles',
        [
            'Datos',
            'Diseño',
            'Cierre final',
            'Textos y créditos',
            'Mapa y tiempo'
        ],
        default='Datos',
        key='step'
    )

    with st.container(
        border=True
    ):

        if step == 'Datos':

            st.subheader(
                'Elige qué quieres contar'
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
                    'Vista previa y MP4 usan la misma composición.'
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
            if categorical_endcard:
                # A ranked numerical endcard would falsely imply arithmetic
                # meaning for land-cover or other class codes.
                p['endcard_enabled'] = False
                st.info(
                    'Las capas categóricas no usan este cierre numérico. '
                    'Desactívalo o prepara un cierre de clases específico.'
                )

            p['endcard_enabled'] = st.toggle(
                'Añadir el cierre al final del video',
                p.get('endcard_enabled', True),
                key=f'endcard_enabled_{revision}',
                disabled=categorical_endcard,
            )

            if p['endcard_enabled']:
                aggregation = st.segmented_control(
                    'Cómo se combinan las fechas',
                    ['sum', 'mean'],
                    default=p.get('endcard_aggregation', 'sum'),
                    format_func=lambda value: (
                        'Acumular · lluvia, caudal por intervalo'
                        if value == 'sum'
                        else 'Promediar · temperatura, índices'
                    ),
                    key=f'endcard_aggregation_{revision}',
                    help=(
                        'Acumular suma cada fecha: úsalo solo cuando cada '
                        'mapa representa una cantidad del intervalo. '
                        'Promediar conserva las unidades de variables '
                        'intensivas, como °C, NDWI o anomalías.'
                    ),
                )
                if aggregation is not None:
                    p['endcard_aggregation'] = aggregation

                if p['endcard_aggregation'] == 'sum':
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

                p['endcard_duration'] = st.number_input(
                    'Duración del cierre (segundos)',
                    min_value=1.0,
                    max_value=30.0,
                    value=float(p.get('endcard_duration', 6.0)),
                    step=0.5,
                    key=f'endcard_duration_{revision}'
                )

                st.caption(
                    'Se agregará después de la última fecha. Las cifras se '
                    'calculan desde los rásteres exportados y también quedan '
                    'guardadas en receipt.json.'
                )
                st.caption(
                    'El ranking nacional usa las 24 provincias, incluida '
                    'Galápagos: cada valor es la media espacial de píxeles '
                    'válidos dentro del polígono provincial, no el dato de '
                    'su capital.'
                )

                p['endcard_title'] = st.text_input(
                    'Título del cierre',
                    p['endcard_title'],
                    max_chars=80,
                    key=f'endcard_title_{revision}'
                )
                p['endcard_subtitle'] = st.text_input(
                    'Subtítulo del cierre',
                    p['endcard_subtitle'],
                    max_chars=150,
                    key=f'endcard_subtitle_{revision}'
                )

                c1, c2 = st.columns(2)
                p['endcard_section_1'] = c1.text_input(
                    'Bloque 1',
                    p['endcard_section_1'],
                    max_chars=60,
                    key=f'endcard_section1_{revision}'
                )
                p['endcard_section_1_note'] = c2.text_input(
                    'Nota del bloque 1',
                    p['endcard_section_1_note'],
                    max_chars=120,
                    key=f'endcard_section1note_{revision}'
                )
                c3, c4 = st.columns(2)
                p['endcard_section_2'] = c3.text_input(
                    'Ranking 1–12',
                    p['endcard_section_2'],
                    max_chars=60,
                    key=f'endcard_section2_{revision}'
                )
                p['endcard_section_2_note'] = c4.text_input(
                    'Nota del ranking 1–12',
                    p['endcard_section_2_note'],
                    max_chars=120,
                    key=f'endcard_section2note_{revision}'
                )
                c5, c6 = st.columns(2)
                p['endcard_section_3'] = c5.text_input(
                    'Ranking 13–24',
                    p['endcard_section_3'],
                    max_chars=60,
                    key=f'endcard_section3_{revision}'
                )
                p['endcard_section_3_note'] = c6.text_input(
                    'Nota del ranking 13–24',
                    p['endcard_section_3_note'],
                    max_chars=120,
                    key=f'endcard_section3note_{revision}'
                )
                p['endcard_footer'] = st.text_input(
                    'Texto técnico del pie',
                    p['endcard_footer'],
                    max_chars=150,
                    key=f'endcard_footer_{revision}'
                )
                p['endcard_footer_2'] = st.text_input(
                    'Cobertura geográfica del pie',
                    p['endcard_footer_2'],
                    max_chars=150,
                    key=f'endcard_footer2_{revision}'
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

            try:
                rows_for_time = timeline(
                    p
                )
                minimum_duration = (
                    len(rows_for_time)
                    / 30
                )
            except Exception:
                rows_for_time = []
                minimum_duration = 0.1

            p['duration'] = st.number_input(
                'Duración total del video (segundos)',
                min_value=max(
                    0.1,
                    minimum_duration
                ),
                max_value=7200.0,
                value=max(
                    float(
                        p['duration']
                    ),
                    minimum_duration
                ),
                step=1.0,
                key=f'duration_{revision}'
            )

            cols = st.columns(2)

            if cols[0].button(
                'Ritmo corto',
                help='≈26 s para 366 fechas'
            ):

                try:
                    p['duration'] = max(
                        len(
                            timeline(
                                p
                            )
                        )
                        / 30,
                        26.0
                    )
                    rerun_project()
                except ValueError as error:
                    st.error(
                        str(error)
                    )

            if cols[1].button(
                '1,5 s por fecha'
            ):

                try:
                    p['duration'] = (
                        len(
                            timeline(
                                p
                            )
                        )
                        * 1.5
                    )
                    rerun_project()
                except ValueError as error:
                    st.error(
                        str(error)
                    )

            p['width'] = st.selectbox(
                'Resolución vertical',
                [
                    1080,
                    720
                ],
                index=(
                    0
                    if p['width'] == 1080
                    else 1
                ),
                format_func=lambda n:
                    f'{n} × {n * 16 // 9}',
                key=f'width_{revision}'
            )

            p['crf'] = st.selectbox(
                'Calidad de codificación',
                [
                    18,
                    16,
                    22
                ],
                index=[
                    18,
                    16,
                    22
                ].index(
                    p['crf']
                ),
                format_func=lambda value:
                    {
                        18:
                            'Alta',
                        16:
                            'Muy alta · archivo mayor',
                        22:
                            'Ligera · pruebas'
                    }[
                        value
                    ],
                key=f'quality_{revision}'
            )

            st.caption(
                '30 fps · H.264 · todas las fechas incluidas.'
            )

    if st.button(
        'Guardar proyecto',
        icon=':material/save:',
        key='save_project'
    ):
        target = save_project()
        st.success(
            f'Proyecto guardado: {target.name}'
        )


# =============================================================================
# RIGHT PREVIEW
# =============================================================================

with right:

    st.subheader('Tu video')

    try:
        rows = validate(p)
        error_message = None
    except (
        ValueError,
        TypeError,
        KeyError
    ) as error:
        rows = []
        error_message = str(error)
        st.warning(
            error_message
        )

    if rows:

        st.caption(
            f'{len(rows)} fechas · '
            f'{p["duration"]:g} s de mapa'
            + (f' + {p["endcard_duration"]:g} s de cierre'
               if p.get('endcard_enabled', True) else '')
            + ' · '
            f'{p["width"]} × {p["width"] * 16 // 9}'
        )

        index = (
            st.slider(
                'Fecha de la vista previa',
                1,
                len(rows),
                1,
                key=f'preview_index_{revision}'
            )
            - 1
            if len(rows) > 1
            else 0
        )

        st.caption(
            rows[index]['date']
        )

        if st.button(
            'Actualizar vista previa',
            type='primary',
            icon=':material/preview:',
            key='preview_button'
        ):

            try:

                with st.spinner(
                    'Dibujando con la maqueta…'
                ):

                    png = preview_bytes(
                        snapshot(),
                        index,
                        RENDER_CACHE_VERSION
                    )

                st.session_state.preview = {
                    'png':
                        png,
                    'signature':
                        snapshot(),
                    'index':
                        index
                }

            except Exception as error:

                st.error(
                    f'No se pudo dibujar: {error}'
                )

        last = st.session_state.preview

        if last:

            if (
                last['signature']
                != snapshot()
                or last['index']
                != index
            ):

                st.caption(
                    'Hay cambios pendientes. '
                    'Pulsa Actualizar vista previa.'
                )

            if p['layout'] == 'maqueta':

                st.image(
                    last['png'],
                    width=360,
                    alt='Vista previa de la maqueta Ecuador Vivo'
                )

                st.caption(
                    'La maqueta aprobada ya incorpora su zona segura. '
                    'El MP4 usa esta misma composición.'
                )

            else:

                guides = st.toggle(
                    'Ver márgenes de seguridad',
                    key='safe_guides'
                )

                displayed = (
                    guided_preview(
                        last['png'],
                        json.loads(
                            last['signature']
                        ).get(
                            'layout',
                            'social'
                        )
                    )
                    if guides
                    else last['png']
                )

                st.image(
                    displayed,
                    width=360
                )

            st.download_button(
                'Guardar imagen PNG',
                last['png'],
                file_name='vista-previa.png',
                mime='image/png',
                icon=':material/image:'
            )

        if p.get('endcard_enabled', True):
            st.markdown('#### Vista previa del cierre')
            st.caption(
                'La tarjeta se añade después del último mapa y se adapta a '
                'TikTok, Instagram Reels y Shorts mediante la misma zona segura.'
            )
            if st.button(
                'Actualizar vista previa del cierre',
                icon=':material/analytics:',
                key='endcard_preview_button'
            ):
                try:
                    with st.spinner('Calculando métricas y dibujando el cierre…'):
                        png = endcard_preview_bytes(
                            snapshot(),
                            RENDER_CACHE_VERSION
                        )
                    st.session_state.endcard_preview = {
                        'png': png,
                        'signature': snapshot(),
                    }
                except Exception as error:
                    st.error(f'No se pudo dibujar el cierre: {error}')

            endcard_last = st.session_state.endcard_preview
            if endcard_last:
                if endcard_last['signature'] != snapshot():
                    st.caption('El cierre tiene cambios pendientes. Actualiza su vista previa.')
                st.image(
                    endcard_last['png'],
                    width=360,
                    alt='Vista previa del cierre de métricas Ecuador Vivo'
                )
                st.download_button(
                    'Guardar cierre PNG',
                    endcard_last['png'],
                    file_name='cierre-metricas.png',
                    mime='image/png',
                    icon=':material/image:'
                )
            else:
                st.caption('Actualiza esta vista para desbloquear la exportación con cierre.')

        else:

            reference = (
                ROOT
                / '_local'
                / 'climate-studio'
                / '2024-01-01-1days'
                / 'frame-2024-01-01.png'
            )

            if reference.exists():

                st.image(
                    str(reference),
                    width=360,
                    alt='Referencia de la maqueta aprobada'
                )

                st.caption(
                    'Referencia aprobada. '
                    'Pulsa Actualizar vista previa para usar el editor.'
                )

        active = [
            state
            for _, state in statuses()
            if state.get('state')
            in (
                'queued',
                'running'
            )
        ]

        preview_ready = (
            last is not None
            and last['signature']
            == snapshot()
            and (
                not p.get('endcard_enabled', True)
                or (
                    st.session_state.endcard_preview is not None
                    and st.session_state.endcard_preview['signature'] == snapshot()
                )
            )
        )

        if not preview_ready:

            st.caption(
                'Actualiza la vista previa antes de exportar.'
            )

        if st.button(
            'Generar video',
            type='primary',
            icon=':material/movie:',
            disabled=(
                bool(active)
                or not preview_ready
            ),
            key='render_button'
        ):

            try:

                folder = start_job(
                    copy.deepcopy(
                        p
                    )
                )

                st.session_state.active_job = str(
                    folder
                )

                st.success(
                    'Exportación iniciada. '
                    'Revisa Exportaciones en la barra lateral.'
                )

            except Exception as error:

                st.error(
                    f'No se pudo iniciar: {error}'
                )

        if active:

            st.caption(
                'Hay una exportación activa. '
                'Puedes seguir diseñando mientras termina.'
            )

        st.download_button(
            'Descargar proyecto JSON',
            snapshot(),
            file_name='ecuador-vivo-proyecto.json',
            mime='application/json'
        )
