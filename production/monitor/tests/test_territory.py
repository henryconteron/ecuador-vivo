import unittest

from prepare_territory import BulletinParser, parse_bulletin
from reel_territory import BOX, EXTENT, SCENES, depth_y, project
from prepare_napo_history import REPORTS, verify_report
from reel_napo_history import SCENES as HISTORY_SCENES, historical_count


SAMPLE = """[REVISADO]
Evento: igepn2026lsvn
Ocurrido: 2026-06-16 15:12:34
Mag.: 3.7M
Prof.: 21.0 km
Lat.: 1.170° S
Long.: 77.810° W
Localizado: a 19.23 km de Tena, Napo"""


class TerritoryTests(unittest.TestCase):
    def test_case_keeps_original_type_and_local_time(self):
        row = parse_bulletin({"post": "SismosVolcanesIGEPN/11947", "text": SAMPLE})
        self.assertEqual(row["magnitude_type"], "M")  # Never invent Mw/MLv.
        self.assertEqual(row["depth_km"], 21)
        self.assertEqual(row["latitude"], -1.17)
        self.assertEqual(row["longitude"], -77.81)
        self.assertEqual(row["local_time"], "2026-06-16T15:12:34-05:00")
        self.assertEqual(row["utc_time"], "2026-06-16T20:12:34+00:00")

    def test_missing_depth_is_not_imputed_zero(self):
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            parse_bulletin({"post": "SismosVolcanesIGEPN/11947", "text": SAMPLE.replace("Prof.: 21.0 km", "")})

    def test_official_parser_excludes_views_and_published_time(self):
        parser = BulletinParser()
        parser.feed('<div data-post="SismosVolcanesIGEPN/11947"><div class="tgme_widget_message_text">'
                    + SAMPLE.replace("\n", "<br>") + '</div><span>2.39K views 20:18</span></div>')
        self.assertEqual(len(parser.messages), 1)
        self.assertNotIn("views", parser.messages[0]["text"])
        self.assertTrue(parse_bulletin(parser.messages[0])["local_time"].endswith("15:12:34-05:00"))

    def test_two_bulletins_are_one_event(self):
        after = parse_bulletin({"post": "SismosVolcanesIGEPN/11947", "text": SAMPLE})
        before = parse_bulletin({"post": "SismosVolcanesIGEPN/11946",
                                "text": SAMPLE.replace("REVISADO", "PRELIMINAR").replace("21.0 km", "8.0 km")})
        self.assertEqual(before["id"], after["id"])
        self.assertNotEqual(before["depth_km"], after["depth_km"])

    def test_depth_axis_is_fixed_and_positive_down(self):
        self.assertEqual(depth_y(0), 650)
        self.assertEqual(depth_y(30), 1130)
        self.assertLess(depth_y(8), depth_y(21))
        self.assertAlmostEqual(depth_y(8), 778)
        self.assertAlmostEqual(depth_y(21), 986)
        for invalid in (-1, 31, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                depth_y(invalid)

    def test_map_projection_and_timeline_are_consistent(self):
        west, east, south, north = EXTENT
        self.assertEqual(project(west, north), BOX[:2])
        self.assertEqual(project(east, south), BOX[2:])
        point = project(-77.81, -1.17)
        self.assertTrue(BOX[0] < point[0] < BOX[2] and BOX[1] < point[1] < BOX[3])
        self.assertEqual((SCENES[0][0], SCENES[-1][1]), (0, 80))
        self.assertTrue(all(a[1] == b[0] for a, b in zip(SCENES, SCENES[1:])))

    def test_historical_selection_is_chronological_and_not_homogenized(self):
        events = [row for report in REPORTS for row in report["events"]]
        self.assertEqual(len(events), 6)
        self.assertEqual([row["date"] for row in events], sorted(row["date"] for row in events))
        self.assertEqual([row["type"] for row in events], ["Ms", "Ms", "MLv", "MLv", "Mw", "Mw"])
        for row in events[:2]:
            self.assertIsNone(row["depth_km"])
            self.assertIsNone(row["latitude"])
            self.assertIsNone(row["longitude"])

    def test_historical_verification_rejects_missing_source_values(self):
        report = REPORTS[1]
        source = "18 de junio de 2023 5.3 MLv 0.66 77.61 2.2km"
        self.assertIn("2.2km", verify_report(report, source.encode()))
        with self.assertRaisesRegex(ValueError, "Unverified"):
            verify_report(report, source.replace("2.2km", "").encode())

    def test_history_precedes_2026_question_and_case(self):
        names = [scene[2] for scene in HISTORY_SCENES]
        self.assertEqual(names[:4], ["historia_1987", "mapa_historico", "pregunta_2026", "mapa_2026"])
        self.assertEqual((HISTORY_SCENES[0][0], HISTORY_SCENES[-1][1]), (0, 109))
        self.assertTrue(all(a[1] == b[0] for a, b in zip(HISTORY_SCENES, HISTORY_SCENES[1:])))
        self.assertEqual([historical_count(t) for t in (0, 4.49, 4.5, 9, 13.5, 17.99)], [1, 1, 2, 3, 4, 4])

    def test_selected_historical_coordinates_fit_reference_map(self):
        rows = [r for source in REPORTS for r in source["events"] if r["latitude"] is not None]
        self.assertEqual(len(rows), 4)
        for row in rows:
            x, y = project(row["longitude"], row["latitude"])
            self.assertTrue(BOX[0] < x < BOX[2] and BOX[1] < y < BOX[3])
