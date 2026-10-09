# Ecuador Vivo Studio: tareas

## Corte vigente 4b.3b · reserva de cuota · 2026-10-08

- [x] Núcleo implementado: instancias/bindings, reloj CFR existente, mapas RGBA + fecha protegida + leyenda estática verificada; preview/export/receipt, caché y persistencia/duplicación/clipboard.
- [x] Cierre automatizado: 87 OK, 157.849 s (12 nuevas + regresiones), tmp/studio2-4b3b-final-tests-v1.log; MP4 real y PNG exactos, ciencia intacta. Suites parciales anteriores solapadas.
- [ ] Cerrar 4b.3b: export/reproducción Chrome por documento JSON estructurado. Apertura/fecha/seek/hold/tres tamaños comprobados, pero dos timeouts esperando diálogo Exportar MP4. v1 Deploy interceptó el clic; v2 viewer elimina Deploy, posible rerun pendiente de diagnóstico. NO declarar terminado ni empezar 4b.4a.
- [x] Checkpoint reproducible guardado con archivos, evidencias, fixture permanente, servidores propios y comando de reanudación. Leer el bloque vigente superior del checkpoint; no repetir SIG/G1/4b.0–3a.

Lo inferior documenta el estado anterior. F01–F25/BYOD y recursos personales conservados.

## SIG + STUDIO · prioridad operativa vigente · 2026-10-08

Chrome de runtime final: 6 checks/42.841 s/MP4/visibility actual OK, `tmp/sig-g1-current-runtime-browser.log`; evidencia vigente `tmp/sig-g1-browser.json`. Servidor propio 8516 launcher 13092; próximo 4b.3b.

Cierre G1 adicional: 9 GeoJSON + 19 timeline = 28 OK, 5.854 s; receipt comprueba binding real/visibilidad/ausencia de capa eliminada. Export final 183 frames sin cálculos, `tmp/sig-g1-validation.json`. Decoder tiene 8 tests propios al cerrar su guarda de publicación; suites abajo se solapan, no sumarlas como distintas.

- [x] SIG-0: acceso a SIG/Studio directo sobre proyecto compartido, preparación/resultados científicos reales y retorno conservando documento/historial. Alcance ECU actual, no SIG universal.
- [x] SIG-1: enviar revisión o mapa temporal 4a a escenas persistentes por APIs existentes/commit; reintento idempotente, perfil compartido, undo/recovery/MP4 y ciencia intacta. 6 nuevos tests OK + 39 regresiones OK; Chrome final 6 checks/MP4 real/tres viewports OK, `tmp/sig-studio-first-browser.json`.
- [x] 4b.2: bundle privado RGBA sellado/thumbnail/hashes/calendario/progreso/cancelación y budgets efectivos, sin publicación ni cambio schema. 15 ejecutados: 14 OK + 1 omitido por WinError 1314 (symlink); 4 regresiones v1 OK. Evidencia `tmp/studio2-4b2-validation.json`. 4b.0/4b.1 intactos, SIG aún 4a opaco.
- [x] 4b.3a: decoder interno por observación/LRU acotado, AssetFrames.map_at y budgets conjuntos, sin publicar campos nuevos. 7 tests OK + 29 regresiones (28 OK y 1 omitido symlink). Serie 32 observaciones/cache dos tiles, sin benchmark RSS.
- [x] SIG-G1: GeoJSON RFC7946 Polygon/MultiPolygon 2D → región por ID/CRS → vista RGBA → Studio/MP4/reopen, fuera de bbox ECU con atributos/originales exactos/procedencia/licencia. 8 nuevos + 38 regresiones = 46 OK; Chrome final 6 checks/40.194 s/tres tamaños/MP4 OK. No reproyección/estadísticas universales; antimeridiano/polos/tipos no soportados rechazados. Evidencia `tmp/sig-g1-browser.json`.
- [ ] 4b.3b siguiente exacto: reloj/bindings/renderer/fecha/leyenda compartidos; luego 4b.4a/4b.4b publicación/gestos y overlays/crop. Multimedia/clips/audio 5–7 por dependencias.

Guarda final privada: 35 tests (8 decoder + 8 GeoJSON + 19 timeline), 19.228 s, OK; validate_export impide publicar kind=temporal_map sin renderer/reloj. Se solapan con suites anteriores, no sumar como nuevos.

Registro vivo F01–F25/BYOD: `tmp/ecuador-vivo-sig-studio-implementation-plan.md`; checkpoint actualizado. La autorización nueva supera las restricciones históricas de sesiones cerradas inferiores. Sin commit/push/reset/clean ni borrados personales.

## STUDIO 2.0 · trabajo actual · 2026-10-08

- [x] Especificación completa y UTF-8 verificados: secciones 1–21 + RESULTADO ESPERADO, 36.301 bytes, sin caracteres de reemplazo; estado de Git y checkpoint reconstruidos. No repetir auditoría científica ni UX cerrado.
- [x] Incremento 0: dependencias/contratos y plan incremental registrados; autorización del usuario para implementar y continuar automáticamente. No modificaciones destructivas ni revisión externa opcional.
- [x] Incremento 1a: reparación de alta tabular y metadata de productos exportados, con RED/GREEN y validación de las rutas existentes.
- [x] Incremento 1b: documento/identidad/revisión canónicos y proyección legacy explícita; navegación/guardado/recovery atómicos.
- [x] Incremento 2: inicio profesional, recientes y creación libre/template; acceso explícito a preparación de datos existente.
- [x] Incremento 3 completo: asistente/resultados y escenas científicas vinculadas automáticamente; regeneración explícita con diferencias.
  - [x] 3a: fábrica desde CalculationResult existentes, acción real «Crear proyecto en Studio», regeneración de escena con diferencias, conservación de versión y undo; Chrome/worker validados.
  - [x] 3b: asistente desde Inicio, worker privado con progreso/cancelación, revisión verificable y publicación explícita al mismo Studio. 53 focalizados OK y 7 checks Chrome/MP4 reales; detalles en checkpoint.
  - [x] 3c: regeneración de estructura completa, diferencias, conservación explícita de escenas editadas, archivo/recuperación y undo/redo canónico. 6 tests propios dentro de 59 focalizados finales OK; Chrome con MP4 real.
