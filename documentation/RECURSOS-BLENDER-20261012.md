# Recursos con Blender · primer flujo completo

Fecha: 12 octubre de 2026, Guayaquil. Dirección aprobada por el usuario: integrar Blender ahora, dentro de Ecuador Vivo. Esta entrega implementa el recurso orográfico, no todo el editor tipo Canva ni el catálogo 3D propuesto.

## Cómo usarlo

1. Abre Ecuador Vivo en `http://127.0.0.1:8534/` y recarga después del reinicio del servidor.
2. En Inicio, abre **La montaña no fabrica agua** para ver el ejemplo editable ya guardado. También aparece en **Recursos → Mis recursos**.
3. Para crear otro, entra a **Recursos → Estudio 3D**. No necesitas abrir previamente un proyecto.
4. Ajusta nombre/formato de la nueva escena, duración de 1–30 s, giro/inclinación/encuadre/recorrido de cámara, relieve ilustrativo, luz, colores, condensación y lluvia.
5. Pulsa **Generar vista** para una imagen. Después **Probar animación · calidad ligera**; usa **Generar recurso Full HD** cuando apruebes los ajustes. Cambiar un control no inicia un render.
6. El progreso se actualiza sin mantener bloqueada la página. Puedes cancelar el proceso propio. Los renders recientes se pueden volver a abrir desde la biblioteca; una receta idéntica reutiliza su resultado.
7. Un render final permite **Abrir recurso en el lienzo**, **Añadir como escena a mi video**, o **Actualizar objeto 3D · conservar diseño** si el proyecto contiene ese recurso. Esta última acción cambia el clip y su receta, no los textos, sus transformaciones, duración de escena, voz, subtítulos ni otras escenas.
8. En Studio mueve/redimensiona el objeto de video y edita, añade o elimina textos/figuras con las herramientas existentes. En Recursos del lienzo, **Editar cámara y materiales 3D** vuelve a la receta de la escena seleccionada.
9. Puedes descargar el `.blend` para modificar mallas, materiales y animación en Blender. Los controles integrados editan parámetros del modelo orográfico, no todas las herramientas de modelado de Blender.

