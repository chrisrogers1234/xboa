import unittest
import os

from xboa.core import *
from xboa.hit   import Hit
from xboa.bunch import Bunch
from xboa.common import rg
import xboa.common as common

import xboa.test.TestTools
run_test = xboa.test.TestTools.run_test
run_test_group = xboa.test.TestTools.run_test_group
__float_tol = xboa.test.TestTools.__float_tol
parse_tests = xboa.test.TestTools.parse_tests
__test_root_hist = xboa.test.TestTools.test_root_hist
__test_root_canvas = xboa.test.TestTools.test_root_canvas
__test_root_graph = xboa.test.TestTools.test_root_graph

import StringIO
import sys
import time
import math
import string
import random
import xboa.common.config as config
try:
  config.has_numpy()
  import numpy
  from numpy import linalg
except ImportError:
  pass
try:
  config.has_multiprocessing()
  import multiprocessing
except ImportError:
  pass

import operator
import bisect

#=======================================================================================================================#
#======================                COMMON                ==============================================================#
#=======================================================================================================================#

def common_substitute_test():
  out1 = open('test1.in', 'w')
  if not out1: return 'warn'
  out1.write('some test input\nis written here')
  out1.close()
  common.substitute('test1.in', 'test1.out', {'some':'a bit of', 'test':'tested', 'input':'output', 'written':'read', 'there':'here', 'kx':'uga'})
  out2 = open('test1.out', 'r')
  if not out2: return 'warn'
  lines = out2.readlines()
  out2.close()
  if not lines == ['a bit of tested output\n','is read here']: return 'fail'
  os.remove('test1.in')
  os.remove('test1.out')
  return 'pass'

def __sin_x_one_pass(xyz):
  fgh = []
  for x in xyz:
    fgh.append( __sin_x(x) )
  return fgh
    
def __sin_x(x):
  y = []
  for value in x:
    y.append(math.sin(value))
  return y


def common_nd_newton_raphson1_test():
  solution = common.nd_newton_raphson1(__sin_x, [1., 1.e-5], [0.1, 0.1], [1.e-3,1.e-3])
  y = __sin_x(solution)
  if abs(y[0]) > 1e-5 or abs(y[1] > 1e-5):
    return 'fail'
  return 'pass'

def common_nd_newton_raphson2_test():
  solution = common.nd_newton_raphson2(__sin_x_one_pass, [1.e-5, 1.e-5], [0.1, 0.1], [1.e-3,1.e-3])
  y = __sin_x(solution)
  if abs(y[0]) > 1e-5 or abs(y[1] > 1e-5):
    return 'fail'
  return 'pass'

def common_make_root_canvas_test():
  testpass = True
  canvas = common.make_root_canvas('canvas_name')
  testpass &= canvas.GetName().find('canvas_name') > -1
  canvas = common.make_root_canvas('canvas_name_2', 'canvas_title', bg_color=10, highlight_color=12, border_mode=1, frame_fill_color=2)
  testpass &= __test_root_canvas(canvas, 'canvas_name_2', 'canvas_title', 10, 12, 1, 2)
  if testpass: return 'pass'
  return 'fail'

def common_n_bins_test():
  testpass  = True
  n_p = 20000
  testpass &= common.n_bins(n_p, n_dimensions=1 ) == (n_p/10+1, 0, 0)
  testpass &= common.n_bins(n_p, n_dimensions=2)  == (int(n_p**0.7/10.)+1, int(n_p**0.7/10.)+1, 0)
  testpass &= common.n_bins(n_p, n_dimensions=3)  == (int(n_p**0.5/10.)+1, int(n_p**0.5/10.)+1, int(n_p**0.5/10.)+1)
  testpass &= common.n_bins(n_p, nx_bins=10, n_dimensions=3)  == (10,    int(n_p**0.5/10.)+1, int(n_p**0.5/10.)+1)
  testpass &= common.n_bins(n_p, ny_bins=10, n_dimensions=3)  == (int(n_p**0.5/10.)+1, 10,                   int(n_p**0.5/10.)+1)
  testpass &= common.n_bins(n_p, nz_bins=10, n_dimensions=3)  == (int(n_p**0.5/10.)+1, int(n_p**0.5/10.)+1, 10)
  if testpass: return 'pass'
  else:        return 'fail'

