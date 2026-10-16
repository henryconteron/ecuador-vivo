"""Design structure and isolation; not a substitute for visual acceptance."""
import unittest
from pathlib import Path
from html.parser import HTMLParser

FRONT=Path(__file__).with_name('workspace_frontend')

class Tags(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.labels=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        if attrs.get('aria-label'):self.labels.append(attrs['aria-label'])

class EditorialSurfaceTests(unittest.TestCase):
    def test_immersive_editor_has_reachable_tools_and_non_modal_movable_windows(self):
        markup=(FRONT/'workspace.html').read_text(encoding='utf8')
        self.assertIn('class="studio-tools"',markup)
        self.assertEqual(markup.count('data-studio-window='),2)
        self.assertEqual(markup.count('data-window-drag'),2)
        self.assertEqual(markup.count('data-window-resize'),2)
        self.assertEqual(markup.count('aria-modal="false"'),2)
        for name in ('focus-mode','focus-exit','selection-properties'):
            self.assertIn('id="'+name+'"',markup)
    def test_studio_has_distinct_project_and_workspace_rows_without_lost_controls(self):
        markup=(FRONT/'workspace.html').read_text(encoding='utf8');tags=Tags();tags.feed(markup)
        self.assertEqual(len(tags.ids),len(set(tags.ids)))
        self.assertIn('projectbar',markup)
        for name in ('project-name','export','format','play','save-resource','nav-sig','canvas-stage','scene-add','tracks','context-fields'):
            self.assertIn(name,tags.ids)
    def test_shared_native_styles_are_owned_and_have_no_sig_or_global_theme_rules(self):
        css=(FRONT/'surfaces.css').read_text(encoding='utf8')
        self.assertIn('ev_home_nav',css);self.assertIn('ev_resources_nav',css)
        self.assertNotIn('sig_integrated_shell',css)
        self.assertNotIn('stale',css)
        self.assertNotIn('@import',css)
    def test_studio_styles_are_consolidated_and_accessible(self):
        css=(FRONT/'workspace.css').read_text(encoding='utf8')
        self.assertIn('--header-height:',css)
        self.assertIn('prefers-reduced-motion',css)
        self.assertIn('focus-visible',css)
        self.assertIn('max-width:600px',css)
        self.assertNotIn('Editorial finish:',css)

if __name__=='__main__':unittest.main()
