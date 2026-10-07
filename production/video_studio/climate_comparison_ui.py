"""Climate comparison workbench embedded in the Ecuador Vivo video editor."""

from __future__ import annotations

import calendar
import datetime as dt
import hashlib
import io
import json
import uuid
import urllib.request
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from climate_comparison import (
    CHIRPS_PARAMETER,
    POWER_VARIABLES,
    annual_rank,
    cached_chirps_download,
    cached_power_download,
    display_units,
    ee_climate_script,
    parse_cpc_index,
    province_boundaries,
    summarize_chirps_month,
    summarize_raster_months,
    year_range,
)
from comparison_video import create_comparison_job, render_preview, render_comparison_endcard
from comparison_maps import map_steps
from model import PALETTES, STORE
from jobs import write_json


ROOT = Path(__file__).resolve().parents[2]
RONI_URL = "https://www.cpc.ncep.noaa.gov/data/indices/RONI.ascii.txt"
ONI_URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
NOAA_RONI_INFO = "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/"
NOAA_OISST_INFO = "https://developers.google.com/earth-engine/datasets/catalog/NOAA_CDR_OISST_V2_1"
ERA5_INFO = "https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_HOURLY"
CHIRPS_CATALOG_LAST_DAY = dt.date(2026, 8, 31)


def _source_label_for_ui(output):
    if str(output.get("source", "")).startswith("CHIRPS"):
        return "CHIRPS v3 · UCSB / Climate Hazards Center · ~5,6 km"
    if "POWER" in str(output.get("source", "")):
        return "NASA POWER · NASA / MERRA-2 · ~50–60 km"
    return str(output.get("source", "Fuente indicada en el manifiesto"))