def __sine_list(const1, const2, list_of_x):
  y = []
  for x in list_of_x:
    y.append(const1*math.sin(const2*x))
  return y

def common_min_max_test():
  test_pass = True
  out = common.min_max([-0.1,-0.5,-0.9,0.0])
  test_pass = test_pass and abs(out[0]--0.99) < __float_tol
  test_pass = test_pass and abs(out[1]-+0.09) < __float_tol
  out = common.min_max(x_float_list=[-0.1,-0.5,-0.9,0.0], weight_list=[1,1,0,1])
  test_pass = test_pass and abs(out[0]--0.55) < __float_tol
  test_pass = test_pass and abs(out[1]-+0.05) < __float_tol
  out = common.min_max(x_float_list=[-0.1,-0.5,-0.9,0.0], weight_list=[1,1,0,1], margin=0.0)
  test_pass = test_pass and abs(out[0]--0.5) < __float_tol
  test_pass = test_pass and abs(out[1]-+0.0) < __float_tol
  out = common.min_max(x_float_list=[-0.1,-0.5,-0.9,0.0], weight_list=[1,1,0,1], margin=0.0, xmin=+100.)
  test_pass = test_pass and abs(out[0]-100.) < __float_tol
  test_pass = test_pass and abs(out[1]-+0.0) < __float_tol
  out = common.min_max(x_float_list=[-0.1,-0.5,-0.9,0.0], weight_list=[1,1,0,1], margin=0.0, xmax=-100.)
  test_pass = test_pass and abs(out[0]--0.5) < __float_tol
  test_pass = test_pass and abs(out[1]+100.) < __float_tol
  out = common.min_max([-10., 10.], [0.,0.])
  test_pass = test_pass and abs(out[0]+1.) < __float_tol
  test_pass = test_pass and abs(out[1]-1.) < __float_tol
  if   test_pass: return 'pass'
  else:           return 'fail'

def common_multisort_test():
  multilist = [[-1,1,0,7,4],['a','c','b','e','d'],['alfred','caltrops','bracken','elven','daphne']]
  multilist = common.multisort(multilist)
#  print multilist
  if multilist == [[-1,0,1,4,7],['a','b','c','d','e'],['alfred','bracken','caltrops','daphne','elven']]: return 'pass'
  return 'fail' 

def common_get_bin_edges_test():
  n = range(-21,101)
  for i in range(len(n)): n[i] = float(n[i])**2 #note minimum is not n[0]
  edges = common.get_bin_edges(n, 20)
  if len(edges) != 21: return 'fail'
  if edges[0] != 0. or edges[-1] != n[-1]: return 'fail'
  for i in range( len(edges) - 1):
    if abs(edges[i+1] - edges[i] - n[-1]/20.) > __float_tol: return 'fail'

  edges = common.get_bin_edges(n, 20, -10, 10)
  for i,x in enumerate(edges):
    if abs(x-float(i)+10.) > __float_tol: return 'fail'
  return 'pass'
  

def __build_test_histogram():
  x_list = range(-200,10000)
  y_list = range(-100,10100)
  w_list = []
  for i in range( len(x_list) ): 
    x_list[i] = float(x_list[i])/10.
    y_list[i] = float(y_list[i])/20.
    w_list.append(x_list[i])
  bin_x     = range(-15,100,10)
  bin_y     = range(-4, 200,10)

  c_1d   = numpy.zeros((len(bin_x)-1,1))
  c_2d   = numpy.zeros((len(bin_x)-1,len(bin_y)-1))
  c_2d_w = numpy.zeros((len(bin_x)-1,len(bin_y)-1))

  for i,x in enumerate(x_list):
    p = bisect.bisect_right(bin_x,x_list[i])-1
    q = bisect.bisect_right(bin_y,y_list[i])-1
    if p>=0 and p<len(c_1d):
      c_1d  [p]    += 1.
      if q>=0 and q<len(c_2d[0]):
        c_2d  [p][q] += 1.
        c_2d_w[p][q] += w_list[i]

  return ( (c_1d, c_2d, c_2d_w), (bin_x, bin_y), (x_list,y_list,w_list))  

