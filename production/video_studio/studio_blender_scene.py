"""Compose a Blender object with editable Studio text; no new video renderer."""
import copy
import uuid
from output_profiles import profile_for
from studio_blender import validate_recipe
from studio_model import Element,Scene,validate_studio
from studio_resource_projects import create_resource_project

SOURCES=[{'title':'NOAA/NWS · ascenso orográfico','url':'https://forecast.weather.gov/glossary.php?word=OROGRAPHIC'},
    {'title':'NOAA/NWS · desarrollo de nubes','url':'https://www.weather.gov/source/zhu/ZHU_Training_Page/clouds/cloud_development/clouds.htm'}]


def _asset_id(asset):
    if not isinstance(asset,dict) or asset.get('kind')!='video':raise ValueError('El recurso 3D necesita un video verificado.')
    return 'blender.'+asset['sha256'][:24]


def create_scene_project(recipe,asset,job_id,title,definition):
    recipe=validate_recipe(recipe)
    project=create_resource_project(title,definition,duration=recipe['duration'])
    # Free projects inherit legacy rain defaults. Do not label an illustration
    # as CHIRPS observations, a dated climate series or measured precipitation.
    project.update(source='local',variable='Ilustración 3D',title=title,
        description='Ascenso orográfico: recurso conceptual editable en Blender.',
        citation='Base conceptual: NOAA / NWS',start='',end='',units='',entries=[],
        source_url=SOURCES[0]['url'],duration=round(recipe['duration']*30)/30,
        legend='',note='Ilustración conceptual; no es un pronóstico.',
        resolution_note='Geometría ilustrativa; no corresponde a un DEM.',scale_note='',boundary_note='')
    profile=profile_for(definition);w,h=profile.width,profile.height;portrait=h/w>=1.4
    sid='resource.blender.'+uuid.uuid4().hex;aid=_asset_id(asset)
    unit=min(w,h);left=w*.085;right=w*.14 if portrait else w*.06;available=w-left-right
    elements=[]
    def add(name,kind,box,style):
        element=Element(id=sid+'.'+name,name=name,type=kind,style=style,
            transform=dict(zip(('x','y','width','height'),[round(v) for v in box])),z_index=len(elements)).to_dict()
        element['resource_role']=name;elements.append(element)
    def text(name,content,box,size,color='#edf5f7',display=False):
        add(name,'text',box,dict(text=content,font_family='Barlow Condensed Display' if display else 'Barlow Condensed',
            font_size=max(8,round(size)),color=color,bold=display))
    brand_y=h*.065 if portrait else h*.07
    text('brand','ECUADOR VIVO / ANDES PULSO',(left,brand_y,available,unit*.055),unit*.026,'#58e4ce')
    if portrait:
        display_title='La montaña\nno fabrica agua' if title=='La montaña no fabrica agua' else title
        text('title',display_title,(left,h*.105,available,h*.115),unit*.082,display=True)
        text('subtitle','El aire asciende. La humedad puede condensarse.',(left,h*.225,available,h*.045),unit*.029,'#b8cbd1')
        body=(left,h*.28,available,h*.35)
        callout=(left,h*.65,available,h*.075)
    else:
        text('title',title,(left,h*.15,w*.39,h*.18),unit*.06,display=True)
        text('subtitle','El aire asciende. La humedad puede condensarse.',(left,h*.37,w*.36,h*.13),unit*.03,'#b8cbd1')
        body=(w*.48,h*.19,w*.47,h*.57)
        callout=(left,h*.57,w*.36,h*.12)
    add('blender_render','video',body,dict(asset_id=aid,fit='contain',mute=True,loop=False))
    text('explanation','1. Aire en movimiento\n2. Ascenso y posible condensación\n3. Una nube no siempre produce lluvia',callout,unit*.028,'#58e4ce')
    note_y=h*(.745 if portrait else .845)
    source_y=h*(.785 if portrait else .889)
    text('note','ILUSTRACIÓN 3D · NO ES UN PRONÓSTICO',(left,note_y,available,unit*.038),unit*.022,'#58e4ce')
    text('source','Base conceptual: NOAA / NWS · Relieve y partículas ilustrativos.',(left,source_y,available,unit*.045),unit*.022,'#b8cbd1')
    credit_y=h*(.825 if portrait else .94)
    credit=' · '.join(project.get(field,'') for field in ('author','tiktok','instagram') if project.get(field))
    text('credit',credit,(left,credit_y,available,unit*.042),unit*.022,'#b8cbd1')
    scene=Scene(id=sid,name=title,duration=round(recipe['duration']*30)/30,elements=elements,background=recipe['background']).to_dict()
    scene['resource']=dict(id='blender.orographic',version=1,illustrative=True,sources=SOURCES,
        note='No DEM, escala física, microfísica, viento medido ni pronóstico.',
        blender=dict(recipe=recipe,job_id=job_id,engine='Blender',version='4.5.4 LTS'))
    project['studio']['scenes']=[scene];project['studio']['timeline']=[sid]
    project['studio']['media']={aid:copy.deepcopy(asset)}
    validate_studio(project['studio'])
    return project


def replace_render(project,scene_id,recipe,asset,job_id):
    recipe=validate_recipe(recipe);result=copy.deepcopy(project)
    scene=next((s for s in result['studio']['scenes'] if s['id']==scene_id),None)
    if scene is None or 'blender' not in scene.get('resource',{}):raise ValueError('La escena no es un recurso Blender editable.')
    render=next((e for e in scene['elements'] if e.get('resource_role')=='blender_render' and e['type']=='video'),None)
    if render is None:raise ValueError('El objeto 3D se eliminó. Inserta una escena nueva para recuperarlo.')
    aid=_asset_id(asset);result['studio']['media'][aid]=copy.deepcopy(asset);render['style']['asset_id']=aid
    scene['resource']['blender'].update(recipe=recipe,job_id=job_id)
    # Authored timing, text, transforms, tracks and other scenes are preserved.
    validate_studio(result['studio'])
    return result
