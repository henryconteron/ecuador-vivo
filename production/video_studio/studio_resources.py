"""Editable educational diagrams using Studio's existing scene graph.

All marks are illustrations. This catalogue never reads datasets, calculates
scientific results, assigns observations or modifies an existing data registry.
"""
import copy
import math
import re
import uuid

from output_profiles import profile_for
from studio_model import Element, Scene, validate_studio

INK = '#04151e'
WHITE = '#f3f7f9'
MINT = '#58e4ce'
BLUE = '#65bde9'
MUTED = '#b5cbd5'
LINE = '#285466'

RESOURCE_CATALOG = (
    {'id': 'focus_legend', 'name': 'Una idea a la vez', 'category': 'Elementos gráficos',
     'summary': 'Guía la mirada: posición, color y tamaño comunican cosas distintas.',
     'subtitle': 'Primero observa. Después interpreta.',
     'note': 'Una leyenda explica el símbolo; no demuestra una causa.',
     'sources': [{'title': 'Esri · variables visuales: color y tamaño', 'url': 'https://developers.arcgis.com/javascript/latest/visualization/data-driven-styles/visual-variables/'}]},
    {'id': 'temperature_height', 'name': '¿Qué significa temperatura a 2 m?', 'category': 'Clima',
     'summary': 'Distingue la altura de medición sobre el suelo de la altitud del terreno.',
     'subtitle': 'Dos alturas diferentes. Una confusión frecuente.',
     'note': 'NASA POWER: aire a 2 m sobre la elevación media de la celda; no sobre el nivel del mar.',
     'sources': [{'title': 'NASA POWER · parámetros meteorológicos', 'url': 'https://power.larc.nasa.gov/docs/methodology/meteorology/'}]},
    {'id': 'rain_volume', 'name': '¿Cuánta agua es 1 mm de lluvia?', 'category': 'Agua',
     'summary': 'Convierte una unidad abstracta en una lámina de agua sobre un área.',
     'subtitle': 'Una lámina pequeña. Un volumen fácil de imaginar.',
     'note': 'Equivalencia geométrica: 1 mm sobre 1 m² = 1 litro. Dibujo sin escala física.',
     'sources': [{'title': 'USGS · volumen de lluvia: profundidad por área', 'url': 'https://water.usgs.gov/edu/activity-howmuchrain-metric.html'}]},
    {'id': 'comparable_calendar', 'name': 'Comparar el mismo periodo', 'category': 'Comparaciones',
     'summary': 'Explica ventanas comparables y por qué una fecha ausente no equivale a cero.',
     'subtitle': 'Mismos meses. Misma cobertura. Misma pregunta.',
     'note': 'Los años A y B son etiquetas ilustrativas. Un dato ausente no es cero.',
     'sources': [{'title': 'NOAA · comparar con el mismo mes de referencia', 'url': 'https://content-drupal.climate.gov/maps-data/data-snapshots/data-source/temperature-us-monthly-difference-average'},
                 {'title': 'CF Conventions 1.12 · datos ausentes', 'url': 'https://cfconventions.org/Data/cf-conventions/cf-conventions-1.12/cf-conventions.html#missing-data'}]},
    {'id': 'province_grid', 'name': 'Una provincia no es su capital', 'category': 'Método',
     'summary': 'Diferencia una ubicación puntual del resumen de un territorio con datos.',
     'subtitle': 'Un punto cuenta una historia. Un territorio, otra.',
     'note': 'Grilla ilustrativa, no geográfica. Los pesos y la cobertura dependen del método.',
     'sources': [{'title': 'NASA POWER · soporte espacial de las celdas', 'url': 'https://power.larc.nasa.gov/docs/methodology/meteorology/'}]},
    {'id': 'enso_anomaly', 'name': '¿Qué significa una anomalía?', 'category': 'Clima',
     'summary': 'Explica observado menos referencia y distingue los índices Niño 1+2 y Niño 3.4.',
     'subtitle': 'No es solo calor: es la diferencia respecto a una referencia.',
     'note': 'Niño 1+2 y Niño 3.4 resumen regiones distintas; no son un mapa detallado del mar.',
     'sources': [{'title': 'NOAA CPC · regiones e índices de temperatura del mar', 'url': 'https://www.cpc.ncep.noaa.gov/data/indices/'},
                 {'title': 'NOAA · definición de anomalía respecto al mismo mes', 'url': 'https://content-drupal.climate.gov/maps-data/data-snapshots/data-source/temperature-us-monthly-difference-average'}]},
)


