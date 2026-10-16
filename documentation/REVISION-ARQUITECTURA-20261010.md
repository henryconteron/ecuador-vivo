# Revisión de Ecuador Vivo SIG y Studio — 10 octubre 2026

## Decisión

Conservar el motor científico Python, el proyecto compartido, OpenLayers y el editor de composición existentes. No hay evidencia suficiente para justificar una reconstrucción completa o cambiar de framework ahora. Cerrar la interacción y presentación del SIG como primer recorrido aprobado; después aplicar el mismo criterio a Studio.

Las correcciones realizadas después del análisis anterior mejoran el producto. La atenuación de Streamlit, la pérdida del nombre/historial y el calendario al retornar del preview ya cuentan con correcciones y evidencias. La lentitud, el acabado visual y el video de temperatura siguen abiertos. No declarar una v1 final.

## Alcance y verificación de esta revisión

Se leyeron ambos registros entregados por el usuario, los cambios actuales de producción y los informes de opacidad, edición, datos y cierre. Se contrastaron con el diagnóstico anterior. Se revisó la captura `tmp/ux-redesign/v1-definitive-editing-1791608173270946900.png`.

Se verificaron los hashes SHA-256 de las tres respuestas POWER conservadas contra `tmp/v1-definitive-power-probe.json`: coinciden. `git diff --check` y `git apply --check documentation/v1-usable-gitignore-proposal.diff` terminaron correctamente; la propuesta no se aplicó.

El registro existente declara 29 pruebas OK en 5,073 s. Esta revisión inspeccionó la regresión y su evidencia, pero no confirma una nueva ejecución de las 29: el intento local no produjo resultados y se interrumpió. No se realizaron nuevas mediciones del navegador ni nuevas consultas al proveedor. Los datos de disponibilidad describen las respuestas guardadas, no una comprobación de disponibilidad en tiempo real.

## Hallazgos resueltos y límites

| Tema | Evidencia y conclusión |
|---|---|
| Atenuación | `host.css` limita la regla al contenedor del editor. La evidencia recuperada contiene 4250 muestras, mínimo 1 y 1642 muestras stale; el contraste sin CSS vuelve a 0,33. Es una corrección de presentación válida con el indicador propio de guardado. No demuestra edición rápida ni ausencia universal de problemas visuales. |
| Nombre e historial | `show_workspace` usa la proyección actual de la sesión canónica antes de crear `WorkspaceSession`. La regresión comprueba nombre en memoria, payload y disco, versión e historial. El problema fue real, no únicamente un selector de prueba. |
| Undo/Redo | El recorrido guardado verifica los transforms: inicial (46,157,1156,796), desplazado (76,167,1156,796), Undo inicial, Redo desplazado. No extrapolar a toda combinación de acciones. |
| Calendario | `editMode()` restituye el cuadro del lienzo y llama a `clock(frame)`. Evidencia de retorno: cuadro 0 y fecha 2024-01-01. |
| Recargas | `app.py` condiciona las recargas a `ECUADOR_VIVO_DEVELOPMENT_RELOAD=1`; el lanzador normal elimina esa variable y desactiva el observador. Conservar esta separación. |
| Documentación | Existe `documentation/ESTADO.md` breve y los históricos tienen aviso. Los documentos nuevos y `dev/` aparecen sin seguimiento en Git; crearlos localmente no equivale a publicarlos en el repositorio. |

Mi recomendación anterior de evitar cualquier CSS contra la atenuación fue demasiado rígida. La evidencia identifica el efecto del framework y justifica la regla acotada; todavía hace falta abordar su duración.

## Arquitectura: qué está frenando el editor

**Prioridad 1 — confirmar una edición aún depende de preparar la presentación.** En `studio_workspace.py`, `WorkspaceSession.commit()` construye `PreparedTimeline` y solicita miniaturas antes de `save_snapshot()`. `show_workspace()` vuelve a preparar timeline, lienzo, miniaturas, preview y calendario antes de entregar el componente. Ya hay cachés: el hallazgo no es ausencia de caché. La ruta sigue incluyendo trabajo de render y validación; las ventanas stale medidas llegan a 6,0 s en autoguardado y 6,2 s en una ventana de arrastre. Es evidencia de espera, no un perfil que atribuya todos esos segundos a una función.

Remedio: medir por separado validación documental, integridad de recursos, miniaturas, preview y guardado. Mantener la validación necesaria para aceptar y guardar un comando; preparar productos visuales después, por escena afectada. Conservar la última imagen mientras se actualiza y mostrar el reconocimiento del comando sin reconstruir todos los controles. No eliminar comprobaciones de integridad para ganar velocidad.

