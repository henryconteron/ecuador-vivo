# Ecuador Vivo · contrato del incremento geoespacial

## Alcance y diseño

Se conserva una sola aplicación: SIG analiza; Studio compone; la web pública permite comprobar la evidencia. No se migra a Rust, no se instala GeoLibre completo y no se publica automáticamente.

Referencias consultadas: GeoLibre (capas, vistas y procesamiento separado), RustGIS (comandos y contexto), Layout Composer (objetos vinculados y composición cartográfica), Climattic (mapa, fecha, anomalía y comparación regional). Implementación propia, sin código ni arte de esos proyectos copiados en este incremento.

1. Reproducción SIG: precarga corta y caché de presentación limitada; nunca una caché de resultados científicos. Fecha e imagen se cambian juntas, se conserva el último cuadro válido ante error. Límites: cuatro observaciones, 24 MiB de imágenes decodificadas, 30 segundos; invalidación por proyecto, representación y dirección de observación.
2. Evidencia: paquete publicable separado del proyecto privado. Solo transferencias activas; las series sin estadísticas verificadas lo declaran y no heredan cifras de lluvia. No exportar rutas locales ni credenciales en los archivos públicos.
3. Interfaz: navegación compacta, barra de herramientas por tareas, jerarquía de capas, estado de la serie, inspector y panel de resultados; mapa como área dominante. Controles reales, teclado y estados vacíos. No añadir botones de funcionalidades inexistentes.
4. Web: entrada editorial a historias con mapa y evidencia, sin convertir el sitio público en el editor privado. Conservar los casos, datos y licencias existentes.

## Verificación

Pruebas de caché (reutilización, coalescencia, caducidad, límites y liberación); paquetes con temperatura/lluvia y rechazo de resultados inactivos o productos alterados; typecheck/build del componente; pruebas de portal; revisión local visual con permiso expreso del usuario. No alterar los pilotos originales para probar.

## Afinado con geomaster y frontend-design

Dirección: mesa cartográfica ecuatoriana, no catálogo de tarjetas SaaS. El mapa es el documento; los controles forman un marco compacto y los resultados una libreta inferior. Se preservan las referencias oscuras/mint del usuario en SIG/Studio y la identidad editorial existente de la web, no se impone otra marca.

Tokens: océano `#07151d`, panel `#0e202a`, línea `#2b4654`, texto `#f3f7f9`, secundario `#b0c6d0`, acción `#58e4ce`. Tipografía de sistema existente para controles; Newsreader ya existente en la web para relatos. Etiquetas de tareas en sentence case; números tabulares solo donde ayudan a comparar fechas y valores. Alineación izquierda; cero movimiento automático decorativo. Acento reservado a selección, reproducción y envío.

La crítica al primer pase detectó dos cosas: la miniatura de capa no debe usar una paleta inventada, y «Resultados» no debe presentar estadísticas de otra serie. Se corrigen en presentación sin alterar el registro científico. Se muestran CRS, dimensiones, paso de celda en las unidades nativas, NoData y calibración; jamás se equiparan grados a kilómetros. La interfaz no recalcula estadísticas ni lee TIFF completos en un rerun.

## Qué quedó implementado

- SIG: barra de tareas, árbol buscable con agrupación temporal, inspector de datos/procedencia y resultados vinculados a la selección. Paletas del dato, no gradientes ficticios. Paneles móviles, estado accesible y salida con dimensiones adaptativas; sin prometer equivalencia con QGIS/ArcGIS.
- Reproducción: caché exclusivamente de presentación, precarga de dos fechas, coalescencia de solicitudes, invalidación por revisión y liberación de URLs. Se cotejan fecha y SHA del original servido. Una respuesta atrasada ya no cambia el nuevo proyecto ni una vista cerrada.
- Studio → Exportar → Preparar evidencia para Andes Pulso. Solo MP4 final correspondiente al documento, originales y calendario; se vuelve a calcular lluvia desde fuentes nativas antes de incluir sus métricas. Una serie genérica sin estadísticas no se presenta como lluvia ni recibe cifras inventadas. ZIP separado del paquete privado antiguo; no incluye `project.json`, rutas locales ni tokens.
- Panel privado → Catálogos y videos → Studio → Andes Pulso. Importar valida ZIP, nombres, calendario, PNG/MP4, tamaños y huellas; no extrae rutas arbitrarias, enlaces ni ejecutables. Guarda en `_local/site-admin/studio-drafts/<id>`. Reimportar es idempotente; un contenido diferente no sobrescribe el borrador.
- Incorporar a la web es otra acción con casilla de revisión científica/derechos. Verifica de nuevo los archivos y escribe `data/cases/studio/<id>` y un índice independiente. No toca los cinco casos del registro existente ni publica en GitHub. Los controles de Git ya existentes siguen separados.
- Andes Pulso: nueva libreta pública con video, mapas por fecha, escala compartida, estado explícito de cobertura/NoData, resultados, método, fuentes/licencias y descargas. Carga mapas bajo demanda y verifica su huella antes de mostrarlos. No reproduce automáticamente ni consulta fuentes remotas nuevas. El índice empieza vacío: ningún piloto ni caso de prueba fue presentado como publicación real.

