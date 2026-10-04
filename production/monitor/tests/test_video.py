import unittest
from unittest.mock import patch
import pandas as pd
from export_video import basemap, render_frame, depth_color, load_catalog, WIDTH, HEIGHT


class VideoTests(unittest.TestCase):
    def test_mixed_iso_dates(self):
        frame=pd.DataFrame(dict(time=["1901-01-01 00:00:00+00:00","1906-09-28 15:24:36.940000+00:00"],magnitude=[4,8.8]))
        with patch("export_video.pd.read_csv",return_value=frame):
            catalog=load_catalog("unused.csv",1900,2026,4)
        self.assertEqual(len(catalog),2)
        self.assertEqual(str(catalog.time.dt.tz),"UTC")

    def test_depth_scale_clamps_and_unknown(self):
        self.assertEqual(depth_color(300),depth_color(600))
        self.assertEqual(depth_color(-1),depth_color(0))
        self.assertEqual(depth_color(float("nan")),(136,147,146))

    def test_vertical_frame(self):
        selected=pd.DataFrame(dict(longitude=[-79],latitude=[-1],depth=[20],magnitude=[5]))
        image=render_frame(basemap(),selected,2000,1900,2026,4,"2026-10-02 15:53")
        self.assertEqual(image.size,(WIDTH,HEIGHT))
        self.assertEqual(image.mode,"RGB")


if __name__=="__main__":
    unittest.main()
