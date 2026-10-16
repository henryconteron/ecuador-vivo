# Ecuador Vivo — estado vigente (2026-10-16)

## Consolidación y entrega a GitHub · 16 octubre 2026

Auditoría: `AUDITORIA-PUBLICACION-20261016.md`. Producción audiovisual y guiones
no publicados quedan locales; no agregarlos al preparar esta entrega. Se
conserva una sola raíz y compilación SIG actual. Corregidos los contratos de
presentación/publicación de CSV geográfico, con sus pruebas de regresión.
No reanudar mejoras de interfaz durante esta operación de respaldo.
Verificación final: 747 pruebas Studio sin fallos (una omitida), 41 Python de
la web, 22 del panel privado, 37 Node del SIG, comprobaciones web, tipos y build
correctos. Auditoría del índice sin rutas privadas, medios nuevos ni firmas
de credenciales. Servidor local en 8534 comprobado con HTTP 200.

## Proyecto consolidado · mejoras pausadas por el usuario

Segunda limpieza finalizada: `LIMPIEZA-VERSIONES-20261015.md`.
495 archivos reemplazados retirados, aproximadamente 963 MiB lógicos.
Videos y guiones vigentes: `videos/README.md`. Conservadas las diez piezas
y los dos episodios de El Niño; 47 pruebas correctas. El ZIP de temporales
de la primera consolidación fue eliminado por petición de conservar solo lo actual.

Una única carpeta activa: `C:/Users/JHONY CONTERON/OneDrive/Documentos/GitHub/fallas-ecuador`.
Abrir con los lanzadores de esa raíz. Guía: `VERSION-ACTUAL.md`; resultado y
recuperación de la limpieza: `CONSOLIDACION-20261015.md`. Web, Inicio, SIG,
Studio y Recursos se conservan en la misma instalación. Compilación SIG única
`sig-workbench.js/css`, sin bundles antiguos activos. Checkpoint funcional v9.
Las revisiones de este chat están en `_local/maintenance/revisiones-20261015/`;
los insumos auxiliares oceánicos están en `_local/scientific-inputs/enso/`.
No continuar añadiendo funciones durante esta pausa.

## SIG · contraste GeoLibre/RustGIS · 15 octubre · incremento vigente v9

**Cierre previo: v8; avance actual: v9.** Grupos Mapa/Datos/Análisis/Serie temporal/Salida;
catálogo flotante de 15 operaciones reales con búsqueda/familia/requisitos.
Nuevas: centroides, puntos interiores, envolvente convexa por entidad y contornos
con huecos. CRS adecuado exigido, originales/atributos/procedencia conservados.
Exportar capa expone GeoJSON/original y GeoTIFF nativo, separado de Studio.
Los análisis corren en un proceso local separado, con progreso, cancelación
cooperativa y aceptación manual. El resultado se incorpora sin pisar el encuadre
ni las ediciones concurrentes. Cambiar paleta ráster conserva capas y fuentes.
El logotipo montaña común se usa en Inicio, SIG y Studio; Recursos comparte
paleta e iconografía y conserva papel crema para el lienzo editorial.
Informe: `documentation/SIG-HERRAMIENTAS-20261015.md`.
37 pruebas Node y 73 Python focalizadas en v8, TypeScript/build aprobados.
v9 reutiliza hasta 256 SHA-256 ráster únicamente mientras coincide el token de
revisión del archivo. Una edición con mismo tamaño y mtime restaurado invalida
la huella y es rechazada. Pasaron 34 pruebas Python focalizadas de raster y
refinamientos; falta benchmark con ráster grande.
Navegador 8534: contornos reales calculados e incorporados; la capa se retiró
después de la prueba y el guardado confirmó su salida. Inicio, Studio, Recursos
y SIG inspeccionados. Queda pendiente el acceso remoto a COG por rangos, cobertura
detallada de servicios y benchmark; el catálogo no es universal. No cambié la UI
ni los proyectos/pilotos en este incremento de rendimiento.

Antecedentes v5/v6/v7/v8 (activo: v9):

Auditoría de fuente fijada a GeoLibre `5e8da6e` y RustGIS `3f943773`, sin
instalarlos ni ejecutar REA sobre código fuente. Informe y matriz de alcance:
`documentation/SIG-ADAPTACION-OPEN-GEOS-20261015.md`.
Añadidos al SIG existente: buscador de comandos Ctrl+K, historial local de
encuadres (40) y medición esférica de distancia/área mediante bocetos efímeros.
Conservados OpenLayers, estilo vigente, operaciones científicas y puente Studio.
Segundo incremento: cámara local inmediata, persistencia tras 400 ms de quietud
y confirmación de gestos antes de acciones; una capa lógica por calendario activo,
observaciones desplegables/buscables y visibilidad conjunta en una transacción.
Registro histórico v6: `sig-workbench-v6.js/css`. Sin dependencias nuevas ni cambios
de videos/pilotos. TypeScript/build, 31 pruebas Node y 33 Python focalizadas aprobados.
Instancia 8534 iniciada con permiso; **acceso al navegador ahora operativo**.
QA real: buscar sin tilde, medir línea/polígono, terminar/cancelar, Ctrl+K/Enter
y anterior/siguiente probados. Además serie real de 30 fechas: tres zooms → un
guardado, misma instancia y 30 construcciones sin aumento; selección de día 15,
visibilidad conjunta, paleta conservando escala, reproducción local y guardar
inmediatamente tras zoom comprobados. La revisión real detectó/corrigió el receptor
de los temporizadores del navegador, con regresión roja/verde. Capturas y límites
constan en el informe. Copias de QA conservadas; originales/pilotos intactos.
No equivale a portar ambos SIG completos: COG remoto por ventana y cobertura
completa de capacidades siguen pendientes. No se midieron FPS, RAM ni paridad
de rendimiento; no se renderizó video nuevo.
Sin commit/push/publicación ni limpieza; preservar cambios previos del usuario.

## Recursos científico · 13 octubre · implementación autorizada vigente

Recursos ahora abre mesa propia de autoría, biblioteca/propiedades flotantes,
seis plantillas, búsqueda/favoritos, objetos e ilustraciones CC0, guardar/reabrir
y envío explícito a Studio. Documento independiente: no pisa el video activo.
Cuatro editores instalados/conectados: Excalidraw, Fabric, React Flow, Ketcher;
conservan original editable más PNG compuesto. Manim en entorno separado,
sin panel de generación aún. Blender existente reutilizado, no un 3D general.
Motores diferidos, aproximadamente 1,05 GiB de archivos instalados nuevos.
Auditoría npm: 4 bajos, 0 moderados/altos/críticos tras overrides compatibles.

Informe completo y límites: RECURSOS-CIENTIFICOS-IMPLEMENTACION-20261013.md.
Pruebas AppTest/Node/compilación y render PNG real vertical/horizontal aprobadas;
36 hashes SIG/layout/render base intactos. Sin commit/push ni borrado de proyectos.
**No hay aceptación visual de navegador**: sigue denegado; no eludir. Los editores
React/WASM requieren prueba real. RC4–RC7 completos y video revisado pendientes.
SIG no se ha cambiado en esta implementación.
Instancia 8534 reiniciada sin tareas activas; health y fuente local 200,
cabecera nosniff correcta y log inicial de errores vacío. Recargar Ctrl+F5.

## Studio inmersivo / Inicio / Recursos · 13 octubre · segunda pasada vigente

