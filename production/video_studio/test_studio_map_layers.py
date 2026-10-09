"""4b.0: synthetic signed rasters, geographic masks and genuine missing support."""
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image
import rasterio
from rasterio.transform import from_bounds

import data
import maqueta
from endcard import SummaryAccumulator
from model import default_project
from test_scientific_integrity import rectangle


def two_region_fixture(folder):
    """Synthetic global grid: mainland, island, Jan 1/3; island absent on Jan 3."""
    extent = (-92.2, -5.2, -75.0, 2.2)
    width, height = 172, 74  # 0.1 degree grid, not real Ecuador observations.
    transform = from_bounds(*extent, width, height)
    mainland = (-80, -3, -78, -1)
    island = (-91.5, -.8, -90.5, .2)
    shape = {'type': 'FeatureCollection', 'features': [
        rectangle(mainland, 'Synthetic mainland'), rectangle(island, 'Synthetic island')]}
    rows, cols = np.indices((height, width))
    lon = transform.c + (cols + .5) * transform.a
    lat = transform.f + (rows + .5) * transform.e
    main = (lon > mainland[0]) & (lon < mainland[2]) & (lat > mainland[1]) & (lat < mainland[3])
    gal = (lon > island[0]) & (lon < island[2]) & (lat > island[1]) & (lat < island[3])
    first = np.full((height, width), -9999, dtype='float32')
    first[main] = 4
    first[main & (lon < -79) & (lat > -2)] = 0
    first[main & (lon < -79) & (lat < -2)] = -4
    first[main & (lon > -79) & (lat > -2)] = -9999
    first[gal] = -4
    first[gal & (lon > -91)] = 0
    second = first.copy()
    second[gal] = -9999
    path = Path(folder) / 'synthetic-two-regions-two-dates.tif'
    with rasterio.open(path, 'w', driver='GTiff', width=width, height=height,
                       count=2, dtype='float32', crs='EPSG:4326', transform=transform,
                       nodata=-9999) as src:
        src.write(first, 1)
        src.write(second, 2)
    project = default_project()
    project.update(source='local', variable='Synthetic signed field', units='°C',
                   bbox=list(maqueta.MAIN_BOX), start='2025-01-01', end='2025-01-03',
                   citation='Synthetic 4b.0 fixture; not observed Ecuador data',
                   show_provinces=False, cities=[], stops=[-4, 0, 4],
                   palette=['#204060', '#40a080', '#d08040'],
                   entries=[{'date': '2025-01-01', 'path': str(path), 'band': 1},
                            {'date': '2025-01-03', 'path': str(path), 'band': 2}])
    return project, shape


