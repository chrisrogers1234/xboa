import random
import math 
import unittest
import numpy
import array
import ROOT
import sys

from xboa.tracking import MatrixTracking
from xboa.algorithms.peak_finder import WindowPeakFinder
from xboa.algorithms.tune import FFTTuneFinder
from xboa.hit import Hit
import xboa.Common as common

PI = math.pi

class SignalGenerator(object):
    def __init__(self, number_of_signals, frequencies, magnitudes, phases):
      self.frequencies = frequencies
      self.magnitudes = magnitudes
      self.phases = phases
      self.number_of_signals = number_of_signals
      self.systematic_walk = None
      self.decay_constant = None
      self.signal_noise = None # gaussian, RMS

    def generate_signal(self):
        u_list = []
        for sig in range(self.number_of_signals):
            u = 0.
            if self.systematic_walk != None:
                u = sig*self.systematic_walk
            if self.signal_noise != None:
                u += random.gauss(0., self.signal_noise)
            for i, freq in enumerate(self.frequencies):
                mag = self.magnitudes[i]
                phi = self.phases[i]
                u += mag*math.sin(2.*math.pi*freq*sig+phi)
            if self.decay_constant != None:
                u *= math.exp(-self.decay_constant*sig)
            u_list.append(u)
        return u_list

def _bins_list(grid):
    bins = [grid[0]-(grid[1]-grid[0])/2.]
    bins += [(grid[i]+grid[i+1])/2. for i in range(len(grid)-1)]
    bins += [grid[-1]+(grid[-1]-grid[-2])/2.]
    bins = [float(x) for x in bins]
    print(bins)
    bins = array.array('d', bins)
    return bins

def two_d_surface_grid(grid_x, grid_y, name):
    bins_x = _bins_list(grid_x)
    bins_y = _bins_list(grid_y)
    hist = ROOT.TH2D(name, name, len(grid_x), bins_x, len(grid_y), bins_y)
    hist.SetStats(False)
    return hist

class FTTuneSigTestCase(unittest.TestCase):

    def _test_get_tune(self):
        # check basic tune calculation
        for n in [50, 100, 500, 1000]:
            for phi_d in range(1, 10):
              sig = SignalGenerator(n, [1./10.], [1.], [PI/phi_d])
              ft = FFTTuneFinder()
              ft.u = sig.generate_signal()
              tune = ft.get_tune()
              self.assertTrue(abs(tune-1./10.) < 1e-2)
        #ft.plot_fft("Test")

    def _test_get_tune_noise(self):
        # check basic tune calculation in the presence of noise
        canvas = common.make_root_canvas("tune noise")
        n_signal_list = [50, 100, 200, 500]
        noise_list = [0., 1., 1.5, 2., 2.5, 3., 4., 5., 6., 7., 8., 9., 10.]
        hist = two_d_surface_grid(n_signal_list, noise_list, "Noise")
        for n in n_signal_list:
            for noise in noise_list:
                success = 0
                for i in range(10):
                    sig = SignalGenerator(n, [0.1], [1.], [PI/4.])
                    sig.signal_noise = noise
                    ft = FFTTuneFinder()
                    ft.u = sig.generate_signal()
                    tune = ft.get_tune()
                    if abs(tune-0.1) < 1e-2:
                        success += 1
                hist.Fill(n, noise, success)
                print(n, noise, success)
        hist.Draw("COLZ")
        canvas.Update()
        input()

    def _test_get_tune_walk(self):
        # check basic tune calculation in the presence of a systematic walk

        # comment: looks like when the walk "speed" is of order same as the
        # fractional tune, the FT resolves the peak okay
        canvas = common.make_root_canvas("tune walk")
        n_signal_list = [50, 100, 200, 300, 400, 500]
        walk_list = [i/80. for i in range(17)]
        noise = 1.0
        hist = two_d_surface_grid(n_signal_list, walk_list, "Walk")
        ref_tune = 0.2
        ref_magnitude = 1.0
        for n in n_signal_list:
            for walk in walk_list:
                success = 0
                for i in range(10):
                    sig = SignalGenerator(n, [ref_tune], [ref_magnitude], [PI/4.])
                    sig.signal_noise = noise
                    sig.systematic_walk = walk
                    ft = FFTTuneFinder(peak_finder = WindowPeakFinder(n/100+5, 3.))
                    ft.u = sig.generate_signal()
                    try:
                        tune = ft.get_tune()
                    except ValueError:
                        tune = -1.
                    if abs(tune-ref_tune) < 1e-2:
                        success += 1
                    else:
                        print("  TUNE", tune)
                    if n == 500 and abs(walk-0.1) < 1e-3 and i < 4:
                        ft.plot_signal("SIGNAL")
                        ft.plot_fft("FT")
                hist.Fill(n, walk, success)
                print(n, noise, walk, success)
        canvas.cd()
        hist.Draw("COLZ")
        canvas.Update()
        input()

    def _test_get_tune_double_freq(self):
        ref_tune = [0.01, 0.001]
        ref_magnitude = [1.0, 0.1]
        ref_phase = [PI/4., PI/2.]
        n_signals = 20000
        noise = 1.0
        for i in range(1):
            print("Generating", i)
            sig = SignalGenerator(n_signals, ref_tune, ref_magnitude, ref_phase)
            sig.signal_noise = noise
            ft = FFTTuneFinder(peak_finder = WindowPeakFinder(n_signals/1000+5, 10.))
            ft.u = sig.generate_signal()
            print("Getting tune", i)
            try:
                tune = ft.get_tune(1.)
            except ValueError:
                tune = -1.
            for i in range(len(ft.peak_x_list)):
                print(ft.peak_x_list[i], ft.peak_y_list[i])
            ft.plot_signal("SIGNAL")
            ft.plot_fft("FT")
        input()


if __name__ == "__main__":
    unittest.main()

