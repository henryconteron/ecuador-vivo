"""Continuous preview/export uses one clock, including delayed entrances."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).parent))
import imageio_ffmpeg
import numpy as np
from studio_model import Scene,Element
from studio_editing import new_workspace
from studio_timeline import PreparedTimeline,export_movie


class StudioAnimationTests(unittest.TestCase):
    def project(self,mode):
        p=new_workspace({'endcard_enabled':False});p['studio']['output_profile']={'id':'custom','width':160,'height':160}
        p['studio']['scenes']=[Scene(id='s',duration=.3,background='#000000',elements=[Element(id='shape',type='shape',
            transform={'x':80,'y':80,'width':40,'height':40},style={'fill':'#ffffff'},
            animation={'in':mode,'out':mode,'duration':.1,'delay':1/30})]).to_dict()]
        p['studio']['timeline']=['s'];return p

    def test_delayed_entrance_is_invisible_until_start_for_every_mode(self):
        for mode in ('fade','slide','scale','wipe'):
            p=self.project(mode);before=copy.deepcopy(p);prepared=PreparedTimeline(p)
            self.assertEqual(max(prepared.frame_at(0).convert('RGB').tobytes()),0,mode)
            self.assertEqual(max(prepared.frame_at(1).convert('RGB').tobytes()),0,mode)
            self.assertEqual(prepared.frame_at(4).getpixel((90,90))[:3],(255,255,255),mode)
            self.assertEqual(p,before)

    def test_all_animation_frames_match_export_and_none_is_static(self):
        for mode in ('none','fade','slide','scale','wipe'):
            p=self.project(mode);prepared=PreparedTimeline(p)
            with tempfile.TemporaryDirectory() as directory:
                target=Path(directory)/'movie.mp4';export_movie(p,target)
                reader=imageio_ffmpeg.read_frames(str(target),pix_fmt='rgb24');next(reader)
                try: frames=list(reader)
                finally: reader.close()
                self.assertEqual(len(frames),9)
                for index,frame in enumerate(frames):
                    expected=prepared.frame_at(index).convert('RGB').tobytes()
                    self.assertLess(float(np.mean(np.abs(np.frombuffer(frame,dtype=np.uint8).astype(int)-np.frombuffer(expected,dtype=np.uint8).astype(int)))),3)
                if mode=='none': self.assertEqual(prepared.frame_at(0).tobytes(),prepared.frame_at(8).tobytes())


if __name__=='__main__': unittest.main()
