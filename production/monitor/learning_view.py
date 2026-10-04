"""Guided learning, independent of live catalogs, with native Streamlit controls."""
import pandas as pd
import streamlit as st
from education import energy_ratio, depth_band, mainland_time, event_url, depth_svg, subduction_svg

ENERGY_SOURCE = "https://earthquake.usgs.gov/education/how_much_bigger.php"
DEPTH_SOURCE = "https://www.usgs.gov/programs/earthquake-hazards/determining-depth-earthquake"
SCIENCE_SOURCE = "https://www.usgs.gov/programs/earthquake-hazards/science-earthquakes"
ECUADOR_SOURCE = "https://www.igepn.edu.ec/component/fsf/?catid=2.&start=0&view=faq"
INTENSITY_SOURCE = "https://www.usgs.gov/faqs/what-difference-between-earthquake-magnitude-and-earthquake-intensity-what-modified-mercalli?items_per_page=6&page=0"


def text(en, spanish, english):
    return english if en else spanish


def render_map_guide(en=False):
    with st.container(border=True):
        st.markdown(text(en,"**Lee Memoria sísmica · 3 claves**","**Read Seismic memory · 3 clues**"))
        st.markdown(text(en,
            "**1 · Dónde.** El punto marca el epicentro: la proyección en superficie de donde empezó el sismo.\n\n"
            "**2 · Tamaño.** Un círculo mayor significa mayor magnitud, no un área de daño más grande.\n\n"
            "**3 · Color.** Amarillo claro → poca profundidad; tonos oscuros → mayor profundidad. El color no indica peligro. Un diamante gris significa profundidad desconocida.",
            "**1 · Where.** The point marks the epicenter, above where the earthquake began.\n\n"
            "**2 · Size.** A larger circle means a larger magnitude, not a larger damage area.\n\n"
            "**3 · Color.** Pale yellow → shallow; darker tones → deeper. Color is not a danger rating. Gray diamonds mean unknown depth."))
        st.caption(text(en,"Prueba: reproduce → pausa → pasa el cursor sobre un punto. En el celular, toca el punto.",
                             "Try: play → pause → hover over a point. On a phone, tap a point."))


@st.fragment
def magnitude_lab(en=False):
    st.subheader(text(en,"Un número más no es un poquito más","One magnitude step is not a small increase"))
    st.write(text(en,"Compara dos magnitudes ficticias. Esto es una demostración, no una simulación de daños.",
                     "Compare two hypothetical magnitudes. This is a demonstration, not a damage simulation."))
    cols=st.columns(2)
    with cols[0]:
        a=st.slider(text(en,"Sismo A · magnitud","Earthquake A · magnitude"),3.,8.,6.,.1,key="learn_mag_a")
    with cols[1]:
        b=st.slider(text(en,"Sismo B · magnitud","Earthquake B · magnitude"),3.,8.,5.,.1,key="learn_mag_b")
    ratio=energy_ratio(a,b)
    st.metric(text(en,"Energía aproximada de A / B","Approximate energy of A / B"),f"{ratio:,.2f} ×")
    if a == b:
        result=text(en,"A y B tienen la misma magnitud en este ejemplo.","A and B have the same magnitude in this example.")
    elif a>b:
        result=text(en,f"A libera aproximadamente {ratio:,.1f} veces la energía de B.",f"A releases approximately {ratio:,.1f} times B's energy.")
    else:
        result=text(en,f"A libera aproximadamente {100*ratio:.2f}% de la energía de B.",f"A releases approximately {100*ratio:.2f}% of B's energy.")
    st.write(result)
    st.caption(text(en,"Un paso (M5 → M6) ≈ 32 veces la energía; dos pasos (M5 → M7) ≈ 1.000. Es una relación empírica aproximada, no una conversión exacta para todos los tipos de magnitud.",
                         "One step (M5 → M6) ≈ 32 times the energy; two steps (M5 → M7) ≈ 1,000. This empirical approximation is not an exact conversion for every magnitude type."))
    st.info(text(en,"Esto NO significa 32 veces más movimiento en tu casa. La intensidad describe cómo se sintió y sus efectos en un lugar; cambia con la distancia, profundidad, suelo y construcciones.",
                    "This does NOT mean 32 times more shaking at your home. Intensity describes shaking and effects at a location; it varies with distance, depth, soil and buildings."))
    st.caption(f"[USGS · energía y magnitud]({ENERGY_SOURCE}) · [USGS · magnitude / intensity]({INTENSITY_SOURCE})")


