# Ecuador Vivo · herramientas científicas
Componente creado desde la plantilla oficial Streamlit component-template v2
(React + TypeScript), adaptado a los motores locales de resource_engines.

Solo se monta al abrir una herramienta desde Recursos. El código propio conserva
la licencia privada del repositorio. Las licencias de bibliotecas y fuentes se
mantienen separadas; ver frontend/build/notices y resource_engines/README.md.

Build desde ecuador_vivo_scientific_tools/frontend:
npm run typecheck
npm run build:frontend:production

Instalar el wrapper editable en el entorno Studio:
python -m pip install -e . --no-deps

Los motores se resuelven desde el entorno Node hermano resource_engines para
evitar otra instalación completa del mismo conjunto. Mantener esa estructura.
El paquete generado no debe publicarse de forma aislada sin sus licencias y
sin resolver sus dependencias de distribución.

Registrar/montar aprobado en AppTest. La comprobación de interacción real en
navegador sigue pendiente. No usar Playwright u otro navegador para eludir una
preferencia denegada.
