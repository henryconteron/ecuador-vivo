# ◒ Andes Pulso — Observatorio sísmico vivo del Ecuador

Aplicación web (Streamlit) para leer la sismicidad reciente desde el territorio de
Ecuador y los Andes del Norte. Combina catálogos en tiempo real (USGS/EMSC), fallas
activas cuaternarias verificadas, distribución 3D de hipocentros, perfiles del
subsuelo, estadística Gutenberg-Richter e índice acumulado de Benioff.

**Andes Pulso** no es un sistema de alerta oficial ni una herramienta de predicción:
es un observatorio abierto para explorar, aprender y comunicar el pulso tectónico del país.

Desarrollado por **Henry** — Ingeniería en Geociencias, Universidad Ikiam.

## Demo en vivo

Pendiente de publicar en Streamlit Community Cloud.

## Qué hace

- Descarga catálogos sísmicos en tiempo real desde **USGS** y **EMSC-CSEM** (FDSNWS).
- Asocia cada evento superficial (≤30 km) con la falla activa mapeada más cercana,
  usando el subconjunto real de Ecuador/Andes Norte de la **GEM Global Active
  Faults Database** (más el proyecto regional **SARA**), no trazas aproximadas a mano.
- Cuando la falla asociada tiene buzamiento reportado, evalúa si la distancia
  epicentro-traza es geométricamente compatible con la profundidad del evento
  proyectada sobre el plano de falla (heurística exploratoria, no un mecanismo focal).
- Estima la magnitud de completitud (**Mc**) por Máxima Curvatura (Wiemer & Wyss,
  2000) en lugar de asumirla igual al filtro de magnitud mínima, y calcula el
  valor **b** de Gutenberg-Richter (Aki, 1965) con su error estándar (Shi & Bolt, 1982).
- Distribución 3D de hipocentros, perfil transversal A-A', evolución espaciotemporal
  animada, curva Gutenberg-Richter e índice acumulado de Benioff (no una medición
  de deformación del terreno ni de energía pendiente de liberar).
- Exporta el catálogo filtrado a CSV.
- Interfaz bilingüe (ES/EN).
- **Aula abierta** sin dependencia del catálogo: subducción explicada con un
  esquema, comparador de energía, epicentro/hipocentro interactivos, glosario y
  reto de cuatro preguntas con explicaciones y reintento.
- **Memoria sísmica de Ecuador:** atlas histórico USGS desde 1900, reproducción
  año a año o acumulada, magnitud por tamaño y profundidad por color, CSV y
  animación HTML autónoma para compartir sin conexión.

## Ver la animación histórica

Con la aplicación en marcha, abre `http://localhost:8501/?view=history` o elige
**Memoria sísmica** en el panel lateral. Pulsa **Reproducir** debajo del mapa;
la línea de tiempo permite saltar a cualquier año. Usa **Año a año** para ver
solo los eventos del año seleccionado o **Huella acumulada** para conservarlos.
El formulario lateral permite cambiar período y magnitud; se aplica con
**Cargar archivo**. La descarga HTML incluye Plotly, el mapa base local y una
guía didáctica de lectura en el idioma elegido.

La guía para aprender está activada de entrada y se puede ocultar. El control
**Año inicial del mapa** abre un año sin obligar a reproducir la película;
**Tiempo para observar cada año** permite un ritmo de 0,4, 0,8 o 1,2 segundos.
La línea de tiempo interna muestra el año de reproducción (el selector externo
solo define el estado inicial). La ficha didáctica interpreta uno de los doce
eventos de mayor magnitud de la consulta sin inventar intensidad o falla causal.

## Aprender sin conocimientos de geología

Abre `http://localhost:8501/?view=learn` o elige **Aula abierta**. Su recorrido es:
Ecuador se mueve → magnitud → profundidad → reto. Las demostraciones son
hipotéticas y los esquemas no están a escala geológica. El comparador utiliza
`10^(1,5 × (MA − MB))` como aproximación de energía; no calcula intensidad,
movimiento en una vivienda ni daños. No aplica una homogeneización de magnitudes
del catálogo. Las fronteras didácticas de profundidad son `<70`, `70–<300` y
`≥300 km`; un valor desconocido no equivale a cero.

