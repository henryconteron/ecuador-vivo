"""Tests for staging a local video as an Andes Pulso draft."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
import publication


class PublicationDraft(unittest.TestCase):
    def test_montage_keeps_example_credits_and_hash_but_not_private_paths(self):
        public = publication._public_receipt({'project':{'storyboard':{'cards':[
            {'path':'C:/Users/Someone/private/example.mp4','citation':'Archivo histórico · fuente', 'sha256':'c'*64}]}},
            'montage':{'cards':[{'kind':'video','path':'/private/example.mp4','sha256':'c'*64,
                                'citation':'Archivo histórico · fuente','duration_seconds':5}]}})
        self.assertNotIn('path',public['project']['storyboard']['cards'][0])
        self.assertNotIn('path',public['montage']['cards'][0])
        self.assertEqual(public['montage']['cards'][0]['sha256'],'c'*64)
        self.assertEqual(public['montage']['cards'][0]['citation'],'Archivo histórico · fuente')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'site'
        self.store = Path(self.temp.name) / 'local'
        self.job = self.store / 'jobs' / 'finished'
        self.job.mkdir(parents=True)
        self.root.mkdir()
        (self.root / 'data' / 'cases').mkdir(parents=True)
        (self.root / 'assets' / 'media' / 'andes-pulso').mkdir(parents=True)
        (self.job / 'ecuador-vivo.mp4').write_bytes(b'not a full video; fixture only')
        (self.job / 'endcard.png').write_bytes(b'poster fixture')
        (self.job / 'status.json').write_text(json.dumps({'state': 'complete'}))
        receipt = {
            'complete': True,
            'project': {
                'variable': 'Lluvia', 'title': 'LLUVIA EN ECUADOR',
                'units': 'mm/día', 'cadence': 'Diaria',
                'entries': [{'date': '2024-01-01', 'path': 'local-only.tif'}],
                'source': 'chirps', 'citation': 'CHIRPS v2',
            },
            'source_records': [{'date': '2024-01-01', 'band': 1,
                                'sha256': 'a' * 64,
                                'source_url': 'https://example.org/data.tif'}],
            'video_sha256': 'b' * 64,
            'endcard': {
                'enabled': True,
                'summary': {
                    'year': 2024, 'aggregation': 'sum', 'units': 'mm/día',
                    'aggregate_units': 'mm', 'province_rank': [
                        {'name': 'Napo', 'value': 12.5, 'days': 365,
                         'coverage': 1.0}
                    ],
                    'city_rank_units': 'mm', 'ranking_kind': 'provinces',
                    'national_extent': True, 'warnings': [],
                    'extreme_method': 'native_source_pixels',
                },
            },
        }
        (self.job / 'receipt.json').write_text(json.dumps(receipt))
        self.registry = self.root / 'data' / 'cases' / 'registry.json'
        self.registry.write_text(json.dumps({'schema_version': 1, 'cases': []}),
                                 encoding='utf-8')
        self.patchers = [
            patch.object(publication, 'ROOT', self.root),
            patch.object(publication, 'STORE', self.store),
            patch.object(publication, 'REGISTRY', self.registry),
        ]
        for item in self.patchers:
            item.start()

    def tearDown(self):
        for item in reversed(self.patchers):
            item.stop()
        self.temp.cleanup()

    def test_default_id_and_draft_contains_video_and_data(self):
        project = json.loads((self.job / 'receipt.json').read_text(encoding='utf-8'))['project']
        self.assertEqual(publication.default_case_id(project), 'lluvia-ecuador-2024')
        record = publication.prepare_case(self.job, 'lluvia-ecuador-2024')
        self.assertEqual(record['status'], 'draft')
        self.assertEqual(record['title_en'], 'Rainfall across Ecuador')
        self.assertTrue((self.root / record['video']['href']).is_file())
        case_dir = self.root / 'data' / 'cases' / record['id']
        for filename in ('receipt.json', 'summary.json', 'metrics-provinces.csv',
                         'sources.csv', 'methodology.md'):
            self.assertTrue((case_dir / filename).is_file(), filename)
        public_receipt = json.loads((case_dir / 'receipt.json').read_text(encoding='utf-8'))
        self.assertNotIn('entries', public_receipt['project'])
        self.assertNotIn('path', public_receipt['source_records'][0])
        self.assertEqual(json.loads(self.registry.read_text(encoding='utf-8'))['cases'][0]['id'],
                         record['id'])

    def test_collision_does_not_overwrite_existing_draft(self):
        record = publication.prepare_case(self.job, 'lluvia-ecuador-2024')
        video_path = self.root / record['video']['href']
        video_path.write_bytes(b'keep this existing file')
        with self.assertRaises(FileExistsError):
            publication.prepare_case(self.job, 'lluvia-ecuador-2024')
        self.assertEqual(video_path.read_bytes(), b'keep this existing file')

    def test_comparison_draft_keeps_monthly_data_and_provider_receipts(self):
        receipt_path = self.job / 'receipt.json'
        receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
        receipt['render_type'] = 'climate_comparison'
        receipt['project'].update(source='local', cadence='Mensual', start='2020-01-01', end='2024-03-31')
        receipt['source_records'] = [{'provider': 'NASA POWER', 'period': {'start': '2024-01-01', 'end': '2024-03-31'},
            'archive_sha256': 'c'*64, 'source_url': 'https://example.org/power', 'manifest_path_local': 'C:/private/data.json'}]
        receipt['comparison'] = {'aggregation': 'day-weighted temporal mean', 'years': [2020, 2024]}
        receipt['methodology'] = {'coverage_rule': 'Complete months only'}
        receipt['endcard']['summary']['comparison_copy'] = {'subtitle': 'Comparación de periodos equivalentes'}
        receipt['endcard']['summary']['scope'] = 'Napo'
        receipt['endcard']['summary']['comparison_cards'] = [{'value': '12.5 °C'}]
        receipt_path.write_text(json.dumps(receipt), encoding='utf-8')
        (self.job / 'comparison.csv').write_text('year,month,value\n2024,1,12.5\n', encoding='utf-8')
        record = publication.prepare_case(self.job, 'comparacion-ecuador-2024')
        case_dir = self.root / 'data/cases' / record['id']
        self.assertTrue((case_dir / 'comparison.csv').exists())
        self.assertTrue((case_dir / 'metrics-periods.csv').exists())
        self.assertFalse((case_dir / 'metrics-provinces.csv').exists())
        self.assertIn('territory_or_year', (case_dir / 'metrics-periods.csv').read_text(encoding='utf-8-sig'))
        self.assertEqual(record['territories'], ['Napo'])
        public = json.loads((case_dir / 'receipt.json').read_text(encoding='utf-8'))
        self.assertEqual(public['source_records'][0]['archive_sha256'], 'c'*64)
        self.assertNotIn('manifest_path_local', public['source_records'][0])
        summary = json.loads((case_dir / 'summary.json').read_text(encoding='utf-8'))
        self.assertEqual(summary['metric_definitions']['coverage_rule'], 'Complete months only')

    def test_only_completed_jobs_can_be_staged(self):
        (self.job / 'status.json').write_text(json.dumps({'state': 'running'}))
        with self.assertRaises(ValueError):
            publication.prepare_case(self.job, 'lluvia-ecuador-2024')

    def test_geographic_csv_publication_requires_explicit_sharing(self):
        path = self.job / 'receipt.json'
        receipt = json.loads(path.read_text(encoding='utf-8'))
        receipt['render_type'] = 'geographic_csv'
        receipt['project'].update(variable='Registros de especies', source='local',
            units='registros', start=None, end=None, period_labels=['2024', '2026'])
        receipt['endcard']['summary'].update(scope='Ecuador', comparison_cards=[{'value': '3'}],
            comparison_copy={'subtitle': 'Registros geográficos', 'section_2': 'REGISTROS POR CATEGORÍA'})
        receipt['comparison'] = {'aggregation': 'count of records, not populations', 'records': []}
        receipt['methodology'] = {'coverage_rule': 'No records does not demonstrate absence.'}
        path.write_text(json.dumps(receipt), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'coordenadas sensibles'):
            publication.prepare_case(self.job, 'especies-ecuador')
        self.assertFalse((self.root / 'data/cases/especies-ecuador').exists())
        receipt['project']['share_spatial_records'] = True
        path.write_text(json.dumps(receipt), encoding='utf-8')
        (self.job / 'comparison.csv').write_text('lat,lon,category,period\n-.994,-77.813,TEST,2024\n', encoding='utf-8')
        record = publication.prepare_case(self.job, 'especies-ecuador')
        self.assertEqual(record['kind'], 'geographic_records')
        self.assertEqual(record['period_es'], '2024 – 2026')
        target = self.root / 'data/cases/especies-ecuador'
        self.assertTrue((target / 'comparison.csv').exists())
        self.assertTrue((target / 'metrics-records.csv').exists())

    def test_public_receipt_removes_local_comparison_inputs(self):
        result = publication._public_receipt({'project': {'comparison_data': {'receipts': [{'zip_path': 'C:/private/data.zip'}]}},
            'source_records': [{'request_urls': ['https://example.org/query'], 'source_csv_sha256': ['d'*64]}]})
        self.assertNotIn('comparison_data', result['project'])
        self.assertEqual(result['source_records'][0]['source_csv_sha256'], ['d'*64])


if __name__ == '__main__':
    unittest.main()
