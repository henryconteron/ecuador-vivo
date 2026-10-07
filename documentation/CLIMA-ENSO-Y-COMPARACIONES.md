# Comparaciones climáticas y ENSO en el Editor de video

Las herramientas de comparación viven dentro de **Abrir editor de videos** →
**Editor** → **Tipo de video: Comparación climática**. No requieren un laboratorio o lanzador separado. Desde
esa sección puedes comparar periodos y territorios, diseñar una maqueta vertical
y exportar el MP4 junto con su CSV y recibo de fuentes.

Consulta de fuentes y prueba inicial: **7 de octubre de 2026**. Las fechas de disponibilidad son las visibles ese día en el catálogo y pueden cambiar con las actualizaciones.

## Pregunta editorial

¿Qué estaba pasando en el Pacífico y qué observamos en Ecuador? Para responder sin atribuir causalidad por coincidencia, conviene enlazar cuatro escalas: índice oceánico (RONI/ONI), mapa de TSM (NOAA OISST), viento (ERA5) y lluvia/temperatura continental (CHIRPS, NASA POWER e INAMHI). Ningún producto por sí solo demuestra que un episodio de lluvia o sequía fue causado por El Niño.

## Fuentes aptas para la maqueta

| Dato | Fuente y cobertura verificada | Uso y cautela |
|---|---|---|
| ENSO | [RONI de NOAA CPC](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/) y [tabla ASCII RONI](https://www.cpc.ncep.noaa.gov/data/indices/RONI.ascii.txt). Serie 1950–2026; anomalía relativa Niño 3.4, promedio móvil de 3 meses. | CPC marca episodio histórico solo si la anomalía supera ±0,5 °C al menos cinco estaciones solapadas; los valores recientes pueden revisarse hasta dos meses. No es una medición local del clima ecuatoriano. La app conserva ONI para continuidad histórica. |
| Temperatura del mar | [NOAA OISST v2.1 en Earth Engine](https://developers.google.com/earth-engine/datasets/catalog/NOAA_CDR_OISST_V2_1). Diaria, 0,25° (~27,8 km), desde 1981; al consultar, llegaba al 4 oct 2026. | Integra satélite, barcos y boyas; interpola huecos. Existen producto preliminar (~1 día) y final (~14 días). En Earth Engine las bandas `sst` y `anom` llevan escala 0,01 y se multiplican por 0,01 para expresarse en °C. |
| Lluvia espacial | [CHIRPS v3 RNL en Earth Engine](https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHC_CHIRPS_V3_DAILY_RNL). Diario, 0,05° (~5,6 km), desde 1981; el catálogo consultado llegaba al 31 ago 2026. | CHIRPS es fundamentalmente pentadal/mensual; la serie diaria distribuye esos totales con precipitación diaria ERA5. La fecha no necesariamente corresponde a una ventana uniforme observada por pluviómetros. Útil para patrón espacial; contrastar con INAMHI. |
| Viento y temperatura del aire | [ERA5 horario en Earth Engine](https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_HOURLY). Grilla ~27,8 km; al consultar, llegaba al 1 oct 2026, 15:00 UTC. | Es reanálisis, no estación: combina modelo y observaciones. Las bandas `u_component_of_wind_10m` y `v_component_of_wind_10m` describen componentes este/norte del viento a 10 m; `temperature_2m` está en K y se convierte a °C restando 273,15. |
| Clima de fondo y comparación | [NASA POWER Daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/), desde 1981, grilla regional de esta consulta 0,5° × 0,625° (~50–60 km). | Cómodo para series comparables de lluvia, temperatura, viento y humedad. No atribuirle escala de barrio; para ciudades se presenta la celda próxima, no una estación ni microclima. |
| Observación local | [INAMHI, visor diario](https://inamhi.gob.ec/ddia/visor) y [aviso de datos de acceso público](https://www.inamhi.gob.ec/info-liberada/). | Estaciones puntuales. Cada estación/variable tiene su propia cobertura; confirmar días faltantes y control de calidad. El endpoint probado no entregó una bandera QC. |
| Contexto del país | [Boletines ERFEN/INOCAR](https://www.inocar.mil.ec/web/index.php/boletines/erfen/boletines-de-prensa) y [Índice Ecuatoriano del Fenómeno El Niño](https://www.inocar.mil.ec/web/index.php/publicaciones/documentos-legales-erfen/638-indice-ecuatoriano-del-fenomeno-el-nino-iefen). | Fuente ecuatoriana para condición y perspectiva. Sus archivos PDF no se convierten automáticamente en una serie numérica hasta transcribir y verificar cada valor. |

## Primer control de datos realizado

- NOAA RONI y ONI descargados desde las tablas oficiales. Última temporada encontrada en la captura: **JAS 2026**, RONI **+1,69 °C** (CPC lo muestra redondeado como +1,7 °C) y ONI **+2,16 °C**. La app debe presentarlos como índices recientes sujetos a revisión, no anunciar automáticamente una clasificación/impacto en Ecuador.
- NASA POWER devolvió **30/30 fechas** para septiembre de 2024 y septiembre de 2026 en los ejemplos de lluvia y temperatura. Para el polígono de Napo, la temperatura media espacial de la grilla fue **15,54 °C** (sep. 2024) y **14,70 °C** (sep. 2026). Para el país, el promedio espacial de precipitación mensual estimado fue **48,70 mm** y **276,17 mm**, respectivamente.
- **Advertencia editorial:** la diferencia de lluvia de NASA POWER es una señal para revisar, no una conclusión. Antes de usarla en un video hay que comparar con CHIRPS v3 (más fino) y las estaciones INAMHI; revisar límites, cobertura y método. Nunca decir “El Niño causó…” solo porque dos curvas coincidan.
- La estación **M1124 SIERRAZUL**, cantón Archidona (Napo), devolvió **25 de 30 días** para precipitación en septiembre de 2026; faltan los días 1–5. Su ZIP conserva la ausencia y la nota de que no hubo bandera de control de calidad; no se inventaron datos.

## Cálculos de la maqueta

- Para precipitación se suma el total diario de cada celda dentro del mes; después se calcula el promedio espacial por el polígono, con ponderación aproximada por área (`cos(latitud)`). La unidad de gráfico es **mm/mes**, no mm/día.
- Para un periodo con varios meses, las provincias solo entran al ranking cuando todos los meses solicitados tienen cobertura completa. La lluvia suma los acumulados mensuales completos (**mm del periodo**); temperatura, viento y humedad promedian las medias mensuales ponderándolas por número de días.
- En CHIRPS el panel permite un mes por consulta (hasta tres años) para evitar descargas prolongadas. CHIRPS y NASA POWER no se mezclan dentro de una misma curva.
- Faltantes se mantienen como faltantes. Cero es una observación, no un sinónimo de “sin dato”.

El video de comparación ahora muestra uno o dos **mapas mensuales**, derivados
de los GeoTIFF originales y con una escala de color fija entre todos los años.
Las líneas de revisión y los rankings quedan como apoyo de cálculo o en el cierre,
no como el cuerpo del video. Los mapas no se reconstruyen a partir de promedios.
Para CSV de registros puntuales o valores provinciales, consulta la
[guía de mapas y CSV](GUIA-MAPAS-Y-CSV-VIDEOS.md).

## Archivos fuente guardados para reproducibilidad

Se creó la carpeta `Datos_Historicos_2026/ENSO_y_comparaciones` en Google Drive. La subida de archivos no se pudo completar desde el navegador disponible, así que la carpeta todavía está vacía. La muestra local está bajo `_local/climate-explorer/samples/` y `_local/video-studio/downloads/`; no está versionada en Git. Cada ZIP conserva `metadata.json` con fechas, escala, unidades, huecos y huellas SHA-256. Para terminar el respaldo, sube desde esas carpetas las dos tablas NOAA, los cuatro ZIP NASA POWER (lluvia/temperatura, septiembre 2024/2026), el ZIP INAMHI de Archidona y este documento. Esta muestra no es un archivo histórico exhaustivo; las series largas se consultan en sus fuentes y no se descargan completas por defecto.

## Citas y licencias

Mantener junto a cualquier mapa/video el nombre del proveedor, identificador/versión, intervalo consultado, resolución, unidad, estadístico, fecha de descarga y enlace de fuente. CHIRPS v3 y NOAA CDR OISST declaran acceso público; para redistribuir datos de estaciones INAMHI, conservar la atribución y verificar los términos vigentes de la institución. Los boletines de INOCAR se citan por documento y fecha.
