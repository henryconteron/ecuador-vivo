"""Data → visualization → secure montage snapshot; no computation on styling."""
import copy
import hashlib
import io
import json
import uuid
from pathlib import Path
import streamlit as st
from calculation_results import summary_results
from visualizations import VisualizationSpec, render_visualization, snapshot_checksum
from storyboard import dimensions, store_media, cards_for

SCIENTIFIC_FIELDS=('source','start','end','entries','bbox','scale','offset','nodata',
                   'clip_ecuador','kind','variable','units','cadence','source_units',
                   'endcard_aggregation','endcard_aggregation_mode','endcard_accumulated_units')
LABELS={'kpi':'KPI','metric':'Métrica','horizontal_bar':'Barras horizontales',
        'vertical_bar':'Barras verticales','dot':'Dots','lollipop':'Lollipop',
        'line':'Línea por categoría','ranking':'Ranking','comparison':'Comparación'}


def scientific_identity(project):
    identity={key:project[key] for key in SCIENTIFIC_FIELDS if key in project}
    from data import scientific_file_versions
    versions=scientific_file_versions(project)
    return hashlib.sha256(json.dumps([identity,versions],sort_keys=True,allow_nan=False).encode()).hexdigest()


def capture_snapshot(project,calculate, *, progress=None, cancelled=None):
    """Explicit scientific operation, with original source hashes for recovery."""
    from model import validate
    from data import rain_path
    from jobs import sha256
    settings=copy.deepcopy(project)
    rows=validate(settings)
    if settings['kind']!='continuous':
        raise ValueError('Estas métricas requieren datos continuos; no promediar códigos categóricos.')
    hashes={};records=[]
    for index, row in enumerate(rows):
        if cancelled and cancelled():
            raise InterruptedError('Preparación científica cancelada.')
        path,url=rain_path(row['date']) if settings['source']=='chirps' else (Path(row['path']),row.get('source_url',''))
        path=str(path)
        if path not in hashes: hashes[path]=sha256(path)
        records.append(dict(date=row['date'],band=row.get('band',1),file=path,sha256=hashes[path],source_url=url))
        if progress: progress(index + 1, len(rows), row['date'])
    identity=scientific_identity(settings)
    # Include content identity in the cache key for explicit captures, even if
    # a file replacement preserves its mtime and byte size.
    settings['_scientific_revision_sha256']=hashlib.sha256(json.dumps(records,sort_keys=True).encode()).hexdigest()
    results=summary_results(settings,calculate(settings))
    if cancelled and cancelled():
        raise InterruptedError('Preparación científica cancelada.')
    if identity!=scientific_identity(settings) or any(sha256(path)!=value for path,value in hashes.items()):
        raise ValueError('La fuente cambió durante el cálculo; carga nuevamente los resultados.')
    return dict(results=results,source_records=records,scientific_identity=identity)


def add_visualization_card(project,spec,snapshot):
    """Store exactly the preview PNG as an explicit, reproducible static card.

    The original project is updated only after validating the candidate montage.
    Hash-addressed assets can be reused; no source project/file is overwritten.
    """
    image=render_visualization(spec,snapshot['results'],dimensions(project))
    buffer=io.BytesIO();image.save(buffer,format='PNG')
    asset=store_media(buffer.getvalue(),'visualizacion-'+spec.kind+'.png')
    candidate=copy.deepcopy(project)
    existing=cards_for(candidate)
    cards=[{key:value for key,value in row.items() if key not in ('frames','seconds')}
           for row in existing]
    identifier='viz.'+uuid.uuid4().hex[:12]
    result=copy.deepcopy(snapshot['results'][spec.binding['result_id']])
    cards.append(dict(asset,id=identifier,label=LABELS[spec.kind],duration=6.,fit='contain',
                      title='',citation='',data_visualization={
                          'spec':spec.to_dict(),'result':result,
                          'source_records':copy.deepcopy(snapshot['source_records']),
                          'scientific_identity':snapshot['scientific_identity'],
                          'output_dimensions':list(image.size),'mode':'static_snapshot',
                          'image_sha256':asset['sha256']}))
    metadata=cards[-1]['data_visualization']
    metadata['snapshot_sha256']=snapshot_checksum(metadata)
    candidate['storyboard']={'enabled':True,'cards':cards}
    cards_for(candidate)
    project['storyboard']=candidate['storyboard']
    return identifier


