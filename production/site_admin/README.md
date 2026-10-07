# Panel personal de Ecuador Vivo

Aplicación local de Streamlit para editar la web estática sin tener que escribir HTML o JavaScript.

## Abrir

Desde la carpeta raíz del repositorio, haz doble clic en `Abrir panel personal de la web.vbs`. El panel escucha solo en `127.0.0.1:8511`; no se añade al sitio público. Reutiliza el entorno virtual de Video Studio si ya existe.

## Cómo usarlo

1. Selecciona la página. En **Textos e idiomas** edita español e inglés. En **Elementos** busca textos, imágenes, enlaces, menú y pie; puedes cambiar su apariencia, ocultarlos, duplicarlos, moverlos entre hermanos o retirarlos.
2. **Bloques** añade secciones bilingües con texto, enlace, imagen o video. **Catálogos y videos** edita, añade o retira registros de Biblioteca, Datos y Andes Pulso mediante formularios, sin escribir JSON.
3. **Recursos** añade imágenes, MP4, PDF, CSV y GeoJSON de hasta 25 MiB; usa su ruta en elementos o catálogos. Para videos grandes usa alojamiento externo. Retirar un elemento no borra el archivo fuente.
4. **Diseño** ajusta colores y ancho global. Cada elemento tiene controles de tipografía, fondo, alineación y espaciado.
5. **Capas del visor** retira fuentes integradas o añade GeoJSON, WMS y XYZ con cita y sistema Tierra/Agua/Cielo/Vida/Riesgo. Las fuentes nuevas están apagadas inicialmente; su leyenda aparece solo al activarlas. El servidor de origen debe permitir acceso desde el navegador (CORS).
6. Comprueba **Vista previa**, que muestra el sitio real servido localmente. Prueba enlaces, idiomas y visor; mover o eliminar componentes interactivos puede afectar su funcionamiento.
7. Cada guardado crea una copia privada en `_local/site-admin/backups`. **Historial** recupera versiones sin sobrescribir cambios posteriores. **Cambios y GitHub** muestra diferencias y pide confirmación explícita para commit y push.

El panel no guarda claves de GitHub: usa la autenticación que Git ya tenga configurada en el equipo. Si hay cambios previos en los mismos archivos, archivos ya preparados, o una edición posterior fuera del panel, excluye esos archivos de su publicación para no mezclarlos.

## Alcance actual y límites

El panel protege scripts, estructura raíz y rutas privadas. Permite controlar contenido, estructura y diseño existentes; no crea lógica nueva de JavaScript, modelos científicos o conectores arbitrarios. No es un editor de arrastrar y soltar. Ocultar un componente es más seguro que eliminarlo cuando está conectado con el visor.

Guardar una ficha no verifica sus afirmaciones científicas ni convierte un borrador en un caso validado. Los videos se preparan desde **Video Studio → Exportaciones → Andes Pulso**, conservando CSV, método, fuentes y métricas. Revisa el caso antes de publicarlo.

Las comparaciones climáticas están en **Video Studio → Editor → Tipo de video: Comparación climática**. No necesitan otro laboratorio.

## Pruebas locales

```powershell
& '.\_local\video-studio\.venv\Scripts\python.exe' -m unittest discover -s production\site_admin -p 'test_*.py' -v
```
