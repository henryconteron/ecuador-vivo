"""Pure authoring commands: scientific registries and legacy artwork are retained."""
import copy
import math
from studio_model import migrate_project, validate_studio
from output_profiles import profile_for
from studio_templates import template_scene,THEMES,TYPOGRAPHY


def new_workspace(project):
    result = migrate_project(project)
    studio = result['studio']
    if any(s.get('renderer', 'studio') == 'studio' for s in studio['scenes']):
        return result
    studio['legacy_timeline'] = list(studio['timeline'])
    profile = {'id': 'tiktok'}
    scene = template_scene('cover', profile_for(profile))
    studio['scenes'].append(scene)
    studio['timeline'] = [scene['id']]
    studio['output_profile'] = profile
    validate_studio(studio)
    return result


def timeline_rows(studio):
    validate_studio(studio)
    return _timeline_rows_validated(studio)


def _timeline_rows_validated(studio):
    """Internal row builder for an already validated private snapshot."""
    scenes = {s['id']: s for s in studio['scenes']}
    rows, start = [], 0
    for sid in studio['timeline']:
        scene = scenes[sid]
        frames = max(1, round(scene['duration']*30))
        rows.append({'id': sid, 'name': scene['name'], 'frames': frames,
                     'seconds': frames/30, 'start_frame': start, 'end_frame': start+frames})
        start += frames
    if start>7200*30: raise ValueError('Timeline cuantizada excede dos horas.')
    return rows


def edit_scene(project, command, scene_id=None, **values):
    result = copy.deepcopy(project)
    studio = result['studio']
    validate_studio(studio)
    scene = next((s for s in studio['scenes'] if s['id'] == scene_id), None)
    if command in ('update', 'duplicate', 'delete') and (not scene or scene.get('renderer', 'studio') != 'studio'):
        raise ValueError('Esta operación requiere una escena libre; las referencias legacy se conservan.')
    if command == 'add':
        fresh = values['scene']
        studio['scenes'].append(copy.deepcopy(fresh))
        studio['timeline'].append(fresh['id'])
    elif command == 'duplicate':
        import uuid
        fresh = copy.deepcopy(scene)
        fresh['id'] = 'scene.'+uuid.uuid4().hex
        fresh['name'] = scene['name']+' · copia'
        if fresh.get('map_instances'):
            mapping={iid:'instance.'+uuid.uuid4().hex for iid in fresh['map_instances']}
            fresh['map_instances']={mapping[iid]:clock for iid,clock in fresh['map_instances'].items()}
            for element in fresh['elements']:
                if element.get('temporal_binding'):element['temporal_binding']['instance_id']=mapping[element['temporal_binding']['instance_id']]
        studio['scenes'].append(fresh)
        studio['timeline'].insert(studio['timeline'].index(scene_id)+1, fresh['id'])
    elif command == 'delete':
        if len(studio['timeline']) == 1:
            raise ValueError('Conserva al menos una escena en la timeline.')
        studio['timeline'].remove(scene_id)
        # Keep the scene for recovery; no assets or source files are deleted.
    elif command == 'update':
        for field in ('name', 'background', 'elements'):
            if field in values: scene[field] = copy.deepcopy(values[field])
        if 'duration' in values:
            duration = values['duration']
            if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not math.isfinite(duration) or not 1/30 <= duration <= 7200:
                raise ValueError('Duración fuera de rango.')
            scene['duration'] = max(1, round(duration*30))/30
    elif command == 'reorder':
        order = values['order']
        if not isinstance(order, list) or len(order) != len(studio['timeline']) or set(order) != set(studio['timeline']):
            raise ValueError('Reordenar debe conservar todas las referencias de la timeline.')
        studio['timeline'] = list(order)
    elif command == 'separate_timeline':
        # Explicit resolution, never a load-time migration: keep every scene
        # and preserve the legacy order for the existing montage route.
        by_id={s['id']:s for s in studio['scenes']}
        legacy=[sid for sid in studio['timeline'] if by_id[sid].get('renderer','studio')!='studio']
        free=[sid for sid in studio['timeline'] if sid not in legacy]
        if legacy:
            previous=studio.setdefault('legacy_timeline',[])
            if not isinstance(previous,list): raise ValueError('Referencia de timeline legacy inválida.')
            previous.extend(sid for sid in legacy if sid not in previous)
        if not free:
            existing=next((s for s in studio['scenes'] if s.get('renderer','studio')=='studio'),None)
            if existing is None:
                existing=template_scene('blank',profile_for(studio['output_profile']))
                studio['scenes'].append(existing)
            free=[existing['id']]
        studio['timeline']=free
    else:
        raise ValueError('Comando de escena desconocido.')
    validate_studio(studio)
    return result


