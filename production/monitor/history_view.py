"""Streamlit interface for the historical, reference-inspired Ecuador atlas."""
from datetime import datetime, timezone
from pathlib import Path
from hashlib import sha256
import requests
import streamlit as st

from historical import fetch_history, build_animation, annual_counts, export_animation
from learning_view import render_map_guide, event_reader


@st.cache_data(ttl=3600, max_entries=8, show_spinner=False)
def load_history(first_year, last_year, minimum, cutoff):
    return fetch_history(first_year,last_year,minimum,cutoff)


@st.cache_data(max_entries=2, show_spinner=False)
def animation(df, first_year, last_year, accumulated, english, cutoff, minimum, renderer_version, initial_year, frame_ms):
    # Streamlit hashes DataFrame values, not attrs. Keep provenance in explicit arguments.
    df.attrs.update(cutoff=cutoff,minimum=minimum)
    return build_animation(df,first_year,last_year,accumulated,english,initial_year,frame_ms)


@st.fragment
def map_player(df, first, last, minimum, mode, en):
    if first < last:
        current=st.session_state.setdefault("history_read_year",last)
        if not first <= current <= last:
            st.session_state.history_read_year=last
        year=st.slider("Año inicial del mapa" if not en else "Map opening year",min_value=first,max_value=last,key="history_read_year")
    else:
        year=first
    speed=st.select_slider("Tiempo para observar cada año" if not en else "Time to observe each year",[.4,.8,1.2],value=.8,
                           format_func=lambda v:f"{v:g} s",key="history_speed")
    accumulated=mode!="annual"
    selected=df[df.time.dt.year<=year] if accumulated else df[df.time.dt.year==year]
    st.caption((f"Estado inicial: {len(selected):,} registros " + (f"desde {first} hasta {year}." if accumulated else f"de {year}.")) if not en else
               f"Opening state: {len(selected):,} records " + (f"from {first} through {year}." if accumulated else f"in {year}."))
    st.caption("Reproducir recorre el período desde el inicio. El contador dentro del mapa muestra el año de la película. Los puntos son registros pasados, no sismos en curso." if not en else
               "Play runs from the start of the period. The map's internal counter shows the movie year. Points are past records, not ongoing earthquakes.")
    with st.spinner("Preparando la película cartográfica…" if not en else "Preparing the cartographic animation…"):
        renderer_version=sha256((Path(__file__).parent / "historical.py").read_bytes()).hexdigest()
        fig=animation(df,first,last,accumulated,en,df.attrs["cutoff"],minimum,renderer_version,year,round(speed*1000))
    st.plotly_chart(fig,width="stretch",key="history_map",theme=None,
                    config=dict(displaylogo=False,scrollZoom=False,toImageButtonOptions=dict(filename="andes_pulso_memoria",scale=2)))
    with st.container(horizontal=True):
        if st.button("Preparar animación descargable" if not en else "Prepare downloadable animation",key="history_export"):
            st.download_button("Descargar animación HTML" if not en else "Download HTML animation",export_animation(fig),
                file_name=f"andes_pulso_ecuador_{first}_{last}_{mode}.html",mime="text/html",key="history_html",on_click="ignore")
        st.download_button("Catálogo CSV" if not en else "Catalog CSV",df.to_csv(index=False).encode("utf-8"),
            file_name=f"andes_pulso_ecuador_{first}_{last}.csv",mime="text/csv",on_click="ignore")


