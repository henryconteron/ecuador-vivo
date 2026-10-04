# Un río visto desde el espacio — versión 9

Montaje local en `artifacts/rios_doce_v9/rio_doce_desde_el_espacio_v9.mp4`.
No modifica el atlas ni las versiones anteriores. No se publica automáticamente.
Duración del montaje: 10:06,5; 29 segmentos, 30 fotogramas por segundo.

## Capítulos

- 00:00 — Dos imágenes del río Doce y la rotura de Fundão.
- 01:02 — Qué registra un satélite.
- 01:42 — La señal de las partículas en el agua.
- 02:03 — Detectar agua y estudiar turbidez son preguntas distintas.
- 02:49 — Construcción y significado de MNDWI.
- 03:50 — Cambiar el umbral sin cambiar el río.
- 04:48 — Una celda, varias superficies; zoom sin detalle inventado.
- 05:30 — Nivel, superficie y caudal.
- 05:54 — Jatunyacu: observaciones de 2019, 2024 y 2026.
- 07:13 — Series temporales, conexión y nubes.
- 08:12 — Investigar las causas y qué no mide un índice.
- 08:54 — Volver al Doce: satélite más comprobaciones independientes.
- 09:41 — Fuentes y créditos.

## Dirección y apertura

Se recuperan el formato vertical 1080 × 1920, la paleta verde oscuro, crema y lima,
la jerarquía tipográfica y los subtítulos de la versión 6. La narrativa visual
parte de un cambio visible, presenta el hecho documentado y abre una pregunta;
el método llega después como respuesta. Es un guion original conversacional,
no una imitación de voz ni una copia de un divulgador.

Ambas imágenes satelitales del Doce aparecen juntas durante los tres segmentos
iniciales: arriba 11 septiembre 2015; abajo 30 noviembre 2015. Se muestra la
desembocadura, no se presenta un tributario como el río principal. El círculo es
una guía de atención, no una delimitación calculada de la pluma.

## Fuentes y qué sustentan

1. **USGS EROS (2015), Brazilian Mining Disaster, Doce River**.
   https://eros.usgs.gov/media-gallery/image-of-the-week/brazilian-mining-disaster-doce-river
   Fuente de las dos observaciones Landsat 8, sus fechas, ubicación y contexto
   del desastre. Se conserva la lámina original completa junto al montaje.
   Crédito: USGS EROS / Landsat; la lámina original también reconoce NASA.
   Se recortan los dos paneles de igual tamaño sin realzar colores ni inventar
   detalle. No se registran de nuevo ni se calcula superficie a partir del JPG.
   No se supone que la fecha anterior representa una cuenca intacta.
   Contexto adicional del desastre y nombre de Fundão: NASA Earth Observatory,
   *Contaminated Rio Doce Water Flows into the Atlantic* (2015):
   https://science.nasa.gov/earth/earth-observatory/contaminated-rio-doce-water-flows-into-the-atlantic-87083/

2. **Rudorff, N.; Rudorff, C. M.; Kampel, M.; Ortiz, G. (2018)**.
   *Remote sensing monitoring of the impact of a major mining wastewater disaster
   on the turbidity of the Doce River plume off the eastern Brazilian coast*.
   ISPRS Journal of Photogrammetry and Remote Sensing, 145, 349–361.
   https://doi.org/10.1016/j.isprsjprs.2018.02.013
   Resumen publicado consultado en NASA MODIS:
   https://modis.gsfc.nasa.gov/sci_team/pubs/abstract_new.php?id=27170
   Se consultó el resumen, no se afirma haber leído el texto completo.
   Sustenta el uso de Landsat y MODIS-Aqua, un método semianalítico con selección
   de bandas rojo/NIR y contraste con caudal y turbidez medidos en el río.
   El video **no reproduce** su estimación de turbidez. No convierte MNDWI en
   concentración de sedimentos ni atribuye el impacto solo por un color marrón.
   No repite cifras preliminares de víctimas, volumen o composición química.

