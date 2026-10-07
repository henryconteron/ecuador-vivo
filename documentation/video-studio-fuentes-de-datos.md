# Fuentes de datos del Estudio de Video

## Conectores disponibles

| Fuente | Producto que entrega | Periodo/limitación del conector | Uso en el video | Atribución y cautela |
| --- | --- | --- | --- | --- |
| CHIRPS v3 (CHC/UCSB) | GeoTIFF diario recortado a Ecuador continental + Galápagos; paquete ZIP y manifiesto con URL fuente y huella SHA-256 del recorte | 31 días por paquete. `final/rnl` desde 1981; productos diarios `sat` basados en IMERG desde 2001. La publicación preliminar/final tiene latencia distinta. | Se envía directamente al editor como serie ráster; métricas temporales automáticas para precipitación. | El CHC explica que CHIRPS se construye fundamentalmente en pentadas/meses; los productos diarios reparten esos totales con ERA5 (`rnl`) o IMERG Late (`sat`). Las fechas son etiquetas coherentes, no una ventana observada idéntica para todas las estaciones. La versión preliminar puede revisarse. No se descarga el ráster global completo: el ZIP guarda la ventana recortada para Ecuador. |
| NASA POWER | CSV regional original, GeoTIFF multibanda derivado y manifiesto con URL, periodo, resolución nativa y faltantes | Una variable por solicitud; hasta 366 días por paquete. Consulta diaria regional en UTC. | Se envía como variable continua al editor. La tarjeta final de ranking provincial se desactiva por defecto: el grid meteorológico es regional y la interpolación visual no agrega resolución. | Indicar `NASA POWER · NASA Langley Research Center`, código de variable y periodo. Son datos meteorológicos de productos de modelado/reanálisis, no pluviómetros o termómetros INAMHI. El CSV fuente se incluye en el ZIP y su hash queda en el manifiesto. |
| INAMHI | CSV de observaciones diarias de una estación, metadata y ZIP | Consulta de 31 días. El endpoint usado por el visor puede devolver una ventana más corta/reciente o no cubrir el periodo histórico pedido. El panel filtra la respuesta a las fechas solicitadas y enumera faltantes. | Descarga y análisis tabular directo. **No se envía como superficie al mapa**: una observación de estación es un punto, no un promedio provincial ni un campo interpolado. | Citar INAMHI, estación, variable, fecha de descarga y periodo. La API pública no proporciona una bandera de control de calidad en esta consulta ni una licencia explícita dentro de la respuesta; el manifiesto conserva ambas limitaciones. Para histórico ausente, la institución publica el correo `datos@inamhi.gob.ec`. |

Todo lo descargado y sus copias de trabajo se guardan bajo `_local/video-studio/`, que está excluido de Git. El ZIP incluye los archivos usados y `metadata.json`: CHIRPS aporta los GeoTIFF recortados, POWER conserva el CSV fuente y su GeoTIFF derivado, e INAMHI conserva el CSV de observaciones. Los archivos preparados para el editor se guardan por huella SHA-256 para evitar copias redundantes.

## Fuentes nacionales catalogadas para siguientes conectores

Estas instituciones aparecen como enlaces de descubrimiento, no como APIs ya integradas:

- **IGM**: cartografía oficial, catálogo geográfico y servicios interoperables. Antes de automatizar descargas hay que elegir escala/capa y respetar sus términos.
- **IIGE**: geología y energía, metadatos y servicios WMS/WCS. Su licencia permite usos especificados bajo atribución y fecha de descarga; prohíbe desnaturalizar o presentar la información como postura oficial del instituto.
- **IG-EPN**: catálogos sísmicos, acelerogramas, mecanismos focales y señales; las modalidades y formularios dependen del producto.
- **INOCAR**: datos costeros/oceanográficos y consultas de mareas por puerto y fecha; todavía no se automatiza porque no se ha confirmado una API pública estable.
- **IEDG**: catálogo institucional para descubrir geoportales y servicios públicos.
- **Datos Abiertos Ecuador**: catálogo transversal. Cada dataset puede tener formato, licencia, cobertura temporal y actualización distintos.

## Implementación de un nuevo conector

Un proveedor debe registrar (1) endpoint oficial y método de acceso, (2) licencia/atribución, (3) variable/unidades, (4) CRS, resolución espacial y paso temporal, (5) NoData y control de calidad, (6) cobertura y latencia, (7) archivos originales + consulta reproducible, y (8) pruebas offline con respuestas de ejemplo. Solo se habilita “Usar en el editor” cuando la estructura del producto coincide con el renderizador y su significado físico; estaciones puntuales requieren una capa de símbolos por estación, no interpolación silenciosa.

## Referencias oficiales

- INAMHI, [liberación de información hidrometeorológica](https://www.inamhi.gob.ec/info-liberada/) y [visor diario](https://inamhi.gob.ec/ddia/visor).
- Climate Hazards Center, UC Santa Barbara, [CHIRPS v3](https://www.chc.ucsb.edu/data/chirps3), [repositorio oficial](https://data.chc.ucsb.edu/products/CHIRPS/v3.0/) y [FAQ de CHIRPS v3](https://wiki.chc.ucsb.edu/CHIRPS3_FAQ).
- NASA Langley Research Center, [Daily POWER API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/) y [preguntas frecuentes sobre los datos](https://power.larc.nasa.gov/docs/faqs/data/).
- Ecuador, [Geoportal IGM](https://www.geoportaligm.gob.ec/geoportal-igm/), [Geoportal IIGE y licencia de descargas](https://geoportal.geoenergia.gob.ec/), [catálogos del IG-EPN](https://igepn.edu.ec/catalogos-sismicos/formulario-catalogos-sismicos), [consulta de mareas INOCAR](https://www.inocar.mil.ec/mareas/form_mareas.php), [geoportales de la IEDG](https://www.iedg.gob.ec/servicios/geoportales/) y [Datos Abiertos Ecuador](https://www.datosabiertos.gob.ec/).

La consulta vía API del visor de INAMHI se considera una interfaz pública observada, no una API formal con contrato de estabilidad. Si cambia, el panel debe fallar con mensaje visible y conservar la opción de acceso institucional.
