# Ecuador Vivo · piloto de evidencia satelital de parcelas

Estado vigente (18 de octubre de 2026): flujo técnico del piloto local implementado
y ejecutado hasta informe/paquete verificable. No es servicio de certificación,
plataforma pública ni detector de deforestación validado.

## Entrega vigente: expediente técnico local

### Parcelas ecuatorianas recuperadas y persistencia experimental

Se encontró documentación parcelaria más concreta: ReforesTree publica seis sitios
agroforestales ecuatorianos con inventarios GPS/especies/años de plantación, límites
de estudio y dron2020 a2cm/px. DatasetCCBY4.0 https://zenodo.org/records/6813783 ;
paperrevisado https://arxiv.org/html/2201.11192v2 . El ZIPpublicado mide7.514.326.095
bytes; no se descargó entero. `reforestree_reference.py` leyó su índice ZIP64 y
miembros pequeños por rangosHTTP206 estrictos con presupuesto8MB. Se recuperó
`field_data.csv` y SHP/DBF/SHX/PRJ; CRCpor miembro verificado, no MD5delZIPcompleto.

Expediente privado: `_local/parcelas/referencias/reforestree-6813783/`.
Solo891.379bytes retenidos. `parcelas-estudio.geojson` contiene seis geometrías
derivadas, áreas0,3976–0,5297ha; inventario asociado a seis sitios por presencia de
puntos dentro del polígono. Dos geometrías originales válidas; cuatro presentan
autointersecciones y sus derivados make_valid quedan marcados para revisión.
Se eliminó ZparaGeoJSON2D, manteniendo originales. No se afirma validez catastral.
La revisiónv2 del paper corrige desalineación dron/campo, así que hay que revisar
sus datos corregidos antes de coregistro subpíxel. No se han descargado ni
interpretado los ortomosaicos. Los años de plantación de individuos no prueban
la cobertura anterior ni fecha de deforestación.

Otra fuente verificada: ElDeseo/Yaguachi documenta15SAF,12establecidos2016 y3en2017,
total11,8873ha; no se recuperaron sus polígonos digitales y no se transfirió esa
historia a los sitios ReforesTree. Fuente:
https://centrosuragraria.com/index.php/revista/article/download/209/423?inline=1 .

Se ejecutó `persistence.py` sin nuevas descargas sobre seis imágenes radar
ecuatorianas. Mediana lineal VHde tresfechas2020 y descenso>=3dB en las tres2022;
ambasépocas abarcan>=60días, máscarasválidas y mismaórbita. Se obtuvieron34centros
y27polígonos candidatos, guardados en `ecuador-2435/persistencia-experimental/`.
Es umbral heurístico explícito no calibrado, no se informa exactitud, hectáreas
deforestadas ni decisión EUDR. Persistencia en observaciones no prueba continuidad
entre fechas ni bosque inicial. Puede responder a humedad/manejo/speckle/terreno.
52pruebas focalizadas, compilación y comprobación Git correctas.

### Búsqueda de validación independiente (continuación)

Se recuperó y auditó el conjunto de VALIDACIÓN WRI/Google DeepMind, Zenodo
15224684 v3 (CC BY 4.0), 438.143 bytes, MD5 publicado
`bc804d30187986108e17cbbf75b9082f` coincidente. No se descargó su mapa automático
ni el entrenamiento. De 3.574 registros, 12 centros caen en la geometría
geoBoundaries Ecuador ya incluida. Salida y atribución:
`_local/parcelas/validacion/referencias-wri-ecuador/AUDITORIA.md`,
`candidatos-ecuador.geojson`, `auditoria.json` y CSV original.

Su independencia respecto a nuestro flujo radar es útil para buscar casos,
pero la unidad de interpretación es aproximadamente 1 km y el motor de pérdida
se asigna a 2001–2022 agregado. No hay perímetro de finca ni fecha precisa del
evento. No se inventaron polígonos alrededor de esos puntos ni se llamó a esas
etiquetas validación de nuestro detector. También se evaluaron las descripciones
primarias de ReforesTree (biomasa, no trayectoria histórica) y MapBiomas Ecuador
(mapa clasificado, no referencia independiente para medir exactitud por sí solo).

