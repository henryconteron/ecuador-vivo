"""Historical USGS catalog and tile-free cartographic animation (no Streamlit)."""
from datetime import datetime, timezone
from pathlib import Path
import json
import math

import pandas as pd
import plotly.graph_objects as go
from plotly.colors import sample_colorscale
import requests

SERVICE = "https://earthquake.usgs.gov/fdsnws/event/1/"
# A regional rectangle, NOT Ecuador's political boundary. Galápagos is outside.
BOUNDS = dict(minlatitude=-5.5, maxlatitude=2.5, minlongitude=-83, maxlongitude=-74.5)
MAX_EVENTS = 6000
COLUMNS = ["id", "time", "longitude", "latitude", "depth", "magnitude", "mag_type", "place"]
DEPTH_SCALE = [[0, "#fff0af"], [20/300, "#f6c576"], [70/300, "#e37e62"],
               [120/300, "#a84153"], [200/300, "#582d4d"], [1, "#201b2a"]]


def normalize_features(features):
    rows = []
    for feature in features:
        props = feature.get("properties") or {}
        coords = (feature.get("geometry") or {}).get("coordinates") or []
        try:
            lon, lat = float(coords[0]), float(coords[1])
            magnitude = float(props["mag"])
            time = pd.to_datetime(props["time"], unit="ms", utc=True)
            if not all(math.isfinite(n) for n in (lon, lat, magnitude)) or pd.isna(time):
                continue
            if not -180 <= lon <= 180 or not -90 <= lat <= 90:
                continue
        except (KeyError, TypeError, ValueError, IndexError, OverflowError):
            continue
        try:
            depth = float(coords[2])
            if not math.isfinite(depth):
                depth = None
        except (TypeError, ValueError, IndexError):
            depth = None
        rows.append(dict(id=str(feature.get("id") or f"{time.isoformat()}:{lon}:{lat}:{magnitude}"),
                         time=time, longitude=lon, latitude=lat, depth=depth,
                         magnitude=magnitude, mag_type=str(props.get("magType") or "N/D"),
                         place=str(props.get("place") or "N/D")))
    df = pd.DataFrame(rows, columns=COLUMNS)
    df["time"] = pd.to_datetime(df["time"], utc=True)
    return df.drop_duplicates("id").sort_values(["time", "id"]).reset_index(drop=True)


def fetch_history(first_year, last_year, minimum, endtime, get=requests.get, page_size=2000):
    """Fixed UTC cutoff and 1-based pagination; never silently truncate a catalog."""
    if not 1900 <= first_year <= last_year <= datetime.now(timezone.utc).year:
        raise ValueError("El período debe estar entre 1900 y el año actual.")
    cutoff = pd.Timestamp(endtime)
    if cutoff.tzinfo is None:
        raise ValueError("El corte debe incluir zona horaria UTC.")
    cutoff = min(cutoff.tz_convert("UTC"), pd.Timestamp(f"{last_year + 1}-01-01", tz="UTC") - pd.Timedelta(milliseconds=1))
    params = dict(BOUNDS, starttime=f"{first_year}-01-01T00:00:00Z",
                  endtime=cutoff.isoformat(), minmagnitude=minimum, eventtype="earthquake")
    count_response = get(SERVICE + "count", params=params, timeout=(5, 40))
    count_response.raise_for_status()
    expected = int(count_response.text) if count_response.status_code != 204 else 0
    if expected > MAX_EVENTS:
        raise ValueError(f"La consulta contiene {expected:,} eventos; el límite de la animación es {MAX_EVENTS:,}. "
                         "Aumenta la magnitud mínima o reduce el período. No se ha truncado el catálogo.")
    features = []
    for offset in range(1, expected + 1, page_size):
        response = get(SERVICE + "query", params=dict(params, format="geojson", orderby="time-asc",
                       limit=page_size, offset=offset), timeout=(5, 40))
        response.raise_for_status()
        if response.status_code != 204:
            features.extend(response.json().get("features", []))
    if len(features) != expected:
        raise ValueError("El catálogo cambió durante la descarga o llegó incompleto. Vuelve a cargarlo.")
    df = normalize_features(features)
    df.attrs.update(source="USGS", expected=expected, omitted=expected-len(df),
                    cutoff=cutoff.isoformat(), bounds=BOUNDS.copy(), minimum=minimum)
    return df


def magnitude_size(magnitude):
    """Fixed diameter in px, not an energy or rupture-area measurement."""
    return 3 + 1.3 * max(float(magnitude) - 2, 0) ** 1.7


