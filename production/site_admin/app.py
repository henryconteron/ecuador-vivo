"""Private, local-only control panel for the Ecuador Vivo static website."""

from __future__ import annotations

import json
import hashlib
import datetime as dt
import uuid
import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import site_editor as editor  # noqa: E402
import content_manager as manager
from preview_server import start_preview

st.set_page_config(page_title="Ecuador Vivo · Panel personal", page_icon="🛠️", layout="wide")
st.title("Panel personal · Ecuador Vivo")
st.caption("Editor local de la web. Los cambios no se publican hasta que tú confirmes una acción de Git.")

PAGES = editor.PAGE_FILES
st.session_state.setdefault("page", "index.html")
st.session_state.setdefault("baseline_status", {})
st.session_state.setdefault("publishable_paths", set())
st.session_state.setdefault("saved_hashes", {})


def git(*args: str, timeout: int = 20) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True,
                          encoding="utf-8", errors="replace", timeout=timeout, check=False)


def remember_baseline(relative: str) -> None:
    if relative in st.session_state.baseline_status:
        return
    status = git("status", "--porcelain", "--", relative).stdout.strip()
    st.session_state.baseline_status[relative] = status
    if not status:
        st.session_state.publishable_paths.add(relative)


def save_path(relative: str, content: str | bytes, expected=None) -> None:
    remember_baseline(relative)
    target = (ROOT / relative).resolve()
    if not target.is_relative_to(ROOT.resolve()) or any(part.startswith('.') for part in Path(relative).parts):
        raise ValueError('Ruta fuera del sitio o archivo privado.')
    if (relative not in editor.PAGE_FILES and relative not in {
            'assets/js/i18n.js', 'assets/css/portal.css', 'data/site-settings.json',
            *(item[0] for item in manager.CATALOGS.values())}
            and not relative.startswith('assets/media/editor/')):
        raise ValueError('El panel no escribe código ejecutable ni archivos internos.')
    if expected is not None and (not target.is_file() or target.read_text(encoding='utf-8') != expected):
        raise ValueError('El archivo cambió fuera del panel. Recarga antes de guardar para conservar esos cambios.')
    payload = content.encode('utf-8') if isinstance(content, str) else content
    backup_dir = ROOT / '_local/site-admin/backups'
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / (dt.datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8])
    if target.exists():
        backup.with_suffix('.bak').write_bytes(target.read_bytes())
    backup.with_suffix('.json').write_text(json.dumps({
        'path': relative, 'existed': target.exists(),
        'after_sha256': hashlib.sha256(payload).hexdigest(),
        'at': dt.datetime.now().isoformat(),
    }), encoding='utf-8')
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + '.admin-tmp')
    temporary.write_bytes(payload)
    temporary.replace(target)
    st.session_state.saved_hashes[relative] = hashlib.sha256(target.read_bytes()).hexdigest()
    st.session_state.last_saved = relative


def current_source(page: str) -> str:
    return editor.page_path(page).read_text(encoding="utf-8")


page = st.selectbox("Página", PAGES, format_func=lambda item: {
    "index.html": "Inicio", "explore.html": "Visor principal", "learn.html": "Aprender",
    "datos.html": "Datos", "biblioteca.html": "Biblioteca", "andes-pulso.html": "Andes Pulso",
}.get(item, item.replace(".html", "").replace("-", " ").title()), key="page")

if st.session_state.get("last_saved"):
    st.success(f"Guardado localmente: {st.session_state.pop('last_saved')}")

content_tab, elements_tab, structure_tab, catalogs_tab, resources_tab, design_tab, map_tab, preview_tab, history_tab, publish_tab = st.tabs(
    ["Textos e idiomas", "Elementos", "Bloques", "Catálogos y videos", "Recursos", "Diseño", "Capas del visor", "Vista previa", "Historial", "Cambios y GitHub"]
)

