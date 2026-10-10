# SIG-ENGINE-0 — decisión arquitectónica recomendada

Fecha: 2026-10-09. Auditoría y prueba de concepto terminadas; migración de producción pendiente. Evidencia reproducible: `tmp/ecuador-vivo-sig-engine-0-audit.md`. Esta decisión define el camino de SIG-U2; no afirma que el motor nuevo esté integrado.

## Adopción aprobada y evidencia integrada · 2026-10-09

Usuario aceptó esta arquitectura; SIG-U2.0 integrado y funcionalmente validado. El párrafo inicial se conserva como fecha de decisión previa a integración. Estado vigente: checkpoint principal; informe tmp/ecuador-vivo-sig-u20-report.md. OpenLayers10.11.0 retenido/encapsulado, SVG conservado, WebGL con Canvas explícito en fallo/context loss; fuentes/IDs/CRS/science originales, intentos secuenciados y cache íntegra, sin otro reloj/proyecto.

Gate integrado v5000 mediana p95 rAF **16.900 ms**, cumple ≤33; baseline de este corte **83.305 ms** (no mezclar con standalone ENGINE-0). Persistencia v1000 N=10 / sondeo20ms p95 **1202.54 ms**, no cumple ≤500. Equivalencia funcional cerrada, rendimiento de confirmación pendiente. 50 Python + 5 UI posteriores, build/typecheck, 11 Chrome y snapshots/reapertura verificados. Memoria total, rendimiento fallback Canvas y formatos adicionales no demostrados en este corte.

Dependencias distribuidas fijadas/avisos: ol BSD2, rbush MIT, quickselect ISC; sin decoder GeoTIFF beta en build runtime. No distribución pública ni datos personales incluidos. U2.1 plan únicamente; gate persistencia antes de ampliar. Mantener GDAL/GEOS/PROJ y Studio, ninguna sustitución extra por anticipado.

## Decisión

Conservar un proyecto canónico y las transacciones existentes. Mantener Rasterio/GDAL para I/O/ventanas/warps, Shapely/GEOS para geometría e índices y pyproj/PROJ para CRS/mediciones adecuadas. Mantener Studio, sus once plantillas, MapLayerPainter, raster_alpha, bundles/decoder/cache, calendario/CFR, validadores, recibos y exportación existentes.

Adoptar **OpenLayers como SDK de presentación SIG 2D** mediante un adaptador pequeño. Conservar SVG U1 hasta que el consumidor nuevo supere un recorrido integrado equivalente. Separar CRS nativo, CRS de vista y CRS de resultado. No persistir objetos SDK, geometrías reproyectadas de display ni otro documento científico. IDs de selección siempre remiten a las entidades canónicas.

Utilizar fuentes vectoriales retenidas y actualización incremental; WebGL cuando resulte probado para esa capa/dispositivo. La API WebGLVector 10.11.0 tiene advertencia de estabilidad: encapsularla, fijar versión y pruebas; no convertirla en formato de proyecto. Canvas puede servir a capas acotadas; no presentar ese fallback como equivalente de rendimiento ni ampliar el SVG artesanal.

Para el primer ráster SIG-U2, preferir **servicio local de ventanas/teselas RGBA preparado con GDAL y la colorización/NoData existentes**. El original permanece intacto; COG y pirámides son derivados trazables de acceso/display. El cliente no analiza estadísticas sobre overviews. El PoC GeoTIFFSource/WebGLTile demuestra COG directo y reproyección; su dependencia geotiff 3.1.0-beta.0 requiere gate adicional antes de usarla en distribución. No hacer depender U2 del decoder beta ni instalar el build completo con dependencias opcionales innecesarias. Construir los módulos realmente usados y fijar su árbol de dependencias al integrar.

## Evidencia y alternativas

48 casos Chrome, tres rondas rotadas sobre las mismas geometrías, verifican identidad de picking. v5000: mediana del p95 de intervalos rAF, SVG 78.2 ms, OpenLayers Canvas 152.4 ms, OpenLayers WebGL 21.8 ms, MapLibre 17.3 ms. Apertura standalone v5000: 128.0/141.2/298.2/697.7 ms respectivamente. No son FPS físicamente presentados ni latencia total de Streamlit. Memoria registrada, pero heap/RSS acumulados entre páginas no permiten elegir el motor por memoria aislada.

