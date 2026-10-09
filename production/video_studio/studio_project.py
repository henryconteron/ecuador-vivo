"""Canonical Studio document; source projection is only a compatibility view.

No second file/model/renderer is introduced. Source edits merge into the same
document without replacing immutable scientific registries or authored scenes.
"""
import copy
import uuid
from studio_editing import new_workspace

DOCUMENT_VERSION = 1


def request_studio_navigation(state):
    # Native widgets may already exist in this run; consume before their creation.
    state['_pending_studio_navigation'] = True


def consume_studio_navigation(state):
    if state.pop('_pending_studio_navigation',False):
        state['section']='Editor'
        state['studio_phase']='Estudio'


def source_projection(document):
    return copy.deepcopy({k:v for k,v in document.items() if k not in ('studio', 'project_meta')})


def _metadata(document):
    meta = document.get('project_meta', {})
    if not isinstance(meta, dict): raise ValueError('Identidad de proyecto inválida.')
    if type(meta.get('document_version', DOCUMENT_VERSION)) is not int or meta.get('document_version', DOCUMENT_VERSION) != DOCUMENT_VERSION:
        raise ValueError('Versión de documento no compatible.')
    if not isinstance(meta.get('id', ''), str): raise ValueError('Identidad de proyecto inválida.')
    if type(meta.get('revision', 0)) is not int or meta.get('revision', 0) < 0:
        raise ValueError('Revisión de proyecto inválida.')
    if meta.get('mode','scientific') not in ('free','scientific'):
        raise ValueError('Modo de proyecto desconocido.')
    return {**copy.deepcopy(meta), 'document_version': DOCUMENT_VERSION,
            'id': meta.get('id') or 'project.'+uuid.uuid4().hex,
            'revision': meta.get('revision', 0), 'mode': meta.get('mode', 'scientific')}


def publish_document(state, document):
    state['project_document'] = document
    state['project'] = source_projection(document)
    return document


def synchronize_source(state, source):
    previous = state.get('project_document')
    if previous is None:
        document = new_workspace(source)
        document['project_meta'] = _metadata(document)
        return publish_document(state, document)
    if source_projection(previous) == source_projection(source): return previous
    document = {**source_projection(source), 'studio': copy.deepcopy(previous['studio']),
                'project_meta': _metadata(previous)}
    document['project_meta']['revision'] += 1
    return publish_document(state, document)


def prepare_commit(candidate, previous):
    document = copy.deepcopy(candidate)
    metadata = _metadata(candidate)
    clock = _metadata(previous)
    document['project_meta'] = {**metadata,'id':clock['id'],'revision':clock['revision']}
    document['project_meta']['revision'] += 1
    return document


def replace_document(state, source):
    # Opening/recovering creates a copy; saved files and previous sessions survive.
    document = new_workspace(source)
    metadata = _metadata(document)
    document['project_meta'] = {**metadata, 'id':'project.'+uuid.uuid4().hex, 'revision':0}
    return publish_document(state, document)


def workspace_key(document):
    # Never derive editor identity from source-widget revision or arbitrary names.
    identifier = _metadata(document)['id']
    return 'free_studio_'+uuid.uuid5(uuid.NAMESPACE_URL, identifier).hex


def validate_document(document):
    from model import validate
    from studio_timeline import PreparedTimeline
    prepared = new_workspace(document)
    metadata = _metadata(prepared)
    if metadata['mode'] != 'free': validate(source_projection(prepared))
    PreparedTimeline(prepared)
    return prepared