- [ ] Incremento 4: recurso temporal lógico, calendario, continente/Galápagos y overlays progresivos.
  - [x] 4a: puente prerenderizado real desde `data.load_values`/`render.compose`, manifiesto fecha–fotograma/fuente/banda/hash/revisión, recurso lógico único y escena mediante commit/autosave existentes; calendario común para decoder, trim/loop/hold, preview y recibo de exportación. Suite completa 350 OK antes de la última guarda de revisión; 9 cartográficas finales OK después; Chrome final 7 checks/MP4 real. No se declara edición cartográfica plena.
  - [ ] 4b: capas RGBA/máscaras de continente y Galápagos con geometría independiente y calendario compartido; overlays independientes realmente renderizables.
  - [x] 4b.0: riesgo NoData continental reproducido RED (clip/ventana) y corregido mediante alfa común finito × máscara geográfica; cero y negativos válidos/costas intactos. Fixture sintético de ambas regiones, fechas 1/3 de enero y ausencia del inset en la segunda; PNG RGBA sobre dos fondos y resúmenes nativos inmutables. 5 nuevos + 8 regresiones focalizadas OK.
  - [x] 4b.1: tiles RGBA locales continent/galapagos con bbox/grid/CRS constantes y una observación científica común, usando painter compartido con maqueta. NoData/inset ausente transparentes, fuentes/revisión/bandas verificadas, CRS nativo y resultados intactos. 9 nuevos tests OK y 8 comparaciones exactas de píxeles/layout legacy; sin UI/publicación de capas todavía.
  - [x] 4b.2: bundle privado sellado con progreso/cancelación/manifiesto/thumbnail, validado en continuación SIG vigente; 14 OK + 1 omitido, 4 regresiones v1 OK. Sin publicación de capas todavía.
- [ ] Incremento 5: biblioteca/importación múltiple de imagen/video/audio, metadatos y gestión segura.
- [ ] Incremento 6: clips/pistas renderizables, move/trim/split, selección/snap/huecos y compatibilidad.
- [ ] Incremento 7: narración/música/SFX independientes, envolventes y forma de onda, mezclador existente.
- [ ] Incremento 8: navegación, inspector, preview/entrega y recuperación integrados.
- [ ] Incremento 9: suite, Chrome, flujos científicos/libres, recursos/rendimiento y refinamiento.

Checkpoint 4a (2026-10-08): **350 tests, 211.926 s, OK**, `tmp/studio2-temporal-full-final-tests.log`. Después de la guarda que reconstruye cada revisión original y verifica también sus CalculationResult: **9 tests, 13.947 s, OK**, `tmp/studio2-temporal-revision-final-tests.log`; próximo discovery 351, no declarado ejecutado. Chrome final **7 checks**, `tmp/studio2-temporal-browser.json` / `tmp/studio2-temporal-browser-sealed.log`: preparación/cancelación, revisión sin publicar y reapertura, un recurso lógico con miniatura, escena real, playhead/fecha, MP4/recibo/autosave y tres viewports sin overflow. Fixture GeoTIFF sintético de dos bandas con fechas 1 y 3 de enero; sus resultados de navegador proceden de capture_snapshot/SummaryAccumulator existentes. Siete cuadros, intervalos [0,3) y [3,7); no fecha interpolada para el 2. Unit tests comparan índices y bytes decodificados en trim/loop, hold, corrupción, revisión, guardado/undo/recovery y compatibilidad de fuentes nuevas con mapas antiguos. Mutación en copia en memoria detectada, `tmp/studio2-temporal-mutation-final.log`, fuentes intactas. Primer discovery falló al inspeccionar una función AppTest mientras se editaba su archivo; repetición estable OK. Reintentos Chrome por sincronización del arnés conservados, no sumar sus checks. Checkpoint vigente: siguiente **4b**, sin iniciar. Sin commit/push ni borrado; tmp/_local/untracked conservados.

Checkpoint 1a: RED inicial 5 casos y RED adicional de estado JSON inválido; GREEN **49 tests, 25.184 s, OK** (`tmp/studio2-foundation-tests.log`). Incluye worker real y comparación preview/MP4. Chrome local 8513: **3 checks OK** (`tmp/studio2-foundation-browser.json`): abrir copia científica, insertar tabla con `value=null`, exportar/reproducir. Captura `tmp/ux-redesign/studio2-tabular-1366.png` inspeccionada. Los tres exportadores declaran nombre/MIME/hash; fallback explícito para receipts antiguos. La inserción conserva su posición inicial y puede requerir recolocar elementos superpuestos; no se afirma cierre UX 2.0.

Checkpoint 1b: **53 tests focalizados, 18.382 s, OK** (`tmp/studio2-project-compatibility.log`); cuatro casos nuevos RED/GREEN más regresión de cambio de revisión de widgets. Chrome **5 checks OK** (`tmp/studio2-document-browser.json`): rename, Datos y retorno al mismo documento/historial, tres tamaños sin overflow horizontal. Capturas `tmp/ux-redesign/studio2-document-*.png`. El proceso de prueba se reinició al cambiar firmas Python; el primer intento usó un módulo importado anterior y no se cuenta como validación. Documento único `project_document`, namespace aditivo `project_meta`, proyección legacy sin Studio; guardado/exportación JSON completos. No se retira el rechazo del exportador legacy a escenas libres. Archivos guardados se abren como copias. Autosave del workspace publica después del preflight/guardado; edición de Datos conserva su guardado explícito hasta el asistente.

Checkpoint 2: creación libre/template e inicio integrado; **3 tests RED/GREEN, 1.236 s, OK**, más regresión RED/GREEN de recientes legacy. Chrome **7 checks OK** (`tmp/studio2-home-browser.json`): nuevo inicio, crear YouTube libre, texto/autosave, Inicio/Studio con historial y tres tamaños. Capturas `tmp/ux-redesign/studio2-home-*.png`, `studio2-free-*.png`, inspeccionadas. Recientes y abrir/importar conservan archivos originales; JSON no empaqueta medios. Los controles nativos instalados usan React Aria, no BaseWeb: el verificador se corrigió por inspección DOM, sin hacks CSS en producto. Datos científicos abre la adquisición existente; asistente/generación corresponde al incremento 3, todavía pendiente.

Checkpoint 3a: fábrica y UI conectadas desde Maqueta → Visualizaciones → Cargar resultados científicos → Crear proyecto en Studio. Fixture CHIRPS v2 existente de un día produce **8 escenas** con métricas/gráfico/créditos y bindings; no inserta un mapa temporal automáticamente. Regeneración de escena propone antes/después, requiere reemplazo explícito, archiva versión anterior y permite cancelar/undo; no regenera aún la estructura completa. **5 tests de ciencia, 2.726 s, OK** tras RED de hash Unicode y pérdida de bindings; **64 focalizados, 32.417 s, OK** (`tmp/studio2-science-focused.log`). Chrome final: **9 checks OK** (`tmp/studio2-science-browser.json`), exportación/reproducción worker real de las ocho escenas acortadas a 0.1 s cada una. Capturas `studio2-generated-1920.png`, `-1366.png`, `-768.png`; las de 1366 y 768 inspeccionadas al cierre.

Consolidación Studio 2.0: suite completa final **325 tests, 348.856 s, OK** (`tmp/studio2-full-tests-final.log`), anterior al último arreglo de navegación diferida. Después: **8 tests focalizados, 0.856 s, OK** (`tmp/studio2-navigation-queue-green.log`) y los 9 checks Chrome científicos. No se afirma una nueva suite completa de 326 tests. Chrome exitoso acumulado: **24 checks** (3 + 5 + 7 + 9), sin sumar las validaciones históricas. Primera suite: 322 tests, cuatro errores de entrada legacy tras introducir Inicio; se adaptó únicamente la entrada por «Montaje anterior», cuatro regresiones OK y suite final OK. Error real de Streamlit al modificar `studio_phase` después de instanciar el widget corregido con cola consumida antes de crear widgets. No hay una regresión reproducida que siga abierta en estos incrementos.

