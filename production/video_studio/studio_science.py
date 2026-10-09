"""Editable scene proposals from existing CalculationResult revisions.

Only presentation is generated here. No provider, raster/statistical pipeline
or interpretation is duplicated. A proposal never mutates the live document.
"""
import copy
import hashlib
import json
import uuid
from collections import Counter
from studio_editing import attach_snapshot, new_workspace, snapshot_revision
from studio_project import replace_document
from studio_templates import template_scene, TEMPLATE_BINDINGS
from studio_timeline import PreparedTimeline
from output_profiles import profile_for


def _hash(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,allow_nan=False).encode('utf-8')).hexdigest()


def result_display_name(identifier, result):
    """Editorial meaning of existing indicators, without changing stored results."""
    key=identifier.rsplit('.',1)[-1]
    labels={'mean_period':'Media del período', 'peak_pixel_value':'Máximo de píxel',
            'minimum_pixel_value':'Mínimo de píxel', 'peak_date_mean':'Máximo de medias por fecha',
            'province_rank':'Resumen provincial'}
    if key=='peak_month_value':
        provenance=result.get('provenance',{})
        period=provenance.get('period_kind','month')
        labels[key]='Máximo de agregados · '+{'month':'mes','year':'año','quarter':'trimestre'}.get(period,str(period))
    return result['variable']+' · '+labels.get(key,key)


def _mark(scene, revision, role, template):
    scene['generation']={'scientific_revision':revision,'role':role,'template':template,
                         'initial_content_sha256':_hash(scene)}
    return scene


def restored_snapshot(project):
    """Recover the exact factory snapshot from its immutable stored registries."""
    meta = project.get('project_meta', {})
    revision, identity = meta.get('scientific_revision'), meta.get('scientific_identity')
    if not revision or not identity: return None
    studio = project['studio']
    records = studio['datasets'].get('sources.' + revision)
    if records is None: raise ValueError('Faltan fuentes de la revisión científica.')
    prefix = 'calc.' + revision[:16] + '.'
    results = {}
    for identifier, stored in studio['calculations'].items():
        if not identifier.startswith(prefix): continue
        original = copy.deepcopy(stored)
        rid = identifier[len(prefix):]
        original['id'] = rid
        # summary_results names its receipt field "source_records". Attachment
        # replaces that pointer with the canonical dataset id, not a new value.
        original['provenance']['source_records_ref'] = 'source_records'
        results[rid] = original
    snapshot = {'results':results,'source_records':copy.deepcopy(records),'scientific_identity':identity}
    if snapshot_revision(snapshot) != revision:
        # Older/custom fixtures omitted that receipt pointer. Accept only when
        # the entire original snapshot's exact revision is recovered.
        for result in results.values(): result['provenance'].pop('source_records_ref',None)
        if snapshot_revision(snapshot) != revision:
            raise ValueError('La revisión almacenada cambió; no se puede regenerar automáticamente.')
    return snapshot


def generate_scientific_project(source, snapshot, profile, *, theme='Ecuador Vivo', title=None):
    result=attach_snapshot(new_workspace(source),snapshot)
    result['studio']['output_profile']=copy.deepcopy(profile)
    result['studio']['theme']=theme
    output=profile_for(profile)
    revision=snapshot_revision(snapshot)
    registry=result['studio']['calculations']
    ids=['calc.'+revision[:16]+'.'+rid for rid in snapshot['results']]
    scalars=[rid for rid in ids if 'rows' not in registry[rid] and registry[rid].get('value') is not None]
    tables=[rid for rid in ids if any(row.get('value') is not None for row in registry[rid].get('rows',[]))]
    citation=str(source.get('citation') or 'Consultar procedencia de los resultados')
    period=str(source.get('start',''))+' a '+str(source.get('end',''))
    credit=citation+' · '+period
    scenes=[]

    def make(template,role,bindings=None):
        scene=template_scene(template,output,theme=theme,bindings=bindings)
        for element in scene['elements']:
            if element['type']=='source': element['style']['text']=credit
        scenes.append(scene)
        return scene

    cover=make('cover','cover')
    for element in cover['elements']:
        if element['id']=='title':element['style']['text']=title or str(source.get('title') or 'Resultados científicos')
        if element['id']=='body':element['style']['text']=str(source.get('variable','Resultados'))+' · '+period
    _mark(cover,revision,'cover','cover')
    for rid in scalars:
        scene=make('metric_focus','metric',{'metric':{'result_id':rid,'field':'value'}})
        scene['name']=registry[rid]['variable']+' · '+rid.rsplit('.',1)[-1]
        label=result_display_name(rid,registry[rid])
        next(e for e in scene['elements'] if e['id']=='title')['style']['text']=label
        next(e for e in scene['elements'] if e['type']=='metric')['style']['visualization']['style']['title']=label
        _mark(scene,revision,'metric','metric_focus')
    for rid in tables:
        scene=make('ranking_focus','chart',{'ranking':{'result_id':rid,'field':'rows'}})
        scene['name']=registry[rid]['variable']+' · gráfico'
        element=next(e for e in scene['elements'] if e.get('data_binding'))
        element['type']='chart';element['style']['visualization']['kind']='horizontal_bar'
        next(e for e in scene['elements'] if e['id']=='title')['style']['text']=registry[rid]['variable']
        _mark(scene,revision,'chart','ranking_focus')
    closing=make('closing','credits')
    next(e for e in closing['elements'] if e['id']=='title')['style']['text']='Fuentes y metodología'
    next(e for e in closing['elements'] if e['id']=='body')['style']['text']='Revisa las fuentes y añade tu explicación editorial respaldada por los datos.'
    _mark(closing,revision,'credits','closing')
    # Preserve previous scenes as recoverable resources; creation opens a copy.
    result['studio']['scenes'].extend(scenes)
    result['studio']['timeline']=[s['id'] for s in scenes]
    result['project_meta']={**result.get('project_meta',{}),'mode':'scientific',
                           'scientific_revision':revision,'scientific_identity':snapshot['scientific_identity']}
    result=replace_document({},result)
    PreparedTimeline(result)
    return result


