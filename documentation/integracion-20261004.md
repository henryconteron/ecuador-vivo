# Integración de Ecuador Vivo · 4 de octubre de 2026

## Implementado

- Repositorio GitHub renombrado de `fallas-ecuador` a `ecuador-vivo`, conservando su historial. Remoto local actualizado.
- Portada basada en la propuesta visual, con imagen satelital original atribuida y cambio ES/EN.
- Visor existente conservado como `explore.html`. Los enlaces antiguos con parámetros del atlas se encaminan al visor desde la portada.
- Catálogo público de 15 conjuntos/servicios, con acceso, fuentes, cobertura y límites diferenciados.
- Biblioteca inicial de cuatro estudios/informes sobre Ecuador, sin activar el antiguo feed global.
- Caso Andes Pulso con video local, 2661 eventos conservados, verificación de integridad, mapa, tabla, filtros, descargas, método y derechos.
- Código científico y audiovisual del monitor preservado en `production/monitor/`; fuente del feed en `tools/biblioteca/original/`.

## Consolidación, respaldo y recuperación

Los artefactos de `monitor-sismos` fueron consolidados en `_local/monitor-artifacts`; el inventario actual contiene 6071 archivos. `production/monitor/artifacts` apunta a ese almacén único, de modo que las herramientas integradas trabajan sin duplicar los datos. Se retiraron únicamente los 9 MP4 enumerados en `cleanup-plan-20261004.json`, 46299012 bytes (44,2 MiB), a la Papelera de Windows. No se vació la Papelera.

Se creó un respaldo privado en Google Drive, **Ecuador Vivo — respaldo de producción**, compuesto por cinco paquetes divididos en 24 fragmentos, más dos manifiestos. La lectura posterior confirmó los 26 objetos, sus nombres y 2064572928 bytes de fragmentos. Los manifiestos conservan los SHA-256 calculados antes de la carga; la conexión de Drive no expone un hash remoto para afirmar una segunda comprobación criptográfica.

El repositorio `feed-geologico` recibió un aviso de transición en el commit `68e171a8e621e48f7f730ff705a19f63820b098b` y quedó archivado en GitHub: continúa público, consultable y reversible, pero en modo de solo lectura. No existía un repositorio remoto independiente llamado `monitor-sismos`. La antigua URL `fallas-ecuador` redirige al repositorio vigente `ecuador-vivo`; no representa otro proyecto para borrar.

Se conservaron maestros finales, voces originales, datos y trabajos en curso. El inventario detallado y recibo de ejecución están en `_local/migration-20261004/`. El procedimiento de recuperación está en `documentation/recuperacion-produccion-20261005.md`.

## Pendiente, sin ocultarlo

- Confirmar qué edición local coincide exactamente con los videos publicados en Instagram/TikTok.
- Los renderizadores históricos tienen rutas y dependencias entre versiones; preservación no equivale por sí sola a portabilidad completa.
- La carpeta local antigua `C:\Users\JHONY CONTERON\monitor-sismos` y los paquetes temporales de preparación del respaldo aún requieren una retirada manual: el entorno de automatización bloqueó las eliminaciones recursivas. Antes de hacerlo deben conservarse `_local/monitor-artifacts`, `production/monitor/` y el respaldo de Drive.
- Windows también mantiene ocupada la carpeta local `fallas-ecuador`; no fue posible renombrarla a `ecuador-vivo`. El repositorio remoto ya tiene el nombre nuevo. El cambio local debe hacerse con los editores, servidores y terminales de esa carpeta cerrados; no afecta al nombre público del sitio.
- La colección bibliográfica es inicial, no una revisión exhaustiva ni una validación científica independiente.

## Comprobación

`pnpm run check` o `npm run check` ejecutan los controles del atlas, laboratorio fluvial y portal. El núcleo consolidado del monitor se probó desde `production/monitor`: 160 pruebas correctas y 17 omitidas por dependencias o condiciones opcionales.
