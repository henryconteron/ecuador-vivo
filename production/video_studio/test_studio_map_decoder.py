"""Private lazy RGBA adapter, with calendar and cache bounded independently."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
from test_studio_map_layers import prepared_two_region_project


class MapDecoderTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.project,self.shape=prepared_two_region_project(self.temp.name)
        self.before=copy.deepcopy(self.project)
        self.patches=[patch('studio_map_bundles.MEDIA_ROOT',Path(self.temp.name)/'media'),
            patch('data.boundary',return_value=self.shape),patch('maqueta.boundary',return_value=self.shape),
            patch('data.map_dimensions',return_value=(65,70))]
        for p in self.patches:p.start()
        from studio_map_bundles import prepare_bundle
        self.record=prepare_bundle(self.project,7/30,continent_size=(130,140),galapagos_size=(68,74))

    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        self.temp.cleanup()

    @staticmethod
    def release(context):
        for image in context['images'].values():image.close()

    def test_constructor_does_not_decode_observation_tiles_and_at_has_one_shared_date(self):
        from studio_map_bundles import BundleFrames,_decode_png
        with patch('studio_map_bundles._decode_png',wraps=_decode_png) as decode, \
                patch('data.load_values',side_effect=AssertionError('Raster IO during decode')), \
                patch('maqueta.load_galapagos_scene',side_effect=AssertionError('Inset IO during decode')):
            with BundleFrames(self.record) as frames:
                self.assertEqual(decode.call_count,1)  # thumbnail only
                self.assertEqual(frames.cache.bytes_used,0)
                for frame,date,index in [(0,'2025-01-01',0),(2,'2025-01-01',0),(3,'2025-01-03',1),(6,'2025-01-03',1)]:
                    context=frames.at(frame)
                    self.assertEqual(context['observation']['date'],date)
                    self.assertEqual(context['observation']['source_index'],index)
                    self.assertEqual(set(context['images']),{'continent','galapagos'})
                    self.release(context)
        self.assertEqual(self.project,self.before)

    def test_lossless_pixels_and_absent_inset_survive_forward_and_backward_seek(self):
        from studio_map_bundles import BundleFrames
        with BundleFrames(self.record) as frames:
            for frame,index in [(6,1),(0,0),(3,1),(2,0)]:
                context=frames.at(frame)
                for lid,image in context['images'].items():
                    path=Path(self.record['manifest_path']).parent/frames.manifest['observations'][index]['layers'][lid]['path']
                    with Image.open(path) as expected:self.assertEqual(image.tobytes(),expected.tobytes())
                    self.assertEqual(image.mode,'RGBA')
                if index==1:self.assertEqual(context['images']['galapagos'].getchannel('A').getextrema(),(0,0))
                self.release(context)

    def test_weighted_lru_evicts_and_returned_images_do_not_mutate_cache(self):
        from studio_map_bundles import BundleFrames,_decode_png
        budget=130*140*4+512
        with BundleFrames(self.record,cache_bytes=budget) as frames,patch('studio_map_bundles._decode_png',wraps=_decode_png) as decode:
            original=frames.at(0,('continent',));pixels=original['images']['continent'].tobytes()
            original['images']['continent'].paste('white',(0,0,130,140));self.release(original)
            again=frames.at(0,('continent',));self.assertEqual(again['images']['continent'].tobytes(),pixels);self.release(again)
            self.assertEqual(decode.call_count,1)
            for frame in (3,0,6,2):
                self.release(frames.at(frame,('continent',)))
                self.assertLessEqual(frames.cache.bytes_used,budget)
            self.assertEqual(decode.call_count,5)
        self.assertEqual(frames.cache.bytes_used,0)

    def test_warm_cache_does_not_hide_corrupted_missing_tile_or_manifest(self):
        from studio_map_bundles import BundleFrames
        for target in ('observations/000000/continent.png','manifest.json'):
            with self.subTest(target=target),BundleFrames(self.record) as frames:
                self.release(frames.at(0))
                path=Path(self.record['manifest_path']).parent/target;old=path.read_bytes()
                path.write_bytes(old+b'changed')
                with self.assertRaises(ValueError):frames.at(0)
                path.write_bytes(old)
        with BundleFrames(self.record) as frames:
            self.release(frames.at(0));path=Path(self.record['manifest_path']).parent/'observations/000000/continent.png'
            path.rename(path.with_suffix('.preserved'))
            with self.assertRaises(ValueError):frames.at(0)

    def test_assetframes_accepts_private_bundle_without_relaxing_legacy_media_path(self):
        from studio_media import AssetFrames,import_asset
        import io
        stream=io.BytesIO()
        with Image.new('RGBA',(4,3),'red') as image:image.save(stream,format='PNG')
        ordinary=import_asset(stream.getvalue(),'decoder-test.png')
        with AssetFrames({'map.fixture':self.record,'ordinary':ordinary}) as assets:
            self.assertEqual(set(assets.at(0)),{'ordinary'})
            context=assets.map_at('map.fixture',3,cursor_id='instance.one')
            self.assertEqual(context['observation']['date'],'2025-01-03')
            self.assertEqual(context['images']['galapagos'].getchannel('A').getextrema(),(0,0))
            assets.map_at('map.fixture',0,cursor_id='instance.two')
            self.assertEqual(len(assets.map_products),2)
            self.assertLessEqual(assets.map_cache.bytes_used,32*1024*1024)
            with patch('studio_media.TOTAL_PIXEL_BUDGET',10),self.assertRaises(ValueError):assets.map_at('map.fixture',0)
        self.assertEqual(assets.map_products,{})
        self.assertEqual(assets.map_cache.bytes_used,0)
        malformed={**ordinary,'path':self.record['manifest_path']}
        with self.assertRaises(ValueError):AssetFrames({'ordinary':malformed})

    def test_invalid_source_frame_layer_and_budget_are_rejected(self):
        from studio_map_bundles import BundleFrames
        for budget in (-1,True,320_000_001):
            with self.subTest(budget=budget),self.assertRaises(ValueError):BundleFrames(self.record,cache_bytes=budget)
        with BundleFrames(self.record) as frames:
            for frame in (-1,True,1.0,7):
                with self.subTest(frame=frame),self.assertRaises(ValueError):frames.at(frame)
            for layers in (('unknown',),('continent','continent'),(),None):
                with self.subTest(layers=layers),self.assertRaises(ValueError):frames.at(0,layers)

    def test_32_observation_series_does_not_accumulate_decoded_frames(self):
        import datetime as dt
        from studio_project import source_projection
        from studio_science import generate_scientific_project
        from visualization_ui import capture_snapshot
        from endcard import SummaryAccumulator
        import data
        from studio_map_bundles import prepare_bundle,BundleFrames,_decode_png
        source=source_projection(self.project);original=source['entries']
        source['entries']=[{**original[i%2],'date':str(dt.date(2025,1,1)+dt.timedelta(days=2*i))} for i in range(32)]
        source.update(start=source['entries'][0]['date'],end=source['entries'][-1]['date'],duration=96/30)
        def calculate(settings):
            with patch('endcard.province_boundaries',return_value=[]):acc=SummaryAccumulator(settings,self.shape)
            for row in settings['entries']:
                values,metadata=data.load_values(settings,row);acc.observe(row['date'],values,spatial_stats=metadata['spatial_stats'])
            return acc.to_dict()
        project=generate_scientific_project(source,capture_snapshot(source,calculate),{'id':'custom','width':320,'height':180})
        record=prepare_bundle(project,96/30,continent_size=(130,140),galapagos_size=(68,74))
        budget=(130*140+68*74)*4+1024
        with patch('studio_map_bundles._decode_png',wraps=_decode_png) as decode,BundleFrames(record,cache_bytes=budget) as frames:
            self.assertEqual(decode.call_count,1)
            with patch('data.load_values',side_effect=AssertionError('Decode recalculated science')):
                for index in list(range(32))+list(reversed(range(32))):
                    context=frames.at(index*3)
                    self.assertEqual(context['observation']['date'],source['entries'][index]['date'])
                    self.release(context)
                    self.assertLessEqual(frames.cache.bytes_used,budget)
            self.assertLessEqual(len(frames.cache._lru.entries),2)

    def test_private_decoder_does_not_authorize_unrendered_document_publication(self):
        from studio_timeline import PreparedTimeline
        candidate=copy.deepcopy(self.project);candidate['studio']['media']['private.bundle']=self.record
        with self.assertRaisesRegex(ValueError,'privados'):PreparedTimeline(candidate)
        self.assertEqual(self.project,self.before)


if __name__=='__main__':unittest.main()
