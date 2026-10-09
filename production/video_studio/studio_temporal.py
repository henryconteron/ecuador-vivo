"""Verifiable calendar adapter for existing CFR media and scientific datasets."""
import copy
import datetime as dt
import math
import re
from bisect import bisect_right


def _hash(value):
    import hashlib
    import json
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def video_frame_index(time, style, metadata):
    """The single sampling rule used by both decoder and scientific calendar."""
    start, end = style.get('trim_in', 0), style.get('trim_out', metadata['duration'])
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v)
           for v in (start, end)) or not 0 <= start < end <= metadata['duration'] + .001:
        raise ValueError('Trim del video fuera de su duración.')
    loop = style.get('loop', False)
    if type(loop) is not bool: raise ValueError('Loop debe ser booleano.')
    count = max(1, round((end-start)*30))
    index = max(0, math.floor(time*30+1e-7))
    return (index % count if loop else min(index, count-1)) + round(start*30)


def instance_frame(record, instance, frame):
    """Integer instance contract, delegating to the existing single CFR rule."""
    if type(frame) is not int or frame<0:raise ValueError('Fotograma de escena inválido.')
    start,end=instance['trim_in_frame'],instance['trim_out_frame']
    if (type(start) is not int or type(end) is not int or not 0<=start<end<=record['total_frames']
            or type(instance['loop']) is not bool):raise ValueError('Reloj fuera del bundle científico.')
    return video_frame_index(frame/30,{'trim_in':start/30,'trim_out':end/30,'loop':instance['loop']},record)


def bundle_observation(manifest, source_frame, *, starts=None):
    """Verified half-open calendar; source frame has already used the CFR rule."""
    if type(source_frame) is not int or not 0<=source_frame<manifest['total_frames']:
        raise ValueError('Fotograma fuera del calendario científico.')
    starts=starts if starts is not None else [s['start_frame'] for s in manifest['intervals']]
    span=manifest['intervals'][bisect_right(starts,source_frame)-1]
    return {'date':span['date'],'source_index':span['source_index'],'source_frame':source_frame,
            'scientific_revision':manifest['scientific_revision']}


def validate_resource(record):
    manifest = record.get('temporal_map')
    if not isinstance(manifest, dict) or _hash(manifest) != record.get('temporal_manifest_sha256'):
        raise ValueError('El manifiesto cartográfico cambió o está incompleto.')
    total = manifest.get('total_frames')
    if (type(manifest.get('version')) is not int or manifest.get('version') != 1 or manifest.get('fps') != 30 or type(total) is not int
            or not 1 <= total <= 216000 or manifest.get('duration') != total/30
            or record.get('kind') != 'video' or record.get('duration') != total/30
            or manifest.get('video_sha256') != record.get('sha256')
            or manifest.get('resolution') != record.get('size')):
        raise ValueError('Reloj o producto cartográfico incompatible.')
    for key in ('scientific_revision', 'scientific_identity'):
        if not re.fullmatch('[0-9a-f]{64}', str(manifest.get(key))):
            raise ValueError('Identidad científica cartográfica inválida.')
    settings = manifest.get('cartographic_settings')
    if not isinstance(settings,dict) or any(manifest.get(key) != settings.get(key)
            for key in ('source','variable','units')) or manifest.get('region') != settings.get('bbox'):
        raise ValueError('La descripción cartográfica no coincide con los parámetros registrados.')
    if manifest.get('temporal_interpolation') is not False or manifest.get('representation') != 'opaque_prerendered_map':
        raise ValueError('Regla de representación cartográfica incompatible.')
    intervals, records = manifest.get('intervals'), manifest.get('source_records')
    if not isinstance(intervals, list) or not intervals or not isinstance(records, list) or len(intervals) != len(records):
        raise ValueError('Calendario sin correspondencia de fuentes.')
    cursor = 0
    previous = None
    for index, (interval, source) in enumerate(zip(intervals, records)):
        date = dt.date.fromisoformat(interval['date'])
        end = interval['end_frame']
        if (type(end) is not int or type(interval['start_frame']) is not int or interval['start_frame'] != cursor or not cursor < end <= total
                or type(interval['source_index']) is not int or interval['source_index'] != index or source['date'] != interval['date']
                or (previous is not None and date <= previous)
                or not re.fullmatch('[0-9a-f]{64}', str(source.get('sha256')))
                or not isinstance(source.get('file'), str) or type(source.get('band')) is not int or source['band'] < 1):
            raise ValueError('Intervalos, fechas o archivos de origen incoherentes.')
        previous, cursor = date, end
    if cursor != total: raise ValueError('El calendario no cubre todos los fotogramas.')
    return manifest


