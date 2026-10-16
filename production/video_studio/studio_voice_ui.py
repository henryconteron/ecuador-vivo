"""Native voice/subtitle controls over the existing durable Studio session."""
import copy
import hashlib
import json
from pathlib import Path
import uuid

import pandas as pd
import streamlit as st

from studio_captions import DEFAULT_CAPTION_STYLE, export_captions, parse_captions, prepare_captions
from studio_editing import timeline_rows
from studio_media import import_asset
from studio_typography import FONT_FAMILIES
from studio_voice import MAX_AUDIO_TRACKS, audio_media_path, validate_audio_tracks


def _audio_mime(name):
    return {'.wav':'audio/wav','.mp3':'audio/mpeg','.m4a':'audio/mp4'}.get(Path(str(name)).suffix.lower(),'audio/wav')


def _commit(session,candidate,key,message):
    session.commit(candidate)
    session.state[key+'_notice']=message
    st.rerun()


def _add_voice(session,key,total):
    with st.container(border=True):
        st.subheader('Añadir tu voz',anchor=False)
        st.caption('Audio local: no se envía a servicios de transcripción. MP3, WAV o M4A; máximo 100 MB.')
        source=st.segmented_control('Origen',['Archivo','Micrófono'],default='Archivo',key=key+'_source')
        if source=='Micrófono':
            upload=st.audio_input('Grabar voz',sample_rate=48000,key=key+'_microphone')
        else:
            upload=st.file_uploader('Archivo de voz',type=['mp3','wav','m4a'],max_upload_size=100,key=key+'_upload')
        if upload is not None:
            st.audio(upload.getvalue(),format=_audio_mime(getattr(upload,'name','grabacion.wav')),
                     alt='Escuchar la voz antes de añadirla al video')
        if st.button('Añadir voz al video',type='primary',icon=':material/mic:',
                     disabled=upload is None,key=key+'_add'):
            try:
                if len(session.project['studio'].get('audio_tracks',[]))>=MAX_AUDIO_TRACKS:
                    raise ValueError('Ya hay 16 pistas. Quita una antes de añadir otra.')
                record=import_asset(upload.getvalue(),getattr(upload,'name','grabacion.wav'))
                candidate=copy.deepcopy(session.project); studio=candidate['studio']
                aid=next((aid for aid,value in studio['media'].items()
                          if value.get('kind')=='audio' and value.get('sha256')==record['sha256']),None)
                aid=aid or 'audio-'+record['sha256'][:20]
                studio['media'][aid]=record
                duration=min(record['duration'],total/30)
                studio.setdefault('audio_tracks',[]).append({'id':'voice-'+uuid.uuid4().hex[:12],
                    'asset_id':aid,'start':0.,'trim_in':0.,'trim_out':duration,
                    'duration':duration,'mute':False,'volume':1.,'loop':False})
                validate_audio_tracks(studio,total)
                _commit(session,candidate,key,'Voz añadida. Ajusta su inicio y recorte; escucha el montaje con Reproducir.')
            except (ValueError,OSError,TypeError) as error: st.error(str(error))


