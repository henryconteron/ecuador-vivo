import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("discovery", Path(__file__).resolve().parents[1] / "scripts" / "discover_ecuador_studies.py")
discovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(discovery)

class DiscoveryTests(unittest.TestCase):
    def test_candidates_are_not_publications(self):
        item = {"DOI": "10.example/test", "title": ["Geology of Ecuador"], "license": [{"URL": "https://creativecommons.org/licenses/by/4.0/"}]}
        self.assertEqual(len(discovery.select_candidates([item, item])), 1)
        self.assertEqual(discovery.select_candidates([dict(item, title=["Geology of Australia"])]), [])
        self.assertEqual(discovery.select_candidates([dict(item, license=[])]), [])
        self.assertIn("needs-editorial", discovery.select_candidates([item])[0]["status"])
