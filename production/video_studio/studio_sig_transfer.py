"""One existing SIG action -> sealed map, native results, editable Studio scenes."""
import copy,hashlib,json
from studio_sig_layers import workspace_for
from studio_map_bundles import prepare_geographic_bundle,read_bundle
from studio_sig_summary import rainfall_contract,summarize_series
from studio_templates import rainfall_scenes
from studio_territory import options_for,boundaries


def science_inputs(project):
    state=workspace_for(project);time=state.get('raster_time')
    if not time:raise ValueError('Prepara primero el periodo y la secuencia temporal en SIG.')
    sources=[project['studio']['geography']['sources'][state['layers'][lid]['source_id']] for lid in time['layers']]
    rainfall_contract(sources)
    payload=[[(s['sha256'],s['date'],s['units'],s['semantics'],s['raster'],s['provenance']) for s in sources],
             time.get('cadence'),options_for(project)['territory'],boundaries()[1],'native_sig_summary_v4']
    return sources,hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def validate_transfer(project):
    transfer=project['studio'].get('sig_transfer')
    if not transfer:return
    active=set(project['studio']['timeline'])
    if not any(s['id'] in active and s.get('rainfall_template') for s in project['studio']['scenes']):return
    # A new SIG selection is a new preparation, not a mutation of the already
    # sealed Studio movie. Validate that movie against ITS originals/calendar,
    # otherwise changing from rain to temperature cannot even be committed.
    record=project['studio']['media'].get(transfer['asset_id'])
    if record is None:raise ValueError('Falta el mapa de los resultados vinculados.')
    manifest=read_bundle(record,verify_tiles=False);binding=manifest['geographic_binding']
    registry=project['studio'].get('geography',{}).get('sources',{})
    try:sources=[registry[e['id']] for e in binding['sources']]
    except KeyError as error:raise ValueError('Faltan originales de la serie ya enviada a Studio; no se sustituyeron por la selección actual.') from error
    rainfall_contract(sources)
    payload=[[(s['sha256'],s['date'],s['units'],s['semantics'],s['raster'],s['provenance']) for s in sources],
             binding.get('cadence'),binding.get('presentation',{}).get('territory'),boundaries()[1],'native_sig_summary_v4']
    identity=hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    if identity!=transfer['science_inputs']:
        raise ValueError('Los originales, intervalos o método del video enviado cambiaron. Actualiza sus resultados antes de exportar; la selección nueva del SIG no sustituye el video existente.')


