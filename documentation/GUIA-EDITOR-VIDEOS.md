# Ecuador Vivo · tu editor local de videos

## Abrirlo sin escribir código

1. En la carpeta del proyecto, haz doble clic en **Abrir editor de videos.vbs**.
2. Se abre el editor en `http://127.0.0.1:8510/`. Esa dirección funciona únicamente en tu computadora mientras está encendida la aplicación.
3. La primera instalación necesita Python e Internet. Las siguientes aperturas reutilizan el entorno preparado. No hay una suscripción ni un servicio de IA necesario para exportar.

No es la página pública de Ecuador Vivo: es una herramienta privada de producción. Usa una ventana de navegador como interfaz, pero los archivos se procesan localmente. Los datos y videos no se suben a GitHub.

## Tu primer video

En **Editor**, el selector **Tipo de video** cambia entre **Mapa temporal**, **Comparación climática** y **CSV geográfico** sin salir del espacio de edición. La comparación adapta título, unidades, mapas y tarjeta final al dato seleccionado. Conserva la misma identidad, créditos y zona segura de 1080 × 1920.

Para comparar: elige años y territorio, pulsa **Descargar y calcular comparación**, revisa los valores y edita el diseño. Lluvia suma meses completos; temperatura, velocidad del viento y humedad usan medias ponderadas por días. Si cambias fuente, variable, fechas o territorio, se bloquea la exportación anterior hasta recalcular. Los meses parciales y los píxeles sin todas las fechas no se tratan como cero. Puedes guardar el proyecto con las tablas y reabrirlo sin descargar otra vez.

Las herramientas de ENSO y mar/viento aún son de consulta y preparación de datos/scripts; no son exportadores automáticos de MP4. El panel de la **web** se abre aparte en `http://127.0.0.1:8511/`.

El editor tiene cuatro espacios. Solo se muestra el que seleccionas:

1. **Datos:** importa o consulta la serie y verifica fuentes, unidades, fechas y cálculos. En CSV revisa coordenadas, permisos y cita. Para una primera prueba usa 1–7 días.
2. **Maqueta:** es el único lienzo para ver y ajustar mapa y métricas. En **Fecha de trabajo del lienzo**, el deslizador cambia la fecha visible. Selecciona un elemento para mover, redimensionar, ocultar o eliminar. Los ajustes generales de paleta, plantilla y créditos están en **Configuración de la plantilla y créditos**. **OK · aplicar y guardar** redibuja textos e iconos en este mismo lienzo y guarda el borrador; no hace falta una vista previa aparte.
3. **Montaje:** elige relación de aspecto y resolución. Ajusta el tiempo del mapa y métricas; si activas una secuencia personalizada, aquí se controla el orden y duración de cada tarjeta y se importan ejemplos.
4. **Exportar:** guarda una copia definitiva del proyecto o descarga su JSON y pulsa **Generar video**. Los datos y el diseño actuales se validan directamente, sin obligarte a actualizar imágenes previas. El resultado y su progreso aparecen en **Exportaciones**, en la barra lateral.

Pulsa **OK** antes de cambiar de tarjeta, fecha o espacio si has movido piezas en el lienzo: los cambios locales aún no aplicados no viajan al video. **Guardar e ir a exportar** aplica la maqueta y abre la revisión de exportación; no inicia un render costoso sin tu siguiente confirmación.

**Obtener datos** sigue siendo el directorio de descargas. CHIRPS v3/NASA POWER permiten **Descargar y preparar → Usar esta serie en el editor**. INAMHI conserva observaciones puntuales y no las convierte en una superficie inventada.

### Fuentes automáticas y alcance

- **CHIRPS v3:** productos diarios preliminares o finales, en particiones basadas en satélite IMERG o reanálisis ERA5; paquete máximo de 31 días. Los GeoTIFF se recortan en el equipo e incluyen Ecuador continental y Galápagos. Las cifras diarias proceden de repartir totales pentadales: no son necesariamente una ventana idéntica de lluvia observada por cada pluviómetro.
- **NASA POWER:** precipitación, temperatura, viento y humedad diarios. Descarga un GeoTIFF multibanda y CSV por variable, hasta 366 días. El grid de meteorología tiene escala regional (~50–60 km); el cambio de tamaño para el video no le agrega resolución.
- **INAMHI:** consulta observaciones puntuales de las estaciones del visor, con CSV, fecha de descarga y manifiesto de procedencia. Puede faltar parte del histórico solicitado; la interfaz lo informa. Esas series sirven para revisar estaciones, no se promedian por provincia ni se usan como superficie en el mapa.
- **IGM, IIGE, IG-EPN, INOCAR, IEDG y Datos Abiertos Ecuador:** están enlazados en el directorio de fuentes para descubrir cartografía, geología, sismicidad y datos costeros. Todavía no son conectores de descarga automática: cada servicio requiere confirmar formato, escala, licencia y estructura antes de habilitarlo.

