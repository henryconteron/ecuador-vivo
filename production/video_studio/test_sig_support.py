"""Native support is not screen sharpness or an assumed kilometre resolution."""
import copy, unittest
from studio_support import grid_info, matching_results

class SupportTests(unittest.TestCase):
 def source(self,crs,transform):
  return {'type':'raster','native_crs':crs,'raster':{'shape':[100,200],'transform':transform,'band':1,'scale':.1,'offset':-2,'nodata':-9999}}
 def test_degrees_are_not_reported_as_metres_and_calibration_is_retained(self):
  source=self.source('EPSG:4326',[.05,0,-94,0,-.05,5,0,0,1]);before=copy.deepcopy(source)
  info=grid_info(source)
  self.assertEqual(info['unit'],'degree');self.assertEqual(info['step'],[.05,.05])
  self.assertEqual(info['scale'],.1);self.assertEqual(info['offset'],-2);self.assertEqual(source,before)
 def test_projected_rotated_grid_uses_native_step_vectors(self):
  info=grid_info(self.source('EPSG:32718',[300,400,0,400,-300,0,0,0,1]))
  self.assertEqual(info['step'],[500.,500.]);self.assertEqual(info['unit'],'metre')
 def test_missing_crs_is_not_guessed(self):
  source=self.source(None,[1,0,0,0,-1,0,0,0,1])
  self.assertIsNone(grid_info(source))
 def test_inactive_or_different_series_results_are_not_shown(self):
  p={'studio':{'timeline':['rain-scene'],'sig_transfer':{'asset_id':'rain-map','results':['r'],'scene_ids':['rain-scene']},
   'media':{'rain-map':{'source_dataset':'rain-inputs'}},'datasets':{'rain-inputs':[{'sha256':'rain','date':'2024-09-01'}]},
   'geography':{'sources':{'s':{'sha256':'rain','date':'2024-09-01'}},'map_workspace':{'layers':{'l':{'source_id':'s'}},'raster_time':{'layers':['l'],'presentation':{'territory':'ecuador'}}}}}}
  self.assertEqual(matching_results(p),['r'])
  p['studio']['geography']['sources']['s']['sha256']='temperature'
  self.assertEqual(matching_results(p),[])
  p['studio']['geography']['sources']['s']['sha256']='rain'
  p['studio']['geography']['map_workspace']['raster_time']['presentation']['territory']='province'
  self.assertEqual(matching_results(p),[])
  p['studio']['timeline']=[];self.assertEqual(matching_results(p),[])

if __name__=='__main__':unittest.main()
