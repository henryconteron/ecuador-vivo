# Ríos de Napo: elegir el índice antes de interpretar el cambio

Nueva vista previa educativa, independiente de los videos sísmicos. Conserva
el primer video NDWI de 2019/2026 en su carpeta original. La segunda versión
añade 2024, compara NDWI y MNDWI, muestra un cálculo con un píxel real y
explica resolución, incertidumbre y significado del cambio observado.

## Entregables locales

Carpeta ignorada por Git: `artifacts/rios_napo_indices_v2/`.

- `rios_napo_2019_2024_2026_vista_previa.mp4`: montaje vertical narrado.
- `comparacion_jatunyacu_indices_2019_2024_2026.jpg`: lámina ampliable con
  las tres fechas en RGB, NDWI y MNDWI; mismos encuadres y ajustes.
- `guion_elevenlabs.txt`: nueva narración para una toma del autor, sin gastar
  créditos ni reutilizar la voz de otro episodio.
- `manifest.json`: fechas, Items STAC, calibración, cuadrícula, QA, fórmulas,
  diagnóstico auxiliar y hashes de los recortes científicos y sus vistas.
- `selection_2024.json`: búsqueda y cobertura SCL local de los candidatos.
- `video_metadata.json`: formato, duración, hashes y verificación de audio/MP4.
- `subtitulos_borrador.srt`: revisar sincronización antes de publicación.

La voz Microsoft Pablo es una referencia gratuita de sistema, no la voz del
autor ni una imitación de un divulgador. No se ha publicado nada automáticamente.

## Fechas y selección

| Adquisición | Fuente fijada | Tipo |
| --- | --- | --- |
| 11/07/2019 | `sentinel-2-l2a / S2B_17MRU_20190711_0_L2A` | Una escena L2A |
| 08/08/2024 | `sentinel-2-c1-l2a / S2A_T17MRU_20240808T153803_L2A` | Una escena L2A |
| 29/07/2026 | `sentinel-2-c1-l2a / S2C_T17MRU_20260729T153626_L2A` | Una escena L2A |

Se examinaron los 18 candidatos MRU devueltos para junio–agosto de 2024:
la escena del 8 de agosto dio cobertura SCL útil entre 98,7% y 99,6% en
las cuatro ventanas originales. Las escenas de julio no ofrecían cobertura
suficiente en todas ellas. La elección no usa una puntuación de cambio del río
ni busca el resultado más dramático. El examen no es una búsqueda exhaustiva
de todo 2024. La ventana adicional de detalle del Jatunyacu se fijó después
para ampliar la curva observada, no para maximizar una diferencia espectral.

**No son las medianas anuales 2019/2024 del atlas**. No se mezcla una mediana
anual con una adquisición individual bajo una misma etiqueta temporal.
Las fechas están próximas en el calendario, pero no se igualaron caudal,
lluvia antecedente, nivel, estado estacional ni condiciones atmosféricas.
Las escenas pertenecen a sensores S2B/S2A/S2C; la comparación no incluye
una validación local independiente de sesgos entre sensores.

## Qué índice usamos y por qué

NDWI de McFeeters: `(B3 − B8) / (B3 + B8)`.
MNDWI de Xu: `(B3 − B11) / (B3 + B11)`.

Ambos contrastan verde con una banda infrarroja. No son mapas de contaminación,
ni de humedad de la vegetación, ni una medida directa del volumen de agua.
MNDWI sustituye NIR por SWIR1 para mejorar la separación respecto a otras
superficies en los casos estudiados por Xu (2006). Eso no demuestra que gane
en cualquier cauce, turbidez, sombra o sensor.

En la revisión visual del encuadre de 2024, MNDWI aporta un contraste más
marcado en parte del agua respecto a los bancos claros. **Se adopta como
lectura principal educativa para estos cauces amplios**, con NDWI y RGB como
comprobaciones complementarias. No se ha medido exactitud independiente y
no se presenta como un algoritmo universalmente superior.

El diagnóstico SCL conservado en el manifiesto es auxiliar y correlacionado
con la propia teledetección. No es verdad de campo. Por ejemplo, en el detalle
del Jatunyacu la diferencia de medianas SCL agua/no vegetado es aproximadamente:

| Fecha | NDWI | MNDWI |
| --- | ---: | ---: |
| 2019 | 0,479 | 0,574 |
| 2024 | 0,119 | 0,155 |
| 2026 | 0,243 | 0,242 |

Esto ayuda a explorar el contraste en esos grupos, **no evalúa exactitud**:
no mejora en todas las fechas y no basta para elegir un umbral de agua.
No se aplica automáticamente `índice > 0` ni se calculan hectáreas.
NDVI/NDMI responderían a otras preguntas sobre vegetación/humedad; no se
añaden como si todos los índices midieran el mismo fenómeno. AWEI puede ser
una alternativa para confusiones por sombras, pero no se ha ensayado aquí y
no se afirma que fuera mejor sin pruebas independientes.

## Comparación justa: 20 m, no detalle inventado

1. Lectura de recortes COG públicos HTTPS de Element 84 Earth Search;
   sin cuenta, pago, buckets requester-pays ni exportaciones nuevas en GEE.
