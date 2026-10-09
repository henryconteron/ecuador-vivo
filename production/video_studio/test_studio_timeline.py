import copy
import io
import tempfile
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import imageio_ffmpeg
import subprocess
from PIL import Image
sys.path.insert(0, str(Path(__file__).parent))
from studio_model import Scene, Element
from studio_editing import new_workspace
from output_profiles import profile_for
from studio_render import render_scene
from studio_timeline import frame_at, export_movie, validate_export
from studio_media import import_asset, AssetFrames


class StudioTimelineTests(unittest.TestCase):
    def test_export_rejects_non_json_project_before_publishing(self):
        with tempfile.TemporaryDirectory() as directory:
            project=self.project();project['unknown']=float('nan')
            target=Path(directory)/'movie.mp4'
            with self.assertRaises(ValueError): export_movie(project,target)
            self.assertFalse(target.exists())

    def test_export_does_not_publish_on_sidecar_failure(self):
        import studio_timeline
        original=studio_timeline._write_staged_json
        def fail_receipt(path,value):
            if value.get('renderer')=='studio_scene_v1': raise OSError('Synthetic sidecar failure')
            return original(path,value)
        with tempfile.TemporaryDirectory() as directory,patch.object(studio_timeline,'_write_staged_json',side_effect=fail_receipt):
            target=Path(directory)/'movie.mp4'
            with self.assertRaises(OSError): export_movie(self.project(),target)
            for name in ('movie.mp4','project.json','receipt.json'):
                self.assertFalse((Path(directory)/name).exists(),name)

    def test_export_preserves_preexisting_staging_and_reservation(self):
        for name in ('.project.studio-partial.json','.receipt.studio-partial.json',
                     '.project.studio-partial.json.tmp','.receipt.studio-partial.json.tmp','.studio-export.lock'):
            with tempfile.TemporaryDirectory() as directory:
                existing=Path(directory)/name;existing.write_text('existing export',encoding='utf-8')
                with self.assertRaises(ValueError): export_movie(self.project(),Path(directory)/'movie.mp4')
                self.assertEqual(existing.read_text(encoding='utf-8'),'existing export')
                self.assertFalse((Path(directory)/'movie.mp4').exists())

    def test_export_rejects_destinations_that_alias_sidecars(self):
        for name in ('project.json','receipt.json','.studio-export.lock','movie.png'):
            with tempfile.TemporaryDirectory() as directory:
                target=Path(directory)/name
                with self.assertRaises(ValueError): export_movie(self.project(),target)
                self.assertFalse(target.exists())

    def test_lock_close_failure_releases_only_its_reservation(self):
        original=Path.open
        class FailingClose:
            def __init__(self,stream): self.stream=stream
            def __enter__(self): return self
            def write(self,value): return self.stream.write(value)
            def __exit__(self,*args): self.stream.close();raise OSError('Lock close failed')
        def open_path(path,*args,**kwargs):
            stream=original(path,*args,**kwargs)
            return FailingClose(stream) if path.name=='.studio-export.lock' else stream
        with tempfile.TemporaryDirectory() as directory,patch.object(Path,'open',open_path):
            target=Path(directory)/'movie.mp4'
            with self.assertRaises(OSError): export_movie(self.project(),target)
            self.assertFalse((Path(directory)/'.studio-export.lock').exists())
            self.assertFalse(target.exists())

    def test_partial_sidecar_write_is_cleaned_without_publication(self):
        original=Path.open
        class FailingWrite:
            def __init__(self,stream): self.stream=stream
            def __enter__(self): return self
            def write(self,value): self.stream.write('partial');raise OSError('Sidecar disk full')
            def __exit__(self,*args): self.stream.close()
        def open_path(path,*args,**kwargs):
            stream=original(path,*args,**kwargs)
            return FailingWrite(stream) if path.name.startswith('.receipt.studio-partial.json') else stream
        with tempfile.TemporaryDirectory() as directory,patch.object(Path,'open',open_path):
            target=Path(directory)/'movie.mp4'
            with self.assertRaises(OSError): export_movie(self.project(),target)
            self.assertFalse(target.exists())
            self.assertFalse(list(Path(directory).glob('.*studio-partial*')))

    def test_quantized_timeline_obeys_two_hour_limit(self):
        from studio_timeline import PreparedTimeline
        project=self.project()
        project['studio']['scenes']=[Scene(id=f's{i}',duration=.05).to_dict() for i in range(99)]+[
            Scene(id='last',duration=7195.05).to_dict()]
        project['studio']['timeline']=[s['id'] for s in project['studio']['scenes']]
        with self.assertRaises(ValueError): PreparedTimeline(project)

    def test_cleanup_failures_roll_back_published_products(self):
        import studio_media
        original_unlink=Path.unlink
        original_close=studio_media.AssetFrames.close
        def fail_lock(path,*args,**kwargs):
            original_unlink(path,*args,**kwargs)
            if path.name=='.studio-export.lock': raise OSError('Lock release failed')
        def fail_media(source):
            original_close(source)
            raise OSError('Reader close failed')
        for fixture in (patch.object(Path,'unlink',fail_lock),patch.object(studio_media.AssetFrames,'close',fail_media)):
            with self.subTest(fixture=fixture),tempfile.TemporaryDirectory() as directory,fixture:
                with self.assertRaises(OSError): export_movie(self.project(),Path(directory)/'movie.mp4')
                for name in ('movie.mp4','project.json','receipt.json'):
                    self.assertFalse((Path(directory)/name).exists(),name)

    def test_asset_adapter_cannot_mutate_prepared_scene(self):
        from studio_timeline import PreparedTimeline
        project=self.project()
        project['studio']['scenes'][0]['elements']=[Element(id='box',type='shape',
            transform={'x':20,'y':20,'width':100,'height':100},style={'fill':'#000000'}).to_dict()]
        prepared=PreparedTimeline(project)
        before=prepared.frame_at(0).tobytes()
        class Adapter:
            def at(self,time,elements):
                elements[0]['style']['fill']='#ffffff'
                return {}
        self.assertEqual(prepared.frame_at(0,assets=Adapter()).tobytes(),before)
        self.assertEqual(prepared.frame_at(0).tobytes(),before)

    def test_prepared_timeline_preserves_pixels_and_isolates_source_mutation(self):
        from studio_timeline import PreparedTimeline
        project=self.project()
        project['studio']['calculations']['rain']={'value':132.4,'variable':'precipitation','units':'mm','provenance':{'warnings':[]}}
        project['studio']['scenes'][0]['elements']=[Element(id='bound',type='text',
            transform={'x':20,'y':20,'width':180,'height':60},style={'text':'{{value}}','font_size':20},
            data_binding={'result_id':'rain','field':'value'}).to_dict()]
        before=copy.deepcopy(project)
        prepared=PreparedTimeline(project)
        expected=[frame_at(project,frame).tobytes() for frame in range(6)]
        self.assertEqual([prepared.frame_at(frame).tobytes() for frame in range(6)],expected)
        project['studio']['calculations']['rain']['value']=999
        project['studio']['timeline'].reverse()
        rows=prepared.rows;rows[0]['end_frame']=999;rows.reverse()
        self.assertEqual(prepared.total_frames,6)
        self.assertEqual([prepared.frame_at(frame).tobytes() for frame in range(6)],expected)
        self.assertEqual(prepared.project,before)
        exposed=prepared.project;exposed['studio']['calculations'].clear()
        self.assertEqual(prepared.project,before)
        with self.assertRaises(ValueError): prepared.frame_at(6)

    def test_sparse_vfr_random_seek_keeps_preceding_frame(self):
        import storyboard
        with tempfile.TemporaryDirectory() as directory, patch.object(storyboard,'MEDIA_ROOT',Path(directory)):
            folder=Path(directory)
            for name,color in (('red','red'),('blue','blue'),('green','green')):
                Image.new('RGB',(320,180),color).save(folder/(name+'.png'))
            (folder/'frames.txt').write_text("file 'red.png'\nduration 10\nfile 'blue.png'\nduration 10\nfile 'green.png'\nduration 1\nfile 'green.png'\n",encoding='utf-8')
            source=folder/'sparse.mp4'
            completed=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-f','concat','-safe','0',
                '-i',str(folder/'frames.txt'),'-fps_mode','vfr','-c:v','libx264','-pix_fmt','yuv420p',str(source)],
                capture_output=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),timeout=30)
            self.assertEqual(completed.returncode,0,completed.stderr.decode(errors='replace'))
            record=import_asset(source.read_bytes(),'sparse.mp4')
            element=Element(id='v',type='video',style={'asset_id':'clip','mute':True}).to_dict()
            with AssetFrames({'clip':record}) as assets:
                for seconds,channel in ((4,0),(14,2),(2,0),(20,1)):
                    pixel=assets.at(seconds,[element])['video.v'].getpixel((100,100))
                    self.assertGreater(pixel[channel],120,(seconds,pixel))
                    self.assertLess(sum(pixel[:3])-pixel[channel],10,(seconds,pixel))

    def test_vfr_seek_trim_and_loop_match_sequential_frames(self):
        import storyboard
        with tempfile.TemporaryDirectory() as directory, patch.object(storyboard,'MEDIA_ROOT',Path(directory)):
            folder=Path(directory)
            durations=(.04,.07,.11)
            manifest=[]
            for index in range(60):
                path=folder/f'frame-{index:02d}.png'
                Image.new('RGB',(320,180),(index*4,255-index*4,(index*29)%256)).save(path)
                manifest.extend([f"file '{path.name}'",f'duration {durations[index%3]}'])
            manifest.append("file 'frame-59.png'")
            (folder/'frames.txt').write_text('\n'.join(manifest),encoding='utf-8')
            source=folder/'vfr.mp4'
            completed=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-f','concat','-safe','0',
                '-i',str(folder/'frames.txt'),'-fps_mode','vfr','-c:v','libx264','-pix_fmt','yuv420p',str(source)],
                capture_output=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),timeout=30)
            self.assertEqual(completed.returncode,0,completed.stderr.decode(errors='replace'))
            video=import_asset(source.read_bytes(),'vfr.mp4')
            element=Element(id='v',type='video',style={'asset_id':'clip','mute':True}).to_dict()
            with AssetFrames({'clip':video}) as sequential:
                reference=[sequential.at(frame/30,[element])['video.v'].tobytes() for frame in range(120)]
            with AssetFrames({'clip':video}) as random_access:
                for frame in (90,31,62,0,119,45,30,91):
                    self.assertEqual(random_access.at(frame/30,[element])['video.v'].tobytes(),reference[frame],f'VFR frame {frame}')
            element['style'].update(trim_in=1.1,trim_out=1.5,loop=True)
            with AssetFrames({'clip':video}) as trimmed:
                for frame in (0,5,11,12,17,25):
                    self.assertEqual(trimmed.at(frame/30,[element])['video.v'].tobytes(),reference[33+frame%12],f'trim/loop frame {frame}')

    def test_export_preserves_existing_project_and_rejects_unknown_presentation(self):
        p=self.project()
        with tempfile.TemporaryDirectory() as directory:
            existing=Path(directory)/'project.json';existing.write_text('USER PROJECT',encoding='utf-8')
            with self.assertRaises(ValueError): export_movie(p,Path(directory)/'movie.mp4')
            self.assertEqual(existing.read_text(encoding='utf-8'),'USER PROJECT')
            self.assertFalse((Path(directory)/'movie.mp4').exists())
        profile=profile_for(p['studio']['output_profile'])
        for changes in ({'style':{'font_weight':'ultrabold'}},{'animation':{'in':'none','unexpected':1}}):
            element=Element(id='text',type='text',style={'text':'A'}).to_dict();element.update(changes)
            scene=Scene(id='s',elements=[element]).to_dict()
            with self.assertRaises(ValueError): render_scene(scene,profile,{})

    def test_media_budget_is_checked_before_decoding_and_trim_uses_seek(self):
        import studio_media
        from unittest.mock import Mock
        fake=Mock();fake.stat.return_value.st_size=1;fake.read_bytes.return_value=b'a';fake.suffix='.png'
        digest=__import__('hashlib').sha256(b'a').hexdigest()
        image=Mock();image.width=10000;image.height=4000
        image.__enter__=Mock(return_value=image);image.__exit__=Mock(return_value=False)
        image.convert.return_value=image
        image.size=(10000,4000)
        image.getexif.return_value={}
        records={str(i):{'path':'safe.png','sha256':digest,'kind':'image'} for i in range(3)}
        with patch.object(studio_media,'media_path',return_value=fake),patch.object(studio_media.Image,'open',return_value=image), \
             patch.object(studio_media.ImageOps,'exif_transpose',return_value=image):
            with self.assertRaises(ValueError): AssetFrames(records)
        self.assertEqual(image.convert.call_count,2)
        source=Mock();source.records={};source.images={};source.videos={'clip':(Path('safe.mp4'),{'duration':300})};source.cursors={}
        source._map_pixels.return_value=0  # This isolated legacy-video fixture has no bundle products.
        element=Element(id='v',type='video',style={'asset_id':'clip','trim_in':299,'trim_out':300}).to_dict()
        frame=Image.new('RGB',(2,2),'red').tobytes()
        reader=iter([{'size':(2,2)},frame])
        with patch.object(studio_media.imageio_ffmpeg,'read_frames',return_value=reader) as decode:
            result=AssetFrames.at(source,0,[element])
            self.assertEqual(result['video.v'].size,(2,2))
            self.assertIn('-ss',decode.call_args.kwargs['input_params'])
            self.assertEqual(decode.call_args.kwargs['input_params'][-1],'298.0')

    def project(self):
        p = new_workspace({'endcard_enabled': False})
        studio = p['studio']
        studio['output_profile'] = {'id': 'custom', 'width': 320, 'height': 180}
        first = Scene(id='red', duration=.1, background='#ff0000').to_dict()
        second = Scene(id='blue', duration=.1, background='#0000ff').to_dict()
        studio['scenes'] = [first, second]
        studio['timeline'] = ['red', 'blue']
        return p

    def test_frame_boundaries_and_preview_use_identical_renderer(self):
        p = self.project()
        before = copy.deepcopy(p)
        self.assertEqual(frame_at(p, 0).getpixel((0,0)), (255,0,0,255))
        self.assertEqual(frame_at(p, 2).getpixel((0,0)), (255,0,0,255))
        self.assertEqual(frame_at(p, 3).getpixel((0,0)), (0,0,255,255))
        self.assertEqual(frame_at(p, 5).getpixel((0,0)), (0,0,255,255))
        with self.assertRaises(ValueError): frame_at(p, 6)
        self.assertEqual(p, before)

    def test_export_has_exact_frames_receipt_and_preview_pixels(self):
        p = self.project()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)/'movie.mp4'
            receipt = export_movie(p, target)
            reader = imageio_ffmpeg.read_frames(str(target), pix_fmt='rgb24')
            metadata = next(reader)
            frames = list(reader)
            self.assertEqual(metadata['size'], (320,180))
            self.assertEqual(len(frames), 6)
            self.assertEqual(receipt['total_frames'], 6)
            self.assertEqual(receipt['timeline'][1]['start_frame'], 3)
            self.assertEqual(receipt['calculations'], p['studio']['calculations'])
            for index in (0,3,5):
                decoded = Image.frombytes('RGB', (320,180), frames[index])
                expected = frame_at(p, index).convert('RGB')
                self.assertLess(max(abs(a-b) for a,b in zip(decoded.getpixel((100,100)), expected.getpixel((100,100)))), 4)
            self.assertTrue((Path(directory)/'receipt.json').is_file())

    def test_legacy_unsupported_and_invalid_registry_fail_before_file_creation(self):
        p = self.project()
        p['studio']['scenes'][0]['renderer'] = 'legacy'
        with self.assertRaises(ValueError): validate_export(p)
        p = self.project()
        p['studio']['calculations']['bad'] = {'value': float('nan')}
        with self.assertRaises(ValueError): validate_export(p)
        p = self.project()
        p['studio']['scenes'][0]['elements'] = [Element(id='e', type='table').to_dict()]
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)/'movie.mp4'
            with self.assertRaises(ValueError): export_movie(p, target)
            self.assertFalse(target.exists())
            self.assertFalse((Path(directory)/'receipt.json').exists())

    def test_animation_known_pixels_and_data_integrity(self):
        profile = profile_for({'id':'custom','width':320,'height':180})
        registry = {'rain': {'value':132.4, 'units':'mm'}}
        before = copy.deepcopy(registry)
        element = Element(id='box',type='shape', transform={'x':20,'y':20,'width':100,'height':100},
            style={'fill':'#ffffff'}, animation={'in':'fade','out':'none','duration':1,'delay':0})
        scene = Scene(id='s', duration=3, background='#000000', elements=[element]).to_dict()
        self.assertEqual(render_scene(scene,profile,registry,time=0).getpixel((50,50)),(0,0,0,255))
        self.assertEqual(render_scene(scene,profile,registry,time=.5).getpixel((50,50)),(128,128,128,255))
        self.assertEqual(render_scene(scene,profile,registry,time=1).getpixel((50,50)),(255,255,255,255))
        for mode in ('slide','scale','wipe'):
            scene['elements'][0]['animation']['in'] = mode
            self.assertEqual(render_scene(scene,profile,registry,time=0).getpixel((50,50)),(0,0,0,255))
            self.assertEqual(render_scene(scene,profile,registry,time=1).getpixel((50,50)),(255,255,255,255))
        self.assertEqual(registry,before)
        scene['elements'][0]['animation']['duration'] = 4
        with self.assertRaises(ValueError): render_scene(scene,profile,registry,time=0)

    def test_image_video_assets_secure_and_shared_frames(self):
        import storyboard
        with tempfile.TemporaryDirectory() as directory, patch.object(storyboard,'MEDIA_ROOT',Path(directory)):
            image = Image.new('RGB',(80,40),'green'); buffer=io.BytesIO(); image.save(buffer,format='PNG')
            asset = import_asset(buffer.getvalue(),'foto.png')
            self.assertEqual(asset['size'],[80,40])
            with AssetFrames({'photo':asset}) as assets:
                self.assertEqual(assets.at(0)['photo'].size,(80,40))
            Path(asset['path']).write_bytes(b'changed')
            with self.assertRaises(ValueError): AssetFrames({'photo':asset})
            with self.assertRaises(ValueError): AssetFrames({'bad':{'path':'C:/secret.png','sha256':'0'*64,'kind':'image'}})
            with self.assertRaises(ValueError): import_asset(b'bad','bad.exe')
            source=Path(directory)/'clip.mp4'
            writer=imageio_ffmpeg.write_frames(str(source),(320,180),fps=30,macro_block_size=1)
            writer.send(None)
            for color in ('red','green','blue'): writer.send(Image.new('RGB',(320,180),color).tobytes())
            writer.close()
            video=import_asset(source.read_bytes(),'clip.mp4')
            p=self.project();p['studio']['media']['clip']=video
            scene=p['studio']['scenes'][0]
            scene['elements']=[Element(id='clip',type='video',transform={'x':0,'y':0,'width':320,'height':180},
                              style={'asset_id':'clip','mute':True,'trim_in':0,'loop':False}).to_dict()]
            with AssetFrames(p['studio']['media']) as assets:
                first=frame_at(p,0,assets=assets)
                last=frame_at(p,2,assets=assets)
                self.assertGreater(first.getpixel((100,100))[0],240)
                self.assertGreater(last.getpixel((100,100))[2],240)
            scene['elements'][0]['style']['mute']=False
            self.assertEqual(validate_export(p).width,320)


if __name__=='__main__': unittest.main()
