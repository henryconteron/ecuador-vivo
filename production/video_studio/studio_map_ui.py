"""Explicit preparation, calendar review and durable publication in Studio."""
from pathlib import Path
import json
import streamlit as st
from model import validate
from studio_project import source_projection
from studio_map_jobs import start_map_job, map_status, read_resource
from studio_temporal import attach_map


@st.fragment(run_every='1s')
def _poll(job, key):
    status = map_status(job)
    st.progress(status.get('progress',0),text=status.get('message','Preparando mapa'))
    if st.button('Cancelar preparación del mapa',key=key+'_map_cancel'):
        Path(job).joinpath('cancel.request').touch()
        st.rerun()
    if status.get('state') not in ('queued','running'): st.rerun()


def show_map_dialog(session, key, *, publish_label='Insertar mapa y escena en Studio', publisher=None):
    st.caption('Puente prerenderizado verificable: mapa, fechas, leyenda e inset del compositor actual. Continente/Galápagos y overlays independientes se integrarán en 4b.')
    job = st.session_state.get(key+'_map_job')
    if not job:
        try:
            rows = validate(source_projection(session.project))
            minimum = len(rows)/30
            duration = st.number_input('Duración del mapa · segundos',min_value=minimum,max_value=7200.,
                value=max(minimum,min(7200.,float(session.project.get('duration',26)))),step=1/30,key=key+'_map_duration')
            st.caption(f'{len(rows)} fechas · {rows[0]["date"]} — {rows[-1]["date"]} · 30 FPS · sin interpolación temporal.')
            if st.button('Preparar mapa desde datos',type='primary',key=key+'_map_start'):
                st.session_state[key+'_map_job'] = str(start_map_job(session.project,duration))
                st.rerun()
        except (ValueError,TypeError,KeyError,OSError) as error: st.error(str(error))
    else:
        try:
            status = map_status(job)
            if status.get('state') in ('queued','running'):
                _poll(job,key)
            elif status.get('state') == 'complete':
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
                st.session_state.pop(key+'_map_job',None); st.rerun()
        except (ValueError,TypeError,KeyError,OSError) as error: st.error(str(error))
    if st.button('Cerrar sin insertar',key=key+'_map_close'):
        # The private worker can finish while its dialog is closed; reopening resumes it.
        st.session_state.pop(key+'_dialog',None); st.rerun()