Límites abiertos: asistente integral y publicación de preparación científica; mapas lógicos/calendario y Galápagos independiente; importación múltiple/audio autónomo; clips y pistas reales; regeneración de estructura; paquete portátil y matriz completa A–F. JSON conserva referencias locales. Cambios estéticos no reemplazan revisiones científicas. Un intento Chrome con propuesta de 48 s excedió el timeout del arnés; el worker terminó, pero eso no acredita rendimiento final. La prueba corta posterior pasó. Sin auditoría científica histórica repetida ni dependencias nuevas.

**DETENCIÓN SOLICITADA POR EL USUARIO · cambio de cuenta:** operación segura en curso finalizada; no iniciar otro incremento. Traspaso: `tmp/ecuador-vivo-studio-2-checkpoint.md`; informe: `tmp/ecuador-vivo-studio-integration-report.md`. Git revisado: 23 archivos tracked modificados, 687 inserciones/180 eliminaciones, además de numerosos untracked previos y nuevos; el stat no representa solo Studio 2.0. No descartar ni limpiar. Diff check previo OK; comprobación final documental registrada en el checkpoint. Sin commit/push/reset/clean ni eliminación de archivos.

**Siguiente pendiente exacto: incremento 4.** 3b/3c terminados en la reanudación autorizada: asistente privado, revisión/publicación explícita y estructura regenerable con diferencias/archivo/recuperación. Suite **341 tests, 468.943 s, OK**, antes del último arreglo de reconstrucción y la guarda de cambio de fuente; después **59 focalizados, 12.461 s, OK**, incluida nueva regresión de puntero real de procedencia (próximo discovery: 342). No afirmar otra suite completa final. Chrome de estructura registra los checks del asistente y regeneración sin sumarlos dos veces; detalle en checkpoint e informe. No empezar 4 en este cierre. Historial anterior conservado abajo.

Cierre Chrome sobre código final: **12 checks OK**, `tmp/studio2-structure-browser.json` / `tmp/studio2-science-structure-browser-final.log`; incluye los 7 checks de asistente ya registrados y 5 adicionales de estructura, no 19 nuevos. Dos MP4 reales de 0.8 s: generación inicial y estructura regenerada con edición humana conservada. Tres viewports, unidades/bindings/revisión/datasets guardados y ausencia de excepciones JS. Captura `studio2-structure-diff.png` inspeccionada; también revisión 1366 y 768. Git diff/whitespace/documentos UTF-8 comprobados al cierre. No repetir auditorías ni los incrementos cerrados.

Checkpoint 4b.0 (2026-10-08): **5 tests nuevos, 0.658 s, OK** (`tmp/studio2-4b0-final-tests.log`) y **8 regresiones seleccionadas, 0.253 s, OK** (`tmp/studio2-4b0-regression-tests.log`), 13 distintos. RED del compositor real conservado en `tmp/studio2-4b0-red.log`: faltante continental opaco en recorte y ventana, corregido solo en la pintura; estadísticas/resampling/costas finitas intactos. Checker de planificación Windows verificado mediante `tmp/studio2-4b-planning-error-check.py`, nueve hashes de 4a intactos. Sin suite general ni Chrome/UI nueva. Siguiente **4b.1**, no iniciado; los bloques «sin iniciar 4b» anteriores son historial superado por este cierre parcial.

Checkpoint 4b.1 (2026-10-08): **9 tests nuevos, 4.134 s, OK**, `tmp/studio2-4b1-final-tests.log` (solo MapTileTests; no repetir los 13 de 4b.0), y **8 comparaciones RGB/layout exactas OK**, `tmp/studio2-4b1-legacy-compatibility.json`. Tres fuentes funcionales: maqueta.py (helpers compartidos), studio_map_layers.py (adaptador privado), test_studio_map_layers.py (tests nuevos). PNG sintéticos y trazabilidad en `tmp/studio2-4b1-tiles/` / `tmp/studio2-4b1-tile-artifacts.json`. CRS proyectado, categorías, min-island/NoData/halo, grid fijo, fechas con huecos, integridad científica y fallback provincial cubiertos. Sin bundle/media/schema/reloj de Studio/Chrome/MP4 nuevos; siguiente **4b.2**, no iniciado. Logs de fixtures fallidos conservados. Fuente categórica sin métricas del test usa dataset canónico explícito; no se implementó otra publicación categórica. Checkpoint vigente actualizado; bloques anteriores son historial.

## CHECKPOINT ESTABLE ACTUAL · rediseño UX/UI completo · 2026-10-08

- [x] Reconstrucción del código y baseline real: **285 tests OK, 244.201 s**, `tmp/ux-redesign-baseline-tests.log`; capturas previas Chrome 1920×1080, 1366×768 y 768×1024 en `tmp/ux-redesign/before-*.png`. No auditoría científica repetida.
- [x] Incremento 1: cinco regiones en un CCv2 aislado; `5 · Estudio` abre el workspace antes de formularios/sidebar legacy. Shell dentro del viewport en los tres tamaños, sin overflow horizontal global ni excepciones JS. `shell.json`, `after-shell-*.png`; spec/decisión de arquitectura en `documentation/ECUADOR-VIVO-STUDIO-UX.md`.
- [x] Incremento 2: zoom/pan/fit/guías/snapping, drag/resize reales, teclado, selección múltiple, undo/redo y guardado de gestos. Lifecycle del ShadowRoot corregido para evitar handles/listeners duplicados. Atomicidad ante seek inválido reproducida RED y corregida. `after-interactions-1366.png`, `interactions.json`: **20 checks Chrome OK**.
- [x] Incremento 3: capas compactas, nombres legibles, visibilidad/locks/reorder, grupos persistentes, biblioteca con los **11 templates**, recursos/datasets/resultados y upload nativo de imagen/video. Flujo completo de un mismo proyecto incorpora formato, template, texto, multimedia, edición real de canvas y reordenamiento antes de reproducir/guardar/exportar.
- [x] Incremento 4: inspector contextual por texto/imagen/video/visualización/escena/grupo, fuentes/roles/paletas/animación y bindings/unidades/procedencia. Proyecto CHIRPS existente de un día: **6 CalculationResult** idénticos tras editar apariencia, exportar y recuperar copia. **9 checks Chrome OK**, `science-flow.json`; `after-science-*.png`.
- [x] Incremento 5: timeline con miniaturas, duraciones, playhead, reorder real, duplicación, seek, zoom y colapso; chips corresponden a videos/audio del modelo. Preview central reproduce exactamente el MP4 descargado; HTTP Range **206**, JSON/MP4 descargados realmente. Multimedia/flujo completo: **21 checks Chrome OK**, `media-flow.json`; `after-media-*.png`. Los **30 cuadros** descargados se compararon con PreparedTimeline: diferencia media máxima **2.1852/255**, pico AAC decodificado **0.04818**. No motor paralelo de presentación.
- [x] Incremento 6: Design System propio carbón/petróleo/turquesa, SVG uniformes, texto/foco/bordes con contraste probado, estados de guardado/error/carga y controles accesibles. AppTest RED/GREEN corrige recuperación exitosa anunciada como error. Chrome **25 checks OK**, `accessibility.json`; no se declara certificación global de accesibilidad.
- [x] Incremento 7: responsive real en los tres tamaños, paneles simultáneos en escritorio y drawers a 768 px, timeline/playhead visibles, sin scroll horizontal global; selección/foco/secciones y campos pendientes sobreviven reruns. Worker obsoleto continúa hasta finalizar; regla temporal alineada a escenas en zoom 50/250, RED/GREEN Chrome registrado en `tmp/ux-redesign-ruler-red.log`. **10 checks de estado OK**, `state.json`. Capturas finales `after-final-*.png`, inspeccionadas visualmente junto a multimedia y ciencia.
- [x] Cierre: **301 tests completos, 283.806 s, OK**, `tmp/ux-redesign-final-tests.log`; **85 comprobaciones funcionales Chrome + tres layouts OK**, `tmp/ux-redesign-final-browser.log`. Compatibilidad del canvas anterior **96 checks × 3 anchos OK**, `tmp/ux-redesign-canvas-compatibility.log`; integración CCv2/worker anterior **17 checks OK**, `tmp/ux-redesign-transport.log`. `git diff --check` y whitespace de **29 archivos**, incluidos nuevos, OK.

