import unittest
import numpy as np
from tools.parcelas.persistence import persistent_drop
from tools.parcelas.reforestree_reference import RangeReader,SIZE


class PersistenceTests(unittest.TestCase):
    def test_three_observations_required_not_one_outlier(self):
        before=np.ones((3,2,2)); after=np.ones((3,2,2)); after[0]=.1
        self.assertFalse(persistent_drop(before,after,np.ones_like(before,dtype=bool),np.ones_like(after,dtype=bool)).any())

    def test_sustained_signal_drop_marked_for_review(self):
        a=np.ones((3,2,2)); b=a*.25
        self.assertTrue(persistent_drop(a,b,a.astype(bool),a.astype(bool)).all())

    def test_missing_is_not_change(self):
        a=np.ones((3,2,2)); mask=a.astype(bool); mask[1]=False
        self.assertFalse(persistent_drop(a,a*.1,mask,np.ones_like(mask)).any())

    def test_reader_rejects_full_archive(self):
        with self.assertRaises(ValueError): RangeReader().read(SIZE)

    def test_reader_rejects_bad_offset(self):
        with self.assertRaises(ValueError): RangeReader().seek(-1)
