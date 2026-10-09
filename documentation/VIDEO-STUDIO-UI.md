# Contrato de interfaz · Estudio de video

## Alcance

Mejorar exclusivamente la interfaz local de `production/video_studio`: jerarquía,
tipografía, espaciado, adaptación y accesibilidad. Se conservan las claves de
estado, callbacks, validación, cálculos, datos y composición del MP4/PNG.
No se añade una segunda vista previa ni otro servicio.

## Referencias y decisiones

Se revisaron tres pantallas del producto existente: **Datos**, **Maqueta** y
**Montaje**, junto con la maqueta editorial de lluvia ya aprobada. No se copia
una interfaz externa ni se añaden ilustraciones decorativas.

- Datos: mantener formularios nativos y avisos de fuentes; reducir el peso del
  título general y distinguir la fuente del periodo.
- Maqueta: el lienzo es el área principal. Herramientas agrupadas arriba;
  propiedades organizadas en selección, posición, contenido y organización.
  Guardar debe permanecer visible sin recorrer todo el inspector.
- Montaje: agrupar formato, resolución y fondo con controles que se envuelven
  cuando falta anchura. Mantener la secuencia separada del diseño.
- Navegación: cuatro fases numeradas, con los valores internos intactos.
  La barra lateral mantiene proyectos y navegación global.

## Sistema visual

Azul tinta de Ecuador Vivo en la barra lateral y el texto; área de trabajo
blanco papel, superficies gris verdoso y turquesa oscuro para acciones y
selecciones. El mapa conserva su fondo original. Sin gradientes, tarjetas
promocionales, fondos ilustrados ni CDN.
Fuentes locales Segoe UI/system-ui; cuerpo 16 px; títulos 32/24/20 px.
Espaciado de 4/8/12/16/24 px; bordes visibles; radio de 6 px.
El tema nativo de Streamlit gobierna controles y colores. El componente del
lienzo consume las mismas variables `--st-*` dentro de su ámbito aislado.

La prueba en navegador mostró que Streamlit usa texto blanco sobre el color
primario de botones y etiquetas seleccionadas. Un turquesa claro corregía la
navegación sobre fondo oscuro, pero reducía ese contraste. Se adoptó una
superficie clara con acento oscuro en el área principal para resolver ambos
estados sin sobrescribir estilos internos de Streamlit. La barra lateral
conserva el azul oscuro y controles secundarios.

## Adaptación y accesibilidad

- Comprobar 320, 768, 1024 y 1440 px de anchura.
- Lienzo e inspector en dos columnas donde caben; en una columna si el
  componente dispone de menos de 720 px. Sin scroll horizontal del formulario.
- Una cabecera h1 principal; secciones principales h2. Etiquetas persistentes.
- Foco visible, botones de al menos 44 px en el componente; controles nativos
  para teclado. Mantener las coordenadas como alternativa a arrastrar.
- Estado de cambios con `role="status"`; texto que explica los campos calculados
  no editables; ocultar elementos decorativos a tecnologías de asistencia.
- La selección no depende solo del color: se conserva el estado accesible del
  control nativo y el nombre del elemento seleccionado.
- Los errores, cargas, ausencia de datos y controles desactivados mantienen sus
  condiciones originales. No se disimula un error como resultado correcto.

## Verificación

Pruebas de regresión del estudio, revisión en navegador del lienzo y montaje,
teclado, contraste de tokens y desbordamientos en los cuatro tamaños. Estas
comprobaciones no sustituyen una auditoría completa con lector de pantalla.

### Resultado de la revisión · 7 octubre 2026

- 112 pruebas de regresión del estudio y 3 pruebas de contrato de interfaz: OK.
- Lienzo a 320/768/1024/1440 px: sin controles desbordados horizontalmente.
- Montaje a 320 px: formato, resolución y fondo se apilan sin recortarse.
- Movimiento con flechas, foco visible, eliminación y Deshacer comprobados en
  navegador; las pruebas de edición se deshicieron sin guardar el proyecto.
- Contraste de texto, notas nativas al 60% de opacidad, botones, selecciones,
  bordes y estados comprobado con los colores finales. La prueba en navegador
  confirmó blanco sobre turquesa oscuro en botones y etiquetas nativos.
- Sin errores ni advertencias en la consola durante la comprobación final.
- No se modificaron los módulos de cálculos ni los renderizadores del video.
