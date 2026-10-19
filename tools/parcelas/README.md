# Piloto local de parcelas · sin modificar el SIG

Estado vigente: flujo técnico local completo y ejecutado para CERSGIS 352 (Ghana).
No es plataforma pública ni detector de deforestación validado. La receta SNAP
original permanece en borrador; el procesamiento real usa la API oficial RTC.
Usa el Python geoespacial ya instalado; no hay dependencias nuevas ni suscripciones.

## Ejecutar todo o revisar el resultado

Checkpoint de cuota: `python -m tools.parcelas.field_cases` prepara exclusivamente
RF05/RF06 (geometrías originales válidas) y consulta metadatos acotados, sin ProcessAPI.
Entrada de continuación: `_local/parcelas/parcelas-campo-ecuador/CONTINUAR-AQUI.md`.
Ya ejecutado: catálogos oct-dic2020/2025, GeoJSON individuales y soporte real por
grilla. Solo3y5celdas20m plenamente contenidas respectivamente: no asumir que
todos los píxeles de borde son observaciones puras de la parcela. 55pruebas pasan.

Parcelas reales documentadas: `python -m tools.parcelas.reforestree_reference`
usa rangos HTTP estrictos (206/Content-Range, máximo8MB total por ejecución),
rechaza descargas completas del ZIP7,5GB y lee solo miembros pequeños permitidos.
Datos retenidos ~0,89MB: inventario y seis polígonos; CRCpor miembro verificado,
NO checksum del archivo completo, que no se ha descargado. No copia ortomosaicos.
Ver `_local/parcelas/referencias/reforestree-6813783/FINCAS-DOCUMENTADAS.md`.
Dos geometrías originales válidas; cuatro reparadas topológicamente con revisión
pendiente. Todos son polígonos de estudio agroforestal, no linderos de propiedad.

Persistencia diagnóstica: `python -m tools.parcelas.persistence` (sin red),
requiere tres observaciones por época y al menos60días de separación dentro
de cada época. Detecta descensos VH repetidos con umbral heurístico3dB, NO tala.
Guarda27polígonos candidatos/34centros en
`_local/parcelas/ecuador-2435/persistencia-experimental/`, para inspección SIG.
No se modificaron proyectos ni se publicaron datos. 52pruebas focalizadas pasan.

Caso Ecuador real, radar y óptico (contexto público, NO finca inventada):

```powershell
& './tools/parcelas/completar-piloto.ps1' -CasoEcuador
& './tools/parcelas/completar-piloto.ps1' -CasoEcuador -SoloInforme
```

Salida: `_local/parcelas/ecuador-2435/resultado/INFORME.md`, `comparacion.png`,
`evidencia.json` y huellas. Se ejecutaron 12 solicitudes reales (867.328 bytes),
seis ópticas y seis radar, con la misma credencial local segura y sin publicar.
Sentinel-2 visible/NIR a 10 m, máscara SCL nativa 20 m; radar RTC a paso 20 m.
No se aumenta artificialmente la resolución con IA. RGB con escala fija solo
visual; datos en reflectancia y potencia lineal. Fuente de ambos sensores verificada
mediante ID devuelto por servicio frente al producto del catálogo seleccionado.
Selección óptica por fracción válida de las tres fechas examinadas de cada época:
10oct2020 58,72%, 5oct2022 100%; radar 5oct2020 y 7oct2022, misma órbita120
ascendente Sentinel-1A, datos válidos 100% según máscaras. Separación 5 y 2 días.
NDVI sobre 5.872 centros comunes; radar sobre 2.500, en grillas independientes.
No restar óptico a radar ni inferir tala de diferencias. 47 pruebas focalizadas pasan.
El área de estudio de 1km×1km NO reconstruye un lindero ni verifica fecha de tala.

Auditoría adicional de referencias: `python -m tools.parcelas.reference_gate`
con el entorno geoespacial ya indicado. Descarga acotada (CSV 438.143 bytes),
MD5 fijado, 3.574 muestras de validación humana; guarda 12 centros ecuatorianos.
No descarga rásteres ni entrenamiento. Ver
`_local/parcelas/validacion/referencias-wri-ecuador/AUDITORIA.md`.
Es selección de casos para revisión, no validación terminada: unidades ~1 km,
periodo agregado 2001–2022, sin perímetros de parcela ni fechas de evento.
La puerta de aceptación `assess_reference` impide tratarlos como tales.
No se calcula precisión del detector ni conformidad EUDR. 42 pruebas pasan.

Desde la raíz del repositorio:

```powershell
& './tools/parcelas/completar-piloto.ps1'
# Sin red ni autenticación, para comprobar el informe ya creado:
& './tools/parcelas/completar-piloto.ps1' -SoloInforme
```

Resultado principal: `_local/parcelas/piloto-352/expediente/resultado/INFORME.md`.
Paquete portable: `expediente/ecuador-vivo-piloto-352.zip`, dentro del mismo piloto.
Incluye informe, dos figuras, CSV, geometría, procedencia, huellas, catálogos y
los 25 recortes/solicitudes seleccionados. No contiene credenciales ni tokens.
Todo permanece local e ignorado por Git.

