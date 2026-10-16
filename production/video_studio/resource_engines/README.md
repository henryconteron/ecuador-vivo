# Motores científicos opcionales

Instalados por petición expresa del usuario, fuera del paquete SIG y de las
dependencias de la web. Versiones exactas y árbol reproducible en package-lock.
No cargar estos paquetes al abrir Inicio o SIG.

- Excalidraw 0.18.1: dibujo/flechas; MIT.
- Fabric.js 7.4.0: composición vectorial; MIT.
- React Flow 12.12.0: mecanismos/conectores; MIT.
- Ketcher 3.18.0 + servicio standalone: moléculas; Apache 2.0.
- Three.js 0.180.0: disponible, además de la copia previa three-r180; MIT.
- resvg 2.6.2: rasterizar únicamente la selección SVG saneada de Bioicons.
- Manim 0.22.0: instalado en _local/resource-tools/.venv; MIT. Comprobados import,
  geometrías básicas y pip check. Aún no hay panel de generación Manim integrado.
- Blender: integración orográfica existente; no reinstalado ni sustituido.

BioRender es solo referencia, no software/biblioteca libre distribuida aquí.
Smithsonian es un catálogo remoto, no una instalación. No se descargaron sus
colecciones. Bioicons: cinco ilustraciones seleccionadas CC0, originales,
derivados PNG y procedencia fijada a commit en artwork/catalog.json.

Los cuatro editores se conectan mediante el componente CCv2 creado desde la
plantilla oficial de Streamlit en ../ecuador-vivo-scientific-tools. Importaciones
JS diferidas: no iniciar todos los motores ni un servidor Node adicional.
Guardan una imagen PNG para Studio y JSON/molfile del original para reabrir.
No convertir esa imagen compuesta en piezas editables del lienzo principal ni
afirmar que el editor químico valida toda interpretación científica.

Instalación inicial sin scripts de terceros. Dependencias transitivas fijadas
para corregir avisos altos. Última auditoría: 0 críticos/altos/moderados, 4 bajos
(herramientas Mermaid/KaTeX transitivas); revisar antes de distribuir públicamente.
El wrapper propio sigue la licencia privada del repositorio, NO la de los motores.
El inventario y avisos se generan con report-licenses.mjs tras compilar.

Pendiente: aprobación visual real y pruebas de edición/exportación en navegador.
Las pruebas AppTest/Node no validan WebGL, fuentes de dibujo ni el motor WASM.
