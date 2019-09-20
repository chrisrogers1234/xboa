import gc
import sys
import operator
import unittest

from xboa.core import Hitcore
from xboa.core import Bunchcore

class BunchcoreTestCase(unittest.TestCase):

    def setUp(self):
        self.bunchcore = Bunchcore()
        self.events = range(5, 21)
        for i in self.events:
            hitcore = Hitcore()
            hitcore.set('x', float(i))
            hitcore.set('y', -float(i))
            hitcore.set('pz', 10.-float(i))
            hitcore.set('energy', 10.-float(i)**2.)
            hitcore.set('local_weight', float(i)+1.)
            hitcore.set('event_number', i)
            self.bunchcore.set_item(hitcore, i)

    def test_init(self):
        bc = Bunchcore(20)
        self.assertEqual(bc.length(), 0)
        self.assertEqual(sys.getrefcount(bc), 2)
        bc2 = bc
        self.assertEqual(sys.getrefcount(bc), 3)
        del bc2 
        self.assertEqual(sys.getrefcount(bc), 2)

    def test_get_item(self):
        mem_dump_in = Hitcore.dump_memory()
        bc1 = Bunchcore()
        hc1 = Hitcore()

        self.assertEqual(sys.getrefcount(hc1), 2)
        bc1.set_item(hc1, 0)
        self.assertEqual(sys.getrefcount(hc1), 2)
        hc2 = bc1.get_item(0)
        self.assertEqual(sys.getrefcount(hc2), 2)
        self.assertEqual(hc1, hc2)
        hc3 = bc1.get_item(-1)
        self.assertEqual(hc3, hc1)

        hc11 = Hitcore()
        bc1.set_item(hc11, 1)
        hc12 = bc1.get_item(1)
        self.assertEqual(hc12, hc11)
        self.assertNotEqual(hc12, hc1)
        hc13 = bc1.get_item(-2)
        self.assertEqual(hc13, hc11)

        bc1.set_item(hc11, 4)
        hc22 = bc1.get_item(4)
        self.assertEqual(hc22, hc11)
        hc23 = bc1.get_item(-5)
        self.assertEqual(hc23, hc11)
        hc24 = bc1.get_item(3) # no value stored, pad with None
        self.assertEqual(hc24, None)

        try:
            bc1.get_item("not an int")
            raise RuntimeError("Expected an exception")
        except TypeError:
            pass

        del(bc1)
        self.assertEqual(sys.getrefcount(hc1), 2)

    def test_set_item(self):
        bc1 = Bunchcore()
        hc1 = Hitcore()
        # should extend the bunchcore
        bc1.set_item(hc1, 19)
        self.assertEqual(bc1.length(), 20)
        bc1.set_item(hc1, -20)
        self.assertEqual(bc1.length(), 20)
        bc1.set_item(hc1, 20)
        self.assertEqual(bc1.length(), 21)
        bc1.set_item(hc1, -21)
        self.assertEqual(bc1.length(), 21)
        bc1.set_item(hc1, -31)
        bc1.set_item(hc1, -25)
        try:
          bc1.set_item(hc1)
          raise RuntimeError("Expected an exception")
        except TypeError:
          pass
        try:
          bc1.set_item(hc1, "not an int")
          raise RuntimeError("Expected an exception")
        except TypeError:
          pass
        try:
          bc1.set_item("not a hitcore", 0)
          raise RuntimeError("Expected an exception")
        except TypeError:
          pass

    def test_moment(self):
        for i in self.events:
            hitcore = self.bunchcore.get_item(i)
        x_mean = self.bunchcore.moment(['x'], {'x':1.}) #calculation tested at Bunch level
        y_mean = self.bunchcore.moment(['y'], {'y':-1.}) #calculation tested at Bunch level
        self.assertAlmostEqual(x_mean, 13.074074074074073)
        self.assertAlmostEqual(y_mean, -13.074074074074073)
        cov_xy = self.bunchcore.moment(['x', 'y'], {})
        sig_x = self.bunchcore.moment(['x', 'x'], {})**0.5
        sig_y = self.bunchcore.moment(['y', 'y'], {})**0.5
        corr_xy = cov_xy/sig_x/sig_y
        self.assertAlmostEqual(corr_xy, -1.)
        try:
            self.bunchcore.moment('not a list', {'x':1.})
            raise RuntimeError("Expected an exception")
        except TypeError:
            pass
        try:
            self.bunchcore.moment(['x'], 'not a dict')
            raise RuntimeError("Expected an exception")
        except TypeError:
            pass

    def test_covariance_matrix(self):
        vlist = ['x', 'y']
        mdict = {'x':1., 'y':3., 'nonsense':0.1}
        cov_matrix = self.bunchcore.covariance_matrix(vlist, mdict)
        self.assertEqual(len(cov_matrix), 2)
        for i in range(2):
            self.assertEqual(len(cov_matrix[i]), 2)
        weight_sum = sum([self.bunchcore.get_item(i).get('weight') \
                                                          for i in self.events])
        for i in range(2):
            for j in range(2):
                squares_list = []
                for k in self.events:
                    x = self.bunchcore.get_item(k).get(vlist[i])-mdict[vlist[i]]
                    y = self.bunchcore.get_item(k).get(vlist[j])-mdict[vlist[j]]
                    weight = self.bunchcore.get_item(k).get('weight')
                    squares_list.append(x*y*weight)
                self.assertAlmostEqual(cov_matrix[i][j],
                                       sum(squares_list)/weight_sum)

    def test_covariance_matrix_bad_inputs(self):
        try:
            self.bunchcore.covariance_matrix('not a list', {'x':1.})
            raise RuntimeError("Expected an exception")
        except TypeError:
            pass
        try:
            self.bunchcore.covariance_matrix(['bad', 'string'], {'x':1.})
            raise RuntimeError("Expected an exception")
        except ValueError:
            pass
        try:
            self.bunchcore.covariance_matrix([0], {'x':1.})
            raise RuntimeError("Expected an exception")
        except ValueError:
            pass
        try:
            self.bunchcore.covariance_matrix(['x'], 'not a dict')
            raise RuntimeError("Expected an exception")
        except TypeError:
            pass
        try:
            self.bunchcore.covariance_matrix(['x'], {0:1.})
            raise RuntimeError("Expected an exception")
        except TypeError:
            pass
        try:
            self.bunchcore.covariance_matrix(['x'], {'x':'string'})
            raise RuntimeError("Expected an exception")
        except TypeError:
            pass

    def test_cut_double_local(self):
        self.bunchcore.cut_double("x", operator.gt, 9.5, False)
        for i in self.events:
            hitcore = self.bunchcore.get_item(i)
            if hitcore.get('x') > 9.5:
                self.assertAlmostEqual(hitcore.get('local_weight'), 0.)
            else:
                self.assertAlmostEqual(hitcore.get('local_weight'), i+1)

    def test_cut_double_global(self):
        for i in self.events:
            hitcore = self.bunchcore.get_item(i)
            self.assertAlmostEqual(hitcore.get('global_weight'), 1)
        self.bunchcore.cut_double("x", operator.gt, 10.5, True)
        for i in self.events:
            hitcore = self.bunchcore.get_item(i)
            if i > 10:
                self.assertAlmostEqual(hitcore.get('global_weight'), 0)
            else:
                self.assertAlmostEqual(hitcore.get('global_weight'), 1)
        Hitcore.clear_global_weights()
        for i in self.events:
            hitcore = self.bunchcore.get_item(i)
            self.assertAlmostEqual(hitcore.get('global_weight'), 1)

    def bad_callable(self):
        pass

    def test_cut_double_bad(self):
        try:
            self.bunchcore.cut_double("none", operator.gt, 10.5, True)
            raise RuntimeError("Should have thrown")
        except TypeError:
            pass
        try:
            self.bunchcore.cut_double("x", self.bad_callable, 10.5, True)
            raise RuntimeError("Should have thrown")
        except TypeError:
            pass
        try:
            self.bunchcore.cut_double("x", operator.gt, "string", True)
            raise RuntimeError("Should have thrown")
        except TypeError:
            pass
        # this is okay, "string" evaluates to true
        self.bunchcore.cut_double("x", operator.gt, 10.5, "string")
        # now clear any weightings applied!
        Hitcore.clear_global_weights()

    def test_index_by_power(self):
        #self.assertEqual(self.bunchcore.index_by_power(0, 1), [[0]])
        try:
            self.bunchcore.index_by_power(-1, 3)
            raise RuntimeError("Should have thrown")
        except ValueError:
            pass
        try:
            self.bunchcore.index_by_power(3, 0)
            raise RuntimeError("Should have thrown")
        except ValueError:
            pass
        # max_order, n_axes
        #self.assertEqual(self.bunchcore.index_by_power(3, 1),
        #                 [[i] for i in range(3)])
        # max_order, n_axes
        index = self.bunchcore.index_by_power(2, 2)
        ref_index = [[0, 0], [0, 1], [0, 2], [1, 1], [1, 0], [2, 0]]
        self.assertEqual(sorted(index), sorted(ref_index))
        # this checks for a few properties; doesn't do a full check
        index = sorted(self.bunchcore.index_by_power(6, 4))
        for element in index:
            self.assertEqual(len(element), 4) # n_axes < 4
            self.assertLess(sum(element), 7) # max_order < 7
            for i, item in enumerate(index[1:]): # unique
                self.assertNotEqual(index[i], item)

    def _check_moment_tensor(self, variables, max_size):
        index_by_power = self.bunchcore.index_by_power(max_size, len(variables))
        test_moments = self.bunchcore.moment_tensor(variables, max_size)
        self.assertEqual(len(index_by_power), len(test_moments))
        ref_moments = []
        for i, index in enumerate(index_by_power):
            moment_variables = []
            for j, power in enumerate(index):
                for k in range(power):
                    moment_variables.append(variables[j])
            mean = dict(zip(variables, [0.]*len(variables)))
            ref_moments.append(self.bunchcore.moment(moment_variables, mean))
        for i, test_moment in enumerate(test_moments):
            self.assertAlmostEqual(ref_moments[i], test_moments[i], 3)
        

    def test_moment_tensor(self):
        variables = ["px", "x"]
        self._check_moment_tensor(variables, 2)
        variables = ["x", "y", "pz", "energy", "px"]
        self._check_moment_tensor(variables, 4)
        

if __name__ == "__main__":
  unittest.main()


