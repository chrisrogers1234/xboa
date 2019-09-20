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

"""Gaussian smoothing module - expect to import from smoothing module directly
"""

import math

class GaussianSmoothing(object):
    """
    Gaussian smoothing class applies a smoothing by summing nearby data and
    weighting according to a truncated Gaussian distribution.

    The Smoothing function has two parameters
    - sigma (float) controls the width of the Gaussian distribution
    - range_ (int) controls the truncation of the Gaussian. Only data points 
      within range_ of the principle data point will be added into the smoothed
      value of the principle data point.
    - boundary

    Smoothing near to the boundaries is performed using whatever data is
    available. Normalisation at the boundaries can be handled in either of two
    ways
    - if adjust_boundary_normalisation is True, normalisation is performed using
      the sum of available weights (so if we are on the boundary, the 
      normalisation factor is increased and we get larger weightings).
    - if adjust_boundary_normalisation is False, every smoothed element gets the
      same weighting.
    """
    def __init__(self, sigma, range_, adjust_boundary_normalisation):
        """
        Initialise the smoothing
        - sigma (float) width of the Gaussian distribution
        - range_ (int) truncation distance applied to the Gaussian distribution
        - adjust_boundary_normalisation (bool) set to true to adjust the
          normalisation factor near to the edge of the data array due to the
          fact there are fewer elements in the smoothing
        """
        self.sigma = sigma
        self.range_ = range_
        two_sig_sq = 2.*sigma**2
        self._weights = [math.exp(-i**2./two_sig_sq) \
                         for i in range(-self.range_, self.range_+1)]
        self.norm = None
        if not adjust_boundary_normalisation:
            self.norm = sum(self._weights)

    def smooth(self, signal):
        """Smooth the signal"""
        signal_out = [self._smooth_one(signal, i) for i in range(len(signal))]
        return signal_out

    def _smooth_one(self, signal, i):
        """Smooth the point in signal at index i"""
        s_0 = max(0, i-self.range_)
        s_1 = min(len(signal), i+self.range_+1)
        sigs = [signal[s_index] for s_index in range(s_0, s_1)]

        w_0 = s_0 - i + self.range_
        w_1 = s_1 - i + self.range_
        assert(w_1-w_0 == s_1 - s_0)
        weights = [self._weights[w_index] for w_index in range(w_0, w_1)]

        if self.norm == None: # variable normalisation factor
            this_norm = sum(weights)
        else: # fixed normalisation factor
            this_norm = self.norm
        weighted = [weights[j]*sigs[j]/this_norm for j in range(s_1-s_0)]
        smoothed = sum(weighted)
        return smoothed