def _png_bytes(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


@st.cache_data(ttl=6 * 60 * 60, show_spinner=False)
def load_enso_indices():
    """Read official NOAA text tables and retain their retrieval fingerprint."""
    result = {}
    for label, url, column in (("RONI", RONI_URL, "ANOM"), ("ONI", ONI_URL, "ANOM")):
        request = urllib.request.Request(url, headers={"User-Agent": "EcuadorVivo/1.0"})
        with urllib.request.urlopen(request, timeout=25) as response:
            raw = response.read()
        table = parse_cpc_index(raw.decode("utf-8-sig", "replace"), column)
        result[label] = {
            "frame": table,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "url": url,
            "bytes": raw,
            "retrieved": dt.datetime.now(dt.timezone.utc).isoformat(),
        }
    return result


def line_chart(frame, *, x, y, color, title, y_title, tooltip=None):
    month_order = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    chart = alt.Chart(frame).mark_line(point=True, strokeWidth=2).encode(
        x=alt.X(x, title="Mes", sort=month_order),
        y=alt.Y(y, title=y_title, scale=alt.Scale(zero=False)),
        color=alt.Color(color, title="Año"),
        tooltip=tooltip or ["year:N", "month_label:N", alt.Tooltip("value:Q", format=".2f")],
    ).properties(title=title, height=340)
    return chart


def show_comparison(project=None, *, phase='Datos'):
    project = project if project is not None else st.session_state.project
    revision = st.session_state.get('revision', 0)
    saved_output = st.session_state.get('climate_comparison') or project.get('comparison_data', {})
    info = POWER_VARIABLES
    valid_key = f'comparison_valid_{revision}'
    if phase == 'Datos':
        st.session_state[valid_key] = False
        st.subheader("Compara el mismo periodo en distintos años")
        st.write(
            "Elige una variable, años y escala territorial. Los promedios de provincia se calculan "
            "sobre celdas nativas que intersectan su polígono; no se toma el valor de la capital."
        )

        # Source/mode alter the following widgets and must trigger an immediate rerun.
        with st.container(border=True):
            source = st.selectbox(
                "Fuente climática",
                [
                    "NASA POWER · temperatura, lluvia, viento y humedad (~50–60 km)",
                    "CHIRPS v3 · lluvia diaria detallada (~5,6 km; un mes por consulta)",
                ], index=1 if str(saved_output.get('source', '')).startswith('CHIRPS') else 0,
                key=f'comparison_source_{revision}',
            )
            use_chirps = source.startswith("CHIRPS")
            if use_chirps:
                st.caption("El catálogo CHIRPS v3 diario consultado el 7 oct 2026 llegaba hasta 31 ago 2026; comprueba cobertura antes de solicitar fechas más recientes.")
            info = POWER_VARIABLES
            variable_labels = (
                {"Precipitación diaria acumulada · CHIRPS v3": CHIRPS_PARAMETER}
                if use_chirps else {item["label"]: code for code, item in info.items()}
            )
            left, middle, right = st.columns(3)
            with left:
                saved_parameter = saved_output.get('parameter')
                variable_options = list(variable_labels)
                selected_label = next((name for name, code in variable_labels.items() if code == saved_parameter), variable_options[0])
                label = st.selectbox("Variable", variable_options, index=variable_options.index(selected_label), key=f'comparison_parameter_{revision}_{use_chirps}')
                parameter = variable_labels[label]
            with middle:
                years = st.multiselect(
                    "Años a comparar · máximo 3",
                    options=list(range(1981, dt.date.today().year + 1)),
                    default=saved_output.get('years', [2016, 2024, 2026]),
                    max_selections=3,
                    key=f'comparison_years_{revision}',
                )
            with right:
                mode_label = st.selectbox(
                    "¿Qué comparamos?",
                    ["Promedio nacional", "Una provincia", "Una ciudad", "Ranking de provincias"],
                    index={'nacional': 0, 'provincia': 1, 'ciudad': 2, 'ranking': 3}.get(saved_output.get('mode'), 0),
                    key=f'comparison_mode_{revision}',
                )
            month_left, month_right, area_col = st.columns(3)
            with month_left:
                first_month = st.selectbox("Desde el mes", range(1, 13), index=saved_output.get('first_month', 1) - 1,
                                           key=f'comparison_first_month_{revision}',
                                           format_func=lambda month: f"{month:02d} · {MONTHS[month - 1]}")
            with month_right:
                last_month = st.selectbox("Hasta el mes", range(1, 13), index=saved_output.get('last_month', 9) - 1,
                                          key=f'comparison_last_month_{revision}',
                                          format_func=lambda month: f"{month:02d} · {MONTHS[month - 1]}")
            province_names = sorted(
                feature.get("properties", {}).get("shapeName", "")
                for feature in province_boundaries()
            )
            city_names = [
                "Quito", "Guayaquil", "Cuenca", "Tena", "Puyo", "Puerto Fco. de Orellana",
                "Esmeraldas", "Loja", "Macas", "Pto. Baquerizo Moreno",
            ]
            area = "Ecuador"
            if mode_label == "Una provincia":
                with area_col:
                    selected_area = saved_output.get('area', 'Napo')
                    area = st.selectbox("Provincia", province_names, index=province_names.index(selected_area) if selected_area in province_names else 0, key=f'comparison_province_{revision}')
            elif mode_label == "Una ciudad":
                with area_col:
                    selected_area = saved_output.get('area', 'Tena')
                    area = st.selectbox("Ciudad", city_names, index=city_names.index(selected_area) if selected_area in city_names else city_names.index('Tena'), key=f'comparison_city_{revision}')
            else:
                with area_col:
                    st.caption("Las 24 provincias se ordenan solo en modo ranking.")
            submitted = st.button("Descargar y calcular comparación", type="primary", key='calculate_comparison')

        if first_month > last_month:
            st.warning("El mes inicial debe ser anterior o igual al mes final.")
            return
        if source.startswith("CHIRPS") and first_month != last_month:
            st.info("CHIRPS ofrece más detalle espacial. Para limitar descargas, este prototipo compara un mes por consulta; usa NASA POWER para periodos de varios meses.")
            return
        if source.startswith("CHIRPS"):
            unavailable = [
                year for year in years
                if dt.date(year, first_month, calendar.monthrange(year, first_month)[1]) > CHIRPS_CATALOG_LAST_DAY
            ]
            if unavailable:
                st.warning(
                    "La última fecha CHIRPS v3 verificada en el catálogo es 31 ago 2026. "
                    f"Quita o cambia el periodo de {', '.join(map(str, unavailable))}; "
                    "no se solicitarán días todavía no publicados."
                )
                return
        requested_mode = {
            "Promedio nacional": "nacional",
            "Una provincia": "provincia",
            "Una ciudad": "ciudad",
            "Ranking de provincias": "ranking",
        }[mode_label]
        if submitted:
            if not years:
                st.error("Selecciona al menos un año.")
                return
            if len(years) > 3:
                st.error("Para cuidar el servicio de datos, compara hasta tres años por consulta.")
                return
            years = sorted(set(years))
            monthly_frames, receipts = [], []
            status = st.status(
                "Consultando CHIRPS v3 y calculando estadísticas…" if use_chirps
                else "Consultando NASA POWER y calculando estadísticas…",
                expanded=True,
            )
            progress = st.progress(0.0)
            try:
                for year_index, year in enumerate(years):
                    start, end = year_range(year, first_month, last_month)
                    status.write(f"{year}: {start:%d %b %Y} – {end:%d %b %Y}")
                    if use_chirps:
                        chirps_start = dt.date(year, first_month, 1)
                        chirps_end = dt.date(year, first_month, calendar.monthrange(year, first_month)[1])

                        def report_day(current, total, day):
                            progress.progress(
                                min(1.0, (year_index + current / total) / len(years)),
                                text=f"{year} · CHIRPS {current}/{total} ({day})",
                            )

                        download = cached_chirps_download(
                            chirps_start, chirps_end, "final_era5", progress=report_day
                        )
                        frame = summarize_chirps_month(
                            download, year, first_month, mode=requested_mode, area=area,
                        )
                    else:
                        download = cached_power_download(start, end, parameter)
                        frame = summarize_raster_months(
                            download["tiff_path"], parameter, year, first_month, last_month,
                            mode=requested_mode, area=area,
                        )
                    if not frame.empty:
                        monthly_frames.append(frame)
                    receipts.append(download)
                    progress.progress((year_index + 1) / len(years))
                    gaps = len(download.get("missing_dates", []))
                    status.write(f"{year}: {download['count']} fechas devueltas; {gaps} fecha(s) sin respuesta.")
                st.session_state["climate_comparison"] = {
                    "frames": monthly_frames,
                    "receipts": receipts,
                    "years": years,
                    "parameter": parameter,
                    "source": source,
                    "mode": requested_mode,
                    "area": area,
                    "first_month": first_month,
                    "last_month": last_month,
                }
                status.update(label="Comparación lista", state="complete", expanded=False)
            except Exception as error:  # user-facing recovery for remote/API faults
                status.update(label="No se pudo completar la comparación", state="error", expanded=True)
                st.error(str(error))
                st.info("Las descargas previas quedan en _local/video-studio/downloads; no se publican en GitHub.")

    else:
        if not saved_output:
            st.info('Primero descarga y calcula una comparación en Datos.')
            return
        source = saved_output.get('source', '')
        parameter = saved_output['parameter']
        years = saved_output['years']
        requested_mode = saved_output['mode']
        area = saved_output['area']
        first_month, last_month = saved_output['first_month'], saved_output['last_month']

    output = st.session_state.get("climate_comparison") or saved_output
    if not output:
        st.info("Empieza con NASA POWER para comparar temperatura, lluvia, viento y humedad (~50–60 km); elige CHIRPS v3 para lluvia más detallada (~5,6 km) en una ventana de un mes.")
        return
    current_result = (
        output["parameter"] == parameter
        and output.get("source") == source
        and output["mode"] == requested_mode
        and output["area"] == area
        and sorted(output.get("years", [])) == sorted(years)
        and output.get("first_month") == first_month
        and output.get("last_month") == last_month
    )
    if phase == 'Datos':
        st.session_state[valid_key] = current_result
    if not current_result or st.session_state.get(valid_key) is False:
        st.warning(
            "Se conserva la consulta anterior, pero el diseño y la exportación "
            "se bloquean hasta calcular los controles actuales."
        )
        return
    frames = [part if isinstance(part, pd.DataFrame) else pd.DataFrame(part) for part in output['frames']]
    output = {**output, 'frames': frames}
    combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if combined.empty:
        st.warning("No hubo suficientes datos para construir el mapa. Revisa fecha, cobertura y provincia.")
        return

    variable_label = (
        "Precipitación acumulada CHIRPS v3"
        if output["parameter"] == CHIRPS_PARAMETER
        else info[output["parameter"]]["label"]
    )
    ranked = annual_rank(output['frames'], output['parameter'],
        years_included=output['years'],
        months_expected=range(output['first_month'], output['last_month'] + 1)) if output['mode'] == 'ranking' else None
    if phase == 'Datos':
        with st.expander('Revisar cálculos, tablas y archivos fuente', expanded=False):
            if output["mode"] == "ranking":
                for year, data in ranked.groupby("year"):
                    st.markdown(f"**{year} · {MONTHS[output['first_month'] - 1]}–{MONTHS[output['last_month'] - 1]}**")
                    complete_data = data.dropna(subset=["value"])
                    if complete_data.empty:
                        st.warning(f"{year}: no hay cobertura completa para comparar todo el periodo; revisa faltantes o reduce la ventana.")
                        st.dataframe(data, hide_index=True)
                        continue
                    if len(complete_data) < len(data):
                        st.warning("Se excluyeron provincias con meses incompletos para no sumar periodos desiguales.")
                    ranking_chart = alt.Chart(complete_data).mark_bar().encode(
                        x=alt.X(
                            "value:Q",
                            title=display_units(
                                output["parameter"],
                                period_total=(output["parameter"] in ("PRECTOTCORR", CHIRPS_PARAMETER)),
                            ),
                        ),
                        y=alt.Y("area:N", sort="-x", title="Provincia"),
                        color=alt.Color("value:Q", legend=None, scale=alt.Scale(scheme="turbo")),
                        tooltip=["area:N", "value:Q", "units:N", "statistic:N"],
                    ).properties(height=560, title=f"Ranking espacial de las provincias · {year}")
                    st.altair_chart(
                        ranking_chart,
                        width="stretch",
                        alt=f"Ranking de las provincias por {variable_label} en {year}.",
                    )
                    st.dataframe(data, hide_index=True)
                export = ranked.to_csv(index=False).encode("utf-8-sig")
            else:
                valid = combined.dropna(subset=["value"])
                if valid.empty:
                    st.warning("Los meses incompletos se dejaron en blanco para no subestimar acumulados ni comparar ventanas distintas.")
                    st.dataframe(combined, hide_index=True)
                    return
                chart = line_chart(
                    valid,
                    x="month_label:N",
                    y="value:Q",
                    color="year:N",
                    title=f"{variable_label} · {output['area']}",
                    y_title=display_units(output["parameter"]),
                )
                st.altair_chart(
                    chart,
                    width="stretch",
                    alt=f"Comparación mensual de {variable_label} para {output['area']} entre los años {', '.join(map(str, output['years']))}.",
                )
                if output["mode"] == "ciudad":
                    sample = valid.iloc[0]
                    cell_scale = "~5,6 km" if output["parameter"] == CHIRPS_PARAMETER else "~50–60 km"
                    st.caption(
                        f"Ciudad aproximada al punto de grilla más cercano ({sample.cell_lat:.3f}° lat, "
                        f"{sample.cell_lon:.3f}° lon). La celda es de {cell_scale}: no representa "
                        "el microclima urbano ni una estación puntual."
                    )
                export = combined.to_csv(index=False).encode("utf-8-sig")
                st.dataframe(combined, hide_index=True)
            st.download_button("Descargar tabla de comparación · CSV", export,
                               file_name="ecuador-vivo-comparacion-climatica.csv", mime="text/csv")
            st.markdown("**Descargas fuente completas**")
            st.caption("Cada ZIP conserva CSV original por mosaico, GeoTIFF unido y metadatos con fecha, escala, huecos y huellas SHA-256.")
            for receipt in output["receipts"]:
                try:
                    payload = Path(receipt["zip_path"]).read_bytes()
                    st.download_button(
                        f"Bajar {receipt['start'][:4]} · datos fuente {receipt.get('provider', 'climáticos')} (ZIP)",
                        payload,
                        file_name=Path(receipt["zip_path"]).name,
                        mime="application/zip",
                        key=f"climate-{receipt.get('parameter', receipt.get('product', 'data'))}-{receipt['start']}-{receipt['end']}",
                    )
                except (OSError, KeyError):
                    st.warning(f"No se encontró el ZIP fuente de {receipt.get('start', '')[:4]}.")

            st.info(
                "Método: precipitación = acumulado diario en cada celda y luego promedio espacial por área; "
                "temperatura, viento y humedad = media diaria/temporal y luego promedio espacial. "
                "La estimación de área usa ponderación cos(latitud); no se rellenan fechas ausentes. "
                "NASA POWER/MERRA-2 describe patrones regionales, no observaciones de estación. "
                "CHIRPS v3 tiene ~5,6 km de resolución y aquí se limita a un mes por consulta; sus valores diarios se derivan de estimaciones pentadales."
            )

        st.info('Cálculos listos. Continúa en Maqueta para componer el video.')
        return

    st.divider()
    st.subheader("Maqueta audiovisual · Ecuador Vivo / Andes Pulso")
    st.caption(
        "El video muestra mapas de los rásteres originales, mes a mes y con escala fija. "
        "Las tablas y los rankings quedan para el cierre de métricas. "
        "Con tres años, el primer año se compara con cada uno de los siguientes."
    )
    # The maps show MONTHLY fields, even when the closing ranking covers a
    # longer period. Do not label a monthly map with the period-total units.
    video_units = display_units(output['parameter'])
    first_year = min(output["years"])
    default_title = (
        f"¿Dónde fue mayor la {variable_label.lower()}?"
        if output["mode"] == "ranking"
        else f"¿Cómo cambió la {variable_label.lower()}?"
    )
    designs = project.setdefault('comparison_designs', {})
    design_id = output['parameter'] + '/' + output['mode']
    previous_design = project.get('comparison_design', {})
    design = designs.get(design_id, previous_design if previous_design.get('parameter') == output['parameter'] and previous_design.get('mode') == output['mode'] else {})
    prefix = f'comparison_design_{revision}_{output["parameter"]}_{output["mode"]}'
    title = design.get('title', default_title)
    subtitle = design.get('subtitle', f"Misma escala. {len(output['years'])} años. {output['area']}.")
    citation = design.get('citation', _source_label_for_ui(output))
    author, credits, brand = project['author'], project['credits'], project['brand']
    tiktok, instagram = project.get('tiktok', ''), project.get('instagram', '')
    palette = design.get('palette', 'Termal editorial' if output['parameter'] == 'T2M' else list(PALETTES)[0])
    editorial_margins = design.get('editorial_margins', 'referencia')
    gradient_1 = design.get('title_gradient_1', '#26ede0') if design.get('editorial_revision') == 2 else '#26ede0'
    gradient_2 = design.get('title_gradient_2', '#229ffa') if design.get('editorial_revision') == 2 else '#229ffa'
    background, accent = design.get('background', project['background']), design.get('accent', project['accent'])
    duration = float(design.get('duration', 20))
    map_layout = design.get('map_layout', 'Dos mapas')
    map_smooth = design.get('map_smooth', True)
    manual_scale = design.get('manual_scale', False)
    scale_min, scale_max = design.get('scale_min', 0.), design.get('scale_max', 40.)
    scale_min = 0. if scale_min is None else float(scale_min)
    scale_max = 40. if scale_max is None else float(scale_max)
    closing, auto_closing = design.get('endcard_enabled', True), design.get('endcard_auto_text', True)
    endcard_title, endcard_subtitle = design.get('endcard_title', 'MÉTRICAS FINALES'), design.get('endcard_subtitle', '')
    endcard_duration = float(design.get('endcard_duration', 6))
    manual_copy = dict(design.get('endcard_copy', {}))
    manual_findings = [dict(item) for item in design.get('endcard_findings', [])]
    while len(manual_findings) < 3:
        manual_findings.append({'title': '', 'body': ''})
    if phase == 'Maqueta':
        with st.expander('Configuración de la plantilla y créditos'):
            control = st.segmented_control('Controles', ['Diseño', 'Textos y créditos', 'Cierre final'],
                                           default='Diseño', key=prefix + '_controls')
            with st.container(border=True):
                if control == 'Diseño':
                    margin_choice = st.selectbox('Ocupación del lienzo', ['Referencia · grande', 'Márgenes ampliados'],
                        index=1 if editorial_margins == 'amplios' else 0, key=prefix + '_margins')
                    editorial_margins = 'amplios' if margin_choice == 'Márgenes ampliados' else 'referencia'
                    st.caption('El estilo grande reproduce las proporciones de la referencia. Los márgenes ampliados reducen el diseño para interfaces que superponen muchos controles.')
                    map_layout = st.selectbox('Composición del mapa', ['Dos mapas', 'Un mapa · años secuenciales'],
                        index=0 if map_layout == 'Dos mapas' else 1, key=prefix + '_map_layout')
                    map_smooth = st.toggle('Suavizado visual de la grilla', value=map_smooth, key=prefix + '_map_smooth',
                        help='Solo presentación. No aumenta resolución ni cambia los cálculos sobre la grilla nativa.')
                    manual_scale = st.toggle('Fijar escala de colores manualmente', value=manual_scale, key=prefix + '_manual_scale')
                    if manual_scale:
                        limits_cols = st.columns(2)
                        scale_min = limits_cols[0].number_input('Mínimo', value=scale_min, key=prefix + '_scale_min')
                        scale_max = limits_cols[1].number_input('Máximo', value=scale_max, key=prefix + '_scale_max')
                    st.caption('Una sola escala para todos los mapas. Galápagos se presenta reubicado; sin color significa sin cobertura válida.')
                    title = st.text_input('Título del video', title, max_chars=72, key=prefix + '_title')
                    subtitle = st.text_input('Frase de entrada', subtitle, max_chars=96, key=prefix + '_subtitle')
                    palette_names = list(PALETTES)
                    palette = st.selectbox('Paleta', palette_names, index=palette_names.index(palette) if palette in PALETTES else 0, key=prefix + '_palette')
                    colors = st.columns(2)
                    background = colors[0].color_picker('Fondo', background, key=prefix + '_background')
                    accent = colors[1].color_picker('Acento', accent, key=prefix + '_accent')
                    title_colors = st.columns(2)
                    gradient_1 = title_colors[0].color_picker('Título · color inicial', gradient_1, key=prefix + '_gradient_1')
                    gradient_2 = title_colors[1].color_picker('Título · color final', gradient_2, key=prefix + '_gradient_2')
                elif control == 'Textos y créditos':
                    citation = st.text_input('Crédito visible de la fuente', citation, max_chars=100, key=prefix + '_citation')
                    author = st.text_input('Autoría', author, max_chars=72, key=prefix + '_author')
                    credits = st.text_input('Profesión / créditos', credits, key=prefix + '_credits')
                    brand = st.text_input('Marca', brand, key=prefix + '_brand')
                    tiktok = st.text_input('TikTok', tiktok, key=prefix + '_tiktok')
                    instagram = st.text_input('Instagram', instagram, key=prefix + '_instagram')
                elif control == 'Cierre final':
                    closing = st.toggle('Añadir tarjeta final calculada', value=closing, key=prefix + '_closing')
                    auto_closing = st.toggle('Títulos del cierre automáticos según la variable', value=auto_closing, key=prefix + '_auto_closing')
                    endcard_title = st.text_input('Título del cierre', endcard_title, key=prefix + '_endcard_title')
                    endcard_subtitle = st.text_input('Subtítulo del cierre (manual)', endcard_subtitle, disabled=auto_closing, key=prefix + '_endcard_subtitle')
                    if not auto_closing:
                        with st.expander('Otros textos del cierre · vacíos = automáticos'):
                            for field, caption in [('section_1', 'Sección 01'), ('section_1_note', 'Nota 01'),
                                                   ('section_2', 'Sección 02'), ('section_2_note', 'Nota 02'),
                                                   ('section_3', 'Sección 03'), ('section_3_note', 'Nota 03'),
                                                   ('rank_axis_label', 'Etiqueta del eje'), ('footer', 'Fuente del cierre'),
                                                   ('footer_2', 'Detalle del territorio')]:
                                manual_copy[field] = st.text_input(caption, manual_copy.get(field, ''), key=prefix + '_copy_' + field)
                        if output['mode'] != 'ranking':
                            with st.expander('Editar los tres hallazgos · vacíos = calculados'):
                                st.caption('Las cifras y las barras se calculan siempre. Si cambias la explicación, comprueba que siga siendo fiel a los datos.')
                                for i, item in enumerate(manual_findings):
                                    item['title'] = st.text_input(f'Hallazgo {i+1} · título', item.get('title', ''), max_chars=70, key=prefix + f'_finding_{i}_title')
                                    item['body'] = st.text_area(f'Hallazgo {i+1} · explicación', item.get('body', ''), max_chars=180, key=prefix + f'_finding_{i}_body')
    config = {
        'parameter': output['parameter'], 'mode': output['mode'],
        'map_layout': map_layout, 'map_smooth': map_smooth, 'manual_scale': manual_scale,
        'scale_min': scale_min if manual_scale else None,
        'scale_max': scale_max if manual_scale else None,
        "name": f"Comparación · {variable_label} · {first_year}–{max(output['years'])}",
        "title": title,
        "subtitle": subtitle,
        "citation": citation,
        "author": author,
        "credits": credits, "brand": brand, "tiktok": tiktok, "instagram": instagram,
        "palette": palette,
        "palette_colors": PALETTES[palette],
        "background": background,
        "accent": accent,
        "text": project['text'],
        "title_gradient_1": gradient_1,
        "title_gradient_2": gradient_2,
        "editorial_margins": editorial_margins, "editorial_revision": 2,
        "visual_layout": design.get('visual_layout', {}),
        "delivery": project.get('delivery', {}),
        "storyboard": project.get('storyboard', {}),
        "endcard_enabled": closing, "endcard_auto_text": auto_closing,
        "endcard_title": endcard_title, "endcard_subtitle": endcard_subtitle,
        "endcard_copy": manual_copy,
        "endcard_findings": manual_findings,
        "endcard_duration": endcard_duration,
        "duration": duration,
        "variable": variable_label,
        "units": video_units,
        "method": "Mapas mensuales · escala fija · Galápagos reubicado · sin color: sin dato. Suavizar no añade resolución.",
    }
    project['comparison_design'] = config
    designs[design_id] = config
    project.update(author=author, credits=credits, brand=brand, tiktok=tiktok, instagram=instagram)
    project['comparison_data'] = {**output, 'frames': [json.loads(part.to_json(orient='records')) for part in output['frames']]}
    st.session_state.project = project
    from workspace import authoring_config, export_check
    from storyboard import base_timing
    config = authoring_config(config)
    project['comparison_design'] = config
    designs[design_id] = config
    steps = map_steps(output, config)
    if phase == 'Montaje':
        if not project.get('storyboard', {}).get('enabled'):
            config['duration'] = st.number_input('Duración del mapa · segundos',
                min_value=max(1/30, len(steps)/30), max_value=3600., value=float(duration), key=prefix+'_duration')
            if closing:
                config['endcard_duration'] = st.number_input('Duración de métricas · segundos',
                    min_value=1/30, max_value=300., value=float(endcard_duration), key=prefix+'_endcard_duration')
        project['comparison_design'] = config
        designs[design_id] = config
        return
    if phase == 'Maqueta':
        from layout_editor import show_layout_editor
        with st.expander('Fecha de trabajo del lienzo'):
            index = st.select_slider('Momento del mapa en el lienzo', options=list(range(len(steps))),
                value=len(steps)-1, format_func=lambda i: ' / '.join(f'{MONTHS[m-1]} {y}' for y,m in steps[i]),
                key=prefix+'_preview_step', persist_state='session') if len(steps) > 1 else 0
        progress = (index+.5)/len(steps)
        def persist_visual_layout(layout):
            config['visual_layout'] = layout
            project['comparison_design'] = config
            designs[design_id] = config
        try:
            show_layout_editor(config,
                lambda settings: render_preview(combined, output, settings, rank_frame=ranked, progress=progress),
                (lambda settings: render_comparison_endcard(combined, output, settings, rank_frame=ranked)[0]) if closing else None,
                project=project, persist=persist_visual_layout, key=prefix+'_visual')
        except (ValueError, KeyError, TypeError, OSError) as error:
            st.error(f'No se pudo abrir la maqueta: {error}')
        return

    timed = base_timing(config)
    ready = export_check(timed,
        lambda settings: render_preview(combined, output, settings, rank_frame=ranked),
        (lambda settings: render_comparison_endcard(combined, output, settings, rank_frame=ranked)[0]) if timed.get('endcard_enabled') else None)
    if st.button('Generar video comparativo · MP4', type='primary', icon=':material/movie:',
        key='generate_comparison_video', disabled=not ready):
        progress_widget = st.progress(0., text='Preparando video comparativo…')
        try:
            job = create_comparison_job(combined, output, config, rank_frame=ranked,
                progress_callback=lambda value: progress_widget.progress(value, text=f'Codificando MP4 · {value:.0%}'))
            st.success(f'Video listo en Exportaciones: {job.name}. CSV y recibo de fuentes conservados junto al MP4.')
        except Exception as error:
            st.error(f'No se pudo generar el video: {error}')
    saved_project = {**project, 'name': config['name']}
    with st.container(horizontal=True):
        if st.button('Guardar proyecto', key='save_comparison_project', icon=':material/save:'):
            target = STORE/'projects'/(dt.datetime.now().strftime('%Y%m%d-%H%M%S')+'-comparacion-'+uuid.uuid4().hex[:6]+'.json')
            write_json(target, saved_project)
            st.success('Proyecto guardado; puedes reabrir sus cálculos sin descargar de nuevo.')
        st.download_button('Exportar proyecto JSON', json.dumps(saved_project, ensure_ascii=False, indent=2).encode('utf-8'),
            file_name='ecuador-vivo-comparacion.json', mime='application/json', key='export_comparison_project')


MONTHS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
          "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


def show_enso():
    st.subheader("El Niño: mirar el océano y preguntar qué cambió en tierra")
    st.write(
        "El Niño no se resume con un termómetro ni con una sola lluvia extrema. "
        "Aquí se comparan índices oficiales del Pacífico con series ecuatorianas, "
        "sin convertir coincidencia temporal en causalidad."
    )
    try:
        indices = load_enso_indices()
        roni = indices["RONI"]["frame"].assign(index="RONI · actual")
        oni = indices["ONI"]["frame"].assign(index="ONI · serie histórica")
        combined = pd.concat([roni, oni], ignore_index=True)
        combined["year"] = combined["date"].dt.year
        chart = alt.Chart(combined).mark_line().encode(
            x=alt.X("date:T", title="Temporada de tres meses"),
            y=alt.Y("value:Q", title="Anomalía de TSM (°C)", scale=alt.Scale(zero=False)),
            color=alt.Color("index:N", title="Índice"),
            tooltip=["index:N", "date:T", "season:N", alt.Tooltip("value:Q", format=".2f")],
        ).properties(height=360, title="RONI y ONI · definiciones diferentes, misma unidad")
        st.altair_chart(chart, width="stretch", alt="Serie de RONI y ONI de NOAA, anomalías de temperatura superficial del mar en temporadas móviles de tres meses.")
        latest = indices["RONI"]["frame"].iloc[-1]
        st.metric("Último RONI publicado", f"{latest.value:+.2f} °C", latest.date.strftime("%b %Y"))
        st.caption(
            f"Tablas consultadas: {indices['RONI']['retrieved'][:10]} · "
            "RONI oficial, base 1991–2020 y promedio móvil de tres meses. El valor reciente puede revisarse."
        )
        csv = combined.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Descargar RONI + ONI consultados · CSV", csv,
                           file_name="noaa-roni-oni-ecuador-vivo.csv", mime="text/csv")
    except Exception as error:
        st.warning(f"No se pudo actualizar NOAA en línea: {error}")
        st.markdown(f"[Abrir la tabla oficial RONI de NOAA]({NOAA_RONI_INFO})")

    st.markdown("#### Cómo se conectan las escalas")
    st.markdown(
        "- **Mar:** temperatura superficial del mar (TSM) y su anomalía en el Pacífico oriental.\n"
        "- **Atmósfera:** viento en componentes hacia el este y hacia el norte; su combinación da dirección y rapidez.\n"
        "- **Ecuador:** lluvia, temperatura y estaciones locales; la respuesta cambia entre Costa, Andes, Amazonía e islas.\n"
        "- **Comprobación:** comparar estación, producto satelital/reanálisis y boletín ERFEN; no son mediciones equivalentes."
    )
    st.markdown(
        "**Fuentes ecuatorianas:** [boletines ERFEN/INOCAR](https://www.inocar.mil.ec/web/index.php/boletines/erfen/boletines-de-prensa) · "
        "[Índice ecuatoriano IEFEN](https://www.inocar.mil.ec/web/index.php/publicaciones/documentos-legales-erfen/638-indice-ecuatoriano-del-fenomeno-el-nino-iefen) · "
        "[datos diarios INAMHI](https://inamhi.gob.ec/ddia/visor)."
    )