def _voice_tracks(session,key,total):
    tracks=validate_audio_tracks(session.project['studio'],total)
    if not tracks:
        st.info('Todavía no hay una pista de voz. Puedes subirla o grabarla arriba.')
        return
    st.subheader('Pistas del video',anchor=False)
    by_id={track['id']:track for track in tracks}
    media=session.project['studio']['media']
    selected=st.selectbox('Pista de voz',list(by_id),key=key+'_selected',
        format_func=lambda tid:media[by_id[tid]['asset_id']].get('name',tid)+' · '+tid[-6:])
    track=by_id[selected]; record=media[track['asset_id']]
    st.audio(str(audio_media_path(record['path'])),format=_audio_mime(record['path']),
             alt='Audio original de la pista seleccionada')
    st.caption(f"Origen: {record['duration']:.2f} s · video: {total/30:.2f} s · tiempos globales, no relativos a cada escena.")
    with st.form(key+'_track_'+selected):
        with st.container(horizontal=True):
            start=st.number_input('Inicio en el video (s)',min_value=0.,max_value=total/30,
                value=track['start'],step=1/30,format='%.3f')
            duration=st.number_input('Duración de la pista (s)',min_value=1/30,max_value=total/30,
                value=track['duration'],step=1/30,format='%.3f')
        with st.container(horizontal=True):
            left=st.number_input('Recorte inicial del audio (s)',min_value=0.,max_value=float(record['duration']),
                value=track['trim_in'],step=1/30,format='%.3f')
            right=st.number_input('Recorte final del audio (s)',min_value=0.,max_value=float(record['duration']),
                value=track['trim_out'],step=1/30,format='%.3f')
        volume=st.slider('Volumen',0.,2.,track['volume'],step=.05,help='1 = volumen original; 0 = silencio.')
        with st.container(horizontal=True):
            mute=st.checkbox('Silenciar esta pista',value=track['mute'])
            loop=st.checkbox('Repetir el fragmento',value=track['loop'])
        st.caption('Sin repetir: si la pista dura más que el fragmento, el resto queda en silencio. Nunca alarga el video.')
        saved=st.form_submit_button('Guardar pista',type='primary')
    if saved:
        try:
            candidate=copy.deepcopy(session.project)
            updated={**track,'start':start,'duration':duration,'trim_in':left,'trim_out':right,
                     'volume':volume,'mute':mute,'loop':loop}
            candidate['studio']['audio_tracks']=[updated if row['id']==selected else row
                for row in candidate['studio'].get('audio_tracks',[])]
            validate_audio_tracks(candidate['studio'],total)
            _commit(session,candidate,key,'Pista guardada.')
        except (ValueError,OSError,TypeError) as error: st.error(str(error))
    if st.button('Quitar pista del video',icon=':material/delete:',key=key+'_remove_'+selected):
        try:
            candidate=copy.deepcopy(session.project)
            candidate['studio']['audio_tracks']=[row for row in candidate['studio']['audio_tracks'] if row['id']!=selected]
            _commit(session,candidate,key,'Pista retirada del video. El audio original permanece en la biblioteca.')
        except (ValueError,OSError,TypeError) as error: st.error(str(error))


def _caption_style(style):
    style={**DEFAULT_CAPTION_STYLE,**style}
    with st.expander('Tipografía, posición y fondo'):
        st.caption('Medidas relativas al lienzo: la misma caja se adapta a vertical, horizontal y cuadrado.')
        style['font_family']=st.selectbox('Tipografía',FONT_FAMILIES,index=FONT_FAMILIES.index(style['font_family']))
        with st.container(horizontal=True):
            style['font_size']=st.number_input('Tamaño del texto (% del alto)',.5,15.,float(style['font_size']*100),step=.1)/100
            style['min_font_size']=st.number_input('Tamaño mínimo (% del alto)',.5,15.,float(style['min_font_size']*100),step=.1)/100
        with st.container(horizontal=True):
            for field,label in (('x','Izquierda (%)'),('y','Arriba (%)'),('width','Ancho (%)'),('height','Alto (%)')):
                style[field]=st.number_input(label,0.,100.,float(style[field]*100),step=1.)/100
        with st.container(horizontal=True):
            style['color']=st.color_picker('Color del texto',style['color'])
            style['background']=st.color_picker('Fondo del subtítulo',style['background'])
            style['stroke_color']=st.color_picker('Borde del texto',style['stroke_color'])
        style['background_opacity']=st.slider('Opacidad del fondo',0.,1.,float(style['background_opacity']),step=.05)
        with st.container(horizontal=True):
            style['stroke_width']=st.number_input('Grosor del borde (% del alto)',0.,1.,float(style['stroke_width']*100),step=.05)/100
            style['padding']=st.number_input('Margen interior (% del alto)',0.,10.,float(style['padding']*100),step=.1)/100
        style['alignment']=st.selectbox('Alineación',['left','center','right'],
            index=['left','center','right'].index(style['alignment']),format_func=lambda v:{'left':'Izquierda','center':'Centro','right':'Derecha'}[v])
        style['bold']=st.checkbox('Texto en negrita',value=style['bold'])
    return style


