# Ecuador Vivo Studio 2.0 · contratos incrementales

## Extensión 4b.3b · núcleo implementado, cierre de interfaz pendiente

Estado 2026-10-08: 87 pruebas automatizadas OK/MP4 real; Chrome export/reproducción pendiente, no incremento terminado. Las guardas privadas históricas de 4b.2/3a inferiores quedan sustituidas **solo para v2 autorizado con consumidores completos** por esta extensión, no por inserción ordinaria de multimedia.

Scene.map_instances: registro por id de asset_id/trim_in_frame/trim_out_frame/loop; Element.temporal_binding: instance_id/channel, exclusivamente continent/galapagos (type map), date (type text protegido) y legend_static (type legend con auxiliar RGBA). Ambos mapas y auxiliares reciben una observación común; instance_frame delega en video_frame_index, BundleFrames/calendario comparten bundle_observation. NoData/no cobertura conserva alfa vacío y fecha real. Transform editorial no cambia CRS/datos/estadísticas. Fecha ISO no se almacena en style.text ni admite DataBinding/trim/asset por elemento temporal.

Bundle v2 puede incluir auxiliaries.legend_static con legend.png/hash/bytes/size/mode/spec de escala/clases/unidades congeladas. Builder y colorizer existentes; todas las clases, error explícito si no cabe. Viejos v2 privados sin auxiliar siguen decodificables, pero publicación requiere preparación explícita de nuevo bundle completo. validate_maps reconstruye revisión desde datasets/calculations; exige fuente/revisión/hash/header íntegros, referencias de instancia/binding, fecha/leyenda y consumidores correspondientes. Mapas visibles requieren auxiliares visibles. Recursos huérfanos, relojes/revisiones incompatibles y asset_id ordinario para bundle se rechazan; no publicación silenciosa. v1 opaco/estáticos y sus campos conservados.

PreparedTimeline/renderer/AssetFrames comparten contexto; PNG de capas RGBA se compone antes de H.264 RGB. Cache verifica bytes actuales antes de servir productos calientes. Recibo RGBA tiene instancia/clock/hash/revisión/bindings/transforms/spans globales por eventos/ciclos, sin scan por frame/capa. Duplicar pareja copia auxiliares/nueva instancia, duplicar región conserva clock; escenas/clipboard remapean referencias y commit/recovery/undo existentes verifican documento. Clipboard incompleto falla explícitamente antes del commit.

UI actual permite abrir un documento estructurado válido y protege contenido observado; no anuncia la inserción guiada ni gestos cartográficos de 4b.4a/4b.4b como terminados. Leyenda semántica/formatos/counter/crop/template cartográfico siguen pendientes. Futuras series multi-año/plantillas deben conservar instancias, observaciones, fechas y procedencia, con componentes editables; no se añadió otro motor.

Especificación del usuario: `../tmp/ecuador-vivo-studio-2-prompt.md`, 21 secciones y RESULTADO ESPERADO, UTF-8 verificado el 2026-10-08. El usuario autoriza implementación progresiva, pruebas y checkpoints; no hace falta repetir aprobación de un plan ni solicitar revisiones externas opcionales. El diseño conserva el workspace y los once templates. No introduce proveedores nuevos.

## Mapa de capacidades y orden

| Capacidad | Responsabilidad | Dependencias |
|---|---|---|
| project-document | Identidad estable, revisión canónica, proyección legacy, snapshots | schema/Scene/Element/recovery existentes |
| job-products | Metadata validada del MP4 publicado y compatibilidad de recibos antiguos | workers existentes |
| project-start | Inicio, recientes, creación libre/template, abrir copia | project-document |
| scientific-project | Preparación explícita, CalculationResult y fábrica de escenas | project-document, proveedores/resumen/templates existentes |
| temporal-map | Recurso lógico, calendario/manifest y composición RGBA progresiva | scientific-project, compositor existente |
| media-library | Importación real, validación/miniaturas/onda y gestión | project-document, media/FFmpeg existentes |
| clip-timeline | Clips por escena, pistas, reloj y comandos editables | project-document, media-library, renderer existente |
| independent-audio | Fuentes autónomas, envolventes y schedule | clip-timeline, mezclador existente |

Orden de construcción: correcciones y project-document → project-start → scientific-project → temporal-map → media-library → clip-timeline → independent-audio → integración UX → validación integral. Contratos de campos nuevos se incorporan únicamente cuando el consumidor/render está implementado; no guardar campos ignorados por exportación.

## Decisiones y límites

