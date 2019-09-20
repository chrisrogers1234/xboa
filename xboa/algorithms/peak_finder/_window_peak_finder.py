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

class WindowPeakFinder(object):
    """
    Find peaks in a list of data points by looking for the peak within a window

    This algorithm will ignore subpeaks that are close to the main peak
    (assuming e.g. that they are noise)
    """
    def __init__(self, window_size, threshold_over_mean, window_step):
        """
        Initialise the peak finder
        - window_size integer size of the window over which we look for peaks.
        - threshold_over_mean float, require the peak to be greater than a 
          multiple of the data mean within the window to be registered
        - window_step float, move the window by window_step on each iteration
        """
        self.window_size = int(window_size)
        self.threshold = float(threshold_over_mean)
        self.window_step = int(window_step)

    def find_peaks(self, data):
        """
        Find peaks in the data

        - data list of floats that contains data within which we seek to find
        peaks

        Makes a window and looks for the highest value within that window. If
        the highest value is at the boundary of the window, it is ignored; else
        the peak is saved. The index corresponding to window start is then
        incremented by one and the routine is repeated.

        uses window_size that is the smallest of self.window_size and len(data)

        Returns a list of indices, each index corresponding to the location of a
        peak
        """
        peaks = []
        window_size = self.window_size
        if len(data) < self.window_size:
            window_size = len(data)
        win_sz_float = float(window_size)
        for i in range(0, len(data)-window_size+1, self.window_step):
            # optimisation - we can update max_value and max_index by just
            # checking the next entry, rather than checking the entire data set 
            test = data[i:i+window_size]
            max_value = max(test)
            max_index = test.index(max_value)
            if (i != 0 and max_index == 0) or \
               (i != len(data)-window_size and \
                max_index == window_size-1): # on bounds
                pass
            else:
                max_index += i
                if max_index not in peaks:
                    if self.threshold < 1.:
                        peaks.append(max_index)
                    else: # computationally expensive, so try to leave it til last
                        mean = sum(test)/win_sz_float
                        sigma = (sum([x**2 for x in test])-mean**2)**0.5\
                                /win_sz_float
                        if max_value-mean > sigma*self.threshold:
                            peaks.append(max_index)
        return peaks

