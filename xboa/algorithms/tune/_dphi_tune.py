import sys
import math
import numpy
import xboa.common
import xboa.common.matplotlib_wrapper as matplotlib_wrapper


from xboa.algorithms.closed_orbit import EllipseClosedOrbitFinderIteration
from xboa.algorithms.peak_finder import WindowPeakFinder

class DPhiTuneFinder(object):
    def __init__(self, u_data = None, up_data = None):
        self.u = u_data
        self.up = up_data
        self.centre = None
        self.ellipse = None
        self.point_circles = []
        self.dphi = []
        self.tune = None
        self.tune_error = None
        self.axis1 = ""
        self.axis2 = ""

    def get_tune(self, tune_tolerance = None):
        if self.u == None or self.up == None:
            raise ValueError("Missing data set for Tune calculation")

        points = list(zip(self.u, self.up))
        try:
            self.centre, self.ellipse = xboa.common.fit_ellipse(
                                              points,
                                              1e9,
                                              verbose = False)

        except ValueError:
            sys.excepthook(*sys.exc_info())
        self.get_dphi_list()
        self.tune = numpy.mean(self.dphi)
        self.tune_error = numpy.std(self.dphi)
        return numpy.mean(self.dphi)

    def run_tracking(self, axis1, axis2, delta1, delta2, reference_hit, tracking, use_hits=None):
        """
        Set position data from tracking output

        - reference_hit: Hit on the closed orbit (for a ring).
        - axis: string, variable from Hit.get_variables() over which the tune
                will be found.
        - delta: float, displacement from the reference_hit.
        - tracking: xboa.tracking.TrackingBase, tracking object to propagate
                particles through the lattice.
        - use_hits: list of integers, only consider hits returned by tracking 
                with an index in use_hits. If set to None, consider all hits.
        """
        hit = reference_hit.deepcopy()
        self.axis1 = axis1
        self.axis2 = axis2
        hit[axis1] += delta1
        hit[axis2] += delta2
        hits_out = tracking.track_one(hit)
        if use_hits != None:
            hits_out = [hit for i, hit in enumerate(hits_out) if i in use_hits]
        
        self.u = [hit[axis1] for hit in hits_out]
        self.up = [hit[axis2] for hit in hits_out]

    def get_dphi_list(self):
        cholesky = numpy.linalg.cholesky(self.ellipse)
        cholesky_inv = numpy.linalg.inv(cholesky)
        points = zip(self.u, self.up)
        plot_x, plot_y = [], []
        self.point_circles = []
        for point in points:
            point_array = numpy.array([point[0]-self.centre[0],
                                    point[1]-self.centre[1]])
            self.point_circles.append(numpy.dot(cholesky_inv, point_array))

        old_phi = -math.atan2(self.point_circles[0][1], self.point_circles[0][0])
        index = 1
        for point in self.point_circles[1:]:
            phi = -math.atan2(point[1], point[0])
            delta = phi-old_phi
            if delta < 0.:
                delta += math.pi*2.
            self.dphi.append(delta/math.pi/2.)
            old_phi = phi
            index += 1

    def plot_phase_space_root(self):
        """
        Plot the raw phase space used in the tune calculation.

        Returns a tuple of canvas, axes histogram, graph
        """
        ps_canvas = xboa.common.make_root_canvas("dphi tune PS canvas")
        ps_hist, ps_graph = xboa.common.make_root_graph("dphi PS", self.u, self.axis1, self.up, self.axis2)
        ps_hist.SetTitle("Fitted points before Cholesky decomposition to circle")
        ps_hist.Draw()
        ps_graph.SetMarkerStyle(24)
        ps_graph.Draw("PSAME")
        ps_canvas.Update()
        return ps_canvas, ps_hist, ps_graph

    def plot_cholesky_space_root(self, circle_canvas = None, scale = 1.):
        """
        Plot the cholesky space used in the tune calculation.

        - circle_canvas: if not set to None, draw the graph using existing axes
                         on this canvas. If set to None, a canvas is generated
        - scale: scale points by a factor (for example to draw several circles
                 on the same axes by scaling each circle by a small amount)

        The tune calculation works by fitting an ellipse to the data and then
        projecting the ellipse onto a circle; and calculating the advance from
        one point to the next. This plots the ellipse after projecting onto a
        circle.

        Returns a tuple of canvas, axes histogram, graph
        """
        circle_x = [point[0]*scale for point in self.point_circles]
        circle_y = [point[1]*scale for point in self.point_circles]
        circle_hist, circle_graph = xboa.common.make_root_graph("dphi circle", circle_x, "", circle_y, "")
        circle_hist.SetTitle("Fitted points after Cholesky decomposition to circle")
        if circle_canvas == None:
            circle_canvas = xboa.common.make_root_canvas("dphi tune circle canvas")
            circle_hist.Draw()
        circle_graph.SetMarkerStyle(24)
        circle_graph.Draw("PSAME")
        circle_canvas.Update()
        return circle_canvas, circle_hist, circle_graph

    def plot_phase_space_matplotlib(self, x_label, y_label, fig_index=None):
        """
        Plot the raw phase space used in the tune calculation.
        - fig_index: index of matplot figure; set to None to create a new figure

        Returns the fig_index
        """
        fig_index = matplotlib_wrapper.make_scatter(self.u, x_label,
                                                  self.up, y_label,
                                                  fig_index=fig_index)
        return fig_index


    def plot_cholesky_space_matplotlib(self, fig_index = None, scale = 1.):
        """
        Plot the cholesky space used in the tune calculation.

        - fig_index: index of matplot figure; set to None to create a new figure
        - scale: scale points by a factor (for example to draw several circles
                 on the same axes by scaling each circle by a small amount)

        The tune calculation works by fitting an ellipse to the data and then
        projecting the ellipse onto a circle; and calculating the advance from
        one point to the next. This plots the ellipse after projecting onto a
        circle.

        Returns a tuple of canvas, axes histogram, graph
        """
        circle_x = [point[0]*scale for point in self.point_circles]
        circle_y = [point[1]*scale for point in self.point_circles]
        fig_index = matplotlib_wrapper.make_scatter(circle_x, "",
                                                  circle_y, "",
                                                  fig_index=fig_index)
        return fig_index

