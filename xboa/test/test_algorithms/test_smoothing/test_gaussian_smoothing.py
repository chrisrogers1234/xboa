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

"""Test Gaussian smoothing algorithm"""

import unittest
import math
from xboa.algorithms.smoothing import GaussianSmoothing
import xboa.Common as common
import numpy

class TestGaussianSmoothing(unittest.TestCase):
    """Test Gaussian Smoothing"""

    def test_smoothing(self):
        """Check that we remove high frequency FFT components as desired"""
        signal = [math.sin(2.*math.pi*i/100)+math.sin(2.*math.pi*i/5.) \
                  for i in range(1000)]
        smoothing = GaussianSmoothing(10., 100, True)
        smoothed = smoothing.smooth(signal)
        self.assertEqual(len(smoothed), len(signal))

        comment_out_draw = """
        canvas = common.make_root_canvas('signal')
        hist, graph = common.make_root_graph('', range(0, len(signal)), '', signal, '')
        hist.Draw()
        graph.Draw()
        canvas.Update()


        canvas = common.make_root_canvas('smoothed')
        hist, graph = common.make_root_graph('', range(0, len(smoothed)), '', smoothed, '')
        hist.Draw()
        graph.Draw()
        canvas.Update()
        """

        print('signal fft - should have two FT components')
        signal_fft = numpy.fft.fft(numpy.array(signal))
        fft_arr = [x for x in numpy.absolute(signal_fft)]
        self.assertGreater(fft_arr[10], 400.) 
        self.assertGreater(fft_arr[200], 400.) 
        print([(i, z) for i, z in enumerate(fft_arr) if z > 10.0])
        print('smoothed fft - should have high frequency FT components removed')
        smoothed_fft = numpy.fft.fft(numpy.array(smoothed))
        fft_arr = [x for x in numpy.absolute(smoothed_fft)]
        self.assertEqual(fft_arr.index(max(fft_arr)), 10)
        self.assertGreater(fft_arr[10], 400.) 
        [self.assertLess(x, 10.) for x in fft_arr[20:500]]
        print([(i, z) for i, z in enumerate(fft_arr) if z > 10.0])

    def test_smoothing_const(self):
        """Check the normalisation factor and handling of boundaries"""
        signal = [1. for i in range(100)]
        smoothing = GaussianSmoothing(10., 10, True)
        smoothed = smoothing.smooth(signal)
        self.assertEqual(len(smoothed), len(signal))
        self.assertAlmostEqual(min(smoothed), min(signal))
        self.assertAlmostEqual(max(smoothed), max(signal))

    def test_smoothing_delta(self):
        """
        Check the peak is always on the delta function, even at boundaries,
        when normalisation is handled properly
        """
        for delta_index in [5, 2, 8]:
            signal = [0. for i in range(10)]
            signal[delta_index] = 1.
            smoothing = GaussianSmoothing(10., 3, False)
            smoothed = smoothing.smooth(signal)
            self.assertEqual(smoothed.index(max(smoothed)), delta_index)

if __name__ == "__main__":
    unittest.main()

