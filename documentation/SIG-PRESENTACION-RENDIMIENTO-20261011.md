# SIG: recorte, acabado social y transferencia (11 octubre 2026)

## Causas encontradas

El SIG omitía el `presentation` y el encuadre territorial al pedir la representación. La reproducción diferida omitía lo mismo. OpenLayers imponía nearest incluso cuando el inspector decía suavizado. La ruta genérica de Studio usaba la composición mínima; solo CHIRPS v2 diario nacional recibía la maqueta editorial.

Ahora vista inicial, reproducción y exportación usan la misma máscara y opciones territoriales, paleta de lluvia de ocho colores, escala común propia de la variable, contorno y provincias. El suavizado bilinear es sobre valores exclusivamente visuales; la máscara de soporte nativo nearest se aplica al final junto con el polígono. No se rellenan NoData ni fechas. Un producto no seleccionado deja de aparecer detrás de los huecos de la serie; su visibilidad canónica no se elimina. Las nuevas importaciones tienen opacidad 100%; se respetan opacidades ya editadas.

Galápagos nacional aparece como inset del mismo original, fecha, variable y escala cuando existe cobertura nativa del archipiélago. No se inventan valores desde el continente. La ruta sellada puede recuperar el original global CHIRPS ya verificable; el visor no descarga otro producto para suplirlo. El inset es una reubicación editorial, no coordenadas reales junto al continente.

Las series numéricas genéricas pasan a la maqueta editorial editable de lluvia con títulos, unidades, periodo, escala y crédito propios. No reciben métricas de precipitación como si fueran temperatura o viento. Se mantienen los originales, fuentes, cálculos y ediciones de posición/texto/visibilidad del usuario. Los formatos diagnósticos diminutos conservan una composición compacta. No se añaden interpolaciones de estaciones ni animaciones temporales CSV en esta corrección.

## Mediciones e intentos

Datos locales reales: 30 bandas NASA POWER T2M, 1–30 septiembre 2026, mismos originales ya adquiridos. Preset TikTok 1080×1920; 6 segundos, sin audio. No descargar otra vez ni hacer benchmarks sobre proyectos personales. Scripts de evidencia en `dev/review_sig_presentation*.py`; perfiles y reportes en `tmp/sig-presentation-review/`.

| Cambio aislado / acumulado | Primer envío (s) | Repetición (s) | Decisión |
|---|---:|---:|---|
| Base, perfil instrumentado | 71.7 | 79.9 | Referencia |
| Límites transformados cacheados por revisión de archivo | 47.2 | 52.2 | Conservar: menos lecturas y transformaciones repetidas |
| Maqueta compartida, sin doble validación completa; reusar bundle intacto | 35.0 | 5.3 | Conservar: no generar otro bundle en un envío idéntico |
| Caché de máscara/tinta, corrida instrumentada posterior | 64.9 | 14.6 | Total ruidoso; no atribuir una mejora global a esta corrida |
| Repetición real sin instrumentación, metadatos 8 | 64.6 | 16.2 | Variación del sistema, conservando la comprobación |
| Metadatos acotados 128, mismo calendario y geometría; opacidad 100% | 59.4 | 11.5 | Conservar: evita expulsar cada fecha de un mes; hashes siguen obligatorios |

La caché geométrica se contrastó separadamente, alternando cuatro corridas de geometría/tinta sin caché y con caché a 800×900: mediana ~0.61 s frente a ~0.016 s (36–39 veces en esa operación, **no** en todo el envío). Bytes de máscara e imagen iguales; copias nuevas al consumir, límites 8 entradas / 12 MiB. Se conserva por esa evidencia, sin prometer un tiempo total estable. Primeros envíos pueden tardar ~un minuto; no son instantáneos. El ahorro mayor es repetir sin cambios, sin omitir verificación nativa ni de los tiles al usar/exportar el producto.

La caché de metadatos almacena diccionarios pequeños, no rásteres. Cada consulta verifica autorización, SHA256 y tags del original antes/después del lookup. Los límites territoriales cacheados se invalidan por identidad de archivo, tamaño, mtime y revisión NTFS ChangeTime, incluidos cambios que restauren tamaño/mtime; se devuelven copias. Las capacidades diferidas admiten los dos canales de la longitud máxima de serie soportada, evitando que el antiguo límite de 128 expulse las primeras fechas de un año. Expiran y no permiten acceso a rutas arbitrarias.

## Resolución y fuentes

NASA POWER meteorológico tiene celdas de 0.5°×0.625° (~50–60 km), no detalle urbano. El suavizado no cambia esa resolución ni transforma reanálisis en medición de campo. ERA5-Land a ~11 km es una alternativa más fina para temperatura del aire a 2 m, documentada en el catálogo oficial, pero **no se conectó ni descargó** en esta corrección. No sustituir T2M por temperatura superficial MODIS para simular mayor resolución.

- NASA POWER: https://power.larc.nasa.gov/docs/tutorials/
- ERA5-Land diario: https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_DAILY_AGGR

Cambios locales. Sin commit, push, publicación web ni eliminación de proyectos previos. La evidencia generada es una muestra de revisión; no una nueva versión científica de los datos.
