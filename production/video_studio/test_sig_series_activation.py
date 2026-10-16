"""Regression for downloaded dates admitted as unrelated visible images."""
import copy,hashlib,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import test_sig_raster as fixtures
from test_sig_raster import raster_bytes
from studio_sig_layers import workspace_for

class ActivationTests(unittest.TestCase):
 setUp=fixtures.RasterTests.setUp
 tearDown=fixtures.RasterTests.tearDown
 def download(self):
  entries=[]
  for index,day in enumerate(['2026-09-01','2026-09-02','2026-09-03']):
   content=raster_bytes([[index+20]]);path=Path(self.temp.name)/('day'+str(index)+'.tif');path.write_bytes(content)
   entries.append({'path':str(path),'date':day,'artifact_sha256':hashlib.sha256(content).hexdigest()})
  return {'provider':'NASA POWER','variable':'Temperature fixture','units':'°C','profile_kind':'temperature',
   'citation':'NASA POWER synthetic test','manifest':{'source_url':'https://power.larc.nasa.gov/'},'entries':entries}
 def test_download_button_activates_the_clock_without_a_second_apply(self):
  from streamlit.testing.v1 import AppTest
  app=AppTest.from_string('''import streamlit as st
from types import SimpleNamespace
from studio_sig_series_ui import acquire_panel
def commit(candidate):st.session_state.document=candidate
acquire_panel(SimpleNamespace(project=st.session_state.document,key='activation',state=st.session_state,commit=commit))
''')
  app.session_state.document=self.project;app.run(timeout=30)
  app.selectbox(key='activation_series_provider').select('NASA POWER').run(timeout=30)
  with patch('providers.download_power_regional',return_value=self.download()):
   app.button(key='activation_series_download').click().run(timeout=30)
  self.assertFalse(app.exception);self.assertFalse(app.error)
  state=workspace_for(app.session_state.document)
  self.assertEqual(len(state['raster_time']['layers']),3)
  self.assertEqual(state['active_layer'],state['raster_time']['layers'][0])
 def test_existing_download_is_recovered_once_and_undo_is_respected(self):
  from studio_sig_series import admit_download,restore_downloaded_series
  project,ids=admit_download(self.project,self.download())
  session=SimpleNamespace(project=project,state={},key='activation')
  session.commit=lambda candidate:setattr(session,'project',candidate)
  self.assertTrue(restore_downloaded_series(session))
  self.assertEqual(workspace_for(session.project)['raster_time']['layers'],ids)
  self.assertEqual(session.project['studio']['calculations'],project['studio']['calculations'])
  session.project=project # Simulate undoing the presentation transaction.
  self.assertFalse(restore_downloaded_series(session))
  self.assertNotIn('raster_time',workspace_for(session.project))
 def test_clicking_dated_layer_activates_its_sequence_and_changes_the_frame(self):
  from studio_sig_series import admit_download,select_observation
  project,ids=admit_download(self.project,self.download());before=copy.deepcopy(project)
  selected=select_observation(project,ids[1]);state=workspace_for(selected)
  self.assertEqual(state['raster_time']['index'],1);self.assertEqual(state['active_layer'],ids[1])
  selected=select_observation(selected,ids[2]);self.assertEqual(workspace_for(selected)['raster_time']['index'],2)
  self.assertEqual(selected['studio']['geography']['sources'],project['studio']['geography']['sources'])
  self.assertEqual(project,before)
 def test_restore_does_not_guess_between_products_or_retry_failed_save_silently(self):
  from studio_sig_series import admit_download,restore_downloaded_series
  project,ids=admit_download(self.project,self.download())
  session=SimpleNamespace(project=project,state={},key='activation',commit=lambda _:(_ for _ in ()).throw(OSError('Synthetic save failure')))
  with self.assertRaises(OSError):restore_downloaded_series(session)
  self.assertEqual(session.project,project);self.assertEqual(session.state,{})
  other=self.download();other['variable']='Other variable';other['citation']='Other product'
  # Different values as well as a distinct product (same original cannot be redeclared).
  for entry in other['entries']:
   path=Path(entry['path']);path.write_bytes(raster_bytes([[99]]));entry['artifact_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
  project,_=admit_download(project,other);session.project=project
  self.assertFalse(restore_downloaded_series(session))
 def test_reopened_sig_payload_has_one_observation_and_date_click_really_changes_it(self):
  from studio_sig_series import admit_download
  from test_sig_map_ui import SigMapUiTests
  project,ids=admit_download(self.project,self.download())
  probe=SigMapUiTests();probe.project=project;probe.temp=self.temp
  app=probe.app(project)
  with probe.patches():
   app.run(timeout=30);probe.assert_clean(app)
   self.assertEqual(probe.payload['raster_time']['layers'],ids)
   images=[layer for layer in probe.payload['layers'] if layer.get('image')]
   self.assertEqual(len(images),1);self.assertEqual(images[0]['date'],'2026-09-01')
   scales=[layer['scale'] for layer in probe.payload['layers'] if layer['type']=='raster']
   self.assertTrue(all(scale==scales[0] for scale in scales))
   probe.layer(app,'active',layer_id=ids[2])
   self.assertEqual(probe.payload['raster_time']['index'],2)
   images=[layer for layer in probe.payload['layers'] if layer.get('image')]
   self.assertEqual(len(images),1);self.assertEqual(images[0]['date'],'2026-09-03')
   self.assertEqual(app.session_state.project_document['studio']['calculations'],project['studio']['calculations'])

if __name__=='__main__':unittest.main()
