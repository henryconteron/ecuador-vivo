"""Integrated free-scene workspace over the existing model, canvas and render."""
import copy
import datetime as dt
import json
from pathlib import Path
import uuid
import streamlit as st
from streamlit.errors import StreamlitAPIException
from PIL import Image
from model import STORE
from jobs import read_json
from studio_recovery import save_snapshot as write_json, recover_snapshot, list_snapshots
from studio_model import Element, validate_studio
from studio_editing import (new_workspace, edit_scene, patch_canvas, timeline_rows,
                            adapt_profile, attach_snapshot, duplicate_elements,apply_scene_design)
from studio_templates import THEMES, TEMPLATES, TEMPLATE_BINDINGS, TYPOGRAPHY, PALETTES, template_scene,template_result_ids
from output_profiles import PRESETS, profile_for, adaptive_regions
from studio_media import import_asset, AssetFrames
from studio_timeline import PreparedTimeline
from studio_cache import StudioPreviewCache
from studio_typography import FONT_FAMILIES, FONT_ROLES, element_font_role
from studio_palette_ui import color_scale_inputs
from studio_composition import group_elements
from layout_engine import _png
from layout_editor import mount_canvas

TIMELINE_HTML = '''<section class="timeline" aria-label="Timeline de escenas"><header><strong>Timeline</strong><span id="total"></span></header><div id="scenes" role="list"></div><label>Playhead <input id="playhead" type="range" min="0" step="1"><output id="time"></output></label><small>Arrastra para ordenar · Mayús + flechas: reordenar · Enter: seleccionar · Aplica el canvas antes de cambiar de escena.</small></section>'''
TIMELINE_CSS = '''.timeline{font:14px var(--st-font);color:var(--st-text-color);border-top:1px solid var(--st-border-color);padding-top:10px}.timeline header{display:flex;justify-content:space-between;margin-bottom:8px}#scenes{display:flex;gap:8px;overflow-x:auto;padding:4px}button{font:inherit;color:inherit;background:var(--st-secondary-background-color);border:1px solid var(--st-border-color);border-radius:4px;padding:6px;cursor:pointer;min-width:126px;max-width:160px}button[aria-current=true]{border:2px solid var(--st-primary-color)}button img{width:120px;height:76px;object-fit:contain;display:block;background:#10171d}button span{display:block;max-width:125px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}button:focus-visible,input:focus-visible{outline:3px solid var(--st-primary-color)}label{display:flex;gap:10px;align-items:center;margin:10px 0}input{flex:1;min-width:50px;accent-color:var(--st-primary-color)}small{color:var(--st-gray-text-color)}'''
TIMELINE_JS = '''export default function({parentElement:root,data,setTriggerValue}){
 const q=id=>root.querySelector('#'+id),rows=structuredClone(data.rows);let dragged=null;
 const send=value=>setTriggerValue('changed',{...value,nonce:Date.now()});
 const reorder=(from,to)=>{const ids=rows.map(r=>r.id),index=ids.indexOf(from);ids.splice(index,1);ids.splice(to,0,from);send({action:'reorder',order:ids})};
 q('scenes').replaceChildren();rows.forEach((row,index)=>{const button=document.createElement('button');button.type='button';button.draggable=true;button.setAttribute('aria-current',String(row.id===data.selected));button.setAttribute('aria-label',(index+1)+' · '+row.name+' · '+row.seconds+' segundos');const image=document.createElement('img');image.src=row.thumbnail;image.alt='';const text=document.createElement('span');text.textContent=(index+1)+' · '+row.name;const time=document.createElement('span');time.textContent=row.seconds.toFixed(2)+' s';button.append(image,text,time);button.onclick=()=>send({action:'select',id:row.id});button.ondragstart=e=>{dragged=row.id;e.dataTransfer.setData('text/plain',row.id)};button.ondragover=e=>e.preventDefault();button.ondrop=e=>{e.preventDefault();if(dragged&&dragged!==row.id)reorder(dragged,index)};button.onkeydown=e=>{if(e.shiftKey&&['ArrowLeft','ArrowRight'].includes(e.key)){e.preventDefault();const to=index+(e.key==='ArrowLeft'?-1:1);if(to>=0&&to<rows.length)reorder(row.id,to)}};q('scenes').append(button)});
 const total=rows.at(-1).end_frame;q('total').textContent=rows.length+' escenas · '+(total/30).toFixed(2)+' s · 30 fps';q('playhead').max=total-1;q('playhead').value=data.frame;const label=()=>q('time').textContent=(Number(q('playhead').value)/30).toFixed(2)+' s';label();q('playhead').oninput=label;q('playhead').onchange=()=>send({action:'seek',frame:Number(q('playhead').value)});
}'''
TIMELINE_CSS=TIMELINE_CSS.replace('}', '}\n')
_TIMELINE=st.components.v2.component('ecuador_vivo_scene_timeline',html=TIMELINE_HTML,css=TIMELINE_CSS,js=TIMELINE_JS)


