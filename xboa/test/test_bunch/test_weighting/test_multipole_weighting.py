# This file is a part of xboa
#
# xboa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# xboa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with xboa in the doc folder.  If not, see 
# <http://www.gnu.org/licenses/>.

import unittest
import random

import numpy

from xboa.bunch import Bunch
from xboa.hit import Hit
from xboa.bunch.weighting import MultipoleWeighting

class TestMultipoleWeighting(unittest.TestCase):
    def _generate_bunch(self, weight_vars, n_events):
        test_bunch = Bunch()
        for i in range(n_events):
            test_hit = Hit()
            for var in weight_vars:
                test_hit[var] = random.gauss(0., 1.**0.5)
            test_hit["event_number"] = i
            test_bunch.append(test_hit)
        return test_bunch

    def test_apply_weights(self):
        """
        Check that apply weights works as expected
        """
        test_bunch_1 = self._generate_bunch(["x", "y"], 10000)
        test_bunch_2 = test_bunch_1.deepcopy()
        ellipse = numpy.array([[1.0, 0.], [0., 0.5]])
        mean = numpy.array([0., 0.])
        multipole_weighting = MultipoleWeighting(2, ["x", "y"], ellipse, mean)
        # local
        test_bunch_1 = multipole_weighting.apply_weights(test_bunch_1, False)
        mean_out_1 = test_bunch_1.mean(['x', 'y'])
        cov_out_1 =  test_bunch_1.covariance_matrix(['x', 'y'])
        self.assertAlmostEqual(test_bunch_1[0]['global_weight'], 1., 1e-6)
        # global
        test_bunch_2 = multipole_weighting.apply_weights(test_bunch_2, True)
        mean_out_2 = test_bunch_2.mean(['x', 'y'])
        cov_out_2 =  test_bunch_2.covariance_matrix(['x', 'y'])
        self.assertAlmostEqual(test_bunch_2[0]['local_weight'], 1., 1e-6)
        self.assertEqual(mean_out_1, mean_out_2)
        for i in range(2):
            for j in range(2):
                self.assertEqual(cov_out_1[i, j], cov_out_2[i, j])
        # should be close-ish to 0.5
        self.assertTrue(abs(cov_out_1[0, 0] - 1.0) < 0.2)
        self.assertTrue(abs(cov_out_1[1, 1] - 0.5) < 0.1)

    def test_apply_weights_4d(self):
        weight_vars = ["x", "px", "y", "py"]
        test_bunch = self._generate_bunch(weight_vars, 10000)
        ellipse = numpy.zeros([4, 4])
        for i in range(3):
            ellipse[i, i] = 1.
        ellipse[3, 3] = 0.5
        mean = numpy.zeros([4])
        print("Target")
        print(mean)
        print(ellipse)
        multipole_weighting = MultipoleWeighting(3, weight_vars, ellipse, mean)
        print("Before")
        print(test_bunch.mean(weight_vars))
        print(test_bunch.covariance_matrix(weight_vars))
        test_bunch = multipole_weighting.apply_weights(test_bunch, False)
        print("After")
        print(test_bunch.mean(weight_vars))
        print(test_bunch.covariance_matrix(weight_vars))
        for i in range(5):
            test_bunch = multipole_weighting.apply_weights(test_bunch, False)
            print("Again", i)
            print(test_bunch.mean(weight_vars))
            print(test_bunch.covariance_matrix(weight_vars))
        moment_tensor = test_bunch._Bunch__bunchcore.moment_tensor\
                                                               (weight_vars, 4)
        moment_index = test_bunch._Bunch__bunchcore.index_by_power\
                                                           (4, len(weight_vars))
        for index, tensor in zip(moment_index, moment_tensor):
            print(index, tensor)

    def test_apply_weights_broke(self):
        test_bunch = self._generate_bunch(["x", "px"], 10)
        ellipse = numpy.zeros([2, 2])
        mean = numpy.array([0., 0.])
        print(test_bunch.mean(["x", "px"]))
        print(test_bunch.covariance_matrix(["x", "px"]))
        multipole_weighting = MultipoleWeighting(2, ["x", "px"], ellipse, mean)
        multipole_weighting.apply_weights(test_bunch, False)
        print(test_bunch.mean(["x", "px"]))
        print(test_bunch.covariance_matrix(["x", "px"]))

if __name__ == "__main__":
    unittest.main()

