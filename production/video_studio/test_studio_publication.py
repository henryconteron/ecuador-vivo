"""Public evidence never inherits inactive results or private authoring paths."""
import copy, hashlib, json, tempfile, unittest, zipfile
from pathlib import Path
from unittest.mock import patch
from studio_publication import public_case, prepare_publication

class PublicationTests(unittest.TestCase):
 def setUp(self):
  self.project={'name':'Temperatura de septiembre','studio':{'timeline':['temp'],
   'scenes':[{'id':'temp','series_template':'map'},{'id':'rain','rainfall_template':'map'}],
   'sig_map_transfer':{'asset_id':'temp-map','scene_ids':['temp']},
   'sig_transfer':{'asset_id':'rain-map','scene_ids':['rain'],'science_dataset':'rain-results','results':['rain-value']},
   'datasets':{'rain-results':{'summary':{'mean_period':999}}},
   'calculations':{'rain-value':{'variable':'Lluvia','value':999,'units':'mm'}},
   'media':{'temp-map':{},'rain-map':{}}}}
  self.manifest={'variable':'Temperatura','units':'°C','source_records':[{'date':'2026-09-01','sha256':'a'*64,'file':'C:/private/file.tif','source_url':'https://example.org/data?token=private'}],
   'geographic_binding':{'presentation':{'territory':'ecuador','resampling':'bilinear'},'scale':{'stops':[0,10,20]}},
   'scientific_revision':'b'*64,'temporal_interpolation':False}
 def test_temperature_has_no_inactive_rain_statistics_or_private_paths(self):
  original=copy.deepcopy(self.project)
  case=public_case(self.project,self.manifest)
  self.assertEqual(case['variable'],'Temperatura');self.assertEqual(case['results'],[])
  self.assertEqual(case['metrics_status'],'not_calculated')
  text=json.dumps(case);self.assertNotIn('999',text);self.assertNotIn('C:/',text);self.assertNotIn('token=',text)
  self.assertEqual(self.project,original)
 def test_only_active_rain_results_are_exported(self):
  self.project['studio']['timeline']=['rain']
  case=public_case(self.project,{**self.manifest,'variable':'Precipitación','units':'mm'})
  self.assertEqual(case['results'][0]['value'],999);self.assertEqual(case['metrics_status'],'linked_results')
 def test_ambiguous_or_missing_transfer_is_not_silently_assigned(self):
  for timeline in ([],['temp','rain']):
   self.project['studio']['timeline']=timeline
   with self.assertRaises(ValueError):public_case(self.project,self.manifest)
 def test_changed_video_or_document_is_rejected(self):
  with tempfile.TemporaryDirectory() as directory:
   job=Path(directory);video=b'test fixture, not a movie';(job/'video.mp4').write_bytes(video)
   (job/'project.json').write_text(json.dumps(self.project),encoding='utf-8')
   receipt={'delivery_kind':'final','video_sha256':hashlib.sha256(video).hexdigest(),'project_sha256':hashlib.sha256(json.dumps(self.project,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()}
   (job/'receipt.json').write_text(json.dumps(receipt),encoding='utf-8')
   with patch('studio_publication.read_bundle',return_value=self.manifest),patch('studio_publication.map_files',return_value={}),patch('studio_publication.verify_originals') as verify:
    path=prepare_publication(job,self.project)
    verify.assert_called_once_with(self.project,self.manifest)
    with zipfile.ZipFile(path) as archive:
     self.assertIn('case.json',archive.namelist());self.assertNotIn('project.json',archive.namelist())
     self.assertEqual(json.loads(archive.read('case.json'))['status'],'draft')
    changed=copy.deepcopy(self.project);changed['name']='edited'
    with self.assertRaisesRegex(ValueError,'documento'):prepare_publication(job,changed)
    (job/'video.mp4').write_bytes(b'changed')
    with self.assertRaisesRegex(ValueError,'video'):prepare_publication(job,self.project)

 def test_private_paths_in_results_are_refused(self):
  self.project['studio']['timeline']=['rain']
  self.project['studio']['calculations']['rain-value']['rows']=[{'name':'C:/Users/private/source.tif','value':2}]
  with self.assertRaisesRegex(ValueError,'privad'):public_case(self.project,self.manifest)

 def test_inactive_legacy_rain_package_is_not_generated(self):
  from studio_package import prepare_package
  self.assertIsNone(prepare_package('no-existing-job',self.project))

if __name__=='__main__':unittest.main()
