"""Explicit acquisition within SIG; no second laboratory or automatic downloads."""
import datetime as dt
import streamlit as st


def acquire_panel(session):
    from providers import CHIRPS_PRODUCTS,POWER_VARIABLES
    source=st.selectbox('Fuente de las observaciones',['Capas del proyecto','NASA POWER','CHIRPS v3','Importar serie GeoTIFF','INAMHI · estaciones'],key=session.key+'_series_provider')
    if source=='Capas del proyecto':return
    if source=='Importar serie GeoTIFF':
        import_series(session);return
    if source=='INAMHI · estaciones':
        st.info('INAMHI entrega observaciones por estación, no un ráster continuo de todo Ecuador. No se convertirán sus puntos en un mapa de lluvia nacional inventado. El descargador de estaciones sigue disponible en Obtener datos; esta preparación anima series GeoTIFF.')
        st.link_button('Consultar INAMHI','https://inamhi.gob.ec/')
        return
    if source=='NASA POWER':
        variable=st.selectbox('Variable a descargar',list(POWER_VARIABLES),format_func=lambda k:POWER_VARIABLES[k]['label']+' · '+POWER_VARIABLES[k]['units'],key=session.key+'_series_power')
        st.caption('Grilla regional, no estaciones ni detalle de calles. Incluye la extensión continental e insular. Los límites se recortan al preparar el video.')
        st.link_button('Producto y resolución · NASA POWER','https://power.larc.nasa.gov/docs/services/api/temporal/daily/')
    else:
        variable=st.selectbox('Producto de lluvia',list(CHIRPS_PRODUCTS),format_func=lambda k:CHIRPS_PRODUCTS[k]['label'],key=session.key+'_series_chirps')
        st.caption('El preliminar puede cambiar. Los productos finales se publican con retraso; no se sustituirán productos ni días ausentes en silencio.')
        st.link_button('Metodología · CHIRPS v3','https://chc.ucsb.edu/data/chirps3')
    today=dt.date.today();last=today.replace(day=1)-dt.timedelta(days=1);first=last.replace(day=1)
    period=st.date_input('Periodo de descarga (máximo 31 días por solicitud)',value=(first,last),max_value=today,key=session.key+'_series_download_dates')
    st.caption('Descarga solo al pulsar el botón. Se conservan originales, fechas, máscara y procedencia. No descarga décadas ni archivos globales completos.')
    if st.button('Descargar e incorporar al SIG',key=session.key+'_series_download',type='primary'):
        bar=st.progress(0,text='Consultando disponibilidad real…')
        try:
            if len(period)!=2 or not 2<=(period[1]-period[0]).days+1<=31:raise ValueError('Selecciona entre 2 y 31 días, de inicio a fin.')
            from providers import download_power_regional,download_chirps_v3
            from studio_sig_series import admit_download
            def progress(done,total,day):bar.progress(min(1.,done/max(1,total)),text='Recibiendo '+str(day))
            if source=='NASA POWER':download=download_power_regional(*period,variable,progress=progress)
            else:download=download_chirps_v3(*period,product=variable,progress=progress)
            candidate,ids=admit_download(session.project,download)
            from studio_sig_series import activate_series
            from studio_sig_layers import workspace_for
            from studio_territory import options_for,DEFAULT
            presentation=options_for(session.project) if workspace_for(session.project).get('raster_time') else DEFAULT
            candidate=activate_series(candidate,ids,cadence='daily',presentation=presentation)
            session.commit(candidate);session.state[session.key+'_series_imported']=ids
            from studio_sig_workspace import choose_tool
            choose_tool(session,'Propiedades')
            session.state[session.key+'_series_download_notice']=f"{len(ids)} fechas incorporadas · {download['variable']} · {download['units']}"
            if download.get('missing_dates'):
                session.state[session.key+'_series_download_notice']+=' · Fechas ausentes: '+', '.join(download['missing_dates'])
            bar.progress(1.,text='Serie activada en el mapa. Puedes ajustar territorio, periodo y duración.');st.rerun()
        except Exception as error:
            # Provider/network errors must not escape a Streamlit fragment. The
            # candidate is only committed after every original has been verified.
            st.error('No se incorporó la descarga: '+str(error))
            st.caption('Prueba fechas anteriores o el producto preliminar, si corresponde. La disponibilidad depende del proveedor; el proyecto abierto no se sustituyó.')
        finally:bar.empty()
    notice=session.state.get(session.key+'_series_download_notice')
    if notice:st.success(notice)