def common_histogram_test():
  testpass = True

  ((c_1d, c_2d, c_2d_w), (bin_x, bin_y), (x_list,y_list,w_list)) = __build_test_histogram()

  hist_1d   = common.histogram(x_list, bin_x)
  hist_2d   = common.histogram(x_list, bin_x, y_list, bin_y)
  hist_2d_w = common.histogram(x_list, bin_x, y_list, bin_y, w_list)

  testpass &= hist_1d  [1] == bin_x
  testpass &= hist_2d  [1] == bin_x and hist_2d  [2] == bin_y
  testpass &= hist_2d_w[1] == bin_x and hist_2d_w[2] == bin_y

  (pm,qm) = c_2d.shape
  for p in range( pm ):
    testpass &= abs(hist_1d[0][p,0] - c_1d[p,0]) < __float_tol
    for q in range( qm ):
      testpass &=  abs(hist_2d  [0][p,q] - c_2d  [p,q]) < __float_tol
      testpass &=  abs(hist_2d_w[0][p,q] - c_2d_w[p,q]) < __float_tol

  return 'pass'

def common_make_root_histogram_test():
  x_list = range(0,10000)
  w_list = []
  for i in range( len(x_list) ): 
    x_list[i] = float(x_list[i])/10000.
    w_list.append(x_list[i])
  y_list = __sine_list(2., 2.*math.pi, x_list)
  hist1 = common.make_root_histogram('hist sin(x)', y_list, 'hist of x', 100)
  hist2 = common.make_root_histogram('hist sin(x)', y_list, 'hist of x', 50, x_list, 'hist of y', 50)
  hist3 = common.make_root_histogram('hist sin(x)', y_list, 'hist of x', 10, x_list, 'hist of y', 10, w_list)
  testpass = __test_root_hist(hist3,'hist sin(x)','hist of x','hist of y',common.min_max(y_list, w_list, rg.histo_margin)[0], common.min_max(y_list, w_list, rg.histo_margin)[1], 
                                                                          common.min_max(x_list, w_list, rg.histo_margin)[0], common.min_max(x_list, w_list, rg.histo_margin)[1], 
                              rg.line_color, rg.line_style, rg.line_width, rg.fill_color, '')
  hist4 = common.make_root_histogram('hist sin(x)', y_list, 'hist of x', 10, x_list, 'hist of y', 10, w_list, xmin=y_list[7500],xmax=y_list[2500],ymin=x_list[2500],ymax=x_list[7500],
                                     line_color=1, line_style=2, line_width=3, fill_color=4, hist_title_string='title_string')
  testpass = __test_root_hist(hist4,'hist sin(x)', 'hist of x', 'hist of y', y_list[7500], y_list[2500], x_list[2500], x_list[7500], 1, 2, 3, 4, 'title_string')
  canvas1 = common.make_root_canvas('hist_test1')
  hist1.Draw()
  canvas2 = common.make_root_canvas('hist_test2')
  hist2.Draw('cont1z')
  canvas3 = common.make_root_canvas('hist_test3')
  hist3.Draw('lego')
  canvas4 = common.make_root_canvas('hist_test4')
  hist4.Draw('lego')
  if not testpass: return 'fail'
  return 'pass'

