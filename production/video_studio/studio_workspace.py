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

def _register():
    return st.components.v2.component('ecuador_vivo_workspace',
        html=(ASSETS/'workspace.html').read_text(encoding='utf-8'),
        css=layout_editor.CSS+'\n'+(ASSETS/'workspace.css').read_text(encoding='utf-8-sig'),
        js=layout_editor.JS.replace('export default function(component)','function mountCanvas(component)',1)+'\n'+(ASSETS/'workspace.js').read_text(encoding='utf-8'))

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
        prepared=PreparedTimeline(candidate)
        with AssetFrames(candidate['studio']['media'],cache=self.cache.media) as assets:self.cache.for_timeline(prepared,assets).thumbnails()
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

def show_workspace(source_project,*,key='free_studio',snapshot=None,canonical=False):
    global _COMPONENT
    try:session=WorkspaceSession(st.session_state,key,source_project,canonical=canonical)
    except (ValueError,TypeError,KeyError,OSError) as error:st.error('No se pudo abrir el workspace: '+str(error));return
    component_key=key+'_workspace'
    def changed():
        message=st.session_state.get(component_key,{}).get('command')
        if not message:return
        try:
            action=message['action']
            if action=='navigate':
                if message['phase'] not in ('Inicio','SIG','Datos','Maqueta','Montaje','Exportar'):raise ValueError('Ruta desconocida.')
                session.dispatch({**message,'action':'save'})
                if message['phase'] in ('Inicio','SIG'):st.session_state['section']=message['phase']
                else:st.session_state['studio_phase']=message['phase']
                return
            if action=='status':return
            if action=='upload':
                session.dispatch({**message,'action':'save'});st.session_state[key+'_dialog']='upload';return
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
            if action in ('regenerate','regenerate_structure','temporal_map'):
                session.dispatch({**message,'action':'save'})
                st.session_state[key+'_dialog']=action;return
            if action=='paste':message={**message,'elements':st.session_state.get(key+'_clipboard',[]),'map_instances':st.session_state.get(key+'_clipboard_maps',{})}
            if action=='cancel':
                job=st.session_state.get(key+'_job')
                if job: (Path(job)/'cancel.request').touch()
                return
            session.dispatch(message)
            if action in ('play','export'):
                from studio_jobs import start_studio_job
                job=st.session_state.get(key+'_job');status=read_json(Path(job)/'status.json',{}) if job else {}
                if job and st.session_state.get(key+'_job_hash')==document_hash(session.project) and status.get('state') in ('queued','running','complete'):return
                st.session_state[key+'_job']=str(start_studio_job(session.project));st.session_state[key+'_job_hash']=document_hash(session.project)
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
        prepared=PreparedTimeline(project)
        with AssetFrames(studio['media'],cache=session.cache.media) as assets:
            view=session.cache.for_timeline(prepared,assets);payload=view.canvas(session.selected,canvas_payload)
            rows=view.thumbnails();row=next(r for r in rows if r['id']==session.selected)
            frame=st.session_state.get(key+'_frame',row['start_frame'])
            if not row['start_frame']<=frame<row['end_frame']:frame=row['start_frame']
            payload.update(rows=rows,frame=frame,preview='data:image/png;base64,'+base64.b64encode(view.preview(frame)).decode())
        digest=document_hash(project)
        payload.update(workspace_mode=True,version=session.version,scene_data=scene,project=project,
            command_ack=st.session_state.get(key+'_command_ack',0),
            recovery_key='ecuador-vivo-canvas:'+digest+':'+session.selected,ui_key='ecuador-vivo-workspace:'+key,
            can_undo=bool(st.session_state[key+'_workspace_history']),can_redo=bool(st.session_state[key+'_workspace_future']),
            saved_at=st.session_state.get(key+'_saved_at',''),error=st.session_state.pop(key+'_error',''),notice=st.session_state.pop(key+'_notice',''),
            templates=TEMPLATES,themes=list(THEMES),typography=list(TYPOGRAPHY),palettes=PALETTES,
            font_families=list(FONT_FAMILIES),font_roles=FONT_ROLES,profiles={pid:label for pid,(label,_,_) in PRESETS.items()},
            template_bindings=TEMPLATE_BINDINGS,template_results={t:template_result_ids(t,studio['calculations']) for t in TEMPLATE_BINDINGS},
            recovery=[{'path':str(p),'name':p.name} for p in list_snapshots(session.store/'projects')],
            can_attach=snapshot is not None)
        from studio_temporal import calendar_receipt
        payload['scientific_calendar'] = calendar_receipt(project,prepared.rows)
        payload['map_thumbnails'] = {}
        # The same verified decoder/cache supplies thumbnails; no extra image assets.
        with AssetFrames(studio['media'],cache=session.cache.media) as assets:
            for aid,record in studio['media'].items():
                if 'temporal_map' not in record: continue
                element = {'id':'thumbnail.'+aid,'type':'video','style':{'asset_id':aid}}
                image = assets.at(0,[element])['video.'+element['id']].copy()
                image.thumbnail((160,284))
                import io
                buffer=io.BytesIO(); image.save(buffer,format='PNG'); image.close()
                payload['map_thumbnails'][aid]='data:image/png;base64,'+base64.b64encode(buffer.getvalue()).decode()
                cursor=assets.cursors.pop((element['id'],aid))
                cursor['reader'].close()
                if cursor['frame'] is not None: cursor['frame'].close()
        job=st.session_state.get(key+'_job');payload['job']=read_json(Path(job)/'status.json',{}) if job else {}
        payload['job_stale']=bool(job and st.session_state.get(key+'_job_hash')!=digest)
        if job and payload['job'].get('state')=='complete' and not payload['job_stale']:
            from studio_delivery import register_movie
            payload['movie_url']=register_movie(job)
            payload['receipt']=read_json(Path(job)/'receipt.json')
        if _COMPONENT is None:_COMPONENT=_register()
        try:_COMPONENT(key=component_key,data=payload,on_command_change=changed,width='stretch',height='content')
        except StreamlitAPIException as error:
            if 'is not registered' not in str(error):raise
            _COMPONENT=_register();_COMPONENT(key=component_key,data=payload,on_command_change=changed,width='stretch',height='content')
    except (ValueError,TypeError,KeyError,OSError) as error:st.error('No se pudo dibujar la escena: '+str(error));return

    if st.session_state.get(key+'_dialog'):
        @st.dialog({'upload':'Importar multimedia','project':'Abrir proyecto JSON','preview':'Preview audiovisual','regenerate':'Propuesta de escena','regenerate_structure':'Propuesta de estructura científica','temporal_map':'Mapa temporal y calendario científico'}[st.session_state[key+'_dialog']],width='medium',
                   on_dismiss=lambda:st.session_state.pop(key+'_dialog',None))
        def upload_dialog():
            mode=st.session_state[key+'_dialog']
            if mode=='temporal_map':
                from studio_map_ui import show_map_dialog
                show_map_dialog(session,key)
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
                job=Path(st.session_state[key+'_job']);movie=job/'video.mp4'
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
