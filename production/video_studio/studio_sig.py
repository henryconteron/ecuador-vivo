"""SIG preparation surface over the shared document, factory and workspace."""
import copy
import streamlit as st
from studio_project import source_projection, workspace_key, request_studio_navigation
from studio_science import restored_snapshot, _hash
from studio_timeline import PreparedTimeline
from output_profiles import profile_for


def merge_scientific_proposal(project, proposal):
    """Append an explicit scientific proposal; retries reuse its authored scenes."""
    PreparedTimeline(proposal)
    snapshot = restored_snapshot(proposal)
    if snapshot is None: raise ValueError('La propuesta no tiene una revisión científica verificable.')
    old, incoming = project['studio'], proposal['studio']
    if profile_for(old['output_profile']) != profile_for(incoming['output_profile']):
        raise ValueError('Elige el formato del proyecto compartido; cambia su formato en Studio antes de enviar.')
    active = [next(s for s in incoming['scenes'] if s['id'] == sid) for sid in incoming['timeline']]
    transfer = _hash({'revision':proposal['project_meta']['scientific_revision'],
        'scenes':[{k:v for k,v in s.items() if k not in ('id','generation')} for s in active]})
    result = {**source_projection(project), **source_projection(proposal), 'name':project.get('name','Proyecto sin título'), 'studio':copy.deepcopy(old),
              'project_meta':{**copy.deepcopy(project['project_meta']),
                  **{k:proposal['project_meta'][k] for k in ('mode','scientific_revision','scientific_identity')}}}
    studio = result['studio']
    for registry in ('calculations','datasets','media'):
        for identifier, value in incoming[registry].items():
            if identifier in studio[registry] and studio[registry][identifier] != value:
                raise ValueError('Conflicto con un recurso o revisión inmutable: '+identifier)
            studio[registry][identifier] = copy.deepcopy(value)
    retained = [s for s in studio['scenes'] if s.get('generation',{}).get('sig_transfer_id') == transfer]
    if not retained:
        retained = copy.deepcopy(active)
        for scene in retained:
            scene['generation']['sig_transfer_id'] = transfer
        studio['scenes'].extend(retained)
    # Legacy scenes stay in the document. The existing Studio renderer requires
    # an active free-scene timeline; previously authored Studio scenes stay active.
    studio['timeline'] = [sid for sid in studio['timeline'] if
        next(s for s in studio['scenes'] if s['id'] == sid).get('renderer','studio') == 'studio']
    studio['timeline'].extend(s['id'] for s in retained if s['id'] not in studio['timeline'])
    PreparedTimeline(result)
    return result, retained[0]['id']


def send_map(session, record):
    """Reuse a verified map's scene on retry; publish through the same transaction."""
    from studio_temporal import attach_map, validate_resource
    validate_resource(record)
    aid = 'map.'+record['temporal_manifest_sha256']
    stored = session.project['studio']['media'].get(aid)
    if stored is not None and stored != record:
        raise ValueError('El recurso cartográfico inmutable cambió.')
    scene = next((s for s in session.project['studio']['scenes'] if any(
        e.get('style',{}).get('asset_id') == aid and not e.get('editor_deleted') for e in s['elements'])), None)
    candidate = copy.deepcopy(session.project) if scene else attach_map(session.project, record)
    if scene is None: scene = candidate['studio']['scenes'][-1]
    timeline = candidate['studio']['timeline']
    if scene['id'] not in timeline: timeline.append(scene['id'])
    candidate['studio']['timeline'] = [sid for sid in timeline if next(
        s for s in candidate['studio']['scenes'] if s['id'] == sid).get('renderer','studio') == 'studio']
    if candidate != session.project: session.commit(candidate)
    session.state[session.key+'_selected'] = scene['id']
    request_studio_navigation(session.state)


def show_sig(source):
    from studio_workspace import WorkspaceSession
    from studio_sig_map_ui import show_sig_map
    document = st.session_state['project_document']
    key = workspace_key(document)
    session = WorkspaceSession(st.session_state, key, source, canonical=True)
    show_sig_map(session)
