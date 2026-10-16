"""Logical temporal visibility is atomic and never changes scientific records."""
import copy
import unittest
from unittest.mock import patch
import test_sig_raster as fixtures


class SeriesVisibilityTests(unittest.TestCase):
    setUp=fixtures.RasterTests.setUp
    tearDown=fixtures.RasterTests.tearDown
    pair=fixtures.RasterTests.pair

    def test_one_copy_one_validation_preserves_sources_science_and_calendar(self):
        from studio_sig_layers import series_visibility_command,workspace_for,validate_map_workspace
        project,ids=self.pair();before=copy.deepcopy(project)
        with patch('studio_sig_layers.validate_map_workspace',wraps=validate_map_workspace) as validate:
            changed=series_visibility_command(project,False)
        self.assertLessEqual(validate.call_count,2)
        self.assertTrue(all(not workspace_for(changed)['layers'][lid]['visible'] for lid in ids))
        self.assertEqual(project,before)
        for key in ('sources','regions','views'):self.assertEqual(changed['studio']['geography'][key],before['studio']['geography'][key])
        for key in ('calculations','datasets','scenes','timeline'):self.assertEqual(changed['studio'][key],before['studio'][key])
        self.assertEqual(workspace_for(changed)['raster_time'],workspace_for(before)['raster_time'])
        self.assertEqual(series_visibility_command(changed,True),project)
        with self.assertRaises(ValueError):series_visibility_command(project,1)