def annual_counts(df, first_year, last_year):
    return df.groupby(df["time"].dt.year).size().reindex(range(first_year, last_year+1), fill_value=0)


def _event_trace(df, unknown=False, english=False):
    selected = df[df["depth"].isna() if unknown else df["depth"].notna()]
    # External strings are escaped: Plotly hover labels accept HTML.
    from html import escape
    custom = [[row.time.strftime("%Y-%m-%d %H:%M UTC"), escape(row.place),
               row.magnitude, "N/D" if pd.isna(row.depth) else f"{row.depth:.1f}",
               escape(row.mag_type)] for row in selected.itertuples()]
    marker = dict(size=[magnitude_size(m) for m in selected["magnitude"]],
                  opacity=.8, line=dict(color="#502b2a", width=.6))
    marker.update(dict(color="#889392", symbol="diamond") if unknown else
                  dict(color=selected["depth"].tolist(), coloraxis="coloraxis"))
    return go.Scatter(x=selected["longitude"].tolist(), y=selected["latitude"].tolist(),
                      mode="markers", marker=marker, customdata=custom, showlegend=False,
                      name="Earthquakes" if english else "Sismos",
                      hovertemplate=("%{customdata[0]}<br><b>M %{customdata[2]:.1f} (%{customdata[4]})</b>"
                                     "<br>%{customdata[1]}<br>" + ("Depth" if english else "Profundidad") +
                                     ": %{customdata[3]} km<extra></extra>"))


def _annotations(year, count, accumulated, english):
    label = ("cataloged events" if english else "sismos catalogados")
    mode = ("CUMULATIVE" if english else "ACUMULADO") if accumulated else ("THIS YEAR" if english else "EN ESTE AÑO")
    annotations = [dict(x=.025, y=.97, xref="paper", yref="paper", showarrow=False, align="left",
                 xanchor="left", yanchor="top", font=dict(color="#314238", size=16),
                 text=f"<span style='font-size:52px'><b>{year}</b></span><br>"
                      f"{count:,} {label}<br><span style='font-size:11px'>{mode} · USGS</span>"),
            dict(x=.96, y=.96, xref="paper", yref="paper", text="N<br>↑", showarrow=False,
                 font=dict(size=23, color="#314238")),
            dict(x=-77.85, y=-1.5, text="E C U A D O R", showarrow=False,
                 font=dict(size=20, color="#526747")),
            dict(x=-76.3, y=1.8, text="COLOMBIA", showarrow=False, font=dict(size=12, color="#728376")),
            dict(x=-76.7, y=-4.8, text="PERÚ", showarrow=False, font=dict(size=12, color="#728376")),
            dict(x=-82.1, y=-3.8, text="OCÉANO<br>PACÍFICO", showarrow=False,
                 font=dict(size=15, color="#7b9594"))]
    annotations.append(dict(x=1.02,y=.84,xref="paper",yref="paper",text="Depth · km" if english else "Prof. · km",
                            showarrow=False,xanchor="left",font=dict(size=12)))
    for depth in [0,20,70,120,200,300]:
        annotations.append(dict(x=1.055,y=.22+depth/300*.56,xref="paper",yref="paper",
                                text="≥300" if depth==300 else str(depth),showarrow=False,
                                xanchor="left",font=dict(size=11)))
    return annotations


