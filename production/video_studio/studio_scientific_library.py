"""Lightweight catalog and explicit capability status, no engine imports at startup."""
import base64
import json
import hashlib
from functools import lru_cache
from pathlib import Path

ROOT=Path(__file__).parent
REPO=ROOT.parent.parent
ARTWORK_COLLECTIONS={
    'bioicons': ROOT/'resource_engines/artwork',
    'expedicion': REPO/'assets/images/expedicion',
}
ARTWORK_BYTE_LIMIT=8*1024*1024


def _asset_path(folder,filename):
    """A catalogue can name files only inside its explicit artwork collection."""
    if not isinstance(filename,str) or not filename or Path(filename).is_absolute():
        raise ValueError('Ruta de ilustración inválida.')
    root=folder.resolve();path=(root/filename).resolve()
    if path==root or not path.is_relative_to(root) or not path.is_file():
        raise ValueError('La ilustración no pertenece a su colección.')
    if path.stat().st_size>ARTWORK_BYTE_LIMIT:
        raise ValueError('La ilustración supera el límite de 8 MiB.')
    return path


def _validated_artwork(folder,entry):
    original=_asset_path(folder,entry['original'])
    original_bytes=original.read_bytes()
    if len(original_bytes)>ARTWORK_BYTE_LIMIT or hashlib.sha256(original_bytes).hexdigest()!=entry['sha256']:
        raise ValueError('El original cambió; revisa su procedencia.')
    image=_asset_path(folder,entry['image'])
    image_bytes=original_bytes if image==original else image.read_bytes()
    if len(image_bytes)>ARTWORK_BYTE_LIMIT:
        raise ValueError('La ilustración supera el límite de 8 MiB.')
    if entry.get('asset_sha256') and hashlib.sha256(image_bytes).hexdigest()!=entry['asset_sha256']:
        raise ValueError('La imagen cambió; revisa su procedencia.')
    mime={'.webp':'image/webp','.png':'image/png'}.get(image.suffix.lower())
    if mime is None:raise ValueError('Formato de ilustración incompatible.')
    return image,image_bytes,mime


def _catalog_assets(folder,collection):
    try:
        pack=json.loads((folder/'catalog.json').read_text(encoding='utf8'))
        entries=pack.get('items',[])
    except (ValueError,OSError,AttributeError):return []
    if not isinstance(entries,list) or len(entries)>1000:return []
    result=[]
    for entry in entries:
        try:
            if not isinstance(entry,dict) or entry.get('type')!='asset':continue
            _,content,mime=_validated_artwork(folder,entry)
            result.append({**entry,'collection':collection,
                'preview':'data:'+mime+';base64,'+base64.b64encode(content).decode()})
        except (ValueError,OSError,KeyError,TypeError):continue
    return result

@lru_cache(maxsize=1)
def installed_engines():
    modules=ROOT/'resource_engines/node_modules'
    packages=[('@excalidraw/excalidraw','Excalidraw','https://github.com/excalidraw/excalidraw'),
        ('fabric','Fabric.js','https://github.com/fabricjs/fabric.js'),('@xyflow/react','React Flow','https://github.com/xyflow/xyflow'),
        ('ketcher-react','Ketcher','https://github.com/epam/ketcher'),('three','Three.js','https://github.com/mrdoob/three.js')]
    result=[]
    for package,name,url in packages:
        try:version=json.loads((modules/package/'package.json').read_text(encoding='utf8'))['version']
        except (OSError,ValueError,KeyError):version=None
        tool={'Excalidraw':'drawing','Fabric.js':'vector','React Flow':'diagram','Ketcher':'molecule'}.get(name)
        result.append({'name':name,'version':version,'url':url,'tool':tool,'status':('Editor local integrado · documento editable' if tool else 'Motor 3D local disponible') if version else 'No instalado'})
    manim=REPO/'_local/resource-tools/.venv/Lib/site-packages/manim'
    result.append({'name':'Manim','version':'0.22.0' if manim.is_dir() else None,'url':'https://www.manim.community/',
        'status':'Entorno aislado · render bajo petición' if manim.is_dir() else 'No instalado'})
    result.append({'name':'Blender','version':'Local','url':'https://www.blender.org/','status':'Integrado · receta orográfica, cámara y materiales'})
    return result

