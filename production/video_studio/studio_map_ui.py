"""Explicit preparation, calendar review and durable publication in Studio."""
from pathlib import Path
import json
import streamlit as st
from model import validate
from studio_project import source_projection
from studio_map_jobs import start_map_job, map_status, read_resource, read_bundle_resource
from studio_temporal import attach_map, attach_map_layers, review_map_layers, _hash


def show_layer_review(session,key,record,*,publish_label='Insertar capas',publisher=None,prepared_job_key=None,
                      prepare_dialog='temporal_layers'):
    """Native review for a prepared or retained library resource; explicit commit."""
    try:
        manifest=review_map_layers(session.project,record)
        from output_profiles import profile_for
        profile=profile_for(session.project['studio']['output_profile'])
        base=st.session_state.setdefault(key+'_layer_review_base',
            {'project':_hash(session.project),'record':_hash(record)})
        st.subheader('Mapa de capas')
        st.write(manifest['variable']+(' · '+manifest['units'] if manifest['units'] else ' · sin unidad declarada'))
        st.caption(record['period'][0]+' — '+record['period'][1]+f' · {len(manifest["observations"])} observaciones · sin interpolación temporal')
        if manifest.get('observation_selection'):
            st.info('Una observación de '+str(len(manifest['source_records']))+' fechas de la revisión. Es el valor observado de esa fecha, no un promedio ni un acumulado del período completo.')
        st.write('Fuente: '+(manifest['citation'] or manifest['source']))
        st.caption(f'Revisión {manifest["scientific_revision"][:12]} · perfil {profile.name} · {profile.width} × {profile.height} · 30 FPS')
        from maqueta import MAIN_BOX
        if manifest['region']!=list(MAIN_BOX):st.warning('Dominio continental parcial: se conserva el encuadre preparado; no representa todo Ecuador continental. Consulta los límites en los detalles.')
        st.image(str(Path(record['manifest_path']).parent/manifest['thumbnail']['path']),
            width=240,alt='Vista de las capas preparadas; cada región conserva su transparencia')
        covered={lid:sum(o['layers'][lid]['state']=='covered' for o in manifest['observations']) for lid in manifest['layers']}
        for lid,name in (('continent','Continente'),('galapagos','Galápagos')):
            text=f'{name}: {covered[lid]}/{len(manifest["observations"])} observaciones con cobertura.'
            if covered[lid]<len(manifest['observations']):st.warning(text+' Las fechas sin cobertura serán transparentes, sin sustituir datos.')
            else:st.caption(text)
        st.caption('Se añadirá una escena con regiones independientes, fecha protegida, leyenda verificada, variable/unidades y fuente. El proyecto actual se conserva.')
        with st.expander('Escala, calendario y procedencia'):
            st.image(str(Path(record['manifest_path']).parent/manifest['auxiliaries']['legend_static']['path']),
                alt='Leyenda completa y sellada de los valores representados')
            st.dataframe([{'Fecha':o['date'],'Continente':o['layers']['continent']['state'],
                'Galápagos':o['layers']['galapagos']['state'],'CRS nativo':o['native_crs'],
                'Desde frame':s['start_frame'],'Hasta frame (exclusivo)':s['end_frame']}
                for o,s in zip(manifest['observations'],manifest['intervals'])],hide_index=True,
                alt='Correspondencia de fechas, cobertura y fotogramas científicos')
            st.json({'revisión':manifest['scientific_revision'],'manifest_sha256':record['manifest_sha256'],
                'fuentes':manifest['source_records'],'regiones':manifest['layers'],
                'escala':manifest['auxiliaries']['legend_static']['spec'],'NoData':manifest['nodata'],
                'advertencias':manifest['warnings']},expanded=False)
        if st.button(publish_label,type='primary',key=key+'_layers_publish'):
            if _hash(record)!=base['record']:raise ValueError('El recurso cambió. Cierra y revisa otra vez antes de insertar.')
            candidate=attach_map_layers(session.project,record,base_sha256=base['project'])
            if publisher is None:
                session.commit(candidate)
                st.session_state[session.key+'_selected']=candidate['studio']['timeline'][-1]
            else:publisher(candidate)
            st.session_state.pop(prepared_job_key or key+'_layers_map_job',None)
            for suffix in ('_layer_review_base','_layer_review_asset','_dialog','_frame'):
                st.session_state.pop(key+suffix,None)
            st.rerun()
    except (ValueError,TypeError,KeyError,OSError) as error:
        st.error('No se pueden insertar las capas: '+str(error))
    if st.button('Preparar otro mapa de capas',key=key+'_layers_prepare_again'):
        st.session_state.pop(prepared_job_key or key+'_layers_map_job',None)
        for suffix in ('_layer_review_base','_layer_review_asset'):
            st.session_state.pop(key+suffix,None)
        st.session_state[key+'_dialog']=prepare_dialog
        st.rerun()
    if st.button('Cerrar sin insertar',key=key+'_layers_close'):
        st.session_state.pop(key+'_layer_review_base',None)
        st.session_state.pop(key+'_layer_review_asset',None)
        st.session_state.pop(key+'_dialog',None)
        st.rerun()


