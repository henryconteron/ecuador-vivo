"""Validated, serializable project settings for the local video editor."""

import copy
import datetime as dt
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / '_local' / 'video-studio'
TEMPLATE_VERSION = 6

PALETTES = {
    'Ecuador Vivo · maqueta': [
        '#052c44', '#0a6194', '#1da9d6', '#42c9c7',
        '#bcec98', '#fed35c', '#fd643b', '#cf2a6a'
    ],
    'Ecuador Vivo · original': [
        '#102b36', '#185069', '#207ea1', '#38b9bc',
        '#8adab0', '#f5df80', '#f39a55', '#b74362'
    ],
    'Océano': ['#071b36', '#123c69', '#176b96', '#1595ad', '#3ebdb6', '#81d9c1', '#b7ead8', '#effcf3'],
    'Calor': ['#16004d', '#2636a6', '#166ed1', '#25c7e8', '#d9ed65', '#ffbd28', '#ed563b', '#ad0f68'],
    'Vegetación': ['#68412b', '#a06c3b', '#c5a45e', '#e6dda3', '#b7d589', '#72b667', '#33864a', '#0b5335'],
    'Anomalías': ['#313695', '#4575b4', '#74add1', '#e0f3f8', '#fff7bc', '#fdae61', '#d73027', '#a50026'],
    'Viridis': ['#440154', '#46327e', '#365c8d', '#277f8e', '#1fa187', '#4ac16d', '#a0da39', '#fde725'],
}

CLASSES = [
    {'value': 0, 'label': 'Agua', 'color': '#419bdf'},
    {'value': 1, 'label': 'Árboles', 'color': '#397d49'},
    {'value': 2, 'label': 'Pasto', 'color': '#88b053'},
    {'value': 3, 'label': 'Vegetación inundada', 'color': '#7a87c6'},
    {'value': 4, 'label': 'Cultivos', 'color': '#e49635'},
    {'value': 5, 'label': 'Matorral', 'color': '#dfc35a'},
    {'value': 6, 'label': 'Construido', 'color': '#c4281b'},
    {'value': 7, 'label': 'Suelo desnudo', 'color': '#a59b8f'},
    {'value': 8, 'label': 'Nieve / hielo', 'color': '#b39fe1'},
]

TEXT_DEFAULTS = {
    'author': 'Henry P. Conteron Moreta',
    'credits': 'Ing. Geociencias',
    'counter_label': '',
    'date_format': 'DD / MM / AAAA',
    'scale_note': 'Escala fija · resolución nativa ≈ 5,6 km',
    'category_note': 'Clases originales · vecino más cercano · sin mezclar códigos',
    'boundary_note': '',
    'city_labels': {},
    'tiktok': '@elgeocientifico',
    'instagram': '@henry_conteron',
    'title_gradient_1': '#58B8F8',
    'title_gradient_2': '#F3F2EE',
    'endcard_title': 'MÉTRICAS FINALES',
    'endcard_subtitle': 'Así se comportó la lluvia en Ecuador durante 2024.',
    'endcard_section_1': '2024 EN CIFRAS',
    'endcard_section_1_note': 'Resumen del periodo observado.',
    'endcard_section_2': '¿DÓNDE LLOVIÓ MÁS?',
    'endcard_section_2_note': 'Provincias · promedio espacial · ranking 1–12',
    'endcard_section_3': 'PROVINCIAS 13–24',
    'endcard_section_3_note': 'Continuación del ranking.',
    'endcard_footer': 'CHIRPS v2 · resolución nativa ≈ 5,6 km',
    'endcard_footer_2': 'Ecuador continental + Galápagos · límites: geoBoundaries',
}

BOOL_DEFAULTS = {
    'show_galapagos': True,
    'show_provinces': True,
    'show_play_button': True,
    'endcard_enabled': True,
}

ENDCARD_DEFAULTS = {
    'endcard_duration': 6.0,
    # Sum is appropriate for precipitation increments. Intensive variables
    # such as temperature and spectral indices must use a temporal mean.
    'endcard_aggregation': 'sum',
    'endcard_accumulated_units': 'mm',
    # Each ranking entry is the native-raster spatial mean of an ADM1 polygon.
    # Keeping this explicit makes its method auditable in saved projects.
    'endcard_rank_mode': 'provinces',
}