def common_make_root_graph_test():
  testpass = True
  canvas = common.make_root_canvas('graph_test')
  x_list = range(0,100)
  for i in range( len(x_list) ): x_list[i] = float(x_list[i])/100.
  y_list = __sine_list(2., 2.*math.pi, x_list)
  mm = common.min_max(x_list) + common.min_max(y_list)
  (hist,graph) = common.make_root_graph('test', x_list, 'x [2#pi rad]', y_list, 'a*sin(b*x)')
  if not __test_root_hist(hist, '', 'x [2#pi rad]', 'a*sin(b*x)', mm[0], mm[1], mm[2], mm[3], rg.line_color, rg.line_style, rg.line_width, rg.fill_color, ''): return 'fail'
  (hist,graph) = common.make_root_graph('test', x_list, 'x [2#pi rad]', y_list, 'a*sin(b*x)', xmin=-1001., xmax=+1001, ymin=-1002., ymax=+1002.,line_color=201, line_style=202, line_width=203, fill_color=204, hist_title_string='mr title')
  testpass &= __test_root_hist(hist, 'namey', 'x [2#pi rad]', 'a*sin(b*x)', -1001., +1001., -1002., +1002., rg.line_color, rg.line_style, rg.line_width, rg.fill_color, 'mr title') 
  testpass &= __test_root_graph(graph, 'namey', x_list, y_list, 201, 202, 203, 204)
  (x_list, y_list) = ([3,2,1], [3,2,1]) #check that x_list and y_list are not changed by sort
  (hist,graph) = common.make_root_graph('test', x_list, 'x', y_list, 'y')
  testpass &=   (x_list, y_list) == ([3,2,1], [3,2,1])
  hist.Draw()
  graph.Draw()
  common.clear_root()
  if testpass: return 'pass'
  else:        return 'fail'

def common_make_root_graph_2d_test():
  return 'fail'

def common_make_root_multigraph_test():
  canvas = common.make_root_canvas('multigraph_test')
  x_list_of_lists = []
  y_list_of_lists = []
  for i in range(2):
    x_list_of_lists.append(range(0,50))
    for i in range( len(x_list_of_lists[-1]) ):
      x_list_of_lists[-1][i] /= 10.
    x_list_of_lists.append(range(0,100))
    for i in range( len(x_list_of_lists[-1]) ):
      x_list_of_lists[-1][i] /= 20.
  for i in range( len(x_list_of_lists) ):
     y_list_of_lists.append(__sine_list(i+1, i+1, x_list_of_lists[i]))
  (hist,list_of_graphs) = common.make_root_multigraph('test', x_list_of_lists, 'x [rad]', y_list_of_lists, 'a*sin(b*x)')
  hist.Draw()
  for graph in list_of_graphs:
    graph.Draw()
  return 'pass' # a test that can't fail - excellent!

def common_wait_for_root_test():
  time.sleep(1)
  common._common._canvas_persistent = []
  common.wait_for_root() #cant test with a root canvas as i want to automate the test...
  return 'pass'

def common_wait_for_matplot_test():
  common.wait_for_matplot()
  return 'pass' # a test that can't fail - excellent!

def common_make_matplot_graph_test():
  x_list = range(0,100)
  for i in range( len(x_list) ): x_list[i] = float(x_list[i])/100.
  y_list = __sine_list(2., 2.*math.pi, x_list)
  myplot = common.make_matplot_graph(x_list, 'x [2#pi rad]', y_list, 'a*sin(b*x)')
  return 'pass' # a test that can't fail - excellent!

def common_make_matplot_histogram_test():
  x_list = range(0,10000)
  w_list = []
  for i in range( len(x_list) ): 
    x_list[i] = float(x_list[i])/10000.
    w_list.append(x_list[i])
  y_list = __sine_list(2., 2.*math.pi, x_list)
  common.make_matplot_histogram(y_list, 'hist of x', 100)
  common.make_matplot_histogram(y_list, 'hist of x', 50, x_list, 'hist of y', 50)
  common.make_matplot_histogram(y_list, 'hist of x', 10, x_list, 'hist of y', 10, w_list)
  return 'pass' # a test that can't fail - excellent!

def common_make_matplot_scatter_test():
  x_list = range(0,10000)
  for i in range( len(x_list) ): 
    x_list[i] = float(x_list[i])/10000.
  y_list = __sine_list(2., 2.*math.pi, x_list)
  common.make_matplot_scatter(y_list, 'hist of x', x_list, 'hist of y')
  return 'pass' # a test that can't fail - excellent!