Implementación: `studio_workspace.py`, `studio_workspace_commands.py`, `workspace_frontend/`, wrapper público aislado `studio_server.py` y entrega Range/token/TTL `studio_delivery.py`. Lanzador habitual usa el wrapper. Verificador reproducible: `python production/video_studio/verify_workspace_browser.py` con aplicación en puerto 8512; tests nuevos en `test_studio_workspace.py`.

Scene/Element/model_version=1, CalculationResult, 11 templates, ciencia/presentación, audio/animaciones/autosave/recovery y rutas legacy preservados. Sin dependencias nuevas, commit/push ni reversión de cambios anteriores. Siete incrementos cerrados; no queda una decisión de usuario pendiente para este rediseño. Los checkpoints técnicos históricos siguientes conservan su contexto.

## CHECKPOINT TÉCNICO ANTERIOR · roadmap editorial validado · 2026-10-08

- [x] Familias locales y roles integrados; paletas declarativas y personalización; once templates preservados.
- [x] Multimedia compuesta: grupos persistentes, rotación compatible y mezcla de audios originales con mute/ganancia por clip, sincronización y limitador verificado. AudioSource permite futuros proveedores de narración/música/SFX sin cambiar el contrato de proyectos anteriores.
- [x] Animaciones y preview continuo: cinco modos, entradas/salidas/retrasos y cada frame probados; preview audiovisual y descarga usan exactamente el mismo MP4 del worker.
- [x] Autosave y recuperación: snapshots aceptados con backup anterior; abrir copia preserva archivo elegido; gestos pendientes por pestaña/revisión y cancelación segura.
- [x] Accesibilidad del editor por teclado/estados/labels/foco/contraste/targets/responsive; cleanup explícito de lectores FFmpeg y caché; mediciones y pulido final documentados abajo.
- [x] **285 tests, 204.606 s, OK**, `tmp/studio-roadmap-final-full.log`, incluye todos los incrementos y últimas regresiones. Chrome **96 checks × 3 anchos OK** y transporte real **17 checks OK**. `git diff --check` y whitespace de **43 archivos** (incluidos untracked) OK. Sin dependencias nuevas, commit/push, reversión ni cambios de cálculos científicos.

El roadmap solicitado está recorrido dentro de los contratos documentados. Extensiones posteriores: UI/schema de pistas independientes de narración/música/SFX; rotación de texto/visualizaciones con contrato de legibilidad; recuperación de gestos tras cierre de pestaña y auditoría global de accesibilidad. No son capacidades presentes ni decisiones pendientes para este incremento. Los checkpoints históricos siguientes conservan su contexto; el checkpoint UX anterior gobierna esta entrega.

## Recursos, accesibilidad y pulido · incremento cerrado · 2026-10-08

- [x] Adaptador local para imageio-ffmpeg 0.6.0: reaping/join/cierre de pipes en EOF, cierre temprano y error inicial. Sin monkeypatch global/site-packages ni alteración del decode. AssetFrames intenta limpieza completa y propaga errores; caché libera imágenes propias en reemplazo/evicción/clear sin cerrar copias prestadas. Revisión local del adaptador sin otro fallo confirmado.
- [x] Recursos: **2 tests, 0.388 s, OK**, `tmp/studio-resources-green.log`; CFR/VFR/trim/rollback: **19 tests, 4.959 s, OK**, `tmp/studio-resources-timeline.log`. Prueba real registra ResourceWarning y exige ninguno en estas rutas. No se silencian warnings de terceros.
- [x] aria-pressed de selección/lock/visibilidad, estado anunciado y teclas documentadas; controles numéricos como alternativa al resize. Guías identificadas como márgenes orientativos. Chrome **96 checks por tres anchos**, `tmp/studio-accessibility-browser.log`; contraste/labels/foco/targets **3 tests OK**. No declarar certificación de accesibilidad global.
- [x] Entrada slide antes de delay: RED mostró contenido prematuro; GREEN oculta progreso cero. **2 tests, 0.977 s, OK**, `tmp/studio-animation-green.log`, cubren todas las entradas/salidas/retraso y cada frame MP4 de none/fade/slide/scale/wipe. Preview continuo usa el mismo MP4.
- [x] Rendimiento medido con fixture existente 60 cuadros/30.000 filas: mediana baseline 3.397 s y preparada 0.567 s, aproximadamente 6×. Once templates: productos cold 1.196 s, warm 0.015 s, 161.641 bytes de caché. `tmp/studio-final-performance.json`; tres muestras, medidas locales indicativas. Se elimina copia de preflight innecesaria y hash duplicado en UI. Sin relajar hashes/budgets ni ciencia.
- [x] Transporte final Chrome/CCv2/worker **17 checks OK**, `tmp/studio-final-transport.log`.
- [x] Suite final **285 tests, 204.606 s, OK**, `tmp/studio-roadmap-final-full.log`; diff/whitespace OK. Checkpoint estable registrado arriba.

## Autosave y recovery · incremento validado · 2026-10-08

