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
import numpy

from xboa.algorithms.peak_finder import RefinePeakFinder

def _test_data(n, k_1, noise):
    return [math.sin(2.*math.pi*i/k_1)+random.gauss(0., noise) \
            for i in range(n)]

class RefinePeakFinderTestCase(unittest.TestCase):
    def test_init(self):
        # check finder initialises properly
        pf = RefinePeakFinder([10, 20], 1, 2, True)
        self.assertEqual(pf.peak_list, [10, 20])
        self.assertEqual(pf.delta_seed, 1)
        self.assertEqual(pf.max_delta, 2)
        self.assertEqual(pf.draw, True)

    def test_fit_no_noise(self):
        # check fit works in the absence of noise
        test_data = _test_data(200, 100, 1e-9)
        pf = RefinePeakFinder([20, 120], 10, 20, False)
        peaks = pf.find_peaks(test_data)
        self.assertEqual(peaks, [25, 125])

    def test_fit_noise(self):
        # check fit works with noise added
        test_data = _test_data(200, 100, 0.1)
        pf = RefinePeakFinder([20, 120], 20, 50, False)
        peaks = pf.find_peaks(test_data)
        self.assertEqual(len(peaks), 2)
        self.assertLess(abs(peaks[0]-20), 10)
        self.assertLess(abs(peaks[1]-120), 10)

    def test_fit_errors(self):
        # check find_peak_errors
        test_data = _test_data(2000, 1000, 0.01)
        seeds = [240, 1240]
        pf = RefinePeakFinder(seeds, 20, 100, True)
        peaks = pf.find_peak_errors(test_data)
        for i, a_peak in enumerate(peaks):
            print a_peak
            self.assertLess(abs(a_peak['y']-1.0), 0.01)
            self.assertLess(abs(a_peak['x']-seeds[i]-10), 5.0)
            self.assertEqual(abs(a_peak['x_in']-seeds[i]), 0)
            covs = a_peak['cov(x,y)']
            det = numpy.linalg.det(numpy.array(covs))
            self.assertLess(det**0.5, 0.01)

    def test_fit_window(self):
        # check fit works in the absence of noise
        test_data = _test_data(200, 100, 1e-9)
        pf = RefinePeakFinder([20, 110], 6, 10, False)
        peaks = pf.find_peaks(test_data)
        self.assertEqual(peaks, [25]) # max_delta too small to get 125 peak
        pf = RefinePeakFinder([20, 110], 2, 7, False)
        peaks = pf.find_peaks(test_data)
        self.assertEqual(peaks, []) # delta goes 2, 4, -8-; so fails on 25 peak
        pf = RefinePeakFinder([20, 110], 2, 9, False)
        peaks = pf.find_peaks(test_data)
        self.assertEqual(peaks, [25]) # delta goes 2, 4, 8; so passes on 25 peak

if __name__ == "__main__":
    unittest.main()