Usuario rechazó el acabado anterior y pidió priorizar video, como organización
SIG, sin tocar SIG. Studio elimina columnas permanentes: herramientas arriba,
biblioteca/propiedades flotantes movibles y redimensionables, montaje recogido
por defecto y modo Solo video. Selección ofrece Editar sin abrir inspector al
seleccionar. Preferencias locales por pestaña, no en el documento científico;
no emiten comandos, no recalculan, no alteran plantillas ni video exportado.
Inicio asimétrico (Studio protagonista y SIG/Recursos horizontales); Recursos
con láminas mayores y jerarquía de colección. frontend-design aplicado con
contrato previo en `documentation/DISENO-ESPACIOS-20261013.md`.

51 pruebas Python y 5 Node aprobadas; JS y cuatro CSS parseados; 36 huellas
protegidas SIG/render/layout base idénticas. Navegador sigue bloqueado por
preferencia: falta aceptación visual real, no eludir mediante otros motores.
No commit, push, publicación, borrados ni dependencias nuevas.
Archivos nuevos: workspace_frontend/workspace_windows.js y su test Node.
studio_workspace.py y lista de recarga de app.py incluyen el módulo nuevo.
Instancia 8534 reiniciada después de comprobar ausencia de tareas activas;
health 200, errores de arranque vacíos. Script compuesto CCv2 completo pasa
sintaxis Node; 6 contratos/contraste revalidados tras los últimos ajustes CSS.
Recargar Ctrl+F5 para recibir esta segunda pasada, no las columnas anteriores.

## Inicio / Studio / Recursos · diseño editorial · 13 octubre · vigente

Usuario pidió usar frontend-design para mejorar toda la apariencia de esos tres
espacios dejando SIG exactamente como está. Contrato y entrega en
`documentation/DISENO-ESPACIOS-20261013.md`. Inicio con acciones claras,
accesos visuales y catálogo más limpio; Studio separa navegación de proyecto y
herramientas, con CSS consolidado (26.247 → 19.385 bytes), nuevo marco de lienzo,
inspector, biblioteca, montaje y ventanas nativas; Recursos con cabecera propia,
categorías/resúmenes y configuración/vista agrupadas. Reutiliza ilustraciones
locales, Segoe UI/Bahnschrift con fallback y paleta petróleo/turquesa.

Ningún motor, cálculo, plantilla exportada, proyecto ni archivo del SIG cambiado:
37 huellas protegidas iguales. Tema global intacto; selectores limitados a sus
superficies. 50 pruebas focalizadas aprobadas, sintaxis JS y cinco CSS correctos,
contraste del editor verificado; mutación de contraste detectada/restaurada.
**No hay aceptación visual de navegador**: preferencia guardada sigue bloqueada;
no eludir con headless o capturas indirectas. Falta captura humana tras recargar.
Sin commit/push, publicación ni limpieza.
Instancia 8534 reiniciada sin navegador ni renders activos: health 200, log
inicial vacío. Ctrl+F5 para recibir el marco nuevo de Studio.

## SIG · fluidez, herramientas compactas y paletas · 13 octubre · vigente v4

Usuario aportó capturas de oscurecimiento al hacer zoom y herramientas gigantes.
Se midió una serie real de 30 fechas: 182 verificaciones de ráster por gesto;
comando+payload caliente 1246,6 ms. Caché de recetas GDAL por SHA verificado y
pruebas nativas limitadas a cada operación (NTFS ChangeTime/identidad/stat, SHA
renovado entre operaciones) reducen esa etapa a mediana 172,8 ms. Gesto con
guardado en store temporal y propiedades: 278,0 ms; no latencia de navegador.
No se oculta el indicador ocupado mediante CSS ni se relaja la validación científica.

Herramientas ahora en ventana contextual no modal de 430 px, scroll interno y
fragmento propio: el mapa no se bloquea por el formulario. Sin selector de
herramienta/títulos duplicados. Abrir proyecto mantiene modal pequeño.
Se unificaron Preparar serie y Periodo/duración. Serie temporal → Paleta y estilo
abre Propiedades; cuatro paletas, opacidad atómica, escala común sin cambiar
nudos/NoData/cálculos. Selección conservada en configuración, snapshot, historial
y bundle verificado de Studio. Fuentes, pilotos y videos personales preservados.

**Registro activo v4** (`sig-workbench-v4.js/css`); sustituye v3/v2/v1 en registro,
sin borrar archivos ajenos. 102 pruebas focalizadas + 6 de callbacks de mapa,
19 frontend, typecheck/build y diff-check aprobados. Prueba de mutación de paleta
detectada/restaurada. AppTest de formularios, cierre, paleta, guardado y deshacer;
acabado visual real aún pendiente de captura por preferencia de navegador bloqueada.
Guía, diseño, medición y límites: `documentation/SIG-FLUIDEZ-HERRAMIENTAS-20261013.md`.
Componente real + assets v4 registrados con AppTest adicional; instancia local
8534 reiniciada sin abrir navegador, health 200. Recargar. Panel privado y Blender
de escritorio intactos; no había renders activos, solo estados `test-*` antiguos.
Sin commit/push, publicación, motores nuevos ni limpieza fuera de alcance.

## SIG · activación real del calendario · 13 octubre · vigente

La captura nueva confirmó que v2 sí cargó, pero el calendario no aparecía: la adquisición incorporaba fechas sin configurar `raster_time`, y el comando activo de una capa no elegía su observación. Ahora descargar/importar una serie configura el reloj canónico antes de guardar, cierra la preparación y abre el mapa. Seleccionar una fecha desde Capas o leyenda cambia `raster_date`; selector directo de fechas disponible junto a la barra flotante, sin reloj duplicado.

Se comprobó **en memoria, sin escribir el borrador**, el proyecto `borrador-studio-20261013-152033-4332f795.json`: NASA POWER / Precipitación corregida / 30 fechas / sin reloj. Recuperación automática al abrir SIG solo para un único producto compatible con tags verificados de admisión del proveedor; una transacción reversible, respeta deshacer durante la sesión y no descarga otra vez. Si hay varias fuentes o datos inválidos, no mezcla ni elige silenciosamente. Fuentes, archivos, métricas, pilotos y video conservados.

Bundle activo **sig-workbench-v3.js + sig-workbench-v3.css**. 62 pruebas Python SIG/serie aprobadas, 19 frontend, typecheck/build correctos. Prueba AppTest recorre apertura de descarga antigua → calendario → única imagen/escala común → clic en otra fecha → cambio real de imagen; no es una revisión visual con navegador. Mutación del guard de recuperación detectada y restaurada. Acceso visual automatizado sigue bloqueado por preferencia: no eludir ni afirmar captura del resultado. Sin commit/push/publicación ni borrados.

## SIG · ventanas flotantes y control temporal · 13 octubre · vigente

Capturas nuevas del usuario piden recuperar espacio del mapa. Capas, Referencia, Propiedades y Atributos ahora tienen accesos junto a Mapa/Análisis/Serie temporal/Salida. Ventanas no modales inicialmente cerradas, desplazables/redimensionables y tabla ampliable; sin columnas laterales ni tabla inferior permanentes. Control temporal compacto solo con serie preparada, fecha/extremos reales, anterior/siguiente, reproducción/pausa, zoom del intervalo de observaciones, configuración y comparación existente. Cerrar pausa y oculta, no elimina la serie.

Bundle activo **sig-workbench-v2.js + sig-workbench-v2.css**; reemplaza el registro v1, no volver a cargar v1 ni `index-u20`. Conservar un mapa/reloj, fuentes, cálculos, pilotos y plantilla de video. 42 pruebas Python y 19 frontend aprobadas, typecheck/build correctos. Controlador de ventanas probado con nodos unitarios en memoria, no mediante navegador. No nuevas dependencias, commit/push ni borrado. Guía: `documentation/SIG-VENTANAS-FLOTANTES-20261013.md`. Capturas recibidas validan el punto de partida; **acabado nuevo aún pendiente de captura tras recargar** porque preferencia de navegador sigue bloqueada. No eludirla.

