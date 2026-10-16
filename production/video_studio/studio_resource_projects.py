"""Reusable illustrations are ordinary, single-scene Studio documents.

The library is a metadata view over the existing saved-project folder. It has
no second renderer, database, app, audio clock or scientific calculation path.
"""
import copy
from functools import lru_cache
import json
from pathlib import Path
import uuid

from output_profiles import profile_for
from studio_model import validate_scene, validate_studio

_ILLUSTRATION_TYPES = frozenset(('text', 'shape', 'icon', 'source', 'logo',
                                'background', 'group', 'image', 'video'))


def _label(value, label, maximum=180):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(label + ': escribe un texto de 1 a ' + str(maximum) + ' caracteres.')
    return value.strip()


def _tag(project, name, category):
    name = _label(name, 'Nombre')
    project['name'] = name
    project['project_meta']['resource'] = {'version': 1, 'name': name,
                                          'category': _label(category, 'Categoría', 80)}
    return project


def create_resource_project(name, profile, *, resource_id=None, duration=6):
    """Return a new blank/template project; never save it or mutate another one."""
    from studio_home import create_project
    project = create_project('free', profile, theme='Ecuador Vivo Social', name=name)
    active = project['studio']['timeline'][0]
    project['studio']['scenes'] = [scene for scene in project['studio']['scenes'] if scene['id'] == active]
    project['studio'].pop('legacy_timeline', None)
    if resource_id is not None:
        from studio_resources import resource_scene
        scene = resource_scene(resource_id, profile_for(profile), duration=duration, title=name)
        project['studio']['scenes'] = [scene]
        project['studio']['timeline'] = [scene['id']]
    else:
        if isinstance(duration, bool) or not isinstance(duration, (int, float)):
            raise ValueError('Duración de recurso inválida.')
        project['studio']['scenes'][0]['duration'] = duration
    validate_studio(project['studio'])
    return _tag(project, name, 'Mis recursos')


def _illustration(scene):
    validate_scene(scene)
    if (scene.get('renderer', 'studio') != 'studio' or scene.get('map_instances')
            or any(element['type'] not in _ILLUSTRATION_TYPES
                   or element.get('data_binding') or element.get('temporal_binding')
                   for element in scene['elements'])):
        raise ValueError('Los mapas y resultados científicos permanecen en su proyecto. '
                         'Guarda aquí una escena ilustrativa sin vínculos científicos.')


def _fresh_scene(scene):
    fresh = copy.deepcopy(scene)
    fresh['id'] = 'scene.' + uuid.uuid4().hex
    ids = {element['id']: 'element.' + uuid.uuid4().hex for element in fresh['elements']}
    groups = {element['group_id'] for element in fresh['elements'] if element.get('group_id')}
    ids.update({group: ids.get(group, 'group.' + uuid.uuid4().hex) for group in groups})
    for element in fresh['elements']:
        element['id'] = ids[element['id']]
        if element.get('group_id'):
            element['group_id'] = ids[element['group_id']]
        if element['type'] == 'video':
            element.setdefault('style', {})['mute'] = True
    # Keep only authored drawing fields and the explanation's provenance.
    allowed = {'id', 'name', 'duration', 'elements', 'background', 'renderer',
               'resource', 'resource_overlays', 'typography', 'font_roles'}
    return {key: value for key, value in fresh.items() if key in allowed}


def resource_from_scene(project, scene_id, name, category='Mis recursos'):
    """Capture one illustrative scene with only its image/video asset closure.

    This explicit copy never converts the entire video into a library item.
    Narration, captions, other scenes and scientific registries are not copied.
    """
    scene = next((scene for scene in project['studio']['scenes'] if scene['id'] == scene_id), None)
    if scene is None:
        raise ValueError('Selecciona una escena existente para guardar el recurso.')
    _illustration(scene)
    result = create_resource_project(name, project['studio']['output_profile'])
    fresh = _fresh_scene(scene)
    result['studio']['scenes'] = [fresh]
    result['studio']['timeline'] = [fresh['id']]
    used = {element.get('style', {}).get('asset_id') for element in fresh['elements']}
    used.discard(None)
    media = project['studio'].get('media', {})
    if any(asset not in media or media[asset].get('kind') not in ('image', 'video') for asset in used):
        raise ValueError('El recurso necesita una imagen o video seguro presente en la biblioteca.')
    result['studio']['media'] = {asset: copy.deepcopy(media[asset]) for asset in used}
    validate_studio(result['studio'])
    return _tag(result, name, category)


