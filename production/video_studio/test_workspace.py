"""Shared authoring/export workflow; does not download data or create jobs."""
import unittest
from unittest.mock import Mock, patch

from workspace import PHASES, authoring_config, export_check


class WorkspaceTests(unittest.TestCase):
    def test_four_distinct_phases(self):
        self.assertEqual(PHASES, ('Datos', 'Maqueta', 'Montaje', 'Exportar'))

    def test_authoring_copy_preserves_sources_values_and_removed_elements(self):
        original = {'units': '°C', 'offset': -273.15,
                    'visual_layout': {'map': {'label': {'deleted': True}}}}
        result = authoring_config(original)
        self.assertTrue(result['visual_layout']['full_canvas'])
        self.assertNotIn('full_canvas', original['visual_layout'])
        self.assertEqual(result['units'], original['units'])
        self.assertEqual(result['offset'], original['offset'])
        self.assertTrue(result['visual_layout']['map']['label']['deleted'])
        result['visual_layout']['map']['label']['deleted'] = False
        self.assertTrue(original['visual_layout']['map']['label']['deleted'])

    @patch('workspace.st')
    def test_export_checks_current_design_without_an_old_preview(self, ui):
        config = {'duration': 2., 'endcard_enabled': True, 'endcard_duration': 3.,
                  'visual_layout': {'map': {'label': {'deleted': True}}}}
        map_renderer, end_renderer = Mock(), Mock()
        self.assertTrue(export_check(config, map_renderer, end_renderer))
        map_renderer.assert_called_once_with(config)
        end_renderer.assert_called_once_with(config)
        ui.error.assert_not_called()

    @patch('workspace.st')
    def test_invalid_current_data_blocks_export(self, ui):
        renderer = Mock(side_effect=ValueError('Datos incompletos'))
        self.assertFalse(export_check({'duration': 2.}, renderer))
        self.assertIn('Datos incompletos', ui.error.call_args.args[0])

    @patch('workspace.st')
    def test_endcard_requested_without_renderer_blocks_export(self, ui):
        self.assertFalse(export_check({'duration': 2., 'endcard_enabled': True,
                                      'endcard_duration': 3.}, Mock()))
        ui.error.assert_called_once()


if __name__ == '__main__':
    unittest.main()
