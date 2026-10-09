"""Studio 2.0 integration regressions; fixtures are synthetic and isolated."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parent))
from test_studio_jobs import small_project
from studio_workspace_commands import workspace_command
from studio_timeline import PreparedTimeline


class TabularInsertionTests(unittest.TestCase):
    def setUp(self):
        self.project = small_project()
        self.project['studio']['calculations']['table'] = {
            'id': 'table', 'variable': 'Synthetic provincial rainfall', 'units': 'mm',
            'value': None, 'rows': [{'name': 'A', 'value': 4}, {'name': 'B', 'value': None}],
            'provenance': {'fixture': True},
        }

    def test_rows_with_none_scalar_can_be_inserted_and_rendered(self):
        before = copy.deepcopy(self.project)
        for kind in ('chart', 'ranking'):
            with self.subTest(kind=kind):
                project = workspace_command(self.project, 'red', {
                    'action': 'add_element', 'kind': kind, 'result_id': 'table',
                    'visualization': 'horizontal_bar',
                })
                element = project['studio']['scenes'][0]['elements'][0]
                self.assertEqual(element['data_binding'], {'result_id': 'table', 'field': 'rows'})
                self.assertEqual(project['studio']['calculations'], before['studio']['calculations'])
                self.assertEqual(PreparedTimeline(project).frame_at(0).size, (320, 180))
        self.assertEqual(self.project, before)

    def test_table_is_not_a_scalar_and_scalar_is_not_a_chart(self):
        scalar = next(rid for rid, r in self.project['studio']['calculations'].items() if 'rows' not in r)
        for kind, rid in [('metric', 'table'), ('chart', scalar), ('ranking', scalar)]:
            with self.subTest(kind=kind):
                with self.assertRaises(ValueError):
                    workspace_command(self.project, 'red', {'action': 'add_element', 'kind': kind, 'result_id': rid})


class PublishedProductsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.job = Path(self.temp.name) / 'job'
        self.job.mkdir()
        self.payload = b'Synthetic MP4 placeholder: resolver tests, no codec claim'
        self.digest = hashlib.sha256(self.payload).hexdigest()
        (self.job / 'status.json').write_text(json.dumps({'state': 'complete'}), encoding='utf-8')

    def receipt(self, name, **extra):
        (self.job / name).write_bytes(self.payload)
        data = {'video_sha256': self.digest, **extra}
        (self.job / 'receipt.json').write_text(json.dumps(data), encoding='utf-8')

    def test_declared_video_resolves_without_assuming_worker_filename(self):
        from job_products import published_movie
        self.receipt('custom-final.mp4', artifacts={'video': {
            'name': 'custom-final.mp4', 'mime': 'video/mp4', 'sha256': self.digest}})
        self.assertEqual(published_movie(self.job), self.job / 'custom-final.mp4')

    def test_old_legacy_and_studio_receipts_remain_readable(self):
        from job_products import published_movie
        self.receipt('ecuador-vivo.mp4', complete=True)
        self.assertEqual(published_movie(self.job), self.job / 'ecuador-vivo.mp4')
        self.receipt('video.mp4', renderer='studio_scene_v1')
        self.assertEqual(published_movie(self.job), self.job / 'video.mp4')

    def test_partial_missing_and_escaping_metadata_fail_closed(self):
        from job_products import published_movie
        self.receipt('video.mp4', renderer='studio_scene_v1')
        (self.job / 'status.json').write_text(json.dumps({'state': 'running'}), encoding='utf-8')
        self.assertIsNone(published_movie(self.job))
        (self.job / 'status.json').write_text(json.dumps({'state': 'complete'}), encoding='utf-8')
        for name in ('../video.mp4', 'C:/video.mp4', 'video.partial.mp4', 'missing.mp4'):
            (self.job / 'receipt.json').write_text(json.dumps({'artifacts': {'video': {
                'name': name, 'mime': 'video/mp4', 'sha256': self.digest}}}), encoding='utf-8')
            with self.subTest(name=name):
                with self.assertRaises(ValueError): published_movie(self.job)

    def test_malformed_status_is_reported_as_invalid_metadata(self):
        from job_products import published_movie
        (self.job / 'status.json').write_text('[]', encoding='utf-8')
        with self.assertRaises(ValueError): published_movie(self.job)

    def test_real_studio_worker_publishes_declared_product(self):
        from unittest.mock import patch
        import studio_jobs
        from test_studio_jobs import tracked_workers, wait_terminal
        from job_products import published_movie
        with patch.object(studio_jobs, 'STORE', Path(self.temp.name)), tracked_workers():
            job = studio_jobs.start_studio_job(small_project())
            self.assertEqual(wait_terminal(job)['state'], 'complete')
            receipt = json.loads((job / 'receipt.json').read_text(encoding='utf-8'))
            movie = published_movie(job)
            self.assertEqual(movie.name, receipt['artifacts']['video']['name'])
            self.assertEqual(hashlib.sha256(movie.read_bytes()).hexdigest(), receipt['artifacts']['video']['sha256'])


if __name__ == '__main__': unittest.main()