def build_animation(df, first_year, last_year, accumulated=True, english=False, initial_year=None, frame_ms=400):
    initial_year = last_year if initial_year is None else int(initial_year)
    if not first_year <= initial_year <= last_year or not 100 <= frame_ms <= 2000:
        raise ValueError("Invalid initial year or playback speed.")
    fig = go.Figure()
    countries = json.loads((Path(__file__).parent / "assets" / "andes_countries.geojson").read_text(encoding="utf-8"))
    for feature in countries["features"]:
        coords = feature["geometry"]["coordinates"][0]
        fig.add_trace(go.Scatter(x=[c[0] for c in coords], y=[c[1] for c in coords],
                                mode="lines", fill="toself", fillcolor="#ccd4b5" if feature["properties"]["name"] == "Ecuador" else "#e0e3ce",
                                line=dict(color="#7f8c6d", width=1.4), hoverinfo="skip", showlegend=False))
    # Explicit trace slots are essential: empty years must clear old markers too.
    slots = [len(fig.data), len(fig.data)+1]
    initial = df[df["time"].dt.year <= initial_year] if accumulated else df[df["time"].dt.year == initial_year]
    fig.add_trace(_event_trace(initial, english=english))
    fig.add_trace(_event_trace(initial, unknown=True, english=english))
    fig.add_trace(go.Scatter(x=[-78.4678,-79.8891,-79.0045,-79.653], y=[-.1807,-2.1709,-2.9001,.9682],
                            text=["Quito","Guayaquil","Cuenca","Esmeraldas"], mode="markers+text",
                            textposition="bottom right", textfont=dict(size=11,color="#293b34"),
                            marker=dict(size=4,color="#293b34"), hoverinfo="skip", showlegend=False))
    for mag in [4, 6, 8]:
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=f"M {mag}",
                                marker=dict(size=magnitude_size(mag), color="#e9ba7c", line=dict(color="#502b2a",width=1)), hoverinfo="skip"))
    frames = []
    for year in range(first_year, last_year+1):
        selected = df[df["time"].dt.year <= year] if accumulated else df[df["time"].dt.year == year]
        frames.append(go.Frame(name=str(year), traces=slots,
                      data=[_event_trace(selected, english=english), _event_trace(selected, unknown=True, english=english)],
                      layout=dict(annotations=_annotations(year,len(selected),accumulated,english))))
    fig.frames = frames
    immediate = dict(mode="immediate", frame=dict(duration=0,redraw=True), transition=dict(duration=0))
    fig.update_layout(template="none", height=720, paper_bgcolor="#eee9d9", plot_bgcolor="#d6e3e1",
        margin=dict(l=40,r=90,t=40,b=140), font=dict(family="Arial, sans-serif",color="#314238"),
        title=dict(text=("ECUADOR · SEISMIC MEMORY" if english else "ECUADOR · MEMORIA SÍSMICA"),font=dict(size=18)),
        meta=dict(first_year=first_year,last_year=last_year,minimum=df.attrs.get("minimum"),cutoff=df.attrs.get("cutoff"),english=english),
        xaxis=dict(range=[-83,-74.5],fixedrange=True,constrain="domain",dtick=2, ticksuffix="°",showgrid=True,gridcolor="#bacdcb",zeroline=False),
        yaxis=dict(range=[-5.5,2.5],fixedrange=True,constrain="domain",dtick=2,ticksuffix="°",scaleanchor="x",scaleratio=1,
                   showgrid=True,gridcolor="#bacdcb",zeroline=False),
        coloraxis=dict(colorscale=DEPTH_SCALE,cmin=0,cmax=300,showscale=False),
        # A permanent key is independent of whether the current year has points.
        shapes=[dict(type="rect",xref="paper",yref="paper",x0=1.02,x1=1.04,
                     y0=.22+i/60*.56,y1=.22+(i+1)/60*.56,line=dict(width=0),fillcolor=color)
                for i,color in enumerate(sample_colorscale(DEPTH_SCALE,[(i+.5)/60 for i in range(60)]))],
        legend=dict(title="MAGNITUDE" if english else "MAGNITUD",orientation="h",x=.37,y=-.08,itemsizing="trace"),
        annotations=_annotations(initial_year,len(initial),accumulated,english),
        updatemenus=[dict(type="buttons",direction="left",x=0,y=-.13,xanchor="left",yanchor="top",
                         bgcolor="#f8f3e5",bordercolor="#acb99a", buttons=[
            dict(label="▶ Play" if english else "▶ Reproducir",method="animate",
                 args=[None,dict(mode="immediate",fromcurrent=False,frame=dict(duration=frame_ms,redraw=True),transition=dict(duration=0))]),
            dict(label="Ⅱ Pause" if english else "Ⅱ Pausa",method="animate",args=[[None],immediate]),
            dict(label="↺ 1900" if first_year==1900 else f"↺ {first_year}",method="animate",args=[[str(first_year)],immediate])])],
        sliders=[dict(active=initial_year-first_year,x=0,y=-.04,len=1,pad=dict(t=60,b=0),
                      currentvalue=dict(prefix="Year · " if english else "Año · ",font=dict(size=15)),
                      steps=[dict(label=str(year),method="animate",args=[[str(year)],immediate]) for year in range(first_year,last_year+1)])])
    return fig


