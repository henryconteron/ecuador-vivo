"""Viewport workspace over existing Scene/Element, render and durable snapshots."""
import base64
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import uuid
import streamlit as st
from streamlit.errors import StreamlitAPIException
from model import STORE
from jobs import read_json
from studio_editing import new_workspace, attach_snapshot, timeline_rows
from studio_workspace_commands import workspace_command
from studio_recovery import save_snapshot, recover_snapshot, list_snapshots
from studio_cache import StudioPreviewCache
from studio_media import AssetFrames, import_asset
from studio_timeline import PreparedTimeline
from studio_ui import canvas_payload
from studio_templates import TEMPLATES, THEMES, TYPOGRAPHY, PALETTES, TEMPLATE_BINDINGS, template_result_ids
from studio_typography import FONT_FAMILIES, FONT_ROLES
from output_profiles import PRESETS
import layout_editor

ASSETS=Path(__file__).with_name('workspace_frontend')
SOURCE_MTIME=Path(__file__).stat().st_mtime_ns
SOURCE_ASSET_MTIMES=tuple((ASSETS/name).stat().st_mtime_ns for name in ('workspace.html','workspace.css','resource_workspace.css','workspace_windows.js','resource_workspace.js','workspace.js'))

def _register():
    """Register presentation assets once; normal progress updates reuse the root."""
    return st.components.v2.component('ecuador_vivo_workspace',
        html=(ASSETS/'workspace.html').read_text(encoding='utf-8'),
        css=layout_editor.CSS+'\n'+(ASSETS/'workspace.css').read_text(encoding='utf-8-sig')+'\n'+(ASSETS/'resource_workspace.css').read_text(encoding='utf-8'),
        js=layout_editor.JS.replace('export default function(component)','function mountCanvas(component)',1)+'\n'+(ASSETS/'workspace_windows.js').read_text(encoding='utf-8')+'\n'+(ASSETS/'resource_workspace.js').read_text(encoding='utf-8')+'\n'+(ASSETS/'workspace.js').read_text(encoding='utf-8'))

_COMPONENT=None