**MapLibre GL JS** es mejor en el workload de cámara medido; worker corregido y promoteId explícito conservan IDs. No se rechaza por los cuatro timeouts iniciales, que fueron errores del prototipo. No se elige como único consumidor universal porque su contrato de display/teselas no equivale a una vista 2D en cualquier CRS. Sería preferible para un producto limitado a Mercator/globo y basemap/MVT. No añadir dos SDKs por anticipado: conservar la opción arquitectónica y exigir necesidad y presupuesto antes de otro consumidor. Referencias: [MapLibre](https://maplibre.org/maplibre-gl-js/docs/), [sources/teselas](https://maplibre.org/maplibre-style-spec/sources/).

**OpenLayers** ofrece el mejor ajuste al alcance inmediato de SIG: vista CRS explícita, fuentes GIS, interacción y ráster; el PoC verifica valores nativos CHIRPS, NoData dentro del lienzo, dos fechas y EPSG:4326→3857. No se anuncia soporte universal de todos los CRS por probar solo dos. [GeoTIFFSource](https://openlayers.org/en/latest/apidoc/module-ol_source_GeoTIFF-GeoTIFFSource.html), [WebGLVector y advertencia de estabilidad](https://openlayers.org/en/latest/examples/webgl-vector-layer.html).

**QGIS** aporta patrones de providers, processing, feedback/cancelación y render jobs; no añadir su GUI/core como runtime obligatorio ni copiar algoritmos GPL. **GeoLibre** aporta una referencia de separación de store/adaptadores/procesamiento; no adoptar su proyecto, UI ni código. **DuckDB Spatial** queda opcional para U3/consultas columnares cuando se pruebe una necesidad; no duplica la ciencia Python ni es requisito de U2. Estas aplicaciones no se benchmarkearon. No crear algoritmos GIS propios.

## Contratos de datos y rendimiento

Fuente original inmutable: hash, CRS/WKT, transform, dimensiones, bandas, dtype, escala/offset, unidades, NoData/máscara, licencia/procedencia y revisiones. Derivado: hash fuente, parámetros/versión del algoritmo, grid/CRS de salida, resampling explícito, máscara, fecha/observación/revisión, clases/paleta. Caché: usuario/autorización y recurso + hashes/revisión + banda + CRS/grid/window/zoom + resampling + estilo/máscara. Límites de memoria/disco y invalidación por cambios; ninguna caché debe obviar la comprobación de integridad o autorización.

Cámara local durante el gesto, transacción al terminar; conservar undo/recovery con comandos versionados y ack. No reconstruir fuente inmutable al cambiar cámara o selección. El perfil actual encuentra dos parseos y reconstrucción de geometrías en operaciones de vista; el SDK no elimina ese coste. Caché de representación validada por contenido es parte del primer corte, sin quitar validación de archivos cambiados.

Vector grande: filtros espaciales/índice, MVT/LOD derivados e IDs estables cuando los límites actuales se superen; elegir generador maduro y fijar licencia antes de añadirlo. No implementado ni medido a escala masiva aquí. Raster grande: ventanas/bloques/overviews, Range 206, caché separada de ciencia. COG comprimido fue más lento para leer la banda completa en el fixture: no recomendar conversión automática de todo archivo.

Temporal: una observación científica identificada por fecha/hash/revisión; el selector SIG consume el calendario existente. Studio conserva su reloj CFR y bindings. Preload/cancelación de display no cambian calendario ni inventan cobertura. Una muestra de dos fechas no valida las 366 fechas ni un nuevo time lapse. La exportación científica no se sustituye por captura WebGL.

## Licencias y distribución

OpenLayers BSD-2-Clause; MapLibre BSD-3-Clause y avisos adicionales incluidos; GeoTIFF.js MIT. Conservar avisos en paquetes/documentación, fijar dependencias reales y crear inventario de componentes/avisos para el build distribuido. Los rangos npm guardados no son un lockfile de dependencias transitivas resueltas. No declarar lista completa de terceros a partir de solo la licencia principal.

GDAL generalmente MIT, con licencias distintas posibles en binarios/driver dependencies; GEOS LGPL, PROJ MIT. Auditar el artefacto distribuido, permitir los derechos que exija LGPL y revisar redistribución de binarios/grids. QGIS GPLv2+ requiere evaluación si se enlaza/copia/distribuye; un subprocess no da una exención automática. [GDAL](https://gdal.org/en/stable/license.html), [PROJ](https://proj.org/en/stable/about.html#license), [GEOS](https://libgeos.org/), [QGIS](https://qgis.org/license/).

Mantener BYOD, fuentes personales fuera del paquete y ejemplos con permisos. Licencia del software, dependencias, grids/basemaps y datasets separadas. Los COG CHIRPS de tmp son privados, no fixtures CC0 ni recursos de distribución. No se incorporó código QGIS/GeoLibre ni SDK nuevo a producción en este corte.

## Migración incremental y gate de SIG-U2

1. **SIG-U2.0 — consumidor retenido equivalente:** introducir OpenLayers tras opción explícita, sobre el mismo payload/catálogo; IDs, huecos/multipartes, pan/zoom/fit, orden/visibilidad/estilo, selección, comandos/undo/save/recovery y navegación SIG↔Studio. Reutilizar validadores/caché por contenido para evitar parseos de cámara. No retirar SVG antes de Chrome integrado y pruebas de persistencia/no parciales.
2. **SIG-U2.1 — fuente ráster real:** extensión aditiva y versionada del catálogo actual (los validadores hoy solo permiten vector/OGC:CRS84), importar un GeoTIFF propio controlado; metadata y rechazo CRS desconocido; ventana RGBA/NoData con GDAL, vista CRS explícita y muestra nativa verificable. No introducir un catálogo paralelo ni publicar ciencia sobre teselas. Compatibilidad v1 demostrada antes del commit del documento.
3. **SIG-U2.2 — nuevos CRS/vector/estilo:** reproyección de presentación explícita, errores fuera del dominio/polos/antimeridiano según capacidades reales, política de resampling y límites de datos. Fijar dependencias/avisos del build; probar WebGL y pérdida de contexto, autorización/rutas y actualización incremental. No declarar todos los formatos ni CRS por tener una librería capaz.
4. U3 tabla ligada/calculadora segura → U4 geoprocesamiento según maestro; U5 calendario y U6 publicación unificada. F01–F25/BYOD permanecen. observation_layers, attach_map_layers y parpadeo continúan abiertos para integración; ningún benchmark los resuelve.

Presupuestos propuestos, **no resultados implementados**: cámara rAF p95 ≤33 ms en fixture v5000 controlado; disponibilidad del mapa caliente ≤2 s para 1000 entidades; cambio de selección/cámara reconocido y persistido p95 ≤500 ms en loopback con fuente validada; límites de RAM explícitos medidos con procesos aislados antes de subir límites. Si el backend sigue tardando segundos, resolver el parseo repetido antes de añadir formatos. Pruebas CI deben contemplar variación; estos valores son objetivos para el corte, no gates ya cumplidos por producción.

Decisiones abiertas de implementación: build/version estable y API WebGL exactos, formatos/codec de tile y servidor local integrado con permisos, cache budget/evicción/integridad, PROJ grids offline permitidos, protocolo selección/tablas y escala masiva/context loss. No cambian la elección de responsabilidades ni obligan a otro modelo/render audiovisual. No se inició SIG-U2 en esta auditoría.


## Continuidad de SIG analítico vectorial · 2026-10-09

El SIG analiza y exporta datos sin requerir video. Operaciones propias usan bibliotecas geoespaciales instaladas y producen derivados verificables dentro del workspace profesional, sin reconstruir Studio. La navegación Inicio→SIG es explícita y vence la cola de Studio; inspector siempre conserva una sección activa. Contratos/evidencia/limitaciones vigentes: tmp/ecuador-vivo-sig-vector-analysis-report.md y checkpoint único. No se cierra el rendimiento, ráster/temporal universal o observation_layers mediante este corte.
