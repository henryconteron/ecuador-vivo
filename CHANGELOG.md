# Registro de cambios

## Sin publicar — 2026-09-30

- Pipeline provincial progresivo Napo a 10 m: RGB sin pérdida por teselas, comparación
  temporal y cribado NDWI por escena con celdas candidatas de 1 km, QA y
  atribución. Primer bloque Tena–Archidona real habilitado: 392 teselas, 67 MB
  con carga por zona visible. El cribado permanece pendiente, sin puntos
  ficticios; no se fabrica resolución ni se atribuyen causas del cambio.
- Primer intento provincial cancelado por alto consumo de cuota; cribado
  original falló por memoria. Reformulación por bloques y muestra trimestral
  limitada, sin publicar esos intentos como productos listos.
- RGB del bloque completado en nueve minutos (1,67 horas EECU); recibo y
  archivos verificados. Se solicitó cancelar el cribado del bloque tras cuatro
  intentos automáticos sin resultado verificable; imágenes y cribado tienen
  estados independientes.

- Visor satelital Napo con zoom y paneo georreferenciados, corte de comparación
  2019/2024, año individual, opacidad, leyenda reactiva y enlaces reproducibles.
- NDMI, diferencia de NDVI y apoyo observacional derivados del GeoTIFF real ya
  exportado, con fórmulas nativas, soporte común y escalas fijas documentadas.
- Laboratorio fluvial bilingüe 2019/2024 con vistas RGB/NDVI/MNDWI, cuadrícula
  común, zoom editorial al Jatunyacu y contraste con monitoreo MAAP/EcoCiencia.
- Exportador multibanda y procesador Python que verifican fórmulas espectrales,
  QA por banda, soporte común y procedencia; sin clasificación automática de minería.
- Compatibilidad ES5 en la validación de conteos del exportador óptico anterior.
- Laboratorio visual bilingüe Sentinel-2/MapBiomas 2024: comparación deslizable de
  Tena–Archidona, 296 escenas enlazadas a QA, máscara común explícita, calidad y fuentes.
- Procesador Python de imagen óptica con recibo, SHA-256, rejilla compartida y
  pruebas de procedencia, máscara y conservación de píxeles oscuros válidos.
- Comparación real MapBiomas Ecuador V1 2000/2024 en la ventana Tena–Archidona,
  con cuadrícula nativa común, recibo, SHA-256, leyenda dinámica y atribución CC BY 4.0.
- Exportador Earth Engine asíncrono: no crea tareas cuando falla la consulta o la
  validación de años, resolución y alineación; pruebas de regresión de ese flujo.
- Porcentajes de clases raras expresados como «<0,1%», sin redondear su presencia a cero.
- Leyenda desplazable y separada de la atribución cuando se activan muchas clases.

## [0.1.0] — 2026-09-21

Primera versión pública del atlas Ecuador Vivo.

- Catálogo reproducible de fallas activas derivado de GEM GAF-DB, con procedencia SARA y *Active Tectonics of the Andes*.
- Capas interactivas de sismicidad, relieve, geomorfología, agua, precipitación, temperatura, nubosidad, inundaciones, estaciones y anomalías térmicas.
- Navegación contextual por Tierra, Agua, Cielo, Vida y Riesgo.
- Interfaz bilingüe en español e inglés, modo demostración y guía educativa.
- Validación automática de módulos, contenido, esquema y metadatos del catálogo.
- Documentación de fuentes, licencias, alcance de citas y límites de interpretación.

Esta versión es una base científica y educativa inicial; las capas remotas pueden cambiar según la disponibilidad y las políticas de sus proveedores.
