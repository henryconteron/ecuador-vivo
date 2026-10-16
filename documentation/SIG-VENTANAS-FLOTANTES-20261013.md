# SIG: mapa libre y ventanas bajo demanda

## Contrato visual

Referencias: capturas del usuario de SIG, barra histórica de Google Earth y herramientas compactas. No copiar marcas ni añadir botones sin implementación.

Paleta conservada: océano #081b26, panel #142c38, superficie #1c3946, borde #355363, texto #edf4f7, acento #60d5c4. Segoe UI local, controles de 12–13 px, iconos SVG propios.

Una superficie cartográfica a todo el ancho. En la fila superior de tareas se añaden Capas, Referencia, Propiedades y Atributos. Ventanas no modales, cerradas al entrar, desplazables y redimensionables; no reservar columnas ni tabla inferior. Resultados y Mensajes quedan en la misma ventana de tablas.

El control temporal flota solo con una serie preparada. Fecha confirmada, reproducción, pasos anterior/siguiente, acercar/alejar el intervalo visible, extremos reales y configuración existente. Cerrar oculta el control y pausa, no elimina datos. Acercar el intervalo no crea ni interpola observaciones.

Mantener un solo mapa y un solo reloj. Abrir/mover/cerrar ventanas es estado local de presentación: no dispara cálculos ni guardados científicos. Teclado: botones nativos, Escape cierra la ventana enfocada, cabecera movible por flechas, Shift aumenta el paso. En ancho pequeño, paneles ajustados al contenedor.

La preferencia del navegador sigue bloqueando revisión automatizada; no sustituirla con otro navegador. Capturas recibidas sirven como referencia inicial, no como prueba del resultado nuevo. Verificación: pruebas de estructura, geometría local, regresión y compilación. No commit global: árbol contiene trabajo previo del usuario.

## Resultado implementado

Cuatro accesos de ventanas junto a las tareas, controles cerrados al entrar, tabla flotante con ampliar/restaurar. Capas, Referencia y Propiedades también flotan y tienen redimensionado por esquina o Ctrl+flechas desde su título. Escape restaura el foco al acceso correspondiente. Estado aislado por instancia y observadores liberados al desmontar.

Control temporal compacto sobre el mapa: aparece con `raster_time.layers`, muestra la fecha y extremos originales, pasos anterior/siguiente, reproducción/pausa, zoom del intervalo de observaciones, configuración del periodo existente y comparación cuando hay exactamente dos observaciones. Al cerrar se pausa, sin quitar la serie; el acceso Control temporal permite recuperarlo. La cinta superior conserva análisis vectorial, ráster y estadísticas, formato/encuadre y envío a Studio. No se añadieron iconos falsos de funciones de Google Earth no implementadas (regla, inclinación 3D o visitas guiadas).

Bundle activo explícito: `sig-workbench-v2.js` y `sig-workbench-v2.css`. Sin dependencias nuevas ni cambios en cálculos/datos/plantilla de video. Antiguos bundles conservados pero no registrados.

42 pruebas Python SIG focalizadas aprobadas; 19 pruebas frontend (modelos, caché y controlador con nodos de prueba, no navegador); typecheck y compilación correctos. Prueba de mutación en el límite de dos observaciones falla como corresponde y fue restaurada. Sin push, publicación ni eliminación de datos. La aceptación visual del resultado todavía requiere captura posterior a recargar.

## Corrección del recorrido de datos (bundle vigente v3)

La siguiente captura mostró el marco v2 actualizado, pero 30 archivos superpuestos y ningún reloj. La descarga todavía terminaba en admisión, no en activación: se corrigió el recorrido y el clic de capa fechada. No atribuir el fallo a caché.

Descargar/importar activa el reloj; cierre del diálogo y vuelta al mapa. El borrador real de las 15:21 contiene 30 observaciones de precipitación corregida de NASA POWER, no temperatura. Recuperación comprobada sin escribir ni descargar datos. Al abrir SIG, solo se repara automáticamente una descarga antigua de producto único, fechas válidas, variable/unidad compatibles y tags de admisión verificados; conserva cálculos y fuentes, permite deshacer y no reintenta durante la misma sesión tras deshacer.

Selector nativo para elegir fecha directamente; barra y selector comparten la misma observación. La leyenda solo muestra la fecha presentada; sus observaciones son botones reales, no texto inerte. Al seleccionar fechas de otra fuente se configura solo su grupo compatible.

62 pruebas Python focalizadas aprobadas (incluido AppTest de apertura/selección/render único), 19 frontend y compilación correctos. Guard de recuperación sometido a mutación, fallo detectado y código restaurado. Resultado visual nuevo pendiente de captura. Bundle explícito vigente: `sig-workbench-v3.js` / `sig-workbench-v3.css`.
