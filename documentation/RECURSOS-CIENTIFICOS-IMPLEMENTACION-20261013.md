# Recursos científicos · implementación del 13 de octubre de 2026

Solicitud aprobada: aplicar la propuesta Canva científico e instalar los candidatos
abiertos. Se ha construido una primera mesa de autoría, no se declara terminada
toda la visión RC1–RC7 ni aprobado su acabado visual.

## Entregado

- Recursos abre directamente un lienzo independiente del video actual, con
  biblioteca y propiedades flotantes, herramientas arriba y montaje recogido.
  Nuevo recurso, seis plantillas, búsqueda por tema, favoritos por sesión,
  biblioteca guardada, formas, textos e imágenes. Guarda con el sistema existente.
- Enviar a Studio inserta explícitamente la escena en el video. Editar Recursos
  no modifica automáticamente el video abierto ni sus datos/cálculos.
- Excalidraw 0.18.1, Fabric.js 7.4.0, React Flow 12.12.0 y Ketcher/standalone
  3.18.0 instalados y conectados mediante un componente Streamlit CCv2 generado
  desde su plantilla oficial. Se importan al abrir su editor, no en Inicio/SIG.
- Cada editor conserva JSON/molfile y añade PNG a la composición. Se puede
  reabrir el editor original desde Propiedades. El PNG es un objeto compuesto;
  sus piezas NO se convierten en elementos independientes del lienzo principal.
  React Flow exporta una representación uniforme, no una captura idéntica del editor.
- Cinco ilustraciones Bioicons CC0 con original, PNG, autor, licencia y hash;
  catálogo fijado a commit. Son ilustraciones, no registros de especies en Ecuador.
- Manim 0.22.0 instalado en entorno aislado y comprobado con geometrías básicas;
  todavía no tiene panel de generación. Three.js está disponible. Se reutiliza
  Blender y su panel existente; no se ha construido un modelador 3D general.

## Tamaño y licencias

Medición de bytes de archivos, no espacio físico NTFS: dependencias científicas
601,1 MiB; herramientas de compilación 81,9 MiB; entorno Manim 357,9 MiB;
componente compilado con avisos y fuentes 33,8 MiB. Total aproximado 1,05 GiB.
No se clonaron catálogos completos ni se instalaron BioRender o Smithsonian.
BioRender es referencia de producto, no biblioteca libre utilizable sin licencia.

Versiones/overrides reproducibles en resource_engines/package-lock.json.
Auditoría npm tras ajustes compatibles: 0 críticos, altos y moderados; 4 bajos
transitivos relacionados con Mermaid/KaTeX. No significa ausencia de riesgo;
revisar antes de distribuir públicamente. Avisos e inventario de 552 paquetes
de primer nivel del árbol instalado en frontend/build/notices e inventory.json;
no constituye auditoría legal completa de todas las dependencias anidadas.
El código propio conserva la licencia privada del repositorio, y los motores
mantienen sus licencias MIT/Apache y las ilustraciones CC0.

## Evidencia y límites

Pruebas Python de rutas reales AppTest, independencia de documentos, guardar/abrir,
transferencia a Studio, validación PNG/JSON, fuente local acotada, recursos previos,
Inicio y arranque aprobadas. Nueva prueba importa bytes PNG reales, conserva receta
tras JSON, verifica assets por hash y renderiza cuadros 1080×1920 y 1920×1080.
Seis pruebas Node de ventanas/búsqueda aprobadas; sintaxis JS, CSS y compilación
TypeScript/Vite aprobadas. Manim import y pip check aprobados. 36 archivos
protegidos del SIG, render y layout base conservan su SHA-256 inicial.

**Pendiente de aceptación visual real**: la preferencia guardada del navegador
sigue denegada. No se elude con headless u otro motor de capturas. AppTest no
ejecuta React, WASM o WebGL: los cuatro editores compilan y montan su componente,
pero sus gestos/exportación reales, fuentes, teclado, tamaños 1366/1920 y
legibilidad en teléfono necesitan revisión en navegador. No se promete todavía
paridad exacta con la ilustración ni un MP4 nuevo aceptado visualmente.

RC4 (anclajes nativos al agrupar/duplicar), RC5 (mejor acabado 3D), RC6
(fotogramas clave por objeto), ampliar catálogo y RC7 (paquete/video revisado)
siguen pendientes. No se alteran cálculos científicos para crear recursos.

Acceso: recargar Ecuador Vivo en 8534 y abrir Recursos. Herramientas abre los
cuatro editores; 3D reutiliza Blender; Propiedades permite volver al original.
No se hicieron commit, push, publicación, limpieza ni cambios en el SIG.
