import { ECUADOR_CONTINENTAL_BOUNDS } from "./config.js";

// An editorial viewing window around both towns, NOT an administrative boundary.
export const REGION_VIEWS = Object.freeze({
  ecuador: { bounds: ECUADOR_CONTINENTAL_BOUNDS },
  napo: { bounds: [[-1.12, -78.04], [-0.72, -77.55]] },
});

export function normalizeRegionFocus(value) {
  return value === "napo" ? "napo" : "ecuador";
}

// Native sampling/scale describes the source, not the WMS image or screen pixels.
export const SPATIAL_CONTEXTS = Object.freeze([
  { id: "faults", name: ["Fallas GEM", "GEM faults"], resolution: ["Escala original no documentada", "Original map scale undocumented"], limit: ["La traza regional no delimita una ruptura medida en campo.", "A regional trace does not delimit a field-measured rupture."] },
  { id: "evidence", name: ["Indicadores geomorfológicos", "Geomorphic indicators"], resolution: ["Puntos representativos regionales", "Regional representative points"], limit: ["No son ubicaciones precisas ni huellas cartografiadas de cada forma.", "These are not precise locations or mapped footprints of individual landforms."] },
  { id: "hillshade", name: ["Relieve sombreado Esri", "Esri shaded relief"], resolution: ["Mosaico multifuente · detalle variable", "Multi-source mosaic · variable detail"], limit: ["Sirve para contexto visual, no para medir escarpes pequeños ni modelar inundación local.", "Visual context, not a basis for measuring small scarps or modelling local flooding."] },
  { id: "basins", name: ["Cuencas INAMHI / MAATE", "INAMHI / MAATE watersheds"], resolution: ["Escala no especificada en la ficha pública", "Scale unspecified in public metadata"], limit: ["No equivale a una delimitación detallada de las microcuencas de Tena y Archidona.", "Not equivalent to detailed delineation of Tena and Archidona subcatchments."] },
  { id: "stations", name: ["Estaciones INAMHI", "INAMHI stations"], resolution: ["Ubicación puntual · instantánea de metadatos", "Point locations · metadata snapshot"], limit: ["No hay series medidas en esta capa. Un punto no representa la lluvia de todo el cantón.", "This layer has no measured time series. A point does not represent rainfall across a canton."] },
  { id: "precipitation", name: ["Precipitación IMERG", "IMERG precipitation"], resolution: ["Cuadrícula 0,1° · ≈11 km en Napo", "0.1° grid · ≈11 km in Napo"], limit: ["Tasa satelital, no acumulado ni medición por barrio. Acercar el mapa no añade detalle.", "Satellite rate, not accumulation or a neighbourhood measurement. Zoom adds no detail."] },
  { id: "air-temperature", name: ["Temperatura del aire AIRS", "AIRS air temperature"], resolution: ["Cuadrícula 1° · ≈111 km en Napo", "1° grid · ≈111 km in Napo"], limit: ["Contexto regional: no permite distinguir la temperatura de Tena frente a Archidona.", "Regional context: cannot resolve temperature differences between Tena and Archidona."] },
  { id: "cloud-fraction", name: ["Nubosidad MODIS", "MODIS cloud cover"], resolution: ["Producto con componentes de 1 y 5 km", "Product with 1 and 5 km components"], limit: ["Observación durante el paso satelital; huecos no significan cielo despejado.", "Observation during the satellite overpass; gaps do not mean clear skies."] },
  { id: "flood", name: ["Agua superficial VIIRS", "VIIRS surface water"], resolution: ["Cuadrícula de 250 m", "250 m grid"], limit: ["Nubes y vegetación pueden ocultar agua; no delimita amenaza ni sustituye verificación local.", "Clouds and vegetation can obscure water; not a hazard boundary or a substitute for local checks."] },
  { id: "thermal", name: ["Anomalías térmicas VIIRS", "VIIRS thermal anomalies"], resolution: ["Muestreo nominal de 375 m", "Nominal 375 m sampling"], limit: ["Una detección no define el tamaño de un incendio ni confirma su causa.", "A detection does not define fire size or confirm its cause."] },
  { id: "earthquakes", name: ["Sismos USGS", "USGS earthquakes"], resolution: ["Localización con incertidumbre por evento", "Location with event-specific uncertainty"], limit: ["La cercanía a una falla no identifica por sí sola la estructura responsable.", "Proximity to a fault alone does not identify the responsible structure."] },
]);

export function activeSpatialContexts(activeLayers, language = "es", { demo = false } = {}) {
  const locale = language === "en" ? 1 : 0;
  return SPATIAL_CONTEXTS.filter((entry) => activeLayers[entry.id] === true).map((entry) => ({
    id: entry.id,
    name: entry.name[locale],
    resolution: demo && ["faults", "evidence"].includes(entry.id)
      ? ["Geometría sintética · sin escala científica", "Synthetic geometry · no scientific scale"][locale] : entry.resolution[locale],
    limit: demo && ["faults", "evidence"].includes(entry.id)
      ? ["Solo prueba de interfaz, no observación de Ecuador.", "Interface testing only, not an observation from Ecuador."][locale] : entry.limit[locale],
  }));
}
