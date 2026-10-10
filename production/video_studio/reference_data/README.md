# Capas de referencia incluidas

Estas licencias corresponden a **datos**, separadas de la licencia del software y de los avisos de OpenLayers/otras dependencias. Los recursos personales BYOD y la caché ambiental CHIRPS no se empaquetan automáticamente.

- Ecuador ADM0 y ADM1: geoBoundaries gbOpen, William & Mary / geoLab; Runfola et al. (2020), *geoBoundaries: A global database of political administrative boundaries*, PLoS ONE 15(4): e0231866, https://doi.org/10.1371/journal.pone.0231866. Revisión original `9469f09`, reutilizada de los insumos existentes. [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), con atribución y declaración de cambios. [Datos y política geoBoundaries](https://www.geoboundaries.org/countryDownloads.html). Referencia académica abierta; no se afirma autoridad oficial ecuatoriana.
- Latinoamérica: Natural Earth v5.1.2, Tom Patterson, Nathaniel Vaughn Kelso y colaboradores. [Dominio público y condiciones](https://www.naturalearthdata.com/about/terms-of-use/). Polígonos 1:110M generalizados, fronteras de facto; no aptos como límites catastrales ni dominios provinciales detallados.

Cambios: normalización declarada CRS84/EPSG:4326 a RFC7946; retirada de declaraciones `bbox`; coordenadas y atributos intactos. Selección de 20 países del archivo Natural Earth. Galápagos se obtiene de la provincia homónima original, sin trasladar coordenadas. El manifiesto registra SHA256 original, SHA256 de la representación, bytes, procedencia, cambios y número de entidades.

Aquí “Latinoamérica” comprende Argentina, Bolivia, Brasil, Chile, Colombia, Costa Rica, Cuba, Ecuador, El Salvador, Guatemala, Haití, Honduras, México, Nicaragua, Panamá, Paraguay, Perú, República Dominicana, Uruguay y Venezuela. Es una definición explícita de países soberanos de lenguas española, portuguesa o francesa; excluye Belice, Guyana, Surinam, territorios dependientes y Caribe anglófono. Puede ampliarse como otra selección, sin restricción técnica del SIG.

Nombres/códigos administrativos del insumo se conservan, incluso particularidades originales. No se corrigen atributos o geometrías por motivos estéticos.
