import unittest
from shapely.geometry import box
from tools.parcelas.field_observations import support,create_plan,BASE

class FieldObservationsTests(unittest.TestCase):
    def test_edge_cells_are_not_full_cells(self):
        inside,full=support(box(5,5,35,35),[0,0,40,40],10)
        self.assertEqual(int(full.sum()),4)
        self.assertGreater(int(inside.sum()),int(full.sum()))
        self.assertFalse((full&~inside).any())

    @unittest.skipUnless((BASE/'RF05/catalog-2020.json').exists(),'Local field catalogue integration fixture unavailable')
    def test_field_plan_is_bounded_and_same_orbit(self):
        plan=create_plan()
        self.assertLessEqual(len(plan['observations']),24)
        self.assertEqual(set(plan['fields']),{'RF05','RF06'})
        for f in plan['fields'].values():
            self.assertEqual(f['epsg'],32717)
            self.assertEqual(f['bounds'][2]-f['bounds'][0],200)
        for pair in plan['pairs']:
            self.assertLessEqual(pair['separation_days'],12)
            self.assertIn(pair['period'],('2020','2025'))

if __name__=='__main__': unittest.main()