def common_make_matplot_multigraph_test():
  x_list_of_lists = []
  y_list_of_lists = []
  for i in range(2):
    x_list_of_lists.append(range(0,50))
    for i in range( len(x_list_of_lists[-1]) ):
      x_list_of_lists[-1][i] /= 10.
    x_list_of_lists.append(range(0,100))
    for i in range( len(x_list_of_lists[-1]) ):
      x_list_of_lists[-1][i] /= 20.
  for i in range( len(x_list_of_lists) ):
     y_list_of_lists.append(__sine_list(i+1, i+1, x_list_of_lists[i]))
  common.make_matplot_multigraph(x_list_of_lists, 'x [rad]', y_list_of_lists, 'a*sin(b*x)')
  return 'pass' # a test that can't fail - excellent!

def common_show_matplot_and_continue_test():
  common.matplot_show_and_continue()
  return 'pass' # a test that can't fail - excellent!

def __subprocess_function_1(some_arg, some_other_arg):
  if some_arg != 'hello' and some_other_arg != 'world':
    print 'error in common_subprocess_test - aborting'
    sys._exit()
  while True:
    time.sleep(60)

def __subprocess_function_2(some_arg, some_other_arg):
  if some_arg != 'hello' and some_other_arg != 'world':
    print 'error in common_subprocess_test - aborting'
    sys._exit()
  for i in range(5):
    print i,' ',
  print

def __subprocess_function_3():
  pass

def common_subprocess_test():
  pid1 = common.subprocess(__subprocess_function_1,   ('hello', 'world'))
  pid2 = common.subprocess(__subprocess_function_2, ('hello', 'world'))
  return 'pass'

def common_kolmogorov_smirnov_test_test():
  import random
  list_1 = []
  list_2 = []
  list_3 = []
  for i in range(10000): list_1.append( random.gauss(0., 1.) )
  for i in range(10000): list_2.append( random.gauss(0., 1.) )
  for i in range(10000): list_3.append( random.gauss(0.1, 1.1) )
  testpass  = True
  testpass &= 1.-common.kolmogorov_smirnov_test(list_1, list_1) < __float_tol
  testpass &= common.kolmogorov_smirnov_test(list_1, list_2) > 1e-3
  testpass &= common.kolmogorov_smirnov_test(list_1, list_3) < 1e-3 
  if testpass: return 'pass'
  else:        return 'fail'


def __is_alive(process):
  if type(process) == type(1):
    try: 
      os.kill(process, 0)
      return True
    except:
      return False  
  else:
    return process.is_alive()

def common_kill_subprocesses_test():
  pid1 = common.subprocess(__subprocess_function_1, ('hello', 'world'))
  pid2 = common.subprocess(__subprocess_function_2, ('hello', 'world'))
  common.kill_all_subprocesses()
  if __is_alive(pid1) or __is_alive(pid2): 
    return 'fail - there is a known issue with python < 2.6 if using PyROOT'
  return 'pass'


def common_normalise_vector_test():
  import random
  for dim in range(2,5):
    for v_count in range(10):
      vector         = numpy.matrix(numpy.zeros(dim))
      for ind,value in numpy.ndenumerate(vector):
        vector[ind] = random.random()
      matrix_inverse = numpy.matrix(numpy.ones([dim,dim]))
      for (i,j),value in numpy.ndenumerate(matrix_inverse):
        if i != j: matrix_inverse[i,j] /= (i+1)/10./(j+1)
      vector = common.normalise_vector(vector, matrix_inverse)
      if abs( (vector*matrix_inverse*vector.transpose())[0,0]-1. )>common.float_tolerance:
        return 'fail'
  return 'pass'

def common_make_grid_test():
  grid_list = ((2, 2), (3,2), (2,3),(2,4))
  testpass  = True
  for grid_var in grid_list:
    n_dim,n_per_dim = grid_var
    grid = common.make_grid(*grid_var)
    #check there are correct number of particles
    testpass &= len(grid)==n_per_dim**n_dim
    #check there are no repeats
    for i,vec1 in enumerate(grid):
      for j,vec2 in enumerate(grid[i+1:]):
        testpass &= ((vec1-vec2)*(vec1-vec2).transpose())[0,0] > common.float_tolerance
    #check on an integer multiple of grid spacing
    for vec in grid:
      for pos in vec.flat:
        grid_spacing = (1./float(n_per_dim-1))
        testpass &= abs(pos/grid_spacing-round(pos/grid_spacing)) < common.float_tolerance
  if testpass: return 'pass'
  return 'fail'

