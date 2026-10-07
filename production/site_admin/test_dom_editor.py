from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dom_editor as dom
from content_manager import validate_catalog


class DOMTests(unittest.TestCase):
    def test_nested_elements_preserve_children_and_scripts(self):
        html = '<main><section id="a"><h2>Hola <em>mundo</em></h2><img src="x.jpg"></section></main><script>let a=1;</script>'
        selected = next(row for row in dom.nodes(html) if row.tag == 'em')
        updated = dom.edit_node(html, selected.key, text='agua & roca')
        self.assertIn('<em>agua &amp; roca</em>', updated)
        self.assertIn('<script>let a=1;</script>', updated)
        section = next(row for row in dom.nodes(html) if row.tag == 'section')
        self.assertNotIn('<section', dom.remove_node(html, section.key))

    def test_move_and_duplicate_nested_blocks(self):
        html = '<main><div><article id="a"><p>A</p></article>\n<article id="b"><p>B</p></article></div></main>'
        selected = next(row for row in dom.nodes(html) if row.attrs.get('id') == 'b')
        updated = dom.move_node(html, selected.key, 'up')
        self.assertLess(updated.index('id="b"'), updated.index('id="a"'))
        duplicate = dom.duplicate_node(html, selected.key)
        self.assertEqual(duplicate.count('id="b"'), 1)
        self.assertEqual(duplicate.count('<p>B</p>'), 2)

    def test_visibility_marker_persists_until_explicit_restore(self):
        html = '<section id="earth"><h2>Tierra</h2></section>'
        key = dom.nodes(html)[0].key
        hidden = dom.edit_node(html, key, visible=False)
        self.assertIn('data-site-admin-hidden="true"', hidden)
        self.assertIn(' hidden ', hidden)
        self.assertEqual(dom.edit_node(hidden, key, visible=True), html)

    def test_href_and_design_reject_executable_payloads(self):
        html = '<a href="datos.html">Datos</a>'
        key = dom.nodes(html)[0].key
        for attrs in [{'href': 'javascript:alert(1)'}, {'onclick': 'evil()'}, {'srcdoc': '<script>x</script>'}]:
            with self.assertRaises(ValueError):
                dom.edit_node(html, key, attributes=attrs)
        with self.assertRaises(ValueError):
            dom.edit_node(html, key, style={'color': 'url(https://bad)'})
        with self.assertRaises(ValueError):
            dom.remove_node('<script>x</script>', '0')

    def test_catalog_rejects_duplicate_ids_and_script_links(self):
        with self.assertRaises(ValueError):
            validate_catalog({'records': [{'id': 'a'}, {'id': 'a'}]}, 'records')
        with self.assertRaises(ValueError):
            validate_catalog({'records': [{'id': 'a', 'url': 'javascript:bad()'}]}, 'records')
        self.assertEqual(validate_catalog({'records': [{'id': 'valid-id', 'title': {'es': 'Hola', 'en': 'Hello'}}]}, 'records')['records'][0]['id'], 'valid-id')

    def test_existing_catalogs_are_editable_without_rejecting_viewer_queries(self):
        import json
        import site_editor
        from content_manager import CATALOGS
        for relative, collection in CATALOGS.values():
            validate_catalog(json.loads((site_editor.ROOT / relative).read_text(encoding='utf-8')), collection)

    def test_private_panel_switches_pages_and_catalogs_without_stale_widget_errors(self):
        from streamlit.testing.v1 import AppTest
        at = AppTest.from_file(str(Path(__file__).parent / 'app.py'), default_timeout=30).run()
        self.assertFalse(at.exception)
        at.selectbox(key='page').select('learn.html').run()
        self.assertFalse(at.exception)
        at.selectbox(key='admin_catalog').select('Andes Pulso · casos y videos').run()
        self.assertFalse(at.exception)
        at.selectbox(key='catalog_record_Andes Pulso · casos y videos').select(0).run()
        self.assertFalse(at.exception)


if __name__ == '__main__':
    unittest.main()
