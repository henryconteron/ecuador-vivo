"""One shared local montage panel for raster, comparison and CSV projects."""
import copy
import datetime as dt
import uuid

import streamlit as st

from model import STORE
from jobs import write_json
from storyboard import (FORMATS, DEFAULT_FORMAT, dimensions, cards_for, store_media,
                        card_preview)

LABELS = {'map': 'Mapa animado', 'endcard': 'Métricas calculadas', 'snapshot': 'Último mapa · pausa',
          'image': 'Imagen', 'video': 'Clip de video', 'text': 'Tarjeta de explicación'}


def timeline_config(project):
    """Use the active editor's timing, not the dormant raster timing."""
    kind = project.get('video_type', 'Mapa temporal')
    design = project.get('comparison_design', {}) if kind == 'Comparación climática' else project.get('spatial_design', {}) if kind == 'CSV geográfico' else {}
    return {**project, **design, 'delivery': project.get('delivery', {}),
            'storyboard': project.get('storyboard', {})}


def show_storyboard(project, key='story', *, always_open=False):
    """Store only small metadata in project; uploads live in the private media folder."""
    enabled = always_open or st.toggle('Formato y secuencia de tarjetas', key=key+'_open')
    if not enabled:
        return
    with st.container(border=True):
        st.subheader('Salida del video')
        previous = project.get('delivery', {})
        choices = list(FORMATS)
        cols = st.columns(3)
        format_name = cols[0].selectbox('Formato del archivo final', choices,
            index=choices.index(previous.get('format', DEFAULT_FORMAT)), key=key+'_format')
        quality = cols[1].selectbox('Resolución de salida', ['1080p', '720p'],
            index=1 if previous.get('quality', '720p' if project.get('width') == 720 else '1080p') == '720p' else 0, key=key+'_quality')
        background = cols[2].color_picker('Fondo de los márgenes', previous.get('background', project.get('background', '#04151e')), key=key+'_background')
        project['delivery'] = {'format': format_name, 'quality': quality, 'background': background}
        # Render the source artwork at its native canvas size; reduce only at
        # delivery. An old 720p setting must not soften a new 1080p export.
        project['width'] = 1080
        width, height = dimensions(project)
        st.caption(f'{width} × {height} px · 30 fps · H.264. Los mapas y las métricas encajan completos, sin deformación ni recorte. El formato horizontal añade espacio lateral: no redistribuye automáticamente una maqueta vertical.')
        st.caption('El lienzo de Maqueta muestra el formato elegido. Las guías 9:16 son orientativas: revisa una prueba real en el teléfono; las interfaces y portadas de cada red pueden recortar distinto.')

        storyboard = project.setdefault('storyboard', {'enabled': False, 'cards': []})
        storyboard['enabled'] = st.toggle('Usar secuencia personalizada', value=storyboard.get('enabled', False), key=key+'_enabled')
        if not storyboard['enabled']:
            st.caption('Sin secuencia personalizada: mapa y cierre habituales, adaptados al formato elegido.')
            return
        if not storyboard.get('cards'):
            storyboard['cards'] = [dict(id='map', kind='map', label='Mapa animado', duration=None)]
            if timeline_config(project).get('endcard_enabled', True):
                storyboard['cards'].append(dict(id='endcard', kind='endcard', label='Métricas calculadas', duration=None))
        cards = storyboard['cards']
        active = timeline_config(project)
        st.subheader('Tu secuencia')
        st.caption('Selecciona una tarjeta, edita su duración y colócala antes o después con las flechas. Los ejemplos no entran en los cálculos: sus créditos quedan separados en el recibo.')
        try:
            resolved = cards_for(active)
            total = sum(row['seconds'] for row in resolved)
            start = 0.
            for i, row in enumerate(resolved):
                st.caption(f'{i+1:02d} · {start:g}–{start+row["seconds"]:g} s · {row.get("label") or LABELS[row["kind"]]}')
                start += row['seconds']
            st.caption(f'Duración prevista: {total:g} s. Los cortes se alinean a fotogramas de 1/30 s.')
        except (ValueError, TypeError, OSError) as error:
            st.warning(str(error))
        ids = [row['id'] for row in cards]
        pending = st.session_state.pop(key+'_pending_selection', None)
        if pending in ids:
            st.session_state[key+'_selected'] = pending
        active_id = st.session_state.get(key+'_active_card', ids[0])
        selected = st.selectbox('Tarjeta de la secuencia', ids,
            format_func=lambda value: f'{ids.index(value)+1:02d} · {next(row.get("label") or LABELS[row["kind"]] for row in cards if row["id"] == value)}',
            index=None if key+'_selected' in st.session_state else ids.index(active_id) if active_id in ids else 0,
            key=key+'_selected')
        st.session_state[key+'_active_card'] = selected
        row = next(card for card in cards if card['id'] == selected)
        index = cards.index(row)
        with st.container(horizontal=True):
            if st.button('Antes', icon=':material/arrow_upward:', disabled=index == 0, key=key+'_up'):
                cards[index-1], cards[index] = cards[index], cards[index-1]
                st.session_state[key+'_pending_selection'] = selected
                st.rerun()
            if st.button('Después', icon=':material/arrow_downward:', disabled=index == len(cards)-1, key=key+'_down'):
                cards[index+1], cards[index] = cards[index], cards[index+1]
                st.session_state[key+'_pending_selection'] = selected
                st.rerun()
            if st.button('Duplicar tarjeta', icon=':material/content_copy:', disabled=row['kind'] == 'map' or len(cards) >= 30, key=key+'_clone'):
                duplicate = copy.deepcopy(row)
                duplicate['id'] = uuid.uuid4().hex[:12]
                duplicate['label'] = row.get('label', LABELS[row['kind']])+' · copia'
                cards.insert(index+1, duplicate)
                st.session_state[key+'_pending_selection'] = duplicate['id']
                st.rerun()
            if st.button('Quitar de la secuencia', icon=':material/remove_circle_outline:', disabled=row['kind'] == 'map', key=key+'_remove'):
                cards.remove(row)
                st.session_state[key+'_pending_selection'] = cards[min(index,len(cards)-1)]['id']
                st.rerun()
        # Stable per-card keys prevent one card inheriting another's fields.
        prefix = key+'_'+selected
        is_base = row['kind'] in ('map', 'endcard')
        # Keep this dependency outside the form: toggling it must immediately
        # enable the duration field, without requiring a first Apply click.
        follow = st.checkbox('Usar duración de los controles del editor',
            value=row.get('duration') is None, disabled=not is_base, key=prefix+'_follow')
        with st.form(prefix+'_edit'):
            edited = dict(row)
            edited['label'] = st.text_input('Nombre de la tarjeta', row.get('label', LABELS[row['kind']]), max_chars=80)
            default = active.get('duration', 20.) if row['kind'] == 'map' else active.get('endcard_duration', 6.) if row['kind'] == 'endcard' else 6.
            if row['kind'] == 'video':
                default = min(6., max(1/30, float(row.get('source_duration', 6.))))
            seconds = st.number_input('Duración de esta tarjeta · segundos', min_value=1/30,
                max_value=3600. if row['kind'] == 'map' else 300., value=float(row.get('duration') or default),
                step=1., disabled=is_base and follow)
            edited['duration'] = None if is_base and follow else seconds
            if row['kind'] in ('image', 'video', 'text'):
                edited['title'] = st.text_input('Título visible de la tarjeta', row.get('title', ''), max_chars=150)
                if row['kind'] == 'text':
                    edited['body'] = st.text_area('Explicación', row.get('body', ''), max_chars=600, height=160)
                edited['citation'] = st.text_area('Fuente / fecha / créditos del ejemplo', row.get('citation', ''), max_chars=240)
            if row['kind'] in ('image', 'video'):
                fit = st.selectbox('Encuadre del ejemplo', ['Encajar completo', 'Rellenar con recorte'],
                    index=1 if row.get('fit') == 'cover' else 0)
                edited['fit'] = 'cover' if fit == 'Rellenar con recorte' else 'contain'
            if row['kind'] == 'video':
                edited['start'] = st.number_input('Inicio dentro del clip · segundos', min_value=0.,
                    max_value=max(0., float(row.get('source_duration', 300.))-1/30), value=float(row.get('start', 0)), step=1.)
                edited['audio'] = st.checkbox('Conservar audio de este clip', value=row.get('audio', False))
                st.caption(f'Clip original: {float(row.get("source_duration", 0)):g} s. No se repetirá ni acelerará para rellenar tiempo.')
            submitted = st.form_submit_button('Aplicar tarjeta', icon=':material/check:')
            if submitted:
                candidate = copy.deepcopy(active)
                candidate['storyboard']['cards'][index] = edited
                try:
                    cards_for(candidate)
                    preview = card_preview(edited, project)
                    cards[index] = edited
                    st.session_state[key+'_pending_selection'] = selected
                    st.rerun()
                except (ValueError, OSError, TypeError) as error:
                    st.error(str(error))
        try:
            preview = card_preview(row, project)
            if preview:
                st.image(preview, width=420, alt='Tarjeta ilustrativa en el formato de salida elegido')
            else:
                st.caption('El mapa y las métricas se ven y editan únicamente en Maqueta. Aquí solo ajustas el orden y los tiempos.')
        except (ValueError, OSError, RuntimeError) as error:
            st.error(str(error))

        with st.expander('Añadir imágenes, clips o explicaciones'):
            kind = st.selectbox('Nueva tarjeta', ['Imagen o clip', 'Explicación con texto', 'Pausa del último mapa', 'Métricas calculadas'], key=key+'_new_kind')
            upload = st.file_uploader('Importa un ejemplo desde tu computadora',
                type=['png', 'jpg', 'jpeg', 'webp', 'mp4', 'mov', 'webm', 'mkv'], max_upload_size=100, key=key+'_upload') if kind == 'Imagen o clip' else None
            st.caption('Los recursos se copian solo una vez en _local/video-studio/media. No se suben a internet ni a GitHub. Añade fecha, lugar y fuente; un clip ilustrativo no demuestra el origen de un fenómeno.')
            if st.button('Añadir a la secuencia', icon=':material/add:', disabled=len(cards) >= 30 or (kind == 'Imagen o clip' and not upload), key=key+'_add'):
                try:
                    if kind == 'Imagen o clip':
                        asset = store_media(upload.getvalue(), upload.name)
                        addition = dict(asset, source_duration=asset.get('duration'), duration=min(6., asset.get('duration', 6.)),
                                        label=asset['name'], start=0., audio=False, title='', citation='', fit='contain')
                    else:
                        code = {'Explicación con texto': 'text', 'Pausa del último mapa': 'snapshot', 'Métricas calculadas': 'endcard'}[kind]
                        addition = dict(kind=code, label=LABELS[code], duration=6., title='', body='', citation='')
                    addition['id'] = uuid.uuid4().hex[:12]
                    cards.append(addition)
                    st.session_state[key+'_pending_selection'] = addition['id']
                    st.rerun()
                except (ValueError, OSError, RuntimeError) as error:
                    st.error(str(error))
        st.caption('Continúa en Exportar para guardar el proyecto y generar la secuencia completa. No hay narración automática ni transiciones: los cortes son directos.')