## SIG · nueva mesa cartográfica · 13 octubre · último pase visual

Usuario pidió aproximar la interfaz a GeoLibre, RustGIS, ArcGIS y QGIS. Se sustituyó el marco anterior: cinta contextual con **Mapa / Análisis / Serie temporal / Salida**, paneles de Capas/Propiedades redimensionables, tabla ampliable, iconos SVG propios, escala cartográfica/norte y navegación compacta. Se consolidaron los estilos del marco en `frontend/src/workbench.css`; no volver a apilar temas sobre `map.css`. El motor, las fuentes, las métricas, los pilotos y la plantilla de video se conservan.

Bundle vigente del componente: **`sig-workbench-v1.js` + `sig-workbench-v1.css`**, rutas explícitas tanto en Vite como en `ecuador_vivo_sig_map/__init__.py`; evita persistencia del bundle `index-u20` por caché. Tareas y tamaños son presentación por instancia, no transacciones científicas. Divisores con ratón y teclado; responsive según ancho real del host, no solo la ventana.

41 pruebas Python SIG focalizadas y once frontend aprobadas; typecheck/build/npm audit correctos, sin nuevas dependencias. Instancia 8534 reiniciada sin renders activos, health 200; recargar Ctrl+F5. **Aceptación estética/DOM todavía pendiente**: acceso de navegador sigue bloqueado por preferencia guardada, usuario eligió enviar una captura. No inventar screenshots ni eludir el bloqueo con headless/otro navegador. Guía: `documentation/SIG-MESA-CARTOGRAFICA-20261013.md`. Sin commit, push, publicación ni borrado de datos. No afirmar equivalencia funcional completa con los SIG de referencia.

## SIG → Studio → Andes Pulso · incremento vigente · 13 octubre

Se aplicó jerarquía de herramientas/capas, paleta de la fuente, soporte nativo (CRS, paso de celda, banda/calibración), paneles móviles y filtro de resultados que impide etiquetar cálculos antiguos como propios de una serie nueva. Reproducción con precarga corta y caché de presentación acotada; no cambia cálculos. Vite actualizado por seguridad a 8.0.16, lockfile y compilación comprobados.

Studio prepara un ZIP **público diferente del paquete privado antiguo**, validando video/documento/originales/calendario y recalculando lluvia desde fuentes nativas. Panel personal permite importarlo como borrador privado y, mediante otra revisión explícita, incorporarlo a la web local. Andes Pulso tiene un visor de estas historias con mapa/fecha/escala, método, métricas, fuentes/licencias y descargas. El índice nuevo está vacío: no se publicaron pilotos, datos sintéticos ni contenido sin revisión. No duplicar todo el catálogo ni volver a crear otro laboratorio.

Guía y límites: `documentation/MEJORAS-GEOSPATIAL-20261013.md`. 26 pruebas Python focalizadas de SIG/evidencia/soporte, 22 del panel, cinco de caché y suite web (35 archivos/29 entradas) aprobadas. MP4 real sintético 1080×1920 → ZIP → borrador privado probado; se rechazan originales alterados. Typecheck/build, instalación sin scripts y auditorías npm/pnpm aprobados. UI aún **sin aceptación visual en navegador**: permiso humano concedido, pero acceso CUA denegado por preferencia guardada; no eludirlo.

Instancias reiniciadas/preparadas con autorización y sin renders activos: `http://127.0.0.1:8534/` y `http://127.0.0.1:8511/`, health 200. Recargar la aplicación. Pilotos y autoguardados preservados; sin limpieza, commit, push ni publicación. Pendientes: aceptación visual real, alojamiento para historias grandes, adaptadores para montajes ilustrativos/ENSO sin serie SIG sellada y conectores remotos con cobertura/licencias probadas. Esto no es equivalencia completa con QGIS/ArcGIS/GeoLibre.

## Blender integrado en Recursos · entrega vigente · 12 octubre

Usuario aprobó avanzar e integrar Blender ahora. **Recursos → Estudio 3D** crea el modelo orográfico real con cámara, relieve, luz, materiales, duración, condensación y precipitación ilustrativas. Render explícito en proceso separado, vista fija/prueba ligera/final, progreso y cancelación; no carga Blender al abrir Inicio. Receta acotada y `.blend` conservados; abrir en el lienzo, añadir escena o actualizar objeto preservando composición/textos/voz/subtítulos/otras escenas. Blender 4.5.4 LTS/Eevee local verificado con SHA oficial; no cuenta de pago, admin ni otro servidor/editor. SIG y cálculos originales no modificados.

- Ejemplo editable en Inicio/Mis recursos: **La montaña no fabrica agua**, `_local/video-studio/projects/recurso-3d-orografia-20261012.json`. Metadatos identificados como ilustración 3D local/NOAA, sin CHIRPS/fechas ficticias ni resultados científicos. Solo se actualizó el ejemplo propio tras igualdad byte a byte; snapshot anterior preservado. Ocho pilotos válidos, cero referencias directas ausentes; guard `_local/maintenance/cleanup-20261011-pilot-guard/after-blender-20261012.json` (17 JSON activos, incluidos autoguardados existentes; no se borraron).
- Videos reales de 10 s / 300 cuadros / 30 fps: `_local/resource-development-20261012/blender-proof-final/tiktok/video.mp4` **1080×1920**; `youtube/video.mp4` **1920×1080**. Decodificados enteros, tamaño/duración/hashes/cuadros críticos verificados; revisión visual offline vertical/horizontal. `verification.json` y `ui-verification.json` en esa carpeta. Sin narración. No se hizo aceptación visual de navegador: denegación previa vigente.
- **104 regresiones focalizadas iniciales correctas; 25 comprobaciones finales correctas** tras endurecer metadatos, progreso malformado, resolución y ruta Inicio → Estudio 3D. AppTest del producto real abre el lienzo y reemplaza sin mutar original; cancelación real limpia sus temporales. Prueba de mutación detecta eliminación del guard de cuadros. No se declara toda la suite del repositorio.
- Render final medido **1011,219 s (~17 min)**; composición Studio vertical/horizontal **137,546 / 158,666 s**. Caché por receta reutiliza productos idénticos. Un solo PNG temporal; sin cientos de fotogramas permanentes. El primer clip tuvo corrección explícita de dimensiones por redondeo del codificador, documentada en recibo; worker/regresión ya conservan dimensiones exactas. No afecta datos científicos.
- Motor activo ocupa ~1,14 GiB en `_local/video-studio/tools/blender-4.5.4-windows-x64`. Permanece ~0,86 GiB de instalación fallida 4.5.14 en AppData: borrado automático bloqueado por política; no se eludió. No hubo limpieza adicional de trabajo personal.
- Instancia reiniciada: **http://127.0.0.1:8534/**, procesos **22016/19620** del 12 octubre; health 200 y log de errores vacío. Recargar para usar el nuevo modo. El panel 8511 no se modificó/reinició y no estaba escuchando en la comprobación final.
- Guía, decisión y límites: `documentation/RECURSOS-BLENDER-20261012.md`. Plan aprobado: `documentation/RECURSOS-CREADOR-2D-3D-20261012.md`. Falta aprobación estética humana, transparencia, editor libre de mallas/keyframes/GLB y modelos adicionales (El Niño, infiltración/fallas). No afirmar Canva completo ni simulación física. Sin commit, push o publicación.

## Inicio ligero y creador de Recursos · entrega vigente · 12 octubre

