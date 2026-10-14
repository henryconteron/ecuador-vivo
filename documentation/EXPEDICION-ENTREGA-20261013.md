# Expedición andina · entrega local y web

## Implementado

- Web pública: portada panorámica original, serif local, navegación crema, acciones jade; ilustración identificada como conceptual. Napo real conserva su enlace y crédito en una sección separada.
- Identidad compartida en Datos, Biblioteca, Aprender, Andes Pulso y navegación del atlas.
- Inicio local: mismo paisaje, tipografía editorial, acciones crear/abrir antes de los espacios, proyectos existentes conservados.
- SIG: chrome tinta, propiedades y referencia crema, interacción, límites, paletas y serie temporal sin cambios.
- Studio: entorno tinta compacto y ventanas flotantes conservadas; marca SVG común. Recursos: biblioteca y canvas crema, dos ilustraciones originales insertables.
- Nueva plantilla «Expedición · Ciclo del agua»: imagen, cinco etiquetas, flechas, fuente conceptual y créditos como elementos editables. Formatos TikTok y YouTube comprobados por render del motor real. Los borradores existentes nunca se reemplazan; solo el recurso nuevo empieza con la ilustración.
- Arte optimizado y fuentes: aproximadamente 1,78 MB. Prompts y procedencia en assets/images/expedicion; referencias tipográficas OFL incluidas.

## Comprobación y límites

El usuario comprobó y aprobó la dirección de la portada mediante captura. No se pudo hacer comparación completa del resto de pantallas: el navegador interno rechazó el acceso por preferencia guardada y después Edge no estuvo disponible. A petición del usuario se terminó sin navegador. No se afirma igualdad visual comprobada en todas las resoluciones.

35 archivos de pruebas JavaScript públicos / 29 entradas pasan. Puente Andes Pulso y rutas de recursos pasan. 28 pruebas focalizadas de Inicio, composición, ilustraciones, plantilla, biblioteca y preservación del vídeo pasan. SIG: build, typecheck, 19 pruebas Node y 34 Python/AppTest pasan. Studio/Recursos: 29 Python y 6 Node pasan.

La ejecución general de Studio reunió 720 pruebas y encontró 3 fallos y 16 errores; cinco errores correspondían a la nueva plantilla aún no implementada durante esa ejecución y ya se resolvieron en la pasada focalizada. No se volvió a ejecutar toda la suite. Hay discrepancias en expectativas previas de test_metrics y test_visual_delivery; los otros errores aún requieren diagnóstico y clasificación separados. No se cambiaron cálculos para forzar esas pruebas a verde ni se declaró cerrado el motor científico.

## Limpieza y publicación

Retirados 204 archivos de fixtures temporales de pruebas y compilaciones SIG v1–v3 que ya no están registradas: 2.772.962 bytes lógicos. Respaldo ZIP con verificación SHA-256 antes de cada retirada: _local/maintenance/expedicion-cleanup-20261014-040525/recoverable-copies.zip. Respaldo: 780.103 bytes. Los proyectos, fuentes, datos, vídeos, compilación actual e historial Git se conservan. No se limpiaron dependencias activas ni carpetas ambiguas.

La web pública fue subida a main en el commit 7bd3e58, sin force-push ni borrar historial. GitHub confirmó éxito de Validate atlas (38509760480) y pages build and deployment (38509760290). El entorno SIG/Studio/Recursos permanece local; esta entrega de apariencia no certifica ni publica las modificaciones funcionales anteriores pendientes de revisión. Instancia local reiniciada de forma acotada en 8534; /_stcore/health respondió 200. No se reinició el panel privado 8511 ni otras aplicaciones.
