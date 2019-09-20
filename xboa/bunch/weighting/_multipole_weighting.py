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
@namespace xboa::bunch::weighting::_multipole_weighting is a placeholder for the
MultipoleWeighting class
"""

import bisect
import numpy

class MultipoleWeighting(object):
    """
    Multipole weighting algorithm calculates weights matching some polynomial
    in the dynamical variables.

    See C. T. Rogers "Statistical Weighting for the MICE Beam", EPAC 2006
    """
    def __init__(self, maximum_pole, weight_variables,
                 target_ellipse, target_mean):
        """
        Multipole weighting algorithm
        """
        self.maximum_moment = maximum_pole
        self.weight_variables = weight_variables
        self.v_f_list = None
        self.v_g_list = None
        self.v_f_index_by_power = None
        self.v_g_index_by_power = None
        self._moments_from_ellipse(target_mean, target_ellipse)

    def apply_weights(self, bunch, global_cut):
        """
        Calculate the multipole coefficients and apply statistical weights
        - bunch: object of type xboa.bunch.Bunch containing hit data
        - global_cut: if True statistical weights will be applied to
          hit['global_weight']; else statistical weights will be applied to
          hit['local_weight']
        """
        coefficients = self._calculate_coefficients(bunch)
        weight_var = 'local_weight'
        if global_cut:
            weight_var = 'global_weight'

        # apply weights
        hit_data = bunch.list_get_hit_variable(self.weight_variables)
        sum_weights = 0.
        for i, hit in enumerate(bunch):
            w_i = 1.
            for j, coeff in enumerate(coefficients):
                this_w = coeff # coeff is a_j
                index = self.v_g_index_by_power[j]
                for k, power in enumerate(index):
                    this_w *= hit_data[k][i]**power # this_w is a_j*x_k^power
                w_i += this_w
            sum_weights += w_i/len(bunch)
            bunch[i][weight_var] *= w_i
        # normalise to length of bunch
        for hit in bunch:
            hit[weight_var] /= sum_weights
        return bunch

    def set_target_moments(self, moment_index_list, moment_list):
        """
        Set the desired moments
        - moment_index_list: list of the "power_index" of the moment, which
          identifies the corresponding moment in the moment_list. So if
          weight_variables is ["x", "px"] then the first moments (means) of the
          weight_variables would have moment_indices of [1, 0] and [0, 1] for
          "x" mean and "px" mean respectively. Variance in "x" would have a
          moment index of [2, 0] for <x^2*px^0>. Covariance in x, px would have a
          moment index of [1, 1] for <x^1*px^1>

          So should be a list of list of ints; all list of ints should have the 
          same length as weight_variables; each element should be unique; 
        - moment_list: list of the raw, uncentred moments that the algorithm 
          will attempt to set (i.e. don't subtract the mean). Each list element
          should correspond to a moment from moment_index_list. 
        """
        if len(moment_index_list) != len(moment_list):
            raise ValueError("Length of moment_index_list is different to "+\
                  "length of moment_list")
        for item in moment_index_list:
            if len(item) != len(self.weight_variables):
                raise ValueError(
                    "index length is different to weight_variables length"
                )
            for index in item:
                if type(index) != type(0):
                    raise ValueError("Index type is non-integer")

        for i, item in enumerate(moment_index_list[1:]):
            if item == moment_index_list[i]:
               raise ValueError("Indices should be unique")
        # zip and sort
        sorted_list = sorted(zip(moment_index_list, moment_list))
        # unzip
        self.v_g_index_by_power, self.v_g_list = zip(*sorted_list)

    def _calculate_coefficients(self, bunch):
        """
        Calculate multipole coefficients
        """
        self._setup(bunch)
        m_matrix = numpy.zeros([len(self.v_g_index_by_power),
                                len(self.v_g_index_by_power)])
        for i, list_i in enumerate(self.v_g_index_by_power):
            for j, list_j in enumerate(self.v_g_index_by_power):
                list_ij = [list_i[i1]+list_j[i1] \
                                           for i1, index_i in enumerate(list_i)]
                m_matrix[i, j] = \
                      self._v_f(list_ij) - self._v_f(list_i) * self._v_g(list_j)
        m_inverse = numpy.linalg.inv(m_matrix)
        u_vector = numpy.zeros([len(self.v_g_index_by_power)])
        for i, list_i in enumerate(self.v_g_index_by_power):
            u_vector[i] = self._v_g(list_i) - self._v_f(list_i)
        a_vector = numpy.dot(m_inverse, u_vector)
        return a_vector

    def _v_f(self, index_list):
        """
        Get the element in v_f corresponding to index_list
        """
        index = bisect.bisect_left(self.v_f_index_by_power, index_list)
        v_f_ = self.v_f_list[index]
        return v_f_

    def _v_g(self, index_list):
        """
        Get the element in v_g corresponding to index_list
        """
        index = bisect.bisect_left(self.v_g_index_by_power, index_list)
        v_g_ = self.v_g_list[index]
        return v_g_

    def _setup(self, bunch):
        """
        Calculate v_f for the bunch
        """
        self.v_f_index_by_power = bunch._Bunch__bunchcore.index_by_power\
                         (2*self.maximum_moment, len(self.weight_variables))[1:]
        self.v_f_list = bunch._Bunch__bunchcore.moment_tensor\
                             (self.weight_variables, 2*self.maximum_moment)[1:]
        sorted_list = sorted(zip(self.v_f_index_by_power, self.v_f_list))
        self.v_f_index_by_power, self.v_f_list = zip(*sorted_list)

    def _moments_from_ellipse(self, target_mean, target_ellipse):
        """
        Calculate moments based on ellipses
        """
        n_vars = len(self.weight_variables)
        indices, moments = [], []
        for i in range(n_vars):
            indices.append([0]*n_vars)
            indices[-1][i] += 1
            moments.append(target_mean[i])
        for i in range(n_vars):
            for j in range(i, n_vars):
              indices.append([0]*n_vars)
              indices[-1][i] += 1
              indices[-1][j] += 1
              moments.append(target_ellipse[i, j])
        self.set_target_moments(indices, moments)

def index_by_power():
    pass



