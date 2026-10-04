# Laboratorio y producción de Andes Pulso

Código preservado del proyecto monitor-sismos. La experiencia web pública está en `andes-pulso.html`; GitHub Pages no ejecuta Streamlit ni Python.

Los módulos `seismology.py`, `historical.py` y `education.py` conservan sus pruebas. Ejecutar desde este directorio con un entorno que tenga `requirements.txt`; la app se inicia con `streamlit run app.py`.

Los renderizadores específicos contienen dependencias históricas entre versiones. Se preservan, pero NO se declara que toda la producción sea aún reproducible desde un clon limpio. Los originales de trabajo están en el área privada `_local/monitor-artifacts/` del proyecto principal; no se publican automáticamente. La carpeta `artifacts` del proyecto anterior es un enlace de compatibilidad hacia esa ubicación, no una segunda copia.

No borres fuentes, audios o manifiestos por tener un número de versión anterior. El caso público conserva su propia instantánea y comprobación SHA-256.
