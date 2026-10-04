# Integración de Ecuador Vivo · 4 de octubre de 2026

## Implementado

- Repositorio GitHub renombrado de `fallas-ecuador` a `ecuador-vivo`, conservando su historial. Remoto local actualizado.
- Portada basada en la propuesta visual, con imagen satelital original atribuida y cambio ES/EN.
- Visor existente conservado como `explore.html`. Los enlaces antiguos con parámetros del atlas se encaminan al visor desde la portada.
- Catálogo público de 15 conjuntos/servicios, con acceso, fuentes, cobertura y límites diferenciados.
- Biblioteca inicial de cuatro estudios/informes sobre Ecuador, sin activar el antiguo feed global.
- Caso Andes Pulso con video local, 2661 eventos conservados, verificación de integridad, mapa, tabla, filtros, descargas, método y derechos.
- Código científico y audiovisual del monitor preservado en `production/monitor/`; fuente del feed en `tools/biblioteca/original/`.

## Limpieza ejecutada y recuperación

4563 archivos de `monitor-sismos/artifacts` fueron trasladados a `_local/monitor-artifacts` y comprobados por SHA-256. La ruta original `monitor-sismos/artifacts` es un enlace de compatibilidad sin duplicar el contenido. Se retiraron únicamente los 9 MP4 enumerados en `cleanup-plan-20261004.json`, 46299012 bytes (44,2 MiB), a la Papelera de Windows. No se vació la Papelera; el espacio físico recuperado depende de ella y de OneDrive.

Se conservaron maestros finales, voces originales, datos y trabajos en curso. El inventario detallado y recibo de ejecución están en `_local/migration-20261004/`. También hay respaldos Git de ambos proyectos. El plan de limpieza es una auditoría histórica, no un registro de que se borró todo lo que enumera.

## Pendiente, sin ocultarlo

- Confirmar qué edición local coincide exactamente con los videos publicados en Instagram/TikTok.
- Los renderizadores históricos tienen rutas y dependencias entre versiones; preservación no equivale a portabilidad completa. No eliminar sus fuentes anteriores.
- Windows impidió mover la raíz completa de monitor-sismos porque otro proceso la utiliza. Su contenido audiovisual ya está dentro de Ecuador Vivo; el entorno y la carpeta original no se han eliminado.
- Windows también mantiene ocupada la carpeta local `fallas-ecuador`; no fue posible renombrarla a `ecuador-vivo`. El repositorio remoto ya tiene el nombre nuevo. El cambio local debe hacerse con los editores, servidores y terminales de esa carpeta cerrados; no afecta al nombre público del sitio.
- No se ha borrado el repositorio remoto feed-geologico ni configurado su redirección.
- La colección bibliográfica es inicial, no una revisión exhaustiva ni una validación científica independiente.

## Comprobación

`pnpm run check` o `npm run check` ejecutan los controles del atlas, laboratorio fluvial y portal. `python -m unittest discover -s tests` comprueba los procesos científicos. Las pruebas del núcleo del monitor se ejecutan desde `production/monitor` con sus dependencias.
