"""Scientific launch assistant; native preparation UI, existing Studio editor."""
import copy
import datetime as dt
import json
from pathlib import Path
import uuid
import streamlit as st

from model import STORE, default_project, upgrade_project
from studio_home import project_files
from output_profiles import PRESETS
from studio_templates import THEMES, TEMPLATES
from studio_project import request_studio_navigation
from studio_preparation import (start_preparation, preparation_status, cancel_preparation,
                                read_review, create_from_review)


def _reset():
    job = st.session_state.pop('science_job', None)
    if job: cancel_preparation(job)
    st.session_state.pop('science_source', None)


def show_scientific_assistant(document, open_project, *, publish_label='Crear proyecto en Studio', shared_profile=None):
    st.subheader('Crear desde datos científicos')
    st.caption('Fuente → Preparación → Revisión → Proyecto editable · 30 FPS')
    incoming = st.session_state.pop('_pending_scientific_source', None)
    if incoming is not None:
        _reset()
        st.session_state['science_source'] = incoming
    job = st.session_state.get('science_job')
    if not job:
        with st.container(border=True):
            st.markdown('**1 · Fuente y resultados**')
            source = st.session_state.get('science_source')
            if source is None:
                route = st.selectbox('Datos de partida', ['Proyecto actual','Proyecto guardado','Importar proyecto calculado',
                    'CHIRPS v2 automático','GeoTIFF propios','CHIRPS v3 / NASA POWER / INAMHI / CSV'], key='science_route')
                if route == 'Proyecto actual':
                    source = copy.deepcopy(document)
                elif route == 'Proyecto guardado':
                    chosen = st.selectbox('Proyecto científico guardado', [None]+project_files(STORE/'projects'),
                        format_func=lambda p: 'Selecciona…' if p is None else p.name, key='science_saved')
                    if chosen:
                        from studio_recovery import recover_snapshot
                        source, _ = recover_snapshot(chosen)
                elif route == 'Importar proyecto calculado':
                    upload = st.file_uploader('Proyecto científico JSON', type=['json'], key='science_import')
                    if upload:
                        source = json.loads(upload.getvalue())
                        if not isinstance(source,dict): raise ValueError('El proyecto científico debe ser un objeto JSON.')
                        source = upgrade_project(source)
                elif route == 'CHIRPS v2 automático':
                    source = default_project()
                    period = st.date_input('Período CHIRPS v2', (dt.date(2025,1,1),dt.date(2025,1,2)), key='science_period')
                    if isinstance(period,(tuple,list)) and len(period)==2:
                        source.update(start=str(period[0]), end=str(period[1]))
                    else: source = None
                    st.caption('Precipitación diaria · mm/día · 0,05° · Ecuador continental y Galápagos. Reutiliza archivos locales o descarga CHIRPS v2; no cambia a v3.')
                elif route == 'GeoTIFF propios':
                    source = _local_source()
                else:
                    st.info('CHIRPS v3 y NASA POWER: adquisición existente y envío de serie al asistente. INAMHI: observaciones de estación descargables; CSV geográfico: compositor existente, todavía sin adaptador de métricas Studio.')
                    if st.button('Abrir adquisición existente', key='science_acquire'):
                        st.session_state['science_acquisition'] = True
                        st.session_state['section'] = 'Obtener datos'
                        st.rerun()
            if source:
                st.caption(str(source.get('variable',''))+' · '+str(source.get('units',''))+' · '+str(source.get('start',''))+' → '+str(source.get('end','')))
                st.caption(str(source.get('citation','')))
                st.caption('Cobertura: '+str(source.get('bbox',''))+' · '+str(source.get('resolution_note','Resolución nativa del archivo de origen')))
                if st.button('Preparar revisión científica', type='primary', key='science_prepare'):
                    st.session_state['science_job'] = str(start_preparation(source))
                    st.rerun()
    else:
        status = preparation_status(job)
        if status.get('state') in ('queued','running'): _poll_preparation(job)
        else: _preparation(job, open_project, publish_label=publish_label, shared_profile=shared_profile)


