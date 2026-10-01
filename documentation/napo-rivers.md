# Napo provincial: detalle óptico y señales para revisar

## Cobertura y estado

El objetivo es **la provincia de Napo**, no solo Jatunyacu ni toda la cuenca
internacional del río Napo. Incluye Tena, Archidona y el resto de la provincia.
La cobertura se construye por bloques verificados, no está completa inicialmente.
No es un inventario exhaustivo de ríos ni detecta todos los cambios. También
pueden aparecer lagunas; vegetación, nubes y cauces estrechos limitan la cobertura.

El manifiesto `data/rivers/napo-manifest.json` determina el estado efectivo:
`pending` no habilita imágenes ni marcadores; solo `ready` con archivos reales
verificados los habilita. La ventana anterior a 30 m permanece independiente:
no se amplía artificialmente para fabricar este producto a 10 m.

Exportaciones solicitadas el 30 de septiembre de 2026 desde
[este snapshot reproducible](https://code.earthengine.google.com/9f8b90d605bf69f31301ccef54d4fc31):

- RGB provincial: `napo_province_rgb10_2019_2024`, ID `4FPBQW2EQNP2MKWGOXX2LDWY`.
- Cribado: `napo_water_change_candidates_2019_2024`, ID `I365UUIUYWYW652MRXZYFHYU`.
- Recibo: `napo_province_rgb10_2019_2024_receipt`.

El recibo del **primer intento** conserva 809 escenas enlazadas a QA en 2019 y 810 en 2024,
una única entidad Napo y aproximadamente 12.750,6 km² de área provincial.
Son inventarios de escenas, **no** observaciones útiles en cada píxel.
Las tareas consumen cómputo/cuota del proyecto educativo; no se ha activado
facturación ni contratado imágenes comerciales. No se presupone cuota ilimitada.

**Resultado del primer intento:** el cribado falló por falta de memoria después
de cinco intentos automáticos. Se solicitó cancelar RGB a los 37 minutos;
la cancelación quedó confirmada a los 43 minutos, con 326.601,661 EECU-segundos
(aproximadamente 90,72 horas EECU) de cómputo acumulado.
No se generó ni publicó un producto provincial verificado. Ese snapshot es
histórico y no corresponde al exportador optimizado actual.

**Reformulación:** rejilla provincial de 3 × 3 bloques, IDs 0–8; ejecutar solo
uno cada vez. Bloque 7 cubre un entorno amplio de Tena–Archidona, no un solo río.
Seleccionar hasta ocho escenas por trimestre ordenadas por nubosidad de
granulo: máximo 32 escenas por año y bloque. Exigir 3 observaciones útiles
en ambos años para RGB y mantener 10 para el cribado. La menor nubosidad de
granulo no garantiza cielo despejado en cada río: la máscara local sigue
siendo obligatoria. No lanzar los nueve bloques sin revisar el primero,
cobertura útil y cuota restante. La cobertura publicada describe el bloque
real; no se anuncia provincia completa ni se funden bloques sin revisar
costuras temporales y procedencia. `maxPixels` limita tamaño, no horas EECU.

**Prueba incremental iniciada el 30 de septiembre de 2026:** bloque 7,
bbox `[-77.96546, -1.24118, -77.50557, -0.8169066667]`.
El recibo real descargado documenta 32 escenas enlazadas a QA por año.
No equivale a 32 observaciones útiles en todos los píxeles.

- RGB: `H5FHGL7MUJRDTJW7JMOA7ADT`,
  [snapshot del procesamiento](https://code.earthengine.google.com/cd04879556ac01c5b7d0c841c6a5aeb7).
- Recibo: `2AQ6VDLEXALSPYRO5TKPVWKU`, completado y descargado.
- Cribado del bloque: `I5C5KU7IPWJQ2MEAEYAGHX3U`.
- **RGB completado y verificado localmente:** nueve minutos, 6.020,8965 EECU-segundos
  (aprox. 1,67 horas EECU). Tres chunks GeoTIFF, 122.044.180 bytes descargados;
  392 teselas WebP sin pérdida, 67.023.224 bytes, SHA-256 verificado por archivo.
- El cribado sigue pendiente: la capa real de imágenes está habilitada, pero
  `candidate_status: pending`, `candidate_count: null` y sin puntos publicados.
  Se solicitó cancelar la tarea del bloque tras llegar al cuarto intento
  automático sin resultado verificado. No se declara un error concreto de
  ese intento sin su diagnóstico final. La siguiente mejora del cribado debe
  exportar conteos de agua/observaciones y calcular componentes/celdas localmente,
  evitando repetir la vectorización costosa en Earth Engine.

**Resultado local verificado el 1 de octubre de 2026:** la exportación de
conteos `7SPEIOXTE6V3SJMH5Q455C7Q`,
[snapshot del cálculo](https://code.earthengine.google.com/249686ea4d7665fce92b92e26d7d8b46),
produjo tres chunks GeoTIFF (8.331.626 bytes) y su recibo. Las adquisiciones,
QA, límite y bloque coinciden con el RGB. Python obtuvo 5.329.345 píxeles
comparables y **24 celdas candidatas sin revisar**; el estado actual de cribado
es `ready`. Ese estado certifica integridad técnica, no validación científica
de cada señal. No se volvió a exportar RGB ni se lanzaron los otros ocho bloques.
La lectura final consultada en el Code Editor el 1 de octubre confirmó
`Completed`, primer intento, diez minutos y 4.602,8711 EECU-segundos
(aprox. 1,28 horas EECU). Esto no informa la cuota mensual restante.

**Muestra depurada integrada localmente el 1 de octubre de 2026:** se auditó
en GEE el plan `6283cb911fc0f97444d63f181d20f0f11f02b05954e6802d9f364e7d17734ca6`,
con IDs y fechas exactos, sin sustituir escenas ni rellenar el cupo trimestral.
Se ejecutaron RGB y conteos secuencialmente y se descargaron ambos recibos:

- RGB `QDAQB64MTUFNJKPWQELOL5MK`: `Completed`, diez minutos, primer intento,
  3.233,9036 EECU-segundos. [Snapshot del RGB depurado](https://code.earthengine.google.com/9335199e44354590a4d6f0005fcae77c).
- Recibo RGB `L3E7LRIXGCYNXN7MSRSOSVT3`: completado, cinco segundos.
- Conteos `TI62ULGNHUJHNZFPDPZIMKLH`: `Completed`, trece minutos, primer intento,
  4.414,9360 EECU-segundos. [Snapshot de conteos depurados](https://code.earthengine.google.com/8096332a0680389d6fc5f0184fdd5064).
- Recibo conteos `PNS27AUAQXHFU2FKYEOOTBDT`: completado, tres segundos.

El proyecto figuraba como no comercial, nivel Community. No se modificó
facturación ni se lanzaron los demás bloques. El envío RGB necesitó un reintento
tras un error de conexión; la tarea finalmente aceptada terminó sin error.
No se obtuvo una lectura de cuota mensual restante: no inferirla de estos costes.

Python reconstruyó y verificó ambos productos en `tmp/rivers-next/rebuilt`.
La muestra pasa de 32/32 a **31/32 archivos**, sin cambiar los 17/13 días UTC.
Las 392 teselas RGB tienen exactamente los mismos SHA-256 que antes; permanecen
5.329.345 píxeles comparables, 7.592/8.354 píxeles de señal retenida de
aumento/disminución y las mismas 24 celdas con iguales valores. **No hay una
mejora visual ni nuevas señales demostradas por esta depuración.** Tampoco
constituye revisión de campo, validación estacional ni identificación de causas.

`data/rivers/history/sample-comparison.json` contiene la comparación completa,
comprobada por las pruebas contra los resultados anteriores y nuevos.
El historial conserva manifiesto/configuración/celdas originales y el plan;
`tmp/rivers-next/original-bundle` conserva además las imágenes originales como
respaldo local. No se modificó retrospectivamente el inventario de un producto
antiguo: el nuevo manifiesto procede de exportaciones nuevas reales. La
integración es local, no implica commit, push ni publicación en GitHub Pages.

La primera ejecución reducida no creó tareas porque `merge` modificó los
índices de adquisición. Se corrigió preservando el ID original antes de
combinar trimestres; no se bajó el umbral de nubes ni se aceptó un recibo vacío.

## Por qué el río se veía borroso

La exportación anterior se muestreó a 30 m y su imagen web tiene esa escala.
Ampliarla no recupera los detalles originales. B2/B3/B4/B8 de Sentinel-2 tienen
resolución nominal de 10 m: una nueva exportación de esas bandas conserva
mucho más detalle espacial. Una celda de 30 × 30 m ocupa el área de nueve
celdas de 10 × 10 m; **no** implica nueve veces más exactitud.
La QA SCL sigue siendo de 20 m y no garantiza ausencia total de nube/sombra.

El RGB optimizado es mediana **por banda de la muestra anual seleccionada**,
no de todas las adquisiciones del año, con contraste fijo `0–0,3`,
gamma `1,2`, igual en ambos años. No es la foto de un día: un cauce móvil puede
quedar difuminado temporalmente incluso a 10 m. Para medir orillas, seleccionar
escenas fechadas comparables en estación y nivel hidrológico y validarlas.
No se usa IA, superresolución, enfoque artificial ni relleno de huecos.

## Señales candidatas: cribado exploratorio no validado localmente

1. Periodos 2019 y 2024, muestra trimestral acotada y bloque dentro del límite provincial.
2. Preservar el `system:index` original como `source_scene_index` antes de
   combinar los trimestres (Earth Engine modifica índices al hacer `merge`).
   Unión de ese identificador con `system:index` de Cloud Score+; `cs_cdf ≥ 0,65`.
3. Excluir SCL 0, 1, 3, 8, 9, 10, 11; máscara conjunta B4/B3/B2/B8 y
   denominador verde + NIR positivo.
4. NDWI de agua **por escena**: `(B3 − B8)/(B3 + B8)`; señal de agua con NDWI > 0,2.
5. Frecuencia en la muestra anual = observaciones candidatas de agua / observaciones válidas seleccionadas.
   Es frecuencia entre adquisiciones seleccionadas, **no** porcentaje de días inundados.
   Exigir al menos 10 observaciones válidas en ambos años.
   Exportar cuatro bandas `uint8`: agua/válidas 2019 y agua/válidas 2024.
   Son conteos exactos, no frecuencias redondeadas ni clasificación del RGB.
   Cero agua con ≥10 observaciones útiles es un dato válido; cero observaciones
   es falta de datos. El procesador rechaza un bloque sin apoyo comparable:
   no lo convierte en una colección observada vacía.
6. Diferencia absoluta de frecuencia ≥ 0,5 (50 puntos porcentuales), con
   frecuencia ≥ 0,5 en al menos un año.
7. Componentes conectados de al menos 100 píxeles (aprox. 1 ha), ocho vecinos,
   por separado para aumento y disminución.
   Calculados localmente con SciPy, uniendo chunks en su rejilla original
   antes de etiquetar; no se remuestrea ni rellenan huecos. La diferencia de
   fracciones usa productos cruzados enteros para evitar redondeo del umbral.
   Un componente puede seguir truncado en el borde del bloque provincial;
   no se ha verificado su continuidad con bloques todavía sin procesar.
8. Agrupar en celdas Web Mercator de 1 km y retener las que acumulan ≥ 1 ha
   aproximada de señales. El marcador es el **centro de la celda**, no la
   posición exacta de una ribera ni el nombre de un río.
   Al abrirlo se muestra el contorno de la celda y su porcentaje de superficie
   con comparación válida. Ese porcentaje describe cobertura, no confianza
   del clasificador; tampoco es porcentaje de días con agua.

Los umbrales 0,2 / 0,5 / 10 / 100 / 1 ha son **decisiones de cribado del
proyecto**, no valores universales ni parámetros cuya precisión se haya
validado en Napo. NDWI no es MNDWI (SWIR a 20 m) ni NDMI. El área por celda
es proyectada y aproximada; no reportarla como hectáreas de minería, erosión,
deforestación o contaminación. Las celdas no delimitan un evento o actividad.

Crecidas normales, estacionalidad, fechas despejadas diferentes, bancos de
arena, turbidez, sombras, zonas urbanas, nubes residuales y píxeles mixtos
pueden confundir el resultado. Diez adquisiciones pueden concentrarse en una
estación; el cribado no corrige automáticamente ese sesgo. Diferente frecuencia
anual **no prueba** migración del cauce. No identifica minería, mercurio ni
contaminación química, ni atribuye causas/responsabilidades o evalúa riesgo.

### Auditoría temporal del inventario (2026-10-01)

El panel **¿Qué fechas estamos comparando?** deriva su calendario exclusivamente
de los pares `scene_ids` / `acquired_ms` del recibo verificado. Usa UTC, conserva
todos los productos e identifica grupos con igual fecha/hora de adquisición
en el ID y tesela MGRS, pero distinto procesamiento. No deduce nubosidad local,
calidad por píxel ni fechas de cambio a partir de este inventario.

| Muestra | Archivos seleccionados | Días UTC distintos | Meses representados |
| --- | --- | --- | --- |
| 2019 (actual) | 31 | 17 | 11 |
| 2024 | 32 | 13 | 9 |

La muestra original de 2019 incluía dos productos `20190621T153629_*_T17MRU` con distinto
identificador de procesamiento. Son variantes del mismo pase y tesela: no asumir
que aportan información independiente. El exportador original y sus resultados
conservan ambos en el historial. La muestra actual fue exportada y recalculada
con una sola variante; no se editó el recibo antiguo para simular ese cálculo.
La contribución efectiva de cada variante a cada píxel no se conoce a partir
del inventario global. El mínimo de 10 describe entradas válidas de la muestra,
no diez pases o días independientes. El panel y las fichas lo advierten.

La regla reproducible de deduplicación por adquisición/tesela está documentada
más abajo; se generaron RGB/conteos/recibos emparejados. No editar solo la lista del manifiesto: sería
una procedencia falsa para los archivos existentes. La comparación actual es
exploratoria, no un análisis estacional validado. Cero en un mes significa
ausencia en la muestra acotada, no ausencia de adquisiciones de Sentinel-2.

El calendario abre los identificadores de cada mes; el manifiesto completo
se puede descargar como JSON. No son fotografías individuales disponibles
en este visor. Véase la [descripción oficial de los identificadores y gránulos](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED).

Para revisar cada celda: comprobar escenas originales y fechas, comparar
estaciones iguales, revisar QA y contexto hidrológico, contrastar con campo
y fuentes independientes. Mantener `status: unreviewed` hasta revisión
explícita. Ausencia de marcador no significa ausencia de cambios/actividades.

## Reproducir y publicar

1. Ejecutar `scripts/export_napo_rivers_gee.js`. Si no devuelve exactamente
   una entidad Napo o falla la consulta de adquisiciones, no se crean tareas.
   `exportMode = 'water-counts'` crea solo conteos y recibo; para reproducir
   las imágenes, elegir `'rgb'` en una ejecución separada. No repetir las
   exportaciones que ya estén descargadas/verificadas.
2. Descargar **todos** los chunks GeoTIFF de cada producto y su recibo a
   `data/raw/rivers/` (ignorada por Git). Los candidatos se generan en Python,
   no mediante vectorización en Earth Engine.
3. Dependencias: `requirements-dev.txt` y `requirements-landcover.txt`.
4. Ejecutar:

```powershell
$riverChunks = Get-ChildItem -LiteralPath 'data/raw/rivers' -Filter 'napo_block7_rgb10_2019_2024*.tif'
python scripts/build_napo_rivers.py --inputs $riverChunks.FullName --receipt data/raw/rivers/napo_block7_rgb10_2019_2024_receipt.geojson
$napoCountChunks = Get-ChildItem -LiteralPath 'data/raw/rivers' -Filter 'napo_block7_water_counts_2019_2024-*.tif'
python scripts/build_napo_river_changes.py --inputs $napoCountChunks.FullName --receipt data/raw/rivers/napo_block7_water_counts_2019_2024_receipt.geojson
pnpm run check:rivers
python -m unittest discover -s tests
```

Si solo terminó RGB, no ejecutar el procesador de cambios: se habilitan las imágenes reales,
pero `candidate_status: pending`, `candidate_count: null` y marcadores deshabilitados.
Esto no equivale a una colección vacía observada ni a ausencia de cambios.

El procesador rechaza muestras a 30 m, bandas desconocidas, chunks faltantes
que dejan sin cobertura el bloque dentro de Napo (GEE puede omitir un chunk
completamente exterior al límite mediante `skipEmptyTiles`),
recibos incompatibles y alfa no binario/no común. Produce teselas RGBA de
512 px WebP **sin pérdida**, niveles 8–13. Leaflet usa `zoomOffset=-1`, zoom
nativo máximo 14 (aprox. 9,55 m/px aquí): el remuestreo nearest a rejilla web
no mejora la resolución del sensor. Más zoom es sobreampliación. Incluye
teselas transparentes del exterior para evitar errores de carga; un hueco
no es agua ni suelo desnudo.

El manifiesto conserva recibo y SHA-256 por chunk, tesela y GeoJSON. La
interfaz carga solo las teselas visibles, compara años en la misma posición
y retira la capa si falla una tesela. Marcadores opcionales y leyenda reactiva.
RGB byte es una visualización, **no** una API de reflectancia o valores NDWI.

`screening` conserva el recibo de conteos, SHA-256 de inputs y procesador,
apoyo comparable y método. El procesador verifica la integridad del RGB,
escenas coincidentes, conteos coherentes, cuadrícula nativa, cobertura de
chunks y límites antes de actualizar candidatos/manifiesto; no modifica
las teselas existentes. Una discrepancia del área provincial ≤1 m² se tolera
solo por redondeo de la reducción de Earth Engine, con geometría exactamente
igual. En una interrupción durante publicación, SHA-256 impide mostrar una
colección que no corresponda al manifiesto.

## Reproducir la depuración sin sobrescribir el actual

La receta se genera inicialmente como **planificada**: preparar archivos por
sí solo no ejecuta ni valida nada en Earth Engine. La ejecución real y los
resultados integrados están documentados arriba. Para reproducir la receta:

```powershell
node scripts/prepare_napo_river_sample.mjs
```

Genera, exclusivamente en `tmp/rivers-next/` (ignorado por Git):

- `scene-plan.json`: inventario, decisiones de conservación/descarte y SHA-256
  del manifiesto original; sin nuevas escenas ni relleno del cupo trimestral.
- `napo-config-next.json`: configuración de la muestra depurada, inicialmente
  separada del lote original y ahora coincidente con el conjunto integrado.
- `export_napo_rivers_pinned_gee.js`: script generado con IDs fijos y modo
  `audit` por defecto. No crea tareas de exportación en ese modo. Sí consulta
  metadatos y la unión con QA si se ejecuta en GEE; no presumir coste nulo.

La regla agrupa por fecha/hora de adquisición del ID + tesela MGRS y conserva
el mayor segundo componente del ID (fecha/hora de generación del proveedor).
Es una decisión reproducible, **no una prueba de mejor calidad**. Conserva
`20190621T153629_20190621T154333_T17MRU` y descarta
`20190621T153629_20190621T153627_T17MRU` en el lote depurado. El total
pasa a **31/32 archivos**, manteniendo 17/13 días distintos. Esto no equilibra
estaciones, niveles del río o apoyo por píxel. La ejecución real recalculó
los candidatos y obtuvo los mismos 24, como documenta la comparación.

`node scripts/prepare_napo_river_sample.mjs --check` verifica la receta local
sin escribir. Si el template, bytes del manifiesto o archivos de staging
cambian, el preparador no adapta/sobrescribe silenciosamente. Las pruebas con
simulación local del cliente comprueban cero tareas en `audit`, selección,
fechas y bloque; **no sustituyen una ejecución real de GEE**.

El procesamiento se realizó en este orden (no hace falta repetirlo para
publicar los archivos actuales; una repetición consumiría nueva cuota):

1. Copiar el script generado al Code Editor y ejecutarlo con `exportMode =
   'audit'`. Comprobar que los IDs, fechas, unión con QA y bloque coinciden.
   Ante un ID/QA faltante o cambiado, se detiene: no se sustituye por otro.
2. Revisar variantes, cuota y calidad antes de cambiar explícitamente el modo
   a `rgb`. Exportar solo ese bloque y descargar RGB + su recibo.
3. Usar exactamente la misma receta con `water-counts`; descargar conteos +
   su recibo. Los prefijos llevan `_dedup_<hash>` y no se confunden con el lote
   original. No lanzar todos los bloques ni exportar ambas recetas a ciegas.
4. Construir ambos productos **en staging**, con los parámetros nuevos
   `--config` y `--output-root`; no reemplazar el atlas todavía. Ejemplo, con
   nombres ilustrativos que deben sustituirse por las descargas reales:

```powershell
python scripts/build_napo_rivers.py --inputs data/raw/rivers/NUEVO_RGB.tif --receipt data/raw/rivers/NUEVO_RGB_receipt.geojson --config tmp/rivers-next/napo-config-next.json --output-root tmp/rivers-next/rebuilt
python scripts/build_napo_river_changes.py --inputs data/raw/rivers/NUEVOS_CONTEOS.tif --receipt data/raw/rivers/NUEVOS_CONTEOS_receipt.geojson --config tmp/rivers-next/napo-config-next.json --output-root tmp/rivers-next/rebuilt
node scripts/validate-rivers.mjs --root tmp/rivers-next/rebuilt
```

Si hay varios chunks, incluir **todos** después de `--inputs`; los nombres
`NUEVO_*` no son archivos existentes. Los CLI impiden construir la muestra
fija directamente en la raíz publicada. RGB/conteos deben coincidir con la
lista fija del plan y entre sí; el validador rechaza variantes por pase/tesela.
No mezclar conteos depurados con el RGB antiguo. Tras validación, revisar el
cambio de apoyo observacional y candidatos respecto al lote anterior; la
integración técnica no equivale a validación científica ni revisión de campo.

Para verificar/comparar el lote reconstruido sin modificar el atlas:

```powershell
node scripts/promote_napo_river_sample.mjs
```

Solo después de esa comprobación, `--apply` preserva el lote anterior,
archiva procedencia/comparación y copia el conjunto emparejado con el manifiesto
al final. Se rechaza otro manifiesto de origen, método, bloque o adquisición;
no se borran imágenes antiguas ni se ejecuta Git. La receta original continúa
reproduciéndose desde el archivo histórico tras la integración.

La regla del ID se fundamenta en la [descripción oficial de Sentinel-2 en
Earth Engine](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED).
La carga fija usa [ImageCollection.fromImages](https://developers.google.com/earth-engine/apidocs/ee-imagecollection-fromimages).

## Navegar y compartir una celda, sin certificarla

En los controles del visor, **Recorrer celdas candidatas** permite seleccionar
una celda o avanzar con Anterior/Siguiente. La lista ordena la suma aproximada
de señal de aumento y disminución; no clasifica riesgo, gravedad o confianza.
La selección activa los marcadores y acerca el contorno de 1 km al límite
de visualización nativo. El centro no identifica un río ni localiza cada
píxel de cambio. Los extremos de la lista vuelven al inicio/final.

**Compartir**, en la cabecera, conserva `view=rivers`, año, corte y `cell`.
Al abrir el enlace, la celda se acepta solo si existe en la colección cuyo
SHA-256 y procedencia se verificaron. Un ID desconocido se descarta. Desactivar
los marcadores elimina la selección del enlace y la leyenda correspondiente.
Se comparte una vista, no una revisión científica ni un dictamen.

**Antes de sacar conclusiones** recuerda revisar ambas vistas, escenas
fechadas, QA, nivel del agua y estacionalidad, y contrastar otro sensor o
evidencia de campo. Los RGB son medianas de una muestra anual: no pueden
establecer por sí solos cuándo ocurrió una modificación. Este protocolo es
orientativo; recorrer celdas no modifica el estado `unreviewed`. No se han
añadido nuevas adquisiciones ni resultados de validación mediante esta interfaz.

## Lo más útil después en Earth Engine

| Prioridad | Producto | Utilidad y límite |
| --- | --- | --- |
| 1 | Escenas Sentinel-2 fechadas, series estacionales | Orillas y bancos a 10 m; revisar fecha/QA y nivel del agua antes de medir desplazamientos. |
| 2 | Persistencia de agua + Sentinel-1 | Radar complementario en zonas nubladas; comparar misma órbita/polarización y controlar sombra del relieve. No es foto óptica ni inundación confirmada. |
| 3 | Historia JRC de agua 1984–2021 | Contexto Landsat a 30 m; no mejora el detalle de Sentinel-2 ni alcanza 2024 en v1.4. |
| 4 | Lluvia CHIRPS por cuenca | Contexto húmedo/seco, aproximadamente 5,6 km; no lluvia en cada tramo a 10 m ni caudal. |
| 5 | Terreno y drenajes con DEM | Pendientes y cuencas; no cartografía automáticamente inundaciones, pequeños escarpes o riesgo local. |

Priorizar validar observaciones y documentar incertidumbre, no decenas de
índices sin una pregunta. Para minería: evidencia regional documentada,
revisión visual fechada y campo; no convertir una señal en una acusación.

## Fuentes y atribución

- [Sentinel-2 SR harmonized, bandas y condiciones](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED).
- [Cloud Score+](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_CLOUD_SCORE_PLUS_V1_S2_HARMONIZED).
- [geoBoundaries ADM1 v6, CC BY 4.0](https://developers.google.com/earth-engine/datasets/catalog/WM_geoLab_geoBoundaries_600_ADM1).
- McFeeters, S. K. (1996). *The use of the Normalized Difference Water Index
  (NDWI) in the delineation of open water features*. International Journal of
  Remote Sensing, 17(7), 1425–1432. [DOI:10.1080/01431169608948714](https://doi.org/10.1080/01431169608948714).
  Referencia de la fórmula, no validación de umbrales del atlas.
- [Exportación, proyección y alineación](https://developers.google.com/earth-engine/guides/exporting_images).
- [Suma de observaciones por banda en Earth Engine](https://developers.google.com/earth-engine/apidocs/ee-imagecollection-sum).
- [Componentes y conectividad en SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.label.html).
- [Cuota de niveles no comerciales](https://developers.google.com/earth-engine/guides/noncommercial_tiers):
  Community ofrece 150 horas EECU mensuales. El nivel y saldo efectivo del
  proyecto deben comprobarse; este documento no certifica cuota restante.
- [Sentinel-1 GRD](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD),
  [JRC agua v1.4](https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_GlobalSurfaceWater),
  [CHIRPS diario](https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY):
  propuestas complementarias, no nuevos productos verificados de este análisis.

**Modified Copernicus Sentinel data (2019, 2024)**; QA Cloud Score+ por Google,
CC BY 4.0; límite geoBoundaries v6, CC BY 4.0. Los productos no pasan a MIT
por estar dentro del repositorio.
