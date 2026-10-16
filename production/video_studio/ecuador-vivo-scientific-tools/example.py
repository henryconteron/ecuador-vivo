"""Optional editors; run through Streamlit, not as a plain Python script."""
import streamlit as st
from ecuador_vivo_scientific_tools import scientific_tool
st.set_page_config(page_title="Ecuador Vivo · herramientas científicas",layout="wide")
tool=st.selectbox("Editor",["drawing","vector","diagram","molecule"])
scientific_tool(tool,key="example")