Se implementó `tools/parcelas/reference_gate.py` con criterios explícitos de
aceptación: interpretación humana, independencia, perímetro y fecha verificados.
Cuatro pruebas impiden que etiqueta automática, campos desconocidos o referencia
incompleta se acepten; incluso una referencia completa no produce decisión EUDR.
42 pruebas focalizadas pasan. Falta referencia temporal parcelaria independiente
para validar científicamente; este límite no se ha declarado resuelto.

Entrada única: `tools/parcelas/completar-piloto.ps1`. Su opción `-SoloInforme`
verifica sin red los resultados guardados. No modifica SIG/Studio/Recursos.

Entrega privada canónica:
`_local/parcelas/piloto-352/expediente/resultado/INFORME.md`.
Incluye mapas, gráfico temporal, `serie.csv`, geometría pública,
`evidencia.json` y `huellas.json`. Paquete portable:
`_local/parcelas/piloto-352/expediente/ecuador-vivo-piloto-352.zip`.
El ZIP conserva además catálogos, plan, solicitudes y respuestas originales, sin
credenciales. Integridad de archivos, fuentes y ZIP comprobada offline.

Resultados reales: 221 escenas radar catalogadas entre enero de 2020 y marzo de
2025; selección determinista de una adquisición por trimestre más cuatro previas,
25 fechas finales, mismo Sentinel-1A/IW/órbita45/ascendente/VV-VH.
Cada ID devuelto por el servicio coincide con el producto seleccionado, la fecha
y una huella de escena que cubre el polígono. Misma grilla 20 m, 124 centros
comunes válidos con nodata/sombra/valores inválidos excluidos. Mayor intervalo:
96 días (antes había 1.524 días). No es observación continua ni se interpolan datos.

21 descargas nuevas, 1.112.576 bytes; cuatro reutilizadas, sin duplicarlas.
ZIP final 1.716.701 bytes. Límites: 28 fechas, respuesta 5 MB, lote secuencial,
sin reintentos, token solo en memoria reutilizado dentro de su validez.
La credencial está cifrada con DPAPI fuera del repositorio y vence el 26 de octubre.
38 pruebas focalizadas, compilación, sintaxis PowerShell y ejecución integral
real. Figuras revisadas visualmente. No se probó toda la aplicación Studio.

La conclusión emitida es deliberadamente **evidencia insuficiente para concluir
deforestación**. No es fallo del flujo: no existe historia independiente de cambios
para esta referencia y la señal radar por sí sola no certifica cobertura ni uso.
La porción de cacao está documentada en 2025, no su establecimiento en 2020.
La revisión humana permanece pendiente. No hay publicación, backend público,
validación Ecuador, detector científico ni dictamen EUDR. Esos elementos no se
marcan terminados por haber completado el piloto técnico.

Los apartados siguientes conservan el historial metodológico; las salidas llamadas
«vigentes» dentro de hitos anteriores son diagnósticos de aquel momento, no la
entrega actual de este encabezado. No mezclar la grilla Browser con la API.

## Objetivo y alcance

Producir un expediente técnico reproducible de UNA parcela real, mediante
procesamiento local y revisión humana. Comparar su historia conocida con
observaciones Sentinel-1 y, cuando existan observaciones válidas, Sentinel-2.
No desarrollar todavía una plataforma pública automática, pagos ni cuentas.
No modificar el SIG, Studio, Recursos ni los proyectos guardados en esta etapa.

El punto GPS sirve para localizar: el análisis requiere un perímetro Polygon o
MultiPolygon válido en GeoJSON WGS84, con orden longitud/latitud. La precisión
del GPS del teléfono debe registrarse cuando esté disponible; no se interpreta
como levantamiento catastral. No inferir límites a partir de un punto.

## Base existente e inspección

- Repositorio único: el directorio actual de Ecuador Vivo.
- SNAP localizado en `C:/Program Files/esa-snap/bin/gpt.exe`.
- SNAP 13.0.0: `gpt -h` terminó con código 0 y mostró el inventario de operadores.
  Esto confirma arranque del motor, no procesamiento SAR con escenas reales.
