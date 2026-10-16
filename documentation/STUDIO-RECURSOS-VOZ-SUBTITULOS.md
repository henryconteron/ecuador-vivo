# Recursos, voz y subtítulos · Ecuador Vivo Studio

Entrega local del 12 de octubre de 2026. Es la misma aplicación, proyecto y exportador: no hay otro laboratorio ni entorno instalado.

## Cómo usarlo

1. Abre **http://127.0.0.1:8534/** y elige un proyecto en Inicio.
2. En **Recursos**, elige una explicación, título, acento y duración. Puedes añadir una escena nueva o superponerla a una escena existente. Al confirmar vuelves a Studio; las formas y textos siguen siendo elementos editables. La galería también funciona sin proyecto, pero solo crea uno cuando confirmas.
3. En Studio, abre **Voz y subtítulos**, debajo de la biblioteca de capas. En **Voz**, importa MP3/WAV/M4A o selecciona Micrófono y concede el permiso de grabación en tu navegador. Escucha el original y pulsa **Añadir voz al video**.
4. Ajusta inicio global, duración, recortes, volumen, silencio o repetición. **Guardar pista** conserva el montaje; **Quitar pista** no borra el audio original. Hasta 16 pistas, archivos de 100 MB y videos de dos horas como máximo.
5. En **Subtítulos**, importa SRT/VTT (UTF-8, máximo 2 MB) o añade filas manuales. Inicio y final se escriben en **segundos desde el comienzo del video**, no desde la escena. Los intervalos deben estar ordenados y sin solaparse. Activa **Mostrar subtítulos en el video** y pulsa **Guardar subtítulos**.
6. Abre **Tipografía, posición y fondo** para cambiar tamaño, caja, alineación, colores y borde. X, Y, ancho y alto son porcentajes del lienzo; el tamaño del texto es porcentaje de su altura. Si una frase no cabe en dos líneas, se rechaza el cambio: divídela o amplía su caja. Puedes descargar SRT y VTT por separado.
7. Cierra el panel y revisa el lienzo. **Reproducir** prepara el montaje audiovisual de calidad reducida; **Exportar** produce el MP4 con resolución final, voz mezclada y subtítulos incorporados.

## Biblioteca inicial

| Recurso | Útil para |
| --- | --- |
| Una idea a la vez | Guiar la mirada y explicar una leyenda |
| Temperatura a 2 m | Distinguir altura sobre suelo y altitud |
| 1 mm de lluvia | Entender volumen de agua y acumulación |
| Comparar el mismo periodo | Comparar años sin confundir fechas ausentes con cero |
| Una provincia no es su capital | Explicar mapas de celdas y promedios territoriales |
| Anomalías y regiones Niño | Explicar observado menos referencia y distinguir Niño 1+2/3.4 |

Todos son **esquemas ilustrativos 2D**, no mediciones ni mapas de temperatura del mar. Sus fuentes primarias (NASA POWER, USGS, NOAA, CF y Esri) están en la galería y en los metadatos de la escena. No recalculan ni sustituyen resultados científicos.

## Sincronización y precauciones

- Voz y subtítulos comparten tiempos globales cuantizados a 30 fps. Un subtítulo se muestra desde su inicio, incluido, hasta su final, excluido. Las pistas nuevas usan el mismo redondeo; el comportamiento de los clips anteriores no cambia.
- Reordenar escenas **no desplaza automáticamente** la voz ni los subtítulos. Revisa la sincronización después de cambiar el montaje. Si acortas el video y una pista o subtítulo queda fuera, primero ajusta esos tiempos.
- La voz se mezcla con el audio activo de los clips. El limitador evita sobrepasar el pico de salida; no sustituye una buena grabación. La escucha del panel es del original; **Reproducir** permite escuchar el montaje editado.
- Los subtítulos se ven también en el lienzo como una superposición no seleccionable. Su posición se edita en el panel, no arrastrando esa superposición. No hay una posición universal: comprueba que no tapen mapas, métricas o créditos y que no queden bajo los controles de TikTok/Instagram.
- Grabar o importar voz no la envía a un servicio externo. No se ha incorporado transcripción automática ni generación de voces. El ASR local existente se conserva para una ampliación posterior.
- No hay modelos 3D nuevos todavía. Esta entrega establece primero el recorrido 2D → montaje → voz/subtítulos → MP4.

## Verificación y límites de esta entrega

Pruebas del motor de subtítulos, importación de audio, mezcla AAC, guardado real, reapertura, deshacer/rehacer, caché, render y formularios. Recursos comprobados en ocho perfiles. MP4 vertical real con subtítulos y audio de prueba decodificado y comparado con el render. La demo de nueve segundos está en `_local/resource-development-20261012/demo/recursos-demo.mp4`; no incluye narración inventada y no aparece como proyecto activo.

Los ocho pilotos originales y sus MP4 se han revalidado sin modificarlos. Se preserva también cualquier nuevo autoguardado del usuario. No se crearon borradores de pruebas en proyectos activos, no se instalaron dependencias ni se publicó en GitHub.

La revisión de interfaz en navegador sigue pendiente: el acceso automatizado fue denegado y no se eludió. Los formularios se probaron con Streamlit AppTest y las imágenes del render se inspeccionaron localmente; eso no equivale a verificar todas las interacciones y tamaños en un navegador real.