def transfer_series(project,*,endcard_duration=5.):
    state=workspace_for(project);time=state.get('raster_time')
    if not time:raise ValueError('Prepara primero el periodo y la secuencia temporal en SIG.')
    sources=[project['studio'].get('geography',{}).get('sources',{})[state['layers'][lid]['source_id']] for lid in time['layers']]
    try:rainfall_contract(sources);rainfall=True
    except ValueError:rainfall=False
    if not rainfall or time.get('cadence')!='daily' or options_for(project)['territory']!='ecuador':
        return transfer_map_series(project)
    sources,science_identity=science_inputs(project)
    if options_for(project)['territory']!='ecuador':
        raise ValueError('La plantilla nacional requiere Ecuador continental + Galápagos; la vista SIG puede seguir navegando libremente.')
    candidate=copy.deepcopy(project);studio=candidate['studio'];time=studio['geography']['map_workspace']['raster_time']
    time['template']='rainfall'
    previous=studio.get('sig_transfer',{})
    # Reuse scientific results when only composition/presentation changes.
    if previous.get('science_inputs')==science_identity:
        snapshot=copy.deepcopy(studio['datasets'][previous['science_dataset']])
    else:snapshot=None
    map_identity=hashlib.sha256(json.dumps([science_identity,time['duration'],options_for(candidate),
                    studio['output_profile'],time.get('palette'),[workspace_for(candidate)['layers'][lid]['style']['opacity'] for lid in time['layers']]],sort_keys=True).encode()).hexdigest()
    if previous.get('map_inputs')==map_identity:
        record=studio['media'][previous['asset_id']];manifest=read_bundle(record)
    else:
        record=prepare_geographic_bundle(candidate,time['duration']);manifest=read_bundle(record)
    if snapshot is None:snapshot=summarize_series(sources,manifest['geographic_binding']['inset_sources'],cadence=time['cadence'])
    aid='map.'+record['manifest_sha256'];studio['media'][aid]=record
    studio['datasets'][record['source_dataset']]=copy.deepcopy(manifest['source_records'])
    dataset='science.'+snapshot['identity'];studio['datasets'][dataset]=copy.deepcopy(snapshot)
    studio['datasets']['sources.'+snapshot['identity']]=copy.deepcopy(snapshot['source_records'])
    for result in snapshot['results'].values():
        prior=studio['calculations'].get(result['id'])
        if prior is not None and prior!=result:raise ValueError('La revisión científica inmutable cambió; se requiere otra identidad.')
        studio['calculations'][result['id']]=copy.deepcopy(result)
    scenes=rainfall_scenes(candidate,record,manifest,snapshot,endcard_duration=endcard_duration)
    ids=[]
    for fresh in scenes:
        old=next((s for s in studio['scenes'] if s.get('rainfall_template')==fresh['rainfall_template']),None)
        if old:
            fresh['id']=old['id'];fresh['duration']=old['duration'] if fresh['rainfall_template']=='endcard' else record['duration']
            by_key={e.get('template_key'):e for e in old['elements'] if e.get('template_key')}
            for element in fresh['elements']:
                edited=by_key.get(element.get('template_key'))
                if not edited:continue
                element.update({k:copy.deepcopy(edited[k]) for k in ('id','transform','visible','locked','editor_deleted','group_id') if k in edited})
                for key,value in edited['style'].items():
                    if key in ('asset_id','opacity'):continue
                    if key=='text' and value==edited.get('template_default_text'):continue
                    element['style'][key]=copy.deepcopy(value)
            fresh['elements'] += [copy.deepcopy(e) for e in old['elements'] if not e.get('template_key')]
            studio['scenes'][studio['scenes'].index(old)]=fresh
        else:studio['scenes'].append(fresh)
        ids.append(fresh['id'])
    # Preserve other authored scenes; update the generated pair in place.
    previous_map_ids=set(studio.get('sig_map_transfer',{}).get('scene_ids',[]))
    studio['timeline']=[i for i in studio['timeline'] if i not in previous_map_ids]
    if not all(i in studio['timeline'] for i in ids):
        empty={s['id'] for s in studio['scenes'] if not s.get('elements') and s.get('renderer','studio')=='studio'}
        studio['timeline']=[i for i in studio['timeline'] if i not in ids and i not in empty]+ids
    studio['sig_transfer']={'science_inputs':science_identity,'map_inputs':map_identity,'asset_id':aid,
        'science_dataset':dataset,'scene_ids':ids,'results':[r['id'] for r in snapshot['results'].values()]}
    from studio_timeline import PreparedTimeline
    PreparedTimeline(candidate)
    return candidate


