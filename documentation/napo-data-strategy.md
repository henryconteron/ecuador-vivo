# Prioridad territorial: Tena y Archidona, Napo

Revisión: **30 de septiembre de 2026**. Este informe compara productos y condiciones;
no certifica exactitud local ni convierte un candidato en una capa conectada.
La búsqueda con Exa cubrió 60 resultados solicitados en 12 consultas, agrupadas en
cartografía nacional, alternativas de observación y aplicación/validación local.
Los resultados repetidos y las fuentes secundarias no se trataron como evidencia independiente.

## Decisión

El atlas conserva Ecuador como contexto y añade un encuadre de exploración Tena–Archidona.
Ese rectángulo editorial **no es el límite de la provincia ni de los cantones**, no filtra
el catálogo y no supone mayor precisión. Tampoco debe confundirse la cuenca del río Napo
con la provincia de Napo. Los [GAD de Tena](https://tena.gob.ec/canton-tena/) y
[Archidona](https://archidona.gob.ec/en/informacion-turistica/) son las referencias locales de contexto.

No existe una resolución única adecuada para todo. Una estación es un punto, una hoja
geológica tiene escala cartográfica, un ráster tiene muestreo espacial y cada producto
tiene incertidumbres. Remuestrear AIRS a 30 m solo produciría una apariencia de detalle.

## Fuentes prioritarias y condiciones

| Pregunta | Fuente y detalle publicado | Mejora propuesta | Condición pendiente |
|---|---|---|---|
| ¿Qué rocas y estructuras se cartografiaron? | [IIGE: hojas Tena y Puerto Napo, 1:100.000](https://www.geoenergia.gob.ec/mapas-tematicos-1-100-000/) | Contexto geológico local y consulta a la hoja original | La página prohíbe reproducción sin autorización expresa. No redistribuir PDF, recortes o digitalizaciones sin permiso. Una falla geológica no es necesariamente activa. |
| ¿Qué cartografía oficial y ortofotos cubren la zona? | [IGM: servicios 1:25.000, 1:50.000 y ortofotos](https://www.geoportaligm.gob.ec/portal/index.php/descarga-de-servicios-wms-del-igm/) | Contrastar cartografía base por hoja y adquisición | Verificar cobertura efectiva en ambos cantones, HTTPS, capacidades y condiciones específicas. La ficha de servicios indica CC Attribution-NonCommercial-ShareAlike, sin versión; no asumir dominio público. |
| ¿Cómo cambió el territorio? | [MapBiomas Ecuador: cobertura 30 m](https://ecuador.mapbiomas.org/iniciativas-y-productos/cobertura-y-uso-del-suelo/cobertura-30m/) | Comparar años con la misma colección en recortes cantonales | [Términos CC-BY](https://ecuador.mapbiomas.org/terminos-de-uso/). La web mezcla enlaces de colecciones 3 y 4; fijar el asset y leyenda verificados, no declarar una colección como la última sin comprobarla. |
| ¿Cómo varía la lluvia a largo plazo? | [CHIRPS v3: 0,05°, desde 1981](https://chc.ucsb.edu/data/chirps3), ≈5,6 km cerca del ecuador | Serie mensual, estacionalidad y anomalías con una referencia temporal explícita | Distinguir preliminar/final y validar con pluviómetros locales. Sus variantes diarias se derivan de totales pentadales; no son mediciones independientes de cada día. El productor declara dominio público y proporciona citas de datos y método. |
| ¿Cómo cambia la temperatura del aire? | [ERA5-Land: 9 km nativos, entrega CDS 0,1°, horario desde 1950](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land) | Serie histórica de temperatura a 2 m como complemento al AIRS de 1° | Es reanálisis, no estación ni temperatura superficial de Landsat. No garantiza distinguir ambas ciudades. Verificar términos vigentes del CDS y procesar solo el recorte necesario, sin publicar credenciales. |
| ¿Qué relieve regional puede compararse? | [Copernicus GLO-30: modelo de superficie, 30 m nominales](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM) | Sombreado y perfiles regionales reproducibles | Incluye vegetación e infraestructura. No es un DTM bajo bosque ni sustituye LiDAR o campo para escarpes pequeños. Verificar acceso a teselas y licencia de la instancia concreta antes de redistribuir derivados. |
| ¿Dónde persiste o cambia el agua visible? | [JRC Global Surface Water: Landsat, 30 m](https://global-surface-water.appspot.com/download) | Contexto histórico de agua superficial, no alerta de inundación | Fijar versión. La actualización 1984–2024 combina colecciones Landsat con posibles desplazamientos de registro; historias mensuales/anuales nuevas cubren 2022–2024 y requieren integrar archivos anteriores para una serie completa. Atribuir EC JRC/Google y citar Pekel et al. (2016). |
| ¿Qué caudal modelado tiene un tramo? | [GEOGLOWS: consulta por identificador de río](https://training.geoglows.org/es/rfs/tutorials/query-data/) | Históricos/escenarios modelados para tramos correctamente identificados | No elegir automáticamente el río más cercano: verificar conectividad, versión y contraste con aforos INAMHI. No presentar un pronóstico global como alerta oficial. |
| ¿Qué sismicidad documenta la red nacional? | [Catálogos IG-EPN](https://www.igepn.edu.ec/catalogos-sismicos) | Contrastar sismicidad nacional y eventos locales con USGS | Sus [condiciones de descarga](https://www.igepn.edu.ec/descarga-de-datos) exigen registro y regulan uso y distribución. No aceptar términos en nombre del usuario ni republicar un catálogo sin revisar permiso. |

El [CSV abierto de precipitación INAMHI](https://www.datosabiertos.gob.ec/dataset/precipitacion-total-mensual)
encontrado corresponde a **2019**, con metadata actualizada en 2021: no resuelve por sí solo
el monitoreo actual. La capa de estaciones del atlas contiene ubicaciones y metadatos,
no observaciones. Para calibración local se necesitan las series originales, unidades,
periodos, faltantes y control de calidad de estaciones de la zona.

## Lo que cambia y lo que no

IMERG sigue siendo útil para contexto reciente; CHIRPS añadiría historia y climatología,
no reemplazaría todas sus funciones. AIRS permanece explícitamente regional (1°, ≈111 km).
VIIRS de inundación (250 m) y anomalías térmicas (375 m) conservan sus limitaciones;
el zoom no convierte esas señales en observación por barrio.

Para un estudio de un evento, evaluar radar Sentinel-1 antes/después con procesamiento
y verificación local. En [IW GRD HR](https://sentiwiki.copernicus.eu/web/s1-products),
el espaciado de píxel es 10 × 10 m, pero la resolución publicada es aproximadamente
20 × 22 m: **no anunciarlo como una medición efectiva de 10 m**. Hace falta controlar
geometría, órbita, ruido y relieve; una imagen radar no es automáticamente un mapa validado de inundación.

## Validación: por qué no declarar «el mejor» sin datos locales

La [evaluación en dos cuencas del sur de Ecuador (2026)](https://doi.org/10.1007/s41976-026-00303-1)
encuentra desempeño diferente por régimen, estación y versión, y deficiencias en la variabilidad
intraanual amazónica. No estudia Tena–Archidona ni demuestra que CHIRPS v3 sea superior allí.
Una comparación justa usaría el mismo periodo y variable, estaciones con calidad documentada,
sesgo/error y validación independiente; no calibrar y evaluar con exactamente las mismas observaciones.

## Secuencia de implementación

1. **Hecho en esta revisión:** acceso Tena–Archidona, panel dinámico de resolución/límites,
   distinción de candidatos y plan con procedencia y restricciones.
2. Validar límites cantonales oficiales y una colección fija de MapBiomas; publicar dos o
   tres recortes anuales pequeños, una leyenda y una comparación temporal, no toda la colección nacional.
3. Obtener series INAMHI pertinentes y generar en Python un recorte mensual CHIRPS final
   con periodo/versiones fijos, cobertura de datos y comparación local. Nunca mezclar tasa y acumulado.
4. Preparar temperatura ERA5-Land y relieve Copernicus como contextos separados,
   documentando sus variables y sin remuestreo cosmético que prometa más exactitud.
5. Solo después, desarrollar estudios de eventos con radar, aforos, terreno y evidencia de campo.
   No convertir coincidencias espaciales en causalidad ni en un cálculo de riesgo.

COG/PMTiles externos y series JSON/CSV recortadas mantienen ligero el repositorio.
Ningún acceso requiere incrustar claves en el JavaScript público. Una fuente solo pasará
a `connected` cuando cumpla los criterios de [la red de datos](data-sources.md).
