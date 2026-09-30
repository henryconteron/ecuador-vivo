# Napo: dos años, tres maneras de mirar un río

Laboratorio educativo de Ecuador Vivo. Compara **2019 y 2024** mediante RGB,
NDVI y MNDWI de Sentinel-2. No es un detector de minería, una delimitación de
áreas intervenidas, un estudio de contaminación ni una validación de campo.
Los datos y parámetros reproducibles están en `data/spectral/napo-config.json`;
el recibo, las fechas de las escenas, la cobertura útil y los SHA-256 se conservan
en `data/spectral/napo-manifest.json`.

## Visor geográfico y derivados adicionales

En **Agua** o **Vida**, activa **Imágenes e índices · Napo**. El visor permite
zoom, desplazamiento y comparación 2019/2024 con un corte fijado a la pantalla.
Ambos años usan los mismos límites EPSG:3857 y se mueven juntos. Puedes elegir
un solo año, ajustar opacidad y regresar a Tena–Archidona o al tramo del Jatunyacu.
**Ampliar visor** oculta temporalmente el panel y da todo el espacio al mapa;
**Volver al panel** o Escape restaura la interfaz sin perder la selección.
El botón **Explorar con zoom** del laboratorio abre esa misma señal en el mapa.
La leyenda, atribución y contexto de resolución corresponden a la capa activa;
la trama gris indica ausencia de datos comparables. Fuera del borde exportado
solo se ve el mapa base. Ampliar no aporta más resolución que el muestreo de 30 m.

Se añaden cinco imágenes derivadas del **mismo GeoTIFF multibanda ya exportado**,
sin una nueva consulta ni consumo adicional de cuota de Earth Engine:

- **NDMI 2019/2024**: `(B8 − B11) / (B8 + B11)`. Se calcula sobre las medianas
  de reflectancia NIR y SWIR1 en la cuadrícula nativa. Es una señal relacionada
  con humedad de vegetación, no una medición de lluvia, agua del suelo ni estrés
  hídrico directo. [Fundamento NIR/SWIR — USGS](https://www.usgs.gov/landsat-missions/normalized-difference-moisture-index).
  La documentación enlazada emplea Landsat; aquí se usan las bandas equivalentes
  de Sentinel-2 (B8/B11), no los números de banda de Landsat.
- **Diferencia de NDVI**: `NDVI_2024 − NDVI_2019`, sobre soporte común nativo.
  Rango matemático y paleta fija −2 a +2, centro 0. Valores menores/mayores no
  equivalen a pérdida/ganancia validada de bosque, ni explican causas. No se
  calculan hectáreas de deforestación o minería ni se aplican umbrales automáticos.
- **Observaciones útiles 2019/2024**: banda `clear_count` original, máscara
  conjunta de cinco bandas y filtros de calidad declarados. Escala visual fija
  0–80 en ambos años; el constructor rechaza datos que excedan esa escala,
  en lugar de saturarlos silenciosamente. No representa probabilidad de certeza.
  Solo se muestra soporte común, no todos los píxeles descartados por baja calidad.

Los derivados se calculan **antes** de la reproyección, que utiliza vecino más
cercano. NDMI exige denominador positivo en ambos años; si no lo tiene, ambos
lados quedan sin datos, sin inventar un cero. En esta exportación el soporte
NDMI conserva los 2.499.892 píxeles comunes. Las paletas tienen 129 niveles:
son vistas cuantizadas, no archivos numéricos para medir índices desde sus colores.

Configuración: `data/spectral/napo-explorer-config.json`. Procedencia, cuadrícula,
conteos y SHA-256: `data/spectral/napo-explorer-manifest.json`, enlazado a los
SHA-256 del GeoTIFF y recibo del manifiesto principal. La carga es bajo demanda
por señal (no se descargan las once vistas al abrir el atlas). Los cinco derivados
añaden 4.967.504 bytes; toda la colección de once vistas suma 10.425.730 bytes.
Los errores de imagen retiran la vista completa; una petición antigua no puede
reaparecer después de apagar la capa o cambiar de señal.

Ejemplo de enlace reproducible de **selección y encuadre** (no de un zoom manual):
`?system=water&focus=napo&view=spectral&signal=ndmi&year=2024&compare=1&split=50&area=jatunyacu`.
El selector permite `rgb`, `ndvi`, `mndwi`, `ndmi`, `quality` o `change`.
La diferencia siempre es una sola vista 2019/2024, no dos años independientes.

## Pregunta y alcance

¿Qué cambia en la señal de vegetación y agua de un paisaje fluvial? Primero se
observan las imágenes; después se consideran explicaciones alternativas y se
contrastan fuentes independientes. Un cambio espectral no determina su causa.

La ventana editorial Tena–Archidona es longitud/latitud
`[-78.04, -1.12, -77.55, -0.72]`. El acercamiento al tramo inferior del Jatunyacu
es `[-77.98, -1.10, -77.77, -1.00]`: un recorte de navegación, **no** un polígono
minero ni el límite de una cuenca o cantón. No representa todo el Jatunyacu.
El recorte no cambia los datos ni recalcula estadísticas: estas describen la
ventana completa.

2019 es un registro anterior, **no una referencia prístina**. El informe
[MAAP #230, EcoCiencia/Amazon Conservation, 18 de julio de 2025](https://www.maapprogram.org/ecuador-mining-napo/)
documenta intervención minera en el sector del Jatunyacu desde 2017 mediante
su propio análisis regional, imágenes de mayor resolución y observaciones con
dron. Es evidencia externa a este laboratorio; su área y metodología son
distintas. Aquí no reproducimos sus figuras ni extrapolamos sus resultados a
nuestros píxeles.

## Qué significan las vistas

| Vista | Bandas / fórmula | Lectura prudente |
|---|---|---|
| RGB | B4, B3, B2 | Apariencia óptica con el mismo ajuste visual para ambos años. |
| NDVI | `(B8 − B4) / (B8 + B4)` | Contraste infrarrojo cercano/rojo asociado al verdor de la vegetación; no mide especies, biomasa ni hectáreas deforestadas. |
| MNDWI | `(B3 − B11) / (B3 + B11)` | Contraste verde/SWIR1 que puede destacar agua superficial; no es una máscara confirmada de agua ni mide sedimentos o contaminantes. |

La interpretación de NDVI sigue la explicación de
[USGS](https://www.usgs.gov/landsat-missions/landsat-normalized-difference-vegetation-index),
pero las bandas usadas son **Sentinel-2**, no los números de banda de Landsat.
MNDWI se atribuye a Xu (2006),
[doi:10.1080/01431160600589179](https://doi.org/10.1080/01431160600589179).
El contraste verde/SWIR también está documentado explícitamente por
[USGS EROS](https://www.usgs.gov/centers/eros/science/usgs-eros-archive-vegetation-monitoring-eviirs-global-ndwi).
Existen otros índices llamados NDWI con otras bandas: no son intercambiables.

Las dos escalas son adimensionales, fijas de −1 a +1, sin umbral automático de
clasificación. Una tonalidad representa un intervalo del índice, no un diagnóstico.
Solo el renderizado se discretiza en **129 niveles fijos**, iguales para los dos
años: PNG con paleta indexada y una entrada transparente para NoData. Las
fórmulas y estadísticas se verifican sobre los valores float32 del GeoTIFF,
no sobre esa discretización visual.

## Estado de esta exportación

Procesado y validado el 30 de septiembre de 2026: 293 escenas enlazadas de 2019
y 296 de 2024 (incluyen teselas, no fechas únicas ni observaciones por píxel).
De 2.684.668 centros de píxel nativos dentro de la ventana, 2.499.892 tienen
soporte común (**93,1 %**). La cobertura útil individual es 94,1 % en 2019 y
95,3 % en 2024; los conteos útiles mínimo/mediana/máximo son 3/12/60 y 3/17/74,
respectivamente. El control web muestra el recorte común, no las coberturas
individuales por separado. Estos porcentajes no son áreas de minería ni
exactitud temática. En la cuadrícula web hay 2.513.439 píxeles emparejados:
no restar ni mezclar ese conteo con el nativo UTM.

Las seis vistas suman aproximadamente **5,46 MB**, pero se cargan por pares
solo al abrir cada modo; el RGB inicial suma unos **672 kB**. El GeoTIFF de
trabajo de unos 220 MB queda fuera de Git. No se han activado servicios de pago.
La tarea raster terminó en 18 minutos y registró unos 5.996 EECU-segundos de
cómputo; esto es consumo de cuota, no un precio ni un tiempo garantizado.

La pestaña del Code Editor se cerró entre la exportación raster y la del recibo.
El recibo se regeneró desde la **instantánea del script fuente de esa tarea**,
con los mismos intervalos y parámetros; no se duplicó el cálculo raster.
Esta recuperación se declara para no atribuirles una única ejecución del
editor. El recibo y los SHA-256 documentan la consulta y detectan modificaciones,
pero no son firmas del proveedor ni garantizan inmutabilidad futura del catálogo.

## Método reproducible

1. Se seleccionan las escenas que intersectan la ventana en los intervalos
   `[2019-01-01, 2020-01-01)` y `[2024-01-01, 2025-01-01)`. El extremo final es
   exclusivo. Fuente: `COPERNICUS/S2_SR_HARMONIZED`, reflectancia superficial
   L2A armonizada. La reflectancia es DN × 0,0001.
2. Una unión interna por `system:index` enlaza las escenas con
   `GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED`. Se conserva la lista realmente
   enlazada y sus fechas; no se supone que todas tienen QA.
3. Por escena se exige `cs_cdf ≥ 0,65`, se excluyen SCL 0, 1, 3, 8, 9, 10 y 11,
   y se requiere disponibilidad conjunta de las cinco bandas ópticas. El
   conteo de observaciones utiliza esa misma máscara conjunta.
4. Se calcula la mediana anual **por banda**, con al menos tres observaciones.
   Se calculan NDVI y MNDWI **de esas medianas**; esto no equivale a la mediana
   de los índices de cada escena. Se enmascaran denominadores no positivos.
   La composición puede reunir adquisiciones diferentes por banda/píxel y no
   representa un único día ni una posición instantánea del cauce.
5. Un único GeoTIFF contiene los dos años, cinco bandas ópticas, dos índices y
   el conteo de observaciones por año. Se usa EPSG:32718, una cuadrícula de
   30 m anclada con `[30, 0, 0, 0, -30, 0]`, vecino más cercano y NoData −9999.
   B2/B3/B4/B8 tienen entradas de 10 m; B11, de 20 m. Exportar a 30 m no crea
   detalle de 10 m en la comparación ni implica agregar promedios de área.
6. Python comprueba recibo, fechas, conteos, tipos, orden de bandas, CRS,
   alineación, cobertura del recorte y fórmulas contra el raster. NoData nunca
   se confunde con reflectancia cero válida.
7. La comparación muestra solo el soporte válido común a **ambos años y los
   tres modos**. Los huecos son transparentes. Se reutiliza únicamente la
   cuadrícula web de la vista MapBiomas, **no su máscara ni su clasificación**.
   RGB se reproyecta con interpolación bilineal solo para mostrarlo; índices
   y máscaras usan vecino más cercano. Las estadísticas proceden del raster
   nativo, no de los colores ni de los archivos comprimidos.

## Cómo reproducirlo sin exponer credenciales

Desde la raíz del repositorio:

1. Abrir `scripts/export_napo_spectral_gee.js` en el Code Editor de Earth Engine
   de un proyecto autorizado para uso no comercial. Ejecutar el script y las
   dos tareas generadas. No requiere habilitar facturación ni usar Cloud Storage;
   sí consume la cuota de cómputo de Earth Engine y espacio de Google Drive.
2. Descargar los archivos `napo_spectral_2019_2024.tif` y
   `napo_spectral_2019_2024_receipt.geojson` de la carpeta `EcuadorVivo` a
   `data/raw/spectral/` (ignorada por Git). No subir claves ni tokens.
3. Instalar las dependencias con
   `python -m pip install -r requirements-landcover.txt` y ejecutar:

```powershell
python scripts/build_napo_spectral.py --input data/raw/spectral/napo_spectral_2019_2024.tif --receipt data/raw/spectral/napo_spectral_2019_2024_receipt.geojson --explorer
pnpm run check:spectral
python -m unittest discover -s tests
```

`npm run check:spectral` ejecuta el mismo script en entornos con npm.
Los archivos públicos son seis vistas base, cinco derivados y sus manifiestos; el GeoTIFF
multibanda queda local. Los fallos de validación detienen la publicación del
paquete. El estado pendiente no muestra imágenes ficticias.

## Límites y siguiente investigación defendible

La máscara reduce nubes y sombras, pero no garantiza su ausencia. Caudal,
estacionalidad, turbidez, bancos de arena, cambios naturales del cauce,
agricultura, obras y diferencias de iluminación pueden modificar las señales.
Los años tienen la misma ventana de calendario, **no** las mismas fechas
efectivas despejadas por píxel. Al menos tres observaciones no asegura que
estén repartidas entre estaciones. Una mediana anual puede ocultar eventos
breves o combinar estados distintos del río; no sirve para medir directamente
su migración, ancho, una inundación específica o una tendencia con solo dos años.
No se estima mercurio, calidad del agua, ilegalidad, volumen extraído ni áreas
de minería a partir de estos índices.

Para un estudio fluvial posterior: seleccionar escenas/periodos comparables en
estación y caudal, revisar perfiles de calidad, construir una serie temporal,
delimitar canales con verificación manual y datos de mayor resolución, cuantificar
incertidumbre y contrastar campo e informes independientes. Esa fase requiere
una pregunta de investigación y validación adicional, no solo más índices.

## Fuentes y atribución

- [Sentinel-2 SR Harmonized — catálogo oficial y condiciones de datos](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED).
- [Cloud Score+ S2_HARMONIZED V1 — catálogo oficial, método y CC BY 4.0](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_CLOUD_SCORE_PLUS_V1_S2_HARMONIZED).
  Pasquarella, Brown, Czerwinski y Rucklidge (2023),
  [doi:10.1109/CVPRW59228.2023.00206](https://doi.org/10.1109/CVPRW59228.2023.00206).
- [NDVI — USGS Landsat Missions](https://www.usgs.gov/landsat-missions/landsat-normalized-difference-vegetation-index).
- Xu, H. (2006). *Modification of normalised difference water index (NDWI) to
  enhance open water features in remotely sensed imagery*. International Journal
  of Remote Sensing, 27, 3025–3033. [DOI](https://doi.org/10.1080/01431160600589179).
- [Contraste verde/SWIR — USGS EROS](https://www.usgs.gov/centers/eros/science/usgs-eros-archive-vegetation-monitoring-eviirs-global-ndwi).
- [MAAP #230 — monitoreo independiente de Napo, 2025](https://www.maapprogram.org/ecuador-mining-napo/).

Se revisaron fuentes primarias del productor y del monitoreo regional, no
imágenes genéricas ni ilustraciones generadas. Un resumen indexado del DOI de
Xu contenía texto ajeno al artículo y fue descartado; la fórmula se contrastó
con documentación primaria. No se reutilizan figuras web cuya licencia no se
haya establecido. Las condiciones de las imágenes derivadas están en
`LICENSE-DATA.md`, separadas de MIT para el código.

## English summary

This educational lab compares 2019 and 2024 Sentinel-2 annual per-band median
composites through RGB, NDVI and MNDWI. It uses explicit QA, a single aligned
30 m native export and common valid support for all six display images. The
lower-Jatunyacu zoom is an editorial crop, not a mine, basin or administrative
boundary. 2019 is not a pristine baseline. Spectral change alone does not
establish mining, river migration, deforestation or contamination. MAAP #230
is separately cited regional evidence, not pixel labels or our validation.
