# Fuentes y comprobaciones para publicar

Autor y crédito, según la indicación del autor: Henry Conteron, ingeniero en
geociencias e investigador independiente. El video muestra el crédito completo
en dos líneas para mantenerlo legible; no incluye una afiliación universitaria.
Las versiones anteriores no se sobrescriben.

## Alcance científico

Este video representa el periodo cerrado 1900–2025. **No incluye 2026**.
La consulta independiente del 02/10/2026 sí confirmó registros de 2026; por
ejemplo, M 4,5 (mb) el 15/09/2026 a las 23:45 UTC, 12 km al ONO de Palora,
Ecuador: https://earthquake.usgs.gov/earthquakes/eventpage/us7000thr4
Añadir 2026 exigiría recalcular los datos y sustituir la locución que menciona
«2661 registros» y «hasta 2025». No se cambia silenciosamente ese alcance.
El catálogo no equivale a todos los sismos del Ecuador ni a una selección
exclusivamente dentro de sus fronteras. Mantiene magnitudes originales de
distintos tipos, no una escala Mw homogénea. Las ubicaciones y profundidades
son estimaciones que pueden revisarse. Los perfiles proyectan toda la ventana,
sin identificar fallas ni inferir la geometría de las placas.

Las cifras del video corresponden a la descarga USGS del 02/10/2026: 2661
registros M ≥ 4, 1752 profundidades menores de 70 km, 908 entre 70 y menos de
300 km, ninguna de 300 km o más y una profundidad desconocida. Máximo: 254 km.
La auditoría vuelve a calcular estas cifras desde el GeoJSON original, compara
el CSV renderizado, comprueba los hashes y consulta otra vez el servicio USGS.
El resultado completo queda en `publication_audit.json`.

## Referencias primarias

- Datos y parámetros: https://earthquake.usgs.gov/fdsnws/event/1/
- Epicentro e hipocentro: https://pubs.usgs.gov/gip/earthq1/how.html
- Profundidad y clasificación general: https://www.usgs.gov/programs/earthquake-hazards/determining-depth-earthquake
- Magnitud e intensidad: https://www.usgs.gov/programs/earthquake-hazards/earthquake-magnitude-energy-release-and-shaking-intensity
- Preparación familiar, simulacros y mochila: https://igepn.edu.ec/que-hacer-ante/un-sismo

Se contrastaron las definiciones con fuentes USGS y la preparación con IG-EPN.
Algunas páginas USGS no admitieron apertura directa en el navegador de consulta;
su contenido se pudo contrastar en los resultados indexados del propio USGS.

## Archivo exportado

MP4 vertical de 1080 × 1920, 30 fps, H.264/yuv420p y voz AAC. Duración aproximada:
2:06. La toma aportada se conserva completa, a velocidad original, sin cortes.
La verificación decodifica todos los fotogramas y compara la señal de audio
codificada con la original. Resultado: `encoded_verification.json`.

## Antes de subir

1. Usa el MP4 v6 y la descripción correspondiente a cada plataforma. Ya tiene
   subtítulos incrustados: evita duplicarlos con otra capa automática.
2. Activa la declaración de contenido generado con IA por la voz sintética.
   Las descripciones también identifican ElevenLabs. Los gráficos son una
   visualización programada de registros reales, no una simulación de un evento.
3. El autor confirmó que generó la voz en el **plan gratuito**. Por tanto, usa
   esta versión únicamente para publicación no comercial, sin monetización,
   publicidad o patrocinio. Se incluyó «Voz: elevenlabs.io» en la primera línea
   de ambas descripciones: consérvala como título/encabezado de la publicación.
   ElevenLabs exige atribución «elevenlabs.io» o «11.ai» en el título. Para uso
   comercial, genera otra toma bajo un plan con licencia comercial; una
   suscripción posterior no cambia los permisos de la toma gratuita existente.
   La cuenta no se inspeccionó y no se certifica el cumplimiento del resto de
   condiciones de la plataforma.
4. Conserva las fechas y las advertencias al copiar la descripción. No lo
   presentes como un catálogo completo ni actualizado hasta 2026.

Políticas oficiales consultadas:

- TikTok, audio realista generado con IA: https://support.tiktok.com/es/using-tiktok/creating-videos/ai-generated-content
- Instagram/Meta, declaración de audio sintético: https://about.fb.com/ltam/news/2024/02/etiquetado-de-imagenes-generadas-por-ia-en-facebook-instagram-y-threads/
- Permisos y atribución ElevenLabs: https://help.elevenlabs.io/hc/en-us/articles/13313564601361-Can-I-publish-the-content-I-generate-on-the-platform

La revisión científica y técnica no equivale a autorización para monetizar la voz.
No se publica en ninguna cuenta automáticamente.

## Resultado de esta revisión

La nueva consulta USGS confirmó exactamente los mismos 2661 registros y valores
científicos del periodo histórico guardado. Las cifras de profundidad coinciden.
Pasaron 40 pruebas automatizadas. El MP4 final se decodificó completo: 3785
fotogramas, 1080 × 1920, 30 fps, H.264 y cero errores de decodificación. La voz
codificada conserva la toma original; correlación PCM 0,99998544 sin desfase.
Se revisaron visualmente fotogramas del MP4 y las tarjetas con el crédito nuevo.

No se detectaron errores científicos o técnicos que impidan la publicación
educativa. La publicación con esta voz queda condicionada al uso **no comercial**,
a mantener la atribución y a declarar la voz generada con IA en la plataforma.
