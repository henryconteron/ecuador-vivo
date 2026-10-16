"""Bounded, non-executable tool artifacts with a retained editable recipe."""
import base64,copy,io,json
from PIL import Image
from studio_media import import_asset
from studio_workspace_commands import workspace_command

TOOLS=frozenset(('drawing','diagram','vector','molecule'))

def import_tool_artifact(project,scene_id,payload):
    if not isinstance(payload,dict) or payload.get('tool') not in TOOLS:raise ValueError('Herramienta desconocida.')
    recipe=payload.get('recipe')
    if not isinstance(recipe,dict):raise ValueError('Documento editable inválido.')
    try:encoded=json.dumps(recipe,allow_nan=False,ensure_ascii=False)
    except (ValueError,TypeError,RecursionError) as error:raise ValueError('El documento debe ser JSON finito.') from error
    if len(encoded.encode())>2_000_000:raise ValueError('Documento editable superior a 2 MB.')
    png=payload.get('png','')
    if not isinstance(png,str) or not png.startswith('data:image/png;base64,') or len(png)>12_000_000:raise ValueError('Imagen PNG inválida o demasiado grande.')
    try:
        content=base64.b64decode(png.split(',',1)[1],validate=True)
        with Image.open(io.BytesIO(content)) as image:
            if image.format!='PNG' or image.width*image.height>16_000_000:raise ValueError('PNG superior a 16 MP.')
            image.verify()
    except (ValueError,OSError) as error:raise ValueError('No se pudo verificar el PNG.') from error
    result=copy.deepcopy(project);scene=next(s for s in result['studio']['scenes'] if s['id']==scene_id)
    element_id=payload.get('element_id');element=next((e for e in scene['elements'] if e['id']==element_id),None)
    if element_id and (element is None or element.get('locked') or not element.get('source_document')):raise ValueError('Objeto no editable o bloqueado.')
    asset=import_asset(content,'recurso-'+payload['tool']+'.png');aid='asset.'+asset['sha256'];result['studio']['media'][aid]=asset
    if element is None:
        result=workspace_command(result,scene_id,{'action':'add_element','kind':'image','asset_id':aid,'name':'Figura · '+payload['tool']})
        scene=next(s for s in result['studio']['scenes'] if s['id']==scene_id);element=scene['elements'][-1]
    else:element['style']['asset_id']=aid
    element['source_document']={'version':1,'tool':payload['tool'],'recipe':recipe,'review':'Sin revisar',
        'note':'Objeto compuesto: reabrir el editor original para modificar sus piezas.'}
    return result
