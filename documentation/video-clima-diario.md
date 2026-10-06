# Producción diaria de clima: revisión de octubre de 2026

El producto principal conserva las fechas diarias. La climatología mensual es
otra pieza y no sustituye la serie solicitada.

## Pruebas renderizadas

`production/monitor/render_daily_rain.py` descarga CHIRPS v2 diario desde el
servidor público del Climate Hazards Center. Genera un MP4 vertical 1080 × 1920,
30 fps, con 1,5 segundos por día. No interpola entre fechas. Se probaron
1–7 de enero y 1–7 de junio de 2024. Los archivos, capturas, entradas y recibos
SHA-256 se guardan en `_local/climate-studio/`, excluido de Git.

El render interpola bilinealmente valores y pesos válidos, aplica después
la paleta y recorta al territorio continental. La escala tiene tramos no
uniformes rotulados y permanece idéntica entre días. Los valores superiores
a 120 mm/día saturan el extremo señalado como 120+. NoData queda sin colorear.
Las ciudades son referencias geográficas, no pluviómetros.

CHIRPS v2 (~5,6 km) es una alternativa independiente para esta prueba; sus
valores no deben empalmarse silenciosamente con IMERG (~11 km). La resolución
espacial más fina no demuestra mayor exactitud diaria. La disponibilidad y
validación regional del producto deben revisarse antes de publicar conclusiones.

## Corrección de recetas existentes

Los acumulados y climatologías recuperan la proyección nativa con
`setDefaultProjection` antes de solicitar interpolación bilineal. Las recetas
de lluvia 2024, lluvia 2026, temperatura 2026 y anomalías históricas usan
remuestreo espacial antes de colorear. Se elige bilineal porque evita los
extremos negativos o excesivos que puede introducir interpolación bicúbica.

Las recetas siguen siendo exports base. La composición editorial final requiere
añadir fechas, unidades, fuente y leyenda; aumentar dimensiones por sí solo no
soluciona el problema. Las pruebas locales no validan ejecución en Earth Engine.

## Fuentes

- https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/2024/
- https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY
- https://developers.google.com/earth-engine/guides/resample
- https://developers.google.com/earth-engine/apidocs/ee-image-resample
- Límites: geoBoundaries gbOpen Ecuador ADM0, revisión 9469f09; URL exacta en cada recibo.

Estado actualizado al 6 de octubre de 2026: dos pruebas de siete días y el año
diario completo de 2024 renderizados. El anual contiene 366 fechas, dura 549 s
y se guarda en `_local/climate-studio/2024-01-01-366days/`. El montaje final de
temperatura sigue pendiente. No se publicaron estos videos.

Guía de reproducción local: [Cómo hacer los videos de lluvia](GUIA-VIDEOS-LLUVIA.md).
Las versiones utilizadas están en `production/monitor/requirements-daily-rain.txt`.
