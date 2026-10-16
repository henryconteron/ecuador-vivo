# SIG · adaptación de GeoLibre y RustGIS · 15 octubre 2026

## Contrato de este incremento

Objetivo: potenciar el SIG propio sobre el motor OpenLayers existente. No sustituirlo por otra aplicación ni degradar su serie científica y puente a Studio. La lectura de repositorios públicos es análisis de fuente; no se presenta como decompilación ni como prueba de rendimiento ejecutada. La skill REA recomienda no usar analizadores de binarios para esta situación.

Mapa persistente y dominante. Mantener la identidad vigente de expedición: azul tinta #132b46, controles #203e59, jade #80d8c3, papel #fff5df y Segoe UI para controles. Nada de clonar marcas, llenar la cinta de funciones sin implementar o duplicar el editor de propiedades.

Primera entrega verificable: buscador de comandos reales (Ctrl+K), historial separado de encuadres, medición local de longitud/área. El buscador activa controles existentes; las medidas son bocetos de vista con aproximación esférica, no resultados analíticos, y no se incorporan a los cálculos, proyectos ni videos. Historial acotado por instancia; no comparte memoria entre proyectos. Al desmontar se liberan mapa, eventos e interacciones de dibujo.

Estos gestos de presentación no descargan rasters ni vuelven a ejecutar análisis. Los cambios de encuadre siguen usando el protocolo existente de guardado; no se promete eliminar sus reruns o haber medido FPS. No cambiar la fuente, resolución, CRS, NoData, máscara, escalas temporales o procedencia científica para lograr una vista más fluida.

## Referencias y licencias