def patch_canvas(project, scene_id, entries):
    from layout_engine import clean_layout
    fields={'x','y','w','h','z','font_size','color','text','name','locked','hidden','deleted'}
    if not isinstance(entries,dict): raise ValueError('Patch de canvas debe ser un objeto.')
    for item in entries.values():
        if not isinstance(item,dict) or set(item)-fields:
            raise ValueError('Cambio de canvas desconocido; no se ignorará.')
        if 'text' in item and (not isinstance(item['text'],str) or len(item['text'])>2000):
            raise ValueError('El texto admite hasta 2000 caracteres sin recorte.')
        for field in ('locked','hidden','deleted'):
            if field in item and type(item[field]) is not bool: raise ValueError('Estado de capa debe ser booleano.')
        for field in ('x','y','w','h','z','font_size'):
            if field in item and (isinstance(item[field],bool) or not isinstance(item[field],(int,float))):
                raise ValueError('Las medidas deben ser números, no strings ni booleanos.')
    cleaned = clean_layout({'map': entries})['map']
    for eid,item in entries.items():
        if 'text' in item: cleaned[eid]['text']=item['text']
    result = copy.deepcopy(project)
    scene = next(s for s in result['studio']['scenes'] if s['id'] == scene_id)
    if scene.get('renderer', 'studio') != 'studio': raise ValueError('Canvas libre requiere escena Studio.')
    by_id = {e['id']: e for e in scene['elements']}
    for eid, patch in cleaned.items():
        if eid not in by_id:
            # Existing canvas add-text is an explicit, safe authoring command.
            if not eid.startswith('custom.') or 'icon' in patch:
                raise ValueError('Elemento ajeno a la escena.')
            from studio_model import Element
            by_id[eid] = Element(id=eid, type='text', style={'text': 'Tu texto', 'font_size': 40}).to_dict()
            scene['elements'].append(by_id[eid])
        element = by_id[eid]
        if element.get('locked'):
            for key, value in patch.items():
                existing = {'x': element['transform'].get('x', 0), 'y': element['transform'].get('y', 0),
                    'w': element['transform'].get('width', 100), 'h': element['transform'].get('height', 100),
                    'z': element.get('z_index', 0), 'hidden': not element.get('visible', True),
                    'deleted': element.get('editor_deleted', False), 'name': element.get('name') or element['type'],
                    'font_size': element.get('style', {}).get('font_size'), 'color': element.get('style', {}).get('color'),
                    'text': element.get('style', {}).get('text')}.get(key)
                if key != 'locked' and value != existing:
                    raise ValueError('Elemento bloqueado; desbloquéalo antes de cambiarlo.')
        transform, style = element.setdefault('transform', {}), element.setdefault('style', {})
        for old, new in (('x','x'), ('y','y'), ('w','width'), ('h','height')):
            if old in patch: transform[new] = patch[old]
        if 'name' in patch: element['name'] = patch['name']
        if 'z' in patch: element['z_index'] = patch['z']
        if 'locked' in patch: element['locked'] = patch['locked']
        if 'deleted' in patch: element['editor_deleted'] = patch['deleted']
        if 'hidden' in patch or 'deleted' in patch:
            element['visible'] = not patch.get('hidden', not element.get('visible', True)) and not element.get('editor_deleted', False)
        if 'font_size' in patch: style['font_size'] = round(patch['font_size'])
        if 'color' in patch: style['color'] = patch['color']
        if 'text' in patch and not element.get('data_binding') and element['type'] in ('text','source'):
            style['text'] = patch['text']
    validate_studio(result['studio'])
    return result


def adapt_profile(project, definition):
    """Explicit author request: reflow template roles, constrain manual objects."""
    from output_profiles import adaptive_regions
    profile=profile_for(definition)
    result=copy.deepcopy(project)
    regions=adaptive_regions(profile)
    roles={'title':'title','source':'source','map.placeholder':'map','body':'map',
           'context':'metric','metric':'metric','ranking':'metric'}
    for scene in result['studio']['scenes']:
        if scene.get('renderer','studio')!='studio': continue
        for element in scene['elements']:
            t=element.setdefault('transform',{})
            role=element.get('layout_role')
            if role in regions:
                t.update({k:round(v) for k,v in regions[role].items()})
            else:
                factor=min(1,profile.width/t.get('width',100),profile.height/t.get('height',100))
                t['width']=max(1,round(t.get('width',100)*factor))
                t['height']=max(1,round(t.get('height',100)*factor))
                t['x']=max(0,min(t.get('x',0),profile.width-t['width']))
                t['y']=max(0,min(t.get('y',0),profile.height-t['height']))
    result['studio']['output_profile']=copy.deepcopy(definition)
    validate_studio(result['studio'])
    return result


