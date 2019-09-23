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

"""
\namespace xboa::tracking::_matrix_tracking

Should be imported directly from the xboa::tracking namespace
"""

import numpy

from xboa import common as Common
from xboa.hit import Hit
from ._tracking_base import TrackingBase 

class MatrixTracking(TrackingBase):
    """
    Class to mimic tracking using simple, user-supplied transfer matrices
    Each transfer matrix M_i0 must be of type numpy.matrix, where M is defined
    by u_i = M_i*(u_in-v_in) + v_i and u, v are matrices with shape (1, 6)
    going like (x, px, y, py, t, energy)
    """
    def __init__(self, list_of_transfer_matrices, list_of_offsets, offset_in):
        """
        Initialisation
        - list_of_transfer_matrices list of transfer matrices. Each element
              should be a numpy matrix of shape (6,6)
        - list_of_offsets list of offsets v_i. Each element should be a numpy
              matrix of shape (1,6)
        - offset_in offset v_in. Should be a numpy matrix of shape (1,6)
        """
        TrackingBase.__init__(self)
        if len(list_of_offsets) != len(list_of_transfer_matrices):
            raise IndexError(
              "list_of_offsets must be same length as list_of_tranfer_matrices")
        mat_type = type(numpy.matrix([0.]))
        for offset in list_of_offsets+[offset_in]:
            if type(offset) != mat_type:
                raise TypeError("Offset should be of type "+str(mat_type)+\
                                " not "+str(type(offset)))
            if offset.shape != (1, 6):
                raise TypeError("Offset should be of shape (1,6) not "+\
                                str(offset.shape))
        for tm in list_of_transfer_matrices:
            if type(tm) != mat_type:
                raise TypeError("Matrix should be of type "+str(mat_type)+\
                                " not "+str(type(tm)))
            if tm.shape != (6, 6):
                raise TypeError("Matrix should be of shape (6,6) not "+\
                                str(tm.shape))
        self.tm_list = list_of_transfer_matrices
        self.offset_list = list_of_offsets
        self.offset_in = offset_in

    def track_one(self, hit):
        """
        Track a hit and return a list of output hits
        - hit initial particle coordinates to be tracked

        Return a list of hits, with the first hit being equal to the input hit
        and subsequent hits given by u_i = M_i0 * u_0 with
        u = (x, px, y, py, t, energy)
        """
        hit_list = [hit.deepcopy()]
        for i, tm in enumerate(self.tm_list):
            offset_out = self.offset_list[i]
            vec_in = numpy.matrix([hit['x'], hit['px'], 
                                  hit['y'], hit['py'],
                                  hit['t'], hit['energy']])
            vec_in -= self.offset_in
            vec_out = tm * vec_in.transpose() + offset_out.transpose()
            hit_out = hit.deepcopy()
            for i, key in enumerate(["x", "px", "y", "py", "t", "energy"]):
                hit_out[key] = float(vec_out[i])
            hit_out.mass_shell_condition("pz")
            hit_list.append(hit_out)
        self.last = [hit_list]
        return hit_list

