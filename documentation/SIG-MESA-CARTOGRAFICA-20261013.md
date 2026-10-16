# SIG: mesa cartográfica, no formulario

## Contrato visual

El incremento sustituye el marco visual del SIG, sin migrar el motor OpenLayers ni tocar importaciones, fuentes, cálculos, máscaras, fechas, guardado o exportaciones. Mantiene un solo mapa y un solo reloj temporal.

Referencias: [paneles y barras de QGIS](https://docs.qgis.org/3.40/en/docs/user_manual/introduction/qgis_gui.html), [cinta contextual y paneles de ArcGIS Pro](https://doc.esri.com/en/arcgis-pro/latest/get-started/user-interface.html), [GeoLibre](https://github.com/opengeos/GeoLibre) y [RustGIS](https://github.com/opengeos/RustGIS). Se adapta su organización, no sus marcas, código ni imágenes. No se anuncia equivalencia de capacidades.

La primera propuesta mantenía demasiados botones iguales y acumulaba reglas CSS que se contradecían. Este pase cambia la estructura: navegación de aplicación / tareas contextuales / mapa y paneles redimensionables / transporte temporal / libreta de resultados. No se añade otro mapa, preview de un video ni tarjetas decorativas.

Paleta propia conservada: océano `#081b26`, panel `#142c38`, panel elevado `#1c3946`, línea `#355363`, texto `#edf4f7`, secundario `#afc4ce`, selección `#60d5c4`. Tipografía: Segoe UI disponible localmente, 12–14 px en controles; nombre del proyecto 14 px, sin encabezados gigantes. Iconos vectoriales locales, sin emojis ni fuentes remotas. La única paleta multicolor pertenece al dato.

En escritorio el mapa domina entre Capas y Propiedades; divisores se ajustan con arrastre o teclado. En anchos estrechos los paneles se convierten en cajones superpuestos, con foco y cierre mediante Escape. La tabla inferior puede ampliarse/contraerse. Cambiar tarea o tamaño de panel es presentación local: no guarda documentos ni recalcula datos. La escala cartográfica, cuando se muestra, describe la vista, no precisión o resolución científica.

## Verificación prevista

Modelo de tamaños y tareas con pruebas unitarias; contrato HTML sin IDs repetidos; typecheck/build; pruebas de transporte/capas/SIG y de presentación científica existentes. Navegador local sigue denegado por una preferencia guardada aunque el usuario dio permiso; no se usarán capturas headless ni otro navegador para eludirlo. La aceptación visual permanece pendiente y no se confunde con pruebas de estructura.

Repositorio con trabajo previo sin commit: no incluir cambios ajenos en un commit global ni borrar versiones/datos como parte de este rediseño.

## Implementación y cierre

- Cinta contextual con Mapa / Análisis / Serie temporal / Salida; cambio de tarea enteramente local, sin reruns ni cálculos. Cada botón conserva su función existente.
- Capas compactas con contador, buscador, símbolos/paleta real y acceso a propiedades; propiedades separadas de la navegación. No se añaden herramientas inexistentes para llenar la pantalla.
- Divisores de capas, propiedades y tabla con arrastre y teclado (flechas, Shift, Inicio/Fin); tamaños limitados para dejar espacio al mapa. Ocultar un panel recupera su espacio. Restablecer paneles no modifica el proyecto.
- Tabla ampliable/contraíble; selección de entidades desde un botón accesible en su primera columna. Paneles móviles mutuamente excluyentes, cierre con Escape y retorno del foco.
- Iconos SVG propios/locales en lugar de glifos inconsistentes. Escala con el control nativo de OpenLayers, solo cartográfica; norte fijo corresponde a la vista sin rotación. No cambios en datos, curvas, métricas o plantilla del video.
- Se consolidó el CSS del marco en `workbench.css`, conservando los estilos del motor/mapa. No se borraron proyectos, fuentes ni artefactos anteriores. Nuevos archivos de componente `sig-workbench-v1.js/.css` seleccionados explícitamente en Python, para no depender del bundle anterior en caché ni cargar dos hojas con el mismo glob.
- Estado de paneles/tarea por instancia, no en el documento científico; observador liberado al desmontar. Cambios de tamaño agrupados por frame; no se vuelven a descargar datos. Sin nuevas dependencias.

Pruebas: 41 pruebas Python focalizadas SIG/capas/interacción/presentación/soporte/contrato HTML aprobadas; once de frontend (seis del modelo de mesa, cinco de caché), typecheck, compilación y auditoría npm aprobados. Mutar el valor de tarea por defecto hizo fallar su prueba; restaurado. Sin prueba de interacción DOM, de responsive real o captura de navegador: esas aprobaciones no se deducen de los tests de geometría.

Instancia 8534 reiniciada después de comprobar ausencia de renders activos; health 200. Panel privado 8511 no tocado. El usuario eligió enviar una captura del SIG actualizado; pendiente recibirla para la crítica visual. Recargar con Ctrl+F5. No hubo commit, push ni publicación.

Alcance de este pase: marco profesional y organización del SIG. No significa que se hayan replicado todos los algoritmos de QGIS/ArcGIS, cambiado a Rust, creado vistas 3D o sustituido OpenLayers por GeoLibre.
