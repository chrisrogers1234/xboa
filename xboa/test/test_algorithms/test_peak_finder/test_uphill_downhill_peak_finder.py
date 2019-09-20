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

import math 
import random
import unittest
import ROOT

from xboa.algorithms.smoothing import GaussianSmoothing
from xboa.algorithms.peak_finder import UphillDownhillPeakFinder

def _add_data(data, mag, k_1, phase=0.):
    
    return [x+mag*math.sin(2.*math.pi*i/k_1+phase) for i, x in enumerate(data)]

class UphillDownhillPeakFinderTestCase(unittest.TestCase):
    def test_init(self):
        # initialises properly
        pf = UphillDownhillPeakFinder()

    def test_find_peaks(self):
        test_data = _add_data([0. for i in range(2000)], 100., 400.)
        pf = UphillDownhillPeakFinder()
        self.assertEqual(pf.find_peaks(test_data), [100, 500, 900, 1300, 1700])

    def test_find_peaks_error(self):
        test_data = _add_data([0. for i in range(2000)], 100., 399.,
                               math.pi/2.05)
        pf = UphillDownhillPeakFinder()
        peaks = pf.find_peaks(test_data)
        self.assertEqual(peaks, [2, 401, 800, 1199, 1598, 1997])

        noisy_test_data = [x+random.gauss(0., 100.) for x in test_data]         
        peak_errors = pf.find_peak_errors_derivative(noisy_test_data, peaks, 3)
        for i, a_peak_error in enumerate(peak_errors[:-1]):
            self.assertLess(abs(a_peak_error[0]-peaks[i]), a_peak_error[1])
        # error calculation is wrong because we are near to the array end
        self.assertLess(abs(peak_errors[-1][0]-peaks[-1]),
                        peak_errors[-1][1]*5.)


if __name__ == "__main__":
    unittest.main()