def import_series(session):
    from rasterio.io import MemoryFile
    uploads=st.file_uploader('GeoTIFF de la serie',type=['tif','tiff'],accept_multiple_files=True,max_upload_size=32,key=session.key+'_series_uploads')
    if not uploads:st.caption('Puedes cargar varios archivos o un GeoTIFF multibanda. Declara y revisa la fecha de cada banda.');return
    rows=[]
    try:
        for i,upload in enumerate(uploads):
            with MemoryFile(upload.getvalue()) as memory,memory.open() as ds:
                for band in range(1,ds.count+1):
                    value=ds.tags(band).get('observed_date') or (ds.tags().get('observed_date') if ds.count==1 else '') or ''
                    rows.append({'Archivo':upload.name,'Banda':band,'Fecha AAAA-MM-DD':value,'_upload':i})
    except Exception as error:st.error('No se pudo leer el GeoTIFF: '+str(error));return
    st.caption('Las fechas NO se adivinan del nombre. Completa la tabla; cada banda representa una observación, no una fecha interpolada.')
    import hashlib
    signature=hashlib.sha256('|'.join(u.name+str(u.size) for u in uploads).encode()).hexdigest()[:12]
    table=st.data_editor([{k:v for k,v in r.items() if k!='_upload'} for r in rows],disabled=['Archivo','Banda'],num_rows='fixed',hide_index=True,key=session.key+'_series_date_table_'+signature)
    with st.form(session.key+'_series_import'):
        variable=st.text_input('Variable observada',key=session.key+'_series_variable')
        units=st.text_input('Unidad original',key=session.key+'_series_unit')
        semantics=st.selectbox('Tipo de medición',['scalar','temperature','precipitation'],format_func=lambda k:{'scalar':'Otro valor numérico (sin agregación automática)','temperature':'Temperatura','precipitation':'Precipitación'}[k])
        citation=st.text_input('Fuente y producto')
        license=st.text_input('Licencia o condiciones de uso')
        accept=st.form_submit_button('Incorporar serie revisada')
    if accept:
        from studio_sig_raster import add_raster
        try:
            if len(rows)<2:raise ValueError('El timelapse necesita al menos dos observaciones.')
            dates=[dt.date.fromisoformat(r['Fecha AAAA-MM-DD']).isoformat() for r in table]
            if len(set(dates))!=len(dates):raise ValueError('No repitas fechas dentro de la misma serie.')
            # Same one-band admission as providers, without staging extra copies.
            candidate=session.project;ids=[]
            import rasterio
            for row,edited,day in zip(rows,table,dates):
                content=uploads[row['_upload']].getvalue();band=row['Banda']
                with MemoryFile(content) as memory,memory.open() as ds:
                    profile=ds.profile.copy();profile.update(count=1,compress='deflate');profile.pop('photometric',None)
                    with rasterio.Env(GDAL_TIFF_INTERNAL_MASK=True),MemoryFile() as output:
                        with output.open(**profile) as out:
                            out.write(ds.read(band),1);out.write_mask(ds.read_masks(band))
                            out.scales=(ds.scales[band-1],);out.offsets=(ds.offsets[band-1],)
                            out.update_tags(original_sha256=hashlib.sha256(content).hexdigest(),original_band=str(band),observed_date=day)
                        one=output.read()
                candidate,lid=add_raster(candidate,one,row['Archivo']+' · '+day+'.tif',{'citation':citation,'license':license,'url':''},observed_date=day,variable=variable,units=units,semantics=semantics);ids.append(lid)
            from studio_sig_series import activate_series
            candidate=activate_series(candidate,ids)
            session.commit(candidate);session.state[session.key+'_series_imported']=ids
            from studio_sig_workspace import choose_tool
            choose_tool(session,'Propiedades');st.rerun()
        except (ValueError,TypeError,KeyError,OSError) as error:st.error('No se incorporó la serie: '+str(error))
