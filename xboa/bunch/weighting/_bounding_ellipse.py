#This file is a part of xboa
#
#xboa is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#xboa is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with xboa in the doc folder.  If not, see
#<http://www.gnu.org/licenses/>.

"""
BoundingEllipse class should be imported directly from xboa.bunch.weighting
"""

try:
    import numpy
except ImportError:
    pass

import xboa.common as common
import xboa.common.config as config

class BoundingEllipse(object):
    """
    The BoundingEllipse class defines an arbitrary dimensional ellipse that can
    be taken as a boundary for VoronoiWeighting.

    The bounding ellipse is defined by the locus of points \f$\vec{x}\f$ \n
        \f$ (\vec{x}-\bar{x})^T \mathbf{V^{-1}} (\vec{x}-\bar{x}) = 1 \f$\n
    where \f$\mathbf{V}\f$ is a matrix defining the ellipse orientation and
    \f$ \bar{x} \f$ is a vector defining the ellipse centroid. The
    BoundingEllipse can be used to eliminate points outside of the ellipse
    and define a (finite) set of points distributed about the ellipse boundary.
    """

    def __init__(self, limit_ellipse, limit_mean, limit_n_per_dim):
        """
        Initialise the bounding ellipse
        - limit_ellipse: defines the ellipse. Should be a numpy.array with shape
          (dimension, dimension).
        - limit_mean: defines the ellipse centroid. Should be a numpy.array with
          shape (dimension).
        - limit_n_per_dim: integer that defines the number \f$n\f$ of points on
          the ellipse boundary. xboa will set up points distributed evenly
          about the ellipse, with the number given by \f$n^{D}\f$ where \f$D\f$
          is the ellipse dimension.
        """
        config.has_numpy()
        self.dim = numpy.shape(limit_ellipse)[0]
        if type(limit_n_per_dim) != type(1) or limit_n_per_dim < 1:
            raise ValueError("limit_n_per_dim should be an integer > 1")
        if numpy.shape(limit_ellipse) != (self.dim, self.dim):
            raise ValueError("limit_ellipse shape "+\
                str(numpy.shape(limit_ellipse))+" should be "+\
                str((self.dim, self.dim)))
        if numpy.shape(limit_mean) != (self.dim,):
            raise ValueError("limit_mean shape "+\
                str(numpy.shape(limit_mean))+" should be "+\
                str((self.dim,)))
        self.bounding_points = common.make_shell(limit_n_per_dim,
                                                 limit_ellipse)
        bp_temp = [None]*numpy.shape(self.bounding_points)[0]
        for i, row in enumerate(self.bounding_points):
            bp_temp[i] = [None]*self.dim
            for j in range(self.dim):
                bp_temp[i][j] = row[0, j]+limit_mean[j]
        self.bounding_points = numpy.array(bp_temp)
        self.ellipse_det = numpy.linalg.det(limit_ellipse)
        self.ellipse_inv = numpy.linalg.inv(limit_ellipse)
        self.mean = limit_mean

    def cut_on_bound(self, points_in):
        """
        Iterate over the points, and delete items that are outside the ellipse.
        - points_in. Set of n points in form of a numpy array with shape
          (n, dimension).
        Returns a tuple of (points_out, not_cut_indices) where points_out is a
        numpy array of shape (m, dimension) containing all points that sit on or
        inside the ellipse boundary and not_cut_indices is a list of integers
        of length m corresponding to the position in points_in of each of the m
        points_out.
        """
        points = points_in
        i = 0
        index = 0
        not_cut_indices = []
        while i < len(points):
            point = points[i]
            delta = point - self.mean
            delta_t = numpy.transpose(delta)
            arg = delta.dot(self.ellipse_inv.dot(delta_t))
            if arg > 1.:
                points = numpy.delete(points, i, 0)
            else:
                not_cut_indices.append(index)
                i += 1
            index += 1
        return points, not_cut_indices

