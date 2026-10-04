# Ríos de Napo · NDWI con imágenes de 2026

Video educativo independiente del catálogo sísmico. No reemplaza ni modifica
los reels nacionales ni la serie Memoria sísmica. Se conserva su diseño vertical,
mapa desde el primer cuadro, tipografía, colores y crédito profesional.

## Qué se está produciendo

`artifacts/rios_napo_ndwi_2026/`: fuentes STAC, recortes GeoTIFF científicos,
vistas RGB/NDWI, manifiesto con SHA-256, guion, storyboard y video. La carpeta
está ignorada por Git como los demás videos; no se publica automáticamente.

Cuatro ventanas editoriales: entorno de Tena, tramo inferior del Jatunyacu,
Napo aguas abajo de Puerto Napo y entorno de Puerto Misahuallí. No equivalen
a cuencas, límites administrativos ni un inventario de todos los ríos de Napo.
Los cauces estrechos de Tena pueden quedar mezclados con sus orillas en 10 m.

## Selección de imágenes reales

- 11/07/2019: `S2B_17MRU_20190711_0_L2A`.
- 29/07/2026: `S2C_T17MRU_20260729T153626_L2A`, colección `sentinel-2-c1-l2a`.

Son adquisiciones individuales L2A, no medianas anuales. Se eligió el mismo mes
pero los días difieren en 18 días de calendario: **no se ha igualado el caudal**,
la precipitación antecedente ni el estado estacional del río. Son una comparación
educativa y una base para revisión, no una estimación de migración del cauce.

Se consultó el catálogo hasta el corte 02/10/2026. La selección de 2026 examinó
diez candidatos con menor nubosidad de tesela y los seis más recientes de la
tesela 17MRU, eliminando IDs duplicados; no es un examen exhaustivo de toda la
provincia ni demuestra que julio sea la última adquisición despejada disponible.
Las fuentes y resultados locales SCL están en `quality_search.json`.

La escena del 02/10/2026 descartó los cuatro recortes por SCL. También se
descartó para el montaje la del 29/09/2026: el porcentaje global de nubes parecía
aceptable, pero en Tena/Jatunyacu/Napo la cobertura útil local fue muy baja.
No se rellenan esos huecos con imágenes de otra fecha bajo una etiqueta única.

## Método y límites

Fuente: Copernicus Sentinel-2, distribuido como COG por Element 84 Earth Search
y AWS Open Data. Solo enlaces públicos HTTPS, sin credenciales, buckets
requester-pays, facturación ni nuevas tareas de Earth Engine.

1. Guardar el Item STAC completo y su fecha. B4/B3/B2/B8 tienen entrada de 10 m.
2. Convertir DN a reflectancia con **scale y offset del asset STAC**, aplicados
   una sola vez. No deducir el offset solo del año ni trasladar las reglas de
   `S2_SR_HARMONIZED` a estos COG. El TIFF no codifica esos factores como escalas
   de banda; el manifiesto conserva los factores realmente utilizados.
   **2026 usa Collection 1**: se detectó una contradicción en la colección antigua
   `sentinel-2-l2a` (flag de offset ya aplicado, asset aún declaraba −0,1).
   Se rechaza ese caso en código. `calibration_audit.json` contrasta cuatro
   ventanas alineadas de 12×12 píxeles del mismo producto: C1 conserva DN 1000
   unidades mayores y su corrección declarada reproduce la reflectancia de los
   COG antiguos ya corregidos. No se aplica un ajuste arbitrario a las imágenes.
3. SCL nativa de 20 m, remuestreada con vecino más cercano a la cuadrícula óptica.
   Se aceptan 4/5/6 (vegetación, no vegetado, agua), se requiere soporte conjunto
   en las cuatro bandas, reflectancias no negativas y denominador positivo.
   No se usa Cloud Score+ en esta nueva receta: **no es la QA del atlas anual**.
4. NDWI por adquisición: `(B3 − B8) / (B3 + B8)`, McFeeters (1996). No MNDWI
   `(B3 − B11) / (B3 + B11)`, ni NDMI; sus significados/bandas son diferentes.
5. Las dos escenas deben compartir exactamente CRS, transformación y tamaño.
   Se exige EPSG:32717 y cuadrícula de 10 m. Los dos años se muestran solamente
   sobre su máscara válida común, incluso en RGB. La trama representa NoData.
