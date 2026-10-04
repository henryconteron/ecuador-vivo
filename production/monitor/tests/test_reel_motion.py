import json
from pathlib import Path
import tempfile
import unittest

import pandas as pd
from PIL import Image

from reel_captions import caption_groups, wrap_words, srt_time, CAPTION_BOX, Captions
from reel_motion import MotionDesign, ease
from reel_design import BG, MAP, base_map, render_map


class CaptionTests(unittest.TestCase):
    def test_wrapping_grouping_times_and_all_words_preserved(self):
        texts="Mira cómo se llena este mapa. Son sismos registrados a lo largo de más de un siglo.".split()
        words=[dict(text=text,start=i*.4,end=i*.4+.35) for i,text in enumerate(texts)]
        groups=caption_groups(dict(segments=[dict(words=words)],duration=8))
        self.assertEqual([word["text"] for group in groups for word in group["words"]],texts)
        self.assertTrue(all(len(wrap_words(group["words"]))<=2 for group in groups))
        self.assertTrue(all(a["end"]<=b["start"] for a,b in zip(groups,groups[1:])))
        self.assertEqual(srt_time(61.123),"00:01:01,123")
        self.assertLess(CAPTION_BOX[3],1621)  # Professional credit remains unobstructed.

    def test_caption_pixels_stay_inside_reserved_band(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            source=dict(duration=2,segments=[dict(words=[dict(text="Profundidad",start=0,end=1)])])
            (folder/"audio_transcript.json").write_text(json.dumps(source),encoding="utf-8")
            captions=Captions(folder)
            original=Image.new("RGB",(1080,1920),BG)
            result=captions.draw(original.copy(),.5)
            self.assertEqual(original.crop((0,0,1080,1430)).tobytes(),result.crop((0,0,1080,1430)).tobytes())
            self.assertEqual(original.crop((0,1591,1080,1920)).tobytes(),result.crop((0,1591,1080,1920)).tobytes())
            self.assertIsNone(captions.current(1.5))
            captions.save()
            self.assertTrue((folder/"subtitulos.srt").exists())

    def test_long_number_keeps_its_unit_instead_of_flashing_one_word(self):
        words=[dict(text=text,start=start,end=end) for text,start,end in [
            ("Esta",0,.2),("selección",.2,.6),("reúne",.6,1),("2661",1,3),("registros,",3,3.7)]]
        groups=caption_groups(dict(segments=[dict(words=words)],duration=4))
        self.assertEqual([group["text"] for group in groups],["Esta selección reúne","2661 registros,"])


class MotionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.folder=Path(self.temp.name)
        (self.folder/"audio_transcript.json").write_text(json.dumps(dict(duration=121.15,segments=[])),encoding="utf-8")
        self.df=pd.DataFrame(dict(id=["us20005j32","deep","unknown"],time=pd.to_datetime(["2016-04-16","2020-01-01","1901-01-07"],utc=True),
                                 longitude=[-79.9218,-78,-81],latitude=[.3819,-2,-2],depth=[20.59,254,float("nan")],
                                 magnitude=[7.8,4.5,5]))
        self.motion=MotionDesign(self.folder,self.df,dict(exported_count=2661))
        self.source=render_map(base_map(1900,2025,4),self.df,2025)

    def tearDown(self):
        self.temp.cleanup()

    def test_all_editorial_states_fit_safe_width(self):
        for kind,seconds in [("hold",[32,35,40]),("guide",[48,51.9,54,56,58,60.5,62.5,64]),
                             ("depth",[66,69,72,74,77,80]),("profile",[82,86,88,90,95,98,101,104]),
                             ("action",[106,110,114,115.5,117]),("end",[118.5,120,124])]:
            for second in seconds:
                with self.subTest(kind=kind,second=second):
                    image=self.motion.render(self.source,kind,2025,second,0,second/126.17)
                    self.assertEqual(image.size,(1080,1920))

    def test_catalog_map_is_translated_not_distorted_or_animated(self):
        first=self.motion.render(self.source,"year",2025,25,0,.2)
        later=self.motion.render(self.source,"year",2025,29,0,.3)
        region=(90,300,930,1090)
        self.assertEqual(first.crop(region).tobytes(),later.crop(region).tobytes())
        # Ignore the outline; actual map pixels are preserved exactly.
        self.assertEqual(first.crop((92,302,928,1088)).tobytes(),self.source.crop((92,362,928,1148)).tobytes())

    def test_reveals_change_explanation_not_the_source_data(self):
        original=self.df.copy(deep=True)
        self.assertNotEqual(self.motion.depth(70).tobytes(),self.motion.depth(79).tobytes())
        self.assertNotEqual(self.motion.action(114).tobytes(),self.motion.action(117.8).tobytes())
        pd.testing.assert_frame_equal(original,self.df)
        self.assertEqual(len(self.motion.known),2)
        self.assertEqual(ease(0,1),0)
        self.assertEqual(ease(2,1),1)


if __name__=="__main__":
    unittest.main()
