"""Local browser fixture: a named test copy fails visual preparation only.

Run on a separate loopback test port; never used by the normal launcher.
No source file, project validation or renderer behavior is changed on disk.
"""
from pathlib import Path
import sys

PRODUCTION=Path(__file__).resolve().parents[1]/'production/video_studio'
sys.path.insert(0,str(PRODUCTION))
import studio_cache

original=studio_cache._PreviewSession.preview
if not getattr(original,'_visual_failure_fixture',False):
    def preview(self,frame):
        if self.prepared.project.get('name','').startswith('Prueba de fallo visual'):
            raise RuntimeError('Fallo controlado de preparación visual (sesión de prueba)')
        return original(self,frame)
    preview._visual_failure_fixture=True
    studio_cache._PreviewSession.preview=preview

import streamlit as st
from starlette.routing import Route
from studio_server import movie_route,raster_route,job_route
app=st.App(PRODUCTION/'app.py',routes=[
    Route('/studio-media/{token}',movie_route,methods=['GET','HEAD']),
    Route('/sig-display/{token}',raster_route,methods=['GET']),
    Route('/studio-status/{token}',job_route,methods=['GET'])])
