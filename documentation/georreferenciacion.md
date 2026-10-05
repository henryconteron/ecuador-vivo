# Georreferenciación: medir antes de publicar

## Estado · 4 de octubre de 2026

El verificador `georreferenciar.html` calcula un diagnóstico local de transformación afín. No georreferencia imágenes, no reproyecta, no exporta GeoTIFF y no certifica cartografía. Se mantiene separado del GeoLibre externo. Ninguna hoja ecuatoriana ha sido validada con este flujo.

### Fuente real examinada

GADM Tena, Unidad PFyOT / Secretaría Técnica de Planificación: [documento municipal, Mapa 8, página 20](https://tena.gob.ec/images/sampledata/PDF/PLANACTUALIZADO/normativa.pdf#page=20). El pie fecha la elaboración en junio de 2014 y cita cartas Tena/Puerto Napo de 1986. La página no muestra escala ni cuadrícula; menciona un shapefile adjunto no recuperado en esta revisión. No sustituimos ese vector con una digitalización aproximada ni inferimos actividad reciente a partir de trazas históricas. Se conserva el original descargado solo en `_local/`; no se redistribuye el PDF ni su figura.

Descarga revisada: 9 303 319 bytes; SHA-256 `12893082be0e27e539bbaee82fc600f0f3882399ca3c535a0a1ae901b41787bd`. La huella identifica esta copia, no certifica su contenido. El CRS de un mapa concreto debe confirmarse en sus metadatos originales; no se asigna por su sola ubicación en Ecuador.

## Datos de entrada

Descarga el ejemplo desde el verificador y reemplaza sus valores. Es **sintético**, con un ajuste exacto de tres controles y cuatro comprobaciones desplazadas 20 m. Nunca usar sus coordenadas para ubicar una hoja real. No es un conversor del formato `.points` de QGIS ni del formato de GeoLibre.

- `schema_version`: 1.
- `title`, `source`, `license`: texto obligatorio. Declarar condiciones desconocidas cuando corresponda no equivale a permiso de publicación.
- `synthetic`: booleano; `true` para datos inventados o didácticos. El sistema no puede comprobar esta declaración.
- `crs`: solo `EPSG:32717` o `EPSG:32718` (WGS 84 / UTM 17S o 18S), destino en metros. No acepta coordenadas geográficas ni cambia de datum. Las comprobaciones de rango no demuestran que el CRS declarado sea correcto.
- `pixel_convention`: `center-zero-based-y-down`. Origen en el centro del píxel superior izquierdo, x hacia la derecha, y hacia abajo. Convierte explícitamente otras convenciones antes de cargar. No invertir ejes automáticamente.
- `raster`: `width`, `height` enteros entre 2 y 100000; `sha256` opcional, 64 caracteres hexadecimales minúsculos del archivo exacto de imagen. Aquí no se carga la imagen: el hash es declarado, no verificado.
- `points`: 3–200 registros; cada uno con `id` único, `role` (`control` o `check`), `pixel_x`, `pixel_y`, `easting`, `northing` numéricos. Al menos tres controles no alineados. Tamaño máximo del JSON: 256 KiB.

## Método reproducible

Solo `control` entra en el ajuste por mínimos cuadrados. Se centran y normalizan las coordenadas de píxel para reducir problemas numéricos; se estiman dos funciones lineales con término independiente:

`E = e.offset + e.x * (pixel_x - cx) / sx + e.y * (pixel_y - cy) / sy`

`N = n.offset + n.x * (pixel_x - cx) / sx + n.y * (pixel_y - cy) / sy`

Los parámetros están en `transform` del informe. `sx` y `sy` son las desviaciones estándar poblacionales de los píxeles de control. Se rechazan alineación/casi alineación, transformación singular, coordenadas no finitas y posiciones repetidas. Se rechazan posiciones de imagen separadas menos de 0,000001 píxel o de destino menos de 0,001 m, también entre roles.

Para cada punto: `dx = E_calculado - E_referencia`, `dy = N_calculado - N_referencia`, distancia euclídea `sqrt(dx² + dy²)`. Por rol: `RMSE = sqrt(sum(dx² + dy²) / n)`. No se divide por grados de libertad: es RMSE descriptivo, no una estimación de varianza. La comprobación no participa en el ajuste. Sin puntos `check`, sus métricas son `null`, nunca cero. Metros del CRS proyectado, no distancia geodésica corregida por factor de escala UTM.

La independencia de la referencia no puede deducirse del JSON. Reservar puntos antes del ajuste y documentar su procedencia. No quitar puntos porque empeoran el resultado sin explicar y conservar la decisión. Tres controles pueden dar residuo cero por construcción. Un RMSE pequeño no elimina errores de datum, sesgo compartido con la referencia ni incertidumbre del mapa original. Tampoco define exactitud de campo, actividad de fallas o riesgo.

El aviso de distribución compara el rango de controles con ambos ejes de la imagen; no calcula cobertura de la envolvente convexa ni garantiza estabilidad en zonas sin controles. El número de comprobaciones es informativo: no establece conformidad con ninguna norma de exactitud. No hay umbral universal aprobado/reprobado.

## Privacidad y conservación

No hay envío de coordenadas, guardado automático ni conexión a Drive. Recargar borra el contenido. Editar la entrada invalida y deshabilita el informe anterior hasta recalcular. El informe incluye entrada, parámetros, residuos por punto y avisos; revisar coordenadas sensibles antes de compartir. Las fuentes se muestran como texto, nunca ejecutadas ni descargadas automáticamente.

Para un caso real: obtener imagen original y permiso; confirmar escala/datum/proyección; registrar resolución y hash; seleccionar controles y comprobaciones distribuidos; georreferenciar en QGIS o GeoLibre; comprobar el resultado y documentar transformaciones/remuestreo; conservar originales, puntos, informe y derivado. Preferir un vector o raster georreferenciado oficial si existe. No confundir un diagnóstico afín independiente con la comprobación de una transformación TPS u otro modelo.

## Referencia técnica

[QGIS 3.44, Georreferenciador](https://docs.qgis.org/3.44/es/docs/user_manual/working_with_raster/georeferencer.html): puntos, transformaciones y reporte de residuos. La implementación de este diagnóstico es propia y limitada a ajuste afín; no reproduce toda la funcionalidad de QGIS. Las decisiones científicas y de publicación requieren revisión humana.
