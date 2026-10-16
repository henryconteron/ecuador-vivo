# Cierre parcial de la v1 — 10 octubre 2026

## Verificado

Trabajo 1: `tmp/v1-definitive-opacity-1791607536944122200-recovered.json`.
El transporte CDP inicial excedió 10 MB; se recuperaron las mismas muestras
desde el mismo Chrome, sin repetir gestos ni reiniciar. El driver ahora descarga
en bloques de 100 filas, como la recuperación que funcionó.

| Fase | Muestras | Workspace stale | Mínimo efectivo | Ventanas stale (ms) |
|---|---:|---:|---:|---|
| Autoguardado | 850 | 360 | 1 | 6029,6 |
| Arrastre/restauración | 850 | 646 | 1 | 6222,3; 4591,8 |
| Cambio de escena | 850 | 428 | 1 | 3743,0; 3450,6 |
| Reproducción | 850 | 208 | 1 | 3468,0 |
| Retorno de preview | 850 | 0 | 1 | Ninguna observada |

Total: 4250, 1642 stale, mínimo 1, cero muestras sin mapa decodificado.
El contraste sin CSS tuvo 331 muestras, 322 stale y mínimo 0,33.
El único stale externo fue un contenedor invisible del stylesheet (419 muestras),
no un control visible: no se extendió el selector. El coste dominante fue
arrastre/restauración: 10,814 s acumulados; causa interna no perfilada, sin optimización.
La fase de retorno no valida por sí sola el comportamiento stale: no ocurrió en ella.

Trabajo 2: `tmp/v1-definitive-editing-1791608173270946900.json`.
Nombre persistido en input, documento del componente y JSON guardado, con revisiones
por gesto. Se corrigió un bug real: el argumento capturado del fragment sobreescribía
el documento canónico actual y borraba el historial. `show_workspace` toma ahora
la proyección actual de `session_state`. `editMode()` actualiza playhead y `clock(frame)`.
Transform (x,y,width,height): (46,157,1156,796) → (76,167,1156,796);
Undo restaura el primero; Redo el segundo. Retorno: frame 0, fecha 2024-01-01.
29 pruebas OK (28 existentes + regresión focalizada): `tmp/v1-definitive-29-tests.log`.
El cambio de nombre del driver se hace con click CDP, Ctrl+A (`rawKeyDown`/`keyUp`),
`Input.insertText`, Enter y Tab para blur; entrada en `dev/studio_v1_measure.py`,
implementación en `dev/studio_v1_opacity.py` y `dev/studio_v1_editing.py`.

Trabajo 3: arranque normal y reinicio manual en `documentation/V1-ARRANQUE.md`.
Sintaxis del lanzador y reutilización de 8526 probadas; arranque nuevo no probado.
Históricos copiados, originales conservados: `documentation/archive/v1-usable-20261009/`;
hashes en `tmp/v1-definitive-archive.json`. `.gitignore` solo propuesto, no aplicado.

Solo Chrome headless propio por CDP en esta ejecución. PIDs 3664, 24044 y 14000
cerrados. No se usó computer ni se operaron ventanas del usuario en esta ejecución.
Hubo un reinicio propio ENTRE mediciones para cargar la corrección: 10276 → 8648.
Cero reinicios dentro de cada medición. 8527/PID 8648 cerrado tras verificar identidad:
`tmp/v1-definitive-server-shutdown-8648.json`. 8510–8526 conservan sus PIDs;
8526 sigue en 27784 y necesita el reinicio manual documentado para cargar las correcciones.

## No verificado o fallando

Trabajo 4 bloqueado: el método zonal existente usa centros de píxel nativos y
ponderación cos(latitud). Con T2M de 0,5° × 0,625°, Carchi, Bolívar y Tungurahua
tienen 0 centros; solo 21 de 24 provincias tienen estadística. Galápagos tiene 2.
`tmp/v1-definitive-power-coverage.json` y la comprobación independiente por
Shapely `polygon.covers(Point)` coinciden en las 24 provincias:
`tmp/v1-definitive-power-coverage-independent.json`.
No se asignaron ceros, capitales, interpolaciones ni valores de provincias vecinas.

