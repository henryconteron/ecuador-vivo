const SEARCHABLE_PROPERTIES = Object.freeze([
  "nombre",
  "nombre_en",
  "provincia",
  "provincia_en",
  "sistema",
  "sistema_en",
  "catalog_id",
  "catalog_name",
  "fuente",
  "reference",
]);

export function hasCatalogFilters({ query = "", movement = "all" } = {}) {
  return String(query).trim() !== "" || movement !== "all";
}

export function filterFaultCatalog(
  features,
  { query = "", movement = "all" } = {},
  { normalize, movementOf },
) {
  const normalizedQuery = normalize(query);
  return features.filter((feature) => {
    const properties = feature.properties ?? {};
    const searchableText = normalize(
      SEARCHABLE_PROPERTIES.map((property) => properties[property]).filter(Boolean).join(" "),
    );
    const matchesQuery = normalizedQuery === "" || searchableText.includes(normalizedQuery);
    const matchesMovement = movement === "all" || movementOf(feature) === movement;
    return matchesQuery && matchesMovement;
  });
}

export function sortFaultCatalog(features, { localizedProperty, locale = "es" }) {
  return [...features].sort((left, right) =>
    localizedProperty(left, "nombre").localeCompare(
      localizedProperty(right, "nombre"),
      locale,
    ),
  );
}