- FPS: 30, reloj entero de cuadros; audio 48 kHz/1600 muestras por cuadro. No ofrecer FPS sin soporte.
- Documento: extensión aditiva del JSON actual, no tercer modelo. Identidad/revisión explícitas; consumidores científicos/legacy reciben una proyección documentada, y sus cambios se incorporan al documento con escenas/recursos/revisiones conservados. Un proyecto antiguo se abre en copia, nunca se reescribe automáticamente.
- Revisiones científicas inmutables y bindings explícitos; no actualizar escenas antiguas al seleccionar una fuente/fecha nueva. Estética no llama proveedores/calculadores.
- Productos exportados: recibo declara nombre relativo, MIME y hash del MP4; resolver valida metadata, estado completo y confinamiento al directorio del trabajo. Recibos antiguos usan su contrato de renderer conocido; ningún sondeo arbitrario de MP4.
- Clips/pistas propuestos: campos aditivos por escena; clip con id, track_id, element_id/asset_id, start_frame, duración e intervalo de origen. Tiempo de composición y del recurso separados. Sin campos equivocados fingiendo compatibilidad.
- Edición temporal inicialmente no-ripple: mover/trim/delete no desplaza otros clips; huecos muestran fondo y silencio; superposiciones siguen orden de pista/capa. Split conserva recurso/binding y reloj, genera ids nuevos y admite undo. Ripple solo como operación explícita posterior.
- Mapas: primer puente puede ser prerenderizado + calendario verificable (sección 6.5); no anunciar edición científica plena. Continente e inset requieren capas RGBA/máscaras reales, no supuesto alfa H.264. Recursos internos no se muestran como cientos de PNG en biblioteca.
- Regeneración/template: propuesta separada, diferencias y acción explícita; conservar/reemplazar/cancelar, sin pisar edición humana.
- Inicio y timeline extienden el frontend actual con tokens/paneles existentes. CCv2 para interacción; uploader nativo/transferencia real, sin permisos/rutas del Explorador inventados.
- JSON no incluye archivos multimedia/GeoTIFF y no equivale a paquete portátil.

## Verificación

### SIG-G1 · GeoJSON y vista geográfica implementados

El recibo declara visibilidad por elemento efectivamente vinculado y omite mapas eliminados o reemplazados; la escena no puede referenciar una vista inexistente. Ocultar una capa conserva la referencia y las coordenadas originales.

Namespace opcional aditivo `studio.geography={version:1,sources,regions,views}` validado en preflight/recovery y consumido en SIG/UI/fábrica/receipt. Sources: bytes originales externos bajo STORE/geography/sources/{sha}.geojson, id/path/sha256/bytes/name/native_crs/provenance(citation,license,url). Regions: id por source-revisión/feature_index, source_id, índice/ID GeoJSON original y bbox calculado de geometría, no nombre de país. Views: id/region_id/asset_id/display_crs/method/bbox/size/image_sha256; asset ordinario RGBA verificado de media, renderer map con contain, título/source independientes. `generation.geographic_view_id` identifica el envío idempotente; selección/posición editorial no cambia geometrías/atributos ni CalculationResult. Receipt geographic_views conserva fuente/hash/licencia/CRS/bbox/imagen/transform. Originales no se empaquetan ni descargan automáticamente; JSON sigue siendo por referencias, no paquete portable.

Primera ruta genérica admite Feature/FeatureCollection RFC7946 Polygon/MultiPolygon 2D WGS84 longitude/latitude OGC:CRS84, agujeros/multipart/topología válida, fuera de bbox ECU. Sin reproyección/medición/estadísticas; rasterización angular por centros de píxel reutiliza geometry_mask, projector y outline_layer existentes. Rechaza CRS legacy, antimeridiano/polos, coordenadas/tipos no soportados, números no finitos/JSON duplicado/IDs duplicados o bbox incoherente; no repara silenciosamente. Budgets: 8 MiB/archivo, 250000 posiciones, 5000 regiones y 64 MiB de fuentes/proyecto, 100 vistas. Fuente missing/corrupta falla antes de reabrir/exportar píxeles antiguos. Licencia/citación son declaraciones obligatorias, no verificación legal ni sustitución de obligaciones del software; URL pública no admite credenciales/query/fragmentos, conectores y almacén de secretos pendientes.

### SIG/Studio integrado · contrato de navegación y envío

SIG y Studio son superficies del mismo `project_document` y WorkspaceSession canónico, con clave por identidad estable. Studio directo no requiere datasets. SIG reutiliza el asistente/fábrica y jobs de mapa 4a. Enviar una revisión añade escenas al formato actual, conserva escenas Studio previas y archiva legacy sin borrarlo; campos desconocidos/registros inmutables permanecen. `generation.sig_transfer_id` identifica contenido/revisión y tiene consumidor de reintento en studio_sig; no sobrescribe edición humana. Enviar un mapa reutiliza su escena por asset/manifiesto; duplicación explícita continúa siendo comando Studio. Commit/preflight/autosave/undo existentes; navegación no calcula y fechas/bindings no cambian por edición visual. UI opcional del asistente/mapa conserva defaults históricos. Importadores ECU no se anuncian universales; 4b.1 privado no se publica por este puente. G1 y gestión completa BYOD siguen pendientes.

### Bundle RGBA 4b.2 · contrato privado implementado