API real: las dos regiones nacionales devolvieron 464 celdas; última fecha completa
de la ventana reciente consultada: 2026-10-08. Ventana candidata de 61 días:
2026-08-09–2026-10-08; NO se ha comprobado completa en sus 61 días.
Fuente reciente GEOSIT, unidad C; resolución nativa medida 0,5° × 0,625°.
La climatología regional acepta la consulta pero ignora 1991–2020: responde
2001–2025 y lo advierte. El endpoint personalizado documentado responde 404.
Evidencia, URLs, cabeceras y hashes: `tmp/v1-definitive-power-probe.json`.
No se construyó aún la alternativa diaria 1991–2020: el bloqueo del ranking
interrumpió el Trabajo 4. No hay anomalías, ranking completo, MP4, receipt.json,
tiempos de primer render/cache ni smoke extremo a extremo de esta v1.

Referencias oficiales: [climatología regional y personalizada](https://power.larc.nasa.gov/docs/services/api/temporal/climatology/),
[resolución y reemplazo de datos recientes](https://power.larc.nasa.gov/docs/services/),
[latencia y fuentes](https://power.larc.nasa.gov/docs/faqs/data/).
No se elevó el límite de 32 observaciones por preparación SIG. El requisito de
61 días frente al alcance congelado sigue registrado; no se comprobó composición en dos clips.

## Diferencias de diseño frente a las referencias que quedan

No se realizó una comparación visual sistemática en este corte. Los screenshots
`tmp/ux-redesign/v1-definitive-opacity-1791607536944122200.png` y
`tmp/ux-redesign/v1-definitive-editing-1791608173270946900.png` son evidencia de
estabilidad y calendario; no validan equivalencia de diseño con las referencias.
No se abordaron cambios de diseño adicionales.

Lista exacta de archivos detectados como creados/modificados, incluidos ignorados:
`tmp/v1-definitive-files.json`. Las copias de borrador creadas se enumeran además
en `tmp/v1-definitive-copies.json`; ninguna se borró.

Siguiente paso único: resolver el criterio zonal de las tres provincias sin centros
nativos antes de continuar el Trabajo 4. La alternativa de intersección de celdas
con polígonos cambiaría el método exigido; no se implementó sin esa decisión.

## Comandos preparados, NO ejecutados

No usar el tag hasta que pasen los criterios pendientes. Revisar primero el
inventario y resolver el versionado de las dependencias de los drivers en tmp/.

```powershell
git status --short
git diff --stat
git add -- production/video_studio/app.py production/video_studio/studio_workspace.py production/video_studio/workspace_frontend/workspace.js production/video_studio/workspace_frontend/host.css production/video_studio/launch.ps1 production/video_studio/test_studio_v1_name.py documentation/ESTADO.md documentation/V1-ARRANQUE.md documentation/V1-CIERRE.md documentation/v1-usable-gitignore-proposal.diff documentation/archive/v1-usable-20261009 tasks/plan.md tasks/todo.md dev/studio_v1_measure.py dev/studio_v1_opacity.py dev/studio_v1_resume_opacity.py dev/studio_v1_editing.py dev/studio_v1_inventory.py dev/studio_v1_archive.py dev/studio_v1_record_server.py dev/studio_v1_power_probe.py dev/studio_v1_power_coverage.py dev/studio_v1_verify_coverage.py
git diff --cached --stat
git commit -m "Complete Ecuador Vivo Studio usable v1"
git tag -a v1-usable -m "Ecuador Vivo Studio usable v1"
```

No se ejecutaron commit, tag, push, instalación de paquetes ni comandos de borrado.