- Existen scripts `build_napo_landcover.py` y `build_napo_spectral.py` con controles
  de procedencia, máscaras y grillas. Son antecedentes, no un analizador de fincas
  ni evidencia de validación para cacao. Evaluar reutilización sin alterarlos.
- La web pública es estática: no puede ejecutar SNAP en el teléfono o GitHub Pages.

## Contrato del primer expediente

Entrada: polígono autorizado, identificador no personal, cultivo declarado
(no detectado automáticamente), historia conocida y ventanas temporales acordadas.
La comparación alrededor del 31 de diciembre de 2020 debe incluir contexto
anterior y posterior; no reemplazarlo por una comparación arbitraria de dos días.

Salida local: geometría validada, inventario de escenas y controles de calidad,
receta y versión del procesamiento, mapas con leyendas, serie temporal, borrador
de informe y registro explícito de revisión. Resultados iniciales: pendiente de
revisión o evidencia insuficiente. No emitir «cumple EUDR», «sin deforestación»
ni hectáreas deforestadas a partir de un umbral no validado.

## Controles científicos

- Registrar producto, adquisición, órbita relativa, dirección, modo, polarización,
  unidades, CRS, resolución efectiva, máscara y versiones de herramientas.
- Seleccionar series radar compatibles; no mezclar órbitas como si fueran iguales.
- Distinguir amplitud, potencia lineal y dB; no recalibrar productos ya calibrados.
- Diseñar y verificar el grafo SNAP según el producto real y el relieve. La
  corrección geométrica no equivale a normalización radiométrica del terreno.
- Documentar speckle, sombras, layover y cambios de humedad como fuentes de error.
- En óptico conservar nubes, sombras y NoData como inválidos; calibrar por metadatos.
- Calcular áreas y comparaciones sobre grillas y máscaras verificadas, nunca PNG.
- Pérdida de cobertura arbórea, cambio de señal y conversión a agricultura son
  conceptos diferentes. El cultivo declarado necesita evidencia independiente.
- No suavizado generativo ni relleno de nubes como evidencia de cambios reales.
- No presentar rendimiento científico hasta validar con historia independiente.

## Organización prevista, sin duplicar el proyecto

- `tools/parcelas/`: futura receta SNAP y herramientas de orquestación local.
- `tests/`: pruebas de entradas, grillas, estados y trazabilidad.
- `_local/parcelas/`: futuros expedientes privados e imágenes; nunca publicación
  ni subida automática de coordenadas o datos del productor.
- Este documento conserva alcance, límites y criterios de aceptación.

No crear estas herramientas ni descargar escenas hasta aprobar el alcance y
seleccionar la parcela. Primero un proceso secuencial con límites de memoria,
espacio, tiempo y tamaño de entrada; nada de lotes nacionales ni paralelismo libre.

## Estilo y pruebas

Python con funciones pequeñas, rutas explícitas, argumentos sin shell interpolado,
errores claros y salidas que no sobrescriban originales. Ejemplo de contrato:
`validate_parcel(feature)` rechaza geometría inválida antes de buscar escenas.
Las pruebas usarán `unittest`, archivos temporales y fixtures sintéticas marcadas
como tales. Una prueba sintética no valida detección de deforestación.

Comandos de comprobación inicial (PowerShell, sin procesar imágenes):

```powershell
Get-Command gpt -ErrorAction SilentlyContinue
& 'C:/Program Files/esa-snap/bin/gpt.exe' -h
git diff --check
```

Los comandos de análisis y pruebas específicas se documentarán cuando existan;
no presentar comandos de herramientas aún no implementadas como funcionales.

## Criterios de aceptación del piloto

1. SNAP inicia y los operadores necesarios están disponibles, con versión registrada.
2. Se recibe una parcela real autorizada y su historia independiente.
3. Se descubren escenas reales pertinentes y se informa cualquier falta de cobertura.
4. El procesamiento termina dentro de límites medidos y preserva trazabilidad.
5. El expediente permite verificar fechas, máscaras, leyendas y procedencia.
6. El borrador distingue observación, interpretación y limitación; requiere revisión.
7. Se registran tiempo, almacenamiento y discrepancias con la historia conocida.