- Inicio reorganizado: Crear/Abrir arriba; SIG, Studio y Recursos con tres portadas originales WebP ligeras. Se eliminó el render de un proyecto reciente usado de portada; motores de datos/descarga/video aplazados hasta su ruta. Abrir SIG entra directamente a un borrador con referencias, sin formulario de nombre obligatorio. Proyectos recientes siguen buscables/paginados, miniaturas optativas.
- Recursos: seis plantillas, lienzo desde cero y Mis recursos. Edición en el mismo lienzo de Studio, 21 formas/símbolos locales y Guardar recurso para almacenar una copia reutilizable de una escena. Abrir una plantilla/diseño independiente guarda la copia de trabajo del video anterior; no lo convierte ni borra. Inserción con IDs propios y adaptación proporcional al perfil. No copia voz/subtítulos/datos científicos a la biblioteca ilustrativa; rechaza mapas/resultados desacoplados.
- Medición AppTest del servidor, tres procesos fríos: mediana Inicio 4,632 → 2,430 s (47,5 % menos); reruns 0,463 → 0,322 s. Opacidad de serie de 30 observaciones agrupada en una sola transacción validada: medición focalizada previa 22.137 → 937,6 ms. PNG reutilizado sin recompresión, conservando verificación nativa y máscara. No son benchmarks de navegador ni equivalencia de velocidad con GeoLibre.
- **137 pruebas focalizadas finales aprobadas**, TypeScript typecheck/build y sintaxis JavaScript correctos; guard posterior de ocho pilotos válido, cero referencias ausentes. Diez JSON activos actuales (ocho pilotos + dos autoguardados existentes), todos preservados. Navegador sigue denegado: revisión offline/AppTest, no aceptación visual de DOM/responsive. Sin nuevas dependencias, limpieza, commit, push ni publicación.
- Detalles, fuentes, uso y límites: `documentation/INICIO-RECURSOS-SIG-20261012.md`; arte/prompt: `documentation/PORTADAS-ECUADOR-VIVO-20261012.md`. No se promete Canva completo, nuevas herramientas analíticas masivas, ASR automático o editor 3D en este incremento. La entrega de voz/subtítulos inferior se conserva.
- Instancia vigente: **http://127.0.0.1:8534/**, reiniciada el 12 octubre a las 02:23 (Guayaquil), procesos 16856/21548. Health 200 y log de errores vacío; panel web 8511 intacto, health 200. Recargar el navegador para ver los cambios. Los procesos/horarios de entregas inferiores son histórico.

## Recursos, voz y subtítulos · última entrega · 12 octubre

- Nueva galería Recursos dentro de la misma aplicación, accesible desde Inicio/Studio. Seis esquemas 2D animados, editables y con fuentes primarias verificadas; inserción como escena o superposición sin cambiar los registros científicos. Ocho perfiles existentes, sin instalar paquetes ni otro motor.
- Studio → Voz y subtítulos: importar MP3/WAV/M4A, grabar micrófono, editar inicio global/recorte/duración/ganancia/silencio/repetición; importar, escribir y descargar SRT/VTT; tamaño, posición, tipografía, colores y fondo editables. Audio y subtítulos salen en MP4 con el mismo reloj a 30 fps; captions visibles también en el lienzo, caché invalidada por track y posición global.
- Corregido guardado de audio en ResourceProofs y exclusión de audio de selectores de imágenes. Guardado real, recuperación y deshacer/rehacer verificados. Preflight revisa todos los subtítulos antes de crear la exportación; no corta palabras en silencio. ASR local preservado, pero transcripción automática y puente 3D aún pendientes.
- Demo vertical 1080×1920 / 30 fps / 9 s: `_local/resource-development-20261012/demo/recursos-demo.mp4`. Solo recursos/subtítulos de ejemplo, sin inventar voz del usuario. Exportación separada de prueba también verificó AAC 48 kHz y cuadros decodificados. Ocho pilotos originales intactos; guard posterior `_local/maintenance/cleanup-20261011-pilot-guard/after-resources-20261012.json`. Hay un autoguardado adicional del usuario, preservado.
- Verificación final: **115 pruebas focalizadas aprobadas** (73,4 s), sintaxis JS compuesta válida y AppTest de Inicio → Recursos sin proyecto → Studio/formulario correcto. Una mutación de validación temporal fue detectada por su test. Navegador sigue denegado: AppTest y renders locales comprobados, no afirmar aceptación visual en navegador. Guía y límites en `documentation/STUDIO-RECURSOS-VOZ-SUBTITULOS.md`. Sin commit, push, nuevas dependencias ni nuevas limpiezas.
- Studio 8534 reiniciado a las 00:47 del 12 octubre: procesos 18104/9532, health 200 y log de errores vacío. Panel web 8511 preservado, health 200. Demo completa: 270 cuadros decodificados / 9 s, SHA coincide con recibo, 342.698 bytes.

## Limpieza y catálogo de Inicio · última entrega

- Carpeta inventariada de 22,84 a 7,28 GB lógicos: 161 perfiles QA y 622 derivados de monitor retirados. 654 proyectos antiguos archivados con permiso en `_local/maintenance/proyectos-anteriores-20261011-234719.zip`; cada entrada verificada antes de retirar originales. Solo ocho pilotos recientes en proyectos activos, intactos y revalidados. Fuentes compartidas, maestros publicados, ASR, entorno, web e historial Git conservados.
- Sesión nueva sin ejemplo de lluvia precargado; Inicio con catálogo completo, búsqueda, paginación, apertura independiente de miniatura y cierre sin borrar. 22 pruebas focalizadas finales + 10 preparación aprobadas; revisión independiente 9/9. Dos pruebas SIG previas con selectores obsoletos siguen registradas, sin declarar suite general verde.
- Acceso único vigente **http://127.0.0.1:8534/**; launcher alineado al mismo puerto, 19 Studio anteriores cerrados, 8534 reiniciado. Panel personal 8511 conservado. Navegador denegó verificación visual: no se eludió; aceptación estética pendiente.
- Los 43 jobs adicionales y el ráster sintético propuestos para retirada NO se borraron: herramienta bloqueó esa etapa. Informe preciso, recuperación y límites en `documentation/LIMPIEZA-STUDIO-20261011.md`.
- Trabajo aprobado de Recursos + voz/subtítulos: implementado en la entrega superior. Existe ASR local reutilizable; no volver a descargarlo por defecto. No reiniciar auditorías ni recrear perfiles persistentes por cada test.

## Acabado SIG/Studio y reproducción temporal (11 octubre, posterior al preparador)