with content_tab:
    source = current_source(page)
    editables, _, _ = editor.scan_html(source)
    if not editables:
        st.info("Esta página no tiene textos bilingües marcados que el panel pueda editar todavía.")
    else:
        st.markdown("Edita los textos que la web ya publica en español e inglés. Los campos se escapan como texto, no como HTML.")
        chosen = st.selectbox("Texto de la página", editables, format_func=lambda row: row.label)
        st.caption(f"Elemento: `{chosen.tag}` · clave local `{chosen.key}`. No se modifica la estructura interna del componente.")
        with st.form("page_text_form"):
            new_es = st.text_area("Español", value=chosen.attrs.get(chosen.es_attr, ""), height=110, key=f'copy-es-{page}-{chosen.key}')
            new_en = st.text_area("English", value=chosen.attrs.get(chosen.en_attr, "") if chosen.en_attr else "", height=110,
                                  disabled=not bool(chosen.en_attr), key=f'copy-en-{page}-{chosen.key}')
            href_value = chosen.attrs.get("href", "")
            new_href = st.text_input("Enlace (si el texto es un vínculo)", value=href_value,
                                     disabled="href" not in chosen.attrs, key=f'copy-href-{page}-{chosen.key}',
                                     help="Acepta rutas del sitio, fragmentos, https://, mailto: o tel:. No acepta código ejecutable.")
            submitted = st.form_submit_button("Guardar texto en esta página", type="primary")
        if submitted:
            try:
                patch = {chosen.key: {"es": new_es, "en": new_en}}
                if "href" in chosen.attrs:
                    patch[chosen.key]["href"] = editor._safe_href(new_href)
                updated = editor.apply_text_edits(source, patch)
                relative = page
                save_path(relative, updated, expected=source)
                st.rerun()
            except (ValueError, OSError) as exc:
                st.error(str(exc))

    keys = editor.translation_keys_for_page(page)
    if keys:
        st.divider()
        st.subheader("Textos del visor y etiquetas traducidas")
        st.caption("Incluye etiquetas que viven en el catálogo de idioma, por ejemplo nombres y mensajes de las capas del mapa.")
        i18n_path = ROOT / "assets/js/i18n.js"
        i18n_source = i18n_path.read_text(encoding="utf-8")
        pairs = {}
        for key in keys:
            try:
                pair = editor.read_translation_pair(i18n_source, key)
                if len(pair) == 2:
                    pairs[key] = pair
            except ValueError:
                continue
        if pairs:
            chosen_key = st.selectbox("Etiqueta", list(pairs), format_func=lambda key: f"{key} · {pairs[key]['es'][:70]}")
            with st.form("translation_form"):
                trans_es = st.text_area("Español", value=pairs[chosen_key]["es"], key='translation_es_' + chosen_key)
                trans_en = st.text_area("English", value=pairs[chosen_key]["en"], key='translation_en_' + chosen_key)
                update_translation = st.form_submit_button("Guardar traducción")
            if update_translation:
                try:
                    save_path("assets/js/i18n.js", editor.apply_translation_pair(i18n_source, chosen_key, trans_es, trans_en), expected=i18n_source)
                    st.rerun()
                except (ValueError, OSError) as exc:
                    st.error(str(exc))

with elements_tab:
    manager.show_elements(page, current_source(page), save_path)

with catalogs_tab:
    manager.show_catalogs(ROOT, save_path)

with resources_tab:
    manager.show_resources(ROOT, save_path)

