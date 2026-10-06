"""Ecuador Vivo local video studio. Launch with Abrir editor de videos.vbs."""
import copy
import datetime as dt
import io
import json
import os
from pathlib import Path
import uuid

import pandas as pd
import streamlit as st

from model import default_project, upgrade_project, validate, timeline, PALETTES, STORE, ROOT
from data import boundary, load_values, store_upload, inspect_file, rain_path
from render import compose
from social import guided_preview
from jobs import start_job, read_json, write_json, statuses

st.set_page_config(page_title='Ecuador Vivo · Estudio de video', page_icon=':material/movie:', layout='wide')
st.session_state.setdefault('project', default_project())
st.session_state.setdefault('revision', 0)
st.session_state.setdefault('preview', None)
st.session_state.setdefault('import_rows', [])
st.session_state.setdefault('active_job', None)
p = upgrade_project(st.session_state.project)
revision = st.session_state.revision


def replace_project(project):
    st.session_state.project = project
    st.session_state.revision += 1
    st.session_state.preview = None
    st.session_state.import_rows = []


@st.cache_data(max_entries=8, show_spinner=False)
def preview_bytes(project_json, index):
    project = json.loads(project_json)
    rows = validate(project)
    values, _ = load_values(project, rows[index])
    image = compose(project, values, boundary(), rows[index]['date'], index, len(rows))
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()


def snapshot():
    return json.dumps(p, ensure_ascii=False, sort_keys=True)


def save_project():
    target = STORE / 'projects' / (dt.datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:6] + '.json')
    write_json(target, p)
    return target


with st.sidebar:
    st.title('Ecuador Vivo', icon=':material/public:')
    st.caption('ESTUDIO DE VIDEO · LOCAL')
    section = st.radio('Espacio de trabajo', ['Editor', 'Exportaciones', 'Cómo usarlo'], key='section')
    st.caption('Una plantilla, tus datos y tu historia.')
    st.subheader('Tus proyectos')
    projects = sorted((STORE / 'projects').glob('*.json'), reverse=True)
    chosen = st.selectbox('Abrir un proyecto guardado', [None] + projects,
                          format_func=lambda f: 'Selecciona…' if f is None else (read_json(f, {}).get('name', f.stem) + ' · ' + f.stem[:15]))
    if st.button('Abrir proyecto', disabled=chosen is None, icon=':material/folder_open:'):
        candidate = read_json(chosen)
        try:
            validate(candidate)
            replace_project(candidate)
            st.rerun()
        except (ValueError, TypeError, KeyError) as error:
            st.error(f'No se pudo abrir: {error}')
    if st.button('Nueva plantilla original', icon=':material/add:'):
        replace_project(default_project())
        st.rerun()
    with st.expander('Importar proyecto JSON'):
        restored = st.file_uploader('Proyecto exportado', type=['json'], key='restore_file')
        if st.button('Restaurar ajustes', disabled=restored is None):
            try:
                candidate = json.loads(restored.getvalue())
                validate(candidate)
                replace_project(candidate)
                st.rerun()
            except (ValueError, TypeError, KeyError) as error:
                st.error(f'No se pudo restaurar: {error}')
    st.caption('Guarda tu proyecto antes de abrir otro. Los videos se guardan en tu equipo.')

