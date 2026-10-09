"""4b.3b: structured maps use one verified observation and shared CFR clock."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
from test_studio_map_layers import prepared_two_region_project


class TemporalLayersTests(unittest.TestCase):
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

    def document(self, *, loop=False,start=0,end=7,length=15):
        from studio_model import Element,Scene
        project=copy.deepcopy(self.project)
        elements=[]
        for channel,kind,box in [('continent','map',(0,0,130,140)),('galapagos','map',(145,0,68,74)),
                ('date','text',(140,80,160,32)),('legend_static','legend',(0,140,320,40))]:
            elements.append(Element(id=channel,type=kind,transform=dict(zip(('x','y','width','height'),box)),
                style={'font_size':16} if kind=='text' else {'fit':'contain'},
                temporal_binding={'instance_id':'instance.one','channel':channel}).to_dict())
        scene=Scene(id='scene.layers',duration=length/30,elements=elements,map_instances={'instance.one':{
            'asset_id':'map.fixture','trim_in_frame':start,'trim_out_frame':end,'loop':loop}}).to_dict()
        prefix=Scene(id='scene.prefix',duration=2/30).to_dict()
        project['studio']['media']['map.fixture']=copy.deepcopy(self.record)
        project['studio']['scenes']+=[prefix,scene]
        project['studio']['timeline']=[prefix['id'],scene['id']]
        return project

    def test_same_instance_seek_trim_loop_hold_and_multiple_instances(self):
        from studio_media import AssetFrames
        from studio_temporal import calendar_at,instance_frame
        from studio_timeline import PreparedTimeline
        for loop in (False,True):
            project=self.document(loop=loop,start=1,end=5)
            scene=project['studio']['scenes'][-1];clock=scene['map_instances']['instance.one']
            prepared=PreparedTimeline(project)
            with AssetFrames(project['studio']['media']) as assets,patch('data.load_values',side_effect=AssertionError('Science during seek')):
                for frame in (0,2,3,4,12,1,14):
                    expected=1+(frame%4 if loop else min(frame,3))
                    self.assertEqual(instance_frame(self.record,clock,frame),expected)
                    product=assets.at(frame/30,scene['elements'],map_instances=scene['map_instances'])
                    contexts=[product['temporal.'+e['id']] for e in scene['elements']]
                    self.assertTrue(all(c==contexts[0] for c in contexts))
                    self.assertEqual(contexts[0]['date'],'2025-01-01' if expected<3 else '2025-01-03')
                    self.assertTrue(all(v['source_frame']==expected for v in calendar_at(project,frame+2)))
                    with prepared.frame_at(frame+2,assets=assets):pass
                    self.assertNotIn('text',scene['elements'][2]['style'])
            # Two independent instances may use the same scientific resource.
            scene['map_instances']['instance.two']={**clock,'trim_in_frame':3,'trim_out_frame':7,'loop':False}
            for e in list(scene['elements']):
                duplicate=copy.deepcopy(e);duplicate['id']='second.'+e['id'];duplicate['temporal_binding']['instance_id']='instance.two'
                scene['elements'].append(duplicate)
            PreparedTimeline(project)
            with AssetFrames(project['studio']['media']) as assets:
                product=assets.at(0,scene['elements'],map_instances=scene['map_instances'])
                self.assertEqual(product['temporal.continent']['date'],'2025-01-01')
                self.assertEqual(product['temporal.second.continent']['date'],'2025-01-03')
        self.assertEqual(self.project,self.before)

    def test_absent_inset_is_transparent_and_date_content_is_protected(self):
        from studio_timeline import PreparedTimeline,frame_at
        from studio_model import validate_scene
        project=self.document();prepared=PreparedTimeline(project)
        with patch('data.load_values',side_effect=AssertionError('Scientific IO')),patch('endcard.SummaryAccumulator',side_effect=AssertionError('Calculation')):
            with prepared.frame_at(5) as image,frame_at(project,5) as direct:
                self.assertEqual(image.tobytes(),direct.tobytes())
                background=image.getpixel((310,0))
                self.assertEqual(image.crop((145,0,213,74)).getextrema(),tuple((v,v) for v in background))
                row=next(r for r in image.info['visual_scene'].items if r['id']=='date')
                self.assertEqual(row['text'],'2025-01-03');self.assertFalse(row['content_editable'])
        scene=copy.deepcopy(project['studio']['scenes'][-1]);scene['elements'][2]['style']['text']='invented date'
        with self.assertRaises(ValueError):validate_scene(scene)

    def test_receipt_event_spans_match_every_frame_and_global_offset(self):
        from studio_temporal import calendar_receipt,calendar_at
        from studio_editing import timeline_rows
        for loop in (False,True):
            project=self.document(start=1,end=5,loop=loop,length=15)
            receipt=calendar_receipt(project,timeline_rows(project['studio']))[0]
            self.assertEqual(len(receipt['bindings']),4)
            self.assertEqual(receipt['manifest_sha256'],self.record['manifest_sha256'])
            self.assertEqual(receipt['intervals'][0]['start_frame'],2)
            for frame in range(2,17):
                value=calendar_at(project,frame)[0]
                span=next(s for s in receipt['intervals'] if s['start_frame']<=frame<s['end_frame'])
                self.assertEqual(value['date'],span['date'])
                self.assertEqual(value['source_frame'],span['source_frame']+(frame-span['start_frame'])*span['source_step'])

    def test_invalid_unbound_or_unauthorized_documents_never_publish(self):
        from studio_timeline import PreparedTimeline,export_movie
        candidates=[]
        p=self.document();p['studio']['scenes'][-1]['map_instances']['instance.one']['trim_out_frame']=8;candidates.append(p)
        p=self.document();p['studio']['datasets'][self.record['source_dataset']][0]['band']=2;candidates.append(p)
        p=self.document();p['studio']['scenes'][-1]['elements'][2]['visible']=False;candidates.append(p)
        p=self.document();p['studio']['scenes'][-1]['elements'].pop();candidates.append(p)
        p=self.document();p['studio']['scenes'][-1]['elements'][0]['temporal_binding']['instance_id']='unknown';candidates.append(p)
        p=self.document();p['studio']['scenes'][-1]['elements'][0]['temporal_binding']=None;candidates.append(p)
        p=self.document();p['studio']['scenes'][-1]['elements'][0]['style']['asset_id']='map.fixture';candidates.append(p)
        for index,p in enumerate(candidates):
            with self.subTest(index=index),self.assertRaises(ValueError):PreparedTimeline(p)
            target=Path(self.temp.name)/('invalid'+str(index))/'movie.mp4'
            with self.assertRaises(ValueError):export_movie(p,target)
            self.assertFalse(target.parent.exists())

    def test_save_reopen_recovery_preserve_bindings_revisions_and_hashes(self):
        from studio_recovery import save_snapshot,recover_snapshot
        from studio_project import replace_document,validate_document
        p=self.document(loop=True,start=1,end=5);path=Path(self.temp.name)/'draft.json'
        save_snapshot(path,p);save_snapshot(path,p)
        reopened,previous=recover_snapshot(path);self.assertFalse(previous)
        copied=replace_document({},validate_document(reopened))
        self.assertEqual(copied['studio'],p['studio'])
        self.assertEqual(copied['project_meta']['scientific_revision'],p['project_meta']['scientific_revision'])
        path.write_text('{invalid',encoding='utf-8')
        recovered,previous=recover_snapshot(path);self.assertTrue(previous)
        self.assertEqual(recovered['studio'],p['studio'])

    def test_warm_preview_canvas_and_thumbnail_cannot_hide_changed_png(self):
        from studio_timeline import PreparedTimeline
        from studio_media import AssetFrames
        from studio_cache import StudioPreviewCache
        project=self.document();prepared=PreparedTimeline(project);cache=StudioPreviewCache()
        with AssetFrames(project['studio']['media']) as assets:
            view=cache.for_timeline(prepared,assets)
            view.preview(2);view.canvas('scene.layers',lambda *args:{'cached':True});view.thumbnails()
            path=Path(self.record['manifest_path']).parent/'observations/000000/continent.png'
            path.write_bytes(path.read_bytes()+b'changed')
            for consume in (lambda:view.preview(2),lambda:view.canvas('scene.layers',None),view.thumbnails):
                with self.assertRaises(ValueError):consume()
        cache.clear()

    def test_old_private_bundle_remains_readable_but_needs_explicit_legend_preparation(self):
        from studio_map_bundles import read_bundle,_bytes,_digest,BundleFrames
        from studio_timeline import PreparedTimeline
        manifest=read_bundle(self.record);aux=manifest.pop('auxiliaries')
        old=_bytes(manifest);path=Path(self.record['manifest_path']);path.write_bytes(old)
        record={**self.record,'manifest_sha256':_digest(old),'bytes':len(old)+manifest['thumbnail']['bytes']+
                sum(item['bytes'] for obs in manifest['observations'] for item in obs['layers'].values())}
        self.assertNotIn('auxiliaries',read_bundle(record))
        with BundleFrames(record) as decoder:
            product=decoder.at(0)
            for image in product['images'].values():image.close()
        project=self.document();project['studio']['media']['map.fixture']=record
        with self.assertRaisesRegex(ValueError,'leyenda'):PreparedTimeline(project)

    def test_atomic_duplication_clipboard_scene_and_undo_preserve_clocks(self):
        from studio_editing import duplicate_elements,edit_scene
        from studio_timeline import PreparedTimeline
        from studio_workspace import WorkspaceSession
        project=self.document(loop=True,start=1,end=5);original=project['studio']['scenes'][-1]
        single=duplicate_elements(project,original['id'],['galapagos'])
        self.assertEqual(len(single['studio']['scenes'][-1]['map_instances']),1);PreparedTimeline(single)
        pair=duplicate_elements(project,original['id'],['continent','galapagos'])
        scene=pair['studio']['scenes'][-1];self.assertEqual(len(scene['map_instances']),2)
        self.assertEqual(len(scene['elements']),8);PreparedTimeline(pair)
        duplicated=edit_scene(project,'duplicate',original['id']);PreparedTimeline(duplicated)
        self.assertNotEqual(set(duplicated['studio']['scenes'][-1]['map_instances']),set(original['map_instances']))
        state={};session=WorkspaceSession(state,'layers',project,store=Path(self.temp.name)/'workspace')
        state['layers_selected']=original['id']
        session.dispatch({'action':'copy','version':session.version,'scene':session.selected,'ids':['continent','galapagos']})
        self.assertEqual(len(state['layers_clipboard']),4)
        session.dispatch({'action':'select','version':session.version,'scene':session.selected,'id':'scene.prefix'})
        session.dispatch({'action':'paste','version':session.version,'scene':session.selected,
            'elements':state['layers_clipboard'],'map_instances':state['layers_clipboard_maps']})
        PreparedTimeline(session.project)
        self.assertEqual(len(session.project['studio']['scenes'][-2]['map_instances']),1)
        session.dispatch({'action':'undo','version':session.version,'scene':session.selected})
        self.assertEqual(session.project['studio'],project['studio'])
        self.assertEqual(project,self.document(loop=True,start=1,end=5))

    def test_active_map_products_release_previous_scene_instances_within_budget(self):
        from studio_media import AssetFrames
        project=self.document();scene=project['studio']['scenes'][-1]
        with AssetFrames(project['studio']['media']) as assets:
            assets.at(0,scene['elements'],map_instances=scene['map_instances'])
            budget=assets._map_pixels()
            for index in range(5):
                iid='instance.scene'+str(index)
                elements=copy.deepcopy(scene['elements'])
                for e in elements:e['temporal_binding']['instance_id']=iid
                clocks={iid:scene['map_instances']['instance.one']}
                with patch('studio_media.TOTAL_PIXEL_BUDGET',budget):assets.at(index/30,elements,map_instances=clocks)
                self.assertEqual(len(assets.map_products),1);self.assertEqual(assets._map_pixels(),budget)

    def test_real_mp4_and_receipt_use_same_preview_frames_without_scientific_io(self):
        import imageio_ffmpeg
        import numpy as np
        from studio_timeline import PreparedTimeline,export_movie
        project=self.document(loop=True,start=1,end=5,length=10);prepared=PreparedTimeline(project)
        target=Path(self.temp.name)/'export'/'movie.mp4'
        with patch('data.load_values',side_effect=AssertionError('Export calculated science')),patch('endcard.SummaryAccumulator',side_effect=AssertionError('Export stats')):
            receipt=export_movie(project,target)
            reader=imageio_ffmpeg.read_frames(str(target),pix_fmt='rgb24');metadata=next(reader)
            self.assertEqual(metadata['size'],(320,180))
            count=0
            try:
                for count,content in enumerate(reader,1):
                    with prepared.frame_at(count-1) as expected:
                        actual=np.frombuffer(content,dtype='uint8').reshape(180,320,3)
                        difference=np.abs(actual.astype('int16')-np.asarray(expected.convert('RGB')).astype('int16'))
                        self.assertLess(float(difference.mean()),5)
            finally:reader.close()
            self.assertEqual(count,12);self.assertEqual(receipt['total_frames'],12)
            self.assertEqual(receipt['scientific_calendar'][0]['clock']['trim_in_frame'],1)
        self.assertEqual(project['studio']['calculations'],self.project['studio']['calculations'])

    def test_legend_is_sealed_and_uses_complete_matching_semantics(self):
        from studio_map_bundles import BundleFrames,legend_spec
        with BundleFrames(self.record) as decoder:
            item=decoder.manifest['auxiliaries']['legend_static']
            self.assertEqual(item['spec'],legend_spec(decoder.manifest['cartographic_settings']))
            product=decoder.at(3,('continent','galapagos','legend_static'))
            try:
                self.assertEqual(product['observation']['date'],'2025-01-03')
                self.assertEqual(product['images']['galapagos'].getchannel('A').getextrema(),(0,0))
                self.assertEqual(product['images']['legend_static'].getchannel('A').getextrema(),(0,255))
            finally:
                for image in product['images'].values():image.close()
            path=Path(self.record['manifest_path']).parent/item['path'];path.write_bytes(path.read_bytes()+b'changed')
            with self.assertRaises(ValueError):decoder.at(3,('legend_static',))
        self.assertEqual(self.project,self.before)

    def test_categorical_legend_retains_more_than_eight_classes(self):
        from studio_map_bundles import paint_legend
        settings={'kind':'categorical','legend':'Classes','units':'code','classes':[
            {'value':i,'label':'Class '+str(i),'color':'#204060'} for i in range(12)]}
        with paint_legend(settings) as image:
            self.assertEqual(image.height,64+32*12)
            for i in range(12):self.assertEqual(image.getpixel((20,70+i*32)),(32,64,96,255))


if __name__=='__main__':unittest.main()