El nuevo recurso es una ilustración local sin registros de cálculos científicos. Sus metadatos ya no heredan CHIRPS/2024/lluvia. El texto explica el ascenso y la posible condensación; una nube no implica siempre precipitación. Fuentes conceptuales: [NOAA/NWS · ascenso orográfico](https://forecast.weather.gov/glossary.php?word=OROGRAPHIC) y [desarrollo de nubes](https://www.weather.gov/source/zhu/ZHU_Training_Page/clouds/cloud_development/clouds.htm). El relieve y las partículas no son DEM, viento medido, microfísica ni pronóstico local.

## Productos de esta entrega

- Proyecto editable: `_local/video-studio/projects/recurso-3d-orografia-20261012.json`. Se actualizó exclusivamente la demostración creada en esta sesión después de comprobar igualdad byte a byte con su copia original; se conservó un snapshot anterior. No se sobrescribieron pilotos ni proyectos personales.
- MP4 vertical: `_local/resource-development-20261012/blender-proof-final/tiktok/video.mp4`, **1080×1920, 30 fps, 300 cuadros, 10 s**.
- MP4 horizontal: `_local/resource-development-20261012/blender-proof-final/youtube/video.mp4`, **1920×1080, 30 fps, 300 cuadros, 10 s**.
- Ambos tienen composición/textos/créditos separados y no contienen narración. La composición vertical reserva espacio inferior y lateral orientativo; no garantiza todas las superposiciones cambiantes de las redes.
- Recibo, hashes y cuadros críticos: `blender-proof-final/verification.json`, carpetas `tiktok/` y `youtube/`. Los JSON del primer ensayo son evidencia histórica anterior a la corrección de metadatos; usa el proyecto guardado vigente o crea otro desde Recursos.
- Prueba del producto completo a través de controles nativos: `blender-proof-final/ui-verification.json`. Abre el recurso, conserva receta/elementos al reemplazar y verifica nuevamente hashes. AppTest, no aceptación visual de navegador.

## Decisión: motor local, receta acotada y render explícito

Se adopta **Blender 4.5.4 LTS / Eevee** como herramienta local, conservando un único proyecto, reloj de 30 fps, biblioteca multimedia y exportador Studio. No se integra otra aplicación web ni se exige cuenta de pago. [Blender oficial / GPL](https://github.com/blender/blender); mantener sus archivos de licencia al distribuir el motor. Geometría del ejemplo creada para este proyecto, sin modelos externos descargados.

Alternativa revisada: Three.js ya presente en la web permitiría un visor interactivo ligero; no demostraba por sí solo la captura/exportación equivalente a Studio. El usuario pidió Blender ahora. Se eligió su render en proceso separado con receta validada y `.blend` editable. La primera entrega no añade simultáneamente otro visor, editor de keyframes o parser GLB.

La receta admite únicamente campos/valores acotados, sin rutas, scripts o código pegado. El worker ejecuta el script propio con `--factory-startup --disable-autoexec`. Verifica ubicación/huella del motor, identidad de receta, número de cuadros, resolución y hashes de productos antes de incorporarlos. No abre archivos `.blend` arbitrarios del usuario.

Instalador repetible: `production/video_studio/install_blender.ps1`, ZIP oficial y SHA-256 de `download.blender.org`, sin administrador ni cambios en runtimes/sistema de Windows. Motor activo: `_local/video-studio/tools/blender-4.5.4-windows-x64/blender.exe`. La instalación fallaba con SideBySide/`blender.crt` en AppData y arrancó al ubicarla en la carpeta local del proyecto; eso no demuestra una causa definitiva del comportamiento de Windows. No se modificó el ejecutable firmado.

## Tiempo y espacio medidos

El primer render final de 300 cuadros tardó **1011,219 s (unos 17 min)** en esta computadora. Componer el MP4 con Studio tardó **137,546 s vertical / 158,666 s horizontal** en este ensayo. No anunciar render instantáneo. La vista ligera usa 640×534 y menos muestras; no se extrapola un tiempo que no se midió. El render final del objeto usa 1080×900, 64 muestras y se adapta como un elemento al perfil del video.

Solo se usa un PNG de trabajo, consumido/confirmado antes del siguiente cuadro. Al finalizar o cancelar se retira ese archivo propio y el MP4 parcial; se conservan poster, MP4, `.blend`, receta, recibo y registros acotados. No hay una carpeta permanente de 300 PNG. La biblioteca conserva recetas distintas: muchos renders finales pueden volver a ocupar espacio; no se borra automáticamente trabajo del usuario. Un fallo/cancelación de la misma receta requiere cambiar un ajuste para crear un trabajo nuevo; recuperación/reintento general sigue pendiente.

La primera codificación redondeó indebidamente 1080×900 a 1088×912 por el ajuste de macroblocks de imageio. Una prueba real detectó la discrepancia. El worker ahora fija `macro_block_size=1` y una regresión de 34×30 comprueba tamaño exacto. El primer clip ilustrativo fue normalizado explícitamente con Lanczos a 1080×900; esa corrección consta en su recibo y no afectó datos científicos. No afirmar que ese clip anterior nunca fue remuestreado.

Espacio adicional medido: motor activo **1.222.427.582 bytes (~1,14 GiB)**. Además permanece la instalación fallida **4.5.14** en `C:/Users/JHONY CONTERON/AppData/Local/EcuadorVivo/tools/blender-4.5.14-windows-x64`, **924.651.936 bytes (~0,86 GiB)**. La retirada automática de esa copia fue bloqueada por la política de la herramienta; no se intentó eludirla. No confundir esa carpeta con el motor activo del repositorio.

## Verificación y límites

- Suite focalizada anterior: 104 casos correctos de Recursos, composición, voz, subtítulos, narrativa, workspace, Inicio y startup. Se añadieron regresiones de metadatos ilustrativos, estado de progreso malformado, resolución de codificación y ruta Inicio → Estudio 3D.
- Grupo final de 25 pruebas correcto después de esas correcciones; los grupos se solapan, no sumar ambos como 129 pruebas únicas.
- AppTest sobre el producto real: visualización del resultado, apertura del lienzo y reemplazo sin mutar el original ni añadir cálculos científicos. Cambio de controles/visita no lanza Blender. Motor ausente da un mensaje accionable.
- Cancelación real del worker comprobada: estado cancelado, proceso propio terminado, sin fotograma ni MP4 parcial. No se cerraron motores/procesos de otros proyectos.
- Cada MP4 completo fue decodificado: tamaño, 300 cuadros, 30 fps, duración y tres cuadros críticos distintos. Revisión visual offline de títulos, crédito y composición vertical/horizontal. Guardia posterior: ocho pilotos válidos y cero referencias directas ausentes.
- No se automatizó navegador: la denegación previa sigue vigente. Pendiente revisión humana de interfaz/responsive y aprobación estética; AppTest no sustituye esas comprobaciones.
- Clip 3D RGB opaco: **transparencia no implementada**. No ofrece edición libre de mallas dentro del navegador, trayectorias arbitrarias, importación de GLB, visores Three.js nuevos, fotorealismo ni simulación física. El `.blend` sí contiene geometría/materiales/cámara/animación editables en Blender.
- Después de aprobar visualmente este ejemplo: reorganizar la autoría dentro del lienzo compartido y ampliar recursos a infiltración/escorrentía, El Niño/Pacífico y fallas, cada uno con fuente, límites y MP4 probado. El resto del plan no se marca terminado por esta integración.

## Archivos y repetición técnica

Módulos pequeños: `studio_blender.py` (receta/jobs/integridad), `studio_blender_worker.py` (control/render), `blender_orographic.py` (escena), `studio_blender_scene.py` (composición editable), `studio_blender_ui.py` (controles). Integración lazy en `studio_resources_ui.py` y evento del lienzo en `studio_workspace.py`/`workspace.js`. No se cambió SIG, fórmulas, pilotos, voz o subtítulos.

Herramientas de verificación: `dev/blender_integration_check.py` (exportar ambos perfiles a carpetas independientes; requiere destino nuevo para una repetición) y `dev/blender_ui_check.py` (controles sobre un producto existente). Los binarios/renders permanecen en `_local`, no versionados. No hubo commit, push ni publicación web.