def show_ocean_wind():
    st.subheader("Una sola escena: mar, viento y continente")
    st.write(
        "La maqueta usa Earth Engine, que ya está en tu cuenta: genera el mapa en ese entorno y permite "
        "exportarlo directamente a Drive sin guardar aquí un archivo global pesado."
    )
    date = st.date_input("Día de la escena", value=dt.date(2024, 2, 1), min_value=dt.date(1981, 9, 1), max_value=dt.date.today())
    controls = st.columns(5)
    show_sst = controls[0].checkbox("Temperatura del mar · NOAA OISST", value=True)
    show_anomaly = controls[1].checkbox("Anomalía de TSM", value=True)
    show_air_temp = controls[2].checkbox("Temperatura continental · ERA5", value=True)
    show_wind = controls[3].checkbox("Vectores de viento · ERA5", value=True)
    show_rain = controls[4].checkbox("Lluvia diaria · CHIRPS v3", value=False)
    script = ee_climate_script(
        date.isoformat(), show_sst=show_sst, show_anomaly=show_anomaly,
        show_wind=show_wind, show_air_temp=show_air_temp, show_rain=show_rain,
    )
    st.download_button("Descargar script para Earth Engine · .js", script.encode("utf-8"),
                       file_name=f"ecuador-vivo-oceano-viento-{date:%Y%m%d}.js", mime="text/javascript")
    with st.expander("Vista previa del script que se descargará"):
        st.code(script, language="javascript", wrap_lines=False)
    st.link_button("Abrir Google Earth Engine Code Editor", "https://code.earthengine.google.com/")
    st.caption(
        "Copia el .js en tu Code Editor, pulsa Run y activa las capas. Para exportar a Drive, "
        "quita los comentarios de Export.image.toDrive y ejecuta la tarea desde la pestaña Tasks. "
        "El script no accede ni guarda credenciales. En Earth Engine puedes encender/apagar cada capa desde el control de capas."
    )
    st.markdown(
        f"Datos: [NOAA OISST diaria, 0,25° desde 1981]({NOAA_OISST_INFO}) · "
        f"[ERA5 horario, ~31 km]({ERA5_INFO})."
    )
    st.caption("Corte del catálogo consultado el 7 oct 2026: CHIRPS v3 diario hasta 31 ago; OISST hasta 4 oct; ERA5 horario hasta 1 oct 15:00 UTC. Las coberturas se actualizan con rezago; verifica la fecha antes de exportar.")
    st.warning(
        "OISST combina satélites, barcos y boyas y completa huecos por interpolación. CHIRPS diario reparte totales pentadales usando ERA5; no equivale a una observación diaria uniforme. ERA5 es una reanálisis: "
        "un campo horario modelado con observaciones, no un sensor que mida cada pixel. "
        "La escena une variables con escalas y métodos distintos; se deben identificar por separado."
    )