if section == 'Cómo usarlo':
    st.title('Del dato al video', icon=':material/help:')
    st.markdown('''
1. En **Editor → Datos**, elige lluvia automática o tus GeoTIFF.
2. En **Diseño**, cambia título, descripción, fondo y colores. En **Textos y créditos**,
   añade tu nombre, marca, agradecimientos, fuentes y etiquetas del video.
3. En **Mapa y tiempo**, elige encuadre, ciudades, duración y resolución.
4. Pulsa **Actualizar vista previa**. Puedes revisar cualquier fecha.
5. Pulsa **Generar video**. Sigue el avance y descarga el resultado en **Exportaciones**.

**Lluvia automática:** reutiliza los datos de 2024 que ya tienes y descarga fechas
faltantes desde CHIRPS. Una fecha sin publicar produce un error, nunca se rellena con cero.

**GeoTIFF:** importa una variable por video. Cada banda seleccionada corresponde a
una fecha. Puedes importar temperatura, índices o categorías. Revisa las fechas,
unidades, factor, desplazamiento y NoData; el editor no aplica máscaras QA por ti.
Los datos deben llegar preparados científicamente. Las categorías conservan sus códigos.

**Duración:** todas las fechas aparecen, sin inventar transiciones entre ellas.
La duración se redondea al cuadro más próximo a 30 fps. 366 fechas × 1,5 segundos
reproduce el ritmo del video anual original.

**Guardar proyecto** conserva tus ajustes. Cada exportación crea una carpeta nueva,
su MP4, imágenes y recibo con fuentes. No sobrescribe el video original.

Puedes cerrar la pestaña mientras se exporta; mantén encendida la computadora.
Los proyectos no incluyen los TIFF dentro del JSON: respalda también los archivos importados.
Esta primera versión produce video vertical sin audio y una variable principal por video.
''')
    st.code(str(STORE), language=None)
    st.caption('Datos y resultados permanecen en _local, fuera de Git. Descarga automática disponible para CHIRPS; otras fuentes se importan.')
    st.stop()


@st.fragment(run_every=3)
def jobs_panel():
    all_jobs = statuses()
    if not all_jobs:
        st.info('Todavía no has exportado desde este editor. Empieza con una prueba de siete días.')
        return
    # Render only one video player at a time; long videos do not flood page memory.
    selected = st.selectbox('Exportación', [str(folder) for folder, _ in all_jobs],
        format_func=lambda value: read_json(Path(value)/'project.json', {}).get('name', Path(value).name) + ' · ' + Path(value).name)
    folder = Path(selected)
    state = read_json(folder / 'status.json', {})
    st.progress(min(1., max(0., state.get('progress', 0.))), text=state.get('message', 'Preparando…'))
    active = state.get('state') in ('queued', 'running')
    if active:
        st.caption('El trabajo continúa en segundo plano. Puedes volver al editor.')
        if st.button('Cancelar esta exportación', key='cancel_' + folder.name, icon=':material/stop:'):
            (folder / 'cancel.request').touch()
            st.info('Cancelación solicitada; se detendrá al terminar la lectura o el cuadro en curso.')
    elif state.get('state') == 'complete':
        st.success('MP4 terminado · conserva el diseño y la configuración de este proyecto')
        with st.container(width=400):
            st.video(str(folder / 'ecuador-vivo.mp4'), alt='Video cartográfico exportado desde Ecuador Vivo')
        with st.container(horizontal=True):
            st.download_button('Descargar MP4', data=lambda: (folder/'ecuador-vivo.mp4').read_bytes(),
                               file_name='ecuador-vivo-' + folder.name + '.mp4', mime='video/mp4', icon=':material/download:')
            st.download_button('Recibo de fuentes', (folder/'receipt.json').read_bytes(),
                               file_name='receipt.json', mime='application/json')
            if st.button('Abrir carpeta', key='open_' + folder.name, icon=':material/folder:'):
                os.startfile(folder)
    else:
        st.warning(state.get('message', 'El trabajo no terminó.'))
        st.caption('El original y los datos descargados se conservan. Corrige el problema y genera una nueva exportación.')
    st.caption(str(folder))


if section == 'Exportaciones':
    st.title('Tus exportaciones', icon=':material/video_library:')
    jobs_panel()
    st.stop()

st.title('Cuenta una historia con tus mapas', icon=':material/movie:')
st.caption('El diseño de Ecuador Vivo, ahora en tus manos. Datos reales · vista previa · MP4 vertical.')
left, right = st.columns([1.25, 1], gap='large')

