# Arquitectura técnica

Revisión: 2026-10-05.

Ecuador Vivo es un sitio estático: las páginas, los módulos JavaScript y los datos públicos se
sirven directamente desde GitHub Pages. No requiere servidor propio, base de datos ni claves en
el navegador. Las fuentes remotas se consultan solo cuando una capa las necesita y los productos
locales conservan manifiestos o recibos de procedencia.

## Flujo del visor

```text
explore.html
    │
    ├── i18n.js ───────────── textos ES/EN
    └── map.js ────────────── coordinación del visor
          ├── config/data ─── URLs, límites y carga GeoJSON
          ├── systems ─────── Tierra, Agua, Cielo, Vida y Riesgo
          ├── symbology ───── estilos cartográficos
          ├── popups ──────── fichas seguras de fallas y evidencias
          ├── fault-catalog ─ búsqueda, filtros y ordenación
          ├── station-panel ─ carga, estado, filtro y fichas INAMHI
          ├── earthquake-panel ─ consulta y lista sísmica
          ├── wms-layer ───── ciclo de vida y opacidad de capas WMS
          └── geology / imagery / spectral / rivers / landcover / local-data
                              experiencias temáticas independientes
```

`map.js` conserva la coordinación que realmente cruza varias capas: mapa Leaflet, selección del
sistema, leyenda reactiva, conteo de fuentes y «Explícame este lugar». La lógica que puede probarse
sin un navegador vive en módulos pequeños. Esta separación evita introducir un empaquetador en un
proyecto que puede seguir desplegándose como archivos estáticos y permite que un fallo temático no
obligue a reescribir todo el visor.

## Datos y procedencia

- `data/geojson/` contiene instantáneas pequeñas y publicables.
- `data/manifests/`, los manifiestos junto a cada producto y las páginas de método fijan origen,
  fecha, parámetros, hashes o límites cuando corresponda.
- Las capas WMS/WMTS y APIs permanecen externas; la interfaz identifica al proveedor y muestra un
  estado de carga o error.
- `_local/`, credenciales, originales pesados y notas privadas no forman parte del sitio público.
- Los indicadores derivados son evidencia de observación, no atribución automática de causas.

## Barreras de calidad

`pnpm run check` ejecuta lint, descubre automáticamente todas las pruebas `test-*.mjs`, valida
catálogos, manifiestos, importaciones locales y recursos bilingües. `python -m unittest discover -s
tests` cubre los procesos científicos y geoespaciales en Python. La publicación se bloquea si
alguno falla.

Las advertencias científicas documentadas —por ejemplo, citas a nivel de catálogo o escalas no
declaradas— se conservan como advertencias visibles: no se silencian ni se convierten en precisión
inventada.

## Cómo añadir una capa

1. Registrar fuente, licencia, resolución, fecha y limitaciones.
2. Aislar carga, normalización y estado en un módulo de `assets/js/map/`.
3. Mantener `map.js` como coordinador y no como depósito de lógica temática.
4. Añadir una prueba que cubra éxito, ausencia de datos y error de red cuando aplique.
5. Incorporar textos ES/EN y comprobar navegación por teclado y movimiento reducido.
6. Ejecutar ambos conjuntos de pruebas y revisar manualmente escritorio y móvil antes de publicar.

La lista operativa completa está en [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md).
