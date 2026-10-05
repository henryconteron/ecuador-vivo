import { loadRecentEarthquakes } from "./data.js";
import { filterEarthquakes, normalizeEarthquakeFilters } from "./seismicity.js";

export function createEarthquakePanel(map, earthquakeLayer, elements, context) {
  const { t, template, formatNumber, formatUtcDate, updateLegendVisibility, updateSourceCount, getSelectedPoint, renderPlaceExplanation } = context;

  let earthquakeCatalog = [];
  let visibleEarthquakeCatalog = [];
  let earthquakeGeneratedAt = null;
  let earthquakeState = "loading";
  let earthquakeRequestId = 0;
  let earthquakeAttributionAdded = false;

  function getEarthquakeFilters() {
    return normalizeEarthquakeFilters({
      days: elements.earthquakeDays.value,
      minimumMagnitude: elements.earthquakeMinimumMagnitude.value,
      depth: elements.earthquakeDepthFilter.value,
    });
  }

  function locateEarthquake(feature) {
    elements.earthquakeToggle.checked = true;
    if (!map.hasLayer(earthquakeLayer)) earthquakeLayer.addTo(map);
    updateLegendVisibility();
    const [longitude, latitude] = feature.geometry.coordinates;
    map.setView([latitude, longitude], Math.max(map.getZoom(), 9));
    earthquakeLayer.eachLayer((layer) => {
      if (layer.feature === feature) layer.openPopup();
    });
    if (window.matchMedia("(max-width: 64rem)").matches) {
      document.querySelector("#map").scrollIntoView({
        behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth",
        block: "start",
      });
    }
  }

  function renderEarthquakeList(features) {
    elements.earthquakeList.replaceChildren();
    elements.earthquakeListCount.textContent = String(features.length);
    if (features.length === 0) {
      const empty = document.createElement("li");
      empty.className = "earthquake-list-empty";
      empty.textContent = t("earthquakes.listEmpty");
      elements.earthquakeList.append(empty);
      return;
    }
    const maximumListedEvents = 200;
    features.slice(0, maximumListedEvents).forEach((feature) => {
      const properties = feature.properties ?? {};
      const depth = Number(feature.geometry.coordinates?.[2]);
      const item = document.createElement("li");
      const button = document.createElement("button");
      const title = document.createElement("strong");
      const detail = document.createElement("small");
      button.type = "button";
      title.textContent = `M ${formatNumber(properties.mag)} · ${properties.place || t("value.unavailable")}`;
      detail.textContent = `${formatUtcDate(properties.time)} · ${t("popup.depth")} ${
        Number.isFinite(depth) ? `${formatNumber(depth)} km` : t("value.unavailable")
      }`;
      button.append(title, detail);
      button.addEventListener("click", () => locateEarthquake(feature));
      item.append(button);
      elements.earthquakeList.append(item);
    });
    if (features.length > maximumListedEvents) {
      const limitNotice = document.createElement("li");
      limitNotice.className = "earthquake-list-empty";
      limitNotice.textContent = template("earthquakes.listLimited", {
        shown: maximumListedEvents,
        total: features.length,
      });
      elements.earthquakeList.append(limitNotice);
    }
  }

  function updateEarthquakeStatus() {
    elements.earthquakeStatus.dataset.state = earthquakeState;
    if (earthquakeState === "loading") {
      elements.earthquakeStatus.textContent = t("earthquakes.loading");
      return;
    }
    if (earthquakeState === "error") {
      elements.earthquakeStatus.textContent = t("earthquakes.error");
      return;
    }
    elements.earthquakeStatus.textContent = template("earthquakes.loaded", {
      count: visibleEarthquakeCatalog.length,
      date: formatUtcDate(earthquakeGeneratedAt),
    });
  }

  function renderEarthquakes() {
    visibleEarthquakeCatalog = filterEarthquakes(earthquakeCatalog, getEarthquakeFilters());
    earthquakeLayer.clearLayers();
    earthquakeLayer.addData({ type: "FeatureCollection", features: visibleEarthquakeCatalog });
    elements.earthquakeCount.textContent = String(visibleEarthquakeCatalog.length);
    elements.earthquakeToggle.disabled = earthquakeState !== "loaded";
    if (earthquakeState === "error") elements.earthquakeToggle.checked = false;
    if (elements.earthquakeToggle.checked && !map.hasLayer(earthquakeLayer)) earthquakeLayer.addTo(map);
    if (!elements.earthquakeToggle.checked && map.hasLayer(earthquakeLayer)) map.removeLayer(earthquakeLayer);
    updateLegendVisibility();
    renderEarthquakeList(visibleEarthquakeCatalog);
    updateEarthquakeStatus();
    updateSourceCount();
    if (getSelectedPoint()) renderPlaceExplanation();
  }

  async function loadEarthquakeData() {
    const requestId = ++earthquakeRequestId;
    const filters = getEarthquakeFilters();
    earthquakeState = "loading";
    elements.earthquakeToggle.disabled = true;
    updateEarthquakeStatus();
    try {
      const result = await loadRecentEarthquakes({
        days: filters.days,
        minimumMagnitude: filters.minimumMagnitude,
      });
      if (requestId !== earthquakeRequestId) return;
      earthquakeCatalog = result.features;
      earthquakeGeneratedAt = result.generatedAt;
      earthquakeState = "loaded";
      if (!earthquakeAttributionAdded) {
        map.attributionControl.addAttribution(
          'Earthquake data: <a href="https://earthquake.usgs.gov/earthquakes/search/" target="_blank" rel="noopener">USGS</a>',
        );
        earthquakeAttributionAdded = true;
      }
    } catch (error) {
      if (requestId !== earthquakeRequestId) return;
      console.error(error);
      earthquakeCatalog = [];
      earthquakeGeneratedAt = null;
      earthquakeState = "error";
    }
    renderEarthquakes();
  }

  return {
    loadEarthquakeData,
    renderEarthquakes,
    updateStatus: updateEarthquakeStatus,
    getVisibleCatalog: () => visibleEarthquakeCatalog,
    getState: () => earthquakeState,
    hasData: () => earthquakeCatalog.length > 0,
  };
}