Los ZIP incluyen los datos preparados/originales aplicables, la consulta reproducible, crédito y manifiesto. La descarga local se guarda en `_local/video-studio/downloads/`; las copias ráster listas para el editor, en `_local/video-studio/imports/`. Esos archivos no se suben al sitio ni a GitHub.

Escribe textos breves: el editor reduce su tamaño para que quepan; un párrafo largo será menos legible en el teléfono. Las líneas personales vacías no muestran texto. El crédito de límites vacío recupera automáticamente la atribución a geoBoundaries. Los números de fechas, contador y escala se generan a partir de los datos; no son adornos editables libremente.

## Temperatura, índices y cobertura del suelo

1. Obtén **GeoTIFF numéricos y georreferenciados**, no capturas de pantalla coloreadas. Puedes usar los procedimientos de [la guía de datos](GUIA-DATOS-PARA-VIDEOS.md).
2. En **Datos**, cambia a «Mis archivos GeoTIFF», selecciona los archivos y pulsa **Leer archivos**. El editor guarda una copia local.
3. Revisa la tabla: marca solo las bandas de la variable, asigna una fecha `AAAA-MM-DD` por banda y pulsa **Usar esta serie**. No incluyas bandas de calidad o número de observaciones como si fueran fechas. No admite varias observaciones con la misma fecha; prepara previamente un mosaico si corresponde.
4. Usa la preparación adecuada: temperatura ya en °C, temperatura en Kelvin, índices o cobertura Dynamic World. Las plantillas ayudan, pero no identifican automáticamente el producto.
5. Revisa **fuente, unidades, frecuencia, factor, desplazamiento y NoData**. La fórmula aplicada es `valor mostrado = valor del TIFF × factor + desplazamiento`. No se aplican además los factores embebidos del archivo. Si ya exportaste °C, no vuelvas a restar 273,15.
6. Para categorías, usa los códigos exactos de tu producto y pulsa **Aplicar clases**. La tabla inicial es de Dynamic World, no de todos los mapas de uso del suelo. Se admiten hasta 12 clases.
7. Ajusta la escala y la región, revisa imágenes y genera el video.

Una serie diaria con fechas faltantes se rechaza. Si las observaciones son irregulares, selecciona «Por observación»: cada observación recibe aproximadamente la misma duración, aunque los intervalos reales entre fechas difieran. No se inventan días intermedios.

### Cómo elegir las métricas del cierre

En **Cierre final**, elige **Acumular** únicamente cuando cada mapa representa
una cantidad del intervalo: por ejemplo, CHIRPS en `mm/día` se suma y el
ranking anual queda en `mm`. Para temperatura, NDWI, MNDWI, anomalías u otras
variables intensivas, elige **Promediar**: el ranking y el mes destacado se
calculan como promedios temporales y mantienen la unidad original. Los valores
negativos no se eliminan; son válidos para índices y temperaturas. El promedio
nacional pondera la latitud para aproximar el área de cada píxel geográfico.

El ranking nacional es de **las 24 provincias**, incluida Galápagos. Para cada
fecha, el editor calcula la media de todos los píxeles válidos del ráster
original dentro del polígono ADM1 de cada provincia; luego acumula o promedia
esas medias según la variable elegida. No es una lectura de la capital ni una
estación meteorológica. Si tu GeoTIFF no llega a Galápagos, el cierre mostrará
solo las provincias realmente cubiertas, en lugar de inventar un valor insular.

No actives el cierre numérico para coberturas, usos del suelo u otras clases:
sus códigos son etiquetas y no admiten suma o promedio. Para esas capas, usa
un cierre editorial específico con proporciones de área preparadas fuera del
editor.

## Calidad visual y rigor

### Publicar en TikTok, Instagram y Reels

La **Maqueta Ecuador Vivo · aprobada** ya incorpora una zona segura común para TikTok, Instagram Reels y Shorts. El MP4 sigue siendo 1080 × 1920 (9:16), H.264, 30 fps; **Redes sociales** y **Márgenes amplios** son alternativas con más espacio. **Diseño clásico** recupera la distribución anterior.