@lru_cache(maxsize=1)
def scientific_objects():
    from studio_resource_actions import GRAPHIC_ELEMENTS
    drawings={
        'icon.cloud':'M28 72h62a18 18 0 0 0 0-36 26 26 0 0 0-48-5A21 21 0 0 0 28 72ZM35 86l-4 9m28-9-4 9m28-9-4 9',
        'icon.thermometer':'M52 22a8 8 0 0 1 16 0v49a20 20 0 1 1-16 0ZM60 38v45m0 0v10m22-58h12m-12 15h8',
        'icon.wind':'M18 42h65a12 12 0 1 0-12-12M15 60h84a10 10 0 1 0-10-10M22 78h50a12 12 0 1 1-12 12',
        'icon.mountain':'m15 92 34-58 14 22 15-30 29 66ZM37 56l11 9 9-12M70 44l10 10 8-8',
        'icon.calendar':'M24 30h72v68H24ZM24 50h72M40 20v22m40-22v22M40 66h6m14 0h6m14 0h6M40 82h6m14 0h6',
        'icon.bars':'M22 98V68h18v30Zm30 0V45h18v53Zm30 0V20h18v78Z',
        'circle':'M60 20a40 40 0 1 0 0 80 40 40 0 0 0 0-80Z',
        'line':'M20 60h80','divider':'M20 60h80','rectangle':'M20 30h80v60H20Z',
        'marker':'M60 28a32 32 0 1 0 0 64 32 32 0 0 0 0-64Z',
    }
    items=[]
    for shape,name in GRAPHIC_ELEMENTS.items():
        if shape.startswith('icon.') and shape in ('icon.tiktok','icon.instagram'):continue
        category='Clima' if shape in ('icon.cloud','icon.wind','icon.thermometer') else 'Geología' if shape=='icon.mountain' else 'Elementos gráficos'
        path=drawings.get(shape,'M24 30h72v60H24ZM38 48h44M38 62h32M38 76h20')
        image='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><rect width="120" height="120" fill="#0b1821"/><path d="'+path+'" fill="none" stroke="#70d9c5" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
        items.append({'id':shape,'shape':shape,'name':name,'category':category,'summary':'Símbolo conceptual editable · Ecuador Vivo',
            'type':'shape','preview':'data:image/svg+xml;base64,'+base64.b64encode(image.encode()).decode()})
    for collection,folder in ARTWORK_COLLECTIONS.items():
        items.extend(_catalog_assets(folder,collection))
    return items

def scientific_templates(definition):
    from studio_resources import RESOURCE_CATALOG
    from studio_resources_ui import _template_thumbnail
    from studio_expedicion_templates import illustrated_templates
    result=[]
    for row in RESOURCE_CATALOG:
        result.append({**row,'preview':'data:image/png;base64,'+base64.b64encode(_template_thumbnail(row['id'],definition)).decode()})
    return illustrated_templates(definition)+result


def insert_bioicon(project,scene_id,identifier):
    from studio_media import import_asset
    from studio_workspace_commands import workspace_command
    import copy
    entry=next((r for r in scientific_objects() if r['id']==identifier and r['type']=='asset'),None)
    if entry is None:raise ValueError('Ilustración científica desconocida.')
    folder=ARTWORK_COLLECTIONS.get(entry.get('collection','bioicons'))
    if folder is None:raise ValueError('Colección de ilustraciones desconocida.')
    image,content,_=_validated_artwork(folder,entry)
    asset=import_asset(content,image.name);aid='asset.'+asset['sha256']
    result=copy.deepcopy(project);result['studio']['media'][aid]=asset
    result=workspace_command(result,scene_id,{'action':'add_element','kind':'image','asset_id':aid,'name':entry['name']})
    scene=next(s for s in result['studio']['scenes'] if s['id']==scene_id)
    scene['elements'][-1]['scientific_provenance']={k:entry[k] for k in (
        'author','license','source','sha256','summary','collection','generated_by',
        'source_sha256','asset_sha256','observational_data') if k in entry}
    return result
