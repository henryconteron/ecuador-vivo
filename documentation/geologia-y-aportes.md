# Geología, aprendizaje y aportes · 2026-10-04

## Cartografía realmente disponible

Se consultó el [Geoportal del IIGE](https://geoportal.geoenergia.gob.ec/) y su [directorio de servicios](https://capas.geoenergia.gob.ec/arcgis/rest/services). El atlas incorpora el WMS `Geologia_General`, capa 0. Es un servicio externo: disponibilidad, contenido y cobertura pueden cambiar. No se presenta como cobertura completa del país.

También se conserva una selección espacial reproducible en `data/geology/`: 56 polígonos de unidades y cuatro polígonos del índice de hojas que intersectan la ventana oeste -78.1, sur -1.2, este -77.6, norte -0.7 (longitud/latitud WGS84). Son polígonos completos, **no recortados a la ventana ni a Napo**. Las geometrías se solicitaron al servicio con `outSR=4326`; no se georreferenciaron capturas de pantalla.

- Unidades: [metadatos del servicio](https://capas.geoenergia.gob.ec/arcgis/rest/services/Geologia_General/MapServer/0). No se pudo establecer una escala de compilación con los metadatos consultados. No atribuirles automáticamente 1:100 000.
- Hojas: [índice IIGE](https://capas.geoenergia.gob.ec/arcgis/rest/services/Cartas_Geologicas_100K/MapServer/0). Un índice de hojas no equivale al contenido geológico de esas hojas. Tena (OBJECTID 129) figura **En revisión**, versiones 1987 / 2020. Puerto Napo, Chalupas y S. José de Poaló figuran Programada en la copia consultada.
- Los atributos se conservan como los devuelve el IIGE, incluidos textos truncados, espacios, categorías incompletas y nombres originales en español. No se completaron con inferencias.
- Los colores de la copia local son una ayuda de lectura de Ecuador Vivo, **no la leyenda oficial**. El WMS conserva la representación del proveedor y enlaza su leyenda.
- Acercar no aumenta la precisión. No usar para ingeniería, límites de predios ni identificación automática de una muestra.

`scripts/export_iige_geology.py` consulta el número esperado, comprueba IDs únicos y conserva las geometrías, direcciones de consulta, fecha, tamaño y SHA-256. Serializa GeoJSON UTF-8 LF: la huella corresponde a esa copia, no a los bytes HTTP originales. Una nueva ejecución cambia la edición y requiere revisión. No se ejecuta automáticamente en la web.

### Atribución y condiciones

Instituto de Investigación Geológico y Energético (IIGE), datos descargados el 4 de octubre de 2026 desde sus servicios oficiales. [Condiciones del Geoportal](https://geoportal.geoenergia.gob.ec/). Se deben conservar fuente y fecha, sin implicar respaldo institucional ni alterar el sentido de los datos. Estos datos no están cubiertos por la licencia MIT del código. La consulta pública de metadatos no sustituye revisar condiciones para cada redistribución.

## Aprender sobre rocas

`rocks.html` recupera y adapta el módulo de observación del antiguo feed: familias de rocas, registro ordenado, hipótesis, ejercicios, seguridad y ficha descargable. La versión original sigue preservada en `tools/biblioteca/original/cursos/observacion-rocas.html`. La ficha es privada de la pestaña, sin guardado automático.

Dos artículos locales de acceso abierto se incorporaron a la biblioteca con DOI, autoría y licencia contrastados con Crossref:

- Huatatoca-Mamallacta et al. (2025), [Shunku Rumi](https://doi.org/10.3390/geosciences15110419), CC BY 4.0.
- Vera-Jaramillo et al. (2026), [afloramiento del Jatunyacu](https://doi.org/10.3390/geosciences16060215), CC BY 4.0.

Las síntesis expresan pertinencia, no una revisión independiente de resultados. No se descargaron ni georreferenciaron sus figuras en esta etapa.

## Feed científico: descubrir no es publicar

El flujo es **descubrir → revisar acceso y pertinencia → comprobar alcance → incorporar**. `scripts/discover_ecuador_studies.py` produce candidatos en `_local/`, nunca altera la biblioteca pública. Hay una acción manual “Discover Ecuador studies (review queue)” que guarda una lista de revisión durante 14 días.

Límites: una página de 100 resultados Crossref, palabra Ecuador en el título, metadatos de licencia Creative Commons. Puede omitir estudios de Napo cuyo título no mencione Ecuador; no garantiza disponibilidad efectiva del texto, calidad, ausencia de retractaciones ni exhaustividad. El feed anterior global no se republica indiscriminadamente. Revisar versión, licencia y avisos de la editorial antes de aceptar un candidato. No hay una actualización periódica programada.

## Aportar y comparar

El visor admite una capa GeoJSON local (máximo 10 MB, 5000 entidades, 100000 vértices), coordenadas longitud/latitud WGS84 dentro del rango del visor Web Mercator. Rechaza CRS declarados, geometrías no soportadas, números fuera de rango y anillos abiertos. Estas verificaciones **no prueban** validez topológica ni científica, ni detectan toda inversión longitud/latitud. Los atributos se muestran como texto, nunca como HTML ejecutable.

La capa permanece en memoria, identificada en magenta como no verificada, asociada al sistema activo al cargar. Se puede apagar, ajustar su opacidad, acercar y retirar. Se pierde al recargar. El archivo no se envía; los mapas base siguen solicitando teselas externas. No se comparten archivos locales al compartir la URL.

Para contribuir públicamente hay un formulario de propuesta en GitHub (requiere cuenta): fuente, autoría, licencia, territorio, escala/CRS y límites. **No es almacenamiento público inmediato**, ni un foro sin moderación. No subir información personal, coordenadas sensibles, documentos restringidos ni datos sin permiso.

## Referencias de arquitectura y siguiente capacidad

- [UGS Geologic Map Portal](https://github.com/UGS-GIO/geolMapPortal): referencia para conectar hojas y cartografía consultable.
- [AuScope AVRE](https://www.auscope.org.au/avre): referencia para separar descubrimiento de recursos y modelos 3D. Su visor geomodels no respondió durante esta consulta; no se ha afirmado probarlo.
- [GeoLibre](https://github.com/opengeos/GeoLibre) y [funciones documentadas](https://geolibre.app/features/): el laboratorio ofrece ahora una apertura externa opcional con datos públicos versionados. La revisión posterior confirmó un georreferenciador en su código y tutorial oficial. No se instaló ni se copió el proyecto completo. Véase [integración y límites](laboratorio-y-almacenamiento.md).

La validación de una hoja ecuatoriana con puntos de control queda pendiente: requiere CRS origen/destino, puntos distribuidos, transformación, puntos de comprobación independientes, residuos y error reportado, recorte de márgenes, licencia y registro de autoría. Superponer una imagen estirada no equivale a georreferenciarla. No prometer precisión por el solo aspecto visual.

Un repositorio público de aportes requerirá identidad, almacenamiento, cuotas, análisis de archivos, moderación, retirada y versiones. La comparación local y las propuestas revisadas funcionan sin crear todavía esa infraestructura ni comprometer pagos.
