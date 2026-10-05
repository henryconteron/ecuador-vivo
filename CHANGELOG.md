# Registro de cambios

## 2026-10-04 — Superficie Slab2 documentada

- Sustituida la malla inventada por el recorte nativo Slab2 South America 2018, desde la distribución oficial USGS; profundidad, incertidumbre, manifiesto y generación reproducible con originales fijados por SHA-256.
- Inspección por coordenadas, color por incertidumbre y descarga. Huecos conservados, sin interpolación ni conexión de nodos separados por NoData.
- Eliminada la división conceptual de superficie en dos placas; el plano tenue solo representa profundidad cero. No se simula el volumen de la placa Sudamericana.
- Catálogo histórico sin cambios; geometría modelada, incertidumbre de superficie e hipocentros se distinguen explícitamente.

## 2026-10-04 — Prototipos 3D y navegación compacta

- Escena conceptual Nazca–Sudamérica separada explícitamente de los hipocentros USGS 1900–2025; filtros, profundidades y fichas con comprobación SHA-256 del catálogo conservado. No incorpora Slab2 ni sismos en vivo.
- Relieve matemático sintético con giro, perfil móvil y descarga local; sin CRS ni unidades físicas.
- Accesos rápidos en inicio, paneles independientes en el visor y selector de capítulos en Aprender.
- Tres síntesis introductorias con fuentes USGS sobre rocas, cuencas e incertidumbre de modelos 3D. No supone una revisión completa de todas las lecciones.
- Los mapas personales georreferenciados no se importaron ni modificaron.

## 2026-10-04 — Diagnóstico de georreferenciación

- Verificador ES/EN de puntos: ajuste afín, comprobaciones reservadas, residuos y reporte JSON local sin envío de datos.
- Ejemplo explícitamente sintético que contrasta ajuste de 0 m y comprobaciones de 20 m; no es una hoja validada.
- Revisión del Mapa 8 del GADM Tena, página 20: sin cuadrícula/escala visible; se prioriza recuperar el vector original mencionado, sin publicar una superposición aproximada.
- Pruebas numéricas, controles degenerados, coordenadas repetidas, edición e invalidación de informes.

## 2026-10-04 — Cartoteca y laboratorio externo

- Cartoteca bilingüe con filtros de unidades, litología y estado de hojas IIGE, selección en mapa y exportación GeoJSON con procedencia.
- GeoLibre externo bajo apertura explícita, con conjuntos públicos fijados a una revisión y guías de comparación y georreferenciación. Sin conexión con cuentas privadas ni publicación automática.
- Empaquetado portátil y verificación SHA-256 del piloto geológico; respaldo privado en Drive con recuperación comprobada. No constituye un respaldo completo del proyecto.
- Pruebas de filtros, integridad, procedencia, apertura opcional y archivos de respaldo.

## 2026-10-04 — Sistemas independientes, geología y cuaderno de rocas

- Aislamiento real de capas por sistema y combinación explícita; preferencias de capas conservadas al volver al apartado.
- Geología IIGE regional y selección Tena–Archidona con integridad, procedencia, descarga y límites de escala visibles.
- Comparación privada de GeoJSON, validación básica y propuestas públicas separadas para revisión.
- Lección bilingüe de rocas recuperada del feed, ejercicios y ficha descargable.
- Dos estudios abiertos de Napo incorporados con DOI y licencia documentada; filtro de acceso y descubrimiento bibliográfico manual sin publicación automática.
- Símbolo vectorial Ecuador Vivo compartido por las páginas del portal.

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