def _entry(resource_id):
    entry = next((item for item in RESOURCE_CATALOG if item['id'] == resource_id), None)
    if entry is None:
        raise ValueError('Recurso educativo desconocido.')
    return entry


class _Diagram:
    """Logical diagram geometry, uniformly fitted into a format-specific body."""
    def __init__(self, scene_id, profile, duration, title, subtitle, accent):
        self.id = scene_id
        self.elements = []
        self.accent = accent
        self.duration = duration
        self.portrait = profile.height / profile.width >= 1.4
        self.left = max(profile.margin, profile.width * (.09 if self.portrait else .06))
        right = max(profile.margin, profile.width * (.15 if self.portrait else .06))
        self.width = profile.width - self.left - right
        top = max(profile.margin, profile.height * (.105 if self.portrait else .075))
        end = profile.height - max(profile.margin, profile.height * (.20 if self.portrait else .08))
        unit = min(profile.width, profile.height)
        self.text('brand', (self.left, top, self.width, unit * .04),
                  'ECUADOR VIVO / ANDES PULSO', unit * .024, accent, bold=True)
        title_y = top + unit * .07
        title_h = unit * (.19 if self.portrait else .11)
        self.text('title', (self.left, title_y, self.width, title_h), title,
                  unit * (.075 if self.portrait else .065), WHITE, bold=True, display=True)
        sub_y = title_y + title_h + unit * .018
        sub_h = unit * (.09 if self.portrait else .055)
        self.text('subtitle', (self.left, sub_y, self.width, sub_h), subtitle, unit * .033, MUTED)
        self.footer_y = end - unit * .115
        diagram_y = sub_y + sub_h + unit * .025
        diagram_h = self.footer_y - diagram_y - unit * .025
        self.scale = min(self.width / 900, diagram_h / 650)
        self.origin = (self.left + (self.width - 900 * self.scale) / 2,
                       diagram_y + (diagram_h - 650 * self.scale) / 2)
        self.unit = unit

    def _add(self, name, kind, box, style, delay=None, mode='fade'):
        animation = {'in': 'none', 'out': 'none', 'duration': 0, 'delay': 0}
        if delay is not None and self.duration > 2 / 30:
            span = min(.45, self.duration * .10)
            animation = {'in': mode, 'out': 'none', 'duration': span,
                         'delay': min(delay * min(1, self.duration / 6), max(0, self.duration - span - 1 / 30))}
        x, y, w, h = box
        element = Element(id=self.id + '.' + name, type=kind, name=name.replace('_', ' '),
                          transform={'x': round(x), 'y': round(y), 'width': max(1, round(w)),
                                     'height': max(1, round(h))}, style=style, animation=animation,
                          z_index=len(self.elements)).to_dict()
        element['resource_role'] = name
        self.elements.append(element)

    def text(self, name, box, text, size=40, color=WHITE, *, bold=False, display=False, delay=None, alignment='left'):
        self._add(name, 'text', box, {'text': text, 'font_size': max(8, min(400, round(size))),
                  'color': color, 'bold': bold, 'alignment': alignment,
                  'font_family': 'Barlow Condensed Display' if display else 'Barlow Condensed'}, delay)

    def box(self, box):
        x, y, w, h = box
        return (self.origin[0] + x * self.scale, self.origin[1] + y * self.scale,
                w * self.scale, h * self.scale)

    def label(self, name, box, text, size=40, color=WHITE, **kwargs):
        self.text(name, self.box(box), text, size * self.scale, color, **kwargs)

    def shape(self, name, box, *, fill=None, shape='rectangle', opacity=1, outline=None, delay=None, mode='fade'):
        style = {'fill': fill or self.accent, 'shape': shape, 'opacity': opacity}
        if outline:
            style['outline'] = outline
        self._add(name, 'shape', self.box(box), style, delay, mode)

    def panel(self, name, box, delay=None):
        self.shape(name, box, fill='#071b27', shape='panel', outline=LINE, delay=delay)

    def finish(self, entry):
        u = self.unit
        self.text('disclaimer', (self.left, self.footer_y, self.width, u * .036),
                  'ESQUEMA ILUSTRATIVO · ELEMENTOS EDITABLES', u * .023, self.accent, bold=True)
        self.text('method_note', (self.left, self.footer_y + u * .043, self.width, u * .070),
                  entry['note'], u * .025, MUTED)


