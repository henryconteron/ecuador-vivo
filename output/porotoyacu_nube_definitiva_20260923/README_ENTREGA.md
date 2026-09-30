# Porotoyacu — paquete recalculado con la nube definitiva

Este paquete se calculó **solo** a partir de `NUBE_COMPLETA_FINAL_TERRENO_MICRORELIEVE_DEPURADO_UTM18S.laz`, ubicado en `C:\Users\JHONY CONTERON\Downloads\Perimetral 1-20260831T211605Z-1-001\ENTREGA_FINAL_MICRORELIEVE_PERFILES_20260923`. No se editó ni duplicó el LAZ. Su SHA-256 es `69106c3d56a8819a4603118a7042b082b6331894de0489e7cda7f2e31d5439b2`. El manifiesto JSON conserva esa identidad, las clases, el CRS y la procedencia geométrica.

## Resultado verificable

- 13,619,241 puntos; 2,810,862 Ground (clase 2; 20.64%). EPSG:32718.
- En celdas ocupadas de 2 × 2 m: 94,274 con algún punto y 44,429 con Ground (47.13%); 49,845 (52.87%) sin observación directa de terreno. Densidades medias sobre la huella ocupada: 36.12 y 7.45 puntos/m² para todos y Ground.
- 32 perfiles de 180 m. La clasificación de soporte de la faja ±5 m y bins longitudinales de 1 m (mínimo 3 Ground por bin) da 7 A, 5 B y 20 C. A/B: P1, P2, P3, P5, P6, P7, P9, P10, P11, P18, P23 y P24. No se rellenaron bins vacíos para este control.
- P32 tiene solo 27.86% de bins Ground válidos entre 30–170 m y un hueco máximo de 50 m: sus formas visibles en el DSM no autorizan medir altura de escarpe. P21 y P4 también son C. La tabla CSV permite revisar todos los perfiles y tres semianchos de faja (2.5, 5 y 7.5 m).

## Archivos para la composición en QGIS y el artículo

- `figuras/Figura_2a_MDT_traza_32_perfiles_NUBE_FINAL.pdf` y `.png`: mapa de contexto con 32 líneas y la posición local mapeada. **Versión previa:** su fondo usa el raster de 60 m con el hueco norte; para la composición final en QGIS cargar `rasters/MDT_contexto_continuo_huella_1m.tif` y reexportar el mapa. El fondo interpolado es **solo para visualización**.
- `figuras/Figura_2b_perfiles_1x_NUBE_FINAL.pdf` y `.png`: lámina de cinco perfiles (P32, P21, P18, P11, P4), ejes a escala física aproximadamente 1:1, con puntos Ground/no Ground, DSM de todas las clases excepto ruido 7, DTM medido e interpolación contextual diferenciados. El PDF es vectorial; el PNG de alta resolución puede usarse como imagen en el diseño de QGIS.
- `figuras/Figura_S1_32_perfiles_soporte_ground.pdf` y `.png`: control de los 32 perfiles.
- `densidad_2m/figura_validacion_nube_4_paneles.pdf` y `.png`: densidad de todos los puntos, Ground, retención y soporte directo, para la Figura 5.
- `datos/trazas_32_perfiles_SOLO_GEOMETRIA.gpkg`: capa de las 32 líneas y otra capa de la referencia local a 60 m, con clases A/B/C. Se comprobaron sus extremos contra la geometría usada en el remuestreo. **No contiene** las columnas antiguas de pie, corona ni altura de escarpe.
- `rasters/MDT_ground_observado_1m.tif`: mediana Ground por celda; NoData donde no hay Ground. Esta es la capa apropiada para inspeccionar soporte directo en QGIS.
- `rasters/MDT_contexto_interpolado_1m.tif`: **reemplazado** como fondo de Figura 2; dejó un hueco visible en el norte por el límite de relleno de 60 m y valores espurios en algunos bordes. Se conserva solo para trazabilidad.
- `rasters/MDT_contexto_continuo_huella_1m.tif`: nuevo fondo para la composición de Figura 2 en QGIS. Interpola las medianas Ground y cubre la huella de puntos de todas las clases con un margen de 10 m. Conserva exactamente las celdas Ground originales y no usa las elevaciones del MDS para estimar terreno. Es contexto visual, no medición en zonas sin Ground.
- `rasters/DISTANCIA_al_Ground_observado_1m.tif` y `rasters/QA_MDT_contexto_continuo_huella.json`: distancia al soporte Ground y control de la corrección. Hay 28,568 celdas visualizadas a más de 60 m de Ground y 8,025 a más de 100 m; 19,619 celdas fuera de la envolvente convexa Ground usan el vecino Ground más próximo, es decir, **extrapolación visual**. No usar esos sectores para alturas o interpretación fina. `scripts/corregir_mdt_contexto_huella.py` reproduce ambos rasters.
- `rasters/MDS_todas_clases_sin_ruido_1m.tif`: máximo de todas las clases excepto clase 7, incluido Road Surface (clase 11). No es un MDT.
- `datos/control_soporte_32_perfiles.csv`, `perfiles_ground_bins_1m.csv`, `puntos_5_perfiles_representativos.csv` y `perfiles_raster_contexto_0p5m.csv`: respaldo cuantitativo.
- `manuscrito/Manuscript_Conteron_etal_2026_NUBE_FINAL_v5.docx`: copia actualizada del manuscrito anterior, con cifras y Figuras 2/5 recalculadas. `manuscrito/Matriz_revision_reenvio_NUBE_FINAL_v5.docx` actualiza la evidencia para revisores/coautores. Los archivos fuente originales no se sobrescribieron.

## Método y límites

Las coordenadas de las 32 líneas proceden del CSV histórico, pero **ninguna cota histórica** se reutilizó. Las elevaciones de perfiles, mapas y controles se calcularon de nuevo del LAZ identificado por SHA-256. El mapa de contexto previo aplicaba un límite de 60 m; el raster corregido interpola dentro de una huella derivada de la presencia de puntos, conserva las medianas Ground observadas y entrega por separado la distancia a Ground. La altura de celdas de 1 m o 2 m no equivale a exactitud vertical. No hay GCP/checkpoints independientes que permitan estimar exactitud absoluta.

No se afirma continuidad de una falla de 700 m, desplazamiento vertical, altura de escarpe, cinemática, actividad reciente ni parámetro de amenaza. Las clases A/B solo sostienen una descripción local y no sustituyen puntos de control independientes. La posición exacta de la línea SRT no estaba en los archivos geométricos verificados de esta entrega; por ello no se dibujó una ubicación especulativa en el mapa. El análisis SRT anterior se conserva en el manuscrito, pero no se recalculó a partir del LAZ.

Para reproducir: el script principal es `scripts/porotoyacu_final_pipeline.py`; la densidad 2 m se calculó con `scripts/analisis_nube_porotoyacu.py`; `scripts/preparar_trazas_qgis.py` crea la capa limpia. Los scripts de actualización del DOCX y de la matriz están en la misma carpeta. El entorno empleado tuvo Python, laspy/lazrs, NumPy, pandas, SciPy, rasterio, matplotlib y python-docx. `MANIFIESTO_NUBE_FINAL.json` y `densidad_2m/resumen_global.json` guardan los parámetros y recuentos auditables.