def export_animation(fig):
    """Embed Plotly so the saved animation has no tile/CDN dependency."""
    from html import escape
    meta = fig.layout.meta or {}
    english = meta.get("english",False)
    guide = """<section aria-label="Map reading guide" style="padding:20px;max-width:900px;margin:auto;font:16px/1.5 Arial;color:#314238">
    <h1>Andes Pulso · Read Ecuador's seismic memory</h1>
    <p><b>1 · Location:</b> a point marks the epicenter, not a damage boundary.
    <b>2 · Size:</b> a larger circle means larger magnitude.
    <b>3 · Color:</b> pale yellow is shallower; darker tones are deeper. Gray diamonds mean unknown depth, not zero.</p>
    <p>Press <b>Play</b>, then <b>Pause</b> and hover over a point. On a phone, tap a point.
    Cumulative traces keeps earlier records; Year by year shows just one year's events.
    These are past records, not ongoing earthquakes.</p>
    <p>Magnitude is earthquake size; intensity describes shaking and effects at a location.
    A larger point or a cluster does not predict damage or the next earthquake.</p>
    </section>""" if english else """<section aria-label="Guía de lectura del mapa" style="padding:20px;max-width:900px;margin:auto;font:16px/1.5 Arial;color:#314238">
    <h1>Andes Pulso · Aprende a leer la memoria sísmica</h1>
    <p><b>1 · Ubicación:</b> el punto marca el epicentro, no un área de daños.
    <b>2 · Tamaño:</b> un círculo mayor indica mayor magnitud.
    <b>3 · Color:</b> amarillo claro indica menor profundidad; tonos oscuros, mayor profundidad. Diamantes grises: dato desconocido, no cero.</p>
    <p>Pulsa <b>Reproducir</b>, luego <b>Pausa</b> y pasa el cursor sobre un punto. En el celular, tócalo.
    Huella acumulada conserva registros anteriores; Año a año muestra solo los de un año.
    Son registros pasados, no sismos que siguen ocurriendo.</p>
    <p>Magnitud es el tamaño del sismo; intensidad es cómo se sintió y sus efectos en cada lugar.
    Un punto mayor o un grupo de puntos no predice daño ni el siguiente sismo.</p>
    </section>"""
    footer = """<footer style="padding:24px;max-width:900px;margin:auto;font:14px/1.6 Arial;color:#314238">
    <b>Andes Pulso · Ecuador continental y margen oceánico</b><br>
    Ventana: 83°–74,5° O / 5,5° S–2,5° N. Incluye países vecinos; no incluye Galápagos.
    Catálogo histórico incompleto. Los conteos anuales no demuestran tendencias físicas;
    los años vacíos no demuestran ausencia de sismos. Magnitudes USGS de distintos tipos,
    no homogeneizadas a Mw. El último año puede estar incompleto.<br>
    Profundidad: escala fija 0–300 km; ≥300 comparte el color final. Diamantes grises: N/D.
    El tamaño del círculo no representa energía ni área de ruptura.<br>
    Fuente: <a href="https://earthquake.usgs.gov/fdsnws/event/1/">USGS FDSN</a> ·
    Made with Natural Earth (dominio público).<br>Henry · Geociencias, Universidad Ikiam.
    No predice sismos ni reemplaza al Instituto Geofísico del Ecuador.<br>"""
    if english:
        footer = """<footer style="padding:24px;max-width:900px;margin:auto;font:14px/1.6 Arial;color:#314238">
        <b>Andes Pulso · Mainland Ecuador and offshore margin</b><br>
        Window: 83°–74.5° W / 5.5° S–2.5° N. Includes neighboring countries, excludes Galápagos.
        Incomplete historical catalog: annual counts alone do not demonstrate physical trends, and empty years do not establish an absence of earthquakes.
        USGS magnitude types are retained, not homogenized to Mw. The latest year may be incomplete.<br>
        Fixed depth scale 0–300 km; ≥300 uses the last color. Gray diamonds: unknown depth.
        Circle size is not energy or rupture area.<br>
        Source: <a href="https://earthquake.usgs.gov/fdsnws/event/1/">USGS FDSN</a> ·
        Made with Natural Earth (public domain).<br>Henry · Geosciences, Universidad Ikiam.
        Does not predict earthquakes or replace Ecuador's Instituto Geofísico.<br>"""
    footer += '<a href="https://www.usgs.gov/programs/earthquake-hazards/science-earthquakes">USGS · concepts</a><br>'
    footer += f"{'Query' if english else 'Consulta'} {meta.get('first_year')}–{meta.get('last_year')} · M ≥ {meta.get('minimum')} · {'UTC cutoff' if english else 'Corte UTC'}: {escape(str(meta.get('cutoff')))}</footer>"
    html = fig.to_html(include_plotlyjs=True, full_html=True, auto_play=False,
                      config=dict(displaylogo=False,responsive=True))
    return html.replace("<body>","<body>"+guide).replace("</body>",footer+"</body>").encode("utf-8")