def _focus(d):
    d.panel('diagram', (0, 0, 900, 650))
    d.shape('halo_outer', (265, 48, 370, 370), shape='circle', opacity=.10, delay=.2, mode='scale')
    d.shape('halo_inner', (335, 118, 230, 230), shape='circle', opacity=.22, delay=.4, mode='scale')
    d.shape('focus_point', (418, 201, 64, 64), shape='marker', delay=.65, mode='scale')
    d.label('look', (200, 360, 500, 70), 'MIRA ESTE PUNTO', 52, d.accent, bold=True, alignment='center', delay=.8)
    for index, (label, detail) in enumerate((('POSICIÓN', '¿Dónde está?'), ('COLOR', '¿Qué variable?'), ('TAMAÑO', '¿Qué cantidad?'))):
        x = 35 + index * 290
        d.shape('rule_' + str(index), (x, 468, 240, 3), fill=LINE, delay=1.2 + index * .3, mode='wipe')
        d.label('key_' + str(index), (x, 493, 240, 60), label, 40, d.accent, bold=True, delay=1.2 + index * .3)
        d.label('detail_' + str(index), (x, 552, 240, 55), detail, 34, MUTED, delay=1.4 + index * .3)


def _temperature(d):
    d.panel('diagram', (0, 0, 900, 650))
    d.shape('terrain_symbol', (45, 65, 335, 285), shape='icon.mountain', fill=BLUE, delay=.2)
    d.label('terrain_label', (35, 355, 345, 90), 'ALTITUD\nDEL TERRENO', 40, MUTED, bold=True, alignment='center', delay=.4)
    d.shape('ground', (450, 350, 390, 5), fill=WHITE)
    d.shape('measurement_height', (510, 146, 4, 204), fill=d.accent, delay=.8, mode='wipe')
    d.shape('height_top', (495, 146, 34, 4), fill=d.accent, delay=.8)
    d.shape('height_bottom', (495, 347, 34, 4), fill=d.accent, delay=.8)
    d.shape('air_temperature', (595, 72, 170, 170), shape='icon.thermometer', delay=1.1, mode='scale')
    d.label('height_value', (555, 256, 270, 77), '2 m', 76, d.accent, bold=True, alignment='center', delay=1.4)
    d.label('height_explanation', (460, 380, 375, 100), 'SOBRE EL TERRENO\nDE LA CELDA', 39, WHITE, bold=True, alignment='center', delay=1.6)
    d.shape('separator', (55, 510, 790, 3), fill=LINE)
    d.label('different_heights', (55, 540, 790, 85), 'ALTITUD ≠ ALTURA DE MEDICIÓN', 46, WHITE, bold=True, alignment='center', delay=2)