6. RGB fijo: 0–0,3, gamma 1,2; NDWI: −1 a +1, misma paleta en ambas fechas.
   No se aplica un umbral automático de agua ni se cuentan hectáreas.
7. El montaje conserva proporciones, usa escala de distancia ajustada al recorte
   y no deforma el río al cambiar de plano. Zoom no implica resolución adicional.

SCL puede equivocarse; no garantiza ausencia de sombras, bruma o nubes. El NDWI
es una señal espectral: valores altos no prueban que cada píxel sea agua. No mide
mercurio, contaminación, legalidad, volumen extraído ni causa de diferencias.

## Historia del video

Imagen real 2026 → verde/infrarrojo → fórmula → RGB/NDWI → comparación Jatunyacu
2019/2026 → Napo → Tena/Puerto Misahuallí → evidencia independiente y límites.
No se inventan polígonos mineros, fotos de río ni curvas espectrales medidas.

El informe **MAAP #249 (24/08/2026)**, de EcoCiencia/Amazon Conservation, se cita
como investigación independiente de Napo con datos de mayor resolución. Sus
conclusiones no se atribuyen al NDWI y no se usan como etiquetas de nuestros
píxeles. No se reproducen sus figuras, fotografías de dron ni datos Planet.
La autorización del usuario para los papers locales no autoriza automáticamente
fotografías de terceros obtenidas ahora de la web.

## Reproducir y revisar

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-river-video.txt
.\venv\Scripts\python.exe prepare_napo_ndwi.py --audit
.\venv\Scripts\python.exe prepare_napo_ndwi.py --quality-audit
.\venv\Scripts\python.exe prepare_napo_ndwi.py
.\venv\Scripts\python.exe reel_napo_ndwi.py artifacts/rios_napo_ndwi_2026
.\venv\Scripts\python.exe -m unittest discover -s tests -p test_napo_ndwi.py
```

La preparación realiza lecturas remotas de recortes, no descarga teselas completas.
Las consultas pueden tardar o fallar; no ofrecen disponibilidad garantizada.
`--storyboard-only` omite audio y MP4; `--silent` produce el montaje sin narración.
La versión narrada usa Microsoft Pablo ya instalada y `synthesize_reel.ps1`:
es una **voz sintética de referencia gratuita**, no imita al autor ni a un divulgador.
La duración se adapta a las tomas completas; no se corta ni acelera la voz.

Se entrega `guion_elevenlabs.txt` para una nueva toma del autor, sin gastar sus
créditos de ElevenLabs desde esta tarea. Los subtítulos se temporizan inicialmente
por cantidad de palabras: **no son alineación fonética certificada**. Revisar
sincronización, calidad visual de los tramos y cualquier afirmación antes de
la publicación. El video sigue rotulado como vista previa.

El exportador verifica hashes de fuentes y derivados, rechaza soporte común
inferior a 55% por ventana, decodifica todo el MP4 y comprueba formato, duración
y presencia del audio. Extrae cuadros del archivo codificado para revisión.
Estas pruebas no equivalen a validación de campo ni evaluación de exactitud.

## Fuentes y atribución

- McFeeters, S. K. (1996). *The use of the Normalized Difference Water Index
  (NDWI) in the delineation of open water features*. IJRS 17, 1425–1432.
  https://doi.org/10.1080/01431169608948714
- Bandas y fórmula Sentinel-2, implementación del proveedor:
  https://custom-scripts.sentinel-hub.com/custom-scripts/sentinel-2/ndwi/
- Catálogo público, calibración scale/offset y acceso gratuito:
  https://github.com/Element84/earth-search/blob/main/README.md
- Sentinel-2 y condiciones Copernicus:
  https://dataspace.copernicus.eu/explore-data/collections/sentinel-data/sentinel-2
- Contexto independiente, no resultado propio:
  https://www.maapprogram.org/mining-ecuador-napo/

Crédito de imágenes: **Contains modified Copernicus Sentinel data (2019, 2026)**;
procesamiento Henry Conteron; distribución Element 84 Earth Search/AWS Open Data.
No afirmar resolución submétrica, imágenes comerciales ni material generado con IA.
