# Estudio local de video

Editor Streamlit para la plantilla cartográfica vertical de Ecuador Vivo. Inicio de usuario: doble clic en `Abrir editor de videos.vbs` en la raíz del repositorio.

La [guía de uso](../../documentation/GUIA-EDITOR-VIDEOS.md) explica datos, diseño, créditos, exportación y límites científicos.

## Desarrollo

Python 3.13 probado en Windows. Instalar `requirements.txt` en un entorno virtual. Desde esta carpeta, ejecutar `python -m streamlit run app.py`; la configuración liga el servidor únicamente a 127.0.0.1:8510. El dibujado usa fuentes Segoe UI de Windows. No desplegar este editor como servicio público sin autenticación, aislamiento y revisión de seguridad.

Pruebas desde la raíz: `python -m unittest discover -s production/video_studio -p 'test_*.py' -v`, usando el entorno del editor. La prueba de lluvia usa la caché de 2024 o requiere red para descargar una fecha y los límites.

`model.py` valida proyectos; `data.py` importa y prepara matrices; `render.py` comparte el dibujado entre PNG y MP4; `jobs.py` ejecuta procesos independientes y registra procedencia; `app.py` implementa la interfaz. Todos los resultados y cachés viven en `_local/video-studio/`, excluido de Git. Los proyectos v1 anteriores se completan con campos opcionales de créditos sin perder sus ajustes.
