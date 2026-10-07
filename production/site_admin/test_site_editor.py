import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import site_editor as editor  # noqa: E402


class SiteEditorTests(unittest.TestCase):
    def test_scan_finds_bilingual_copy_and_only_main_level_blocks(self):
        html = '<main><section id="one"><h2 data-es="Hola" data-en="Hello">Hola</h2><section id="nested"></section></section><nav class="quick"></nav></main>'
        edits, sections, blocks = editor.scan_html(html)
        self.assertEqual(len(edits), 1)
        self.assertEqual([section["id"] for section in sections], ["one", "admin-section-02"])
        self.assertEqual(blocks, [])

    def test_edit_text_is_escaped_and_preserves_page_markup(self):
        html = '<h1 data-es="Viejo" data-en="Old">Viejo</h1>'
        entries, _, _ = editor.scan_html(html)
        updated = editor.apply_text_edits(html, {entries[0].key: {"es": "Agua & roca", "en": "Water < rock"}})
        self.assertIn('data-es="Agua &amp; roca"', updated)
        self.assertIn('data-en="Water &lt; rock"', updated)
        self.assertIn(">Viejo</h1>", updated)

    def test_visibility_can_hide_and_restore_existing_sections(self):
        html = '<main><section class="intro"><h1>Hola</h1></section><section id="data" hidden></section></main>'
        _, sections, _ = editor.scan_html(html)
        hidden = editor.apply_section_visibility(html, {str(sections[0]["id"]): False, "data": True})
        self.assertIn('<section class="intro" data-site-admin-id="admin-section-01" hidden data-site-admin-hidden="true">', hidden)
        self.assertIn('<section id="data"></section>', hidden)
        restored = editor.apply_section_visibility(hidden, {'admin-section-01': True})
        self.assertNotIn('data-site-admin-hidden', restored)

    def test_add_remove_block_and_reject_unsafe_link(self):
        html, block_id = editor.add_content_block('<main><h1>Inicio</h1></main>', "Título", "Title", "Texto", "Text", "Más", "More", "datos.html")
        self.assertIn('data-site-admin-block="' + block_id + '"', html)
        self.assertNotIn('javascript:', editor.remove_content_block(html, block_id))
        with self.assertRaises(ValueError):
            editor.add_content_block('<main></main>', "T", "T", "B", "B", href="javascript:alert(1)")

    def test_only_generated_editorial_blocks_can_be_removed(self):
        with self.assertRaises(ValueError):
            editor.remove_content_block('<main></main>', "existing-section")

    def test_theme_changes_only_supported_tokens_and_width(self):
        css = ':root{--forest:#102b28;--paper:#f1ede2;--portal-ink:#132d29;--portal-muted:#52645e;--lime:#c6df7e;--portal-line:#c6ccbf;--sage:#b4c8b5;--coral:#ed8d74}\n.portal-main{max-width:1440px;margin:auto}'
        theme = editor.read_theme(css)
        theme["forest"] = "#112233"
        updated = editor.apply_theme(css, theme, 1500)
        self.assertIn("--forest:#112233", updated)
        self.assertIn("--site-main-width:1500px", updated)
        self.assertIn("max-width:var(--site-main-width,1440px)", updated)
        with self.assertRaises(ValueError):
            editor.apply_theme(css, {"forest": "red"})

    def test_settings_have_fixed_allowlist(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "settings.json"
            editor.write_map_settings(path, {"mapSources": {"faults": False, "not-a-source": False}})
            result = json.loads(path.read_text(encoding="utf-8"))
        self.assertFalse(result["mapSources"]["faults"])
        self.assertNotIn("not-a-source", result["mapSources"])
        self.assertTrue(result["mapSources"]["evidence"])

    def test_translation_pair_updates_only_requested_key(self):
        source = 'const translations = {\n  es: {\n    "map.title": "Mapa",\n    "map.other": "Otro"\n  },\n  en: {\n    "map.title": "Map",\n    "map.other": "Other"\n  }\n  };'
        self.assertEqual(editor.read_translation_pair(source, "map.title"), {"es": "Mapa", "en": "Map"})
        updated = editor.apply_translation_pair(source, "map.title", "Territorio", "Landscape")
        self.assertIn('"map.title": "Territorio"', updated)
        self.assertIn('"map.other": "Otro"', updated)

    def test_main_site_page_allowlist_is_fixed(self):
        self.assertEqual(editor.page_path("index.html"), editor.ROOT / "index.html")
        with self.assertRaises(ValueError):
            editor.page_path("../../outside.html")


if __name__ == "__main__":
    unittest.main()
