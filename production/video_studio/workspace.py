"""One workflow and export checkpoint shared by the three video editors."""
import copy
import io

import streamlit as st

from storyboard import cards_for, dimensions, format_preview

PHASES = ('Datos', 'Maqueta', 'Montaje', 'Exportar', 'Estudio')


def navigation():
    phase = st.segmented_control('Espacio de edición', PHASES,
        default='Datos', key='studio_phase', persist_state='session',
        format_func=lambda value: f'{PHASES.index(value)+1} · {value}',
        width='stretch', wrap=True,
        help='Datos: fuentes y cálculos. Maqueta: lienzo de mapa. Montaje: tarjetas. Exportar: montaje anterior. Estudio: escenas libres, canvas y timeline propios.')
    return phase or 'Datos'


def download_artwork(image, config, *, label='Descargar tarjeta PNG', key=None):
    output = format_preview(image, config)
    buffer = io.BytesIO()
    output.convert('RGB').save(buffer, format='PNG')
    st.download_button(label, buffer.getvalue(), file_name='ecuador-vivo-tarjeta.png',
                       mime='image/png', key=key)


def export_check(config, render_map, render_endcard=None):
    """Validate current settings, not an old preview; never starts an export."""
    st.header('Revisar y exportar')
    try:
        cards = cards_for(config)
        w, h = dimensions(config)
        st.caption(f'{w} × {h} px · 30 fps · {sum(c["seconds"] for c in cards):g} s · {len(cards)} tarjetas')
        st.caption(' → '.join(c.get('label') or c['kind'] for c in cards))
        # Match the visual editor's authoring canvas even if no edit has yet
        # been applied. This does not alter scientific values or sources.
        render_map(config)
        if any(c['kind'] == 'endcard' for c in cards):
            if not render_endcard:
                raise ValueError('La secuencia pide métricas, pero el cierre está desactivado. Actívalo o quita esa tarjeta en Montaje.')
            render_endcard(config)
    except (ValueError, TypeError, KeyError, OSError) as error:
        st.error(f'Revisa los datos o la maqueta: {error}')
        return False
    st.caption('Generar usa el diseño guardado en el lienzo. No hace falta actualizar una vista previa. Los datos y sus créditos se conservan junto al MP4.')
    return True


def authoring_config(config):
    result = copy.deepcopy(config)
    # The editor and MP4 must use the same base canvas from the very first
    # opening, not switch from a shrunk legacy preview after clicking OK.
    result.setdefault('visual_layout', {})['full_canvas'] = True
    return result