def _local_source():
    from data import store_upload, inspect_file
    uploads = st.file_uploader('GeoTIFF científicos', type=['tif','tiff'], accept_multiple_files=True, key='science_tiffs')
    if not uploads: return None
    rows = []
    for upload in uploads:
        rows.extend(inspect_file(store_upload(upload.name,upload.getvalue()),upload.name))
    # Existing inspection determines bands; users must supply missing dates explicitly.
    edited = st.data_editor(rows, hide_index=True, disabled=['archivo','banda','nombre_banda','path'], key='science_dates')
    entries = [{'date':row['fecha'], 'band':int(row['banda']), 'path':row['path']} for row in edited if row['usar']]
    if not entries: return None
    source = default_project()
    variable = st.text_input('Variable científica', key='science_variable')
    units = st.text_input('Unidad del resultado', key='science_units')
    citation = st.text_input('Fuente y cita de los archivos', key='science_citation')
    with st.container(horizontal=True):
        scale = st.number_input('Factor de escala', value=1., key='science_scale')
        offset = st.number_input('Offset', value=0., key='science_offset')
    source.update(source='local', entries=entries, start=min(e['date'] for e in entries),
                  end=max(e['date'] for e in entries), variable=variable, units=units,
                  citation=citation, scale=scale, offset=offset, source_url='',
                  resolution_note='Resolución nativa de los GeoTIFF importados')
    source['cadence'] = st.selectbox('Cadencia científica', ['Diaria','Mensual','Anual'], key='science_cadence')
    source['endcard_aggregation_mode'] = 'manual'
    source['endcard_aggregation'] = st.selectbox('Operación temporal', ['mean','sum'], key='science_operation')
    source['endcard_accumulated_units'] = st.text_input('Unidad de la suma (si aplica)', key='science_sum_units')
    source['nodata'] = (st.number_input('NoData personalizado', value=-9999., key='science_nodata')
        if st.checkbox('Usar NoData personalizado', key='science_nodata_override') else None)
    st.caption('Se usa el NoData del GeoTIFF salvo que elijas un valor personalizado. Cobertura de métricas: recorte seleccionado en Ecuador.')
    if not variable.strip() or not units.strip() or not citation.strip():
        st.info('Completa variable, unidad y fuente; revisa fechas y bandas antes de preparar.')
        return None
    return source


@st.fragment(run_every='1s')
def _poll_preparation(job):
    state = preparation_status(job)
    if state.get('state') not in ('queued','running'): st.rerun()
    st.markdown('**2 · Preparación científica**')
    st.progress(float(state.get('progress',0)), text=state.get('message','Esperando worker'))
    st.caption('El cálculo sigue en segundo plano. La cancelación se comprueba entre archivos y fechas; una lectura o descarga en curso puede tardar en terminar.')
    if st.button('Cancelar preparación', key='science_cancel'):
        cancel_preparation(job)
        st.rerun()


def _preparation(job, open_project, *, publish_label='Crear proyecto en Studio', shared_profile=None):
    try:
        state = preparation_status(job)
        st.markdown('**2 · Preparación científica**')
        st.progress(float(state.get('progress',0)), text=state.get('message','Esperando worker'))
        if state.get('state') != 'complete':
            if state.get('state') == 'cancelled': st.info(state.get('message'))
            else: st.error(state.get('message','Preparación inválida'))
        else:
            review = read_review(job)
            _review(review, job, open_project, publish_label=publish_label, shared_profile=shared_profile)
        if st.button('Elegir otra fuente / nueva revisión', key='science_reset'):
            _reset(); st.rerun()
    except (ValueError,TypeError,KeyError,OSError) as error:
        st.error(str(error))
        if st.button('Volver a preparar', key='science_retry'):
            _reset(); st.rerun()


