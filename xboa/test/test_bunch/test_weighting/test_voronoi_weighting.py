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

import random
import unittest
import math
import datetime

import numpy
import ROOT

from xboa.hit import Hit
from xboa.bunch import Bunch
from xboa.bunch.weighting import VoronoiWeighting
from xboa.bunch.weighting import BoundingEllipse
import xboa.common as common

class VoronoiWeightingTestCase(unittest.TestCase):
    def setUp(self):
        try:
            common.config.has_scipy()
        except ImportError:
            self.skipTest("Need scipy library for voronoi weighting")
        self.diag = numpy.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],])
        self.root_batch = ROOT.gROOT.IsBatch()
        ROOT.gROOT.SetBatch(not main)

    def tearDown(self):
        ROOT.gROOT.SetBatch(self.root_batch)

    def test_apply_weights_no_bound(self):
        test_bunch = Bunch()
        for i in range(1000):
            x = random.gauss(0., 10.**0.5)
            y = random.gauss(0., 20.**0.5)
            test_hit = Hit.new_from_dict({'x':x, 'y':y})
            test_bunch.append(test_hit)
        my_weights = VoronoiWeighting(['x', 'y'],
                                      numpy.array([[20., 0.],[0., 20.]]))
        print("Plotting weights", datetime.datetime.now())
        canvas, hist = test_bunch.root_histogram('x', 'mm', 'y', 'mm')
        hist.Draw("COLZ")
        canvas.Update()
        print('Covariances ["x", "y"] before\n', test_bunch.covariance_matrix(['x', 'y']))
        print("Applying weights 1 process", datetime.datetime.now())
        my_weights.apply_weights(test_bunch, False, 1)
        print("Applying weights 2 processes", datetime.datetime.now())
        my_weights.apply_weights(test_bunch, False, 2)
        print("Applying weights 4 processes", datetime.datetime.now())
        my_weights.apply_weights(test_bunch, False, 4)
        print("Plotting tesselation", datetime.datetime.now())
        #my_weights.plot_two_d_projection(['x', 'y'], 'weight')
        my_weights.plot_two_d_projection(['x', 'y'], 'content')
        print("Plotting weights", datetime.datetime.now())
        canvas, hist = test_bunch.root_histogram('x', 'mm', 'y', 'mm')
        hist.Draw("COLZ")
        canvas.Update()
        test_bunch.root_histogram('local_weight', nx_bins=100)
        canvas = common.make_root_canvas('local_weight')
        hist = common.make_root_histogram('local_weight', test_bunch.list_get_hit_variable(['local_weight'])[0], 'local_weight', 100)
        hist.Draw()
        canvas.Update()
        canvas = common.make_root_canvas('content')
        hist = common.make_root_histogram('content', my_weights.tile_content_list, 'content', 100)
        hist.Draw()
        canvas.Update()
        print('Covariances ["x", "y"] after\n', test_bunch.covariance_matrix(['x', 'y']))

    def test_apply_weights_bound(self):
        test_bunch = Bunch()
        for i in range(1000):
            x = random.gauss(0., 10.**0.5)
            y = random.gauss(0., 20.**0.5)
            test_hit = Hit.new_from_dict({'x':x, 'y':y})
            test_bunch.append(test_hit)
        limit_ellipse = numpy.zeros([2, 2])
        for i in range(2):
            limit_ellipse[i, i] = 200.
        bound = BoundingEllipse(limit_ellipse, numpy.zeros([2]), 50)

        my_weights = VoronoiWeighting(['x', 'y'],
                                      numpy.array([[20., 0.],[0., 20.]]),
                                      voronoi_bound = bound)
        print("Plotting weights", datetime.datetime.now())
        canvas, hist = test_bunch.root_histogram('x', 'mm', 'y', 'mm')
        hist.Draw("COLZ")
        canvas.Update()
        print('Covariances ["x", "y"] before\n', test_bunch.covariance_matrix(['x', 'y']))
        print("Applying weights", datetime.datetime.now())
        my_weights.apply_weights(test_bunch, False)
        print("Plotting tesselation", datetime.datetime.now())
        #my_weights.plot_two_d_projection(['x', 'y'], 'weight')
        my_weights.plot_two_d_projection(['x', 'y'], 'weight')
        my_weights.plot_two_d_projection(['x', 'y'], 'content')
        print("Plotting weights", datetime.datetime.now())
        canvas, hist = test_bunch.root_histogram('x', 'mm', 'y', 'mm')
        hist.Draw("COLZ")
        canvas.Update()
        test_bunch.root_histogram('local_weight', nx_bins=100)
        canvas = common.make_root_canvas('local_weight')
        hist = common.make_root_histogram('local_weight', test_bunch.list_get_hit_variable(['local_weight'])[0], 'local_weight', 100)
        hist.Draw()
        canvas.Update()
        canvas = common.make_root_canvas('content')
        hist = common.make_root_histogram('content', my_weights.tile_content_list, 'content', 100)
        hist.Draw()
        canvas.Update()
        print('Covariances ["x", "y"] after\n', test_bunch.covariance_matrix(['x', 'y']))

    def plot_gauss(self, x_list, gauss_list):
        canvas = common.make_root_canvas("gauss")
        canvas.Draw()
        canvas.SetLogy()
        hist, graph = common.make_root_graph("gauss", x_list, "position", gauss_list, "Gauss")
        hist.Draw()
        graph.Draw('l')
        fit_function = ROOT.TF1("fit", "gaus")
        graph.Fit(fit_function)
        canvas.Update()
        return fit_function        

    def test_get_pdf_1d(self):
        my_weights = VoronoiWeighting(['x'],
                                      numpy.array([[1.]]),
                                      numpy.array([0.]))
        x_list, gauss_list = [], []
        for i in range(-500, 501):
            point = numpy.array([[1.]])
            point *= i/100.
            x_list.append(i/100.)
            gauss_list.append(my_weights.get_pdf(point))
        fit_function = self.plot_gauss(x_list, gauss_list)

    def test_get_pdf_4d(self):
        for i in range(4):
            self.diag[i, i] = (i+1.)**2.
        my_weights = VoronoiWeighting(['x', 'y', 'px', 'py'],
                                      self.diag,
                                      numpy.array([1., 2., 3., 4.]))
        for i in range(4):
            x_list, gauss_list = [], []
            for j in range(-500, 501):
                point = numpy.array([0., 0., 0., 0.])
                point[i] = (i+1)*j/100.+(i+1)
                x_list.append(point[i])
                gauss_list.append(my_weights.get_pdf(point))
            fit_function = self.plot_gauss(x_list, gauss_list)
            self.assertAlmostEqual(fit_function.GetParameter(1), i+1, 3)
            self.assertAlmostEqual(fit_function.GetParameter(2), i+1, 3)
        x_list, gauss_list = [], []
        for j in range(-500, 501):
            point = numpy.array([1., 2., 3., 4.])
            point *= j/100.
            x_list.append(j/100.)
            gauss_list.append(my_weights.get_pdf(point))
        fit_function = self.plot_gauss(x_list, gauss_list)
        self.assertAlmostEqual(fit_function.GetParameter(1), 1, 3)
        self.assertAlmostEqual(fit_function.GetParameter(2), 0.5, 3) # why 0.5?

    def test_content_circle(self):
        test_bunch = Bunch()
        n_events = 361
        for theta in range(0, n_events-1):
            x = 2.*math.sin(math.radians(theta))
            y = 2.*math.cos(math.radians(theta))
            test_hit = Hit.new_from_dict({'x':x, 'y':y})
            test_bunch.append(test_hit)
        test_hit = Hit.new_from_dict({'x':0., 'y':0.})
        test_bunch.append(test_hit)
        limit_bunch = Bunch.new_hit_shell(3,
                                          numpy.array([[9.5, 0.],[0., 9.5]]),
                                          ['x', 'y'],
                                          '')
        my_weights = VoronoiWeighting(['x', 'y'],
                                      numpy.array([[2., 0.],[0., 1.]]))
        my_weights.apply_weights(test_bunch, False)
        my_weights.plot_two_d_projection(['x', 'y'])
        self.assertEqual(len(my_weights.tile_content_list), n_events)
        non_zero_content = [cont for cont in my_weights.tile_content_list \
                                                                if cont > 1e-6] 
        self.assertEqual(len(non_zero_content), 1)
        self.assertAlmostEqual(non_zero_content[0], math.pi, 3)

    def _test_content_hypersphere(self):
        # disabled because it is slow
        print("Test content hypersphere")
        for i in range(5):
            numpy.seterr(all='ignore')
            test_bunch = Bunch()
            content_predicted = numpy.linalg.det(self.diag)*math.pi**2/2.
            test_bunch = Bunch.new_hit_shell(7,
                                             4.*self.diag,
                                             ['x', 'y', 'px', 'py'],
                                             '')
            test_bunch.append(Hit.new_from_dict({'x':0., 'y':0., 'px':0., 'py':0.}))
            for hit in test_bunch:
                hit['x'] += 1.*i
                hit['px'] += 2.*i
                hit['y'] += 3.*i
                hit['py'] += 4.*i
            my_weights = VoronoiWeighting(['x', 'y', 'px', 'py'],
                                          numpy.array([[2., 0., 0., 0.],
                                                       [0., 1., 0., 0.],
                                                       [0., 0., 1., 0.],
                                                       [0., 0., 0., 1.],]))
            my_weights.apply_weights(test_bunch, False)
            my_weights.plot_two_d_projection(['x', 'y'])
            my_weights.plot_two_d_projection(['px', 'py'])
            #self.assertEqual(len(my_weights.tile_content_list), len(test_bunch)+1)
            content_actual = sum(my_weights.tile_content_list)
            print("Content", content_actual, "Predicted", content_predicted)
            self.assertAlmostEqual(content_actual, content_predicted, 0)
        input()

    def test_content_hypercube(self):
        test_bunch = Bunch()
        for x in range(-2, 3):
            for y in range(-2, 3):
                for px in range(-2, 3):
                    for py in range(-2, 3):
                        test_hit = Hit.new_from_dict({'x':x, 'y':y, 'px':px, 'py':py})
                        test_bunch.append(test_hit)
        limit_bunch = Bunch.new_hit_shell(3,
                                          numpy.array([[9.5, 0.],[0., 9.5]]),
                                          ['x', 'y'],
                                          '')
        my_weights = VoronoiWeighting(['x', 'y', 'px', 'py'],
                                      self.diag)
        my_weights.apply_weights(test_bunch, False)
        my_weights.plot_two_d_projection(['x', 'y'])
        self.assertEqual(len(my_weights.tile_content_list), len(test_bunch))
        self.assertAlmostEqual(sum(my_weights.tile_content_list), 81., 3)
    
    def test_content_square(self):
        test_bunch = Bunch()
        for x in range(-2, 3):
            for y in range(-2, 3):
                test_hit = Hit.new_from_dict({'x':x, 'y':y})
                test_bunch.append(test_hit)
        limit_bunch = Bunch.new_hit_shell(3,
                                          numpy.array([[9.5, 0.],[0., 9.5]]),
                                          ['x', 'y'],
                                          '')
        my_weights = VoronoiWeighting(['x', 'y'],
                                      numpy.array([[2., 0.],[0., 1.]]))
        my_weights.apply_weights(test_bunch, False)
        my_weights.plot_two_d_projection(['x', 'y'])
        self.assertEqual(len(my_weights.tile_content_list), len(test_bunch))
        self.assertAlmostEqual(sum(my_weights.tile_content_list), 9., 3)

main = False
if __name__ == "__main__":
    main = True
    unittest.main()

