# Videos geográficos: mapas primero, métricas al cierre

En el editor local, **Tipo de video** determina la maqueta dentro de la misma
pantalla. La vista previa y el MP4 utilizan el mismo compositor vertical de
1080 × 1920.

### Diseño de las comparaciones

En **Diseño → Ocupación del lienzo**, **Referencia · grande** reproduce las
proporciones de la referencia: título condensado, dos mapas grandes, escala
compartida y cierre con cifras, barras y hallazgos. Es la opción predeterminada.
**Márgenes ampliados** reduce la composición para dejar más espacio a los controles
superpuestos de las redes sociales. Ningún margen garantiza que todas las
interfaces de todas las plataformas queden fuera: revisa el video antes de publicar.

La fuente Barlow Condensed se incluye con su licencia SIL OFL para conservar el
aspecto entre equipos. Los iconos se reutilizan de la maqueta de lluvia; no se
añaden fotografías decorativas ni superficies geográficas inventadas.

Para temperatura, prueba **Termal editorial**. Puedes cambiar la paleta, el fondo
y los dos colores del degradado del título. Un proyecto antiguo conserva su
paleta guardada; selecciona la nueva si quieres reproducir esta referencia.
Las cifras de los ejemplos no se copian: proceden de los datos de la consulta.

## Comparación climática

1. Elige fuente, variable, territorio, años y ventana mensual; calcula la consulta.
2. En **Diseño → Composición del mapa**, elige dos mapas o un mapa secuencial.
3. Con dos mapas se presenta el mismo mes de dos años. Con tres años se compara
   el primero con cada año posterior; ninguno desaparece silenciosamente.
4. Elige el momento de la vista previa. El MP4 recorre todos los momentos.
5. La escala automática utiliza los extremos de las celdas nativas válidas
   que intersectan el territorio, considerando todos los periodos. Puedes fijarla
   manualmente; se mantiene igual en todos los mapas.
6. La tarjeta final conserva cifras y rankings. Las tablas de revisión no son
   el cuerpo del video.

Los mapas mensuales provienen de los GeoTIFF diarios originales. La precipitación
se acumula; temperatura, rapidez del viento y humedad se promedian. Un mes con
fechas ausentes o duplicadas bloquea el mapa. Un píxel con días ausentes permanece
sin dato. Precipitación negativa se considera inválida; temperaturas negativas
siguen siendo válidas. La suavización es exclusivamente visual: no cambia las
métricas, no agrega resolución y no rellena celdas originalmente inválidas.

Incluso al seleccionar un ranking provincial, el cuerpo audiovisual presenta
el campo mensual sobre el mapa; el ranking del periodo aparece al cierre. Las
unidades del mapa y del cierre se resuelven por separado (por ejemplo, mm/mes
frente a mm del periodo). Para una ciudad se ubica el punto de referencia sobre
el mapa nacional; la cifra sigue representando su celda climática, no una estación.

Galápagos se muestra reubicado, con la misma escala y datos originales si existe
cobertura. La nota metodológica identifica el desplazamiento. Sin color significa
sin dato, no cero.

## CSV geográfico: puntos

1. En **Tipo de video → CSV geográfico**, sube un archivo UTF-8 de hasta 20 MiB
   y 100.000 filas. Se aceptan comas o punto y coma como separador.
2. Selecciona las columnas de latitud y longitud y confirma **grados WGS84**.
   Coordenadas UTM en metros requieren reproyección previa; no se adivina el SRC.
3. Selecciona categoría/especie, si existe, y una columna de periodo opcional.
   Hasta seis categorías mantienen la leyenda legible. Filtra previamente archivos
   con más especies. Los periodos se ordenan por su etiqueta; utiliza fechas
   ISO `AAAA-MM-DD` o años para conservar el orden cronológico.
4. Filas inválidas o fuera del encuadre continental/insular detienen la importación;
   puedes autorizar explícitamente excluirlas. Se informa su cantidad.
5. Edita título, fuente, autoría, redes, color de cada categoría, tamaño de puntos,
   fondo, duración y cierre.
6. Revisa que las ubicaciones pertenezcan a Ecuador y que se puedan mostrar.
   Añade la cita para habilitar la exportación.

Cabecera sugerida (sin registros inventados):

```csv
latitude,longitude,species,period
```

Un punto representa una fila del CSV, no necesariamente un animal único. Dos
registros de la misma especie no demuestran dos individuos. La ausencia de puntos
no demuestra ausencia de esa especie. El cierre cuenta registros por categoría,
no estima poblaciones ni una distribución biológica completa.

No publiques coordenadas sensibles de especies amenazadas sin revisar permisos
y riesgos. La autorización para incluir los registros en Andes Pulso está
desactivada por defecto y debe renovarse si cambias el archivo fuente.

## CSV geográfico: provincias

Selecciona **Provincias**, la columna con el nombre oficial y la columna numérica.
Puede existir una columna de periodo. Debe haber una sola fila por provincia y
periodo. Los duplicados se rechazan: el editor no puede decidir científicamente
si esas filas se suman, promedian o representan unidades diferentes.

El mapa une cada valor a su polígono ADM1 real, con escala fija entre periodos.
Incluye Galápagos cuando el CSV lo contiene. Provincias ausentes quedan sin color.
Indica las unidades y el método de producción del valor en la cita/metodología;
los valores se muestran tal como fueron proporcionados, sin cálculo meteorológico
implícito.

## Guardar y llevar a Andes Pulso

**Guardar proyecto CSV** conserva controles, registros y trazabilidad para reabrirlo
desde Tus proyectos. El video final guarda `comparison.csv`, el recibo, la vista
previa y, si está activado, el cierre. Los CSV importados se almacenan una sola vez
por SHA-256 bajo `_local/video-studio/imports/`.

En **Exportaciones → preparar caso web**, los videos CSV exigen autorización
explícita para compartir los registros. El borrador conserva video, métricas,
CSV geográfico y cita. No hace commit, push ni publicación automática. Antes de
publicar revisa permisos, sensibilidad de ubicaciones, unidades y cobertura.

Por ahora este modo CSV admite puntos WGS84 y valores por provincia. No importa
polígonos arbitrarios, no calcula hábitats, no interpola observaciones de estaciones
y no representa automáticamente dirección del viento con flechas.
# Diseño editorial de comparaciones

La vista comparativa usa una pregunta breve, mapas grandes con escala compartida,
una leyenda y notas metodológicas discretas. Galápagos se reubica, sin inventar
valores donde la fuente no los entrega. El suavizado de pantalla no mejora la
resolución nativa. La barra de distancia del continente es aproximada al centro
del encuadre; no corresponde al recuadro insular.

El cierre de comparaciones entre años muestra las cifras calculadas, barras por
año seleccionado y tres hallazgos. La lluvia se acumula; temperatura, humedad y
rapidez del viento conservan el promedio temporal ponderado por días. No se
interpreta la diferencia entre unos pocos años como tendencia climática ni se
atribuyen causas. Los rankings de 24 provincias y los registros CSV mantienen
sus cierres específicos. Los textos y créditos siguen editables.

En **Editor → Comparación climática → Cierre final**, desactiva los títulos
automáticos para personalizar también los tres hallazgos. Un campo vacío utiliza
la explicación calculada. Las cifras y las barras no cambian con el texto.

Para reproducir la prueba visual con copias NASA POWER ya descargadas:
`python production/video_studio/preview_editorial.py`. No descarga nada nuevo.