- [x] Snapshot inicial y comandos aceptados: JSON compatible, flush/fsync/replace, backup anterior y temporales exclusivos limpiados. Abrir copia conserva archivo original, reinicia historial y preserva campos/Scene/Element/calculations/media. Corrupción/estructura inválida activa backup con aviso; no reparar ni borrar snapshot seleccionado.
- [x] Gestos pendientes por pestaña/escena/revisión en sessionStorage; restauración al remontar, error de storage visible, corrupción rechazada antes de tocar geometría. Drag incompleto/cancelado se revierte. OK conserva el límite de aceptación para render/export; no se afirma recuperación tras cerrar la pestaña o corte de energía.
- [x] **5 tests, 8.165 s, OK**, `tmp/studio-recovery-final-focused.log`; **94 checks por tres anchos**, `tmp/studio-recovery-browser.log`. RED/GREEN de falta de recovery y estado corrupto; revisión local reprodujo AttributeError de JSON estructural y normalización corregida. Próxima suite incluye este incremento.
- [x] Continuación posterior realizada: accesibilidad/limpieza de recursos y rendimiento/UX validados en checkpoint superior. Sin dependencias/commit/push.

## Multimedia y preview audiovisual · incremento cerrado · 2026-10-08

- [x] Audios originales superpuestos, mute/volumen por clip, trim/loop y silencio tras fin no-loop. AudioSource desacopla proveedor/schedule/mezclador para futuras pistas independientes. PCM por bloques a 48 kHz, hashes y presupuesto/espacio libre; no cambia ciencia ni schema.
- [x] Limitador con lookahead compensado y pico AAC decodificado verificado <=0.98; receipt trazable, video copiado sin reencode. Preview continuo y descarga reproducen el mismo MP4; aviso cuando cambia el documento. AppTest con worker real, undo y controles.
- [x] Revisión local reprodujo y corrigió adelanto de 85,33 ms por huecos PTS pequeños (RED/GREEN). Mute/zero/hidden/deleted/video sin audio, mezcla/ganancias, trim/loop/fronteras, PTS, picos, cancelación/publicación/cleanup y cuadros probados.
- [x] Rotación multimedia/formas -360..360 con contain completo en caja nativa; mapas proporcionales, texto/gráficos explícitamente rechazados. Tres tests de caja/esquinas/opacidad/animación/PNG-MP4 OK.
- [x] **276 tests, 398.395 s, OK**, `tmp/studio-audio-full.log`; **10 tests, 16.918 s, OK**, `tmp/studio-audio-final-focused.log` (suite completa incluye las comprobaciones AAC adicionales posteriores). Chrome/CCv2/worker **17 checks OK**, `tmp/studio-audio-transport.log`; diff check sin errores. Sin dependencias/commit/push/reversiones.
- [x] Continuación posterior realizada: recovery, recursos/accesibilidad y rendimiento/UX validados en checkpoint superior. Gestos cancelados no persisten; adaptador fijado cierra pipes de producción.

## Grupos persistentes · incremento cerrado · 2026-10-07

- [x] group_id aditivo, comandos puros, selección colectiva, locks, desagrupar, JSON/undo y copiar con identidad nueva. Copia conserva desplazamiento común y rechaza grupos parciales/bloqueados. Ciencia/píxeles previos preservados.
- [x] Suite 262 tests, 387.072 s, OK (`tmp/studio-groups-full.log`), anterior a la última regresión de copia parcial; seis focalizados posteriores OK (`tmp/studio-groups-final-focused.log`). Chrome 87 checks por cada uno de tres anchos (`tmp/studio-groups-browser.log`); CCv2/worker 17 checks OK (`tmp/studio-groups-transport.log`). Focus preventScroll corrige gestos sobre canvas fuera del viewport.
- [x] Continuación posterior realizada: multimedia/audio, preview/animaciones, recovery y cierre del roadmap validados arriba. Decisión del usuario y arquitectura ampliable conservadas; no repetir auditorías.

## Paletas y personalización visual · incremento cerrado · 2026-10-07

- [x] Escalas secuenciales/divergentes/categóricas optativas, dominio/centro o categorías declarados, colores personalizados y leyenda visible con unidades/NoData. Sin inferir centros físicos, dominio ni categorías. Valores representados fuera de escala y etiquetas no declaradas producen error, sin clamp ni modificar CalculationResult.
- [x] Reservas separadas para leyenda y warnings; error cuando no cabe a 8 px. Ranking con escala y sin Top N muestra NoData neutral; no-scale y Top N conservan contratos anteriores. Líneas neutrales se dibujan detrás de puntos coloreados; regresión sobre píxeles reales. Unidades/categorías multilinea rechazadas para no desbordar.
- [x] Inspector: paleta/dominio/centro/categorías/colores/familia en un envío; tinta/fondo/texto configurables. Preflight/undo/JSON/caché y ciencia preservados. AppTest prueba cambio combinado y deshacer; preview/MP4 con Lora/Atkinson y escala explícita OK.
- [x] **10 tests, 3.847 s, OK**, `tmp/studio-palettes-final-focused.log`; RED originales y revisión en `tmp/studio-palettes-{red,review-red,points-red}.log`. Imagen revisada localmente `tmp/studio-palette-review.png`. Revisión acotada: rerun parcial corregido, Top N y normalización de ejes aclarados, multilinea/overdraw reproducidos y corregidos.
- [x] **257 tests, 298.087 s, OK**, `tmp/studio-palettes-full.log`, incluyendo la regresión de publicación durable y todos los focalizados nuevos. JS del canvas sin cambios en este slice; transporte anterior con nueva fuente 15 checks OK.

Siguiente pendiente real: composición, comenzando por grupos persistentes planos; plan y cuatro pruebas RED preparados. No se repiten auditorías ni biblioteca/caché/formato ya validados. Sin nuevas dependencias ni commit/push/reversión; warnings de pipes FFmpeg aún pendientes de limpieza.

## Tipografía integrada · continuación autorizada · 2026-10-07

- [x] Resolver local de Barlow Condensed, Atkinson Hyperlegible y Lora desde bytes; nombres permitidos, sin rutas ni fallback, pesos variables privados. Manifest/licencias verificados. Textos y visualizaciones usan la misma fuente en canvas confirmado/PNG/MP4. Legacy conserva renderer; ausencia de familia conserva Barlow y píxeles.
- [x] Roles título/cuerpo/fuente/datos en controles por escena y elemento; aplicación explícita y pura, locks/tamaños/geometría/bindings/ciencia preservados. JSON/undo/inspector probados. Roles manuales sin metadata usan cuerpo; no se infieren títulos ni herencia futura.
- [x] RED/GREEN de selección, variaciones, fuente ausente, texto vacío, tamaños grandes y fallo de escritura durable. La escritura de borrador precede al avance del estado/historial. Revisión acotada sobre artefacto: rol implícito aclarado en contrato; publicación prematura corregida con reproducción. Solo revisión local, sin CLI externa.
- [x] Suite **246 tests, 233.505 s, OK**, `tmp/studio-typography-full.log`, anterior a la última regresión de borrador; **10 tests, 4.122 s, OK**, `tmp/studio-typography-final-focused.log`, después de esa corrección. Próxima suite incluye 247 tests más los de paletas.
- [x] Chrome → CCv2 → worker con Atkinson: **15 checks OK**, `tmp/studio-typography-transport.log`. PNG/MP4 con ambas familias nuevas dentro de los focalizados. Sin dependencias, commit/push/reversión.