## Límites y decisión pendiente

Siempre: conservar fuentes originales y documentar incertidumbre.
Consultar antes: servicios facturables, nuevas dependencias pesadas, descargas
grandes, publicación y transmisión de datos de una parcela a terceros.
Nunca: credenciales en código, certificación automática ni borrado de datos ajenos.
Falta seleccionar una geometría de referencia con limitaciones explícitas.

## Selección de referencias públicas · 18 de octubre

Fuente prioritaria para una prueba técnica de cultivo conocido: CERSGIS,
Reference Dataset for Land Use Change Mapping in Ghana's Cocoa Landscape
(2024–2025), v2.0, DOI 10.5281/zenodo.16579443, licencia CC BY 4.0.
Contribuyen WRI, NASA SERVIR SCO y UAH. Recopilación septiembre de 2024 a marzo
de 2025. La ficha declara 21.031 polígonos de cacao y distingue un subconjunto
homogéneo. Archivo publicado: 30.810.529 bytes,
MD5 `cc2046b7d3e2035a39baf5f8b9952748`.

Advertencia expresa del proveedor: estos polígonos representan PORCIONES de
cultivos; no son linderos de propiedad ni deben usarse para cumplimiento legal.
El cultivo observado en 2024–2025 no prueba uso agrícola anterior a 2021.
Por tanto, esta fuente permite ensayar el flujo en una geometría real y una
clase documentada, NO validar ausencia de deforestación ni cumplimiento EUDR.
Una prueba en Ghana tampoco acredita precisión en Ecuador.

Referencia ecuatoriana candidata: estudio de sistemas agroforestales de cacao
de El Deseo, Yaguachi, que documenta establecimiento en 2016–2017. En la fuente
consultada no se ha recuperado todavía un perímetro digital inequívoco. No
dibujar una finca aproximada y presentarla como georreferenciación del estudio.
La publicación lleva licencia BY-NC-SA: revisar permisos antes de incorporar
material a un servicio comercial. No se han contactado autores ni productores.

Fuentes:
- https://zenodo.org/records/16579443
- https://centrosuragraria.com/index.php/revista/article/download/209/423?inline=1
- https://redi.cedia.edu.ec/document/74717

No se utilizarán cuadrados ilustrativos de ejemplos de software como parcelas
verificadas, ni clasificaciones de otro modelo como verdad de terreno independiente.

### Geometría seleccionada para el ensayo técnico

Se descargó únicamente el ZIP de referencia (30,8 MB); la huella MD5 coincide
con la publicada. Se inspeccionó el GeoJSON dentro del ZIP sin descomprimir
el conjunto completo ni utilizar las encuestas socioeconómicas.
Los 21.031 registros del GeoJSON coinciden con el inventario de la versión v2.

Selección reproducible, previa a observar resultados satelitales: primer registro
por OBJECT_ID ascendente con geometría válida, una sola parte y área geodésica
entre 3 y 10 ha. Resultado: OBJECT_ID 352, Asunafo North, Ahafo, Ghana; fecha
de referencia marzo de 2025; cacao con árboles de sombra según atributos fuente.
Área geodésica WGS84 calculada: 5,0017304 ha; no es área catastral de una finca.

Se guardó una copia de su geometría original con atributos mínimos y atribución
en `_local/parcelas/referencias/cersgis-16579443/parcela-piloto.geojson`.
El código fuente declara CRS84 (longitud/latitud). Se verificó validez geométrica
con Shapely y área elipsoidal con PyProj. La fecha de referencia no se confunde
con una fecha de plantación; no se ha interpretado el campo ambiguo Replant_Fr.

Inventarios reales consultados y guardados; receta SNAP diagnóstica preparada
como borrador. NO se han procesado imágenes, detectado cambios ni calculado
exactitud científica.

### Checkpoint de implementación · 18 de octubre de 2026

