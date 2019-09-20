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

"""Cut smoothing module - expect to import from smoothing module directly
"""

import copy
import numpy

class CutSmoothing(object):
    """
    CutSmoothing class applies a smoothing by rejecting data that exceeds a
    certain value from the mean, for removing outliers.

    The CutSmoothing function has two parameters
    - cut_range (float) controls the deviation in the data that will be
      accepted. Data with -cut_range < y-y_mean < cut_range will be accepted.
    - step_ (int) controls the size of the window. The algorithm proceeds step
      wise, i.e. it will apply cuts on data in the range [i*step:(i+1)*step] for
      i in the range 0 to n_data/step. The last cut will always be applied on
      data like [n_data-step:n_data].
    """
    def __init__(self, cut_range, step):
        """
        Initialise the smoothing
        - cut_range (float) width of the accepted data
        - step_ (int) size of the cut window
        """
        self.cut_range = cut_range
        self.step = step

    def smooth(self, signal):
        """
        Smooth the signal
        - signal should be an iterable of numbers
        Returns a list of smoothed numbers
        """
        table_out = self.smooth_table([signal], 0)
        return table_out[0]

    def smooth_table(self, table, target_column):
        """
        Smooth a table of data, based on data from a single column.
        - table: iterable of iterables. All columns should be iterables of the 
                 same length.
        - target_column: indexes the column of data that will be considered for 
                  noise rejection. This should be a column of numbers.
        Returns a table of same type as smooth_table; all columns are of the 
        same length. Data is rejected based on the values in target_column.

        Columns need to support: access by (integer) index; del operation
        """
        signal = table[target_column]
        n_signal = len(signal)
        for column in table:
            if len(column) != n_signal:
                print column
                raise IndexError("Column with length "+str(len(column))+\
                                 " not equal to "+str(n_signal))
        will_cut_data = [False]*n_signal

        for i in range(n_signal/self.step):
            data_mean = numpy.mean(signal[i*self.step:(i+1)*self.step])
            for j in range(i*self.step, (i+1)*self.step):
                will_cut_data[j] = abs(signal[j]-data_mean) > self.cut_range

        data_mean = numpy.mean(signal[n_signal-self.step:n_signal])
        for j in range((n_signal/self.step)*self.step, n_signal):
            will_cut_data[j] = abs(signal[j]-data_mean) > self.cut_range

        table_out = copy.deepcopy(table)
        for column in table_out:
            n_cuts = 0
            for i in range(n_signal):
                if will_cut_data[i]:
                    del column[i-n_cuts]
                    n_cuts += 1
        return table_out
        