La ejecución descubrió 221 escenas radar entre enero de 2020 y marzo de 2025,
seleccionó una por trimestre (más cuatro fechas previas) y verificó 25 fechas:
misma plataforma/mode/órbita/dirección, grilla exacta y fuente de servicio frente
al catálogo. 124 centros válidos comunes; mayor intervalo 96 días.
Selección previa a examinar valores; muestreo, no vigilancia continua.
No interpolación, no umbral de tala, no NDVI sobre nubes ni declaración EUDR.

Se ejecutaron 21 solicitudes nuevas (1.112.576 bytes), reutilizando cuatro recortes.
ZIP final 1.716.701 bytes. Máximo 28 observaciones, 5 MB por respuesta, procesamiento
secuencial, sin reintentos automáticos. El token se reutiliza hasta su vencimiento
durante el lote; no se almacena. Si caduca, detener y reanudar conserva el caché.
No volver a descargar archivos existentes. Las huellas y CRC del paquete se
verifican también sin red. Los resultados existentes no se sobrescriben.

38 pruebas focalizadas pasan; ejecución integral real y verificación visual de
las dos figuras terminadas. No se ejecutó la suite ajena de Studio.
Para clientes/Ecuador falta referencia autorizada con historia independiente,
validación científica y revisión profesional: no presentar este ensayo como eso.

## Credencial temporal de Copernicus

Cliente «Ecuador Vivo — piloto» creado con aprobación del usuario y vencimiento
26-10-2026 23:59:59 UTC. Flujo Client Credentials; sin modo SPA ni duración ilimitada.
El secreto se muestra una sola vez en el panel oficial: no pegarlo en chats.

Desde la raíz, ejecutar interactivamente:

```powershell
& './tools/parcelas/configurar-copernicus.ps1'
# En otra ocasión, comprobar la credencial ya guardada:
& './tools/parcelas/configurar-copernicus.ps1' -SoloComprobar
```

Solicita ID y secreto (entrada oculta), verifica OAuth y guarda únicamente el secreto
cifrado con DPAPI CurrentUser, fuera del repositorio/OneDrive, en
`%LOCALAPPDATA%/EcuadorVivo/credenciales/copernicus-piloto.dpapi.json`.
No guarda tokens ni procesa imágenes. No sobrescribe una credencial previa.
DPAPI protege el archivo en reposo, no frente a programas que ya se ejecuten como
el mismo usuario. No compartir el archivo, ni activar transcripciones de terminal.
La verificación OAuth real se completó tras introducir la credencial localmente.

Descarga diagnóstica implementada y ejecutada para las cuatro fechas aprobadas:

```powershell
& './tools/parcelas/descargar-radar-piloto.ps1' -Fecha '2025-03-08'
& './_local/video-studio/.venv/Scripts/python.exe' -m tools.parcelas.process_api inspect 2025-03-08
```

No volver a ejecutar sobre salidas existentes. Experimento fijo para la referencia
Ghana, no interfaz genérica. Máximo 5 MB, sin reintentos, sin token en disco.
La primera fecha descargada (20-03-2025) carece de ID de escena en sus metadatos;
las otras tres ya contienen `orbits` corregido. Esa primera respuesta se conserva
solo como evidencia diagnóstica; la fecha 20-03-2025 ya fue descargada de nuevo en
`api-rtc-20250320-trazable`, sin sobrescribirla, y su procedencia está comprobada.

Serie vigente: `_local/parcelas/piloto-352/serie-api-trazable/INFORME.md` y `serie.json`.
Se genera con `python -m tools.parcelas.api_series` usando el entorno indicado abajo,
sin red. Exige ID de producto del servicio coincidente con catálogo, fecha, cobertura,
misma adquisición, contrato guardado y huellas de archivo. No sobrescribe salidas.
Las cuatro fechas comparten 124 centros válidos. Continúa el vacío de 1.524 días;
sin interpretación forestal ni validez EUDR. Treinta pruebas focalizadas pasan.

Fuente oficial: https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Overview/Authentication.html

Ejecutar desde la raíz del repositorio en PowerShell:

```powershell
& './_local/video-studio/.venv/Scripts/python.exe' -m unittest discover -s tests -p test_parcel_catalog.py
& './_local/video-studio/.venv/Scripts/python.exe' -m tools.parcelas.catalog '_local/parcelas/referencias/cersgis-16579443/parcela-piloto.geojson' --start 2025-03-01 --end 2025-04-01 --output '_local/parcelas/piloto-352/nueva-consulta'
```

La carpeta de salida debe ser nueva. Se guardan inventario y metadatos STAC
originales; no imágenes. El periodo tiene final exclusivo. Máximo 100 ha,
366 días y cinco páginas de 100 elementos por colección; el resultado indica
si la paginación terminó o quedó truncada. La consulta es por caja envolvente:
encontrar escenas candidatas no garantiza cobertura válida de toda la parcela.
La nubosidad de escena NO es la nubosidad dentro del polígono.

