# Ecuador Vivo: mesa de producción editorial

## Segunda pasada: escenario inmersivo

El rechazo de la primera pasada confirma un problema de estructura: dos columnas
permanentes y varias filas auxiliares subordinan el video a sus herramientas.
La nueva propuesta conserva petróleo #132b37, abisal #0b1821, pizarra #203b49,
papel #edf3f5, turquesa #70d9c5 y ámbar #ffdc96 para reproducción/avisos.
Bahnschrift da carácter a Inicio y Recursos; Segoe UI mantiene legible el editor.
Todo alineado a la izquierda salvo el escenario, centrado por su formato real.

```
EV + espacios                               guardado / exportar
nombre / historial                           formato / reproducir
Escenas Capas Multimedia Datos ...             Propiedades / Solo video
┌──────────────── escenario a todo el ancho ───────────────────┐
│ [biblioteca móvil]                        [propiedades]      │
│                video, sin columnas reservadas                │
│              herramientas flotantes del lienzo               │
└─────────────────────────────────────────────────────────────┘
Montaje / duración / añadir                         desplegar
```

Las ventanas se abren solo al pedirlas, admiten movimiento/tamaño y conservan
posición por pestaña, no en el documento científico. Montaje inicia compacto;
Solo video oculta herramientas sin perderlas. Inicio pasa de tres tarjetas
iguales a un acceso Studio protagonista y dos accesos horizontales. Recursos
adopta una biblioteca de láminas en vez de miniaturas apretadas en cajas.

Crítica previa: no usar nuevos gradientes, métricas inventadas ni animaciones
de entrada para simular innovación. El gesto distintivo será el escenario libre
y las herramientas recuperables, con identidad cartográfica/editorial propia.
Mantener controles existentes, historial, accesibilidad y todas las rutas.
No modificar SIG ni producto final. La comprobación visual real sigue pendiente
por la preferencia de navegador denegada; no sustituirla por afirmaciones.

## Alcance

Rediseñar Inicio, Studio, Recursos y sus estados/formularios. Conservar el SIG,
datos, cálculos, proyectos, render del producto final y acciones existentes.
Sin dependencias, fuentes remotas, capacidades ficticias ni nuevas descargas.

## Contrato visual (frontend-design)

Paleta: fondo abisal `#0b1821`, superficie petróleo `#132b37`, relieve pizarra
`#203b49`, línea `#3c5867`, papel `#edf3f5`, señal turquesa `#70d9c5`.
Texto secundario `#b1c3cd`; avisos conservan sus colores semánticos.

Tipografía: Bahnschrift (con fallback Segoe UI) en titulares de Inicio/Recursos;
Segoe UI en edición, navegación y formularios. Datos y tiempos con cifras
tabulares. Jerarquía 36/24/18/14/12 px, sin etiquetas gritadas ni microtexto.

Inicio: navegación compacta, titular útil y acciones; tres accesos ilustrados
con distinto peso, después catálogo de proyectos. Recursos: cabecera, modos
visibles, biblioteca con resumen/categoría, configuración y vista del diseño
en superficies diferenciadas. Studio: barra de proyecto y navegación separadas
de las herramientas del lienzo; biblioteca, escenario, inspector y montaje.

```
Inicio / Recursos:  EV + espacios                         proyecto actual
                   titular / propósito             acción principal
                   biblioteca o accesos visuales
                   proyectos / configuración + muestra

Studio:            EV + espacios                     guardado / exportar
                   proyecto / formato / reproducción
                   biblioteca | herramientas del lienzo | propiedades
                              |       escenario        |
                   montaje / escenas / voz / subtítulos
```

Revisión del brief: descartar la cuadrícula SaaS de cajas idénticas, gradientes
decorativos y márgenes desmesurados. El protagonismo es de los mapas/videos y
recursos del usuario; el marco orienta sin competir. No cambiar el aspecto del
video exportado para embellecer la interfaz. No apilar otra capa de overrides:
consolidar el CSS de Studio y reemplazar los estilos propios de cada superficie.

## Verificación