def common_make_shell_test():
  n_per_dim = 3
  for dim in range(2,4):
    matrix = numpy.matrix(numpy.ones([dim,dim]))
    for (i,j),value in numpy.ndenumerate(matrix):
      if i != j: matrix[i,j] *= 1./float(i+1)/float(j+1)
    matrix_inverse = numpy.linalg.inv(matrix)
    shell          = common.make_shell(n_per_dim, matrix)
    #check there are correct number of particles
    if not (len(shell)==n_per_dim**dim or len(shell)==n_per_dim**dim-1):
      return 'fail'
    #check they are normalised correctly
    for vector in shell:
      if abs( (vector*matrix_inverse*vector.transpose())[0,0]-1. )>common.float_tolerance:
        return 'fail'
  return 'pass'

def common_fit_ellipse_test():
  numpy.random.seed()
  n_oom, n_points_per_magnitude = 6, 100
  points = []
  for n in range(n_oom):
      cov = numpy.array([[int(i == j)*float(i+1)*2**n for i in range(3)] for j in range(3)])
      mean = numpy.array([1.e4-2**n-1., -2**n-1., -2**n-1.])
      points += [x for x in numpy.random.multivariate_normal(mean, cov, n_points_per_magnitude)]
  # running ellipse fitter with 1 iteration is the same as running with loose cuts
  mean_1, cov_1 = common.fit_ellipse(points, 1000., None, 1, False)
  mean_2, cov_2 = common.fit_ellipse(points, 1.e9, None, 10, False)
  testpass = True
  for i in range(3):
      testpass = testpass and mean_1[i] == mean_2[i]
      for j in range(3):
          testpass = testpass and cov_1[i, j] == cov_2[i, j]
  
  # check that we get some convergence
  mean_3, cov_3 = common.fit_ellipse(points, 1000., None, 30, True)
  mean_4, cov_4 = common.fit_ellipse(points, 100., None, 30, True)
  for i in range(3):
      testpass = testpass and mean_4[i] > mean_3[i]
      testpass = testpass and cov_4[i, i] < cov_3[i, i]

  # weight == 0 for all particles with y < 0; check mean 0. < 0.
  weights = [0. for i in points]
  for i, a_point in enumerate(points):
      if a_point[1] < 0.:
          weights[i] = 1.
  mean_5, cov_5 = common.fit_ellipse(points, 1000., weights, 30, True)
  testpass = testpass and mean_5[1] < 0.

  # Does not converge...
  # mean_6, cov_6 = common.fit_ellipse(points, 10., None, 30, True)
  # testpass = testpass and numpy.linalg.det(cov_6) > 0.
  if testpass:
      return 'pass'
  else:
      return 'fail'

def common_make_root_ellipse_function_test():
    testpass = True
    # worth checking by eye - the ellipse should be tilted forwards (i.e. +ve
    # correlation); and should roughly fill the canvas. If one sets correlation
    # to 0., y-intercept at x=0., 200. and x-intercept at y=0., 2.
    ell_cov = numpy.array([[10000., 0.], [0., 1.]])
    ell_mean = [100., 1.]
    canv = common.make_root_canvas("ellipse_function_test_0")
    func = common.make_root_ellipse_function(ell_mean, ell_cov, contours=[1.], xmin=-10., xmax=210., ymin=-0.1, ymax=2.1)
    func.Draw()
    canv.Update()
    for value in [(0., 1.), (200., 1.), (100., 0.), (100., 2.)]:
        testpass = testpass and (func.Eval(*value)-1.) < common.float_tolerance
        if not testpass:
            print 'FAILED ON ', value, func.Eval(*value)

    ell_cov = numpy.array([[3, 1], [1, 2]])
    ell_mean = [1, 1]
    canv = common.make_root_canvas("ellipse_function_test_1")
    func = common.make_root_ellipse_function(ell_mean, ell_cov)
    func.Draw()
    canv.Update()

    ell_cov = numpy.array([[1, 0.99], [0.99, 1]])
    ell_mean = [1, 1]
    canv = common.make_root_canvas("ellipse_function_test_2")
    func = common.make_root_ellipse_function(ell_mean, ell_cov, [1., 0.08], 1-3, 1+3, 1-2, 1+2)
    func.SetLineColor(4)
    func.Draw()
    canv.Update()

    # note this looks grotty - blame ROOT
    testpass = testpass and (func.GetContourLevel(1)-0.08) < common.float_tolerance \
                        and (func.GetContourLevel(0)-1.) < common.float_tolerance
    if testpass:
        return 'pass'
    return 'fail'


