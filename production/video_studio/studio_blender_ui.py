"""Blender authoring inside Recursos: explicit render, native progress and transfer."""
import copy
import json
from pathlib import Path
import streamlit as st
from output_profiles import PRESETS
from studio_blender import (VERSION,blender_executable,default_recipe,validate_recipe,start_job,
    job_status,job_root,cancel_job,verified_product)


def _recent_jobs(store):
    folder=Path(store)/'resource-3d'
    rows=[]
    for path in sorted(folder.glob('*'),key=lambda p:p.stat().st_mtime,reverse=True)[:48]:
        try:
            if not path.is_dir() or path.resolve()!=job_root(path.name,store):continue
            request=json.loads((path/'request.json').read_text(encoding='utf-8'))
            if request['recipe']['version']==VERSION and request['mode']!='poster':
                job_root(path.name,store);rows.append(path.name)
        except (OSError,ValueError,KeyError,TypeError):continue
    return rows


def show_blender_ui(project,on_change,*,key='resource_blender',store=None):
    from model import STORE
    store=Path(store or STORE)
    scenes=[s for s in (project or {}).get('studio',{}).get('scenes',[]) if s.get('resource',{}).get('blender')]
    preferred=st.session_state.get('resource_3d_scene')
    target=next((s for s in scenes if s['id']==preferred),scenes[0] if scenes else None)
    try:base=validate_recipe(target['resource']['blender']['recipe']) if target else default_recipe()
    except ValueError:base=default_recipe();target=None
    # Reopening another object must show its recipe, not stale widget values
    # from a previous scene. Reruns of this same object keep unsent edits.
    target_identity=((project or {}).get('project_meta',{}).get('id'),target['id'] if target else None)
    if st.session_state.get(key+'_target')!=target_identity:
        for field in base:
            st.session_state.pop(key+'_'+field,None)
        st.session_state[key+'_target']=target_identity
    ready=True
    try:blender_executable()
    except (ValueError,OSError) as error:ready=False;st.warning(str(error))
    st.subheader('Estudio 3D',icon=':material/view_in_ar:')
    st.caption('Escena orográfica en Blender. Cámara, relieve, materiales y movimiento editables; textos y composición se editan después en el lienzo de Studio.')
    controls,canvas=st.columns([.35,.65],gap='large')
    with controls:
        with st.form(key+'_form',border=False):
            title=st.text_input('Nombre de la nueva escena','La montaña no fabrica agua',max_chars=180,key=key+'_title')
            selected=st.selectbox('Formato de la nueva escena',list(PRESETS),format_func=lambda pid:PRESETS[pid][0],key=key+'_profile')
            duration=st.slider('Duración del recurso · segundos',1.,30.,float(base['duration']),1.,key=key+'_duration')
            st.markdown('**Cámara**')
            yaw=st.slider('Giro horizontal · grados',-80.,80.,float(base['yaw']),1.,key=key+'_yaw')
            pitch=st.slider('Inclinación · grados',10.,70.,float(base['pitch']),1.,key=key+'_pitch')
            distance=st.slider('Encuadre · menor valor, más cerca',8.,20.,float(base['distance']),.5,key=key+'_distance')
            orbit=st.slider('Recorrido de cámara · grados',0.,45.,float(base['orbit']),1.,key=key+'_orbit')
            st.markdown('**Relieve e iluminación**')
            mountain=st.slider('Altura ilustrativa del relieve',1.,3.5,float(base['mountain']),.1,key=key+'_mountain')
            light=st.slider('Intensidad de luz',100.,3000.,float(base['light']),100.,key=key+'_light')
            ground=st.color_picker('Superficie',base['ground'],key=key+'_ground')
            rock=st.color_picker('Corte de roca',base['rock'],key=key+'_rock')
            water=st.color_picker('Aire y gotas',base['water'],key=key+'_water')
            background=st.color_picker('Fondo',base['background'],key=key+'_background')
            moist=st.checkbox('Mostrar condensación conceptual',base['moist'],key=key+'_moist')
            rain=st.checkbox('Mostrar precipitación ilustrativa',base['rain'],key=key+'_rain')
            poster=st.form_submit_button('Generar vista',key=key+'_poster',disabled=not ready,icon=':material/photo:')
            preview=st.form_submit_button('Probar animación · calidad ligera',key=key+'_preview',disabled=not ready,icon=':material/play_arrow:')
            final=st.form_submit_button('Generar recurso Full HD',key=key+'_final',disabled=not ready,type='primary',icon=':material/movie:')
        if poster or preview or final:
            recipe={**base,'duration':duration,'yaw':yaw,'pitch':pitch,'distance':distance,'orbit':orbit,
                'mountain':mountain,'light':light,'ground':ground,'rock':rock,'water':water,'background':background,'moist':moist,'rain':rain}
            try:
                mode='poster' if poster else 'preview' if preview else 'final'
                identifier=start_job(recipe,mode=mode,store=store)
                st.session_state[key+'_job']=identifier;st.rerun()
            except (ValueError,OSError) as error:st.error(str(error))
        st.caption('Cambiar los controles no inicia un render. Se aplican al pulsar Generar. Regenerar un objeto conserva los textos, su posición y la duración ya editada en Studio.')
    with canvas:
        recent=_recent_jobs(store)
        if recent:
            selected_job=st.selectbox('Renders 3D de esta biblioteca',[None,*recent],key=key+'_recent',
                format_func=lambda value:'Selecciona un render guardado…' if value is None else
                    {'preview':'Prueba ligera','final':'Full HD'}[value.rsplit('-',1)[-1]]+' · '+value[:8])
            if selected_job and st.button('Abrir render guardado',key=key+'_open_job'):
                st.session_state[key+'_job']=selected_job;st.rerun()
        identifier=st.session_state.get(key+'_job')
        if not identifier:
            st.info('Ajusta la cámara y genera una vista. Después prueba la animación y crea el recurso final para tu video.')
        else:
            current=job_status(identifier,store)
            running=current['state'] in ('queued','running')
            @st.fragment(run_every='2s' if running else None)
            def progress():
                status=job_status(identifier,store)
                st.progress(max(0.,min(1.,float(status.get('progress',0)))),text=status.get('message','Render Blender'))
                if status['state'] in ('queued','running'):
                    if st.button('Cancelar render',key=key+'_cancel'):
                        cancel_job(identifier,store);st.caption('Cancelación solicitada; la copia original no cambia.')
                elif running:st.rerun(scope='app')
            progress()
            if current['state']=='complete':
                try:
                    folder,recipe,receipt=verified_product(identifier,store)
                    st.image(str(folder/'poster.png'),width='stretch',alt='Escena 3D orográfica renderizada en Blender')
                    if identifier.endswith('-poster'):st.caption('Vista fija. Genera la animación para incorporarla al video.')
                    else:
                        st.video(str(folder/'video.mp4'),alt='Animación 3D orográfica')
                        final_product=identifier.endswith('-final')
                        if not final_product:st.caption('Animación ligera: genera Full HD antes de incorporarla al video final.')
                        open_canvas=st.button('Abrir recurso en el lienzo',key=key+'_edit',disabled=not final_product,type='primary')
                        insert=st.button('Añadir como escena a mi video',key=key+'_insert',disabled=not final_product or project is None)
                        replace=st.button('Actualizar objeto 3D · conservar diseño',key=key+'_replace',disabled=not final_product or target is None)
                        if open_canvas or insert or replace:
                            from studio_media import import_asset
                            from studio_blender_scene import create_scene_project,replace_render
                            from studio_resource_projects import insert_saved_resource
                            asset=import_asset((folder/'video.mp4').read_bytes(),'orografia-blender.mp4')
                            if replace:candidate=replace_render(project,target['id'],recipe,asset,identifier)
                            else:
                                definition=project['studio']['output_profile'] if insert else {'id':selected}
                                resource=create_scene_project(recipe,asset,identifier,title,definition)
                                candidate=insert_saved_resource(project,resource) if insert else resource
                            on_change(candidate)
                    st.download_button('Descargar escena Blender editable',data=(folder/'scene.blend').read_bytes(),
                        file_name='ecuador-vivo-orografia.blend',mime='application/octet-stream',key=key+'_blend')
                    st.caption(f"{receipt['frames']} cuadros · Blender {receipt['version']} · {receipt['render_seconds']:g} s de render · receta y archivos verificados")
                except (ValueError,OSError,TypeError,KeyError) as error:st.error(str(error))
            elif current['state'] in ('failed','cancelled','missing'):
                st.warning(current.get('message','El render no está disponible.'))
        with st.expander('Qué explica y qué no'):
            st.caption('El relieve, las gotas y el umbral de condensación son ilustrativos. No son un DEM, viento observado, simulación de microfísica ni pronóstico local. Una nube no siempre produce lluvia.')
            st.markdown('[NOAA/NWS · ascenso orográfico](https://forecast.weather.gov/glossary.php?word=OROGRAPHIC)')
