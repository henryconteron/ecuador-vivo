# Limpieza de revisiones · 15 octubre 2026

Segunda pasada solicitada para conservar las últimas versiones de videos y
guiones y retirar material reemplazado. No modifica composiciones, datos
científicos, lógica de la aplicación, SIG ni interfaz.

## Retirado

- Seis ZIP de guiones/composiciones anteriores de El Niño.
- Cinco carpetas de revisiones del reel sísmico; se conserva la entrega v6,
  con catálogo, observaciones USGS, audio original y subtítulos.
- Capturas intermedias y artefactos antiguos de comprobación. Se conserva
  la revisión más reciente y las imágenes todavía enlazadas.
- El ZIP de temporales/prototipos de la primera consolidación. No se creó
  otro respaldo que vuelva a ocupar ese espacio.

Total: **495 archivos**, **1.009.703.879 bytes (963 MiB aproximadamente)**
de tamaño lógico retirado. Inventario posterior: **8,773 GiB** en el proyecto.
No confundir tamaño lógico con espacio físico asignado por OneDrive/NTFS.

La retirada es permanente en la carpeta de trabajo: **no hay un nuevo ZIP de
recuperación**. El historial Git se conserva; los archivos no versionados no
tienen recuperación garantizada.

## Verificación

- Diez composiciones del lote y dos episodios de El Niño conservados.
- Proyectos guardados, mapas, medios vinculados y fuentes conservados.
- 1.293 archivos conservados comprobados por SHA-256 sin cambios.
- Doce estados internos del editor conservados; no se exige hash inmutable
  porque las vistas previas pueden actualizarlos mientras funcionan.
- 25 pruebas ENSO y 22 de colección/importación/revisión: correctas.
- Aplicación en puerto 8534: salud HTTP 200.

No se borra un insumo porque su nombre contenga v2/v6: algunos se utilizan
desde renderizadores posteriores. Tampoco se eliminan herramientas activas,
datos diarios de una serie temporal o episodios distintos. Un respaldo antiguo
de Git contiene commits ausentes del Git actual; se conserva por no ser
íntegramente redundante. Los documentos históricos no son instalaciones.

## Entradas vigentes

- `VERSION-ACTUAL.md`: instalación única y estructura.
- `videos/README.md`: composiciones y guiones actuales.
- `_local/maintenance/version-unica-20261015/plan.json`: rutas exactas,
  razones, tamaños y huellas de retirada y protección.
- `_local/maintenance/version-unica-20261015/despues/`: inventario posterior.
