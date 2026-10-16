"""Local editorial gate. No upload, rendering, or verification on idle reruns."""
import streamlit as st
from studio_import import ID, private_base, import_draft, draft_metadata, stage_draft

def show_studio_import(root,save):
    st.subheader('Studio → Andes Pulso')
    st.caption('Importa el ZIP público de un video final. Primero queda privado; incorporarlo a la web y publicarlo en GitHub son acciones separadas.')
    with st.expander('Importar evidencia de Studio'):
        uploaded=st.file_uploader('Paquete andes-pulso-publico…zip',type=['zip'],max_upload_size=160,key='studio-evidence-upload')
        if st.button('Verificar e importar como borrador privado',disabled=uploaded is None):
            try:
                with st.spinner('Comprobando archivos, calendario y huellas…'):
                    target=import_draft(root,uploaded.getvalue())
                st.success('Borrador privado guardado. Todavía no está en la web ni en GitHub.')
                st.session_state['studio-draft-choice']=target.name
            except (ValueError,OSError) as error:st.error(str(error))
    base=private_base(root)
    ids=sorted(p.name for p in base.iterdir() if p.is_dir() and ID.fullmatch(p.name)) if base.exists() else []
    if not ids:
        st.info('Aquí aparecerán los videos y su evidencia después de importar. No se muestra contenido de ejemplo como si fuera real.')
        return
    identifier=st.selectbox('Borradores importados',ids,key='studio-draft-choice')
    try:case,target=draft_metadata(root,identifier)
    except (ValueError,OSError) as error:st.error(str(error));return
    st.subheader(case['title'])
    st.write(f"{case['variable']} · {case['units']} · {case['period']['start']} — {case['period']['end']}")
    film,evidence=st.columns([1,2],gap='large')
    with film:st.video(str(target/'video.mp4'))
    with evidence:
        maps=case['maps'];index=st.slider('Fecha del mapa',0,len(maps)-1,0,key='studio-map-date-'+identifier) if len(maps)>1 else 0
        observation=maps[index];st.caption(observation['date'])
        for channel,name in observation['channels'].items():st.image(str(target/name),caption=channel,width='stretch')
        with st.expander('Métricas y método'):
            if case['results']:st.json(case['results'])
            else:st.info('Sin métricas agregadas verificadas. No se sustituyen por datos de otra variable.')
        with st.expander('Procedencia, derechos y límites'):
            st.json(case['sources']);st.write(case['limitations'])
    st.warning('Las huellas comprueban integridad, no demuestran por sí solas que una conclusión científica sea correcta. Revisa unidades, periodo, cobertura, narración y derechos de datos, imágenes y audio.')
    reviewed=st.checkbox('He revisado los cálculos, la interpretación y los derechos; quiero incorporar este caso a la web local.',key='studio-reviewed-'+identifier)
    if st.button('Incorporar a Andes Pulso local',disabled=not reviewed,type='primary'):
        try:
            with st.spinner('Verificando de nuevo e incorporando los archivos…'):
                stage_draft(root,identifier,save,reviewed=reviewed)
            st.success('Caso incorporado a la web local. No se ha publicado: revisa «Cambios y GitHub» cuando quieras subirlo.')
        except (ValueError,OSError) as error:st.error(str(error))