def validate_maps(project):
    studio = project['studio']
    bundles={}
    for record in studio['media'].values():
        if record.get('kind')=='temporal_map':
            from studio_map_bundles import read_bundle
            manifest=read_bundle(record)
            if 'legend_static' not in manifest.get('auxiliaries',{}):
                raise ValueError('El bundle privado necesita una leyenda verificada antes de publicación.')
            bundles[record['manifest_sha256']]=manifest
        elif 'temporal_map' in record:manifest = validate_resource(record)
        else:continue
        if studio['datasets'].get('sources.' + manifest['scientific_revision']) != manifest['source_records']:
            raise ValueError('El mapa no corresponde a su dataset científico inmutable.')
        # Reconstruct each retained revision from its original registry, including
        # older maps after the current source changes. This is pure JSON, no raster IO.
        from studio_science import restored_snapshot
        restored_snapshot({**project,'project_meta':{**project.get('project_meta',{}),
            'scientific_revision':manifest['scientific_revision'],
            'scientific_identity':manifest['scientific_identity']}})
    for scene in studio['scenes']:
        instances=scene.get('map_instances',{})
        for iid,instance in instances.items():
            record=studio['media'].get(instance['asset_id'],{})
            if record.get('kind')!='temporal_map' or record.get('manifest_sha256') not in bundles:
                raise ValueError('La instancia no corresponde a un bundle científico autorizado.')
            instance_frame(record,instance,0)
            bound=[e for e in scene['elements'] if e.get('temporal_binding',{}).get('instance_id')==iid]
            channels={e['temporal_binding']['channel'] for e in bound}
            if not channels & {'continent','galapagos'} or not {'date','legend_static'}<=channels:
                raise ValueError('La instancia requiere mapa, fecha protegida y leyenda verificada.')
            visible=lambda e:e.get('visible',True) and not e.get('editor_deleted')
            if any(visible(e) and e['type']=='map' for e in bound):
                active={e['temporal_binding']['channel'] for e in bound if visible(e)}
                if not {'date','legend_static'}<=active:
                    raise ValueError('Un mapa visible requiere fecha y leyenda visibles.')
        for element in scene['elements']:
            record = studio['media'].get(element.get('style', {}).get('asset_id'), {})
            if record.get('kind')=='temporal_map':raise ValueError('Un bundle estructurado requiere binding temporal, no asset_id por capa.')
            if 'temporal_map' not in record: continue
            style = element.get('style', {})
            if element['type'] != 'video' or style.get('fit', 'contain') != 'contain':
                raise ValueError('El mapa temporal requiere video y encuadre completo · contain.')
            first = video_frame_index(0, style, record)
            last = video_frame_index((max(1, round((style.get('trim_out', record['duration'])-style.get('trim_in', 0))*30))-1)/30,
                                     style, record)
            if not 0 <= first <= last < record['temporal_map']['total_frames']:
                raise ValueError('El recorte cuantizado excede el calendario científico.')
    used={i['asset_id'] for s in studio['scenes'] for i in s.get('map_instances',{}).values()}
    if any(r.get('kind')=='temporal_map' and aid not in used for aid,r in studio['media'].items()):
        raise ValueError('Los bundles privados requieren bindings y consumidores completos antes de publicación.')


def observation(record, style, frame, *, starts=None):
    """Half-open intervals; non-looping clips hold the final observed date."""
    manifest = record['temporal_map']
    source_frame = video_frame_index(frame/30, style, record)
    return bundle_observation(manifest,source_frame,starts=starts)


def calendar_at(project, frame):
    from studio_editing import timeline_rows
    row = next(r for r in timeline_rows(project['studio']) if r['start_frame'] <= frame < r['end_frame'])
    scene = next(s for s in project['studio']['scenes'] if s['id'] == row['id'])
    result=[{'element_id': e['id'], 'asset_id': e['style']['asset_id'],
             **observation(project['studio']['media'][e['style']['asset_id']], e['style'], frame-row['start_frame'])}
            for e in scene['elements'] if e.get('visible', True) and not e.get('editor_deleted')
            and 'temporal_map' in project['studio']['media'].get(e.get('style', {}).get('asset_id'), {})]
    from studio_map_bundles import read_bundle
    for iid,instance in scene.get('map_instances',{}).items():
        record=project['studio']['media'][instance['asset_id']]
        value=bundle_observation(read_bundle(record,verify_tiles=False),instance_frame(record,instance,frame-row['start_frame']))
        for e in scene['elements']:
            if e.get('temporal_binding',{}).get('instance_id')==iid and e.get('visible',True) and not e.get('editor_deleted'):
                result.append({'element_id':e['id'],'asset_id':instance['asset_id'],'instance_id':iid,
                               'channel':e['temporal_binding']['channel'],**value})
    return result


