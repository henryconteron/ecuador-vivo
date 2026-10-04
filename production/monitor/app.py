import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import HeatMap, Fullscreen
from streamlit_folium import st_folium
from datetime import datetime, timedelta, timezone
import math
import json
import os
from html import escape

from seismology import (
    calcular_valor_b,
    estimar_mc_maxima_curvatura,
    evaluar_consistencia_buzamiento,
    vectorized_haversine,
)

# ------------------------------------------------------------------------------
# 1. IDENTIDAD VISUAL — ANDES PULSO
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Andes Pulso · Observatorio sísmico del Ecuador",
    page_icon="◒",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Manrope:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Manrope', system-ui, sans-serif;
        background: #171811;
        color: #eee5d3;
    }
    .stApp { background: radial-gradient(circle at 92% -10%, #5f4e2d 0, transparent 30%), #171811; }
    [data-testid="stSidebar"] { background: #222319; border-right: 1px solid #4b4a38; }
    [data-testid="stSidebar"] > div:first-child { background: transparent; }
    
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1440px !important;
    }

    .andes-brand { margin: 0.4rem 0 1.4rem; }
    .andes-brand .eyebrow, .hero-eyebrow {
        font-family: 'DM Mono', monospace; font-size: 0.67rem; letter-spacing: 0.18em;
        color: #dcb25a; font-weight: 500;
    }
    .andes-brand .name { font-family: 'Fraunces', serif; color: #f4ead4; font-size: 1.75rem; line-height: 1; letter-spacing: -0.06em; }
    .andes-brand .rule { display: block; width: 42px; height: 3px; background: #c95434; margin-top: 0.55rem; }
    .andes-hero {
        position: relative; overflow: hidden; margin: 0.25rem 0 1.25rem; padding: 2.1rem 2.4rem 2rem;
        background: linear-gradient(120deg, #303227 0%, #25271d 60%, #3e3523 100%);
        border: 1px solid #615d43; border-radius: 18px; box-shadow: 0 18px 45px rgba(0,0,0,.22);
    }
    .andes-hero:after {
        content: ""; position: absolute; inset: auto -6% -70% 28%; height: 250px; opacity: .72;
        background: repeating-radial-gradient(ellipse at 45% 105%, transparent 0 19px, rgba(235,218,172,.13) 20px 21px, transparent 22px 37px);
        transform: rotate(-5deg); pointer-events: none;
    }
    .hero-title { font-family: 'Fraunces', serif; color: #f7efd9; font-size: clamp(2.35rem, 5vw, 4.6rem); line-height: .93; letter-spacing: -0.07em; margin: .5rem 0 .55rem; position: relative; z-index: 1; }
    .hero-subtitle { color: #d8d1bc; font-size: 1rem; max-width: 650px; line-height: 1.6; position: relative; z-index: 1; }
    .hero-chip { display: inline-flex; margin-top: 1.2rem; padding: .34rem .65rem; border: 1px solid rgba(231,181,72,.45); border-radius: 999px; color: #f1cc74; font: .67rem 'DM Mono', monospace; letter-spacing: .08em; position: relative; z-index: 1; }

    /* Tarjetas de lectura */
    div[data-testid="metric-container"] {
        background: #24251b;
        border: 1px solid #4b4d39;
        border-radius: 14px;
        padding: 14px 18px;
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.16);
        transition: transform .2s ease, background .2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-3px); background: #2b2d21;
    }
    div[data-testid="metric-container"] label {
        color: #bdb79e !important; font-size: 0.66rem !important; font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #f0c262 !important;
        font-family: 'Fraunces', serif !important;
        font-weight: 700 !important;
        font-size: 1.85rem !important;
    }

    /* Pulso vivo */
    .telemetry-banner {
        background: #2a2b1f; border: 1px solid #5e6048; border-left: 4px solid #c95434;
        border-radius: 12px; padding: 14px 20px; margin: 10px 0 18px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .pulse-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #e4b454; box-shadow: 0 0 0 0 rgba(228, 180, 84, .7);
        display: inline-block;
        animation: pulse 1.8s infinite;
        margin-right: 8px;
    }
    @keyframes pulse {
        0% { transform: scale(.95); box-shadow: 0 0 0 0 rgba(228, 180, 84, .7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(228, 180, 84, 0); }
        100% { transform: scale(.95); box-shadow: 0 0 0 0 rgba(228, 180, 84, 0); }
    }

    /* Pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px; border-bottom: 1px solid #4e4d3d;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px; border-radius: 8px 8px 0 0; padding: 8px 15px;
        color: #c1bba7; font-weight: 600; font-size: 0.83rem; background: transparent;
        border: 1px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        background: #292a20 !important; color: #f0c262 !important;
        border: 1px solid #4e4d3d !important; border-bottom: 2px solid #c95434 !important;
    }
    .stButton > button, [data-testid="stDownloadButton"] > button { border-radius: 8px; border: 1px solid #c25a3c; background: #c95434; color: #fff8e8; font-weight: 700; }
    .stButton > button:hover, [data-testid="stDownloadButton"] > button:hover { background: #db6745; border-color: #db6745; }
    [data-testid="stCaptionContainer"] { color: #c1bba7; opacity: 1; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. SISTEMA DE LOCALIZACIÓN (I18N DINÁMICO)
# ------------------------------------------------------------------------------
if "lang" not in st.session_state:
    st.session_state.lang = "ES"

I18N = {
    "ES": {
        "title": "ANDES PULSO",
        "subtitle": "Observatorio sísmico vivo del Ecuador · datos abiertos, lectura tectónica y memoria del territorio.",
        "eyebrow": "ECUADOR · ANDES DEL NORTE",
        "live_chip": "LECTURA DEL CATÁLOGO RECIENTE",
        "sidebar_head": "Configura tu lectura",
        "source_label": "Catálogo Sísmico:",
        "region_label": "Zona del mapa:",
        "window_days": "Últimos días:",
        "min_magnitude": "Magnitud Mínima (M):",
        "basemap_label": "Fondo del mapa:",
        "layers_header": "Qué mostrar en el mapa",
        "layer_faults": "Fallas Activas (GEM GAF-DB / SARA)",
        "layer_volcanoes": "Arcos Volcánicos (Smithsonian GVP)",
        "layer_heatmap": "Concentración de registros (no peligro)",
        "kpi_events": "Sismos en tu consulta",
        "kpi_max_mag": "Mayor magnitud",
        "kpi_mean_depth": "Profundidad Media",
        "kpi_b_val": "Valor b (Aki G-R)",
        "kpi_energy": "Energía aproximada",
        "tab_map": "🗺️ Dónde ocurrieron",
        "tab_3d": "🪐 Bajo la superficie",
        "tab_time": "⏱️ Cuándo ocurrieron",
        "tab_gr": "📈 Análisis avanzado",
        "tab_data": "📋 Datos y descarga",
        "heading_3d": "Distribución 3D de Hipocentros",
        "heading_profile": "Perfil Seccional Transversal (Swath Slice)",
        "heading_time": "Los registros a través del tiempo",
        "heading_gr": "Ley Gutenberg-Richter y Umbral de Completitud",
        "heading_strain": "Índice acumulado de Benioff (aproximación)",
        "heading_catalog": "Registro Estructurado de Eventos & Telemetría",
        "caution_note": "Aviso Metodológico: La proximidad espacial entre un epicentro y una traza constituye una pista estructural preliminar; no sustituye la inversión de tensores focales ni modelado de fuentes.",
        "shallow_legend": "Profundidad ≤30 km",
        "inter_legend": "Profundidad >30–70 km",
        "deep_legend": "Profundidad >70 km",
        "assoc_fault": "Falla Mapeada Más Próxima:",
        "distance_fault": "Distancia a la traza:",
        "export_btn": "📥 Exportar Catálogo Filtrado (CSV)",
        "no_data": "No se registraron sismos con los parámetros configurados.",
        "recent_alert": "Sismo más reciente de esta consulta:"
    },
    "EN": {
        "title": "ANDES PULSO",
        "subtitle": "Ecuador's live seismic observatory · open data, tectonic reading, and territorial memory.",
        "eyebrow": "ECUADOR · NORTHERN ANDES",
        "live_chip": "RECENT CATALOG RECORDS",
        "sidebar_head": "Shape your reading",
        "source_label": "Seismic Catalog:",
        "region_label": "Map area:",
        "window_days": "Last days:",
        "min_magnitude": "Minimum Magnitude (M):",
        "basemap_label": "Map background:",
        "layers_header": "What to show on the map",
        "layer_faults": "Active Faults (GEM GAF-DB / SARA)",
        "layer_volcanoes": "Volcanic Arcs (Smithsonian GVP)",
        "layer_heatmap": "Record concentration (not danger)",
        "kpi_events": "Events in your query",
        "kpi_max_mag": "Largest magnitude",
        "kpi_mean_depth": "Mean Depth",
        "kpi_b_val": "b-Value (Aki G-R)",
        "kpi_energy": "Approximate energy",
        "tab_map": "🗺️ Where they occurred",
        "tab_3d": "🪐 Below the surface",
        "tab_time": "⏱️ When they occurred",
        "tab_gr": "📈 Advanced analysis",
        "tab_data": "📋 Data and download",
        "heading_3d": "3D Hypocenter Distribution",
        "heading_profile": "Transverse Section Profile (Swath Slice)",
        "heading_time": "Records through time",
        "heading_gr": "Gutenberg-Richter Law & Completeness Threshold",
        "heading_strain": "Cumulative Benioff index (approximation)",
        "heading_catalog": "Structured Event & Telemetry Registry",
        "caution_note": "Methodological Notice: Spatial proximity between an epicenter and a fault trace is an exploratory hint; it does not replace focal mechanism inversions.",
        "shallow_legend": "Depth ≤30 km",
        "inter_legend": "Depth >30–70 km",
        "deep_legend": "Depth >70 km",
        "assoc_fault": "Closest Mapped Fault:",
        "distance_fault": "Distance to trace:",
        "export_btn": "📥 Export Structured Registry (CSV)",
        "no_data": "No earthquakes cataloged with the configured parameters.",
        "recent_alert": "Most recent earthquake in this query:"
    }
}

t = I18N[st.session_state.lang]

def cambiar_idioma():
    # Run before the full script: an early rerun would clean up the learning widgets.
    st.session_state.lang = st.session_state.app_lang

# ------------------------------------------------------------------------------
# 3. MODELO SISMOTECTÓNICO Y VOLCÁNICO REGIONAL
# ------------------------------------------------------------------------------
# Fuente: GEM Global Active Faults Database (GAF-DB) + proyecto regional SARA,
# filtrado a la ventana Ecuador/Andes Norte. Dataset real (no trazas aproximadas
# a mano): geometría, cinemática y buzamiento reportado provienen del catálogo
# original cuando están disponibles.
# Cita: Styron, R., & Pagani, M. (2020). The GEM Global Active Faults Database.
#       Earthquake Spectra, 36(1_suppl), 160-180. https://doi.org/10.1177/8755293020944182
# Licencia: CC-BY-SA 4.0 · https://github.com/GEMScienceTools/gem-global-active-faults
APP_DIR = os.path.dirname(os.path.abspath(__file__))
FAULTS_DATA_PATH = os.path.join(APP_DIR, "ecuador_active_faults.geojson")
MAX_CATALOG_EVENTS = 1500

@st.cache_data(show_spinner=False)
def cargar_fallas_activas(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            geo = json.load(f)
        return geo, geo.get("metadata", {})
    except FileNotFoundError:
        return {"type": "FeatureCollection", "features": []}, {}
    except (json.JSONDecodeError, OSError, TypeError) as exc:
        return {"type": "FeatureCollection", "features": []}, {"load_error": str(exc)}

ACTIVE_FAULTS_DATA, FAULTS_METADATA = cargar_fallas_activas(FAULTS_DATA_PATH)
FAULTS_DATA_AVAILABLE = len(ACTIVE_FAULTS_DATA.get("features", [])) > 0

VOLCANOES_DATA = [
    {"name": "Cotopaxi", "lat": -0.6806, "lon": -78.4378, "elev": 5897, "type": "Stratovolcano"},
    {"name": "Guagua Pichincha", "lat": -0.1711, "lon": -78.5981, "elev": 4784, "type": "Stratovolcano"},
    {"name": "Tungurahua", "lat": -1.4670, "lon": -78.4420, "elev": 5023, "type": "Stratovolcano"},
    {"name": "Sangay", "lat": -2.0050, "lon": -78.3410, "elev": 5286, "type": "Stratovolcano"},
    {"name": "Reventador", "lat": -0.0770, "lon": -77.6560, "elev": 3562, "type": "Stratovolcano"},
    {"name": "Sumaco", "lat": -0.5360, "lon": -77.6260, "elev": 3732, "type": "Stratovolcano"}
]

# ------------------------------------------------------------------------------
# 4. MOTOR GEODÉSICO VECTORIZADO (NUMPY ULTRA-SPEED)
# ------------------------------------------------------------------------------
PROCESSED_FAULTS = []
for feature in ACTIVE_FAULTS_DATA["features"]:
    coords = np.array(feature["geometry"]["coordinates"])
    lons = coords[:, 0]
    lats = coords[:, 1]
    # Densificación: se agregan puntos medios entre vértices consecutivos para
    # que la búsqueda de distancia mínima no subestime la cercanía en segmentos largos.
    mid_lons = (lons[:-1] + lons[1:]) / 2.0
    mid_lats = (lats[:-1] + lats[1:]) / 2.0
    props = feature["properties"]
    PROCESSED_FAULTS.append({
        "name": props.get("name", "N/D"),
        "slip_type": props.get("slip_type", "N/D"),
        "dip_deg": props.get("dip_deg"),
        "lower_seis_depth_km": props.get("lower_seis_depth_km"),
        "net_slip_rate_mm_yr": props.get("net_slip_rate_mm_yr"),
        "lats": np.concatenate([lats, mid_lats]),
        "lons": np.concatenate([lons, mid_lons])
    })

def asociar_estructura_tectonica(lat, lon, profundidad, idioma):
    if not math.isfinite(profundidad) or profundidad > 30.0:
        return {
            "nombre": ("N/A (fuera del filtro superficial o profundidad desconocida)" if idioma == "ES"
                       else "N/A (outside shallow screening or unknown depth)"),
            "distancia_km": None,
            "dip_deg": None,
            "consistente_buzamiento": None
        }

    if not PROCESSED_FAULTS:
        return {
            "nombre": "Sin datos de fallas para esta región" if idioma == "ES" else "No fault data for this region",
            "distancia_km": None, "dip_deg": None, "consistente_buzamiento": None
        }

    falla_optima = "Sin traza mapeada próxima" if idioma == "ES" else "No mapped fault nearby"
    distancia_optima = float("inf")
    dip_optimo = None

    for ftr in PROCESSED_FAULTS:
        dists = vectorized_haversine(lat, lon, ftr["lats"], ftr["lons"])
        min_f = float(np.min(dists))
        if min_f < distancia_optima:
            distancia_optima = min_f
            falla_optima = ftr["name"]
            dip_optimo = ftr["dip_deg"]

    consistencia = None
    if dip_optimo is not None and distancia_optima != float("inf"):
        resultado = evaluar_consistencia_buzamiento(profundidad, distancia_optima, dip_optimo)
        consistencia = resultado[0] if resultado else None

    return {
        "nombre": falla_optima,
        "distancia_km": distancia_optima,
        "dip_deg": dip_optimo,
        "consistente_buzamiento": consistencia
    }

# ------------------------------------------------------------------------------
# 5. EXTRACCIÓN Y PIPELINE FDSNWS
# ------------------------------------------------------------------------------
@st.cache_data(ttl=300, show_spinner=False)
def obtener_catalogo_sismico(fuente, dias, min_mag, region, idioma):
    fin = datetime.now(timezone.utc)
    inicio = fin - timedelta(days=dias)

    if region == "Ecuador & Northern Andes":
        minlat, maxlat, minlon, maxlon = -5.5, 2.5, -82.5, -74.5
    elif region == "Eastern Pacific (Americas)":
        minlat, maxlat, minlon, maxlon = -60.0, 65.0, -180.0, -65.0
    else:
        minlat, maxlat, minlon, maxlon = -85.0, 85.0, -180.0, 180.0

    if fuente == "USGS":
        url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        parametros = {
            "format": "geojson",
            "starttime": inicio.isoformat(),
            "endtime": fin.isoformat(),
            "minmagnitude": min_mag,
            "minlatitude": minlat, "maxlatitude": maxlat,
            "minlongitude": minlon, "maxlongitude": maxlon,
            "limit": MAX_CATALOG_EVENTS, "orderby": "time"
        }
    else:
        url = "https://www.seismicportal.eu/fdsnws/event/1/query"
        parametros = {
            "format": "json",
            "starttime": inicio.isoformat(),
            "endtime": fin.isoformat(),
            "minmag": min_mag,
            "minlat": minlat, "maxlat": maxlat,
            "minlon": minlon, "maxlon": maxlon,
            "limit": MAX_CATALOG_EVENTS
        }

    try:
        solicitud = requests.get(
            url,
            params=parametros,
            timeout=(4, 20),
            headers={"User-Agent": "AndesPulso/1.0 (academic seismic observatory)"},
        )
        solicitud.raise_for_status()
        carga = solicitud.json().get("features", []) if solicitud.status_code != 204 else []
    except (requests.RequestException, ValueError) as exc:
        return pd.DataFrame(), f"Error de enlace telemétrico con {fuente}: {str(exc)}"

    eventos = []
    for feature in carga:
        prop = feature.get("properties") or {}
        geom = feature.get("geometry") or {}
        coordenadas = geom.get("coordinates", [])

        if len(coordenadas) < 3 or coordenadas[0] is None or coordenadas[1] is None:
            continue

        try:
            lon_val = float(coordenadas[0])
            lat_val = float(coordenadas[1])
            prof_val = float(coordenadas[2]) if coordenadas[2] is not None else float("nan")
        except (TypeError, ValueError):
            continue

        mag_val = prop.get("mag")
        if mag_val is None:
            mag_val = prop.get("magVal")
        try:
            mag_val = float(mag_val)
        except (TypeError, ValueError):
            continue
        if not all(math.isfinite(v) for v in (lon_val,lat_val,mag_val)) or not -180 <= lon_val <= 180 or not -90 <= lat_val <= 90 or not 0 <= mag_val <= 10:
            continue
        if not math.isfinite(prof_val):
            prof_val=float("nan")

        t_raw = prop.get("time")
        tiempo_dt = pd.to_datetime(t_raw, unit="ms" if isinstance(t_raw, (int, float)) else None, utc=True, errors="coerce")
        if pd.isna(tiempo_dt):
            continue

        joules = 10.0 ** (4.8 + 1.5 * mag_val) if mag_val > 0 else 0.0
        asociacion = asociar_estructura_tectonica(lat_val, lon_val, prof_val, idioma) if region == "Ecuador & Northern Andes" else {
            "nombre": "N/D (sin cobertura regional de fallas)" if idioma == "ES" else "N/D (no regional fault coverage)",
            "distancia_km": None,"dip_deg": None,"consistente_buzamiento": None,
        }
        falla_vinculada = asociacion["nombre"]
        distancia_km = asociacion["distancia_km"]
        dip_falla = asociacion["dip_deg"]
        consistente_buzamiento = asociacion["consistente_buzamiento"]

        if not math.isfinite(prof_val):
            regimen_str = "N/D"
        elif prof_val <= 30.0:
            regimen_str = "Profundidad ≤30 km" if idioma == "ES" else "Depth ≤30 km"
        elif prof_val <= 70.0:
            regimen_str = "Profundidad >30–70 km" if idioma == "ES" else "Depth >30–70 km"
        else:
            regimen_str = "Profundidad >70 km" if idioma == "ES" else "Depth >70 km"

        eventos.append({
            "id": feature.get("id", str(prop.get("unid", ""))),
            "lugar": prop.get("place", prop.get("flynn_region", "Región no descrita")),
            "magnitud": mag_val,
            "tiempo": tiempo_dt,
            "fecha_str": tiempo_dt.strftime("%Y-%m-%d"),
            "latitud": lat_val,
            "longitud": lon_val,
            "profundidad_km": prof_val,
            "regimen": regimen_str,
            "energia_j": joules,
            "benioff_strain": math.sqrt(joules),
            "falla_asociada": falla_vinculada,
            "distancia_falla_km": distancia_km,
            "dip_falla_deg": dip_falla,
            "consistente_buzamiento": consistente_buzamiento,
            "fuente": fuente,
            "url_evento": prop.get("url", "")
        })

    df_resultado = pd.DataFrame(eventos)
    if not df_resultado.empty:
        df_resultado = df_resultado.sort_values(by="tiempo").reset_index(drop=True)
        df_resultado["strain_acumulado"] = df_resultado["benioff_strain"].cumsum()
    df_resultado.attrs["limit_reached"] = len(carga) >= MAX_CATALOG_EVENTS
    df_resultado.attrs["fetched_at"] = fin.isoformat()
    return df_resultado, None

# ------------------------------------------------------------------------------
# 6. PANEL LATERAL DE CONTROL OPERATIVO
# ------------------------------------------------------------------------------
with st.sidebar:
    col_nav_logo, col_nav_lang = st.columns([3, 1])
    with col_nav_logo:
        st.markdown("""
        <div class="andes-brand">
            <div class="eyebrow">OBSERVATORIO TERRITORIAL</div>
            <div class="name">Andes Pulso</div>
            <span class="rule"></span>
        </div>
        """, unsafe_allow_html=True)
    with col_nav_lang:
        opciones_idioma = ["ES", "EN"]
        idx_idioma = opciones_idioma.index(st.session_state.lang)
        st.selectbox("🌐", opciones_idioma, index=idx_idioma, label_visibility="collapsed", key="app_lang", on_change=cambiar_idioma)

    vista = st.segmented_control(
        "Explorar" if st.session_state.lang == "ES" else "Explore",
        ["recent", "history", "learn"],
        default=st.query_params.get("view") if st.query_params.get("view") in ["history", "learn"] else "recent",
        format_func=lambda v: {
            "recent": "Pulso reciente", "history": "Memoria sísmica", "learn": "Aula abierta"
        }[v] if st.session_state.lang == "ES" else {
            "recent": "Recent activity", "history": "Seismic memory", "learn": "Open classroom"
        }[v],
        key="atlas_view",
    )

if vista == "history":
    from history_view import render_history
    render_history(st.session_state.lang)
    st.stop()

if vista == "learn":
    from learning_view import render_learning
    render_learning(st.session_state.lang)
    st.stop()

with st.sidebar:
    st.caption("Quantitative Geodynamics & Tectonics Platform")
    st.markdown("---")

    st.markdown(f"#### {t['sidebar_head']}")
    fuente_seleccionada = st.selectbox(t["source_label"], ["USGS", "EMSC"])
    regiones_disponibles = ["Ecuador & Northern Andes", "Eastern Pacific (Americas)", "Global"]
    region_seleccionada = st.selectbox(t["region_label"], regiones_disponibles)

    c_dias, c_mag = st.columns(2)
    with c_dias:
        dias_filtro = st.slider(t["window_days"], 1, 60, 20)
    with c_mag:
        mag_filtro = st.slider(t["min_magnitude"], 1.0, 7.0, 2.5, 0.5)

    st.markdown("---")
    st.markdown(f"#### {t['layers_header']}")
    capas_mapa_opciones = [
        "OpenTopoMap (Topografía OSM + Relieve)",
        "Esri Dark Canvas (Nocturno)",
        "ESRI World Imagery (Satélite)",
        "Esri World Topo Map",
        "OpenStreetMap Standard"
    ]
    capa_cartografica = st.selectbox(t["basemap_label"], capas_mapa_opciones, index=0)

    fallas_cobertura_ok = "Ecuador" in region_seleccionada and FAULTS_DATA_AVAILABLE
    mostrar_fallas = st.checkbox(
        t["layer_faults"], value=fallas_cobertura_ok, disabled=not fallas_cobertura_ok
    )
    if not fallas_cobertura_ok:
        st.caption(
            "⚠️ Trazas de falla verificadas solo disponibles para Ecuador & Andes Norte."
            if st.session_state.lang == "ES"
            else "⚠️ Verified fault traces are only available for Ecuador & Northern Andes."
        )
    mostrar_volcanes = st.checkbox(t["layer_volcanoes"], value=True)
    mostrar_calor = st.checkbox(t["layer_heatmap"], value=False)

    st.markdown("---")
    st.caption("Open Geospatial Services: OpenStreetMap, OpenTopoMap, USGS, EMSC-CSEM.")
    if FAULTS_DATA_AVAILABLE:
        st.caption(
            "Fallas activas: GEM Global Active Faults DB + SARA "
            "(Styron & Pagani, 2020, *Earthquake Spectra* 36(S1), doi:10.1177/8755293020944182), CC-BY-SA 4.0."
        )
    elif FAULTS_METADATA.get("load_error"):
        st.error(f"No se pudo leer el catálogo local de fallas: {FAULTS_METADATA['load_error']}")
    st.markdown("---")
    st.caption("ANDES PULSO · Henry — Ingeniería en Geociencias, Universidad Ikiam")

# Carga telemétrica
with st.spinner("Sincronizando telemetría sísmica y modelos tectónicos..."):
    df_sismos, error_msg = obtener_catalogo_sismico(
        fuente_seleccionada,
        dias_filtro,
        mag_filtro,
        region_seleccionada,
        st.session_state.lang,
    )

if error_msg:
    st.warning(f"⚠️ {error_msg}")

if df_sismos.attrs.get("limit_reached"):
    st.warning(
        f"La consulta alcanzó el límite de {MAX_CATALOG_EVENTS:,} eventos. "
        "Aumenta la magnitud mínima o reduce la ventana para evitar sesgos por truncamiento."
    )

# ------------------------------------------------------------------------------
# 7. ENCABEZADO Y TELEMETRÍA EN TIEMPO REAL
# ------------------------------------------------------------------------------
st.markdown(f"""
<section class="andes-hero">
    <div class="hero-eyebrow">{t['eyebrow']}</div>
    <div class="hero-title">{t['title']}</div>
    <div class="hero-subtitle">{t['subtitle']}</div>
    <div class="hero-chip">◒ &nbsp; {t['live_chip']}</div>
</section>
""", unsafe_allow_html=True)
st.caption("Una herramienta de Henry · Ingeniería en Geociencias · Universidad Ikiam")

with st.expander("Empieza aquí · cómo leer este pulso" if st.session_state.lang == "ES" else "Start here · how to read this activity", expanded=True):
    st.write("1 · Elige zona, días y magnitud mínima en el panel lateral. Los números resumen solo esa consulta, no todos los sismos del país.\n\n"
             "2 · Toca un círculo para leer magnitud, profundidad y fecha. El tamaño indica magnitud; el color, profundidad. Ninguno representa daño en tu barrio.\n\n"
             "3 · Explora dónde y cuándo ocurrieron, o entra al Aula abierta para probar los conceptos con dibujos y ejemplos." if st.session_state.lang == "ES" else
             "1 · Choose an area, days and minimum magnitude in the sidebar. Counts describe only that query, not every earthquake in Ecuador.\n\n"
             "2 · Tap a circle for magnitude, depth and date. Size indicates magnitude; color indicates depth. Neither describes neighborhood damage.\n\n"
             "3 · Explore where and when they occurred, or visit the Open classroom for diagrams and examples.")
    st.link_button("Ir al Aula abierta" if st.session_state.lang == "ES" else "Go to the Open classroom","?view=learn")
    st.caption("Es un catálogo consultado, no una alerta en tiempo real ni un pronóstico. Una falla cercana o un volcán en el mapa no demuestra la causa del sismo." if st.session_state.lang == "ES" else
               "This is a catalog query, not a real-time alert or forecast. A nearby fault or mapped volcano does not establish the earthquake's cause.")

if df_sismos.empty:
    st.warning(t["no_data"])
    st.stop()

# Evento más reciente
ultimo_evento = df_sismos.iloc[-1]
delta_tiempo = datetime.now(timezone.utc) - ultimo_evento["tiempo"]
horas_transcurridas = delta_tiempo.total_seconds() / 3600.0

st.markdown(f"""
<div class="telemetry-banner">
    <div>
        <span class="pulse-dot"></span>
        <strong style="color: #f7efd9;">{t['recent_alert']}</strong>
        <span style="color: #f0c262; font-weight: 700;">M {ultimo_evento['magnitud']:.1f}</span> —
        <span style="color: #ded5c0;">{escape(str(ultimo_evento['lugar']))}</span>
        <span style="color: #aaa48f; font-size: 0.85rem;">(Hace {horas_transcurridas:.1f} hrs · Prof: {f"{ultimo_evento['profundidad_km']:.1f} km" if pd.notna(ultimo_evento['profundidad_km']) else "N/D"})</span>
    </div>
    <div style="font-family: 'DM Mono', monospace; font-size: 0.8rem; color: #e4b454;">
        {ultimo_evento['tiempo'].strftime('%Y-%m-%d %H:%M UTC')}
    </div>
</div>
""", unsafe_allow_html=True)

mc_estimado = estimar_mc_maxima_curvatura(df_sismos["magnitud"])
mc = mc_estimado if mc_estimado is not None else mag_filtro
mags_completas = df_sismos[df_sismos["magnitud"] >= mc]["magnitud"]
estimacion_b, error_b, _ = calcular_valor_b(df_sismos["magnitud"], mc)
cadena_b = f"{estimacion_b:.2f} ± {error_b:.2f}" if estimacion_b is not None else "N/D"

energia_mwh = (df_sismos["energia_j"].sum()) / (3.6e9)

# Grid de KPIs
m1, m2, m3 = st.columns(3)
m1.metric(t["kpi_events"], f"{len(df_sismos):,}")
m2.metric(t["kpi_max_mag"], f"M {df_sismos['magnitud'].max():.1f}")
m3.metric(t["kpi_mean_depth"], f"{df_sismos['profundidad_km'].mean():.1f} km" if df_sismos['profundidad_km'].notna().any() else "N/D")
with st.expander("Para profundizar · indicadores técnicos" if st.session_state.lang == "ES" else "Explore further · technical indicators"):
    m4, m5 = st.columns(2)
    m4.metric(t["kpi_b_val"], cadena_b,
        help=f"Aki (1965) + Shi & Bolt (1982). Mc ≈ {mc:.2f} (Máxima Curvatura; Wiemer & Wyss, 2000).")
    m5.metric(t["kpi_energy"], f"{energia_mwh:.2f} MWh")
    st.write("El valor b compara la abundancia de sismos pequeños y grandes dentro de la muestra. Mc estima desde qué magnitud el registro podría ser suficientemente completo; no es el tamaño del próximo sismo. Una consulta corta puede dar estimaciones muy inciertas.\n\n"
             "La energía es una aproximación a partir de magnitud, no una medición ni energía utilizable. Se mezclan tipos de magnitud sin homogeneizar: no la interpretes como un balance físico exacto ni como daño." if st.session_state.lang == "ES" else
             "b compares the abundance of smaller and larger earthquakes in the sample. Mc estimates a possible catalog completeness threshold, not the next earthquake's size. Short queries can give highly uncertain estimates.\n\n"
             "Energy is approximated from magnitude, not measured or usable energy. Mixed magnitude types are not homogenized: this is not an exact physical balance or a damage estimate.")
    st.caption(f"Mc ≈ M {mc:.2f} · n={len(mags_completas)} · Máxima Curvatura / Aki MLE")

st.caption(
    f"{'Fuente' if st.session_state.lang == 'ES' else 'Source'}: **{fuente_seleccionada}** · "
    f"{'Corte de consulta UTC' if st.session_state.lang == 'ES' else 'Query cutoff UTC'}: **{df_sismos.attrs.get('fetched_at','N/D')}**"
)
st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 8. CONSOLA DE ANÁLISIS EN PESTAÑAS TÉCNICAS
# ------------------------------------------------------------------------------
tab_mapa, tab_perfil3d, tab_tiempo, tab_analisis, tab_registro = st.tabs([
    t["tab_map"], t["tab_3d"], t["tab_time"], t["tab_gr"], t["tab_data"]
])

# ------------------------------------------------------------------------------
# PESTAÑA 1: VISOR TOPOGRÁFICO Y SISMOTECTÓNICO MULTI-CAPA
# ------------------------------------------------------------------------------
with tab_mapa:
    lat_centro = -1.2 if "Ecuador" in region_seleccionada else (10.0 if "Pacific" in region_seleccionada else 20.0)
    lon_centro = -78.5 if "Ecuador" in region_seleccionada else (-100.0 if "Pacific" in region_seleccionada else 0.0)
    zoom_centro = 7 if "Ecuador" in region_seleccionada else (3 if "Pacific" in region_seleccionada else 2)

    mapa_folium = folium.Map(location=[lat_centro, lon_centro], zoom_start=zoom_centro, tiles=None, control_scale=True)

    # 1. Capa Topográfica Abierta de OpenStreetMap
    folium.TileLayer(
        tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        attr="Kartendaten: &copy; OpenStreetMap-Mitwirkende, SRTM | Kartendarstellung: &copy; OpenTopoMap (CC-BY-SA)",
        name="Topografía (OpenTopoMap OSM)",
        show=capa_cartografica.startswith("OpenTopoMap"),
    ).add_to(mapa_folium)

    # 2. Capa Oscura Esri
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ",
        name="Nocturno (Esri Canvas)",
        show=capa_cartografica.startswith("Esri Dark"),
    ).add_to(mapa_folium)

    # 3. Capa Satelital de Alta Definición
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
        name="Satelital (Esri World Imagery)",
        show=capa_cartografica.startswith("ESRI World Imagery"),
    ).add_to(mapa_folium)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri",
        name="Esri World Topo Map",
        show=capa_cartografica.startswith("Esri World Topo"),
    ).add_to(mapa_folium)

    # 4. OpenStreetMap Estándar
    folium.TileLayer(
        tiles="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="&copy; OpenStreetMap contributors",
        name="OpenStreetMap Estándar",
        show=capa_cartografica.startswith("OpenStreetMap Standard"),
    ).add_to(mapa_folium)

    # Inyección de estructuras neotectónicas
    if mostrar_fallas:
        grupo_fallas = folium.FeatureGroup(name="Fallas Activas (GEM/SARA)")
        for ftr in ACTIVE_FAULTS_DATA["features"]:
            props = ftr["properties"]
            coords_poli = [[punto[1], punto[0]] for punto in ftr["geometry"]["coordinates"]]
            dip_txt = f"{props['dip_deg']:.0f}°" if props.get("dip_deg") is not None else "N/D"
            tasa_txt = f"{props['net_slip_rate_mm_yr']:.1f} mm/año" if props.get("net_slip_rate_mm_yr") is not None else "N/D"
            folium.PolyLine(
                locations=coords_poli,
                color="#c95434",
                weight=3.0,
                opacity=0.9,
                tooltip=(f"<b>{props['name']}</b><br>Cinemática: {props['slip_type']}<br>"
                         f"Buzamiento: {dip_txt}<br>Tasa: {tasa_txt}<br>"
                         f"Fuente: {props.get('catalog_name', 'GEM GAF-DB')}")
            ).add_to(grupo_fallas)
        grupo_fallas.add_to(mapa_folium)

    # Inyección de arcos volcánicos
    if mostrar_volcanes:
        grupo_volcanes = folium.FeatureGroup(name="Arcos Volcánicos (Smithsonian GVP)")
        for v in VOLCANOES_DATA:
            icono = """<div style="font-size: 17px; text-shadow: 0 0 4px #000;">🌋</div>"""
            folium.Marker(
                location=[v["lat"], v["lon"]],
                icon=folium.DivIcon(html=icono),
                tooltip=f"<b>Volcán {v['name']}</b> ({v['elev']} msnm)<br>{v['type']}"
            ).add_to(grupo_volcanes)
        grupo_volcanes.add_to(mapa_folium)

    # Densidad Kernel
    if mostrar_calor:
        puntos_densidad = [[fila["latitud"], fila["longitud"], fila["magnitud"]] for _, fila in df_sismos.iterrows()]
        HeatMap(puntos_densidad, radius=16, blur=12, max_zoom=8, name="Densidad Kernel").add_to(mapa_folium)

    # Marcadores de eventos con cálculo de profundidad
    for _, r in df_sismos.iterrows():
        prof = r["profundidad_km"]
        color_evento = "#889392" if pd.isna(prof) else "#ef4444" if prof <= 30 else ("#f59e0b" if prof <= 70 else "#0ea5e9")
        radio_marcador = max(3.5, int(r["magnitud"] * 2.3))

        dist_falla_str = f"{r['distancia_falla_km']:.1f} km" if r['distancia_falla_km'] is not None else "N/A"
        dip_str = f"{r['dip_falla_deg']:.0f}°" if r.get('dip_falla_deg') is not None else "N/D"
        if r.get('consistente_buzamiento') is True:
            consist_html = "<span style='color:#16a34a; font-weight:600;'>Sí (compatible con buzamiento)</span>"
        elif r.get('consistente_buzamiento') is False:
            consist_html = "<span style='color:#dc2626; font-weight:600;'>No (distancia no compatible)</span>"
        else:
            consist_html = "N/D"
        popup_contenido = f"""
        <div style="font-family: 'Manrope', sans-serif; font-size: 12px; min-width: 230px; color: #2c281f;">
            <b style="font-size: 13px; color: #0284c7;">{escape(str(r['lugar']))}</b>
            <hr style="margin: 4px 0; border: 0.5px solid #cbd5e1;">
            <b>Magnitud:</b> M {r['magnitud']:.1f}<br>
            <b>Profundidad:</b> {f"{r['profundidad_km']:.1f} km" if pd.notna(r['profundidad_km']) else "N/D"}<br>
            <b>Intervalo de profundidad:</b> {escape(str(r['regimen']))}<br>
            <b>Fecha UTC:</b> {r['tiempo'].strftime('%Y-%m-%d %H:%M')}<br>
            <b>Coordenadas:</b> {r['latitud']:.3f}, {r['longitud']:.3f}<br>
            <hr style="margin: 4px 0; border: 0.5px dashed #cbd5e1;">
            <b>{t['assoc_fault']}</b> {escape(str(r['falla_asociada']))}<br>
            <b>{t['distance_fault']}</b> {dist_falla_str}<br>
            <b>Buzamiento reportado:</b> {dip_str}<br>
            <b>Consistencia geométrica:</b> {consist_html}
        </div>
        """
        folium.CircleMarker(
            location=[r["latitud"], r["longitud"]],
            radius=radio_marcador,
            color=color_evento,
            weight=1.2,
            fill=True,
            fill_color=color_evento,
            fill_opacity=0.85,
            popup=folium.Popup(popup_contenido, max_width=290)
        ).add_to(mapa_folium)

    folium.LayerControl(position="topright", collapsed=False).add_to(mapa_folium)
    Fullscreen().add_to(mapa_folium)
    st_folium(mapa_folium, width="100%", height=590, returned_objects=[])

    st.caption(f"🔴 {t['shallow_legend']} | 🟡 {t['inter_legend']} | 🔵 {t['deep_legend']} | ━━ Fallas Activas | 🌋 Arcos Volcánicos")
    st.caption("Los colores son intervalos de profundidad, no identifican el régimen tectónico ni el peligro. Haz clic en un círculo para leer el registro; tamaño = magnitud. La falla más cercana es una asociación exploratoria, no una causa confirmada." if st.session_state.lang == "ES" else
               "Colors are depth intervals, not tectonic regimes or danger levels. Click a circle to read the record; size = magnitude. The nearest fault is an exploratory association, not a confirmed cause.")
    st.caption("Gris = profundidad desconocida. No se representa a profundidad cero en las vistas de hipocentros." if st.session_state.lang == "ES" else
               "Gray = unknown depth. It is not plotted at zero depth in hypocenter views.")

# ------------------------------------------------------------------------------
# PESTAÑA 2: HIPOCENTROS 3D & CORTE SECCIONAL DE SUBDUCCIÓN
# ------------------------------------------------------------------------------
with tab_perfil3d:
    st.caption("Imagina mirar el subsuelo de lado: la profundidad crece hacia abajo. El control de latitud selecciona una franja para el corte. No se dibujan los puntos sin profundidad conocida ni se identifica una falla con este dibujo." if st.session_state.lang == "ES" else
               "Imagine viewing underground from the side: depth increases downward. The latitude control selects a strip for the section. Records without depth are not plotted, and this diagram does not identify a fault.")
    col_ctrl, col_corte_title = st.columns([1.2, 0.8])
    with col_ctrl:
        st.markdown(f"#### {t['heading_3d']}")
    with col_corte_title:
        st.markdown(f"#### {t['heading_profile']}")

    lat_min_data, lat_max_data = float(df_sismos["latitud"].min()), float(df_sismos["latitud"].max())
    if lat_min_data == lat_max_data:
        lat_max_data += 0.5

    rango_lat = st.slider(
        "Franja de Latitud para el Perfil A–A' (°):",
        min_value=lat_min_data,
        max_value=lat_max_data,
        value=(lat_min_data, lat_max_data),
        step=0.2
    )

    df_slice = df_sismos[(df_sismos["latitud"] >= rango_lat[0]) & (df_sismos["latitud"] <= rango_lat[1])]

    c_3d, c_perfil = st.columns([1.2, 0.8])
    with c_3d:
        figura_3d = go.Figure(data=[go.Scatter3d(
            x=df_sismos["longitud"],
            y=df_sismos["latitud"],
            z=df_sismos["profundidad_km"],
            mode="markers",
            marker=dict(
                size=df_sismos["magnitud"] * 2.2,
                color=df_sismos["profundidad_km"],
                colorscale="Plasma_r",
                colorbar=dict(title="Prof (km)"),
                opacity=0.85
            ),
            text=[f"{l}<br>M {m:.1f} | Prof: {p:.1f} km<br>Falla: {f}" 
                  for l, m, p, f in zip(df_sismos['lugar'], df_sismos['magnitud'], df_sismos['profundidad_km'], df_sismos['falla_asociada'])],
            hoverinfo="text"
        )])
        figura_3d.update_layout(
            scene=dict(
                xaxis=dict(title="Longitud (°)", backgroundcolor="#24251b", gridcolor="#4e4d3d"),
                yaxis=dict(title="Latitud (°)", backgroundcolor="#24251b", gridcolor="#4e4d3d"),
                zaxis=dict(title="Profundidad (km)", autorange="reversed", backgroundcolor="#24251b", gridcolor="#4e4d3d"),
                bgcolor="#24251b"
            ),
            paper_bgcolor="#171811",
            font=dict(color="#ded5c0", family="Manrope"),
            height=510,
            margin=dict(l=5, r=5, t=10, b=10)
        )
        st.plotly_chart(figura_3d, width="stretch")

    with c_perfil:
        if df_slice.empty:
            st.info("Ajusta el slider de latitud para visualizar eventos en este corte transversal.")
        else:
            figura_perfil = px.scatter(
                df_slice,
                x="longitud",
                y="profundidad_km",
                color="profundidad_km",
                size="magnitud",
                color_continuous_scale="Plasma_r",
                labels={"longitud": "Longitud W-E (°)", "profundidad_km": "Profundidad (km)"},
                template="plotly_dark",
                title=f"Corte A-A' [{rango_lat[0]:.1f}° a {rango_lat[1]:.1f}° Lat]"
            )
            figura_perfil.update_yaxes(autorange="reversed", gridcolor="#4e4d3d", zeroline=False)
            figura_perfil.update_xaxes(gridcolor="#4e4d3d")
            figura_perfil.update_layout(
                paper_bgcolor="#171811",
                plot_bgcolor="#24251b",
                font=dict(family="Manrope", color="#ded5c0"),
                height=480,
                coloraxis_showscale=False,
                margin=dict(l=10, r=10, t=35, b=10)
            )
            st.plotly_chart(figura_perfil, width="stretch")

# ------------------------------------------------------------------------------
# PESTAÑA 3: EVOLUCIÓN 4D Y MIGRACIÓN ESPACIOTEMPORAL
# ------------------------------------------------------------------------------
with tab_tiempo:
    st.markdown(f"#### {t['heading_time']}")
    st.caption("Secuencia día a día de registros. Los grupos de puntos no identifican por sí solos réplicas, enjambres ni una migración de ruptura." if st.session_state.lang == "ES" else
               "Day-by-day records. Clusters alone do not establish aftershocks, swarms or rupture migration.")

    df_animado = df_sismos.sort_values(by="tiempo").copy()
    figura_anim = px.scatter(
        df_animado,
        x="longitud",
        y="latitud",
        animation_frame="fecha_str",
        animation_group="id",
        size="magnitud",
        color="profundidad_km",
        color_continuous_scale="Viridis",
        hover_name="lugar",
        range_x=[df_animado["longitud"].min() - 0.5, df_animado["longitud"].max() + 0.5],
        range_y=[df_animado["latitud"].min() - 0.5, df_animado["latitud"].max() + 0.5],
        labels={"fecha_str": "Fecha UTC", "profundidad_km": "Profundidad (km)"},
        template="plotly_dark"
    )
    figura_anim.update_layout(
        paper_bgcolor="#171811",
        plot_bgcolor="#24251b",
        font=dict(family="Manrope", color="#ded5c0"),
        height=540,
        margin=dict(l=10, r=10, t=20, b=10)
    )
    st.plotly_chart(figura_anim, width="stretch")

# ------------------------------------------------------------------------------
# PESTAÑA 4: LEY GUTENBERG-RICHTER & BENIOFF STRAIN
# ------------------------------------------------------------------------------
with tab_analisis:
    st.info("Lectura exploratoria, no predicción. La curva G-R cuenta cuántos sismos superan cada magnitud. La curva de Benioff suma raíces de energías estimadas: sube cuando se añaden eventos; no mide deformación del terreno ni energía que falta por liberar." if st.session_state.lang == "ES" else
            "Exploratory analysis, not prediction. The G-R curve counts events above each magnitude. The Benioff curve sums square roots of estimated energies: it rises as events are added, not as a measurement of ground deformation or remaining energy.")
    col_gr, col_strain = st.columns(2)

    with col_gr:
        st.markdown(f"#### {t['heading_gr']}")
        escalones_m = np.arange(df_sismos["magnitud"].min(), df_sismos["magnitud"].max() + 0.4, 0.2)
        conteo_n = [np.sum(df_sismos["magnitud"] >= b) for b in escalones_m]
        filtro_valido = np.array(conteo_n) > 0
        m_vals = escalones_m[filtro_valido]
        log_n_vals = np.log10(np.array(conteo_n)[filtro_valido])

        figura_gr = go.Figure()
        figura_gr.add_trace(go.Scatter(
            x=m_vals,
            y=log_n_vals,
            mode="markers",
            marker=dict(color="#e4b454", size=8),
            name="log10 N(>=M) Observado"
        ))

        if estimacion_b is not None and estimacion_b > 0:
            n_mc = np.sum(df_sismos["magnitud"] >= mc)
            if n_mc > 0:
                a_param = math.log10(n_mc) + estimacion_b * mc
                m_fit = np.linspace(mc, df_sismos["magnitud"].max(), 50)
                log_n_fit = a_param - estimacion_b * m_fit
                figura_gr.add_trace(go.Scatter(
                    x=m_fit,
                    y=log_n_fit,
                    mode="lines",
                    line=dict(color="#ef4444", width=2.2, dash="dash"),
                    name=f"Ajuste G-R (b={estimacion_b:.2f})"
                ))

        figura_gr.update_layout(
            template="plotly_dark",
            paper_bgcolor="#171811",
            plot_bgcolor="#24251b",
            xaxis_title="Magnitud (M)",
            yaxis_title="log10 N (Acumulado)",
            font=dict(family="Manrope", color="#ded5c0"),
            height=400,
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(x=0.05, y=0.15, bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(figura_gr, width="stretch")

    with col_strain:
        st.markdown(f"#### {t['heading_strain']}")
        figura_strain = px.line(
            df_sismos,
            x="tiempo",
            y="strain_acumulado",
            template="plotly_dark",
            labels={"tiempo": "Fecha UTC", "strain_acumulado": "Σ √E estimada (J^0.5)"}
        )
        figura_strain.update_traces(line_color="#f59e0b", line_width=2.5)
        figura_strain.update_layout(
            paper_bgcolor="#171811",
            plot_bgcolor="#24251b",
            font=dict(family="Manrope", color="#ded5c0"),
            height=400,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(figura_strain, width="stretch")

# ------------------------------------------------------------------------------
# PESTAÑA 5: CATÁLOGO ESTRUCTURADO Y EXPORTACIÓN
# ------------------------------------------------------------------------------
with tab_registro:
    st.markdown(f"#### {t['heading_catalog']}")
    columnas_tabla = [
        "tiempo", "lugar", "magnitud", "profundidad_km",
        "latitud", "longitud", "regimen", "falla_asociada", "distancia_falla_km",
        "dip_falla_deg", "consistente_buzamiento", "fuente", "url_evento"
    ]
    df_exportable = df_sismos[columnas_tabla].sort_values(by="tiempo", ascending=False)
    st.dataframe(
        df_exportable,
        width="stretch",
        height=420,
        hide_index=True,
        column_config={
            "regimen": st.column_config.TextColumn("Intervalo de profundidad" if st.session_state.lang == "ES" else "Depth interval"),
            "url_evento": st.column_config.LinkColumn("Evento original", display_text="Abrir fuente"),
            "magnitud": st.column_config.NumberColumn("Magnitud", format="%.1f"),
            "profundidad_km": st.column_config.NumberColumn("Profundidad (km)", format="%.1f"),
            "distancia_falla_km": st.column_config.NumberColumn("Distancia a falla (km)", format="%.1f"),
        },
    )

    csv_datos = df_exportable.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=t["export_btn"],
        data=csv_datos,
        file_name=f"andes_pulso_{fuente_seleccionada}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )
