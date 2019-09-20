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

class UphillDownhillPeakFinder(object):
    """
    Find peaks in a list of data by looking at first derivative
    """
    def __init__(self):
        """
        Initialise the peak finder
        """
        self.fit = ROOT.TF1("fit","[0]+[1]*x+[2]*x*x+[3]*x*x*x+[4]*x*x*x", 0., 1.)

    def _get_derivative(self, data):
        return [data[i+1]-data[i] for i, x in enumerate(data[1:])]

    def find_peak_errors_derivative(self, data, peak_list, delta_index, draw=False):
        """
        Find the error on the peak estimation based on a linear fit to the
        derivative
        """
        derivative = self._get_derivative(data)
        # we want to fit for x = my + c
        # c is the peak
        # chi2 gives estimate of fit errors
        peak_with_errors = []
        for peak in peak_list:
            x_min = max(peak-delta_index, 0)
            x_max = min(peak+delta_index+1, len(derivative))
            x_list = range(x_min, x_max)
            y_list = derivative[x_min:x_max]
            graph = ROOT.TGraph(len(x_list))
            for i in range(5):
                self.fit.SetParameter(i, 0.)
            for i in range(2, 5):
                self.fit.FixParameter(i, 0.)
            self.fit.SetRange(min(y_list), max(y_list))
            for i, x in enumerate(x_list):
                y = y_list[i]
                graph.SetPoint(i, y, x) # note this is intentionally backwards
            graph.Fit(self.fit, "NO")
            if draw:
                canvas = common.make_root_canvas("derivatives")
                canvas.Draw()
                canvas.cd()
                hist, graph = common.make_root_graph("name", x_list, "", y_list, "")
                hist.Draw()
                graph.SetMarkerStyle(6)
                graph.Draw('p')
                canvas.Update()

                canvas = common.make_root_canvas("values")
                canvas.Draw()
                canvas.cd()
                hist, graph = common.make_root_graph("name", x_list, "", data[x_min:x_max], "")
                hist.Draw()
                graph.SetMarkerStyle(6)
                graph.Draw('p')
                canvas.Update()
            peak_with_errors.append([self.fit.GetParameter(0),
                                     self.fit.GetParError(0)])
        return peak_with_errors


    def find_peaks(self, data):
        """
        Find peaks in the data
        """
        derivative = self._get_derivative(data)
        peak_list = []
        for i, x in enumerate(derivative[1:]):
            if derivative[i] > 0. and derivative[i+1] < 0.: 
                peak_list.append(i+1)
        return peak_list

    fit_list = []

