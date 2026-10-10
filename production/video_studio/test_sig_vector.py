"""Analytic fixtures only: not real environmental measurements."""
import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
from pyproj import Transformer
from shapely.geometry import shape
import test_studio_geography as fixtures
from studio_sig_vector import add_csv,run_operation,layer_features,export_layer,add_ogr
from studio_sig_layers import add_geojson_layer,layer_command,map_payload
from studio_geography import validate_geography,render_region


class VectorTests(unittest.TestCase):
    setUp=fixtures.GeographyTests.setUp
    tearDown=fixtures.GeographyTests.tearDown
    def points(self):
        data=b'x,y,value,missing\n-78.5,-0.1,0,\n-78.49,-0.11,-5,\n'
        project,lid=add_csv(self.project,data,'points.csv',self.provenance,x='x',y='y',source_crs='EPSG:4326')
        return project,lid,data
    def test_csv_origin_crs_points_attributes_and_tamper_even_hot_cache(self):
        project,lid,data=self.points();source,features=layer_features(project,lid)
        self.assertEqual([f['properties']['value'] for f in features],['0','-5'])
        self.assertIsNone(features[0]['properties']['missing'])
        self.assertEqual(Path(source['origin']['path']).read_bytes(),data)
        self.assertEqual(features[0]['geometry']['type'],'Point')
        self.assertEqual(map_payload(project)['layers'][0]['features'][0]['geometry']['coordinates'],[-78.5,-.1])
        Path(source['origin']['path']).write_bytes(data+b'altered')
        with self.assertRaises(ValueError):validate_geography(project['studio'])
        self.assertEqual(self.project,self.before)
    def test_unknown_crs_invalid_rows_zero_y_and_projected_input(self):
        for crs in ('','unknown'):
            with self.assertRaises(ValueError):add_csv(self.project,b'x,y\n0,0\n','bad.csv',self.provenance,x='x',y='y',source_crs=crs)
        for data in (b'x,y\n,0\n',b'x,y\nnan,0\n',b'x,x\n0,0\n'):
            with self.assertRaises(ValueError):add_csv(self.project,data,'bad.csv',self.provenance,x='x',y='y',source_crs='EPSG:4326')
        p,lid=add_csv(self.project,b'x,y\n0,0\n','zero.csv',self.provenance,x='x',y='y',source_crs='EPSG:4326')
        self.assertEqual(layer_features(p,lid)[1][0]['geometry']['coordinates'],[0.,0.])
        x,y=Transformer.from_crs(4326,32717,always_xy=True).transform(-78.5,-.1)
        p,lid=add_csv(self.project,f'x,y\n{x},{y}\n'.encode(),'utm.csv',self.provenance,x='x',y='y',source_crs='EPSG:32717')
        self.assertAlmostEqual(layer_features(p,lid)[1][0]['geometry']['coordinates'][0],-78.5,places=8)
    def test_lines_points_do_not_become_polygon_statistics(self):
        invalid={'type':'Feature','properties':{},'geometry':{'type':'LineString','coordinates':[[0,0]]}}
        with self.assertRaisesRegex(ValueError,'Geometría'):
            add_geojson_layer(self.project,json.dumps(invalid).encode(),'invalid-line.geojson',self.provenance)
        doc={'type':'FeatureCollection','features':[{'type':'Feature','properties':{},'geometry':{'type':'LineString','coordinates':[[-78.5,-.1],[-78.49,-.11]]}}]}
        p,lid=add_geojson_layer(self.project,json.dumps(doc).encode(),'line.geojson',self.provenance)
        rid=map_payload(p)['layers'][0]['features'][0]['region_id']
        with self.assertRaisesRegex(ValueError,'dominio'):render_region(p,rid)
        self.assertEqual(layer_features(p,lid)[1][0]['geometry']['type'],'LineString')
    def test_buffer_metric_domain_and_immutable_sources(self):
        p,lid,_=self.points();before=copy.deepcopy(p)
        for crs in ('','EPSG:4326','EPSG:3857','EPSG:32631'):
            with self.assertRaises(ValueError):run_operation(p,lid,'buffer',{'crs':crs,'distance':1000})
        result,new=run_operation(p,lid,'buffer',{'crs':'EPSG:32717','distance':1000})
        source,features=layer_features(result,new)
        from shapely.ops import transform
        projector=Transformer.from_crs('OGC:CRS84',32717,always_xy=True)
        self.assertAlmostEqual(transform(projector.transform,shape(features[0]['geometry'])).area,3_136_548.49,delta=.1)
        self.assertEqual(source['operation']['units'],'m');self.assertEqual(p,before)
        self.assertEqual(source['operation']['parameters']['quad_segs'],16)
        self.assertIn('GEOS',source['operation']['engine'])
        self.assertEqual(result['studio']['calculations'],p['studio']['calculations'])
        bad=copy.deepcopy(result);bad['studio']['geography']['sources'][source['id']]['operation']['units']='degrees'
        with self.assertRaises(ValueError):validate_geography(bad['studio'])
    def test_calculation_filter_missing_and_no_silent_overwrite(self):
        p,lid,_=self.points()
        result,new=run_operation(p,lid,'calculate',{'field':'value','output':'double','operator':'multiply','constant':2,'units':'test units'})
        self.assertEqual([f['properties']['double'] for f in layer_features(result,new)[1]],[0.,-10.])
        r,n=run_operation(p,lid,'calculate',{'field':'missing','output':'absent','operator':'multiply','constant':2,'units':''})
        self.assertTrue(all(f['properties']['absent'] is None for f in layer_features(r,n)[1]))
        r,n=run_operation(p,lid,'filter',{'field':'value','operator':'less','value':0})
        self.assertEqual(len(layer_features(r,n)[1]),1)
        for params in [{'field':'unknown','output':'x','operator':'add','constant':1},
            {'field':'value','output':'value','operator':'add','constant':1},
            {'field':'missing','output':'x','operator':'divide','constant':0}]:
            with self.assertRaises(ValueError):run_operation(p,lid,'calculate',params)
    def test_derivatives_clip_intersection_dissolve_measure_export_and_reopen(self):
        p,lid,_=self.points();p,buffer=run_operation(p,lid,'buffer',{'crs':'EPSG:32717','distance':1000})
        p,dissolved=run_operation(p,buffer,'dissolve',{'field':None})
        self.assertEqual(len(layer_features(p,dissolved)[1]),1)
        p,clipped=run_operation(p,lid,'clip',{},other=dissolved)
        self.assertEqual(len(layer_features(p,clipped)[1]),2)
        p,intersect=run_operation(p,lid,'intersection',{},other=buffer)
        self.assertGreaterEqual(len(layer_features(p,intersect)[1]),2)
        p,measured=run_operation(p,dissolved,'measure',{'crs':'EPSG:32717'})
        self.assertGreater(layer_features(p,measured)[1][0]['properties']['ev_area_m2'],0)
        exported=json.loads(export_layer(p,measured));self.assertEqual(exported['ecuador_vivo_operation']['tool'],'measure')
        from studio_recovery import save_snapshot,recover_snapshot
        path=Path(self.temp.name)/'result.json';save_snapshot(path,p);r,_=recover_snapshot(path);self.assertEqual(r,p)
        self.assertEqual(layer_command(p,{'action':'rename','layer_id':measured,'name':'Resultado medido'})['studio']['geography']['map_workspace']['layers'][measured]['name'],'Resultado medido')
        self.assertEqual(self.project,self.before)
    def test_ogr_geopackage_native_crs_and_original_retained(self):
        import geopandas as gpd
        from shapely.geometry import Point
        path=Path(self.temp.name)/'points.gpkg'
        gpd.GeoDataFrame({'value':[0,-5]},geometry=[Point(0,0),Point(100,100)],crs=32717).to_file(path,engine='pyogrio',driver='GPKG',layer='points')
        raw=path.read_bytes();p,lid=add_ogr(self.project,raw,'points.gpkg',self.provenance,kind='gpkg',layer='points')
        self.assertEqual(Path(layer_features(p,lid)[0]['origin']['path']).read_bytes(),raw)
        self.assertEqual(layer_features(p,lid)[1][0]['properties']['value'],0)
        with self.assertRaises(ValueError):add_ogr(self.project,raw,'bad.gpkg',self.provenance,kind='gpkg',source_crs='EPSG:4326')
        with patch('pyogrio.list_layers') as reader:
            with self.assertRaises(ValueError):add_ogr(self.project,b'<OGRVRTDataSource/>','bad.gpkg',self.provenance,kind='gpkg')
            reader.assert_not_called()

    def test_failed_durable_commit_and_undo_do_not_lose_inputs(self):
        from studio_project import publish_document,workspace_key,source_projection
        from studio_workspace import WorkspaceSession
        from studio_recovery import recover_snapshot
        p,lid,_=self.points();state={};publish_document(state,p)
        session=WorkspaceSession(state,workspace_key(p),source_projection(p),store=Path(self.temp.name),canonical=True)
        candidate,new=run_operation(p,lid,'buffer',{'crs':'EPSG:32717','distance':1000})
        version=session.version
        with patch('studio_workspace.save_snapshot',side_effect=OSError('Test storage unavailable')):
            with self.assertRaises(OSError):session.commit(candidate)
        self.assertEqual(session.project,p);self.assertEqual(session.version,version)
        session.commit(candidate)
        recovered,_=recover_snapshot(session.state[session.key+'_draft']);self.assertEqual(recovered,session.project)
        session.dispatch({'action':'undo','version':session.version,'scene':session.selected})
        self.assertEqual(session.project['studio']['geography'],p['studio']['geography'])
        session.dispatch({'action':'redo','version':session.version,'scene':session.selected})
        self.assertEqual(session.project['studio']['geography'],candidate['studio']['geography'])

    def test_flatgeobuf_line_import_and_wrong_container_rejected(self):
        import geopandas as gpd
        from shapely.geometry import LineString
        path=Path(self.temp.name)/'lines.fgb'
        gpd.GeoDataFrame({'value':[-5]},geometry=[LineString([(-78.5,-.1),(-78.49,-.11)])],crs=4326).to_file(path,engine='pyogrio',driver='FlatGeobuf')
        raw=path.read_bytes()
        p,lid=add_ogr(self.project,raw,'lines.fgb',self.provenance,kind='fgb')
        self.assertEqual(layer_features(p,lid)[1][0]['geometry']['type'],'LineString')
        self.assertEqual(layer_features(p,lid)[1][0]['properties']['value'],-5)
        with self.assertRaises(ValueError):add_ogr(self.project,raw,'wrong.gpkg',self.provenance,kind='gpkg')


if __name__=='__main__':unittest.main()