def render_history(language="ES"):
    en = language == "EN"
    now = datetime.now(timezone.utc)
    st.html("""<section class="andes-hero">
        <div class="hero-eyebrow">ANDES PULSO / ATLAS 01</div>
        <div class="hero-title">Memoria sísmica.</div>
        <div class="hero-subtitle">Un país que se mueve. Una historia que deja huella.</div>
        <div class="hero-chip">◒ ECUADOR · OCÉANO · ANDES</div></section>""" if not en else """
        <section class="andes-hero"><div class="hero-eyebrow">ANDES PULSO / ATLAS 01</div>
        <div class="hero-title">Seismic memory.</div><div class="hero-subtitle">A land in motion. A history written in its traces.</div>
        <div class="hero-chip">◒ ECUADOR · OCEAN · ANDES</div></section>""")
    st.caption("Adaptación cartográfica de la referencia de @notasdeungeologo · Datos reales USGS" if not en else
               "Cartographic adaptation of @notasdeungeologo's reference · Real USGS data")
    guided=st.toggle("Mostrar guía para aprender" if not en else "Show learning guide",value=True,key="history_guided")
    if guided:
        render_map_guide(en)
    with st.sidebar:
        st.markdown("### Archivo histórico" if not en else "### Historical archive")
        with st.form("history_filters"):
            years = st.slider("Período · años UTC" if not en else "Period · UTC years",1900,now.year,(1900,now.year),key="history_years")
            minimum = st.select_slider("Magnitud mínima" if not en else "Minimum magnitude",options=[3.,3.5,4.,4.5,5.,5.5,6.],value=4.,key="history_min")
            submitted = st.form_submit_button("Cargar archivo" if not en else "Load archive",width="stretch",type="primary")
        st.caption("Ecuador continental + margen oceánico y áreas vecinas. No incluye Galápagos." if not en else
                   "Mainland Ecuador + offshore margin and neighboring areas. Excludes Galápagos.")
        st.caption("Colores: profundidad. Círculos: magnitud. Diamantes grises: profundidad desconocida." if not en else
                   "Color: depth. Circle size: magnitude. Gray diamonds: unknown depth.")
    # The active filters change only on form submission; a playback/view switch never fetches a new period.
    if "history_query" not in st.session_state or submitted:
        st.session_state.history_query = (*years,minimum,now.isoformat())
    first,last,minimum,cutoff = st.session_state.history_query
    mode = st.segmented_control("Lectura del territorio" if not en else "Map perspective",
        ["cumulative","annual"],default="cumulative",key="history_mode",
        format_func=lambda v: ("Huella acumulada" if v=="cumulative" else "Año a año") if not en else
                              ("Cumulative traces" if v=="cumulative" else "Year by year"))
    st.caption(("Huella acumulada conserva registros de años anteriores. Año a año muestra solo los del año seleccionado." if not en else
                "Cumulative traces retains previous years' records. Year by year shows only the selected year's records."))
    with st.spinner("Consultando el archivo histórico USGS…" if not en else "Fetching the USGS historical archive…"):
        try:
            df = load_history(first,last,minimum,cutoff)
        except (requests.RequestException,ValueError) as exc:
            st.error(("No se pudo cargar el archivo: " if not en else "Unable to load the archive: ")+str(exc))
            st.info("Prueba otro período o una magnitud mínima mayor y pulsa Cargar archivo." if not en else
                    "Try a shorter period or a higher minimum magnitude, then press Load archive.")
            return
    if df.attrs["omitted"]:
        st.warning(f"{df.attrs['omitted']} registros duplicados o sin coordenadas, fecha o magnitud válidas fueron excluidos." if not en else
                   f"{df.attrs['omitted']} duplicate or invalid records were excluded.")
    if df.empty:
        st.info("Sin eventos catalogados para estos filtros. Esto no demuestra ausencia de sismos." if not en else
                "No cataloged events for these filters. This does not establish an absence of earthquakes.")
        return
    with st.container(horizontal=True):
        st.metric("Sismos catalogados" if not en else "Cataloged events",f"{len(df):,}",border=True)
        st.metric("Archivo consultado" if not en else "Queried archive",f"{first} — {last}",border=True)
        st.metric("Magnitud máxima" if not en else "Largest magnitude",f"M {df.magnitude.max():.1f}",border=True)
    st.caption((f"Filtro M ≥ {minimum:g} · Corte UTC: {df.attrs['cutoff']} · " +
                "Pulsa Reproducir para recorrer los años o arrastra la línea de tiempo.") if not en else
               f"Filter M ≥ {minimum:g} · UTC cutoff: {df.attrs['cutoff']} · Play or scrub the timeline.")
    map_player(df,first,last,minimum,mode,en)
    st.caption("La escala de profundidad es fija (0–300 km; ≥300 comparte el color final). El tamaño del símbolo no representa energía ni área de ruptura." if not en else
               "Fixed depth scale: 0–300 km (≥300 uses the last color). Symbol size does not represent energy or rupture area.")
    st.subheader("Registros por año, no un pronóstico" if not en else "Records per year, not a forecast")
    st.caption("Cada barra cuenta eventos que cumplen el filtro. Las redes de observación y la cobertura histórica cambian; una barra mayor no demuestra por sí sola un aumento de actividad." if not en else
               "Each bar counts events matching the filter. Monitoring and historical coverage change; a taller bar alone does not establish increased activity.")
    counts = annual_counts(df,first,last).rename("Sismos catalogados" if not en else "Cataloged events")
    st.bar_chart(counts,color="#c95434",height=160)
    if guided:
        event_reader(df,en)
        with st.container(border=True):
            st.markdown("**Lo que este mapa no puede decirte**" if not en else "**What this map cannot tell you**")
            st.write("No mide el daño en tu barrio ni señala el próximo sismo. Un grupo de puntos no confirma una falla ni una secuencia de réplicas por sí solo." if not en else
                     "It does not measure damage in your neighborhood or locate the next earthquake. A cluster alone cannot establish a fault or an aftershock sequence.")
            st.link_button("Seguir aprendiendo en el Aula abierta" if not en else "Continue in the Open classroom","?view=learn")
    with st.expander("Cómo leer este archivo · fuentes y límites" if not en else "Reading the archive · sources and limitations"):
        st.markdown("""El año 1900 es el inicio de esta consulta, **no el primer sismo del Ecuador**. Los registros históricos son incompletos y las redes de monitoreo cambian: no compares conteos anuales como una tendencia física sin estudiar la completitud.

La selección es una ventana regional (83°–74,5° O; 5,5° S–2,5° N), no un filtro por fronteras. Se incluyen sismos oceánicos y de países vecinos. Las magnitudes conservan el tipo reportado por USGS; no están homogeneizadas a Mw. Los años sin puntos significan que no hay registros que cumplan los filtros. El último año puede estar incompleto.

Fuentes: [USGS FDSN Event API](https://earthquake.usgs.gov/fdsnws/event/1/) · [Natural Earth, dominio público](https://www.naturalearthdata.com/about/terms-of-use/) · [Reel de referencia](https://www.instagram.com/reel/Dd4-gbFCZV3/).

El mapa base se incluye localmente. La animación descargada funciona sin conexión. Andes Pulso no predice sismos ni reemplaza al Instituto Geofísico del Ecuador.""" if not en else """
1900 starts this query, **not Ecuador's earthquake history**. Historical records are incomplete and monitoring networks change. Annual counts alone are not evidence of changing seismicity.

Regional rectangle: 83°–74.5° W, 5.5° S–2.5° N, not a political-boundary filter. Includes offshore and neighboring-country events, excludes Galápagos. USGS magnitude types are retained, not homogenized to Mw. Empty years have no matching catalog records. The latest year may be incomplete.

[USGS FDSN Event API](https://earthquake.usgs.gov/fdsnws/event/1/) · [Natural Earth, public domain](https://www.naturalearthdata.com/about/terms-of-use/) · [Reference reel](https://www.instagram.com/reel/Dd4-gbFCZV3/).

The downloaded animation works offline. Andes Pulso does not predict earthquakes or replace Ecuador's Instituto Geofísico.""")
    st.caption("ANDES PULSO · Henry — Geociencias, Universidad Ikiam · Made with Natural Earth")