with structure_tab:
    source = current_source(page)
    _, sections, blocks = editor.scan_html(source)
    st.subheader("Mostrar u ocultar bloques")
    st.caption("Se controlan los bloques principales dentro de `<main>`. Ocultar conserva el contenido y no elimina datos ni recursos.")
    if sections:
        current_rows = [{"id": row["id"], "bloque": row["label"], "visible": row["visible"]} for row in sections]
        edited_rows = st.data_editor(
            pd.DataFrame(current_rows), hide_index=True, width="stretch",
            disabled=["id", "bloque"],
            column_config={"id": None, "bloque": st.column_config.TextColumn("Bloque"),
                           "visible": st.column_config.CheckboxColumn("Visible en la web")},
            key=f"sections-{page}",
        )
        if st.button("Guardar visibilidad de bloques", key=f"save-sections-{page}", type="primary"):
            visibility = {str(row["id"]): bool(row["visible"]) for row in edited_rows.to_dict("records")}
            try:
                save_path(page, editor.apply_section_visibility(source, visibility), expected=source)
                st.rerun()
            except (ValueError, OSError) as exc:
                st.error(str(exc))
    else:
        st.info("No encontramos bloques principales editables en esta página.")

    st.divider()
    st.subheader("Añadir un bloque editorial")
    with st.form("add_editorial_block"):
        block_title_es = st.text_input("Título · español")
        block_title_en = st.text_input("Title · English")
        block_body_es = st.text_area("Texto · español")
        block_body_en = st.text_area("Text · English")
        block_link_es = st.text_input("Texto del botón · español (opcional)")
        block_link_en = st.text_input("Button label · English (optional)")
        block_href = st.text_input("Destino del botón (opcional)", placeholder="datos.html o https://…")
        block_media_kind = st.selectbox('Contenido visual adicional', ['Sin recurso', 'Imagen', 'Video'])
        block_media_href = st.text_input('Ruta o URL https del recurso', placeholder='assets/media/editor/foto.jpg')
        block_media_alt = st.text_input('Descripción del recurso / texto alternativo')
        add_block = st.form_submit_button("Añadir bloque al final de la página", type="primary")
    if add_block:
        if not block_title_es.strip() or not block_title_en.strip() or not block_body_es.strip() or not block_body_en.strip():
            st.error("Completa título y texto en ambos idiomas.")
        else:
            try:
                updated, block_id = editor.add_content_block(source, block_title_es, block_title_en,
                    block_body_es, block_body_en, block_link_es, block_link_en, block_href)
                if block_media_kind != 'Sin recurso' and block_media_href:
                    from html import escape
                    href = escape(editor._safe_href(block_media_href), quote=True)
                    alt = escape(block_media_alt, quote=True)
                    extra = (f'<figure><img src="{href}" alt="{alt}" loading="lazy" style="max-width:100%"><figcaption>{alt}</figcaption></figure>'
                             if block_media_kind == 'Imagen' else f'<video controls preload="metadata" src="{href}" aria-label="{alt}" style="max-width:100%"></video>')
                    marker = updated.find('data-site-admin-block="' + block_id)
                    position = updated.find('</section>', marker)
                    updated = updated[:position] + extra + updated[position:]
                save_path(page, updated, expected=source)
                st.success(f"Bloque creado ({block_id}).")
                st.rerun()
            except (ValueError, OSError) as exc:
                st.error(str(exc))
    if blocks:
        st.markdown("**Bloques añadidos desde este panel**")
        block = st.selectbox("Selecciona uno para retirarlo", blocks, format_func=lambda row: row["id"])
        if st.button("Retirar bloque seleccionado", type="secondary"):
            try:
                save_path(page, editor.remove_content_block(source, block["id"]), expected=source)
                st.rerun()
            except (ValueError, OSError) as exc:
                st.error(str(exc))

