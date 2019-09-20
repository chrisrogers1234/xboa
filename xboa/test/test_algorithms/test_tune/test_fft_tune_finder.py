import math 
import unittest
import numpy
import ROOT
import sys

from xboa.tracking import MatrixTracking
from xboa.algorithms.peak_finder import WindowPeakFinder
from xboa.algorithms.tune import FFTTuneFinder
from xboa.hit import Hit
import xboa.common as common

def matrix(phi_x, num_turns):
    # x is conventional ellipse
    # y is phase advance = pi
    # t is phase advance = complex
    f_x = 2*math.pi - phi_x
    cos = math.cos(f_x)
    sin = math.sin(f_x)
    b_x = 10.
    a_x = 1.
    g_x = (1.+a_x**2.)/b_x
    data = [[cos+sin*a_x,  sin*b_x,     0.0,  0.0, 0.0,  0.0],
            [-sin*g_x,     cos-sin*a_x, 0.0,  0.0, 0.0,  0.0],
            [0.0,  0.0,  0.0, -1.0, 0.0,  0.0],
            [0.0,  0.0,  1.0,  0.0, 0.0,  0.0],
            [0.0,  0.0,  0.0,  0.0, 1.0,  0.0],
            [0.0,  0.0,  0.0,  0.0, 0.0,  1.0]]
    matrix = numpy.matrix(data)
    matrix_list = [matrix]
    for i in range(num_turns-1):
        matrix_list.append(matrix*matrix_list[-1])
        for j in range(6):
            if math.isnan(matrix_list[-1][j, j]):
                print("ARG", i, matrix_list[-1], '\n\n', matrix_list[-5])
                raise ValueError("ARG")
    matrix_list = matrix_list
    offset = numpy.matrix([10., 7., 0., 0., 0., 1000.])
    offset_list = [offset]*num_turns
    offset_in = numpy.matrix([10., 7., 0., 0., 0., 1000.])
    tracking = MatrixTracking(matrix_list,
                                   offset_list,
                                   offset_in)
    co = Hit.new_from_dict({'x':10., 'px':7., 'energy':1000.,
                   'pid':2212, 'mass':common.pdg_pid_to_mass[2212]})
    if abs(numpy.linalg.det(matrix) - 1.0) > 1e-9:
        raise ValueError("TM determinant should be 1, got "+\
                          str(numpy.linalg.det(matrix)))
    return co, tracking