- Corregida la vista rectangular/pixelada: SIG inicial y reproducción diferida usan ahora el polígono elegido, contorno/provincias y bilinear configurado. Se conserva la máscara finita nativa y se recorta después de suavizar. Datos fuera del territorio quedan transparentes; las otras series no aparecen a través de NoData. Colores compartidos con lluvia, escala propia de cada variable. Nuevas importaciones opacas; opacidades ya editadas no se pisan.
- La temperatura/viento y demás series numéricas compatibles usan la composición editorial editable de lluvia: titular, fecha, contador, mapas, leyenda y créditos reales. No se inventan métricas generales ni se reutilizan fórmulas de precipitación para otra variable. El envío idéntico reutiliza su bundle verificado y conserva ediciones de composición del usuario. Galápagos nacional usa la misma fuente/fecha en un inset declarado a distinta escala cuando hay cobertura nativa.
- Prueba real final: **Septiembre 2026 · temperatura · diseño corregido**, proyecto `_local/video-studio/projects/andes-pulso-temperatura-septiembre-2026-20261011-200238.json`. 30 fechas NASA POWER T2M, 1–30 septiembre 2026; muestra de 6 s, 1080×1920, 30 FPS, 180 cuadros decodificados, hashes originales sin cambios. MP4, imágenes y verificación: `tmp/sig-presentation-review/final-20261011-200238/`. No contiene métricas de temperatura no verificadas ni audio.
- Navegador real aislado: Studio y SIG a 1920×1080 / 1366×768, sin excepciones ni desbordamiento horizontal; reproducción hasta 3 septiembre, fecha/inset presentes, respuestas de mapas 200. Instancia actual con estos cambios: **http://127.0.0.1:8534/**. Abrir el proyecto indicado en Recientes; las instancias anteriores pueden conservar módulos antiguos.
- Rendimiento: referencia 71.7 s / repetición 79.9 s; última comprobación 59.4 s / repetición 11.5 s. La primera generación todavía puede tardar alrededor de un minuto; no es instantánea. Cachés acotadas para límites por revisión, máscara/tinta inmutable y metadatos de un mes; se siguen comprobando hashes de originales y recursos. Análisis, variaciones y mediciones aisladas en `documentation/SIG-PRESENTACION-RENDIMIENTO-20261011.md`.
- Verificación: grupo de 60 regresiones de ráster/territorio/series/lluvia/editorial; después de los últimos ajustes, 6 pruebas nuevas de presentación y 3 de hash caliente/NoData/bundle; todas correctas. TypeScript y compilación del componente correctos, `git diff --check` sin errores. Sin commit, push, publicación ni borrado de proyectos personales.
- NASA POWER sigue siendo una grilla de ~50–60 km: suavizar no crea resolución científica. Se investigó ERA5-Land (~11 km) como alternativa equivalente para T2M, pero **no** se conectó ni descargó en esta entrega. Los límites de CSV temporal, categorías y métricas genéricas señalados debajo continúan vigentes.

## Corrección del preparador temporal SIG (11 de octubre, posterior a la revisión editorial)

- Resuelto `KeyError: geography` al abrir Preparar timelapse en un proyecto nuevo/antiguo sin capas. Leer el panel no modifica el documento. También protegido el panel de operaciones ráster vacío y la configuración con observaciones ausentes.
- Un único flujo en SIG: fuente/producto, variable/unidad, periodo, observaciones reales, cadencia, territorio, suavizado exclusivamente visual, contornos, duración y todos los perfiles existentes (incluidos TikTok, Reels, Shorts, YouTube y tamaño personalizado). Las fuentes/variables incompatibles se seleccionan por separado. No se rellenan días ni se infiere una fecha del nombre.
- Adquisición explícita dentro del panel: NASA POWER (lluvia, temperatura media/máxima/mínima, velocidad del viento y humedad) y CHIRPS v3 (preliminar/final sat/final rnl), máximo 31 días por solicitud. Reutiliza los conectores del proyecto. Importación múltiple GeoTIFF o multibanda con tabla editable de fechas. Bandas separadas sin remuestreo, conservando escala/offset/máscara, hash del original y banda de procedencia. Documento incorporado solo si la serie completa pasa la validación.
- Salidas: Ecuador continental + Galápagos; solo continente; solo Galápagos; cualquiera de las 24 provincias; o ventana SIG. Los nuevos territorios usan los polígonos de referencia geoBoundaries existentes, con atribución, máscara posterior al remuestreo y encuadre expandido para no cortar el territorio. El mapa base no viaja al video. La navegación SIG no se restringe al área exportada. El suavizado no aumenta resolución científica.
- Enviar a Studio ya no exige CHIRPS v2 para todo: series numéricas compatibles pasan como mapas, calendario, leyenda y crédito real editables. La ruta nacional CHIRPS v2 diario conserva sus cálculos y tarjeta final. Cambiar la preparación SIG no invalida un video sellado anterior: se verifica contra sus propias fuentes/fechas. Un nuevo envío reemplaza únicamente las escenas generadas de la línea temporal, preservando las escenas archivadas y las demás escenas del usuario.
- **Límites explícitos:** esta ruta temporal es GeoTIFF numérico, no CSV de puntos, clases categóricas ni direcciones vectoriales. INAMHI son estaciones: no se interpolan a un ráster nacional ni se publicitan como un conector de mapas ya terminado. Las métricas generales de temperatura/viento/CHIRPS v3 NO se inventan usando la fórmula de lluvia; falta declarar/verificar sus contratos de agregación y tarjetas. La biblioteca de datos/descargador previo se conserva.
- Prueba real: NASA POWER T2M para 1–2 septiembre 2026, ambas fechas devueltas, sin días ausentes. Renderizadas salidas nacional, Galápagos y Napo. Evidencia `tmp/sig-series-20261011/report.json`; MP4 corto de Napo `napo-temperatura-septiembre-prueba.mp4`, 1080×1920, 30 FPS, 30 cuadros decodificados. Es comprobación funcional, no el video final de todo septiembre ni una nueva maqueta editorial. Descarga regional pequeña, sin descarga global ni limpieza de datos personales.
- Verificación: 49 pruebas de series, ráster, territorio, contratos y plantilla editorial por grupos. La primera ejecución detectó dos pruebas de interfaz con selectores anteriores al shell: actualizadas para abrir los diálogos actuales mediante sus eventos y conservar las comprobaciones de error/atomicidad. Reejecución de las ocho regresiones nuevas y esas dos pruebas: 10/10 correctas. Comprobación de sintaxis JavaScript y `git diff --check` sin errores (solo advertencias de finales de línea del trabajo existente).
- Instancia con el código corregido: **http://127.0.0.1:8533/**. Se preservan las ventanas/servidores anteriores; sus módulos cargados pueden mostrar código viejo. Sin commit, push ni publicación web. Las secciones inferiores son histórico y deben interpretarse junto con estas precisiones.

## Revisión editorial de apariencia (11 de octubre, entrega visual posterior)

Esta revisión cambia presentación, no el motor científico. Parte del proyecto real `andes-pulso-entrega-20261011.json`; conserva sus mapas sellados, datos, cálculos, geografía, transferencia y calendario. No sustituye composiciones personales ni borra archivos. Sin commit, push o publicación.

