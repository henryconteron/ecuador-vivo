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
    from studio_scientific_ui import show_scientific_assistant
    document = st.session_state['project_document']
    key = workspace_key(document)
    session = WorkspaceSession(st.session_state, key, source, canonical=True)
    st.title('Ecuador Vivo · SIG')
    st.caption('Preparación geográfica y resultados científicos · mismo proyecto que Studio')
    with st.container(horizontal=True):
        if st.button('Inicio', key='sig_home'):
            st.session_state['section'] = 'Inicio'; st.rerun()
        if st.button('Abrir Studio', key='sig_studio', icon=':material/movie:'):
            request_studio_navigation(st.session_state); st.rerun()
    st.write('**Proyecto activo:** '+str(session.project.get('name','Proyecto sin título')))
    st.info('GeoJSON propio: polígonos 2D con vista guardada y envío a Studio. GeoTIFF/resultados científicos: recorrido actual de Ecuador. Tabla SIG, reproyección y estadísticas para regiones arbitrarias siguen pendientes. BYOD: usa recursos autorizados; no se empaquetan automáticamente para distribución.')
    from studio_geographic_ui import show_geography
    show_geography(session)
    snapshot = restored_snapshot(session.project)
    if snapshot:
        st.subheader('Revisión disponible en el proyecto')
        st.caption(str(session.project.get('citation',''))+' · '+str(session.project.get('start',''))+' → '+str(session.project.get('end','')))
        st.dataframe([{'Resultado':rid,'Variable':r['variable'],'Unidad':r['units'],
            'Valor':r.get('value'),'Filas':len(r.get('rows',[]))} for rid,r in snapshot['results'].items()],
            hide_index=True, alt='Resultados científicos de la revisión compartida')
        with st.expander('Fechas, archivos y procedencia'):
            st.dataframe(snapshot['source_records'], hide_index=True, alt='Fechas, bandas y hashes de origen')
        if st.button('Preparar mapa temporal', key='sig_prepare_map', icon=':material/map:'):
            st.session_state[key+'_dialog'] = 'temporal_map'; st.rerun()
    maps = {aid:r for aid,r in session.project['studio']['media'].items() if 'temporal_map' in r}
    if maps:
        from studio_media import AssetFrames
        from studio_temporal import observation
        aid = st.selectbox('Mapas del proyecto', list(maps), format_func=lambda k:maps[k]['name'], key='sig_map_view', persist_state='session')
        record = maps[aid]
        frame = st.slider('Fotograma del mapa', 0, record['temporal_map']['total_frames']-1, 0,
                          key='sig_map_frame_'+record['temporal_manifest_sha256'][:16]) if record['temporal_map']['total_frames'] > 1 else 0
        current = observation(record, {}, frame)
        st.caption('Fecha observada: '+current['date']+' · '+record['temporal_map']['citation']+' · '+record['temporal_map']['units'])
        with AssetFrames({aid:record},cache=session.cache.media) as assets:
            image = assets.at(frame/30,[{'id':'sig.preview','type':'video','style':{'asset_id':aid}}])['video.sig.preview']
            st.image(image, width=360, alt='Mapa temporal verificado de la fecha observada')
        st.caption('Recurso 4a opaco: inset y overlays incrustados; capas RGBA editables todavía pendientes.')
        if st.button('Enviar mapa a Studio', key='sig_send_map', type='primary'):
            send_map(session,record); st.rerun()
    def accept(proposal):
        candidate, selected = merge_scientific_proposal(session.project, proposal)
        if candidate != session.project: session.commit(candidate)
        st.session_state[key+'_selected'] = selected
    with st.expander('Preparar datos y enviar resultados a Studio', expanded=snapshot is None):
        st.caption('El envío conserva las escenas Studio existentes. El montaje anterior permanece archivado en el documento. Elige el formato actual del proyecto; los archivos locales siguen siendo necesarios al reabrir.')
        show_scientific_assistant(session.project, accept, publish_label='Enviar resultados a Studio',
                                  shared_profile=session.project['studio']['output_profile'])
    if st.session_state.get(key+'_dialog') == 'temporal_map':
        from studio_map_ui import show_map_dialog
        st.subheader('Mapa temporal · preparación y revisión')
        show_map_dialog(session,key,publish_label='Enviar mapa a Studio',publisher=lambda record:send_map(session,record))