class MapNoDataTests(unittest.TestCase):
    def test_categorical_zero_remains_visible_and_missing_support_stays_transparent_after_resize(self):
        project = default_project()
        project.update(kind='categorical', classes=[
            {'value': 0, 'label': 'Synthetic zero', 'color': '#40a080'},
            {'value': 1, 'label': 'Synthetic one', 'color': '#d08040'}])
        values = np.array([[0, np.nan], [1, 1]], dtype='float32')
        resized = maqueta.resize_values(values, 8, 8, project['kind'])
        mask, _, _ = maqueta.build_mask_and_rings(
            {'features': [rectangle((0, 0, 1, 1))]}, (0, 0, 1, 1), 8, 8)
        rgba = Image.fromarray(maqueta.colorize(resized, project)).convert('RGBA')
        rgba.putalpha(maqueta.raster_alpha(resized, mask))
        self.assertEqual(rgba.getpixel((1, 1)), (*maqueta.hex_to_rgb('#40a080'), 255))
        self.assertEqual(rgba.getpixel((6, 1))[3], 0)
        self.assertEqual(rgba.getpixel((6, 6)), (*maqueta.hex_to_rgb('#d08040'), 255))
        self.assertTrue(np.isnan(values[0, 1]))

    def test_rgba_png_distinguishes_zero_negative_and_nodata_on_light_and_dark_backgrounds(self):
        project = default_project()
        project.update(stops=[-4, 0, 4], palette=['#204060', '#40a080', '#d08040'])
        values = np.array([[-4, 0, np.nan, np.inf, -np.inf],
                           [4, 0, -4, np.nan, 4]], dtype='float32')
        original = values.copy()
        mask = Image.fromarray(np.array([[255, 255, 255, 255, 255],
                                        [0, 128, 64, 255, 255]], dtype='uint8'))
        rgba = Image.fromarray(maqueta.colorize(values, project)).convert('RGBA')
        rgba.putalpha(maqueta.raster_alpha(values, mask))
        payload = io.BytesIO()
        rgba.save(payload, format='PNG')
        with Image.open(io.BytesIO(payload.getvalue())) as png:
            self.assertEqual(png.mode, 'RGBA')
            self.assertEqual(png.size, mask.size)
            np.testing.assert_array_equal(np.asarray(png)[..., 3],
                                          [[255, 255, 0, 0, 0], [0, 128, 64, 0, 255]])
            for color in ('#f0f5f8', '#102030'):
                background = Image.new('RGBA', png.size, color)
                result = Image.alpha_composite(background, png)
                for point in ((2, 0), (3, 0), (4, 0), (0, 1), (3, 1)):
                    self.assertEqual(result.getpixel(point), background.getpixel(point))
                self.assertEqual(result.getpixel((0, 0)), (*maqueta.hex_to_rgb('#204060'), 255))
                self.assertEqual(result.getpixel((1, 0)), (*maqueta.hex_to_rgb('#40a080'), 255))
        np.testing.assert_array_equal(values, original)

    def test_alpha_preserves_existing_finite_coast_pixels_and_rejects_incompatible_grid(self):
        project = default_project()
        values = np.array([[-4, 0, 4]], dtype='float32')
        mask = Image.fromarray(np.array([[64, 128, 255]], dtype='uint8'))
        np.testing.assert_array_equal(np.asarray(maqueta.raster_alpha(values, mask)), np.asarray(mask))
        # The compositor still uses the same RGB paste math at every finite
        # sample, including partial coast coverage and preexisting decoration.
        old = Image.new('RGBA', mask.size, (25, 60, 100, 36))
        new = old.copy()
        rgb = Image.fromarray(maqueta.colorize(values, project))
        old.paste(rgb, (0, 0), mask)
        new.paste(rgb, (0, 0), maqueta.raster_alpha(values, mask))
        self.assertEqual(old.tobytes(), new.tobytes())
        absent = np.full((1, 3), np.nan, dtype='float32')
        self.assertIsNone(maqueta.raster_alpha(absent, mask).getbbox())
        with self.assertRaises(ValueError):
            maqueta.raster_alpha(values, Image.new('L', (2, 1)))
        with self.assertRaises(ValueError):
            maqueta.raster_alpha(values, Image.new('RGB', (3, 1)))

    def test_mainland_missing_land_is_not_minimum_color_in_clipped_or_window_map(self):
        values = np.array([[0, np.nan], [-4, 4]], dtype='float32')
        original = values.copy()
        project = default_project()
        box = (-80, -3, -78, -1)
        project.update(source='local', bbox=list(box), show_galapagos=False,
                       show_provinces=False, cities=[], stops=[-4, 0, 4],
                       palette=['#204060', '#40a080', '#d08040'])
        shape = {'type': 'FeatureCollection', 'features': [rectangle(box)]}
        captured = {}
        full_layer = maqueta.full_layer

        def capture(canvas, layer, **kwargs):
            if kwargs.get('key') == 'map.main':
                captured['main'] = layer.copy()
            return full_layer(canvas, layer, **kwargs)

        # Isolate raster coverage from geographic border/glow decoration while
        # exercising the actual legacy compositor and its layer publication.
        for clip in (True, False):
            with self.subTest(clip_ecuador=clip), \
                    patch('maqueta.make_glow', side_effect=lambda mask, *a, **k: Image.new('RGBA', mask.size)), \
                    patch('maqueta.outline_layer', side_effect=lambda size, *a: Image.new('RGBA', size)), \
                    patch('maqueta.full_layer', side_effect=capture):
                project['clip_ecuador'] = clip
                before = copy.deepcopy(project)
                maqueta.compose_maqueta(project, values, shape, '2025-01-01', 0, 2)
                # Square source fits centrally in MAIN_W x MAIN_H.
                x = maqueta.MAIN_X
                y = maqueta.MAIN_Y + (maqueta.MAIN_H - maqueta.MAIN_W) // 2
                size = maqueta.MAIN_W
                tile = captured['main']
                self.assertEqual(tile.getpixel((x + size*3//4, y + size//4))[3], 0,
                                 'NoData inside land must not paint the minimum/zero color')
                for cx, cy, color in [(1, 1, '#40a080'), (1, 3, '#204060'), (3, 3, '#d08040')]:
                    self.assertEqual(tile.getpixel((x + size*cx//4, y + size*cy//4)),
                                     (*maqueta.hex_to_rgb(color), 255))
                self.assertEqual(project, before)
        np.testing.assert_array_equal(values, original)

    def test_two_region_two_date_fixture_has_native_signed_data_and_missing_inset(self):
        with tempfile.TemporaryDirectory() as folder:
            project, shape = two_region_fixture(folder)
            before = copy.deepcopy(project)
            records = []
            with patch('data.boundary', return_value=shape), \
                    patch('maqueta.boundary', return_value=shape), \
                    patch('data.map_dimensions', return_value=(65, 70)):
                for entry in project['entries']:
                    values, metadata = data.load_values(project, entry)
                    records.append((values, metadata))
                first = maqueta.load_galapagos_scene(project, '2025-01-01', 34, 37)
                absent = maqueta.load_galapagos_scene(project, '2025-01-03', 34, 37)
            self.assertEqual([r['date'] for r in project['entries']], ['2025-01-01', '2025-01-03'])
            self.assertEqual([m['band'] for _, m in records], [1, 2])
            self.assertEqual(first['valid_pixels'], 100)
            self.assertAlmostEqual(first['mean'], -2, delta=.01)
            self.assertEqual(first['max'], 0)
            self.assertTrue(np.isfinite(first['values']).any())
            self.assertTrue(np.isnan(first['values'][0, 0]))  # ocean
            self.assertEqual(absent['valid_pixels'], 0)
            self.assertIsNone(absent['mean'])
            self.assertIsNone(absent['max'])
            self.assertTrue(np.isnan(absent['values']).all())
            for values, metadata in records:
                stat = metadata['spatial_stats']
                self.assertEqual(stat['valid_pixels'], 300)
                self.assertEqual(stat['total_pixels'], 400)
                self.assertEqual(stat['coverage'], .75)
                self.assertEqual((stat['min'], stat['max']), (-4, 4))
                self.assertTrue((values == 0).any())
                self.assertTrue((values == -4).any())
                self.assertTrue(np.isnan(values).any())
            # Reuse the native summary contract: resizing/color/alpha must not
            # substitute display pixels for source statistics or modify inputs.
            with patch('endcard.province_boundaries', return_value=[]):
                native = SummaryAccumulator(project, shape)
                painted = SummaryAccumulator(project, shape)
            metadata_before = copy.deepcopy([m for _, m in records])
            for entry, (values, metadata) in zip(project['entries'], records):
                original = values.copy()
                stat = metadata['spatial_stats']
                native.observe(entry['date'], values, spatial_stats=stat)
                display = maqueta.resize_values(values, 130, 140, project['kind'])
                mask, _, _ = maqueta.build_mask_and_rings(shape, project['bbox'], 130, 140)
                rgba = Image.fromarray(maqueta.colorize(display, project)).convert('RGBA')
                rgba.putalpha(maqueta.raster_alpha(display, mask))
                painted.observe(entry['date'], display, spatial_stats=stat)
                np.testing.assert_array_equal(values, original)
            self.assertEqual(native.to_dict(), painted.to_dict())
            self.assertEqual([m for _, m in records], metadata_before)
            island_mask, _, _ = maqueta.build_mask_and_rings(
                shape, maqueta.GALAPAGOS_BOX, 34, 37, min_outer_area=maqueta.GAL_MIN_AREA_DEG2)
            self.assertIsNotNone(maqueta.raster_alpha(first['values'], island_mask).getbbox())
            self.assertIsNone(maqueta.raster_alpha(absent['values'], island_mask).getbbox())
            self.assertEqual(project, before)


def prepared_two_region_project(folder, *, bbox=None, crs='EPSG:4326'):
    """Capture this synthetic source through the established scientific APIs."""
    from visualization_ui import capture_snapshot
    from studio_science import generate_scientific_project
    source, shape = two_region_fixture(folder)
    # model.timeline confines local imports to STORE/imports. Preserve a
    # content-addressed synthetic original there; never relax that guard.
    import hashlib
    from model import STORE
    payload = Path(source['entries'][0]['path']).read_bytes()
    if crs != 'EPSG:4326':
        from rasterio.io import MemoryFile
        from rasterio.warp import transform_bounds
        with MemoryFile(payload) as raw, raw.open() as src:
            bounds = transform_bounds(src.crs, crs, *src.bounds)
            pixels = src.read()
            with MemoryFile() as projected:
                with projected.open(driver='GTiff', width=src.width, height=src.height, count=src.count,
                                    dtype=src.dtypes[0], crs=crs, nodata=src.nodata,
                                    transform=from_bounds(*bounds, src.width, src.height)) as dst:
                    dst.write(pixels)
                payload = projected.read()
    digest = hashlib.sha256(payload).hexdigest()
    imported = STORE / 'imports' / ('studio2-4b1-synthetic-' + digest + '.tif')
    imported.parent.mkdir(parents=True, exist_ok=True)
    if not imported.exists():
        with imported.open('xb') as stream:
            stream.write(payload)
    assert hashlib.sha256(imported.read_bytes()).hexdigest() == digest
    for entry in source['entries']:
        entry['path'] = str(imported)
    source['cadence'] = 'Por observación'
    if bbox is not None:
        source['bbox'] = list(bbox)

    def calculate(settings):
        accumulator = SummaryAccumulator(settings, shape)
        for row in settings['entries']:
            values, metadata = data.load_values(settings, row)
            accumulator.observe(row['date'], values, spatial_stats=metadata['spatial_stats'])
        return accumulator.to_dict()

    with patch('data.boundary', return_value=shape), \
            patch('endcard.province_boundaries', return_value=[]), \
            patch('data.map_dimensions', return_value=(65, 70)):
        snapshot = capture_snapshot(source, calculate)
    return generate_scientific_project(source, snapshot, {'id': 'custom', 'width': 320, 'height': 180}), shape


class MapTileTests(unittest.TestCase):
    def test_provincial_geometry_hash_records_actual_paint_or_visible_fallback(self):
        from studio_map_layers import MapLayerPainter
        from studio_science import _hash
        with tempfile.TemporaryDirectory() as folder:
            project, shape = prepared_two_region_project(folder)
            project['show_provinces'] = True
            provinces = {'features': [rectangle((-79.8, -2.8, -78.2, -1.2))]}
            with patch('data.boundary', return_value=shape), patch('maqueta.boundary', return_value=shape), \
                    patch('data.map_dimensions', return_value=(65, 70)):
                with patch('maqueta.adm1_boundary', return_value=provinces):
                    painter = MapLayerPainter(project, continent_size=(130, 140), galapagos_size=(68, 74))
                    pair = painter.render_observation(0)
                self.assertEqual(pair['layers']['continent']['grid']['province_geometry_sha256'], _hash(provinces))
                self.assertTrue(pair['layers']['continent']['provinces_painted'])
                self.assertFalse(pair['layers']['galapagos']['provinces_painted'])
                self.assertFalse(pair['warnings'])
                with patch('maqueta.adm1_boundary', side_effect=OSError('Synthetic unavailable geometry')):
                    painter = MapLayerPainter(project, continent_size=(130, 140), galapagos_size=(68, 74))
                    fallback = painter.render_observation(1)
                self.assertIsNone(fallback['layers']['continent']['grid']['province_geometry_sha256'])
                self.assertFalse(fallback['layers']['continent']['provinces_painted'])
                self.assertTrue(fallback['warnings'])
                self.assertFalse(fallback['layers']['galapagos']['borders_painted'])

    def test_projected_source_preserves_native_crs_and_selected_domain_without_changing_science(self):
        from studio_map_layers import MapLayerPainter
        with tempfile.TemporaryDirectory() as folder:
            box = (-80, -3, -78, -1)
            project, shape = prepared_two_region_project(folder, bbox=box, crs='EPSG:3857')
            original = copy.deepcopy(project)
            with patch('data.boundary', return_value=shape), patch('maqueta.boundary', return_value=shape), \
                    patch('data.map_dimensions', return_value=(65, 70)), \
                    patch('endcard.SummaryAccumulator', side_effect=AssertionError('Recalculated')):
                painter = MapLayerPainter(project, continent_size=(80, 80), galapagos_size=(68, 74))
                pair = painter.render_observation(0)
            self.assertEqual(pair['observation']['native_crs'], 'EPSG:3857')
            self.assertEqual(pair['layers']['continent']['grid']['bbox'], list(box))
            self.assertEqual(pair['layers']['continent']['grid']['name'], 'Región principal · bbox seleccionado')
            self.assertEqual(pair['layers']['continent']['grid']['crs'], 'EPSG:4326')
            self.assertEqual(pair['layers']['galapagos']['grid']['crs'], 'EPSG:4326')
            self.assertEqual(pair['rules']['statistics_domain'], 'primary bbox unchanged; inset is editorial')
            self.assertEqual(pair['layers']['galapagos']['state'], 'covered')
            self.assertEqual(project, original)
            self.assertIsNone(project['nodata'])  # embedded -9999 remains a source mask

    def test_source_revision_metadata_and_mid_load_changes_are_rejected(self):
        from studio_map_layers import MapLayerPainter
        with tempfile.TemporaryDirectory() as folder:
            project, shape = prepared_two_region_project(folder)
            with patch('data.boundary', return_value=shape), patch('maqueta.boundary', return_value=shape), \
                    patch('data.map_dimensions', return_value=(65, 70)):
                for field, value in [('band', 2), ('date', '2025-01-02')]:
                    changed = copy.deepcopy(project)
                    changed['entries'][0][field] = value
                    with self.subTest(field=field), self.assertRaises(ValueError):
                        MapLayerPainter(changed)
                changed = copy.deepcopy(project)
                next(iter(changed['studio']['calculations'].values()))['value'] = 999
                with self.assertRaises(ValueError):
                    MapLayerPainter(changed)
                painter = MapLayerPainter(project, continent_size=(130, 140), galapagos_size=(68, 74))
                digest = painter.render_observation(0)['observation']['source']['sha256']
                with patch('data.sha256', return_value='0'*64), self.assertRaises(ValueError):
                    painter.render_observation(0)
                with patch('data.sha256', side_effect=[digest, '0'*64]), self.assertRaises(ValueError):
                    painter.render_observation(0)
                values, metadata = data.load_values(project, project['entries'][0])
                with patch('data.load_values', return_value=(values, {**metadata, 'band': 2})), self.assertRaises(ValueError):
                    painter.render_observation(0)
                with patch('maqueta.boundary', return_value={'features': []}), self.assertRaises(ValueError):
                    painter.render_observation(0)
                with patch('maqueta.load_galapagos_scene', return_value=None), self.assertRaises(ValueError):
                    painter.render_observation(0)
                for invalid in (-1, 2, True, .5):
                    with self.subTest(index=invalid), self.assertRaises(ValueError):
                        painter.render_observation(invalid)

    def test_geographic_size_settings_and_returned_layer_records_are_isolated(self):
        from studio_map_layers import MapLayerPainter
        with tempfile.TemporaryDirectory() as folder:
            project, shape = prepared_two_region_project(folder)
            with patch('data.boundary', return_value=shape), patch('maqueta.boundary', return_value=shape), \
                    patch('data.map_dimensions', return_value=(65, 70)):
                for size in ([], (True, 140), (0, 1), (10000, 10000), (100, 20)):
                    with self.subTest(size=size), self.assertRaises(ValueError):
                        MapLayerPainter(project, continent_size=size)
                project['show_galapagos'] = False
                painter = MapLayerPainter(project, continent_size=(130, 140), galapagos_size=(68, 74))
                pair = painter.render_observation(0)
                self.assertEqual(pair['layers']['galapagos']['state'], 'disabled')
                self.assertIsNone(pair['layers']['galapagos']['image'].getbbox())
                specs = painter.layer_specs
                specs['continent']['bbox'][0] = 0
                settings = painter.cartographic_settings
                settings['palette'][0] = '#ffffff'
                pair['layers']['continent']['grid']['size'][0] = 1
                pair['observation']['source']['band'] = 99
                # Human settings changes after preparation cannot alter its
                # frozen source, geography, palette or scientific identities.
                project['bbox'][0] = -1
                project['palette'][0] = '#ffffff'
                unchanged = painter.render_observation(0)
                self.assertEqual(unchanged['layers']['continent']['grid']['bbox'], list(maqueta.MAIN_BOX))
                self.assertEqual(unchanged['layers']['continent']['image'].size, (130, 140))
                self.assertEqual(unchanged['observation']['source']['band'], 1)

    def test_categorical_inset_uses_known_codes_and_rejects_unmapped_island_code(self):
        from studio_map_layers import MapLayerPainter
        from studio_science import restored_snapshot, generate_scientific_project
        from visualization_ui import scientific_identity
        from studio_project import source_projection
        with tempfile.TemporaryDirectory() as folder:
            project, shape = prepared_two_region_project(folder)
            source = source_projection(project)
            source.update(kind='categorical', endcard_enabled=False, units='class', classes=[
                {'value': -4, 'label': 'Synthetic -4', 'color': '#204060'},
                {'value': 0, 'label': 'Synthetic zero', 'color': '#40a080'},
                {'value': 4, 'label': 'Synthetic four', 'color': '#d08040'}])
            snapshot = restored_snapshot(project)
            snapshot['results'] = {}  # no invented means/statistics of class codes
            snapshot['scientific_identity'] = scientific_identity(source)
            categorical = generate_scientific_project(source, snapshot, {'id': 'custom', 'width': 320, 'height': 180})
            # A source-only categorical revision has no CalculationResult. The
            # old attach_snapshot stores sources inside its result loop, so the
            # fixture explicitly supplies the existing canonical dataset field.
            # Do not change that older publication path in this extraction slice.
            revision = categorical['project_meta']['scientific_revision']
            categorical['studio']['datasets']['sources.' + revision] = copy.deepcopy(snapshot['source_records'])
            before = copy.deepcopy(categorical)
            with patch('data.boundary', return_value=shape), patch('maqueta.boundary', return_value=shape), \
                    patch('data.map_dimensions', return_value=(65, 70)):
                painter = MapLayerPainter(categorical, continent_size=(130, 140), galapagos_size=(68, 74))
                pair = painter.render_observation(0)
                gal = pair['layers']['galapagos']['image']
                xy = maqueta.projector(maqueta.GALAPAGOS_BOX, 68, 74)
                for lon, color in [(-91.3, '#204060'), (-90.7, '#40a080')]:
                    self.assertEqual(gal.getpixel(tuple(map(int, xy(lon, -.3)))), (*maqueta.hex_to_rgb(color), 255))
                with patch('maqueta.load_galapagos_scene', return_value={'values': np.full((74, 68), 99, dtype='float32')}):
                    with self.assertRaisesRegex(ValueError, 'clases'):
                        painter.render_observation(0)
            self.assertEqual(categorical, before)

    def test_shared_painters_are_consumed_by_legacy_and_layer_adapter(self):
        from studio_map_layers import MapLayerPainter
        with tempfile.TemporaryDirectory() as folder:
            project, shape = prepared_two_region_project(folder)
            with patch('data.boundary', return_value=shape), patch('maqueta.boundary', return_value=shape), \
                    patch('data.map_dimensions', return_value=(65, 70)):
                painter = MapLayerPainter(project)
                self.assertEqual(tuple(painter.layer_specs['continent']['size']), maqueta.main_map_size(project['bbox']))
                self.assertEqual(tuple(painter.layer_specs['galapagos']['size']),
                                 (maqueta.GAL_W_MAX, round(maqueta.GAL_W_MAX * maqueta.GAL_ASPECT)))
                values, _ = data.load_values(project, project['entries'][0])
                with patch('maqueta.paint_raster_layer', wraps=maqueta.paint_raster_layer) as raster, \
                        patch('maqueta.paint_map_outline', wraps=maqueta.paint_map_outline) as outlines:
                    maqueta.compose_maqueta(project, values, shape, '2025-01-01', 0, 2)
                    self.assertEqual((raster.call_count, outlines.call_count), (2, 2))
                    raster.reset_mock(); outlines.reset_mock()
                    painter.render_observation(0)
                    self.assertEqual((raster.call_count, outlines.call_count), (2, 2))

    def test_min_island_holes_and_signed_no_data_follow_existing_masks(self):
        from studio_map_layers import MapLayerPainter
        with tempfile.TemporaryDirectory() as folder:
            project, shape = prepared_two_region_project(folder)
            shape['features'].append(rectangle((-89.5, .5, -89.4, .6), 'Synthetic tiny island'))
            hole = rectangle((-91.2, -.5, -90.8, -.1))['geometry']['coordinates'][0]
            shape['features'][1]['geometry']['coordinates'].append(hole)
            values = np.zeros((370, 340), dtype='float32')
            xy = maqueta.projector(maqueta.GALAPAGOS_BOX, 340, 370)
            x, y = map(int, xy(-90.6, -.3))
            values[y-4:y+5, x-4:x+5] = np.nan
            with patch('data.boundary', return_value=shape), patch('maqueta.boundary', return_value=shape), \
                    patch('data.map_dimensions', return_value=(65, 70)), \
                    patch('maqueta.load_galapagos_scene', return_value={'values': values}):
                painter = MapLayerPainter(project, continent_size=(130, 140), galapagos_size=(340, 370))
                tile = painter.render_observation(0)['layers']['galapagos']
            self.assertEqual(tile['grid']['min_outer_area_deg2'], maqueta.GAL_MIN_AREA_DEG2)
            for point in ((-89.45, .55), (-91, -.3), (-90.6, -.3), (-92, 1)):
                self.assertEqual(tile['image'].getpixel(tuple(map(int, xy(*point))))[3], 0)
            self.assertEqual(tile['image'].getpixel(tuple(map(int, xy(-91.4, -.3))))[3], 255)
            # RGBA resampling must not reveal the minimum RGB placeholder at
            # an alpha transition (no black/minimum-colored NoData halo).
            stripe = maqueta.paint_raster_layer(np.array([[0, np.nan]], dtype='float32'), project, Image.new('L', (2, 1), 255))
            scaled = stripe.resize((16, 8), Image.Resampling.BILINEAR)
            expected = np.array(maqueta.hex_to_rgb('#40a080'))
            pixels = np.asarray(scaled)
            samples = pixels[pixels[..., 3] >= 64, :3].astype(int)
            self.assertLessEqual(int(np.max(np.abs(samples - expected))), 2)

    def test_two_tiles_share_observation_and_keep_geographic_grid_when_inset_is_missing(self):
        from studio_map_layers import MapLayerPainter
        with tempfile.TemporaryDirectory() as folder:
            project, shape = prepared_two_region_project(folder)
            original = copy.deepcopy(project)
            with patch('data.boundary', return_value=shape), patch('maqueta.boundary', return_value=shape), \
                    patch('data.map_dimensions', return_value=(65, 70)), \
                    patch('endcard.SummaryAccumulator', side_effect=AssertionError('New science')):
                painter = MapLayerPainter(project, continent_size=(130, 140), galapagos_size=(68, 74))
                first, last = painter.render_observation(0), painter.render_observation(1)
            self.assertEqual(first['observation']['date'], '2025-01-01')
            self.assertEqual(last['observation']['date'], '2025-01-03')
            self.assertEqual([first['observation']['source_index'], last['observation']['source_index']], [0, 1])
            self.assertEqual([first['observation']['source']['band'], last['observation']['source']['band']], [1, 2])
            self.assertEqual(first['observation']['scientific_revision'], project['project_meta']['scientific_revision'])
            self.assertEqual(first['observation']['source']['file'], project['entries'][0]['path'])
            for layer_id, size, box in [('continent', (130, 140), maqueta.MAIN_BOX),
                                         ('galapagos', (68, 74), maqueta.GALAPAGOS_BOX)]:
                a, b = first['layers'][layer_id], last['layers'][layer_id]
                self.assertEqual(a['grid'], b['grid'])
                self.assertEqual(tuple(a['grid']['bbox']), box)
                self.assertEqual(a['grid']['crs'], 'EPSG:4326')
                self.assertEqual(a['image'].size, size)
                self.assertEqual(b['image'].size, size)
                self.assertEqual(a['image'].mode, 'RGBA')
                self.assertEqual(a['grid']['id'], layer_id)
            self.assertEqual(first['layers']['galapagos']['state'], 'covered')
            self.assertEqual(last['layers']['galapagos']['state'], 'no_coverage')
            self.assertIsNone(last['layers']['galapagos']['image'].getbbox())
            self.assertGreater(first['layers']['galapagos']['data_pixels'], 0)
            self.assertEqual(last['layers']['galapagos']['data_pixels'], 0)
            self.assertEqual(project, original)

    def test_png_tiles_use_existing_colors_support_and_borders_without_poster_background(self):
        from studio_map_layers import MapLayerPainter
        with tempfile.TemporaryDirectory() as folder:
            project, shape = prepared_two_region_project(folder)
            with patch('data.boundary', return_value=shape), patch('maqueta.boundary', return_value=shape), \
                    patch('data.map_dimensions', return_value=(65, 70)):
                painter = MapLayerPainter(project, continent_size=(130, 140), galapagos_size=(68, 74))
                pair = painter.render_observation(0)
                values, _ = data.load_values(project, project['entries'][0])
            display = maqueta.resize_values(values, 130, 140, project['kind'])
            mask, rings, xy = maqueta.build_mask_and_rings(shape, project['bbox'], 130, 140)
            expected = Image.fromarray(maqueta.colorize(display, project)).convert('RGBA')
            expected.putalpha(maqueta.raster_alpha(display, mask))
            expected.alpha_composite(maqueta.outline_layer((130, 140), [(rings, maqueta.MAP_BORDER, 2.2)]))
            self.assertEqual(pair['layers']['continent']['image'].tobytes(), expected.tobytes())
            for layer in pair['layers'].values():
                stream = io.BytesIO()
                layer['image'].save(stream, format='PNG')
                with Image.open(io.BytesIO(stream.getvalue())) as decoded:
                    self.assertEqual(decoded.mode, 'RGBA')
                    self.assertEqual(decoded.size, layer['image'].size)
                    self.assertEqual(decoded.tobytes(), layer['image'].tobytes())
                    for color in ('#f0f5f8', '#102030'):
                        bg = Image.new('RGBA', decoded.size, color)
                        self.assertEqual(Image.alpha_composite(bg, decoded).getpixel((0, 0)), bg.getpixel((0, 0)))
            main = pair['layers']['continent']['image']
            for lon, lat, color in [(-79.5, -1.5, '#40a080'), (-79.5, -2.5, '#204060')]:
                self.assertEqual(main.getpixel(tuple(map(int, xy(lon, lat)))), (*maqueta.hex_to_rgb(color), 255))
            self.assertEqual(main.getpixel(tuple(map(int, xy(-78.5, -1.5))))[3], 0)


if __name__ == '__main__':
    unittest.main()