3. **Xu, H. (2006)**. *Modification of normalised difference water index (NDWI)
   to enhance open water features in remotely sensed imagery*.
   https://doi.org/10.1080/01431160600589179
   MNDWI: (verde − SWIR) / (verde + SWIR). En Ecuador se usan B3 y B11 a 20 m.
   Es una demostración de superficie candidata a agua, no el algoritmo del Doce.

4. **McFeeters, S. K. (1996)**.
   https://doi.org/10.1080/01431169608948714
   Contextualiza la respuesta de agua y vegetación en el infrarrojo cercano del
   esquema introductorio. Las flechas no son espectros medidos.

5. **USGS, How Streamflow is Measured**.
   https://www.usgs.gov/water-science-school/science/how-streamflow-measured
   Distingue superficie mojada de caudal: sección y velocidad.

6. **Dethier et al. (2023)**.
   https://doi.org/10.1038/s41586-023-06309-9
   Contexto general de minería y sedimentos en ríos tropicales, no diagnóstico
   causal de las tres observaciones del Jatunyacu.

7. **Cavallo et al. (2025)**.
   https://doi.org/10.1016/j.jhydrol.2025.133416
   Contexto de observación de ríos no permanentes; no validación en Ecuador.

## Ecuador: trazabilidad y límites

Se reutiliza la evidencia auditada de la versión 6, sin descargar imágenes nuevas:
11 julio 2019, 8 agosto 2024 y 29 julio 2026. Crédito: contiene datos Copernicus
Sentinel modificados; procesamiento Henry Conteron / Ecuador Vivo.

Cuadrícula común 20 m; máscara de observaciones útiles; valores de bandas antes
de colorear. Los umbrales >0 y >0,2 son exploratorios, no calibrados para este río.
El cambio de umbral se aplica a la misma imagen 2024: modifica la clasificación,
no el paisaje. El zoom usa las muestras existentes sin crear detalle nuevo.
No se interpolan estados del cauce entre fechas. Véase `NAPO_RIOS_METODOS_V4.md`.

No se afirma que el Jatunyacu se secó ni que sus diferencias sean causadas por
minería. No se estima mercurio, profundidad, caudal o erosión a partir de MNDWI.
Los esquemas están rotulados como didácticos y no reconstruyen los sitios.

## Reutilización y revisión

Política de contenido USGS:
https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits
El contenido producido por USGS es de dominio público en Estados Unidos; la
agencia advierte que algunos materiales de terceros tienen derechos separados.
La lámina usada es una publicación USGS sin marca de copyright de terceros.
Se da crédito textual; no se usa su logotipo para sugerir aval del proyecto.

Narración sintética es-EC-LuisNeural. Se reutilizan grabaciones con idéntico texto
y solo se generan las nuevas intervenciones; no se contrata una API de pago.
Las versiones anteriores se conservan y sus hashes figuran en el manifiesto.

El manifiesto guarda origen, recortes, hashes y alcance de cada fuente. La
verificación técnica revisa el archivo codificado, audio, subtítulos y fotogramas.
Esto no sustituye escuchar el video completo ni una revisión científica humana.

## Comprobaciones y reproducción

Se añadieron cinco pruebas dedicadas: orden narrativo y alcance científico,
presencia simultánea de ambos paneles originales, máscara y conteos reales,
duraciones de voz y subtítulos, y conservación de versiones anteriores.

Preparación y montaje: `reel_river_satellite_story.py`, acciones `prepare`,
`voices`, `storyboard` y `export`, en ese orden. Requiere la lámina USGS descargada
y la evidencia local auditada de la versión 6. Las acciones usan la instalación
existente de video y reutilizan las grabaciones idénticas de la versión 8.

Verificación del MP4: `verify_river_satellite_story.py`. La salida de la revisión
se guarda en `verification.json`; las imágenes extraídas de cada escena quedan
en `encoded_*.jpg` y `storyboard_encoded.jpg`. El guion para grabar con voz humana
está en `GUION_PARA_GRABAR.md`, junto al MP4.
