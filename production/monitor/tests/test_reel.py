import copy
import unittest

import pandas as pd
from PIL import ImageDraw, Image

from prepare_reel import audit_features
from reel_editorial import base_map, render_map, closing_card, intro_card, timeline, FPS, write, depth_card, profile_card, depth_counts, profile_point, text_card
from reel_design import DEPTH_BOX, MAG_BOX, CREDIT, CREDIT_NAME, CREDIT_SPECIALTY, animate_card, purpose_card, action_card


def feature(event_id="one",depth=20):
    return dict(id=event_id,geometry=dict(coordinates=[-79,-1,depth]),
                properties=dict(time=1710000000000,mag=5,magType="mw",place="Test"))


class ReelTests(unittest.TestCase):
    def test_catalog_validation_preserves_unknown_depth(self):
        df,checks=audit_features([feature(),feature("unknown",None)],1900,2025,4)
        self.assertTrue(all(checks.values()))
        self.assertEqual(len(df),2)
        self.assertTrue(pd.isna(df[df.id=="unknown"].iloc[0].depth))
        self.assertEqual(str(df.time.dt.tz),"UTC")

    def test_audit_refuses_bad_data_instead_of_discarding(self):
        with self.assertRaises(ValueError):
            audit_features([feature(),feature()],1900,2025,4)
        for field,value in [("magnitude",None),("longitude",-90),("depth",float("inf")),("time",1800000000000)]:
            bad=copy.deepcopy(feature())
            if field in ["longitude","depth"]:
                bad["geometry"]["coordinates"][0 if field=="longitude" else 2]=value
            else:
                bad["properties"]["mag" if field=="magnitude" else "time"]=value
            with self.assertRaises(ValueError):
                audit_features([bad],1900,2025,4)

    def test_video_period_and_exact_duration(self):
        scenes=timeline(1900,2025)
        self.assertEqual([year for kind,year,_ in scenes if kind=="year"],list(range(1900,2026)))
        self.assertAlmostEqual(sum(n for _,_,n in scenes)/FPS,116.8)
        self.assertEqual(FPS,30)

    def test_all_cards_fit_publication_canvas(self):
        df,_=audit_features([feature(),feature("unknown",None)],1900,2025,4)
        base=base_map(1900,2025,4)
        images=[intro_card(1900,2025,4),intro_card(1900,2025,4,True),depth_card(),profile_card(df),purpose_card(),action_card(),
                text_card("Conocer. Prepararse.",["Preparen su kit de emergencia."],"Conciencia sísmica: llevar lo aprendido a la acción"),
                closing_card(dict(exported_count=2661,minimum=4,downloaded_at_utc="2026-10-02"))]
        for year in [1900,1949,1960,1990,2025]:
            images.append(render_map(base,df[df.time.dt.year<=year],year))
        self.assertTrue(all(image.size==(1080,1920) and image.mode=="RGB" for image in images))
        with self.assertRaises(ValueError):
            write(ImageDraw.Draw(Image.new("RGB",(1080,1920))),(900,100),"long text",50)

    def test_depth_boundaries_and_missing_are_not_zero(self):
        df=pd.DataFrame(dict(depth=[0,69.9,70,299.9,300,700,float("nan")]))
        counts=depth_counts(df)
        self.assertEqual(counts,dict(shallow=2,intermediate=2,deep=2,unknown=1))
        self.assertEqual(sum(counts.values()),len(df))

    def test_profiles_invert_depth_and_do_not_clip_deeper_catalog(self):
        self.assertEqual(profile_point(-83,0,(-83,-74.5),(150,575,900,860)),(150,575))
        self.assertEqual(profile_point(-74.5,300,(-83,-74.5),(150,575,900,860)),(900,860))
        df,_=audit_features([feature(depth=301)],1900,2025,4)
        with self.assertRaises(ValueError):
            profile_card(df)

    def test_legends_have_separate_rows_and_safe_margins(self):
        self.assertGreater(MAG_BOX[1]-DEPTH_BOX[3],10)
        self.assertEqual(DEPTH_BOX[0],MAG_BOX[0])
        self.assertEqual(DEPTH_BOX[2],MAG_BOX[2])
        self.assertEqual(CREDIT,"Henry Conteron, ingeniero en geociencias e investigador independiente")
        self.assertEqual(CREDIT_NAME,"Henry Conteron")
        self.assertEqual(CREDIT_SPECIALTY,"Ingeniero en geociencias e investigador independiente")

    def test_editorial_motion_and_narration_reading_time(self):
        image=intro_card(1900,2025,4)
        self.assertNotEqual(animate_card(image,"intro",0,0).tobytes(),animate_card(image,"intro",.25,.25).tobytes())
        adjusted=timeline(1900,2025,{"intro":20*FPS})
        self.assertEqual(adjusted[0][2],20*FPS)
        self.assertEqual([n for kind,_,n in adjusted if kind=="year"],[9]*126)


if __name__=="__main__":
    unittest.main()
