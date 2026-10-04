# El río que desaparece de un mapa — guion y dirección v5

## Diagnóstico creativo

Objetivo: que una persona sin conocimientos de teledetección quiera seguir
mirando y entienda la diferencia entre observación, detección e interpretación.
Audiencia general; vocabulario accesible sin sacrificar trazabilidad científica.

**Fortalezas de v4:** datos reales, tres fechas explícitas, comparaciones justas,
fuentes verificables y separación entre observación y causalidad.

**Debilidades:** arranque geográfico sin recompensa inmediata; catálogo de
siglas en vez de conflicto; frases que anuncian lecciones; reiteración de
advertencias; composición de tarjetas que hace sentir una presentación narrada.
El título promete preguntas, pero la secuencia prioriza métodos.

**Mejoras:** demostración al inicio; una promesa que el video cumple; mecanismo
antes de terminología; ejemplo ecuatoriano a mitad de la historia; una pregunta
que provoca la siguiente; límites mostrados cuando ayudan a resolver una duda.

**Ajuste estratégico:** pasar de “cómo aplicamos índices en Napo” a “cómo un río
puede desaparecer de un mapa sin desaparecer del paisaje”. Napo es un caso real,
no una promesa de cobertura global ni un relato de minería confirmada. No se
presentan nuestros recortes ecuatorianos como si fueran otros ríos del mundo.

Aplicación de las habilidades de crítica creativa, ganchos y storytelling visual:
impacto y claridad guían la apertura; el conflicto guía el orden; cada visual
debe aportar una prueba o una pregunta, no adornar una fórmula.

## Diez aperturas evaluadas

| Gancho propio | Por qué funciona / precaución | Uso |
|---|---|---|
| Voy a hacer desaparecer parte de un río de este mapa, sin sacar agua. | Demostración inmediata; aclarar “de este mapa”, no afirmar desaparición física. | Elegido para video completo |
| ¿Y si el río no cambió… pero el mapa sí? | Contraste entre territorio y representación, sin adjudicar el caso. | Reel corto |
| Dos mapas. La misma imagen. ¿A cuál creerías? | Invita a predecir antes de explicar; no promete verdad solo por apariencia. | Apertura participativa |
| Este azul no es agua: es una decisión sobre la luz. | Desarma la equivalencia color=medición; requiere mostrar que es una visualización. | Pieza sobre índices |
| ¿Puedes ver una sequía en una sola fotografía? | Pregunta relevante; evitar que el título anuncie sequía detectada. | Episodio sobre tiempo |
| Hay agua en la imagen. ¿Por qué eso no demuestra que el río fluya? | Distingue presencia de conectividad y caudal. | Clip sobre pozas |
| El río cambia de color. La causa no viene escrita en la imagen. | Introduce sedimentos y causas con prudencia. | Clip de investigación |
| Acercamos el mapa. ¿Apareció detalle… o solo un píxel más grande? | Prueba visual de resolución; no demoniza el zoom útil. | Microvideo técnico |
| Cuatro métodos coinciden. ¿Pueden estar equivocados los cuatro? | Suspense sobre consenso; explicar bandas/errores compartidos. | Capítulo de validación |
| Antes de señalar una mina, probemos otra explicación. | Invita a contrastar hipótesis; no sugiere que las minas no tengan impactos. | Pieza sobre causalidad |

No se ha medido retención ni probado estas aperturas con audiencia. Se elige
la primera porque ya podemos **demostrarla con nuestros datos**, no por una
predicción de viralidad.

## Narrativa central y secuencia visual

Conflicto: interpretar una señal como si fuera el fenómeno. Promesa: explicar
cómo cambió el mapa y qué haría falta para saber cómo cambió el río.

| Momento | Narración / función | Visual y ejecución |
|---|---|---|
| Demostración | Una imagen; dos reglas | MNDWI>0 → MNDWI>0,2, 08 AGO 2024, mismo soporte. Corte, no deformar río. |
| Sospechoso | Una diferencia parece pedir un culpable | RGB 2019/2024; causas como hipótesis, nunca etiquetas sobre píxeles. |
| El río como sistema | Agua, sedimentos, vegetación y nivel | RGB real; observar bancos y brazos. No inventar flechas de erosión local. |
| Luz invisible | Dar la razón física antes del nombre | RGB identificado como visible; explicar bandas sin simular una curva medida. |
| La herramienta | Una fórmula responde a la duda | NDWI, luego MNDWI; dividir por suma, no caudal ni volumen. |
| Recompensa | Resolver exactamente el truco inicial | Mismos mapas candidatos y umbrales explícitos. |
| Desacuerdo | Cómo sabemos si una regla sirve | Acuerdo de detectores: ámbar conserva incertidumbre, no “confianza”. |
| Caso real | Probar la idea en paisaje ecuatoriano | 2019/2024/2026, capítulos propios; 2024 recibe más tiempo. |
| Nueva complicación | Agua presente no asegura flujo | Pozas y conectividad explicadas; no diagnosticar sequía con tres fechas. |
| Lo que transporta | Una pregunta distinta necesita otra señal | NDTI rojo/verde dentro de candidatos; gris y trama diferenciados. |
| Causa | Comparar hipótesis rivales | Minería documentada + crecidas; exigir prueba local y controles. |
| Cierre circular | Desapareció del mapa, no del paisaje | Regresar a regla/observación; invitar a buscar explicaciones comprobables. |

