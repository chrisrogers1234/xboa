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
Closed orbit finder
"""

import math
import json
import copy
try:
    import numpy
except ImportError:
    pass
import xboa.common as common
import xboa.common.matplotlib_wrapper as matplotlib_wrapper
import xboa.common.config as config

class EllipseClosedOrbitFinder(object):
    """
    Find the closed orbit given an ellipse
    """
    def __init__(self, tracking, seed_hit, eps_max = 1e6, use_seed = False):
        """
        Initialise the closed orbit finder
        - tracking: object of type TrackingBase used for tracking particles.
              tracking should return a list of hits all of which sit at the cell
              end
        - seed_hit: hit object used as a seed for finding the closed orbit. For
              tracking, takes e.g. pid from this variable. Uses the dynamical
              variables as seeds for closed orbit finding.
        - eps_max: ignore particles with amplitude greater than eps_max.
        - use_seed: set to True to use the seed as the first point in the 
              ellipse when finding ellipses

        Requires numpy
        """
        config.has_numpy()
        self.tracking = tracking
        self.seed = seed_hit
        self.eps_max = eps_max
        self.use_seed = use_seed

    def scan_generator(self, step_start_dict, step_end_dict, step_size_dict):
        """
        Make a generator to scan over the variables, looking for closed orbits.
        - step_start_dict dict defining the start position for the scan
        - step_end_dict dict defining the end position for the variable scan
        - step_size_dict dict of step sizes for the variable scan
        Each dictionary should have the same set of keys. The keys should be
        hit set_variable keys.

        Returns an iterable of EllipseClosedOrbitFinderIterations, one iteration
        for each point in the scan; e.g. call next() against the return value to
        get the next element in the list, or put it in a loop like
            my_scan = [x for x in yield_scan(start, end, step)]
        """
        next_hit = self.seed.deepcopy()
        step = copy.deepcopy(step_start_dict)
        keys = sorted(step.keys())
        while True:
            for key in keys:
                if step[key] >= step_end_dict[key]:
                    raise StopIteration("Run out of steps at "+json.dumps(step))
                next_hit[key] = step[key]
            hit_list = self.tracking.track_one(next_hit)
            x_list = [[hit[key] for key in keys] for hit in hit_list]
            yield EllipseClosedOrbitFinderIteration(keys,
                                                    x_list,
                                                    self.eps_max)
            i = len(keys)-1
            key = keys[i]
            step[key] += step_size_dict[key]
            while step[key] > step_end_dict[key] and i > 0:
                step[key] = step_start_dict[key]
                i -= 1
                key = keys[i]
                step[key] += step_size_dict[key]

    def find_closed_orbit_generator(self, closed_orbit_variable_list,
                                    number_of_points, max_iterations=100):
        """
        Make a generator that finds the closed orbit
        - closed orbit variable_list: list of string variable names over which
          the finder will run to find the closed orbit
        - number_of_points; require a certain number of points for the ellipse
              fit. If a call to tracking does not generate the required number
              of points, take the last output from tracking and throw it back
              through. If this does not return any new hits (i.e. the particle
              has fallen out of the accelerator acceptance) then raise a Runtime
              Error
        - max_iterations: maximum number of iterations to make. If set to None,
              keep iterating until we find a closed orbit. This can go forever.

        Returns a generator object that will continue iterating until the
        tracking noise is large. If the closed orbit finder fails to fit an
        ellipse (for example because the test particle is going out of bounds or
        is singular) then find_closed_orbit raises a RuntimeError.

        The caller is invited to break out of the loop early if, for example,
        she does not require convergence to the precision of the tracking.

        Note that this can make a warning from numpy like
           "Warning: invalid value encountered in double_scalars"
        """
        keys = closed_orbit_variable_list
        next_hit = self.seed.deepcopy()
        noise_mean = None
        iteration = 0
        while iteration < max_iterations or max_iterations == None:
            iteration += 1
            x_list = self._get_points(keys, next_hit, number_of_points)
            try:
                my_co = EllipseClosedOrbitFinderIteration(keys, x_list,
                                                          self.eps_max, True)
            except  (numpy.linalg.linalg.LinAlgError, ValueError):
                if len(x_list) > number_of_points:
                    raise StopIteration("Closed orbit has reached numerical "+\
                                        "precision limit. Nice!")
                else:
                    raise ValueError("Failed to find ellipse determinant.")

            yield my_co
            if my_co.get_mean_noise() < my_co.get_sigma_noise():
                raise StopIteration("Closed orbit finder has reached "+\
                                    "convergence limit. Tracking noise is "+\
                                    "greater than ellipse size.")
            for i, var in enumerate(keys):
                next_hit[var] = my_co.centre[i]
        raise StopIteration("Closed orbit finder has finished iterating without converging.")
 

    def check_closed_orbit(self, test_variable_dict, number_of_points):
        """
        Check whether test_variables fall on the closed orbit
        - test_variable_dict: dictionary mapping variable names to variable
              values. Typically variables should be dynamical variables of the
              hit. Other variables will be filled from seed.
        - number_of_points; require a certain number of points for the ellipse
              fit. If a call to tracking does not generate the required number
              of points, take the last output from tracking and throw it back
              through. If this does not return any new hits (i.e. the particle
              has fallen out of the accelerator acceptance) then raise a Runtime
              Error

        Return is a EllipseClosedOrbitFinderIteration
        """
        next_hit = self.seed.deepcopy()
        keys = sorted(test_variable_dict.keys())
        for var in keys:
            next_hit[var] = test_variable_dict[var]
        x_list = self._get_points(keys, next_hit, number_of_points)
        co_check = EllipseClosedOrbitFinderIteration(keys, x_list, self.eps_max, False)
        try:
            co_check.calculate_ellipse()
        except numpy.linalg.linalg.LinAlgError:
            pass
        except ValueError:
            pass
        return co_check

    def _get_points(self, keys, next_hit, number_of_points):
        hit_list = []
        if self.use_seed:
            hit_list.append(next_hit)
        while len(hit_list) < number_of_points:
            hit_list += self.tracking.track_one(next_hit)[1:]
            if hit_list[-1] == next_hit:
                raise RuntimeError("Tracking failed to generate an ellipse")
            next_hit = hit_list[-1]
        x_list = [[hit[var] for var in keys] for hit in hit_list]
        return x_list

class EllipseClosedOrbitFinderIteration(object):
    """
    Data following a single pass of the closed orbit finder

    Handle a single iteration of the CO finder. Few utility functions to find
    the ellipse, look for convergence and return outputs to the user.
    """
    def __init__(self, keys, points, eps_max, calculate_ellipse = False):
        """
        Initialisation
        - keys keys that tell us what the variables mean
        - points list of points. Each point is a list that represents a vector
          in the space defined by keys
        - eps_max when fitting the ellipse, ignore points with amplitude greater
          than eps_max
        - calculate_ellipse set to true to calculate the ellipse. Otherwise, the
          ellipse can be calculated by a call to calculate_ellipse()

        Requires numpy
        """
        config.has_numpy()
        self.keys = keys
        self.points = points
        self.eps_max = eps_max
        self.centre = None
        self.ellipse = None
        self.noise = None
        if calculate_ellipse == True:
            self.calculate_ellipse()

    def calculate_ellipse(self):
        """
        Calculate the beam ellipse and noise list based on points

        Raises a ValueError if noise cannot be calculated.
        """
        self.centre, self.ellipse = common.fit_ellipse(self.points,
                                                      self.eps_max,
                                                      verbose = False)
        noise_list = []
        ellipse = copy.deepcopy(self.ellipse)
        ellipse /= numpy.linalg.det(ellipse)**(1./len(self.centre))
        ellipse_inv = numpy.linalg.inv(ellipse)
        for x_vec in self.points:
            x_numpy = numpy.matrix(x_vec)-self.centre
            noise = x_numpy * ellipse_inv * x_numpy.transpose()
            noise_list.append(float(noise[0]))
        for value in noise_list:
            if math.isnan(value) or math.isinf(value):
                raise ValueError("Failed to calculate noise; "+\
                                 "ellipse may not be well-conditioned")
        self.noise = noise_list

    def get_mean_noise(self):
        """
        Return the mean of the noise list.

        If noise is None, will attempt to calculate noise by calling
        calculate_ellipse. Raises a ValueError if noise cannot be calculated.
        """
        if self.noise == None:
            self.calculate_ellipse()
        if len(self.noise) == 0:
            raise ValueError("Failed to calculate noise - ellipse singular?")
        n_noise = float(len(self.noise))
        mean_noise = sum(self.noise)/n_noise
        return mean_noise


    def get_sigma_noise(self):
        """
        Return the standard deviation of the noise list

        If noise is None, will attempt to calculate noise by calling
        calculate_ellipse. Raises a ValueError if noise cannot be calculated.
        """
        if self.noise == None:
            self.calculate_ellipse()
        if len(self.noise) == 0:
            raise ValueError("Failed to calculate noise - ellipse singular?")
        mean_noise = self.get_mean_noise()
        noise_squ = [noise*noise for noise in self.noise]
        var_noise = sum(noise_squ)/len(self.noise)-mean_noise**2
        if var_noise <= 0.:
            return 0.
        return var_noise**0.5

    def plot_ellipse_root(self, x_axis_string, y_axis_string,
                     x_axis_units, y_axis_units,
                     marker_style=4,
                     title_string='fit', canvas=None):
        """
        Plot the beam ellipse for a set of points
        - x_axis_string: string name of the variable to go on the x_axis
        - y_axis_string: string name of the variable to go on the y_axis
        - x_axis_units: string units on the x axis
        - y_axis_units: string units on the y axis
        - title_string: title of the histogram

        Return value is a tuple of (canvas, histogram, ellipse, graph) where
        canvas is an object of type ROOT.TCanvas, histogram is an object of type
        ROOT.TH2D, ellipse is an object of type ROOT.TF2 and graph is an object
        of type ROOT.TGraph
        """
        config.has_root()
        x_var = self.keys.index(x_axis_string)
        x_list = [x[x_var]*common.units[x_axis_units] for x in self.points]
        y_var = self.keys.index(y_axis_string)
        y_list = [x[y_var]*common.units[y_axis_units] for x in self.points]
        if x_axis_units != '':
            x_axis_string += ' ['+x_axis_units+']'
        if y_axis_units != '':
            y_axis_string += ' ['+y_axis_units+']'
        hist, graph = common.make_root_graph(title_string,
                                x_list, x_axis_string, y_list, y_axis_string)
        if canvas == None:
            canvas = common.make_root_canvas(title_string)
            hist.Draw()
        canvas.cd()
        x_min = hist.GetXaxis().GetXmin()
        x_max = hist.GetXaxis().GetXmax()
        y_min = hist.GetYaxis().GetXmin()
        y_max = hist.GetYaxis().GetXmax()
        graph.SetMarkerStyle(marker_style)
        graph.Draw('p')
        ellipse = None
        if type(self.centre) != type(None):
            ell_centre = [self.centre[x_var], self.centre[y_var]]
            ell_matrix = [
                [self.ellipse[x_var, x_var], self.ellipse[x_var, y_var]],
                [self.ellipse[x_var, y_var], self.ellipse[y_var, y_var]]
            ]
            ell_matrix = numpy.array(ell_matrix)
            contours = [self.get_mean_noise()]
            ellipse = common.make_root_ellipse_function(ell_centre, ell_matrix,
                          [2.], x_min, x_max, y_min, y_max)
            ellipse.Draw("SAME")
        else:
            ellipse = common.make_root_ellipse_function(
                                                     [0., 0.],
                                                     [[1, 0], [0., 1.]],
                                                     [2.],
                                                     x_min, x_max, y_min, y_max)
        canvas.Update()
        return canvas, hist, ellipse, graph


    def plot_ellipse_matplotlib(self, x_axis_string, y_axis_string,
                                   x_axis_units="", y_axis_units=""):
        """
        Plot the beam ellipse for a set of points
        - x_axis_string: string name of the variable to go on the x_axis
        - y_axis_string: string name of the variable to go on the y_axis
        - x_axis_units: string units on the x axis; leave blank for no units
        - y_axis_units: string units on the y axis; leave blank for no units

        Return value is a tuple of (canvas, histogram, ellipse, graph) where
        canvas is an object of type ROOT.TCanvas, histogram is an object of type
        ROOT.TH2D, ellipse is an object of type ROOT.TF2 and graph is an object
        of type ROOT.TGraph
        """
        config.has_matplotlib()
        x_var = self.keys.index(x_axis_string)
        x_list = [x[x_var]*common.units[x_axis_units] for x in self.points]
        y_var = self.keys.index(y_axis_string)
        y_list = [x[y_var]*common.units[y_axis_units] for x in self.points]
        if x_axis_units != '':
            x_axis_string += ' ['+x_axis_units+']'
        if y_axis_units != '':
            y_axis_string += ' ['+y_axis_units+']'
        fig_index = matplotlib_wrapper.make_scatter(x_list, x_axis_string, 
                                                    y_list, y_axis_string)
        """
        if type(self.centre) != type(None):
            ell_centre = [self.centre[x_var], self.centre[y_var]]
            ell_matrix = [
                [self.ellipse[x_var, x_var], self.ellipse[x_var, y_var]],
                [self.ellipse[x_var, y_var], self.ellipse[y_var, y_var]]
            ]
            x_list, y_list = [None]*361, [None]*361
            for i in range(361):
                theta = math.radians(i)
                x_list[i] = ell_centre[0]+ell_matrix[0][0]**0.5*math.cos(theta)
                y_list[i] = ell_centre[1]+ell_matrix[1][1]**0.5*math.sin(theta)
            matplotlib_wrapper.make_matplot_graph(x_list, x_axis_string,
                                                  y_list, y_axis_string,
                                                  sort=False,
                                                  fig_index=fig_index)
        """
        return fig_index


    def json_repr(self):
        """
        Represent the iteration as a json object
        - points: list of float points in the iteration
        - keys: list of keys that defines the points
        - eps_max: maximum error on the ellipse fit

        (To get the noise, etc call __init__ against this data)
        """
        return {
            "points":self.points,
            "keys":self.keys,
            "eps_max":self.eps_max
        }
