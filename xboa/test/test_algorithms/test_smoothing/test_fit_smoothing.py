import unittest
import math
import ROOT
from xboa.algorithms.smoothing import FitSmoothing
import xboa.Common as common

class TestFitSmoothing(unittest.TestCase):
    def test_smoothing(self):
        signal = [math.sin(2.*math.pi*i/100)+math.sin(2.*math.pi*i/10.) for i in range(1000)]
        fit = ROOT.TF1("fit", "[0]*sin(2.*pi*x/100.)")
        fit.SetParameter(0, 2.)
        smoothing = FitSmoothing(fit)
        smoothed = smoothing.smooth(signal)
        self.assertEqual(len(smoothed), len(signal))

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

        self.assertAlmostEqual(min(smoothed), -1.)
        self.assertAlmostEqual(max(smoothed), 1.)


if __name__ == "__main__":
    unittest.main()