Estos márgenes son una decisión editorial del proyecto, no coordenadas oficiales ni una garantía universal. [TikTok explica](https://ads.tiktok.com/resources/help/article/tiktok-auction-in-feed-ads?lang=en-GB) que el área segura depende de dimensiones, texto y formatos añadidos y que la vista previa puede diferir entre dispositivos. Su guía corresponde a anuncios; se toma como referencia de diseño, no como certificación de publicaciones orgánicas. [Meta recomienda creatividades Reels verticales y dentro de una zona segura](https://www.facebook.com/business/ads/facebook-instagram-reels-ads).

En **Maqueta**, activa **Guías sociales** para orientar las piezas del formato 9:16. Las guías no aparecen en el MP4 ni en el PNG descargado. Exportar valida el diseño actual; ya no hay un botón separado para actualizar vistas previas. Revisa las frases y evita letras demasiado pequeñas.

Antes de publicar:

1. Genera una prueba corta y ábrela en el teléfono.
2. En la plataforma, conserva **9:16 / tamaño original**; evita ampliar con los dedos o «rellenar» con recorte.
3. Revisa el borrador con tu descripción, botones y subtítulos reales. Si ocupan más espacio, exporta con **Márgenes amplios** o acorta la descripción visible.
4. Comprueba la portada por separado: la cuadrícula del perfil puede usar un recorte diferente al video vertical. No se promete que la misma composición quepa completa en una miniatura cuadrada.
5. La duración de 9:09 del video anual se conserva si la eliges, pero no se garantiza que todos los tipos de publicación/cuentas la admitan. Para un clip corto de un año, baja la duración (por ejemplo 60–90 s); siguen apareciendo todas las fechas.

Los MP4 ya exportados no cambian: hay que generar una exportación nueva para aplicar estos ajustes. Los proyectos antiguos se migran a la maqueta aprobada; puedes elegir otra distribución en **Diseño**.

- 1080p es la resolución del video, no la resolución científica del sensor.
- La lluvia y otras variables continuas usan interpolación espacial para visualización; las categorías usan vecino más cercano para no mezclar códigos.
- La escala es fija durante el video. No cambies las unidades ni la atribución para hacer que los datos parezcan otra variable.
- No se rellenan fechas faltantes con cero. Una fecha CHIRPS aún no publicada detiene la exportación y muestra el error.
- Los TIFF deben llegar con las máscaras de nubes/calidad y las agregaciones científicas ya preparadas. El editor no determina por sí solo si un cambio fue causado por minería, sequía u otro proceso.
- La fuente científica es obligatoria y no se sustituye por tu firma. Conserva también la atribución de los límites a geoBoundaries si personalizas ese texto.

## Dónde queda todo

Dentro del proyecto:

- `_local/video-studio/projects/`: configuraciones guardadas, sin los TIFF dentro del JSON.
- `_local/video-studio/imports/`: copias de GeoTIFF importados.
- `_local/video-studio/downloads/`: paquetes descargados de CHIRPS v3, NASA POWER e INAMHI con sus manifiestos.
- `_local/video-studio/cache/`: nuevos datos descargados y límites.
- `_local/video-studio/jobs/`: una carpeta por exportación con MP4, configuración, imágenes inicial/final, `endcard.png`, registro y recibo de procedencia con hashes.
- `_local/climate-studio/`: los datos de lluvia y videos anteriores; el editor los reutiliza sin borrarlos.

Respalda **projects + imports** juntos. Los proyectos importados en otro equipo requieren volver a enlazar su serie mediante la carga de GeoTIFF. Cada exportación tiene una carpeta nueva: no sobrescribe el original.

## Si algo se interrumpe

Puedes cerrar la pestaña mientras se exporta, pero no apagues ni suspendas la computadora. «Cancelar esta exportación» se atiende después de la lectura en curso; una descarga puede tardar en responder. Los archivos incompletos nunca aparecen como MP4 terminado. Si se cierra inesperadamente el proceso, el editor permite iniciar otra exportación sin borrar los datos anteriores.

Si la dirección local no abre, vuelve a usar **Abrir editor de videos.vbs**. Si falla, revisa `_local/video-studio/server-errors.log`.

## Alcance de esta versión

Una variable principal por mapa, con formatos verticales, cuadrados y horizontales y una secuencia de tarjetas. CHIRPS v3 y NASA POWER pueden preparar series ráster desde el propio panel. Los CSV con coordenadas pueden representarse como puntos mediante **CSV geográfico**; no se convierten en una superficie interpolada de estaciones automáticamente. Puedes intercalar fotos, clips, explicaciones y pausas del último mapa. Los clips admiten conservar su audio original; no hay pista musical global, narración automática, transiciones ni varios mapas animados independientes en un mismo proyecto. Los demás portales están catalogados para siguientes conectores.

## Editar la maqueta sin escribir código

El lienzo está en **Editor → Maqueta**, no en otra aplicación. Funciona con **Maqueta Ecuador Vivo**, **Comparación climática** y **CSV geográfico**.

1. Elige **Mapa** o **Métricas**. Sus distribuciones se guardan por separado. Cambia la fecha visible con el deslizador; la exportación conserva toda la serie, no solo esa fecha.
2. Haz clic en una pieza o selecciónala en **Elemento**. Arrastra o escribe **X**, **Y**, **Ancho**, **Alto**. Las medidas son de la maqueta base 1080 × 1920, no de tu monitor.
3. Ajusta letra, color, texto editable o icono. **Añadir texto** y **Añadir icono** crean piezas. Movimiento y eliminación se ven al instante; **OK** redibuja contenido e iconos con el mismo motor del MP4.
4. **Eliminar elemento** (o **Supr** con el lienzo enfocado) lo retira del diseño y de la lista principal. **Elementos eliminados → Recuperar elemento** lo devuelve, incluso después de guardar. **Ocultar elemento** es una alternativa temporal que lo mantiene en la lista.
5. **Deshacer / Rehacer** funcionan antes de aplicar. **Restaurar tarjeta** recupera la composición inicial de esa tarjeta, sin cambiar datos ni la otra tarjeta.
6. **OK · aplicar y guardar** actualiza un borrador local del proyecto abierto. No crea una copia nueva por cada ajuste y nunca sobrescribe el proyecto original. En **Exportar → Guardar proyecto** puedes crear una versión independiente.
7. **Guardar e ir a exportar** aplica primero y abre Exportar. El PNG de la tarjeta actual también se puede descargar desde el mismo lienzo.

El borrador queda en `_local/video-studio/projects/borrador-maqueta-FECHA-HORA-ID.json`. No publica en GitHub. Las cifras eliminadas siguen en las tablas y recibos: se retira su representación, no el dato científico. Conserva créditos visibles antes de publicar.

### Qué se mantiene vinculado a los datos

- El continente, sus puntos y nombres se mueven como un grupo para no descolocar ciudades. Galápagos y la leyenda son grupos separados.
- Los mapas conservan su proporción. En las comparaciones, la barra de distancia y el norte viajan con el mapa y se redimensionan juntos; la plantilla de lluvia no lleva una barra de distancia.
- Cambiar el tamaño de la leyenda no cambia su rango, unidades ni paleta. Ampliar un mapa no mejora la resolución científica del sensor.
- Las cifras y fechas calculadas permiten ajustes visuales, pero no sustituir manualmente su valor. Los valores de las barras estadísticas tampoco se editan arrastrando. Los textos generales siguen disponibles en **Textos y créditos**.
- Bordes auxiliares y detalles cartográficos internos no son piezas independientes. El lienzo no edita geometrías geográficas; el orden y los tiempos se manejan en **Formato y secuencia de tarjetas**.

### Márgenes y legibilidad

El lienzo editable usa el video completo: al aplicar una distribución propia ya no se añade el encogimiento automático de la plantilla anterior. Mantén textos, leyendas y créditos importantes dentro de las **Guías sociales** amarillas. Son orientativas y no se exportan; no garantizan el mismo recorte en todas las plataformas. El mapa puede sobresalir de ellas si decides hacerlo, pero no dejes cifras importantes bajo botones o descripciones de la red social.

Se avisa cuando hay textos pequeños. Comprueba que tus frases caben en sus cajas y que los elementos no se superponen. El editor no sustituye la revisión de un borrador real en TikTok o Instagram.

## Elegir formato y montar una historia

Todo está en **Editor → Montaje**. Sirve para mapas temporales, comparaciones climáticas y CSV geográficos; no abre otro laboratorio.

1. Elige un formato y resolución: **9:16** (1080 × 1920), **16:9** (1920 × 1080), **1:1** (1080 × 1080), **4:5** (1080 × 1350) o **4:3** (1440 × 1080). También puedes exportar a **720p**, reduciendo proporcionalmente ambas dimensiones. Los MP4 son H.264, 30 fps.
2. Cambia **Fondo de los márgenes** si lo necesitas. Los mapas y las métricas encajan completos y mantienen su proporción: nunca se recortan automáticamente. La maqueta de mapas sigue diseñada sobre un lienzo vertical de 1080 × 1920; elegir horizontal añade márgenes laterales, **no redistribuye las piezas como una plantilla horizontal nueva**. El lienzo de Maqueta muestra estos márgenes de salida; los textos verticales se verán más pequeños en horizontal.
3. Activa **Usar secuencia personalizada**. Se conserva exactamente un **Mapa animado**; se incluye el cierre si estaba activado. El listado muestra el inicio y final de cada tarjeta y la duración total.
4. En **Añadir imágenes, clips o explicaciones**, escoge el tipo y pulsa **Añadir a la secuencia**. Puedes cargar PNG, JPG, WebP, MP4, MOV, WebM o MKV, hasta **100 MB por archivo**. También hay tarjetas de explicación, pausas del último mapa y copias de las métricas. Hasta 30 tarjetas y dos horas de montaje.
5. Selecciona **Tarjeta de la secuencia**. Con **Antes / Después** cambias el orden; **Duplicar tarjeta** repite una imagen, ejemplo o cierre; **Quitar de la secuencia** lo retira del montaje, sin borrar el archivo original. El mapa animado no se duplica ni se elimina.
6. Cambia el nombre, título, explicación, duración y **Fuente / fecha / créditos del ejemplo**; pulsa **Aplicar tarjeta**. Usa frases cortas: si no caben con tamaño legible se pide reducirlas, sin truncarlas silenciosamente.
7. Para una imagen o clip, elige **Encajar completo** (sin recorte) o **Rellenar con recorte** (decisión explícita tuya). Los títulos y créditos tienen franjas propias y no tapan el ejemplo. En un clip, selecciona **Inicio dentro del clip** y duración; activa **Conservar audio** solo si quieres usar su audio original. El fragmento no puede exceder el video fuente: no se repite, acelera ni inventa material para completar tiempo.
8. Para mapa y métricas, deja **Usar duración de los controles del editor** o desmárcalo para dar un tiempo propio a esa tarjeta. **La duración manual de la secuencia prevalece**. Se redondea a fotogramas de 1/30 s. Si hay más fechas que fotogramas, el editor pide aumentar la duración; no descarta fechas silenciosamente.
9. La tarjeta ilustrativa seleccionada se muestra automáticamente después de aplicar sus ajustes. Mapa y métricas se ven y editan solo en **Maqueta**. Cambiar de formato no cambia los cálculos.
10. En **Exportar**, guarda el proyecto y pulsa **Generar video**. Incluye todas las tarjetas, en el orden y tiempos elegidos, mediante cortes directos.

Ejemplo: explicación (3 s) → mapa histórico (20 s) → clip de archivo (5 s) → pausa del último mapa (3 s) → métricas (8 s). Para un sismo, verifica fecha, lugar, fuente y permiso de reutilización del clip. Un video ilustrativo no prueba la causa de un fenómeno ni entra en las estadísticas del mapa.

### Archivos, respaldo y trazabilidad del montaje

- Las fotos y clips se copian a `_local/video-studio/media/`; importaciones idénticas no duplican el archivo. No se suben a internet automáticamente. **Respalda projects + imports + media** juntos. Cambiar o borrar una copia importada bloquea la exportación hasta volver a importarla.
- **Exportar → Guardar proyecto** crea una versión independiente. Los archivos anteriores no se sobrescriben. Un JSON no contiene las fotos ni videos: al trasladarlo a otro equipo hay que volver a importar esos recursos.
- Cada exportación conserva el orden, fotogramas, duraciones, créditos y hashes de los ejemplos en `receipt.json → montage`. Las métricas siguen procediendo exclusivamente de los datos científicos seleccionados. Preparar un caso de Andes Pulso conserva esa trazabilidad sin publicar rutas personales del equipo; sigue siendo un borrador que tú revisas antes del commit.
- El montaje genera segmentos intermedios y puede ocupar más espacio que el MP4 final. Se conservan en la carpeta de esa exportación para diagnóstico; no se borran automáticamente. Comienza con una prueba corta, especialmente si tienes poco espacio.
- Las guías sociales del lienzo son orientativas para vertical, no para todas las relaciones de aspecto. Revisa el video y la portada en el teléfono; la interfaz de cada red puede cubrir o recortar áreas distintas.

Prueba técnica reproducible, con los datos originales de temperatura que ya estén en la caché y sin nuevas descargas: `python production/video_studio/preview_editorial.py --video --story-demo`. Produce un montaje de 15 s, horizontal 1280 × 720, con explicación, mapa, imagen, clip ilustrativo y cierre. No publica ni modifica tus proyectos guardados.
