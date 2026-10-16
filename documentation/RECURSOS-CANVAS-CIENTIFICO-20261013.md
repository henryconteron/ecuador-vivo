# Recursos: taller de explicación científica

## Autorización de implementación · 13 octubre

El usuario aprobó reproducir la maqueta e instalar candidatos. La restricción de
no instalar de la propuesta inferior queda sustituida por esa autorización.
Instalación aislada del SIG; BioRender es referencia propietaria, Bioicons y
Smithsonian son catálogos con licencia por objeto, no programas instalables.
No clonar colecciones masivas. Separar explícitamente instalación, integración
y validación; no considerar una dependencia instalada como herramienta probada.

Propuesta del 13 de octubre de 2026. Solicitud: investigación, ilustración y plan.
NO implementada. No instalar motores, modificar SIG ni alterar proyectos o datos
por esta solicitud. Skills: frontend-design, imagegen y planificación.

## Qué construir

Un creador de figuras, mecanismos, objetos y animaciones científicas con la
facilidad de composición de Canva. No una copia de Canva, otro SIG o una
aplicación externa incrustada. SIG explora/calcula; Recursos explica; Studio
monta el relato, voz, subtítulos y video final. Un documento e historial comunes.

## Base verificada en el código

- studio_resources.py contiene seis plantillas conceptuales: foco gráfico,
  temperatura a 2 m, milímetros de lluvia, calendario comparable, provincia vs.
  capital y anomalía. No es aún una biblioteca multidisciplinar de objetos.
- studio_resources_ui.py ofrece plantillas, 3D, guardados y lienzo libre, pero
  la galería sigue llevando a formularios, no a composición directa de objetos.
- El lienzo compartido ya resuelve capas, transformaciones, grupos, historial,
  formatos y ventanas flotantes. Aprovecharlo, no construir otro editor básico.
- Blender actual tiene una receta orográfica con cámara, materiales y render
  bajo petición. No es un modelador 3D general con manipulación directa.
- Ya hay guardado/inserción de recursos y exportación común. Three.js local
  disponible en assets/vendor/three-r180: verificar API de ESA versión.

## Contrato visual y crítica previa

Paleta: abisal #0b1821, petróleo #132b37, pizarra #203b49, papel #edf3f5,
turquesa #70d9c5, arena #e0b77b. Bahnschrift en títulos; Segoe UI de 13–15 px en
controles. Texto alineado a la izquierda, lienzo centrado según su formato.
Los colores de interfaz nunca sustituyen una escala científica.

Dos vistas dentro de Recursos: Biblioteca y Crear. Biblioteca no exige proyecto;
Crear abre un recurso independiente sin convertir ni borrar el video abierto.

```
EV / Inicio / SIG / Studio / Recursos       guardar / Enviar a Studio
Biblioteca | Crear                   formato / historial / reproducir
Objetos / Plantillas / 3D / Datos / Texto / Mis recursos / Importar
┌ biblioteca plegable ┐                                 ┌ propiedades ┐
│ buscar y filtrar   │       lienzo dominante           │ objeto      │
│ piezas reales     │       objetos conectados         │ animación   │
│ fuente y licencia │       texto y figuras editables   │ procedencia │
└ movible           ┘                                 └ contextual  ┘
Capas / pasos de explicación / animación local             desplegar
```

Biblioteca y propiedades movibles/plegables: no reservar columnas vacías.
El lienzo domina. Catálogo de objetos y mecanismos con miniaturas de contenido
real. Sin un gran hero ocupando el editor ni una pared de formularios iguales.
En 3D, anotaciones 2D separadas y controles contextuales de cámara/materiales.

Crítica: más tarjetas y neones repetirían la propuesta genérica. La diferencia
será construir explicaciones con objetos, conexiones, pasos y procedencia.
No mostrar capacidades futuras como disponibles ni sellos de validación falsa.
La ilustración de esta entrega es MAQUETA GENERADA, no captura funcional; su
ejemplo orográfico es conceptual, no medición ni simulación validada.

Ilustración realizada con imagegen integrado, solo para explorar/aprobar diseño;
sin incorporar la imagen a la aplicación. Prompt de dirección: «Maqueta de
escritorio en español, Ecuador Vivo Recursos, petróleo/turquesa, navegación
compacta, biblioteca científica plegable con objetos de varias disciplinas,
lienzo 16:9 dominante con relieve orográfico conceptual y anotaciones editables,
propiedades contextuales, fuentes/licencias y pasos de explicación plegables;
crédito Henry P. Conteron Moreta; señalar funciones por desarrollar». Se revisó
la imagen generada: títulos/controles principales legibles, jerarquía y selección
visibles. Los detalles artísticos del 3D no son un render obtenido del motor
actual ni una garantía de su rendimiento; eso debe demostrarse en RC5.