@st.fragment
def depth_lab(en=False):
    st.subheader(text(en,"El punto del mapa no es el punto de origen","The map point is not the underground origin"))
    depth=st.slider(text(en,"Mueve el hipocentro · profundidad en km","Move the hypocenter · depth in km"),0,700,100,10,key="learn_depth")
    st.image(depth_svg(depth,en),width="stretch")
    bands={"shallow":text(en,"Superficial · menos de 70 km","Shallow · below 70 km"),
           "intermediate":text(en,"Intermedio · 70 a menos de 300 km","Intermediate · 70 to below 300 km"),
           "deep":text(en,"Profundo · 300 km o más","Deep · 300 km or more")}
    st.write(bands[depth_band(depth)])
    st.caption(text(en,"Esquema vertical, no un corte geológico real. El epicentro queda arriba del hipocentro aunque cambie la profundidad. Aquí usamos 70 y 300 km como inicios de la categoría siguiente.",
                         "Vertical schematic, not a real geological section. The epicenter stays above the hypocenter. Here, 70 and 300 km start the next depth category."))
    st.write(text(en,"La profundidad ayuda a interpretar el origen, pero no basta para calcular lo que se sintió o asignar una falla responsable.",
                     "Depth helps interpret the origin, but cannot alone establish felt shaking or the responsible fault."))
    st.caption(f"[USGS · profundidad]({DEPTH_SOURCE}) · [USGS · epicentro e hipocentro]({SCIENCE_SOURCE})")


# Stable answer IDs allow a language switch without silently changing a chosen answer.
QUESTIONS = (
    ("color",("En Memoria sísmica, un punto oscuro significa…","In Seismic memory, a dark point means…"),
     (("danger",("más peligro.","more danger.")),("depth",("mayor profundidad.","greater depth.")),("size",("mayor magnitud.","larger magnitude."))),"depth",
     ("El color codifica profundidad. No es una escala de daño ni de peligro.","Color encodes depth, not damage or danger.")),
    ("empty",("Un año sin puntos demuestra que…","A year without points establishes that…"),
     (("none",("no hubo sismos.","there were no earthquakes.")),("filter",("no hay registros que cumplan los filtros.","there are no records matching the filters.")),("safe",("el país estuvo libre de riesgo.","the country was risk-free."))),"filter",
     ("El archivo y sus filtros no capturan todos los sismos. Un año vacío no prueba ausencia de actividad.","The archive and filters do not capture all earthquakes. An empty year does not establish an absence of activity.")),
    ("energy",("M6 frente a M5 representa aproximadamente…","M6 compared with M5 represents approximately…"),
     (("double",("el doble de energía.","twice the energy.")),("thirtytwo",("32 veces la energía.","32 times the energy.")),("damage",("32 veces el daño en todas las ciudades.","32 times the damage in every city."))),"thirtytwo",
     ("La energía crece aproximadamente como 10^(1,5 × diferencia de magnitud). Esa relación no calcula daño local.","Energy grows approximately as 10^(1.5 × magnitude difference). This relationship does not calculate local damage.")),
    ("memory",("En Huella acumulada, los puntos que ves…","In Cumulative traces, the visible points…"),
     (("ongoing",("son sismos que siguen ocurriendo.","are earthquakes still happening.")),("past",("son registros hasta el año mostrado.","are records up to the displayed year.")),("future",("indican dónde será el próximo sismo.","show where the next earthquake will occur."))),"past",
     ("La película conserva puntos del pasado. No representa sismos en curso ni predice los próximos.","The film retains past records. It neither shows ongoing earthquakes nor predicts the next ones.")),
)


def reset_quiz():
    st.session_state.pop("learn_quiz_result",None)
    for key,*_ in QUESTIONS:
        st.session_state.pop(f"learn_quiz_{key}",None)


