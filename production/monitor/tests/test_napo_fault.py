import io
import unittest
import zipfile

from prepare_napo_fault import CITY_IDS, parse_cities, parse_reviewed
from reel_napo_fault import SCENES, EXTENT, ZOOM_EXTENT, BOX, viewport, locate, schematic_slip


def gazetteer(feature_class="P"):
    rows = []
    for identity, name in CITY_IDS.items():
        fields = [""]*19
        fields[0], fields[1], fields[4], fields[5] = identity, name, "-0.99", "-77.81"
        fields[6], fields[7], fields[8], fields[10] = feature_class, "PPL", "EC", "23"
        rows.append("\t".join(fields))
    raw = io.BytesIO()
    with zipfile.ZipFile(raw, "w") as archive:
        archive.writestr("EC.txt", "\n".join(rows))
    return raw.getvalue()


class FaultReelTests(unittest.TestCase):
    def test_city_markers_are_populated_places_not_canton_centroids(self):
        cities = parse_cities(gazetteer())
        self.assertEqual({c["name"] for c in cities}, set(CITY_IDS.values()))
        with self.assertRaisesRegex(ValueError, "feature class"):
            parse_cities(gazetteer("A"))

    def test_second_case_keeps_reviewed_bulletin_type_not_preliminary(self):
        body = """[REVISADO]
Evento: igepn2026qghw
Ocurrido: 2026-08-19 22:21:38
Mag.: 3.7MLv
Prof.: 3.0 km
Lat.: 1.101° S
Long.: 78.025° W"""
        raw = '<div data-post="SismosVolcanesIGEPN/12282"><div class="tgme_widget_message_text">'+body.replace("\n", "<br>")+"</div></div>"
        row = parse_reviewed(raw.encode())
        self.assertEqual(row["id"], "igepn2026qghw")
        self.assertEqual(row["magnitude_type"], "MLv")
        self.assertEqual(row["depth_km"], 3)
        self.assertEqual(row["longitude"], -78.025)
        with self.assertRaisesRegex(ValueError, "reviewed bulletin"):
            parse_reviewed(raw.replace("REVISADO", "PRELIMINAR").encode())

    def test_always_map_first_then_question_map_zoom_and_new_lesson(self):
        names = [scene[2] for scene in SCENES]
        self.assertEqual(names[:5], ["mapa_historico", "pregunta_2026", "mapa_2026", "zoom_tena", "que_es_falla"])
        self.assertTrue(set(names).isdisjoint({"historia_1987", "boletines", "profundidad", "conceptos"}))
        self.assertEqual((SCENES[0][0], SCENES[-1][1]), (0, 100))
        self.assertTrue(all(a[1] == b[0] for a, b in zip(SCENES, SCENES[1:])))

    def test_camera_zoom_changes_viewport_not_coordinates(self):
        self.assertEqual(viewport(0), EXTENT)
        self.assertEqual(viewport(1), ZOOM_EXTENT)
        self.assertEqual(viewport(-1), EXTENT)
        self.assertEqual(viewport(2), ZOOM_EXTENT)
        lon, lat = -77.81315, -.9961
        for phase in (0, .25, .5, .75, 1):
            extent = viewport(phase)
            x, y = locate(lon, lat, extent)
            self.assertTrue(BOX[0] < x < BOX[2] and BOX[1] < y < BOX[3])
            recovered_lon = extent[0]+(x-BOX[0])/(BOX[2]-BOX[0])*(extent[1]-extent[0])
            recovered_lat = extent[3]-(y-BOX[1])/(BOX[3]-BOX[1])*(extent[3]-extent[2])
            self.assertAlmostEqual(recovered_lon, lon)
            self.assertAlmostEqual(recovered_lat, lat)

    def test_conceptual_slip_is_one_release_not_periodic_prediction(self):
        values = [schematic_slip(t) for t in (0, 1.9, 2, 2.15, 2.3, 2.6, 4, 11.9)]
        self.assertEqual(values[:3], [0, 0, 0])
        self.assertEqual(values[-3:], [52, 52, 52])
        self.assertEqual(values, sorted(values))
