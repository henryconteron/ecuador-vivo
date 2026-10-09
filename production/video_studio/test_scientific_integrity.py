"""Small independent fixtures for native statistics and faithful display."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import rasterio
from rasterio.transform import from_bounds

sys.path.insert(0, str(Path(__file__).parent))
import data
from endcard import SummaryAccumulator
from maqueta import resize_values, load_galapagos_scene, GALAPAGOS_BOX
from model import default_project
from variables import detect_profile


def rectangle(box, name='Test'):
    west, south, east, north = box
    return {'type': 'Feature', 'properties': {'shapeName': name},
            'geometry': {'type': 'Polygon', 'coordinates': [[
                [west, south], [east, south], [east, north],
                [west, north], [west, south]]]}}


class NativeScientificIntegrity(unittest.TestCase):
    def test_categorical_source_does_not_compute_means_of_codes(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.raster(folder,np.array([[0,1],[0,1]],dtype='int16'))
            project=default_project()
            project.update(source='local',kind='categorical',bbox=[-1,-1,1,1],clip_ecuador=False,
                           endcard_enabled=False,classes=[{'value':0},{'value':1}])
            with patch('data.map_dimensions',return_value=(2,2)):
                values,metadata=data.load_values(project,{'date':'2024-01-01','path':str(path),'band':1},
                                                 province_features=[rectangle((-1,-1,1,1))])
            self.assertIsNone(metadata['spatial_stats'])
            self.assertEqual(metadata['province_samples'],{})
            self.assertEqual(set(values.ravel()),{0,1})

    def test_categorical_inset_reports_support_without_mean_of_class_codes(self):
        with tempfile.TemporaryDirectory() as folder:
            path=self.raster(folder,np.array([[0,1],[1,0]],dtype='int16'),box=GALAPAGOS_BOX)
            project=default_project()
            project.update(source='local',kind='categorical',
                           entries=[{'date':'2024-01-01','path':str(path),'band':1}])
            geo={'features':[rectangle(GALAPAGOS_BOX)]}
            with patch('maqueta.boundary',return_value=geo),patch('data.boundary',return_value=geo):
                result=load_galapagos_scene(project,'2024-01-01',8,8)
            self.assertIsNone(result['mean'])
            self.assertIsNone(result['max'])
            self.assertEqual(result['valid_pixels'],4)
            self.assertEqual(result['statistics_method'],'native_categorical_support')

    def test_all_nodata_retains_the_domain_denominator_without_inventing_zero(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.raster(folder, np.full((2,2), -9999, dtype='int16'))
            with rasterio.open(path) as src:
                stat = data.native_domain_stats(src, 1,
                    {'bbox':[-1,-1,1,1], 'clip_ecuador':False})
            self.assertIsNone(stat['mean'])
            self.assertEqual(stat['valid_pixels'],0)
            self.assertEqual(stat['total_pixels'],4)
            self.assertEqual(stat['coverage'],0)

    def test_projected_crs_uses_pixel_mean_without_latitude_weights(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'projected.tif'
            with rasterio.open(path,'w',driver='GTiff',width=1,height=2,count=1,
                               dtype='float32',crs='EPSG:3857',
                               transform=from_bounds(0,0,111319,8399737,1,2)) as dst:
                dst.write(np.array([[0],[100]],dtype='float32'),1)
            with rasterio.open(path) as src:
                stat = data._polygon_stats(src,1,[rectangle((0,0,1,60))])['Test']
            self.assertEqual(stat['mean'],50)
            self.assertEqual(stat['weighting'],'native_pixel_mean_projected_crs')

    def test_summary_labels_projected_weights_and_unclipped_domain_truthfully(self):
        project = default_project()
        project.update(clip_ecuador=False)
        accumulator = SummaryAccumulator(project, {'features':[]})
        stat = dict(mean=15,min=10,max=20,coverage=1,
                    weighting='native_pixel_mean_projected_crs',
                    spatial_domain='source_pixels_within_bbox')
        accumulator.observe('2024-01-01',np.array([[15]]),spatial_stats=stat)
        summary = accumulator.to_dict()
        self.assertNotEqual(summary['spatial_domain'],'ecuador_continental')
        self.assertNotIn('coseno',summary['scope'])
        self.assertIn('CRS proyectado',summary['scope'])

    def test_editorial_copy_never_changes_the_physical_aggregation(self):
        project = default_project()
        project.update(variable='NDVI', units='', source='local')
        self.assertEqual(detect_profile(project)['kind'], 'index')
        self.assertEqual(detect_profile(project)['aggregation'], 'mean')
        expected = detect_profile(project)
        project.update(title='LLUVIA', name='Lluvia', description='Lluvia acumulada',
                       legend='Lluvia', background='#000000')
        self.assertEqual(detect_profile(project), expected)

    def test_rainfall_title_cannot_switch_sum_to_anomaly_mean(self):
        project = default_project()
        expected = detect_profile(project)
        self.assertEqual(expected['aggregation'], 'sum')
        project['title'] = 'Anomalía: explicación del concepto'
        self.assertEqual(detect_profile(project), expected)

    def raster(self, folder, values, *, box=(-1, -1, 1, 1), nodata=-9999):
        path = Path(folder) / 'input.tif'
        with rasterio.open(path, 'w', driver='GTiff', count=1,
                           width=values.shape[1], height=values.shape[0],
                           dtype=values.dtype, crs='EPSG:4326',
                           transform=from_bounds(*box, values.shape[1], values.shape[0]),
                           nodata=nodata) as dst:
            dst.write(values, 1)
        return path

    def test_integer_nodata_preserves_zero_and_negative_physical_values(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.raster(folder, np.array([[0, 10], [20, -9999]], dtype='int16'))
            with rasterio.open(path) as src:
                stat = data._polygon_stats(src, 1, [rectangle((-1, -1, 1, 1))],
                                           scale=2, offset=-5)['Test']
            # Valid physical pixels: -5, 15, 35. Rows are symmetric about equator.
            self.assertAlmostEqual(stat['mean'], 15)
            self.assertEqual((stat['min'], stat['max']), (-5, 35))
            self.assertEqual(stat['valid_pixels'], 3)
            self.assertEqual(stat['total_pixels'], 4)
            self.assertEqual(stat['coverage'], .75)

    def test_source_nodata_is_exact_not_an_epsilon_around_valid_zero(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.raster(folder, np.array([[0, 1e-9], [2e-9, 0]], dtype='float64'), nodata=None)
            with rasterio.open(path) as src:
                stat = data._polygon_stats(src, 1, [rectangle((-1, -1, 1, 1))],
                                           source_nodata=0)['Test']
            self.assertAlmostEqual(stat['mean'], 1.5e-9, delta=1e-15)
            self.assertEqual(stat['valid_pixels'], 2)

    def test_summary_uses_native_pixels_independent_of_display_resolution(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.raster(folder, np.array([[0, 10], [20, -9999]], dtype='float32'))
            project = default_project()
            project.update(source='local', variable='Temperatura', units='°C',
                           bbox=[-1, -1, 1, 1], clip_ecuador=False)
            row = {'date': '2024-01-01', 'path': str(path), 'band': 1}
            results = []
            for size in [(19, 11), (2, 2)]:
                with patch('data.map_dimensions', return_value=size):
                    values, metadata = data.load_values(project, row)
                acc = SummaryAccumulator(project, {'features': []})
                kwargs = ({'spatial_stats': metadata['spatial_stats']}
                          if 'spatial_stats' in metadata else {})
                acc.observe(row['date'], values, **kwargs)
                result = acc.to_dict()
                self.assertAlmostEqual(result['mean_period'], 10)
                self.assertEqual(result['peak_pixel_value'], 20)
                self.assertEqual(result['mean_method'], 'native_source_pixels')
                self.assertEqual(metadata['spatial_stats']['coverage'], .75)
                results.append(result)
            self.assertEqual(results[0], results[1])

    def test_geographic_weights_have_an_explicit_expected_value(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.raster(folder, np.array([[0], [100]], dtype='float32'),
                               box=(0, 0, 1, 60))
            with rasterio.open(path) as src:
                stat = data._polygon_stats(src, 1, [rectangle((0, 0, 1, 60))])['Test']
            # cos(45°)=.7071067812, cos(15°)=.9659258263.
            self.assertAlmostEqual(stat['mean'], 57.73502691896, places=8)

    def test_continuous_display_preserves_negative_values_and_missing_support(self):
        values = np.array([[-4, np.nan], [-4, -4]], dtype='float32')
        display = resize_values(values, 8, 8, 'continuous')
        self.assertEqual(float(display[0, 0]), -4)
        self.assertTrue(np.isnan(display[0, -1]))
        self.assertTrue(np.isnan(values[0, 1]))
        self.assertEqual(float(values[1, 1]), -4)

    def test_categorical_display_preserves_nodata_separately_from_code_zero(self):
        values = np.array([[0, np.nan], [1, 1]], dtype='float32')
        display = resize_values(values, 4, 4, 'categorical')
        self.assertEqual(display[0, 0], 0)
        self.assertTrue(np.isnan(display[0, -1]))

    def test_local_island_statistics_do_not_depend_on_inset_dimensions(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.raster(folder, np.array([[-4, -4], [-4, -9999]], dtype='int16'),
                               box=GALAPAGOS_BOX)
            project = default_project()
            project.update(source='local', units='°C', variable='Temperatura',
                           entries=[{'date': '2024-01-01', 'band': 1, 'path': str(path)}])
            geo = {'type': 'FeatureCollection', 'features': [rectangle(GALAPAGOS_BOX)]}
            for size in [(17, 11), (2, 2)]:
                with patch('maqueta.boundary', return_value=geo), patch('data.boundary', return_value=geo):
                    result = load_galapagos_scene(project, '2024-01-01', *size)
                self.assertEqual(result['valid_pixels'], 3)
                self.assertEqual(result['mean'], -4)
                self.assertEqual(result['max'], -4)
                self.assertEqual(result['statistics_method'], 'native_source_pixels')


if __name__ == '__main__':
    unittest.main()
