"""Analytic projected fixtures, not environmental observations."""
import copy,json,unittest
from pyproj import Transformer
from shapely.geometry import Polygon,shape,mapping
from shapely.ops import transform
import test_studio_geography as fixtures
from studio_sig_layers import add_geojson_layer
from studio_sig_vector import run_operation,layer_features,export_layer
from studio_geography import validate_geography

class GeometryToolsTests(unittest.TestCase):
    setUp=fixtures.GeographyTests.setUp
    tearDown=fixtures.GeographyTests.tearDown

    def ring(self):
        outer=[(500000,9800000),(501000,9800000),(501000,9801000),(500000,9801000)]
        hole=[(500200,9800200),(500800,9800200),(500800,9800800),(500200,9800800)]
        original=Polygon(outer,[hole])
        to_view=Transformer.from_crs(32717,'OGC:CRS84',always_xy=True)
        data=json.dumps({'type':'Feature','id':'ring','properties':{'value':0,'missing':None},
            'geometry':mapping(transform(to_view.transform,original))}).encode()
        project,lid=add_geojson_layer(self.project,data,'ring.geojson',self.provenance)
        return project,lid,original

    def test_centroid_and_interior_are_distinct_preserve_attributes_and_sources(self):
        project,lid,original=self.ring();before=copy.deepcopy(project)
        to_metric=Transformer.from_crs('OGC:CRS84',32717,always_xy=True)
        points=[]
        for tool in ('centroid','point_on_surface'):
            result,new=run_operation(project,lid,tool,{'crs':'EPSG:32717'})
            source,features=layer_features(result,new)
            self.assertEqual(len(features),1)
            self.assertEqual(features[0]['properties'],{'value':0,'missing':None})
            point=transform(to_metric.transform,shape(features[0]['geometry']));points.append(point)
            self.assertEqual(source['operation']['tool'],tool)
            self.assertIn('projected',source['operation']['parameters']['geometry_method'])
            self.assertEqual(source['operation']['inputs'][0]['sha256'],layer_features(project,lid)[0]['sha256'])
            validate_geography(result['studio']);self.assertIn(tool,export_layer(result,new).decode())
            corrupted=copy.deepcopy(result);corrupted['studio']['geography']['sources'][source['id']]['operation']['parameters']['crs']='EPSG:4326'
            with self.assertRaises(ValueError):validate_geography(corrupted['studio'])
            for key in ('calculations','datasets','scenes'):self.assertEqual(result['studio'][key],project['studio'][key])
        self.assertAlmostEqual(points[0].x,500500,places=6);self.assertAlmostEqual(points[0].y,9800500,places=6)
        self.assertFalse(original.covers(points[0]));self.assertTrue(original.contains(points[1]))
        self.assertEqual(project,before)

    def test_hull_and_boundaries_keep_holes_and_per_feature_semantics(self):
        project,lid,original=self.ring()
        result,new=run_operation(project,lid,'convex_hull',{'crs':'EPSG:32717'})
        hull=transform(Transformer.from_crs('OGC:CRS84',32717,always_xy=True).transform,shape(layer_features(result,new)[1][0]['geometry']))
        self.assertAlmostEqual(hull.area,1_000_000,places=3)
        result,new=run_operation(project,lid,'boundary',{})
        boundary=shape(layer_features(result,new)[1][0]['geometry'])
        self.assertEqual(boundary.geom_type,'MultiLineString');self.assertEqual(len(boundary.geoms),2)
        self.assertEqual(layer_features(result,new)[1][0]['properties']['value'],0)
        self.assertEqual(project['studio']['geography']['map_workspace']['active_layer'],lid)

    def test_invalid_crs_and_non_polygon_boundaries_fail_without_partial_result(self):
        project,lid,_=self.ring();before=copy.deepcopy(project)
        for tool in ('centroid','point_on_surface','convex_hull'):
            for crs in ('','EPSG:4326','EPSG:3857','EPSG:32631'):
                with self.assertRaises(ValueError):run_operation(project,lid,tool,{'crs':crs})
        point={'type':'Feature','properties':{},'geometry':{'type':'Point','coordinates':[-79,-2]}}
        p,l=add_geojson_layer(project,json.dumps(point).encode(),'point.geojson',self.provenance)
        with self.assertRaisesRegex(ValueError,'polígonos'):run_operation(p,l,'boundary',{})
        self.assertEqual(project,before)

if __name__=='__main__':unittest.main()
