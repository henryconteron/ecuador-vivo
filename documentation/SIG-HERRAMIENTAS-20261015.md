# SIG · herramientas y organización · 15 octubre 2026

Cuarto incremento de `SIG-ADAPTACION-OPEN-GEOS-20261015.md`. Alcance: organizar
funciones existentes, mejorar la lectura repetida de fuentes ráster e incorporar
capacidades vectoriales pequeñas verificables; no instalar ni portar GeoLibre/
RustGIS completos. Registro activo: **v9**.

## Contrato de diseño y comparación

Mantener azul profundo, jade, ventanas de papel, tipografía del SIG y mapa
dominante. Separar tareas de navegación, entrada, procesamiento, tiempo y salida.
Capas/Referencia/Propiedades/Atributos siguen siendo ventanas locales, no tareas
analíticas. No añadir botones sin implementación ni columnas permanentes.

- GeoLibre, commit `5e8da6e91122565c9a8891a4e79a7fd215873adf`:
  `apps/geolibre-desktop/src/components/layout/toolbar/AddDataMenu.tsx` separa
  archivos/servicios/nube/bases; los descriptores no son los ejecutores.
  `packages/processing/src/vector-tools.ts` incluye centroides y convex hull.
- RustGIS, commit `3f9437739babf6b334e9cef77fa56eb95142992f`:
  `crates/ui-egui/src/ribbon.rs` agrupa tareas en cinta;
  `crates/analysis/src/tools.rs` describe herramientas, incluida envolvente y
  conversión de geometrías a puntos con opción interior.
- Adaptación propia: cinco grupos, catálogo de procesamiento con filtros y
  requisitos, ejecutores Python existentes. No se copiaron implementaciones ni
  recursos de estas referencias, ni se cambiaron sus licencias. GeoLibre usa MIT
  y RustGIS Apache-2.0; cualquier futura reutilización literal debe conservar
  los avisos exigidos. No se declaran equivalencia algorítmica ni paridad completa.

## Organización implementada

| Grupo | Responsabilidad visible |
|---|---|
| Mapa | Navegar, identificar, medir aproximadamente, restablecer ventanas |
| Datos | Agregar archivos y abrir el asistente científico existente |
| Análisis | Catálogo único; accesos Vectorial/Ráster filtran ese mismo catálogo; resultados |
| Serie temporal | Preparar observaciones, periodo/duración, paleta y reloj existente |
| Salida | Formato del video y exportación explícita de capa |

Catálogo: **15 operaciones reales: 11 vectoriales y 4 ráster**. Cuatro vectoriales
son nuevas; las otras once ya existían. Agrupadas en Proximidad, Superposición,
Geometría, Medición, Atributos y Ráster. Búsqueda tolerante a tildes, filtro por
familia, explicación del requisito cuando no hay datos. El catálogo no lee
geometrías ni píxeles para calcular disponibilidad. Esta comprobación es básica
(tipo/cantidad); CRS, geometría, máscara, alineación y variables se validan en el
formulario/ejecutor. No equivale todavía a un registro completo de capacidades.

`studio_sig_tool_catalog.py` comparte etiquetas/identificadores con formularios;
seleccionar una herramienta solo preselecciona la operación. No ejecuta sin
«Calcular en segundo plano» y, al terminar, «Incorporar resultado». Rechaza eventos de versión obsoleta. El catálogo
se cierra antes de abrir el formulario para evitar solaparlos; Escape devuelve
el foco al disparador. Su ventana reutiliza movimiento, tamaño y límites locales.

## Cuatro herramientas nuevas y corrección geoespacial

1. **Centroides:** centro geométrico por entidad en el CRS proyectado elegido;
   puede quedar fuera de un polígono cóncavo o dentro de un hueco.
2. **Puntos interiores:** punto representativo de GEOS por entidad. Para polígonos
   se sitúa dentro de la geometría; no se presenta como su centroide.
3. **Envolvente convexa:** una por entidad, no de toda la capa. Entradas puntuales
   o lineales pueden producir puntos/líneas; no inventar un polígono.
4. **Extraer contornos:** bordes exteriores e interiores de Polygon/MultiPolygon.
   Rechaza capas con otras geometrías, sin omitir entidades silenciosamente.

Las tres primeras requieren CRS proyectado en metros, con área de uso compatible;
se rechazan grados, Web Mercator y proyecciones conocidas fuera de su territorio.
No se elige UTM automáticamente para todo Ecuador y Galápagos. El usuario debe
escoger una proyección apropiada; validar área de uso no garantiza distorsión cero.
Contornos es una operación topológica, sin distancias; trabaja en CRS84.