## Cómo probarlo

1. Abrir Ecuador Vivo en `http://127.0.0.1:8534/` y recargar para cargar el componente nuevo. Usar un proyecto propio o piloto; seleccionar datos/territorio en SIG y enviar a Studio.
2. Terminar y exportar MP4. En Exportar, preparar evidencia y después descargar el paquete público. Si cambian originales, documento o video, se exige una nueva exportación. El paquete antiguo `andes-pulso.zip` es privado: **no usarlo para subir evidencia pública**.
3. Abrir el panel personal en `http://127.0.0.1:8511/`. Importar el ZIP como borrador, revisar sus fechas, fuentes, cobertura y métricas. Las huellas comprueban integridad, no revisión científica independiente.
4. Solo cuando corresponda, marcar la revisión e incorporar a la web local. Consultar Andes Pulso desde Vista previa del panel. Publicar en GitHub sigue siendo una decisión posterior del propietario.

Límites: imágenes públicas hasta 64 MiB en conjunto, video hasta 96 MiB, metadata hasta 2 MiB, ZIP hasta 160 MiB; no se truncan fechas para cumplirlos. Historias largas pueden necesitar alojamiento externo, todavía no configurado en este flujo. El paquete conserva representaciones, método y huellas de originales; no duplica todos los TIFF y no permite reproducir un cálculo sin conseguir los originales. No se habilitó publicación, ni transferencia masiva a Drive, ni nuevos conectores autenticados. La evidencia nueva funciona con las series SIG de rásteres selladas actuales; los pilotos ilustrativos/ENSO o montajes sin esa transferencia requieren un adaptador propio, no métricas forzadas.

## Verificación de cierre, 13 octubre 2026

- 22 pruebas focalizadas Python de presentación/interacción/SIG/evidencia aprobadas; además cuatro de soporte nativo (grados vs metros, rotación, CRS ausente y resultados de otra serie). Suite del panel: 22 pruebas aprobadas, incluido el borrador importado en estado de solo lectura sin volver a leer/hashar todos los medios en cada rerun.
- Flujo real de prueba: dos TIFF sintéticos → SIG → MP4 1080×1920 → ZIP público → importación privada. Cambio posterior del TIFF rechazado. Ningún dato sintético se conserva en catálogos públicos.
- Cinco pruebas de caché aprobadas. TypeScript y compilación de OpenLayers aprobados. Suite de la web: 35 archivos descubiertos, 29 entradas, todos aprobados; incluye 17 medios/archivos preservados y 2661 registros del caso sísmico existente.
- Prueba de mutación: invertir el requisito de revisión hizo fallar su prueba; restaurado y suite aprobada. Sintaxis Python/JavaScript y diff sin errores de espacios.
- Aviso de Vite 8.0.10 resuelto con parche 8.0.16, misma línea de versión: [aviso oficial](https://github.com/advisories/GHSA-fx2h-pf6j-xcff), [release](https://github.com/vitejs/vite/releases/tag/v8.0.16). Lockfile revisado; instalación `npm ci --ignore-scripts`, compilación y auditoría completos correctos. Auditorías npm del componente y pnpm del portal: cero avisos conocidos; no equivalen a auditoría integral de Python, Blender o toda la aplicación.
- Usuario autorizó la revisión local, pero CUA denegó la apertura por preferencia guardada. **Sin screenshots, revisión de DOM ni aprobación visual/responsive en navegador. No se eludió usando Playwright ni otro navegador.** Las pruebas offline no sustituyen esa aceptación.
- Reinicio autorizado, sin trabajos activos; Ecuador Vivo 8534 y panel privado 8511 responden health 200. No se abrió ninguna pestaña. Pilotos/autoguardados preservados, sin limpieza, commit, push ni publicación.

## Referencia del procedimiento geoespacial

Geomaster aportó las comprobaciones de CRS/unidades, calibración y separación entre representación y análisis. Se consultó el registro vigente (v2, 2 septiembre 2026) antes de citar: Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026). *Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents*. [doi:10.48550/arXiv.2609.00065](https://doi.org/10.48550/arXiv.2609.00065). Referencia del procedimiento, no certificación de los resultados ni evidencia de precisión de la aplicación.

## Fuentes de referencia

- https://github.com/opengeos/GeoLibre
- https://github.com/opengeos/RustGIS
- https://github.com/Defani/Layout-Composer
- https://github.com/taylor-geospatial/s2-stac-geoparquet
- https://dynamical.org/catalog/
- https://www.facebook.com/61592473967530/videos/pcb.122122963329415798/1618208803333707

Conectores remotos y herramientas adicionales deben tener validación y prueba propias. La existencia de un servicio no confirma su cobertura, resolución, licencia ni disponibilidad para Ecuador.
