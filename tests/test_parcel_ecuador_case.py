import unittest
from tools.parcelas.ecuador_case import build_payload, sensor_request, verify_source


class EcuadorCaseTests(unittest.TestCase):
    def test_small_field_uses_own_crs_and_native_spacing(self):
        p=build_payload('optical','2020-10-01',[600000,9870000,600200,9870200],epsg=32717)
        self.assertEqual(p['output']['width'],20)
        self.assertEqual(p['output']['height'],20)
        self.assertTrue(p['input']['bounds']['properties']['crs'].endswith('/32717'))

    def test_optical_service_product_matches_selected_catalog(self):
        self.assertEqual(verify_source({'orbits':[{'tiles':[{'sentinel2ProductId':'scene.SAFE'}]}]},'optical','scene'),'product_id_matched_catalog')

    def test_other_radar_source_rejected(self):
        with self.assertRaises(ValueError):
            verify_source({'orbits':[{'tiles':[{'sentinel1ProductId':'other.SAFE'}]}]},'radar','scene')

    def test_optical_native_visible_grid_not_ai_upscale(self):
        p=build_payload('optical','2020-10-01',[500000,9950000,501000,9951000])
        self.assertEqual(p['output']['width'],100)
        self.assertIn('REFLECTANCE',p['evalscript'])
        self.assertIn('SCL',p['evalscript'])

    def test_radar_different_grid_explicit_same_extent(self):
        p=build_payload('radar','2020-10-01',[500000,9950000,501000,9951000], 'ASCENDING')
        self.assertEqual(p['output']['width'],50)
        self.assertTrue(p['input']['data'][0]['processing']['orthorectify'])
        self.assertEqual(p['input']['data'][0]['dataFilter']['orbitDirection'],'ASCENDING')

    def test_reject_unknown_sensor(self):
        with self.assertRaises(ValueError):
            sensor_request('fake')