def show_visualizations(project,calculate, *, key='visualizations',on_create_studio=None):
    st.header('Visualizaciones de datos')
    st.caption('Los valores se calculan al cargar resultados. Cambiar el tipo, color o título reutiliza el mismo resultado.')
    try:
        identity=scientific_identity(project)
    except (ValueError,OSError,TypeError) as error:
        st.error(str(error));return
    state_key=key+'_snapshot'
    if st.button('Cargar resultados científicos',key=key+'_load'):
        try:
            with st.spinner('Calculando y registrando fuentes…'):
                st.session_state[state_key]=capture_snapshot(project,calculate)
                identity=scientific_identity(project)
        except (ValueError,OSError,TypeError) as error:
            st.error(str(error))
    snapshot=st.session_state.get(state_key)
    if not snapshot:
        st.info('Carga los resultados del proyecto para crear una visualización.');return
    if snapshot['scientific_identity']!=identity:
        st.warning('Cambió la fuente, variable, periodo o metodología. Carga nuevamente los resultados.');return
    if on_create_studio is not None and st.button('Crear proyecto en Studio',type='primary',key=key+'_studio'):
        try: on_create_studio(snapshot)
        except (ValueError,OSError,TypeError,KeyError) as error:st.error(str(error))
    with st.container(horizontal=True,wrap=True):
        kind=st.selectbox('Visualización',list(LABELS),format_func=LABELS.get,key=key+'_kind')
        scalar=kind in ('kpi','metric')
        options=[identifier for identifier,result in snapshot['results'].items()
                 if ('rows' not in result if scalar else 'rows' in result)]
        identifier=st.selectbox('Resultado calculado',options,key=key+'_result_'+str(scalar))
        color=st.color_picker('Color de datos','#13bfd1',key=key+'_color')
    with st.expander('Etiquetas y orden'):
        title=st.text_input('Título de la visualización',max_chars=200,key=key+'_title')
        descending=st.checkbox('Orden descendente',value=True,disabled=kind in ('line','comparison'),key=key+'_descending')
        top=st.number_input('Top N · 0 muestra todos',min_value=0,max_value=1000,value=5,step=1,
                            disabled=scalar or kind in ('line','comparison'),key=key+'_top')
    try:
        spec=VisualizationSpec(kind=kind,binding={'result_id':identifier,'field':'value' if scalar else 'rows'},
                               style={'color':color,'title':title},descending=descending,
                               top_n=None if scalar or kind in ('line','comparison') or not top else int(top))
        image=render_visualization(spec,snapshot['results'],dimensions(project))
        st.image(image,width=600,alt=title or LABELS[kind])
        result=snapshot['results'][identifier]
        provenance=result['provenance']
        for warning in provenance.get('warnings',[]):
            st.warning(warning)
        st.caption(f'{result["units"]} · {provenance.get("spatial_domain")} · {provenance.get("temporal_operation")} · {provenance.get("weighting")}')
        if kind=='line': st.caption('Eje X: categorías equidistantes en el orden del resultado; no representa intervalos temporales inferidos.')
        output=io.BytesIO();image.save(output,format='PNG')
        st.download_button('Descargar PNG',output.getvalue(),file_name='ecuador-vivo-visualizacion.png',mime='image/png',key=key+'_png')
        if st.button('Añadir instantánea al montaje',key=key+'_add'):
            add_visualization_card(project,spec,snapshot)
            st.success('Visualización añadida al montaje; su PNG y procedencia se conservan juntos.')
        st.caption('La tarjeta añadida es una instantánea. Si cambias datos, formato o estilo, genera otra; el montaje encaja la anterior sin deformarla.')
    except (ValueError,OSError,TypeError) as error:
        st.error(str(error))
