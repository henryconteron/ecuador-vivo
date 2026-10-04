export const ATLAS_SYSTEMS = Object.freeze(["earth", "water", "sky", "life", "risk"]);

export function normalizeAtlasSystem(value) {
  return ATLAS_SYSTEMS.includes(value) ? value : "earth";
}

export function contentBelongsToSystem(value, system) {
  const activeSystem = normalizeAtlasSystem(system);
  return String(value || "")
    .split(/\s+/)
    .filter(Boolean)
    .includes(activeSystem);
}

export function selectedSystems(system, combined = []) {
  return [...new Set([normalizeAtlasSystem(system), ...combined.filter(value => ATLAS_SYSTEMS.includes(value))])];
}

export function contentBelongsToSelection(value, system, combined = []) {
  return selectedSystems(system, combined).some(item => contentBelongsToSystem(value, item));
}

// Keep user preferences, but remove actual layers outside the explicit selection.
// Dispatching change uses each layer's existing cleanup (including async cancellation).
export function createSystemScope(controls, onChange = control => control.dispatchEvent(new Event("change"))) {
  const preferences = new Map(controls.map(control => [control, control.checked]));
  let updating = false;
  controls.forEach(control => control.addEventListener("change", () => {
    if (!updating) preferences.set(control, control.checked);
  }));
  return (system, combined = [], restore = true) => {
    updating = true;
    try {
      for (const control of controls) {
        const owners = control.closest("[data-system-content]")?.dataset.systemContent;
        const checked = Boolean(contentBelongsToSelection(owners, system, combined) && (restore ? preferences.get(control) : control.checked));
        if (control.checked !== checked) { control.checked = checked; onChange(control); }
      }
    } finally { updating = false; }
  };
}
