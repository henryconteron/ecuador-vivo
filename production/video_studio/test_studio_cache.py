"""Session presentation cache contracts; real assets, renders and Streamlit reruns."""
import copy
import hashlib
import io
import os
import struct
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
import imageio_ffmpeg
sys.path.insert(0,str(Path(__file__).parent))
import studio_media
import studio_timeline
import storyboard
from studio_editing import new_workspace
from studio_model import Scene,Element
from studio_ui import canvas_payload
from studio_cache import StudioPreviewCache


class StudioCacheTests(unittest.TestCase):
    def clip(self,name,size,colors):
        path=self.root/name
        writer=imageio_ffmpeg.write_frames(str(path),size,fps=30,macro_block_size=1)
        writer.send(None)
        for color in colors: writer.send(Image.new('RGB',size,color).tobytes())
        writer.close()
        return path.read_bytes()

    def test_warm_products_still_enforce_combined_media_budget(self):
        studio=self.project['studio']
        studio['media']['clip']=studio_media.import_asset(self.clip('small.mp4',(8,8),['blue']*3),'clip.mp4')
        studio['scenes'][0]['elements']=[Element(id='v',type='video',style={'asset_id':'clip'},
            transform={'x':0,'y':0,'width':100,'height':100}).to_dict()]
        cache=StudioPreviewCache()
        with patch.object(studio_media,'TOTAL_PIXEL_BUDGET',200,create=True):
            self.draw(cache)
            for aid,color in (('extra1','blue'),('extra2','green')):
                stream=io.BytesIO();Image.new('RGB',(8,8),color).save(stream,format='PNG')
                studio['media'][aid]=studio_media.import_asset(stream.getvalue(),aid+'.png')
            with self.assertRaises(ValueError): self.draw(cache)

    def test_video_probe_uses_verified_hash_when_file_stat_is_unchanged(self):
        first=self.clip('one.mp4',(8,8),['red']*3)
        second=self.clip('two.mp4',(16,8),['blue']*6)
        length=max(len(first),len(second))+16
        def padded(content):
            size=length-len(content)
            return content+struct.pack('>I4s',size,b'free')+bytes(size-8)
        path=self.root/'mutable.mp4';path.write_bytes(padded(first));stat=path.stat()
        record={'path':str(path),'kind':'video','sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        cache=StudioPreviewCache()
        with studio_media.AssetFrames({'v':record},cache=cache.media) as assets:
            self.assertEqual(tuple(assets.videos['v'][1]['size']),(8,8))
        path.write_bytes(padded(second));os.utime(path,ns=(stat.st_atime_ns,stat.st_mtime_ns))
        record['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        with studio_media.AssetFrames({'v':record},cache=cache.media) as assets:
            self.assertEqual(tuple(assets.videos['v'][1]['size']),(16,8))
            self.assertAlmostEqual(assets.videos['v'][1]['duration'],.2,places=2)

    def test_video_metadata_mutation_cannot_cross_session_boundary(self):
        record=studio_media.import_asset(self.clip('metadata.mp4',(8,8),['red']*3),'metadata.mp4')
        with studio_media.AssetFrames({'v':record},cache=StudioPreviewCache().media) as first:
            first.videos['v'][1]['size'][0]=999
        with studio_media.AssetFrames({'v':record},cache=StudioPreviewCache().media) as second:
            self.assertEqual(tuple(second.videos['v'][1]['size']),(8,8))

    def setUp(self):
        self.folder=tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root=Path(self.folder.name)
        media=patch.object(storyboard,'MEDIA_ROOT',self.root);media.start();self.addCleanup(media.stop)
        output=io.BytesIO();Image.new('RGB',(8,8),'red').save(output,format='PNG')
        photo=studio_media.import_asset(output.getvalue()+b'\0\0','photo.png')
        self.project=new_workspace({'endcard_enabled':False});studio=self.project['studio']
        studio['output_profile']={'id':'custom','width':320,'height':180}
        studio['media']={'photo':photo}
        studio['calculations']={'rain':{'value':12,'variable':'precipitation','units':'mm','provenance':{'warnings':[]}}}
        studio['scenes']=[Scene(id='a',duration=.1,elements=[
            Element(id='photo',type='image',transform={'x':0,'y':0,'width':100,'height':100},style={'asset_id':'photo'}).to_dict(),
            Element(id='text',type='text',transform={'x':120,'y':20,'width':180,'height':60},
                style={'text':'{{value}}','font_size':20},data_binding={'result_id':'rain','field':'value'}).to_dict()]).to_dict(),
            Scene(id='b',duration=.1,background='#0000ff').to_dict()]
        studio['timeline']=['a','b']

    def draw(self,cache,project=None, *, frame=0):
        prepared=studio_timeline.PreparedTimeline(project or self.project)
        with studio_media.AssetFrames(prepared.project['studio']['media'],cache=cache.media) as assets:
            view=cache.for_timeline(prepared,assets)
            return view.canvas('a',canvas_payload),view.thumbnails(),view.preview(frame)

    def test_warm_rerun_reuses_decoding_and_renders_with_identical_pixels(self):
        cache=StudioPreviewCache();before=copy.deepcopy(self.project)
        with patch.object(studio_media.Image,'open',wraps=studio_media.Image.open) as decode, \
             patch.object(studio_timeline,'_render_validated_scene',wraps=studio_timeline._render_validated_scene) as render:
            first=self.draw(cache);calls=render.call_count
            self.assertEqual(decode.call_count,1)
            self.assertEqual(self.draw(cache),first)
            self.assertEqual(decode.call_count,1)
            self.assertEqual(render.call_count,calls)
        with Image.open(io.BytesIO(first[2])) as cached:
            self.assertEqual(cached.tobytes(),studio_timeline.frame_at(self.project,0).tobytes())
        self.assertEqual(self.project,before)

    def test_keys_invalidate_only_dependent_scenes_and_profile(self):
        cache=StudioPreviewCache();self.draw(cache)
        current=copy.deepcopy(self.project)
        with patch.object(studio_timeline,'_render_validated_scene',wraps=studio_timeline._render_validated_scene) as render:
            current['studio']['scenes'][1]['background']='#00ff00';self.draw(cache,current)
            self.assertEqual(render.call_count,1)
            render.reset_mock();current['studio']['calculations']['rain']['value']=15;self.draw(cache,current)
            self.assertEqual(render.call_count,2)  # a: authoring plus temporal preview
            render.reset_mock();current['studio']['calculations']['unused']={'value':1,'variable':'precipitation','units':'mm','provenance':{'warnings':[]}}
            self.draw(cache,current);self.assertEqual(render.call_count,0)
            current['studio']['timeline'].reverse()
            _,rows,_=self.draw(cache,current,frame=3)
            self.assertEqual([r['id'] for r in rows],['b','a']);self.assertEqual(render.call_count,0)
            current['studio']['output_profile']['width']=640;self.draw(cache,current,frame=3)
            self.assertEqual(render.call_count,3)

    def test_content_hash_verification_cannot_be_bypassed_by_unchanged_stat(self):
        cache=StudioPreviewCache();self.draw(cache)
        record=self.project['studio']['media']['photo'];path=Path(record['path']);stat=path.stat()
        content=io.BytesIO();Image.new('RGB',(8,8),'blue').save(content,format='PNG')
        self.assertEqual(len(content.getvalue()),stat.st_size)
        path.write_bytes(content.getvalue());os.utime(path,ns=(stat.st_atime_ns,stat.st_mtime_ns))
        with self.assertRaises(ValueError): self.draw(cache)
        record['sha256']=hashlib.sha256(content.getvalue()).hexdigest()
        _,_,preview=self.draw(cache)
        with Image.open(io.BytesIO(preview)) as image: self.assertEqual(image.getpixel((50,50)),(0,0,255,255))

    def test_returned_payload_and_decoded_images_do_not_mutate_cache(self):
        cache=StudioPreviewCache();first=self.draw(cache)
        first[0]['layers'][0]['x']=999;first[1][0]['thumbnail']='broken'
        with studio_media.AssetFrames(self.project['studio']['media'],cache=cache.media) as assets:
            assets.images['photo'].paste('green',(0,0,8,8))
        second=self.draw(cache)
        self.assertEqual(second[0]['layers'][0]['x'],0)
        self.assertNotEqual(second[1][0]['thumbnail'],'broken')
        with studio_media.AssetFrames(self.project['studio']['media'],cache=cache.media) as assets:
            self.assertEqual(assets.images['photo'].getpixel((0,0)),(255,0,0,255))

    def test_cache_is_bounded_and_separate_instances_do_not_share_entries(self):
        cache=StudioPreviewCache(max_bytes=500,media_max_bytes=100)
        for number in range(8):
            project=copy.deepcopy(self.project);project['studio']['scenes'][0]['name']=str(number)
            self.draw(cache,project,frame=number%3)
            self.assertLessEqual(cache.bytes_used,500);self.assertLessEqual(cache.media.bytes_used,100)
        fresh=StudioPreviewCache()
        self.assertEqual(fresh.bytes_used,0);self.assertEqual(fresh.media.bytes_used,0)
        with patch.object(studio_timeline,'_render_validated_scene',wraps=studio_timeline._render_validated_scene) as render:
            self.draw(fresh);self.assertGreater(render.call_count,0)

    def test_cached_video_metadata_and_frames_preserve_trim_loop_pixels(self):
        path=self.root/'clip.mp4'
        writer=imageio_ffmpeg.write_frames(str(path),(320,180),fps=30,macro_block_size=1)
        writer.send(None)
        for color in ('red','blue','green'): writer.send(Image.new('RGB',(320,180),color).tobytes())
        writer.close()
        studio=self.project['studio'];studio['media']['clip']=studio_media.import_asset(path.read_bytes(),'clip.mp4')
        studio['scenes'][0]['elements']=[Element(id='v',type='video',transform={'x':0,'y':0,'width':320,'height':180},
            style={'asset_id':'clip','trim_in':1/30,'trim_out':.1,'loop':True}).to_dict()]
        cache=StudioPreviewCache()
        expected=[studio_timeline.frame_at(self.project,i).tobytes() for i in range(3)]
        with patch.object(studio_media,'probe_video',wraps=studio_media.probe_video) as probe:
            for repeat in range(2):
                for frame in (2,0,1):
                    _,_,png=self.draw(cache,frame=frame)
                    with Image.open(io.BytesIO(png)) as image: self.assertEqual(image.tobytes(),expected[frame])
            self.assertEqual(probe.call_count,1)

    def test_invalid_document_or_frame_cannot_use_previous_products(self):
        cache=StudioPreviewCache();self.draw(cache)
        invalid=copy.deepcopy(self.project);invalid['studio']['calculations']['rain']['value']=float('nan')
        with self.assertRaises(ValueError): self.draw(cache,invalid)
        for frame in (-1,6,True):
            with self.assertRaises(ValueError): self.draw(cache,frame=frame)

    def test_ui_rerun_reuses_cache_without_scientific_reads(self):
        from streamlit.testing.v1 import AppTest
        import studio_ui
        script='import sys\nsys.path.insert(0,{!r})\nfrom studio_ui import show_studio\nshow_studio({!r},key="cached")'.format(str(Path(__file__).parent),self.project)
        with patch.object(studio_ui,'STORE',self.root),patch('data.load_values',side_effect=AssertionError('No science')), \
             patch.object(studio_timeline,'_render_validated_scene',wraps=studio_timeline._render_validated_scene) as render:
            app=AppTest.from_string(script,default_timeout=30).run()
            self.assertFalse(app.exception);self.assertFalse(app.error)
            calls=render.call_count;app.run()
            self.assertFalse(app.exception);self.assertFalse(app.error)
            self.assertEqual(render.call_count,calls)


if __name__=='__main__': unittest.main()