with design_tab:
    css_path = ROOT / "assets/css/portal.css"
    css_source = css_path.read_text(encoding="utf-8")
    try:
        theme = editor.read_theme(css_source)
    except ValueError as exc:
        theme = {}
        st.error(str(exc))
    st.subheader("Paleta global")
    st.caption("La paleta cambia el sistema visual compartido por las páginas principales; no altera estilos de mapas de datos ni gráficos científicos.")
    labels = {"forest": "Bosque / fondo oscuro", "paper": "Fondo claro", "portal-ink": "Texto principal",
              "portal-muted": "Texto secundario", "lime": "Acento", "portal-line": "Bordes claros",
              "sage": "Acento secundario", "coral": "Contraste cálido"}
    color_cols = st.columns(4)
    chosen_colors = {}
    for idx, token in enumerate(editor.THEME_VARS):
        with color_cols[idx % 4]:
            chosen_colors[token] = st.color_picker(labels[token], theme.get(token, "#102b28"), key=f"theme-{token}")
    width_current = 1440
    match = __import__("re").search(r"--site-main-width:\s*(\d+)px", css_source)
    if match:
        width_current = int(match.group(1))
    max_width = st.slider("Ancho máximo del contenido (px)", 900, 1800, width_current, 20)
    if st.button("Guardar diseño global", type="primary"):
        try:
            updated_css = editor.apply_theme(css_source, chosen_colors, max_width)
            save_path("assets/css/portal.css", updated_css, expected=css_source)
            st.rerun()
        except (ValueError, OSError) as exc:
            st.error(str(exc))
    st.markdown(
        f'<div style="padding:1.3rem;border-radius:12px;background:{chosen_colors.get("forest", "#102b28")};'
        f'color:{chosen_colors.get("paper", "#f1ede2")};border:1px solid {chosen_colors.get("portal-line", "#c6ccbf")}">'
        f'<small style="color:{chosen_colors.get("lime", "#c6df7e")}">ECUADOR VIVO · VISTA DE PALETA</small>'
        f'<h3 style="margin:.5rem 0">Una web que puedes cuidar sin editar código</h3>'
        f'<p style="color:{chosen_colors.get("portal-muted", "#52645e")}">El contenido conserva su evidencia, sus fuentes y sus dos idiomas.</p></div>',
        unsafe_allow_html=True,
    )

with map_tab:
    settings_path = ROOT / "data/site-settings.json"
    settings = editor.read_map_settings(settings_path)
    st.subheader("Fuentes disponibles en el visor")
    st.caption("Desactivar retira el control de la capa del mapa, sin borrar ni cambiar los datos archivados.")
    source_cols = st.columns(3)
    selected_sources = {}
    for idx, (source_id, (label, _toggle)) in enumerate(editor.MAP_SOURCES.items()):
        with source_cols[idx % 3]:
            selected_sources[source_id] = st.toggle(label, value=settings["mapSources"][source_id], key=f"map-source-{source_id}")
    if st.button("Guardar fuentes del visor", type="primary"):
        try:
            relative = "data/site-settings.json"
            document = {**settings, 'mapSources': selected_sources}
            save_path(relative, json.dumps(document, ensure_ascii=False, indent=2) + '\n', expected=settings_path.read_text(encoding='utf-8'))
            st.rerun()
        except (ValueError, OSError) as exc:
            st.error(str(exc))
    st.info("Si una fuente no existe aún o el sitio no tiene una capa correspondiente, este control no la inventa: solo administra las capas conectadas que aparecen en la lista.")
    st.subheader('Añadir tus propias fuentes cartográficas')
    st.caption('GeoJSON WGS84, WMS o teselas XYZ. Cada fuente pertenece a Tierra, Agua, Cielo, Vida o Riesgo y solo aparece en su apartado; la leyenda sigue su activación. El servidor externo debe permitir acceso desde el navegador.')
    custom_sources = settings.get('customMapSources', [])
    selected_source = st.selectbox('Fuente personalizada', [None] + list(range(len(custom_sources))),
        format_func=lambda idx: 'Añadir fuente' if idx is None else custom_sources[idx]['id'], key='custom_source_choice')
    draft_source = custom_sources[selected_source] if selected_source is not None else {
        'id': '', 'title_es': '', 'title_en': '', 'type': 'geojson', 'system': 'earth',
        'url': '', 'layers': '', 'citation': '', 'color': '#55e2cb', 'enabled': True,
    }
    with st.form('custom_source_form'):
        source_id = st.text_input('ID de la fuente', draft_source['id'])
        title_es = st.text_input('Título en español', draft_source['title_es'])
        title_en = st.text_input('Title in English', draft_source['title_en'])
        source_type = st.selectbox('Tipo de servicio', ['geojson', 'wms', 'xyz'], index=['geojson', 'wms', 'xyz'].index(draft_source['type']))
        system_id = st.selectbox('Apartado', ['earth', 'water', 'sky', 'life', 'risk'],
            index=['earth', 'water', 'sky', 'life', 'risk'].index(draft_source['system']),
            format_func=lambda key: {'earth': 'Tierra', 'water': 'Agua', 'sky': 'Cielo', 'life': 'Vida', 'risk': 'Riesgo'}[key])
        source_url = st.text_input('URL o ruta GeoJSON', draft_source['url'])
        source_layers = st.text_input('Capas WMS · separadas por coma', draft_source.get('layers', ''))
        source_citation = st.text_input('Institución / cita / escala', draft_source['citation'])
        source_color = st.color_picker('Color del símbolo GeoJSON', draft_source.get('color', '#55e2cb'))
        source_enabled = st.checkbox('Disponible en el visor', draft_source.get('enabled', True))
        add_source = st.form_submit_button('Guardar fuente personalizada', type='primary')
    if add_source:
        try:
            revised_sources = list(custom_sources)
            record = dict(id=source_id, title_es=title_es, title_en=title_en, type=source_type,
                system=system_id, url=source_url, layers=source_layers, citation=source_citation,
                color=source_color, enabled=source_enabled)
            if selected_source is None:
                revised_sources.append(record)
            else:
                revised_sources[selected_source] = record
            editor.validate_custom_sources(revised_sources)
            save_path('data/site-settings.json', json.dumps({**settings, 'customMapSources': revised_sources}, ensure_ascii=False, indent=2) + '\n', expected=settings_path.read_text(encoding='utf-8'))
            st.rerun()
        except (ValueError, OSError) as exc:
            st.error(str(exc))
    if selected_source is not None and st.button('Retirar fuente personalizada'):
        revised_sources = list(custom_sources)
        del revised_sources[selected_source]
        save_path('data/site-settings.json', json.dumps({**settings, 'customMapSources': revised_sources}, ensure_ascii=False, indent=2) + '\n', expected=settings_path.read_text(encoding='utf-8'))
        st.rerun()