**Prioridad 1 — reproducir comparte la ruta de exportación.** Las acciones `play` y `export` llaman a `start_studio_job`. La reutilización evita ciertos renders repetidos, pero el primer preview puede requerir el MP4 final completo. El corte anterior documentó aproximadamente 282–515 s para una composición Full HD de 24 s. Hace falta una previsualización de menor coste con el mismo calendario y las mismas fuentes, separada del render final. Es una tarea delimitada; no hace falta reemplazar el motor científico.

**Prioridad 2 — el controlador todavía se reconstruye en cambios documentales.** La firma de `workspace.js` incluye versión, escena y documento. Una firma distinta pasa por dispose/montaje; las mejoras conservan medios y reducen interrupciones, pero el editor aún necesita actualizar controles y elementos por identidad. La estabilidad de un MP4 no acredita fluidez del modo de edición.

**Prioridad 2 — el diseño del SIG depende de widgets y estructura interna de Streamlit.** `studio_sig_map_ui.py` combina mapa propio con paneles y acciones nativas; `sig_map_frontend/workspace.css` modifica contenedores mediante `data-testid`, claves y `!important`. Permite avanzar, pero hace costoso ajustar densidad y estados con precisión. Consolidar la barra, árbol de capas, inspector y franja temporal alrededor del componente OpenLayers existente. Reutilizar el protocolo de comandos y confirmaciones; no crear otro documento, catálogo ni motor.

## Temperatura: el bloqueo científico está bien detectado, pero tiene solución metodológica

Las respuestas conservadas tienen una malla de 0,5° × 0,625°. `_polygon_stats` selecciona por centros de celda (`all_touched=False`). Con esa selección Carchi, Bolívar y Tungurahua quedan sin centros; la comprobación geométrica independiente coincide. Esto no demuestra falta de cobertura espacial del proveedor en esas provincias.

Una posible alternativa es ponderar valores por el área de intersección entre las celdas nativas y cada provincia. Hay que validarla y declararla como una estimación de malla gruesa: no crea observaciones locales ni mayor resolución. No basta con activar `all_touched=True` y dar el mismo peso a cualquier celda tocada. Mantener el método actual como opción documentada. Para una entrega que conserve ese método, presentar las 24 provincias y marcar tres sin estimación, sin introducirlas en el ranking numérico.

La climatología guardada responde 2001–2025, fuente MERRA2 y horario LST; la serie reciente responde GEOSIT y UTC. No constituye la línea base 1991–2020 solicitada. Antes de calcular anomalías hay que verificar periodo base, definición diaria/mensual, horario, malla y cambio de fuente. Descargar y validar la alternativa histórica es trabajo pendiente; no está resuelto por restar dos respuestas API.

El requisito de 61 días y el límite de 32 observaciones por preparación también deben conciliarse. Usar dos clips con escala común y continuidad de fechas es una propuesta compatible con el límite; el recorrido completo no está validado. Un ranking por anomalía debe titularse «más por encima/debajo de lo normal»; «más cálidas/frías» corresponde a temperatura absoluta. Ambas medidas pueden mostrarse con etiquetas distintas.

## Entrega siguiente, acotada

1. Ejecutar la versión actual con recargas desactivadas y una única instancia identificada. El servidor antiguo 8526 no acredita que las correcciones nuevas estén cargadas. No intervenir otros procesos.
2. Cerrar el SIG: mapa central persistente, árbol compacto, inspector con Estilo/Datos/Procedencia, franja temporal única y Enviar a Studio. Ajustar frente a las referencias suministradas con capturas reales a 1366×768 y 1920×1080. Mostrar datos y vacíos con contraste legible.
3. Separar la confirmación del comando de la preparación visual costosa; medir antes y después. El objetivo de diseño puede avanzar en paralelo con este trabajo, sin esperar nuevas fuentes climáticas.
4. Verificar un único recorrido: abrir tres fechas reales → reproducir/pausar/buscar → ajustar escala y formato → guardar/reabrir → enviar → mover texto/mapa → Undo/Redo → exportar. Repetir únicamente ante fallos o cambios pertinentes. Un test de ocho escenas con tres fechas repetidas sigue siendo una prueba de edición, no una serie histórica.
5. Abordar el preview rápido y el video de temperatura con sus decisiones metodológicas registradas. El diseño final y la validez de anomalías son criterios separados.

El éxito de la próxima entrega requiere que la pantalla se acerque a las referencias y que el recorrido sea utilizable. Suites verdes y exportación correcta, por sí solas, no cumplen ese objetivo.

## Cambios de esta revisión

Solo este informe. No se modificaron producción, proyectos, datos, `.gitignore` ni históricos; no se ejecutaron commit, tag, publicación o reinicios. Los resultados anteriores siguen conservados en `documentation/ESTADO.md` y `documentation/V1-CIERRE.md`.
