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

"""Tests for _closed_orbit_finder"""

import unittest

import numpy.linalg
import ROOT

import xboa.common as common
from xboa.hit import Hit
from xboa.tracking import MatrixTracking
from xboa.algorithms.closed_orbit import EllipseClosedOrbitFinder

class TestEllipseClosedOrbitFinder(unittest.TestCase):
    """Tests for the EllipseClosedOrbitFinder"""
    def setUp(self):
        """Setup the EllipseClosedOrbitFinder"""
        self.num_turns = 5
        # x is conventional ellipse
        # y is phase advance = pi
        # t is phase advance = complex
        data = [[1.0,  0.5,  0.0,  0.0, 0.0,  0.0],
                [-0.5, 0.75, 0.0,  0.0, 0.0,  0.0],
                [0.0,  0.0,  0.0, -1.0, 0.0,  0.0],
                [0.0,  0.0,  1.0,  0.0, 0.0,  0.0],
                [0.0,  0.0,  0.0,  0.0, 2.0,  2.0],
                [0.0,  0.0,  0.0,  0.0, 2.0,  2.5]]
        matrix = numpy.matrix(data)
        self.matrix_list = [matrix**(i+1) for i in range(self.num_turns)]           
        offset = numpy.matrix([10., 7., 0., 0., 0., 1000.])
        self.offset_list = [offset]*self.num_turns
        self.offset_in = numpy.matrix([10., 7., 0., 0., 0., 1000.])
        self.tracking = MatrixTracking(self.matrix_list,
                                       self.offset_list,
                                       self.offset_in)
        self.co = Hit.new_from_dict({'x':10., 'px':7., 'energy':1000.,
                       'pid':2212, 'mass':common.pdg_pid_to_mass[2212]})
        if abs(numpy.linalg.det(matrix) - 1.0) > 1e-9:
            raise ValueError("TM determinant should be 1, got "+\
                              str(numpy.linalg.det(matrix)))

    def test_init(self):
        """test EllipseClosedOrbitFinder.__init__"""
        co_finder = EllipseClosedOrbitFinder(self.tracking,
                                             self.co)

    def test_check_co_x(self):
        """test EllipseClosedOrbitFinder.check_co - x"""
        n_turns = 10
        co_finder = EllipseClosedOrbitFinder(self.tracking, self.co)
        test_values = {'x':11., 'px':8.}
        co_check = co_finder.check_closed_orbit(test_values, n_turns)
        self.assertEqual(co_check.keys, sorted(test_values.keys()))
        # check we have reasonable convergence properties
        for i, key in enumerate(co_check.keys):
            self.assertLess(abs(self.co[key]-co_check.centre[i]),
                            abs(self.co[key]-test_values[key])/2. )
        # check noise is of correct length
        n_noise = float(len(co_check.noise))
        self.assertGreater(n_noise, n_turns-1)
        # noise should be "clean" if we are fitting the ellipse properly
        mean_noise = sum(co_check.noise)/n_noise
        self.assertAlmostEqual(co_check.get_mean_noise(), mean_noise)
        noise_squ = [noise*noise for noise in co_check.noise]
        sigma_noise = (sum(noise_squ)/n_noise-mean_noise**2)**0.5
        self.assertAlmostEqual(co_check.get_sigma_noise(), sigma_noise)


    def test_check_co_y(self):
        """test EllipseClosedOrbitFinder.check_co - y"""
        n_turns = 10
        co_finder = EllipseClosedOrbitFinder(self.tracking, self.co)
        test_values = {'y':1., 'py':1.}
        co_check = co_finder.check_closed_orbit(test_values, n_turns)
        # check we have reasonable convergence properties
        for i, key in enumerate(co_check.keys):
            self.assertLess(abs(self.co[key]-co_check.centre[i]),
                            abs(self.co[key]-test_values[key])/2. )
        # check noise is of correct length
        n_noise = float(len(co_check.noise))
        self.assertGreater(n_noise, n_turns-1)
        # noise should be "clean" if we are fitting the ellipse properly
        self.assertLess(co_check.get_sigma_noise()*2.,
                        co_check.get_mean_noise())

    def test_check_co_t(self):
        """test EllipseClosedOrbitFinder.check_co - t"""
        n_turns = 5
        co_finder = EllipseClosedOrbitFinder(self.tracking, self.co)
        test_values = {'t':0.1, 'energy':1000.1}
        co_check = co_finder.check_closed_orbit(test_values, n_turns)
        # Should be divergent
        # co_check.plot_ellipse('t', 'energy', 'ns', 'MeV')
        # note this makes a more-or-less straight line in t-energy so tends to
        # produce singular ellipses
        self.assertGreater(co_check.get_sigma_noise()*2.,
                           co_check.get_mean_noise())

    def test_check_co_xy(self):
        """test EllipseClosedOrbitFinder.check_co - xy
        """
        n_turns = 10
        co_finder = EllipseClosedOrbitFinder(self.tracking, self.co)
        test_values = {'x':11., 'px':8., 'y':1., 'py':1.}
        co_check = co_finder.check_closed_orbit(test_values, n_turns)
        # check that we have converged in 2D
        for i, key in enumerate(co_check.keys):
            self.assertLess(abs(self.co[key]-co_check.centre[i]),
                            abs(self.co[key]-test_values[key])/2. )
        self.assertLess(co_check.get_sigma_noise()*2.,
                        co_check.get_mean_noise())

    def test_check_co_json_repr(self):
        """
        test EllipseClosedOrbitFinderIteration.json_repr
        """
        n_turns = 10
        co_finder = EllipseClosedOrbitFinder(self.tracking, self.co)
        test_values = {'x':11., 'px':8., 'y':1., 'py':1.}
        co_check = co_finder.check_closed_orbit(test_values, n_turns)
        self.assertEqual(co_check.json_repr()["points"], co_check.points)
        self.assertEqual(co_check.json_repr()["keys"], co_check.keys)
        self.assertEqual(co_check.json_repr()["eps_max"], co_check.eps_max)

    def test_check_co_plot_ellipse(self):
        """
        test EllipseClosedOrbitFinderIteration.json_repr
        """
        n_turns = 20
        co_finder = EllipseClosedOrbitFinder(self.tracking, self.co)
        test_values = {'x':11., 'px':8., 'y':1., 'py':1.}
        co_check = co_finder.check_closed_orbit(test_values, n_turns)
        canvas, hist, ellipse, graph = \
                  co_check.plot_ellipse("x", "px", "mm", "MeV/c", 4, "test_fit")
        # mock-up that we failed to find an ellipse; check that doesn't throw
        co_check.centre = None
        co_check.ellipse = None
        co_check.noise = None
        canvas, hist, ellipse, graph = \
                  co_check.plot_ellipse("x", "px", "mm", "MeV/c", 4, "no_ell")

    def test_scan_steps(self):
        """
        test EllipseClosedOrbitFinder.scan_generator generates correct start x
        """
        co_finder = EllipseClosedOrbitFinder(self.tracking, self.co)
        scan_start = {'x':-1., 'y':-2., 'z':-3.}
        scan_end = {'x':4.1, 'y':5., 'z':6.433}
        scan_step = {'x':1., 'y':2., 'z':3.}
        scan_gen = co_finder.scan_generator(scan_start, scan_end, scan_step)
        start = [scan_start[key] for key in ['x', 'y', 'z']]
        end = [scan_end[key] for key in ['x', 'y', 'z']]
        last_step = scan_gen.next().points[0]
        self.assertEqual(last_step, start)
        for item in scan_gen:
            step = item.points[0]
            self.assertGreater(step, last_step)
            self.assertLess(step, end)
            last_step = step
        scan_gen = co_finder.scan_generator(scan_start, scan_end, scan_step)
        scan_list = [x for x in scan_gen]
        self.assertEqual(len(scan_list), 6*4*4)

    def test_scan_data(self):
        """
        check that the scan data is calculated correctly
        """
        co_finder = EllipseClosedOrbitFinder(self.tracking, self.co)
        scan_start = {'x':9., 'px':6.}
        scan_end = {'x':11.1, 'px':8.1}
        scan_step = {'x':1., 'px':1.}
        scan_gen = co_finder.scan_generator(scan_start, scan_end, scan_step)
        co_iter = scan_gen.next()
        self.assertEqual(len(co_iter.points), 6)
        co_iter = scan_gen.next()
        co_iter = scan_gen.next()
        co_iter = scan_gen.next()
        # this should be on the closed orbit
        co_iter = scan_gen.next()
        for point in co_iter.points:
            for i, x in enumerate(point):
                self.assertAlmostEqual(point[i], [7., 10.][i])

    def test_co_finder(self):
        """
        Check that the co finder converges
        """
        test_hit = self.co.deepcopy()
        test_hit["x"] += 1.
        test_hit["y"] += 1.
        co_finder = EllipseClosedOrbitFinder(self.tracking, test_hit)
        for test_keys in [["x", "px"], ["x", "px", "y", "py"]]:
            co_generator = co_finder.find_closed_orbit_generator(test_keys, 10)
            try:
                canv = None
                for my_co in co_generator:
                   canv, i, j, k =  my_co.plot_ellipse('x', 'px', 'mm', 'MeV/c', canvas=canv)
            except ValueError:
                pass
            test_co = [self.co[key] for key in my_co.keys]
            for i, item in enumerate(my_co.centre):
                self.assertAlmostEqual(my_co.centre[i], test_co[i], 3)

if __name__ == "__main__":
    unittest.main()