def snapshot_revision(snapshot):
    """Keep the existing scientific revision byte contract, including UTF-8 text."""
    import hashlib
    import json
    return hashlib.sha256(json.dumps(snapshot,sort_keys=True,allow_nan=False).encode()).hexdigest()


def attach_snapshot(project, snapshot):
    """Append a scientific revision. Existing bindings keep their exact values."""
    from calculation_results import CalculationResult
    from studio_model import validate_binding
    result=copy.deepcopy(project)
    studio=result['studio']
    identity=snapshot['scientific_identity']
    import re
    if not isinstance(identity,str) or not re.fullmatch(r'[a-f0-9]{64}',identity):
        raise ValueError('Identidad científica inválida.')
    import hashlib
    import json
    revision=snapshot_revision(snapshot)
    for rid,value in snapshot['results'].items():
        identifier='calc.'+revision[:16]+'.'+rid
        validate_binding({'result_id':identifier,'field':'value'})
        payload=copy.deepcopy(value);payload['id']=identifier
        records_id='sources.'+revision
        payload['provenance']['source_records_ref']=records_id
        CalculationResult(payload)
        if identifier in studio['calculations'] and studio['calculations'][identifier]!=payload:
            raise ValueError('La revisión científica cambió: conserva la anterior y carga una identidad nueva.')
        studio['calculations'][identifier]=payload
        records=copy.deepcopy(snapshot['source_records'])
        if records_id in studio['datasets'] and studio['datasets'][records_id]!=records:
            raise ValueError('Las fuentes de una revisión existente no pueden reemplazarse.')
        studio['datasets'][records_id]=records
    validate_studio(studio)
    return result


def duplicate_elements(project, scene_id, ids, *, elements=None,map_instances=None):
    import uuid
    result=copy.deepcopy(project)
    scene=next(s for s in result['studio']['scenes'] if s['id']==scene_id)
    profile=profile_for(result['studio']['output_profile'])
    source=elements if elements is not None else [e for e in scene['elements'] if e['id'] in ids]
    if elements is None and set(ids)-{e['id'] for e in source}: raise ValueError('Selección desconocida.')
    temporal_ids={e['temporal_binding']['instance_id'] for e in source if e.get('temporal_binding')}
    remap={}
    for iid in temporal_ids:
        channels={e['temporal_binding']['channel'] for e in source if e.get('temporal_binding',{}).get('instance_id')==iid}
        if elements is not None or {'continent','galapagos'}<=channels:
            clock=(map_instances or {}).get(iid) if elements is not None else scene.get('map_instances',{}).get(iid)
            if clock is None:raise ValueError('Clipboard cartográfico sin reloj; copia la instancia completa de nuevo.')
            if elements is None:
                source+= [e for e in scene['elements'] if e.get('temporal_binding',{}).get('instance_id')==iid and e not in source]
            if any(e.get('locked') or e.get('editor_deleted') for e in source if e.get('temporal_binding',{}).get('instance_id')==iid):
                raise ValueError('Duplica la instancia cartográfica completa y desbloqueada.')
            remap[iid]='instance.'+uuid.uuid4().hex
            scene.setdefault('map_instances',{})[remap[iid]]=copy.deepcopy(clock)
    selected_ids={e['id'] for e in source}
    groups={e.get('group_id') for e in source if e.get('group_id')}
    if elements is None:
        required=[e for e in scene['elements'] if e.get('group_id') in groups and not e.get('editor_deleted')]
        if any(e['id'] not in selected_ids or e.get('locked') for e in required):
            raise ValueError('Duplica el grupo completo y desbloqueado; no se copiará parcialmente.')
    cloned_groups={}
    group_offsets={}
    for group_id in {e.get('group_id') for e in source if e.get('group_id')}:
        members=[e for e in source if e.get('group_id')==group_id and not e.get('locked') and not e.get('editor_deleted')]
        transforms=[e.get('transform',{}) for e in members]
        group_offsets[group_id]=(max(0,min([10]+[profile.width-t.get('x',0)-t.get('width',100) for t in transforms])),
                                 max(0,min([10]+[profile.height-t.get('y',0)-t.get('height',100) for t in transforms])))
    for element in source:
        if element.get('locked') or element.get('editor_deleted'): continue
        clone=copy.deepcopy(element);clone['id']='element.'+uuid.uuid4().hex
        if clone.get('temporal_binding') and clone['temporal_binding']['instance_id'] in remap:
            clone['temporal_binding']['instance_id']=remap[clone['temporal_binding']['instance_id']]
        if clone.get('group_id'):
            clone['group_id']=cloned_groups.setdefault(clone['group_id'],'group.'+uuid.uuid4().hex)
        clone['name']=(clone.get('name') or clone['type'])+' · copia'
        t=clone.setdefault('transform',{})
        dx,dy=group_offsets.get(element.get('group_id'),(10,10))
        t['x']=max(0,min(t.get('x',0)+dx,profile.width-t.get('width',100)))
        t['y']=max(0,min(t.get('y',0)+dy,profile.height-t.get('height',100)))
        clone['z_index']=min(3800,max((e.get('z_index',0) for e in scene['elements']),default=0)+1)
        clone.pop('layout_role',None)
        scene['elements'].append(clone)
    validate_studio(result['studio'])
    return result


