# Registro de cambios

## Sin publicar — 2026-10-01

- Muestra fija depurada 31/32 auditada y ejecutada en GEE: RGB y conteos
  descargados, reconstruidos y verificados en staging e integrados localmente.
  No cambió ninguna de las 392 teselas RGB ni los resultados de las 24 celdas:
  mejora de procedencia, no de resolución, apariencia o validación científica.
- Comparación ES/EN descargable desde el calendario, archivo de procedencia
  original y plan; promoción comprobada con respaldo recuperable antes de
  reemplazar archivos, manifiesto al final y sin commit/push automático.
- Recibos de muestras fijas deben coincidir con IDs del plan y rechazar pases/
  teselas repetidos. CLI RGB/conteos con configuración explícita y staging
  obligatorio para esas muestras; validación por raíz alternativa.

- Auditoría temporal ES/EN del recibo real: calendario mensual e inventario
  de fechas/IDs, manifiesto descargable y distinción entre archivos, días
  diferentes y apoyo por píxel. 31/32 archivos corresponden a 17/13 días.
- Advertencia explícita de dos variantes del pase/tesela del 21 de junio de
  2019 en el lote original; se conserva ese recibo histórico y se exporta una
  muestra emparejada nueva, sin presumir independencia de los conteos.
  Los 24 candidatos siguen sin validación de campo o hidrológica.

- Navegador ES/EN para las celdas de cribado, anterior/siguiente y selección
  con zoom nativo; enlaces compartidos que reabren una celda verificada.
  Guía de revisión plegable, sin convertir exploración en validación científica
  ni consumir nuevas exportaciones de Earth Engine. Orden por señal, no riesgo.

- Cribado real del bloque 7 Tena–Archidona: 24 celdas candidatas sin revisar,
  derivadas de conteos ópticos exportados, no de las imágenes RGB. Marcadores
  opcionales, contorno de revisión de 1 km y acercamiento al abrir una ficha.
- Procedencia de conteos y RGB emparejada por escenas, QA, límite y cuadrícula;
  fracciones exactas, componentes de ocho vecinos en Python sin cortar las
  costuras entre archivos. 5.329.345 píxeles comparables; áreas aproximadas,
  sin atribuir minería, contaminación ni cambios confirmados del cauce.
- Pruebas de falta de datos, cero agua observado, umbral exacto, desbordamiento
  numérico, conectividad, costuras y rechazo de datos incompatibles; integridad
  SHA-256 y publicación que no modifica las teselas RGB existentes.
- Leyenda limitada en anchura para no cubrir el visor ampliado; fichas ES/EN
  con apoyo observacional por celda, no presentado como índice de confianza.

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
