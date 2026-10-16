# Versión actual · auditoría de publicación · 16 octubre 2026

## Qué se guarda

Repositorio existente: `henryconteron/ecuador-vivo`, rama `main`. Se conserva
una sola raíz de trabajo local, `fallas-ecuador`; no se crea otro clon ni una
carpeta con una segunda instalación. La web, Inicio, SIG, Studio y Recursos
forman el mismo producto. Guía vigente: `VERSION-ACTUAL.md`.

La entrega añade las fuentes pendientes de esas áreas, sus pruebas, recursos
de interfaz y componentes compilados actuales con sus licencias. El índice
completo contiene aproximadamente 240 MiB; los cambios preparados, unos 40 MB.
No se confunde ese tamaño con los datos y programas locales de producción.

## Fuera de esta entrega

- `videos/`: composiciones, guiones, capturas, voces y entregas no publicadas.
- Sus herramientas y pruebas particulares de producción, que requieren esos
  insumos locales. Los editores generales sí se conservan en el repositorio.
- `_local/`: proyectos privados, originales científicos, autoguardados,
  cachés, trabajos de render, Blender, Manim y entornos de ejecución.
- `node_modules`, metadatos `egg-info`, estados `.hyperframes`, temporales,
  nuevas voces y videos y paquetes ZIP.

La pieza sísmica ya presente en el historial público no se modifica ni retira.
No se reescribe el historial Git. **GitHub respalda el código y los recursos
públicos, no sustituye el respaldo de los videos/proyectos privados.**

## Consolidación y correcciones

- SIG conserva una sola compilación vigente `sig-workbench.js/css` y sus
  dependencias; los bundles sustituidos se retiran del árbol actual.
- Los metadatos Python generados dejan de versionarse, sin quitar la
  instalación editable que utiliza el entorno local.
- Retirada una propuesta antigua de `.gitignore` ya superada. Las reglas
  efectivas excluyen producción privada y material audiovisual no publicado.
- La revisión amplia detectó pruebas ligadas a botones y claves de pantallas
  anteriores. Se adaptaron a formularios y eventos actuales, sin recuperar
  botones duplicados ni desactivar las comprobaciones científicas.
- Corregidos dos flujos de CSV geográfico: dibujar su cierre y preparar su
  publicación no requieren inventar una agregación meteorológica. Se
  conservan conteos o valores originales y sus límites. Las variables
  meteorológicas desconocidas, unidades incompatibles y fechas duplicadas
  siguen rechazándose.

## Comprobaciones

- Web: ESLint, 35 archivos de pruebas JavaScript, 29 entradas y siete
  validadores; correctos. Se conservan los avisos documentados de escala y
  procedencia de los catálogos, sin presentarlos como datos más precisos.
- Python de la web: 41 pruebas correctas.
- SIG: 37 pruebas Node, tipos TypeScript y compilación de producción correctos.
- Recursos: tipos TypeScript correctos. Auditorías npm del componente
  científico y SIG sin vulnerabilidades; motores de Recursos con cuatro
  avisos bajos, ninguno alto/crítico. No se aplicaron actualizaciones forzadas.
- Panel privado: 22 pruebas correctas. Dependencias Python: `pip check` correcto.
- Los módulos afectados por las correcciones pasaron sus pruebas focalizadas.
- Segunda ejecución completa de Studio: **747 pruebas, cero fallos/errores,
  una omitida**, en 578 segundos. No se ocultaron los veinte fallos detectados
  en la primera ejecución: se corrigieron sus causas/expectativas y se volvió
  a ejecutar toda la batería.
- Servidor local iniciado sin abrir pestañas; salud HTTP 200, registro de
  errores vacío en la comprobación de arranque.
- `scripts/audit_git_release.py` revisa los blobs exactos del índice: rutas
  privadas, medios no publicables, límite de tamaño, firmas de credenciales,
  sintaxis Python e importaciones relativas de componentes compilados.
- `git diff --cached --check`: correcto.

El análisis de firmas no garantiza detectar todo secreto posible; las pruebas
automatizadas y la comprobación de arranque no equivalen a una evaluación
visual exhaustiva de todos los editores ni certifican ausencia de errores.

## Recuperación

La raíz del repositorio contiene los lanzadores actuales. La instalación desde
una copia nueva, incluidos los dos componentes empaquetados de Streamlit, está
documentada en `production/video_studio/README.md`. No se deben restaurar
copias de versiones anteriores encima del código actual.
