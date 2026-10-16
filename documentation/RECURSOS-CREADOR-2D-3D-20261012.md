# Recursos: creador visual 2D/3D · dirección aprobada

Estado: revisión y plan, NO funciones implementadas. Fecha: 12 octubre de 2026, Guayaquil. Amplía la tarea de puente 3D existente, sin sustituir los pendientes anteriores ni cambiar SIG/cálculos/pilotos. Skills empleadas: `frontend-design`, `planning-and-task-breakdown` y descubrimiento de skills. La planificación exige revisar esta arquitectura con el usuario antes de implementar.

## Aprobación y primer incremento · 12 octubre

El usuario aprobó avanzar e integrar Blender de inmediato. Primera escena orográfica con receta, `.blend`, producto animado y composición editable probada en vertical/horizontal: `RECURSOS-BLENDER-20261012.md`. La etapa 1 tiene evidencia técnica del recorrido completo, cancelación y controles, pero transparencia y aprobación estética/responsive humana siguen pendientes. No se han terminado las etapas 2/3 ni los otros tres modelos. Los párrafos inferiores documentan la propuesta previa; no interpretar su estado inicial como la entrega actual.

## Diagnóstico del código actual

`studio_resources_ui.py` es una galería de seis esquemas con controles y un enlace al editor. `studio_resources.py` produce textos y formas 2D con composición semejante en todas las plantillas. `studio_resource_projects.py` permite guardarlas/reutilizarlas. El lienzo compartido de Studio sí permite manipular elementos, pero no hay objeto 3D, cámara, luces, materiales, edición de trayectorias o puente de render 3D a MP4. Cambiar las miniaturas no resuelve esa carencia.

Ya existen recursos aprovechables: Three.js 0.180 local con licencia MIT y procedencia en `assets/vendor/three-r180`; modelos conceptuales en `assets/js/learning-world.js` (fallas, escorrentía, aire orográfico), funciones científicas separadas y límites documentados en `documentation/aprender-3d.md`. No existe transferencia de esos modelos a Studio. Su geometría didáctica no equivale a DEM, simulación hidrodinámica o medición de campo.

La GPU reportada es Intel Iris Xe integrada. El nombre del adaptador no demuestra rendimiento; hace falta medir la primera escena. No se encontró `blender` en PATH ni en la carpeta convencional examinada. No se instaló nada durante esta revisión.

## Experiencia objetivo

Recursos debe abrir un área de trabajo, no un formulario largo con ejemplos casi iguales:

```text
Proyecto / formato / deshacer / reproducir / guardar / Enviar a Studio
┌──────────────────┬───────────────────────────┬──────────────────────┐
│ Buscar recursos  │                           │ Objeto seleccionado  │
│ Plantillas       │    Lienzo 2D + objeto 3D  │ Color / tipografía   │
│ Objetos 3D       │    fondo real del video   │ Cámara / iluminación │
│ Diagramas        │    texto y flechas encima │ Material / animación │
│ Multimedia       │                           │ Fuente / límites     │
│ Mis recursos     │                           │                      │
├──────────────────┴───────────────────────────┴──────────────────────┤
│ Escenas / pistas de objetos / animación / fotogramas clave          │
└────────────────────────────────────────────────────────────────────┘
```

Biblioteca buscable por tema, medio y función narrativa: clima/mar, agua/territorio, geología/sismos, naturaleza; objetos independientes y escenas completas. Miniaturas del contenido real, vistas animadas solo al solicitarlas, estado claro de disponible/en preparación. No anunciar como disponible un catálogo futuro.

Mantener la identidad Ecuador Vivo: fondo tinta `#0c1b24`, superficies `#112b36`, acento `#58e4ce`, texto `#edf5f7`, secundario `#b8cbd1`, líneas `#33515e`. El objeto explicativo domina el lienzo; la interfaz permanece discreta. Tipografía existente del proyecto para evitar descargas. Fondos, márgenes, títulos y créditos son editables, no parte de un póster aplanado.

## Referencias abiertas revisadas