def _rain(d):
    d.panel('diagram', (0, 0, 900, 650))
    d.shape('rain_icon', (55, 55, 115, 115), shape='icon.cloud', delay=.2)
    d.label('rain_depth', (200, 56, 640, 110), '1 mm DE LLUVIA', 75, d.accent, bold=True, display=True, delay=.4)
    d.shape('water_layer', (110, 252, 680, 35), fill=BLUE, delay=.7, mode='wipe')
    d.shape('ground', (110, 287, 680, 8), fill=WHITE)
    d.shape('depth_line', (76, 252, 4, 43), fill=d.accent, delay=.8)
    d.label('area', (230, 320, 440, 70), 'SOBRE 1 m²', 54, WHITE, bold=True, alignment='center', delay=1)
    d.shape('equivalence_rule', (110, 420, 680, 3), fill=LINE)
    d.label('volume', (110, 454, 680, 110), '1 LITRO DE AGUA', 85, d.accent, bold=True, display=True, alignment='center', delay=1.5)
    d.label('accumulation', (120, 575, 660, 45), 'La lluvia del periodo se acumula en el tiempo.', 32, MUTED, alignment='center', delay=2)


def _calendar(d):
    for index, name in enumerate(('AÑO A', 'AÑO B')):
        x = index * 470
        d.panel('calendar_panel_' + str(index), (x, 0, 430, 450))
        d.shape('calendar_icon_' + str(index), (x + 145, 35, 140, 140), shape='icon.calendar', delay=.3 + index * .4)
        d.label('year_' + str(index), (x + 30, 195, 370, 75), name, 64, d.accent, bold=True, alignment='center', delay=.5 + index * .4)
        d.label('period_' + str(index), (x + 30, 290, 370, 75), 'MISMO PERIODO', 43, WHITE, bold=True, alignment='center', delay=.8 + index * .4)
        d.label('dates_' + str(index), (x + 30, 370, 370, 55), 'Solo fechas disponibles', 32, MUTED, alignment='center', delay=1 + index * .4)
    d.label('equal_coverage', (30, 490, 840, 80), 'COMPARA LA MISMA VENTANA', 57, WHITE, bold=True, alignment='center', delay=1.6)
    d.label('missing_not_zero', (40, 585, 820, 50), 'SIN DATO ≠ CERO', 43, d.accent, bold=True, alignment='center', delay=2)


def _province(d):
    d.panel('diagram', (0, 0, 900, 650))
    for row in range(3):
        for column in range(3):
            index = row * 3 + column
            d.shape('cell_' + str(index), (60 + column * 105, 100 + row * 105, 99, 99),
                    fill=('#1c647f', '#238ba0', '#58b8ba')[index % 3], delay=.2 + index * .1)
    d.shape('capital_point', (187, 227, 38, 38), shape='marker', fill='#ffce70', delay=1.2, mode='scale')
    d.label('capital_label', (60, 450, 330, 80), 'CAPITAL: UN PUNTO', 39, '#ffce70', bold=True, delay=1.5)
    d.shape('separator', (440, 70, 3, 460), fill=LINE)
    d.label('province_label', (490, 105, 350, 165), 'PROVINCIA:\nUN TERRITORIO', 54, d.accent, bold=True, delay=1.2)
    d.label('spatial_mean', (490, 292, 350, 190), 'Un resumen usa las celdas\ny la cobertura del área,\nno solo su capital.', 39, WHITE, delay=1.6)
    d.label('support_note', (55, 565, 790, 60), 'RESOLUCIÓN Y COBERTURA IMPORTAN', 43, MUTED, bold=True, alignment='center', delay=2)