def insert_saved_resource(target, resource):
    """Append a reusable scene without touching the target's global clocks/data."""
    if not is_resource(resource):
        raise ValueError('Este archivo no es un recurso reutilizable.')
    by_id = {scene['id']: scene for scene in resource['studio']['scenes']}
    timeline = resource['studio']['timeline']
    if len(timeline) != 1 or len(by_id) != 1:
        raise ValueError('Un recurso reutilizable debe contener una sola escena.')
    source = by_id[timeline[0]]
    _illustration(source)
    result = copy.deepcopy(target)
    fresh = _fresh_scene(source)
    original = profile_for(resource['studio']['output_profile'])
    destination = profile_for(target['studio']['output_profile'])
    factor = min(destination.width / original.width, destination.height / original.height)
    offset_x = (destination.width - original.width * factor) / 2
    offset_y = (destination.height - original.height * factor) / 2
    media = result['studio'].setdefault('media', {})
    asset_ids = {}
    for element in fresh['elements']:
        box = element['transform']
        box['x'] = round(box.get('x', 0) * factor + offset_x)
        box['y'] = round(box.get('y', 0) * factor + offset_y)
        for size in ('width', 'height'):
            box[size] = max(1, round(box.get(size, 100) * factor))
        style = element.get('style', {})
        for field in ('font_size', 'stroke_width', 'outline_width', 'padding', 'radius'):
            if isinstance(style.get(field), (float, int)):
                style[field] = max(8 if field == 'font_size' else 0, round(style[field] * factor))
        asset = style.get('asset_id')
        if asset:
            record = resource['studio'].get('media', {}).get(asset)
            if not isinstance(record, dict) or record.get('kind') not in ('image', 'video'):
                raise ValueError('Archivo multimedia ausente o incompatible en el recurso.')
            if asset not in asset_ids:
                renamed = asset if asset not in media or media[asset] == record else 'asset.' + uuid.uuid4().hex
                asset_ids[asset] = renamed
                media[renamed] = copy.deepcopy(record)
            style['asset_id'] = asset_ids[asset]
    result['studio']['scenes'].append(fresh)
    result['studio']['timeline'].append(fresh['id'])
    validate_studio(result['studio'])
    return result


def is_resource(project):
    if not isinstance(project, dict) or not isinstance(project.get('project_meta'), dict):
        return False
    tag = project['project_meta'].get('resource', {})
    return isinstance(tag, dict) and type(tag.get('version')) is int and tag['version'] == 1


@lru_cache(maxsize=128)
def _file_metadata(path, modified, size):
    # Metadata only: never instantiate PreparedTimeline, load an asset or render.
    if size > 8 * 1024 ** 2:
        return None
    try:
        project = json.loads(Path(path).read_text(encoding='utf-8-sig'))
        if not isinstance(project, dict) or not is_resource(project):
            return None
        tag = project['project_meta']['resource']
        return {'path': path, 'name': _label(tag.get('name'), 'Nombre'),
                'category': _label(tag.get('category', 'Mis recursos'), 'Categoría', 80),
                'modified': modified, 'project_id': project['project_meta'].get('id', '')}
    except (OSError, ValueError, TypeError, KeyError, AttributeError, RecursionError):
        return None


def resource_files(store):
    """Read a bounded, stat-keyed metadata catalogue over normal saved projects."""
    root = (Path(store) / 'projects').resolve()
    if not root.is_dir():
        return []
    candidates = []
    for path in root.glob('*.json'):
        if path.name.endswith('.previous.json') or not path.is_file() or not path.resolve().is_relative_to(root):
            continue
        try:
            stat = path.stat()
        except OSError:
            continue  # A file can disappear while another window saves its library.
        candidates.append((str(path), stat.st_mtime_ns, stat.st_size))
    results, identities = [], set()
    for signature in sorted(candidates, key=lambda row: row[1], reverse=True):
        record = _file_metadata(*signature)
        if record and (record['project_id'] or record['path']) not in identities:
            results.append(dict(record))
            identities.add(record['project_id'] or record['path'])
    return results


def load_resource(path, store):
    root = (Path(store) / 'projects').resolve()
    selected = Path(path).resolve()
    if not selected.is_relative_to(root) or selected.suffix.lower() != '.json' or selected.stat().st_size > 8 * 1024 ** 2:
        raise ValueError('El recurso debe estar en la biblioteca local de proyectos.')
    document = json.loads(selected.read_text(encoding='utf-8-sig'))
    if not isinstance(document, dict) or not is_resource(document):
        raise ValueError('No se encontró un recurso reutilizable válido.')
    validate_studio(document['studio'])
    return resource_from_scene(document, document['studio']['timeline'][0], document['name'],
                               document['project_meta']['resource']['category'])