with preview_tab:
    st.subheader('Comprueba la página real antes de publicar')
    @st.cache_resource
    def preview_service():
        return start_preview(ROOT)
    server = preview_service()
    preview_url = f'http://127.0.0.1:{server.server_port}/{page}?lang=es'
    st.link_button('Abrir vista previa en otra ventana', preview_url)
    st.iframe(preview_url, height=740, alt='Vista previa local de la página seleccionada')
    st.caption('Esta vista ejecuta los componentes reales y carga los catálogos guardados. El sitio publicado no cambia hasta hacer commit y push.')

with history_tab:
    st.subheader('Copias antes de cada guardado')
    backup_root = ROOT / '_local/site-admin/backups'
    backups = sorted(backup_root.glob('*.json'), reverse=True) if backup_root.exists() else []
    if backups:
        selected_backup = st.selectbox('Versión', backups, format_func=lambda path: json.loads(path.read_text(encoding='utf-8'))['at'] + ' · ' + json.loads(path.read_text(encoding='utf-8'))['path'])
        metadata = json.loads(selected_backup.read_text(encoding='utf-8'))
        target = (ROOT / metadata['path']).resolve()
        backup_file = selected_backup.with_suffix('.bak')
        can_restore = metadata['existed'] and backup_file.is_file() and target.is_file() and target.is_relative_to(ROOT.resolve())
        confirm_restore = st.checkbox('Confirmo recuperar esta versión local')
        if st.button('Recuperar versión', disabled=not (can_restore and confirm_restore)):
            if hashlib.sha256(target.read_bytes()).hexdigest() != metadata['after_sha256']:
                st.error('Hay cambios posteriores a esa versión. Recupera primero el guardado más reciente para no sobrescribirlos.')
            else:
                save_path(metadata['path'], backup_file.read_bytes())
                st.rerun()
    else:
        st.info('Cada cambio del panel crea una copia privada aquí. No se sube a GitHub.')

