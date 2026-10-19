"""Offline checks for the published snapshot; no credentials or private fixtures."""
import csv
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/casos/parcelas-sentinel'

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.paths = []; self.ids = set(); self.fragments = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs: self.ids.add(attrs['id'])
        for key in ('src', 'href'):
            value = attrs.get(key, '')
            if value.startswith('#'): self.fragments.append(value[1:])
            elif value and not value.startswith(('http:', 'https:', 'mailto:')):
                self.paths.append(value.split('?')[0].split('#')[0])

class ParcelPublicationTests(unittest.TestCase):
    def test_public_assets_and_anchors_resolve(self):
        parser = Links(); parser.feed((ROOT / 'parcelas-sentinel.html').read_text(encoding='utf-8'))
        self.assertTrue(set(parser.fragments).issubset(parser.ids))
        for path in parser.paths:
            self.assertTrue((ROOT / path).is_file(), path)

    def test_public_hashes_and_no_sensitive_metadata(self):
        manifest = json.loads((DATA / 'huellas-publicas.json').read_text(encoding='utf-8'))
        self.assertEqual(set(manifest), {'evidencia-publica.json', 'escenas.csv', 'metricas.csv', 'RF05.png', 'RF06.png', 'INFORME.md'})
        for name, digest in manifest.items():
            self.assertEqual(hashlib.sha256((DATA / name).read_bytes()).hexdigest(), digest)
        raw = (DATA / 'evidencia-publica.json').read_text(encoding='utf-8')
        for excluded in ('client_secret', 'access_token', 'secret_dpapi', 'source_name', 'coordinates', 'latitude', 'longitude'):
            self.assertNotIn(excluded, raw)

    def test_metrics_and_product_receipts_match_snapshot(self):
        snapshot = json.loads((DATA / 'evidencia-publica.json').read_text(encoding='utf-8'))
        self.assertEqual(snapshot['status'], 'observations_not_validated_deforestation')
        with (DATA / 'escenas.csv').open(encoding='utf-8', newline='') as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 21)
        self.assertEqual(rows, snapshot['observations'])
        with (DATA / 'metricas.csv').open(encoding='utf-8', newline='') as stream:
            metrics = list(csv.DictReader(stream))
        expected = [{'plot_id': p['plot_id'], **m} for p in snapshot['plots'] for m in p['measurements']]
        self.assertEqual(len(metrics), len(expected))
        for row, source in zip(metrics, expected):
            for key, value in source.items():
                self.assertEqual(row[key], '' if value is None else str(value))
        page = (ROOT / 'parcelas-sentinel.html').read_text(encoding='utf-8')
        for metric in expected:
            if metric['value'] is not None:
                display = f"{metric['value']:.4f}".replace('.', ',').replace('-', '−')
                self.assertIn(display, page)
        rf05 = snapshot['plots'][0]
        self.assertEqual(rf05['common_valid_support']['optical_centres'], 0)
        self.assertTrue(all(m['value'] is None for m in rf05['measurements'] if m['sensor'] == 'optical'))

    def test_entry_points_link_to_study(self):
        for name in ('index.html', 'laboratorio.html'):
            self.assertIn('href="parcelas-sentinel.html"', (ROOT / name).read_text(encoding='utf-8'))

if __name__ == '__main__':
    unittest.main()
