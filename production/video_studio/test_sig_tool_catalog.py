import copy,unittest
from types import SimpleNamespace
import test_studio_geography as fixtures
from studio_sig_layers import add_geojson_layer
from studio_sig_tool_catalog import VECTOR_TOOLS,RASTER_TOOLS,tool_catalog,launch_operation

class ToolCatalogTests(unittest.TestCase):
    setUp=fixtures.GeographyTests.setUp
    tearDown=fixtures.GeographyTests.tearDown
    def test_catalog_unique_grouped_and_explicit_requirements_without_reads(self):
        empty=tool_catalog(self.project)
        self.assertEqual(len({t['id'] for t in empty}),len(empty))
        self.assertEqual(len(empty),15);self.assertTrue(all(not t['available'] and t['reason'] for t in empty))
        project,lid=add_geojson_layer(self.project,self.content,'regions.geojson',self.provenance)
        before=copy.deepcopy(project);tools={t['id']:t for t in tool_catalog(project)}
        self.assertTrue(tools['centroid']['available']);self.assertFalse(tools['clip']['available'])
        self.assertTrue(tools['boundary']['available']);self.assertFalse(tools['raster_difference']['available'])
        self.assertEqual(project,before)

    def test_raster_availability_and_direct_form_presets(self):
        from test_sig_raster import raster_bytes
        from studio_sig_raster import add_raster
        from studio_sig_workspace import preferences
        project,_=add_raster(self.project,raster_bytes([[1,2],[3,4]]),'a.tif',self.provenance,
                             observed_date='2024-01-01',variable='Control',units='mm')
        tools={t['id']:t for t in tool_catalog(project)}
        self.assertFalse(tools['raster_difference']['available'])
        self.assertFalse(tools['raster_zonal']['available'])
        project,_=add_raster(project,raster_bytes([[2,3],[4,5]]),'b.tif',self.provenance,
                             observed_date='2024-01-02',variable='Control',units='mm')
        project,_=add_geojson_layer(project,self.content,'regions.geojson',self.provenance)
        before=copy.deepcopy(project);session=SimpleNamespace(project=project,key='test',state={},version=7)
        tools={t['id']:t for t in tool_catalog(project)}
        self.assertTrue(all(tools[t['id']]['available'] for t in RASTER_TOOLS))
        launch_operation(session,'raster_difference')
        self.assertEqual(preferences(session)['tool'],'Ráster y tiempo')
        self.assertEqual(session.state['sig_raster_tool'],'Diferencia B − A')
        self.assertEqual(project,before)
        self.assertEqual({t['id'] for t in VECTOR_TOOLS},{'buffer','clip','intersection','dissolve','measure','calculate','filter','centroid','point_on_surface','convex_hull','boundary'})
    def test_launch_validates_capability_and_chooses_existing_form_without_mutation(self):
        from studio_sig_workspace import preferences
        project,lid=add_geojson_layer(self.project,self.content,'regions.geojson',self.provenance)
        session=SimpleNamespace(project=project,key='test',state={},version=7)
        before=copy.deepcopy(project)
        launch_operation(session,'centroid')
        self.assertEqual(preferences(session)['tool'],'Análisis vectorial')
        self.assertEqual(session.state['test_vector_operation'],'Centroides')
        self.assertEqual(session.state['test_sig_dialog'],'tools')
        with self.assertRaises(ValueError):launch_operation(session,'raster_difference')
        with self.assertRaises(ValueError):launch_operation(session,'not-real')
        self.assertEqual(project,before)

    def test_capabilities_use_presented_geometry_and_native_grid_metadata(self):
        from studio_sig_layers import map_payload
        from studio_sig_vector import run_operation
        project,lid=add_geojson_layer(self.project,self.content,'regions.geojson',self.provenance)
        project,line=run_operation(project,lid,'boundary',{},name='Lines')
        tools={t['id']:t for t in tool_catalog(project,map_payload(project)['layers'])}
        self.assertFalse(tools['boundary']['available']);self.assertIn('polígonos',tools['boundary']['reason'])
        from test_sig_raster import raster_bytes
        from studio_sig_raster import add_raster
        for value,date,units in [(1,'2024-01-01','mm'),(2,'2024-01-02','°C')]:
            project,_=add_raster(project,raster_bytes([[value,2],[3,4]]),date+'.tif',self.provenance,observed_date=date,variable='Control',units=units)
        tools={t['id']:t for t in tool_catalog(project,map_payload(project)['layers'])}
        self.assertFalse(tools['raster_difference']['available']);self.assertIn('compatibles',tools['raster_difference']['reason'])

if __name__=='__main__':unittest.main()
