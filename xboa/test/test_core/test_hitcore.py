import sys
import unittest
import xboa.core
from xboa.core import Hitcore
from xboa.core import WeightContext

class HitcoreTest(unittest.TestCase):
    def test_alloc(self):
        a = Hitcore()
        b = a
        self.assertEqual(sys.getrefcount(a), 3)
        del b
        self.assertEqual(sys.getrefcount(a), 2)

    def test_get_vars(self):
        ref_get_vars = ['x', 'y', 'z', 't', 'px', 'py',
               'pz', 'energy', 'mass', 'local_weight', 'global_weight',
               'bx', 'by', 'bz', 'ex', 'ey', 'ez', 'sx', 'sy', 'sz', 'path_length',
               'proper_time', 'e_dep', 'charge', 'event_number', 'station', 'pid',
               'status', 'spill', 'particle_number']
        self.assertEqual(sorted(Hitcore.get_variables()),
                         sorted(ref_get_vars))

    def test_set_vars(self):
        self.assertEqual(sorted(Hitcore.set_variables()),
                         sorted(['x', 'y', 'z', 't', 'px', 'py',
               'pz', 'energy', 'mass', 'local_weight', 'global_weight', 'bx', 'by',
               'bz', 'ex', 'ey', 'ez', 'sx', 'sy', 'sz', 'path_length',
               'proper_time', 'e_dep', 'charge', 'event_number', 'station', 'pid',
               'status', 'spill', 'particle_number', 'eventNumber',
               'particleNumber']))

    def test_set(self):
        a = Hitcore()
        z_target = 112.0
        a.set('z',  z_target)
        try:
            a.set('bilbo', 114.0)
            raise KeyError('Expected exception for bad set variable')
        except:
            pass

    def test_get(self):
        a = Hitcore()
        z_target = 112.0
        a.set('z', z_target)
        if( abs(a.get('z') - z_target) > 1e-9):
            raise KeyError('get or set failed')
        try:
          a.get('bilbo')
          raise KeyError('Did not get expected exception for bad get variable')
        except:
          pass
        return 'pass'

    def test_global_weight(self):
        hitcore_list_1, hitcore_list_2 = [], []
        for spill in range(3):
            for event in range(3):
                for particle in range(3):
                    hitcore_1 = Hitcore()
                    hitcore_1.set('spill', spill)
                    hitcore_1.set('event_number', event)
                    hitcore_1.set('particle_number', particle)
                    hitcore_list_1.append(hitcore_1)
                    hitcore_2 = Hitcore()
                    hitcore_2.set('spill', spill)
                    hitcore_2.set('event_number', event)
                    hitcore_2.set('particle_number', particle)
                    hitcore_list_2.append(hitcore_2)

        for i, ref_hitcore in enumerate(hitcore_list_1):
            ref_hitcore.set('global_weight', 0.2)
            for hitcore_list in hitcore_list_1, hitcore_list_2:
                for j, test_hitcore in enumerate(hitcore_list):
                    if i == j:
                        self.assertAlmostEqual(
                                         test_hitcore.get('global_weight'), 0.2)
                    elif j < i:
                        self.assertAlmostEqual(
                                         test_hitcore.get('global_weight'), 0.9)
                    else:
                        self.assertAlmostEqual(
                                         test_hitcore.get('global_weight'), 1.0)
            ref_hitcore.set('global_weight', 0.9)

        Hitcore.clear_global_weights()
        for i, ref_hitcore in enumerate(hitcore_list):
            self.assertAlmostEqual(test_hitcore.get('global_weight'), 1.0)

    def test_weight_context(self):
        hitcore_list_1 = []
        for spill in range(3):
            for event in range(3):
                for particle in range(3):
                    hitcore_1 = Hitcore()
                    hitcore_1.set('spill', spill)
                    hitcore_1.set('event_number', event)
                    hitcore_1.set('particle_number', particle)
                    hitcore_list_1.append(hitcore_1)
        print()
        WeightContext.get_current_context().print_address()
        WeightContext.set_current_context(WeightContext())
        WeightContext.get_current_context().print_address()
        for hitcore_1 in hitcore_list_1:
            hitcore_1.set("global_weight", hitcore_1.get("spill") % 2)
        for hitcore_1 in hitcore_list_1:
            self.assertEqual(hitcore_1.get("global_weight"), hitcore_1.get("spill") % 2)
        WeightContext.set_current_context(WeightContext())
        WeightContext.get_current_context().print_address()
        for hitcore_1 in hitcore_list_1:
            self.assertEqual(hitcore_1.get("global_weight"), 1.0)


    def test_compare(self):
        hc1 = Hitcore()
        hc2 = Hitcore()
        hc3 = hc1
        self.assertTrue(hc1 == hc3)
        self.assertFalse(hc1 != hc3)

        self.assertFalse(hc1 == hc2)
        self.assertTrue(hc1 != hc2)

        self.assertFalse(hc1 == 0)
        self.assertFalse(0 == hc1)
        try:
            hc1 < hc2
            raise RuntimeError('Expected failure')
        except TypeError:
            pass


if __name__ == "__main__":
  unittest.main()


