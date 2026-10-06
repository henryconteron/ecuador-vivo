# Banco de datos para tus videos de Ecuador Vivo

Fuentes oficiales consultadas el **6 de octubre de 2026**. La fecha más reciente
disponible cambia por producto. «Actualizado» no significa que exista una imagen
sin nubes de Tena de hoy. Guarda la fecha de consulta y el periodo efectivamente
descargado junto a cada trabajo.

Esta guía complementa [el tutorial del video de lluvia](GUIA-VIDEOS-LLUVIA.md).
Incluye descargas, decisiones de calidad, ideas de videos y los pasos pendientes
para convertir cada fuente al diseño que ya tienes.

## 1. Por dónde empezar

Mi propuesta editorial, en este orden:

1. **La lluvia que cambia cada día:** repetir CHIRPS con otros años. Es el flujo
   que ya produce el MP4 final automáticamente.
2. **Décadas de lluvia y calor:** descargar datos mensuales, calcular anomalías
   respecto de una referencia fija y comparar años completos.
3. **Cómo cambió Ecuador desde 1985:** cobertura y uso del suelo de MapBiomas.
4. **Los ríos que se mueven:** escenas Sentinel-2 y Landsat del mismo tramo,
   con agua, vegetación y suelo expuesto como capas separadas.
5. **El Pacífico se calienta y se enfría:** temperatura marina y contexto ENSO.
6. **La ciudad de noche:** luces nocturnas y crecimiento urbano.

La calidad depende de escoger una fuente adecuada para la pregunta. Un píxel
de 10 m sirve para estudiar cambios del paisaje; una estimación de lluvia de
5–11 km sirve para patrones regionales. Ambas pueden producir buenos videos.

## 2. Fuentes recomendadas y qué permite cada una

Los enlaces son las fichas oficiales: contienen acceso, bandas, términos de uso
y citas. Las resoluciones son nominales o de la malla entregada; no garantizan
que todo objeto de ese tamaño sea identificable.