- Plantilla de lluvia reconstruida siguiendo las dos capturas del usuario: titulares condensados con acento azul, fondo azul noche, marca menta, subtítulo, calendario, fecha y contador dinámicos, continente protagonista, Galápagos independiente, ciudades contrastadas, leyenda y créditos. Mapa, textos e iconos siguen siendo capas editables, no una captura aplanada.
- Tarjeta final con cuatro indicadores en una fila y rankings provinciales 1–12 / 13–24 apilados y con eje común. Valores fuera de las barras, nombres ajustados al espacio, 24 provincias y unidades vinculadas al registro científico. Cero válido y ausencia conservan su significado. Se presenta el periodo realmente disponible, no un año completo ficticio.
- Inicio, paneles SIG y espacio de Studio comparten colores, jerarquía, espaciado y estados de selección. Iconos vectoriales locales sin descargas; tipografía Barlow Condensed Display con fuentes ya incluidas. El tema opcional **Ecuador Vivo Social** aplica la base editorial a nuevas composiciones; los temas y proyectos anteriores conservan su apariencia. La automatización científica completa de esta ruta sigue limitada a CHIRPS diario: el nuevo acabado no habilita silenciosamente cálculos de otras variables.
- Nuevo proyecto editable: `_local/video-studio/projects/andes-pulso-diseno-editorial-20261011.json`, nombre **Andes Pulso · diseño editorial · 1–7 enero 2024**. Abrir en Proyectos recientes del entorno de revisión **http://127.0.0.1:8532/**. Las instancias anteriores permanecen activas; 8531 puede seguir mostrando código cargado antes de esta revisión. Para posteriores arranques se conserva el procedimiento existente de `studio_server.py`.
- MP4 y paquete local: `_local/video-studio/jobs/studio-20261011-175601-ea987c44/`, `video.mp4` y `andes-pulso.zip`. Muestra real 1–7 enero 2024, 1080×1920, 30 FPS, 276 cuadros, 9,2 s (mapa 4,2 s + tarjeta 5 s). No se añadió audio ni se renderizó el año entero.
- Evidencia en `tmp/editorial-design-20261011/`: composiciones completas y reducidas, Inicio/Studio a 1920×1080 y 1366×768, SIG, `browser-report.json` y `movie-verification.json`. Comprobación de los dos tamaños sin excepciones ni desbordamiento horizontal de la página; el editor conserva zoom y desplazamiento de su propia línea temporal. Los márgenes sociales son orientativos, no garantía universal frente a interfaces de las plataformas.
- Verificación: 58 pruebas acotadas aprobadas (`test_studio_editorial`, `test_visualizations`, `test_rainflow_contract`, `test_studio_editor_delivery`, `test_studio_typography`, `test_territory_export`); tras el último ajuste tipográfico se repitieron 15 casos de presentación/fuentes. Sintaxis Python/JS, build del componente SIG y `git diff --check` aprobados. No se declara la suite completa del repositorio.
- Archivos principales de esta revisión: nuevos `studio_editorial.py`, `studio_social_template.py`, `test_studio_editorial.py`; presentación en `studio_templates.py`, `studio_typography.py`, `studio_render.py`, `visualizations.py`, `studio_home_visual.py`, `workspace_frontend/home.css`, `workspace_frontend/workspace.css`, opciones de formas en `workspace_frontend/workspace.js`, `frontend/src/map.css` y su build. Herramientas reproducibles: `dev/render_editorial_design.py`, `dev/review_editorial_ui.py`, `dev/verify_editorial_artifact.py`. Los cambios científicos previos de otros turnos siguen presentes, pero no se modificaron sus agregaciones en esta revisión.

Siguiente paso: revisar la copia editorial y ajustar a gusto desde Studio; después ensayar un año diario real acotado. No confundir el diseño reutilizable con validación de todos los datos y formatos futuros.

Checkpoint principal. Los apartados del 10 de octubre conservados más abajo son históricos: los pendientes de envío SIG, recuperación visual y carga del diseño quedaron superados por la evidencia de la sesión anterior y esta continuación. No se reconstruyó el proyecto; sin commit, push, tag, reset, descartes ni limpieza.

## Recorrido SIG → Studio → MP4 con métricas (11 de octubre, continuación)

Entrega corta real sobre el entorno existente. Referencia de lluvia abierta y revisada desde `C:/Users/JHONYC~1/AppData/Local/Temp/codex-clipboard-923f09d7-2fa3-4a49-bd89-8e6b443e674e.png`. Su lenguaje tipográfico y composición se implementan como elementos, sin usar la captura como fondo.

- Un botón «Enviar a Studio» prepara el mapa temporal sellado y los resultados nativos, y crea/actualiza dos escenas: mapa y tarjeta final. Conserva el proyecto, escenas previas y ediciones de una plantilla ya enviada. Los cambios editoriales reutilizan cálculos y mapas; cambios de entradas científicas bloquean exportación hasta actualizar sus vínculos explícitamente.
- Plantilla vertical 1080×1920 con marca, título, periodo, fecha y contador de observación dinámicos, continente e inset independientes, leyenda horizontal, fuentes/resolución/autoría. Galápagos conserva sus propios datos. Ciudades opcionales agrupadas con el continente, etiquetas con halo; sin escala de distancia ficticia. Adaptación 1920×1080 con redistribución, no recorte; evidencia `horizontal-final.png`.
- Escala fija CHIRPS diaria 0, 1, 5, 10, 20, 40, 70, 120+. Leyenda por tramos coherente con los colores; saturación superior explícita. Valores científicos originales sin recorte, bilinear exclusivamente visual, máscaras y NoData conservados. El calendario es 1–7 enero de 2024: siete observaciones, no 366.
- Cálculo automático de esta ruta verificado para CHIRPS v2 diario. Usa `_polygon_stats` y `SummaryAccumulator`, celdas nativas en polígonos provinciales, aproximación de área cos(latitud), inclusión por centros, sin fracciones de celdas fronterizas. Combina continente e islas por pesos, no por media de sus medias. Provincia sin centros válidos o sin todas las observaciones: «Sin datos». Ranking de las 24 provincias, con eje común en sus dos columnas.
- Resultados del periodo: suma de medias nacionales diarias **57,60512913968051 mm**; media nacional por fecha **8,2293041628115 mm/día**; mayor media diaria **19,31295884788013 mm/día**, 2 enero; máximo de celda **312,9021911621094 mm/día**, 2 enero. La suma de medias no es volumen nacional ni máximo acumulado de celda. Galápagos tiene cero válido todos los días; no ausencia.
- Navegador propio: abrir entrada en SIG, reproducir/pausar fechas, enviar con un botón, mover continente, recolocar/redimensionar Galápagos, editar créditos, guardar/reabrir copia, editar rótulo vinculado de métrica y exportar. Resultados idénticos tras edición/reapertura y reenvío sin recalcular. Durante el cierre se corrigieron controles restaurados de otra escena, entrada silenciosa durante un comando pendiente y slider temporal desfasado respecto al lienzo presentado.

### Productos verificables

- Proyecto editable final: `_local/video-studio/projects/andes-pulso-entrega-20261011.json`. Entrada para repetir desde SIG: `andes-pulso-rainflow-entrada.json`. Copias personales/originales preservados.
- Trabajo final inmutable: `_local/video-studio/jobs/studio-20261011-160804-47ceb188/`. Contiene `video.mp4`, `project.json`, `receipt.json`, `andes-pulso.zip`. 1080×1920, 30 FPS, 276 cuadros, 9,2 s: 4,2 s de siete fechas + 5 s de tarjeta final. SHA video `ed43fe6d4967f41e998357ceb702d77fe3e21fccb551b9795fee05c9fb31335f`; SHA canónico proyecto `208f7f38843c350c2a6720a0abc072412849b298700a700ec6fef6e9ab79c35f`.
- MP4 decodificado completo; revisados cuadros de las siete fechas y tarjeta inicial/intermedia/final. Comparación con el renderizador actual: error RGB medio 0,96–1,38/255 por compresión. Evidencia `tmp/rainflow-20261011/movie-verification.json`, `mp4-018.png`, `mp4-126.png`, `mp4-275.png`.
- ZIP preparado automáticamente en exportación final, **sin publicación**: video, proyecto, recibo, resultados JSON, 24 provincias CSV, medias diarias CSV, métodos/cobertura y fuentes. Referencias a originales/bundles locales; no es un archivo autónomo que duplique todos los rásteres. Copias exportables en `tmp/rainflow-20261011/exportables/`.
- Evidencia adicional: `state-verification.json`, `ciudades-opcionales.png`, `proyecto-horizontal-final.json`. Capturas Inicio/Studio/tarjeta a 1366×768 y 1920×1080 en la misma carpeta; SIG final `sig-1366.png` y `sig-1920.png` revisado con seis resultados enlazados (panel desplazable) y leyenda 120+; comparación territorial conservada.

- Cierre del panel Resultados del SIG: seis cálculos enlazados con valor, unidad, periodo, método, ID, procedencia y advertencias; presentación desde el registro inmutable, sin volver a leer píxeles. Verificación sobre el proyecto entregado en `sig-resultados.json`. Inspector declara 120+ y saturación visual, conservando valores originales. Comprobación TypeScript y compilación exclusiva del componente SIG aprobadas.

### Pruebas y límites

