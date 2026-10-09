"""Additive Studio schema. Pure migration; no filesystem, UI or calculation.

Legacy drawing remains authoritative for migrated scenes. An export route must
explicitly support renderer='studio' before accepting free-element scenes.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field, asdict
import json
import math
import re

SCHEMA_VERSION = 1
ELEMENT_TYPES = frozenset(('text', 'map', 'chart', 'metric', 'ranking', 'image',
                           'video', 'shape', 'icon', 'legend', 'table', 'source',
                           'logo', 'background', 'group'))
ANIMATIONS = frozenset(('none', 'fade', 'slide', 'scale', 'wipe'))
LEGACY_KINDS = frozenset(('map', 'endcard', 'snapshot', 'image', 'video', 'text'))


def check_schema(project):
    version = project.get('schema_version', SCHEMA_VERSION)
    if type(version) is not int or version != SCHEMA_VERSION:
        raise ValueError('schema_version no compatible; conserva el archivo original.')


def _id(value):
    if not isinstance(value, str) or not re.fullmatch(r'[\w.-]{1,180}', value):
        raise ValueError('Identificador Studio inválido.')
    return value


def _number(value, minimum, maximum, label):
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or not minimum <= value <= maximum):
        raise ValueError(f'{label}: número finito fuera de rango.')


def _json(value):
    try:
        payload = json.dumps(value, allow_nan=False, ensure_ascii=False)
    except (ValueError, TypeError, OverflowError, RecursionError) as error:
        raise ValueError('El modelo Studio debe ser JSON finito sin objetos ejecutables.') from error
    if len(payload) > 4_000_000:
        raise ValueError('El modelo Studio excede el presupuesto de 4 MB de texto.')


def validate_binding(binding):
    if not isinstance(binding, dict) or set(binding) != {'result_id', 'field'}:
        raise ValueError('Binding declarativo inválido.')
    _id(binding['result_id'])
    if not isinstance(binding['field'], str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,79}', binding['field']):
        raise ValueError('El binding solo admite nombres de campo, no expresiones.')


@dataclass(frozen=True)
class DataBinding:
    result_id: str
    field: str = 'value'

    def to_dict(self):
        result = asdict(self)
        validate_binding(result)
        return result


def validate_element(element):
    if not isinstance(element, dict):
        raise ValueError('Elemento Studio inválido.')
    _id(element.get('id'))
    if element.get('type') not in ELEMENT_TYPES:
        raise ValueError('Tipo de elemento Studio desconocido.')
    transform = element.get('transform', {})
    if not isinstance(transform, dict) or set(transform) - {'x', 'y', 'width', 'height', 'rotation'}:
        raise ValueError('Transform inválido.')
    for name, default in (('x', 0), ('y', 0), ('width', 100), ('height', 100), ('rotation', 0)):
        _number(transform.get(name, default), 1 if name in ('width', 'height') else -8192,
                8192, name)
    for name in ('visible', 'locked'):
        if type(element.get(name, True if name == 'visible' else False)) is not bool:
            raise ValueError(f'{name} debe ser booleano.')
    _number(element.get('z_index', 0), -10000, 10000, 'z_index')
    if 'group_id' in element: _id(element['group_id'])
    if not isinstance(element.get('style', {}), dict):
        raise ValueError('Style debe ser un objeto.')
    if not isinstance(element.get('name', ''), str) or len(element.get('name', '')) > 180:
        raise ValueError('Nombre de elemento demasiado largo.')
    animation = element.get('animation', {})
    if not isinstance(animation, dict):
        raise ValueError('Animación inválida.')
    for name in ('in', 'out'):
        if animation.get(name, 'none') not in ANIMATIONS:
            raise ValueError('Animación desconocida.')
    for name in ('duration', 'delay'):
        _number(animation.get(name, 0), 0, 300, name)
    if element.get('data_binding') is not None:
        validate_binding(element['data_binding'])
    temporal=element.get('temporal_binding')
    if 'temporal_binding' in element and temporal is None:raise ValueError('Binding temporal nul no admitido; omite el campo opcional.')
    if temporal is not None:
        kinds={'continent':'map','galapagos':'map','date':'text','legend_static':'legend'}
        if (not isinstance(temporal,dict) or set(temporal)!={'instance_id','channel'}
                or temporal.get('channel') not in kinds or element['type']!=kinds[temporal['channel']]):
            raise ValueError('Binding temporal o consumidor incompatible.')
        _id(temporal['instance_id'])
        if element.get('data_binding') is not None or set(element.get('style',{})) & {'asset_id','trim_in','trim_out','loop','text'}:
            raise ValueError('El binding temporal protege la fecha y usa exclusivamente el reloj de instancia.')
    _json(element)


@dataclass(frozen=True)
class Element:
    id: str
    type: str
    name: str = ''
    transform: dict = field(default_factory=lambda: {
        'x': 0, 'y': 0, 'width': 100, 'height': 100, 'rotation': 0})
    style: dict = field(default_factory=dict)
    data_binding: dict | None = None
    animation: dict = field(default_factory=lambda: {'in': 'none', 'out': 'none', 'duration': 0, 'delay': 0})
    visible: bool = True
    locked: bool = False
    z_index: float = 0
    temporal_binding: dict | None = None

    def to_dict(self):
        result = asdict(self)
        if result['temporal_binding'] is None:result.pop('temporal_binding')
        validate_element(result)
        return result


def validate_scene(scene):
    if not isinstance(scene, dict):
        raise ValueError('Escena Studio inválida.')
    _id(scene.get('id'))
    if not isinstance(scene.get('name', ''), str) or len(scene.get('name', '')) > 180:
        raise ValueError('Nombre de escena inválido.')
    _number(scene.get('duration'), 1 / 30, 7200, 'duration')
    if scene.get('renderer', 'studio') not in ('legacy', 'studio'):
        raise ValueError('Renderer desconocido.')
    elements = scene.get('elements')
    if not isinstance(elements, list) or len(elements) > 600:
        raise ValueError('Una escena admite hasta 600 elementos.')
    if scene.get('renderer') == 'legacy' and elements:
        raise ValueError('Una escena legacy no exporta elementos libres; usa renderer Studio compatible.')
    ids = []
    for element in elements:
        validate_element(element)
        ids.append(element['id'])
    if len(ids) != len(set(ids)):
        raise ValueError('IDs de elementos repetidos en una escena.')
    instances=scene.get('map_instances',{})
    if not isinstance(instances,dict) or len(instances)>600:raise ValueError('Registro de instancias cartográficas inválido.')
    for iid,clock in instances.items():
        _id(iid)
        if not isinstance(clock,dict) or set(clock)!={'asset_id','trim_in_frame','trim_out_frame','loop'}:
            raise ValueError('Reloj cartográfico incompleto.')
        _id(clock['asset_id'])
        if (type(clock['trim_in_frame']) is not int or type(clock['trim_out_frame']) is not int
                or not 0<=clock['trim_in_frame']<clock['trim_out_frame']<=216000 or type(clock['loop']) is not bool):
            raise ValueError('Trim cartográfico requiere fotogramas enteros y loop booleano.')
    if instances and scene.get('renderer','studio')!='studio':raise ValueError('Instancias requieren renderer Studio.')
    for element in elements:
        if element.get('temporal_binding',{}).get('instance_id') not in instances and element.get('temporal_binding'):
            raise ValueError('Binding temporal apunta a una instancia ausente.')
    _json(scene)


@dataclass(frozen=True)
class Scene:
    id: str
    name: str = 'Escena'
    duration: float = 6
    elements: list = field(default_factory=list)
    background: str = '#04141F'
    renderer: str = 'studio'
    map_instances: dict | None = None

    def to_dict(self):
        result = {name: copy.deepcopy(value) for name, value in vars(self).items() if name != 'elements'}
        result['elements'] = [element.to_dict() if isinstance(element, Element)
                              else copy.deepcopy(element) for element in self.elements]
        if result['map_instances'] is None:result.pop('map_instances')
        validate_scene(result)
        return result


def validate_studio(studio):
    if not isinstance(studio, dict) or studio.get('model_version') != 1 or type(studio.get('model_version')) is not int:
        raise ValueError('Namespace studio incompatible; no se sobrescribirá.')
    scenes, timeline = studio.get('scenes'), studio.get('timeline')
    if not isinstance(scenes, list) or not 1 <= len(scenes) <= 100 or not isinstance(timeline, list):
        raise ValueError('Studio requiere escenas y timeline explícitos.')
    for scene in scenes:
        validate_scene(scene)
    ids = [scene['id'] for scene in scenes]
    for value in timeline:
        _id(value)
    if len(ids) != len(set(ids)) or not timeline or len(timeline) != len(set(timeline)) or any(value not in ids for value in timeline):
        raise ValueError('Timeline con referencias ausentes o IDs repetidos.')
    by_id = {scene['id']: scene for scene in scenes}
    if sum(by_id[value]['duration'] for value in timeline) > 7200:
        raise ValueError('Timeline excede dos horas.')
    for name in ('datasets', 'calculations', 'media'):
        if not isinstance(studio.get(name), dict):
            raise ValueError(f'{name} debe ser un registro por ID.')
    for scene in scenes:
        for element in scene['elements']:
            binding = element.get('data_binding')
            if binding:
                result = studio['calculations'].get(binding['result_id'])
                if not isinstance(result, dict) or binding['field'] not in result:
                    raise ValueError('Binding apunta a un resultado/campo inexistente.')
    _json(studio)
    return studio


def migrate_project(project):
    """Copy legacy project plus Studio namespace; stable IDs and frame timing.

    Unknown top-level fields (even scenes/calculations) retain their old meaning.
    Partial namespaces fail visibly; never silently repair or erase user work.
    """
    if not isinstance(project, dict):
        raise ValueError('El proyecto debe ser un objeto JSON.')
    check_schema(project)
    result = copy.deepcopy(project)
    result['schema_version'] = SCHEMA_VERSION
    if 'studio' in result:
        validate_studio(result['studio'])
        return result
    storyboard = project.get('storyboard', {})
    if storyboard.get('enabled'):
        cards = storyboard.get('cards', [])
    else:
        cards = [{'id': 'map', 'kind': 'map', 'label': 'Mapa'}]
        if project.get('endcard_enabled', True):
            cards.append({'id': 'endcard', 'kind': 'endcard', 'label': 'Métricas'})
    if not isinstance(cards, list) or not cards:
        raise ValueError('No hay tarjetas legacy válidas para migrar.')
    scenes = []
    for card in cards:
        if not isinstance(card, dict) or card.get('kind') not in LEGACY_KINDS:
            raise ValueError('Tarjeta legacy desconocida.')
        scene_id = 'legacy.' + _id(card.get('id'))
        default = (project.get('duration', 26) if card['kind'] == 'map'
                   else project.get('endcard_duration', 6) if card['kind'] == 'endcard' else 6)
        seconds = card.get('duration') if card.get('duration') is not None else default
        _number(seconds, 1 / 30, 7200, 'duration')
        scene = Scene(id=scene_id, name=card.get('label') or card['kind'],
                      duration=max(1, round(seconds * 30)) / 30,
                      renderer='legacy').to_dict()
        scene['legacy_card'] = copy.deepcopy(card)
        scenes.append(scene)
    result['studio'] = {'model_version': 1, 'scenes': scenes,
                        'timeline': [scene['id'] for scene in scenes],
                        'datasets': {}, 'calculations': {}, 'media': {},
                        'theme': 'Ecuador Vivo', 'output_profile': {'mode': 'legacy_delivery'}}
    validate_studio(result['studio'])
    return result