Momentos clave: cambio de regla a pocos segundos; revelación explícita de los
umbrales; pausa visual en 2024; diferencia agua/flujo; cierre que paga la promesa.

Dirección estética: conservar imágenes reales y geometría; pocos términos por
escena, títulos que hagan preguntas o abran conflictos, leyendas legibles.
Paletas con función científica (agua azul, desacuerdo ámbar, NDTI distinto).
Evitar fondos genéricos, efectos alarmistas o música/clips de divulgadores.
Esta versión mejora la narrativa y prueba visual; no se presenta como un
documental con rodaje propio ni montaje final de alta producción.

## La demostración no es un hallazgo ambiental

`prepare_river_story.py` verifica y copia la evidencia v4 a una carpeta nueva.
Lee MNDWI de reflectancia **nativa calibrada**; recorta a la cuadrícula exacta
del detalle Jatunyacu y conserva el soporte común de las tres fechas.
El umbral 0,2 es una elección editorial para mostrar sensibilidad, **no un
umbral óptimo o una calibración de agua en Napo**. Los dos candidatos usan >,
no >=. Los píxeles que exceden 0,2 son un subconjunto de los que exceden 0.
Los recuentos quedan en `hook_evidence.json`: nunca hectáreas de agua perdida.

El guion habla de desaparición **del mapa** y cierra la distinción. No afirma
desecación real, concentración de sedimentos, responsabilidad de una mina,
agua pura en todos los candidatos ni exactitud de ningún detector.
Acuerdo de cuatro métodos comparte errores; QA puede eliminar agua sombreada.
Trama=sin observación, no lecho seco. La imagen 2026 es del 29 de julio, no
todo el año ni una vista en directo. Comparación a 20 m, no resolución nueva
por ampliar. Las causas generales no se atribuyen a estos tramos sin pruebas.

## Guion y entregables

Guion fuente: `SCRIPT` en `reel_river_story.py`; la exportación genera un
**texto limpio y listo para grabar**, sin marcas técnicas intercaladas:
`artifacts/rios_historia_v5/guion_elevenlabs.txt`.

El nombre del archivo es compatible con el flujo previo; no se contacta ese
servicio ni se gastan créditos. Narración de muestra con Microsoft Pablo
instalado, claramente indicada; no clonación o imitación de ningún divulgador.

`artifacts/rios_historia_v5/` contiene storyboard, MP4 de referencia, SRT
borrador, imágenes de cada capítulo, manifiesto de evidencia y recibo de video.
Nada se publica. V4 y todos los videos anteriores quedan intactos.

```powershell
python prepare_river_story.py
.\venv\Scripts\python.exe reel_river_story.py --storyboard-only
.\venv\Scripts\python.exe reel_river_story.py
python -m unittest discover -s tests -p test_river_story.py
```

Se necesitan los artefactos locales v4 verificados. Matemática geográfica con
Python/rasterio; montaje con el entorno de video. No cambia la aplicación
Streamlit, no agrega páginas al atlas, no descarga otras regiones ni inicia GEE.

Antes de publicar: leer el texto en voz alta y ajustar ritmo; grabar la voz
propia si se desea; alinear subtítulos (su tiempo actual es aproximado);
revisar interpretación científica y conservar bibliografía en descripción.
Las transiciones de demostración siguen fases editoriales aproximadas; revisar
su correspondencia con la toma definitiva, no asumir alineación palabra a palabra.

## Fuentes

Para fórmulas, escenas y límites se mantiene [el método v4](NAPO_RIOS_METODOS_V4.md):
McFeeters (1996), Xu (2006), Feyisa et al. (2014), Cavallo et al. (2025), Lobo
et al. (2018), Dethier et al. (2023), Copernicus / Element 84 Earth Search.

Para la nueva explicación general de cauces y causas naturales:

- [USGS, Geomorphology, Sediment, and Habitat](https://www.usgs.gov/centers/washington-water-science-center/science/science-topics/geomorphology-sediment-and-habitat):
  transporte, erosión y depósito de sedimentos, hidráulica y geometría del cauce.
- [USGS, Dams and Rivers: A Primer on the Downstream Effects of Dams](https://www.usgs.gov/publications/dams-and-rivers-a-primer-downstream-effects-dams):
  cambios de bancos y vegetación dependen de flujo, crecidas y carga sedimentaria;
  no se afirma presencia de una presa en nuestros recortes.

Inspiración de estructura, no autoridad de resultados ni guion copiado:
los dos videos de Veritasium y El Robot de Platón consultados previamente
están enlazados en el método v4. No se reutiliza su texto, marca, voz ni material.

Contains modified Copernicus Sentinel data (2019, 2024, 2026).
Procesamiento y divulgación: Henry Conteron.
