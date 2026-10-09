"""CSV geography in the same personal video editor, with preview and endcard."""
import datetime as dt
import hashlib
import io
import json
import uuid
from pathlib import Path

import pandas as pd
import streamlit as st

from comparison_video import render_preview, render_comparison_endcard, create_comparison_job
from data import store_upload
from jobs import write_json
from model import PALETTES, STORE
from spatial_csv import prepare_csv, read_csv


def _png(image):
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()


@st.cache_data(max_entries=4, show_spinner=False)
def _read(payload):
    return read_csv(payload)


def _column(columns, candidates, key, label, *, optional=False):
    names = ['(ninguna)'] + columns if optional else columns
    selected = next((c for c in columns if c.lower().strip() in candidates), names[0])
    chosen = st.selectbox(label, names, index=names.index(selected), key=key)
    return None if chosen == '(ninguna)' else chosen


def show_spatial_csv(project, *, phase='Datos'):
    valid_key = f'spatial_valid_{st.session_state.get("revision", 0)}'
    if phase == 'Datos':
        st.session_state[valid_key] = False
        st.header('Datos geográficos desde CSV')
        st.caption('Puntos: observaciones, estaciones, pozos o registros de especies. Provincias: un valor explícito por provincia y periodo.')
        uploaded = st.file_uploader('CSV geográfico', type=['csv'], key='geographic_csv_upload')
        saved = project.get('spatial_data')
        output = None
        if uploaded:
            payload = uploaded.getvalue()
            digest = hashlib.sha256(payload).hexdigest()
            try:
                data = _read(payload)
            except (ValueError, pd.errors.ParserError) as error:
                st.error(str(error))
                return
            prefix = 'spatial_' + digest[:12]
            kind_label = st.segmented_control('Geometría', ['Puntos', 'Provincias'], default='Puntos', key=prefix+'_kind')
            kind = 'points' if kind_label == 'Puntos' else 'polygons'
            columns = list(data.columns)
            with st.container(border=True):
                if kind == 'points':
                    coords = st.columns(2)
                    with coords[0]:
                        latitude = _column(columns, ['lat', 'latitude', 'latitud', 'decimallatitude'], prefix+'_lat', 'Columna de latitud')
                    with coords[1]:
                        longitude = _column(columns, ['lon', 'lng', 'longitude', 'longitud', 'decimallongitude'], prefix+'_lon', 'Columna de longitud')
                    category = _column(columns, ['especie', 'species', 'scientificname', 'categoria', 'category', 'tipo'], prefix+'_category', 'Columna de categoría / especie', optional=True)
                    confirmed = st.checkbox('Confirmo que las coordenadas son grados WGS84, no metros UTM', key=prefix+'_wgs84')
                    province = value = None
                    st.caption('Hasta seis categorías por video. Las coordenadas se dibujan como puntos; no se convierten en una superficie de distribución.')
                else:
                    province = _column(columns, ['provincia', 'province', 'shapename', 'area'], prefix+'_province', 'Columna de provincia')
                    value = _column(columns, ['value', 'valor', 'mean', 'media'], prefix+'_value', 'Columna numérica')
                    latitude = longitude = category = None
                    confirmed = True
                    st.caption('Una fila por provincia y periodo. Usa nombres oficiales; los faltantes no son cero.')
                period = _column(columns, ['date', 'fecha', 'periodo', 'period', 'year', 'año', 'eventdate'], prefix+'_period', 'Columna de periodo', optional=True)
                exclude_invalid = st.checkbox('Autorizar excluir filas inválidas (se informará cuántas)', key=prefix+'_exclude_invalid')
            if not confirmed:
                st.info('Confirma el SRC de las coordenadas antes de generar el mapa.')
                return
            try:
                output = prepare_csv(data, kind=kind, latitude=latitude, longitude=longitude, category=category,
                                     province=province, value=value, period=period, allow_invalid=exclude_invalid)
                stored_key = 'spatial_file_' + digest
                stored_path = st.session_state.get(stored_key)
                if not stored_path or not Path(stored_path).is_file():
                    stored_path = str(store_upload(uploaded.name, payload))
                    st.session_state[stored_key] = stored_path
                path = Path(stored_path)
                output['receipts'] = [{'provider': 'CSV del usuario', 'csv_path': str(path),
                    'manifest': {'source_csv_sha256': [digest], 'retrieved_utc': dt.datetime.now(dt.timezone.utc).isoformat()}}]
                output['source_filename'] = uploaded.name
                output['source_sha256'] = digest
                if output['rejected_rows']:
                    st.warning(f"Se excluyeron {output['rejected_rows']} de {output['input_rows']} filas. {output['valid_rows']} registros válidos.")
            except (ValueError, KeyError) as error:
                st.error(str(error))
                return
        elif saved:
            output = saved
            st.caption(f"Proyecto abierto: {output.get('source_filename', 'CSV')} · {len(output['records'])} registros. Sube otro CSV para reemplazarlo.")
        else:
            st.info('Sube un CSV con latitud/longitud o provincia/valor. No se muestran datos de ejemplo como si fueran reales.')
            st.download_button('Plantilla CSV de puntos (solo cabecera)', b'latitude,longitude,species,period\n',
                               file_name='plantilla-puntos.csv', mime='text/csv')
            return

        st.session_state[valid_key] = True
    else:
        output = project.get('spatial_data')
        if not output or st.session_state.get(valid_key) is False:
            st.info('Primero importa y valida las coordenadas o provincias del CSV en Datos.')
            return

    project['spatial_data'] = output
    config = dict(project.get('spatial_design', {}))
    if config.get('source_sha256') != output.get('source_sha256'):
        config['reviewed_coordinates'] = False
        config['share_spatial_records'] = False
    config['source_sha256'] = output.get('source_sha256')
    point_mode = output['map_kind'] == 'points'
    defaults = {'title': 'LOS DATOS TIENEN UN LUGAR', 'subtitle': 'Cada punto es un registro, no una población.' if point_mode else 'Un valor por provincia. Sin inventar los faltantes.',
                'variable': 'Registros geográficos' if point_mode else 'Variable del CSV', 'units': 'registros' if point_mode else '',
                'citation': '', 'duration': 20, 'palette': list(PALETTES)[0], 'endcard_enabled': True,
                'endcard_duration': 6, 'endcard_title': 'MÉTRICAS FINALES', 'endcard_auto_text': True}
    for key, value in defaults.items():
        config.setdefault(key, value)
    for key in ('background', 'accent', 'text', 'brand', 'author', 'credits', 'tiktok', 'instagram', 'title_gradient_1', 'title_gradient_2'):
        config.setdefault(key, project[key])
    config.update(map_layout='Un mapa · años secuenciales', palette_colors=PALETTES.get(config['palette'], next(iter(PALETTES.values()))),
                  parameter='CSV_RECORDS', mode='nacional', name='CSV geográfico · Ecuador')
    if phase == 'Maqueta':
        with st.expander('Configuración de la plantilla y créditos'):
            control = st.segmented_control('Controles del mapa', ['Diseño', 'Textos y créditos', 'Cierre final'], default='Diseño', key='spatial_controls')
            with st.container(border=True):
                if control == 'Diseño':
                    config['title'] = st.text_input('Título del video', config['title'], max_chars=72, key='spatial_title')
                    config['subtitle'] = st.text_input('Frase de entrada', config['subtitle'], max_chars=96, key='spatial_subtitle')
                    config['variable'] = st.text_input('Qué representan los datos', config['variable'], key='spatial_variable')
                    if not point_mode:
                        config['units'] = st.text_input('Unidades declaradas del CSV', config['units'], key='spatial_units')
                        config['palette'] = st.selectbox('Paleta', list(PALETTES), index=list(PALETTES).index(config['palette']), key='spatial_palette')
                        config['palette_colors'] = PALETTES[config['palette']]
                    else:
                        for category, color in output['category_colors'].items():
                            output['category_colors'][category] = st.color_picker(category, color, key='spatial_color_'+category)
                        output['point_size'] = st.slider('Tamaño de los puntos', 3, 12, output.get('point_size', 6), key='spatial_point_size')
                    config['background'] = st.color_picker('Fondo', config['background'], key='spatial_background')
                elif control == 'Textos y créditos':
                    for field, label in [('brand', 'Marca'), ('author', 'Autoría'),
                                         ('credits', 'Profesión / créditos'), ('tiktok', 'TikTok'), ('instagram', 'Instagram')]:
                        config[field] = st.text_input(label, config[field], key='spatial_'+field)
                else:
                    config['endcard_enabled'] = st.toggle('Añadir tarjeta final', value=config['endcard_enabled'], key='spatial_closing')
                    config['endcard_title'] = st.text_input('Título del cierre', config['endcard_title'], key='spatial_endcard_title')
    if phase == 'Datos':
        if point_mode:
            st.warning('Un registro no prueba una distribución completa ni el número de animales. Evita publicar coordenadas sensibles de especies amenazadas.')
        config['reviewed_coordinates'] = st.checkbox('Revisé que las ubicaciones del CSV son de Ecuador y se pueden mostrar públicamente',
            value=config.get('reviewed_coordinates', False), key='spatial_coordinates_reviewed_' + str(output.get('source_sha256', 'saved'))) if point_mode else True
        config['share_spatial_records'] = st.checkbox('Permitir incluir las coordenadas / valores del CSV al preparar el caso web',
            value=config.get('share_spatial_records', False), key='spatial_share_' + str(output.get('source_sha256', 'saved')),
            help='Desactivado por defecto. La exportación local siempre conserva los datos; publicar requiere revisar permisos y sensibilidad.')
        config['citation'] = st.text_input('Fuente y cita del CSV', config['citation'], key='spatial_source_citation')
        if not config['citation'].strip():
            st.info('Añade la fuente y su cita antes de exportar.')
    config['method'] = 'Registros geolocalizados · no equivale a población ni distribución completa.' if point_mode else 'Valores por provincia del CSV · sin interpolar · sin color: sin dato.'
    config.update(delivery=project.get('delivery', {}), storyboard=project.get('storyboard', {}))
    project.update(spatial_design=config, spatial_data=output)
    st.session_state.project = project
    frame = pd.DataFrame(output['records'])
    if phase == 'Datos':
        with st.expander('Revisar registros validados'):
            st.dataframe(frame, hide_index=True, alt='Registros geográficos validados')
        st.info('Datos listos. Continúa en Maqueta para componer tu mapa.')
        return
    from workspace import authoring_config, export_check
    from storyboard import base_timing
    config = authoring_config(config)
    project['spatial_design'] = config
    if phase == 'Montaje':
        if not project.get('storyboard', {}).get('enabled'):
            config['duration'] = st.number_input('Duración del mapa · segundos',
                min_value=max(1/30, len(output['periods'])/30), max_value=3600.,
                value=float(config['duration']), key='spatial_duration')
            if config['endcard_enabled']:
                config['endcard_duration'] = st.number_input('Duración de métricas · segundos',
                    min_value=1/30, max_value=300., value=float(config['endcard_duration']), key='spatial_endcard_duration')
        project['spatial_design'] = config
        return
    if phase == 'Maqueta':
        from layout_editor import show_layout_editor
        with st.expander('Fecha de trabajo del lienzo'):
            current = st.select_slider('Periodo del mapa en el lienzo', output['periods'],
                value=output['periods'][-1], key='spatial_preview_period', persist_state='session')
        progress = (output['periods'].index(current)+.5)/len(output['periods'])
        def persist_visual_layout(layout):
            config['visual_layout'] = layout
            project['spatial_design'] = config
        try:
            show_layout_editor(config,
                lambda settings: render_preview(frame, output, settings, progress=progress),
                (lambda settings: render_comparison_endcard(frame, output, settings)[0]) if config['endcard_enabled'] else None,
                project=project, persist=persist_visual_layout, key='spatial_visual')
        except (ValueError, KeyError, TypeError, OSError) as error:
            st.error(f'No se pudo abrir la maqueta: {error}')
        return

    timed = base_timing(config)
    ready = export_check(timed, lambda settings: render_preview(frame, output, settings),
        (lambda settings: render_comparison_endcard(frame, output, settings)[0]) if timed.get('endcard_enabled') else None)
    if not config['citation'].strip() or not config.get('reviewed_coordinates'):
        st.warning('Antes de exportar, añade la cita y revisa los permisos de las coordenadas en Datos.')
    if st.button('Generar video geográfico · MP4', type='primary',
        disabled=not ready or not config['citation'].strip() or not config.get('reviewed_coordinates')):
        progress_bar = st.progress(0., text='Preparando mapas…')
        try:
            job = create_comparison_job(frame, output, config, progress_callback=progress_bar.progress)
            st.success(f'Video listo en Exportaciones: {job.name}. CSV y recibo conservados junto al MP4.')
        except Exception as error:
            st.error(f'No se pudo exportar: {error}')
    with st.container(horizontal=True):
        if st.button('Guardar proyecto CSV', icon=':material/save:'):
            target = STORE/'projects'/('csv-'+dt.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6]+'.json')
            write_json(target, project)
            st.success('Guardado para reabrir desde Tus proyectos.')
        st.download_button('Exportar proyecto JSON', json.dumps(project, ensure_ascii=False, indent=2).encode('utf-8'),
            file_name='ecuador-vivo-csv.json', mime='application/json')

