"""Native scale controls; values are declarations accepted only on submit."""
import streamlit as st
from studio_templates import PALETTES


def color_scale_inputs(palette, *, current=None,key,all_fields=False):
    current=current if current and (all_fields or current.get('palette')==palette) else {}
    kind=PALETTES[palette]['type']
    st.caption('Escala de color declarada: no cambia valores, unidades ni ejes. La leyenda se incluye en preview y export.')
    suffix='' if all_fields else '_'+palette
    colors=st.text_area('Colores personalizados · un #RRGGBB por línea · opcional',
        '\n'.join(current.get('colors',[])),key=key+'_colors'+suffix,
        help='Vacío usa los colores de la paleta elegida. Categorías: un color distinto por etiqueta.')
    scale={'palette':palette}
    parsed=[line.strip() for line in colors.splitlines() if line.strip()]
    if parsed: scale['colors']=parsed
    if kind=='categorical' or all_fields:
        names=st.text_area('Categorías declaradas · una por línea',
            '\n'.join(current.get('categories',[])),key=key+'_categories'+suffix)
        if kind=='categorical': scale['categories']=names.splitlines()
    if kind!='categorical' or all_fields:
        low,high=current.get('domain',[-1.,1.] if kind=='diverging' or all_fields else [0.,1.])
        domain=[st.number_input('Mínimo del dominio',value=float(low),key=key+'_minimum'+suffix),
                st.number_input('Máximo del dominio',value=float(high),key=key+'_maximum'+suffix)]
        if kind!='categorical': scale['domain']=domain
        if kind=='diverging' or all_fields:
            center=st.number_input('Centro de la escala',value=float(current.get('center',0)),key=key+'_center'+suffix)
            if kind=='diverging': scale['center']=center
            st.caption('El centro usa las unidades del resultado. Decláralo según su significado; no se asume un cero físico.')
    if all_fields: st.caption('El formulario se aplica completo: categorías para paletas categóricas; dominio para numéricas; centro solo para divergentes.')
    return scale
