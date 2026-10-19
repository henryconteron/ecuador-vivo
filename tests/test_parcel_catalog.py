"""Offline contracts; synthetic fixtures do not validate deforestation detection."""
import unittest
from unittest.mock import patch
from io import BytesIO
import json

from tools.parcelas.catalog import validate_parcel, summarize_items, build_search_url, discover


class ParcelCatalogTests(unittest.TestCase):
    def parcel(self):
        return {"type": "FeatureCollection", "features": [{"type": "Feature",
                "properties": {}, "geometry": {"type": "Polygon", "coordinates": [
                    [[-2.74, 6.82], [-2.73, 6.82], [-2.73, 6.83], [-2.74, 6.82]]]}}]}

    def test_polygon_is_validated_and_measured(self):
        result = validate_parcel(self.parcel())
        self.assertGreater(result["area_ha"], 0)
        self.assertEqual(result["bbox"], [-2.74, 6.82, -2.73, 6.83])

    def test_rejects_point_and_empty_or_multiple_features(self):
        for features in ([], self.parcel()["features"] * 2,
                         [{"geometry": {"type": "Point", "coordinates": [-2, 6]}}]):
            with self.subTest(features=features), self.assertRaises(ValueError):
                validate_parcel({"type": "FeatureCollection", "features": features})

    def test_rejects_wrong_crs_and_unclosed_ring(self):
        data = self.parcel()
        data["crs"] = {"properties": {"name": "EPSG:3857"}}
        with self.assertRaises(ValueError):
            validate_parcel(data)
        data = self.parcel()
        data["features"][0]["geometry"]["coordinates"][0][-1] = [-2.74, 6.821]
        with self.assertRaises(ValueError):
            validate_parcel(data)

    def test_url_encodes_bounded_dates(self):
        url = build_search_url("sentinel-1-grd", [-3, 6, -2, 7], "2025-03-01", "2025-04-01")
        self.assertIn("limit=100", url)
        with self.assertRaises(ValueError):
            build_search_url("sentinel-1-grd", [-3, 6, -2, 7], "2025-04-01", "2025-03-01")

    def test_groups_orbits_and_keeps_clouds_unknown(self):
        items = []
        for orbit in (45, 147, None):
            items.append({"id": str(orbit), "collection": "sentinel-1-grd",
                          "properties": {"datetime": "2025-03-01T00:00:00Z",
                                         "sat:relative_orbit": orbit,
                                         "sat:orbit_state": "ascending",
                                         "sar:instrument_mode": "IW",
                                         "sar:polarizations": ["VV", "VH"]}})
        result = summarize_items(items)
        self.assertEqual(len(result["radar_groups"]), 2)
        self.assertEqual(len(result["radar_unusable_metadata"]), 1)
        self.assertIsNone(result["items"][0]["scene_cloud_percent"])
        self.assertEqual(result["analysis_status"], "metadata_only_not_processed")

    def test_duplicate_ids_do_not_inflate_count(self):
        item = {"id": "a", "collection": "sentinel-2-l2a", "properties": {}}
        self.assertEqual(summarize_items([item, item])["item_count"], 1)

    def test_reversed_multipart_rings_do_not_cancel_area(self):
        data = self.parcel()
        polygon = [[[-2.74, 6.82], [-2.739, 6.82], [-2.739, 6.821], [-2.74, 6.82]]]
        single = self.parcel()
        single["features"][0]["geometry"]["coordinates"] = polygon
        second = [[[x + .02, y] for x, y in reversed(polygon[0])]]
        data["features"][0]["geometry"] = {"type": "MultiPolygon", "coordinates": [polygon, second]}
        self.assertAlmostEqual(validate_parcel(data)["area_ha"],
                               validate_parcel(single)["area_ha"] * 2, places=5)

    def test_pagination_bound_is_reported_and_end_is_exclusive(self):
        page = {"type": "FeatureCollection", "features": [
            {"properties": {"datetime": "2025-03-01T00:00:00Z"}},
            {"properties": {"datetime": "2025-04-01T00:00:00Z"}}],
            "links": [{"rel": "next", "href": "https://stac.dataspace.copernicus.eu/v1/search?page=2"}]}
        with patch("tools.parcelas.catalog.urlopen", return_value=BytesIO(json.dumps(page).encode())):
            items, complete = discover("sentinel-1-grd", [-3, 6, -2, 7], "2025-03-01", "2025-04-01", max_pages=1)
        self.assertEqual(len(items), 1)
        self.assertFalse(complete)

    def test_external_pagination_is_rejected(self):
        page = {"type": "FeatureCollection", "features": [],
                "links": [{"rel": "next", "href": "https://example.com/search"}]}
        with patch("tools.parcelas.catalog.urlopen", return_value=BytesIO(json.dumps(page).encode())):
            with self.assertRaises(ValueError):
                discover("sentinel-1-grd", [-3, 6, -2, 7], "2025-03-01", "2025-04-01")


if __name__ == "__main__":
    unittest.main()