Se añadió `tools/parcelas/catalog.py`: valida un polígono, limita consultas al
catálogo STAC público CDSE, conserva los metadatos y registra truncamiento de
paginación. No instala dependencias ni descarga imágenes. Se utiliza el Python
existente de `_local/video-studio/.venv/`. Documentación ejecutable en
`tools/parcelas/README.md`; nueve pruebas offline en `tests/test_parcel_catalog.py`.
Todas pasaron; se verificaron compilación Python y formato XML. No se ejecutó
la suite completa de Studio: sus archivos y rutas no se modificaron.

Resultados de consultas completas, sin paginación truncada:

| Ventana (fin exclusivo) | Sentinel-1 GRD | Sentinel-2 L2A |
|---|---:|---:|
| 2020-10-01 / 2021-02-01 | 20 | 25 |
| 2025-03-01 / 2025-04-01 | 2 | 8 |

Carpetas privadas: `_local/parcelas/piloto-352/catalogo-corte2020/` y
`_local/parcelas/piloto-352/catalogo-202503/`. Cada una conserva
`catalog-summary.json` y `catalog-items.geojson`. Radar: IW, ascendente,
órbita relativa 45, VH+VV. Agrupación por metadatos no garantiza todavía
equivalencia radiométrica. Las escenas 2025 encontradas son SAFE COG;
se debe comprobar compatibilidad de lectura de SNAP 13 antes de descargarlas.

`tools/parcelas/sentinel1-grd-diagnostic.xml` contiene ocho nodos diagnósticos:
lectura, órbita, ruido de borde, ruido térmico, calibración, recorte con contexto,
corrección geométrica del terreno y escritura. La ayuda del operador
Terrain-Correction respondió; XML bien formado NO implica grafo científicamente
validado ni ejecutado. No aplica terrain flattening ni speckle. No comparar sus
salidas como deforestación. Usar fuente GRD original, nunca recalibrar RTC.

Próxima acción segura: inspeccionar acceso y tamaño de los productos seleccionados,
verificar lector SAFE COG y todos los parámetros del grafo. Después acordar
descarga acotada de un producto, DEM/órbita necesarios, medir RAM/tiempo y
comprobar máscaras/unidades. La parcela sigue sin historia de deforestación
verificada: no convertir el ensayo de procesamiento en informe EUDR.

No hay interfaz pública nueva, publicación, commit ni push. El código nuevo es
aditivo; SIG, Studio, Recursos, videos y proyectos guardados siguen intactos.

### Continuación · diagnóstico real de acceso y calidad

`tools/parcelas/preflight.py` comprobó ayuda de los ocho operadores del SNAP
instalado: código 0 y todos los nombres de parámetros presentes. Solo nombres,
NO valores ni ejecución SAR. Evidencia en `_local/parcelas/piloto-352/preflight-snap13/`.
El manifest oficial de la escena del 20 de marzo devuelve HTTP 401 sin credenciales.
No se intentó evadir autenticación ni buscar credenciales guardadas.

`tools/parcelas/optical_quality.py` leyó ventanas reales de SCL por acceso parcial
a COG públicos, con límites de ventana y caché. Dos escenas, ambas en EPSG:32630,
resolución SCL nativa 20 m, 124 centros de píxel dentro del polígono:
- 19 marzo 2025: 124 clasificados como sombra de nube (SCL 3).
- 9 marzo 2025: 12 en SCL 8 y 112 en SCL 9 (nubes).
Fracción despejada definida como SCL 4/5/6: 0 % en ambas. No se calcula NDVI.
No son observaciones de campo de nubosidad; son etiquetas del algoritmo SCL.
La selección examinó solo dos candidatos de la primera página Earth Search,
con paginación adicional presente: no concluir que todo marzo es inutilizable.

Se guardaron recortes GeoTIFF, procedencia y conteos en
`_local/parcelas/piloto-352/calidad-optica-202503/`. Resumen humano:
`_local/parcelas/piloto-352/INFORME-PRELIMINAR.md` (diagnóstico, no informe EUDR).
Quince pruebas focalizadas aprobadas, compilación Python correcta. No se ejecutó
la suite completa del producto; no se cambiaron sus componentes existentes.

