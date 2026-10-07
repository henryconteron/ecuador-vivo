"""Safe, structured edits for the local Ecuador Vivo website editor."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import uuid


ROOT = Path(__file__).resolve().parents[2]
PAGE_FILES = (
    "index.html", "explore.html", "learn.html", "datos.html", "biblioteca.html",
    "andes-pulso.html", "geologia.html", "georreferenciar.html", "laboratorio.html",
    "lecturas.html", "modelos.html", "rivers.html", "rocks.html",
)
THEME_VARS = (
    "forest", "paper", "portal-ink", "portal-muted", "lime", "portal-line", "sage", "coral",
)
MAP_SOURCES = {
    "faults": ("Fallas geológicas", "fault-toggle"),
    "evidence": ("Indicadores geomorfológicos", "evidence-toggle"),
    "hillshade": ("Relieve sombreado", "hillshade-toggle"),
    "basins": ("Cuencas hidrográficas", "basin-toggle"),
    "stations": ("Estaciones hidrometeorológicas", "station-toggle"),
    "precipitation": ("Precipitación", "precipitation-toggle"),
    "airTemperature": ("Temperatura del aire", "air-temperature-toggle"),
    "cloudFraction": ("Fracción de nube", "cloud-fraction-toggle"),
    "flood": ("Agua superficial / inundación observada", "flood-toggle"),
    "thermal": ("Anomalías térmicas", "thermal-toggle"),
    "earthquakes": ("Sismicidad reciente", "earthquake-toggle"),
    "geology": ("Geología regional", "geology-toggle"),
    "landcover": ("Cobertura del suelo", "landcover-toggle"),
    "rivers": ("Imágenes de ríos", "rivers-toggle"),
    "spectral": ("Imágenes e índices espectrales", "spectral-map-toggle"),
}


@dataclass
class Editable:
    key: str
    tag: str
    start: int
    raw: str
    attrs: dict[str, str]
    es_attr: str
    en_attr: str
    label: str


class _Scan(HTMLParser):
    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.offsets = [0]
        for match in re.finditer("\n", source):
            self.offsets.append(match.end())
        self.editables: list[Editable] = []
        self.sections: list[dict[str, str | bool]] = []
        self.blocks: list[dict[str, str]] = []
        self.stack: list[str] = []
        self.void_tags = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        line, col = self.getpos()
        start = self.offsets[line - 1] + col
        raw = self.get_starttag_text() or ""
        attr_map = {key: value or "" for key, value in attrs}
        pairs = (
            ("data-es", "data-en"),
            ("data-title-es", "data-title-en"),
            ("data-alt-es", "data-alt-en"),
            ("data-placeholder-es", "data-placeholder-en"),
            ("data-aria-es", "data-aria-en"),
        )
        for es_attr, en_attr in pairs:
            if es_attr in attr_map and en_attr in attr_map:
                ordinal = len(self.editables) + 1
                ident = attr_map.get("id") or attr_map.get("class", "").split(" ")[0]
                excerpt = re.sub(r"\s+", " ", attr_map[es_attr]).strip()
                label = f"{ordinal:03} · {tag}{' #' + ident if ident else ''} · {excerpt[:88]}"
                self.editables.append(Editable(
                    key=f"text-{ordinal}", tag=tag, start=start, raw=raw,
                    attrs=attr_map, es_attr=es_attr, en_attr=en_attr, label=label,
                ))

        if tag == "meta" and attr_map.get("name", "").lower() == "description" and "content" in attr_map:
            ordinal = len(self.editables) + 1
            self.editables.append(Editable(
                key=f"text-{ordinal}", tag=tag, start=start, raw=raw,
                attrs=attr_map, es_attr="content", en_attr="",
                label=f"{ordinal:03} · meta description · {attr_map['content'][:88]}",
            ))

        inside_main = "main" in self.stack
        top_level_block = tag in {"section", "article", "nav", "aside"} and (
            tag == "section" and "section" not in self.stack
            or self.stack and self.stack[-1] == "main"
        )
        if inside_main and top_level_block:
            ordinal = len(self.sections) + 1
            ident = attr_map.get("data-site-admin-id") or attr_map.get("id") or f"admin-section-{ordinal:02}"
            display = attr_map.get("id") or attr_map.get("class", "").split(" ")[0] or tag
            is_block = bool(attr_map.get("data-site-admin-block"))
            self.sections.append({
                "id": ident,
                "label": f"{ordinal:02} · {display}",
                "visible": "hidden" not in attr_map,
                "start": str(start),
                "raw": raw,
                "block": is_block,
            })
            if is_block:
                self.blocks.append({"id": ident, "label": display})
        if tag not in self.void_tags:
            self.stack.append(tag)

    def handle_endtag(self, tag: str):
        if tag in self.stack:
            self.stack = self.stack[:len(self.stack) - 1 - self.stack[::-1].index(tag)]


def scan_html(source: str) -> tuple[list[Editable], list[dict[str, str | bool]], list[dict[str, str]]]:
    parser = _Scan(source)
    parser.feed(source)
    return parser.editables, parser.sections, parser.blocks


def _replace_attribute(raw: str, name: str, value: str | None) -> str:
    pattern = re.compile(rf"(?<![\w:-]){re.escape(name)}\s*=\s*([\"'])(.*?)\1", re.DOTALL)
    escaped = escape(value or "", quote=True)
    if pattern.search(raw):
        return pattern.sub(lambda m: f"{name}={m.group(1)}{escaped}{m.group(1)}", raw, count=1)
    if value is None:
        return raw
    return raw[:-1].rstrip() + f' {name}="{escaped}">'


def apply_text_edits(source: str, edits: dict[str, dict[str, str]]) -> str:
    entries, _, _ = scan_html(source)
    replacements = []
    for entry in entries:
        values = edits.get(entry.key)
        if not values:
            continue
        raw = entry.raw
        raw = _replace_attribute(raw, entry.es_attr, values.get("es"))
        if entry.en_attr:
            raw = _replace_attribute(raw, entry.en_attr, values.get("en"))
        if "href" in values and "href" in entry.attrs:
            raw = _replace_attribute(raw, "href", values["href"])
        replacements.append((entry.start, entry.start + len(entry.raw), raw))
    for start, end, raw in reversed(replacements):
        source = source[:start] + raw + source[end:]
    return source


def apply_section_visibility(source: str, visibility: dict[str, bool]) -> str:
    _, sections, _ = scan_html(source)
    replacements = []
    for section in sections:
        enabled = visibility.get(str(section["id"]))
        if enabled is None:
            continue
        raw = str(section["raw"])
        if "id=" not in raw and "data-site-admin-id=" not in raw:
            raw = _replace_attribute(raw, "data-site-admin-id", str(section["id"]))
        if enabled:
            raw = re.sub(r"\s+hidden(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+))?(?=\s|/?>)", "", raw, count=1)
            raw = re.sub(r'\s+data-site-admin-hidden=("[^"]*"|\x27[^\x27]*\x27)', '', raw)
        else:
            if not re.search(r"(?<![\w:-])hidden(?:\s|=|/?>)", raw):
                raw = raw[:-1].rstrip() + " hidden>"
            raw = _replace_attribute(raw, 'data-site-admin-hidden', 'true')
        replacements.append((int(section["start"]), int(section["start"]) + len(str(section["raw"])), raw))
    for start, end, raw in reversed(replacements):
        source = source[:start] + raw + source[end:]
    return source


def _safe_href(value: str) -> str:
    value = value.strip()
    if not value:
        return "#"
    if re.search(r'[\x00-\x20\\]', value) or re.match(r"^(javascript|data|vbscript):", value, re.IGNORECASE) or value.startswith("//"):
        raise ValueError("El enlace debe ser una ruta local o una dirección https segura.")
    if value.startswith(("https://", "mailto:", "tel:", "#", "/", "./", "../")):
        return value
    if re.fullmatch(r"[\w.-]+(?:/[\w./%-]*)?(?:\?[^<>\"']*)?(?:#[^<>\"']*)?", value):
        return value
    raise ValueError("El enlace debe ser una ruta local o una dirección https segura.")


def add_content_block(source: str, title_es: str, title_en: str, body_es: str, body_en: str,
                      link_es: str = "", link_en: str = "", href: str = "") -> tuple[str, str]:
    if "</main>" not in source.lower():
        raise ValueError("Esta página no contiene un bloque main donde añadir contenido.")
    block_id = f"editorial-{uuid.uuid4().hex[:10]}"
    link = ""
    if href.strip():
        safe_href = escape(_safe_href(href), quote=True)
        link = (f'<p><a class="button button-secondary" href="{safe_href}" '
                f'data-es="{escape(link_es, quote=True)}" data-en="{escape(link_en, quote=True)}">'
                f'{escape(link_es)}<span aria-hidden="true"> ↗</span></a></p>')
    block = (
        f'\n<section class="site-editor-block" data-site-admin-id="{block_id}" '
        f'data-site-admin-block="{block_id}">\n'
        f'<h2 data-es="{escape(title_es, quote=True)}" data-en="{escape(title_en, quote=True)}">{escape(title_es)}</h2>\n'
        f'<p data-es="{escape(body_es, quote=True)}" data-en="{escape(body_en, quote=True)}">{escape(body_es)}</p>\n'
        f'{link}\n</section>\n'
    )
    match = re.search(r"</main\s*>", source, re.IGNORECASE)
    return source[:match.start()] + block + source[match.start():], block_id


def remove_content_block(source: str, block_id: str) -> str:
    if not re.fullmatch(r"editorial-[a-f0-9]{10}", block_id):
        raise ValueError("Solo se pueden retirar bloques creados desde este panel.")
    pattern = re.compile(
        rf"\s*<section\b(?=[^>]*data-site-admin-block=[\"']{re.escape(block_id)}[\"'])[^>]*>.*?</section\s*>",
        re.IGNORECASE | re.DOTALL,
    )
    updated, count = pattern.subn("\n", source, count=1)
    if count != 1:
        raise ValueError("No se encontró el bloque seleccionado; no se modificó la página.")
    return updated


def read_theme(css: str) -> dict[str, str]:
    root = re.search(r":root\s*\{([^}]*)\}", css)
    if not root:
        raise ValueError("No se encontró la paleta :root en portal.css.")
    return {name: value.lower() for name, value in re.findall(r"--([\w-]+)\s*:\s*(#[0-9a-fA-F]{6})", root.group(1))}


def apply_theme(css: str, colors: dict[str, str], max_width: int | None = None) -> str:
    if not re.search(r":root\s*\{[^}]*\}", css):
        raise ValueError("No se encontró la paleta :root en portal.css.")
    updated = css
    for name in THEME_VARS:
        value = colors.get(name)
        if value and not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            raise ValueError(f"Color no válido para {name}.")
        if not value:
            continue
        pattern = re.compile(rf"(--{re.escape(name)}\s*:\s*)#[0-9a-fA-F]{{6}}")
        updated, count = pattern.subn(rf"\g<1>{value.lower()}", updated, count=1)
        if not count:
            raise ValueError(f"No existe la variable CSS --{name}.")
    if max_width is not None:
        if not 900 <= int(max_width) <= 1800:
            raise ValueError("El ancho del contenido debe estar entre 900 y 1800 px.")
        if "--site-main-width:" in updated:
            updated = re.sub(r"--site-main-width:\s*\d+px", f"--site-main-width:{int(max_width)}px", updated, count=1)
        else:
            updated = re.sub(r"(:root\s*\{)", rf"\1--site-main-width:{int(max_width)}px;", updated, count=1)
        updated = re.sub(r"\.portal-main\s*\{([^}]*)\}",
                          lambda m: ".portal-main{" + re.sub(r"max-width\s*:\s*[^;]+", "max-width:var(--site-main-width,1440px)", m.group(1)) + "}",
                          updated, count=1)
    return updated


def read_map_settings(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "mapSources": {key: True for key in MAP_SOURCES}}
    data = json.loads(path.read_text(encoding="utf-8"))
    sources = data.get("mapSources", {})
    return {"version": 1, "mapSources": {key: bool(sources.get(key, True)) for key in MAP_SOURCES},
            'customMapSources': data.get('customMapSources', [])}


def validate_custom_sources(rows):
    if not isinstance(rows, list) or len(rows) > 20:
        raise ValueError('Usa como máximo 20 fuentes personalizadas.')
    ids = set()
    for row in rows:
        ident = row.get('id', '')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', ident) or ident in ids or ident in MAP_SOURCES:
            raise ValueError('Cada fuente necesita un ID único en minúsculas y guiones.')
        ids.add(ident)
        if row.get('type') not in {'geojson', 'wms', 'xyz'} or row.get('system') not in {'earth', 'water', 'sky', 'life', 'risk'}:
            raise ValueError('Tipo de servicio o apartado inválido.')
        url = str(row.get('url', ''))
        if not url.startswith('https://') and not url.startswith('data/'):
            raise ValueError('La fuente debe usar HTTPS o un GeoJSON dentro de data/.')
        _safe_href(url)
        if not row.get('title_es') or not row.get('title_en') or not row.get('citation'):
            raise ValueError('Completa título en ambos idiomas y cita de cada fuente.')
        if row['type'] == 'wms' and not row.get('layers'):
            raise ValueError('Un servicio WMS necesita los nombres de sus capas.')
        if not re.fullmatch(r'#[0-9a-fA-F]{6}', row.get('color', '#55e2cb')):
            raise ValueError('El color debe ser #RRGGBB.')
    return rows


def write_map_settings(path: Path, settings: dict) -> None:
    safe = {"version": 1, "mapSources": {key: bool(settings.get("mapSources", {}).get(key, True)) for key in MAP_SOURCES}}
    path.write_text(json.dumps(safe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def translation_keys_for_page(page: str) -> list[str]:
    source = (ROOT / page).read_text(encoding="utf-8")
    parser = HTMLParser()
    keys: set[str] = set()

    class KeyScan(HTMLParser):
        def handle_starttag(self, tag, attrs):
            for attr, value in attrs:
                if attr in {"data-i18n", "data-i18n-placeholder", "data-i18n-aria", "data-i18n-title", "data-i18n-alt"} and value:
                    keys.add(value)

    scanner = KeyScan()
    scanner.feed(source)
    return sorted(keys)


def _translation_line(text: str, start: int, end: int, key: str) -> tuple[int, int, str] | None:
    target = re.compile(rf"(?m)^(\s*{re.escape(json.dumps(key, ensure_ascii=False))}\s*:\s*)(\"(?:\\.|[^\"\\])*\")(\s*,?\s*)$")
    match = target.search(text, start, end)
    if not match:
        return None
    return match.start(2), match.end(2), match.group(2)


def read_translation_pair(source: str, key: str) -> dict[str, str]:
    es_start = source.find("es: {")
    en_start = source.find("en: {", es_start + 5)
    end = source.rfind("\n  };", en_start)
    if es_start < 0 or en_start < 0 or end < 0:
        raise ValueError("No se reconocieron los bloques de idioma del catálogo.")
    result = {}
    for lang, start, stop in (("es", es_start, en_start), ("en", en_start, end)):
        found = _translation_line(source, start, stop, key)
        if found:
            result[lang] = json.loads(found[2])
    return result


def apply_translation_pair(source: str, key: str, es: str, en: str) -> str:
    es_start = source.find("es: {")
    en_start = source.find("en: {", es_start + 5)
    end = source.rfind("\n  };", en_start)
    if es_start < 0 or en_start < 0 or end < 0:
        raise ValueError("No se reconocieron los bloques de idioma del catálogo.")
    replacements = []
    for lang, start, stop, value in (("es", es_start, en_start, es), ("en", en_start, end, en)):
        found = _translation_line(source, start, stop, key)
        if found:
            replacements.append((found[0], found[1], json.dumps(value, ensure_ascii=False)))
    if len(replacements) != 2:
        raise ValueError(f"La clave {key} no aparece en español e inglés; no se guardó.")
    for start, stop, value in reversed(replacements):
        source = source[:start] + value + source[stop:]
    return source


def page_path(page: str) -> Path:
    if page not in PAGE_FILES:
        raise ValueError("La página seleccionada no pertenece a la lista segura del editor.")
    path = ROOT / page
    if path.parent != ROOT:
        raise ValueError("Ruta de página fuera del sitio.")
    return path