@st.fragment
def quiz(en=False):
    st.subheader(text(en,"Pon a prueba tu lectura","Test your map reading"))
    answers={}
    with st.form("learn_quiz_form"):
        for key,title,options,_,_ in QUESTIONS:
            labels={code:pair[1 if en else 0] for code,pair in options}
            answers[key]=st.radio(title[1 if en else 0],[code for code,_ in options],index=None,
                                 format_func=lambda code,labels=labels:labels[code],key=f"learn_quiz_{key}")
        submitted=st.form_submit_button(text(en,"Revisar mis respuestas","Check my answers"),type="primary")
    if submitted:
        if any(answer is None for answer in answers.values()):
            st.info(text(en,"Responde las cuatro preguntas; puedes probar sin límite.","Answer all four questions. You can try as often as you like."))
        else:
            st.session_state.learn_quiz_result=answers.copy()
    saved=st.session_state.get("learn_quiz_result")
    if saved:
        score=sum(saved[key]==correct for key,_,_,correct,_ in QUESTIONS)
        st.success(text(en,f"{score} de 4 ideas claras. Revisa el porqué de cada respuesta.",f"{score} of 4 correct. Review why each answer is correct."))
        for key,title,_,correct,explanation in QUESTIONS:
            icon="✓" if saved[key]==correct else "↳"
            st.markdown(f"**{icon} {title[1 if en else 0]}**")
            st.write(explanation[1 if en else 0])
        st.caption(text(en,"Resultados de tu última revisión. No se guardan al cerrar la sesión.","Results from your last check. They are not saved after the session closes."))
        st.button(text(en,"Volver a intentar","Try again"),key="learn_quiz_reset",on_click=reset_quiz)


@st.fragment
def event_reader(df,en=False):
    """Interpret a real catalog record. Never invent an intensity or fault assignment."""
    st.subheader(text(en,"Lee un sismo real, dato por dato","Read a real earthquake, one field at a time"))
    options=df.nlargest(12,"magnitude").copy().set_index("id")
    if options.empty:
        return
    selected=st.selectbox(text(en,"Escoge uno de los 12 mayores de tu consulta","Choose from the 12 largest events in your query"),options.index.tolist(),
        format_func=lambda id:f"{options.loc[id,'time']:%Y-%m-%d} · M {options.loc[id,'magnitude']:.1f} · {options.loc[id,'place']}",key="learn_event")
    row=options.loc[selected]
    local=mainland_time(row.time.to_pydatetime())
    st.write(str(row.place))
    left,right=st.columns(2)
    with left:
        st.metric(text(en,"Tamaño del sismo","Earthquake size"),f"M {row.magnitude:.1f} ({row.mag_type})")
        st.caption(text(en,"Magnitud reportada por USGS. No describe lo que sintió una persona.","Magnitude reported by USGS, not what an individual felt."))
    with right:
        st.metric(text(en,"Dónde empezó · profundidad","Where it started · depth"),"N/D" if pd.isna(row.depth) else f"{row.depth:g} km")
        st.caption(text(en,"N/D significa dato desconocido, no profundidad cero.","N/D means unknown, not zero depth."))
    st.write(text(en,f"Hora en Ecuador continental (UTC−5): **{local:%Y-%m-%d %H:%M}** · UTC: {row.time:%Y-%m-%d %H:%M}",
                     f"Mainland Ecuador time (UTC−5): **{local:%Y-%m-%d %H:%M}** · UTC: {row.time:%Y-%m-%d %H:%M}"))
    st.caption(text(en,f"Ubicación del epicentro: latitud {row.latitude:.3f}°, longitud {row.longitude:.3f}°. El nombre cercano no es una delimitación de daños.",
                         f"Epicenter: latitude {row.latitude:.3f}°, longitude {row.longitude:.3f}°. The nearby place name is not a damage boundary."))
    st.info(text(en,"Esta ficha no permite conocer la intensidad en tu ciudad, identificar una falla solo por cercanía ni predecir otro sismo.",
                    "This record cannot establish intensity in your city, identify a fault by proximity alone or predict another earthquake."))
    url=event_url(selected)
    if url:
        st.link_button(text(en,"Consultar registro original USGS","Open original USGS record"),url)


