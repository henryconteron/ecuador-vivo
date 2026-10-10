"""Public ASGI wrapper; launch with streamlit run studio_server.py.

st.App is isolated here so traditional app.py remains supported.
https://docs.streamlit.io/develop/api-reference/server/st.app
"""
from pathlib import Path
import streamlit as st
from starlette.routing import Route
async def movie_route(request):
    from studio_delivery import movie_response
    return await movie_response(request)

async def raster_route(request):
    from studio_delivery import raster_response
    return await raster_response(request)

async def job_route(request):
    from studio_delivery import job_response
    return await job_response(request)

app=st.App(Path(__file__).with_name('app.py'),
    routes=[Route('/studio-media/{token}',movie_route,methods=['GET','HEAD']),
            Route('/sig-display/{token}',raster_route,methods=['GET']),
            Route('/studio-status/{token}',job_route,methods=['GET'])])