Siguiente pendiente real en ejecución: paletas declarativas con dominio/centro/categorías y leyenda visible. Se conservan checkpoints históricos abajo. Warnings conocidos de Streamlit/Rasterio y pipes FFmpeg continúan registrados para limpieza de recursos; no son cierre del roadmap.

- [x] Git, inventario, skills y baseline: 115 tests OK.
- [x] Auditoría estática de módulos/flujo y reporte científico con pendientes explícitos.
- [x] RED/GREEN científico: integer masks, sentinel exacto, negativos/NoData display, main e inset nativos.
- [x] Checkpoint científico inicial: 121 tests OK; fixture inset añadido después, 7 focused OK.
- [x] Fase 1: modelo Studio con migración pura, versión, escenas/elementos/bindings y referencias; test_studio_model.py.
- [x] Perfiles: custom/márgenes, integración compatible con delivery; tests de perfiles/storyboard. Reflow todavía API.
- [x] Primer incremento del editor: capas/lock/rename, zoom y comandos compatibles; tests y Chrome. Ver estado del segundo incremento abajo.
- [x] Checkpoint integración tras revisión: 175 tests OK (158.521 s), Chrome 3×12 checks OK, diff check limpio; documentación de capacidades reales y pendientes actualizada.
- [ ] Escenas libres con render común y timeline visual; no exportar cambios ignorados.
- [x] CalculationResult inmutable y VisualizationSpec; bindings sin cálculo visual. VariableSpec explícito y consolidación temporal pendientes.
- [x] KPI/bar/dot/lollipop/line/ranking/comparison del resumen; Maqueta → Visualizaciones → PNG/instantánea al montaje/receipt.
- [x] Render API de escenas libres con geometría nativa/assets por ID; integración editor/MP4 libre pendiente.
- [ ] Templates/themes/multimedia compuesto/data→visualization.
- [ ] Animación, autosave/recovery, performance/accesibilidad y revisión visual.

Los items abiertos todavía no tienen cierre de integración. Existe implementación parcial según el checkpoint siguiente.

## Checkpoint de cierre · 2026-10-07 · segundo incremento

Desarrollo detenido por instrucción del usuario. Sin commits, push, cambios de rama ni reversiones. Se conservan los cambios locales anteriores. **No se declara cerrado el incremento:** falta validar el conjunto final y el navegador después de los últimos cambios.

Verificaciones de cierre: `git status --short` consultado; árbol con cambios y archivos nuevos sin commit. `git diff --check` terminó con exit code 0; único aviso LF→CRLF en `production/video_studio/.streamlit/config.toml`. Este comando comprueba el diff de archivos tracked, no incorpora los untracked. No se ejecutaron tests nuevos al cerrar.

### Completado y verificado dentro de este incremento

- [x] Baseline previo a la nueva implementación: 175 tests, 170.711 s, OK; `tmp/studio-increment2-baseline.log`.
- [x] Comandos puros de escenas: borrador separado, conservación de referencias legacy, duplicación, orden, duración cuantizada a 30 fps, retiro de timeline sin borrar escena y patch sin modificar bindings.
- [x] Contratos sintéticos de render temporal: límites de cuadros, PNG/preview desde el mismo render y exportación MP4 de seis cuadros con dimensiones 320×180 y tolerancia de compresión explícita.
- [x] Tests de animación none/fade/slide/scale/wipe, imágenes/video compuesto silencioso, paths/hashes, presupuesto de imágenes antes de decodificar, trim con seek y protección de `project.json` existente.
- [x] AppTest de Estudio: abrir, añadir/duplicar, deshacer, quitar/recuperar y guardar borrador sin llamar `data.load_values`; geometría contain sin acumular offsets; revisiones científicas nuevas conservan resultados/bindings anteriores.
- [x] Regresiones de revisión: texto hasta 2000 caracteres sin truncado silencioso, patch desconocido rechazado, desbloqueo de metadata predeterminada, CSS inline CCv2 registrado correctamente.

### Implementado parcialmente; falta cierre de integración

- [ ] `Estudio` añadido después de las cuatro fases anteriores en `workspace.py`/`app.py`; `studio_ui.py` reutiliza el canvas existente, integra inspector, timeline CCv2, preview de cuadro, PNG/JSON, borrador y ruta independiente de jobs/MP4.
- [ ] Multiselección: Shift+clic, marquee, Ctrl+A con foco en canvas, movimiento/resize conjunto, delete, undo/redo; copy/paste/duplicate en escenas libres. El ajuste tipográfico del resize fue implementado después de la última validación Chrome concluida.
- [ ] Biblioteca inicial: cinco templates editables, diez temas, siete presets tipográficos con Barlow Condensed OFL y cuatro paletas declaradas. Reflow explícito por regiones; no toda la biblioteca de la especificación está implementada.
- [ ] Biblioteca segura de imágenes/video y composición con contain/cover, opacidad, trim, loop y mute. Animaciones usan el render temporal común. Audio compuesto y rotación no están soportados.
- [ ] Reutilización explícita de snapshots ya calculados mediante IDs de revisión y fuentes en `studio.datasets`; revisar el flujo completo desde Visualizaciones hasta receipt.
- [ ] Job Studio independiente con `request.json`, estado, cancelación y receipt. La exportación sintética directa pasó; el ciclo completo UI → subprocess → descarga aún no se verificó.
- [ ] Ampliación de `verify_canvas_browser.py` a multiselección, marquee, resize, atajos y timeline: la última llamada de edición/ejecución fue interrumpida; no hay resultado confirmado de esa ampliación. Revisar el archivo antes de retomarla.

### Evidencia disponible y límites

- `test_studio_editing.py`: 5 tests OK (0.084 s), antes de las ampliaciones posteriores del módulo; necesita repetición al retomar.
- Discovery `test_studio*.py`: 43 tests OK (44.392 s), antes de las últimas correcciones; no sustituye una suite final.
- Última ejecución focalizada: `test_studio_timeline.py`, 7 tests OK (0.432 s); `test_studio_ui.py`, 4 tests OK (3.129 s). También hubo RED reproducido antes de las correcciones.
- Chrome concluido durante este incremento: tres anchos 1422/750/504, 12 checks por ancho, OK; `test_canvas_features.py`, 3 tests OK. Esa ejecución comprobó contratos anteriores, **no** toda la multiselección/timeline actual.
- FFmpeg real: seis cuadros, dimensiones y colores contra `frame_at`; video sintético compuesto probado. No se certificó todavía igualdad de seek aleatorio y lectura secuencial para clips VFR o tasas distintas de 30 fps.
- Última suite completa aprobada: los 175 tests del baseline, antes del segundo incremento. No hay suite completa aprobada del estado final actual.
- Warnings conocidos: contexto Streamlit ausente en bare mode/AppTest; PendingDeprecationWarning de Rasterio; FFmpeg vacío en tests deliberados de cancelación; aviso LF→CRLF del config local. Sandbox de shell falló durante la sesión; comandos de lectura/tests requirieron ejecución escalada. CUA no estuvo operativo en el incremento anterior.

