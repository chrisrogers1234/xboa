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
HullContent class should be imported directly from xboa.bunch.weighting
"""

import multiprocessing
import signal
import os

try:
    import numpy
except ImportError:
    pass
try:
    import scipy
except ImportError:
    pass

import xboa.common as common
import xboa.common.config as config

class HullContent(object):
    """
    HullContent class is used for parallelised calculation of convex hull
    contents from a Voronoi tesselation.
    """
    def __init__(self, tesselation, region_list, n_procs = 1):
        """
        Calculate the contents of the tesselation and store in tile_content_list
        - tesselation: object of type scipy.spatial.Voronoi containing the
          convex hulls (tiles) which need content calculated
        - region_list: list of regions over which hulls should be calculated.
        - n_procs: number of processes to use.
        """
        config.has_numpy()
        config.has_scipy()
        try:
            self.tesselation = tesselation
            self.region_list = region_list
            self.pool = multiprocessing.Pool(n_procs, _init_worker)
            self.tile_content_list = None
            self.recalculate()
        except:
            self.pool.terminate()
            raise
      

    def recalculate(self):
        """
        Recalculate the tile content list
        """
        job_list = [None]*len(self.region_list)
        for i in self.region_list:
            tile_index = self.tesselation.point_region[i]
            region = self.tesselation.regions[tile_index]
            tile_index = self.tesselation.point_region[i]
            region = self.tesselation.regions[tile_index]
            points = numpy.array([self.tesselation.vertices[j] for j in region])
            job_list[i] = (region, points)
        self.tile_content_list = self.pool.map(_tile_content, job_list)

def _init_worker():
    pass

def _get_cm_matrix(simplex, triangulation, dimension):
    elements = numpy.zeros([dimension+2, dimension+2])
    for i in range(1, dimension+2):
        elements[i, 0] = 1.
        elements[0, i] = 1.
    for i, vertex_i in enumerate(simplex):
        for j, vertex_j in enumerate(simplex[i+1:]):
            j += i+1
            point_i = triangulation.points[vertex_i]
            point_j = triangulation.points[vertex_j]
            square = [(point_i[d] - point_j[d])**2 \
                                             for d in xrange(dimension)]
            length_sq = sum(square)
            elements[i+1, j+1] = length_sq
            elements[j+1, i+1] = length_sq
    return elements

def _tile_content(args):
    """
    Calculate the tile content for the index at point_index

    Use Cayler-Menger determinant to calculate content of an arbitrary
    dimensional simplex.
    """
    try:
        region, points = args
        if -1 in region or len(region) == 0: # points at infinity
            return 0.
        dimension = numpy.shape(points)[1]
        content = 0.
        triangulation = scipy.spatial.Delaunay(points)
        coefficient = (-1)**(dimension+1)/2.**dimension
        coefficient /= numpy.math.factorial(dimension)**2.
        for simplex in triangulation.simplices:
            elements = _get_cm_matrix(simplex, triangulation, dimension)
            det = numpy.linalg.det(elements)
            if det != det: # underflow
                det = 0.
            this_content = (coefficient*det)**0.5
            if this_content == this_content:
                content += this_content
    # python bug - can't handle KeyboardInterrupt so we convert to a 
    # RuntimeError instead
    except KeyboardInterrupt:
        raise RuntimeError("KeyboardInterrupt helper")
    return content


