# Limpieza e Inicio de Ecuador Vivo Studio · 11–12 octubre 2026

## Resultado y alcance

Una sola instalación operativa de Studio + SIG en **http://127.0.0.1:8534/**. El acceso `Abrir editor de videos.vbs` utiliza `production/video_studio/launch.ps1`, actualizado al mismo puerto. El panel personal de la web, 8511, se conserva separado.

Inventario completo de metadatos de archivos y carpetas, sin seguir junctions/symlinks ni leer/hidratar el contenido de todos los rásteres. No equivale a una auditoría semántica manual de cada archivo. Las dependencias de la aplicación, proyectos y pilotos se revisaron por separado.

| Medida | Antes | Después |
|---|---:|---:|
| Tamaño lógico inventariado | 22.839.182.245 bytes | 7.276.601.864 bytes |
| Archivos | 148.740 | 25.421 |
| Carpetas reales recorridas | 71.025 | 3.711 |
| Proyectos JSON en carpeta activa | 662 | 8 |

Reducción aproximada: **15,56 GB decimales / 68 %**. Tamaño lógico, no medición de bloques físicos liberados: OneDrive, enlaces y cachés pueden producir diferencias respecto al Explorador. Los inventarios no incluyen dos veces los destinos de enlaces ni sus propios informes posteriores.

## Qué se retiró

- 161 perfiles desechables `tmp/sig-studio-chrome-*` y `tmp/ux-redesign-chrome`: 15.046.863.026 bytes. Objetivos exactos validados, sin referencias de proyectos protegidos ni procesos activos antes de borrar. Son cachés regenerables, no perfiles personales del navegador.
- 25 MP4 intermedios inequívocos y 597 capturas QA del antiguo monitor: 470.107.263 bytes. Se conservaron maestros publicados, voces, guiones, imágenes satelitales, catálogos y datos originales. Estos derivados se pueden volver a generar; no se conservaron copias idénticas de las capturas eliminadas.
- 654 JSON anteriores de proyectos, **archivados con autorización adicional explícita**, incluidos autoguardados ambiguos y proyectos personales. No se destruyeron: ZIP verificado por tamaño y SHA-256 de cada entrada antes de retirar cada original.
- 19 instancias antiguas de Studio cerradas. Instancia 8534 reiniciada para cargar los módulos corregidos, tras comprobar identidad de procesos y ausencia de FFmpeg activo. Panel personal 8511 conservado.

No se retiraron los 43 trabajos adicionales de QA propuestos ni el ráster sintético `tmp/sig-engine0/fixtures/large-striped.tif`: la herramienta bloqueó esa etapa adicional y no se intentó eludir el bloqueo. Los candidatos están documentados; siguen existiendo.

## Restaurar un proyecto antiguo

Respaldo: `_local/maintenance/proyectos-anteriores-20261011-234719.zip` (12.668.915 bytes).

SHA-256 del ZIP: `08888869d4589a4d97ef1688d2f4f276f0a8111aaf25b6c6f34fac541be50824`.

1. Abrir el ZIP en el Explorador.
2. Entrar en `_local/video-studio/projects` dentro del ZIP.
3. Copiar únicamente el JSON deseado a `_local/video-studio/projects` de la instalación.
4. Volver a Inicio y actualizar. No sobrescribir un piloto actual.

El ZIP conserva documentos y autoguardados, no duplica sus grandes fuentes. Las dependencias compartidas se conservaron en su ubicación para hacer posible la recuperación. El JSON adyacente al ZIP enumera rutas, tamaños y hashes originales.

## Qué se conservó expresamente

- Los ocho proyectos piloto recientes, sus ocho MP4 finales, recibos, mapas editables, calendarios, fuentes y recursos. 8/8 aperturas, 8 hashes MP4 y 8 hashes de documentos coinciden después de limpiar; ninguna referencia directa faltante.
- La versión actual de `production/video_studio` y el paquete SIG editable con sus recursos compilados. 82 de 87 módulos no-test resultan alcanzables desde las entradas: nombres antiguos no justifican su eliminación.
- Entorno Python vigente, herramientas de desarrollo, web principal, licencias y avisos.
- `.git` (~1,59 GB), recuperación histórica y originales CHIRPS 2024 (~1,51 GB), límites nativos y preparados. No se reescribió historial ni se ejecutaron reset/clean.
- Maestro sísmico v6 publicado, fuentes únicas y paquetes ASR existentes (~403 MiB), reutilizables para futuros subtítulos sin otra descarga grande.

## Inicio corregido

- Sesión nueva sin proyecto cargado: «Sin proyecto abierto». Abrir SIG/Studio conduce a elegir o crear.
- Catálogo completo, búsqueda por nombre/variable/archivo, orden y páginas de 12. Los ocho pilotos quedan en una sola página. Se excluyen archivos `.previous.json` del catálogo activo.
- Miniaturas opcionales; su fallo no bloquea el botón Abrir. Importar un JSON guarda una copia local que aparece en Inicio.
- Cerrar proyecto no borra su archivo. Volver a Inicio durante una sesión conserva el proyecto elegido hasta cerrarlo explícitamente.

## Verificación y límites

Cinco reproducciones fallaron antes de corregir. Pasaron 22 pruebas focalizadas finales (9 nuevas de Inicio, 5 Home y 8 de documento), otras 10 de preparación y los 8 pilotos reales. Revisión independiente: 9/9 nuevas aprobadas. Dos pruebas SIG previas conservan selectores obsoletos (`sig_import_format`, `home_new_sig`); no se declara toda la suite verde.

El navegador denegó acceso a localhost para revisión visual. Se respetó ese límite: sin CDP, otro navegador ni captura alternativa. La revisión estética en navegador queda pendiente; los controles de estado se verifican con AppTest. Salud HTTP del servidor 8534 comprobada.

Evidencia en `_local/maintenance`: inventarios `cleanup-20261011-before-fast` / `cleanup-20261011-after`, guard inicial y `cleanup-20261011-pilot-guard/after-cleanup.json`, recibo de archivo, manifiestos de retiradas y comprobación de Inicio. Scripts de mantenimiento requieren PowerShell >= 7.2 y no son launchers de la app.

## Próximo paso aprobado, todavía no implementado

Recursos explicativos integrados, pista de voz independiente y subtítulos. Reutilizar el mezclador actual, Three.js local y ASR ya descargado; empezar por un recorrido completo de franja fría y El Niño. No crear otro laboratorio, entorno Python, motor de cálculo ni catálogo paralelo.