Los grupos radar separan modo, órbita relativa, dirección y polarizaciones;
faltan comprobar incidencia, diferencias de procesamiento y calidad por píxel
antes de comparar. No se emiten conclusiones EUDR ni índices de exactitud.

## Receta SNAP: no ejecutada con imágenes

`sentinel1-grd-diagnostic.xml` es una receta diagnóstica para un producto GRD SAFE
original con metadatos completos. No usar sobre rásteres ya calibrados o RTC.
No se ha verificado aún su ejecución con un producto real ni la compatibilidad
del lector de SNAP 13 con los SAFE COG encontrados en el catálogo.

Parámetros pendientes: `input` (producto original local), `contextWkt` (área con
margen suficiente para corrección y análisis, no el recorte mínimo de 5 ha),
`mapProjection` (CRS proyectado apropiado, explícito) y `output` (archivo nuevo).
Para Ghana corresponde considerar UTM 30N, no reutilizar UTM de Ecuador.
Se propone espaciado de salida de 20 m, sin afirmar resolución o exactitud de 20 m.
Se preserva potencia lineal sigma0; no hay filtro speckle ni normalización
radiométrica del terreno en esta receta. No interpretar diferencias como tala.

Antes de ejecutarla: validar ayuda de cada operador y lector, disponibilidad
del DEM/órbitas (pueden requerir descargas), espacio y memoria, y ejecutar un
solo producto con dos hilos y caché acotada. No introducir credenciales en el grafo.
El acceso a imágenes completas de CDSE puede requerir cuenta gratuita; el
inventario público no demuestra acceso anónimo a los píxeles.

Procedencia y estado: `documentation/PILOTO-PARCELAS.md`.
Documentación oficial: https://step.esa.int/docs/tutorials/SNAP_CommandLine_Tutorial.pdf

## Comprobaciones implementadas

```powershell
& './_local/video-studio/.venv/Scripts/python.exe' -m unittest discover -s tests -p 'test_parcel*.py'
& './_local/video-studio/.venv/Scripts/python.exe' -m tools.parcelas.preflight --items '_local/parcelas/piloto-352/catalogo-202503/catalog-items.geojson' --output '_local/parcelas/piloto-352/nuevo-preflight'
& './_local/video-studio/.venv/Scripts/python.exe' -m tools.parcelas.optical_quality '_local/parcelas/referencias/cersgis-16579443/parcela-piloto.geojson' --output '_local/parcelas/piloto-352/nueva-calidad-optica'
```

Preflight ejecuta únicamente la ayuda de operadores (hasta 75 s por operador)
y solicita como máximo 1024 bytes del manifest oficial, sin credenciales.
No ejecuta el grafo, no valida parámetros numéricos y no descarga el producto.

Calidad óptica es una prueba acotada a marzo de 2025 de la referencia aprobada:
consulta una página pública Earth Search y lee ventanas SCL de los dos candidatos
de menor nubosidad de escena entre los recibidos. Indica si quedan más páginas;
no es una búsqueda exhaustiva de fechas despejadas. No recalibra reflectancia,
calcula NDVI ni usa SCL como mapa de cacao. Guarda los recortes nativos de 20 m.
Resultados y fuentes en cada salida; carpetas nuevas para evitar sobrescritura.

## Comparación diagnóstica de dos recortes procesados

```powershell
& './_local/video-studio/.venv/Scripts/python.exe' -m tools.parcelas.radar_pair '_local/parcelas/piloto-352/radar-pair-manifest.json' --output '_local/parcelas/piloto-352/nueva-comparacion-radar'
```

Requiere manifiesto local con las opciones de procesamiento observadas y SHA256
de dos exportaciones. Verifica máscaras, geometría, grillas idénticas y soporte
común positivo/finito. Conserva potencia lineal hasta calcular
`10*log10(media posterior/media anterior)`; no confundirlo con la media de
diferencias en dB. Exporta JSON y Markdown, no una clasificación forestal.
No usar el par con ajustes de capa desconocidos de la primera descarga:
los recortes RTC explícitos están en carpetas diferentes y no son originales GRD.
La igualdad de opciones UI no verifica por sí sola la procedencia escena a escena.

## Observaciones históricas y vacíos

```powershell
& './_local/video-studio/.venv/Scripts/python.exe' -m tools.parcelas.radar_series '_local/parcelas/piloto-352/radar-series-manifest.json' --output '_local/parcelas/piloto-352/nueva-serie-historica'
```

Acepta de 2 a 24 fechas y reutiliza el lector validado de los ZIP. Requiere
fechas únicas crecientes, huellas correctas, grillas idénticas y soporte válido
común en todas las fechas y polarizaciones. Cruza las fechas con los inventarios
locales: exige una escena candidata que cubra todo el polígono por fecha y el
mismo satélite, modo, órbita relativa y dirección. Esa correspondencia NO prueba
el linaje exacto de la salida del servicio.

Registra intervalos superiores a 30 días como vacíos descriptivos, sin
interpolarlos. Treinta días es un umbral de presentación del piloto, no un criterio
de detección forestal. Las estadísticas no prueban que hubiera bosque/cacao en
2020 y no producen un dictamen EUDR. El reporte explicita estos límites.
