"""Local preflight contracts; these tests do not validate SAR processing."""
from pathlib import Path
import tempfile
import unittest

from tools.parcelas.preflight import inspect_graph, missing_parameters


class PreflightTests(unittest.TestCase):
    def test_graph_has_eight_operators_and_required_inputs(self):
        graph = inspect_graph(Path("tools/parcelas/sentinel1-grd-diagnostic.xml"))
        self.assertEqual(len(graph), 8)
        self.assertEqual(graph[0]["operator"], "Read")
        self.assertIn("continueOnFail", graph[1]["parameters"])

    def test_parameters_are_checked_against_documented_xml(self):
        help_text = "<parameters><file>file</file><copyMetadata>boolean</copyMetadata></parameters>"
        self.assertEqual(missing_parameters(["file", "unexpected"], help_text), ["unexpected"])

    def test_graph_with_unknown_dependency_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.xml"
            path.write_text('<graph><node id="a"><operator>Read</operator><sources><sourceProduct refid="missing"/></sources><parameters/></node></graph>')
            with self.assertRaises(ValueError):
                inspect_graph(path)


if __name__ == "__main__":
    unittest.main()