def instance_spans(manifest,instance,length,offset=0):
    """Intervals/cycles, not a scan per output frame or per visual layer."""
    start,end=instance['trim_in_frame'],instance['trim_out_frame'];count=end-start
    clipped=[{**s,'start_frame':max(start,s['start_frame']),'end_frame':min(end,s['end_frame'])}
             for s in manifest['intervals'] if s['start_frame']<end and start<s['end_frame']]
    result=[];cycle=0
    while cycle<length:
        for span in clipped:
            a=cycle+span['start_frame']-start;b=min(length,cycle+span['end_frame']-start)
            if a>=length:break
            result.append({**bundle_observation(manifest,span['start_frame']),
                           'start_frame':offset+a,'end_frame':offset+b,'source_step':1})
        if not instance['loop']:break
        cycle+=count
    if not instance['loop'] and length>count:
        result.append({**bundle_observation(manifest,end-1),'start_frame':offset+count,
                       'end_frame':offset+length,'source_step':0})
    return result


def calendar_receipt(project, rows):
    """Compact date spans, computed from the same integer clock as decoded frames."""
    result = []
    scenes = {s['id']: s for s in project['studio']['scenes']}
    for row in rows:
        from studio_map_bundles import read_bundle
        scene=scenes[row['id']]
        for iid,instance in scene.get('map_instances',{}).items():
            record=project['studio']['media'][instance['asset_id']];manifest=read_bundle(record,verify_tiles=False)
            result.append({'scene_id':row['id'],'instance_id':iid,'asset_id':instance['asset_id'],'fps':30,
                'manifest_sha256':record['manifest_sha256'],'scientific_identity':manifest['scientific_identity'],
                'scientific_revision':manifest['scientific_revision'],'clock':copy.deepcopy(instance),
                'bindings':[{'element_id':e['id'],'temporal_binding':copy.deepcopy(e['temporal_binding']),
                    'transform':copy.deepcopy(e.get('transform',{})),'visible':e.get('visible',True),
                    'editor_deleted':e.get('editor_deleted',False),'fit':e.get('style',{}).get('fit','contain')}
                    for e in scene['elements'] if e.get('temporal_binding',{}).get('instance_id')==iid],
                'intervals':instance_spans(manifest,instance,row['end_frame']-row['start_frame'],row['start_frame'])})
        for element in scenes[row['id']]['elements']:
            record = project['studio']['media'].get(element.get('style', {}).get('asset_id'), {})
            if 'temporal_map' not in record or not element.get('visible', True) or element.get('editor_deleted'): continue
            spans = []
            previous_frame = None
            starts = [i['start_frame'] for i in record['temporal_map']['intervals']]
            for frame in range(row['end_frame']-row['start_frame']):
                value = observation(record, element['style'], frame, starts=starts)
                global_frame = row['start_frame']+frame
                if (not spans or value['date'] != spans[-1]['date'] or value['source_frame'] < previous_frame):
                    spans.append({**value, 'start_frame': global_frame, 'end_frame': global_frame+1})
                else: spans[-1]['end_frame'] = global_frame+1
                previous_frame = value['source_frame']
            result.append({'scene_id': row['id'], 'element_id': element['id'],
                           'asset_id': element['style']['asset_id'], 'fps': 30, 'intervals': spans})
    return result


def attach_map(project, record):
    """Publish one logical resource and scene; leave every previous scene intact."""
    from studio_science import restored_snapshot
    from studio_preparation import verify_sources
    from studio_model import Scene, Element
    from studio_timeline import PreparedTimeline
    from output_profiles import profile_for
    import uuid
    manifest = validate_resource(record)
    snapshot = restored_snapshot(project)
    if snapshot is None or manifest['scientific_revision'] != project['project_meta'].get('scientific_revision'):
        raise ValueError('El mapa pertenece a otra revisión científica.')
    if manifest['scientific_identity'] != snapshot['scientific_identity'] or manifest['source_records'] != snapshot['source_records']:
        raise ValueError('La procedencia del mapa no coincide con la revisión científica.')
    verify_sources(project, snapshot)
    result = copy.deepcopy(project)
    studio = result['studio']
    aid = 'map.' + record['temporal_manifest_sha256']
    if aid in studio['media'] and studio['media'][aid] != record:
        raise ValueError('No se puede sustituir un recurso científico inmutable.')
    studio['media'][aid] = copy.deepcopy(record)
    profile = profile_for(studio['output_profile'])
    scene = Scene(id='scene.'+uuid.uuid4().hex, name=record['name'][:180], duration=record['duration'],
                  elements=[Element(id='element.'+uuid.uuid4().hex, type='video', name='Mapa temporal verificable',
                      transform={'x':0,'y':0,'width':profile.width,'height':profile.height},
                      style={'asset_id':aid,'fit':'contain','trim_in':0,'loop':False,'mute':True}).to_dict()]).to_dict()
    studio['scenes'].append(scene); studio['timeline'].append(scene['id'])
    PreparedTimeline(result)
    return result


