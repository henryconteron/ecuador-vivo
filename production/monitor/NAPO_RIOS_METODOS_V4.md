# Un río, tres preguntas: video de Napo, versión 4

Nueva pieza **de video**, no otra página del atlas. Las versiones anteriores
quedan intactas. Entregables locales en `artifacts/rios_napo_metodos_v4/`:

- `rios_napo_metodos_v4_vista_previa.mp4`: montaje vertical 1080×1920,
  narrado con Microsoft Pablo instalado; gratuito, no voz del autor.
- `guion_elevenlabs.txt`: texto para grabar personalmente o usar con el servicio
  que el autor elija; esta ejecución no llama a ElevenLabs ni consume créditos.
- `comparacion_metodos_2019_2024_2026.jpg`: lámina ampliable con imágenes reales.
- `subtitulos_borrador.srt`: tiempos aproximados por longitud de texto,
  **requieren alineación manual antes de publicación**.
- `storyboard_metodos.jpg`, imágenes QA y fotogramas del MP4 codificado.
- `manifest.json`, `source_manifest.json`, STAC y GeoTIFF nativos: trazabilidad.
- `video_metadata.json`: duración, comprobaciones de audio y decodificación.

## La decisión editorial que cambia

Ya **no elegimos MNDWI como ganador** por contraste visual. El relato empieza
por una diferencia real en el Jatunyacu y una prueba sobre la misma imagen:
cambiar el índice cambia el contraste, no la cantidad de agua observada.
Luego separa tres preguntas:

1. Localizar agua: comparar NDWI/MNDWI/AWEInsh/AWEIsh con referencias locales.
2. Investigar lecho expuesto: agua, sedimento y vegetación clasificados, muchas
   fechas, niveles/caudal y lluvia. No-agua no equivale a lecho seco.
3. Investigar sedimentos dentro del agua: señal óptica y calibración con
   muestras contemporáneas. NDTI no devuelve NTU, mg/L ni mercurio.

2024 tiene capítulo propio más largo. Se conserva color natural en las tres
fechas, para no reducir la explicación a mapas de índices. Napo recibe otra
lectura RGB/NDVI; no se anuncia cobertura de todos los ríos de la provincia.

## Referencias narrativas revisadas

Se consultaron videos originales y sus transcripciones disponibles:

- Veritasium, [What Everyone Gets Wrong About Planes](https://www.youtube.com/watch?v=vjDYfvPW4mA).
  El inicio presenta una contradicción, recoge intuiciones y desarrolla el
  mecanismo que permite responderla; después enlaza una nueva pregunta.
  Sus [capítulos y fuentes oficiales](https://www.veritasium.com/videos/2025/1/17/what-everyone-gets-wrong-about-planes)
  permiten revisar la estructura. La fecha de esa página no es necesariamente
  la publicación original del video.
- El Robot de Platón, [¿Por qué No Hay Autos que Funcionen con Agua?](https://www.youtube.com/watch?v=-pciFAJRFLs).
  Parte de una pregunta cotidiana e historia difundida, la confronta con
  evidencia y distingue conceptos que suelen confundirse. La transcripción
  automática contiene errores: se usa para estructura, no como fuente científica.

Adaptación **propia**, no copia de guiones, muletillas, chistes o identidad:
gancho → intuición → prueba visible → mecanismo → preguntas distintas →
caso local → evidencia que falta → cierre que responde al gancho.
No se reutilizan clips, música ni voz de esos canales. No se afirma haber
analizado íntegramente su catálogo audiovisual.

## Qué se muestra realmente

Adquisiciones individuales L2A fijadas, no medianas anuales:

| Fecha | Colección / escena |
|---|---|
| 11 julio 2019 | sentinel-2-l2a / S2B_17MRU_20190711_0_L2A |
| 8 agosto 2024 | sentinel-2-c1-l2a / S2A_T17MRU_20240808T153803_L2A |
| 29 julio 2026 | sentinel-2-c1-l2a / S2C_T17MRU_20260729T153626_L2A |

La fecha 2026 es la más reciente **de esta selección**, no la última imagen
disponible ni una vista actual en vivo. 2019 no es una referencia prístina.
Son sensores S2B/S2A/S2C: no hemos validado sesgos locales entre sensores.

Ventanas editoriales de Tena, Jatunyacu, Napo y Puerto Misahuallí, más detalle
del Jatunyacu. No son cuencas, límites de ríos ni toda Napo. Archidona no está
incluida. Las ventanas y adquisiciones provienen del procesamiento previo;
no se seleccionaron por maximizar un cambio espectral.

Se reutilizan **GeoTIFF de seis bandas calibradas**, verificados por SHA-256,
orden de bandas, QA binaria y geometría. Se copian a esta carpeta: reproducir
el montaje no necesita que el atlas esté abierto. No se calculan índices desde
PNG, capturas, video, colores de mapas ni paquetes reproyectados a Web Mercator.
No se usan fotografías generadas por IA ni curvas ficticias de reflectancia.

Bandas B2/B3/B4/B8/B11/B12 en EPSG:32717, paso nativo de 20 m. B2/B3/B4/B8
proceden de promediar reflectancia de bloques alineados de 10 m **antes** de
cocientes; SWIR conserva 20 m. La escala/offset STAC se aplicó una vez en el
constructor original. Sus metadatos y linaje están en `source_manifest.json`.

QA original conservadora SCL 4/5/6 y reflectancias no negativas; se exige además
que todas las señales tengan denominadores válidos. Cada vista utiliza el
**soporte válido común de las tres fechas**. SCL es QA, nunca verdad de campo.
Puede omitir agua oscura/sombreada: este montaje no valida una solución al
problema de sombras. La trama es NoData, no una clase seca. Escalas visuales
fijas, proporciones intactas y barra de 1 km; zoom no crea detalle independiente.

| Señal | Fórmula aplicada a reflectancia |
|---|---|
| NDWI | (B3−B8)/(B3+B8) |
| MNDWI | (B3−B11)/(B3+B11) |
| AWEInsh | 4(B3−B11)−0,25B8−2,75B12 |
| AWEIsh | B2+2,5B3−1,5(B8+B11)−0,25B12 |
| NDVI | (B8−B4)/(B8+B4) |
| NDTI | (B4−B3)/(B4+B3) |

Los métodos originales Landsat se aplican aquí a bandas correspondientes de
Sentinel-2; no se afirma reproducción exacta de sus validaciones originales.
NDWI/MNDWI/NDVI/NDTI tienen escala visual −1/+1. AWEI utiliza también −1/+1
**solo para el color editorial**: no es normalizado y valores exteriores saturan
la paleta. Los valores originales quedan en las reflectancias reproducibles.
NDVI utiliza verde para mayor contraste de verdor; NDTI marrón para mayor
contraste rojo/verde. No se comparte el azul de agua para insinuar que vegetación
o sedimento equivalen a agua. Las paletas son editoriales, no calibraciones.

Todos los detectores usan umbral **cero, exploratorio y sin calibración local**.
Acuerdo azul 4/4, desacuerdo ámbar 1–3/4, oscuro 0/4: votos correlacionados,
no confianza, probabilidad ni exactitud. El mapa 2019→2024 marca:

- Coral: 4/4→0/4, pérdida candidata de señal de agua.
- Verde: 0/4→4/4, aparición candidata.
- Azul: 4/4→4/4, señal estable; oscuro: 0/4→0/4.
- Ámbar: cualquier otro caso común; trama: sin observación.

Esto **no** clasifica sedimentos expuestos, cauce seco o minería, ni cuantifica
migración o erosión. NDTI se muestra solo en candidatos 4/4; gris sólido fuera
de ellos. Cambian las máscaras de selección por fecha: no se calcula diferencia
cuantitativa de turbidez sobre píxeles distintos. No hemos aplicado corrección
atmosférica específica de agua ni calibración de sedimento en Napo.

## Afirmaciones y respaldo

| Mensaje | Fuente y límite |
|---|---|
| NDWI verde/NIR para agua | McFeeters (1996); no caudal ni profundidad |
| MNDWI cambia NIR por SWIR1 | Xu (2006); no ganador local automático |
| AWEI aborda confusiones con sombras/superficies oscuras | Feyisa et al. (2014); Landsat, no nuestra evaluación en Napo |
| Clasificar agua/sedimento/vegetación para investigar lecho seco | Cavallo et al. (2025); dos tramos italianos, no resultados en Ecuador |
| Calibrar señales ópticas con muestreo de sedimentos | Lobo et al. (2018); Amazonía brasileña, no trasladar coeficientes a Napo |
| Minería aluvial puede alterar carga de sedimentos | Dethier et al. (2023); estudio tropical amplio, no atribución de nuestros píxeles |

El video no muestra un modelo multibanda entrenado ni inventa exactitud. Esa
evaluación requiere etiquetas independientes, separar entrenamiento/prueba,
comparar precisión/recuperación/IoU del agua, y reportar también agua omitida
por QA. Muchas fechas, hidrología, corregistro e incertidumbre hacen falta para
inferir periodos secos. No se interpola una película entre las tres observaciones.

## Reproducir

Preparación de esta versión a partir del hand-off local de datos nativos:

```powershell
python prepare_napo_methods.py --source-root 'C:/Users/JHONY CONTERON/OneDrive/Documentos/GitHub/fallas-ecuador'
.\venv\Scripts\python.exe reel_napo_methods.py --storyboard-only
.\venv\Scripts\python.exe reel_napo_methods.py
python -m unittest discover -s tests -p test_napo_methods.py
```

`--source-root` es parámetro explícito, no dependencia de servidor web. En otra
máquina se necesitan esos recortes nativos y su manifiesto de procedencia;
están ignorados en Git por tamaño. Este preparador no descarga fuentes faltantes
ni activa GEE. El constructor original gratuito del hand-off está documentado
en el atlas. La preparación usa Python con rasterio; el montaje usa `venv`
con dependencias de video. `requirements-river-video.txt` permite unificarlos.

**Antes de publicar:** revisar montaje, ajustar subtítulos a voz final, contrastar
interpretaciones con un especialista y conservar fuentes/limitaciones en la
descripción. El montaje no se sube automáticamente ni modifica episodios previos.

## Bibliografía y crédito

- McFeeters (1996): https://doi.org/10.1080/01431169608948714
- Xu (2006): https://doi.org/10.1080/01431160600589179
- Feyisa et al. (2014): https://doi.org/10.1016/j.rse.2013.08.029
  [Resumen de los autores](https://researchprofiles.ku.dk/en/publications/automated-water-extraction-index-a-new-technique-for-surface-wate/).
- Cavallo et al. (2025), *Estimating dry bed periods in non-perennial rivers
  using Sentinel-2 satellite data*: https://doi.org/10.1016/j.jhydrol.2025.133416
  [Repositorio institucional](https://iris.polito.it/retrieve/82a0c475-8768-47c5-98b5-daffdaed7f23/Cavallo_et_al_2025_compressed.pdf).
- Lobo et al. (2018), *Monitoring Water Siltation Caused by Small-Scale Gold Mining
  in Amazonian Rivers Using Multi-Satellite Images*: https://www.intechopen.com/chapters/62698
- NDTI rojo/verde, tabla de índices (no calibración Napo): https://www.mdpi.com/2073-4441/17/15/2195
- Dethier et al. (2023), *A global rise in alluvial mining increases sediment
  load in tropical rivers*: https://doi.org/10.1038/s41586-023-06309-9
  [Resumen del artículo](https://pubmed.ncbi.nlm.nih.gov/37612396/).
- Sentinel-2, bandas/resolución: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED
- Earth Search, acceso/calibración COG: https://github.com/Element84/earth-search

Contains modified Copernicus Sentinel data (2019, 2024, 2026).
Procesamiento y divulgación: Henry Conteron. Distribución: Element 84 Earth
Search / AWS Open Data. Fuentes narrativas no son fuentes de resultados científicos.
