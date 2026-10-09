"""Private bundles use real synthetic raster observations, not CFR PNG lists."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from test_studio_map_layers import prepared_two_region_project


class MapBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.project, self.shape = prepared_two_region_project(self.temp.name)
        self.before = copy.deepcopy(self.project)
        self.patches = [patch('studio_map_bundles.MEDIA_ROOT', Path(self.temp.name)/'media'),
            patch('data.boundary',return_value=self.shape),patch('maqueta.boundary',return_value=self.shape),
            patch('data.map_dimensions',return_value=(65,70)),
            patch('endcard.summary_for_project',side_effect=AssertionError('Bundle recalculated science'))]
        for p in self.patches: p.start()

    def tearDown(self):
        for p in reversed(self.patches): p.stop()
        self.temp.cleanup()

    def prepare(self, **kwargs):
        from studio_map_bundles import prepare_bundle
        return prepare_bundle(self.project,7/30,continent_size=(130,140),galapagos_size=(68,74),**kwargs)

    def test_lossless_bundle_has_two_visual_ids_one_calendar_and_no_document_publication(self):
        from studio_map_bundles import read_bundle
        record = self.prepare()
        manifest = read_bundle(record)
        self.assertEqual(manifest['version'],2)
        self.assertEqual(set(manifest['layers']),{'continent','galapagos'})
        self.assertEqual([(i['date'],i['start_frame'],i['end_frame']) for i in manifest['intervals']],
            [('2025-01-01',0,3),('2025-01-03',3,7)])
        self.assertEqual(manifest['observations'][1]['layers']['galapagos']['state'],'no_coverage')
        self.assertEqual(manifest['source_records'],self.project['studio']['datasets']['sources.'+manifest['scientific_revision']])
        self.assertEqual(self.project,self.before)
        self.assertEqual(len(list(Path(record['manifest_path']).parent.glob('observations/*/*.png'))),4)

    def test_manifest_tile_and_thumbnail_corruption_are_rejected(self):
        from studio_map_bundles import read_bundle
        for target in ('manifest.json','observations/000000/continent.png','thumbnail.png'):
            with self.subTest(target=target):
                record = self.prepare()
                path = Path(record['manifest_path']).parent/target
                path.write_bytes(path.read_bytes()+b'changed')
                with self.assertRaises(ValueError): read_bundle(record)

    def test_cancel_at_start_during_and_final_never_returns_ready_header(self):
        for stop in (0,1,2):
            calls=[]
            def progress(done,total,message): calls.append(done)
            def cancelled(): return (stop==0 or bool(calls) and calls[-1]>=stop)
            with self.subTest(stop=stop),self.assertRaises(InterruptedError):
                self.prepare(progress=progress,cancelled=cancelled)
        self.assertEqual(self.project,self.before)

    def test_limits_and_low_disk_fail_without_omitting_dates_or_overwriting_old_bundle(self):
        from studio_map_bundles import read_bundle
        record=self.prepare(); old=Path(record['manifest_path']).read_bytes()
        for name,limit in [('PNG_LIMIT',1),('MANIFEST_LIMIT',1),('BUNDLE_LIMIT',1)]:
            with self.subTest(name=name),patch('studio_map_bundles.'+name,limit),self.assertRaises(ValueError): self.prepare()
        with patch('studio_map_bundles.shutil.disk_usage',return_value=type('Disk',(),{'free':0})()),self.assertRaises(ValueError): self.prepare()
        self.assertEqual(Path(record['manifest_path']).read_bytes(),old)
        read_bundle(record); self.assertEqual(self.project,self.before)

    def reseal(self, record, change):
        from studio_map_bundles import _bytes, _digest
        modified=copy.deepcopy(record);path=Path(record['manifest_path'])
        old=path.read_bytes();manifest=json.loads(old);change(manifest)
        content=_bytes(manifest);path.write_bytes(content)
        modified['manifest_sha256']=_digest(content);modified['bytes']+=len(content)-len(old)
        return modified

    def test_resealed_traversal_grid_calendar_and_malformed_json_are_rejected(self):
        from studio_map_bundles import read_bundle
        changes=[lambda m:m['observations'][0]['layers']['continent'].update(path='../outside.png'),
            lambda m:m['layers']['continent'].update(transform=[0]*9),
            lambda m:m['intervals'][1].update(date='2025-01-02'),
            lambda m:m.update(observations=[]),lambda m:m.update(layers=None)]
        for change in changes:
            with self.subTest(change=change),self.assertRaises(ValueError): read_bundle(self.reseal(self.prepare(),change))

    def test_missing_wrong_mode_and_false_no_coverage_tiles_are_rejected(self):
        from studio_map_bundles import read_bundle, _digest
        from PIL import Image
        record=self.prepare();path=Path(record['manifest_path']).parent/'observations/000000/continent.png'
        path.rename(path.with_suffix('.preserved'))
        with self.assertRaises(ValueError): read_bundle(record)
        for mode in ('RGB','RGBA'):
            with self.subTest(mode=mode):
                record=self.prepare();path=Path(record['manifest_path']).parent/'observations/000001/galapagos.png'
                with Image.new(mode,(68,74),'white') as image: image.save(path,format='PNG')
                content=path.read_bytes()
                def changed(m):
                    item=m['observations'][1]['layers']['galapagos'];item['sha256']=_digest(content);item['bytes']=len(content)
                changed_record=self.reseal(record,changed)
                # Update total bytes too: rejection must come from mode/alpha, not only the size guard.
                manifest=json.loads(Path(record['manifest_path']).read_bytes())
                changed_record['bytes']=len(Path(record['manifest_path']).read_bytes())+manifest['thumbnail']['bytes']+sum(
                    item['bytes'] for obs in manifest['observations'] for item in obs['layers'].values())
                with self.assertRaises(ValueError): read_bundle(changed_record)

    def test_bad_source_band_date_and_duration_fail_before_a_ready_bundle(self):
        from studio_map_bundles import prepare_bundle
        for field,value in [('band',2),('date','2025-01-02')]:
            bad=copy.deepcopy(self.project);bad['entries'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError): prepare_bundle(bad,7/30)
        for duration in (True,float('nan'),float('inf'),0,-1,7201):
            with self.subTest(duration=duration),self.assertRaises(ValueError): prepare_bundle(self.project,duration)
        self.assertEqual(self.project,self.before)

    def test_cancel_at_final_seal_preserves_private_files_without_returning_header(self):
        final=[]
        def progress(done,total,message):
            if 'sellando' in message: final.append(message)
        with self.assertRaises(InterruptedError): self.prepare(progress=progress,cancelled=lambda:bool(final))
        self.assertTrue(list((Path(self.temp.name)/'media/map-bundles').glob('*/manifest.json')))
        self.assertEqual(self.project,self.before)

    def test_png_bytes_preserve_painter_rgba_and_projected_native_crs(self):
        from studio_map_bundles import prepare_bundle,read_bundle
        from studio_map_layers import MapLayerPainter
        from PIL import Image
        project,_=prepared_two_region_project(self.temp.name,crs='EPSG:3857')
        record=prepare_bundle(project,7/30,continent_size=(130,140),galapagos_size=(68,74))
        manifest=read_bundle(record)
        painter=MapLayerPainter(project,continent_size=(130,140),galapagos_size=(68,74))
        for index,obs in enumerate(manifest['observations']):
            self.assertEqual(obs['native_crs'],'EPSG:3857')
            pair=painter.render_observation(index)
            try:
                for lid,tile in pair['layers'].items():
                    with Image.open(Path(record['manifest_path']).parent/obs['layers'][lid]['path']) as image:
                        self.assertEqual(image.tobytes(),tile['image'].tobytes())
            finally:
                for tile in pair['layers'].values():tile['image'].close()

    def test_resolved_symlink_cannot_escape_bundle_directory(self):
        import os
        from studio_map_bundles import read_bundle
        record=self.prepare();path=Path(record['manifest_path']).parent/'observations/000000/continent.png'
        outside=Path(self.temp.name)/'outside-preserved.png';outside.write_bytes(path.read_bytes())
        path.rename(path.with_suffix('.preserved'))
        try:os.symlink(outside,path)
        except OSError as error:self.skipTest('Windows no permite crear enlace de prueba: '+str(error))
        with self.assertRaises(ValueError):read_bundle(record)

    def test_bounded_32_observation_sample_keeps_calendar_and_pngs_per_observation(self):
        import datetime as dt
        from studio_project import source_projection
        from studio_science import generate_scientific_project
        from visualization_ui import capture_snapshot
        from endcard import SummaryAccumulator
        import data
        from studio_map_bundles import prepare_bundle,read_bundle
        source=source_projection(self.project)
        original=source['entries']
        source['entries']=[{**original[i%2],'date':str(dt.date(2025,1,1)+dt.timedelta(days=i*2))} for i in range(32)]
        source.update(start=source['entries'][0]['date'],end=source['entries'][-1]['date'],duration=96/30)
        def calculate(settings):
            with patch('endcard.province_boundaries',return_value=[]):acc=SummaryAccumulator(settings,self.shape)
            for row in settings['entries']:
                values,metadata=data.load_values(settings,row);acc.observe(row['date'],values,spatial_stats=metadata['spatial_stats'])
            return acc.to_dict()
        snapshot=capture_snapshot(source,calculate)
        project=generate_scientific_project(source,snapshot,{'id':'custom','width':320,'height':180})
        progress=[]
        record=prepare_bundle(project,96/30,continent_size=(130,140),galapagos_size=(68,74),
            progress=lambda done,total,message:progress.append((done,total)))
        manifest=read_bundle(record)
        self.assertEqual(len(manifest['observations']),32)
        self.assertEqual(manifest['total_frames'],96)
        self.assertEqual(len(list(Path(record['manifest_path']).parent.glob('observations/*/*.png'))),64)
        self.assertEqual(progress[-1],(32,32))
        self.assertEqual([i['date'] for i in manifest['intervals']],[e['date'] for e in source['entries']])
        self.assertLess(record['bytes'],1024*1024)


class MapBundleWorkerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.project,self.shape=prepared_two_region_project(self.temp.name)
        self.before=copy.deepcopy(self.project)
        self.patch=patch('studio_map_bundles.MEDIA_ROOT',Path(self.temp.name)/'media');self.patch.start()

    def tearDown(self):self.patch.stop();self.temp.cleanup()

    def job(self,name):
        from jobs import write_json
        job=Path(self.temp.name)/name;job.mkdir()
        write_json(job/'request.json',{'project':self.project,'duration':7/30,'representation':'rgba_observation_bundle',
            'layer_sizes':{'continent_size':[130,140],'galapagos_size':[68,74]}})
        return job

    def execute(self,job):
        from studio_map_jobs import execute
        with patch('data.boundary',return_value=self.shape),patch('maqueta.boundary',return_value=self.shape),\
                patch('data.map_dimensions',return_value=(65,70)),\
                patch('render.compose',side_effect=AssertionError('RGBA used opaque compositor')),\
                patch('endcard.summary_for_project',side_effect=AssertionError('RGBA recalculated science')):
            execute(job,root=self.temp.name)

    def test_worker_complete_resource_and_status_hashes_are_verified_without_publication(self):
        from studio_map_jobs import read_bundle_resource
        from jobs import read_json,write_json
        job=self.job('ready');self.execute(job)
        self.assertEqual(read_json(job/'status.json')['state'],'complete')
        record=read_bundle_resource(job,root=self.temp.name)
        self.assertFalse((job/'resource.json').exists())
        self.assertEqual(self.project,self.before)
        write_json(job/'bundle-resource.json',{**record,'duration':1})
        with self.assertRaises(ValueError):read_bundle_resource(job,root=self.temp.name)

    def test_worker_cancellation_at_start_during_and_after_header_never_offers_resource(self):
        from studio_map_jobs import read_bundle_resource
        from jobs import read_json,write_json
        for stage in ('start','during','header'):
            job=self.job(stage)
            if stage=='start':(job/'cancel.request').touch()
            def writing(path,value):
                write_json(path,value)
                if (stage=='during' and Path(path).name=='status.json' and value.get('progress',0)>=.5
                        or stage=='header' and Path(path).name=='bundle-resource.json'):
                    (job/'cancel.request').touch()
            with self.subTest(stage=stage),patch('studio_map_jobs.write_json',side_effect=writing):self.execute(job)
            self.assertEqual(read_json(job/'status.json')['state'],'cancelled')
            with self.assertRaises(ValueError):read_bundle_resource(job,root=self.temp.name)
        self.assertEqual(self.project,self.before)

    def test_worker_changed_source_and_unknown_representation_fail_visibly(self):
        from jobs import read_json,write_json
        from studio_map_jobs import read_bundle_resource
        for change in ('band','representation'):
            job=self.job(change);request=read_json(job/'request.json')
            if change=='band':request['project']['entries'][0]['band']=2
            else:request['representation']='unknown'
            write_json(job/'request.json',request);self.execute(job)
            self.assertEqual(read_json(job/'status.json')['state'],'failed')
            with self.assertRaises(ValueError):read_bundle_resource(job,root=self.temp.name)
        self.assertEqual(self.project,self.before)

    def test_real_process_prepares_private_v2_and_can_cancel_without_active_publication(self):
        import time
        from storyboard import MEDIA_ROOT
        from studio_map_jobs import start_map_job,map_status,read_bundle_resource
        with patch('studio_map_bundles.MEDIA_ROOT',MEDIA_ROOT):
            for cancel in (False,True):
                job=start_map_job(self.project,7/30,representation='rgba_observation_bundle',
                    layer_sizes={'continent_size':[130,140],'galapagos_size':[68,74]})
                if cancel:(job/'cancel.request').touch()
                end=time.monotonic()+45
                while time.monotonic()<end:
                    state=map_status(job)
                    if state['state'] not in ('queued','running'):break
                    time.sleep(.1)
                self.assertEqual(state['state'],'cancelled' if cancel else 'complete',state)
                if cancel:
                    with self.assertRaises(ValueError):read_bundle_resource(job)
                else:
                    record=read_bundle_resource(job);self.assertEqual(record['representation'],'rgba_observation_bundle')
                self.assertEqual(self.project,self.before)


if __name__=='__main__':unittest.main()
