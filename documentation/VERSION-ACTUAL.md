# Ecuador Vivo · ubicación y versión actual

La única carpeta de trabajo del proyecto es:

`C:/Users/JHONY CONTERON/OneDrive/Documentos/GitHub/fallas-ecuador`

Aquí están la web, Inicio, SIG, Studio, Recursos, datos y videos. Las carpetas de
datos, herramientas y compilaciones cumplen funciones distintas; no son copias
completas del producto. No duplicar el repositorio para guardar un avance.

Entrega a GitHub del 16 de octubre: `AUDITORIA-PUBLICACION-20261016.md`.
Los videos y la producción privada se mantienen locales; las reglas de Git
impiden agregarlos por accidente. Reinstalación desde una copia nueva:
`production/video_studio/README.md`.

## Abrir

- **Aplicación local:** `Abrir editor de videos.vbs`, en la raíz. Usa
  `production/video_studio/launch.ps1` y `studio_server.py`, puerto **8534**.
- **Página web:** `index.html` y los archivos web de la raíz.
- **Panel privado de la web:** `Abrir panel personal de la web.vbs`.
- **Videos y guiones:** `videos/`; la colección y los lanzadores están en
  `videos/expedicion-lote-20261013/` y `dev/launch_expedicion_previews.ps1`.

## Organización

| Carpeta | Contenido que se conserva |
|---|---|
| `production/video_studio/` | Código actual de Inicio, SIG, Studio y Recursos |
| `production/site_admin/` | Panel privado y borradores de la web |
| `assets/`, `data/` | Interfaz pública, ilustraciones, datos y catálogos |
| `videos/` | Composiciones, mapas, guiones y evidencia de cada video |
| `_local/video-studio/` | Proyectos guardados, medios, datos científicos, Blender y entorno Python |
| `_local/scientific-inputs/enso/` | Referencias y dependencias científicas de los mapas oceánicos |
| `_local/climate-studio/`, `_local/monitor-artifacts/` | Insumos y productos anteriores todavía vinculados al trabajo científico |
| `_local/maintenance/` | Inventarios, verificaciones y recuperación de archivos retirados |
| `documentation/ESTADO.md` | Punto de continuación vigente |
| `scripts/`, `dev/`, `tests/` | Preparación de datos, desarrollo y verificación |

## Una compilación activa del SIG

El componente usa `sig-workbench.js` y `sig-workbench.css`. La compilación limpia
su propia carpeta `frontend/build/` y genera un inventario de los archivos y
dependencias actuales. No se guardan allí variantes v4, v5, v6, v7 o v8.
Las fuentes TypeScript y los archivos de bloqueo permiten reconstruirla.

El historial de Git conserva la evolución del código. Los informes históricos
de `documentation/` documentan decisiones y pruebas; el punto de entrada para
continuar es siempre `ESTADO.md`, no un checkpoint antiguo.

## Consolidación del 15 de octubre de 2026

Registro inicial: `CONSOLIDACION-20261015.md`. Segunda pasada:
`LIMPIEZA-VERSIONES-20261015.md`. Por petición de conservar solo lo actual,
se retiró también el ZIP de temporales de la primera pasada. El catálogo de
videos y guiones vigentes está en `videos/README.md`.
Los temporales nuevos deben generarse en `tmp/` y las revisiones persistentes en
`_local/maintenance/`, evitando dispersarlas fuera de esta carpeta.