class FFTTuneTestCase(unittest.TestCase):
    def setUp(self):
        """Setup the EllipseClosedOrbitFinder"""

    def test_get_tune(self):
        # check test initialises properly
        co, tracking = matrix(math.pi/4., 1000)
        fft = FFTTuneFinder()
        fft.run_tracking('x', 1.0, co, tracking)
        tune = fft.get_tune()
        self.assertTrue(abs(tune*2.*math.pi-math.pi/4.) < 1e-2)

    def test_get_tune_peak_finder(self):
        # check test initialises properly
        co, tracking = matrix(math.pi/4., 1000)
        fft = FFTTuneFinder(peak_finder = WindowPeakFinder(5, 0., 1.))
        fft.run_tracking('x', 1.0, co, tracking)
        tune = fft.get_tune()
        self.assertTrue(abs(tune*2.*math.pi-math.pi/4.) < 1e-2)

    def test_get_tune_use_hits(self):
        # check test initialises properly
        co, tracking = matrix(math.pi/12., 1000)
        fft = FFTTuneFinder()
        fft.run_tracking('x', 1.0, co, tracking, use_hits = list(range(0, 1000, 4)))
        tune = fft.get_tune()
        #print "TUNE", tune*2.*math.pi, 4.*math.pi/12.
        fft.plot_fft("TUNE")
        self.assertTrue(abs(tune*2.*math.pi-4.*math.pi/12.) < 1e-2)

    def test_plot_fft(self):
        # test fft plots okay
        co, tracking = matrix(math.pi/4., 1000)
        fft = FFTTuneFinder()
        fft.run_tracking('x', 1.0, co, tracking)
        tune = fft.get_tune()
        canvas, hist, graph = fft.plot_fft("Test")
        self.assertEqual(canvas.GetTitle(), "Test")
        self.assertEqual(hist.GetTitle(), "Test")
        self.assertEqual(graph.GetTitle(), "Test")
        self.assertEqual(hist.GetXaxis().GetTitle(), "frequency")
        self.assertEqual(hist.GetYaxis().GetTitle(), "magnitude")
        self.assertEqual(graph.GetN(), len(fft.k_mag_y))
        for i in range(len(fft.k_mag_y)):
            x, y = ROOT.Double(0.), ROOT.Double(0.)
            graph.GetPoint(i, x, y)
            self.assertAlmostEqual(fft.k_mag_x[i], x)
            self.assertAlmostEqual(fft.k_mag_y[i], y)

    def test_fit_fft(self):
        # test fft plots okay
        co, tracking = matrix(math.pi/4., 1000)
        fft = FFTTuneFinder()
        fft.run_tracking('x', 1.0, co, tracking)
        tune = fft.get_tune()
        peak = fft.k_mag_x.index(fft.peak_x_list[0])
        canvas, hist, graph, fit = fft.plot_fft_fit("Test", peak, peak-5, peak+5)
        fitted_tune = fit.GetParameter(0)
        self.assertTrue(abs(fitted_tune*2.*math.pi-math.pi/4.) < 1e-2)

    def test_sft(self):
        # test slow fourier transform
        did_pass = {}
        for n_turns in range(10, 16):
            did_pass[n_turns] = True
            co, tracking = matrix(-5.*math.pi/3., n_turns)
            fft = FFTTuneFinder()
            fft.run_tracking('x', 1.0, co, tracking)
            try:
                tune = fft.get_tune()
            except ValueError:
                pass # statistics are low enough that no primary peaks can be found
            canvas, hist, graph = fft.plot_fft("SFT Test")
            graph.SetMarkerStyle(4)
            graph.Draw("PL")
            n_points = len(fft.k_mag_x)*10
            graph2 = ROOT.TGraph(n_points)
            for i in range(n_points):
                x = i/float(n_points)/2.
                y = fft._sft(x)
                graph2.SetPoint(i, x, y)
            graph2.SetMarkerStyle(6)
            graph2.SetLineColor(2)
            graph2.Draw("PL")
            canvas.Update()
            for i, x_ref in enumerate(fft.k_mag_x):
                y_ref = fft.k_mag_y[i]
                y_test = fft._sft(x_ref)
                #self.assertAlmostEqual(y_test, y_ref)
                if y_test-y_ref > (y_test+y_ref)/200:
                    did_pass[n_turns] = False
        self.assertEqual(sum(did_pass.values()), len(did_pass))

    def _ft_test(self, fft):
        fft._fft_find_peaks()
        peak_index = fft._get_max_peak()
        tune_fft = fft.fractional_tune
        # recursive refine
        fft._recursive_refine_peak(fft.k_mag_x[peak_index], 1e-6)
        fft._find_peaks()
        peak_index = fft._get_max_peak()
        tune_sft = fft.fractional_tune
        # now reset for hanning filter
        fft.use_hanning_filter = True
        fft.k_mag_x = []
        fft.k_mag_y = []
        fft._fft_find_peaks()
        peak_index = fft._get_max_peak()
        fft._recursive_refine_peak(fft.k_mag_x[peak_index], 1e-6)
        fft._find_peaks()
        peak_index = fft._get_max_peak()
        tune_sft_hanning = fft.fractional_tune
        return tune_fft, tune_sft, tune_sft_hanning

    def test_sft_accuracy(self):
        # test slow fourier transform
        canvas = common.make_root_canvas("SFT Residuals")
        hist = common.make_root_histogram('', [], 'Residuals', 1000, [], '', 
                                 1000, xmin=1., xmax=1000.0, ymin=0.0, ymax=1.0)
        hist.Draw()
        for i in range(3, 4):
            truth_list, sft_list, fft_list, n_list = [], [], [], []
            tune = i*0.1
            for n in [5, 10, 20, 50, 100, 200, 500, 1000]:
                co, tracking = matrix(tune*2.*math.pi, n)
                fft = FFTTuneFinder()
                fft.run_tracking('x', 10.0, co, tracking)
                tune_sft, tune_fft, tune_sft_hanning = 0., 0., 0.
                try:
                    tune_fft, tune_sft, tune_sft_hanning = self._ft_test(fft)
                except ValueError:
                    # statistics are low enough that no primary peaks can be 
                    # found
                    sys.excepthook(*sys.exc_info())
                if tune > 0.5:
                    tune_sft = 1-tune_sft
                    tune_fft = 1-tune_fft
                #print "truth", tune, "sft", tune_sft, 
                #print "fft", tune_fft, "hanning", tune_sft_hanning
                truth_list.append(tune)
                sft_list.append(tune_sft)
                fft_list.append(tune_fft)
                n_list.append(n)
            residual_list = []
            for i, n in enumerate(n_list):
                if fft_list[i]-truth_list[i] != 0.:
                    residual_list.append(abs(sft_list[i]-truth_list[i])\
                                        /abs(fft_list[i]-truth_list[i]))
            hist, graph = common.make_root_graph("SFT residuals", n_list,
                                "Number of points", residual_list, "Residuals")
            graph.Draw('L')
        canvas.SetLogx()
        canvas.Update()

if __name__ == "__main__":
    unittest.main()