with left:
    step = st.segmented_control('Controles', ['Datos', 'Diseño', 'Textos y créditos', 'Mapa y tiempo'], default='Datos', key='step', wrap=True)
    with st.container(border=True):
        if step == 'Datos':
            st.subheader('Elige qué quieres contar')
            choice = st.selectbox('Origen', ['Lluvia CHIRPS · automática', 'Mis archivos GeoTIFF'],
                                  index=0 if p['source'] == 'chirps' else 1, key=f'source_{revision}')
            source = 'chirps' if choice.startswith('Lluvia') else 'local'
            if source != p['source']:
                p['source'] = source
                if source == 'chirps':
                    defaults = default_project()
                    for key in ('kind', 'variable', 'citation', 'source_url', 'units', 'legend', 'note', 'resolution_note', 'scale', 'offset', 'stops', 'palette', 'cadence'):
                        p[key] = defaults[key]
                else:
                    p.update(citation='', source_url='', resolution_note='Resolución y calidad: según el archivo fuente',
                             note='Serie importada · revisar calidad y fechas', cadence='Por observación')
                st.session_state.revision += 1
                st.rerun()
            if source == 'chirps':
                dates = st.columns(2)
                p['start'] = str(dates[0].date_input('Desde', dt.date.fromisoformat(p['start']), min_value=dt.date(1981,1,1), key=f'start_{revision}'))
                p['end'] = str(dates[1].date_input('Hasta', dt.date.fromisoformat(p['end']), key=f'end_{revision}'))
                st.caption('Lluvia diaria · mm/día · resolución original ≈5,6 km. Busca primero en tu caché y descarga solo lo que falta.')
                try:
                    rows = timeline(p)
                    cached = sum(1 for row in rows if any((ROOT/'_local'/'climate-studio').glob('*/chirps-v2.0.'+row['date'].replace('-','.')+'.tif.gz')) or (STORE/'cache'/'chirps-v2'/('chirps-v2.0.'+row['date'].replace('-','.')+'.tif.gz')).exists())
                    st.caption(f'{cached} de {len(rows)} fechas ya disponibles en tu computadora.')
                except ValueError as error:
                    st.error(str(error))
            else:
                st.caption('Carga TIFF numéricos y georreferenciados. Una banda seleccionada por fecha; se copian al archivo local del editor.')
                files = st.file_uploader('GeoTIFF de tu variable', type=['tif','tiff'], accept_multiple_files=True, key=f'files_{revision}')
                if st.button('Leer archivos', disabled=not files, key='read_files'):
                    try:
                        imported = []
                        with st.spinner('Leyendo bandas y fechas…'):
                            for file in files:
                                path = store_upload(file.name, file.getvalue())
                                imported.extend(inspect_file(path, file.name))
                        st.session_state.import_rows = imported
                    except Exception as error:
                        st.error(str(error))
                if st.session_state.import_rows:
                    st.caption('Marca únicamente la banda de tu variable. Corrige fechas AAAA-MM-DD; no incluyas bandas de calidad como fechas.')
                    table = pd.DataFrame(st.session_state.import_rows).drop(columns='path')
                    edited = st.data_editor(table, hide_index=True, disabled=['archivo','banda','nombre_banda'],
                                            key=f'import_table_{revision}', alt='Bandas a incluir y fechas de los archivos')
                    if st.button('Usar esta serie', key='apply_series'):
                        try:
                            entries = []
                            for i, row in edited.iterrows():
                                if row['usar']:
                                    date = str(dt.date.fromisoformat(str(row['fecha']).strip()))
                                    entries.append({'date': date, 'band': int(row['banda']), 'path': st.session_state.import_rows[i]['path']})
                            candidate = copy.deepcopy(p)
                            candidate['entries'] = entries
                            timeline(candidate)
                            p['entries'] = entries
                            st.success(f'{len(entries)} observaciones listas.')
                        except (ValueError, TypeError) as error:
                            st.error(f'Revisa la selección: {error}')
                st.caption(f'Serie activa: {len(p["entries"])} fechas.')
                preset = st.selectbox('Preparación rápida de variable', ['Personalizada', 'Temperatura ya en °C', 'Temperatura en Kelvin', 'NDVI / MNDWI', 'Cobertura Dynamic World'], key=f'preset_{revision}')
                if st.button('Aplicar preparación', disabled=preset=='Personalizada'):
                    if preset.startswith('Temperatura'):
                        p.update(variable='Temperatura', title='El pulso del calor.', description='Mira cómo cambia la temperatura.',
                                 legend='TEMPERATURA', kind='continuous', units='°C', scale=1.,
                                 offset=-273.15 if preset.endswith('Kelvin') else 0.,
                                 stops=[-10,0,5,10,15,20,30,40], palette=list(PALETTES['Calor']))
                    elif preset == 'NDVI / MNDWI':
                        p.update(variable='Índice espectral', title='Un paisaje en transformación.',
                                 description='Explora lo que revelan los índices.', legend='ÍNDICE', kind='continuous',
                                 units='adimensional', scale=1., offset=0., stops=[-1,-.5,0,.2,.4,.6,.8,1],
                                 palette=list(PALETTES['Vegetación']))
                    else:
                        p.update(variable='Cobertura', title='El territorio cambia.', description='Una historia contada desde el espacio.',
                                 legend='COBERTURA DEL SUELO', units='', kind='categorical', scale=1., offset=0.,
                                 classes=default_project()['classes'])
                    st.session_state.revision += 1
                    st.rerun()
                p['variable'] = st.text_input('Nombre de la variable', p['variable'], key=f'var_{revision}')
                p['kind'] = st.selectbox('Tipo de dato', ['continuous','categorical'], index=0 if p['kind']=='continuous' else 1,
                                       format_func=lambda x: 'Continuo: temperatura, lluvia, índices' if x=='continuous' else 'Categorías: coberturas, usos del suelo', key=f'kind_{revision}')
                p['cadence'] = st.selectbox('Cada mapa representa', ['Diaria','Mensual','Anual','Por observación'],
                                          index=['Diaria','Mensual','Anual','Por observación'].index(p['cadence']), key=f'cadence_{revision}')
                p['citation'] = st.text_input('Fuente / cita visible', p['citation'], max_chars=160, key=f'cite_{revision}')
                p['source_url'] = st.text_input('Enlace de la fuente', p['source_url'], key=f'url_{revision}')
                with st.expander('Unidades y conversión'):
                    p['units'] = st.text_input('Unidades finales', p['units'], key=f'units_{revision}')
                    p['scale'] = st.number_input('Factor: valor × factor + desplazamiento', value=float(p['scale']), format='%.6f', key=f'scale_{revision}')
                    p['offset'] = st.number_input('Desplazamiento', value=float(p['offset']), format='%.6f', key=f'offset_{revision}')
                    nodata = st.text_input('NoData adicional (vacío: usar el del TIFF)', '' if p['nodata'] is None else str(p['nodata']), key=f'nodata_{revision}')
                    try:
                        p['nodata'] = float(nodata) if nodata.strip() else None
                    except ValueError:
                        st.error('NoData debe ser numérico. Se conserva el valor anterior.')
                    st.caption('ERA5 en Kelvin: factor 1, desplazamiento −273,15. Si exportaste ya en °C: factor 1, desplazamiento 0. Se aplica únicamente esta conversión; no se aplican automáticamente factores embebidos ni máscaras QA.')
                    p['resolution_note'] = st.text_input('Nota de resolución', p['resolution_note'], key=f'resolution_{revision}')
        elif step == 'Diseño':
            st.subheader('Dale tu voz al mapa')
            p['name'] = st.text_input('Nombre del proyecto', p['name'], max_chars=100, key=f'name_{revision}')
            p['title'] = st.text_input('Título del video', p['title'], max_chars=100, key=f'title_{revision}')
            p['description'] = st.text_input('Descripción / subtítulo', p['description'], max_chars=150, key=f'desc_{revision}')
            p['legend'] = st.text_input('Título de la leyenda', p['legend'], max_chars=90, key=f'legend_{revision}')
            p['note'] = st.text_input('Nota explicativa', p['note'], max_chars=150, key=f'note_{revision}')
            colors = st.columns(3)
            p['background'] = colors[0].color_picker('Fondo', p['background'], key=f'bg_{revision}')
            p['text'] = colors[1].color_picker('Texto', p['text'], key=f'fg_{revision}')
            p['accent'] = colors[2].color_picker('Acento', p['accent'], key=f'accent_{revision}')
            if p['kind'] == 'continuous':
                palette = st.selectbox('Paleta de partida', list(PALETTES), key=f'palette_{revision}')
                if st.button('Aplicar paleta', key='apply_palette'):
                    p['palette'] = list(PALETTES[palette])
                    if len(p['stops']) != 8:
                        lo, hi = p['stops'][0], p['stops'][-1]
                        p['stops'] = [lo+(hi-lo)*i/7 for i in range(8)]
                    st.session_state.revision += 1
                    st.rerun()
                with st.expander('Editar valores y colores de la escala', expanded=True):
                    table = st.data_editor(pd.DataFrame({'valor':p['stops'], 'color':p['palette']}), hide_index=True,
                                           num_rows='dynamic', key=f'colors_{revision}', alt='Valores y colores de la leyenda continua')
                    if st.button('Aplicar escala', key='apply_scale'):
                        try:
                            candidate = copy.deepcopy(p)
                            candidate['stops'] = [float(v) for v in table['valor']]
                            candidate['palette'] = list(table['color'])
                            validate(candidate)
                            p.update(stops=candidate['stops'], palette=candidate['palette'])
                            st.success('Escala aplicada a todas las fechas.')
                        except (ValueError, TypeError) as error:
                            st.error(str(error))
            else:
                st.caption('La tabla inicial es la leyenda de Dynamic World. Sustitúyela si tu producto usa otros códigos; no se adivinan las clases.')
                classes = st.data_editor(pd.DataFrame(p['classes']), num_rows='dynamic', hide_index=True,
                                         key=f'classes_{revision}', alt='Códigos, nombres y colores de categorías')
                if st.button('Aplicar clases', key='apply_classes'):
                    candidate = copy.deepcopy(p)
                    candidate['classes'] = classes.to_dict('records')
                    try:
                        validate(candidate)
                        p['classes'] = candidate['classes']
                        st.success('Clases guardadas.')
                    except (ValueError, TypeError) as error:
                        st.error(str(error))
        elif step == 'Textos y créditos':
            st.subheader('Tu firma, tus palabras')
            st.caption('Los créditos personales no reemplazan la fuente de los datos. Las fechas y valores siguen ligados a tu serie.')
            p['author'] = st.text_input('Tu nombre / autoría', p['author'], max_chars=120,
                                        placeholder='Elaborado por Henry P. Conteron Moreta', key=f'author_{revision}')
            p['credits'] = st.text_input('Créditos adicionales / redes', p['credits'], max_chars=150,
                                         placeholder='Cartografía y edición · @tu_cuenta', key=f'credits_{revision}')
            p['brand'] = st.text_input('Marca en la cabecera', p['brand'], max_chars=120, key=f'brand_{revision}')
            with st.expander('Fuentes y notas del mapa', expanded=True):
                p['citation'] = st.text_input('Fuente científica visible', p['citation'], max_chars=180, key=f'credit_source_{revision}')
                p['source_url'] = st.text_input('Enlace de la fuente (se guarda en el recibo)', p['source_url'], key=f'credit_url_{revision}')
                p['boundary_note'] = st.text_input('Texto geográfico y crédito de límites', p['boundary_note'], max_chars=180,
                    placeholder='Automático: Ecuador continental · límites: geoBoundaries', key=f'boundary_note_{revision}')
                st.caption('Vacío mantiene el crédito geográfico automático. Si lo personalizas, conserva la atribución a geoBoundaries.')
                p['units'] = st.text_input('Unidades en la leyenda', p['units'], max_chars=40, key=f'credit_units_{revision}')
                p['resolution_note'] = st.text_input('Nota de resolución', p['resolution_note'], max_chars=180, key=f'credit_resolution_{revision}')
                field = 'scale_note' if p['kind'] == 'continuous' else 'category_note'
                p[field] = st.text_input('Explicación de la escala', p[field], max_chars=180, key=f'{field}_{revision}')
                st.caption('Título, subtítulo, título de leyenda y nota explicativa están en Diseño. Los nombres de las categorías están en su tabla de colores.')
            with st.expander('Fecha, contador y nombres de ciudades'):
                p['date_format'] = st.selectbox('Formato de fecha diaria', ['DD / MM / AAAA', 'AAAA-MM-DD', 'MM / DD / AAAA'],
                    index=['DD / MM / AAAA', 'AAAA-MM-DD', 'MM / DD / AAAA'].index(p['date_format']), key=f'date_format_{revision}')
                p['counter_label'] = st.text_input('Palabra del contador', p['counter_label'], max_chars=30,
                    placeholder='Automático: DÍA, MES, AÑO u OBS.', key=f'counter_{revision}')
                st.caption('Los números y las fechas provienen de los datos: cambiar el texto no cambia su significado.')
                for city in p['cities']:
                    p['city_labels'][city] = st.text_input(f'Etiqueta de {city}', p['city_labels'].get(city, city),
                        max_chars=60, key=f'city_label_{city}_{revision}')
                st.caption('Deja vacía una etiqueta para ocultar su nombre. Los puntos permanecen en sus coordenadas reales.')
            st.info('Pulsa Actualizar vista previa para ver tu firma. Guarda el proyecto para reutilizarla en otros videos.')
        else:
            st.subheader('Encuadre y ritmo')
            modes = {'social':'Redes sociales · TikTok / Reels', 'conservative':'Márgenes amplios · más espacio para la interfaz', 'original':'Original · sin protección para redes'}
            p['layout'] = st.selectbox('Distribución para publicar', list(modes), index=list(modes).index(p['layout']),
                                      format_func=modes.get, key=f'layout_{revision}')
            st.caption('9:16 sin estirar. Redes sociales reserva 220 px arriba, 440 abajo y 200 a la derecha en 1080p. Son márgenes editoriales, no una garantía de cada plataforma.')
            if p['layout']=='original':
                st.warning('El diseño original coloca información cerca de los bordes; puede quedar tapada por los controles de TikTok o Reels.')
            else:
                st.info('El mapa y los textos se redistribuyen dentro del área protegida. Si un texto no cabe con un tamaño legible, el editor pide acortarlo; no lo recorta.')
            region = st.selectbox('Encuadre rápido', ['Actual', 'Ecuador continental', 'Tena y Archidona'], key=f'region_{revision}')
            if st.button('Aplicar encuadre', disabled=region=='Actual'):
                p['bbox'] = [-81.5,-5.2,-75.,1.8] if region=='Ecuador continental' else [-78.04,-1.12,-77.55,-.72]
                st.session_state.revision += 1
                st.rerun()
            with st.expander('Límites del mapa'):
                coords = st.columns(2)
                for i, label in enumerate(['Oeste','Sur','Este','Norte']):
                    p['bbox'][i] = coords[i%2].number_input(label, value=float(p['bbox'][i]), format='%.4f', key=f'bbox_{i}_{revision}')
            p['clip_ecuador'] = st.toggle('Recortar datos a Ecuador', p['clip_ecuador'], key=f'clip_{revision}')
            p['cities'] = st.multiselect('Ciudades de referencia', ['Quito','Guayaquil','Cuenca','Tena','Archidona'], p['cities'], key=f'cities_{revision}')
            p['duration'] = st.number_input('Duración total del video (segundos)', min_value=0.1, max_value=7200., value=float(p['duration']), step=1., key=f'duration_{revision}')
            if st.button('Usar ritmo original: 1,5 s por fecha'):
                try:
                    p['duration'] = len(timeline(p))*1.5
                    st.session_state.revision += 1
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))
            p['width'] = st.selectbox('Resolución vertical', [1080,720], index=0 if p['width']==1080 else 1,
                                     format_func=lambda n:f'{n} × {n*16//9}', key=f'width_{revision}')
            p['crf'] = st.selectbox('Calidad de codificación', [18,16,22], index=[18,16,22].index(p['crf']),
                                   format_func=lambda v:{18:'Alta · original',16:'Muy alta · archivo mayor',22:'Ligera · pruebas'}[v], key=f'quality_{revision}')
            st.caption('30 fps · H.264 · todas las fechas incluidas. La resolución de salida no aumenta el detalle científico del dato.')
    if st.button('Guardar proyecto', icon=':material/save:', key='save_project'):
        save_project()
        st.success('Ajustes guardados. Puedes abrirlos desde la barra lateral.')

