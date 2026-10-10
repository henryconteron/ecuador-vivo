"""Multi-date regression over canonical rasters; controlled scientific fixtures."""
import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
from test_sig_raster import RasterTests,raster_bytes
from studio_sig_raster import add_raster,query,calculate
from studio_sig_layers import layer_command,workspace_for,map_payload
from studio_sig_timelapse import configure,output_frame,gaps


class TimelapseTests(unittest.TestCase):
    setUp=RasterTests.setUp
    tearDown=RasterTests.tearDown
    source=RasterTests.source
    def series(self,profile=None):
        p=self.project;ids=[]
        for day,value in [('2024-01-01',0),('2024-01-03',10),('2024-01-04',20)]:
            p,lid=add_raster(p,raster_bytes([[value,-5],[10,-9999]]),day+'.tif',self.provenance,
                observed_date=day,variable='Control',units='mm',semantics='precipitation');ids.append(lid)
        return configure(p,list(reversed(ids)),duration=.3,cadence='daily',profile=profile),ids
    def test_dates_lazy_payload_static_originals_no_partial_changes(self):
        p,ids=self.series();before=copy.deepcopy(p)
        self.assertEqual(workspace_for(p)['raster_time']['layers'],ids)
        payload=map_payload(p);self.assertEqual(sum(bool(x['image']) for x in payload['layers']),1)
        p=layer_command(p,{'action':'raster_date','index':2});self.assertEqual(workspace_for(p)['active_layer'],ids[2])
        self.assertEqual(query(self.source(p,ids[2]),-78.5,-.5)['value'],20)
        self.assertIsNone(query(self.source(p,ids[2]),-77.5,-1.5)['value'])
        self.assertEqual(gaps(['2024-01-01','2024-01-03','2024-01-04'],'daily'),[{'after':'2024-01-01','before':'2024-01-03','missing_intervals':1}])
        with self.assertRaises(ValueError):layer_command(p,{'action':'raster_date','index':3})
        with self.assertRaises(ValueError):calculate(p,ids,'mean','invalid.tif')
        with self.assertRaises(ValueError):configure(p,[ids[0],ids[0]],duration=.3)
        with self.assertRaises(ValueError):configure(p,ids,duration=.1/3)
        with self.assertRaisesRegex(ValueError,'una observación por mes'):configure(p,ids,duration=.3,cadence='monthly')
        with self.assertRaises(ValueError):layer_command(p,{'action':'raster_time','value':{**workspace_for(p)['raster_time'],'compare':True}})
        q,static=add_raster(p,raster_bytes([[3,4],[5,-9999]]),'static.tif',self.provenance,observed_date=None,variable='Elevation',units='m')
        with self.assertRaises(ValueError):configure(q,[ids[0],static])
        self.assertEqual(before['project_meta'],p['project_meta']);self.assertEqual(self.project,self.before)
    def test_adaptive_frame_rendition_calendar_binding_save_undo(self):
        from studio_map_bundles import prepare_geographic_bundle,read_bundle,BundleFrames
        from studio_temporal import attach_map_layers,calendar_at
        from studio_timeline import PreparedTimeline
        from studio_workspace import WorkspaceSession
        from studio_project import workspace_key,source_projection
        from studio_recovery import recover_snapshot
        for profile in ({'id':'youtube'},{'id':'tiktok'}):
            p,ids=self.series(profile);frame=output_frame(p)
            self.assertAlmostEqual((frame['bbox'][2]-frame['bbox'][0])/(frame['bbox'][3]-frame['bbox'][1]),frame['map_width']/frame['map_height'],delta=.003)
            with patch('studio_map_bundles.MEDIA_ROOT',Path(self.temp.name)/'media'):
                record=prepare_geographic_bundle(p,.3);manifest=read_bundle(record)
                self.assertEqual([o['date'] for o in manifest['observations']],['2024-01-01','2024-01-03','2024-01-04'])
                self.assertEqual(manifest['region'],frame['bbox']);self.assertGreater(max(manifest['layers']['continent']['size']),512)
                self.assertEqual(manifest['geographic_binding']['output_profile'],profile)
                with BundleFrames(record) as decoder:
                    for n,date in [(0,'2024-01-01'),(3,'2024-01-03'),(6,'2024-01-04')]:
                        sample=decoder.at(n);self.assertEqual(sample['observation']['date'],date)
                        for image in sample['images'].values():image.close()
                candidate=attach_map_layers(p,record);prepared=PreparedTimeline(candidate)
                from studio_editing import adapt_profile
                other=adapt_profile(p,{'id':'instagram_square'})
                with self.assertRaisesRegex(ValueError,'formato cambió'):attach_map_layers(other,record)
                # Presentation edits after insertion may reuse the same sealed
                # resource, calendar and science in another output format.
                resized=adapt_profile(candidate,{'id':'instagram_square'});PreparedTimeline(resized)
                self.assertEqual(calendar_at(candidate,prepared.rows[-1]['start_frame']+6)[0]['date'],'2024-01-04')
                with prepared.frame_at(prepared.rows[-1]['start_frame']+3):pass
                state={'project_document':copy.deepcopy(p)};s=WorkspaceSession(state,workspace_key(p),source_projection(p),store=Path(self.temp.name)/('store-'+profile['id']),canonical=True)
                s.commit(candidate);saved,_=recover_snapshot(s.state[s.key+'_draft']);self.assertEqual(saved,s.project)
                s.dispatch({'action':'undo','version':s.version,'scene':s.selected});self.assertEqual(s.project['studio'],p['studio'])
                s.dispatch({'action':'redo','version':s.version,'scene':s.selected});self.assertEqual(s.project['studio'],candidate['studio'])
    def test_licensed_references_preserve_geography_and_no_duplicate_sources(self):
        from studio_sig_references import reference,initial_map,catalog,EXTENTS
        from studio_geography import read_source
        p=initial_map(self.project);state=workspace_for(p)
        self.assertEqual(state['view']['bbox'],EXTENTS['Ecuador continental'])
        source=next(s for s in p['studio']['geography']['sources'].values() if s['name']=='Ecuador · 24 provincias')
        features=read_source(source)['features'];self.assertEqual(len(features),24)
        self.assertIn('Galápagos',[f['properties']['shapeName'] for f in features])
        q,lid=reference(p,'latin-america');self.assertEqual(len(catalog()['latin-america']['countries']),20)
        q2,_=reference(q,'latin-america');self.assertEqual(len(q['studio']['geography']['sources']),len(q2['studio']['geography']['sources']))
        self.assertEqual(initial_map(q),q);self.assertEqual(self.project,self.before)