def upgrade_project(p):
    """Upgrade old editor projects to the approved Ecuador Vivo template."""
    if not isinstance(p, dict):
        raise ValueError('El proyecto debe ser un objeto JSON.')

    try:
        version = int(p.get('template_version', 1))
    except (TypeError, ValueError):
        version = 1

    # Migration from the old editor layout. Custom titles are preserved; only
    # the original factory text is replaced with the approved rain template.
    if version < TEMPLATE_VERSION:
        old_title = str(p.get('title', '')).strip()
        old_description = str(p.get('description', '')).strip()

        p['layout'] = 'maqueta'

        if old_title in ('La lluvia cambia.', 'La lluvia cambia'):
            p['title'] = 'LLUVIA EN ECUADOR'

        if old_description == 'Mira dónde cae cada día.':
            p['description'] = 'Así cambió la precipitación día a día durante 2024.'

        if p.get('brand') == 'ECUADOR VIVO  /  ANDES PULSO':
            p['brand'] = 'ECUADOR VIVO / ANDES PULSO'

        old_palette = [
            '#102b36', '#185069', '#207ea1', '#38b9bc',
            '#8adab0', '#f5df80', '#f39a55', '#b74362'
        ]
        if p.get('source') == 'chirps' and p.get('palette') == old_palette:
            p['palette'] = list(PALETTES['Ecuador Vivo · maqueta'])

        if p.get('background') == '#0b1922':
            p['background'] = '#04141F'
        if p.get('text') == '#f3f1e9':
            p['text'] = '#F8FAFB'
        if p.get('accent') == '#77d8bc':
            p['accent'] = '#5DF2D8'

        # The old annual rain default was 1.5 s per date (~549 s). The approved
        # social cut is ~26 s. Only change the exact legacy factory value.
        if p.get('duration') == 549.0:
            p['duration'] = 26.0

        # The first closing card ranked a 3×3 sample around each provincial
        # capital.  Preserve intentional custom copy, but migrate the factory
        # wording to the scientifically stronger provincial zonal statistic.
        if p.get('endcard_section_2_note') in (
            '', 'Capitales provinciales · ranking 1–12',
            'Capitales incluidas · ranking 1–12',
        ):
            p['endcard_section_2_note'] = (
                'Provincias · promedio espacial · ranking 1–12'
            )
        if p.get('endcard_section_3', '').upper().replace('–', '-') == 'CIUDADES 13-24':
            p['endcard_section_3'] = 'PROVINCIAS 13–24'
        p['endcard_rank_mode'] = 'provinces'

        p['template_version'] = TEMPLATE_VERSION

    for key, value in TEXT_DEFAULTS.items():
        p.setdefault(key, copy.deepcopy(value))

    for key, value in BOOL_DEFAULTS.items():
        p.setdefault(key, value)

    for key, value in ENDCARD_DEFAULTS.items():
        p.setdefault(key, value)

    p.setdefault('layout', 'maqueta')
    p.setdefault('template_version', TEMPLATE_VERSION)

    # Old projects usually stored author/credits as empty strings.
    if p.get('layout') == 'maqueta':
        if not p.get('author'):
            p['author'] = TEXT_DEFAULTS['author']
        if not p.get('credits'):
            p['credits'] = TEXT_DEFAULTS['credits']

    return p


def default_project():
    return upgrade_project({
        'version': 1,
        'template_version': TEMPLATE_VERSION,
        'name': '366 días de lluvia en Ecuador',
        'source': 'chirps',
        'kind': 'continuous',
        'variable': 'Lluvia',
        'title': 'LLUVIA EN ECUADOR',
        'description': 'Así cambió la precipitación día a día durante 2024.',
        'brand': 'ECUADOR VIVO / ANDES PULSO',
        'citation': 'CHIRPS v2 · UCSB / Climate Hazards Center',
        'source_url': 'https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY',
        'units': 'mm/día',
        'legend': 'LLUVIA ACUMULADA',
        'note': '',
        'resolution_note': 'Escala fija · resolución nativa ≈ 5,6 km',
        'start': '2024-01-01',
        'end': '2024-12-31',
        'cadence': 'Diaria',
        'duration': 26.0,
        'width': 1080,
        'fps': 30,
        'crf': 18,
        'background': '#04141F',
        'text': '#F8FAFB',
        'accent': '#5DF2D8',
        'palette': list(PALETTES['Ecuador Vivo · maqueta']),
        'stops': [0, 1, 5, 10, 20, 40, 70, 120],
        'classes': copy.deepcopy(CLASSES),
        'bbox': [-81.5, -5.2, -75.0, 1.8],
        'clip_ecuador': True,
        'cities': ['Quito', 'Guayaquil', 'Cuenca', 'Tena'],
        'scale': 1.0,
        'offset': 0.0,
        'nodata': None,
        'entries': [],
        'layout': 'maqueta',
        'author': 'Henry P. Conteron Moreta',
        'credits': 'Ing. Geociencias',
        'tiktok': '@elgeocientifico',
        'instagram': '@henry_conteron',
        'show_galapagos': True,
        'show_provinces': True,
        'show_play_button': True,
        'title_gradient_1': '#58B8F8',
        'title_gradient_2': '#F3F2EE',
        'endcard_enabled': True,
        'endcard_duration': 6.0,
        'endcard_title': 'MÉTRICAS FINALES',
        'endcard_subtitle': 'Así se comportó la lluvia en Ecuador durante 2024.',
        'endcard_section_1': '2024 EN CIFRAS',
        'endcard_section_1_note': 'Resumen del periodo observado.',
        'endcard_section_2': '¿DÓNDE LLOVIÓ MÁS?',
        'endcard_section_2_note': 'Provincias · promedio espacial · ranking 1–12',
        'endcard_section_3': 'PROVINCIAS 13–24',
        'endcard_section_3_note': 'Continuación del ranking.',
        'endcard_footer': 'CHIRPS v2 · resolución nativa ≈ 5,6 km',
        'endcard_footer_2': 'Ecuador continental + Galápagos · límites: geoBoundaries',
        'endcard_aggregation': 'sum',
        'endcard_accumulated_units': 'mm',
        'endcard_rank_mode': 'provinces',
    })


