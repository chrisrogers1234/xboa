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

import unittest

import numpy

from xboa.bunch.weighting import BoundingEllipse

class BoundingEllipseTestCase(unittest.TestCase):
    def test_cut_on_bound_2d(self):
        point_list = []
        for x in range(-50, 51):
            for y in range(-50, 51):
                point_list.append([x/10., y/10.])
        points_in = numpy.array(point_list)
        limit_ellipse = numpy.array([[1.99, 0.0], [0.0, 2.99]])
        limit_mean = numpy.array([0.5, 0.8])
        bound = BoundingEllipse(limit_ellipse, limit_mean, 3)
        points_out, not_cut = bound.cut_on_bound(points_in)
        for point in points_out:
            self.assertLess(abs(point[0]-limit_mean[0]), 2.0)
            self.assertLess(abs(point[1]-limit_mean[1]), 3.0)

    def test_cut_on_bound_4d(self):
        point_list = []
        for u in range(-5, 6):
            for v in range(-5, 6):
                for w in range(-5, 6):
                    for x in range(-5, 6):
                        point_list.append([u*1., v*1., w*1., x*1.])
        points_in = numpy.array(point_list)
        limit_ellipse = numpy.zeros([4, 4])
        for i in range(4):
            limit_ellipse[i, i] = (i+0.999)**2
        limit_mean = numpy.array([1.0, 2.0, 3.0, 4.0])
        bound = BoundingEllipse(limit_ellipse, limit_mean, 3)
        points_out, not_cut = bound.cut_on_bound(points_in)
        for point in points_out:
            self.assertLess(abs(point[0]-limit_mean[0]), 1.0)
            self.assertLess(abs(point[1]-limit_mean[1]), 2.0)
            self.assertLess(abs(point[2]-limit_mean[2]), 3.0)
            self.assertLess(abs(point[3]-limit_mean[3]), 4.0)

    def test_bounding_points(self):
        limit_ellipse = numpy.zeros([4, 4])
        for i in range(4):
            limit_ellipse[i, i] = (i+1.0)**2
        limit_mean = numpy.array([1.0, 2.0, 3.0, 4.0])
        bound = BoundingEllipse(limit_ellipse, limit_mean, 3)
        bounding_points = bound.bounding_points
        for i in range(4):
            limit_ellipse[i, i] = (i+0.999)**2
        bound_inside = BoundingEllipse(limit_ellipse, limit_mean, 3)
        no_points, not_cut = bound_inside.cut_on_bound(bounding_points)
        self.assertEqual(numpy.shape(no_points), (0, 4))
        for i in range(4):
            limit_ellipse[i, i] = (i+1.001)**2
        bound_outside = BoundingEllipse(limit_ellipse, limit_mean, 3)
        bounding_points = bound.bounding_points
        self.assertEqual(numpy.shape(bounding_points), (80, 4))
        all_points, not_cut = bound_outside.cut_on_bound(bounding_points)
        self.assertEqual(numpy.shape(all_points), numpy.shape(bounding_points))

if __name__ == "__main__":
    unittest.main()