def canvas_payload(image, scene, profile):
    """Full element boxes, with transparent padding around contain-fitted assets.

    The padding uses the render's captured tile and position; no second layout
    engine. Moving a centered map therefore does not accumulate centering offsets.
    """
    graph=image.info['visual_scene']
    payload=graph.payload()
    by_id={e['id']:e for e in scene['elements']}
    for row,source in zip(payload['layers'],graph.items):
        element=by_id[row['id']];transform=element.get('transform',{})
        x,y,w,h=(round(transform.get(key,default)) for key,default in
                 (('x',0),('y',0),('width',100),('height',100)))
        tile=Image.new('RGBA',(w,h))
        tile.alpha_composite(source['image'],(row['x']-x,row['y']-y))
        row.update(x=x,y=y,w=w,h=h,original={'x':x,'y':y,'w':w,'h':h},src=_png(tile),
                   deleted=element.get('editor_deleted',False))
        if element.get('group_id'): row['group_id']=element['group_id']
        if element['type'] in ('text','source'):
            # Resizing starts from the font actually drawn, including auto-fit.
            # Keep its baseline so a move/unlock does not rewrite authored style.
            row['original']['font_size']=row['font_size']
    payload.update(scene=scene['id'],entries={},icons=[],free_scene=True,
                   frame_width=profile.width,frame_height=profile.height,safe_area=profile.safe_area)
    return payload


