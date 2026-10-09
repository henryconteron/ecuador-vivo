"""Declarative workspace edits; presentation only, existing model and commands."""
import copy
import uuid
from studio_editing import (edit_scene, patch_canvas, adapt_profile, duplicate_elements,
                            apply_scene_design)
from studio_composition import group_elements
from studio_model import Element
from studio_templates import template_scene, PALETTES
from output_profiles import profile_for, adaptive_regions

STYLE_FIELDS=frozenset(('text','font_size','font_family','bold','alignment','color','fill','shape',
                       'fit','asset_id','trim_in','trim_out','loop','mute','volume','opacity','visualization'))

def workspace_command(project, scene_id, message):
    if not isinstance(message,dict): raise ValueError('Comando inválido.')
    action=message.get('action'); result=copy.deepcopy(project)
    studio=result['studio']; scene=next((s for s in studio['scenes'] if s['id']==scene_id),None)
    if scene is None: raise ValueError('Escena desconocida.')
    if message.get('entries'): result=patch_canvas(result,scene_id,message['entries']);studio=result['studio'];scene=next(s for s in studio['scenes'] if s['id']==scene_id)
    if action in ('canvas','apply','select','seek','export','play','save','copy'): return result
    if action=='rename':
        name=message.get('name')
        if not isinstance(name,str) or not name.strip() or len(name)>180: raise ValueError('Nombre de proyecto inválido.')
        result['name']=name.strip();return result
    if action=='profile': return adapt_profile(result,message['profile'])
    if action=='reorder': return edit_scene(result,'reorder',order=message['order'])
    if action=='scene_properties':
        return edit_scene(result,'update',scene_id,**{k:message[k] for k in ('name','duration','background') if k in message})
    if action in ('scene_duplicate','scene_delete'): return edit_scene(result,action.removeprefix('scene_'),scene_id)
    if action=='scene_recover':
        sid=message['id']
        if sid in studio['timeline'] or not any(s['id']==sid and s.get('renderer','studio')=='studio' for s in studio['scenes']):raise ValueError('Escena no recuperable.')
        studio['timeline'].append(sid);return result
    if action=='separate_timeline': return edit_scene(result,'separate_timeline')
    if action in ('scene_add','template','project_new'):
        fresh=template_scene(message.get('template','blank'),profile_for(studio['output_profile']),
            theme=message.get('theme',studio.get('theme','Ecuador Vivo')),
            typography=message.get('typography','Editorial'),bindings=message.get('bindings',{}),asset_id=message.get('asset_id'))
        if action=='project_new':
            studio['timeline']=[fresh['id']];studio['scenes'].append(fresh);result['name']='Proyecto sin título';return result
        return edit_scene(result,'add',scene=fresh)
    if action=='design':
        return apply_scene_design(result,scene_id,**{k:message[k] for k in ('theme','typography','font_roles') if k in message})
    if action in ('group','ungroup'):return group_elements(result,scene_id,message.get('ids',[]),action=action)
    if action in ('duplicate','paste'):return duplicate_elements(result,scene_id,message.get('ids',[]),elements=message.get('elements') if action=='paste' else None,map_instances=message.get('map_instances') if action=='paste' else None)
    if action=='add_element':
        kind=message['kind'];profile=profile_for(studio['output_profile']);style={};binding=None
        if kind=='text':style={'text':'Tu texto','font_size':min(40,round(profile.width*.1)),'color':'#f0f5f8'}
        elif kind=='shape':style={'shape':'rounded_rectangle','fill':'#13bfd1'}
        elif kind in ('image','map','video'):
            aid=message['asset_id'];asset=studio['media'][aid]
            if asset['kind']=='temporal_map':raise ValueError('El recurso estructurado requiere una instancia con fecha y leyenda; inserción guiada pendiente de 4b.4a.')
            if (kind=='video')!=(asset['kind']=='video'):raise ValueError('Tipo de recurso incompatible.')
            style={'asset_id':aid,'fit':'contain'}
            if kind=='video':style.update(mute=True,volume=1,trim_in=0,loop=False)
        elif kind in ('metric','chart','ranking'):
            rid=message['result_id'];value=studio['calculations'][rid]
            from calculation_results import CalculationResult
            CalculationResult(value)
            binding={'result_id':rid,'field':'rows' if 'rows' in value else 'value'}
            if (kind=='metric')==('rows' in value) or binding['field'] not in value:
                raise ValueError('Representación incompatible con el resultado.')
            style={'visualization':{'kind':message.get('visualization','metric' if kind=='metric' else 'horizontal_bar'),
                'style':{'color':PALETTES[message.get('palette','Earth')]['colors'][-1]}}}
        else:raise ValueError('Tipo no insertable.')
        region=adaptive_regions(profile)['metric' if binding else 'map']
        transform={k:round(v) for k,v in region.items()}
        if kind in ('text','shape'):transform={'x':20,'y':20,'width':min(500,profile.width-40),'height':min(180,profile.height-40)}
        element=Element(id='element.'+uuid.uuid4().hex,type=kind,name=message.get('name',{'text':'Texto','shape':'Forma'}.get(kind,kind)),
            transform=transform,style=style,data_binding=binding,z_index=max((e.get('z_index',0) for e in scene['elements']),default=0)+1).to_dict()
        return edit_scene(result,'update',scene_id,elements=scene['elements']+[element])
    if action=='properties':
        ids=message.get('ids',[]);changed=[e for e in scene['elements'] if e['id'] in ids]
        if not changed or len(changed)!=len(set(ids)) or any(e.get('locked') for e in changed):raise ValueError('Selecciona elementos existentes y desbloqueados.')
        style=message.get('style',{})
        if not isinstance(style,dict) or set(style)-STYLE_FIELDS:raise ValueError('Propiedad de estilo desconocida.')
        for element in changed:
            if element.get('data_binding') and 'text' in style:raise ValueError('El contenido científico se edita en su fuente.')
            element['style'].update(copy.deepcopy(style))
            for field in ('animation','typography_role','data_binding'):
                if field in message:element[field]=copy.deepcopy(message[field])
            if 'rotation' in message:element.setdefault('transform',{})['rotation']=message['rotation']
        return edit_scene(result,'update',scene_id,elements=scene['elements'])
    raise ValueError('Acción desconocida: '+str(action))
