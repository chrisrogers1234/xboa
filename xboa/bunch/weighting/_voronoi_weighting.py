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
VoronoiWeighting class should be imported directly from xboa.bunch.weighting
"""

import math
import bisect
import multiprocessing

try:
    import numpy
except ImportError:
    pass
try:
    import scipy.spatial
except ImportError:
    pass

try:
    import ROOT
except ImportError:
    pass

import xboa.common as common
import xboa.common.config as config

import xboa.bunch.weighting

class VoronoiWeighting(object):
    """
    VoronoiWeighting class enables the user to set statistical weights of Hits
    in a Bunch based on how close they are to neighbouring Hits. The basic
    principle is that if a Hit is in a sparsely populated region of phase space,
    but the desired probability distribution would have the Hit in a more
    densely populated region, we can apply a greater statistical weight to that
    Hit (i.e. we "count" the Hit more than once in e.g. moment calculations
    etc).

    In order to calculate how sparsely populated a particular region is, xboa
    uses a "Voronoi" tesselation. xboa determines the nearest Hits surrounding a
    given Hit, draws lines to those neighbours and then bisects the lines. This
    generates a closed region around the Hit that is closer to that Hit than any
    other.

    xboa calculates the "content" i.e. area/volume/hypervolume of the Voronoi
    tile for each Hit. Hits which sit in a tile with a larger content are
    assumed to be in a more sparsely populated region of phase space, while
    those that sit in a region with a smaller content are assumed to be in a
    less sparsely populated region of phase space.

    xboa assigns weights to each Hit according to a multivariate gaussian. In
    order to prevent Hits on the edge of the distribution from acquiring a
    disproportionate weighting, it is possible to define a bound around the
    distribution. Hits outside the bound are disregarded. A few points are
    defined on the bound, which prevent large Voronoi cells from being
    generated.
    """

    def __init__(self, weight_variables, weight_ellipse,
                 weight_mean = None, voronoi_bound = None):
        """
        Initialise the VoronoiWeighting
        - weight_variables: list of string variable names for call to
          Bunch.get_hit_variable(...). The VoronoiWeighting dimension is equal
          to the length of the list.
        - weight_ellipse: numpy.array corresponding to the covariance matrix of
          the desired multivariate gaussian. Should have numpy.shape like
          (dimension, dimension) where dimension is the dimension of the
          VoronoiWeighting.
        - weight_mean: numpy.array corresponding to the mean of the desired
          multivariate gaussian. If set to None, defaults to array of 0s. Should
          have numpy.shape like (dimension) where dimension is the dimension of
          the VoronoiWeighting.
        - voronoi_bound: BoundingEllipse, corresponding to the maximum bound at
          which Hits are accepted in the VoronoiWeighting. Hits outside this
          bound will have weight set to 0. The ellipse bounding_points are used
          as an external boundary to prevent Voronoi tesselations from getting a
          big tile content (i.e. area/volume/hypervolume).

        Requires numpy and scipy to be installed.

        Returns a VoronoiWeighting object.
        """
        config.has_numpy()
        config.has_scipy()
        self.dim = len(weight_variables)
        if weight_mean == None:
            weight_mean = numpy.array([0.]*self.dim)
        if (self.dim,) != numpy.shape(weight_mean):
            raise ValueError("weight_mean shape "+\
                str(numpy.shape(weight_mean))+" should be "+\
                str((self.dim,))
                )
        if numpy.shape(weight_ellipse) != (self.dim, self.dim):
            raise ValueError("weight_ellipse shape "+\
                    str(numpy.shape(weight_ellipse))+" should be "+\
                    str((self.dim, self.dim))
                )
        self.voronoi_bound = None
        if voronoi_bound != None:
            if voronoi_bound.dim != self.dim:
                raise ValueError("voronoi_bound dimension should be same as "+\
                      "VoronoiWeighting dimension")

            self.voronoi_bound = voronoi_bound
        self.weight_variables = weight_variables
        self.weight_ellipse_inv = numpy.linalg.inv(weight_ellipse)
        self.weight_ellipse_det = numpy.linalg.det(weight_ellipse)
        self.weight_mean = weight_mean
        self.weight_list = None
        self.tesselation = None
        self.tile_content_list = None
        self.real_points = None

    def apply_weights(self, bunch, global_cut, number_of_processes = 1):
        """
        Apply a weighting \f$w_i\f$ to each Hit in bunch corresponding to\n
                    \f$ w_i = c_i f(x_i) \f$\n
        where \f$c_i\f$ is the content of each Voronoi tile and \f$f(x_i)\f$ is
        the value of a multivariate gaussian evaluated at \f$x_i\f$.
        - bunch: xboa.bunch.Bunch object. Evaluate weights for all Hits in bunch
        - global_cut: if set to True, weighting will be applied to the hit's
          global_weight. If set to False, weighting will be applied to the hit's
          local_weight.
        - number_of_processes: number of processes to use for calculating tile 
          content. VoronoiWeighting will use multiprocessing module to make 
          subprocesses to calculate tile content.

        Returns None (the bunch is weighted "in-place")
        """
        self.real_points = bunch.list_get_hit_variable(self.weight_variables)
        self.real_points = zip(*tuple(self.real_points))
        self.real_points = numpy.array(self.real_points)
        if self.voronoi_bound != None:
            self.real_points, not_cut = \
                               self.voronoi_bound.cut_on_bound(self.real_points)
            points = numpy.vstack((self.real_points,
                                   self.voronoi_bound.bounding_points))
        else:
            points = self.real_points
            not_cut = range(len(self.real_points))
        self.tesselation = scipy.spatial.Voronoi(points)
        point_list = range(len(self.real_points))
        self.tile_content_list =  xboa.bunch.weighting.HullContent(self.tesselation, point_list, number_of_processes).tile_content_list
        if global_cut:
            weight = 'global_weight'
        else:
            weight = 'local_weight'
        self.weight_list = [None]*len(bunch)
        for i, hit_index in enumerate(not_cut):
            hit = bunch[hit_index]
            pdf_target = self.get_pdf(self.real_points[i])
            self.weight_list[i] = pdf_target*self.tile_content_list[i]
            hit[weight] = self.weight_list[i]
        for i, hit in enumerate(bunch):
            if i not in not_cut:
                hit[weight] = 0.

    def get_pdf(self, point):
        """
        Calculate a multivariate gaussian at point.
        - bunch: xboa.bunch.Bunch object. Evaluate weights for all Hits in bunch
        - global_cut: if set to True, weighting will be applied to the hit's
          global_weight. If set to False, weighting will be applied to the hit's
          local_weight.
        """
        norm = (2.*math.pi)**numpy.shape(point)[0]*self.weight_ellipse_det
        delta = point - self.weight_mean
        delta_t = numpy.transpose(delta)
        arg = -0.5*delta.dot(self.weight_ellipse_inv.dot(delta_t))
        gauss = math.exp(arg)/norm**0.5
        return gauss

    def plot_two_d_projection(self, projection_axes, fill_option = None,
                              lower = None, upper = None):
        """
        Plot a 2D projection of the voronoi cells.
        - projection_axes: list of length two. Determines the projection that
          will be drawn. Should be a subset of the weight_variables.
        - fill_option: if set to None or 'none', tiles will not be filled. If
          set to 'weight', 'content', 'pdf', tiles will be filled according to
          the calculated point weight, calculated tile content or probability
          density function for that point.
        - lower: integer lower bound for slicing of the tesselation regions. If
          set to None, defaults to 0.
        - upper: integer upper bound for slicing of the tesselation regions. If
          set to None, defaults to the end of the tesselation regions list.

        Requires ROOT to be installed.

        Returns a tuple of (canvas, histogram, point_graph, tile_graph_list)
        where canvas is the ROOT TCanvas, histogram is the ROOT TH2D that makes
        the graph axes, point_graph is the graph with the points plotted,
        tile_graph_list is a list of graphs, one for each tile.
        """
        config.has_root()
        if lower == None:
            lower = 0
        if upper == None:
            upper = len(self.real_points)
        if len(projection_axes) != 2:
            raise ValueError("Expected projection axes of length 2")
        if projection_axes[0] not in self.weight_variables or \
           projection_axes[1] not in self.weight_variables:
            raise ValueError("Projection axes "+str(projection_axes)+\
                             " should be a subset of weight_variables "+
                             str(weight_variables))
        if self.tesselation == None:
            raise ValueError("Need to apply_weights before tesselation can be"+
                             "plotted")
        title = "tesselation_"+str(projection_axes[0])+"_"+\
                str(projection_axes[1])
        canvas = common.make_root_canvas(title)
        proj = [self.weight_variables.index(x) for x in projection_axes]
        x_list = [vertex[proj[0]] for vertex in self.tesselation.vertices]
        y_list = [vertex[proj[1]] for vertex in self.tesselation.vertices]
        points = numpy.transpose(self.real_points)
        hist, points_graph = common.make_root_graph(title,
                                                    points[0][lower:upper],
                                                    projection_axes[0],
                                                    points[1][lower:upper],
                                                    projection_axes[1])
        if fill_option != None and fill_option != 'none':
            hist.SetTitle('Color by '+fill_option)
        hist.Draw("colz")
        points_graph.SetMarkerStyle(6)
        tile_graphs = []
        fill_colors = self._get_fill_colors(fill_option, lower, upper)
        for point_index, tile_index in \
                          enumerate(self.tesselation.point_region[lower:upper]):
            tile = self.tesselation.regions[tile_index]
            if -1 in tile or len(tile) == 0: # points at infinity
                continue
            graph = ROOT.TGraph(len(tile)+1)
            tile_graphs.append(graph)
            for i, vertex_index in enumerate(tile):
                graph.SetPoint(i,
                               x_list[vertex_index],
                               y_list[vertex_index])
            graph.SetPoint(len(tile),
                           x_list[tile[0]],
                           y_list[tile[0]])
            graph.SetFillColor(fill_colors[point_index])
            graph.Draw('f')
            graph.Draw('l')
        points_graph.Draw('p')
        canvas.Update()
        common._common._hist_persistent += tile_graphs
        return canvas, hist, points_graph, tile_graphs

    def _get_fill_colors(self, fill_option, lower, upper):
        """Get fill colors for plot_two_d_projection"""
        if fill_option == "weight":
            fill_data = self.weight_list[lower:upper]
        elif fill_option == "content":
            fill_data = self.tile_content_list[lower:upper]
        elif fill_option == "pdf":
            fill_data = [self.get_pdf(point) for point in self.real_points]\
                                                                   [lower:upper]
        elif fill_option == "none" or fill_option == None:
            return [0]*len(self.real_points) # always white
        else:
            raise ValueError("Did not recognise fill option "+str(fill_option)+\
                       "should be one of ['weight', 'content', 'pdf', 'none']")
        n_colors = ROOT.TColor.GetNumberOfColors()
        bounds = [min(fill_data)+i*(max(fill_data)-min(fill_data))/(n_colors-1)\
                                                     for i in range(n_colors)]
        fill_colors = [bisect.bisect_left(bounds, fill) for fill in fill_data]
        fill_colors = [ROOT.TColor.GetColorPalette(i) for i in fill_colors]
        return fill_colors

