# Ecuador Vivo Studio Design System y contrato UX

## Continuidad Studio 2.0 · 2026-10-08

El cierre UX de 301 tests/85 checks que se conserva abajo pertenece al rediseño anterior. Studio 2.0 incorpora Inicio separado (libre/template, abrir/importar/recientes y acceso a preparación científica) con widgets públicos; el editor mantiene el CCv2 profesional. Volver a Inicio y regresar conserva documento/historial. No se aplican hacks sobre clases internas de Streamlit.

Maqueta → Visualizaciones → Cargar resultados científicos → Crear proyecto en Studio ya genera escenas editables desde CalculationResult existentes. La biblioteca de escenas abre «Cambiar template / regenerar escena»: propuesta antes/después, cancelación o reemplazo explícito archivando versión anterior, undo. No sustituye silenciosamente ediciones humanas. El asistente completo desde Inicio y la regeneración de estructura todavía no existen; tampoco mapas temporales editables, clips multipista o audio independiente.

Evidencia nueva: 24 checks Chrome (3 + 5 + 7 + 9), capturas de Inicio/proyecto libre/ciencia en los tres tamaños; inspección visual final de ciencia a 1366 y 768 px. Nombres de métricas largos y textos pequeños pueden requerir ajustes editoriales; el inspector avisa de legibilidad. No se declara refinamiento final de Studio 2.0. Estado exacto y traspaso: `tmp/ecuador-vivo-studio-2-checkpoint.md`; implementación detenida por el usuario para cambio de cuenta.

## Alcance aprobado · 2026-10-08

La especificación del usuario autoriza siete incrementos consecutivos. No hay migración del motor ni del modelo. Cinco regiones simultáneas: barra superior, recursos/capas, canvas, inspector contextual y timeline. El editor ocupa el viewport; únicamente los paneles y la timeline tienen scroll. A 768 px se abren paneles como drawers. Canvas protagonista, proporciones nativas, controles compactos y foco visible.

## Decisión de arquitectura

El baseline real `tmp/ux-redesign/before-{1920,1366,768}.png` muestra controles verticales y canvas fuera de la primera pantalla (y=1153 px a 1366×768). Columnas/formularios nativos no comparten selección inmediata ni un viewport persistente con el controlador pointer/keyboard existente. Retocar clases internas de Streamlit sería frágil.

Solución mínima: columnas nativas y CSS; no resuelve selección, timeline y persistencia simultáneas. Solución elegida: un componente CCv2 aislado con HTML/CSS/JS locales, reutilizando el controlador de `layout_editor`, operaciones puras, render Pillow, caché, autosave y worker. El frontend envía comandos declarativos versionados; Python valida y guarda antes de publicar documento/historial. `show_studio` y Montaje legacy conservan sus contratos. El componente nuevo es la entrada predeterminada de Estudio.

Reproducción: wrapper público `st.App` y ruta Starlette FileResponse con token aleatorio, archivos completos del worker, Range y caducidad. No MediaFileManager privado, base64 de películas ni otro servidor. Arranque tradicional conserva exportación y ofrece preview nativo si la ruta no está disponible. La ruta requiere Streamlit 1.65 instalado; API experimental aislada en el wrapper, reversible. No dependencia nueva.

## Tokens y ergonomía

Superficies #10171d / #17242c / #20313b; texto #edf3f5, secundario #afc0c9; acento #71dcc8 y tinta #07231e. Espacios 4/8/12/16/24 px, tipografía Segoe UI local, cuerpo 13 px, títulos 14 px; barra 52 px, paneles 244/280 px (220/260 px por debajo de 1350 px), timeline 156 px, footer 26 px. Bordes estructurales #354954; límites de inputs #718a96 con contraste mínimo 3.69:1 sobre las tres superficies; radios 4/8 px. Targets compactos ≥28 px con espacio; controles principales responsive ≥40 px. SVG lineal uniforme. Selección turquesa, foco 2 px, estados guardado/pendiente/error/worker explícitos. Reducir movimiento respeta prefers-reduced-motion.