def timeline(p):
    if p['source'] == 'chirps':
        first = dt.date.fromisoformat(p['start'])
        last = dt.date.fromisoformat(p['end'])
        days = (last - first).days + 1
        if not 1 <= days <= 3660:
            raise ValueError('Elige de 1 a 3660 días, con la fecha final después de la inicial.')
        if first < dt.date(1981, 1, 1) or last > dt.date.today():
            raise ValueError('CHIRPS empieza en 1981; no se admiten fechas futuras.')
        return [{'date': str(first + dt.timedelta(days=i)), 'band': 1} for i in range(days)]

    if not p.get('entries'):
        raise ValueError('Importa tus GeoTIFF y confirma sus fechas y bandas.')

    entries = sorted(p['entries'], key=lambda row: row['date'])
    dates = [dt.date.fromisoformat(row['date']) for row in entries]

    if len(dates) != len(set(dates)):
        raise ValueError('Hay fechas duplicadas. Usa una sola banda de la variable por fecha.')

    if len(entries) > 3660:
        raise ValueError('Divide la serie en lotes de hasta 3660 fechas.')

    for row in entries:
        path = Path(row['path']).resolve()
        if not path.is_relative_to((STORE / 'imports').resolve()) or not path.is_file():
            raise ValueError('Falta un GeoTIFF importado en este equipo. Vuelve a cargarlo en Datos.')
        if not isinstance(row['band'], int) or row['band'] < 1:
            raise ValueError('La banda debe ser un entero a partir de 1.')

    if p['cadence'] == 'Diaria' and any((b - a).days != 1 for a, b in zip(dates, dates[1:])):
        raise ValueError('La serie diaria tiene huecos. Corrige las fechas o elige «Por observación».')

    return entries