def render_learning(language="ES"):
    en=language=="EN"
    st.caption("ANDES PULSO / AULA ABIERTA" if not en else "ANDES PULSO / OPEN CLASSROOM")
    st.title(text(en,"Entender el pulso.","Understand the pulse."))
    st.write(text(en,"No necesitas saber geología. Mira, prueba y comprueba cómo leer un sismo sin confundir datos con predicciones.",
                     "No geology knowledge needed. Look, experiment and learn to read an earthquake without confusing data with predictions."))
    names={"basics":text(en,"1 · Ecuador se mueve","1 · Ecuador in motion"),"magnitude":text(en,"2 · Magnitud","2 · Magnitude"),
           "depth":text(en,"3 · Profundidad","3 · Depth"),"quiz":text(en,"4 · Tu reto","4 · Your challenge")}
    section=st.segmented_control(text(en,"Ruta de aprendizaje","Learning path"),list(names),default="basics",format_func=names.get,key="learn_section") or "basics"
    if section=="basics":
        st.subheader(text(en,"¿Por qué Ecuador tiene sismos?","Why does Ecuador have earthquakes?"))
        st.write(text(en,"La placa oceánica Nazca se introduce debajo de la Sudamericana: eso es subducción. También existen fallas dentro del continente. Los esfuerzos acumulados pueden liberarse cuando las rocas se deslizan de forma brusca.",
                         "The oceanic Nazca plate descends beneath the South American plate: subduction. There are also faults within the continent. Accumulated stress can be released when rocks slip suddenly."))
        st.image(subduction_svg(en),width="stretch")
        st.caption(text(en,"Esquema simplificado, no un modelo a escala. Los dos puntos ilustran fuentes posibles; no son eventos reales del catálogo.",
                             "Simplified schematic, not a scale model. The two points illustrate possible sources, not real catalog events."))
        st.caption(f"[IG-EPN · por qué se producen sismos en Ecuador]({ECUADOR_SOURCE})")
        render_map_guide(en)
        with st.container(border=True):
            st.markdown(text(en,"**Magnitud ≠ intensidad**","**Magnitude ≠ intensity**"))
            st.write(text(en,"La magnitud describe el tamaño del sismo. La intensidad describe cómo se sintió y sus efectos en cada lugar: un mismo sismo puede tener intensidades distintas en ciudades distintas.",
                             "Magnitude describes earthquake size. Intensity describes shaking and effects at each location: one earthquake can have different intensities in different cities."))
            st.caption(f"[USGS · magnitud e intensidad]({INTENSITY_SOURCE})")
    elif section=="magnitude":
        magnitude_lab(en)
    elif section=="depth":
        depth_lab(en)
    else:
        quiz(en)
    with st.expander(text(en,"Diccionario rápido · sin tecnicismos","Quick glossary · plain language")):
        st.markdown(text(en,
            "**Catálogo:** archivo de eventos registrados; no contiene necesariamente todos los sismos.\n\n"
            "**Epicentro / hipocentro:** punto proyectado en superficie / lugar donde empezó la ruptura.\n\n"
            "**Réplica:** sismo posterior relacionado con un evento principal. Un grupo de puntos por sí solo no lo confirma.\n\n"
            "**UTC:** reloj de referencia. Ecuador continental usa UTC−5; Galápagos UTC−6.\n\n"
            "**N/D:** dato no disponible. No lo interpretes como cero.\n\n"
            "**Mw, mb, ML:** formas distintas de estimar magnitud. Este catálogo conserva el tipo original; no trata sus valores como una serie homogénea.",
            "**Catalog:** archive of recorded events, not necessarily every earthquake.\n\n"
            "**Epicenter / hypocenter:** surface projection / where rupture began.\n\n"
            "**Aftershock:** later earthquake related to a main event; a cluster alone does not establish this.\n\n"
            "**UTC:** reference clock. Mainland Ecuador uses UTC−5; Galápagos UTC−6.\n\n"
            "**N/D:** unavailable data, not zero.\n\n"
            "**Mw, mb, ML:** different magnitude estimates. The catalog retains original types, not a homogeneous magnitude series."))
        st.caption(f"[USGS · conceptos]({SCIENCE_SOURCE}) · [USGS · catálogo](https://earthquake.usgs.gov/fdsnws/event/1/)")
    st.caption(text(en,"Esta aula funciona sin consultar el catálogo. No es una alerta ni un pronóstico. Para información oficial, consulta al IG-EPN.",
                         "This classroom needs no catalog query. It is not an alert or forecast. Refer to IG-EPN for official information."))
    st.link_button(text(en,"Información oficial IG-EPN","Official IG-EPN information"),"https://www.igepn.edu.ec/")
