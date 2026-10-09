"""Editable starter scenes. Editorial themes never transform scientific values."""
import uuid
import re
from studio_model import Scene, Element
from output_profiles import adaptive_regions

THEMES = {
    'Ecuador Vivo': ('#04151e', '#f0f5f8', '#13bfd1'),
    'Andes Pulso': ('#121722', '#f6f4eb', '#e9af43'),
    'Scientific': ('#f5f7fa', '#152536', '#247ba0'),
    'Editorial': ('#faf7f0', '#222222', '#aa4634'),
    'Documentary': ('#18201c', '#eeeadd', '#b7ba77'),
    'Minimal Dark': ('#16191d', '#f3f3f3', '#93bdcc'),
    'Minimal Light': ('#ffffff', '#222b33', '#316da1'),
    'Earth': ('#26251e', '#f2ead8', '#b5bd81'),
    'Climate': ('#091e2d', '#eff8fc', '#53b6c5'),
    'Geology': ('#231d22', '#f8eddf', '#d99b68'),
}
TEMPLATES = {'blank': 'Lienzo vacío', 'cover': 'Portada', 'map_metric': 'Mapa + métrica',
             'map_ranking': 'Mapa + ranking', 'closing': 'Conclusión / créditos',
             'metric_focus':'Métrica destacada','ranking_focus':'Ranking',
             'comparison':'Comparación','quote':'Cita','image_caption':'Imagen + créditos',
             'methodology':'Metodología / fuentes'}
TEMPLATE_BINDINGS={'map_metric':('metric','value'),'metric_focus':('metric','value'),
                   'map_ranking':('ranking','rows'),'ranking_focus':('ranking','rows'),
                   'comparison':('comparison','rows')}
TYPOGRAPHY = {'Scientific': (False, 1.), 'Editorial': (True, 1.05),
              'Documentary': (False, 1.1), 'Social Bold': (True, 1.25),
              'Minimal': (False, .95), 'Data Dense': (False, .85), 'Professional': (True, 1.)}
# Discrete colors are authoring choices; no data scale is inferred or changed.
PALETTES = {
    'Rainfall': {'type': 'sequential', 'colors': ('#edf8fb', '#66c2a4', '#006d2c')},
    'Temperature': {'type': 'diverging', 'colors': ('#2166ac', '#f7f7f7', '#b2182b')},
    'Earth': {'type': 'sequential', 'colors': ('#f6e8c3', '#bf9d5c', '#543005')},
    'Editorial': {'type': 'categorical', 'colors': ('#316da1', '#aa4634', '#7566a0')},
}


def template_result_ids(template,registry):
    """Offer complete stored results only; never filter or manufacture rows."""
    if template not in TEMPLATE_BINDINGS: return []
    _,field=TEMPLATE_BINDINGS[template];eligible=[]
    for rid,result in registry.items():
        if field=='value' and 'rows' not in result: eligible.append(rid)
        elif field=='rows' and isinstance(result.get('rows'),list):
            rows=result['rows']
            if template!='comparison' or (len(rows)==2 and all(row.get('value') is not None for row in rows) and
                    rows[0].get('coverage',1)==rows[1].get('coverage',1)):
                eligible.append(rid)
    return eligible