def propose_template(project, scene_id, template):
    before=next((s for s in project['studio']['scenes'] if s['id']==scene_id),None)
    if before is None or before.get('renderer','studio')!='studio':raise ValueError('Selecciona una escena Studio.')
    bound=[copy.deepcopy(e) for e in before['elements'] if e.get('data_binding')]
    bindings={}
    if template in TEMPLATE_BINDINGS:
        role,field=TEMPLATE_BINDINGS[template]
        from studio_templates import template_result_ids
        eligible=template_result_ids(template,project['studio']['calculations'])
        selected=next((e for e in bound if e['data_binding']['field']==field and e['data_binding']['result_id'] in eligible),None)
        if selected is None:raise ValueError('La plantilla requiere un binding compatible de la escena.')
        bindings[role]=selected['data_binding']
    after=template_scene(template,profile_for(project['studio']['output_profile']),
                         theme=project['studio'].get('theme','Ecuador Vivo'),bindings=bindings)
    after['id']=before['id'];after['duration']=before['duration']
    # Keep each scientific binding, including those a target template cannot place.
    retained=Counter((e['data_binding']['result_id'],e['data_binding']['field']) for e in after['elements'] if e.get('data_binding'))
    for element in bound:
        key=(element['data_binding']['result_id'],element['data_binding']['field'])
        if retained[key]:retained[key]-=1
        else:
            if element['id'] in {e['id'] for e in after['elements']}:
                element['id']='element.'+uuid.uuid4().hex
            after['elements'].append(element)
    original_credit=next((e['style'].get('text') for e in before['elements'] if e['type']=='source'),None)
    if original_credit is not None:
        for element in after['elements']:
            if element['type']=='source':element['style']['text']=original_credit
    revision=before.get('generation',{}).get('scientific_revision',project.get('project_meta',{}).get('scientific_revision'))
    _mark(after,revision,'regenerated',template)
    changes=[]
    for field in ('name','background','elements'):
        if before.get(field)!=after.get(field):
            changes.append({'property':field,'before':copy.deepcopy(before.get(field)), 'after':copy.deepcopy(after.get(field))})
    return {'base_sha256':_hash(project),'scene_id':scene_id,'before':copy.deepcopy(before),'after':after,'changes':changes}


def apply_proposal(project, proposal, choice):
    if choice not in ('preserve','replace'):raise ValueError('Elige conservar o regenerar explícitamente.')
    if proposal.get('base_sha256')!=_hash(project):raise ValueError('El documento cambió; prepara una propuesta nueva.')
    result=copy.deepcopy(project)
    if choice=='preserve':return result
    index=next((i for i,s in enumerate(result['studio']['scenes']) if s['id']==proposal['scene_id']),None)
    if index is None or result['studio']['scenes'][index]!=proposal['before']:raise ValueError('La escena cambió.')
    def bindings(scene):
        return Counter((e['data_binding']['result_id'],e['data_binding']['field']) for e in scene['elements'] if e.get('data_binding'))
    if bindings(proposal['before'])!=bindings(proposal['after']):
        raise ValueError('La propuesta debe conservar todos los bindings científicos.')
    archived=copy.deepcopy(proposal['before']);archived['id']='scene.'+uuid.uuid4().hex
    archived['name']=(archived.get('name','Escena')[:155]+' · versión anterior')
    result['studio']['scenes'].append(archived)
    result['studio']['scenes'][index]=copy.deepcopy(proposal['after'])
    PreparedTimeline(result)
    return result