def document_hash(project):
    return hashlib.sha256(json.dumps(project,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()

class WorkspaceSession:
    """Transaction boundary reusable by UI and tests. Save before state/history."""
    def __init__(self,state,key,source,store=None,canonical=False):
        self.state=state;self.key=key;self.store=Path(store or STORE);self.canonical=canonical
        if canonical:
            from studio_project import synchronize_source
            document=synchronize_source(state,source)
            previous=state.get(key+'_document')
            if previous is not None and previous != document:
                state[key+'_version']=state.get(key+'_version',0)+1
                state[key+'_workspace_history']=[];state[key+'_workspace_future']=[]
            state[key+'_document']=document
        if key+'_document' not in state:state[key+'_document']=new_workspace(source)
        state.setdefault(key+'_version',0);state.setdefault(key+'_workspace_history',[]);state.setdefault(key+'_workspace_future',[])
        if not isinstance(state.get(key+'_preview_cache'),StudioPreviewCache):state[key+'_preview_cache']=StudioPreviewCache()
        if not state.get(key+'_draft'):
            destination=self.new_draft();save_snapshot(destination,self.project);state[key+'_draft']=str(destination)
        if self.selected not in self.project['studio']['timeline']:state[key+'_selected']=self.project['studio']['timeline'][0]
    @property
    def project(self):return self.state['project_document'] if self.canonical else self.state[self.key+'_document']
    @property
    def selected(self):return self.state.get(self.key+'_selected',self.project['studio']['timeline'][0])
    @property
    def version(self):return self.state[self.key+'_version']
    @property
    def cache(self):return self.state[self.key+'_preview_cache']
    def new_draft(self):return self.store/'projects'/('borrador-studio-'+dt.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]+'.json')
    def commit(self,candidate,record=True,new_draft=False):
        if self.canonical:
            from studio_project import prepare_commit
            candidate=prepare_commit(candidate,self.project)
        prepared=self.cache.prepare(candidate)
        # Structural/scientific integrity and budgets precede the durable save.
        # Miniatures and preview pixels are presentation work, prepared later.
        with AssetFrames(candidate['studio']['media']) as assets:
            assets.check_budget([e for s in candidate['studio']['scenes'] for e in s['elements']])
            self.cache.validate_presentation(prepared,assets)
        path=self.new_draft() if new_draft else Path(self.state[self.key+'_draft'])
        save_snapshot(path,candidate)
        if record:
            history=self.state[self.key+'_workspace_history'];history.append(copy.deepcopy(self.project));del history[:-20]
            self.state[self.key+'_workspace_future'].clear()
        if self.canonical:
            from studio_project import publish_document
            publish_document(self.state,candidate)
        self.state[self.key+'_document']=candidate;self.state[self.key+'_draft']=str(path)
        self.state[self.key+'_version']+=1
        self.state[self.key+'_saved_at']=dt.datetime.now().strftime('%H:%M:%S')
        if self.selected not in candidate['studio']['timeline']:self.state[self.key+'_selected']=candidate['studio']['timeline'][0]
    def dispatch(self,message):
        if message.get('version')!=self.version:raise ValueError('El documento cambió. Revisa la escena y vuelve a intentar.')
        action=message['action']
        if message.get('scene')!=self.selected:raise ValueError('La selección de escena cambió.')
        if action in ('undo','redo'):
            name='history' if action=='undo' else 'future';other='future' if action=='undo' else 'history'
            stack=self.state[self.key+'_workspace_'+name]
            if not stack:return
            previous=copy.deepcopy(self.project);self.commit(copy.deepcopy(stack[-1]),record=False)
            self.state[self.key+'_workspace_'+other].append(previous);stack.pop();return
        candidate=workspace_command(self.project,self.selected,message)
        # Navigation validation precedes accepting pending geometry/history.
        if action=='select' and message.get('id') not in candidate['studio']['timeline']:raise ValueError('Escena desconocida.')
        if action=='seek':
            rows=timeline_rows(candidate['studio']);frame=message.get('frame')
            if type(frame) is not int or not 0<=frame<rows[-1]['end_frame']:raise ValueError('Tiempo fuera de la timeline.')
        if candidate!=self.project:self.commit(candidate,new_draft=action=='project_new')
        if action in ('scene_add','template'):self.state[self.key+'_selected']=candidate['studio']['timeline'][-1]
        if action=='scene_duplicate':self.state[self.key+'_selected']=candidate['studio']['timeline'][candidate['studio']['timeline'].index(self.selected)+1]
        if action=='project_new':self.state[self.key+'_selected']=candidate['studio']['timeline'][0]
        if action=='select':
            if message['id'] not in candidate['studio']['timeline']:raise ValueError('Escena desconocida.')
            self.state[self.key+'_selected']=message['id'];self.state.pop(self.key+'_frame',None)
        if action=='seek':
            self.state[self.key+'_frame']=frame
            self.state[self.key+'_selected']=next(r['id'] for r in rows if r['start_frame']<=frame<r['end_frame'])
        if action=='copy':
            scene=next(s for s in candidate['studio']['scenes'] if s['id']==self.selected)
            selected=[e for e in scene['elements'] if e['id'] in message.get('ids',[])]
            instances={e['temporal_binding']['instance_id'] for e in selected if e.get('temporal_binding')}
            for iid in instances:
                channels={e['temporal_binding']['channel'] for e in selected if e.get('temporal_binding',{}).get('instance_id')==iid}
                if {'continent','galapagos'}<=channels:
                    selected+=[e for e in scene['elements'] if e.get('temporal_binding',{}).get('instance_id')==iid and e not in selected]
            self.state[self.key+'_clipboard']=copy.deepcopy(selected)
            self.state[self.key+'_clipboard_maps']={iid:copy.deepcopy(scene['map_instances'][iid]) for iid in instances}

@st.fragment
def show_workspace(source_project,*,key='free_studio',snapshot=None,canonical=False):
    global _COMPONENT
    # Fragment reruns retain their original arguments. Use the current canonical
    # compatibility view, otherwise a committed rename is overwritten by it.
    if canonical:source_project=st.session_state.get('project',source_project)
    try:session=WorkspaceSession(st.session_state,key,source_project,canonical=canonical)
    except (ValueError,TypeError,KeyError,OSError) as error:st.error('No se pudo abrir el workspace: '+str(error));return
    if st.session_state.pop(key+'_navigate_app',False):st.rerun(scope='app')
    component_key=key+'_workspace'
    st.html(ASSETS/'host.css')
    def changed():
        message=st.session_state.get(component_key,{}).get('command')
        if not message:return
        try:
            action=message['action']
            if action!='status':st.session_state.pop(key+'_error',None)
            if action=='resource_asset':
                from studio_scientific_library import scientific_objects,insert_bioicon
                if not any(r['id']==message.get('resource_id') and r['type']=='asset' for r in scientific_objects()):raise ValueError('Ilustración desconocida.')
                session.dispatch({**message,'action':'save'})
                session.commit(insert_bioicon(session.project,session.selected,message['resource_id']));return
            if action=='resource_tool':
                from studio_resource_tool_import import TOOLS
                if message.get('tool') not in TOOLS:raise ValueError('Herramienta desconocida.')
                session.dispatch({**message,'action':'save'})
                st.session_state[key+'_tool']=message['tool'];st.session_state[key+'_tool_element']=message.get('element_id')
                st.session_state[key+'_dialog']='resource_tool';return
            if action in ('resource_open','resource_blank','resource_send'):
                from studio_resource_workbench import resource_command
                target=resource_command(session,message)
                if target is not None:
                    from studio_project import replace_document,workspace_key
                    published=replace_document(st.session_state,target)
                    st.session_state[workspace_key(published)+'_selected']=published['studio']['timeline'][-1]
                    st.session_state.pop('_pending_studio_navigation',None)
                    st.session_state['section']='Editor';st.session_state['studio_phase']='Estudio'
                    st.session_state[key+'_navigate_app']=True
                return
            if action=='navigate':
                if message['phase'] not in ('Inicio','SIG','Studio','Recursos','Datos','Maqueta','Montaje','Exportar'):raise ValueError('Ruta desconocida.')
                session.dispatch({**message,'action':'save'})
                if message['phase']=='Studio':st.session_state['section']='Editor';st.session_state['studio_phase']='Estudio'
                elif message['phase'] in ('Inicio','SIG','Recursos'):st.session_state['section']=message['phase']
                else:st.session_state['studio_phase']=message['phase']
                st.session_state[key+'_navigate_app']=True
                return
            if action=='status':return
            if action=='publication':
                if message.get('version')!=session.version:raise ValueError('El proyecto cambió; revisa el video final actualizado.')
                from studio_publication import prepare_publication
                job=st.session_state.get(key+'_job')
                if not job or read_json(Path(job)/'status.json',{}).get('state')!='complete':raise ValueError('Exporta primero el MP4 final.')
                with st.spinner('Comprobando video, mapas y evidencia pública…'):
                    path=prepare_publication(job,session.project)
                st.session_state[key+'_publication']={'path':str(path),'project_hash':document_hash(session.project)}
                st.session_state[key+'_notice']='Paquete público preparado. No se publicó ni se subió a GitHub.'
                return
            if action=='upload':
                session.dispatch({**message,'action':'save'});st.session_state[key+'_dialog']='upload';return
            if action=='voice_captions':
                session.dispatch({**message,'action':'save'});st.session_state[key+'_dialog']='voice_captions';return
            if action=='save_resource':
                session.dispatch({**message,'action':'save'});st.session_state[key+'_dialog']='save_resource';return
            if action=='edit_blender':
                session.dispatch({**message,'action':'save'})
                if not session.canonical:
                    st.session_state[key+'_dialog']='resource_3d';return
                st.session_state['resource_3d_scene']=session.selected
                st.session_state['resource_library_view']='3d'
                st.session_state['section']='Recursos'
                st.session_state[key+'_navigate_app']=True
                return
            if action=='resource_insert':
                from studio_resources import insert_resource
                session.dispatch({**message,'action':'save'})
                candidate=insert_resource(session.project,message.get('resource_id'))
                session.commit(candidate)
                st.session_state[key+'_selected']=candidate['studio']['timeline'][-1]
                return
            if action=='attach':
                from visualization_ui import scientific_identity
                if not snapshot or scientific_identity(source_project)!=snapshot['scientific_identity']:raise ValueError('Carga una revisión vigente en Maqueta → Visualizaciones.')
                session.commit(attach_snapshot(session.project,snapshot));return
            if action=='recover':
                chosen=Path(message['path'])
                if chosen not in list_snapshots(session.store/'projects'):raise ValueError('Borrador desconocido.')
                candidate,previous=recover_snapshot(chosen);session.commit(candidate,new_draft=True)
                st.session_state[key+'_workspace_history'].clear();st.session_state[key+'_workspace_future'].clear()
                st.session_state[key+'_selected']=candidate['studio']['timeline'][0]
                st.session_state[key+'_notice']='Copia recuperada'+(' desde la versión anterior.' if previous else '.');return
            if action=='import_project':
                session.dispatch({**message,'action':'save'});st.session_state[key+'_dialog']='project';return
            if action=='native_preview':
                session.dispatch({**message,'action':'save'});st.session_state[key+'_dialog']='preview';return
            if action=='review_map_layers':
                session.dispatch({**message,'action':'save'})
                aid=message.get('asset_id')
                if session.project['studio']['media'].get(aid,{}).get('kind')!='temporal_map':
                    raise ValueError('Selecciona un mapa de capas de la biblioteca.')
                st.session_state.pop(key+'_layer_review_base',None)
                st.session_state[key+'_layer_review_asset']=aid
                st.session_state[key+'_dialog']='map_layers';return
            if action in ('regenerate','regenerate_structure','temporal_map','temporal_layers'):
                session.dispatch({**message,'action':'save'})
                st.session_state.pop(key+'_layer_review_base',None)
                st.session_state[key+'_dialog']=action;return
            if action=='paste':message={**message,'elements':st.session_state.get(key+'_clipboard',[]),'map_instances':st.session_state.get(key+'_clipboard_maps',{})}
            if action=='cancel':
                suffix='_preview_job' if st.session_state.get(key+'_active_job_kind')=='preview' else '_job'
                job=st.session_state.get(key+suffix)
                if job: (Path(job)/'cancel.request').touch()
                return
            session.dispatch(message)
            if action in ('play','export'):
                from studio_jobs import start_studio_job,preview_identity
                mode='preview' if action=='play' else 'final'
                suffix='_preview_job' if mode=='preview' else '_job'
                identity=preview_identity(session.project) if mode=='preview' else document_hash(session.project)
                st.session_state[key+'_active_job_kind']=mode
                job=st.session_state.get(key+suffix);status=read_json(Path(job)/'status.json',{}) if job else {}
                if job and st.session_state.get(key+suffix+'_hash')==identity and status.get('state') in ('queued','running','complete'):return
                st.session_state[key+suffix]=str(start_studio_job(session.project,mode=mode));st.session_state[key+suffix+'_hash']=identity
        except (ValueError,TypeError,KeyError,OSError) as error:st.session_state[key+'_error']=str(error)
        finally:
            # Acknowledge non-document actions too. Their controlled render must
            # release frontend busy state even when project pixels are identical.
            st.session_state[key+'_command_ack']=st.session_state.get(key+'_command_ack',0)+1

    project=session.project;studio=project['studio'];scene=next(s for s in studio['scenes'] if s['id']==session.selected)
    if any(next(s for s in studio['scenes'] if s['id']==sid).get('renderer','studio')!='studio' for sid in studio['timeline']):
        st.warning('Timeline mixta: conserva el montaje anterior y activa escenas libres.')
        if st.button('Editar solo escenas libres'):
            session.commit(workspace_command(project,session.selected,{'action':'separate_timeline'}));st.rerun()
        return
    try:
        rows=timeline_rows(studio);row=next(r for r in rows if r['id']==session.selected)
        frame=st.session_state.get(key+'_frame',row['start_frame'])
        if not row['start_frame']<=frame<row['end_frame']:frame=row['start_frame']
        payload,visual_pending=session.cache.workspace_products(project,session.selected,frame,canvas_payload)
        canvas_frame=payload['frame']
        payload.update(visual_pending=visual_pending,canvas_frame=canvas_frame,
            preview='data:image/png;base64,'+base64.b64encode(payload['preview']).decode())
        # Geometry is immediately authoritative; retained tiles keep their last
        # valid pixels until an affected scene finishes. No new date is claimed.
        if payload['scene']==session.selected:
            elements={e['id']:e for e in scene['elements']}
            for layer in payload['layers']:
                element=elements.get(layer['id'])
                if not element:continue
                t=element['transform']
                layer.update(x=t['x'],y=t['y'],w=t['width'],h=t['height'],
                    label=element.get('name',layer['label']),hidden=not element.get('visible',True),
                    deleted=element.get('editor_deleted',False),locked=element.get('locked',False))
                layer['original'].update(x=t['x'],y=t['y'],w=t['width'],h=t['height'])
        thumbnails={r['id']:r['thumbnail'] for r in payload['rows']}
        payload['rows']=[{**r,'thumbnail':thumbnails.get(r['id'],'')} for r in rows]
        digest=document_hash(project)
        payload.update(workspace_mode=True,version=session.version,scene=session.selected,scene_data=scene,project=project,
            command_ack=st.session_state.get(key+'_command_ack',0),
            recovery_key='ecuador-vivo-canvas:'+digest+':'+session.selected,ui_key='ecuador-vivo-workspace:'+key,
            can_undo=bool(st.session_state[key+'_workspace_history']),can_redo=bool(st.session_state[key+'_workspace_future']),
            saved_at=st.session_state.get(key+'_saved_at',''),error=st.session_state.get(key+'_error',''),visual_error=session.cache.visual_error or '',notice=st.session_state.pop(key+'_notice',''),
            templates=TEMPLATES,themes=list(THEMES),typography=list(TYPOGRAPHY),palettes=PALETTES,
            font_families=list(FONT_FAMILIES),font_roles=FONT_ROLES,profiles={pid:label for pid,(label,_,_) in PRESETS.items()},
            template_bindings=TEMPLATE_BINDINGS,template_results={t:template_result_ids(t,studio['calculations']) for t in TEMPLATE_BINDINGS},
            recovery=[{'path':str(p),'name':p.name} for p in list_snapshots(session.store/'projects')],
            can_attach=snapshot is not None)
        payload['map_thumbnails'] = {}
        from studio_resources import RESOURCE_CATALOG
        from studio_resource_projects import is_resource
        from studio_resource_actions import GRAPHIC_ELEMENTS
        payload['resource_mode']=is_resource(project)
        if payload['resource_mode']:
            from studio_scientific_library import scientific_objects,installed_engines
            from studio_resource_projects import resource_files
            payload['scientific_objects']=scientific_objects()
            payload['resource_engines']=installed_engines()
            payload['saved_resources']=[{'path':str(r['path']),'name':r['name'],'category':r['category']} for r in resource_files(session.store)]
            from studio_scientific_library import scientific_templates
            payload['explanation_catalog']=scientific_templates(studio['output_profile'])
        payload['graphic_elements']=GRAPHIC_ELEMENTS
        payload['explanation_resources']=[{'id':r['id'],'name':r['name'],'summary':r['summary']} for r in RESOURCE_CATALOG]
        from studio_jobs import preview_identity
        mode=st.session_state.get(key+'_active_job_kind','preview')
        suffix='_preview_job' if mode=='preview' else '_job'
        job=st.session_state.get(key+suffix);payload['job']=read_json(Path(job)/'status.json',{}) if job else {}
        identity=preview_identity(project) if mode=='preview' else digest
        payload['job_stale']=bool(job and st.session_state.get(key+suffix+'_hash')!=identity)
        payload['delivery_kind']=mode
        if job and not payload['job_stale']:
            from studio_delivery import register_job_status
            payload['job_status_url']=register_job_status(job)
        if job and payload['job'].get('state')=='complete' and not payload['job_stale']:
            from studio_delivery import register_movie
            payload['movie_url']=register_movie(job)
            payload['receipt']=read_json(Path(job)/'receipt.json')
        publication=st.session_state.get(key+'_publication')
        if publication and publication['project_hash']==digest and Path(publication['path']).is_file():
            from studio_delivery import register_publication
            payload['publication_url']=register_publication(publication['path'])
        if _COMPONENT is None:_COMPONENT=_register()
        try:_COMPONENT(key=component_key,data=payload,on_command_change=changed,width='stretch',height='content')
        except StreamlitAPIException as error:
            if 'is not registered' not in str(error):raise
            _COMPONENT=_register();_COMPONENT(key=component_key,data=payload,on_command_change=changed,width='stretch',height='content')
    except (ValueError,TypeError,KeyError,OSError) as error:st.error('No se pudo dibujar la escena: '+str(error));return

    if st.session_state.get(key+'_dialog'):
        def dismiss_map_dialog():
            from studio_map_ui import clear_review_state
            clear_review_state(st.session_state,key)
        @st.dialog({'resource_tool':'Editor especializado · recurso compuesto','resource_3d':'Cámara y materiales 3D','save_resource':'Guardar recurso reutilizable','voice_captions':'Voz y subtítulos','upload':'Importar multimedia','project':'Abrir proyecto JSON','preview':'Preview audiovisual','regenerate':'Propuesta de escena','regenerate_structure':'Propuesta de estructura científica','temporal_map':'Mapa temporal y calendario científico','temporal_layers':'Preparar capas cartográficas','observation_layers':'Preparar observación cartográfica','map_layers':'Revisar e insertar capas'}[st.session_state[key+'_dialog']],width='large' if st.session_state[key+'_dialog'] in ('resource_3d','resource_tool') else 'medium',
                   on_dismiss=dismiss_map_dialog)
        def upload_dialog():
            if st.session_state.pop(key+'_tool_imported',False):
                st.session_state.pop(key+'_dialog',None);st.rerun(scope='app')
            mode=st.session_state[key+'_dialog']
            if mode=='resource_tool':
                from ecuador_vivo_scientific_tools import scientific_tool
                from studio_resource_tool_import import import_tool_artifact
                element=next((e for e in scene['elements'] if e['id']==st.session_state.get(key+'_tool_element')),None)
                saved=(element or {}).get('source_document',{})
                def accept_tool():
                    artifact=st.session_state.get(key+'_specialized',{}).get('artifact')
                    if artifact:
                        try:
                            artifact={**artifact,'element_id':element['id'] if element else None}
                            candidate=import_tool_artifact(session.project,session.selected,artifact)
                            session.commit(candidate);st.session_state[key+'_tool_imported']=True
                        except (ValueError,OSError,TypeError,KeyError) as error:st.session_state[key+'_error']=str(error)
                scientific_tool(st.session_state[key+'_tool'],recipe=saved.get('recipe'),key=key+'_specialized',on_artifact_change=accept_tool)
                st.caption('Se conserva el documento original. El recurso se incorpora como objeto compuesto; puedes reabrir este editor desde sus Propiedades.')
                if st.button('Cerrar y volver al lienzo',key=key+'_close_tool'):
                    st.session_state.pop(key+'_dialog',None);st.rerun(scope='app')
                return
            if mode=='resource_3d':
                from studio_blender_ui import show_blender_ui
                def accept_3d(candidate):
                    session.commit(candidate,new_draft=True)
                    st.session_state.pop(key+'_dialog',None);st.rerun(scope='app')
                show_blender_ui(session.project,accept_3d,key=key+'_blender',store=session.store)
                return
            if mode=='save_resource':
                from studio_resource_actions import show_save_resource
                show_save_resource(session,key=key+'_resource_save')
                return
            if mode=='voice_captions':
                from studio_voice_ui import show_voice_captions
                show_voice_captions(session,key=key+'_voice')
                return
            if mode=='map_layers':
                from studio_map_ui import show_layer_review
                show_layer_review(session,key,session.project['studio']['media'].get(st.session_state.get(key+'_layer_review_asset'),{}))
                return
            if mode in ('temporal_map','temporal_layers','observation_layers'):
                from studio_map_ui import show_map_dialog
                structured=mode in ('temporal_layers','observation_layers')
                index=None
                if mode=='observation_layers':
                    from studio_science import restored_snapshot
                    snapshot=restored_snapshot(session.project)
                    if snapshot is None:
                        st.error('Falta una revisión científica. Cierra y prepara o abre la revisión antes de elegir una fecha.')
                        if st.button('Cerrar preparación',key=key+'_observation_close'):dismiss_map_dialog();st.rerun()
                        return
                    dates=[row['date'] for row in snapshot['source_records']]
                    date=st.selectbox('Fecha observada',dates,key=key+'_observation_date',persist_state='session')
                    index=dates.index(date)
                show_map_dialog(session,key,representation='rgba_observation_bundle' if structured else 'opaque_prerendered_map',source_index=index)
                return
            if mode=='regenerate_structure':
                from studio_science import propose_structure,apply_structure,restore_structure
                st.caption('Regenera la secuencia desde la misma revisión científica. Conserva las escenas que elijas; las anteriores quedan archivadas y puedes deshacer.')
                theme=st.selectbox('Estilo de la propuesta',list(THEMES),key=key+'_structure_theme')
                if st.button('Preparar estructura',key=key+'_structure_propose'):
                    try:st.session_state[key+'_structure_proposal']=propose_structure(session.project,theme=theme)
                    except (ValueError,TypeError,KeyError) as error:st.error(str(error))
                proposal=st.session_state.get(key+'_structure_proposal')
                if proposal:
                    st.dataframe([{'Escena':c['name'],'Edición humana':c['modified'],
                        'Propuesta':'Regenerar' if c['after'] else 'Archivar si no se conserva'} for c in proposal['changes']],
                        hide_index=True,alt='Diferencias de estructura y escenas editadas')
                    names={c['id']:c['name'] for c in proposal['changes']}
                    preserve=st.multiselect('Conservar estas escenas',list(names),
                        default=[c['id'] for c in proposal['changes'] if c['modified']],
                        format_func=names.get,key=key+'_structure_preserve_'+proposal['base_sha256'][:12])
                    with st.expander('Diferencias completas de escenas y secuencia'):
                        st.json({'antes':proposal['before_timeline'],'después':proposal['after']['timeline'],'escenas':proposal['changes']},expanded=False)
                    if st.button('Regenerar estructura y archivar anterior',type='primary',key=key+'_structure_accept'):
                        try:
                            session.commit(apply_structure(session.project,proposal,'replace',preserve_ids=preserve))
                            st.session_state.pop(key+'_structure_proposal',None);st.session_state.pop(key+'_dialog',None);st.rerun()
                        except (ValueError,TypeError,KeyError,OSError) as error:st.error(str(error))
                if session.project['studio'].get('structure_history') and st.button('Recuperar estructura anterior',key=key+'_structure_restore'):
                    try:
                        session.commit(restore_structure(session.project))
                        st.session_state.pop(key+'_structure_proposal',None);st.session_state.pop(key+'_dialog',None);st.rerun()
                    except (ValueError,TypeError,KeyError,OSError) as error:st.error(str(error))
                if st.button('Conservar estructura actual / cancelar',key=key+'_structure_cancel'):
                    st.session_state.pop(key+'_structure_proposal',None);st.session_state.pop(key+'_dialog',None);st.rerun()
                return
            if mode=='regenerate':
                from studio_science import propose_template,apply_proposal
                template=st.selectbox('Template de la escena',list(TEMPLATES),format_func=TEMPLATES.get,key=key+'_regenerate_template')
                st.caption('La propuesta conserva los bindings. Revisa las diferencias antes de reemplazar tus textos, posiciones y estilos. La versión anterior queda recuperable.')
                if st.button('Preparar propuesta',key=key+'_regenerate_propose'):
                    try:st.session_state[key+'_proposal']=propose_template(session.project,session.selected,template)
                    except (ValueError,KeyError,TypeError) as error:st.error(str(error))
                proposal=st.session_state.get(key+'_proposal')
                if proposal:
                    st.write('Cambios propuestos: '+', '.join(c['property'] for c in proposal['changes']))
                    with st.expander('Antes y después',expanded=True):
                        st.json({'antes':proposal['before'],'después':proposal['after']},expanded=False)
                    if st.button('Regenerar y conservar versión anterior',type='primary',key=key+'_regenerate_accept'):
                        try:
                            session.commit(apply_proposal(session.project,proposal,'replace'))
                            st.session_state.pop(key+'_proposal',None);st.session_state.pop(key+'_dialog',None);st.rerun()
                        except (ValueError,KeyError,TypeError,OSError) as error:st.error(str(error))
                if st.button('Conservar edición actual / cancelar',key=key+'_regenerate_cancel'):
                    st.session_state.pop(key+'_proposal',None);st.session_state.pop(key+'_dialog',None);st.rerun()
                return
            if mode=='preview':
                suffix='_preview_job' if st.session_state.get(key+'_active_job_kind')=='preview' else '_job'
                job=Path(st.session_state[key+suffix]);movie=job/'video.mp4'
                if movie.is_file():
                    st.video(str(movie))
                    st.download_button('Descargar MP4',movie.read_bytes(),file_name='ecuador-vivo.mp4',mime='video/mp4')
                if st.button('Cerrar preview'):st.session_state.pop(key+'_dialog',None);st.rerun()
                return
            upload=st.file_uploader('Archivo local',type=['png','jpg','jpeg','webp','mp4','mov','webm','mkv'] if mode=='upload' else ['json'],key=key+'_workspace_upload')
            if st.button('Importar',disabled=upload is None,key=key+'_workspace_import'):
                try:
                    if mode=='upload':
                        asset=import_asset(upload.getvalue(),upload.name);candidate=copy.deepcopy(session.project)
                        candidate['studio']['media']['asset.'+asset['sha256']]=asset;session.commit(candidate)
                    else:
                        from studio_project import validate_document
                        candidate=json.loads(upload.getvalue())
                        # Legacy validator intentionally rejects free Studio scenes;
                        # validate its source namespace, then Studio preflight below.
                        session.commit(validate_document(candidate),new_draft=True)
                    st.session_state.pop(key+'_dialog',None);st.rerun()
                except (ValueError,TypeError,KeyError,OSError) as error:st.error(str(error))
            if st.button('Cerrar',key=key+'_workspace_close'):st.session_state.pop(key+'_dialog',None);st.rerun()
        upload_dialog()
