"""Controlled georeferenced fixtures; no claim of real environmental results."""
import copy,io,json,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
import test_studio_geography as fixtures
from studio_sig_raster import add_raster,query,calculate,zonal,representation,settings,verify_source
from studio_sig_layers import workspace_for,layer_command,map_payload,add_geojson_layer


def raster_bytes(values,*,crs='EPSG:4326',transform=None,nodata=-9999):
    values=np.asarray(values,dtype='float32')
    with MemoryFile() as memory:
        with memory.open(driver='GTiff',height=values.shape[0],width=values.shape[1],count=1,dtype='float32',
                         crs=crs,transform=transform or from_origin(-79,0,1,1),nodata=nodata) as ds:ds.write(values,1)
        return memory.read()


class RasterTests(unittest.TestCase):
    setUp=fixtures.GeographyTests.setUp
    tearDown=fixtures.GeographyTests.tearDown
    def pair(self):
        a=raster_bytes([[0,-5],[10,-9999]]);b=raster_bytes([[2,-3],[12,-9999]])
        p,first=add_raster(self.project,a,'control-A.tif',self.provenance,observed_date='2024-01-01',variable='Control',units='mm',semantics='precipitation')
        p,second=add_raster(p,b,'control-B.tif',self.provenance,observed_date='2024-01-03',variable='Control',units='mm',semantics='precipitation')
        p=layer_command(p,{'action':'raster_time','value':{'layers':[first,second],'index':0,'compare':True}})
        return p,[first,second]
    def source(self,p,lid):return p['studio']['geography']['sources'][workspace_for(p)['layers'][lid]['source_id']]
    def test_import_location_native_zero_signed_nodata_and_original(self):
        p,ids=self.pair();s=self.source(p,ids[0]);self.assertEqual(s['raster']['bbox'],[-79.,-2.,-77.,0.])
        self.assertEqual(query(s,-78.5,-.5)['value'],0.)
        self.assertEqual(query(s,-77.5,-.5)['value'],-5.)
        self.assertIsNone(query(s,-77.5,-1.5)['value']);self.assertIsNone(query(s,0,0)['value'])
        self.assertEqual(s['raster']['statistics']['coverage'],.75)
        self.assertEqual(Path(s['path']).read_bytes(),raster_bytes([[0,-5],[10,-9999]]))
        self.assertEqual(self.project,self.before)
    def test_shared_scale_true_rgba_and_calendar_gaps(self):
        p,ids=self.pair();payload=map_payload(p);self.assertEqual(payload['layers'][0]['scale'],payload['layers'][1]['scale'])
        sources=[self.source(p,lid) for lid in ids];scale=settings(sources)
        self.assertEqual([scale['stops'][0],scale['stops'][-1]],[-5.,12.])
        for s in sources:
            image,_=representation(s,scale,size=2)
            try:
                self.assertEqual(image.mode,'RGBA');self.assertEqual(image.getpixel((0,0))[3],255);self.assertEqual(image.getpixel((1,1))[3],0)
            finally:image.close()
        p=layer_command(p,{'action':'raster_date','index':1});self.assertEqual(workspace_for(p)['active_layer'],ids[1])
        self.assertEqual([s['date'] for s in sources],['2024-01-01','2024-01-03'])
        from types import SimpleNamespace
        from studio_sig_workspace import preferences
        self.assertTrue(preferences(SimpleNamespace(project=p,key='reopened',state={}))['time'])
    def test_crs_date_and_alignment_reject_without_document_changes(self):
        p,ids=self.pair();before=copy.deepcopy(p)
        with self.assertRaises(ValueError):add_raster(p,raster_bytes([[1]],crs=None),'unknown.tif',self.provenance,observed_date='2024-01-01',variable='Control',units='mm')
        with self.assertRaises(ValueError):layer_command(p,{'action':'raster_time','value':{'layers':list(reversed(ids)),'index':0,'compare':True}})
        with self.assertRaises(ValueError):layer_command(p,{'action':'raster_date','index':True})
        q,lid=add_raster(p,raster_bytes([[1]],transform=from_origin(-79,0,.5,.5)),'other.tif',self.provenance,observed_date='2024-01-05',variable='Control',units='mm',semantics='precipitation')
        with self.assertRaisesRegex(ValueError,'alineación'):calculate(q,[ids[0],lid],'difference','bad.tif')
        self.assertEqual(p,before)
    def test_existing_alpha_and_empty_coverage_remain_transparent(self):
        from rasterio.enums import ColorInterp
        with MemoryFile() as memory:
            with memory.open(driver='GTiff',height=2,width=2,count=2,dtype='uint8',crs='EPSG:4326',
                             transform=from_origin(-79,0,1,1)) as ds:
                ds.write(np.array([[0,5],[10,20]],dtype='uint8'),1)
                ds.write(np.array([[255,255],[255,0]],dtype='uint8'),2)
                ds.colorinterp=(ColorInterp.gray,ColorInterp.alpha)
            content=memory.read()
        p,lid=add_raster(self.project,content,'alpha.tif',self.provenance,observed_date='2024-01-01',variable='Control',units='unidad')
        source=self.source(p,lid)
        self.assertIsNone(query(source,-77.5,-1.5)['value'])
        image,_=representation(source,settings([source]),size=2)
        try:self.assertEqual(image.getpixel((1,1))[3],0);self.assertEqual(image.getpixel((0,0))[3],255)
        finally:image.close()
        p,lid=add_raster(self.project,raster_bytes([[-9999,-9999],[-9999,-9999]]),'empty.tif',self.provenance,
                         observed_date='2024-01-01',variable='Control',units='unidad')
        source=self.source(p,lid);self.assertIsNone(settings([source]))
        image,_=representation(source,None,size=2)
        try:self.assertEqual(image.getchannel('A').getextrema(),(0,0))
        finally:image.close()
    def test_hot_cache_still_checks_bytes_metadata_and_authorization(self):
        p,ids=self.pair();s=self.source(p,ids[0]);verify_source(s);bad=copy.deepcopy(s);bad['raster']['statistics']['mean']=100
        with self.assertRaises(ValueError):verify_source(bad)
        bad=copy.deepcopy(s);bad['path']=str(Path(self.temp.name)/'not-authorized.tif')
        with self.assertRaises(ValueError):verify_source(bad)
        Path(s['path']).write_bytes(Path(s['path']).read_bytes()+b'changed')
        with self.assertRaises(ValueError):map_payload(p)
    def test_projected_crs_scale_offset_query_and_display_preserve_original(self):
        from pyproj import Transformer
        native=Transformer.from_crs('EPSG:4326','EPSG:32717',always_xy=True)
        display=Transformer.from_crs('EPSG:32717','EPSG:4326',always_xy=True)
        x,y=native.transform(-79,-1)
        with MemoryFile() as memory:
            with memory.open(driver='GTiff',height=2,width=2,count=1,dtype='int16',crs='EPSG:32717',
                             transform=from_origin(x,y,1000,1000),nodata=-9999) as ds:
                ds.write(np.array([[0,5],[10,-9999]],dtype='int16'),1);ds.scales=(2.,);ds.offsets=(-5.,)
            content=memory.read()
        p,lid=add_raster(self.project,content,'projected.tif',self.provenance,observed_date='2024-01-01',variable='Control',units='unidad')
        source=self.source(p,lid);lon,lat=display.transform(x+500,y-500)
        self.assertEqual(query(source,lon,lat)['value'],-5.)
        lon,lat=display.transform(x+1500,y-1500);self.assertIsNone(query(source,lon,lat)['value'])
        image,_=representation(source,settings([source]),size=32)
        try:self.assertEqual(image.mode,'RGBA');self.assertEqual(image.getchannel('A').getextrema(),(0,255))
        finally:image.close()
        self.assertEqual(Path(source['path']).read_bytes(),content);self.assertIn('UTM zone 17S',source['native_crs'])
    def test_calculation_new_result_intersection_mask_and_units(self):
        p,ids=self.pair();before=copy.deepcopy(p)
        for tool,expected in [('difference',2.),('mean',1.)]:
            result,lid=calculate(p,ids,tool,tool+'.tif');s=self.source(result,lid)
            self.assertEqual(query(s,-78.5,-.5)['value'],expected);self.assertIsNone(query(s,-77.5,-1.5)['value'])
            self.assertEqual(s['units'],'mm');self.assertIsNone(s['date']);self.assertEqual(s['raster_operation']['inputs'][1]['date'],'2024-01-03')
        with self.assertRaises(ValueError):calculate(p,ids,'sum','invalid.tif')
        self.assertEqual(p,before)
    def test_zonal_native_centres_units_and_missing_not_zero(self):
        p,ids=self.pair();features=[{'type':'Feature','properties':{'name':'control polygon'},'geometry':{'type':'Polygon','coordinates':fixtures.polygon(-79,-2,2)}}]
        row=zonal(self.source(p,ids[0]),features)[0]
        self.assertEqual(row['valid_cells'],3);self.assertEqual(row['domain_cells_in_raster'],4);self.assertEqual(row['coverage_within_raster'],.75)
        self.assertAlmostEqual(row['mean'],5/3);self.assertEqual(row['min'],-5.);self.assertEqual(row['units'],'mm')
        features[0]['geometry']={'type':'Point','coordinates':[-78.5,-.5]}
        with self.assertRaises(ValueError):zonal(self.source(p,ids[0]),features)
    def test_zonal_derived_layer_recipe_reopen_and_tamper_rejection(self):
        from studio_sig_raster import zonal_layer
        from studio_geography import read_source,validate_geography
        p,ids=self.pair()
        data={'type':'Feature','properties':{'name':'zona sintética'},'geometry':{'type':'Polygon','coordinates':fixtures.polygon(-79,-2,2)}}
        p,zone=add_geojson_layer(p,json.dumps(data).encode(),'zona.geojson',self.provenance)
        before=copy.deepcopy(p);candidate,lid=zonal_layer(p,ids[0],zone);s=self.source(candidate,lid)
        self.assertEqual(s['operation']['tool'],'zonal');self.assertEqual(s['operation']['units'],'mm')
        row=read_source(s)['features'][0]['properties'];self.assertAlmostEqual(row['mean'],5/3)
        self.assertEqual(row['coverage_within_raster'],.75);self.assertEqual(p,before)
        validate_geography(json.loads(json.dumps(candidate))['studio'])
        bad=copy.deepcopy(candidate);self.source(bad,lid)['operation']['parameters']['date']='2024-01-02'
        with self.assertRaises(ValueError):validate_geography(bad['studio'])
    def test_bundle_reuses_decoder_clock_attach_and_rejects_changed_sources(self):
        from studio_map_bundles import prepare_geographic_bundle,BundleFrames,read_bundle
        from studio_temporal import attach_map_layers,calendar_at,calendar_receipt
        from studio_timeline import PreparedTimeline
        from studio_workspace import WorkspaceSession
        from studio_project import source_projection,workspace_key
        from studio_recovery import recover_snapshot
        p,ids=self.pair();before=copy.deepcopy(p)
        with patch('studio_map_bundles.MEDIA_ROOT',Path(self.temp.name)/'media'):
            record=prepare_geographic_bundle(p,.2);manifest=read_bundle(record)
            self.assertFalse(manifest['geographic_binding']['basemap_included'])
            with BundleFrames(record) as frames:
                for frame,expected in [(0,'2024-01-01'),(3,'2024-01-03'),(5,'2024-01-03')]:
                    sample=frames.at(frame);self.assertEqual(sample['observation']['date'],expected)
                    self.assertEqual(sample['images']['galapagos'].getchannel('A').getextrema(),(0,0))
                    for image in sample['images'].values():image.close()
            candidate=attach_map_layers(p,record);prepared=PreparedTimeline(candidate)
            self.assertEqual(next(e['style']['opacity'] for e in candidate['studio']['scenes'][-1]['elements'] if e['type']=='map'),workspace_for(p)['layers'][ids[0]]['style']['opacity'])
            self.assertEqual(calendar_at(candidate,prepared.rows[-1]['start_frame']+3)[0]['date'],'2024-01-03')
            with prepared.frame_at(prepared.rows[-1]['start_frame']):pass
            self.assertEqual(candidate['studio']['calculations'],p['studio']['calculations'])
            self.assertEqual(candidate['project_meta'],p['project_meta'])
            state={'project_document':copy.deepcopy(p)};session=WorkspaceSession(state,workspace_key(p),source_projection(p),store=Path(self.temp.name)/'store',canonical=True)
            session.commit(candidate);saved,_=recover_snapshot(session.state[session.key+'_draft']);self.assertEqual(saved,session.project)
            session.dispatch({'action':'undo','version':session.version,'scene':session.selected});self.assertEqual(session.project['studio'],p['studio'])
            session.dispatch({'action':'redo','version':session.version,'scene':session.selected});self.assertEqual(session.project['studio'],candidate['studio'])
            bad=copy.deepcopy(p);self.source(bad,ids[0])['units']='degC'
            with self.assertRaises(ValueError):attach_map_layers(bad,record)
            bad=layer_command(p,{'action':'style','layer_id':ids[0],'style':{**workspace_for(p)['layers'][ids[0]]['style'],'opacity':.2}})
            with self.assertRaisesRegex(ValueError,'opacidad común'):prepare_geographic_bundle(bad,.2)
        self.assertEqual(p,before)

