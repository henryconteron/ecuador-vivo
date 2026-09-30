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
  exportar frecuencia/observaciones y calcular componentes/celdas localmente,
  evitando repetir la vectorización costosa en Earth Engine.

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
6. Diferencia absoluta de frecuencia ≥ 0,5 (50 puntos porcentuales), con
   frecuencia ≥ 0,5 en al menos un año.
7. Componentes conectados de al menos 100 píxeles (aprox. 1 ha), ocho vecinos,
   por separado para aumento y disminución.
8. Agrupar en celdas Web Mercator de 1 km y retener las que acumulan ≥ 1 ha
   aproximada de señales. El marcador es el **centro de la celda**, no la
   posición exacta de una ribera ni el nombre de un río.

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

Para revisar cada celda: comprobar escenas originales y fechas, comparar
estaciones iguales, revisar QA y contexto hidrológico, contrastar con campo
y fuentes independientes. Mantener `status: unreviewed` hasta revisión
explícita. Ausencia de marcador no significa ausencia de cambios/actividades.

## Reproducir y publicar

1. Ejecutar `scripts/export_napo_rivers_gee.js`. Si no devuelve exactamente
   una entidad Napo o falla la consulta de adquisiciones, no se crean tareas.
2. Descargar **todos** los chunks GeoTIFF `napo_block7_rgb10_2019_2024*`,
   el recibo y el GeoJSON de candidatos a `data/raw/rivers/` (ignorada por Git).
   Conservar también una colección vacía válida: no inventar puntos.
3. Dependencias: `requirements-dev.txt` y `requirements-landcover.txt`.
4. Ejecutar:

```powershell
$riverChunks = Get-ChildItem -LiteralPath 'data/raw/rivers' -Filter 'napo_block7_rgb10_2019_2024*.tif'
python scripts/build_napo_rivers.py --inputs $riverChunks.FullName --receipt data/raw/rivers/napo_block7_rgb10_2019_2024_receipt.geojson --candidates data/raw/rivers/napo_block7_water_candidates_2019_2024.geojson
pnpm run check:rivers
python -m unittest discover -s tests
```

Si solo terminó RGB, omitir `--candidates`: se habilitan las imágenes reales,
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
