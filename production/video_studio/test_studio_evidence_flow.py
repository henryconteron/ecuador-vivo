"""Real small MP4 + geographic bundle through public ZIP into a private draft.

Synthetic raster values only. Artifacts are temporary, not climate content.
"""
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch
import test_sig_presentation as fixtures
from studio_sig_timelapse import configure
from studio_territory import DEFAULT
from studio_sig_transfer import transfer_series
from studio_timeline import export_movie
from studio_publication import prepare_publication

spec=importlib.util.spec_from_file_location('site_studio_import',Path(__file__).resolve().parents[1]/'site_admin/studio_import.py')
admission=importlib.util.module_from_spec(spec);spec.loader.exec_module(admission)

class EvidenceFlowTests(unittest.TestCase):
    setUp=fixtures.PresentationTests.setUp
    tearDown=fixtures.PresentationTests.tearDown
    source=fixtures.PresentationTests.source
    series=fixtures.PresentationTests.series
    def test_native_temperature_final_movie_import_and_changed_original_refusal(self):
        p,ids=self.series();p['studio']['output_profile']={'id':'tiktok'}
        p=configure(p,ids[:2],duration=.2,presentation=DEFAULT)
        root=Path(self.temp.name)
        with patch('studio_map_bundles.MEDIA_ROOT',root/'media'):
            p=transfer_series(p);job=root/'sealed-job';job.mkdir()
            export_movie(p,job/'video.mp4')
            archive=prepare_publication(job,p)
            case,files=admission.inspect_package(archive.read_bytes())
            self.assertEqual(case['observation_dates'],['2024-09-01','2024-09-02'])
            self.assertEqual(case['results'],[])
            self.assertEqual(case['sources'][0]['citation'],self.provenance['citation'])
            self.assertIn('video.mp4',files)
            draft=admission.import_draft(root/'site',archive.read_bytes())
            self.assertTrue(draft.is_relative_to((root/'site/_local/site-admin/studio-drafts').resolve()))
            self.assertFalse((root/'site/data').exists())
            source_path=Path(self.source(p,ids[0])['path'])
            with source_path.open('ab') as stream:stream.write(b'changed synthetic source')
            with self.assertRaises(ValueError):prepare_publication(job,p)

if __name__=='__main__':unittest.main()