def render_embedded(project=None, *, phase='Datos'):
    """Render the comparison tools as a native section of the video studio."""
    if phase != 'Datos':
        show_comparison(project, phase=phase)
        return
    st.subheader("Datos de comparación")
    st.caption(
        "Mismo editor, fuentes y carpeta de proyectos. Compara primero los datos; "
        "después prepara una maqueta audiovisual con el resultado verificable."
    )
    view = st.segmented_control(
        "Tipo de historia",
        ["Años y territorios", "El Niño y Pacífico", "Mar y viento", "Fuentes y método"],
        default="Años y territorios",
        key="climate_comparison_view",
    )
    if view == "Años y territorios":
        show_comparison(project, phase=phase)
    elif view == "El Niño y Pacífico":
        show_enso()
    elif view == "Mar y viento":
        show_ocean_wind()
    else:
        st.subheader("Fuentes y límites de interpretación")
        sources = pd.DataFrame([
            {"Fuente": "INAMHI", "Variables": "Estaciones locales · lluvia, temperatura, viento", "Alcance histórico": "Depende de estación/variable; API diaria con huecos y ventana variable", "Acceso": "Conector probado; valores puntuales, nunca rellenar faltantes", "Uso recomendado": "Verificación local y estudios de ciudades/cuencas"},
            {"Fuente": "CHIRPS v3", "Variables": "Precipitación diaria", "Alcance histórico": "Final RNL desde 1981; ~5,6 km", "Acceso": "Descarga integrada en Obtener datos", "Uso recomendado": "Lluvia espacial histórica; no equivale a pluviómetro"},
            {"Fuente": "NASA POWER / MERRA-2", "Variables": "Precipitación, temperatura, viento, humedad", "Alcance histórico": "Desde 1981; ~50–60 km", "Acceso": "Descarga integrada", "Uso recomendado": "Comparaciones nacionales/regionales; no microclima urbano"},
            {"Fuente": "NOAA CPC", "Variables": "RONI / ONI · índices ENSO", "Alcance histórico": "RONI/ONI desde 1950; temporadas móviles de 3 meses", "Acceso": "Tablas ASCII actualizadas en línea", "Uso recomendado": "Contexto oceánico; no usar como prueba única de impactos ecuatorianos"},
            {"Fuente": "NOAA OISST", "Variables": "TSM y anomalía diaria", "Alcance histórico": "Desde 1981; 0,25°", "Acceso": "Earth Engine → exportación a Drive", "Uso recomendado": "Mapas de calentamiento/enfriamiento en el Pacífico"},
            {"Fuente": "ERA5 / Copernicus", "Variables": "Viento u/v, temperatura, precipitación", "Alcance histórico": "1940–presente; ~31 km; horario", "Acceso": "Earth Engine para escenas/Drive; CDS requiere cuenta y términos", "Uso recomendado": "Circulación atmósfera-mar-tierra; reanálisis, no estación"},
            {"Fuente": "INOCAR / ERFEN", "Variables": "IEFEN, boletines, TSM regional y perspectiva", "Alcance histórico": "Boletines y gráficos; serie automática abierta no confirmada", "Acceso": "PDF/web; extraer valores solo cuando se puedan verificar", "Uso recomendado": "Estado y contexto oficial del Ecuador"},
        ])
        st.dataframe(sources, hide_index=True, width="stretch", alt="Fuentes climáticas, cobertura y límites metodológicos")
        st.markdown(
            "**Para una historia de El Niño:** RONI/ONI + TSM NOAA OISST + viento ERA5 + "
            "lluvia CHIRPS y validación INAMHI/ERFEN. Una fase del índice no garantiza "
            "el mismo impacto en cada provincia."
        )
        st.markdown(
            "[Ficha NOAA RONI](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/) · "
            "[INOCAR ERFEN](https://www.inocar.mil.ec/web/index.php/boletines/erfen/boletines-de-prensa) · "
            "[NASA POWER](https://power.larc.nasa.gov/docs/services/api/temporal/daily/) · "
            "[Catálogo OISST](https://developers.google.com/earth-engine/datasets/catalog/NOAA_CDR_OISST_V2_1)"
        )