def _structure_slot(scene):
    bindings = sorted((e['data_binding']['result_id'],e['data_binding']['field'])
                      for e in scene['elements'] if e.get('data_binding'))
    return ('bindings',tuple(bindings)) if bindings else ('role',scene.get('generation',{}).get('role'))


def propose_structure(project, *, theme=None):
    snapshot = restored_snapshot(project)
    if not snapshot: raise ValueError('Este proyecto no tiene una revisión científica generada.')
    from visualization_ui import scientific_identity
    if scientific_identity(project) != snapshot['scientific_identity']:
        raise ValueError('Cambió la fuente o el período del documento; usa la revisión original o prepara un proyecto con la nueva revisión.')
    generated = generate_scientific_project(project,snapshot,project['studio']['output_profile'],
        theme=theme or project['studio'].get('theme','Ecuador Vivo'))
    new_ids = set(generated['studio']['timeline'])
    scenes = [copy.deepcopy(s) for s in generated['studio']['scenes'] if s['id'] in new_ids]
    by_slot = {_structure_slot(s):s for s in scenes}
    changes = []
    original = {s['id']:s for s in project['studio']['scenes']}
    for identifier in project['studio']['timeline']:
        before = original[identifier]
        after = by_slot.pop(_structure_slot(before),None) if before.get('generation') else None
        if after:
            after['duration'] = before['duration']
            after['generation']['initial_content_sha256'] = _hash({k:v for k,v in after.items() if k!='generation'})
        initial = before.get('generation',{}).get('initial_content_sha256')
        modified = initial != _hash({k:v for k,v in before.items() if k!='generation'})
        changes.append({'id':identifier,'name':before.get('name','Escena'),'modified':modified,
            'replacement_id':after['id'] if after else None,
            'before':copy.deepcopy(before),'after':copy.deepcopy(after)})
    after = {'scenes':scenes,'timeline':[s['id'] for s in scenes],
             'theme':theme or project['studio'].get('theme','Ecuador Vivo')}
    return {'base_sha256':_hash(project),'before_timeline':copy.deepcopy(project['studio']['timeline']),
            'after':after,'after_sha256':_hash(after),'changes':changes}


def apply_structure(project, proposal, choice, *, preserve_ids=()):
    if choice not in ('preserve','replace'): raise ValueError('Elige conservar o regenerar explícitamente.')
    if proposal.get('base_sha256') != _hash(project): raise ValueError('El documento cambió; prepara otra propuesta.')
    if choice == 'preserve': return copy.deepcopy(project)
    if _hash(proposal['after']) != proposal.get('after_sha256'): raise ValueError('La propuesta de estructura cambió.')
    if len(set(preserve_ids)) != len(preserve_ids) or set(preserve_ids)-set(project['studio']['timeline']):
        raise ValueError('Escenas a conservar inválidas.')
    result = copy.deepcopy(project)
    new_scenes = proposal['after']['scenes']
    existing = {s['id'] for s in result['studio']['scenes']}
    if any(s['id'] in existing for s in new_scenes): raise ValueError('Identidad de escena repetida.')
    pending = list(proposal['after']['timeline']); timeline = []
    for change in proposal['changes']:
        replacement = change['replacement_id']
        if change['id'] in preserve_ids:
            timeline.append(change['id'])
            if replacement in pending: pending.remove(replacement)
        elif replacement in pending:
            timeline.append(replacement); pending.remove(replacement)
    timeline.extend(pending)
    history = result['studio'].setdefault('structure_history',[])
    history.append({'timeline':copy.deepcopy(result['studio']['timeline']),
                    'scientific_revision':result['project_meta']['scientific_revision']})
    del history[:-20]
    result['studio']['scenes'].extend(copy.deepcopy(new_scenes))
    result['studio']['timeline'] = timeline
    result['studio']['theme'] = proposal['after']['theme']
    PreparedTimeline(result)
    return result


def restore_structure(project, index=-1):
    result = copy.deepcopy(project)
    history = result['studio'].get('structure_history',[])
    if not history: raise ValueError('No hay estructura anterior guardada.')
    previous = history[index]['timeline']
    if not previous or len(set(previous))!=len(previous): raise ValueError('Estructura anterior inválida.')
    history.append({'timeline':copy.deepcopy(result['studio']['timeline']),
                    'scientific_revision':result['project_meta']['scientific_revision']})
    del history[:-20]
    result['studio']['timeline'] = copy.deepcopy(previous)
    PreparedTimeline(result)
    return result
