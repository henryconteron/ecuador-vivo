"""No-code catalog, resource and element controls for the private web editor."""
import copy
import datetime as dt
from html import escape
import json
from pathlib import Path
import re

import streamlit as st

import dom_editor as dom
import site_editor as editor

CATALOGS = {
    'Biblioteca científica': ('data/library/studies.json', 'records'),
    'Catálogo de datos': ('data/catalog/datasets.json', 'records'),
    'Andes Pulso · casos y videos': ('data/cases/registry.json', 'cases'),
}


def validate_catalog(document, collection):
    rows = document.get(collection)
    if not isinstance(rows, list):
        raise ValueError('No se reconoce la colección del catálogo.')
    ids = [row.get('id') for row in rows if isinstance(row, dict)]
    if len(ids) != len(rows) or any(not isinstance(value, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value) for value in ids):
        raise ValueError('Cada registro necesita un ID en minúsculas y guiones.')
    if len(ids) != len(set(ids)):
        raise ValueError('Hay identificadores duplicados.')
    def check(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {'href', 'url', 'source_url', 'license_url', 'viewer', 'poster'} and isinstance(item, str) and item:
                    editor._safe_href(item)
                check(item)
        elif isinstance(value, list):
            for item in value:
                check(item)
    check(document)
    return document


def fields(value, key, label=''):
    """Recursive forms retain nested catalogs without requiring JSON typing."""
    if isinstance(value, dict):
        result = {}
        for name, item in value.items():
            caption = name.replace('_', ' ')
            if isinstance(item, (dict, list)):
                with st.expander(caption, expanded=name in {'title', 'summary', 'video'}):
                    result[name] = fields(item, key + '/' + name, caption)
            else:
                result[name] = fields(item, key + '/' + name, caption)
        return result
    if isinstance(value, list):
        if all(isinstance(item, (str, int, float)) for item in value):
            text = st.text_area(label + ' · un valor por línea', '\n'.join(map(str, value)), key=key)
            return [line.strip() for line in text.splitlines() if line.strip()]
        result = []
        for index, item in enumerate(value):
            with st.expander(f'{label} · {index + 1}'):
                keep = st.checkbox('Conservar entrada', True, key=key + f'/{index}/keep')
                updated = fields(item, key + f'/{index}', label)
                if keep:
                    result.append(updated)
        if st.checkbox('Añadir una entrada', key=key + '/add'):
            template = blank_record(value[0]) if value else {'href': '', 'label_es': '', 'label_en': ''}
            result.append(fields(template, key + '/new', label))
        return result
    if isinstance(value, bool):
        return st.checkbox(label, value, key=key)
    if isinstance(value, (int, float)):
        return st.number_input(label, value=value, key=key)
    if value is None:
        text = st.text_input(label + ' · opcional', '', key=key)
        return text or None
    return st.text_area(label, str(value), key=key, height=80) if len(str(value)) > 90 or label in {'summary', 'citation', 'limits', 'resumen'} else st.text_input(label, str(value), key=key)


def blank_record(record):
    if isinstance(record, dict):
        return {key: blank_record(value) for key, value in record.items()}
    if isinstance(record, list):
        return [blank_record(record[0])] if record and isinstance(record[0], dict) else []
    if isinstance(record, bool):
        return False
    if isinstance(record, (int, float)):
        return 0
    return '' if record is not None else None


def show_catalogs(root, save):
    name = st.selectbox('Catálogo', list(CATALOGS), key='admin_catalog')
    relative, collection = CATALOGS[name]
    source = (root / relative).read_text(encoding='utf-8')
    document = json.loads(source)
    records = document[collection]
    st.caption('Edita los registros que alimentan la web: textos, idiomas, citas, fuentes, archivos y videos. Guardar no verifica por sí solo la veracidad de un estudio.')
    selected = st.selectbox('Registro', [None] + list(range(len(records))), key='catalog_record_' + name,
                            format_func=lambda idx: 'Añadir nuevo registro' if idx is None else records[idx].get('id', str(idx)))
    templates = st.session_state.setdefault('admin_catalog_templates', {})
    if records:
        templates[name] = blank_record(records[0])
    draft = copy.deepcopy(records[selected]) if selected is not None else copy.deepcopy(templates.get(name, {
        'id': '', 'title_es': '', 'title_en': '', 'summary_es': '', 'summary_en': '',
    }))
    prefix = f'catalog/{name}/{selected}'
    with st.form(prefix):
        revised = fields(draft, prefix)
        save_clicked = st.form_submit_button('Guardar registro', type='primary')
    if save_clicked:
        try:
            candidate = copy.deepcopy(document)
            if selected is None:
                candidate[collection].append(revised)
            else:
                candidate[collection][selected] = revised
            candidate['updated'] = dt.date.today().isoformat()
            validate_catalog(candidate, collection)
            save(relative, json.dumps(candidate, ensure_ascii=False, indent=2) + '\n', expected=source)
            st.rerun()
        except (ValueError, OSError) as error:
            st.error(str(error))
    if selected is not None:
        st.warning('Retirar un registro no borra sus archivos; revisa vínculos relacionados antes de hacerlo.')
        confirm = st.checkbox('Confirmo retirar este registro del catálogo', key=prefix + '/delete_confirm')
        if st.button('Retirar registro', disabled=not confirm, key=prefix + '/delete'):
            candidate = copy.deepcopy(document)
            del candidate[collection][selected]
            candidate['updated'] = dt.date.today().isoformat()
            save(relative, json.dumps(candidate, ensure_ascii=False, indent=2) + '\n', expected=source)
            st.rerun()


def show_elements(page, source, save):
    st.subheader('Todos los elementos de la página')
    st.caption('Incluye cabecera, menú, pie, textos, enlaces, imágenes y bloques anidados. Los cambios conservan el resto del archivo. Los scripts y la estructura raíz están protegidos.')
    query = st.text_input('Buscar texto, imagen, clase o ID', key='node_search_' + page)
    items = [row for row in dom.editable_nodes(source) if query.lower() in row.label.lower()]
    if not items:
        st.info('No hay elementos con ese filtro.')
        return
    selected = st.selectbox('Elemento', items, format_func=lambda row: row.label, key='node_select_' + page)
    if selected.attrs.get('id'):
        st.warning('Este elemento tiene un ID que puede usar el visor o la navegación. Ocultarlo es más seguro que retirarlo; verifica siempre la vista previa después de moverlo o eliminarlo.')
    prefix = page + '/' + selected.key
    translation_key = selected.attrs.get('data-i18n')
    i18n_source = (editor.ROOT / 'assets/js/i18n.js').read_text(encoding='utf-8') if translation_key else ''
    translation = editor.read_translation_pair(i18n_source, translation_key) if translation_key else {}
    with st.form('node_form_' + prefix):
        is_leaf = not selected.children and selected.tag not in dom.VOID
        text = st.text_area('Texto visible (selecciona un hijo si contiene más elementos)', translation.get('es', selected.text.strip()), disabled=not is_leaf, key=prefix + '/text')
        translated_en = st.text_area('English · catálogo de idioma', translation.get('en', ''), key=prefix + '/translated_en') if len(translation) == 2 else None
        attr_values = {}
        for attr in ('href', 'src', 'poster', 'alt', 'title', 'aria-label', 'data-es', 'data-en', 'data-alt-es', 'data-alt-en'):
            if attr in selected.attrs or attr == 'alt' and selected.tag == 'img':
                attr_values[attr] = st.text_input(attr, selected.attrs.get(attr) or '', key=prefix + '/' + attr)
        visible = st.checkbox('Visible', 'hidden' not in selected.attrs, key=prefix + '/visible')
        with st.expander('Diseño de este elemento'):
            styles = dict(part.split(':', 1) for part in (selected.attrs.get('style') or '').split(';') if ':' in part)
            style_values = {}
            for css, caption in [('color', 'Color del texto'), ('background-color', 'Fondo'), ('font-size', 'Tamaño de letra · ej. 24px'), ('text-align', 'Alineación · left / center / right'), ('padding', 'Espaciado interno · ej. 20px'), ('border-radius', 'Redondeado · ej. 12px'), ('max-width', 'Ancho máximo · ej. 900px')]:
                style_values[css] = st.text_input(caption, styles.get(css, '').strip(), key=prefix + '/style/' + css)
        submit = st.form_submit_button('Aplicar al elemento', type='primary')
    if submit:
        try:
            # Bilingual elements are driven by their attributes. Keep their fallback
            # synchronized; non-text edits never flatten child icons or markup.
            replacement_text = attr_values.get('data-es', text) if is_leaf else None
            revised = dom.edit_node(source, selected.key, text=replacement_text, attributes=attr_values, style=style_values, visible=visible)
            if len(translation) == 2 and is_leaf:
                save('assets/js/i18n.js', editor.apply_translation_pair(i18n_source, translation_key, text, translated_en), expected=i18n_source)
            save(page, revised, expected=source)
            st.rerun()
        except (ValueError, OSError) as error:
            st.error(str(error))
    with st.container(horizontal=True):
        for label, action in [('Mover arriba', 'up'), ('Mover abajo', 'down'), ('Duplicar', 'duplicate')]:
            if st.button(label, key=prefix + '/' + action):
                try:
                    revised = dom.duplicate_node(source, selected.key) if action == 'duplicate' else dom.move_node(source, selected.key, action)
                    save(page, revised, expected=source)
                    st.rerun()
                except (ValueError, OSError) as error:
                    st.error(str(error))
    confirm = st.checkbox('Confirmo retirar el elemento y todos sus hijos', key=prefix + '/confirm')
    if st.button('Retirar elemento', disabled=not confirm, key=prefix + '/delete'):
        save(page, dom.remove_node(source, selected.key), expected=source)
        st.rerun()


def show_resources(root, save):
    st.subheader('Imágenes, videos y documentos')
    st.caption('Se añaden a assets/media/editor. Puedes usar la ruta resultante en cualquier imagen, enlace, video o registro. Los archivos pesados deben alojarse fuera del repositorio web.')
    upload = st.file_uploader('Recurso', type=['png', 'jpg', 'jpeg', 'webp', 'mp4', 'pdf', 'csv', 'geojson'], key='admin_upload')
    if upload:
        filename = re.sub(r'[^a-zA-Z0-9_.-]', '-', Path(upload.name).name)
        destination = 'assets/media/editor/' + filename
        if st.button('Añadir recurso', type='primary'):
            if upload.size > 25 * 1024 * 1024:
                st.error('Límite del panel: 25 MiB por archivo. Usa alojamiento externo para videos grandes.')
            elif (root / destination).exists():
                st.error('Ese nombre ya existe. Renombra el archivo para no sobrescribirlo.')
            else:
                save(destination, upload.getvalue(), expected=None)
                st.success('Recurso añadido: ' + destination)
    resources = sorted(path for path in (root / 'assets/media').rglob('*') if path.is_file() and path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp', '.mp4', '.pdf'})
    if resources:
        chosen = st.selectbox('Recursos existentes', resources, format_func=lambda path: path.relative_to(root).as_posix())
        st.code(chosen.relative_to(root).as_posix(), language=None)
        if chosen.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp'}:
            st.image(str(chosen), width=350, alt='Recurso seleccionado de la web')
    st.info('Para quitar un recurso de la página, retira su elemento o su enlace. Los archivos fuente se conservan para evitar romper otras páginas.')
