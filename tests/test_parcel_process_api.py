import unittest
import io
import tarfile
import tempfile
from pathlib import Path
from tools.parcelas.process_api import inspect
from tools.parcelas.process_api import build_request, output_folder, source_product


class ProcessRequestTests(unittest.TestCase):
    def test_archive_path_traversal_rejected_without_extracting(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            with tarfile.open(folder/'response.tar','w') as archive:
                member=tarfile.TarInfo('../escape.tif'); member.size=1
                archive.addfile(member,io.BytesIO(b'x'))
            with self.assertRaises(ValueError):
                inspect('2025-03-20',write=False,folder=folder)
            self.assertFalse((folder/'escape.tif').exists())

    def test_incomplete_original_not_overwritten(self):
        self.assertTrue(output_folder('2025-03-20').name.endswith('-trazable'))

    def test_missing_and_multiple_sources_rejected(self):
        for metadata in ({}, {'orbits': [{'tiles': [{'sentinel1ProductId': 'a'}, {'sentinel1ProductId': 'b'}]}]}):
            with self.assertRaises(ValueError):
                source_product(metadata)

    def test_one_source_returned(self):
        self.assertEqual(source_product({'orbits':[{'tiles':[{'sentinel1ProductId':'scene.SAFE'}]}]}), 'scene')

    def test_fixed_exact_metric_grid_and_masks(self):
        request = build_request('2025-03-20')
        bounds = request['input']['bounds']['bbox']
        self.assertEqual((bounds[2]-bounds[0])/request['output']['width'], 20)
        self.assertEqual((bounds[3]-bounds[1])/request['output']['height'], 20)
        self.assertIn('shadowMask', request['evalscript'])
        self.assertIn('localIncidenceAngle', request['evalscript'])
        self.assertIn('outputMetadata.userData', request['evalscript'])
        self.assertIn('orbits: scenes.orbits', request['evalscript'])

    def test_dates_share_grid_not_time(self):
        a, b = build_request('2020-12-23'), build_request('2025-03-20')
        self.assertEqual(a['output'], b['output'])
        self.assertEqual(a['input']['bounds'], b['input']['bounds'])
        self.assertNotEqual(a['input']['data'][0]['dataFilter']['timeRange'],
                            b['input']['data'][0]['dataFilter']['timeRange'])

    def test_reject_unplanned_date(self):
        with self.assertRaises(ValueError):
            build_request('2026-10-18')

    def test_explicit_processing(self):
        data = build_request('2025-03-20')['input']['data'][0]
        self.assertEqual(data['processing']['backCoeff'], 'GAMMA0_TERRAIN')
        self.assertTrue(data['processing']['orthorectify'])
        self.assertEqual(data['dataFilter']['orbitDirection'], 'ASCENDING')
