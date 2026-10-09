"""Presentation contracts only: no downloads, calculations or exports."""
import ast
from html.parser import HTMLParser
from pathlib import Path
import re
import tomllib
import unittest


ROOT = Path(__file__).parent


def literal(name):
    tree = ast.parse((ROOT / 'layout_editor.py').read_text(encoding='utf-8'))
    return next(ast.literal_eval(node.value) for node in tree.body
                if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == name for target in node.targets))


class Controls(HTMLParser):
    def __init__(self):
        super().__init__()
        self.nodes = []

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))


def contrast(first, second):
    def luminance(color):
        channels = [int(color[i:i+2], 16)/255 for i in (1, 3, 5)]
        linear = [c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4 for c in channels]
        return sum(c*w for c, w in zip(linear, (.2126, .7152, .0722)))
    high, low = sorted((luminance(first), luminance(second)), reverse=True)
    return (high+.05)/(low+.05)


class InterfaceTests(unittest.TestCase):
    def test_reorganization_preserves_every_controller_target(self):
        parser = Controls()
        parser.feed(literal('HTML'))
        ids = [attrs['id'] for _, attrs in parser.nodes if 'id' in attrs]
        self.assertEqual(len(ids), len(set(ids)))
        targets = set(re.findall(r"q\('([a-z]+)'\)", literal('JS')))
        self.assertTrue(targets <= set(ids), targets-set(ids))
        for tag, attrs in parser.nodes:
            if tag == 'button':
                self.assertEqual(attrs.get('type'), 'button')
        stage = next(attrs for _, attrs in parser.nodes if attrs.get('class') == 'stage')
        self.assertEqual(stage['tabindex'], '0')
        self.assertEqual(stage['aria-describedby'], 'keyboard-help')
        pending = next(attrs for _, attrs in parser.nodes if attrs.get('id') == 'pending')
        self.assertEqual(pending['role'], 'status')

    def test_theme_text_actions_and_boundaries_have_visible_contrast(self):
        theme = tomllib.loads((ROOT / '.streamlit/config.toml').read_text(encoding='utf-8'))['theme']
        for surface in ('backgroundColor', 'secondaryBackgroundColor'):
            for text in ('textColor', 'linkColor'):
                self.assertGreaterEqual(contrast(theme[text], theme[surface]), 4.5, (text, surface))
            self.assertGreaterEqual(contrast(theme['borderColor'], theme[surface]), 3, surface)
            # Native primaryColor is a button/focus background, not body text.
            # On dark surfaces it needs non-text contrast; white button text is
            # checked below. Requiring 4.5 both to white and a dark field is
            # mathematically incompatible for these surfaces.
            self.assertGreaterEqual(contrast(theme['primaryColor'],theme[surface]),3)
            # Streamlit renders native captions at 60% opacity.
            ink, background = theme['textColor'], theme[surface]
            caption = '#'+''.join(f'{round(int(ink[i:i+2],16)*.6+int(background[i:i+2],16)*.4):02x}' for i in (1,3,5))
            self.assertGreaterEqual(contrast(caption, background), 4.5, ('caption', surface))
        # The shared legacy Apply button now matches native white button ink.
        # Streamlit native primary buttons/tags always use white text.
        self.assertGreaterEqual(contrast(theme['primaryColor'], '#ffffff'), 4.5)
        for status in ('blue', 'green', 'yellow', 'red'):
            self.assertGreaterEqual(contrast(theme[status+'TextColor'], theme[status+'BackgroundColor']), 4.5, status)

    def test_workbench_has_focus_and_container_based_responsive_rules(self):
        css = literal('CSS')
        self.assertIn(':focus-visible', css)
        self.assertIn('min-height:44px', css)
        self.assertIn('@container(max-width:720px)', css)
        self.assertIn('var(--st-font)', css)
        self.assertIn('var(--st-border-color)', css)
        self.assertNotIn('outline:none', css)


if __name__ == '__main__':
    unittest.main()