def apply_scene_design(project,scene_id, *, theme=None,typography=None,font_roles=None):
    """Explicit styling only: locked artwork, geometry and science are retained."""
    from studio_typography import FONT_ROLES, validate_family, element_font_role
    if font_roles is not None:
        if not isinstance(font_roles,dict) or set(font_roles)-set(FONT_ROLES):
            raise ValueError('Asignación de roles tipográficos inválida.')
        for family in font_roles.values(): validate_family(family)
    if theme is not None and theme not in THEMES: raise ValueError('Tema desconocido.')
    if typography is not None and typography not in TYPOGRAPHY: raise ValueError('Tipografía desconocida.')
    result=copy.deepcopy(project);studio=result['studio'];validate_studio(studio)
    scene=next((s for s in studio['scenes'] if s['id']==scene_id),None)
    if scene is None or scene.get('renderer','studio')!='studio':
        raise ValueError('El diseño requiere una escena libre; legacy se conserva.')
    if theme is not None:
        background,text,accent=THEMES[theme];scene['background']=background
        scene['theme']=theme;studio['theme']=theme
    for element in scene['elements']:
        if element.get('locked'): continue
        kind=element['type'];style=element.setdefault('style',{})
        if font_roles is not None and kind in ('text','source','metric','ranking','chart'):
            role=element_font_role(element)
            if role in font_roles:
                target=style if kind in ('text','source') else style.setdefault('visualization',{}).setdefault('style',{})
                target['font_family']=font_roles[role]
        if theme is not None:
            if kind in ('text','source'): style['color']=text
            elif kind in ('shape','background'): style['fill']=accent
            elif kind in ('metric','ranking','chart'):
                style.setdefault('visualization',{}).setdefault('style',{}).update(background=background,text=text,color=accent)
        if typography is not None and kind in ('text','source'):
            bold,factor=TYPOGRAPHY[typography]
            previous_name=element.get('typography_preset','Professional')
            if previous_name not in TYPOGRAPHY: previous_name='Professional'
            previous=TYPOGRAPHY[previous_name][1]
            transform=element.get('transform',{})
            size=style.get('font_size',max(10,round(min(transform.get('width',100),transform.get('height',100))*.16)))
            if type(size) is not int or not 8<=size<=400: raise ValueError('Tamaño de fuente fuera de rango.')
            base=element.get('typography_base_size')
            if base is not None and (isinstance(base,bool) or not isinstance(base,(int,float)) or
                    not math.isfinite(base) or not 0<base<=400/min(scale for _,scale in TYPOGRAPHY.values())):
                raise ValueError('Base tipográfica fuera de rango.')
            sizes=element.get('typography_sizes',{})
            if (not isinstance(sizes,dict) or any(name not in TYPOGRAPHY or type(value) is not int or not 8<=value<=400 for name,value in sizes.items())):
                raise ValueError('Contrato de tamaños tipográficos inválido.')
            if base is None or element.get('typography_applied_size')!=size:
                base=size/previous
                sizes={previous_name:size}
            applied=sizes[typography] if typography in sizes else max(8,min(400,round(base*factor)))
            style['font_size']=applied
            weight=bold if element.get('typography_weight','regular' if kind=='source' else 'preset')=='preset' else False
            if 'bold' in style or weight: style['bold']=weight
            element.update(typography_preset=typography,typography_base_size=base,
                typography_applied_size=applied,typography_sizes=sizes)
    validate_studio(studio)
    return result