Los diálogos nativos usan `primaryColor=#15836f`: Streamlit impone texto blanco en botones primarios, cuya relación medida es 4.65:1. El workspace controla su propia tinta oscura sobre turquesa. Tests verifican texto ≥4.5:1 y foco/bordes de controles ≥3:1; los separadores decorativos no se confunden con límites de controles. Ver [contrato público de colores Streamlit](https://docs.streamlit.io/develop/concepts/configuration/theming-customize-colors-and-borders).

## Interacciones y contratos

- Selección, zoom, pan, guías y snapping locales; drag/resize usan el controlador existente. Gestos completos se aceptan automáticamente; Escape cancela. Contenido/estilo se rasteriza por el renderer existente, nunca una interpretación tipográfica paralela en el navegador.
- Undo/redo conserva el documento completo del workspace, incluidas propiedades/nombre. Gestos pendientes se recuperan por pestaña; solo revisiones aceptadas se anuncian como guardadas. Comandos obsoletos se rechazan, no sobrescriben un rerun más reciente.
- El inspector conserva secciones abiertas, scroll, foco y cursor durante reruns. Campos contextuales sin enviar se conservan mientras la revisión y selección sean las mismas, incluidos valores rechazados; una revisión aceptada sustituye el draft por datos canónicos. Errores se anuncian con role=alert, sin reintentos automáticos del mismo gesto rechazado.
- Inspector por tipo; bindings científicos declarativos, unidades/procedencia/warnings visibles. Ningún gesto estético llama proveedores/calculadores.
- Timeline representa escenas y elementos reales. El motor actual tiene duración de escena y trim/loop de videos, no tiempos independientes por elemento. No se presentan pistas independientes editables ficticias.
- Miniaturas/duraciones, regla y playhead comparten la geometría de escenas al cambiar zoom temporal o viewport. Reordenar funciona mediante drag/drop y Mayús+flechas; duplicar/quitar conserva las escenas recuperables y el historial. Timeline colapsable; paneles colapsables en escritorio y drawers a ≤1000 px.
- Preparar reproducción y exportar comparten el mismo MP4 y receipt; documentos posteriores invalidan la reproducción anterior. Recuperar abre copia y preserva el original.
- El worker sigue siendo consultado hasta finalizar o fallar aunque el documento cambie. El navegador puede requerir un clic adicional para autorizar audio después de preparar el MP4; el estado lo indica. No se declara reproducción de un snapshot obsoleto como preview del documento actual.

## Validación por incrementos

1. Shell/layout y ruta: tests de contrato + Chrome/capturas.
2. Canvas/zoom/gestos/shortcuts: controlador existente + integración real.
3. Capas/recursos/templates: comandos, grupos/locks y biblioteca.
4. Inspector: selección, propiedades, errores, ciencia inmutable.
5. Timeline: selección/reorder/duplicación/seek/playback y worker.
6. Tokens/estados/accessibilidad: labels/foco/teclado/contraste.
7. Responsive/rendimiento/refinamiento: 1920×1080,1366×768,768 px; flujo completo y suite.

Las capturas y logs reales se registran progresivamente en tasks/todo.md. No se consideran pruebas realizadas por el mero hecho de escribir verificadores.

Fuentes: [CCv2 1.65](https://docs.streamlit.io/develop/api-reference/custom-components/st.components.v2.component), [st.App](https://docs.streamlit.io/1.58.0/develop/api-reference/server/st.app), [organización de paneles Premiere](https://helpx.adobe.com/premiere/desktop/get-started/tour-the-workspace/customize-panels.html), [capas Figma](https://help.figma.com/hc/en-us/articles/26584819173271-Layers-101-Get-started-with-layers). Referencias usadas para organización, sin copiar su diseño.

## Cierre ejecutado · 2026-10-08

Los siete incrementos están validados: **301 tests (283.806 s) OK**, **85 comprobaciones funcionales Chrome + tres layouts OK**, compatibilidad del canvas anterior 96×3 y transporte/worker 17 OK. El flujo completo crea un proyecto, adapta formato, añade template/texto/imagen/video, edita canvas con ratón, reordena escenas, reproduce y descarga JSON/MP4. Recuperación y proyecto científico real conservan cálculos/fuentes/unidades. Tests nuevos cubren comandos/historial/atomicidad/guardado/ruta Range/callbacks/contraste y preservación de contratos.

Capturas reales inspeccionadas: [antes 1366](../tmp/ux-redesign/before-1366.png), [multimedia después 1366](../tmp/ux-redesign/after-media-1366.png), [ciencia después 1366](../tmp/ux-redesign/after-science-1366.png), [1920](../tmp/ux-redesign/after-final-1920.png), [768](../tmp/ux-redesign/after-media-768.png). El canvas vertical del baseline aparecía fuera de pantalla a 1366 px; ahora se ve entero con paneles/timeline simultáneos. A 1920 px la superficie visible del canvas vertical es aproximadamente tres veces la anterior; zoom/pan y colapso de paneles/timeline permiten ampliar el área de trabajo. La superficie del formato horizontal ocupa prácticamente el ancho central.

Reproducción y exportación usan el mismo archivo; los 30 cuadros del MP4 descargado se compararon con el render canónico: diferencia media máxima 2.1852/255 por compresión del códec, pico AAC decodificado 0.04818. No se declara identidad binaria de PNG con video comprimido. Logs autoritativos `tmp/ux-redesign-final-tests.log`, `tmp/ux-redesign-final-browser.log` y `tmp/ux-redesign/download-verification.json`. Diff y whitespace de 29 archivos OK. Sin dependencias nuevas, commit ni push.
