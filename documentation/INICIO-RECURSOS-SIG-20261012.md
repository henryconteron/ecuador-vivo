# Inicio, Recursos y SIG · contrato de esta mejora

## Objetivo

Entrar y trabajar sin esperar un render de video ni rellenar primero un formulario de proyecto. Inicio presenta los tres espacios del mismo documento, con creación/apertura al comienzo. Recursos utiliza el lienzo ya existente para editar diseños reutilizables, sin un editor paralelo.

## Dirección visual

- Paleta existente: fondo tinta `#0c1b24`, superficies `#112b36`, texto `#edf5f7`, texto secundario `#b8cbd1`, acento turquesa `#58e4ce`, líneas `#33515e`.
- Tipografía: la familia del tema para controles; Barlow/Barlow Condensed cuando estén disponibles para encabezados editoriales. Sin fuentes remotas nuevas.
- Navegación compacta; encabezado alineado a la izquierda y acciones Crear/Abrir antes de las tarjetas. Tres portadas decorativas ligeras para SIG/Studio/Recursos; no mapa simplificado ni fotograma de un piloto usado como portada.
- Formulario de creación/importación junto a las acciones superiores, no bajo el catálogo. Biblioteca reciente con búsqueda y paginación; miniaturas optativas.
- Tres columnas en escritorio, una columna en móvil; focos visibles, texto real sin truncar, controles nativos y mensajes de trabajo localizado. No ocultar el estado gris de Streamlit con CSS: eliminar el trabajo que bloquea la interfaz.

## Aceptación

- Inicio no llama al renderizador de un proyecto para crear una portada. Ninguna creación, descarga o exportación ocurre al solo visualizar Inicio.
- Abrir SIG sin documento crea una copia de trabajo vacía al pulsar, con referencias existentes, sin imponer un nombre ni un diálogo inicial. Guardado sigue el mecanismo existente del workspace; no se borran proyectos.
- Crear/Abrir están antes de los espacios. Recursos tiene portada propia y puede crear un diseño vacío o desde plantillas y editarlo en el mismo lienzo.
- Rendimiento comparado antes/después con el mismo procedimiento. Integridad de originales, NoData, máscara, metadatos y cálculo se conserva. No cambiar de motor por conjetura ni copiar código externo sin obligaciones de licencia.
- Pruebas de comportamiento con AppTest, regresiones de render y compilación. Navegador automatizado denegado en la sesión anterior: no eludirlo; no declarar DOM/responsive visualmente comprobado en navegador.

## Fuera de este incremento

No se promete paridad con QGIS/ArcGIS, editor 3D completo, nuevos proveedores de datos o transcripción automática. Se conservan los motores actuales y se mejoran los cuellos medidos.

## Implementación y uso

1. Inicio: Crear proyecto, Abrir proyecto, Usar plantilla y Desde datos aparecen antes de SIG/Studio/Recursos. Abrir SIG sin proyecto abre un borrador de trabajo con las referencias existentes. Ya no pide primero configurar un proyecto. Los proyectos guardados siguen en el catálogo buscable y paginado; las miniaturas son optativas.
2. Recursos: Plantillas, Mis recursos y Crear desde cero. Seis explicaciones 2D reutilizan el renderizador existente; el lienzo vacío permite dibujar con texto, formas e imágenes. Editar una plantilla abre un documento independiente; la copia de trabajo del video anterior se guarda antes del cambio, sin convertir ese video en un recurso.
3. Lienzo: Formas y símbolos ofrece 21 elementos del motor existente. Mover, redimensionar, agrupar, ocultar, borrar, animar y añadir multimedia conservan las herramientas de Studio. Guardar recurso guarda una copia de la escena seleccionada en Mis recursos. Reabrir edita una copia; Añadir al proyecto actual inserta una escena con identificadores propios y ajuste proporcional al formato de destino.
4. Biblioteca: las escenas científicas con mapas/resultados vinculados no se guardan como ilustraciones desconectadas. Los videos, fuentes, métricas y archivos originales permanecen en su proyecto. Voz, subtítulos y otras escenas no se copian a un recurso reutilizable; las imágenes/clips referenciados sí, con clips silenciados. Las pistas globales del video de destino se conservan al insertar.

La biblioteca no incluye todos los recursos de Canva: esta entrega ofrece plantillas propias, gráficos locales y el mismo editor de escenas, no un segundo motor ni un servicio externo.

## Rendimiento medido

- Inicio cargaba motores de datos/descarga/render aunque no hubiese un documento abierto y preparaba un fotograma de video para la portada de Studio. Ahora muestra imágenes WebP estáticas y aplaza esos motores hasta su ruta de uso. No se borra la caché global de otras sesiones al iniciar una nueva.
- AppTest, tres procesos nuevos y tres reruns por proceso: mediana de Inicio en frío **4,632 → 2,430 s**, reducción aproximada **47,5 %**. Mediana de reruns **0,463 → 0,322 s**. La última serie no abrió proyecto ni cargó los motores pesados observados; cero excepciones. Esto mide ejecución del servidor, NO tiempos LCP/INP del navegador. Windows, OneDrive y carga simultánea pueden cambiar los tiempos reales.
- Informes reproducibles: `_local/performance-20261013/startup-before-full-home.json` y `startup-final-full-home.json`, obtenidos con `dev/studio_startup_profile.py`. El nombre histórico de esa carpeta no representa la fecha de esta entrega.
- SIG: cambiar opacidad de 30 observaciones repetía 30 copias/validaciones completas. Se agrupa en una transacción, sin omitir el validador ni las verificaciones del original. Medición focalizada previa al cierre, tres repeticiones: mediana **22.137 → 937,6 ms**; la prueba comprueba equivalencia exacta del documento con el método anterior. No es una promesa de ese tiempo para toda interacción SIG.
- La representación PNG ya almacenada se reutiliza sin otra compresión. Se siguen verificando los bytes/metadatos originales en cada solicitud; máscara, soporte nativo, NoData, fechas, unidades y cálculos no se modifican. Caché de imágenes limitada a ocho entradas/8 MiB. Las vistas de la biblioteca se renderizan a tamaño de previsualización, no a Full HD para después reducirlas.

## Referencias y decisión de motores

Se revisó [GeoLibre](https://github.com/opengeos/GeoLibre): su arquitectura MapLibre/React y procesamiento local no equivalen a una prueba comparativa de velocidad en esta computadora. Se tomó el criterio de trabajo ligero en la interfaz y carga bajo demanda; no se copió código ni se sustituyó a ciegas OpenLayers, Rasterio o el exportador. La documentación de [ArcGIS para datos densos](https://developers.arcgis.com/javascript/latest/visualization/high-density-data/) distingue estrategias de presentación y tamaño de datos. QGIS se conserva como referencia de organización; su página oficial consultada no estuvo accesible por la herramienta web en esta sesión, por lo que no se atribuyen nuevas optimizaciones a una verificación de esa página.

Las herramientas analíticas ya existentes se mantienen. No se han añadido mil herramientas, otro laboratorio, DuckDB-WASM, MapLibre, Cesium ni dependencias nuevas por esta comparación.

## Verificación final

- 137 pruebas focalizadas aprobadas en 251,685 s: Inicio/catálogo/arranque, rutas reales de Recursos con almacenamiento temporal, creación/edición/inserción/guardado de diseños, plantillas, comandos y render de Studio, voz/subtítulos, preservación de calendarios, capas/raster/series/máscaras/caché/protocolo y presentación SIG. Primera pasada detectó un selector de test obsoleto de NASA POWER, corregido al selector real; no se alteró el descargador para hacer pasar el test.
- TypeScript `typecheck` y `build` correctos con dependencias ya instaladas. Sintaxis JavaScript compuesta del lienzo correcta. `git diff --check` sin errores; solo avisos de LF/CRLF del trabajo existente.
- Mutación en memoria del guard de ilustraciones: retirar la prohibición de guardar un mapa científico como recurso hizo fallar la prueba correspondiente. El guard quedó intacto en disco.
- Guard posterior: ocho pilotos válidos, hashes de películas/recibos correctos, cero referencias directas ausentes y cero problemas de parseo. Informe `_local/maintenance/cleanup-20261011-pilot-guard/after-home-resources-20261012.json`. Los diez JSON activos actuales incluyen dos autoguardados anteriores a esta reanudación; se preservaron, no se fuerza el catálogo a ocho archivos.
- Revisión visual offline de las seis plantillas renderizadas en `_local/resource-development-20261012/plantillas-biblioteca.png`. No es una captura del navegador. Pruebas AppTest verifican comportamiento del servidor; la aprobación visual de responsive/DOM en navegador continúa pendiente por la denegación anterior. No se ha intentado eludirla.
- Guías de Streamlit aplicadas: contenido ligero primero, motores diferidos, formularios explícitos, controles nativos, caches limitadas y un único lienzo. Las portadas creadas, sus prompts y destinos están en `documentation/PORTADAS-ECUADOR-VIVO-20261012.md`.
- Sin nuevas dependencias, modelos descargados, limpiezas, commit, push ni publicación web. Esta entrega sustituye la apariencia de Inicio y amplía Recursos; no modifica los datos originales ni promete un SIG equivalente a QGIS/ArcGIS.
- Studio 8534 reiniciado de forma dirigida después de comprobar identidad de sus dos procesos y ausencia de exportaciones activas: nueva pareja 16856/21548, 12 octubre 02:23 Guayaquil. Health 200, errores 0 bytes. Panel web 8511 conservado y health 200. Recargar la página; no se abrió otro navegador ni otra instancia.