def review_map_layers(project, record):
    """Review sealed bytes and the retained scientific revision, without computing."""
    from studio_map_bundles import read_bundle
    from studio_science import restored_snapshot
    from studio_preparation import verify_sources
    manifest=read_bundle(record)
    if 'legend_static' not in manifest.get('auxiliaries',{}):
        raise ValueError('Este recurso antiguo no incluye una leyenda completa. Prepara explícitamente un nuevo mapa de capas; el original se conserva.')
    if project['studio']['datasets'].get(record['source_dataset'])!=manifest['source_records']:
        raise ValueError('Faltan las fuentes de esta revisión en el proyecto. Abre el proyecto que contiene su revisión científica.')
    snapshot=restored_snapshot({**project,'project_meta':{**project.get('project_meta',{}),
        'scientific_revision':manifest['scientific_revision'],'scientific_identity':manifest['scientific_identity']}})
    verify_sources(manifest['cartographic_settings'],snapshot)
    return manifest


def attach_map_layers(project, record, *, base_sha256=None):
    """One complete new scene; the caller durably commits only the validated result."""
    from studio_model import Scene,Element
    from studio_timeline import PreparedTimeline
    from studio_templates import THEMES
    from output_profiles import profile_for,adaptive_regions,contain_bounds
    import uuid
    if base_sha256 is not None and _hash(project)!=base_sha256:
        raise ValueError('El proyecto cambió durante la revisión. Cierra y revisa el recurso otra vez.')
    manifest=review_map_layers(project,record)
    result=copy.deepcopy(project);studio=result['studio']
    matches=[aid for aid,r in studio['media'].items() if r.get('manifest_sha256')==record['manifest_sha256']]
    aid=matches[0] if matches else 'map.'+record['manifest_sha256']
    if aid in studio['media'] and studio['media'][aid]!=record:
        raise ValueError('No se puede sustituir un recurso científico inmutable.')
    studio['media'][aid]=copy.deepcopy(record)
    profile=profile_for(studio['output_profile']);regions=adaptive_regions(profile)
    map_box=regions['map'];side=regions['metric'];gap=max(2,min(profile.width,profile.height)*.015)
    mainland={**map_box,'width':map_box['width']*.72}
    inset={'x':map_box['x']+mainland['width']+gap,'y':map_box['y'],
           'width':max(1,map_box['width']-mainland['width']-gap),'height':map_box['height']*.4}
    date_h=min(60,max(20,side['height']*.18))
    legend={'x':side['x'],'y':side['y']+date_h+gap,'width':side['width'],
            'height':max(1,side['height']-date_h-gap)}
    iid='instance.'+uuid.uuid4().hex;elements=[]
    background,ink,_=THEMES[studio.get('theme','Ecuador Vivo')]
    def add(kind,name,box,style,channel=None):
        elements.append(Element(id='element.'+uuid.uuid4().hex,type=kind,name=name,
            transform=box,style=style,z_index=len(elements),
            temporal_binding={'instance_id':iid,'channel':channel} if channel else None).to_dict())
    add('map','Ecuador continental',contain_bounds(record['layers']['continent']['size'],mainland),{'fit':'contain'},'continent')
    add('map','Galápagos',contain_bounds(record['layers']['galapagos']['size'],inset),{'fit':'contain'},'galapagos')
    add('text','Fecha observada',{**side,'height':date_h},
        {'font_size':max(8,min(40,round(date_h*.5))),'color':ink},'date')
    add('shape','Fondo de leyenda',legend,{'fill':'#04151e','shape':'rectangle'})
    add('legend','Leyenda verificada',legend,{'fit':'contain'},'legend_static')
    add('text','Variable y unidades',regions['title'],
        {'text':manifest['variable']+(' · '+manifest['units'] if manifest['units'] else ''),
         'font_size':max(8,min(48,round(regions['title']['height']*.5))),'color':ink})
    add('source','Fuente',regions['source'],
        {'text':manifest['citation'] or manifest['source'],
         'font_size':max(8,min(24,round(regions['source']['height']*.4))),'color':ink})
    scene=Scene(id='scene.'+uuid.uuid4().hex,name=record['name'][:180],duration=record['duration'],
        background=background,elements=elements,map_instances={iid:{'asset_id':aid,
            'trim_in_frame':0,'trim_out_frame':record['total_frames'],'loop':False}}).to_dict()
    studio['scenes'].append(scene);studio['timeline'].append(scene['id'])
    PreparedTimeline(result)
    return result
