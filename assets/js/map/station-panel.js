import {
  filterStations,
  loadStationSnapshot,
  normalizeStationCategory,
  STATION_SOURCE,
} from "./stations.js";

function popupDetail(documentObject, term, value, unavailable) {
  const group = documentObject.createElement("div");
  const label = documentObject.createElement("dt");
  const description = documentObject.createElement("dd");
  label.textContent = term;
  description.textContent = value || unavailable;
  group.append(label, description);
  return group;
}

export function stationCategoryLabel(feature, t) {
  return t(`stations.${normalizeStationCategory(feature.properties?.categoria)}`);
}

export function createStationPopup(feature, options) {
  const {
    t,
    template,
    formatNumber,
    documentObject = document,
  } = options;
  const properties = feature.properties ?? {};
  const unavailable = t("value.unavailable");
  const article = documentObject.createElement("article");
  const eyebrow = documentObject.createElement("p");
  const title = documentObject.createElement("h3");
  const name = documentObject.createElement("p");
  const details = documentObject.createElement("dl");
  const link = documentObject.createElement("a");

  article.className = "station-popup";
  eyebrow.className = "station-popup-kicker";
  eyebrow.textContent = stationCategoryLabel(feature, t);
  title.textContent = properties.codigo || unavailable;
  name.textContent = properties.nombre || unavailable;
  details.append(
    popupDetail(
      documentObject,
      t("stations.popupAltitude"),
      Number.isFinite(properties.altitud_m)
        ? template("stations.altitude", { altitude: formatNumber(properties.altitud_m, 0) })
        : unavailable,
      unavailable,
    ),
    popupDetail(documentObject, t("stations.popupOwner"), properties.propietario, unavailable),
    popupDetail(
      documentObject,
      t("stations.popupLocation"),
      [properties.canton, properties.provincia].filter(Boolean).join(", "),
      unavailable,
    ),
    popupDetail(
      documentObject,
      t("stations.popupState"),
      t("stations.transmitting"),
      unavailable,
    ),
  );
  link.href = STATION_SOURCE.viewer;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.textContent = t("stations.openViewer");
  article.append(eyebrow, title, name, details, link);
  return article;
}

export function createStationPanel(map, layer, elements, options) {
  const {
    t,
    template,
    formatUtcDate,
    loadSnapshot = loadStationSnapshot,
    updateLegendVisibility,
    updateSourceCount,
    getSelectedPoint,
    renderPlaceExplanation,
  } = options;
  let catalog = [];
  let visibleCatalog = [];
  let metadata = {};
  let state = "loading";
  let attributionAdded = false;

  function updateStatus() {
    elements.stationStatus.dataset.state = state;
    if (state === "loading") {
      elements.stationStatus.textContent = t("stations.loading");
    } else if (state === "error") {
      elements.stationStatus.textContent = t("stations.error");
    } else if (map.hasLayer(layer)) {
      elements.stationStatus.textContent = template("stations.visible", {
        visible: visibleCatalog.length,
        total: catalog.length,
      });
    } else {
      elements.stationStatus.textContent = template("stations.ready", { count: catalog.length });
    }
  }

  function updateRetrievedAt() {
    elements.stationRetrievedAt.dateTime = metadata.retrievedAt || "";
    elements.stationRetrievedAt.textContent = metadata.retrievedAt
      ? formatUtcDate(metadata.retrievedAt)
      : t("value.unavailable");
  }

  function render() {
    visibleCatalog = filterStations(catalog, elements.stationCategory.value);
    layer.clearLayers();
    layer.addData({ type: "FeatureCollection", features: visibleCatalog });
    updateStatus();
    updateLegendVisibility();
    updateSourceCount();
    if (getSelectedPoint()) renderPlaceExplanation();
  }

  function setActive(active) {
    elements.stationCategory.disabled = !active;
    if (active) layer.addTo(map);
    else map.removeLayer(layer);
    updateStatus();
    updateLegendVisibility();
    updateSourceCount();
    if (getSelectedPoint()) renderPlaceExplanation();
  }

  async function load() {
    state = "loading";
    elements.stationToggle.disabled = true;
    updateStatus();
    try {
      const result = await loadSnapshot();
      catalog = result.features;
      metadata = result.metadata;
      state = "loaded";
      elements.stationToggle.disabled = false;
      updateRetrievedAt();
      if (!attributionAdded) {
        map.attributionControl.addAttribution(
          `<a href="${STATION_SOURCE.viewer}" target="_blank" rel="noopener">Estaciones INAMHI</a>`,
        );
        attributionAdded = true;
      }
      render();
    } catch (error) {
      console.error(error);
      catalog = [];
      visibleCatalog = [];
      state = "error";
      elements.stationToggle.checked = false;
      elements.stationToggle.disabled = true;
      elements.stationCategory.disabled = true;
      layer.clearLayers();
      updateStatus();
      updateRetrievedAt();
      updateLegendVisibility();
      updateSourceCount();
    }
  }

  return {
    get catalog() {
      return catalog;
    },
    get visibleCatalog() {
      return visibleCatalog;
    },
    get state() {
      return state;
    },
    load,
    render,
    setActive,
    updateRetrievedAt,
    updateStatus,
  };
}
