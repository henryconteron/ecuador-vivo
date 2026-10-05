export function createWmsLayerController(map, layer, { statusEl, dateEl, i18nPrefix, t, template }) {
  let state = "off";
  let tileErrors = 0;

  function updateStatus() {
    if (!statusEl) return;
    
    statusEl.dataset.state = state;
    const date = dateEl?.value;
    
    if (state === "off") {
      statusEl.textContent = t(`${i18nPrefix}.off`);
    } else if (state === "loading") {
      statusEl.textContent = template(`${i18nPrefix}.loading`, { date });
    } else if (state === "error") {
      statusEl.textContent = t(`${i18nPrefix}.error`);
    } else {
      statusEl.textContent = template(`${i18nPrefix}.loaded`, { date });
    }
  }

  layer.on("loading", () => {
    if (!map.hasLayer(layer)) return;
    state = "loading";
    tileErrors = 0;
    updateStatus();
  });

  layer.on("load", () => {
    if (!map.hasLayer(layer)) return;
    state = tileErrors >= 2 ? "error" : "loaded";
    updateStatus();
  });

  layer.on("tileerror", () => {
    tileErrors++;
    if (tileErrors >= 2) {
      state = "error";
      updateStatus();
    }
  });

  return {
    activate() {
      state = "loading";
      tileErrors = 0;
      layer.addTo(map);
      updateStatus();
    },
    deactivate() {
      map.removeLayer(layer);
      state = "off";
      updateStatus();
    },
    get state() {
      return state;
    },
    updateStatus,
  };
}
