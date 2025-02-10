import matplotlib
import numpy

import unittest
import xboa.common.matplotlib_wrapper

class MatplotlibWrapperTest(unittest.TestCase):
    def setUp(self):
        self.figure = matplotlib.pyplot.figure()
        self.axes = self.figure.add_subplot(1, 1, 1)

    def tearDown(self):
        matplotlib.pyplot.show(block=False)
        input("Press <CR> to continue")
        self.axes.clear()
        del self.axes
        del self.figure

    def test_plot_hist2d_ratio(self):
        h1 = [[0.0, 1.0, 2.0],   [3.0, 4.0, 5.0],    [6.0, 7.0, 8.0]]
        h2 = [[9.0, 10.0, 11.0], [12.0, 0.0, 14.0], [15.0, 16.0, 17.0]]
        xedges = [float(i) for i in range(4)]
        yedges = [float(i) for i in range(5, 9)]
        hist_args = {"cmap":"viridis"}
        hist2d_3 = xboa.common.matplotlib_wrapper.plot_hist2d_ratio(self.axes, h1, h2, xedges, yedges, hist_args)
        self.assertTrue(numpy.equal(hist2d_3[1], xedges).all())
        self.assertTrue(numpy.equal(hist2d_3[2], yedges).all())
        for i, row1 in enumerate(h1):
            for j, element1 in enumerate(row1):
                element2 = h2[i][j]
                if element2 == 0.0:
                    self.assertEqual(hist2d_3[0][i][j], 0.0)
                else:
                    self.assertAlmostEqual(hist2d_3[0][i][j], element1/element2, 1e-12)
        self.assertFalse(True, "Need to test on_nan handling. Improve algorithm, lookup numpy.seterr")


if __name__ == "__main__":
    unittest.main()

