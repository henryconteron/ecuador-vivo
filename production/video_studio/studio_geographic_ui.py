"""Real GeoJSON import/view/send over the canonical WorkspaceSession."""
import streamlit as st
from studio_geography import import_geojson,read_source,region_feature,render_region,make_view,attach_view,_features
from studio_project import request_studio_navigation


def show_geography(session):
    with st.expander('Capas GeoJSON · polígonos propios',expanded=True):
        st.caption('BYOD · Polygon/MultiPolygon 2D RFC7946, hasta 8 MiB. Lon/lat WGS84 explícito; sin reproyección vectorial, antimeridiano ni polos. No se distribuyen automáticamente tus archivos. La licencia registrada es una declaración de procedencia, no una verificación legal.')
        try:
            with st.form('geographic_import_form'):
                upload=st.file_uploader('Importar GeoJSON',type=['geojson','json'],key='geographic_upload',max_upload_size=8)
                citation=st.text_input('Procedencia del GeoJSON',key='geographic_citation',max_chars=1000)
                license=st.text_input('Licencia o condiciones de uso',key='geographic_license',max_chars=1000)
                url=st.text_input('URL pública de origen (opcional)',key='geographic_url',max_chars=1000,
                    help='Sin usuario, contraseña, parámetros ni tokens. No configura una conexión remota.')
                accepted=st.form_submit_button('Importar capa al proyecto',key='geographic_import')
            selection_key=session.key+'_geographic_region'
            if accepted:
                if upload is None:raise ValueError('Selecciona un archivo GeoJSON.')
                candidate,rid=import_geojson(session.project,upload.getvalue(),upload.name,{'citation':citation,'license':license,'url':url})
                if candidate!=session.project:session.commit(candidate)
                st.session_state[selection_key]=rid
                st.success('GeoJSON original conservado y regiones disponibles en este proyecto.')
            registry=session.project['studio'].get('geography')
            if not registry or not registry['regions']:return
            features={sid:_features(read_source(source)) for sid,source in registry['sources'].items()}
            labels={rid:str((features[r['source_id']][r['feature_index']].get('properties') or {}).get('name') or 'Región')[:120]+' · '+rid[-8:]
                for rid,r in registry['regions'].items()}
            rid=st.selectbox('Región GeoJSON',list(labels),format_func=lambda k:labels[k],key=selection_key,persist_state='session')
            feature=region_feature(session.project,rid);region=registry['regions'][rid];source=registry['sources'][region['source_id']]
            st.caption('CRS nativo/display: OGC:CRS84 · orden longitude/latitude WGS84 · vista angular sin medición · '+source['name'])
            with st.expander('Geometría, atributos y derechos del origen'):
                st.json({'region_id':rid,'source_id':source['id'],'sha256':source['sha256'],'bbox':region['bbox'],
                    'properties':feature.get('properties'),'provenance':source['provenance']})
            image,_=render_region(session.project,rid)
            try:st.image(image,width=600,alt='Vista GeoJSON real de la región seleccionada; agujeros transparentes')
            finally:image.close()
            views={vid:v for vid,v in registry['views'].items() if v['region_id']==rid}
            if st.button('Guardar vista geográfica',key='geographic_save_view'):
                candidate,vid=make_view(session.project,rid)
                if candidate!=session.project:session.commit(candidate)
                views={vid:candidate['studio']['geography']['views'][vid]}
                st.success('Vista RGBA guardada, vinculada al GeoJSON original.')
            if views:
                vid=next(iter(views))
                st.caption('Vista guardada · '+vid[-8:]+' · conserva coordenadas/atributos en el origen, posición editorial independiente en Studio.')
                if st.button('Enviar vista a Studio',key='geographic_send',type='primary'):
                    candidate,selected=attach_view(session.project,vid)
                    if candidate!=session.project:session.commit(candidate)
                    st.session_state[session.key+'_selected']=selected
                    request_studio_navigation(st.session_state);st.rerun()
        except (ValueError,TypeError,KeyError,OSError,IndexError) as error:
            st.error('No se pudo usar la capa GeoJSON: '+str(error))
