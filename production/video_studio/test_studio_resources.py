"""Actual process/pipe ownership, including EOF and invalid metadata."""
import gc
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import warnings
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import imageio_ffmpeg
from studio_ffmpeg import read_frames


class StudioResourceTests(unittest.TestCase):
    def test_eof_early_close_and_metadata_failure_reap_all_pipes(self):
        original=subprocess.Popen;children=[]
        def start(*args,**kwargs):
            process=original(*args,**kwargs);children.append(process);return process
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'video.mp4'
            subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-f','lavfi','-i',
                'color=red:s=160x160:r=30:d=0.1','-c:v','libx264','-pix_fmt','yuv420p',str(path)],
                check=True,capture_output=True,timeout=10,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            with warnings.catch_warnings(record=True) as records,patch.object(subprocess,'Popen',side_effect=start):
                warnings.simplefilter('always',ResourceWarning)
                for mode in ('eof','early','invalid'):
                    reader=read_frames(str(path if mode!='invalid' else Path(directory)/'missing.mp4'),pix_fmt='rgb24')
                    if mode=='invalid':
                        with self.assertRaises(OSError): next(reader)
                    else:
                        self.assertEqual(next(reader)['size'],(160,160))
                        if mode=='eof': self.assertEqual(len(list(reader)),3)
                    reader.close()
                    process=children[-1];self.assertIsNotNone(process.poll())
                    self.assertTrue(all(stream is None or stream.closed for stream in (process.stdin,process.stdout,process.stderr)))
                gc.collect()
                self.assertFalse([warning for warning in records if issubclass(warning.category,ResourceWarning)])

    def test_cache_eviction_and_clear_release_owned_images(self):
        from studio_cache import MediaCache
        from PIL import Image
        cache=MediaCache(600);image=Image.new('RGBA',(4,4),'red')
        cache.remember_image('first',image);owned=cache._lru.entries[('image','first')][0]
        borrowed=cache.image('first');cache.remember_image('second',image)
        with self.assertRaises(ValueError): owned.getpixel((0,0))
        self.assertEqual(borrowed.getpixel((0,0)),(255,0,0,255))
        second=cache._lru.entries[('image','second')][0];cache.clear()
        with self.assertRaises(ValueError): second.getpixel((0,0))
        self.assertEqual(cache.bytes_used,0);borrowed.close();image.close()


if __name__=='__main__': unittest.main()