- [Konva](https://github.com/konvajs/konva) y su [editor de ejemplo](https://konvajs.org/docs/sandbox/Canvas_Editor.html): selección, transformaciones, biblioteca, alineación, recorte y capas. MIT; candidato para piezas puntuales, no reemplazo automático del lienzo existente. Incorporarlo exigiría probar que las ediciones se conservan en el exportador actual. Polotno es un SDK comercial según el README de Konva: no adoptarlo como dependencia gratuita sin condiciones.
- [Three.js](https://github.com/mrdoob/three.js): base recomendada para objetos/cámara/materiales y edición 3D. Ya incluido localmente, no hace falta clonar su historial. [GLTFExporter](https://threejs.org/docs/pages/GLTFExporter.html) exporta modelos/escenas glTF, NO el video MP4; esa integración es un trabajo aparte. [WebGLRenderer](https://threejs.org/docs/pages/WebGLRenderer.html) fundamenta el visor. Usar la versión local verificada; los ejemplos actuales pueden requerir adaptar API.
- [Theatre.js](https://github.com/theatre-js/theatre): referencia de diseño de animación por propiedades y fotogramas clave. Su README distingue core Apache 2.0 y editor AGPL 3.0; no tratar todo el paquete como Apache ni incorporar su editor sin revisar las obligaciones. Inicialmente diseñar pistas propias sobre el reloj de Studio.
- [Blender, repositorio oficial](https://github.com/blender/blender): opción futura para modelado y render de mayor elaboración. Software GPL, gratuito. No es necesario instalarlo para la primera prueba Three.js ni implica que sea rápido en esta GPU. Las páginas del manual consultadas no estuvieron accesibles en esta herramienta, por lo que no se basa una implementación específica de Eevee en su lectura.

No copiar código sin conservar licencia/atribución. La licencia del motor no concede licencia sobre cualquier modelo o textura encontrada en Internet. Registrar autor, URL, licencia y fecha por asset; preferir modelos propios y materiales simples al inicio.

## Arquitectura recomendada

Un proyecto, biblioteca y reloj existentes. Recursos añade un modo de autoría al lienzo de Studio; no otra aplicación ni un registro duplicado de voz/subtítulos/mapas.

La receta 3D debe guardar identificador/versión del generador, objetos y parámetros permitidos, materiales, cámara, luces, movimiento y procedencia. Nada de ejecutar JavaScript/Python pegado dentro de un proyecto. Datos reales y modelos conceptuales se distinguen explícitamente; los parámetros visuales no alteran resultados científicos.

El lienzo 2D compone texto, flechas, llamadas, gráficos vinculados y créditos sobre la salida del 3D. El modelo permanece editable en su receta; al enviarlo a Studio se conserva esa receta y el producto verificado, con opción de volver a editar. No entregar únicamente un clip plano y llamarlo modelo editable.

Render: evaluar cada cuadro a `frame / 30`, resolución fija y semilla estable para partículas. NO grabar el visor en tiempo real como garantía de video: puede omitir cuadros. Primero demostrar la captura/exportación determinista de una sola escena y su inserción en el exportador actual. Salida intermedia con transparencia cuando corresponda, cache por receta/version/tamaño; el MP4 final conserva la composición y el audio del video.

Previsualización ligera y exportación Full HD son modos separados. Limitar contexto 3D activo a uno, descargar geometrías/texturas al cerrar y cancelar jobs de forma explícita. Sin descargas masivas de modelos ni nuevas carpetas de PNG permanentes por defecto. Transparencia y compatibilidad de codecs deben probarse, no darse por hechas.

## Recursos iniciales que aportan una explicación

1. **La montaña no fabrica agua**: bloque de relieve con agua/aire, cámara oblicua, recorrido del aire, condensación conceptual y llamadas sincronizadas. Reutilizar la base orográfica y mejorar geometría/materiales/composición. No presentar el umbral visual como cálculo de temperatura ni una nube como prueba de lluvia.
2. **La misma lluvia, distinto terreno**: cuenca en corte, superficie permeable/impermeable, infiltración/escorrentía. Animación didáctica, no simulación de caudal. Solo introducir cifras si se mantiene el balance/fuente/límites declarados.
3. **El Niño: superficie y subsuelo**: sección del Pacífico, viento, agua superficial y termoclina; controles de comparación conceptual, secuencia guiada. Separar esa explicación de SST/índices reales vinculados, con referencia temporal/metodológica explícita; no afirmar que todos los episodios causan lo mismo en todas las provincias.
4. **Una falla en movimiento**: capas, marcador, desplazamiento y cámara; normal/inversa/desgarre, fuentes existentes. No sustituir la mecánica de ruptura por un movimiento rígido ni deducir magnitud.

Expansión posterior: río en corte y transporte de sedimentos, capas/plegamientos, rocas/minerales originales, hábitats/especies con assets licenciados, relieve de datos reales, Slab2/hipocentros existentes. No inventar apariencia taxonómica ni geología de un lugar para llenar la biblioteca. Texturas o imágenes generadas son apoyo artístico, NO modelos 3D reales ni evidencia.

## Orden de implementación y aceptación

### 1. Prueba vertical 3D → Studio → MP4

Alcance: recurso orográfico de 10–15 s con receta editable, objeto 3D real y textos 2D separados. Probar vertical 1080×1920 y horizontal 1920×1080; conservar la salida en temporal hasta aprobación.

Aceptación: cámara/materiales/progreso guardan y reabren; mismos cuadros críticos en preview y exportación bajo tolerancia definida; MP4 tiene duración/cuadros correctos, antialiasing y etiquetas legibles; conserva el proyecto previo y su voz/subtítulos. Transparencia, cancelación y repetir exportación no generan crecimiento ilimitado. No ampliar el catálogo hasta aprobar visualmente este ejemplo.

Archivos previstos: nuevo módulo/receta 3D pequeño, puente de render, integración de asset existente, tests focalizados. No reescribir a la vez todo el editor y todas las plantillas.

### 2. Editor y biblioteca integrados

Alcance: mostrar Recursos como modo del lienzo compartido; biblioteca lateral con búsqueda, objetos/plantillas, inspector contextual y guardar/enviar. Reutilizar transacciones/historial existentes y los proyectos guardados actuales.

Aceptación: arrastrar/editar/borrar objetos y texto, seleccionar cámara/animación, insertar al video sin perder la receta; acciones con teclado/foco, carga ligera y errores claros; no duplicar una misma edición en varios formularios. Pruebas AppTest/transacciones + prueba de navegador autorizada de layout y WebGL.

### 3. Animación reutilizable y variedad

Alcance: fotogramas clave para posición/rotación/escala/cámara, presets de giro, aparición, acercamiento y flechas/recorridos; tres recursos posteriores al orográfico en las mismas primitivas. Importación GLB solo después de definir límites y política de texturas externas.

Aceptación: reloj de 30 fps único, sin interpolar datos observados ausentes; reabrir y deshacer recuperan propiedades; cada recurso tiene fuente, límites, receta, preview y MP4 de prueba; elegir resolución no cambia la ciencia. No anunciar fotorealismo o simulación física universal.

## Riesgos y punto de revisión

El mayor riesgo es conseguir un visor atractivo sin una exportación equivalente. Segundo: instalar motores grandes que empeoren arranque/disco o rompan la composición de Studio. Por eso la primera entrega debe ser **un recurso completo de calidad visible**, no otra galería ampliada sin video probado.

La automatización de navegador fue denegada anteriormente y no se ha revocado explícitamente. No eludirla con otra herramienta. AppTest no valida WebGL: para aprobar la prueba 3D hará falta un recorrido manual del usuario o autorización específica para verificarla en navegador. No declarar paridad con Canva ni render 3D terminado sin esa evidencia.

Pendiente de aprobación de esta dirección antes de cambiar arquitectura o instalar dependencias. No se ha modificado la aplicación, el servidor, los pilotos ni las funciones científicas en esta revisión.
