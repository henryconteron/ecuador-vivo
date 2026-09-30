# Cobertura del suelo: Tena–Archidona, 2000 y 2024

Estado al 30 de septiembre de 2026: **recorte real exportado y validado**. Earth Engine
aceptó el proyecto individual no comercial en el nivel Comunidad. Se descargaron el
GeoTIFF y el recibo de la misma ejecución y se procesaron conservando la cuadrícula
nativa. La comparación tiene 2.697.912 píxeles observados en ambos años; los dos PNG
y el manifiesto `ready` están preparados para publicar. No se publican mapas sintéticos.
La validación técnica no implica una evaluación independiente de exactitud en campo.

## Fuente fijada y comprobaciones

Usamos exclusivamente el [Publisher Catalog de MapBiomas Ecuador LULC V1.0](https://developers.google.com/earth-engine/datasets/catalog/projects_mapbiomas-public_assets_ecuador_lulc_v1):

- Asset: `projects/mapbiomas-public/assets/ecuador/lulc/v1`.
- `ee.ImageCollection`, una imagen por año, banda `classification`, propiedad `year`.
- 30 m nominales; serie publicada 1985–2024; licencia **CC-BY-4.0** en esa ficha.
- Clases y colores transcritos de la tabla de la misma ficha; nombres españoles traducidos.
- Dos años de **la misma versión**, 2000 y 2024. No declarar que V1 es la colección 3 o 4.

La consulta acotada con Exa solicitó 10 resultados en dos búsquedas y se contrastó
con páginas del productor y documentación de Earth Engine. Se descartaron duplicados.
La comprobación HTTP directa encontró que los enlaces históricos `/herramientas/`,
`/codigos-de-la-leyenda/` y el PDF de la colección 3 ya no estaban disponibles.
La página actual de [leyendas](https://ecuador.mapbiomas.org/descargas/informacion-de-la-leyenda/)
ofrece colección 4, mientras la de [mapas](https://ecuador.mapbiomas.org/descargas/mapas-de-la-coleccion/)
todavía anuncia colección 3. No mezclamos esos recursos para construir esta comparación.
Una copia indexada por un buscador no prueba que un enlace siga funcionando.

## Cómo reproducir la exportación

El proyecto del autor ya está registrado para uso individual no comercial en el
nivel **Comunidad**, sin activar facturación. Para reproducir el proceso con otra
cuenta, usa un proyecto propio y declara tu situación real. Comunidad no requiere
cuenta de facturación; otros servicios de Cloud pueden generar cargos si se les
habilita facturación. Véanse los [niveles no comerciales oficiales](https://developers.google.com/earth-engine/guides/noncommercial_tiers).

1. Abre [Earth Engine Code Editor](https://code.earthengine.google.com/).
   Inicia sesión y, si lo solicita, configura un proyecto habilitado siguiendo sus
   instrucciones. Revisa personalmente elegibilidad, términos y posibles cargos;
   no se garantiza que una cuenta nueva tenga acceso inmediato.
2. Abre `scripts/export_napo_landcover_gee.js` en tu editor de texto. Copia **todo**
   su contenido, pégalo en un script nuevo del Code Editor y pulsa **Run**.
   El script consulta el servidor de forma asíncrona: espera a que termine antes
   de abrir Tasks. Solo crea tareas tras validar una imagen por año y ambas grillas.
   Si falla una consulta, imprime el error y no crea exportaciones.
3. Si no hay errores, entra en **Tasks** y ejecuta las dos tareas:
   `napo_mapbiomas_v1_2000_2024` y `napo_mapbiomas_v1_receipt`.
   No cambies escala, proyección, bandas, años ni recorte en las ventanas de exportación.
4. Al terminar, en tu Google Drive abre la carpeta **EcuadorVivo** y descarga
   el `.tif` y el `.geojson`. Colócalos en `data/raw/landcover/` del repositorio;
   esa carpeta está ignorada por Git. No subas el TIFF nacional ni credenciales.
5. Avísame: **«Ya descargué el TIFF y el recibo de MapBiomas»**. Puedo ejecutar
   el procesamiento, revisar las imágenes y dejarte solo los archivos pequeños para publicar.

Si el script dice que no encuentra un año o que las proyecciones difieren, **detente
y copia el error**. No reemplaces el asset por otra colección sin revisar su leyenda.

## Si prefieres procesarlo tú

Desde una terminal abierta en la raíz del repositorio:

Este procesamiento opcional requiere **Python 3.12 o posterior**.

```powershell
python -m pip install -r requirements-landcover.txt
python scripts/build_napo_landcover.py --input "data/raw/landcover/napo_mapbiomas_v1_2000_2024.tif" --receipt "data/raw/landcover/napo_mapbiomas_v1_receipt.geojson"
pnpm run check
python -m unittest discover -s tests -p "test_build_napo_landcover.py"
```

Con Node/npm instalado puedes usar `npm run check` en lugar de `pnpm run check`.
El procesador valida el recibo, códigos, CRS, alineación, NoData y tamaño, luego
genera dos PNG georreferenciados en Mercator y `data/landcover/napo-manifest.json`.
Revisa visualmente ambos mapas y los porcentajes antes del commit. Un recibo declara
procedencia y los SHA-256 detectan cambios; **no son una certificación externa de origen
ni validación independiente de exactitud en Napo**.
Si el TIFF conserva nombres de banda, se contrasta también su orden. Si no los
conserva, el orden procede del recibo y así queda indicado en el manifiesto;
mantén ambos archivos de la misma ejecución y no reorganices bandas manualmente.

## Método y límites científicos

- El recorte es un rectángulo editorial: `[-78.04, -1.12, -77.55, -0.72]`
  en orden oeste, sur, este, norte. Incluye la zona de ambas localidades, **no** sus
  límites cantonales completos. No calcular «deforestación del cantón» con ese recorte.
- Estadísticas de clasificación sobre la **cuadrícula nativa**, sin remuestreo.
  Solo píxeles observados en ambos años; códigos 0 y 27 y máscaras NoData se excluyen.
  La cobertura común se muestra para evitar ocultar observaciones faltantes.
- Porcentajes de píxeles, no hectáreas: una cuadrícula angular no tiene área uniforme.
  No sumar formaciones padre e hijas ni agrupar toda clase agrícola como deforestación.
- Los PNG se reproyectan solo para la visualización Leaflet con **vecino más cercano**;
  nunca se calculan porcentajes desde ellos ni se interpolan colores de clases.
- El tamaño nominal del píxel no equivale a precisión local. Bordes mixtos, nubes,
  mosaicos y errores del clasificador pueden producir cambios de clase aparentes.
- Una transición no identifica su causa ni equivale automáticamente a pérdida de bosque,
  minería ilegal, daño o riesgo. Contrastar imágenes originales, metodología y evidencia local.

La exportación conserva la transformación nativa, porque usar únicamente `scale`
puede desplazar la cuadrícula. Véanse [exportación de imágenes](https://developers.google.com/earth-engine/guides/exporting_images)
y [remuestreo](https://developers.google.com/earth-engine/guides/resample) de Earth Engine.

## Atribución para el atlas

MapBiomas Ecuador — Publisher Catalog LULC V1.0, mapas anuales de cobertura y uso
del suelo de 2000 y 2024, 30 m nominales. Consultado el 30 de septiembre de 2026.
[Fuente, leyenda y licencia CC-BY-4.0](https://developers.google.com/earth-engine/datasets/catalog/projects_mapbiomas-public_assets_ecuador_lulc_v1).
Modificaciones de Ecuador Vivo: recorte editorial Tena–Archidona, comparación de
clases sobre observaciones comunes y reproyección de las vistas web.

Pruebas: los rásteres sintéticos se crean únicamente en directorios temporales de
tests; no son mapas de Napo ni se copian a producción. El CI comprueba también los
SHA-256 de los PNG cuando haya un manifiesto real con estado `ready`.