class RasterUiTests(unittest.TestCase):
    import test_sig_map_ui as ui_fixtures
    setUp=ui_fixtures.SigMapUiTests.setUp
    tearDown=ui_fixtures.SigMapUiTests.tearDown
    app=ui_fixtures.SigMapUiTests.app
    patches=ui_fixtures.SigMapUiTests.patches
    component=ui_fixtures.SigMapUiTests.component
    assert_clean=ui_fixtures.SigMapUiTests.assert_clean

    def test_real_import_form_unknown_crs_atomic_then_valid_and_pixel_query(self):
        from types import SimpleNamespace
        from studio_project import workspace_key
        from studio_sig_workspace import presentation_event
        app=self.app();bad=SimpleNamespace(name='unknown.tif',getvalue=lambda:raster_bytes([[0,-9999]],crs=None))
        with self.patches(),patch('studio_sig_map_ui._OL_COMPONENT',self.component),patch('studio_sig_raster_ui.st.file_uploader',return_value=bad) as uploaded:
            app.run();app.selectbox(key='sig_import_format').select('GeoTIFF').run()
            for key,value in [('sig_raster_date','2024-01-01'),('sig_raster_variable','Control'),('sig_raster_units','unidad'),
                              ('sig_raster_citation','Fixture controlada'),('sig_raster_license','CC0 fixture')]:app.text_input(key=key).input(value)
            before=copy.deepcopy(app.session_state['project_document'])
            app.button(key='sig_raster_submit').click().run()
            self.assertFalse(app.exception);self.assertTrue(app.error);self.assertEqual(app.session_state['project_document'],before)
            uploaded.return_value=SimpleNamespace(name='valid.tif',getvalue=lambda:raster_bytes([[0,-9999]]))
            app.button(key='sig_raster_submit').click().run();self.assert_clean(app)
            p=app.session_state['project_document'];key=workspace_key(p)
            session=SimpleNamespace(project=p,key=key,version=self.payload['version'],state={})
            lid=workspace_for(p)['active_layer'];before=copy.deepcopy(p)
            presentation_event(session,{'action':'query_raster','version':session.version,'layer_id':lid,'lon':-78.5,'lat':-.5})
            self.assertEqual(session.state[key+'_sig_pixel']['value'],0.)
            presentation_event(session,{'action':'query_raster','version':session.version,'layer_id':lid,'lon':-77.5,'lat':-.5})
            self.assertIsNone(session.state[key+'_sig_pixel']['value']);self.assertEqual(session.project,before)
            with self.assertRaises(ValueError):presentation_event(session,{'action':'query_raster','version':-1,'layer_id':lid,'lon':0,'lat':0})

    def test_open_empty_form_rejects_without_document_changes(self):
        app=self.app()
        with self.patches():
            app.run();before=copy.deepcopy(app.session_state['project_document'])
            app.button(key='sig_open_copy').click().run()
            self.assertFalse(app.exception);self.assertEqual(app.session_state['project_document'],before)

if __name__=='__main__':unittest.main()
