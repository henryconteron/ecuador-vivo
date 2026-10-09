"""Allowed portable presentation fonts; legacy editorial drawing stays intact."""
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from PIL import ImageFont

FONT_FAMILIES = ('Barlow Condensed', 'Atkinson Hyperlegible', 'Lora')
FONT_ROLES = {'title':'título', 'body':'cuerpo', 'source':'fuente / créditos', 'data':'datos'}
_FILES = {
    'Barlow Condensed': ('BarlowCondensed-Regular.ttf', 'BarlowCondensed-SemiBold.ttf'),
    'Atkinson Hyperlegible': ('AtkinsonHyperlegible-Regular.ttf', 'AtkinsonHyperlegible-Bold.ttf'),
    'Lora': ('Lora-Variable.ttf', 'Lora-Variable.ttf'),
}


def validate_family(family):
    if not isinstance(family, str) or family not in FONT_FAMILIES:
        raise ValueError('Familia tipográfica desconocida; elige una fuente local de la biblioteca.')


@lru_cache(maxsize=5)
def _font_bytes(filename):
    return (Path(__file__).parent/'assets'/'fonts'/filename).read_bytes()


def studio_font(size, *, family='Barlow Condensed', bold=False):
    validate_family(family)
    if type(size) is not int or not 8 <= size <= 600 or type(bold) is not bool:
        raise ValueError('Tamaño o peso tipográfico fuera de rango.')
    try:
        # Only constant filenames reach here: no project paths or system search.
        # Private FreeTypeFont objects keep variable axes isolated; BytesIO avoids
        # Windows font file handles. Pillow 12.1.1 API:
        # https://pillow.readthedocs.io/en/stable/reference/ImageFont.html
        font = ImageFont.truetype(BytesIO(_font_bytes(_FILES[family][int(bold)])), size)
        if family == 'Lora': font.set_variation_by_axes([600 if bold else 400])
        return font
    except (OSError, ValueError) as error:
        raise ValueError('No se pudo cargar la fuente local; restaura los assets antes de exportar.') from error


def element_font_role(element):
    role = element.get('typography_role', 'source' if element['type']=='source' else
                       'data' if element['type'] in ('metric','ranking','chart') else 'body')
    if not isinstance(role, str) or role not in FONT_ROLES:
        raise ValueError('Rol tipográfico desconocido.')
    return role
