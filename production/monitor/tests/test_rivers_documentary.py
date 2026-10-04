"""Editorial, scientific, motion and narration checks for landscape documentary."""
import json
from pathlib import Path
import unittest
import numpy as np
from reel_rivers_documentary import BEATS, Design, FOLDER, SOURCES, index_mask, plan, FPS, VOICE


class DocumentaryTests(unittest.TestCase):
    def test_editorial_order_and_scope(self):
        ids=[b[0] for b in BEATS]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(ids[:3],["dryphoto","wetphoto","reveal"])
        self.assertLess(ids.index("sensor"),ids.index("contrast"))
        self.assertLess(ids.index("contrast"),ids.index("rulemove"))
        text=" ".join(b[1] for b in BEATS)
        for phrase in ["no son umbrales calibrados", "no mide mercurio", "No fue una recuperación permanente", "Imagínate que un amigo", "inventaría los estados intermedios"]:
            self.assertIn(phrase,text)
        self.assertNotIn("Nilo",text)
        self.assertTrue(all(s["rights"]=="Public Domain" for s in SOURCES))
        self.assertEqual([s["date"] for s in SOURCES],["2014-03-20","2014-03-29"])

    def test_invalid_values_never_become_water(self):
        values=np.array([[-.1,.0,.1,.3,np.nan,.8]])
        valid=np.array([[True,True,True,True,True,False]])
        np.testing.assert_array_equal(index_mask(values,valid,0),[[False,False,True,True,False,False]])
        np.testing.assert_array_equal(index_mask(values,valid,.2),[[False,False,False,True,False,False]])

    def test_render_layout_and_data(self):
        if not (FOLDER/"sources_manifest.json").exists():self.skipTest("Local production assets absent")
        d=Design()
        self.assertEqual(int(index_mask(d.values,d.common,0).sum()),947)
        self.assertEqual(int(index_mask(d.values,d.common,.2).sum()),681)
        for beat in BEATS:
            for t in [0,.4,1]:
                self.assertEqual(d.render(beat,t,"Un subtítulo legible para comprobar el encuadre").size,(1920,1080))
        for sid in ["dryphoto","wetphoto","reveal","stones","bed","pool","discharge","sensor","bands","rulemove","zoom","middle","cloud"]:
            beat=next(b for b in BEATS if b[0]==sid)
            self.assertNotEqual(d.render(beat,.1).tobytes(),d.render(beat,.8).tobytes(),sid)

    def test_narration_is_complete_and_timed(self):
        if not all((FOLDER/f"times_{b[0]}.json").exists() for b in BEATS):self.skipTest("Voices still being generated")
        cursor=0
        for beat,scene in zip(BEATS,plan()):
            self.assertEqual(scene["start_frame"],cursor)
            self.assertGreater(scene["frames"]/FPS,scene["audio_seconds"])
            timing=json.loads((FOLDER/f"times_{beat[0]}.json").read_text(encoding="utf-8"))
            self.assertEqual(timing["voice"],VOICE)
            self.assertNotIn("\ufffd"," ".join(w["text"] for w in timing["words"]))
            self.assertGreaterEqual(len(timing["words"]),len(beat[1].split())*.85)
            self.assertLessEqual(timing["words"][-1]["end"],timing["seconds"]+.3)
            for cue in scene["cues"]:
                self.assertLess(cue["start"],cue["end"])
                self.assertLessEqual(cue["end"],scene["frames"]/FPS)
            cursor+=scene["frames"]


if __name__=="__main__":unittest.main()
