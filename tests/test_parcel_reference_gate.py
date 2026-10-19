import unittest
from tools.parcelas.reference_gate import assess_reference


class ReferenceGateTests(unittest.TestCase):
    def test_human_label_alone_not_parcel_validation(self):
        result=assess_reference({'human_interpreted':True,'independent':True,'parcel_boundary_verified':False,'change_date_verified':False})
        self.assertFalse(result['usable_for_parcel_change_validation'])
        self.assertIn('parcel_boundary_verified',result['missing'])

    def test_model_label_cannot_be_ground_truth(self):
        result=assess_reference({'human_interpreted':False,'independent':True,'parcel_boundary_verified':True,'change_date_verified':True})
        self.assertFalse(result['usable_for_parcel_change_validation'])

    def test_complete_reference_still_not_eudr_decision(self):
        result=assess_reference(dict.fromkeys(['human_interpreted','independent','parcel_boundary_verified','change_date_verified'],True))
        self.assertTrue(result['usable_for_parcel_change_validation'])
        self.assertEqual(result['compliance_decision'],'not_performed')

    def test_unknown_is_not_true(self):
        self.assertFalse(assess_reference({'human_interpreted':'yes'})['usable_for_parcel_change_validation'])