def _enso(d):
    for index, (label, detail) in enumerate((('OBSERVADO', 'Dato del periodo'), ('REFERENCIA', 'Con qué se compara'))):
        x = index * 470
        d.panel('anomaly_part_' + str(index), (x, 0, 430, 205))
        d.label('part_label_' + str(index), (x + 25, 40, 380, 70), label, 52, d.accent, bold=True, alignment='center', delay=.2 + index * .5)
        d.label('part_detail_' + str(index), (x + 30, 125, 370, 60), detail, 35, MUTED, alignment='center', delay=.4 + index * .5)
    d.label('formula', (20, 240, 860, 90), 'ANOMALÍA = OBSERVADO − REFERENCIA', 51, WHITE, bold=True, alignment='center', delay=1.2)
    d.shape('formula_rule', (50, 350, 800, 3), fill=LINE)
    for index, (label, bounds) in enumerate((('NIÑO 1+2', '90–80° O · 10° S–0°'), ('NIÑO 3.4', '170–120° O · 5° S–5° N'))):
        x = index * 470
        d.panel('nino_region_' + str(index), (x, 400, 430, 210), delay=1.6)
        d.label('nino_label_' + str(index), (x + 25, 430, 380, 70), label, 55, BLUE, bold=True, alignment='center', delay=1.8)
        d.label('nino_bounds_' + str(index), (x + 25, 520, 380, 60), bounds, 35, MUTED, alignment='center', delay=2)


_DRAW = {'focus_legend': _focus, 'temperature_height': _temperature, 'rain_volume': _rain,
         'comparable_calendar': _calendar, 'province_grid': _province, 'enso_anomaly': _enso}


def resource_scene(resource_id, profile, *, duration=6, title=None, accent=None):
    """Create a new, independently editable scene for an existing output profile."""
    entry = _entry(resource_id)
    if isinstance(profile, dict):
        profile = profile_for(profile)
    if min(profile.width, profile.height) < 480:
        raise ValueError('Los recursos educativos requieren al menos 480 px en cada lado para conservar textos legibles.')
    if (isinstance(duration, bool) or not isinstance(duration, (int, float))
            or not math.isfinite(duration) or not 1 / 30 <= duration <= 7200):
        raise ValueError('Duración del recurso fuera de rango.')
    if title is not None and (not isinstance(title, str) or not title.strip() or len(title) > 180):
        raise ValueError('El título debe contener entre 1 y 180 caracteres.')
    accent = MINT if accent is None else accent
    if not isinstance(accent, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', accent):
        raise ValueError('El acento debe ser un color #RRGGBB.')
    duration = max(1, round(duration * 30)) / 30
    identifier = 'resource.' + resource_id + '.' + uuid.uuid4().hex
    diagram = _Diagram(identifier, profile, duration, title or entry['name'], entry['subtitle'], accent)
    _DRAW[resource_id](diagram)
    diagram.finish(entry)
    scene = Scene(id=identifier, name=title or entry['name'], duration=duration,
                  elements=diagram.elements, background=INK).to_dict()
    scene['resource'] = {'id': resource_id, 'version': 1, 'illustrative': True,
                         'sources_checked': '2026-10-12',
                         'sources': copy.deepcopy(entry['sources']), 'note': entry['note']}
    return scene


def insert_resource(project, resource_id, *, duration=6, title=None, accent=None,
                    mode='scene', scene_id=None):
    """Explicit author action: append a scene or overlay on a named free scene.

    This is a pure copy operation. The editor's normal commit/save mechanism
    remains responsible for project revisions, persistence and undo/redo.
    """
    if mode not in ('scene', 'overlay'):
        raise ValueError('Elige escena nueva o superposición.')
    validate_studio(project['studio'])
    result = copy.deepcopy(project)
    studio = result['studio']
    profile = profile_for(studio['output_profile'])
    if mode == 'scene':
        fresh = resource_scene(resource_id, profile, duration=duration, title=title, accent=accent)
        studio['scenes'].append(fresh)
        studio['timeline'].append(fresh['id'])
    else:
        target = next((scene for scene in studio['scenes'] if scene['id'] == scene_id), None)
        if target is None or target.get('renderer', 'studio') != 'studio':
            raise ValueError('La superposición requiere elegir una escena Studio editable.')
        fresh = resource_scene(resource_id, profile, duration=target['duration'], title=title, accent=accent)
        top_z = max((element.get('z_index', 0) for element in target['elements']), default=-1)
        for element in fresh['elements']:
            element['z_index'] += top_z + 1
        target['elements'].extend(fresh['elements'])
        target.setdefault('resource_overlays', []).append(fresh['resource'])
    validate_studio(studio)
    return result
