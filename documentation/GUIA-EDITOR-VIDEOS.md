# Ecuador Vivo · tu editor local de videos

## Abrirlo sin escribir código

1. En la carpeta del proyecto, haz doble clic en **Abrir editor de videos.vbs**.
2. Se abre el editor en `http://127.0.0.1:8510/`. Esa dirección funciona únicamente en tu computadora mientras está encendida la aplicación.
3. La primera instalación necesita Python e Internet. Las siguientes aperturas reutilizan el entorno preparado. No hay una suscripción ni un servicio de IA necesario para exportar.

No es la página pública de Ecuador Vivo: es una herramienta privada de producción. Usa una ventana de navegador como interfaz, pero los archivos se procesan localmente. Los datos y videos no se suben a GitHub.

## Tu primer video

1. **Editor → Datos:** deja «Lluvia CHIRPS · automática». Empieza con 1–7 días de enero de 2024 para probar. El año 2024 completo ya está descargado en este equipo.
2. **Diseño:** cambia título, subtítulo, leyenda, nota, fondo, color del texto y paleta. Pulsa **Aplicar paleta** o **Aplicar escala** si modificas sus tablas.
3. **Textos y créditos:** escribe tu nombre en «Tu nombre / autoría», por ejemplo `Elaborado por Henry P. Conteron Moreta`. Añade tu cuenta o colaboradores en «Créditos adicionales / redes». También puedes editar la marca superior, las fuentes visibles, las unidades, las notas, el formato de fecha, la palabra del contador y las etiquetas de las ciudades.
4. **Mapa y tiempo:** elige región, ciudades y duración. «Usar ritmo original» asigna 1,5 segundos por fecha: 366 días ocupan 549 segundos (9 min 9 s). Elige 1080 × 1920 y calidad Alta para conservar el formato original.
5. **Actualizar vista previa:** revisa varias fechas usando el deslizador. La vista previa y el MP4 usan el mismo dibujado. Los cambios no aparecen en la imagen hasta actualizarla.
6. **Guardar proyecto:** conserva tu configuración, incluida tu firma. Así podrás abrirla después y cambiar únicamente los datos y las fechas.
7. **Generar video:** abre **Exportaciones** para ver el progreso, reproducir el resultado, descargar el MP4 o abrir su carpeta.

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

## Calidad visual y rigor

### Publicar en TikTok, Instagram y Reels

En **Mapa y tiempo → Distribución para publicar**, usa **Redes sociales**. El MP4 sigue siendo 1080 × 1920 (9:16), H.264, 30 fps; el contenido se redistribuye, no se estira. Se reservan 220 px arriba, 440 abajo, 80 a la izquierda y 200 a la derecha. El título, mapa, leyenda, notas y firma quedan dentro de esa área. **Márgenes amplios** reserva 280 px arriba y 680 abajo, con un mapa menor. **Original** recupera la distribución anterior, que no protege los créditos frente a la interfaz social.

Estos márgenes son una decisión editorial del proyecto, no coordenadas oficiales ni una garantía universal. [TikTok explica](https://ads.tiktok.com/resources/help/article/tiktok-auction-in-feed-ads?lang=en-GB) que el área segura depende de dimensiones, texto y formatos añadidos y que la vista previa puede diferir entre dispositivos. Su guía corresponde a anuncios; se toma como referencia de diseño, no como certificación de publicaciones orgánicas. [Meta recomienda creatividades Reels verticales y dentro de una zona segura](https://www.facebook.com/business/ads/facebook-instagram-reels-ads).

Activa **Ver márgenes de seguridad** bajo la imagen para comprobar dónde podría superponerse la interfaz. Las franjas rojas son orientativas y nunca aparecen en el MP4 ni en el PNG descargado. Si una frase no cabe con tamaño legible, el editor pide acortarla, sin ocultarla ni reducirla a letra diminuta. Tras cambiar ajustes es obligatorio actualizar la vista previa antes de exportar.

Antes de publicar:

1. Genera una prueba corta y ábrela en el teléfono.
2. En la plataforma, conserva **9:16 / tamaño original**; evita ampliar con los dedos o «rellenar» con recorte.
3. Revisa el borrador con tu descripción, botones y subtítulos reales. Si ocupan más espacio, exporta con **Márgenes amplios** o acorta la descripción visible.
4. Comprueba la portada por separado: la cuadrícula del perfil puede usar un recorte diferente al video vertical. No se promete que la misma composición quepa completa en una miniatura cuadrada.
5. La duración de 9:09 del video anual se conserva si la eliges, pero no se garantiza que todos los tipos de publicación/cuentas la admitan. Para un clip corto de un año, baja la duración (por ejemplo 60–90 s); siguen apareciendo todas las fechas.

Los MP4 ya exportados no cambian: hay que generar una exportación nueva para aplicar esta distribución. Los proyectos sin un campo de distribución adoptan Redes sociales al abrirse; puedes recuperar Original en el selector.

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
- `_local/video-studio/cache/`: nuevos datos descargados y límites.
- `_local/video-studio/jobs/`: una carpeta por exportación con MP4, configuración, imágenes inicial/final, registro y recibo de procedencia con hashes.
- `_local/climate-studio/`: los datos de lluvia y videos anteriores; el editor los reutiliza sin borrarlos.

Respalda **projects + imports** juntos. Los proyectos importados en otro equipo requieren volver a enlazar su serie mediante la carga de GeoTIFF. Cada exportación tiene una carpeta nueva: no sobrescribe el original.

## Si algo se interrumpe

Puedes cerrar la pestaña mientras se exporta, pero no apagues ni suspendas la computadora. «Cancelar esta exportación» se atiende después de la lectura en curso; una descarga puede tardar en responder. Los archivos incompletos nunca aparecen como MP4 terminado. Si se cierra inesperadamente el proceso, el editor permite iniciar otra exportación sin borrar los datos anteriores.

Si la dirección local no abre, vuelve a usar **Abrir editor de videos.vbs**. Si falla, revisa `_local/video-studio/server-errors.log`.

## Alcance de esta versión

Video vertical, una variable principal por video, sin audio. Descarga automática de lluvia CHIRPS; temperatura, índices y cobertura se importan como GeoTIFF preparados. No incluye todavía montaje de varias escenas, narración, música, edición libre por arrastre ni descarga automática de todas las fuentes. El resultado puede llevarse a un editor de video para añadir esos elementos.
