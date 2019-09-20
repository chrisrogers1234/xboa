import math 
import unittest
import numpy
import ROOT
import sys

from xboa.tracking import MatrixTracking
from xboa.algorithms.tune import DPhiTuneFinder
from xboa.hit import Hit
import xboa.common as common

def matrix(phi_x, num_turns):
    # x is conventional ellipse
    # y is phase advance = pi
    # t is phase advance = complex
    f_x = 2*math.pi - phi_x
    cos = math.cos(f_x)
    sin = math.sin(f_x)
    b_x = 10.
    a_x = 1.
    g_x = (1.+a_x**2.)/b_x
    data = [[cos+sin*a_x,  sin*b_x,     0.0,  0.0, 0.0,  0.0],
            [-sin*g_x,     cos-sin*a_x, 0.0,  0.0, 0.0,  0.0],
            [0.0,  0.0,  0.0, -1.0, 0.0,  0.0],
            [0.0,  0.0,  1.0,  0.0, 0.0,  0.0],
            [0.0,  0.0,  0.0,  0.0, 1.0,  0.0],
            [0.0,  0.0,  0.0,  0.0, 0.0,  1.0]]
    matrix = numpy.matrix(data)
    matrix_list = [matrix]
    for i in range(num_turns-1):
        matrix_list.append(matrix*matrix_list[-1])
        for j in range(6):
            if math.isnan(matrix_list[-1][j, j]):
                print("ARG", i, matrix_list[-1], '\n\n', matrix_list[-5])
                raise ValueError("ARG")
    matrix_list = matrix_list
    offset = numpy.matrix([10., 7., 0., 0., 0., 1000.])
    offset_list = [offset]*num_turns
    offset_in = numpy.matrix([10., 7., 0., 0., 0., 1000.])
    tracking = MatrixTracking(matrix_list,
                                   offset_list,
                                   offset_in)
    co = Hit.new_from_dict({'x':10., 'px':7., 'energy':1000.,
                   'pid':2212, 'mass':common.pdg_pid_to_mass[2212]})
    if abs(numpy.linalg.det(matrix) - 1.0) > 1e-9:
        raise ValueError("TM determinant should be 1, got "+\
                          str(numpy.linalg.det(matrix)))
    return co, tracking

class DPhiuneTestCase(unittest.TestCase):
    def setUp(self):
        """Setup the EllipseClosedOrbitFinder"""
        pass

    def test_get_tune(self):
        # check test initialises properly
        co, tracking = matrix(math.pi/4., 1000)
        dphi = DPhiTuneFinder()
        dphi.run_tracking("x", "px", 1.0, 0.0, co, tracking)
        tune = dphi.get_tune()
        print(tune)
        input()

if __name__ == "__main__":
    unittest.main()

