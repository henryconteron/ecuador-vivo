# Laboratorio y almacenamiento portable

## Qué está implementado

- `geologia.html`: cartoteca inicial Tena–Archidona, filtros de atributos, separación entre unidades sin escala documentada e índice de hojas 1:100 000, mapa, selección y descarga GeoJSON con fuente, fecha y huellas de los archivos originales. No se recortan polígonos ni se aumenta la precisión. No es cobertura completa de Ecuador.
- `laboratorio.html`: apertura voluntaria de GeoLibre externo, incrustado o en otra pestaña, con conjuntos públicos fijados al commit `4cf5742c52c58fff5edddbff0c603e9e5fb92ddf`. No envía archivos locales ni credenciales. Las peticiones y la analítica del alojamiento externo dependen de GeoLibre y sus proveedores. No se habilitó control remoto por postMessage ni integración de cuentas.
- Guía para comparar, georreferenciar y documentar resultados. No se ha georreferenciado ni certificado una hoja ecuatoriana. La disponibilidad de funciones, su rendimiento y sus formatos de exportación deben comprobarse por versión.

El georreferenciador de GeoLibre sí está presente en su código y tiene [tutorial oficial](https://www.youtube.com/watch?v=lbioujkDSG0). Esto corrige la revisión inicial que no lo había confirmado. La [documentación de integración](https://geolibre.app/user-guide/embedding/) distingue visor de solo lectura y espacio de edición; este laboratorio abre el espacio editable, no `layout=viewer`. No copiamos código de UGS ni modelos de AuScope: seguimos sus ideas de catálogo por escala y conexión de evidencia.

## Drive: depósito, no motor del visor

Drive se utiliza como destino privado de respaldo. La aplicación pública no incorpora IDs de carpetas privadas, claves ni enlaces de sesión. No se modifica la ubicación de exportación de Earth Engine ni se mueven originales existentes.

Separación propuesta:

1. Originales de Earth Engine y campo: privados, conservados con sus recibos.
2. Respaldos verificados: ZIP con rutas relativas, manifiesto SHA-256, fuente/licencias y documentación.
3. Derivados web: versiones ligeras públicas en el repositorio o, más adelante, un almacenamiento preparado para servir datos geoespaciales.
4. Aportes: revisión antes de publicación; ningún permiso de Drive implica autorización para publicar todos sus archivos.

Google documenta [permisos de compartir](https://support.google.com/drive/answer/2494822?hl=es) y [descarga mediante API](https://developers.google.com/workspace/drive/api/guides/manage-downloads). No asumimos que un enlace de vista privada funcione como recurso público CORS o como servidor de teselas. Una gran cuota de almacenamiento tampoco garantiza la entrega que necesita un visor. Por ahora no dependemos de Drive para que la web funcione.

## Paquete piloto y migración

`python scripts/package_geology_backup.py` crea un ZIP nuevo en `_local/backups/` a partir de una lista explícita de archivos públicos: geología IIGE, documentación y condiciones. No recorre el disco ni incorpora `.env`, credenciales, la carpeta de referencias o producción privada. El paquete es **solo el piloto geológico, no un respaldo completo del proyecto**. Verifica cada entrada contra sus bytes originales después de comprimir. Una huella detecta alteraciones, no valida científicamente la geología.

`python scripts/package_geology_backup.py --verify RUTA.zip` verifica límites, rutas seguras, lista de entradas, tamaños y SHA-256 sin extraer archivos. Nunca ejecutar contenido del ZIP. Conservar el ZIP y la huella exterior en al menos dos ubicaciones; no depender exclusivamente de la cuota temporal de Drive.

Antes de vencer el almacenamiento: descargar inventario y paquetes, verificar las huellas, copiar al destino nuevo, verificar allí y actualizar solo las ubicaciones del registro privado. Mantener identificadores y nombres relativos. No borrar el origen hasta probar la recuperación. No se programó ninguna migración automática ni se asumió una fecha de vencimiento.