with right:
    st.subheader('Tu video', icon=':material/visibility:')
    error_message = None
    try:
        rows = validate(p)
    except (ValueError, TypeError, KeyError) as error:
        rows = []
        error_message = str(error)
        st.warning(error_message)
    if rows:
        st.caption(f'{len(rows)} fechas · {p["duration"]:g} s · {p["width"]} × {p["width"]*16//9}')
        index = st.slider('Fecha de la vista previa', 1, len(rows), 1, key=f'preview_index_{revision}') - 1 if len(rows)>1 else 0
        st.caption(rows[index]['date'])
        if st.button('Actualizar vista previa', type='primary', icon=':material/preview:', key='preview_button'):
            try:
                with st.spinner('Dibujando con tus datos…'):
                    png = preview_bytes(snapshot(), index)
                st.session_state.preview = {'png':png, 'signature':snapshot(), 'index':index}
            except Exception as error:
                st.error(f'No se pudo dibujar: {error}')
        last = st.session_state.preview
        if last:
            if last['signature'] != snapshot() or last['index'] != index:
                st.caption('Hay cambios pendientes de mostrar. Actualiza la vista previa.')
            guides = st.toggle('Ver márgenes de seguridad (solo vista previa)', key='safe_guides')
            displayed = guided_preview(last['png'], json.loads(last['signature']).get('layout','social')) if guides else last['png']
            st.image(displayed, width=360, alt='Vista del video con márgenes orientativos' if guides else 'Previsualización del mapa con el diseño y fecha seleccionados')
            if guides:
                st.caption('Rojo: zonas expuestas a botones/descripciones. Verde: área de contenido. La guía no aparece en el PNG descargado ni en el MP4. La interfaz real depende de la app y de tu descripción.')
            st.download_button('Guardar imagen PNG', last['png'], file_name='vista-previa.png', mime='image/png', icon=':material/image:')
        else:
            reference = ROOT/'_local'/'climate-studio'/'2024-01-01-366days'/'frame-2024-12-31.png'
            if reference.exists():
                st.image(str(reference), width=360, alt='Referencia del video original de lluvia de 2024')
                st.caption('Referencia original. Pulsa Actualizar para ver tu configuración.')
        active = [state for _,state in statuses() if state.get('state') in ('queued','running')]
        preview_ready = last is not None and last['signature']==snapshot()
        if not preview_ready:
            st.caption('Actualiza la vista previa con tus ajustes antes de exportar.')
        if st.button('Generar video', type='primary', icon=':material/movie:', disabled=bool(active) or not preview_ready, key='render_button'):
            try:
                folder = start_job(copy.deepcopy(p))
                st.session_state.active_job = str(folder)
                st.success('Exportación iniciada. Abre Exportaciones en la barra lateral para ver el progreso.')
            except Exception as error:
                st.error(f'No se pudo iniciar: {error}')
        if active:
            st.caption('Hay una exportación activa. Puedes seguir diseñando; revisa su progreso en Exportaciones.')
        st.download_button('Descargar proyecto JSON', snapshot(), file_name='ecuador-vivo-proyecto.json', mime='application/json')
