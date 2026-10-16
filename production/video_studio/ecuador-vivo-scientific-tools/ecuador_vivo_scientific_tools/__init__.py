"""Optional editors generated from Streamlit's official CCv2 React template."""
import streamlit as st
out=st.components.v2.component("ecuador-vivo-scientific-tools.ecuador_vivo_scientific_tools",
    js="scientific-entry.js",css="scientific-tools.css",html='<div class="react-root"></div>')
def scientific_tool(tool,recipe=None,key=None,on_artifact_change=None):
    return out(key=key,data={"tool":tool,"recipe":recipe or {}},
        on_artifact_change=on_artifact_change or (lambda:None),width="stretch",height=610)