- [GeoLibre](https://github.com/opengeos/GeoLibre): MIT, copyright Qiusheng Wu 2026.
- [RustGIS](https://github.com/opengeos/RustGIS): Apache-2.0; revisar también ATTRIBUTION.md antes de reutilizar componentes.

Este incremento implementa patrones propios, sin incorporar código de esos repositorios. Si se reutilizan partes posteriormente, conservar licencia y avisos aplicables; reescribir nombres no elimina esas obligaciones. No se ha instalado ninguno de los dos programas dentro del SIG.

## Fuentes fijadas y alcance de la auditoría

Lectura de fuente y contratos, no benchmark de las aplicaciones de referencia:

- GeoLibre 3.4.0: commit `5e8da6e91122565c9a8891a4e79a7fd215873adf`.
- RustGIS 0.2.0: commit `3f9437739babf6b334e9cef77fa56eb95142992f`.
- Copias de referencia separadas de producción en `_local/maintenance/revisiones-20261015/referencias-sig/` (ubicación consolidada). No se instalaron ni ejecutaron esos programas ni sus dependencias.
- No se utilizó REA contra binarios: hay código fuente suficiente para la pregunta. No es un proceso formal de clean room ni elimina obligaciones de licencia.

### GeoLibre: patrones reutilizables, no un catálogo prometido

1. **Separación de estado, motor y capacidades.** El [contrato del motor](https://github.com/opengeos/GeoLibre/blob/5e8da6e91122565c9a8891a4e79a7fd215873adf/packages/map/src/map-engine.ts#L19) y `renderer-capabilities.ts` permiten varios renderizadores; no todas las funciones funcionan en todos ellos. Zustand/zundo concentra estado e historial en `packages/core/src/store.ts`. En Ecuador Vivo conviene mantener OpenLayers detrás de su adaptador existente, no acoplar el documento científico a una interfaz de otro programa.
2. **Paneles diferidos y retenidos.** [MountWhenOpened](https://github.com/opengeos/GeoLibre/blob/5e8da6e91122565c9a8891a4e79a7fd215873adf/apps/geolibre-desktop/src/components/layout/MountWhenOpened.tsx#L4) monta al abrir y conserva después. La sincronización de capas compara cambios y evita reemplazos innecesarios (`packages/map/src/layer-sync.ts:430`). Es un patrón que debemos medir contra nuestros reruns, no prueba de que nuestra app ya sea igual de rápida.
3. **Tiempo como propiedad de la capa.** [temporal-layers.ts](https://github.com/opengeos/GeoLibre/blob/5e8da6e91122565c9a8891a4e79a7fd215873adf/packages/plugins/src/plugins/temporal-layers.ts#L5) separa fechas disponibles, selección y enlace persistente. `maplibre-time-slider.ts:700` limita actualizaciones a 150 ms, deduplica índices y encola por capa. Debemos conservar fechas reales y reemplazar peticiones obsoletas, no copiar sin límite una cola que pueda atrasarse. `time-slider-symbology.ts` actualiza paleta, bandas, rango y NoData sin cambiar de fuente.
4. **Carga por ventana, caché y trabajo fuera del hilo principal.** `cog-imagery.ts:10` comparte promesas por URL y elimina fallos de caché; `geojson-vt-protocol.ts` usa worker de teselado vectorial; [vector-tool-runner.ts](https://github.com/opengeos/GeoLibre/blob/5e8da6e91122565c9a8891a4e79a7fd215873adf/packages/processing/src/vector-tool-runner.ts#L66) gestiona worker, reutilización y cancelación. No se han integrado en esta entrega.
5. **Registro de herramientas y fuentes organizado.** `packages/processing/src/types.ts` define parámetros/contexto/cancelación; el registro básico no equivale a todos los adaptadores del programa. `apps/geolibre-desktop/src/lib/ui-profile.ts:39` y `AddDataMenu.tsx` separan archivos, servicios, nube, 3D y bases de datos, filtrados por capacidades. Aplicable a nuestro catálogo únicamente cuando haya un lector o servicio operativo detrás.

### RustGIS: qué explica su interacción y qué no

1. **Comandos con disponibilidad y ejecución controlada.** [engine/src/lib.rs](https://github.com/opengeos/RustGIS/blob/3f9437739babf6b334e9cef77fa56eb95142992f/crates/engine/src/lib.rs#L30) define ID, etiqueta, grupo, parámetros, atajo y mutación. `Session::run` valida disponibilidad, conserva snapshots y restaura ante error; historial acotado a 40. Nuestro buscador reutiliza los botones actuales; aún no sustituye el registro de operaciones de Python.
2. **Interacción antes de render caro.** [mapview.rs](https://github.com/opengeos/RustGIS/blob/3f9437739babf6b334e9cef77fa56eb95142992f/crates/ui-egui/src/mapview.rs#L285) transforma la textura previa mientras se navega y espera 180 ms de quietud antes de renderizar completamente; usa claves de revisión/cámara/tamaño y limita refrescos de teselas. El dibujo GIS usa tiny-skia CPU y una textura presentada por egui: no corresponde decir que todo su SIG es GPU ni que Rust por sí solo resuelve nuestra latencia.
3. **Presupuestos explícitos.** `crates/tiles/src/cache.rs` limita caché a 160 MiB web / 384 MiB nativo, con 8 trabajadores nativos y cola acotada. `crates/map/src/source.rs` limita consultas por ventana. `crates/tiles/src/cog.rs` usa HTTP Range y overviews, no exige descargar cada ráster completo. Son referencias de diseño, no umbrales adoptados sin medir nuestro equipo/datos.
4. **Interpolación visual no es detalle científico nuevo.** `crates/render/src/raster.rs` distingue bilineal para continuo y vecino próximo para categorías, con tratamiento de muestras ausentes. El mesh de proyección de pantalla no aumenta resolución original. Debemos preservar categorías, máscara, NoData y resultados nativos.
5. **No confundir animación de cámara con serie científica.** [view.rs](https://github.com/opengeos/RustGIS/blob/3f9437739babf6b334e9cef77fa56eb95142992f/crates/map/src/view.rs#L136) define keyframes de centro/escala/segundos. Su exportación de animación nativa genera PNG/ZIP con límites; no reemplaza nuestro timelapse fechado, sus métricas ni el video vertical de Studio. Algunos lectores GDAL son nativos y no están disponibles en WASM. Tampoco todos sus análisis son asíncronos.

## Matriz de adaptación

| Capacidad | Ecuador Vivo antes de este incremento | Estado de esta entrega |
|---|---|---|
| Mapa persistente y paneles flotantes | Adaptador OpenLayers/CCv2 y ventanas existentes | Conservados, sin cambio de motor ni de marca |
| Búsqueda de herramientas | Botones distribuidos en cinta | Añadido Ctrl+K, búsqueda sin tildes, teclado y filtrado de comandos no disponibles |
| Historial de vistas | Deshacer del proyecto, sin historial local separado | Añadido anterior/siguiente; máximo 40 encuadres por instancia/proyecto |
| Medición interactiva | Sin boceto local dedicado | Distancia y área esféricas, unidades m/km y m²/km²; no analíticas ni exportables |
| Vectorial, ráster, CRS y procedencia | Operaciones propias en Python y capas derivadas | Preservados; no se importó un catálogo ficticio de cientos de herramientas |
| Serie temporal, paleta y puente a Studio | Implementación propia con observaciones/fechas | Una capa lógica para el calendario activo, observaciones desplegables y visibilidad conjunta; paleta/fecha/puente conservados |
| Autoguardado al navegar | Evento de vista al terminar gesto, procesado por Python | Cámara inmediata; solo los encuadres aún no enviados se agrupan tras 400 ms de quietud; confirmación previa a acciones. Persiste mediante Python, no elimina todos los reruns |
| COG remoto por ventana / índices espaciales grandes | No se acreditó equivalencia | Pendiente de integración y benchmark |
| Trabajos analíticos cancelables, catálogo unificado de capacidades | No equivalente al registro de ambas referencias | Pendiente; requiere contratos, errores y pruebas, no solo botones |
| Globo 3D, GDAL web, bases espaciales, edición vectorial general | Sin paridad acreditada | Fuera de esta primera entrega |

## Decisión de integración

Conservar OpenLayers y el documento científico existente. La alternativa de instalar GeoLibre o portar RustGIS completo introduce otro modelo de proyecto, motores de render, dependencias y límites web/nativo; no resuelve automáticamente nuestros reruns y arriesga la transferencia ya construida. Se adopta comportamiento compatible en incrementos comprobables.

La medición vive en una capa temporal independiente, se limpia al salir/cambiar de proyecto/desmontar, pausa reproducción y evita que un clic de dibujo consulte o seleccione un dato. Está deshabilitada para una vista temporal prerenderizada cuya imagen no representa una superficie georreferenciada interactiva. No modifica el registro canónico de capas.

El buscador usa texto seguro y activa controles existentes: no duplica análisis, importa datos ni ejecuta scripts de usuario. El historial de encuadres es local y distinto del deshacer del documento; restaurar un encuadre sigue el guardado vigente. No se cambiaron cálculos, datos nativos, videos, pilotos ni formatos exportados.

## Primer incremento: implementación y verificación histórica

- Nuevos `map-interactions-model.ts`, `map-actions.ts`, `map-actions.css` y `test-map-interactions.mjs` bajo `production/video_studio/ecuador-vivo-sig-map/ecuador_vivo_sig_map/frontend/`.
- Adaptador `src/index.ts` conecta medición, historial y liberación. `src/workbench.ts` añade tres glifos propios. Registro Python y Vite apuntan a `sig-workbench-v5.js/css`; versiones anteriores no son el punto de entrada activo.
- TypeScript y build de producción aprobados; bundle principal 532,79 kB / gzip 154,37 kB, CSS 34,85 kB / gzip 7,41 kB. No se añadieron dependencias.
- **24 pruebas Node aprobadas**, incluidas cinco nuevas: historial/copia/ramificación, límite/validación, búsqueda con tildes, navegación de teclado y medición geográfica conocida (1° ecuatorial ≈111.195 m; cuadrado 1° ≈12.363,7 km²). La revisión detectó y corrigió el índice de ↑ desde el buscador: el test reprodujo `2 !== 3` con la fórmula original, y pasó tras corregir la condición inicial. Este contraste también prueba que la regresión no queda silenciosamente verde.
- **21 pruebas Python aprobadas**: `test_sig_workbench_design`, `test_sig_map_ui`, `test_sig_interaction_performance`, `test_sig_series_activation`, `test_sig_protocol`. Prueban contratos y regresiones focalizadas, no todo el catálogo ni todas las plataformas.
- Instancia local 8534 iniciada con autorización. Revisión real en navegador integrado, viewport normal 1280×720 y mapa nuevo, sin modificar los pilotos: búsqueda `area` sin tilde encuentra medición de área; polígono terminado muestra ≈27.177,99 km²; Escape limpia; zoom habilita anterior; volver/avanzar restaura escala; Ctrl+K, búsqueda `distancia` y Enter activan medición; línea terminada muestra ≈242,72 km y Salir limpia. Son bocetos de prueba, no mediciones de un territorio oficial.
- Captura real: `_local/maintenance/revisiones-20261015/referencias-sig/sig-medicion-verificada.jpg` (ubicación consolidada).
- Tras recompilar y recargar, reabrir el mapa de comprobación y buscar `medir`, ↑ enfoca correctamente «Medir área», el último de dos resultados. Escape cierra y devuelve el foco a Comandos. No se observaron errores de consola con URL de origen local entre los 20 errores recientes consultados; esto no equivale a una auditoría global de consola/red.
- El autoguardado creó un «Mapa sin título» de comprobación; se conserva y no se borró ningún proyecto. Reabrir desde Inicio pasa por Studio y volver a SIG recupera las referencias y el encuadre. No se modificó un piloto para esta prueba.
- No se midieron FPS, latencia extremo a extremo ni pico de memoria; no se ejecutaron las apps de referencia. La reproducción temporal y transferencia conservan pruebas de regresión, pero no se verificó en esta pasada un nuevo timelapse real en el navegador.
- Sin commit/push/publicación, limpieza destructiva ni cambios de licencia del proyecto. El árbol de trabajo ya contenía cambios extensos del usuario: no restaurarlos ni atribuirlos a esta entrega.

## Segundo incremento: cámara diferida y serie lógica · implementado

### Contrato

Conservar el mapa dominante, los paneles flotantes y el lenguaje visual existente. Agrupar únicamente las observaciones del calendario activo como una capa lógica; las fechas permanecen accesibles y no se eliminan registros. Visibilidad compartida en una transacción, sin recalcular valores ni modificar fuentes, métricas o escenas. Cámara local inmediata y persistencia tras 400 ms de quietud; nunca quitar ni renumerar comandos ya enviados. Al abrir herramientas, guardar o navegar, confirmar primero el último encuadre en el mismo evento. Rechazar acciones obsoletas ante cambios externos. Verificar con pruebas focalizadas y revisión real, sin afirmar mejoras de FPS o memoria sin medición.

### Cambios y comprobaciones

- `deferred-view.ts` conserva el último encuadre no enviado, copia defensivamente coordenadas, deduplica, libera temporizadores y respeta comandos numerados en tránsito. Las confirmaciones antiguas no fuerzan ajuste sobre una cámara pendiente. Restaurar una vista externa permite guardar después un encuadre anteriormente aceptado.
- Las acciones de interfaz llevan los gestos pendientes en el mismo evento. `prepare_ui_event` valida su versión, aplica la cadena de gestos primero y actualiza la versión de la acción; rechaza repetición obsoleta tras cambios externos. No hay nueva fuente de verdad ni renumeración de comandos emitidos.
- `series-tree-model.ts` / `layer-tree.ts` presentan el calendario activo como una capa lógica. «Observaciones» crea las filas al desplegar o buscar, mantiene fechas reales y permite seleccionar cada una. El interruptor conjunto usa una transacción canónica y conserva fuentes, calendario, métricas y originales. Las capas fuera del calendario mantienen sus grupos.
- Registro activo actualizado a **sig-workbench-v6.js/css** para evitar usar el bundle anterior en caché. TypeScript/build aprobados: JS 537,07 kB / gzip 155,51 kB; CSS 35,44 kB / gzip 7,52 kB. Sin dependencias nuevas.
- **31 pruebas Node aprobadas**: las 24 previas más cinco de cámara y dos de agrupación. La prueba de copia defensiva detecta la mutación temporal `latest=box` (99 frente a 0), restaurada después. La prueba real detectó `Illegal invocation` al llamar temporizadores del navegador con el modelo como receptor; se reprodujo con una prueba roja específica y se corrigió envolviendo las llamadas. Suite y navegador volvieron a pasar.
- **33 pruebas Python focalizadas aprobadas**: diseño (4), interacción/rendimiento (4), activación (5), protocolo (5), visibilidad conjunta (1), mapa/AppTest (6) y serie/transferencia (8). Cubren la confirmación de cámara antes de guardar, duplicados/cambios externos, conservación científica, series genéricas y transferencia; no son la suite completa del proyecto.
- QA real en 8534 con copia de un borrador existente, sin modificar pilotos: 30 fechas de precipitación de septiembre. En v6 corregido, **tres zooms consecutivos produjeron un único guardado de cámara**, versión 0→1, misma instancia OpenLayers y 30 capas construidas antes/después. No implica una medición de FPS, RAM o latencia extremo a extremo.
- La lista pasó de 30 filas abiertas a **1 capa lógica · 30 fechas**. Desplegar conserva las 30 filas; buscar `2026-09-15` y seleccionarla activa índice 14. Ocultar toda la serie oculta la leyenda y volver a mostrarla la restaura. Viridis se aplica conservando fecha 15 y rango 0–86 mm/día; se restauró la paleta Ecuador Vivo. Cambiar paleta aún reconstruye 30 capas de presentación: optimización posterior, no ocultar este coste.
- Reproducción real avanzó del día 15 al 28 localmente manteniendo versión 6; pausar confirmó la fecha. Zoom seguido inmediatamente de Guardar terminó en estado guardado (versión 9), mismo mapa y 90 construcciones acumuladas —las 60 adicionales fueron los dos cambios de paleta, no el zoom—. El encuadre quedó en `[-82.06981481765835,-3.27696,-74.43018518234165,-0.12304]` antes de ajustar todo para la captura.
- Capturas fuera de producción en la carpeta de auditoría: `sig-serie-antes.jpg` y `sig-serie-agrupada-v6.png`. Las copias de comprobación/autoguardados se conservan; no se borraron proyectos. La instancia se reinició tras comprobar ausencia de renders y respondió health `ok`.
- Acabado comprobado a 1280×720; Capas se puede reducir y mover con teclado para no tapar el reloj. Tras la corrección, no aparecieron errores con origen local posteriores a 15:53:30 UTC entre los 20 errores recientes consultados. Las advertencias 403 de telemetría del controlador del navegador son externas a Ecuador Vivo; no se eludieron protecciones. Reejecución final conjunta: 31 Node y 33 Python en verde, TypeScript y revisión de espacios en diff aprobados.
- Las fuentes, cálculos, CRS, NoData y máscara no fueron sustituidos para suavizar la interacción. No se ha renderizado un video nuevo ni cronometrado una transferencia pesada en esta pasada; se conservan pruebas de regresión del puente.

## Siguiente secuencia pendiente

1. Medir duración de gesto, actualización de fecha, reruns, bytes leídos y RAM en series y vectores grandes. Optimizar cambios de paleta sin reconstruir todas las capas de presentación.
2. Unificar descriptores de herramientas, disponibilidad por tipo de dato y fuentes reales; ejecutar análisis largos como trabajos con progreso/cancelación y resultados derivados atómicos. No mostrar herramientas sin implementación.
3. Integrar lectura COG por ventanas/overviews e índices para vector grande si los benchmarks justifican el coste. Presupuestos de caché explícitos. Globo/3D opcional después, sin reemplazar el SIG 2D científico ni Studio.
