# Slab2 en Ecuador Vivo

## Qué se representa

Recorte de la superficie modelada de la placa subducida, **Slab2 South America, 23 de febrero de 2018**, de Hayes (2018). No es un volumen de las dos placas, una tomografía, una medición directa ni una animación física. No modela la placa Sudamericana, espesores, temperatura, deformación ni velocidades. La interfaz del visor sigue siendo experimental.

- Datos y licencia CC0: [USGS, DOI 10.5066/F7PV6JNV](https://www.usgs.gov/data/slab2-a-comprehensive-subduction-zone-geometry-model).
- Artículo: Hayes et al. (2018), *Slab2, a comprehensive subduction zone geometry model*, Science, [DOI 10.1126/science.aat4723](https://doi.org/10.1126/science.aat4723).
- Distribución oficial usada: [USGS ShakeMap geodata](https://apps.usgs.gov/shakemap_geodata/slabs/), archivos `sam_slab2_dep_02.23.18.grd` y `sam_slab2_unc_02.23.18.grd`.
- [Documentación de formatos USGS](https://ghsc.code-pages.usgs.gov/esi/usgs-slab-models/manual/sg_output_formats.html): profundidad e incertidumbre en kilómetros. No se atribuye aquí un nivel de confianza del 95 % al campo `unc`.

## Recorte reproducible

Consulta del 4 de octubre de 2026. Los dos originales HDF5 se conservan localmente; sus URL y SHA-256 están en [manifest.json](../data/slab2/manifest.json). El generador rechaza originales con otras huellas. Para reconstruir, descargar los dos archivos de la distribución citada a una carpeta de trabajo y ejecutar:

```text
python -m pip install numpy h5py
python scripts/build_slab2_subset.py --source CARPETA_DE_ORIGINALES --output data/slab2
```

No ejecutar este generador para una versión distinta sin revisar antes las fuentes y cambiar sus identificadores. La fecha en el manifiesto identifica esta adquisición, no la ejecución de una reconstrucción posterior.

Ventana geográfica −83 a −74,5° de longitud y −5,5 a 2,5° de latitud. Es Ecuador y entorno regional, no una máscara administrativa. Se conserva el paso nativo de 0,05°: 161 filas × 171 columnas, 21.849 nodos con profundidad. No confundir separación de nodos con resolución efectiva o exactitud geológica.

Transformaciones: longitud original 0–360 a −180–180; profundidad negativa de la grilla a kilómetros positivos hacia abajo; redondeo de profundidad e incertidumbre a 0,001 km para serialización (no representa exactitud métrica). NaN se convierte en `null`, nunca en cero. No se interpola, extrapola ni ajusta con el catálogo de sismos. Las coordenadas se usan como longitud/latitud de la fuente; la pantalla conserva la aproximación cartesiana local descrita en [el documento del visor](prototipos-3d-y-navegacion.md), no una reproyección GIS de precisión.

## Lectura visual y límites

- Malla ligera: se dibuja una de cada cuatro filas/columnas, uniendo únicamente nodos nativos contiguos válidos. No se trazan segmentos sobre huecos. La descarga conserva todos los nodos del recorte.
- Naranja indica la superficie; el modo alternativo colorea su incertidumbre publicada: verde <10 km, amarillo 10–<20 km, coral ≥20 km y gris si falta. Son intervalos de visualización, no clases oficiales de calidad.
- Los controles de latitud y longitud inspeccionan un nodo nativo. El cuadrado blanco lo ubica; fuera de cobertura se informa que no hay modelo.
- Los puntos sísmicos se distinguen por profundidad. Sus incertidumbres no son el campo `unc` de Slab2. No inferir mecanismo focal ni causalidad por proximidad, ni tratar el catálogo superpuesto como validación independiente de Slab2: el modelado de placas puede usar sismicidad como restricción.
- El plano tenue es solo una referencia de profundidad cero, no costa ni frontera de placas. No representa la topografía ni el continente. Los puntos se superponen sin oclusión física.
- Si falla la verificación del archivo, la superficie se oculta: no se sustituye por una curva inventada. El catálogo sísmico se verifica por separado.
- Siguen siendo los 2.661 registros históricos conservados, 1900–2025; no se agregaron sismos de 2026 ni un servicio en vivo.

## Comprobaciones

`node tests/test-slab2.mjs`: huella y tamaño, extensión/paso, conteo, signos, valores ausentes, segmentos que no cruzan huecos y rechazo de archivos alterados. Comparación local de todo el recorte con los originales HDF5 antes de publicar. La integridad verifica conservación, no la exactitud física del modelo.
