# ¿Qué le pasó al río?

Guion conversacional v7. Los títulos organizan la lectura; no se narran.
La apertura del mensaje es una situación imaginaria, no una denuncia recibida.
Las imágenes y la demostración del índice son reales; los ejemplos cotidianos
son analogías. Dirección visual, límites y bibliografía en `RIOS_DIRECCION_V7.md`.

## El mensaje

Imagínate que te llega este mensaje: «Mira lo que le hicieron al río».

Abajo hay dos fotos. En una ves agua. En la otra, unas franjas claras que parecen arena. Y empiezas a unir las piezas: antes estaba bien, ahora está mal, alguien tuvo que hacer algo.

Si es un río que conoces, el mensaje pega distinto. Ya no estás viendo una mancha en un mapa. Estás pensando en el sitio al que ibas, en la gente que vive cerca, en el agua que pasa por ahí.

Pero hay una pregunta que se nos puede escapar entre la primera foto y el botón de compartir: ¿esas imágenes cuentan lo que creemos que cuentan?

Porque las dos pueden ser auténticas… y aun así podemos sacar una conclusión equivocada.

Vamos a abrirlas juntos. Hay algo que podemos comprobar ahora mismo, sin viajar al río. Y algo que, por mucho que acerquemos la pantalla, no vamos a encontrar ahí.

## El lugar donde dejaste los zapatos

Pensemos primero en algo que puedes reconocer sin saber nada de satélites.

Imagínate sentado junto a un río. Dejas los zapatos sobre unas piedras y te acercas al agua. Otro día vuelves al mismo sitio, pero esas piedras están cubiertas. No se fueron a ninguna parte: subió el nivel.

Si tomáramos una foto desde arriba en cada visita, una mostraría más piedras y la otra más agua. El paisaje parecería distinto aunque el lecho siguiera ahí.

Eso puede pasar al comparar imágenes de años diferentes. Una puede coincidir con un nivel más alto y la otra con uno más bajo. El número del año no convierte automáticamente una foto en «antes del daño» y la otra en «después».

Ahora, el río también puede cambiar de verdad sus formas. Transporta arena y grava, erosiona unas zonas y deposita material en otras. Con el tiempo, un brazo puede ocupar otro espacio.

Ahí ya tenemos dos historias distintas: cambió el nivel sobre el lecho, o cambió el propio lecho. A veces ocurren las dos.

Y todavía falta una tercera que ni siquiera sucede en el río.

## Lo que una foto no puede contar

Antes, una cosa: cuando decimos «hay menos agua», ¿qué estamos diciendo exactamente?

Piensa en una piscina. Se ve un montón de agua y, sin embargo, no hay un río atravesándola. Ahora piensa en una manguera: ocupa muy poco espacio, pero está pasando agua todo el tiempo.

No son modelos de un río; sirven para separar dos ideas. Una es cuánto espacio vemos cubierto por agua. Otra, cuánta agua atraviesa un lugar por segundo. A esa segunda la llamamos caudal.

Para medirlo necesitamos conocer la sección por donde pasa y la velocidad del agua. Una foto tomada desde arriba no trae esos datos pegados a las orillas.

Así que una franja más estrecha puede ser una pista de un cambio. No nos entrega, por sí sola, los litros por segundo.

Pero sí podemos empezar por una pregunta más sencilla: ¿qué partes de la imagen podrían ser agua?

## El satélite no sabe que eso es un río

Tú reconoces un río porque has visto muchos: sigues su forma, buscas las orillas, recuerdas cómo se ve el agua.

El sensor del satélite no tiene esa experiencia. Lo que registra es la luz que le llega desde distintas partes del terreno.

Y no se queda solo con los colores que vemos nosotros. También registra ciertas bandas de infrarrojo, fuera de lo que nuestros ojos pueden ver. Una banda es una porción de esa luz que el sensor registra por separado: el verde en una, por ejemplo, y una parte del infrarrojo en otra.

Eso nos interesa porque el agua, la vegetación y el suelo no devuelven la luz de la misma manera. El agua suele dar una respuesta baja en algunas de esas bandas infrarrojas. Podemos aprovechar esa diferencia para buscarla.

No hemos hecho que el satélite entienda qué es un río. Le hemos encontrado una pista en la luz.

## Una fórmula que sí tiene una razón para estar aquí

Para este mapa vamos a comparar dos señales: la luz verde y el infrarrojo de onda corta.

La operación tiene dos partes. Primero restamos una señal de la otra. Después dividimos esa diferencia por su suma. Así calculamos un contraste para cada celda de la imagen.

La herramienta se llama MNDWI: índice de diferencia normalizada de agua modificado.

El nombre es largo. La pregunta que responde es mucho más pequeña: ¿cómo se compara la respuesta en verde con la respuesta en ese infrarrojo?

No estamos contando gotas ni midiendo la profundidad. Tampoco estamos calculando a partir del azul que ves en la pantalla. Primero usamos los valores registrados y procesados; después elegimos colores para mostrar el resultado.

Esto importa porque el azul parece muy convincente. Una vez que pintamos algo como agua, cuesta recordar que antes tuvimos que decidir qué pintar.

Y aquí viene la tercera historia.

## El río cambia… dentro de la computadora

Voy a dejar fija esta observación de 2024. No cambio el día, no cambio el encuadre y no cambio los datos.

Solo muevo una regla.

Primero pintamos de azul las celdas cuyo índice supera cero. Después pedimos que supere cero coma dos. La segunda condición es más exigente: algunas celdas que entraban antes ahora se quedan fuera.