Comparar huellas de los archivos del SIG antes/después. Mantener identificadores
y enlaces de acciones, historial, formatos, audios y accesibilidad de formularios.
Pruebas AppTest, contrato HTML, sintaxis JS/CSS y regresiones focalizadas.
La preferencia guardada sigue bloqueando navegador local: no eludirla. AppTest
no equivale a aceptar estética, desbordamientos o interacción en navegador.

## Implementado

### Segunda pasada entregada: escenario inmersivo

- Studio: escenario a todo el ancho sin columnas reservadas. Diez accesos de
  biblioteca arriba; propiedades en ventana no modal. Ambas ventanas se mueven
  por título, se redimensionan por esquina o flechas, se cierran y conservan
  geometría por pestaña. En pequeño se abre una a la vez. No emiten comandos de
  documento ni cálculos. Migración de las antiguas preferencias de columnas.
- Montaje inicia recogido y se despliega con su control; selección tiene acceso
  contextual a Editar. Barra flotante de lienzo, reproducción diferenciada y
  Solo video con salida visible. Historial, edición y exportación intactos.
- Inicio: Studio como acceso visual principal y SIG/Recursos en accesos
  horizontales; no se renderizan proyectos para esas portadas. Recursos: láminas
  editables más grandes, jerarquía de colección y cabecera ilustrada amplia.
- 51 pruebas Python (AppTest/contratos/regresiones), 5 pruebas Node del controlador
  de ventanas, JS correcto y cuatro hojas parseadas. 36 huellas protegidas de
  esta segunda pasada sin cambios. Sin dependencias, medios ni descargas nuevos.
- No se comprobó composición real en navegador: preferencia de acceso denegada.
  El DOM simulado no valida overflow, tipografía real ni captura visual. Revisar
  con captura humana tras Ctrl+F5. No afirmar aceptación estética todavía.

### Primera pasada (histórico inmediato)

- Inicio: cabecera compacta, acciones de proyecto visibles, accesos visuales con
  Studio destacado, catálogo con nombres/fechas y archivos técnicos relegados a
  la ayuda del botón. Búsqueda, orden, paginación y apertura intactos.
- Studio: dos filas diferenciadas (espacios/guardado/exportación y
  proyecto/formato/reproducción); marco del lienzo tranquilo, propiedades
  legibles, biblioteca con iconos consistentes y montaje con pistas de voz y
  subtítulos diferenciadas. Menús, selecciones y acciones conservan sus IDs.
- Recursos: navegación con identidad de marca, cabecera ilustrada reutilizando
  WebP local ligero; galería con categorías y resúmenes; configuración/vista
  agrupadas. Mismos cuatro modos: plantillas, 3D, guardados y lienzo libre.
- Estilo de los diálogos nativos de Studio acotado a su host; CSS común de
  Inicio/Recursos acotado a esas rutas. No se cambió el tema global.
- CSS del editor consolidado de 26.247 a 19.385 bytes, retirando reglas
  superpuestas, sin añadir dependencias ni nuevos medios. Nuevas reglas
  responsive y foco; no animaciones decorativas ni fuentes en red.

## Comprobado y pendiente

50 pruebas focalizadas correctas: navegación, creación y recuperación de
proyectos, biblioteca, edición, voz y Blender. Contratos de controles únicos y
contraste AA del marco aprobados. Sintaxis JS correcta; cinco hojas CSS parseadas
con PostCSS. Mutación de texto ilegible detectada por la prueba y restaurada.
Huellas de 37 archivos protegidos SIG/render/layout base sin cambios.

Limitación: no se ejecutó navegador ni se produjo una captura nueva; la
preferencia previa lo bloquea. Falta revisar el resultado real con capturas
humanas, especialmente móvil, menús y diálogos. No afirmar que AppTest valida
desbordamientos visuales. Sin commit, push, publicación, borrados ni cambios de
datos, cálculos, plantillas de video, pilotos o motores.
Instancia 8534 reiniciada sin abrir navegador y sin tareas de render activas;
health 200 y registro de errores vacío al arrancar. Recargar con Ctrl+F5.