Límite siguiente: obtener acceso legítimo a un producto original radar para
probar el lector y la receta. Puede ser cuenta CDSE gratuita con autenticación
local segura o un archivo GRD SAFE ya disponible. No solicitar contraseñas por
chat. No actualizar SNAP automáticamente: la compatibilidad COG sigue sin probar.

### Cuenta CDSE y primer recorte radar real · 18 octubre 2026

El usuario proporcionó su pestaña del navegador integrado con sesión iniciada.
Se comprobó la sesión en Copernicus Browser y se visualizó Sentinel-1 IW VV+VH
el 20 de marzo de 2025, centrado en el área pública del piloto.
No se extrajeron cookies, tokens ni contraseñas; no se crearon credenciales.

Exportación Analytical por interfaz oficial: TIFF Float32, bandas Raw VV y VH,
dataMask incluida, UTM 30N, espaciado solicitado 20 m. ZIP de solo 84.035 bytes
recuperado en Downloads y copiado sin borrar el original a:
`_local/parcelas/piloto-352/radar-browser-20250320/Browser_images.zip`.
El primer intento no devolvió ruta al agente; se repitió la exportación pequeña
con captura del evento de descarga. No son dos escenas ni dos observaciones.

Se verificaron dos TIFF, cada uno con dos bandas Float32, 157 filas por 66
columnas, EPSG:32630 y grillas idénticas. Espaciado REAL:
20,1173109848 × 20,0467113185 m (no exactamente 20 m). Dentro de la parcela hay
125 centros de píxel; ambos archivos tienen valores finitos y dataMask=1 allí.
Esto demuestra disponibilidad, no independencia estadística, calidad radiométrica,
ausencia de sombra radar ni identificación de bosque/cacao.

Recibo, SHA256 y límites: `radar-browser-20250320/procedencia.json`.
Los TIFF no incluyen coeficiente de retrodispersión ni configuración completa
de procesamiento en sus etiquetas. La documentación del servicio describe VV/VH
como potencia lineal del coeficiente elegido, pero NO se ha confirmado el
coeficiente de esta exportación particular. Falta inspeccionar opciones avanzadas
y asegurar procedencia antes de comparar fechas. No recalibrar estos recortes
con el grafo SNAP para GRD original. La ejecución SNAP sigue pendiente y es una
ruta distinta a la exportación procesada del navegador.

Documentación de unidades/procesamiento:
https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S1GRD.html

### Par radar con ajustes explícitos · continuación

Se fijaron en el explorador gamma0 terreno (GAMMA0_TERRAIN), ortorrectificación
con COPERNICUS_30, filtro speckle NONE y upsampling NEAREST. Se exportaron
nuevos recortes numéricos Raw VV/VH + dataMask, Float32, UTM30N, de los días
8 y 20 de marzo de 2025. Ajustes observados en UI/URL, sin extraer credenciales.
No se reutilizó el primer recorte de ajustes desconocidos.

ZIP privados (cada uno unos 85 KB):
- `radar-rtc-explicito-20250308/Browser_images.zip`
- `radar-rtc-explicito-20250320/Browser_images.zip`

Manifiesto de procesamiento y huellas: `radar-pair-manifest.json`, dentro del
expediente local. Comparación reproducible mediante `tools/parcelas/radar_pair.py`.
Grillas exactamente iguales entre ambas fechas y polarizaciones, 125 centros
comunes válidos (dataMask=1 y potencia positiva finita). Resultado:
VV −0,192198 dB; VH −0,164921 dB, calculados como 10 log10 de la razón entre
medias en potencia lineal. Son estadísticas del par, no cambios de cobertura,
no significación estadística y no garantía de estabilidad del cultivo.

Salida: `_local/parcelas/piloto-352/comparacion-radar-20250308-20250320/INFORME.md`
y `radar-pair.json`. Diecinueve pruebas focalizadas aprobadas. Sin ejecución
SNAP ni despliegue público. Solo se implementaron herramientas locales aditivas.

