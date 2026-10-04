import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
from streamlit.testing.v1 import AppTest

from historical import normalize_features, fetch_history, annual_counts, build_animation, export_animation, magnitude_size


def feature(id="a", year=2000, mag=5, depth=20):
    return dict(id=id,geometry=dict(coordinates=[-79.,-1.,depth]),
                properties=dict(time=int(pd.Timestamp(f"{year}-03-01",tz="UTC").timestamp()*1000),
                                mag=mag,magType="mw",place="Ecuador"))


def response(features=None, count=None, status=200):
    return Mock(status_code=status,text=str(count),json=Mock(return_value=dict(features=features or [])),
                raise_for_status=Mock())


class HistoricalTests(unittest.TestCase):
    def test_normalize_invalid_unknown_and_duplicates(self):
        malformed = feature("bad")
        malformed["geometry"]["coordinates"][0] = float("inf")
        df = normalize_features([feature(),feature(),feature("unknown",depth=None),feature("missing",mag=None),malformed])
        self.assertEqual(len(df),2)
        self.assertTrue(pd.isna(df.loc[df.id=="unknown","depth"]).all())
        self.assertEqual(str(df.time.dt.tz),"UTC")

    def test_pagination_fixed_cutoff_and_annual_zeros(self):
        get = Mock(side_effect=[response(count=3),response([feature("a"),feature("b")]),response([feature("c",year=2002)])])
        df = fetch_history(2000,2002,4,"2003-05-01T00:00:00Z",get=get,page_size=2)
        self.assertEqual(len(df),3)
        calls=get.call_args_list
        self.assertEqual(calls[1].kwargs["params"]["offset"],1)
        self.assertEqual(calls[2].kwargs["params"]["offset"],3)
        self.assertEqual(calls[0].kwargs["params"]["endtime"],"2002-12-31T23:59:59.999000+00:00")
        self.assertEqual(annual_counts(df,2000,2002).tolist(),[2,0,1])

    def test_refuses_truncated_catalog(self):
        with self.assertRaisesRegex(ValueError,"No se ha truncado"):
            fetch_history(2000,2001,3,"2001-01-01T00:00:00Z",get=Mock(return_value=response(count=6001)))
        with self.assertRaisesRegex(ValueError,"incompleto"):
            fetch_history(2000,2001,3,"2001-01-01T00:00:00Z",get=Mock(side_effect=[response(count=2),response([feature()])]))

    def test_empty_catalog_204(self):
        df = fetch_history(2000,2001,4,"2001-01-01T00:00:00Z",get=Mock(return_value=response(status=204)))
        self.assertTrue(df.empty)
        self.assertEqual(annual_counts(df,2000,2001).tolist(),[0,0])

    def test_animation_empty_years_clear_points_fixed_scales(self):
        df = normalize_features([feature(),feature("b",2002,depth=None)])
        fig=build_animation(df,2000,2002,accumulated=False)
        self.assertEqual([f.name for f in fig.frames],["2000","2001","2002"])
        self.assertEqual(fig.frames[1].data[0].x,())
        self.assertEqual(fig.frames[1].data[1].x,())
        self.assertEqual(fig.frames[1].traces,(3,4))
        self.assertEqual(fig.layout.coloraxis.cmax,300)
        self.assertEqual(len(fig.layout.shapes),60)
        self.assertTrue(any(a.text=="Prof. · km" for a in fig.frames[1].layout.annotations))
        self.assertEqual(fig.frames[0].data[0].marker.size[0],magnitude_size(5))
        cumulative=build_animation(df,2000,2002)
        self.assertEqual(len(cumulative.frames[-1].data[0].x)+len(cumulative.frames[-1].data[1].x),2)
        html=export_animation(fig).decode()
        self.assertIn('plotly.js',html)
        self.assertNotIn('src="https://cdn.plot.ly',html)

    def test_history_ui_does_not_fetch_recent_data(self):
        df=normalize_features([feature()])
        df.attrs.update(omitted=0,cutoff="2002-01-01T00:00:00Z")
        with patch("history_view.load_history",return_value=df) as historical_load, patch("requests.get",side_effect=AssertionError("No recent request allowed")):
            app=AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"),default_timeout=15)
            app.query_params["view"]="history"
            app.run()
            self.assertFalse(app.exception)
            historical_load.assert_called_once()
            self.assertEqual(app.metric[0].value,"1")
            app.segmented_control(key="history_mode").set_value("annual").run()
            self.assertFalse(app.exception)
            app.selectbox(key="app_lang").select("EN").run()
            self.assertFalse(app.exception)
            self.assertEqual(app.metric[0].label,"Cataloged events")
            app.slider(key="history_years").set_value((2000,2002))
            next(button for button in app.button if button.label=="Load archive").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(historical_load.call_args.args[:3],(2000,2002,4.))
            app.button(key="history_export").click().run()
            self.assertFalse(app.exception)
            self.assertTrue(any(e.label=="Download HTML animation" for e in app.get("download_button")))


if __name__ == "__main__":
    unittest.main()
