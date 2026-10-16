"""Bounded presentation work, with the same native-source verification gates."""
import base64
import copy
import io
import unittest
from unittest.mock import patch
from PIL import Image
import test_sig_raster as fixtures


class SigInteractionPerformanceTests(unittest.TestCase):
    setUp = fixtures.RasterTests.setUp
    tearDown = fixtures.RasterTests.tearDown
    pair = fixtures.RasterTests.pair
    source = fixtures.RasterTests.source

    def test_resources_navigation_keeps_scientific_project_intact(self):
        from types import SimpleNamespace
        from studio_sig_shell import shell_event
        project, _ = self.pair()
        before = copy.deepcopy(project)
        session = SimpleNamespace(project=project, state={})
        with patch('studio_sig_shell.st.rerun'):
            shell_event(session, {'action': 'navigate', 'section': 'Recursos'})
        self.assertEqual(session.state['section'], 'Recursos')
        self.assertEqual(project, before)

    def test_series_opacity_is_one_pure_atomic_command(self):
        from studio_sig_layers import series_style_command, layer_command, workspace_for
        project, ids = self.pair()
        before = copy.deepcopy(project)
        expected = project
        for lid in ids:
            style = {**workspace_for(expected)['layers'][lid]['style'], 'opacity': .35}
            expected = layer_command(expected, {'action': 'style', 'layer_id': lid, 'style': style})
        actual = series_style_command(project, .35)
        self.assertEqual(actual, expected)
        self.assertEqual(project, before)
        for field in ('calculations', 'datasets', 'scenes', 'timeline', 'media'):
            self.assertEqual(actual['studio'][field], project['studio'][field])
        for invalid in (True, -1, 1.01, float('nan'), '0.5'):
            with self.assertRaises(ValueError):
                series_style_command(project, invalid)
            self.assertEqual(project, before)

    def test_series_style_still_rejects_changed_native_bytes(self):
        from studio_sig_layers import series_style_command
        from pathlib import Path
        project, ids = self.pair()
        source = self.source(project, ids[0])
        path = Path(source['path'])
        path.write_bytes(path.read_bytes() + b'changed')
        with self.assertRaises(ValueError):
            series_style_command(project, .2)

    def test_warm_png_reuses_identical_encoded_bytes_without_reencoding(self):
        from studio_sig_raster import encoded_representation, representation, settings, _IMAGES
        project, ids = self.pair()
        source = self.source(project, ids[0])
        scale = settings([source])
        _IMAGES.clear()
        encoded, box = encoded_representation(source, scale, size=32)
        with patch.object(Image.Image, 'save', side_effect=AssertionError('Warm image must not be re-encoded')):
            repeated, other_box = encoded_representation(source, scale, size=32)
        self.assertEqual(repeated, encoded)
        self.assertEqual(other_box, box)
        with Image.open(io.BytesIO(base64.b64decode(encoded.split(',', 1)[1]))) as decoded:
            with representation(source, scale, size=32)[0] as original:
                self.assertEqual(decoded.tobytes(), original.tobytes())
        # Encoded presentation is never permission to ignore changed originals.
        from pathlib import Path
        path = Path(source['path'])
        path.write_bytes(path.read_bytes() + b'changed')
        with self.assertRaises(ValueError):
            encoded_representation(source, scale, size=32)


if __name__ == '__main__':
    unittest.main()