Próximo incremento: ampliar a varias fechas antes/después de 2020 con el mismo
contrato, verificar linaje de escenas y geometría de adquisición y registrar
calidad terreno (dataMask no sustituye shadow/layover). Preparar línea base y
validación independiente antes de diseñar un detector. No comparar sigma0 SNAP
con gamma0 RTC como si fueran la misma magnitud. No afirmar rendimiento en
Ecuador a partir del caso de Ghana ni emitir informe legal con estos polígonos.

### Serie histórica mínima · 23 diciembre 2020 a 20 marzo 2025

Se descargaron dos ZIP adicionales de unos 85 KB por la interfaz oficial, con
la misma configuración explícita gamma0 terreno/DEM30/NONE/NEAREST y exportación
analítica Float32 VV/VH + dataMask, UTM30N y espaciado solicitado 20 m:
`radar-rtc-explicito-20201223/Browser_images.zip` y
`radar-rtc-explicito-20210104/Browser_images.zip` dentro del expediente local.
No se extrajeron credenciales; originales de Downloads conservados.

La herramienta `tools/parcelas/radar_series.py` comprueba huellas y cruza fechas
con los catálogos locales. En cada fecha existe una escena candidata que cubre
el polígono, de Sentinel-1A, IW, ascendente y órbita relativa 45; los ángulos de
incidencia de escena son cercanos a 39,07°. Es comprobación de candidatos,
NO confirmación del linaje píxel a píxel de la exportación ni del ángulo local.

Cuatro fechas y grillas idénticas con 125 centros válidos comunes:

| Fecha | VV: dB de media lineal | VH: dB de media lineal |
|---|---:|---:|
| 2020-12-23 | -6,886 | -13,611 |
| 2021-01-04 | -6,378 | -12,623 |
| 2025-03-08 | -7,011 | -12,791 |
| 2025-03-20 | -7,203 | -12,956 |

Vacío explícito: 1.524 días entre enero de 2021 y marzo de 2025. Sin interpolación,
sin asumir estabilidad durante ese periodo. No hay baseline ni detector validado.
El uso agrícola en 2020 continúa DESCONOCIDO: el cacao está documentado en 2025.

Manifiesto: `_local/parcelas/piloto-352/radar-series-manifest.json`.
Salida vigente de la serie: `serie-radar-historica/INFORME.md` y `radar-series.json`
dentro del mismo expediente. Las salidas de pares son diagnósticos específicos,
no otra versión de la aplicación. Veintitrés pruebas focalizadas aprobadas;
compilación Python y comprobación de espacios Git correctas. Sin publicación.

Siguiente trabajo: cerrar la trazabilidad del servicio y automatizar acceso por
API oficial con autenticación autorizada y segura (no copiar tokens del navegador),
para ampliar la línea temporal sin exportaciones manuales repetitivas. Antes de
interpretar cambios: máscaras de sombra/layover, calidad de terreno, humedad y
comparación con evidencia independiente de cambios conocidos. No confundir el
prototipo estadístico con un servicio listo para emitir informes de conformidad.

## Referencias de método

### Acceso automatizado autorizado — 18 de octubre de 2026

El usuario aprobó explícitamente crear un cliente OAuth temporal. Se verificó en
el panel oficial la confirmación «New OAuth client created Ecuador Vivo — piloto».
Vencimiento seleccionado: 26-10-2026 23:59:59 UTC (el panel indica siete días con
su reloj UTC). Client Credentials; SPA y Never expire desactivados. No se cambió
el plan ni se contrataron servicios.

El usuario guardó la credencial localmente y se verificó OAuth correctamente;
no se transcribió el secreto en código ni documentos. El script
`tools/parcelas/configurar-copernicus.ps1` permite introducirlo de forma oculta,
validar OAuth y guardarlo cifrado mediante DPAPI CurrentUser en LocalAppData,
fuera de OneDrive/Git. No guarda el token, no descarga imágenes ni imprime errores
HTTP que puedan contener datos sensibles. Autenticación real comprobada.

### Process API ejecutada: recortes pequeños, no dictamen