### Siguiente tarea exacta

1. Leer este checkpoint y el apartado equivalente de arquitectura; preservar el diff actual.
2. Revisar si quedó aplicada la ampliación de `verify_canvas_browser.py` y ejecutar esa verificación en Chrome; corregir primero fallos de multiselección/resize/timeline, sin añadir funcionalidades.
3. Repetir los tests focalizados nuevos y luego la suite completa `test_*.py`; comprobar también que las rutas antiguas siguen operativas y que la fase añadida conserva las cuatro anteriores.
4. Verificar el job Studio real y un clip con tasa distinta de 30/VFR: seek aleatorio, trim, loop, cuadros/receipt y preview frente a MP4.
5. Resolver los límites detectados: carga/rerender repetido de multimedia y validación JSON por cuadro; mezcla de referencias legacy/free en timeline; custom pequeño y límites de texto; metadata bloqueada y resize tipográfico en transporte CCv2 real. No declarar completado Estudio hasta cerrar estos contratos.

Después: grupos persistentes, rotación, mejores guías/alineación, más templates/paletas/roles tipográficos, audio, autosave/recovery durable y pendientes científicos. No repetir la auditoría original ni cambiar metodologías sin evidencia.

## Continuación del checkpoint · 2026-10-07

- [x] Ampliar y ejecutar el harness interrumpido: multiselección, marquee, resize, atajos y timeline; 49 checks por ancho de Chrome.
- [x] RED/GREEN de cancelación/historial, fuente efectiva, límites y redondeo de resize y vecinos bloqueados.
- [x] RED/GREEN de seek VFR, incluido soporte de cuadros separados por diez segundos; trim/loop contra lectura secuencial.
- [x] UI → worker real → receipt/MP4/descargas y cancelación con AppTest.
- [x] Chrome → CCv2 real → callbacks de producción → reorder/seek → worker/receipt: fixture aislada de seis cuadros, 15 checks.
- [x] Primera suite completa de esta continuación: 195 tests, 136.947 s, OK; `tmp/studio-resume-full.log` (antes de la regresión VFR dispersa y del siguiente slice).
- [x] Resolver explícitamente timelines mixtas en la UI, conservando escenas, orden legacy, resultados y bindings. Ninguna referencia desaparece del documento; el usuario activa una timeline libre antes de render/export; pruebas puras y AppTest OK.
- [x] Reducir validación del registro científico y preparación de escenas repetidas por cuadro, sin cambiar píxeles ni validar menos el documento de entrada. `PreparedTimeline` conserva una copia privada y las APIs anteriores; límites cuantizados, integridad y equivalencia de píxeles probados.
- [x] Endurecer publicación MP4/project/receipt: documento completo JSON finito, extensión MP4, reserva exclusiva, staging propio y rollback ante fallos de escritura, cierre o publicación. 19 tests de timeline OK; se preservan archivos previos. MP4 final se publica después de los sidecars; no se promete transacción atómica frente a corte de energía.
- [x] Repetir suite completa y verificaciones de navegador afectadas al cerrar el estado final: **208 tests, 245.251 s, OK**, `tmp/studio-resume-full-final.log`; Chrome 3×49 checks y transporte real CCv2/worker 15 checks OK.

Cierre de esta continuación: `git diff --check` OK; comprobación de whitespace sobre 15 archivos completos (incluidos untracked) OK. Se conserva el aviso conocido LF→CRLF del config Streamlit. La suite incluye las rutas legacy y las regresiones nuevas de Studio; los gestos Chrome siguen siendo sintéticos. Warnings de contexto Streamlit y FFmpeg sin cuadros corresponden a bare mode/cancelación deliberada. No se hicieron commits, push, reversiones ni cambios de rama; no se agregaron dependencias.

La auditoría original no se repite. Hubo dos revisiones adversariales acotadas a tres ciclos cada una: canvas/VFR y timeline preparada/publicación. Los hallazgos accionables se reprodujeron y corrigieron. La segunda opinión externa se ofreció; no se ejecutó una CLI externa. CUA sigue sin iniciar por el sandbox. Los gestos de los harness son sintéticos y usan un stub de pointer capture; el transporte CCv2, los reruns, callbacks y worker de la segunda verificación son reales. El preroll solicitado de multimedia es acotado; FFmpeg puede decodificar desde un keyframe anterior según el GOP del archivo.

### Siguiente pendiente real

1. Reducir carga/rasterización repetida de assets y thumbnails en reruns del editor con invalidación por escena, bindings, perfil y hash del archivo; medir antes/después y conservar controles de integridad. No añadir una caché global científica.
2. Completar contratos de formatos custom pequeños y texto que no cabe, y navegación con gestos sin aplicar; verificar transporte CCv2 y correspondencia con render confirmado.
3. Continuar biblioteca de templates/themes/tipografías/paletas y multimedia/animaciones sobre las APIs existentes. Grupos persistentes, rotación, audio compuesto y preview continuo siguen abiertos.
4. Recuperación/autosave durable y revisión de accesibilidad, rendimiento y pulido. Borradores/undo actuales no equivalen a recovery completo.

El editor libre, multiselección/resize y timeline visual tienen ahora evidencia de integración; estos límites impiden declarar cerrado todo Estudio o todo el roadmap. Se conservan los checkpoints históricos anteriores.

## Caché multimedia/thumbnails · incremento cerrado

- [x] Caché por sesión para imágenes decodificadas, metadata de video, canvas, thumbnails y PNG temporal; invalidación por escena/perfil/bindings/hash real. LRU con presupuestos contables de 32 MiB para multimedia y 32 MiB para productos; overhead Python y memoria temporal de render no son parte de ese contador. Sin readers persistentes ni caché científica global.
- [x] Reorder/playhead/cambios ajenos reutilizan productos independientes. Controles de paths, archivo real, JSON/documento y 80 MP combinados siguen ejecutándose en hits. Imágenes se decodifican desde los bytes verificados; probe legacy acepta hash opcional y devuelve metadata aislada.
- [x] 11 regresiones de caché, incluidos archivo con stat idéntico, metadata entre sesiones y presupuesto en hit; revisión adversarial de tres ciclos con hallazgos reproducidos/corregidos y revisión final sin más hallazgos.
- [x] Suite de cierre: **219 tests, 147.699 s, OK**, `tmp/studio-cache-full-final.log`. Chrome → CCv2 → worker: 15 checks OK.
- [x] Misma fixture de 12 reruns/3 escenas, tres muestras incluyendo hashing/preparación: mediana **3.477 s → 0.263 s**; decodificaciones **12→1**, probes **12→1**, renders **60→6**. `tmp/studio_cache_benchmark.py`, `tmp/studio-cache-{baseline,cached}.json`; resultados sintéticos, sin promesa universal.

