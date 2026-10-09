"""Pure, flat editorial grouping. Group identity never owns scientific data."""
import copy
import uuid
from studio_model import validate_studio


def group_elements(project,scene_id,ids, *, action='group'):
    if not isinstance(ids,list) or any(not isinstance(i,str) for i in ids) or len(set(ids))!=len(ids):
        raise ValueError('Selección de grupo inválida.')
    result=copy.deepcopy(project);studio=result['studio'];validate_studio(studio)
    scene=next((s for s in studio['scenes'] if s['id']==scene_id),None)
    if scene is None or scene.get('renderer','studio')!='studio': raise ValueError('El grupo requiere una escena libre.')
    by_id={e['id']:e for e in scene['elements']}
    if not ids or set(ids)-set(by_id): raise ValueError('Selecciona elementos existentes.')
    previous={by_id[i]['group_id'] for i in ids if by_id[i].get('group_id')}
    members={e['id'] for e in scene['elements'] if e.get('group_id') in previous}
    if action=='group':
        if len(ids)<2 or members-set(ids): raise ValueError('Agrupa al menos dos elementos y todos los miembros de grupos anteriores.')
        affected=[by_id[i] for i in ids]
        if any(e.get('locked') or e.get('editor_deleted') for e in affected): raise ValueError('Desbloquea o recupera los elementos antes de agrupar.')
        group_id='group.'+uuid.uuid4().hex
        for element in affected: element['group_id']=group_id
    elif action=='ungroup':
        affected=[by_id[i] for i in members]
        if any(e.get('locked') for e in affected): raise ValueError('Desbloquea el grupo antes de desagrupar.')
        for element in affected: element.pop('group_id',None)
    else: raise ValueError('Operación de grupo desconocida.')
    validate_studio(studio)
    return result