Se conserva el original, los atributos (incluidos cero/null), identificadores y
registro científico. Cada resultado es una fuente nueva con huellas, entradas,
fecha, motor, método y CRS. Reabrir/exportar verifica la procedencia. Manual primario:
[Shapely — centroid y representative_point](https://shapely.readthedocs.io/en/stable/manual.html#object.representative_point).

**Exportar capa** permite GeoJSON y, cuando existe, original vectorial; para ráster
descarga el GeoTIFF nativo, no el PNG de pantalla. No publica ni sustituye el envío
a Studio. Es exposición del exportador existente, no un motor de exportación nuevo.

## Cierre v8: coherencia, trabajos y presentación ráster

Vector y las operaciones ráster de cálculo envían el trabajo a un proceso Python
local independiente. **Comparar fechas** conserva su acción inmediata de
presentación. Procesos muestra avance cada 2 s sin volver a dibujar ni serializar
el mapa mientras calcula. Cancelar es cooperativo entre entidades/bloques; una
llamada GEOS individual o la lectura/validación inicial deben finalizar. El
proyecto no cambia hasta **Incorporar resultado**. Al aceptar se verifican
huellas, proyecto e insumos, y solo se fusiona la capa derivada con el estado
actual; se conservan vista, nombre, escenas y ediciones. Los trabajos pendientes
se pueden recuperar al volver a Procesos en el mismo proyecto. No hay retención
automática ni borrado de resultados.

La disponibilidad del catálogo usa geometría, variables, unidades y cuadrícula
de los metadatos ya registrados; no inspecciona píxeles para dibujar el menú.
La validación exacta sigue en el ejecutor. No es un inventario universal ni
garantiza que cualquier par de datasets sea compatible.

Cambiar la paleta de una serie conserva las instancias de capa y fuente; solo
actualiza las imágenes de presentación cuando están listas, manteniendo la
anterior mientras carga. No interpola ni altera los valores nativos o su escala.

### Evidencia v8

- Build Vite: 258 módulos; JS 539,84 kB (gzip 156,43), CSS 37,08 kB (gzip 7,79).
- 37 pruebas Node, TypeScript y build aprobados; estado del encabezado queda
  «Guardado» al cambiar de herramienta y reserva actividad para acciones reales.
- 21 pruebas Python de jobs/análisis/geometría/capacidades y 52 de interfaz,
  serie, presentación y soporte SIG; ambas tandas terminaron OK.
- Navegador 8534: Extraer contornos en Galápagos terminó como resultado listo,
  se incorporó y apareció en la leyenda. Deshacer retiró la capa y el guardado
  confirmó el retorno a la lista original. Inicio, Studio, Recursos y SIG fueron
  observados: marca de montaña común y azul/jade; Inicio y Recursos conservan
  papel crema para lectura y lienzo.

## Evidencia v7 (antecedente)

- TypeScript y build Vite aprobados. Activos `sig-workbench-v7.js/css`:
  JS 539,43 kB (gzip 156,29); CSS 37,02 kB (gzip 7,78). Sin dependencias nuevas.
- **34 pruebas Node**: cámara, historial, búsqueda, geometría de ventanas,
  caché, agrupación temporal y filtros/cinco tareas.
- **82 pruebas Python focalizadas**, no la suite completa del repositorio:
  `test_sig_workbench_design`, `test_sig_map_ui`, `test_sig_tool_catalog`,
  `test_sig_geometry_tools`, `test_sig_vector`, `test_sig_raster`,
  `test_sig_protocol`, `test_sig_series`, `test_sig_interaction_performance`,
  `test_sig_series_activation`, `test_sig_series_visibility`,
  `test_sig_workbench_refinement`. Última ejecución conjunta: 51,167 s, OK.
- Pruebas nuevas rojo→verde: operaciones desconocidas antes de implementar;
  polígono métrico con hueco (centroide fuera, punto interior dentro), hull conocido,
  contorno con huecos, CRS inadecuado, rechazo de entrada no poligonal, receta
  adulterada, originales/calendario/escenas intactos y exportar/reabrir.
- Mutación deliberada del guard de disponibilidad: invertir `not available`
  hace fallar el lanzamiento válido; guard restaurado y pruebas verdes.
- AppTest recorre seleccionar Extraer contornos → ejecutar → nueva capa →
  exportación GeoJSON disponible; evento obsoleto rechazado sin mutación.
- Navegador real 8534: v7 cargado; proyecto propio de QA con tres referencias,
  búsqueda «contornos», operación preseleccionada, ejecución y cuarta capa
  `Extraer contornos.geojson`. Recargar y abrir la copia desde Inicio conserva el
  resultado. No se editaron pilotos. Se conserva el borrador de QA
  `borrador-studio-20261015-113124-481cd099.json`.
- Filtro Ráster muestra cuatro operaciones con requisito GeoTIFF; «envolvente»
  muestra «1 herramienta»; Escape colapsa el catálogo; elegir Centroides cierra
  el catálogo antes de abrir el formulario nativo. Buscar «geometria» también
  devuelve Intersección porque su descripción incluye «geometrías»: intencionado.
- Comprobación DOM de límites a 320/768/1024/1440 px (alto 800): ventana dentro
  de su mapa, anchos 294,4/352/352/352; alto se adapta al mapa. Se restablece el
  tamaño normal. No constituye auditoría WCAG integral ni prueba de todos los
  formularios en móvil. Captura final fuera de producción, carpeta de auditoría.
- Evidencia visual: `_local/maintenance/revisiones-20261015/referencias-sig/sig-herramientas-v7.png` (ubicación consolidada).
  Conserva el SIG real con las cuatro herramientas nuevas visibles. Entre los
  20 errores recientes consultados no hubo errores de origen 8534 posteriores
  a 16:30 UTC. Los 403 de telemetría del controlador son externos; no se eludieron.
  Revisión de espacios del diff aprobada; advertencias LF/CRLF no son fallos.

## Incremento v9 · verificación ráster rápida sin saltarse cambios

Una serie temporal podía volver a leer el contenido completo de cada GeoTIFF para
calcular su SHA-256 en cada rerun, incluso si el archivo no había cambiado. El
verificador ahora conserva hasta 256 huellas por ruta y las reutiliza solo cuando
coincide la revisión del archivo: identidad, dispositivo, tamaño, mtime y
ChangeTime de Windows (ctime en otros sistemas). En caché fría calcula SHA-256 y
vuelve a comprobar la revisión al terminar; cualquier cambio invalida la entrada
y exige recalcular el hash. El confinamiento del almacenamiento, la comprobación
de contenido y los metadatos del original siguen vigentes. No se cachea el
resultado científico ni se altera el ráster.

Prueba de regresión: un GeoTIFF modificado con el mismo tamaño y mtime restaurado
debe invalidar la huella y rechazar los bytes adulterados. Pruebas focalizadas de
raster + refinamientos: 34 casos aprobados, incluida esta regresión. Sin benchmark
de un raster grande, la aceleración demostrada se limita a evitar lecturas de hash
redundantes; no implica acelerar el warp, las estadísticas exhaustivas de
importación ni el acceso COG remoto.

## Límites y continuación

No se portaron globo 3D, edición vectorial general, conectores de bases de datos
ni todos los formatos de referencia. Siguen pendientes trabajos largos
con cancelación inmediata dentro de una llamada GEOS, disponibilidad completa
para todos los datos, acceso a COG remotos por rangos y ventanas, y tiles/índices
para grandes vectores. La cancelación actual espera entre entidades/bloques y la
paleta mantiene las capas pero debe volver a obtener sus imágenes de presentación.
No hay benchmark nuevo de FPS, RAM ni latencia pesada; ejecutar análisis sigue
utilizando Python.
No se renderizaron videos, ni se cambiaron plantillas o fórmulas de los pilotos.
Sin commit/push/publicación. Se archivaron solo los cuatro archivos de borrador
creados durante la inspección (incluida una versión de recuperación) en
`_local/video-studio/archives/sig-ui-qa-20261015.zip` y el archivo posterior de
sesión en `sig-ui-qa-followup-20261015.zip`; los proyectos guardados previamente
no se tocaron.

## Skills y referencia de procedimiento

frontend-design/frontend-ui-engineering: jerarquía por tareas, marca conservada,
ventanas locales con foco/teclado. developing-with-streamlit: ejecución explícita
y estado del componente. incremental-implementation/test-driven-development:
incremento acotado y comprobaciones rojas/verdes. geomaster: separación de
geometría, proyección y presentación, advertencias y procedencia.

Referencia del procedimiento geomaster, registro consultado el 15/10/2026,
última revisión disponible 02/09/2026, sin DOI de revista indicado:
Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026).
*Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents*.
[arXiv:2609.00065](https://doi.org/10.48550/arXiv.2609.00065).
Esta referencia documenta el apoyo metodológico, no valida por sí misma los
resultados geoespaciales ni reemplaza pruebas/documentación de GEOS/PROJ.