def _review(review, job, open_project, *, publish_label='Crear proyecto en Studio', shared_profile=None):
    source, snapshot = review['source'], review['snapshot']
    results = snapshot['results']
    with st.container(border=True):
        st.markdown('**3 · Revisión científica inmutable**')
        st.code(review['revision'], language=None)
        st.caption(str(source.get('variable',''))+' · '+str(source.get('start',''))+' → '+str(source.get('end','')))
        st.caption(str(source.get('citation',''))+' · '+str(source.get('resolution_note','Resolución nativa')))
        st.caption('Cobertura solicitada: '+str(source.get('bbox',''))+' · NoData del proyecto: '+str(source.get('nodata')))
        st.dataframe([{'Resultado':key, 'Variable':r['variable'], 'Unidad':r['units'],
            'Valor':r.get('value'), 'Filas':len(r.get('rows',[])),
            'NoData':sum(row.get('value') is None for row in r.get('rows',[])) if 'rows' in r else int(r.get('value') is None)}
            for key,r in results.items()], hide_index=True, alt='Resultados, unidades y datos faltantes de la revisión preparada')
        warnings = sorted({w for r in results.values() for w in r['provenance'].get('warnings',[])})
        for warning in warnings: st.warning(warning)
        with st.expander('Archivos, fechas efectivas y procedencia'):
            st.dataframe(snapshot['source_records'], hide_index=True, alt='Archivos de origen con fechas, bandas y hashes')
            st.json({key:r['provenance'] for key,r in results.items()})
        st.caption('Enviar resultados crea portada, métricas numéricas, gráficos disponibles y créditos. El mapa se prepara y revisa por separado desde SIG; no se genera automáticamente ni representa un promedio anual.')
    with st.container(border=True):
        st.markdown('**4 · Configuración audiovisual**')
        suffix = Path(job).name
        name = st.text_input('Título del proyecto científico', value=source.get('title','Resultados científicos'), max_chars=200, key='science_name_'+suffix)
        profiles = list(PRESETS)+['custom']
        profile_id = st.selectbox('Formato del proyecto científico', profiles,
            index=profiles.index(shared_profile['id']) if shared_profile else 0,
            disabled=shared_profile is not None,
            format_func=lambda k:PRESETS[k][0] if k in PRESETS else 'Personalizado', key='science_profile_'+suffix)
        profile = {'id':profile_id}
        if profile_id == 'custom':
            profile.update(width=st.number_input('Ancho científico · px',160,3840,shared_profile['width'] if shared_profile else 1920,2,key='science_width_'+suffix,disabled=shared_profile is not None),
                           height=st.number_input('Alto científico · px',160,3840,shared_profile['height'] if shared_profile else 1080,2,key='science_height_'+suffix,disabled=shared_profile is not None))
        if shared_profile is not None:
            profile = copy.deepcopy(shared_profile)
            st.caption('Formato del proyecto compartido; puedes cambiarlo explícitamente en Studio.')
        theme = st.selectbox('Estilo científico', list(THEMES), key='science_theme_'+suffix)
        template = st.selectbox('Plantilla de apertura', ['cover','quote','methodology'],format_func=lambda k:TEMPLATES[k], key='science_template_'+suffix)
        available = [k for k,r in results.items() if r.get('value') is not None or any(row.get('value') is not None for row in r.get('rows',[]))]
        from studio_science import result_display_name
        selected = st.multiselect('Resultados a incorporar', list(results), default=available,
            format_func=lambda k:result_display_name(k,results[k])+(' · Sin datos' if k not in available else ''),
            key='science_results_'+suffix)
        missing=[k for k in selected if k not in available]
        if missing:st.warning('Indicadores sin datos seleccionados: '+', '.join(missing)+'. No se crearán métricas válidas ni se sustituirán por cero.')
        duration = st.number_input('Duración inicial por escena · s',.1,120.,6.,.1,key='science_duration_'+suffix)
        count = 2 + sum(k in available for k in selected)
        st.caption(f'30 FPS · {count} escenas previstas · {count*duration:.1f} s · métricas y gráficos conservan sus bindings.')
        if st.button(publish_label, type='primary', key='science_create'):
            # Read the durable review again; UI configuration never recalculates.
            candidate = create_from_review(read_review(job), profile, selected=selected,
                theme=theme, title=name, duration=duration, cover_template=template)
            candidate['name'] = name.strip() or 'Resultados científicos'
            from studio_recovery import save_snapshot
            if shared_profile is None:
                save_snapshot(STORE/'projects'/('borrador-studio-cientifico-'+uuid.uuid4().hex[:12]+'.json'), candidate)
            open_project(candidate)
            request_studio_navigation(st.session_state)
            st.session_state.pop('science_job',None)
            st.session_state.pop('science_source',None)
            st.session_state.pop('home_mode',None)
            st.rerun()