## Referencias primarias y decisión de encaje

| Referencia | Qué aprovechar | Decisión |
| --- | --- | --- |
| [BioRender canvas](https://help.biorender.com/hc/en-gb/articles/26447997366173-How-to-use-the-BioRender-canvas) | Búsqueda, barra contextual, alineación y organización narrativa | Inspiración de experiencia; no copiar biblioteca ni depender de su servicio |
| [Excalidraw](https://github.com/excalidraw/excalidraw) | Flechas vinculadas, bibliotecas y dibujo editable; MIT | Patrones de conectores/reutilización; no incrustar otra app ni imponer bocetos |
| [Fabric.js](https://github.com/fabricjs/fabric.js) | Transformaciones, grupos, intercambio SVG/JSON; MIT | Candidato solo si una prueba resuelve carencia real sin romper exportación; no migración automática |
| [React Flow / xyflow](https://github.com/xyflow/xyflow) | Nodos y conexiones; MIT | Referencia para mecanismos; módulo opcional, no motor universal de dibujo |
| [Bioicons](https://github.com/duerrsimon/bioicons) | SVG científicos de biología/química | Selección revisada; licencia/autor POR OBJETO, no asumir MIT para todos los dibujos |
| [Three.js](https://github.com/mrdoob/three.js) / [GLTFLoader](https://threejs.org/docs/pages/GLTFLoader.html) | Objetos, cámara, materiales y carga glTF | Versión local para interacción; demostrar equivalencia con render Blender/Studio. GLB no es MP4 |
| [Manim Community](https://www.manim.community/) | Animación explicativa matemática; MIT | Módulo posterior por recetas para fórmulas, funciones y vectores; no dependencia obligatoria de Inicio |
| [Ketcher](https://github.com/epam/ketcher) | Editor molecular web, variante standalone/WASM; Apache 2.0 | Extensión posterior de química; revisar peso y paquetes antes de instalar |
| [Smithsonian Open Access](https://www.si.edu/openaccess/faq) | Material 2D/3D marcado CC0 | Buscar modelos de historia natural; comprobar objeto/archivo, no descargar colecciones completas |

Licencias verificadas: [xyflow](https://github.com/xyflow/xyflow/blob/main/LICENSE),
[Three.js](https://github.com/mrdoob/three.js/blob/dev/LICENSE),
[Manim](https://github.com/ManimCommunity/manim/blob/main/LICENSE),
[Ketcher](https://github.com/epam/ketcher/blob/master/LICENSE).
Esto es evaluación de encaje, NO integración probada. Mantener avisos/autores:
el crédito de Henry P. Conteron Moreta no reemplaza atribuciones de terceros.

## Funciones objetivo

### Biblioteca y composición

- Buscar por disciplina, concepto, formato, tipo de objeto, estilo y licencia.
  Favoritos, recientes, propios y paquetes descargados solo bajo petición.
- Arrastrar piezas al lienzo; texto, llamadas, flechas rectas/curvas, conectores
  anclados que siguen al objeto, leyendas y etiquetas. Alinear/distribuir,
  agrupar, bloquear, ocultar, duplicar y recortar, con historial.
- Plantillas por propósito: mecanismo, ciclo, corte, antes/después, comparación,
  escala e incertidumbre. No reciclar la misma montaña para todas las ciencias.
- 9:16, 16:9, 1:1 y 4:5, guías configurables para redes y adaptación revisable.
  No deformar objetos, escalas o datos para llenar el formato.
- No prometer que una imagen importada se convierte automáticamente en piezas
  editables ni que todo SVG admite edición individual de sus componentes.

### Animación y 3D

- Pasos para revelar, destacar, atenuar y recorrer flechas. Inicio/duración por
  objeto y timeline plegable; fotogramas clave de posición, giro, escala/cámara.
- 3D con cámara, materiales y luces; vistas de corte/explotadas únicamente si el
  modelo y su estructura lo permiten. No todo GLB tiene anatomía interna o rig.
- Three.js para interacción, Blender para acabado de recetas compatibles.
  No render final por cada cambio de cámara. Vista ligera y final separados.
- PNG/video y SVG cuando el contenido sea vectorial compatible. Transparencia
  en PNG y formatos/secuencias probados; no prometer alfa en MP4 convencional.

### Ciencia, datos y transferencia

- Distinguir esquema conceptual, observación, resultado derivado e imagen
  generada de apoyo. Fuente, autor, licencia, fecha y límites por recurso.
- Vincular resultados desde SIG con unidades, periodo y método. Cambiar estilo
  no cambia cifras; faltantes no son ceros. La animación no inventa observaciones.
- Revisión humana explícita: sin revisar/revisado por persona. Una IA no
  garantiza exactitud científica absoluta ni referencias correctas por sí sola.
- Guardar receta/versiones/piezas. Enviar a Studio preserva vínculo editable,
  como copia o referencia versionada explícita, sin perder voz/subtítulos.
  No duplicar los editores de audio, mapas ni cálculos en Recursos.
- IA opcional para borradores artísticos: etiquetada, sin tratarla como evidencia
  ni inventar especies, anatomía, geología o cantidades para llenar el catálogo.

## Colecciones y ejemplos iniciales

Comenzar con clima/mar, agua/territorio y geología/sismos. Después biodiversidad,
química, física, matemáticas/estadística, biología/salud y sociedad/energía.
La arquitectura admite disciplinas; el contenido de cada una requiere revisión.

Demostraciones: lluvia orográfica; El Niño con océano/viento/termoclina conceptual
separado de SST real; falla/ondas sin deducir magnitud; red trófica con fuentes
de especie; observado/referencia/diferencia con resultado y unidades reales.

## Plan por entregas verificables

1. **Un recurso completo en el editor objetivo.** Biblioteca contextual de las
   seis plantillas existentes/lienzo libre → editar → guardar/reabrir → Studio
   → MP4. Aprobar equivalencia 9:16/16:9 y Undo antes de ampliar el catálogo.
2. **Objetos y diagramas.** Colección pequeña revisada, búsqueda/favoritos,
   conectores y llamadas. Aceptar un ciclo que se reorganiza sin romper anclajes;
   SVG seguro sin scripts/recursos externos; créditos conservados al exportar.
3. **3D y explicación animada.** Pulir receta orográfica, validar cámara,
   materiales y tiempos entre vista/final; después El Niño y falla. Textos
   separados, receta recuperable, cancelación y almacenamiento acotado.
4. **Ampliación temática y calidad.** Un paquete por incremento; Manim/Ketcher
   solo tras una prueba pequeña. Cada paquete entrega un video explicativo,
   no únicamente miniaturas. Revisar teléfono, teclado, contraste y fallo de GPU.

Tareas RC1–RC7 y dependencias en tasks/todo.md. No implementar hasta revisar esta
dirección con el usuario. El mayor riesgo debe probarse pronto: que el recurso
se vea/edite/guarde y produzca el mismo resultado al exportarlo.

## Arquitectura, fluidez y almacenamiento

Mantener Scene/Element, historial y exportador actuales; ampliar recetas con
versiones/migraciones explícitas. Si se evalúa Fabric u otro motor, probar primero
el contrato completo. No ejecutar código pegado en proyectos o plantillas.
No instalar todos los candidatos ni clonar sus historiales.

Gestos/zoom/cámara en cliente; transacciones al terminar gestos, no reiniciar
Streamlit por cada movimiento. Renders cancelables, proxies por receta/tamaño,
importaciones diferidas, un contexto 3D activo y liberación de recursos GPU.
Medir en el equipo real; fluidez y tiempo de apertura son criterios por validar,
no promesas de rendimiento de bibliotecas aún no integradas.

Catálogo ligero/miniaturas; tamaño/licencia antes de descargar un modelo. Caché
configurable con inventario, retirar solo derivados identificados, no originales
ni proyectos. No asumir Drive conectado ni prometerlo como alojamiento ya probado.

## Alcance de esta entrega

Solo investigación, plan e ilustración de propuesta. Ningún cambio de aplicación,
servidor, SIG, pilotos o cálculos. No navegador local ni mecanismos para eludir su
preferencia denegada. La maqueta generada no sustituye capturas del producto real
ni pruebas de interacción/render. Próximo paso recomendado: RC1–RC2, un recurso
real editado y exportado, con revisión visual antes de RC3–RC7.