`studio_map_bundles.prepare_bundle/read_bundle` y rama explícita de studio_map_jobs consumen `rgba_observation_bundle`, manifiesto externo v2 y header privado `kind=temporal_map`. No se admiten aún en studio.media/schema público. Dos grids continent/galapagos fijos EPSG:4326 con CRS nativo por observación, fuentes originales/revisión/citación/parámetros científicos congelados y un calendario exclusivo 30 FPS. PNG lossless por observación/capa, no por frame; thumbnail auxiliar RGBA. Header sella manifest con SHA-256, referencia sources.revision, período/metadata/grids compactos; status sella el header. Verificación de rutas relativas confinadas, bytes/dimensión/mode RGBA/alpha vacío y correspondencia fuente-banda-fecha-calendario; no URI remotos desde renderer. PNG ≤100 MiB, manifest ≤8 MiB, bundle ≤1 GiB, 40 MP/capa y 80 MP/pareja, espacio libre comprobado. Fallo/cancelación conserva proyecto/productos anteriores; archivos privados parciales no son recursos listos. Publicación requiere decoder/reloj/renderer de 4b.3, no adaptar automáticamente MP4 antiguos.

### Decoder 4b.3a · consumidor interno implementado

Guarda explícita en validate_export rechaza recursos kind=temporal_map privados en documentos públicos hasta implementar reloj y renderer 4b.3b. La API privada AssetFrames.map_at sigue disponible; no confundirla con publicación de nuevos elementos cartográficos.

BundleFrames/AssetFrames.map_at reciben un source_frame ya resuelto por el futuro reloj compartido, devuelven imágenes por layer_id y una observación/estado de cobertura común; no crear trims individuales. Constructor verifica metadata/thumbnail, no decodifica la serie. Cada petición verifica bytes actuales/manifiesto/confinamiento antes de reutilizar tiles; RGBA decodificado desde esos bytes. MediaCache existente: LRU con peso RGBA real más overhead, presupuesto 32 MiB de tiles por sesión por defecto, independiente de productos activos; activos junto a imágenes/videos ≤80 MP y metadata de bundles ≤8 MiB/sesión. Cursor por instancia, copias protegidas y cierre explícito. Esta API no autoriza guardar bundles/instancias/bindings en documentos públicos hasta 4b.3b con renderer, calendario, fecha y leyenda consumidores.

### Puente cartográfico 4a · contrato implementado

Recurso en `studio.media` conserva kind=video y path/sha256/name/duration/size existentes; campos aditivos **temporal_map** (manifiesto v1) y **temporal_manifest_sha256** se validan y consumen en AssetFrames/PreparedTimeline, biblioteca/inspector y recibo. Dataset `sources.{scientific_revision}` y CalculationResult reconstruidos deben corresponder exactamente a su revisión original; se conservan mapas antiguos cuando cambia la revisión actual. El renderer sigue siendo studio_scene_v1 sobre video seguro, sin nuevo motor científico.

Manifiesto: fuente/citación/URL, variable/unidades/región, cartographic_settings congelados, scientific_revision/scientific_identity, source_records con fecha/banda/archivo/hash, intervals con start_frame/end_frame exclusivos/source_index/date, fps=30, total_frames/duration/resolution, generated_at/state, video_sha256, NoData y reglas de representación. Intervalos contiguos, fechas estrictamente crecientes observadas, sin interpolación. Un solo recurso visible; miniatura interna no crea una entrada por fecha. Calendario comparte índice CFR del decoder; recorte/repetición/último cuadro conservan observación real y exportación declara intervalos globales en scientific_calendar. Movie clock usa el cuadro actual, no redondea a una fecha futura.

Preparación privada por proceso, progreso/cancelación cooperativos y revisión sellada. Publicación explícita añade recurso/escena por WorkspaceSession.commit tras preflight/autosave; fallo/cancelación no publica documento parcial. Recursos incompletos no insertables; originales y productos anteriores no se sobrescriben. Contain obligatorio. MP4 opaco del compositor con inset/overlays incrustados: 4b debe integrar capas alfa reales y overlays independientes antes de anunciar edición cartográfica plena. Proyectos/medios sin los campos aditivos mantienen su comportamiento anterior.

Unittest existente, tests de reproducción antes del arreglo, AppTest para navegación/state y Chrome CDP para interacciones/capturas. Fixtures sintéticos identificados; resultados reales reutilizan caché existente sin reauditar ciencia. Matriz A–F de la sección 18 y tamaños 1920×1080, 1366×768 y 768 px. Preview de cuadros comparte renderer; comprobación audiovisual usa MP4 real, con tolerancia de compresión, no igualdad PNG/H.264 byte a byte.

Fuentes de framework: documentación instalada de Streamlit 1.65, `references/session-state.md`, `testing.md` y `custom-components-v2.md`; contratos públicos https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state y https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest. Se reutiliza el wrapper público aislado existente. No dependencia nueva.

Riesgos: divergencia de proyección/versiones; pérdida por regeneración; calendario alterado por trim/loop; publicación parcial; recursos faltantes; caché ilimitada. Cada uno requiere pruebas antes del cierre del incremento pertinente. El plan no implica que clips/audio independiente/mapas separados estén ya implementados.