def transfer_map_series(project):
    """Generic numeric series: editable map/date/legend, NOT rainfall statistics.

    Explicit Send replaces the previous generated output on the timeline while
    preserving its scene graph, native sources and all other authored scenes.
    """
    candidate=copy.deepcopy(project);studio=candidate['studio']
    time=studio['geography']['map_workspace']['raster_time'];time.pop('template',None)
    from studio_sig_raster import settings,verify_source,verify_series_binding
    sources=[studio['geography']['sources'][workspace_for(candidate)['layers'][lid]['source_id']] for lid in time['layers']]
    for source in sources:verify_source(source)
    identity=hashlib.sha256(json.dumps([sources,time.get('duration',3.),time.get('cadence'),options_for(candidate),
        studio['output_profile'],settings(sources,palette=time.get('palette')),boundaries()[1],
        [workspace_for(candidate)['layers'][lid]['style']['opacity'] for lid in time['layers']],
        'social-map-v1'],sort_keys=True).encode()).hexdigest()
    previous=studio.get('sig_map_transfer',{})
    if previous.get('map_inputs')==identity:
        record=studio['media'][previous['asset_id']]
        manifest=read_bundle(record,verify_tiles=False);verify_series_binding(candidate,manifest)
    else:
        record=prepare_geographic_bundle(candidate,time.get('duration',3.))
        manifest=read_bundle(record,verify_tiles=False)
    old_ids=set(studio.get('sig_transfer',{}).get('scene_ids',[]))|set(studio.get('sig_map_transfer',{}).get('scene_ids',[]))
    empty_ids={s['id'] for s in studio['scenes'] if not s.get('elements') and s.get('renderer','studio')=='studio'}
    studio['timeline']=[i for i in studio['timeline'] if i not in old_ids|empty_ids]
    aid='map.'+record['manifest_sha256'];studio['media'][aid]=record
    studio['datasets'][record['source_dataset']]=copy.deepcopy(manifest['source_records'])
    from output_profiles import profile_for
    profile=profile_for(studio['output_profile'])
    if min(profile.width,profile.height)<270:
        # Tiny custom/diagnostic outputs cannot hold the social poster's type.
        # Keep the existing compact map layout rather than clipping its credit.
        from studio_temporal import attach_map_layers
        candidate=attach_map_layers(candidate,record);studio=candidate['studio']
        studio['sig_map_transfer']={'asset_id':aid,'map_inputs':identity,'scene_ids':[studio['timeline'][-1]],
            'note':'Serie compacta; fuentes y unidades conservadas.'}
        return candidate
    from studio_social_template import scenes
    fresh=scenes(candidate,record,manifest)
    old=next((s for s in studio['scenes'] if s['id'] in previous.get('scene_ids',[]) and s.get('series_template')=='map'),None)
    if old:
        fresh['id']=old['id']
        by_key={e.get('template_key'):e for e in old['elements'] if e.get('template_key')}
        for element in fresh['elements']:
            edited=by_key.get(element.get('template_key'))
            if not edited:continue
            element.update({k:copy.deepcopy(edited[k]) for k in ('id','transform','visible','locked','editor_deleted','group_id') if k in edited})
            for key,value in edited['style'].items():
                if key in ('asset_id','opacity') or key=='text' and value==edited.get('template_default_text'):continue
                element['style'][key]=copy.deepcopy(value)
        fresh['elements'] += [copy.deepcopy(e) for e in old['elements'] if not e.get('template_key')]
        studio['scenes'][studio['scenes'].index(old)]=fresh
    else:studio['scenes'].append(fresh)
    studio['timeline'].append(fresh['id'])
    studio['sig_map_transfer']={'asset_id':aid,'map_inputs':identity,'scene_ids':[fresh['id']],
        'note':'Serie de mapas; sin agregación ni métricas de otra variable.'}
    from studio_timeline import PreparedTimeline
    PreparedTimeline(candidate)
    return candidate


def reflow_rainfall(scene,studio,profile):
    transfer=studio.get('sig_transfer')
    if not transfer or not scene.get('rainfall_template'):return set()
    candidate={'studio':{**studio,'output_profile':{'id':profile.id,**({'width':profile.width,'height':profile.height} if profile.id=='custom' else {})}}}
    record=studio['media'][transfer['asset_id']];manifest=read_bundle(record,verify_tiles=False)
    fresh=next(s for s in rainfall_scenes(candidate,record,manifest,studio['datasets'][transfer['science_dataset']]) if s['rainfall_template']==scene['rainfall_template'])
    boxes={e['template_key']:e['transform'] for e in fresh['elements']}
    changed=set()
    for element in scene['elements']:
        if element.get('template_key') in boxes:
            element['transform'].update(boxes[element['template_key']]);changed.add(element['id'])
    return changed
