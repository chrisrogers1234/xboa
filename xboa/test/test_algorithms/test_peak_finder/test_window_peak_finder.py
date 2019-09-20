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

from xboa.algorithms.peak_finder import WindowPeakFinder

def _test_data(k, n, l = None):
    if l == None:
        l = k
    return [math.sin(2.*math.pi*i/k)*math.exp(-i/l) for i in range(n)]

class PeakFinderTestCase(unittest.TestCase):
    def test_init(self):
        # initialises properly
        pf = WindowPeakFinder(10, 0., 1)
        self.assertEqual(pf.window_size, 10)

    def test_find_peaks_small_window(self):
        # peak finder with window size < space between peaks
        pf = WindowPeakFinder(100, 0., 1)
        test_data = _test_data(200., 500)
        self.assertEqual(pf.find_peaks(test_data), [45, 245, 445])

    def test_find_peaks_large_window(self):
        # peak finder with window size > space between peaks
        # ignores subpeaks close to a main peak
        pf = WindowPeakFinder(100, 0., 1)
        test_data = _test_data(50., 500)
        self.assertEqual(pf.find_peaks(test_data),
                         [11, 61, 111, 161, 211, 261, 311, 361, 411])


    def test_find_peaks_large_window(self):
        # peak finder with window size > signal length
        # ignores subpeaks close to a main peak
        pf = WindowPeakFinder(500, 0., 1)
        test_data = _test_data(50., 500)
        self.assertEqual(pf.find_peaks(test_data),
                         [11])
        pf = WindowPeakFinder(1000, 0., 1)
        test_data = _test_data(50., 500)
        self.assertEqual(pf.find_peaks(test_data),
                         [11])

    def test_find_end(self):
        # peak finder with peaks at the end of the dataset
        pf = WindowPeakFinder(10, 0., 1)
        test_data = _test_data(200., 440)[50:]
        peaks = pf.find_peaks(test_data)
        self.assertTrue(0 in peaks, msg = "Didn't get 0 in "+str(peaks))
        self.assertTrue(389 in peaks, msg = "Didn't get 389 in "+str(peaks))

    def test_threshold(self):
        # peak finder with peaks at the end of the dataset
        test_data = [random.gauss(10., 1.) for i in range(10000)]+\
                    [random.gauss(10., 20.) for i in range(10000)]
        test_data[50] = 25.
        # test_data[50] > 10 sigma from mean
        # test_data[i] < 10 sigma from mean (we expect)
        pf = WindowPeakFinder(500, 10.0, 1)
        peaks = sorted(pf.find_peaks(test_data))
        self.assertTrue(50 in peaks)
        self.assertTrue(peaks[1] > 100)

    def test_step(self):
        # peak finder with peaks at the end of the dataset
        pf = WindowPeakFinder(15, 0., 40)
        test_data = _test_data(20., 1000, 1e9)
        peaks = pf.find_peaks(test_data)
        peak_delta = [test-peaks[i] for i, test in enumerate(peaks[1:])]
        self.assertEqual(peak_delta, [40]*24)

if __name__ == "__main__":
    unittest.main()