Hay menos azul. Pero no acabamos de sacar agua del río.

Lo que cambió fue nuestra selección.

Estos dos valores sirven para demostrar el efecto; no los hemos calibrado como la regla correcta para este sitio. Para elegirla habría que contrastar el mapa con referencias independientes del terreno, no escoger la imagen que más nos guste.

Ahí está la diferencia entre un dibujo bonito y una medición que puedes defender: poder explicar cómo lo obtuviste y cómo sabes si acertaste.

Ya separamos tres cosas que podían parecer la misma: el nivel, las formas del cauce y la regla que produce el mapa.

## El cuadrado que no puedes atravesar con el zoom

Todavía hay un detalle que suele desesperarnos. Acercas la imagen para ver la orilla… y aparecen cuadrados.

En esta comparación trabajamos con celdas de veinte metros de lado. Imagina poner sobre el terreno un cuadrado de ese tamaño. Dentro puede haber un pedazo de río, unas piedras y vegetación.

La medición de esa celda puede mezclar las respuestas de esas superficies. Luego nosotros la mostramos con un color, pero eso no significa que todo el cuadrado tenga exactamente lo mismo dentro.

Por eso una orilla es un lugar difícil: justo ahí estamos intentando separar cosas que el sensor pudo registrar juntas.

Si haces más zoom, el cuadrado se hace más grande en tu pantalla. La observación original sigue siendo la misma.

El zoom sirve para examinar lo que tenemos. No fabrica lo que faltó medir.

## Ahora volvamos a las fotos

Con todo eso en mente, volvamos al paisaje. Este es un tramo del Jatunyacu, en Ecuador.

Tenemos una imagen del 11 de julio de 2019, otra del 8 de agosto de 2024 y otra del 29 de julio de 2026.

Dejemos las fechas en pantalla para poder seguirlas sin perdernos. Lo importante ahora es comparar el mismo lugar, a la misma escala y con el mismo ajuste de color.

En 2024 vale la pena detenerse en las franjas claras y en los brazos de agua. Podemos mover esta cortina y examinar cómo se ven frente a 2019.

Ahí hay diferencias visibles que merecen investigarse. Lo que todavía no hemos medido es cuánto corresponde al nivel del agua y cuánto a cambios en las formas del cauce.

La observación de 2026 añade otro momento. No borra esa pregunta, pero nos permite seguir mirando.

Sería tentador unir las tres imágenes con una transición suave y hacer que el río pareciera transformarse continuamente. Quedaría espectacular. También estaríamos inventando los estados intermedios.

Son tres visitas al paisaje. Entre ellas faltan muchísimas.

## ¿Y si de verdad se está secando?

Entonces necesitamos seguirlo en el tiempo, no quedarnos con las dos fotos que más contrastan.

Hay que buscar muchas observaciones utilizables, revisar las condiciones de cada una y contrastarlas con lluvia, niveles y datos de campo.

Incluso encontrar agua puede no resolverlo: pueden quedar pozas sin una conexión superficial continua entre ellas. Ver una poza no demuestra que el río siga fluyendo por todo ese tramo.

Y si una nube lo tapa, ese día no tenemos una respuesta. No podemos convertir lo que no vimos en «no había agua».

Un hueco en nuestros datos no es un hueco en el río.

## La pregunta incómoda: ¿y la minería?

Sí, la minería aluvial puede aumentar la carga de sedimentos de los ríos. Eso está documentado en estudios de regiones tropicales. Investigar esas intervenciones tiene sentido.

Pero para explicar un cambio concreto hace falta conectar la evidencia.

Si aparece más sedimento, por ejemplo, también hay que revisar las crecidas: pueden movilizar material. Si hay una intervención, necesitamos saber dónde estaba y cuándo ocurrió, no solo que existía en algún lugar de la región.

Podemos comparar aguas arriba y aguas abajo, revisar observaciones anteriores y posteriores, y contrastar lo que vemos con mediciones.

La pregunta deja de ser «¿esta foto se parece a lo que esperaba?» y pasa a ser «¿qué explicación encaja con todas las pruebas?». Incluidas las que podrían hacernos cambiar de idea.

Y una señal óptica no sustituye una muestra de agua: este índice no mide mercurio.

Ser cuidadosos con eso no es quitarle importancia a un posible daño. Si lo hay, necesitamos pruebas que permitan describirlo y sostenerlo.

## Lo que le respondería a mi amigo

Entonces, ¿qué le pasó al río de estas imágenes?

Con esta comparación no podemos afirmar que se haya secado ni atribuir las diferencias a una actividad concreta. Podemos localizar cambios visibles para estudiarlos, y hemos comprobado algo sobre nuestro propio mapa: una regla distinta cambia la detección aunque la observación sea la misma.

Por eso, si me mandaras aquel mensaje, no te respondería «no pasa nada». Tampoco diría «ya encontramos al culpable».

Te diría: «Pasemos un momento aquí. ¿Ves estas diferencias? Vamos a averiguar cuáles siguen apareciendo en otras fechas y qué estaba ocurriendo en el terreno».

Las fotos nos dieron un lugar donde empezar. El índice nos ayudó a examinarlo. Ahora tenemos preguntas que podemos poner a prueba.

Y eso me parece mucho más interesante que ganar una discusión con dos imágenes. Podemos dejar de mirar el río como una mancha que cambió de color y empezar a entender lo que le está pasando.