- 60 pruebas afectadas aprobadas en ejecuciones acotadas: 31 de contratos/gráficos/plantillas; 9 temporales tras corregir el fixture (cantidades por observación en mm, antes declaraba mm/día sin cadencia diaria); 18 territoriales/rásteres; 1 presupuesto anual; 1 incompatibilidad del calendario insular. Logs en `tmp/rainflow-20261011/`: `affected-tests.log` conserva el fallo inicial de preparación del fixture; `temporal-corrected.log` acredita sus nueve casos corregidos. No se declara una suite general verde.
- Ejemplos conocidos: acumulados, integración de tasas por duración, medias ponderadas, NoData/ceros, duplicación/solapamiento de intervalos, bisiesto, unidades incompatibles, categorías/dirección rechazadas sin método específico, área aproximada y polígonos sin centros. Sintaxis JS/Python y `git diff --check` correctos; avisos de finales de línea ya existentes.
- Eliminados límites de 32 observaciones/50 fuentes que impedían series largas. Auditoría **sintética estructural**, no observaciones inventadas: calendario bisiesto de 366, registro y documento de ~3,64 MB aceptados; 26 s permite al menos un cuadro por fecha. Se mantienen límites explícitos de 256 MiB de fuentes y 1 GiB por bundle, cachés acotadas. **No se verificó rendimiento, cobertura ni exportación de un año real completo.**
- Otras familias no están cerradas en la UI científica de este recorrido. La base explícita permite tasas y medias por duración con ejemplos pequeños; temperatura, viento circular, índices con calidad, categorías/transiciones y ocurrencias requieren configuración y validación propia. Variables desconocidas/tasas sin intervalos no reciben métricas genéricas silenciosas. Siguiente paso: revisión visual de esta muestra, luego ensayo anual real acotado antes de afirmar estabilidad anual.

### Arranque vigente y archivos de esta entrega

URL propia vigente: **http://127.0.0.1:8531/**. Instancias anteriores conservadas. Identidad de proceso/creación/cwd/comando comprobada antes de cada reinicio propio; sin reinicios durante exportación/medición. `tmp/rainflow-20261011/server-identity.json` y `server-final.json`.

Desde la raíz, PowerShell (si 8531 ya está activo, abrir su URL):

```powershell
Remove-Item Env:ECUADOR_VIVO_DEVELOPMENT_RELOAD -ErrorAction SilentlyContinue
Set-Location '.\production\video_studio'
& '..\..\_local\video-studio\.venv\Scripts\python.exe' -X utf8 -m streamlit run studio_server.py --server.port 8531 --server.address 127.0.0.1 --server.headless true --server.fileWatcherType none --server.runOnSave false --browser.gatherUsageStats false
```

Bajo `production/video_studio/`: nuevos `studio_sig_summary.py`, `studio_sig_transfer.py`, `studio_package.py`, `test_rainflow_contract.py`; modificados `variables.py`, `data.py`, `endcard.py`, `visualizations.py`, `studio_templates.py`, `studio_sig_raster.py`, `studio_sig_layers.py`, `studio_sig_raster_ui.py`, `studio_sig_timelapse.py`, `studio_map_bundles.py`, `studio_sig_shell.py`, `studio_model.py`, `studio_media.py`, `studio_render.py`, `studio_geography.py`, `studio_editing.py`, `studio_timeline.py`, `studio_jobs.py`, `layout_editor.py`, `workspace_frontend/workspace.js`, `test_studio_temporal.py`; componente SIG `frontend/src/workspace.ts`, `frontend/src/index.ts`, `frontend/src/map.css` y sus derivados `frontend/build/index-u20.js`/`index-u20.css`. Scripts/evidencia en `tmp/rainflow-20261011` y `tmp/*rainflow*.py`; derivados y proyecto en `_local`. Sin limpieza, eliminaciones, commit, push o publicación. Cambios locales previos conservados.

## Entrega cartográfica comprobada el 11 de octubre (evidencia previa conservada)

- Salida configurable Ecuador continental + Galápagos, independiente de la navegación SIG y de visibilidad de capas de referencia. Polígonos reales geoBoundaries ADM0/ADM1 existentes, CRS84 comprobado con pyproj, atribución CC BY 4.0 y hashes sellados. Máscara geométrica posterior al remuestreo; no se exporta mapa base. Contornos/provincias conservan exactamente el soporte observado y los huecos NoData.
- Canal real Galápagos recuperado exclusivamente de ventanas nativas de los originales CHIRPS v2 globales locales, verificando SHA256 contra la procedencia del recorte continental. Fechas 1–3 enero 2024: 380 celdas nativas válidas por día, todas cero; no confundir con ausencia. Archipiélago multipart real, inset independiente editable, sin marco pesado. Crédito declara reubicación y distinta escala. Sin original verificable se informa falta de cobertura, sin copiar valores ni inventarlos; no se añadió descarga automática.
- Datos científicos y consultas conservados. Opciones Celdas nativas / Suavizado visual; bilinear sobre valores, soporte finito nativo nearest y máscara territorial al final. Categorías rechazan bilinear. Nota visible «Suavizado visual; resolución original conservada». Escala común completa, sin recorte silencioso de máximos. Identidad, manifiestos, validadores, caché y recibos incluyen presentación y límites; bundles anteriores legibles.
- Comparación real del 2 enero: `tmp/territory-delivery-20261011/comparacion-2024-01-02.png`. Primera columna utiliza el tile del bundle original existente; segunda y tercera usan las mismas observaciones científicas con máscara y nearest/bilinear. Referencia anterior conserva su encuadre original.
- MP4 corregido inmutable: `_local/video-studio/jobs/studio-20261011-142129-fbbfb617/video.mp4`, proyecto y recibo adyacentes. 1080×1920, 3 s, 90 cuadros a 30 FPS, 1–3 enero 2024. SHA video `0ae259072791b3fc41d943bea1df98fcb77dc1aae25fec9e4f7d6b2f487b2cb4`; SHA canónico proyecto `5abeeefa35fec4b011a68a3b434a968fe97e979f218337c85888fc02ae80de5f`. Hashes verificados; también intactos los hashes de la entrega anterior.
- `tmp/territory-delivery-20261011/verification.json`: cero píxeles de ráster fuera de máscara en ambos canales y tres fechas; composición decodificada del MP4 coincide con lienzo (error RGB medio <1/255 por compresión). Preview reducido usa el mismo PreparedTimeline y recursos. Derivados nuevos; no se sobrescribieron videos finales existentes.
- Serie local más larga comprobada: siete fechas reales 1–7 enero 2024, 210 cuadros de bundle, canal Galápagos cubierto todos los días; proyecto `serie-local-7-dias.json` y manifiesto referenciado en verification.json. No se renderizó ni se validó un año diario; esta prueba tampoco es un MP4 de siete días.
- Adaptación horizontal corregida al detectar solapamientos: redistribuye los recursos territoriales existentes, fecha, leyenda e inset sin modificar datos. Composición real `composicion-horizontal-2024-01-02.png` y proyecto editable `proyecto-horizontal.json`. El MP4 entregado es vertical; no se generó otro MP4 horizontal.

## Verificación y alcance actual

