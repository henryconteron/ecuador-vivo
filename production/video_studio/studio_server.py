"""Public ASGI wrapper; launch with streamlit run studio_server.py.

st.App is isolated here so traditional app.py remains supported.
https://docs.streamlit.io/develop/api-reference/server/st.app
"""
from pathlib import Path
import streamlit as st
from starlette.routing import Route
from studio_delivery import movie_response

app=st.App(Path(__file__).with_name('app.py'),
    routes=[Route('/studio-media/{token}',movie_response,methods=['GET','HEAD'])])