Se continúa automáticamente con formatos pequeños/texto: fallos reproducidos de templates en 160×160, 320×160 y 3840×160; tests RED en `tmp/studio-small-red.log`. El siguiente slice conserva las escenas guardadas; afecta creación/adaptación explícita y el render de tokens largos. La pregunta opcional de segunda opinión externa sigue ofrecida; no se ejecutó ninguna CLI externa.

## Formatos pequeños/responsive · checkpoint recuperado tras interrupción

- [x] Templates/adaptación explícita reservan espacio para texto a 8 px y métricas de 80×80 cuando cabe. No se reescriben escenas existentes al abrir.
- [x] Tokens largos y separadores originales conservados en texto vinculado; pruebas sobre strings dibujados, marcas Unicode de clase cero y ZWJ con modificadores. Error explícito cuando el contenido no cabe a 8 px. Es una segmentación acotada, no una implementación completa de UAX #29.
- [x] Handle de resize de 24 px CSS visible en fit incluso para 3840×160 en contenedor de 320 px; geometría nativa/export sin cambio. Canvas libre fuentes 8–400; legacy conserva límites anteriores.
- [x] Suite completa: **226 tests, 221.567 s, OK**, `tmp/studio-small-full.log`. Las últimas regresiones ZWJ se verificaron después con **7 tests, 37.442 s, OK**, `tmp/studio-small-green-final.log`. Chrome **81 checks por ancho** (1422/750/504), `tmp/studio-small-browser.log`; whitespace sobre 20 archivos y diff check OK, con aviso LF→CRLF conocido.
- [x] Revisión adversarial de tres ciclos: hallazgos de whitespace, marcas y ZWJ reproducidos/corregidos; último ciclo sin hallazgos adicionales. Segunda opinión externa ofrecida, sin CLI externa ejecutada.

Siguiente incremento autorizado: biblioteca de templates descrita al final de `tasks/plan.md`; seis escenas nuevas, comandos puros de diseño, bindings explícitos y compatibilidad de los cinco templates actuales. Después: roles/familias tipográficas y paletas, multimedia/animaciones, autosave/recovery, accesibilidad/rendimiento. Navegación con gestos sin aplicar sigue dentro de recovery; no está cerrada por este checkpoint.

## Templates/themes · incremento cerrado · fin de sesión solicitado

- [x] Seis templates nuevos: `metric_focus`, `ranking_focus`, `comparison`, `quote`, `image_caption`, `methodology`; once en total. Scene/Element y los IDs/layouts/styles de los cinco anteriores se conservan mediante fixture de compatibilidad. Metadata tipográfica aditiva no altera píxeles al abrir.
- [x] Región `body_full` para creación/adaptación explícita; placeholders editables, sin datos/imágenes/mapas/fuentes inventados. Imagen seleccionada de biblioteca usa contain. Placeholder cabe con margen custom máximo; visualización vinculada mantiene mínimo 80×80 y rechaza margen incompatible.
- [x] Binding elegido explícitamente desde CalculationResult; comparación solo ofrece registros completos de dos valores válidos con cobertura comparable. No recorta ni fabrica filas. Preflight fallido conserva documento y selección. Styling no lee datasets ni recalcula ciencia.
- [x] Acciones separadas de tema/tipografía y comando puro `apply_scene_design`; respeta bloqueados, transform, bindings, media y registros. `typography_sizes` conserva el contrato original por preset/rol, sin deriva de redondeo. Aplicación idéntica y roundtrip exactos en 11 templates × 7 presets × 4 perfiles; tamaño manual fija otra base. JSON conserva el contrato. Metadata finita excesiva devuelve ValueError sin mutar el original.
- [x] Revisión local acotada a tres ciclos; hallazgos de bases/rounding, comparación, márgenes y overflow reproducidos/corregidos. Usuario eligió **solo revisión local**: no ejecutar ni volver a ofrecer revisión externa sin nueva solicitud.
- [x] Últimos focalizados afectados: **41 tests, 29.680 s, OK**, `tmp/studio-library-close-focused.log` (templates 11, edición, UI, perfiles y caché), después de la última guarda de metadata. Logs RED: `tmp/studio-templates-{red,review-red,idempotence-red,metadata-red}.log`.
- [x] Suite completa de cierre iniciada antes de esa última regresión: **236 tests, 264.751 s, OK**, `tmp/studio-templates-full-final.log`. La guarda/test adicional se verificaron después en los 41 focalizados; próxima discovery completa debe incluir 237 tests. No se atribuye ese test adicional a una suite ya iniciada.
- [x] Preview/MP4 real de comparación: tres cuadros, error medio de compresión <5/255. Transporte Chrome → CCv2 → callbacks → worker: **15 checks OK**, `tmp/studio-templates-transport.log`. Matriz ampliada pequeña: **7 tests, 72.881 s, OK**, `tmp/studio-templates-small.log`. Chrome responsive anterior 3×81 checks; no se modificó JS en este incremento.

Fuentes preparadas antes de pedir cierre: Atkinson Hyperlegible Regular/Bold y Lora variable, 330.575 bytes incluyendo dos licencias OFL; URLs oficiales fijadas a commits y SHA-256 en `assets/fonts/studio-fonts-manifest.json`. Hash/tamaño/licencias/carga Pillow/eje Lora verificados con `tmp/verify_studio_font_assets.py`. **Sin integración al renderer/UI**: preparación no equivale a cierre tipográfico. Sin dependencias Python/npm nuevas.

`git diff --check` OK y whitespace sobre 25 archivos completos tracked/untracked OK al cerrar. Se preservan cambios existentes; sin commit/push, reversiones ni cambios de rama. Warnings observados: contexto Streamlit bare mode, deprecaciones Rasterio, FFmpeg sin cuadros en cancelación deliberada y ResourceWarning de pipes al cerrar readers (`studio_media.py`); este último queda para pulido de recursos. Avisos LF→CRLF del config conocido y del README de fuentes actualizado.

### Siguiente pendiente exacto al retomar

1. Leer este checkpoint y `tasks/plan.md`; no repetir auditoría ni caché/formato/templates validados.
2. Integrar Barlow y familias preparadas mediante resolver local de nombres permitidos y roles título/cuerpo/fuente/datos, controles por elemento/escena, sin paths del documento ni fallback silencioso. Revisar manifest/licencias y variaciones Pillow; documentos sin `font_family` conservan Barlow/píxeles. Raster del canvas y export usan la misma fuente. RED/GREEN, AppTest y PNG/MP4 antes de cierre.
3. Paletas declarativas secuenciales/divergentes/categóricas con dominio/centro o categorías explícitos y leyenda visible; conservar valores/unidades/bindings. Cuatro paletas actuales son elecciones de tinta, todavía no escalas de datos completas.
4. Multimedia compuesta (grupos/rotación/audio), animaciones/preview continuo, autosave/recovery y accesibilidad/rendimiento. Gestos sin aplicar y recovery durable siguen pendientes.

Se detiene aquí por instrucción expresa de cerrar la sesión con estado estable. No hay otro bloque grande iniciado.
