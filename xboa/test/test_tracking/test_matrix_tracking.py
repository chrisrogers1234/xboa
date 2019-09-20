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
tests of tracking_matrix
"""

import unittest
import numpy

from xboa.hit import Hit
import xboa.common as Common
from xboa.tracking import MatrixTracking

class TestMatrixTracking(unittest.TestCase):
    """
    Test MatrixTracking
    """
    def setUp(self):
        """
        Generate test matrices
        """
        # focussing in x, drift in y, something weird in t
        self.num_turns = 50
        data = [[0.75**0.5, 0.5,        0.0, 0.0, 0.0, 0.0],
                [-0.5,      0.75**0.5, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 1.,  0.5, 0.0, 0.0],
                [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 1./0.9, 0.5],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.9]]
        matrix = numpy.matrix(data)
        self.matrix_list = [matrix**i for i in range(self.num_turns)]           
        offset = numpy.matrix([0., 0., -3., 0., -5., 1000.-6.])
        self.offset_list = [offset*i for i in range(self.num_turns)]
        self.offset_in = numpy.matrix([0., 0., 0., 0., 0., 1000.])

    def test_init(self):
        """
        Test MatrixTracking.__init__
        """
        try: # wrong lengths
            tracking = MatrixTracking(self.matrix_list, self.offset_list[0:4],
                                      self.offset_in)
            self.assertTrue(False, msg="Should have raised")
        except IndexError:
            pass
        try: # offset wrong type
            tracking = MatrixTracking(self.matrix_list,
                                      [1]*len(self.matrix_list), self.offset_in)
            self.assertTrue(False, msg="Should have raised")
        except TypeError:
            pass
        try: # offset wrong shape
            tracking = MatrixTracking(self.matrix_list, self.matrix_list,
                                      self.offset_in)
            self.assertTrue(False, msg="Should have raised")
        except TypeError:
            pass
        try: # matrix wrong type
            tracking = MatrixTracking([1]*len(self.matrix_list),
                                      self.offset_list, self.offset_in)
            self.assertTrue(False, msg="Should have raised")
        except TypeError:
            pass
        try: # matrix wrong shape
            tracking = MatrixTracking(self.offset_list, self.offset_list,
                                      self.offset_in)
            self.assertTrue(False, msg="Should have raised")
        except TypeError:
            pass
        try: # offset_in wrong type
            tracking = MatrixTracking(self.matrix_list,
                                      self.offset_list, 1)
            self.assertTrue(False, msg="Should have raised")
        except TypeError:
            pass
        try: # offset_in wrong shape
            tracking = MatrixTracking(self.offset_list, self.offset_list,
                                      self.matrix_list[0])
            self.assertTrue(False, msg="Should have raised")
        except TypeError:
            pass
        tracking = MatrixTracking(self.matrix_list, self.offset_list,
                                  self.offset_in)
        self.assertEqual(tracking.last, [])

    def test_track_one(self):
        """
        Test MatrixTracking.track_one
        """
        tracking = MatrixTracking(self.matrix_list, self.offset_list,
                                  self.offset_in)
        hit_in = Hit.new_from_dict({"mass":Common.pdg_pid_to_mass[2212],
                                    "charge":1., "pid":2212, "pz":1.,
                                    "x":1., "py":1., "energy": 1001.},
                                    "pz")
        hit_list = tracking.track_one(hit_in)
        self.assertEqual(len(hit_list), self.num_turns+1)
        self.assertEqual(hit_list[0], hit_in)
        self.assertLess(abs(hit_list[-1]['x']), 10.) # should be contained
        self.assertLess(abs(hit_list[-1]['px']), 10.) # should be contained
        self.assertAlmostEqual(abs(hit_list[-1]['py']), hit_in['py']) # drift
        self.assertEqual(tracking.last, [hit_list])

    def test_track_many(self):
        """
        Test MatrixTracking.track_many
        """
        tracking = MatrixTracking(self.matrix_list, self.offset_list,
                                  self.offset_in)
        hit_in = Hit.new_from_dict({"mass":Common.pdg_pid_to_mass[2212],
                                    "charge":1., "pid":2212, "pz":1.,
                                    "x":1., "py":1., "energy": 1001.},
                                    "pz")
        hit_in_2 = Hit.new_from_dict({"mass":Common.pdg_pid_to_mass[2212],
                                    "charge":1., "pid":2212, "pz":1.,
                                    "x":1., "py":1., "energy": 1002.},
                                    "pz")
        hit_list_of_lists = tracking.track_many([hit_in]*3+[hit_in_2])
        for hit_list in hit_list_of_lists[1:-1]:
            self.assertEqual(hit_list, hit_list_of_lists[0])
        self.assertNotEqual(hit_list_of_lists[-1], hit_list_of_lists[0])
        self.assertEqual(tracking.last, hit_list_of_lists)


if __name__ == "__main__":
    unittest.main()