- Selección final: 12 pruebas afectadas aprobadas, 48,952 s, `tmp/territory-delivery-20261011/affected-final.log`. Incluye ocho de territorio/soporte/categorías/identidad/compatibilidad/adaptación, tres timelapse y una de payload SIG. TypeScript typecheck y build aprobados. `git diff --check` sin errores de espacios (avisos de finales de línea existentes).
- Se conservaron las 18 pruebas aprobadas de `tmp/resume-affected-tests.log`, sin repetir el recorrido ya verificado de edición, guardado, Undo/Redo, fallo/recuperación y calendario. Una ejecución acotada anterior de test_sig_raster tuvo diez pruebas de motor aprobadas y dos errores de UI por selectores antiguos `sig_open_copy`/`sig_import_format`; no se declara toda la suite verde ni se amplía el alcance para rehacer esa UI.
- Inicio: previews legibles de SIG/Studio, creación y recientes; SIG: mapa dominante, árbol agrupado, inspector y temporal; Studio: biblioteca organizada, lienzo, inspector contextual y timeline. Capturas reales en `tmp/territory-delivery-20261011/`: inicio y SIG 1366×768/1920×1080, Studio vertical y horizontal en ambas medidas. Referencias profesionales del 9 octubre revisadas. La aceptación estética de la representación queda para revisión del usuario.
- Límites de geoBoundaries son una referencia atribuida, no certificación de frontera oficial. La comprobación de rendimiento/estabilidad cubre esta muestra y siete fechas, no un año. No se ampliaron proveedores, catálogo, temperatura ni anomalías.

## Servidor de revisión y arranque exacto

URL propia: http://127.0.0.1:8530/ . Servidores previos 8526/8527 conservados. Reinicios del servidor propio únicamente tras comprobar listener, PID, creación, cwd y comando; evidencia `server-before-restart.json` / `server-final-identity.json`. Sin watcher ni recarga de desarrollo durante las capturas.

Desde la raíz del repositorio, PowerShell:

```powershell
Remove-Item Env:ECUADOR_VIVO_DEVELOPMENT_RELOAD -ErrorAction SilentlyContinue
Set-Location '.\production\video_studio'
& '..\..\_local\video-studio\.venv\Scripts\python.exe' -X utf8 -m streamlit run studio_server.py --server.port 8530 --server.address 127.0.0.1 --server.headless true --server.fileWatcherType none --server.runOnSave false --browser.gatherUsageStats false
```

No ejecutar otro listener sobre 8530 mientras esté activo; usar la URL existente. El lanzador normal 8526 conserva su procedimiento en V1-ARRANQUE.md.

## Archivos intervenidos en esta continuación

Bajo `production/video_studio/`: nuevos `studio_territory.py`, `test_territory_export.py`; ajustes en `studio_sig_raster.py`, `studio_map_bundles.py`, `studio_sig_timelapse.py`, `studio_sig_layers.py`, `studio_sig_raster_ui.py`, `studio_temporal.py`, `studio_map_ui.py`, `maqueta.py`, `studio_editing.py`, `studio_sig_shell.py`, `workspace_frontend/workspace.js`, `workspace_frontend/home.css`; frontend SIG `frontend/src/workspace.ts`, `frontend/src/index.ts` y sus build/index-u20.js/css. Se añadieron scripts y evidencia acotados en tmp y derivados/proyectos/trabajos en _local; ESTADO.md actualizado. Otros cambios locales ya presentes se mantuvieron. Sin eliminaciones, sin limpieza de _local/tmp ni credenciales/historial.

---

# Histórico conservado — 2026-10-10

Checkpoint válido: este archivo. No se generaron editor-closure-checkpoint.json ni editor-closure-files.json. Sin commit, publicación, reset, descartes ni eliminaciones; avances anteriores conservados.

## Continuación comprobada
- Streamlit 1.65, OpenLayers y proyecto compartido conservados. Recarga solo con ECUADOR_VIVO_DEVELOPMENT_RELOAD=1; servidor normal sin esa variable.
- pollVisual cargado y comprobado en navegador propio: termina después de decodificar; fecha del lienzo cambia cuando se presentan los píxeles.
- Corregidos errores ocultos por Guardado: prioridad de error de comando, preparación y decode. Error de nombre inválido visible con role=alert.
- Fallo visual controlado en instancia aislada 8528: role=alert, seis imágenes decodificadas, fuentes de imagen idénticas a la representación anterior. Captura resume-studio-visual-failure.jpg y JSON en tmp/ux-redesign. Recuperación también comprobada: estado actualizado, role=status, imágenes decodificadas. Instancia 8528 cerrada con identidad verificada.
- Hallado y corregido bloqueo de preview: studio_delivery rechazaba preview-*. Se admiten solo trabajos de prefijo conocido dentro de STORE/jobs; se conservan controles de archivos y recibo.
- Studio real (CHIRPS 1–3 enero 2024): nombre/texto, mover X, redimensionar ancho, ocultar/eliminar/deshacer, guardar/reabrir comprobados. Undo restaura X=53, ancho=994; Redo ancho=974. Preview 360×640, 3 s/90 cuadros; etiqueta explícita calidad reducida. Retorno a edición y búsqueda de fecha comprobados; modificar texto invalida preview.
- Exportación final studio-20261010-023120-ee2224b9: MP4 1080×1920, 3 s, 90 cuadros/30 fps; calendario nativo 1–3 enero, unidades/fuentes/SHA conservados. Hash del video descargado y hash canónico del proyecto coinciden con recibo delivery_kind=final. Descarga comprobada en Downloads/ecuador-vivo.mp4.
- SIG de esta sesión: reproducción, pausa, búsqueda, CRS EPSG:4326, mm/día, NoData -9999, escala común, estilo guardado, formato horizontal/vertical y guardado comprobados. Serie configurada y enviada a Studio: mismo project_meta.id y escena anterior conservada; dos escenas/6 s. Latinoamérica incorporada desde la referencia existente.

## Acabado en curso
- Referencias profesionales de Inicio, SIG y Studio revisadas.
- Escritos ajustes: SIG recupera 66 px de mapa, controles accesibles y textos legibles. Studio biblioteca en dos filas sin etiquetas amontonadas, inspector/timeline mayores y estado de error visible. TypeScript/build pasan; cambios visuales todavía no cargados ni aceptados en navegador.
- Pendiente: concluir nuevo envío SIG, recuperar fallo, reiniciar únicamente servidor propio para cargar diseño, comprobar/capturar Inicio/SIG/Studio en 1366×768 y 1920×1080, vertical y formatos existentes. No ampliar catálogo/proveedores.

## Pruebas y evidencia
- Esta sesión: editor_delivery 3 OK (0,317 s), nombre/historial 1 OK (1,431 s), visual_delivery 8 OK (2,237 s). Selección de 18 afectadas OK en 10,327 s, log tmp/resume-affected-tests.log.
- Historial distinto: 30 pruebas OK (12,669 s); ejecución de 42 con 5 errores y 1 fallo, luego solo esos seis casos corregidos OK. No hubo nueva ejecución completa de 42.
- 206 ms fue perfil intermedio anterior a validaciones de presentación; no latencia final ni medida de navegador.
- Recursos originales, proyectos, videos finales, credenciales, referencias científicas e historial Git conservados. Sin limpieza.

## Abrir y procesos
- Versión de prueba actual: http://127.0.0.1:8527. Propia, estable durante cada comprobación. Cuatro reinicios entre comprobaciones registrados en tmp/resume-studio-processes.json; identidad actual tmp/resume-studio-server-identity.json.
- Instancia aislada de fallo: 8528; fixture dev/studio_visual_failure_server.py, identidad tmp/visual-failure-server-identity.json. Se cerrará solo tras verificar identidad.
- Normal http://127.0.0.1:8526 conservado (identidad leída PID 27784); puede mostrar código anterior. Lanzador normal: powershell.exe -NoProfile -ExecutionPolicy Bypass -File '.\production\video_studio\launch.ps1'. Procedimiento verificado de reinicio en documentation/V1-ARRANQUE.md.
- Siguiente paso: capturar y comprobar los paneles finales en ambas resoluciones y formatos existentes.