2. DN a reflectancia: `DN × scale + offset`, según cada asset STAC, una vez.
   Se rechaza la colección antigua si declara offset ya aplicado y otro offset
   no nulo. En 2024/2026 se usa Collection 1. La auditoría de la primera
   versión comprobó directamente el desplazamiento DN del producto 2026.
3. B11 y SCL se mantienen en su cuadrícula nativa de **20 m**. B2/B3/B4/B8
   de 10 m se agregan mediante media de bloques 2×2 exactamente alineados.
   Se promedia reflectancia **antes** de formar los índices. Si una muestra
   es NoData, su bloque no se rellena. No se interpola SWIR a una supuesta
   resolución independiente de 10 m.
4. QA: SCL 4/5/6, reflectancias agregadas finitas y no negativas en las cinco
   bandas, denominadores positivos. Es una selección conservadora, no una
   garantía de agua ni de ausencia de nubes/bruma/sombras. Puede eliminar
   observaciones útiles y dejar huecos dentro del propio río.
5. Las tres fechas y ambos índices comparten EPSG:32717, transformación,
   dimensiones y **la misma máscara válida común**. RGB también usa ese
   soporte. No se transforma NoData en índice cero ni se rellena con otro año.
6. RGB 0–0,3 y gamma 1,2; índices −1 a +1, misma paleta en todas las vistas.
   No se ajusta el contraste por fecha para exagerar diferencias.
7. La ampliación conserva proporciones y una barra de 1 km de la cuadrícula
   UTM. Cortes entre fechas, sin deformaciones o interpolación del río.
   La explicación central de cada año tiene una toma de voz y capítulo propios:
   la etiqueta temporal no depende del ajuste aproximado de los subtítulos.

Cobertura válida común de toda la ventana: Tena 89,2%; Jatunyacu 95,7%; Napo
89,2%; Puerto Misahuallí 95,4%; detalle Jatunyacu 95,0%. **No son porcentajes
de agua validada ni de completitud del cauce**. Son soporte espacial para
comparar. Los huecos se muestran con trama.

El ejemplo del píxel 2024 usa reflectancias reales: verde ≈0,1053;
NIR ≈0,0642; SWIR ≈0,0457. NDWI ≈0,24, MNDWI ≈0,39. Un MNDWI numéricamente
mayor no implica más agua: cambió el contraste entre bandas. Su posición,
valores completos y SCL=6 están registrados; no se presume agua pura ni una
etiqueta de campo.

## Qué podemos concluir

Podemos señalar diferencias visibles para investigar y enseñar cómo elegir
y comprobar un índice. No demostrar migración del cauce, erosión medida,
extracción minera, contaminación, legalidad o causa de esas diferencias.
Hay que separar **agua presente ese día** de **geometría del cauce**.

Para medir cambios hacen falta más adquisiciones despejadas, control de
caudal/lluvia, revisión geométrica de orillas, tolerancias de corregistro,
etiquetas independientes y validación de incertidumbre. Un informe externo
sobre minería tampoco valida automáticamente estos píxeles.

## Reproducción

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-river-video.txt
.\venv\Scripts\python.exe prepare_napo_indices.py --audit-2024
.\venv\Scripts\python.exe prepare_napo_indices.py
.\venv\Scripts\python.exe reel_napo_indices.py --storyboard-only
.\venv\Scripts\python.exe reel_napo_indices.py
.\venv\Scripts\python.exe -m unittest discover -s tests -p test_napo_indices.py
```

En el entorno usado, la preparación y sus pruebas matemáticas se ejecutaron
con Python global (rasterio instalado); el montaje con el entorno `venv` que
contiene el codificador. Instalar los requisitos opcionales en `venv` unifica
ambos pasos. Los tests matemáticos se omiten explícitamente si falta rasterio.
El exportador comprueba hashes, áreas seguras, decodificación completa del
MP4, duración, formato y audio audible en cada escena. Estas comprobaciones
no sustituyen validación científica de campo ni alineación final de subtítulos.

## Bibliografía y créditos

- McFeeters, S. K. (1996). *The use of the Normalized Difference Water Index
  (NDWI) in the delineation of open water features*. IJRS 17, 1425–1432.
  https://doi.org/10.1080/01431169608948714
- Xu, H. (2006). *Modification of normalised difference water index (NDWI)
  to enhance open water features in remotely sensed imagery*. IJRS 27,
  3025–3033. https://doi.org/10.1080/01431160600589179
- Bandas y resoluciones Sentinel-2 (B3/B8: 10 m; B11: 20 m):
  https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED
  Se cita para las bandas, no se trasladan reglas de calibración GEE a los COG.
- Acceso/calibración del distribuidor:
  https://github.com/Element84/earth-search/blob/main/README.md
- Condiciones de datos Sentinel:
  https://dataspace.copernicus.eu/explore-data/collections/sentinel-data/sentinel-2

**Contains modified Copernicus Sentinel data (2019, 2024, 2026)**.
Procesamiento y divulgación: Henry Conteron. Distribución: Element 84 Earth
Search / AWS Open Data. Todas las imágenes cartográficas proceden de
observaciones reales; no se generaron fotografías ni cauces con IA.
