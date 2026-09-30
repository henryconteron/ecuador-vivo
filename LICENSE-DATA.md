# Licencias de datos

## Catálogo de fallas

`data/geojson/fallas.geojson` es una adaptación de **GEM Global Active Faults
Database (GAF-DB)**. La obra original y esta adaptación se distribuyen bajo
[Creative Commons Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/).

Fuente fijada para esta versión:

- repositorio: GEMScienceTools/gem-global-active-faults;
- commit: `850fd05b48841eb806d61a37043b5567f5bb99dd`;
- blob del archivo: `fb164770b529695544fa864abe2cc9dd8aa5793d`;
- referencia: Styron, R., & Pagani, M. (2020). *The GEM Global Active Faults Database*.
  Earthquake Spectra, 36(1_suppl), 160–180. https://doi.org/10.1177/8755293020944182

La compilación conserva además la procedencia regional declarada por GEM:

- registros `SA_*`: [SARA Active Faults](https://github.com/GEMScienceTools/SARA-Active-Faults),
  Alvarado et al. (2017), https://doi.org/10.13117/SARA-ACTIVE-FAULTS;
- registros `ATA_*`: [Active Tectonics of the Andes, vía GEM GAF-DB](https://github.com/GEMScienceTools/gem-global-active-faults),
  Veloza et al. (2012), https://doi.org/10.1130/GSAT-G156A.1.

La licencia CC BY-SA 4.0 se aplica al archivo GEM y a esta adaptación; las contribuciones regionales
se mantienen identificadas para conservar la atribución de sus autores. La geometría que se sirve en
este atlas es la adaptación espacial de GEM fijada arriba, no una descarga directa e independiente
de cada repositorio regional.

Modificaciones realizadas: selección espacial de registros SARA y ATA que
intersectan Ecuador, asignación preliminar de provincias mediante geoBoundaries,
normalización de campos para la interfaz bilingüe y clasificación visual
simplificada del tipo de movimiento. Las geometrías no fueron recortadas ni
simplificadas.

## Límites administrativos

Los límites de geoBoundaries se usan durante la construcción para selección
espacial y asignación preliminar de provincias. geoBoundaries gbOpen se publica
bajo CC BY 4.0; los archivos de entrada no se redistribuyen en este repositorio.

## Indicadores geomorfológicos

`data/geojson/estructuras.geojson` reúne observaciones factuales sintetizadas y atribuidas a Eguez
et al. (2003), USGS Open-File Report 03-289. Las ubicaciones representativas se derivaron de las
trazas GEM y, por tanto, la capa se distribuye bajo CC BY-SA 4.0. Los puntos no son levantamientos
de la extensión real de las formas y esta limitación debe conservarse en cualquier reutilización.

## Sismicidad

Los eventos del USGS se consultan en tiempo real y no forman parte del catálogo
almacenado en el repositorio. La interfaz mantiene la atribución y el enlace al
evento original.

## Cobertura del suelo de Tena–Archidona

`assets/images/landcover/napo-v1-2000.png` y `napo-v1-2024.png` son adaptaciones de
**MapBiomas Ecuador LULC V1.0 — Publisher Catalog**, años 2000 y 2024, asset
`projects/mapbiomas-public/assets/ecuador/lulc/v1`. La ficha de esta versión declara
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/):
[fuente, leyenda y licencia](https://developers.google.com/earth-engine/datasets/catalog/projects_mapbiomas-public_assets_ecuador_lulc_v1).
Estos mapas derivados conservan esa atribución y se distribuyen bajo CC BY 4.0,
no bajo la licencia MIT del código ni la CC BY-SA del catálogo de fallas.

Modificaciones: recorte rectangular editorial Tena–Archidona, coloreado con la
leyenda publicada y reproyección a EPSG:3857 mediante vecino más cercano solo para
visualización. Las estadísticas se calcularon sobre la cuadrícula nativa común.
El manifiesto `data/landcover/napo-manifest.json` conserva parámetros y SHA-256;
[método y limitaciones](documentation/napo-landcover.md). No se interpretan los
porcentajes como áreas cantonales ni como prueba automática de deforestación.

## Imagen óptica de Napo

`assets/images/imagery/napo-sentinel2-2024.webp` es una composición modificada de
**Copernicus Sentinel-2 L2A SR Harmonized**, bandas B4/B3/B2, adquisiciones de 2024.
Se rige por las [condiciones de los datos Sentinel](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED),
no por la licencia MIT del código. Atribución: **Contains modified Copernicus
Sentinel data (2024)**. Modificaciones: filtro de calidad, mediana por banda,
recorte Tena–Archidona, muestreo a 30 m, reproyección y ajuste visual RGB/WebP.

La máscara utiliza **Google Cloud Score+ S2_HARMONIZED V1** bajo
[CC BY 4.0, según su ficha oficial](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_CLOUD_SCORE_PLUS_V1_S2_HARMONIZED).
Cita del método: Pasquarella, Brown, Czerwinski y Rucklidge (2023),
[doi:10.1109/CVPRW59228.2023.00206](https://doi.org/10.1109/CVPRW59228.2023.00206).

`assets/images/imagery/napo-mapbiomas-2024.png` conserva la atribución y licencia
CC BY 4.0 de MapBiomas Ecuador V1; es la vista 2024 anterior con una máscara óptica
común adicional. No se interpola su clasificación ni se cambia su leyenda.
El manifiesto `data/imagery/napo-manifest.json` conserva escenas, fechas,
parámetros y SHA-256; [método y límites](documentation/napo-imagery.md).

## Laboratorio espectral de Napo

Las seis vistas de `assets/images/spectral/` contienen **modified Copernicus
Sentinel data (2019, 2024)**. Se aplican las condiciones Sentinel indicadas
arriba, no MIT. Modificaciones: QA con Cloud Score+ (Google, CC BY 4.0),
mediana anual por banda, cálculo de NDVI/MNDWI, recorte, muestreo a 30 m,
reproyección y renderizado. Las paletas son visualizaciones, no clasificaciones.
La referencia MapBiomas solo aporta la cuadrícula web; sus clases y su máscara
no se incorporan a estas vistas. Recibo y SHA-256:
`data/spectral/napo-manifest.json`; [método y bibliografía](documentation/napo-spectral-rivers.md).

MAAP #230/EcoCiencia se enlaza y atribuye como contexto independiente. No se
redistribuyen sus imágenes ni se afirma disponer de permiso sobre esas figuras web.

## Datos demostrativos

Los archivos `*.demo.geojson` contienen geometrías sintéticas sin valor
científico. Se incluyen únicamente para probar la interfaz y quedan cubiertos
por la licencia del código salvo indicación posterior.
