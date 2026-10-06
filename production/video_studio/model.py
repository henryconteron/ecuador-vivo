"""Validated, serializable project settings for the local video editor."""
import copy
import datetime as dt
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / '_local' / 'video-studio'
PALETTES = {
    'Ecuador Vivo · original': ['#102b36', '#185069', '#207ea1', '#38b9bc', '#8adab0', '#f5df80', '#f39a55', '#b74362'],
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
    'author': '', 'credits': '', 'counter_label': '',
    'date_format': 'DD / MM / AAAA',
    'scale_note': 'Escala fija · intervalos de color no uniformes',
    'category_note': 'Clases originales · vecino más cercano · sin mezclar códigos',
    'boundary_note': '',  # Empty preserves the automatic, source-aware caption.
    'city_labels': {},
}


def upgrade_project(p):
    """Add optional text controls without changing older saved projects."""
    if not isinstance(p, dict):
        raise ValueError('El proyecto debe ser un objeto JSON.')
    for key, value in TEXT_DEFAULTS.items():
        p.setdefault(key, copy.deepcopy(value))
    p.setdefault('layout', 'social')
    return p


def default_project():
    return upgrade_project({
        'version': 1, 'name': 'Mi video de lluvia', 'source': 'chirps', 'kind': 'continuous',
        'variable': 'Lluvia', 'title': 'La lluvia cambia.', 'description': 'Mira dónde cae cada día.',
        'brand': 'ECUADOR VIVO  /  ANDES PULSO',
        'citation': 'CHIRPS v2 · UCSB / Climate Hazards Center',
        'source_url': 'https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY',
        'units': 'mm/día', 'legend': 'LLUVIA ACUMULADA',
        'note': 'Cada fecha conserva su acumulado diario.',
        'resolution_note': 'Interpolación visual · dato nativo ≈ 5,6 km',
        'start': '2024-01-01', 'end': '2024-12-31', 'cadence': 'Diaria',
        'duration': 549.0, 'width': 1080, 'fps': 30, 'crf': 18,
        'background': '#0b1922', 'text': '#f3f1e9', 'accent': '#77d8bc',
        'palette': list(PALETTES['Ecuador Vivo · original']),
        'stops': [0, 1, 5, 10, 20, 40, 70, 120], 'classes': copy.deepcopy(CLASSES),
        'bbox': [-81.5, -5.2, -75., 1.8], 'clip_ecuador': True,
        'cities': ['Quito', 'Guayaquil', 'Cuenca', 'Tena'],
        'scale': 1., 'offset': 0., 'nodata': None, 'entries': [],
    })


def timeline(p):
    if p['source'] == 'chirps':
        first, last = dt.date.fromisoformat(p['start']), dt.date.fromisoformat(p['end'])
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
    if p['layout'] not in ('social', 'conservative', 'original'):
        raise ValueError('Distribución de video no válida.')
    for key in ('name', 'title', 'description', 'citation', 'units', 'legend', 'brand', 'note', 'resolution_note'):
        if not isinstance(p.get(key), str) or len(p[key]) > 200:
            raise ValueError(f'Revisa el texto de {key} (máximo 200 caracteres).')
    if not p['title'].strip() or not p['citation'].strip():
        raise ValueError('Escribe un título y una fuente para el video.')
    for key in TEXT_DEFAULTS.keys() - {'city_labels'}:
        if not isinstance(p[key], str) or len(p[key]) > 200 or '\n' in p[key] or '\r' in p[key]:
            raise ValueError(f'Revisa {key}: una línea, máximo 200 caracteres.')
    if p['date_format'] not in ('DD / MM / AAAA', 'AAAA-MM-DD', 'MM / DD / AAAA'):
        raise ValueError('Formato de fecha no válido.')
    if not isinstance(p['city_labels'], dict) or any(
        key not in ('Quito', 'Guayaquil', 'Cuenca', 'Tena', 'Archidona') or
        not isinstance(value, str) or len(value) > 60 or '\n' in value or '\r' in value
        for key, value in p['city_labels'].items()
    ):
        raise ValueError('Revisa los nombres de las ciudades (máximo 60 caracteres).')
    for color in [p['background'], p['text'], p['accent'], *p['palette']]:
        if not isinstance(color, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', color):
            raise ValueError('Los colores deben tener formato #RRGGBB.')
    if p['kind'] not in ('continuous', 'categorical'):
        raise ValueError('Tipo de variable no válido.')
    if p['cadence'] not in ('Diaria', 'Mensual', 'Anual', 'Por observación'):
        raise ValueError('Frecuencia temporal no válida.')
    if p['source'] == 'chirps' and (p['kind'] != 'continuous' or p['scale'] != 1 or p['offset'] != 0):
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
    if len(box) != 4 or not all(math.isfinite(x) for x in box) or not (-180 <= box[0] < box[2] <= 180 and -85 <= box[1] < box[3] <= 85):
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
    if not isinstance(duration, (int, float)) or not math.isfinite(duration) or not len(rows) / 30 <= duration <= 7200:
        raise ValueError(f'Usa una duración entre {len(rows) / 30:.2f} y 7200 s; cada fecha necesita al menos un cuadro.')
    return rows


def frame_counts(count, seconds, fps=30):
    total = round(seconds * fps)
    if count < 1 or total < count:
        raise ValueError('Duración insuficiente para mostrar todas las fechas.')
    return [((i + 1) * total // count) - (i * total // count) for i in range(count)]
