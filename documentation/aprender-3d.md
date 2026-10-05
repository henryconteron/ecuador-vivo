# Aprender haciendo · diseño y límites

Actualizado: 4 de octubre de 2026. La nueva entrada `learn.html` ofrece tres experiencias bilingües; el contenido documental anterior se conserva en `lecturas.html`, con sus figuras, atribuciones y citas. Los enlaces profundos anteriores se dirigen a ese archivo. No se borraron medios científicos ni se sustituyeron datos por imágenes generadas.

## Diseño educativo

Secuencia: pregunta → predicción personal → manipulación → explicación → reto con retroalimentación → observación escrita. Público inicial: personas sin formación previa en geociencias. Cada modelo tiene tres posiciones accesibles (antes/durante/después), un deslizador continuo, vistas frontal/oblicua/superior y controles de cámara. El reto se habilita al explorar al menos 70 % del proceso; responder mal ofrece una explicación y permite volver a intentar. Resolver los tres no acredita competencias profesionales ni otorga certificado.

Las skills de estructura de cursos y narrativa visual guiaron los objetivos observables, la secuencia corta, el contraste entre condiciones y la retroalimentación. Se evita una animación decorativa sin tarea. El cuaderno pide separar observación, explicación y límites. Las lecturas de campo siguen disponibles, porque un esquema 3D no reemplaza evidencia real.

## Fuentes científicas y alcance por actividad

### 1. Una capa. Dos destinos.

Base: [USGS, What is a fault and what are the different types?](https://www.usgs.gov/faqs/what-a-fault-and-what-are-different-types). Síntesis propia sobre movimiento relativo normal, inverso y de desgarre.

Geometría: bloques rígidos con capas horizontales, plano inclinado 60° o vertical para desgarre. El bloque derecho es el techo en los modelos inclinados. Para deslizamiento `s`, el movimiento normal es `(0.5s, −sqrt(3)/2*s, 0)`; el inverso cambia ambos signos; el desgarre es `(0,0,s)`. Esto conserva la dirección tangente al plano. Unidades arbitrarias, no velocidad o escala de campo. La capa guía blanca se correlaciona inicialmente; en desgarre se añade un marcador superficial transversal.

No simula dinámica de ruptura, esfuerzos, fricción, deformación interna, erosión, recurrencia, magnitud ni peligro sísmico. La reproducción es un control narrativo, no tiempo geológico. No se denomina dextral/sinistral al movimiento sin definir un marco de observación.

### 2. La misma lluvia. Otro río.

Base: [USGS, Impervious Surfaces and Flooding](https://www.usgs.gov/water-science-school/science/impervious-surfaces-and-flooding). Apoya el vínculo entre impermeabilización, menor área de infiltración y escorrentía; **no aporta los coeficientes del juego**.

Balance inventado y explícito: 100 fichas de agua; infiltración = redondeo(capacidad × fracción permeable). La capacidad didáctica es 60 o 20 fichas para contrastar mayor/menor capacidad inicial; escorrentía = 100 − infiltración. La lluvia, el relieve y demás condiciones se mantienen iguales. Colores: azul para ruta superficial y turquesa para entrada al suelo. Las partículas y edificios son símbolos, no resultados hidrodinámicos.

Omite evaporación, almacenamiento superficial, heterogeneidad, intensidades reales y caudal subterráneo. No calcula caudales, tiempos de concentración, niveles, inundaciones ni efectos cuantitativos de una obra en Ecuador. El terreno es una forma matemática, no un DEM.

### 3. La montaña no fabrica agua.

Base: [NOAA/NWS, Orographic lifting](https://forecast.weather.gov/glossary.php?word=OROGRAPHIC), y [NWS, Cloud Development](https://www.weather.gov/source/zhu/ZHU_Training_Page/clouds/cloud_development/clouds.htm).

Parcela conceptual que asciende por barlovento. Contrasta humedad inicial alta/baja, expansión y posible condensación. Montaña gaussiana y umbral visual 0,65 en unidades abstractas; se eligieron para visualizar el concepto, no proceden de un sondeo. La opción seca no satura durante este recorrido, no afirma que aire seco nunca pueda formar nubes. La esfera es un marcador de parcela, no una burbuja real ni una representación del vapor visible. La nube no implica lluvia.

No calcula presión, temperatura, gradientes adiabáticos, punto de rocío, microfísica, sotavento ni pronóstico local. No toda nube es orográfica.

## Tecnología, privacidad y accesibilidad

- Three.js 0.180.0, MIT, distribuido localmente con su licencia. Descargado del registro npm oficial; archivo original verificado contra SHA-512 publicado. No CDN de scripts ni instalación de servicios externos. Registro: [terceros](../assets/vendor/three-r180/PROVENANCE.md).
- Solo se carga un modelo y un contexto WebGL2. Geometrías/materiales se liberan al cambiar de escena. No hay bucle permanente: la reproducción requiere clic y se detiene al ocultar la pestaña, al cambiar de lección o al terminar. Se limita la densidad de píxeles a 2.
- Respeta movimiento reducido: desactiva reproducción, mantiene posiciones y controles manuales. Cámara operable con botones, flechas y arrastre. Las observaciones no se anuncian cada fotograma.
- Sin WebGL2, las descripciones, balance, controles y retos siguen disponibles. Sin JavaScript, se enlazan lecturas documentales. El 3D es un apoyo, no el único medio de explicación.
- El enlace «modo ligero sin 3D» (`view=text`) omite la carga del motor y mantiene las actividades textuales y numéricas; permite probar el recorrido sin GPU.
- Progreso y nota en `localStorage` del navegador, sin cuentas ni envío a servidores. Si está bloqueado, el recorrido sigue funcionando. Se exporta un cuaderno Markdown con fuentes y límites. «Reiniciar retos» no borra la nota.

## Verificación

Pruebas numéricas: signos y dirección de movimiento, invariancia del plano, conservación de las 100 fichas, monotonía con impermeabilización y contraste de condensación. Pruebas de contenido: tres actividades ES/EN, fuentes, respuestas y retroalimentación. Se siguen verificando por separado las figuras y citas de `lecturas.html`.

Pendientes pedagógicos: prueba con lectores reales, revisión docente y experiencias de rocas/minerales más profundas. Este lanzamiento no equivale a validar experimentalmente la eficacia educativa ni a revisar todos los capítulos documentales anteriores.
