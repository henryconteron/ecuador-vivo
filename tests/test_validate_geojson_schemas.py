import copy
import json
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts.validate_geojson_schemas import ROOT, read_json, validate_catalog


class GeoJsonSchemaValidationTests(unittest.TestCase):
    def test_public_catalogs_satisfy_their_schemas(self):
        pairs = (
            ("fallas.schema.json", "fallas.geojson"),
            ("estructuras.schema.json", "estructuras.geojson"),
        )
        for schema_name, data_name in pairs:
            with self.subTest(data=data_name):
                errors = validate_catalog(
                    ROOT / "data/schemas" / schema_name,
                    ROOT / "data/geojson" / data_name,
                )
                self.assertEqual(errors, [])

    def test_invalid_catalog_reports_property_and_feature_count(self):
        schema_path = ROOT / "data/schemas/fallas.schema.json"
        document = copy.deepcopy(read_json(ROOT / "data/geojson/fallas.geojson"))
        document["metadata"]["feature_count"] = 1
        del document["features"][0]["properties"]["nombre"]

        with tempfile.TemporaryDirectory() as directory:
            invalid_path = Path(directory) / "fallas.geojson"
            invalid_path.write_text(json.dumps(document), encoding="utf-8")
            errors = validate_catalog(schema_path, invalid_path)

        self.assertTrue(any("nombre" in error for error in errors))
        self.assertTrue(any("feature_count" in error for error in errors))

    def test_schemas_are_valid_draft_2020_12_documents(self):
        for schema_path in (ROOT / "data/schemas").glob("*.schema.json"):
            with self.subTest(schema=schema_path.name):
                Draft202012Validator.check_schema(read_json(schema_path))


if __name__ == "__main__":
    unittest.main()
