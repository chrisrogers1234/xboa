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
import sys
try:
    import numpy
except ImportError:
    pass
try:
    import ROOT
except ImportError:
    pass

import xboa.common as common
from xboa.algorithms.peak_finder import WindowPeakFinder

class FFTTuneFinder(object):
    """
    Find the tune using the fast fourier transform technique

    Apply a small displacement to the reference trajectory and track through a
    lattice; use the displaced trajectory 
    """

    def __init__(self, u_data = None, up_data = None, peak_finder = None,
                 use_hanning_filter = False):
        """
        Initialise the tune finder

        - u_data: position data, for use in Fourier Transform calculation
        - up_data: divergence data, only used for plotting (currently)
        - peak_finder: peak finder object, object used to find peaks in the tune
                diagram. If peak_finder is None, uses a WindowPeakFinder with a
                window size 10
        - use_hanning_filer: experimental hanning filter (probably doesnt work)
        """
        self._peak_finder = peak_finder
        if self._peak_finder == None:
            self._peak_finder = WindowPeakFinder(5, 0., 1)
        self.u = u_data
        self.up = up_data
        self.use_hanning_filter = use_hanning_filter 
        self.fractional_tune = None
        self.peak_x_list = []
        self.peak_y_list = []
        self.k_mag_x = None
        self.k_mag_y = None

    def get_tune(self, tune_tolerance = None):
        """
        Find the fractional tune for a given tracking object

        - tune_tolerance: tolerance with which the tune finder will attempt to
            calculate the tune. If set to None, FTTuneFinder will use
            1/len(u)/100

        Displaces the reference hit by an amount delta, tracks this hit using
        the tracking object and runs a one dimensional FFT against the axis
        variable. Number of samples used in the FFT is determined by the 
        tracking object (and hence accuracy of the tune calculation).

        Note that u_data must be of odd length for this algorithm; FFTTuneFinder
        will discard the last element if this is not the case.

        Returns the principle Fourier frequency that is not 0.
        """
        if self.u == None:
            raise ValueError("No data set for Fourier Transform")
        if len(self.u) % 2 == 0:
            if self.up != None:
                del self.up[-1]
            del self.u[-1]
        if tune_tolerance == None:
            tune_tolerance = 1./len(self.u)/100.
        self._fft_find_peaks()
        self._get_max_peak()
        if len(self.peak_x_list) == 0:
            self._sft_find_peaks(tune_tolerance)
        self._get_max_peak()
        if tune_tolerance < 1./len(self.k_mag_x):
            for i, k_x in enumerate(self.peak_x_list):
                try:
                    new_peak_x = self._recursive_refine_peak(k_x, tune_tolerance)
                    self.peak_x_list[i] = new_peak_x
                    index = self.k_mag_x.index(new_peak_x)
                    self.peak_y_list[i] = self.k_mag_y[index]
                except ValueError:
                    sys.excepthook(*sys.exc_info())
            self._get_max_peak()
        return self.fractional_tune

    def run_tracking(self, axis, delta, reference_hit, tracking, use_hits=None):
        """
        Set position data from tracking output

        - reference_hit: Hit on the closed orbit (for a ring).
        - axis: string, variable from Hit.get_variables() over which the tune
                will be found.
        - delta: float, displacement from the reference_hit.
        - tracking: xboa.tracking.TrackingBase, tracking object to propagate
                particles through the lattice.
        - use_hits: list of integers, only consider hits returned by tracking 
                with an index in use_hits. If set to None, consider all hits.
        """
        hit = reference_hit.deepcopy()
        hit[axis] += delta
        hits_out = tracking.track_one(hit)
        if use_hits != None:
            hits_out = [hit for i, hit in enumerate(hits_out) if i in use_hits]
        self.u = [hit[axis] for hit in hits_out]
        self.up = [hit["p"+axis] for hit in hits_out]


    def plot_signal(self, title):
        """
        Plot the FFT frequency spectrum
        - title, string used as a title in FFT plots
        Returns tuple of TCanvas, TH2, TGraph
        """
        canvas = common.make_root_canvas(title)
        x_list = range(len(self.u))
        hist, graph = common.make_root_graph(title,
                                             x_list, 'count', self.u, 'signal')
        hist.SetTitle(title)
        hist.Draw()
        graph.Draw('l')
        canvas.Update()
        return canvas, hist, graph

    def plot_phase_space(self, title):
        """
        Plot the phase space for the fourier transform
        - title, string used as a title in FFT plots
        Returns tuple of TCanvas, TH2, TGraph
        """
        # NEEDS TEST
        canvas = common.make_root_canvas(title)
        print(len(self.u), len(self.up))
        hist, graph = common.make_root_graph(title, self.u, 'displacement',
                                                    self.up, 'divergence')
        hist.SetTitle(title)
        hist.Draw()
        graph.SetMarkerStyle(26)
        graph.Draw('p')
        canvas.Update()
        return canvas, hist, graph


    def plot_fft(self, title, ymin=None, ymax=None):
        """
        Plot the FFT frequency spectrum
        - title, string used as a title in FFT plots
        Returns tuple of TCanvas, TH2, TGraph
        """
        if self.k_mag_x == None or self.k_mag_y == None:
            self.get_tune()
        canvas = common.make_root_canvas(title)
        if ymin == None:
            ymin = max([1e-5, min(self.k_mag_y)])
        hist, graph = common.make_root_graph(title, 
                                             self.k_mag_x, 'frequency',
                                             self.k_mag_y, 'magnitude',
                                             ymin=ymin, ymax=ymax)
        hist.SetTitle(title)
        hist.Draw()
        graph.Draw('l')
        canvas.SetLogy()
        canvas.Update()
        return canvas, hist, graph

    def plot_fft_fit(self, title, peak_k_index,
                     fit_lower_index, fit_upper_index, fit = None):
        """
        Draw the FFT spectrum and fit within a window
        - title, string title for the plot
        - peak_k_index, integer corresponding to element from self.k_mag which
          makes the seed for the position of the hit
        - fit_lower_bound, integer corresponding to the element from self.k_mag
          which makes the lower edge of the fit window
        - fit_lower_bound, integer corresponding to the element from self.k_mag
          which makes the upper edge of the fit window
        - fit, ROOT.TF1 used for fitting. If set to None, a Gaussian will be
          used with reasonable parameters. Note that user has responsibility to
          set the fit window in fit

        Uses the ROOT library to do the fit; this means drawing the data onto a
        ROOT Canvas using self.plot_fft. Fits with a Gaussian; in the presence
        of noisy/low statistics data, this can improve the estimate of tune. 

        Returns a tuple of TCanvas, TH2, TGraph, TF1. Hint:- to get the 
        fractional tune, use TF1::GetParameter(0); to get the estimated error,
        use TF1::GetParError(0).
        """
        canvas, hist, graph = self.plot_fft(title)
        fit_height = self.k_mag_y[peak_k_index]
        fit_centre = self.k_mag_x[peak_k_index]
        fit_low = self.k_mag_x[fit_lower_index]
        fit_hi = self.k_mag_x[fit_upper_index]
        if fit == None:
            fit_function = "[1]*exp(-((x-[0])*[2])**2)"
            fit = ROOT.TF1(title+" fit", fit_function, fit_low, fit_hi)
            fit.SetParameter(0, fit_centre)
            fit.SetParameter(1, fit_height)
            fit.SetParameter(2, fit_height)
        graph.Fit(fit)
        canvas.cd()
        fit.Draw("SAME")
        print("Got peak at", fit.GetParameter(0), "with error", fit.GetParError(0))
        canvas.Update()
        return canvas, hist, graph, fit

    def _get_max_peak(self):
        """
        Find the maximum peak in self.peak_index_list
        """
        peak_index_list = [self.k_mag_x.index(k_x) for k_x in self.peak_x_list]
        peak_values = [self.k_mag_y[i] for i in peak_index_list]
        if len(peak_values) == 0:
            raise ValueError("Can't get max peak - found no peaks at all")
        peak_max = max(peak_values)
        peak_index = self.k_mag_y.index(peak_max)
        self.fractional_tune = self.k_mag_x[peak_index]
        return peak_index

    def _sft_find_peaks(self, interval):
        """
        Perform a slow Fourier Transform and find any peaks
        """
        n_items = int(1./interval/2.)
        self.k_mag_x = [i*interval for i in range(n_items)]
        self.k_mag_y = [self._sft(k_x) for k_x in self.k_mag_x]
        self._find_peaks()

    def _fft_find_peaks(self):
        """
        Perform the Fast Fourier Transform and find any peaks
        """
        fft = numpy.fft.rfft(numpy.array(self.u))
        k_list = [[float(numpy.real(z)), float(numpy.imag(z))] for z in fft]
        self.k_mag_y = [(z[0]**2+z[1]**2)**0.5 for z in k_list]
        self.k_mag_x = [i/2./float(len(k_list)) for i, z in enumerate(k_list)]
        self._find_peaks()

    def _find_peaks(self):
        """
        Run the peak finder
        """
        peak_index_list = sorted(self._peak_finder.find_peaks(self.k_mag_y))
        if len(peak_index_list) == 0:
            return
        if peak_index_list[0] == 0:
            peak_index_list.pop(0)
        self.peak_x_list = [self.k_mag_x[i] for i in peak_index_list]
        self.peak_y_list = [self.k_mag_y[i] for i in peak_index_list]

    def _recursive_refine_peak(self, k_x, x_tolerance):
        """
        Use slow fourier transforms in the region of a peak to recursively
        improve the peak estimate to some tolerance.

        On each iteration, the new k_mag values are appended to k_mag_x/y.

        Stop recursing if the new value is < the neighbouring value; we assume
        this is numerical precision noise and the recursion has converged
        (implicit that the seed peak was closer than any troughs).

        Returns the new peak_index
        """
        peak_index = self.k_mag_x.index(k_x)
        if peak_index+1 == len(self.k_mag_y):
            peak_index -= 1
        y_values = [self.k_mag_y[peak_index-1],
                    self.k_mag_y[peak_index],
                    self.k_mag_y[peak_index+1]]
        if y_values[2] > y_values[0]:
            del y_values[0]
            x_values = [self.k_mag_x[peak_index],
                        self.k_mag_x[peak_index+1]]
            index_right = peak_index+1
        else:
            del y_values[2]
            x_values = [self.k_mag_x[peak_index-1],
                        self.k_mag_x[peak_index]]
            index_right = peak_index
        new_x = (x_values[0] + x_values[1])/2.
        new_y = self._sft(new_x)
        if abs(x_values[1] - x_values[0]) < x_tolerance:
            return self.k_mag_x[peak_index]
        self.k_mag_x.insert(index_right, new_x)
        self.k_mag_y.insert(index_right, new_y)
        # new index for the peak value;
        # if new_y is highest, peak index is the new_y index
        if new_y > y_values[0] and new_y > y_values[1]:
            new_peak_index = index_right
        # if new_y is lowest, the peak has split and we split the recursion 
        # (this is a bit dodgy)
        elif y_values[0] > new_y and y_values[1] > new_y:
            new_peak_index = self.k_mag_y.index(y_values[0])
            self._recursive_refine_peak(self.k_mag_x[new_peak_index], x_tolerance)
            new_peak_index = self.k_mag_y.index(y_values[1])
        # if y_values[0] is highest, peak index is unchanged
        elif y_values[0] > y_values[1]:
            new_peak_index = peak_index
        # else index of y_values[1], which is now 1 higher thanks to insert
        else:
            new_peak_index = peak_index + 1
        return self._recursive_refine_peak(self.k_mag_x[new_peak_index], x_tolerance)

    def _sft(self, k_x):
        """
        Calculate "Slow" Fourier Transform at k_x

        - k_x, float, position at which the sft is found
        - hanning filter, bool, set to True to apply a hanning filter

        "Slow" Fourier transform means using Sum(A_i cos(...) + A_i sin(...)) to
        get the FT at a given k value
        """
        y_point, z_point = 0., 0.
        n = float(len(self.u))
        hanning = 1.
        for m, a_m in enumerate(self.u):
            if self.use_hanning_filter:
                hanning = 2.*math.sin(math.pi*m/n)**2.
            f = 2.*math.pi*m*k_x*(n+1)/n
            dy = hanning*a_m*math.cos(f)
            dz = hanning*a_m*math.sin(f)
            y_point += dy
            z_point += dz
        k_y = (y_point**2+z_point**2)**0.5
        return k_y


