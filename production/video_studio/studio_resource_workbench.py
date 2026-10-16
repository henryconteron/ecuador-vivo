"""Resources is an authoring mode of the existing editor, not another app."""
import copy
from pathlib import Path
import streamlit as st
from studio_workspace import show_workspace
from studio_resource_projects import create_resource_project,is_resource,insert_saved_resource,resource_from_scene,resource_files,load_resource

RESOURCE_KEY='scientific_resources'

def resource_draft(state,video):
    """Keep an independent, recoverable resource without replacing the video."""
    if RESOURCE_KEY+'_source' not in state:
        from studio_expedicion_templates import create_scientific_template
        state[RESOURCE_KEY+'_source']=copy.deepcopy(video) if video and is_resource(video) else create_scientific_template(
            'expedition.water_cycle',{'id':'youtube'},duration=8)
    return state[RESOURCE_KEY+'_source']

def show_resource_workbench(video):
    show_workspace(resource_draft(st.session_state,video),key=RESOURCE_KEY,canonical=False)

def resource_command(session,message):
    """Validate before saving pending geometry; return a target only on Send."""
    if message.get('version')!=session.version or message.get('scene')!=session.selected:
        raise ValueError('El recurso cambió. Revisa la selección antes de continuar.')
    action=message['action']
    if not is_resource(session.project):raise ValueError('Esta acción requiere un recurso.')
    candidate=None
    if action=='resource_open':
        if message.get('path'):
            path=Path(message['path'])
            if path not in [entry['path'] for entry in resource_files(session.store)]:raise ValueError('Recurso guardado desconocido.')
            candidate=load_resource(path,session.store)
        else:
            from studio_resources import RESOURCE_CATALOG
            rid=message.get('resource_id');entry=next((r for r in RESOURCE_CATALOG if r['id']==rid),None)
            if rid=='expedition.water_cycle':
                from studio_expedicion_templates import create_scientific_template
                candidate=create_scientific_template(rid,session.project['studio']['output_profile'],duration=8)
            else:
                if entry is None:raise ValueError('Plantilla científica desconocida.')
                candidate=create_resource_project(entry['name'],session.project['studio']['output_profile'],resource_id=rid,duration=8)
    elif action=='resource_blank':
        candidate=create_resource_project('Nueva explicación',session.project['studio']['output_profile'],duration=8)
    elif action!='resource_send':raise ValueError('Acción de recurso desconocida.')
    session.dispatch({**message,'action':'save'})
    if candidate is not None:
        session.commit(candidate,new_draft=True,record=False)
        session.state[session.key+'_workspace_history'].clear();session.state[session.key+'_workspace_future'].clear()
        session.state.pop(session.key+'_frame',None)
        return None
    resource=resource_from_scene(session.project,session.selected,session.project['name'])
    target=session.state.get('project_document')
    if target and not is_resource(target):return insert_saved_resource(target,resource)
    resource['project_meta'].pop('resource',None)
    return resource
