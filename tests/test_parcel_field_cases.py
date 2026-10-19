import unittest
from tools.parcelas.field_cases import eligible_plot


class FieldCasesTests(unittest.TestCase):
    def test_repaired_requires_review(self):
        self.assertFalse(eligible_plot({'topological_repair_applied':True,'geometry_review':'required_before_analysis'}))

    def test_original_valid_allowed(self):
        self.assertTrue(eligible_plot({'topological_repair_applied':False,'geometry_review':'original_2D_geometry_valid'}))

    def test_unknown_not_automatically_accepted(self):
        self.assertFalse(eligible_plot({}))