| Tema y fuente | Historia / ritmo | Detalle aproximado | Video posible y precaución principal |
| --- | --- | --- | --- |
| [CHIRPS v2](https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY) | Desde 1981; diario | 0,05°, ≈5,6 km | Lluvia de un año o décadas; es la versión del video terminado. |
| [CHIRPS v3 DAILY_SAT](https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHC_CHIRPS_V3_DAILY_SAT) | Desde 1981; diario derivado | 0,05° | Serie alternativa nueva; mantener una sola versión durante toda la comparación. |
| [GPM IMERG V07](https://developers.google.com/earth-engine/datasets/catalog/NASA_GPM_L3_IMERG_V07) | Desde 2000; cada 30 min | ≈11 km | Evolución de episodios de lluvia. Integrar tasas mm/h; distinguir provisional/final. |
| [ERA5-Land diario](https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_DAILY_AGGR) | Desde 1950; diario | Malla ≈11 km | Temperatura del aire, humedad del suelo y otras variables; es reanálisis. |
| [MODIS MOD11A1](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD11A1) | Desde 2000; diario | 1 km | Calor de la superficie diurno/nocturno; faltan observaciones con nubes. |
| [Landsat 8 L2](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2) | Desde 2013; escenas, ciclo de 16 días del satélite | Óptico 30 m; térmico nativo 100 m, entregado a 30 m | Paisaje e islas de calor; el térmico no gana detalle real al entregarse a 30 m. |
| [Landsat 5 L2](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LT05_C02_T1_L2) | Archivo desde 1984 | Óptico 30 m | Antes/después histórico; combinar misiones exige armonización y QA. |
| [Sentinel-2 SR Harmonized](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED) | Desde 2017 en esta colección; escenas | Visible/NIR 10 m; SWIR 20 m | Ríos, vegetación, ciudades, glaciares; en Amazonía la nubosidad limita las fechas útiles. |
| [MapBiomas Ecuador](https://ecuador.mapbiomas.org/en/mapas-de-cobertura-y-uso/) | Colección 3.0: 1985–2024; anual | 30 m | Transformación de cobertura y usos del suelo durante 40 años. |
| [Dynamic World](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1) | Desde 2015; por observación Sentinel-2 | 10 m | Cobertura reciente; guardar probabilidades, no solo la clase ganadora. |
| [Hansen GFC v1.13](https://developers.google.com/earth-engine/datasets/catalog/UMD_hansen_global_forest_change_2025_v1_13) | Base 2000 y pérdida anual hasta 2025 | ≈30 m | Dónde se perdió cobertura arbórea; no atribuye automáticamente deforestación o minería. |
| [MODIS MOD13Q1](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD13Q1) | Desde 2000; compuestos de 16 días | 250 m | Estacionalidad de vegetación con NDVI/EVI; no llamarlo diario. |
| [JRC agua mensual v1.4](https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_MonthlyHistory) | Marzo 1984–diciembre 2021; mensual | 30 m | Historia de agua superficial; esta versión no contiene 2026. |
| [Sentinel-1 GRD](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD) | Desde 2014; escenas radar | Muestreo variable; muchas escenas IW a 10 m | Inundaciones incluso con nubes; requiere comparación por órbita y tratamiento del relieve. |
| [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/download/) | Archivo y detecciones recientes; por pasada | VIIRS nominal 375 m; MODIS 1 km | Pulsos de focos térmicos. Un punto no representa el perímetro de un incendio. |
| [MODIS MCD64A1](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD64A1) | Desde 2000; producto mensual | 500 m | Superficie quemada y fecha estimada; no confundir con detecciones FIRMS. |
| [VIIRS luces mensuales](https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMCFG) | Desde 2012; mensual | ≈464 m | Ecuador iluminándose; revisar cobertura sin nubes y luces temporales. |
| [GHSL superficie construida](https://developers.google.com/earth-engine/datasets/catalog/JRC_GHSL_P2023A_GHS_BUILT_S) | Épocas 1975–2030, cada 5 años | 100 m | Crecimiento urbano estimado; incluye interpolación/extrapolación, no fotos anuales. |
| [NOAA OISST](https://developers.google.com/earth-engine/datasets/catalog/NOAA_CDR_OISST_V2_1) | Desde septiembre 1981; diario | 0,25°, ≈28 km | Temperatura/anomalías del Pacífico; encuadre oceánico, no solo Ecuador continental. |
| [SMAP L4 v008](https://developers.google.com/earth-engine/datasets/catalog/NASA_SMAP_SPL4SMGP_008) | Desde 2015; cada 3 h | 9 km | Humedad del suelo y sequedad regional; producto modelado con asimilación. |
| [GOES-19](https://developers.google.com/earth-engine/datasets/catalog/NOAA_GOES_19_MCMIPF) | Archivo reciente desde 2025; subdiario | Producto GEE 2 km | Nubes en movimiento. Para años anteriores, consultar GOES-16 y su periodo. |
| [Sentinel-5P NO₂](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S5P_OFFL_L3_NO2) | Desde 2018; observaciones por órbita | Huella de varios km, aunque la rejilla L3 sea más fina | Variación regional de columna de NO₂; no equivale a concentración al respirar. |
| [SRTM](https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003) | Campaña de 2000; estático | 30 m | Relieve para mapas 3D, perfiles y fondos; no animar como si midiera erosión anual. |

Cobertura es lo que distingue el sensor (agua, vegetación, superficie construida);
uso incorpora actividades o función del territorio. No toda clasificación visual
permite identificar un uso, una actividad ilegal o su causa.

## 3. Descargar lluvia diaria sin generar todavía videos

Preparé `production/monitor/download_daily_rain.py`. Usa solo Python estándar,
comparte la carpeta de caché con el generador y conserva un registro aparte.
Verifica la compresión y la cabecera TIFF antes de aceptar cada descarga.

Abre PowerShell y entra al proyecto:

```powershell
Set-Location -LiteralPath 'C:\Users\JHONY CONTERON\OneDrive\Documentos\GitHub\fallas-ecuador'
```

Descarga únicamente datos, por ejemplo todo 2023:

```powershell
python production/monitor/download_daily_rain.py --start 2023-01-01 --days 365
```

Más adelante, crea el video con el mismo periodo:

```powershell
python production/monitor/render_daily_rain.py --start 2023-01-01 --days 365
```

Los datos se guardan en `_local/climate-studio/2023-01-01-365days/`.
`download-receipt.json` registra fechas, enlaces y SHA-256; `complete: true`
indica que terminó la descarga solicitada. Si se corta, repite el comando:
revisa y reutiliza los archivos presentes. No reemplaza el registro del video.

Para una secuencia de años, este bloque descarga 2020–2025 de manera secuencial
y calcula los años bisiestos. Puede ocupar varios GB; cambia el rango a lo necesario:

```powershell
foreach ($rainYear in 2020..2025) {
    $rainDays = if ([DateTime]::IsLeapYear($rainYear)) { 366 } else { 365 }
    python production/monitor/download_daily_rain.py --start "$rainYear-01-01" --days $rainDays
    if ($LASTEXITCODE -ne 0) { throw "Se detuvo la descarga de $rainYear; revisa el error." }
}
```

Esto no lanza videos ni requiere Earth Engine. Las descargas son archivos de
cobertura global; el generador recorta Ecuador al leerlos. Los 1,31 GiB observados
para 2024 son una referencia local, no una garantía de tamaño para todos los años.
No se ha descargado automáticamente el rango anterior como parte de esta guía.

Datos actuales: visita el [directorio diario oficial](https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/),
entra al año y verifica el último archivo publicado. Descarga solo ese periodo.
Ejemplo: enero–agosto de 2026 son 243 días:

```powershell
python production/monitor/download_daily_rain.py --start 2026-01-01 --days 243
```

Si el servidor devuelve 404, la fecha puede no estar disponible. No se rellena
con cero lluvia. El descargador actual es exclusivamente **CHIRPS v2**.

## 4. Descargar décadas: preferir mensual para la primera historia

Para recorrer varias décadas en un minuto, comienza por datos mensuales:
1981–2025 son **540 meses**, frente a más de 16.000 días. Conserva los datos diarios
para episodios concretos en los que quieras profundizar.

Tienes dos rutas:

- [GeoTIFF mensuales oficiales de CHIRPS v2](https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/tifs/).
  Elige archivos como `chirps-v2.0.1981.01.tif.gz`. Son globales; puedes descargarlos
  desde el navegador y descomprimir con 7-Zip. Guárdalos en una carpeta separada
  de los diarios, porque representan acumulación mensual.
- Exportar únicamente tu región desde Earth Engine con la receta del paso 5,
  usando `MODE = 'monthly'`. Ahorra almacenamiento local y preserva valores.

El generador del video diario no lee automáticamente archivos mensuales. Su
adaptación necesita fecha mensual, unidades mm/mes, escala nueva y lectura de
esos archivos. Puedes conservar el mismo diseño gráfico.

## 5. Descargar temperatura o lluvia desde Earth Engine: receta preparada

Archivo: `scripts/export_climate_data_for_videos_gee.js`.

1. Abre ese archivo con tu editor y copia todo su contenido.
2. Entra a [Earth Engine Code Editor](https://code.earthengine.google.com/) con tu cuenta.
3. Crea un script nuevo y pega el contenido.
4. Deja la primera prueba con `PRODUCT = 'temperature'`, `YEAR = 2024`,
   `FIRST_MONTH = 1`, `MONTHS = 1` y `MODE = 'daily'`.
5. Presiona **Run**. Revisa **Console**. La receta comprueba que estén todas las
   fechas y que no existan duplicados antes de preparar las tareas.
6. Ve a **Tasks**. Inicia la tarea del GeoTIFF y la del `manifest` mediante **Run**.
7. Espera a que ambas terminen; que se vean en Tasks no significa que terminaron.
8. En Drive abre `EcuadorVivo_Datos` y descarga el TIFF y el CSV.

Un TIFF diario contiene hasta 31 bandas, una por fecha. Es un contenedor de mapas:
no es un MP4 ni una fotografía RGB. Los nombres incluyen fecha, como
`20240101_value`. El CSV conserva el orden, fuente y transformación.

Para descargar un año cambia `MONTHS` a `12`. Se preparan doce TIFF y un CSV.
Ejecuta por lotes pequeños y revisa el primer resultado antes de pedir más años.

| Configuración | Resultado |
| --- | --- |
| `PRODUCT = 'temperature'` | ERA5-Land, temperatura media diaria del aire a 2 m; Kelvin convertido a °C. |
| `PRODUCT = 'rain_v2'` | Lluvia CHIRPS v2 compatible en variable y versión con el último video. |
| `PRODUCT = 'rain_v3'` | Otra serie, CHIRPS v3 DAILY_SAT; guardar separada de v2. |
| `MODE = 'daily'` | Una banda numérica por fecha dentro del TIFF de cada mes. |
| `MODE = 'monthly'` | Un mapa mensual: suma de lluvia o media de temperatura; incluye `valid_days`. |

En modo mensual solo se conservan valores donde hay datos válidos todos los
días del mes. La receta mantiene la malla nativa y NoData `-9999`; no convierte
datos faltantes en sequía o frío. El encuadre es un rectángulo que contiene Ecuador
continental y partes vecinas: recorta al polígono nacional antes de calcular
estadísticas de Ecuador. Para Tena/Archidona puedes usar como ventana editorial
`BBOX = [-78.04, -1.12, -77.55, -0.72]`, que no son límites cantonales.

No cambies `scale` a 10 m para temperatura: no produce información nueva.
La receta utiliza `crsTransform` nativo para conservar la alineación.

**Estado real:** sintaxis revisada localmente; esta nueva receta aún requiere
la primera ejecución autenticada en Earth Engine. No se han enviado exportaciones
masivas ni se ha comprobado tu carpeta de Drive en este turno.
El generador actual de MP4 no importa todavía estos TIFF multibanda; hay que
adaptar su lector. El flujo diario CHIRPS descargado con Python sí funciona completo.

## 6. Datos recientes: cómo saber cuál es realmente el último

En el editor puedes ejecutar esta consulta; cambia el identificador por una
ImageCollection del catálogo (no sirve para productos que son una sola Image):

```javascript
var datos = ee.ImageCollection('ECMWF/ERA5_LAND/DAILY_AGGR');
print('Última imagen del catálogo', datos.sort('system:time_start', false).limit(1));
```

Para escenas Sentinel, agrega `filterBounds(tuRegion)` y revisa cobertura, nubes y
calidad por píxel. Una fecha global reciente puede no cubrir tu sitio.
Los campos de disponibilidad del catálogo pueden diferir del resumen automático;
verifica la colección, no solo la frase del resumen.

Cada producto tiene retrasos y revisiones. Etiqueta el último año como «hasta
agosto de 2026», por ejemplo, y distingue estimaciones provisionales de definitivas.
No empalmes CHIRPS v2, v3 e IMERG para completar huecos sin metodología explícita.

## 7. Cobertura y uso del suelo: la primera gran historia del territorio

### Historia larga: MapBiomas Ecuador

1. Abre [Descargas de MapBiomas Ecuador](https://ecuador.mapbiomas.org/descargas/).
2. Entra a mapas de cobertura y uso y selecciona una colección completa.
3. Usa el enlace de descarga o la herramienta Earth Engine facilitada allí;
   el portal documenta recortes territoriales y temporales.
4. Comienza por tu zona y unos años separados: 1985, 1995, 2005, 2015, 2024.
5. Descarga también la leyenda/códigos, metodología y cita. Luego amplía a todos
   los años para una animación anual.
6. Conserva los códigos originales de clase en GeoTIFF. Para dibujar usa colores
   fijos y remuestreo por vecino más cercano; no suavices códigos con bilineal.

La página de colección consultada presenta **Colección 3.0, 1985–2024**.
Tu receta `scripts/export_napo_landcover_gee.js` utiliza en cambio el producto
[Publisher Catalog V1.0](https://developers.google.com/earth-engine/datasets/catalog/projects_mapbiomas-public_assets_ecuador_lulc_v1),
con dos años configurados. Son etiquetas distintas: no lo renombres como Colección
3.0 ni mezcles sus mapas sin comprobar equivalencia y metodología.

### Cambios recientes: Dynamic World

Usa `GOOGLE/DYNAMICWORLD/V1` y filtra región y fechas. Descarga `label` junto con
las nueve probabilidades. El catálogo incluye ejemplos y acceso al editor.
Empieza con escenas útiles o compuestos mensuales/estacionales, no prometas un
mapa completo sin nubes por día. Guarda número de observaciones por píxel.

Para compuestos, documenta si usaste moda de clases o clase de probabilidad media
máxima: no son operaciones equivalentes. Conserva incertidumbre y revisa cambios
con imágenes ópticas. Una oscilación de clase puede ser error o estacionalidad.

## 8. Imágenes reales, ríos y detalle local

Ruta visual para descargar escenas:

1. Abre [Copernicus Browser](https://browser.dataspace.copernicus.eu/).
2. Busca Tena, Archidona o tu región y delimita un área pequeña.
3. Elige Sentinel-2 L2A y un intervalo de fechas.
4. Revisa varias escenas; el porcentaje global de nubes no asegura un río despejado.
5. Descarga datos analíticos en TIFF o el producto fuente, además del RGB si quieres
   usarlo de referencia. Una captura PNG no conserva las bandas para calcular índices.
6. Guarda ID de escena, fecha, bandas, malla y máscara de nubes.

[Documentación oficial del navegador](https://documentation.dataspace.copernicus.eu/Applications/Browser.html).

Para series procesadas en Earth Engine ya tienes `scripts/export_napo_spectral_gee.js`:
compara 2019 y 2024, exporta bandas, NDVI, MNDWI y conteos, con malla común de 30 m.
Es una composición anual por banda, no una foto de un día. Preserva esa descripción.
Sentinel-2 tiene bandas de 10 y 20 m; para aprovechar más detalle hay que revisar
el procesamiento completo y no solo cambiar el tamaño del archivo exportado.

NDWI usa verde/NIR; MNDWI usa verde/SWIR. Ninguno mide por sí solo minería,
caudal o agua contaminada. Compara épocas hidrológicas similares, revisa sombras
y nubes, muestra RGB junto al índice y mide cambios con una metodología consistente.
Para historia anterior usa Landsat; las misiones y bandas deben armonizarse.

## 9. Vegetación, calor superficial, incendios y luces: descargas prácticas

### MODIS sin escribir un programa nuevo

En [NASA AppEEARS](https://appeears.earthdatacloud.nasa.gov/) puedes solicitar recortes
por área y periodo usando una cuenta Earthdata. Revisa las opciones del portal:
selecciona producto/version, bandas, fechas y formato GeoTIFF; envía el pedido y
descarga los resultados junto con las capas de calidad. También puedes acceder a
los productos desde las fichas Earth Engine de la tabla.

- Vegetación: MOD13Q1.061, `NDVI`, `EVI` y calidad. Factor 0,0001; cada compuesto
  representa 16 días. Para empezar, revisa `SummaryQA == 0` y conserva los huecos.
- Superficie caliente: MOD11A1.061, `LST_Day_1km`, `LST_Night_1km`, `QC_Day`,
  `QC_Night`. Conversión: valor × 0,02 − 273,15. Interpreta los bits de QA según
  la ficha; no uses la máscara de día para las observaciones nocturnas.
- Quemado: MCD64A1.061, `BurnDate` y calidad. El producto es mensual aunque
  contenga el día estimado de quema. No garantiza detección de incendios pequeños.

### Focos térmicos

En [FIRMS Archive Download](https://firms.modaps.eosdis.nasa.gov/download/) selecciona
sensor, fechas y área/país según las opciones disponibles y descarga CSV o formato
geográfico. Conserva fecha y hora, confianza, sensor y FRP cuando esté disponible.
Para recientes utiliza el acceso NRT enlazado en FIRMS y verifica su latencia.
Son puntos de detección, no polígonos del área quemada; varias pasadas pueden
detectar el mismo incendio. No cuentes puntos como número de incendios únicos.

### Luces nocturnas

Colección `NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG`. Descarga `avg_rad` y `cf_cvg` por mes.
Un píxel sin observaciones no equivale a apagón. Compara meses equivalentes y
revisa fuegos, embarcaciones y cambios de cobertura. Para una denuncia o afirmación
de apagones hacen falta registros independientes y una escala temporal adecuada.

## 10. Plantilla para exportar un producto adicional a Drive

Este ejemplo prepara **un mes de luces nocturnas** conservando valores y cobertura.
Cópialo en un script nuevo de Earth Engine. Es una receta, no una exportación ya
ejecutada aquí. No sustituye automáticamente el control de calidad de otros productos.

```javascript
var zona = ee.Geometry.Rectangle([-81.5, -5.2, -75.0, 1.8], 'EPSG:4326', false);
var conjunto = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG')
  .filterDate('2024-01-01', '2024-02-01');
conjunto.size().evaluate(function (n, error) {
  if (error || n !== 1) { print('Revisa disponibilidad', error || n); return; }
  var original = ee.Image(conjunto.first());
  var salida = original.select(['avg_rad', 'cf_cvg']).toFloat();
  salida.projection().evaluate(function (p, err) {
    if (err || !p) { print(err); return; }
    Export.image.toDrive({
      image: salida.clip(zona).unmask(-9999, false),
      description: 'viirs_luces_2024_01', folder: 'EcuadorVivo_Datos',
      region: zona, crs: p.crs, crsTransform: p.transform,
      maxPixels: 1e9, fileFormat: 'GeoTIFF',
      formatOptions: {cloudOptimized: true, noData: -9999}
    });
    print('Guarda estos metadatos junto al TIFF', original);
  });
});
```

Consulta la [documentación de exportación](https://developers.google.com/earth-engine/guides/exporting_images)
para otras geometrías o productos. `scale` y `crsTransform` son alternativas;
no introduzcas ambos. Usa imágenes numéricas, no `.visualize()`, para tus archivos
maestros. `.visualize()` es para la representación coloreada.

## 11. Preparar una historia climática defendible

1. Escoge una serie homogénea y un periodo completo, por ejemplo 1981–2025.
2. Para cada mes suma la lluvia diaria o promedia la temperatura diaria.
3. Comprueba fechas completas y cobertura por píxel. No aceptes un mes incompleto
   porque una función devolvió una imagen.
4. Define una base explícita, por ejemplo 1991–2020. Para enero de un año, resta
   el promedio de los eneros de esa base; no el promedio de todos los meses.
5. Expresa anomalía de lluvia en mm/mes y de temperatura en °C. Si eliges porcentajes,
   trata aparte zonas cuya lluvia de referencia sea cercana a cero.
6. Usa una paleta divergente centrada en cero y una escala fija durante toda la serie.
7. Agrega el contexto ENSO con fechas y fuente de su índice, sin atribuir por sí
   sola cada sequía o inundación a El Niño o La Niña.

Existe una receta anterior, `scripts/export_ecuador_climate_history_gee.js`, con
base **1981–2010**. No la describas como 1991–2020. Además, contar imágenes mensuales
generadas no basta para garantizar que estén completos los datos diarios de cada
mes: ese control requiere revisión antes de usarla como archivo científico final.

NOAA CPC anunció que adoptó **RONI** para el seguimiento ENSO en febrero de 2026.
Para un trabajo nuevo consulta la [serie RONI](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/)
y [su explicación oficial](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/announcement.php).
Si reproduces estudios anteriores con ONI, conserva ese índice y su versión;
no intercambies etiquetas de eventos sin explicarlo.

## 12. Calidad excelente: qué conservar desde la descarga

- **Archivo maestro:** valores originales/convertidos con unidades, GeoTIFF o NetCDF,
  georreferencia, máscara y QA. Para datos de eventos, CSV/GeoJSON con fechas.
- **Representación:** RGB y gráficos derivados; conserva el archivo numérico aunque
  termines usando únicamente el video en redes.
- **Misma malla:** CRS, origen y tamaño de píxel iguales entre fechas de una comparación.
- **Misma escala de color:** fija por variable y periodo; distingue mm/día y mm/mes.
- **Datos continuos:** interpolación espacial documentada para mostrar; sin crear
  detalle científico. Clases y máscaras: vecino más cercano, sin gradientes entre códigos.
- **Fechas:** respeta frecuencia real. Un compuesto mensual no se convierte en diario
  repitiéndolo 30 veces. Una transición animada tampoco es una observación nueva.
- **Encuadre:** nacional para clima regional; local para Sentinel/Landsat. Reserva
  10 m a sitios pequeños antes de intentar exportar todo Ecuador a esa resolución.
- **Salida final:** reutiliza tipografía, fecha, leyenda y composición del video
  aprobado; produce al menos 1080 × 1920 y evita recompresiones sucesivas.

Los TIFF por sí solos no adquieren el diseño del último MP4: cada nueva variable
necesita conectar lectura, conversión, QA y leyenda al montador. El motor actual
solo tiene completada esa conexión para lluvia CHIRPS v2 diaria.

## 13. Archivo organizado y ahorro de espacio/cuota

Estructura sugerida dentro de `_local` o de tu respaldo en Drive:

```text
EcuadorVivo_Datos/
  lluvia/CHIRPS_v2/diario/2024/
  lluvia/CHIRPS_v2/mensual/1981_2025/
  temperatura/ERA5Land/diario/2024/
  temperatura_superficial/MOD11A1_061/
  cobertura/MapBiomas_Ecuador/coleccion_3/
  cobertura/DynamicWorld/
  rios/Sentinel2/
  vegetacion/MOD13Q1_061/
  luces/VIIRS/
  metadatos/
  renders/
```

La caché del generador diario debe quedarse donde el programa la busca;
la estructura anterior es para el archivo de trabajo/respaldo, no una instrucción
para mover esa caché sin adaptar rutas.

Cada lote debe conservar fuente, versión, enlace, cita/licencia, periodo, región,
bandas, unidades, escalas, CRS, NoData, filtros de calidad y fecha de descarga.
Una copia en Drive debe incluir esos metadatos, no solo los colores.

Para ahorrar: descarga una vez, recorta áreas pequeñas, prueba un mes, agrupa
bandas por mes y archiva datos numéricos. Renderizar localmente no consume cuota
de Earth Engine. Exportar en Earth Engine sí usa recursos: el acceso no comercial
tiene [cuotas de cómputo](https://developers.google.com/earth-engine/guides/noncommercial_tiers).
No hace falta habilitar productos de pago para usar estas recetas con un proyecto
no comercial ya habilitado, pero tampoco es cómputo ilimitado.

## 14. Estado de las herramientas entregadas

| Herramienta | Comprobado | Pendiente |
| --- | --- | --- |
| Video diario CHIRPS v2 | Año 2024 generado y revisado | Nuevos periodos según disponibilidad. |
| `download_daily_rain.py` | Descarga real de 2023-01-01 y reutilización/verificación de siete archivos de 2024 | No se han descargado décadas completas. |
| `export_climate_data_for_videos_gee.js` | Sintaxis local y bandas contrastadas con catálogo | Ejecutar primer mes en tu cuenta; revisar salida TIFF/CSV. |
| MapBiomas, MODIS, VIIRS, Sentinel y otras rutas de esta guía | Fuentes y documentación consultadas | Descargar selección y adaptar cada variable al montaje final. |

Mi primera selección sería lluvia y temperatura mensual 1981–2025, MapBiomas
1985–2024 y escenas despejadas del corredor Tena–Archidona. Da material para varias
historias y permite aprender el flujo antes de almacenar muchas fuentes distintas.
