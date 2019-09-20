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

import xboa.common as common

try:
    import ROOT
except ImportError:
    pass
try:
    import numpy
except ImportError:
    pass

class RefinePeakFinder(object):
    """
    Find peaks in a list of data points when you have an estimate of the peaks
    position already, using a quadratic fit (in ROOT) to the peak. This can help
    to refine a peak estimate e.g. in the presence of noise.

    The quality of the fit is estimated using the RMS of the residuals compared
    to the RMS of the actual data within a certain range of the estimated peak.
    """
    def __init__(self, peak_list, delta_seed, max_delta, draw):
        """
        Initialise the peak finder
        - peak_list: [list of ints] list of integer indices of estimated peak
                     positions
        - delta_seed: [int] xboa initially considers points within a range given
                      by delta_seed from the estimated peak position to refine
                      the peak; xboa subsequently then varies delta to improve
                      the fit quality.
        - max_delta: [int] delta cannot increment beyond max_delta.
        - draw: [bool] set to True to draw the fits. In fit plots, "0" is the
                estimated peak position
        """
        self.fit = None
        self.peak_list = peak_list
        self.delta_seed = delta_seed
        self.max_delta = max_delta
        self.draw = draw

    @classmethod
    def sigma(self, data):
        """
        Find the standard deviation from the mean of data

        - data: list of floats containing data

        Retuns float S(x**2)/N - {S(x)/N}**2 where N is the length of data
        """
        mean_square_sum = sum([y**2 for y in data])/len(data)
        mean_sum_square = sum([y for y in data])/len(data)
        return (mean_square_sum-mean_sum_square**2)**0.5

    def _peak_fit(self, data, peak_index, delta_fit, delta_bite):
        """
        Fit the data in the vicinity of peak_index to a quadratic

        - data: list of floats containing data
        - peak_index: the index at which the peak is found
        - delta_fit: the maximum distance from the peak from which data will be
                     drawn for fitting
        - delta_bite: the maximum distance from the peak from which data will be
                     drawn for assessing fit quality

        Goodness-of-fit is an estimation of how well the data is fitted, based
        on comparing the standard deviation of the fit residuals to the sigma of
        data within a small "bite". fit_quality is given by comparing sigma
        (standard deviation) of data in a small bite with sigma of fit
        residuals, like
            Q = (sigma(res)/sigma(bite)-1.)*N(bite)**0.5
        sigma(bite) in this sense is taken to be the natural spread of the raw
        data, and we seek to ensure sigma(res) does not go much above this
        spread.

        Return value is a tuple of (fit_quality, histogram, graph, fit)
        - fit_quality: goodness-of-fit estimation. 
        """
        x_min = max(peak_index-delta_fit, 0)
        x_max = min(peak_index+delta_fit+1, len(data))
        x_list = range(x_min-peak_index, x_max-peak_index)
        y_list = data[x_min:x_max]
        hist, graph = common.make_root_graph("name", x_list, "", data[x_min:x_max], "")
        if self.fit == None:
            quadratic = "[0]+[1]*x+[2]*x*x"
            self.fit = ROOT.TF1("fit", quadratic, min(y_list), max(y_list))
        fit = self.fit
        fit.SetRange(min(y_list), max(y_list))
        for i in range(3):
            fit.ReleaseParameter(i)
            fit.SetParameter(i, 0.)
        #QNOS: Quiet, Do not store graphics, Dont draw
        graph.Fit(fit, 'QNO')
        delta_list = [y_list[i]-fit.Eval(x) for i, x in enumerate(x_list)]
        sigma_delta = self.sigma(delta_list)
        sigma_bite = self.sigma(y_list[delta_fit-delta_bite:delta_fit+delta_bite])
        # fit_quality = (s(residual)/s(data)-1.)*sqrt(n)
        # where n is the number in the s(data) calculation
        fit_quality = (sigma_delta/sigma_bite-1.)*delta_bite**0.5
        return fit_quality, hist, graph, fit

    def find_peak_errors(self, data):
        """
        Find the error on the peak estimation based on a linear fit to the
        derivative
        """
        # we want to fit for x = my + c
        # c is the peak
        # chi2 gives estimate of fit errors
        this_max_delta = min(len(data), self.max_delta)
        peak_with_errors = []
        fit_quality = 0.
        fail_list = []
        for peak in self.peak_list:
            delta_fit = self.delta_seed
            while fit_quality < 1. and delta_fit < this_max_delta:
                delta_fit *= 2
                try:
                    fit_quality, hist, graph, fit = self._peak_fit(data, peak, delta_fit, self.delta_seed)
                except Exception:
                    break
            delta_fit /= 2
            fit_quality, hist, graph, fit = self._peak_fit(data, peak, delta_fit, self.delta_seed)
            if self.draw:
                canvas = common.make_root_canvas("values")
                canvas.Draw()
                canvas.cd()
                hist.Draw()
                graph.SetMarkerStyle(6)
                graph.Draw('p')
                fit_result = graph.Fit(fit, "S") #Return FitResult
                self.fit_list.append(fit)
                self.fit = None
                canvas.Update()
            else:
                #QNOS: Quiet, Do not store graphics, Dont draw, Return FitResult
                fit_result = graph.Fit(fit, 'QNOS')
                common.clear_root()
            
            p0 = fit.GetParameter(0)
            p1 = fit.GetParameter(1)
            p2 = fit.GetParameter(2)


            peak_out = [-p1/2./p2+peak, -p1*p1/4./p2+p0] #x, y
            if abs(peak_out[0]-peak) > delta_fit or \
                   peak_out[0] < 0 or \
                   peak_out[0] > len(data):
                continue
            J = numpy.matrix([[0., -1./2./p2,    p1/2./p2/p2],
                             [1., -p1/2./p2, p1*p1/4./p2/p2]])
            JT = J.T
            CovP = numpy.matrix([
                      [fit_result.GetCovarianceMatrix()(i, j) for i in range(3)]
                                                              for j in range(3)])
            CovPeak = J*CovP*JT
            if self.draw:
                print "=========="
                print "Fit parameters"
                print numpy.array([p0, p1, p2])
                print "Fit errors"
                print CovP            
                print "Jacobian"
                print J
                print "Peak x, y"
                print numpy.array(peak_out)
                print "Covariances errors"
                print CovPeak
                print "=========="
            CovPeak = [[CovPeak[i, j] for i in range(2)] for j in range(2)]
            peak_with_errors.append({"x":peak_out[0],
                                     "y":peak_out[1],
                                     "x_in":peak,
                                     "cov(x,y)":CovPeak})
        return peak_with_errors

    def find_peaks(self, data):
        """
        Find peaks in the data

        - data list of floats that contains ordinates (y-axis values) of data
                 abscissa are assumed to be data index.

        Returns a list of indices, each index corresponding to the location of a
        peak in data
        """
        peak_error_list = self.find_peak_errors(data)
        peak_list = [int(x["x"]) for x in peak_error_list]
        return peak_list

    fit_list = []