def template_scene(template, profile, *, theme='Ecuador Vivo', typography='Professional', bindings=None,asset_id=None):
    if template not in TEMPLATES or theme not in THEMES or typography not in TYPOGRAPHY:
        raise ValueError('Plantilla, tema o estilo tipográfico desconocido.')
    if asset_id is not None and (template!='image_caption' or not isinstance(asset_id,str) or
                               not re.fullmatch(r'[\w.-]{1,180}',asset_id)):
        raise ValueError('La imagen del template requiere un ID interno de biblioteca.')
    bg, text, accent = THEMES[theme]
    bold, factor = TYPOGRAPHY[typography]
    regions = adaptive_regions(profile)
    bindings = bindings or {}
    elements = []

    def add(identifier, kind, region, style, binding=None,role=None,sizes=None):
        transform = {k: round(v) for k, v in region.items()}
        elements.append(Element(id=identifier, type=kind, name=identifier,
            transform=transform, style=style, data_binding=binding, z_index=len(elements)).to_dict())
        elements[-1]['layout_role'] = role or ('map' if identifier in ('map.placeholder','body') else
            'metric' if identifier in ('context','metric','ranking') else identifier)
        if kind in ('text','source'):
            sizes=sizes or {name:style['font_size'] for name in TYPOGRAPHY}
            elements[-1].update(typography_preset=typography,
                typography_base_size=sizes['Professional'],typography_sizes=sizes,
                typography_applied_size=style['font_size'],
                typography_role='source' if kind=='source' else 'title' if identifier=='title' else 'body',
                typography_weight='preset' if 'bold' in style else 'regular')

    title = 'Ecuador Vivo' if template == 'cover' else 'Conclusión' if template == 'closing' else 'Título de la escena'
    if template != 'blank':
        add('title', 'text', regions['title'], {'text': title, 'color': text,
            'font_size': max(8, min(120, round(profile.width*.048*factor))), 'bold': bold},
            sizes={name:max(8,min(120,round(profile.width*.048*scale))) for name,(_,scale) in TYPOGRAPHY.items()})
    if template in ('map_metric', 'map_ranking'):
        # Visible, editable placeholder until the author adds a real map asset.
        add('map.placeholder', 'shape', regions['map'], {'fill': accent, 'opacity': .18})
        field = 'metric' if template == 'map_metric' else 'ranking'
        if field in bindings:
            add(field, field, regions['metric'], {'visualization': {'style': {
                'background': bg, 'color': accent, 'text': text}}}, bindings[field])
        else:
            add('context', 'text', regions['metric'], {'text': 'Añade un mapa y vincula resultados desde Datos.',
                'color': text, 'font_size': max(8, round(profile.width*.028))})
    elif template in ('cover', 'closing'):
        add('body', 'text', regions['map'], {'text': 'Una historia basada en datos' if template == 'cover'
            else 'Fuentes, metodología y créditos', 'color': text,
            'font_size': max(8, round(profile.width*.04)), 'bold': bold})
    elif template in ('metric_focus','ranking_focus','comparison'):
        field=TEMPLATE_BINDINGS[template][0]
        binding=bindings.get(field)
        if binding:
            if min(regions['body_full']['width'],regions['body_full']['height'])<80:
                raise ValueError('La visualización necesita 80×80 px: reduce el margen o amplía el formato.')
            kind='chart' if field=='comparison' else field
            add(field,kind,regions['body_full'],{'visualization':{
                'kind':field,'style':{'background':bg,'color':accent,'text':text}}},binding,role='body_full')
        else:
            add('context','text',regions['body_full'],{
                'text':'Vincula un resultado',
                'color':text,'font_size':max(8,min(120,round(profile.width*.035*factor))),'bold':bold},role='body_full',
                sizes={name:max(8,min(120,round(profile.width*.035*scale))) for name,(_,scale) in TYPOGRAPHY.items()})
    elif template=='image_caption':
        if asset_id:
            add('image','image',regions['body_full'],{'asset_id':asset_id,'fit':'contain'},role='body_full')
        else:
            add('image.placeholder','shape',regions['body_full'],{'fill':accent,'opacity':.18},role='body_full')
            add('context','text',regions['body_full'],{'text':'Elige una imagen',
                'color':text,'font_size':max(8,min(120,round(profile.width*.035*factor)))},role='body_full',
                sizes={name:max(8,min(120,round(profile.width*.035*scale))) for name,(_,scale) in TYPOGRAPHY.items()})
    elif template in ('quote','methodology'):
        content=('Escribe una cita y su atribución.' if template=='quote' else
                 'Completa método y fuentes')
        add('body','text',regions['body_full'],{'text':content,'color':text,
            'font_size':max(8,min(120,round(profile.width*.035*factor))),'bold':bold},role='body_full',
            sizes={name:max(8,min(120,round(profile.width*.035*scale))) for name,(_,scale) in TYPOGRAPHY.items()})
    if template != 'blank':
        add('source', 'source', regions['source'], {'text': 'Fuente y periodo · completa los créditos',
            'color': text, 'font_size': max(8, round(profile.width*.022))})
    return Scene(id='scene.'+uuid.uuid4().hex, name=TEMPLATES[template], background=bg,
                 elements=elements).to_dict()