def show_studio(source_project, *, key='free_studio', snapshot=None):
    state_key=key+'_document'
    if state_key not in st.session_state:
        previous_cache=st.session_state.pop(key+'_preview_cache',None)
        if isinstance(previous_cache,StudioPreviewCache): previous_cache.clear()
        st.session_state[state_key]=new_workspace(source_project)
        st.session_state[key+'_selected']=st.session_state[state_key]['studio']['timeline'][0]
        st.session_state[key+'_version']=0
    project=st.session_state[state_key]
    if not st.session_state.get(key+'_draft'):
        initial=str(STORE/'projects'/('borrador-studio-'+dt.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]+'.json'))
        try:
            write_json(initial,project);st.session_state[key+'_draft']=initial
        except (ValueError,TypeError,KeyError,OSError) as error: st.error('No se pudo guardar el borrador inicial: '+str(error))
    studio=project['studio']
    profile=profile_for(studio['output_profile'])
    version=st.session_state.get(key+'_version',0)
    history=st.session_state.setdefault(key+'_history',[])
    future=st.session_state.setdefault(key+'_future',[])
    if not isinstance(st.session_state.get(key+'_preview_cache'),StudioPreviewCache):
        st.session_state[key+'_preview_cache']=StudioPreviewCache()
    cache=st.session_state[key+'_preview_cache']
    selected=st.session_state.get(key+'_selected',studio['timeline'][0])
    if selected not in studio['timeline']: selected=studio['timeline'][0]
    rows=timeline_rows(studio)
    current_row=next(r for r in rows if r['id']==selected)
    scene=next(s for s in studio['scenes'] if s['id']==selected)
    frame=st.session_state.get(key+'_frame',current_row['start_frame'])
    if not current_row['start_frame']<=frame<current_row['end_frame']: frame=current_row['start_frame']

    def commit(candidate, *, record=True,allow_legacy=False,draft_path=None):
        preflight=copy.deepcopy(candidate) if allow_legacy else candidate
        if allow_legacy:
            ids={s['id'] for s in preflight['studio']['scenes'] if s.get('renderer','studio')=='studio'}
            preflight['studio']['timeline']=[sid for sid in preflight['studio']['timeline'] if sid in ids]
        prepared=PreparedTimeline(preflight) if preflight['studio']['timeline'] else None
        # Preflight pixels before accepting a new document. This never computes science.
        with AssetFrames(candidate['studio']['media'],cache=cache.media) as assets:
            if prepared is not None: cache.for_timeline(prepared,assets).thumbnails()
        draft=draft_path or st.session_state.get(key+'_draft') or str(STORE/'projects'/(
            'borrador-studio-'+dt.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]+'.json'))
        # Publish the durable draft before changing live document/history. A
        # failed disk write must leave the accepted state and undo intact.
        write_json(draft,candidate)
        if record:
            history.append(copy.deepcopy(st.session_state[state_key]['studio']))
            del history[:-10];future.clear()
        st.session_state[state_key]=candidate
        st.session_state[key+'_version']=st.session_state.get(key+'_version',0)+1
        st.session_state[key+'_draft']=draft

    def accept(candidate, *, select=None):
        try:
            commit(candidate)
            if select is not None:
                st.session_state[key+'_selected']=select;st.session_state.pop(key+'_frame',None)
            st.rerun()
        except (ValueError,TypeError,KeyError,OSError) as error: st.error(str(error))

    st.header('Ecuador Vivo Studio')
    st.caption('Escenas libres · borrador separado · cálculo y fuentes conservados. El montaje anterior permanece disponible en Montaje.')
    with st.expander('Borradores guardados y recuperación'):
        snapshots=list_snapshots(STORE/'projects')
        if snapshots:
            recovered_path=st.selectbox('Borrador guardado',[str(path) for path in snapshots],
                format_func=lambda path:Path(path).name,key=key+'_snapshot_choice')
            if st.button('Abrir copia recuperada',key=key+'_snapshot_open'):
                try:
                    candidate,previous=recover_snapshot(recovered_path)
                    destination=str(STORE/'projects'/('borrador-studio-'+dt.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]+'.json'))
                    commit(candidate,allow_legacy=True,record=False,draft_path=destination)
                    history.clear();future.clear()
                    st.session_state[key+'_selected']=candidate['studio']['timeline'][0]
                    st.session_state.pop(key+'_frame',None)
                    st.session_state[key+'_recovery_notice']='Se recuperó la versión anterior porque el snapshot principal no era válido.' if previous else 'Copia recuperada. El archivo seleccionado se conserva.'
                    st.rerun()
                except (ValueError,TypeError,KeyError,OSError) as error: st.error(str(error))
        st.caption('Los cambios aceptados se guardan automáticamente con una versión anterior. Abrir una copia inicia otro historial; los archivos anteriores se conservan. Los gestos pendientes se conservan por pestaña hasta aplicar OK.')
    if st.session_state.get(key+'_recovery_notice'): st.info(st.session_state.pop(key+'_recovery_notice'))
    by_id={s['id']:s for s in studio['scenes']}
    if any(by_id[sid].get('renderer','studio')!='studio' for sid in studio['timeline']):
        st.warning('Esta timeline incluye referencias del montaje anterior. Conserva esas escenas y activa una timeline libre para editarlas en Estudio.')
        st.caption('El borrador guardará todas las escenas, fuentes y resultados; el montaje anterior sigue disponible en Montaje.')
        if st.button('Editar solo escenas libres',key=key+'_separate'):
            accept(edit_scene(project,'separate_timeline'))
        return
    with st.container(horizontal=True,wrap=True):
        for label,stack,other in (('Deshacer',history,future),('Rehacer',future,history)):
            if st.button(label,disabled=not stack,key=key+'_'+label):
                candidate=copy.deepcopy(project);candidate['studio']=copy.deepcopy(stack[-1])
                try:
                    commit(candidate,record=False);other.append(copy.deepcopy(studio));stack.pop();st.rerun()
                except (ValueError,KeyError,OSError) as error: st.error(str(error))
        if st.button('Añadir escena',key=key+'_add'):
            fresh=template_scene('blank',profile)
            candidate=edit_scene(project,'add',scene=fresh)
            st.session_state[key+'_selected']=fresh['id'];accept(candidate)
        if st.button('Duplicar escena',key=key+'_duplicate'): accept(edit_scene(project,'duplicate',selected))
        if st.button('Quitar de timeline',disabled=len(rows)==1,key=key+'_delete'): accept(edit_scene(project,'delete',selected))
        recovered=[s for s in studio['scenes'] if s.get('renderer','studio')=='studio' and s['id'] not in studio['timeline']]
        if recovered:
            recover=st.selectbox('Recuperar escena',recovered,format_func=lambda s:s['name'],key=key+'_recover_choice')
            if st.button('Recuperar',key=key+'_recover'):
                candidate=copy.deepcopy(project);candidate['studio']['timeline'].append(recover['id']);accept(candidate)

    with st.expander('Formato, templates, temas y tipografía'):
        choice=st.selectbox('Formato del estudio',list(PRESETS)+['custom'],
            index=(list(PRESETS)+['custom']).index(profile.id),format_func=lambda v:PRESETS[v][0] if v in PRESETS else 'Personalizado',key=key+'_profile_choice')
        definition={'id':choice}
        if choice=='custom':
            a,b=st.columns(2)
            definition.update(width=a.number_input('Ancho · px',160,3840,profile.width,step=2,key=key+'_custom_w'),
                              height=b.number_input('Alto · px',160,3840,profile.height,step=2,key=key+'_custom_h'))
        st.caption('Adaptar reorganiza las regiones de templates; ajusta los objetos manuales fuera de límites. Los márgenes son recomendaciones editoriales y no se exportan.')
        if st.button('Adaptar escenas al formato',key=key+'_adapt'): accept(adapt_profile(project,definition))
        template=st.selectbox('Template',list(TEMPLATES),format_func=TEMPLATES.get,key=key+'_template')
        theme=st.selectbox('Tema',list(THEMES),key=key+'_theme')
        typography=st.selectbox('Estilo tipográfico',list(TYPOGRAPHY),key=key+'_typography')
        st.caption('Fuentes locales con licencia OFL. Los roles asignan familias sin cambiar tamaños ni pesos.')
        font_roles={}
        for role,label in FONT_ROLES.items():
            family=st.selectbox('Familia · '+label,[None]+list(FONT_FAMILIES),
                format_func=lambda value:'Conservar familias actuales' if value is None else value,
                key=key+'_font_role_'+selected+'_'+role)
            if family is not None: font_roles[role]=family
        if st.button('Aplicar familias por rol',key=key+'_font_roles_apply',disabled=not font_roles):
            accept(apply_scene_design(project,selected,font_roles=font_roles))
        bindings={};template_asset=None
        if template in TEMPLATE_BINDINGS:
            binding_key,field=TEMPLATE_BINDINGS[template]
            eligible=template_result_ids(template,studio['calculations'])
            rid=st.selectbox('Resultado del template',[None]+eligible,
                format_func=lambda rid:'Sin vincular · placeholder editable' if rid is None else
                rid+' · '+studio['calculations'][rid].get('variable','')+' · '+studio['calculations'][rid].get('units',''),
                key=key+'_template_result_'+template)
            if rid is not None: bindings[binding_key]={'result_id':rid,'field':field}
            if template=='comparison': st.caption('Comparación requiere dos observaciones válidas con cobertura comparable.')
        if template=='image_caption':
            eligible=[aid for aid,record in studio['media'].items() if record['kind']=='image']
            template_asset=st.selectbox('Imagen del template',[None]+eligible,
                format_func=lambda aid:'Sin imagen · placeholder editable' if aid is None else studio['media'][aid]['name'],
                key=key+'_template_image')
        if st.button('Añadir escena desde template',key=key+'_template_add'):
            try:
                fresh=template_scene(template,profile,theme=theme,typography=typography,bindings=bindings,asset_id=template_asset)
                candidate=edit_scene(project,'add',scene=fresh);candidate['studio']['theme']=theme
                accept(candidate,select=fresh['id'])
            except (ValueError,TypeError,KeyError) as error: st.error(str(error))
        if st.button('Aplicar tema a esta escena',key=key+'_theme_apply'):
            accept(apply_scene_design(project,selected,theme=theme))
        if st.button('Aplicar tipografía a esta escena',key=key+'_typography_apply'):
            accept(apply_scene_design(project,selected,typography=typography))

    with st.expander('Datos calculados y biblioteca multimedia'):
        if snapshot:
            if st.button('Vincular revisión científica cargada',key=key+'_attach'):
                from visualization_ui import scientific_identity
                if scientific_identity(source_project)!=snapshot['scientific_identity']:
                    st.warning('La fuente cambió: carga una revisión científica nueva en Visualizaciones.')
                else: accept(attach_snapshot(project,snapshot))
        else: st.caption('Carga resultados en Maqueta → Visualizaciones y vuelve aquí para vincular esa revisión sin recalcular.')
        for value in studio['calculations'].values():
            for warning in value.get('provenance',{}).get('warnings',[]): st.warning(warning)
        upload=st.file_uploader('Importar imagen o video · hasta 100 MB',type=['png','jpg','jpeg','webp','mp4','mov','webm','mkv'],key=key+'_upload')
        if upload and st.button('Importar a biblioteca',key=key+'_import'):
            try:
                asset=import_asset(upload.getvalue(),upload.name)
                candidate=copy.deepcopy(project);candidate['studio']['media']['asset.'+asset['sha256']]=asset
                accept(candidate)
            except (ValueError,OSError) as error: st.error(str(error))
        if studio['media']:
            aid=st.selectbox('Recurso del proyecto',list(studio['media']),format_func=lambda value:studio['media'][value]['name'],key=key+'_asset')
            record=studio['media'][aid]
            size=record.get('size',[])
            st.caption(f'{record["name"]} · {size} px · {record.get("duration",0):g} s · {record.get("bytes",0)/1048576:.2f} MB')
            as_map=st.checkbox('Esta imagen es un mapa · mantener contain',disabled=record['kind']=='video',key=key+'_as_map')
            if st.button('Añadir recurso al canvas',key=key+'_asset_add'):
                kind='video' if record['kind']=='video' else 'map' if as_map else 'image'
                element=Element(id='element.'+uuid.uuid4().hex,type=kind,name=record['name'],
                    transform={k:round(v) for k,v in adaptive_regions(profile)['map'].items()},
                    style={'asset_id':aid,'fit':'contain',**({'mute':True,'trim_in':0,'loop':False} if kind=='video' else {})},
                    z_index=max((e.get('z_index',0) for e in scene['elements']),default=0)+1).to_dict()
                accept(edit_scene(project,'update',selected,elements=scene['elements']+[element]))
        if studio['calculations']:
            rid=st.selectbox('CalculationResult',list(studio['calculations']),key=key+'_result')
            value=studio['calculations'][rid];scalar='rows' not in value
            kinds=['metric'] if scalar else ['horizontal_bar','vertical_bar','dot','lollipop','line','ranking','comparison']
            kind=st.selectbox('Representación',kinds,key=key+'_visualization_'+str(scalar))
            palette=st.selectbox('Paleta',list(PALETTES),key=key+'_palette')
            st.caption(PALETTES[palette]['type']+' · tinta del último color; unidades del resultado: '+value.get('units','sin unidad declarada'))
            use_scale=st.checkbox('Usar paleta como escala de datos',key=key+'_use_scale')
            scale=color_scale_inputs(palette,key=key+'_new_scale') if use_scale else None
            if st.button('Añadir visualización vinculada',key=key+'_viz_add'):
                element=Element(id='element.'+uuid.uuid4().hex,type='metric' if scalar else 'chart',name=kind,
                    transform={k:round(v) for k,v in adaptive_regions(profile)['metric'].items()},
                    data_binding={'result_id':rid,'field':'value' if scalar else 'rows'},
                    style={'visualization':{'kind':kind,'style':{'color':PALETTES[palette]['colors'][-1],
                        **({'color_scale':scale} if scale is not None else {})}}},
                    z_index=max((e.get('z_index',0) for e in scene['elements']),default=0)+1).to_dict()
                accept(edit_scene(project,'update',selected,elements=scene['elements']+[element]))

    with st.expander('Escena y elementos · estilo, video y animación'):
        group_ids=st.multiselect('Elementos del grupo',[e['id'] for e in scene['elements'] if not e.get('editor_deleted')],
            format_func=lambda eid:next(e.get('name') or eid for e in scene['elements'] if e['id']==eid),
            key=key+'_group_elements_'+selected)
        st.caption('Los grupos conservan elementos, datos y geometría. Seleccionar un miembro en el canvas selecciona el conjunto.')
        for label,action,disabled in (('Agrupar elementos','group',len(group_ids)<2),('Desagrupar elementos','ungroup',not group_ids)):
            if st.button(label,key=key+'_group_'+action,disabled=disabled):
                try: accept(group_elements(project,selected,group_ids,action=action))
                except ValueError as error: st.error(str(error))
        with st.form(key+'_scene_form_'+selected):
            name=st.text_input('Nombre de escena',scene['name'],max_chars=180)
            duration=st.number_input('Duración · segundos · 30 fps',min_value=1/30,max_value=7200.,value=float(scene['duration']),step=1/30)
            background=st.color_picker('Fondo de escena',scene['background'])
            if st.form_submit_button('Guardar escena'): accept(edit_scene(project,'update',selected,name=name,duration=duration,background=background))
        if scene['elements']:
            eid=st.selectbox('Propiedades del elemento',scene['elements'],format_func=lambda e:e.get('name') or e['id'],key=key+'_element_'+selected)['id']
            element=next(e for e in scene['elements'] if e['id']==eid)
            is_visual=element['type'] in ('metric','ranking','chart')
            current_scale=element['style'].get('visualization',{}).get('style',{}).get('color_scale') if is_visual else None
            with st.form(key+'_element_form_'+selected+'_'+eid):
                style=copy.deepcopy(element['style']);animation=element.get('animation',{})
                font_role=None
                if element['type'] in ('text','source','metric','ranking','chart'):
                    role=element_font_role(element)
                    font_role=st.selectbox('Rol tipográfico',list(FONT_ROLES),index=list(FONT_ROLES).index(role),format_func=FONT_ROLES.get)
                    target=style if element['type'] in ('text','source') else style.setdefault('visualization',{}).setdefault('style',{})
                    families=[None]+list(FONT_FAMILIES)
                    family=st.selectbox('Familia del elemento',families,index=families.index(target.get('font_family')),
                        format_func=lambda value:'Barlow Condensed · predeterminada' if value is None else value)
                    if family is None: target.pop('font_family',None)
                    else: target['font_family']=family
                if is_visual:
                    choices=[None]+list(PALETTES)
                    scale_palette=st.selectbox('Escala del elemento',choices,index=choices.index(current_scale.get('palette') if current_scale else None),
                        format_func=lambda value:'Tinta uniforme · sin escala' if value is None else value,
                        key=key+'_element_scale_'+selected+'_'+eid)
                    target=style.setdefault('visualization',{}).setdefault('style',{})
                    target['color']=st.color_picker('Tinta de visualización',target.get('color','#13bfd1'))
                    target['background']=st.color_picker('Fondo de visualización',target.get('background','#04151e'))
                    target['text']=st.color_picker('Texto de visualización',target.get('text','#f0f5f8'))
                    declaration=color_scale_inputs(scale_palette or 'Earth',current=current_scale,
                        key=key+'_element_scale_fields_'+selected+'_'+eid,all_fields=True)
                    if scale_palette is None: target.pop('color_scale',None)
                    else: target['color_scale']=declaration
                if element['type'] in ('text','source'):
                    if not element.get('data_binding'): style['text']=st.text_area('Contenido',style.get('text',''),max_chars=2000)
                    style['font_size']=st.number_input('Tamaño de letra',8,400,int(style.get('font_size',40)))
                    style['bold']=st.checkbox('Peso destacado · SemiBold / Bold',style.get('bold',False))
                    alignments=['left','center','right']
                    style['alignment']=st.selectbox('Alineación',alignments,index=alignments.index(style.get('alignment','left')))
                    style['color']=st.color_picker('Color',style.get('color','#f0f5f8'))
                elif element['type'] in ('shape','background'):
                    style['fill']=st.color_picker('Relleno',style.get('fill','#13bfd1'))
                    shapes=['rectangle','rounded_rectangle','circle','line','divider']
                    style['shape']=st.selectbox('Forma',shapes,index=shapes.index(style.get('shape','rectangle')))
                elif element['type'] in ('image','logo','video'):
                    style['fit']=st.selectbox('Encuadre',['contain','cover'],index=['contain','cover'].index(style.get('fit','contain')))
                    if element['type']=='video':
                        metadata=studio['media'][style['asset_id']]
                        style['trim_in']=st.number_input('Trim in · segundos',0.,float(metadata['duration']),float(style.get('trim_in',0)),step=1/30)
                        style['trim_out']=st.number_input('Trim out · segundos',0.,float(metadata['duration']),float(style.get('trim_out',metadata['duration'])),step=1/30)
                        style['loop']=st.checkbox('Repetir clip',style.get('loop',False))
                        style['mute']=st.checkbox('Silenciar audio del clip',style.get('mute',True))
                        style['volume']=st.slider('Volumen del clip',0.,2.,float(style.get('volume',1)),step=.05)
                        st.caption('1 = volumen original. La mezcla limita picos y conserva trim/repetición; el preview audiovisual permite escucharla.')
                style['opacity']=st.slider('Opacidad',0.,1.,float(style.get('opacity',1)),step=.05)
                angle=None
                if element['type'] in ('image','video','logo','map','shape','background'):
                    angle=st.number_input('Rotación · grados horarios',-360.,360.,float(element.get('transform',{}).get('rotation',0)),step=1.)
                modes=['none','fade','slide','scale','wipe']
                incoming=st.selectbox('Entrada',modes,index=modes.index(animation.get('in','none')))
                outgoing=st.selectbox('Salida',modes,index=modes.index(animation.get('out','none')))
                anim_duration=st.number_input('Duración de animación · segundos',0.,300.,float(animation.get('duration',.5)),step=.1)
                delay=st.number_input('Retraso de entrada · segundos',0.,300.,float(animation.get('delay',0)),step=.1)
                if st.form_submit_button('Aplicar propiedades',disabled=element.get('locked',False)):
                    elements=copy.deepcopy(scene['elements']);changed=next(e for e in elements if e['id']==eid)
                    changed.update(style=style,animation={'in':incoming,'out':outgoing,'duration':anim_duration,'delay':delay})
                    if angle is not None: changed.setdefault('transform',{})['rotation']=angle
                    if font_role is not None: changed['typography_role']=font_role
                    accept(edit_scene(project,'update',selected,elements=elements))
        if st.button('Añadir forma',key=key+'_shape'):
            element=Element(id='element.'+uuid.uuid4().hex,type='shape',name='Forma',
                transform={'x':20,'y':20,'width':min(300,profile.width-40),'height':min(180,profile.height-40)},
                z_index=max((e.get('z_index',0) for e in scene['elements']),default=0)+1).to_dict()
            accept(edit_scene(project,'update',selected,elements=scene['elements']+[element]))

    try:
        prepared=PreparedTimeline(project)
        with AssetFrames(studio['media'],cache=cache.media) as assets:
            view=cache.for_timeline(prepared,assets)
            payload=view.canvas(selected,canvas_payload)
            import hashlib
            revision=hashlib.sha256(json.dumps(project,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()
            payload['recovery_key']='ecuador-vivo-canvas:'+revision+':'+selected
            component_key=key+'_canvas_'+selected+'_'+str(version)
            def applied():
                message=st.session_state.get(component_key,{}).get('applied')
                if not message or message.get('scene')!=selected: return
                try:
                    candidate=patch_canvas(st.session_state[state_key],selected,message['entries'])
                    action=message.get('action')
                    ids=message.get('selection',[])
                    if not isinstance(ids,list) or any(not isinstance(i,str) for i in ids): raise ValueError('Selección inválida.')
                    if action=='duplicate': candidate=duplicate_elements(candidate,selected,ids)
                    elif action in ('group','ungroup'): candidate=group_elements(candidate,selected,ids,action=action)
                    elif action=='copy':
                        current=next(s for s in candidate['studio']['scenes'] if s['id']==selected)
                        st.session_state[key+'_clipboard']=copy.deepcopy([e for e in current['elements'] if e['id'] in ids])
                    elif action=='paste': candidate=duplicate_elements(candidate,selected,[],elements=st.session_state.get(key+'_clipboard',[]))
                    elif action=='generate': st.session_state[key+'_review']=True
                    commit(candidate)
                except (ValueError,KeyError,TypeError,OSError) as error: st.session_state[key+'_error']=str(error)
            mount_canvas(payload,key=component_key,on_applied_change=applied)
            thumbnails=view.thumbnails()
            timeline_key=key+'_timeline_'+str(version)
            def timeline_changed():
                message=st.session_state.get(timeline_key,{}).get('changed')
                if not message: return
                try:
                    if message['action']=='select':
                        if message['id'] not in studio['timeline']: raise ValueError('Escena desconocida.')
                        st.session_state[key+'_selected']=message['id'];st.session_state.pop(key+'_frame',None)
                    elif message['action']=='reorder': commit(edit_scene(st.session_state[state_key],'reorder',order=message['order']))
                    elif message['action']=='seek':
                        target=message['frame']
                        if type(target) is not int or not 0<=target<rows[-1]['end_frame']: raise ValueError('Playhead fuera de límites.')
                        st.session_state[key+'_frame']=target
                        st.session_state[key+'_selected']=next(r['id'] for r in rows if r['start_frame']<=target<r['end_frame'])
                except (ValueError,KeyError,TypeError,OSError) as error: st.session_state[key+'_error']=str(error)
            global _TIMELINE
            try: _TIMELINE(key=timeline_key,data={'rows':thumbnails,'selected':selected,'frame':frame},on_changed_change=timeline_changed,width='stretch',height='content')
            except StreamlitAPIException as error:
                if 'is not registered' not in str(error): raise
                _TIMELINE=st.components.v2.component('ecuador_vivo_scene_timeline',html=TIMELINE_HTML,css=TIMELINE_CSS,js=TIMELINE_JS)
                _TIMELINE(key=timeline_key,data={'rows':thumbnails,'selected':selected,'frame':frame},on_changed_change=timeline_changed,width='stretch',height='content')
            with st.expander('Preview de cuadro y exportación',expanded=st.session_state.get(key+'_review',False)):
                preview=view.preview(frame)
                st.image(preview,width=min(600,profile.width),alt=f'Preview exacto del cuadro {frame}')
                st.caption(f'Cuadro {frame} · {frame/30:.3f} s · el canvas edita el estado final; este preview aplica video y animaciones al playhead.')
                st.download_button('Descargar cuadro PNG',preview,file_name=f'ecuador-vivo-cuadro-{frame}.png',mime='image/png',key=key+'_png')
                st.download_button('Descargar proyecto Studio',json.dumps(project,ensure_ascii=False,indent=2),file_name='ecuador-vivo-studio.json',mime='application/json',key=key+'_json')
                if st.button('Exportar timeline MP4',key=key+'_export'):
                    from studio_jobs import start_studio_job
                    st.session_state[key+'_job']=str(start_studio_job(project))
                    st.rerun()
                if st.button('Preparar preview audiovisual',key=key+'_av_preview'):
                    from studio_jobs import start_studio_job
                    st.session_state[key+'_job']=str(start_studio_job(project))
                    st.rerun()
                job_value=st.session_state.get(key+'_job')
                if job_value:
                    job=Path(job_value);status=read_json(job/'status.json',{})
                    st.caption(status.get('message','Preparando exportación'))
                    if status.get('state') in ('queued','running'):
                        st.progress(float(status.get('progress',0)))
                        if st.button('Actualizar estado',key=key+'_poll'): st.rerun()
                        if st.button('Cancelar exportación',key=key+'_cancel'): (job/'cancel.request').write_text('cancel',encoding='utf-8');st.rerun()
                    elif status.get('state')=='complete':
                        import hashlib
                        receipt=read_json(job/'receipt.json',{})
                        current_hash=revision
                        if receipt.get('project_sha256')!=current_hash:
                            st.warning('Este preview y sus descargas corresponden a una versión anterior. Prepara el preview audiovisual para escuchar los cambios actuales.')
                        else: st.caption('Preview audiovisual y descarga usan exactamente el mismo MP4.')
                        st.video(str(job/'video.mp4'))
                        st.download_button('Descargar MP4',(job/'video.mp4').read_bytes(),file_name='ecuador-vivo-studio.mp4',mime='video/mp4',key=key+'_mp4')
                        st.download_button('Descargar receipt',(job/'receipt.json').read_bytes(),file_name='receipt.json',mime='application/json',key=key+'_receipt')
                    elif status.get('state') in ('failed','cancelled'): st.warning(status.get('message'))
    except (ValueError,TypeError,KeyError,OSError) as error: st.error(str(error))
    if st.session_state.get(key+'_draft'): st.caption('Borrador guardado: '+st.session_state[key+'_draft'])
    if st.session_state.get(key+'_error'): st.error(st.session_state.pop(key+'_error'))