def validate(p):
    upgrade_project(p)

    if p.get('version') != 1 or p.get('source') not in ('chirps', 'local'):
        raise ValueError('Proyecto no compatible con esta versión del editor.')

    if p['layout'] not in ('maqueta', 'social', 'conservative', 'original'):
        raise ValueError('Distribución de video no válida.')

    for key in (
        'name', 'title', 'description', 'citation', 'units',
        'legend', 'brand', 'note', 'resolution_note'
    ):
        if not isinstance(p.get(key), str) or len(p[key]) > 200:
            raise ValueError(f'Revisa el texto de {key} (máximo 200 caracteres).')

    if not p['title'].strip() or not p['citation'].strip():
        raise ValueError('Escribe un título y una fuente para el video.')

    for key in TEXT_DEFAULTS.keys() - {'city_labels'}:
        value = p[key]
        if not isinstance(value, str) or len(value) > 200 or '\n' in value or '\r' in value:
            raise ValueError(f'Revisa {key}: una línea, máximo 200 caracteres.')

    for key in BOOL_DEFAULTS:
        if not isinstance(p[key], bool):
            raise ValueError(f'{key} debe ser verdadero o falso.')

    if (
        not isinstance(p['endcard_duration'], (int, float))
        or not math.isfinite(p['endcard_duration'])
        or not 1 <= p['endcard_duration'] <= 30
    ):
        raise ValueError('El cierre final debe durar entre 1 y 30 segundos.')

    if p.get('endcard_aggregation') not in ('sum', 'mean'):
        raise ValueError('La métrica temporal del cierre no es válida.')
    if (not isinstance(p.get('endcard_accumulated_units'), str)
            or len(p['endcard_accumulated_units']) > 40
            or '\n' in p['endcard_accumulated_units']
            or '\r' in p['endcard_accumulated_units']):
        raise ValueError('Revisa las unidades acumuladas del cierre.')

    if p['date_format'] not in ('DD / MM / AAAA', 'AAAA-MM-DD', 'MM / DD / AAAA'):
        raise ValueError('Formato de fecha no válido.')

    if not isinstance(p['city_labels'], dict) or any(
        key not in ('Quito', 'Guayaquil', 'Cuenca', 'Tena', 'Archidona')
        or not isinstance(value, str)
        or len(value) > 60
        or '\n' in value
        or '\r' in value
        for key, value in p['city_labels'].items()
    ):
        raise ValueError('Revisa los nombres de las ciudades (máximo 60 caracteres).')

    colors = [
        p['background'], p['text'], p['accent'],
        p['title_gradient_1'], p['title_gradient_2'],
        *p['palette']
    ]
    for color in colors:
        if not isinstance(color, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', color):
            raise ValueError('Los colores deben tener formato #RRGGBB.')

    if p['kind'] not in ('continuous', 'categorical'):
        raise ValueError('Tipo de variable no válido.')

    if p['kind'] == 'categorical' and p.get('endcard_enabled', True):
        raise ValueError(
            'El cierre de métricas requiere una variable continua. '
            'Desactívalo para mapas categóricos.'
        )

    if p['cadence'] not in ('Diaria', 'Mensual', 'Anual', 'Por observación'):
        raise ValueError('Frecuencia temporal no válida.')

    if p['source'] == 'chirps' and (
        p['kind'] != 'continuous' or p['scale'] != 1 or p['offset'] != 0
    ):
        raise ValueError('La lluvia automática mantiene sus unidades originales.')

    if p['kind'] == 'continuous':
        stops = p['stops']
        if not 2 <= len(stops) <= 10 or len(stops) != len(p['palette']):
            raise ValueError('Usa entre 2 y 10 valores, con un color por valor.')
        if not all(math.isfinite(x) for x in stops) or any(b <= a for a, b in zip(stops, stops[1:])):
            raise ValueError('Los valores de la escala deben ser finitos y crecientes.')
    else:
        classes = p['classes']
        if not 1 <= len(classes) <= 12 or len({c['value'] for c in classes}) != len(classes):
            raise ValueError('Usa de 1 a 12 clases con códigos únicos.')
        for c in classes:
            if not math.isfinite(c['value']) or int(c['value']) != c['value']:
                raise ValueError('Las clases deben tener códigos enteros.')
            if not re.fullmatch(r'#[0-9a-fA-F]{6}', c['color']) or not c['label'].strip():
                raise ValueError('Cada clase necesita nombre y color #RRGGBB.')
        if p['scale'] != 1 or p['offset'] != 0:
            raise ValueError('Las categorías conservan sus códigos sin factor ni desplazamiento.')

    box = p['bbox']
    if (
        len(box) != 4
        or not all(math.isfinite(x) for x in box)
        or not (-180 <= box[0] < box[2] <= 180 and -85 <= box[1] < box[3] <= 85)
    ):
        raise ValueError('Revisa los límites oeste, sur, este y norte del mapa.')

    for key in ('scale', 'offset'):
        if not math.isfinite(p[key]):
            raise ValueError('Factor y desplazamiento deben ser finitos.')

    if p['nodata'] is not None and not math.isfinite(p['nodata']):
        raise ValueError('NoData debe ser un número finito o vacío.')

    if p['width'] not in (720, 1080) or p['fps'] != 30 or p['crf'] not in (16, 18, 22):
        raise ValueError('Formato de exportación no admitido.')

    rows = timeline(p)
    duration = p['duration']

    if (
        not isinstance(duration, (int, float))
        or not math.isfinite(duration)
        or not len(rows) / 30 <= duration <= 7200
    ):
        raise ValueError(
            f'Usa una duración entre {len(rows) / 30:.2f} y 7200 s; '
            'cada fecha necesita al menos un cuadro.'
        )

    return rows


def frame_counts(count, seconds, fps=30):
    total = round(seconds * fps)
    if count < 1 or total < count:
        raise ValueError('Duración insuficiente para mostrar todas las fechas.')
    return [
        ((i + 1) * total // count) - (i * total // count)
        for i in range(count)
    ]
