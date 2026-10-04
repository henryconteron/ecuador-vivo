from datetime import datetime, timezone
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

import pandas as pd
from streamlit.testing.v1 import AppTest

from education import energy_ratio, depth_band, mainland_time, event_url, depth_svg, subduction_svg
from historical import build_animation, normalize_features, export_animation

APP = str(Path(__file__).resolve().parents[1] / "app.py")


class LiteracyTests(unittest.TestCase):
    def test_energy_logarithmic_and_direction(self):
        self.assertAlmostEqual(energy_ratio(6,5),31.6227766)
        self.assertAlmostEqual(energy_ratio(7,5),1000)
        self.assertEqual(energy_ratio(5,5),1)
        self.assertAlmostEqual(energy_ratio(4,5)*energy_ratio(5,4),1)
        for invalid in [float("nan"),float("inf"),-1,11]:
            with self.assertRaises(ValueError):
                energy_ratio(invalid,5)

    def test_depth_boundaries_and_missing(self):
        for depth, expected in [(0,"shallow"),(69.99,"shallow"),(70,"intermediate"),(299.99,"intermediate"),(300,"deep"),(700,"deep"),(None,"unknown"),(-2,"unknown"),(float("nan"),"unknown")]:
            self.assertEqual(depth_band(depth),expected)

    def test_clock_and_safe_links(self):
        time=mainland_time(datetime(2026,1,1,2,tzinfo=timezone.utc))
        self.assertEqual(time.strftime("%Y-%m-%d %H:%M"),"2025-12-31 21:00")
        with self.assertRaises(ValueError):
            mainland_time(datetime(2026,1,1))
        self.assertTrue(event_url("us20005j32").endswith("/us20005j32"))
        self.assertIsNone(event_url('../bad"<script>'))

    def test_schematics_accessible_and_validated(self):
        self.assertIn('role="img"',depth_svg(700))
        self.assertIn("Hipocentro",depth_svg(20))
        self.assertIn("Epicenter",depth_svg(20,True))
        self.assertIn("Nazca",subduction_svg())
        for invalid in [-1,701,float("nan")]:
            with self.assertRaises(ValueError):
                depth_svg(invalid)

    def test_manual_opening_year_and_speed(self):
        feature=dict(id="test",geometry=dict(coordinates=[-79,-1,20]),properties=dict(time=946684800000,mag=5,place="Test"))
        df=normalize_features([feature])
        fig=build_animation(df,1999,2001,initial_year=1999,frame_ms=1200)
        self.assertEqual(fig.layout.sliders[0].active,0)
        self.assertEqual(len(fig.data[3].x),0)
        self.assertEqual(fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"],1200)
        self.assertIn("1999",fig.layout.annotations[0].text)
        with self.assertRaises(ValueError):
            build_animation(df,1999,2001,initial_year=1900)

    def test_download_teaches_in_selected_language(self):
        df=normalize_features([])
        df.attrs.update(minimum=4,cutoff='2026-10-02T00:00:00Z')
        for en,phrase in [(False,"Aprende a leer"),(True,"Read Ecuador's seismic memory")]:
            html=export_animation(build_animation(df,2000,2001,english=en)).decode()
            self.assertIn(phrase,html)
            self.assertIn("2026-10-02T00:00:00Z",html)
            self.assertIn("science-earthquakes",html)
            self.assertLess(html.index(phrase),html.index('class="plotly-graph-div"'))


class ClassroomUITests(unittest.TestCase):
    def test_classroom_offline_labs_and_language(self):
        with patch("requests.get",side_effect=AssertionError("Classroom must not fetch a catalog")):
            app=AppTest.from_file(APP,default_timeout=15)
            app.query_params["view"]="learn"
            app.run()
            self.assertFalse(app.exception)
            self.assertEqual(app.title[0].value,"Entender el pulso.")
            self.assertEqual(len(app.get("image")),1)
            app.segmented_control(key="learn_section").set_value("magnitude").run()
            self.assertFalse(app.exception)
            self.assertEqual(app.metric[0].value,"31.62 ×")
            app.slider(key="learn_mag_a").set_value(4.).run()
            self.assertFalse(app.exception)
            self.assertEqual(app.metric[0].value,"0.03 ×")
            app.segmented_control(key="learn_section").set_value("depth").run()
            app.slider(key="learn_depth").set_value(300).run()
            self.assertFalse(app.exception)
            self.assertEqual(len(app.get("image")),1)
            self.assertTrue(any("Profundo" in m.value for m in app.markdown))
            app.selectbox(key="app_lang").select("EN").run()
            self.assertFalse(app.exception)
            self.assertEqual(app.title[0].value,"Understand the pulse.")
            self.assertEqual(app.segmented_control(key="learn_section").value,"depth")
            self.assertEqual(app.slider(key="learn_depth").value,300)

    def test_quiz_requires_answers_explains_and_resets(self):
        with patch("requests.get",side_effect=AssertionError("No catalog")):
            app=AppTest.from_file(APP,default_timeout=15)
            app.query_params["view"]="learn"
            app.run()
            app.segmented_control(key="learn_section").set_value("quiz").run()
            next(b for b in app.button if b.label=="Revisar mis respuestas").click().run()
            self.assertFalse(app.exception)
            self.assertTrue(app.info)
            self.assertFalse(app.success)
            for key,answer in [("color","depth"),("empty","none"),("energy","thirtytwo"),("memory","past")]:
                app.radio(key=f"learn_quiz_{key}").set_value(answer)
            next(b for b in app.button if b.label=="Revisar mis respuestas").click().run()
            self.assertFalse(app.exception)
            self.assertIn("3 de 4",app.success[0].value)
            self.assertTrue(any("año vacío" in m.value for m in app.markdown))
            app.selectbox(key="app_lang").select("EN").run()
            self.assertFalse(app.exception)
            self.assertEqual(app.segmented_control(key="learn_section").value,"quiz")
            self.assertIn("3 of 4",app.success[0].value)
            app.button(key="learn_quiz_reset").click().run()
            self.assertFalse(app.exception)
            self.assertFalse(app.success)
            self.assertTrue(all(r.value is None for r in app.radio))

    def test_recent_unknown_depth_not_zero_or_assigned_to_fault(self):
        now=datetime.now(timezone.utc).timestamp()*1000
        features=[dict(id=f"edu{i}",geometry=dict(coordinates=[-79+i*.2,-1+i*.2,depth]),
                       properties=dict(time=now-i*100000,mag=4.5+i*.1,place="Test"))
                  for i,depth in enumerate([20,80,None])]
        response=Mock(status_code=200,json=Mock(return_value=dict(features=features)),raise_for_status=Mock())
        with patch("requests.get",return_value=response) as get:
            app=AppTest.from_file(APP,default_timeout=15).run()
            self.assertFalse(app.exception)
            catalog=app.dataframe[0].value
            unknown=catalog[catalog.profundidad_km.isna()]
            self.assertEqual(len(unknown),1)
            self.assertEqual(unknown.iloc[0].regimen,"N/D")
            self.assertIn("desconocida",unknown.iloc[0].falla_asociada)
            self.assertNotIn("Interfase de Subducción",catalog.regimen.tolist())
            self.assertIn("T",get.call_args.kwargs["params"]["endtime"])


if __name__=="__main__":
    unittest.main()