def _subtitles(session,key,total):
    captions=copy.deepcopy(session.project['studio'].get('captions',{'enabled':False,'cues':[],'style':{}}))
    revision=hashlib.sha256(json.dumps(captions,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()[:16]
    with st.container(border=True):
        st.subheader('Importar subtítulos',anchor=False)
        upload=st.file_uploader('Archivo SRT o VTT',type=['srt','vtt'],max_upload_size=2,key=key+'_caption_upload')
        replace=st.checkbox('Reemplazar los subtítulos actuales',value=False,key=key+'_replace')
        if st.button('Importar subtítulos',disabled=upload is None,key=key+'_import_captions'):
            try:
                if captions.get('cues') and not replace:
                    raise ValueError('Confirma «Reemplazar los subtítulos actuales» para no perder tu edición por accidente.')
                cues=parse_captions(upload.getvalue(),upload.name)
                imported={**captions,'enabled':True,'cues':cues}
                prepare_captions(imported,total)
                candidate=copy.deepcopy(session.project); candidate['studio']['captions']=imported
                _commit(session,candidate,key,'Subtítulos importados. Revisa el texto y los tiempos antes de exportar.')
            except (ValueError,OSError,TypeError) as error: st.error(str(error))
    st.subheader('Texto y sincronización',anchor=False)
    st.caption(f'Video: {total/30:.2f} s. Añade o elimina filas en la tabla; escribe los tiempos en segundos globales, en orden y sin solaparlos.')
    rows=pd.DataFrame(captions.get('cues',[]),columns=['id','start','end','text'])
    rows=rows.astype({'id':'string','start':'float64','end':'float64','text':'string'})
    with st.form(key+'_captions_form'):
        enabled=st.checkbox('Mostrar subtítulos en el video',value=captions.get('enabled',False))
        edited=st.data_editor(rows,num_rows='dynamic',hide_index=True,disabled=['id'],
            key=key+'_caption_table_'+revision,alt='Editar texto, inicio y final de cada subtítulo',column_config={
                'id':None,'start':st.column_config.NumberColumn('Inicio (s)',min_value=0.,max_value=total/30,step=1/30,format='%.3f',required=True),
                'end':st.column_config.NumberColumn('Final (s)',min_value=0.,max_value=total/30,step=1/30,format='%.3f',required=True),
                'text':st.column_config.TextColumn('Texto',required=True,max_chars=800,width='large')})
        style=_caption_style(captions.get('style',{}))
        saved=st.form_submit_button('Guardar subtítulos',type='primary')
    if saved:
        try:
            cues=[]
            for row in edited.to_dict('records'):
                identifier=row.get('id')
                if pd.isna(identifier) or not identifier: identifier='caption-'+uuid.uuid4().hex[:12]
                cues.append({'id':identifier,'start':row['start'],'end':row['end'],'text':row['text']})
            updated={'enabled':enabled,'cues':cues,'style':style}; prepare_captions(updated,total)
            candidate=copy.deepcopy(session.project); candidate['studio']['captions']=updated
            _commit(session,candidate,key,'Subtítulos guardados. Se verán tanto en el lienzo como en el MP4.')
        except (ValueError,OSError,TypeError) as error: st.error(str(error))
    if captions.get('cues'):
        with st.container(horizontal=True):
            for suffix in ('srt','vtt'):
                st.download_button('Descargar '+suffix.upper(),export_captions(captions['cues'],suffix),
                    file_name='subtitulos.'+suffix,mime='text/plain' if suffix=='srt' else 'text/vtt',key=key+'_download_'+suffix)
    st.caption('No hay transcripción automática en esta entrega. Puedes escribir los subtítulos o importar un archivo; todo queda guardado en el mismo proyecto.')


def show_voice_captions(session,*,key='voice_captions'):
    st.caption('Narración y subtítulos · misma timeline que tus mapas, escenas y métricas.')
    if session.state.get(key+'_notice'): st.success(session.state.pop(key+'_notice'))
    total=timeline_rows(session.project['studio'])[-1]['end_frame']
    panel=st.segmented_control('Editar',['Voz','Subtítulos'],default='Voz',key=key+'_panel')
    try:
        if panel=='Subtítulos': _subtitles(session,key,total)
        else:
            _add_voice(session,key,total)
            _voice_tracks(session,key,total)
    except (ValueError,OSError,TypeError) as error: st.error(str(error))
    if st.button('Cerrar',key=key+'_close'):
        session.state.pop(session.key+'_dialog',None)
        st.rerun()