def __test_run(item):
  if item == 'throw':
    raise RuntimeError('Throwing item '+str(item))
  time.sleep(random.random()) # returns to queue in random order
  return 'output',item

def common_test_function_with_queue():
  queue = multiprocessing.Queue()
  common._common.__function_with_queue((__test_run, queue, ("input",), 5))
  assert queue.get() == (5, ("output", "input"))
  common._common.__function_with_queue((__test_run, queue, ("throw",), 7))
  out = queue.get()
  assert out[0] == 7
  try:
    common._common.__function_with_queue(('no_args',))
    assert False # should raise an exception in parent process
  except Exception:
    pass
  return 'pass'

def common_test_process_list():
  process_out = common.process_list(__test_run, [(i,) for i in range(10)], 3)
  for i in range(10):
    assert process_out[i] == ('output',i) # check sorting
  return 'pass'

def test_matplotlib(test_results):
  # Humm, causes a ROOT crash, humm
  try:
    config.has_matplot()
    tests = [common_wait_for_matplot_test, common_make_matplot_graph_test, common_make_matplot_histogram_test, 
             common_make_matplot_multigraph_test, common_make_matplot_scatter_test, common_show_matplot_and_continue_test]
    run_test_group(test_results, tests, [()]*len(tests))
  except ImportError:
    test_results.append('Warning - could not find MatPlotLib. Skipping MatPlotLib dependent tests')
  return test_results

def test_common():
  test_results = []
  tests = [common_substitute_test, common_min_max_test, common_multisort_test, common_histogram_test, common_get_bin_edges_test, common_subprocess_test, common_kill_subprocesses_test, common_n_bins_test, common_normalise_vector_test]
  run_test_group(test_results, tests, [()]*len(tests))

  try:
    config.has_multiprocessing()
    tests = [common_test_function_with_queue, common_test_process_list]
    run_test_group(test_results, tests, [()]*len(tests))
  except ImportError:
    test_results.append('Warning - could not find multiprocessing. Skipping multiprocessing dependent tests')


  try:
    config.has_numpy()
    tests = [common_nd_newton_raphson1_test, common_nd_newton_raphson2_test, common_fit_ellipse_test, common_make_shell_test]
    run_test_group(test_results, tests, [()]*len(tests))
  except ImportError:
    test_results.append('Warning - could not find NumPy. Skipping NumPy dependent tests')

  try:
    config.has_root()
    # nb common_make_root_ellipse_function_test also depends on numpy
    tests = [common_wait_for_root_test, common_make_root_canvas_test, common_make_root_graph_test, common_make_root_histogram_test, 
             common_make_root_multigraph_test, common_make_root_multigraph_test, common_kolmogorov_smirnov_test_test, common_make_grid_test,
             common_make_root_ellipse_function_test]
    run_test_group(test_results, tests, [()]*len(tests))
  except ImportError:
    test_results.append('Warning - could not find ROOT. Skipping ROOT dependent tests')

  test_results = test_matplotlib(test_results)
  results = parse_tests(test_results)

  print '\n============\n|| COMMON ||\n============'
  print 'Passed ',results[0],' tests\nFailed ',results[1],' tests\n',results[2],' warnings\n\n\n'
  return results

class CommonTestCase(unittest.TestCase):
    def test_common_all(self):
        passes, fails, warns = test_common()
        self.assertEqual(fails, 0)

if __name__ == "__main__":
    unittest.main()

