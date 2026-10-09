# Tipografía del estudio

Barlow Condensed (ExtraBold, SemiBold y Regular), de Jeremy Tribby.
Archivos originales: https://github.com/google/fonts/tree/main/ofl/barlowcondensed

Se incluye la licencia SIL Open Font License 1.1 en `OFL-BarlowCondensed.txt`.
Las fuentes se distribuyen con el editor para que las maquetas mantengan su
tipografía condensada sin depender de las fuentes instaladas en cada equipo.

Familias integradas en Studio: Atkinson Hyperlegible Regular/Bold y Lora variable
(eje de peso 400–700). Se incluyen sus licencias OFL 1.1 sin modificar las fuentes.
`studio-fonts-manifest.json` registra URL oficial fijada a commit, tamaño y SHA-256
de cada archivo. El archivo Lora conserva su contenido original; solo se renombró
el archivo local a `Lora-Variable.ttf`.

Origen: https://github.com/google/fonts/tree/main/ofl/atkinsonhyperlegible
y https://github.com/google/fonts/tree/main/ofl/lora. Estos assets portables
mantienen preview/export con la misma fuente sin instalar dependencias
ni depender de fuentes del sistema. `studio_typography.py` resuelve nombres
permitidos desde bytes locales sin fallback. Barlow conserva Regular/SemiBold;
Lora usa eje 400/600. Cada instancia es privada y no comparte pesos variables.
Roles título/cuerpo/fuente/datos asignan familias mediante una acción explícita;
el inspector permite rol y familia por elemento. Sin `font_family` se conserva
Barlow. Las rutas legacy siguen utilizando su renderer original.
