"""Compact vector workflows inside the existing SIG inspector."""
import json
import streamlit as st
from shapely.errors import GEOSException
from pyproj.exceptions import ProjError
from studio_sig_layers import workspace_for
from studio_sig_vector import layer_features,run_operation,csv_rows,add_csv,add_ogr,ogr_layers,export_layer


def import_general(session):
    from studio_sig_workspace import choose_tool,notify
    fmt=st.selectbox('Formato de entrada',['GeoJSON','CSV de puntos','GeoPackage','FlatGeobuf','GeoTIFF'],key='sig_import_format',persist_state='session')
    if fmt=='GeoJSON':return False
    if fmt=='GeoTIFF':
        from studio_sig_raster_ui import import_panel
        import_panel(session);return True
    kind={'CSV de puntos':'csv','GeoPackage':'gpkg','FlatGeobuf':'fgb'}[fmt]
    upload=st.file_uploader('Archivo '+kind.upper(),type=[kind],max_upload_size=8,key='sig_general_upload_'+kind)
    if upload is None:
        st.caption('Original inmutable; el CRS desconocido requiere una declaración explícita.');return True
    content=upload.getvalue();fields=[];layer=None
    if kind=='csv':
        delimiter=st.selectbox('Separador',[',',';','\t'],format_func=lambda v:'Tabulación' if v=='\t' else v,key='sig_csv_separator')
        try:fields,rows=csv_rows(content,delimiter)
        except ValueError as error:st.error(str(error));return True
        st.caption(f'{len(rows)} filas · coordenadas X/Y; atributos conservados, vacíos como null')
    else:
        try:
            layers=ogr_layers(content,kind)
            layer=st.selectbox('Capa del archivo',[str(v[0]) for v in layers],key='sig_ogr_layer')
        except Exception as error:st.error('No se pudo leer el archivo: '+str(error));return True
    with st.form('sig_general_import'):
        if kind=='csv':
            x=st.selectbox('Columna X (este/longitud)',fields,key='sig_csv_x')
            y=st.selectbox('Columna Y (norte/latitud)',fields,index=min(1,len(fields)-1),key='sig_csv_y')
        native=st.text_input('CRS de origen',placeholder='EPSG:4326, EPSG:32717…',help='Obligatorio para CSV; OGR usa los metadatos cuando existen.',key='sig_general_crs')
        citation=st.text_input('Procedencia',key='sig_general_citation')
        license=st.text_input('Licencia o condiciones',key='sig_general_license')
        accepted=st.form_submit_button('Incorporar capa',key='sig_general_submit')
    if accepted:
        try:
            provenance={'citation':citation,'license':license,'url':''}
            if kind=='csv':candidate,_=add_csv(session.project,content,upload.name,provenance,x=x,y=y,source_crs=native,delimiter=delimiter)
            else:candidate,_=add_ogr(session.project,content,upload.name,provenance,kind=kind,source_crs=native,layer=layer)
            session.commit(candidate);choose_tool(session,'Propiedades');notify(session,'Capa incorporada. Original y CRS de origen conservados.');st.rerun()
        except (ValueError,TypeError,KeyError,OSError) as error:notify(session,error,'error');st.error('No se incorporó la capa: '+str(error))
    return True


def analysis_panel(session):
    from studio_sig_workspace import choose_tool,notify
    state=workspace_for(session.project);lid=state['active_layer']
    if lid is None:st.info('Incorpora y selecciona una capa para analizar.');return
    if state['layers'][lid]['type']=='raster':st.info('Selecciona una capa vectorial o abre Ráster y tiempo.');return
    source,features=layer_features(session.project,lid)
    fields=list(dict.fromkeys(k for f in features for k in (f.get('properties') or {})))
    st.markdown('**Análisis vectorial**');st.caption(state['layers'][lid]['name'])
    tools={'Buffer':'buffer','Recortar':'clip','Intersección':'intersection','Disolver':'dissolve',
           'Superficie y longitud':'measure','Calcular campo':'calculate','Filtrar entidades':'filter'}
    selected=st.selectbox('Operación',list(tools),key=session.key+'_vector_operation',persist_state='session');tool=tools[selected]
    st.caption('Se crea una capa derivada; no se alteran los datos de entrada.')
    with st.form('sig_vector_operation'):
        params={};other=None
        if tool in ('buffer','measure'):
            params['crs']=st.text_input('CRS de cálculo en metros',placeholder='Proyección adecuada al territorio',key='sig_analysis_crs')
            st.caption('Comprueba el área de uso. No se miden grados ni se usa Mercator para estas métricas.')
        if tool=='buffer':params['distance']=st.number_input('Distancia (m)',min_value=.01,max_value=1_000_000.,value=1000.,key='sig_buffer_distance')
        if tool in ('clip','intersection'):
            candidates=[k for k in state['order'] if k!=lid]
            if not candidates:st.info('Añade una capa poligonal para el recorte/intersección.');return
            other=st.selectbox('Capa poligonal',candidates,format_func=lambda k:state['layers'][k]['name'],key='sig_analysis_other')
        if tool=='dissolve':params['field']=st.selectbox('Disolver por campo',[None]+fields,format_func=lambda f:'Todas las entidades' if f is None else f,key='sig_dissolve_field')
        if tool in ('calculate','filter'):
            if not fields:st.info('La capa no tiene campos.');return
            params['field']=st.selectbox('Campo de entrada',fields,key='sig_analysis_field')
        if tool=='calculate':
            params['output']=st.text_input('Campo nuevo',value='resultado',key='sig_analysis_output')
            params['operator']=st.selectbox('Cálculo',['add','subtract','multiply','divide'],format_func=lambda v:{'add':'Sumar constante','subtract':'Restar constante','multiply':'Multiplicar por constante','divide':'Dividir por constante'}[v],key='sig_calc_operator')
            params['constant']=st.number_input('Constante',value=1.,key='sig_calc_constant')
            params['units']=st.text_input('Unidad del resultado',key='sig_calc_units')
            st.caption('Los ausentes permanecen null. Este cálculo por entidad no agrega series climáticas.')
        if tool=='filter':
            params['operator']=st.selectbox('Condición',['equals','contains','greater','less','missing'],format_func=lambda v:{'equals':'Igual a','contains':'Contiene texto','greater':'Mayor que','less':'Menor que','missing':'Dato ausente'}[v],key='sig_filter_operator')
            params['value']=st.text_input('Valor de comparación',key='sig_filter_value')
        name=st.text_input('Nombre de la nueva capa',value=selected,key='sig_analysis_name')
        accepted=st.form_submit_button('Ejecutar y añadir resultado',key='sig_analysis_run')
    if accepted:
        try:
            candidate,new_lid=run_operation(session.project,lid,tool,params,other=other,name=name)
            session.commit(candidate);choose_tool(session,'Propiedades');notify(session,selected+' completado: '+candidate['studio']['geography']['map_workspace']['layers'][new_lid]['name']);st.rerun()
        except (ValueError,TypeError,KeyError,OSError,GEOSException,ProjError) as error:notify(session,error,'error');st.error('No se añadió ningún resultado: '+str(error))


def export_controls(session,lid):
    data=export_layer(session.project,lid)
    st.download_button('Exportar capa GeoJSON',data,file_name='ecuador-vivo-capa.geojson',mime='application/geo+json',key='sig_export_layer')
    source,_=layer_features(session.project,lid)
    origin=source.get('origin')
    if origin:
        from pathlib import Path
        st.download_button('Descargar original '+origin['format'].upper(),Path(origin['path']).read_bytes(),file_name=origin['name'],key='sig_export_original')
