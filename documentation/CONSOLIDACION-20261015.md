# Consolidación del proyecto · 15 octubre 2026

Trabajo de funciones pausado por petición del usuario. El proyecto vigente se
mantiene en una sola carpeta: `fallas-ecuador`, en su ubicación original. La web,
Inicio, SIG, Studio y Recursos pertenecen a esa misma instalación.

## Resultado

- Inventario previo: **11.339.637.803 bytes, 97.329 archivos**, aproximadamente
  **10,56 GiB**. Inventario posterior: **10.415.707.951 bytes, 78.752 archivos**,
  aproximadamente **9,70 GiB**. El inventario posterior incluye los archivos de
  recuperación y las revisiones antes dispersas fuera del repositorio. Los
  pequeños informes y el manifiesto de cierre se escriben después de medir.
- Se retiraron 1.128 objetivos exactos: pruebas anteriores de `tmp/`, capturas
  sueltas, el prototipo de mapa Remotion, sus dependencias y cuatro scripts de
  limpieza antiguos. Los archivos recuperables se guardaron en un ZIP privado de
  **418.579.078 bytes**; cada entrada se comprobó por SHA-256 antes de borrar.
- Se eliminaron doce carpetas `__pycache__` de las fuentes. Son regenerables.
- El componente SIG conserva una sola compilación: `sig-workbench.js/css`, el
  worker utilizado y los inventarios actuales. Se retiraron los bundles
  `index-u20` y `sig-workbench-v4` a `v8`. Vite limpia únicamente su salida de
  compilación y vuelve a generar el inventario de dependencias y hashes.
- Las referencias de GeoLibre/RustGIS, propuestas de diseño y capturas de este
  chat se trasladaron a `_local/maintenance/revisiones-20261015/` y se comprobaron
  por hash. El área del chat deja de contener una segunda colección de trabajo.
- Los datos auxiliares y netCDF4 usados por los generadores oceánicos ahora están
  en `_local/scientific-inputs/enso/`; ambos generadores apuntan a esa ubicación.
  Sus archivos se verificaron antes y después del traslado.

## Conservación

La comparación final de los **10.428 archivos protegidos** está registrada en
`_local/maintenance/consolidacion-20261015/verification.json`. Incluye todos los
proyectos guardados, los videos y guiones, medios, datos públicos, fuentes
geográficas y productos científicos protegidos. No se borraron proyectos ni
se rehicieron videos. Tampoco se cambió el historial de Git.

Blender, los motores instalados de Recursos, el entorno Python y los insumos de
`climate-studio`/`monitor-artifacts` continúan presentes. Algunos renderizadores
dependen de módulos con nombres históricos: no son instalaciones alternativas
del editor, y retirarlos sin migrar sus consumidores rompería esos flujos.

La guía de entrada es `VERSION-ACTUAL.md`; el checkpoint para continuar es
`ESTADO.md`. El manifiesto SHA-256 del código conservado está en
`_local/maintenance/consolidacion-20261015/current-source-manifest.json`.

## Verificaciones

- TypeScript y build de la compilación única del SIG: aprobados; 258 módulos.
- 37 pruebas Node del SIG: aprobadas.
- 16 pruebas Python de arranque, catálogo, Recursos y registro real del SIG:
  aprobadas.
- 25 pruebas Python de los mapas y guiones de El Niño: aprobadas con las rutas
  consolidadas, sin descargar ni renderizar material nuevo.
- Rutas de imports JavaScript de la web: aprobadas.
- Hashes del bundle, worker, inventario y bloqueo de dependencias: comprobados.
- Instancia 8534 reiniciada con el lanzador actual: salud HTTP 200 y registro
  inicial de errores vacío. La revisión de esta limpieza no incluye una nueva
  evaluación visual completa ni de todas las herramientas científicas.

## Recuperar un archivo retirado

ZIP: `_local/maintenance/consolidacion-20261015/archivos-retirados.zip`.
Plan e inventario: `plan.json`, `removed.json`, `moves.json` y carpetas
`antes/`/`despues/`, en la misma carpeta de mantenimiento.

Extraer el ZIP en una carpeta de recuperación separada y escoger los archivos
necesarios. Las rutas internas conservan su ubicación original en el repositorio.
No extraerlo directamente sobre el proyecto vigente: también contiene las
compilaciones y el registro previo del SIG. Las dependencias del prototipo
retirado se pueden reinstalar desde su `package-lock.json` archivado.

Se aplicó la skill de migración para comprobar consumidores antes de retirar
fuentes. El registro de Git se consultó para conservar los cambios existentes;
esta consolidación no hace commit, push ni publicación.