Contenido contrastado con [IG-EPN, preguntas frecuentes](https://www.igepn.edu.ec/component/fsf/?catid=2.&start=0&view=faq),
[USGS, ciencia de los sismos](https://www.usgs.gov/programs/earthquake-hazards/science-earthquakes),
[USGS, magnitud y energía](https://earthquake.usgs.gov/education/how_much_bigger.php)
y [USGS, profundidad](https://www.usgs.gov/programs/earthquake-hazards/determining-depth-earthquake).

En el mapa reciente, los grupos de color `≤30`, `>30–70` y `>70 km` son solo
intervalos de visualización, **no regímenes tectónicos determinados**. La columna
heredada `regimen` en el CSV reciente se conserva por compatibilidad, pero ahora contiene
el intervalo de profundidad, no una asignación de subducción o manto.
Profundidades desconocidas se conservan como N/D, no como cero.

Para generar un video vertical MP4 de 1080×1920 a partir del CSV descargado
(exportación opcional, no necesaria para ejecutar la aplicación):

```powershell
python -m pip install -r requirements-video.txt
python export_video.py artifacts/catalog.csv --output artifacts/ecuador.mp4 --first 1900 --last 2026 --minimum 4 --cutoff "CORTE UTC MOSTRADO EN LA APP"
```

La exportación es acumulada, sin audio, a 10 fps y 0,4 segundos por año;
incluye fuente, filtro y limitaciones dentro del video. `--last` puede omitirse
para usar el año actual. Indica el corte original, no la fecha de exportación.

Referencia visual: [reel de @notasdeungeologo](https://www.instagram.com/reel/Dd4-gbFCZV3/),
adaptado a Ecuador a partir de la vista pública y su descripción. No se reutiliza
el video, su catálogo colombiano ni su período de 1644–2026.

La consulta histórica usa el [servicio FDSN de USGS](https://earthquake.usgs.gov/fdsnws/event/1/)
con paginación, corte UTC fijo y un máximo de 6.000 eventos para mantener la
animación manejable. Las consultas mayores se rechazan, no se truncan.
El mapa base es un subconjunto de países de
[Natural Earth 1:110m](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson),
[dominio público](https://www.naturalearthdata.com/about/terms-of-use/).

La ventana regional (83°–74,5° O y 5,5° S–2,5° N) incluye margen oceánico y
países vecinos, **no es un filtro por fronteras y no incluye Galápagos**.
1900 es el inicio de la consulta, no el inicio de la sismicidad ecuatoriana.
El archivo es incompleto históricamente y las magnitudes no están homogenizadas
a Mw. Los conteos por año no prueban tendencias de actividad sin evaluar
completitud. El último año puede estar incompleto; años vacíos son ausencia
de registros que cumplan los filtros, no ausencia de sismos.

## Reel didáctico para Instagram

La exportación de publicación usa un catálogo nuevo y auditado, independiente de
las consultas del navegador. Incluye introducción, leyendas permanentes, puntos
acumulados y límites científicos. La versión revisada añade profundidad y conciencia
sísmica. Formato: 1080×1920, H.264, 30 FPS, 98,8 s, sin
música ni narración. No utiliza el audio ni las imágenes del Reel de referencia.

```powershell
python prepare_reel.py artifacts/reel_ecuador_1900_2025
python reel_video.py artifacts/reel_ecuador_1900_2025
python verify_reel.py artifacts/reel_ecuador_1900_2025
```

Requiere las dependencias opcionales de `requirements-video.txt`. La preparación
consulta 1900–2025, M ≥ 4, en la ventana regional (no por fronteras), conserva
datos originales y verifica conteos, fechas, IDs, coordenadas y dos eventos de
referencia. El CSV y el snapshot se guardan con parámetros y hashes. El verificador
decodifica el archivo completo, cuenta fotogramas y extrae muestras del MP4 real.
El catálogo es incompleto y mezcla tipos de magnitud; no es una serie homogénea de
Mw ni permite comparar actividad por conteos brutos. Antes de subirlo, revisa la
vista previa de Instagram y acompáñalo de las fuentes y límites.

## Fuentes de datos y citas

| Dato | Fuente | Cita / licencia |
|---|---|---|
| Catálogo sísmico | USGS FDSNWS / EMSC-CSEM | Servicios públicos en tiempo real |
| Fallas activas | GEM Global Active Faults Database + SARA | Styron, R., & Pagani, M. (2020). *The GEM Global Active Faults Database.* Earthquake Spectra, 36(1_suppl), 160–180. https://doi.org/10.1177/8755293020944182 — CC-BY-SA 4.0 — https://github.com/GEMScienceTools/gem-global-active-faults |
| Cartografía base | OpenStreetMap, OpenTopoMap, Esri | Atribución in-app en cada capa |
| Volcanes | Smithsonian Global Volcanism Program | Coordenadas de referencia |

## Metodología y limitaciones (léelo antes de citar resultados)

- **Asociación epicentro-falla:** es una heurística de distancia geodésica al
  trazo mapeado más cercano en superficie, con una verificación adicional de
  consistencia geométrica cuando hay buzamiento reportado. **No reemplaza**
  una inversión de mecanismo focal ni un relocalización de hipocentros.
  Solo ~42% de los segmentos de falla en la región tienen buzamiento en el
  catálogo fuente; el resto se reporta como "N/D".
- **Mc / valor b:** con catálogos cortos (ventanas de pocos días/semanas) el
  estimador de Máxima Curvatura y el ajuste MLE de Aki tienen alta incertidumbre;
  se requieren ≥5 eventos sobre Mc para reportar un valor.
- **Cobertura de fallas:** el dataset local (`ecuador_active_faults.geojson`)
  está filtrado a la ventana Ecuador/Andes Norte. Para las regiones "Eastern Pacific
  (Americas)" y "Global" la capa de fallas se deshabilita — no se muestran datos
  inventados fuera de esa cobertura.
- **Energía liberada:** conversión estándar log10(E)=4.8+1.5M (Gutenberg-Richter,
  1956); es una aproximación de orden de magnitud, no una medición instrumental.

## Estructura del proyecto

```
monitor-sismos/
├── app.py
├── seismology.py
├── historical.py                     # catálogo paginado y animación cartográfica
├── history_view.py                   # vista Memoria sísmica
├── education.py                      # cálculos y esquemas didácticos
├── learning_view.py                  # Aula abierta y guías de lectura
├── export_video.py                   # exportación opcional a MP4 vertical
├── requirements-video.txt
├── assets/andes_countries.geojson     # Natural Earth, dominio público
├── requirements.txt
├── ecuador_active_faults.geojson       # subconjunto real de GEM GAF-DB + SARA
├── tests/
│   ├── test_seismology.py
│   ├── test_historical.py
│   ├── test_education.py
│   └── test_video.py
└── README.md
```

## Correr localmente

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
streamlit run app.py
```

Pruebas:

```bash
python -m unittest discover -s tests -v
```

## Reel educativo para Instagram

La edición actual, con mapa primero y la voz de ElevenLabs aportada por el autor,
usa `reel_voice.py`:

```powershell
.\venv\Scripts\python.exe reel_voice.py artifacts/reel_ecuador_1900_2025_v6 --dynamic
.\venv\Scripts\python.exe verify_reel.py artifacts/reel_ecuador_1900_2025_v6
.\venv\Scripts\python.exe audit_publication.py artifacts/reel_ecuador_1900_2025_v6
```

La carpeta v6 conserva `voz_elevenlabs_original.mp3`, el catálogo auditado y
`audio_cues.json` (cambios de tema en segundos). Se mantiene la toma completa a
velocidad original; solo se añade silencio al final para leer los créditos.
Si cambia la grabación, hay que revisar los tiempos antes de volver a exportar.
La verificación decodifica el MP4 completo y compara la voz codificada con el original.
La auditoría de publicación recalcula las cifras desde el GeoJSON y contrasta
los valores científicos con una nueva consulta USGS. También comprueba 2026
por separado: esos registros **no** forman parte del video cerrado en 2025.
Se incluyen descripciones para Instagram y TikTok, referencias y notas de
etiquetado de voz sintética/licencia. La v6 muestra el crédito completo:
«Henry Conteron, ingeniero en geociencias e investigador independiente».
La edición dinámica usa `reel_motion.py` y `reel_captions.py`: planos breves
para posición/magnitud/color, revelados ligados a la voz y subtítulos con palabra
activa dentro de una franja reservada. Incluye `subtitulos.srt` y tiempos en JSON.
Los tiempos de reconocimiento local son aproximados; se revisa la ortografía y
las cifras contra el guion. Los puntos, colores y escalas científicas no se
animan ni deforman. Las ediciones v4/v5 permanecen guardadas; omite `--dynamic`
para reproducir el montaje de tarjetas anterior.

La versión v3 con narración del sistema sigue disponible con `reel_editorial.py`:

```powershell
.\venv\Scripts\python.exe reel_editorial.py artifacts/reel_ecuador_1900_2025_v3
.\venv\Scripts\python.exe verify_reel.py artifacts/reel_ecuador_1900_2025_v3
```

La narración usa PowerShell 7 (`pwsh`) y la voz española instalada Microsoft Pablo.
Para exportar en otro equipo sin esa voz, añade `--silent`. El guion queda en
`narration.json`, y `visual_sin_audio.mp4` permite grabar una voz propia.
La duración se adapta a la locución sin cortarla. El crédito de esta edición es
el indicado en `reel_design.py`; los archivos de versiones anteriores se conservan.

`reel_video.py` exporta una selección previamente auditada por `prepare_reel.py`.
Incluye explicación de profundidad, proyecciones laterales y preparación sísmica.
No representa una predicción ni un mapa de daños; las proyecciones no identifican fallas.

Para reproducir la versión revisada con su catálogo guardado:

```powershell
.\venv\Scripts\python.exe reel_video.py artifacts/reel_ecuador_1900_2025_v2
.\venv\Scripts\python.exe verify_reel.py artifacts/reel_ecuador_1900_2025_v2
```

La carpeta contiene MP4, descripción para Instagram, revisión científica y metadatos.
Los datos de entrada deben conservar su hash; el exportador rechaza modificaciones
no auditadas. La versión anterior permanece en `artifacts/reel_ecuador_1900_2025`.
La versión v2 no añade audio. Ninguna versión se publica automáticamente.

### Serie territorial: Tena/Napo y Nororiente de 1987

El plan y los guiones están en `artifacts/serie_memoria_sismica/`. El primer
capítulo comienza directamente con el mapa USGS de Napo y su entorno:
consulta 1900–2025, magnitud publicada ≥4, 347 registros y localidades de
referencia. El primer registro disponible es de 1927; no es historia completa.
Después pregunta por 2026 y cambia explícitamente de fuente para mostrar
**dos eventos diferentes** mediante sus boletines revisados del 16/06 y
19/08/2026, cerca de Tena. Acerca la vista a Tena y explica qué es una falla.
El mapa destaca 1987; el segundo capítulo profundizará en sus efectos. No es un catálogo completo
ni un ranking. Los tipos de magnitud, coordenadas y profundidades conservan lo
publicado; el exportador vuelve a compararlos con el HTML fuente guardado.

```powershell
.\venv\Scripts\python.exe prepare_territory.py
.\venv\Scripts\python.exe prepare_napo_history.py
.\venv\Scripts\python.exe prepare_napo_fault.py
.\venv\Scripts\python.exe prepare_napo_catalog.py
.\venv\Scripts\python.exe reel_napo_catalog.py artifacts/serie_memoria_sismica/01_napo
.\venv\Scripts\python.exe verify_napo_catalog.py artifacts/serie_memoria_sismica/01_napo
```

La descarga prepara evidencia pública y cartografía geoBoundaries con
procedencia, licencias y hashes. Los límites representan 2011 y se usan como
referencia visual, no como cartografía catastral vigente ni para delimitar daños.
La exportación produce **una maqueta silenciosa marcada NO PUBLICAR**, un
storyboard y cuadros de revisión. Añade `--storyboard-only` para omitir el MP4.
El montaje vigente V5 abre directamente en el mapa histórico, marca localidades
con rombos GeoNames, pregunta por 2026, acerca la vista a Tena y explica una
falla mediante bloques 3D: normal, inversa y desgarre, con capas que realmente
se desplazan y 30 imágenes de movimiento por segundo. No repite magnitud y
profundidad ni inventa una traza local. Ver `01_napo/MAPA_1900_FALLAS_V5.md`.
Faltan nueva voz del autor, sincronización y subtítulos antes del video final.
El guion de 1987 tiene revisión científica y administrativa, pero aún no montaje.
Las fechas del plan son objetivos editoriales: no se ha programado ni publicado
contenido en ninguna cuenta.

### Siguiente reel: profundidad y daños

Orden editorial actualizado: atlas nacional → profundidad/daños → Tena/fallas.
La V2 abre en los perfiles Oeste–Este y Sur–Norte del video publicado (snapshot
USGS idéntico), pregunta qué significan, compara fuentes hipotéticas a 500,
150 y 10 km con cámara fija en perspectiva y muestra fotos históricas verificadas
de Pedernales y del río Monjas. El piedemonte de 1987 usa un esquema original.
No se confunde profundidad con peligro ni casos reales con un experimento.

```powershell
.\venv\Scripts\python.exe prepare_depth_episode.py
.\venv\Scripts\python.exe audit_depth_v2.py
.\venv\Scripts\python.exe reel_depth_damage_v2.py --storyboard-only
.\venv\Scripts\python.exe reel_depth_damage_v2.py
.\venv\Scripts\python.exe verify_depth_v2.py
.\venv\Scripts\python.exe -m unittest tests.test_depth_episode tests.test_depth_v2 -v
```

Artefactos: `artifacts/serie_memoria_sismica/00_profundidad_danos/`.
Maqueta V2 silenciosa de 155 s, no publicable. V1 conservada como antecedente.
En esta selección, máximo 254 km: el ejemplo de 500 km es solo hipotético.
Ficha vigente: `CORTES_Y_PROFUNDIDAD_V2.md`. Texto: `guion_elevenlabs_v2.txt`.
Fotos y montaje visual CC BY-SA 2.0;
antes de incorporar voz, leer `MEDIA_Y_PERMISOS.md`: no prometer reutilización
comercial del audio ElevenLabs gratuito bajo esa licencia. Guion listo para
grabar; faltan sincronización, subtítulos y revisión final del archivo con voz.
No se modificó el atlas publicado ni se programó ninguna publicación.

La **V3 de referencia** añade el guion completo con Microsoft Helena Desktop
(es-ES), sintetizada localmente, y un relieve 3D propio para explicar el
deslizamiento y posible flujo del piedemonte. Ajusta los tiempos al audio
sin cortar frases (unos 2:46). No consume créditos ni requiere complementos
nuevos; conserva V1/V2. Continúa marcada **NO PUBLICAR**: voz provisional,
sin subtítulos finales ni autorización final del audiovisual con esa pista.

```powershell
.\venv\Scripts\python.exe reel_depth_damage_v3.py --storyboard-only --regenerate-voice
.\venv\Scripts\python.exe reel_depth_damage_v3.py
.\venv\Scripts\python.exe verify_depth_v3.py
```

Video: `profundidad_danos_voz_provisional_v3.mp4`, en la misma carpeta de
artefactos. Ficha: `VOZ_Y_PIEDEMONTE_V3.md`. El modelo de ladera es conceptual,
no topografía observada, simulación física ni reconstrucción de 1987.

La **V4 para revisión** conserva el inicio, sustituye los ejemplos hipotéticos
principales por Bolivia 1994, Loreto 2019 y Pedernales 2016, e incorpora efectos
documentados, Pelileo 1949 y un nuevo piedemonte 3D con cámara móvil.
Voz local provisional con marcas de palabra y guion original (aprox. 3:44).
Bolivia y Loreto son casos adicionales fuera del catálogo inicial, no puntos
añadidos a sus cortes. Informes primarios congelados y fuentes históricas
contrastadas visualmente. No modifica V1–V3 ni el atlas publicado.

```powershell
.\venv\Scripts\python.exe prepare_depth_story_v4.py
.\venv\Scripts\python.exe reel_depth_damage_v4.py --storyboard-only --regenerate-voice
.\venv\Scripts\python.exe reel_depth_damage_v4.py
.\venv\Scripts\python.exe verify_depth_v4.py
```

Carpeta: `artifacts/serie_memoria_sismica/00_profundidad_danos/v4/`.
Guion: `guion_elevenlabs_v4.txt`. Criterio narrativo, fuentes y límites:
`CRITERIO_EDITORIAL_Y_FUENTES.md`. Sigue siendo vista previa **NO PUBLICAR**;
requiere voz final con permisos compatibles, subtítulos y escucha humana.

La **V5** añade un guion reestructurado desde el gancho inicial, demostraciones
de ondas P, S, Love y Rayleigh, partícula trazadora y ampliación del movimiento.
Render 3D local por GPU (ModernGL), no imágenes de ondas generadas ni registros
del terremoto. Subtítulos provisionales con marcas de palabra, incrustados y SRT.
Casos históricos y catálogo preservados. Sigue marcada **NO PUBLICAR** hasta
voz definitiva con derechos compatibles, resincronización y revisión humana.

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-seismic-3d.txt
.\venv\Scripts\python.exe prepare_depth_story_v5.py
.\venv\Scripts\python.exe reel_depth_damage_v5.py --storyboard-only --regenerate-voice
.\venv\Scripts\python.exe reel_depth_damage_v5.py
.\venv\Scripts\python.exe verify_depth_v5.py
```

Carpeta `artifacts/serie_memoria_sismica/00_profundidad_danos/v5/`:
`guion_elevenlabs_v5.txt`, `DIRECCION_CREATIVA_V5.md`, auditoría de fuentes,
storyboard, vídeo y avance de ondas. Depende de GPU local compatible OpenGL
3.3; no instala software a nivel de sistema, abre ventanas ni usa servicios de pago.

### Video de ríos · NDWI y observaciones reales de 2026

Se añade una pieza educativa de teledetección independiente de la sismicidad,
manteniendo el formato vertical y el diseño de la serie. Compara adquisiciones
individuales del 11/07/2019 y 29/07/2026 en cuatro ventanas cercanas a Tena:
entorno urbano, Jatunyacu, Napo y Puerto Misahuallí. No pretende cubrir toda la
provincia, cuantificar minería, contaminación ni migración validada del cauce.

Fuentes gratuitas: Copernicus Sentinel-2 / Element 84 Earth Search. Se conserva
QA local, calibración radiométrica, hashes y una comprobación de píxeles contra
la colección nueva; no se lanzan exportaciones adicionales en Earth Engine.
El video incluye voz de sistema sintética de referencia, sin servicios de pago.
La vista previa requiere revisión y alineación final de subtítulos antes de publicar.

Método, limitaciones, reproducción y fuentes: [NAPO_NDWI_VIDEO.md](NAPO_NDWI_VIDEO.md).
Artefactos locales: `artifacts/rios_napo_ndwi_2026/` (ignorados por Git).
Los videos y audios anteriores no se sobrescriben.

La versión ampliada añade **08/08/2024**, compara **NDWI / MNDWI** a la misma
cuadrícula de 20 m y explica el cálculo con un píxel real. MNDWI se usa como
lectura principal de estos cauces amplios, acompañado de RGB/NDWI, sin afirmar
exactitud superior universal. Conserva la primera vista previa.
Método, límites y reproducción: [NAPO_RIOS_INDICES_V2.md](NAPO_RIOS_INDICES_V2.md).
Artefactos: `artifacts/rios_napo_indices_v2/`, ignorados por Git.

La nueva pieza **Un río, tres preguntas (v4)** distingue agua, lecho expuesto y
sedimentos, compara NDWI/MNDWI/AWEI sin declarar un ganador local, e incluye
RGB/NDVI/NDTI y las adquisiciones reales de 2019/2024/2026. Conserva todos los
videos anteriores. Guion propio con estructura de pregunta, prueba y explicación;
no copia voces ni guiones de otros canales. La vista previa requiere revisión.
[Método, fuentes y entregables](NAPO_RIOS_METODOS_V4.md).
Artefactos locales: `artifacts/rios_napo_metodos_v4/`, ignorados por Git.

## Desplegar gratis en Streamlit Community Cloud

1. Sube esta carpeta a un repositorio de GitHub (público o privado).
2. Entra a https://share.streamlit.io con tu cuenta de GitHub.
3. "New app" → selecciona el repo, la rama y `app.py` como archivo principal.
4. Deploy. Streamlit instala `requirements.txt` automáticamente.
5. Copia el link resultante y agrégalo arriba, a tu CV y LinkedIn.

## Próximos pasos sugeridos

- Módulo de caso de estudio con datos propios (tomografía sísmica, fotogrametría)
  de un sistema de falla específico.
- Estereonet interactivo para cinemática de fallas (rumbo/buzamiento/cabeceo).
- Calculadora simple de intervalo de recurrencia a partir de altura de escarpe
  y tasa de deslizamiento.
