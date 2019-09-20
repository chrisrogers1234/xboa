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

"""Test Cut smoothing algorithm"""

import unittest
import math
from xboa.algorithms.smoothing import CutSmoothing
import numpy

class TestCutSmoothing(unittest.TestCase):
    """Test Cut Smoothing"""

    def test_smoothing(self):
        """Check that we remove noise as desired"""
        signal = [numpy.random.uniform(9., 11.) for i in range(1000)]
        signal[10] = 20. # check we remove positive outlier
        signal[101] = 0. # check we remove negative outlier
        signal[999] = 20. # check we remove outlier at end
        cut_smoothing = CutSmoothing(5., 100) # range 5 < x < 15; 
                                              # window is 100 elements wide
        signal_out = cut_smoothing.smooth(signal)
        self.assertEqual(len(signal_out), 997) # we removed three values
        for x in signal_out:
            self.assertLess(x, 15.)
            self.assertGreater(x, 5.)

    def test_smooth_table(self):
        """Check that we smooth a table okay"""
        signal = [numpy.random.uniform(9., 11.) for i in range(1000)]
        signal[10] = 20. # check we remove positive outlier
        signal[101] = 0. # check we remove negative outlier
        signal[999] = 20. # check we remove outlier at end

        test = [True for i in range(1000)]
        test[10] = False
        test[101] = False
        test[999] = False
        cut_smoothing = CutSmoothing(5., 97) # range 5 < x < 15; 
                                              # window is 97 elements wide
        # nb: 1000%97 != 0; so we check the handling of the last window is done
        # right 
        table_out = cut_smoothing.smooth_table([signal, test], 0)
        self.assertEqual(len(table_out[0]), 997) # we removed three values
        for x in table_out[0]:
            self.assertLess(x, 15.)
            self.assertGreater(x, 5.)
        self.assertEqual(len(table_out[1]), 997) # we removed three values
        for x in table_out[1]:
            self.assertTrue(x)

        table_out = cut_smoothing.smooth_table((test, signal), 1)
        self.assertEqual(len(table_out[0]), 997) # we removed three values
        self.assertEqual(len(table_out[1]), 997) # we removed three values


if __name__ == "__main__":
    unittest.main()

