"""Run the actual canonical SIG workspace, rather than a disconnected demo."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import streamlit as st
from studio_home import create_project
from studio_project import publish_document,workspace_key,source_projection
from studio_workspace import WorkspaceSession
from studio_sig_map_ui import show_sig_map

st.set_page_config(layout='wide')
if 'project_document' not in st.session_state:
    publish_document(st.session_state,create_project('free',{'id':'custom','width':640,'height':360},name='SIG adapter local example'))
project=st.session_state['project_document']
session=WorkspaceSession(st.session_state,workspace_key(project),source_projection(project),canonical=True)
show_sig_map(session)