with publish_tab:
    status = git("status", "--short").stdout.strip()
    branch_result = git("branch", "--show-current")
    branch = branch_result.stdout.strip() or "(HEAD separado)"
    remote = git("remote", "get-url", "origin")
    st.write(f"**Rama local:** `{branch}`")
    st.write(f"**Origen:** `{remote.stdout.strip() if remote.returncode == 0 else 'sin remoto origin'}`")
    if remote.returncode != 0:
        st.warning("No existe un remoto `origin`; el panel no intentará publicar cambios.")
    st.write("**Estado local:**")
    st.code(status or "árbol de trabajo limpio", language="text")
    saved = sorted(st.session_state.saved_hashes)
    safe_dirty = [path for path in saved if st.session_state.baseline_status.get(path, "")]
    if saved:
        st.caption("Archivos que el panel puede separar de cambios previos: " + ", ".join(saved))
        diff = git('diff', '--', *saved).stdout
        with st.expander('Revisar diferencias antes del commit'):
            st.code(diff or 'Archivos nuevos: revisa los recursos y catálogos en la vista previa.', language='diff')
    if safe_dirty:
        st.warning("Hay archivos editados antes de abrir el panel. Se excluyen de la publicación automática para no mezclar tus cambios: " + ", ".join(safe_dirty))
    changed_after_save = [path for path in saved if not (ROOT / path).is_file() or hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
                          != st.session_state.saved_hashes.get(path)]
    if changed_after_save:
        st.warning("Cambió fuera del panel desde el último guardado y se excluye del commit: " + ", ".join(changed_after_save))
    staged = git("diff", "--cached", "--name-only").stdout.strip()
    if staged:
        st.warning("Hay archivos ya preparados en Git. El panel no creará un commit para evitar incluirlos por error; revísalos primero en GitHub Desktop.")
    st.markdown("Los archivos pueden revisarse primero en la pestaña **Cambios** de GitHub Desktop. El panel no lee ni guarda tokens de GitHub; Git usa la autenticación que ya tenga configurada tu equipo.")
    confirmation = st.checkbox("Confirmo que quiero crear un commit y publicarlo en GitHub ahora.")
    commit_message = st.text_input("Mensaje del commit", value="Actualiza contenido de Ecuador Vivo")
    # A panel-saved path is dirty by definition; allow it only if it was clean at edit time.
    eligible = [path for path in saved if st.session_state.baseline_status.get(path, "") == ""
                and (ROOT / path).is_file()
                and git("status", "--porcelain", "--", path).stdout.strip()
                and hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == st.session_state.saved_hashes.get(path)]
    if st.button("Crear commit y hacer push", type="primary", disabled=not (confirmation and commit_message.strip() and eligible and remote.returncode == 0) or bool(staged)):
        try:
            add_result = git("add", "--", *eligible)
            if add_result.returncode:
                raise RuntimeError(add_result.stderr or add_result.stdout)
            commit_result = git("commit", "-m", commit_message.strip(), timeout=60)
            if commit_result.returncode:
                raise RuntimeError(commit_result.stderr or commit_result.stdout)
            push_result = git("push", "origin", branch, timeout=120)
            if push_result.returncode:
                raise RuntimeError("El commit quedó local, pero Git no pudo completar el push. " + (push_result.stderr or push_result.stdout))
            st.success("Commit publicado. " + commit_result.stdout.strip())
            st.session_state.publishable_paths.clear()
            st.session_state.saved_hashes.clear()
        except (OSError, subprocess.SubprocessError, RuntimeError) as exc:
            st.error(str(exc))
    elif not eligible:
        st.info("Publicación automática disponible para los archivos que el panel edite cuando estaban limpios al iniciar. Los cambios preexistentes se mantienen separados; usa GitHub Desktop para revisarlos y publicarlos tú.")

st.divider()
st.caption("Privacidad: este panel solo escucha en 127.0.0.1. No se despliega a GitHub Pages y no incorpora contraseñas ni claves API.")