Se implementaron `process_api.py` y `descargar-radar-piloto.ps1`. Este experimento
está restringido a la referencia pública de Ghana y cuatro fechas explícitas;
no es aún una herramienta genérica para cualquier parcela. Usa la credencial DPAPI,
HTTPS, endpoint fijo, sin redirecciones ni reintentos y respuesta acotada a 5 MB.
No guarda tokens ni imprime excepciones HTTP. Las salidas no se sobrescriben.

Cuatro solicitudes reales completadas: 2020-12-23, 2021-01-04, 2025-03-08 y
2025-03-20. Archivos `api-rtc-YYYYMMDD/response.tar`, en total 210.944 bytes.
Grilla fija UTM 30N, 72×62 celdas, paso exacto de 20 m (no exactitud de 20 m).
RTC gamma0 terreno, DEM Copernicus 30, sin speckle, remuestreo vecino más cercano.
Bandas VV/VH en potencia lineal, dataMask, shadowMask y ángulo de incidencia local.
Cada inspección encontró 124 centros dentro del polígono, disponibles y sin
señal de sombra según esta máscara; no son 124 observaciones independientes.
La máscara no descarta todo layover ni otros errores del terreno.

La primera respuesta (2025-03-20) reveló que serializar directamente `scenes` no
conserva sus propiedades de órbita; queda como diagnóstico con trazabilidad
incompleta, NO incorporarla a una serie de procedencia cerrada. Se corrigió a
`scenes.orbits`, siguiendo el ejemplo oficial. Las otras tres respuestas sí
incluyen fecha e identificador Sentinel-1 original del servicio, coincidentes
con los candidatos catalogados previamente. No es una certificación independiente
del procesamiento remoto. No mezclar estas grillas con los ZIP anteriores del
Browser, cuyo paso difiere ligeramente. Las inspecciones quedan en sus carpetas.

Actualización: cuarta fecha completada con metadatos corregidos en
`api-rtc-20250320-trazable` (52.736 bytes, SHA256
`2fc48fe84dc19a674da558dccd13c4f44f805454b0feaf7f85a43b954e0fa68c`).
La respuesta incompleta anterior NO se usa en la serie vigente.

Se ejecutó `tools.parcelas.api_series`: cuatro ID de producto devueltos por el
servicio coinciden exactamente con el catálogo, fecha y cobertura completa de la
parcela. Mismo Sentinel-1A/IW/órbita 45/ascendente/VV-VH, contratos de solicitud
verificados y huellas coincidentes con inspecciones. Grillas fijas iguales y 124
centros válidos comunes tras excluir nodata, sombra y valores no finitos/no positivos.
No es una verificación independiente del procesamiento del proveedor.

Informe vigente: `_local/parcelas/piloto-352/serie-api-trazable/INFORME.md`;
datos/procedencia en `serie.json`. VV/VH dB de media lineal, respectivamente:
23-12-2020 -6,901/-13,534; 04-01-2021 -6,408/-12,714;
08-03-2025 -6,958/-12,903; 20-03-2025 -7,154/-13,000.
Las diferencias frente al diagnóstico Browser anterior reflejan otro soporte/grilla;
no mezclar ambos productos. No se suavizan datos científicos ni se interpolan fechas.

30 pruebas focalizadas aprobadas y ejecución integral de la serie con datos reales.
No se modificó SIG/Studio ni se publicó nada.
Pendiente: ampliar línea
temporal de forma acotada, validar calidad/soporte común y contrastar cambios
con evidencia independiente. El vacío de 1.524 días sigue sin resolverse.

Fuentes de implementación:
https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S1GRD.html
https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Evalscript/resources/metadata_sh_docs.html

Skill de seguridad aplicada: acceso limitado en duración, secreto separado del
repositorio y errores genéricos. La credencial no sustituye los controles científicos
pendientes y su disponibilidad no demuestra validez de un dictamen EUDR.

- SNAP, ejecución oficial de grafos:
  https://step.esa.int/docs/tutorials/SNAP_CommandLine_Tutorial.pdf
- Earth Engine, tratamientos y límites de Sentinel-1:
  https://developers.google.com/earth-engine/guides/sentinel1
- ESA, seguimiento de pérdida forestal mediante series radar:
  https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-1/Using_a_data_cube_to_monitor_forest_loss_in_the_Amazon