@st.fragment(run_every='1s')
def _poll(job, key):
    status = map_status(job)
    st.progress(status.get('progress',0),text=status.get('message','Preparando mapa'))
    if st.button('Cancelar preparación del mapa',key=key+'_map_cancel'):
        Path(job).joinpath('cancel.request').touch()
        st.rerun()
    if status.get('state') not in ('queued','running'): st.rerun()


def show_map_dialog(session, key, *, publish_label='Insertar mapa y escena en Studio', publisher=None,
                    representation='opaque_prerendered_map',source_index=None):
    structured=representation=='rgba_observation_bundle'
    job_key=key+('_layers_map_job' if structured else '_map_job')
    if structured and source_index is not None:job_key+='_observation_'+str(source_index)
    st.caption('Prepara continente y Galápagos con transparencia y un calendario científico compartido.' if structured else
        'Mapa prerenderizado: fecha, leyenda e inset integrados. Para componentes independientes usa Preparar capas cartográficas en Studio.')
    job = st.session_state.get(job_key)
    if not job:
        try:
            rows = validate(source_projection(session.project))
            if source_index is not None and (not structured or type(source_index) is not int or not 0<=source_index<len(rows)):
                raise ValueError('La fecha seleccionada no pertenece a esta revisión.')
            selected_rows=rows if source_index is None else [rows[source_index]]
            minimum = len(selected_rows)/30
            duration = st.number_input('Duración del mapa · segundos',min_value=minimum,max_value=7200.,
                value=max(minimum,min(7200.,float(session.project.get('duration',26)))),step=1/30,key=key+'_map_duration')
            st.caption(f'{len(selected_rows)} fechas · {selected_rows[0]["date"]} — {selected_rows[-1]["date"]} · 30 FPS · sin interpolación temporal.')
            if source_index is not None:st.info('Se prepara solo esta observación; los resultados de toda la revisión se conservan. La duración es visual: no representa una nueva agregación temporal.')
            if st.button('Preparar mapa desde datos',type='primary',key=key+'_map_start'):
                options={'representation':representation}
                if source_index is not None:options['source_index']=source_index
                st.session_state[job_key] = str(start_map_job(session.project,duration,**options))
                st.rerun()
        except (ValueError,TypeError,KeyError,OSError) as error: st.error(str(error))
    else:
        try:
            status = map_status(job)
            if status.get('state') in ('queued','running'):
                _poll(job,key)
            elif status.get('state') == 'complete':
                if structured:
                    show_layer_review(session,key,read_bundle_resource(job),
                        publish_label=publish_label if publisher else 'Insertar capas',publisher=publisher,
                        prepared_job_key=job_key,
                        prepare_dialog='observation_layers' if source_index is not None else 'temporal_layers')
                    return
                record = read_resource(job)
                manifest = record['temporal_map']
                st.success('Mapa y calendario verificados; todavía no se han añadido al proyecto.')
                st.image(str(Path(job)/'thumbnail.png'),width=160)
                st.write(record['name'])
                st.caption(f'{record["size"][0]} × {record["size"][1]} · {manifest["total_frames"]} fotogramas · {record["duration"]:.3f} s · {manifest["units"]}')
                st.dataframe([{'Fecha':i['date'],'Desde fotograma':i['start_frame'],'Hasta (exclusivo)':i['end_frame'],
                    'Banda':manifest['source_records'][i['source_index']]['band'],
                    'SHA-256':manifest['source_records'][i['source_index']]['sha256']} for i in manifest['intervals']],
                    hide_index=True,alt='Calendario científico y hashes de datos de origen')
                with st.expander('Manifiesto de fuentes, revisión y representación'):
                    st.json(manifest,expanded=False)
                st.download_button('Descargar manifiesto científico',
                    data=json.dumps(manifest,ensure_ascii=False,indent=2),
                    file_name='calendario-cientifico.json',mime='application/json',key=key+'_map_manifest')
                if st.button(publish_label,type='primary',key=key+'_map_publish'):
                    record = read_resource(job)
                    if publisher is not None: publisher(record)
                    else:
                        candidate = attach_map(session.project,record)
                        session.commit(candidate)
                        st.session_state[key+'_selected'] = candidate['studio']['timeline'][-1]
                    st.session_state.pop(key+'_map_job',None)
                    st.session_state.pop(key+'_dialog',None)
                    st.rerun()
            else:
                st.warning(status.get('message','Preparación interrumpida; el proyecto se conserva.'))
            if status.get('state') not in ('queued','running') and st.button('Preparar otro mapa',key=key+'_map_retry'):
                st.session_state.pop(job_key,None); st.session_state.pop(key+'_layer_review_base',None); st.rerun()
        except (ValueError,TypeError,KeyError,OSError) as error: st.error(str(error))
    if st.button('Cerrar sin insertar',key=key+'_map_close'):
        # The private worker can finish while its dialog is closed; reopening resumes it.
        st.session_state.pop(key+'_dialog',None); st.rerun()
