# SIG: mapa estable y herramientas de trabajo

## Contrato de diseño

Mesa cartográfica, no formulario a pantalla completa. El mapa es el centro; los
controles persistentes viven arriba y cada operación abre una ventana contextual.

Paleta: océano `#081b26`, panel `#142c38`, superficie `#1c3946`, línea
`#355363`, texto `#edf4f7`, selección `#60d5c4`. Segoe UI para comandos y
formularios, 13–14 px; títulos de ventana 16 px. Alineación izquierda.

```
Proyecto / espacios / guardar
Mapa | Análisis | Serie temporal | Salida     Capas / Referencia / Propiedades
Comandos del grupo activo
┌──────────────────── mapa persistente ────────────────────┐
│ control temporal, si existe         ┌ herramienta ──────┐│
│                                    │ entrada           ││
│                                    │ parámetros        ││
│                                    │ ejecutar / cerrar ││
│                                    └───────────────────┘│
└──────────────────── estado discreto ─────────────────────┘
```

Revisión del brief: no añadir tarjetas, gradientes decorativos ni menús de
capacidades inexistentes. Conservar los acentos del proyecto; reducir títulos
repetidos y formularios expansivos. Los avisos científicos permanecen accesibles.
Paleta temporal compartida, sin alterar valores ni inventar resolución.

## Referencias y alcance

Se estudió la separación entre menús, paneles flotantes y mapa persistente de
[GeoLibre](https://github.com/opengeos/GeoLibre), y los grupos de tareas de
[RustGIS](https://github.com/opengeos/RustGIS). Inspiración de interacción, sin
copiar su código ni afirmar equivalencia funcional o de rendimiento.

La revisión visual del navegador local permanece bloqueada por la preferencia
guardada. Verificación mediante pruebas, compilación y capturas aportadas; no
presentar esto como aceptación visual de la aplicación ejecutándose.

## Medición inicial

Serie local de 30 observaciones: comando de cámara + payload caliente, mediana
1246,6 ms (5 muestras). 182 verificaciones de ráster, cada una reabre GDAL para
leer la receta, incluso con bytes verificados y metadatos calientes. No incluye
guardado del proyecto, comunicación con navegador ni descarga de teselas.

## Entrega

- Caché acotada de recetas GDAL por contenido verificado; metadatos declarados se
  comparan siempre. Pruebas nativas por operación, no persistentes: SHA al entrar,
  identidad/tamaño/mtime/NTFS ChangeTime en reutilización y al salir; se descartan
  al terminar. Se detectan incluso cambios de igual tamaño con mtime restaurado.
- En la misma serie, comando + payload caliente: mediana 172,8 ms (5 muestras).
  Gesto completo con commit, payload y propiedades: 278,0 ms en almacenamiento
  temporal (5 muestras). No son latencia de navegador, FPS ni mediciones de OSM.
  El benchmark `dev/bench_sig_gesture.py --transaction` nunca guarda sobre pilotos.
- Herramientas no modales de 430 px, contenido acotado al alto de pantalla,
  formulario independiente del fragmento del mapa. Apertura de proyectos conserva
  modal pequeño. Cierre por callback, probado en AppTest.
- Un solo acceso Preparar/ajustar serie; engranaje temporal reutiliza ese acceso.
  Paleta y estilo abre el editor existente, no un formulario duplicado.
- Cuatro paletas compartidas: Ecuador Vivo, Viridis, temperatura azul-rojo y
  océano. Conservar nudos, escala, NoData, fuentes y cálculos; aplicación atómica
  con opacidad, historial/deshacer, snapshot y bundle de Studio verificables.
- Bundle activo `sig-workbench-v4.js/css`, registro Python y Vite coincidentes.
  Versiones pequeñas anteriores no se borraron; ya no están registradas.

Validación: 102 pruebas focalizadas de SIG/ciencia/UI y otras 6 de callbacks de
mapa/guardado/deshacer; 19 frontend; typecheck/build y diff-check correctos.
Prueba adicional del componente real y sus assets registrados aprobada en AppTest.
Mutación deliberada que ignoraba la paleta detectada por la regresión y restaurada.
AppTest no es revisión visual. No se ocultó mediante CSS el estado ocupado global:
las esperas largas por descarga/cálculo siguen comunicándose. No se garantiza que
Streamlit nunca muestre actividad; se redujo el trabajo que la causaba al navegar.
Sin cambios de motores, dependencias, publicación, commit, push ni limpieza.
Instancia 8534 reiniciada sin navegador: health 200, sin errores en log inicial.
Solo había estados antiguos `test-*` sin workers; ningún render de la aplicación
activo. Blender de escritorio y panel privado intactos. Recargar para cargar v4.
