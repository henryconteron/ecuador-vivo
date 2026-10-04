// Shared language/navigation; independent of live data or external services.
const supported = new Set(["es", "en"]);
const storedLanguage = () => { try { return localStorage.getItem("atlas-language"); } catch { return null; } };
let language = new URLSearchParams(location.search).get("lang") || storedLanguage() || "es";
if (!supported.has(language)) language = "es";
export function applyPortalLanguage(next = language) {
  language = supported.has(next) ? next : "es";
  document.documentElement.lang = language;
  document.querySelectorAll("[data-es][data-en]").forEach(el => { el.textContent = el.dataset[language]; });
  for (const [selector, property, es, en] of [
    ["[data-placeholder-es][data-placeholder-en]", "placeholder", "placeholderEs", "placeholderEn"],
    ["[data-alt-es][data-alt-en]", "alt", "altEs", "altEn"],
  ]) document.querySelectorAll(selector).forEach(el => { el[property] = el.dataset[language === "es" ? es : en]; });
  document.querySelectorAll("[data-aria-es][data-aria-en]").forEach(el => el.setAttribute("aria-label", el.dataset[language === "es" ? "ariaEs" : "ariaEn"]));
  document.querySelectorAll("[data-portal-language]").forEach(button => {
    button.textContent = language === "es" ? "EN" : "ES";
    button.setAttribute("aria-label", language === "es" ? "Switch to English" : "Cambiar a español");
  });
  document.querySelectorAll("a[data-keep-lang]").forEach(link => {
    const url = new URL(link.getAttribute("href"), location.href);
    if (url.origin !== location.origin) return;
    url.searchParams.set("lang", language);
    link.setAttribute("href", url.pathname + url.search + url.hash);
  });
  const title = document.querySelector("title[data-title-es]");
  if (title) document.title = title.dataset[language === "es" ? "titleEs" : "titleEn"];
  try { localStorage.setItem("atlas-language", language); } catch { /* Works with storage disabled. */ }
  window.dispatchEvent(new CustomEvent("portal:language", { detail: { lang: language } }));
  return language;
}
window.portalLanguage = () => language;
window.applyPortalLanguage = applyPortalLanguage;
document.querySelectorAll("[data-portal-language]").forEach(button => button.addEventListener("click", () => {
  applyPortalLanguage(language === "es" ? "en" : "es");
  const url = new URL(location.href); url.searchParams.set("lang", language); history.replaceState(null, "", url);
}));
window.addEventListener("atlas:languagechange", event => applyPortalLanguage(event.detail.language));
applyPortalLanguage();

