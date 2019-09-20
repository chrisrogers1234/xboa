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
#

"""
common contains some global physics and other parameters, plus some useful functions
- icool_pid_to_pdg = dict from icool particle identification indices to pdg indices
- pdg_pid_to_icool = inverse of above
- constants        = string to number dict of physical constants
- units            = string to number dict of some units
Functions documented below
"""

import operator
import copy
import bisect
import sys
import string
import math
import os
import pydoc
import bisect
import atexit
import time
import signal
import ctypes
from . import config
try:
    import ROOT
except ImportError:
    pass
try:
    import matplotlib
    import matplotlib.pyplot as pyplot
except ImportError:
    pass
try:
    import numpy
    import numpy.linalg as linalg
except ImportError:
    pass
try:
    import multiprocessing
except ImportError:
    pass


float_tolerance = 1.e-9
kill_subprocesses_at_exit = True


pdg_pid_to_muon1 = {-13:'mu+'}
muon1_pid_to_pdg = {}
for k,v in pdg_pid_to_muon1.items():
  muon1_pid_to_pdg[v] = k

icool_pid_to_pdg = {0:0, 1:-11, 2:-13, 3:211, 4:321, 5:2212, -1:11, -2:13, -3:-211, -4:-321, -5:-2212};
pdg_pid_to_icool = {};
for k,v in icool_pid_to_pdg.items():
  pdg_pid_to_icool[v] = k;

#* MARS PARTICLE ID (JJ):
#* 1 2 3   4   5  6  7   8   9 10 11 12   13  14 15 16  17  18  19   20  21
#* p n pi+ pi- K+ K- mu+ mu- g e- e+ pbar pi0 d  t  He3 He4 num nuam nue nuae
#* 22  23  24 25  26  27   28   29   30   31   32   33   34  35   36   37   38    39    40
#* K0L K0S K0 AK0 LAM ALAM SIG+ SIG0 SIG- nbar KSI0 KSI- OM- sib- si0b sib+ AKSI0 ksib+ omb+

mars_pid_to_pdg  = {1:2212, 2:2112, 3:211, 4:-211, 5:321, 6:-321, 7:-13, 8:13, 9:22, 10:11, 11:-11, 12:-2212, 13:111, 14:1000010020, 15:1000010030, 16:1000020030, 17:1000020040, 18:14, 19:-14, 20:12, 21:-12, 22:130, 23:310, 24:311, 25:-311,26:3122,27:-3122,28:0,29:0,30:0,31:-2112,32:0,33:0,34:0,35:0,36:0,38:0,39:0,40:0};
pdg_pid_to_mars  = {}
for k,v in mars_pid_to_pdg.items():
  pdg_pid_to_mars[v] = k;

pdg_pid_to_mass  = {0:0, 11:0.510998910, 12:0., 13:105.6583668, 14:0., 22:0., 111:134.9766, 211:139.57018, 321:493.667, 2112:939.56536, 2212:938.271996, 1000010020:1876.1239, 1000010030:2809.432, 1000020030:2809.41346, 1000020040: 3728.4001, 130:497.614, 310:497.614, 311:497.614, 3122:1115.683}
pdg_pid_to_name  = {0:'none', 11:'e-', 12:'electron neutrino', 13:'mu-', 14:'muon neutrino', 22:'photon', 111:'pi0', 211:'pi+', 321:'K+', 2112:'neutron', 2212:'proton', 1000010020:'deuterium', 1000010030:'tritium', 1000020030:'3He', 1000020040:'4He', 130:'K0L', 310:'K0S', 311:'K0', 3122:'lambda',
-11:'e+', -12:'electron antineutrino', -13:'mu+', -14:'muon antineutrino', -211:'pi-', -321:'K-', -2112:'antineutron', -2212:'antiproton', -3122:'antilambda'}

pdg_pid_to_charge  = {0:0, 11:-1, 12:0, 13:-1, 14:0, 22:0, 111:0, 211:+1, 321:+1, 2112:0, 2212:+1, 1000010020:0, 1000010030:0, 1000020030:0, 1000020040:0, 130:0, 310:0, 311:0, 3122:0, -11:+1, -12:0, -13:+1, -14:0, -211:-1, -321:-1, -2112:0, -2212:-1, -3122:0}


constants        = {'c_light':299.792458, 'pi':3.14159265,'echarge':1}
units            = {'':1.,
  'mum':1.e-3, 'mm':1., 'cm':10., 'm':1.e3, 'km':1.e6, 
  'ns':1., 'mus':1.e3, 'ms':1e6, 's':1.e9, 
  'eV':1e-6, 'keV':1e-3, 'MeV':1., 'GeV':1.e3, 'TeV':1e6, 
  'eV/c':1e-6, 'keV/c':1e-3, 'MeV/c':1., 'GeV/c':1.e3, 'TeV/c':1e6, 
  'eV/c2':1e-6, 'keV/c2':1e-3, 'MeV/c2':1., 'GeV/c2':1.e3, 'TeV/c2':1e6, 
  'Gauss':1.e-7, 'mT':1.e-6, 'T':1.e-3, 'kT':1.,
  'V':1.e-6, 'kV':1.e-3, 'MV':1., 'GV':1.e3, 
  'kHz':1.e-6, 'MHz':1.e-3, 'GHz':1.,
  'GV/m':1.,'GV/mm':1.e3,
  'kW':6.24150974e6, 'MW':6.24150974e9, 'GW':6.24150974e12,
  'degrees':2.*constants['pi']/360., 'radians':1., 'deg':2.*constants['pi']/360., 'rad':1., 'degree':2.*constants['pi']/360., 'radian':1.,
  'echarge':1., 'Coulomb':6.24150974*10.**18.
}

### root globals
#line_color_int=1, line_style_int=1, line_width_int=2, fill_color_int=None, stats_bool=False, hist_title_string=''
class rg:
  """
  Container to hold some details of root global style information
  """
  canvas_border_mode     = 0
  canvas_highlight_color = 2
  canvas_fill_color      = 10
  hist_fill_color        = canvas_fill_color
  line_width             = 2
  line_color             = 1
  line_style             = 1
  fill_color             = 0
  graph_fill_color       = 10
  stats                  = False
  histo_margin           = 0.0 #margin around edge of a histogram inside axes
  graph_margin           = 0.1 #margin around edge of a graph inside axes
  fit_color              = 4
  fit_style              = 2

## privates
_canvas_persistent      = []
_hist_persistent        = []
_graph_persistent       = []
_legend_persistent      = []
_function_persistent      = []

## pyplot globals
_figure_index = 1

def substitute(file_name_in, file_name_out, switch_dict):
  """
  Read in file_name_in and write to file_name_out, replacing key with value in switch_dict. Must be a built in function somewhere to do same...

  - file_name_in  = string name of the input file
  - file_name_out = string name of the output file
  - switch_dict   = dict of values to be swapped to the values they will be swapped for

  e.g. common.substitute('file.in', 'file.out', {'energy':'momentum'})
  """
  fin  = open(file_name_in,  'r')
  fout = open(file_name_out, 'w')
  for line in fin:
    for key, value in switch_dict.items():
      line = line.replace(str(key), str(value))
    fout.write(line)
  fin.close()
  fout.close()

wrapped_y_function = None
def __y_function_wrapper(x_list_of_lists):
  global wrapped_y_function
  out = []
  for value in x_list_of_lists: out.append(wrapped_y_function(value))
  return out

def nd_newton_raphson1(y_function, y_tolerances_list, x_start_values_list, x_deltas_list, max_iteration=10, x_upper_limits=None, x_lower_limits = None, verbose=True):
  """
  Root finding in an arbitrary dimensional system. Returns x-value for y(x) = 0; caveat is dimension of y must equal dimension of x.
  If you use this, you might find more and better root finding functions in SciPy module

  - y_function is a reference to the function to be minimised i.e. y(x); it takes a list of x-values; and returns a list of y-values
  - y_tolerances_list is a list of tolerances; the iteration will stop when abs(value) < value_tolerance
  _ x_start_values_list is a list of the values I will try to start with
  - x_deltas_list is a list of the initial estimates of the error on x
  - max_iteration is the maximum number of iterations allowed
  - x_upper_limits is for future development
  - x_lower_limits is for future development

  e.g. nd_newton_raphson(some_function, [0.1, 0.1], [0,0], [1,1]) will find root to y(x) < (0.1,0.1); starting at x=(0,0); initial error estimated to be [1,1]. 
  some_function would be called like some_function([x_0, x_1]) and should return a list like [y_0,y_1]
  """
  global wrapped_y_function
  wrapped_y_function = y_function
  return nd_newton_raphson2( __y_function_wrapper, y_tolerances_list, x_start_values_list, x_deltas_list, max_iteration, x_upper_limits, x_lower_limits, verbose)

def nd_newton_raphson2(y_function, y_tolerances_list, x_start_values_list, x_deltas_list, max_iteration=10, x_upper_limits=None, x_lower_limits = None, verbose=True):
  """
  Alternative version of nd_newton_raphson1. Here y_function takes a list of lists of x_values, of length dimension+1 and returns a list of lists of y_values
  Optimisation for when y_function can be made faster by running several jobs at once...

  - y_function is a reference to the function to be minimised i.e. y(x); it takes a list of lists of x-values; and returns a list of lists y-values
  - y_tolerances_list is a list of tolerances; the iteration will stop when abs(value) < value_tolerance
  - x_start_values_list is a list of the values I will try to start with
  - x_deltas_list is a list of the initial estimates of the error on x
  - max_iteration is the maximum number of iterations allowed
  - x_upper_limits is for future development
  - x_lower_limits is for future development

  e.g. nd_newton_raphson(some_function, [0.1, 0.1], [0,0], [1,1]) will find root to y(x) < (0.1,0.1); starting at x=(0,0); initial error estimated to be [1,1]. 
  some_function would be called like some_function([[x_00, x_01] ,[x_10, x_11], [x_20, x_21]) and should return a list like [[y_00,y_01],[y_10,y_11],[y_20,y_21]]
  """
  config.has_numpy()
  done                = False
  x_list              = []
  for key in range( len(x_start_values_list)+1 ):
    x_list.append( copy.deepcopy(x_start_values_list) )
  delta_x             = numpy.matrix( str(x_deltas_list) )
  count  = copy.deepcopy(max_iteration)
  limits = type(x_upper_limits) == type([]) and type(x_lower_limits) == type([])
  if limits:
    delta_limit = []
    for i in range(len(x_start_values_list)): delta_limit.append(x_upper_limits[i]-x_lower_limits[i])
  while not done and count > 0:
    count -= 1
    jacobian          = numpy.matrix( numpy.zeros( (len(x_start_values_list), len(x_start_values_list)) ) )
    for i in range( len(x_start_values_list) ):
      if limits: #make the function periodic with the limits
        x_list[0][i] -= delta_limit[i]*math.floor(x_list[0][i]/delta_limit[i]-x_lower_limits[i]);
    for i in range( len(x_start_values_list) ):
      x_list[i+1]     = copy.deepcopy(x_list[0])
      x_list[i+1][i] += delta_x[0,i]
    y_x = y_function(x_list)
    try:
      y_x0 = numpy.matrix( str(y_x[0]) )
    except:
      raise RuntimeError('Newton-Raphson failed to evaluate function with input '+str(x_list)+' and output '+str(y_x))
    # check that I move closer to the root... should stabilise the function I hope
    # vdot requires 1d array-like for some numpy versions
    y_test = numpy.array(y_x0).flatten()
    y_magnitude_squared = numpy.vdot(y_test, y_test)
    for i in range( len(x_start_values_list) ):
      if abs(delta_x[0,i]) < float_tolerance:
        print('Warning - returned without convergence; delta_x',str(delta_x),'is below float tolerance')
        return x_list[0]
      for j in range( len(y_tolerances_list) ):
        jacobian[j,i] =  (y_x[i+1][j] - y_x[0][j])/delta_x[0,i]
      x_list[i+1][i]           -= delta_x[0,i]
    try:
      delta_x = -(linalg.inv(jacobian)*y_x0.transpose()).transpose()
    except:
      print('Newton-Raphson failed with (singular?) jacobian\n',jacobian,'\nbailing out')
      print('x:',x_list[0],'   y(x):',y_x[0],'   dx:',delta_x)
      return x_list[0]
    done  = True
    if verbose: print('x:',x_list[0],'   y(x):',y_x[0],'   dx:',delta_x)
    for i in range( len(x_start_values_list) ):
      if abs(y_x[0][i]) > y_tolerances_list[i]: 
        done = False
      x_list[0][i] += delta_x[0,i]
    y_x0 = y_function([x_list[0]])
  return x_list[0]

def min_max(x_float_list, weight_list=[], margin = 0.1, xmin=None, xmax=None):
  """
  Return minimum and maximum of a list (i) discarding values with ~0 weight and (ii) adding a margin. For making histograms.

  - x_float_list = return minimum and maximum of this list of floats
  - weight_list  = ignore items in x_float_list if weight is 0. Ignored if weight_list is not same length as x_float_list
  - margin = add a margin given by (x_max-x_min)*margin
  - xmin = if set, will override the xmin value
  - xmax = if set, will override the xmax value

  e.g. common.min_max([0.1,0.2,0.3,0.4], [0,1,1,1], 0.2) will return [0.16,0.44]
  """
  new_floats = x_float_list
  if len(weight_list) == len(x_float_list):
    new_floats =  []
  for ind in range(len(weight_list)):
    if weight_list[ind] > 1e-6:
      new_floats.append(x_float_list[ind]) 
  if len(new_floats) == 0: x = [0.,0.]
  else:                      x = [min(new_floats), max(new_floats)]
  delta = (x[1]-x[0])*margin
  x[0] -= delta
  x[1] += delta
  if(x[1] - x[0] < 1e-9):
    x[0] -= 1.
    x[1] += 1.
  if xmin!=None: x[0] = xmin
  if xmax!=None: x[1] = xmax
  return x

def multisort(list_of_lists):
  """Sort a list of lists by the first list"""
  #first convert from vertical lists to horizontal lists
  horizontal_list = []
  for i in range( len(list_of_lists[0]) ):
    horizontal_list.append([])
    for j in range( len(list_of_lists) ):
      horizontal_list[-1].append(list_of_lists[j][i])
  #now sort by first element
  getitem = operator.itemgetter(0)
  horizontal_list = sorted(horizontal_list, key=getitem)
  #now convert back to list_of_lists
  for i in range( len(list_of_lists) ):
    for j in range( len(list_of_lists[0]) ):
      list_of_lists[i][j] = horizontal_list[j][i]
  return list_of_lists

def n_bins(n_points, nx_bins=None, ny_bins=None, nz_bins=None, n_dimensions=1):
  """
  Dynamically decide a number of bins depending on the number of points in the histogram

  - n_points     = number of data points in the histogram
  - nx_bins      = set to an integer to override the automatic selection for number of x bins
  - ny_bins      = set to an integer to override the automatic selection for number of y bins
  - n_dimensions = set to number of dimensions in the histogram 

  Return value is a tuple (nx_bins, ny_bins, nz_bins), setting 0 to values that are out of the dimension range
  """
  out = [nx_bins, ny_bins, nz_bins]
  num_events = float(n_points)
  if nx_bins==None and n_dimensions==1: out[0] = int(num_events/10.)+1
  if nx_bins==None and n_dimensions==2: out[0] = int(num_events**0.7/10.)+1
  if ny_bins==None and n_dimensions==2: out[1] = int(num_events**0.7/10.)+1
  if nx_bins==None and n_dimensions==3: out[0] = int(num_events**0.5/10.)+1
  if ny_bins==None and n_dimensions==3: out[1] = int(num_events**0.5/10.)+1
  if nz_bins==None and n_dimensions==3: out[2] = int(num_events**0.5/10.)+1
  for i in range(3): 
    if out[i] == None: out[i]= 0 #set out to 0 for values that are out of the dimension range
  return tuple(out)

def histogram(x_values, x_bins, y_values=None, y_bins=None, weights=None):
  """
  Get a 1d or 2d list of bin weights from a set of data, weights and bin edges

  - x_values = list of x values to be binned
  - x_bins   = list of x bin edges
  - y_values = list of y values to be binned. Set to None to make a 1d binning
  - y_bins   = list of y bin edges of same length as x_values
  - weights  = list of statistical weights of same length as x_values. Set to None to make all weights default to 1.

  Return value is a tuple of (bin_weights, x_bins, y_bins)
  """
  config.has_numpy()
  is_1d    = False
  if weights == None:
    weights = [1.]*len(x_values)
  if y_values == None:
    is_1d    = True
    y_values = [0.]*len(x_values)
    y_bins   = [-1.,1.]
  contents = numpy.zeros((len(x_bins)-1, len(y_bins)-1), )
  for i,x in enumerate(x_values):
    p = bisect.bisect_right(x_bins,x_values[i])-1
    q = bisect.bisect_right(y_bins,y_values[i])-1
    if p>=0 and p<len(x_bins)-1 and q>=0 and q<len(y_bins)-1:
      contents[p,q] += weights[i]
  out = (contents, x_bins, y_bins)
  if is_1d: return (contents, x_bins, [])
  else:     return (contents, x_bins, y_bins)

def get_bin_edges(list_of_variables, number_of_bins, xmin=None, xmax=None):
  """
  Get a sorted list of equally spaced bin edges from a list of floats

  - list_of_variables = list of floats to be binned
  - number_of_bins    = number of bins to make; note that there will be number_of_bins+1 edges
  - xmin              = lower edge of all the bins (set to None to auto-detect)
  - xmax              = upper edge of all the bins (set to None to auto-detect)
  """
  my_bins = []
  mm      = min_max(list_of_variables, margin=0.0)
  if xmin!=None: mm[0]=xmin
  if xmax!=None: mm[1]=xmax
  delta   = (mm[1] - mm[0])/float(number_of_bins)
  for i in range(number_of_bins+1):
    my_bins.append(mm[0]+delta*i)
  return my_bins

def make_root_canvas(name_string, title_string=None, bg_color=rg.canvas_fill_color, highlight_color=rg.canvas_highlight_color, 
                     border_mode=rg.canvas_border_mode, frame_fill_color=rg.hist_fill_color):
  """
  Make a root canvas with name canvas_name_string-<index> where <index> is a unique integer starting from 0

  - name_string      = Name of the canvas. Due to a ROOT bug, xboa adds a unique identifier to the name_string to ensure the canvas is drawn.
  - title_string     = Title of the canvas (as displayed in canvas window title bar); if set to None will use the name_string.
  - bg_color         = Fill color of the canvas.
  - highlight_color  = When a canvas is selected, ROOT draws a border with a particular color to indicate that the canvas is selected.
  - border_mode      = When a canvas is selected, ROOT draws a border if border mode is not set to 0.
  - frame_fill_color = Fill color of frames drawn on the canvas (e.g. histograms).
  """
  config.has_root()
  canvas_name_string = name_string+"-"+str(len(_canvas_persistent))
  if title_string == None: title_string = name_string
  canvas = ROOT.TCanvas(canvas_name_string, title_string)
  canvas.SetHighLightColor(highlight_color)
  canvas.SetFillColor(bg_color)
  canvas.SetBorderMode(border_mode)
  canvas.SetFrameFillColor(frame_fill_color)
  _canvas_persistent.append(canvas)
  return canvas

def make_root_histogram(name_string, x_float_list, x_axis_string, n_x_bins, y_float_list=[], y_axis_string='', n_y_bins=0, weight_list=[], xmin=None, xmax=None, ymin=None, ymax=None,
                        line_color=rg.line_color, line_style=rg.line_style, line_width=rg.line_width, fill_color=rg.fill_color, stats=rg.stats, hist_title_string=''):
  """
  Make a root histogram with data taken from float lists and axes named after the axis strings.

  - name_string   = name given to the histogram
  - x_float_list  = list of x-data
  - x_axis_string = string used to label the x-axis
  - n_x_bins      = number of bins in x direction
  - y_float_list  = list of y-data. If number of items in y list not equal to number in x list, will build 1d histogram
  - y_axis_string = string used to label the y-axis
  - n_y_bins      = number of y bins
  - weight_list   = if present, each item will be filled with weight taken from this list
  - xmin          = float that overrides auto-detection of minimum x-axis value
  - xmax          = float that overrides auto-detection of maximum x-axis value
  - ymin          = float that overrides auto-detection of minimum y-axis value
  - ymax          = float that overrides auto-detection of maximum y-axis value
  - line_color    = int that sets the line colour of the histogram
  - line_style    = int that sets the line style of the histogram
  - line_width    = int that sets the line width of the histogram
  - fill_color    = int that sets the fill color of the histogram
  - stats         = set to True to plot a stats box on the histogram
  - hist_title_string = specify the string that will appear as a title on the canvas

  Return value is the histogram
  """
  config.has_root()
  name_string += " "+str(len(_hist_persistent))
  if len(y_float_list) == len(x_float_list):
    x_min_max = min_max(x_float_list, weight_list, margin=rg.histo_margin, xmin=xmin, xmax=xmax)
    y_min_max = min_max(y_float_list, weight_list, margin=rg.histo_margin, xmin=ymin, xmax=ymax)
    hist = ROOT.TH2D(name_string, hist_title_string+';'+x_axis_string+';'+y_axis_string, n_x_bins, x_min_max[0], x_min_max[1], n_y_bins, y_min_max[0], y_min_max[1])
    if(len(weight_list) == len(x_float_list)):
      for i in range( len(x_float_list) ):
        hist.Fill(x_float_list[i], y_float_list[i], weight_list[i])
    else:
      for i in range( len(x_float_list) ):
        hist.Fill(x_float_list[i], y_float_list[i])
  else:
    x_min_max = min_max(x_float_list, weight_list, margin=rg.histo_margin, xmin=xmin, xmax=xmax)
    hist = ROOT.TH1D(name_string, hist_title_string+';'+x_axis_string, n_x_bins, x_min_max[0], x_min_max[1])
    if(len(weight_list) == len(x_float_list)):
      for i in range( len(x_float_list) ):
        hist.Fill(x_float_list[i], weight_list[i])
    else:
      for i in range( len(x_float_list) ):
        hist.Fill(x_float_list[i])
  _hist_persistent.append(hist)
  hist.SetLineColor(line_color)
  hist.SetLineStyle(line_style)
  if fill_color!=None: hist.SetFillColor(fill_color)
  hist.SetStats(stats)
  return hist

def make_root_legend(canvas, root_item_list):
    """
    Build a legend for the canvas
    """
    config.has_root()
    if len(root_item_list) == 0:
        raise KeyError("No items for ROOT legend")
    canvas.cd()
    leg = ROOT.TLegend()
    for index, leg in enumerate(root_item_list):
        leg_min =  0.89-0.08*len(root_item_list)
    if leg_min < 0.1:
        leg_min = 0.1
    leg = ROOT.TLegend(0.0, leg_min, 0.4, 0.90) # pylint: disable=E1101
    leg.SetEntrySeparation(0.6)
    for i, hist in enumerate(root_item_list):
        leg.AddEntry(hist, root_item_list[i].GetName())
    leg.SetFillColor(10)
    leg.SetBorderSize(0)
    leg.Draw()
    canvas.Update()
    _legend_persistent.append(leg)
    return leg


#def make_root_graph_2d(name_string, x_float_list, x_axis_string, y_float_list, y_axis_string, z_float_list, z_axis_string, sort=True, xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,
#                  line_color=rg.line_color, line_style=rg.line_style, line_width=rg.line_width, fill_color=rg.graph_fill_color, hist_title_string=''):
#  """
#  Make a root graph with data taken from float lists and axes named after the axis strings. Return value is a tuple of (hist, graph)
#    name_string   = name given to the histogram
#    x_float_list  = list of x-data
#    x_axis_string = string used to label the x-axis
#    y_float_list  = list of y-data
#    y_axis_string = string used to label the y-axis
#    z_float_list  = list of z-data
#    z_axis_string = string used to label the z-axis
#    sort          = boolean - set to true to automatically sort input data
#    xmin          = float that overrides auto-detection of minimum x-axis value
#    xmax          = float that overrides auto-detection of maximum x-axis value
#    ymin          = float that overrides auto-detection of minimum y-axis value
#    ymax          = float that overrides auto-detection of maximum y-axis value
#    zmin          = float that overrides auto-detection of minimum z-axis value
#    zmax          = float that overrides auto-detection of maximum z-axis value
#    line_color    = int that sets the line colour of the graph
#    line_style    = int that sets the line style of the graph
#    line_width    = int that sets the line width of the graph
#    fill_color    = graphs dont usually get a fill, but sometimes the fill colour turns up in e.g. legend drawing
#    hist_title_string    = specify the string that will appear as a title
#  Return value is a tuple of (histogram, graph, graph_2) where graph is the TGraph2D and graph_2 is a graph of x vs y
#  """
#  has_root()
#  if(len(x_float_list) == 0 or len(x_float_list) != len(y_float_list) or len(x_float_list) != len(z_float_list)):
#    raise IndexError('Attempt to draw graph with no x-points, or different number of x to y to z points.')
#  multilist = [x_float_list, y_float_list, z_float_list]
#  if sort: multisort(multilist)
#  x_min_max = min_max(multilist[0], margin=rg.graph_margin, xmin=xmin, xmax=xmax)
#  y_min_max = min_max(multilist[1], margin=rg.graph_margin, xmin=ymin, xmax=ymax)
#  z_min_max = min_max(multilist[1], margin=rg.graph_margin, xmin=zmin, xmax=zmax)
#  hist  = make_root_histogram(name_string, [], x_axis_string, 1000, [], y_axis_string, 1000, [], x_min_max[0], x_min_max[1], y_min_max[0], y_min_max[1], 
#                    line_color=rg.line_color, line_style=rg.line_style, line_width=0, fill_color=None, stats=False, hist_title_string=hist_title_string)
#  hist.SetMinimum(z_min_max[0])
#  hist.SetMaximum(z_min_max[1])
#  graph = ROOT.TGraph2D(len(x_float_list))
#  graph.SetTitle(name_string)
#  graph.SetName(name_string)
#  graph.SetHistogram(hist)
#  graph_2 = ROOT.TGraph(len(x_float_list))
#  for i in range(len(x_float_list)):
#    graph.SetPoint(i, x_float_list[i], y_float_list[i], z_float_list[i])
#    graph_2.SetPoint(i, x_float_list[i], y_float_list[i])
#  _graph_persistent.append(graph)
#  _graph_persistent.append(graph_2)
#  return (hist, graph, graph_2)


def make_matplot_histogram(x_float_list, x_axis_string, n_x_bins, y_float_list=[], y_axis_string='', n_y_bins=0, weight_list=[]):
  """
  Make a matplot graph with data taken from float lists and axes naemd after the axis strings. Return value is a tuple of (hist, graph)
  matplot can format using tex expressions - use '$some math expression$' to include math text in your labels

  - x_float_list  = list of x-data
  - x_axis_string = string used to label the x-axis
  - y_float_list  = list of y-data
  - y_axis_string = string used to label the y-axis

  After building the graph, use matplotlib.pyplot.show() to show something on the screen
  """
  config.has_matplot()
  config.has_numpy()
  global _figure_index
  pyplot.figure(_figure_index)
  _figure_index += 1
  if(len(x_float_list) == 0):
    raise IndexError('Attempt to draw histogram with no x-points')
  if not len(y_float_list) == len(x_float_list):
#    x_min_max = min_max(x_float_list, weight_list, margin=histo_margin)
#    my_bins = range(int(n_x_bins))
#    for i in range(len(my_bins)): my_bins[i] = x_min_max[0]+float(i)*(x_min_max[1]-x_min_max[0])/float(len(my_bins))
    if(weight_list == []):
      (n, my_bins) = numpy.histogram(a=x_float_list, bins=n_x_bins)
    else:
      (n, my_bins) = numpy.histogram(a=x_float_list, bins=n_x_bins, weights=weight_list)
    new_bins  = []
    new_n     = []
    index     = 0
    while(abs(n[index])<1.e-9 and index < len(n)): index += 1
    for i in range(index, len(n)-1):
      new_bins.append((my_bins[i] + my_bins[i+1])/2.)
      new_n.append(n[i])
    hist = pyplot.plot(new_bins, new_n)
    pyplot.xlabel(x_axis_string)
  else:
    if len(weight_list) == len(x_float_list): hist = pyplot.hexbin(x_float_list, y_float_list, weight_list, gridsize=(n_x_bins,n_y_bins))
    else:                                     hist = pyplot.hexbin(x_float_list, y_float_list, gridsize=(n_x_bins,n_y_bins))
    pyplot.xlabel(x_axis_string)
    pyplot.ylabel(y_axis_string)
  return hist

def make_root_graph(name_string, x_float_list, x_axis_string, y_float_list, y_axis_string, sort=True, xmin=None, xmax=None, ymin=None, ymax=None, 
                    line_color=rg.line_color, line_style=rg.line_style, line_width=rg.line_width, fill_color=rg.graph_fill_color, hist_title_string=''):
  """
  Make a root graph with data taken from float lists and axes named after the axis strings. Return value is a tuple of (hist, graph)

  - name_string   = name given to the histogram
  - x_float_list  = list of x-data
  - x_axis_string = string used to label the x-axis
  - y_float_list  = list of y-data
  - y_axis_string = string used to label the y-axis
  - sort          = boolean - set to true to automatically sort input data
  - xmin          = float that overrides auto-detection of minimum x-axis value
  - xmax          = float that overrides auto-detection of maximum x-axis value
  - ymin          = float that overrides auto-detection of minimum y-axis value
  - ymax          = float that overrides auto-detection of maximum y-axis value
  - line_color    = int that sets the line colour of the graph
  - line_style    = int that sets the line style of the graph
  - line_width    = int that sets the line width of the graph
  - fill_color    = graphs dont usually get a fill, but sometimes the fill colour turns up in e.g. legend drawing
  - hist_title_string    = specify the string that will appear as a title

  Return value is a tuple of (histogram, graph)
  """
  config.has_root()
  x_float_list = copy.deepcopy(x_float_list)
  y_float_list = copy.deepcopy(y_float_list)
  if(len(x_float_list) == 0 or len(x_float_list) != len(y_float_list)):
    raise IndexError('Attempt to draw graph with no x-points, or different number of x to y points')
#  name_string += " "+str(len(_hist_persistent))
  multilist = [x_float_list, y_float_list]
  if sort: multisort(multilist)
  x_min_max = min_max(multilist[0], margin=rg.graph_margin, xmin=xmin, xmax=xmax)
  y_min_max = min_max(multilist[1], margin=rg.graph_margin, xmin=ymin, xmax=ymax)
  hist  = make_root_histogram(name_string, [], x_axis_string, 1000, [], y_axis_string, 1000, [], x_min_max[0], x_min_max[1], y_min_max[0], y_min_max[1], 
                    line_color=rg.line_color, line_style=rg.line_style, line_width=0, fill_color=None, stats=False, hist_title_string=hist_title_string)
  graph = ROOT.TGraph(len(x_float_list))
  graph.SetTitle(name_string)
  graph.SetName(name_string)
  graph.SetLineColor(line_color)
  graph.SetLineStyle(line_style)
  graph.SetLineWidth(line_width)
  graph.SetFillColor(fill_color)
  for i in range(len(x_float_list)):
    graph.SetPoint(i, x_float_list[i], y_float_list[i])
  _graph_persistent.append(graph)
  return (hist, graph)
  
def make_matplot_graph(x_float_list, x_axis_string, y_float_list, y_axis_string, sort=True):
  """
  Make a matplot graph with data taken from float lists and axes naemd after the axis strings. Return value is a tuple of (hist, graph)
  matplot can format using tex expressions - use '$some math expression$' to include math text in your labels

  - x_float_list  = list of x-data
  - x_axis_string = string used to label the x-axis
  - y_float_list  = list of y-data
  - y_axis_string = string used to label the y-axis
  - sort          = boolean - set to true to automatically sort input data

  After building the graph, use matplotlib.pyplot.show() to show something on the screen
  """
  config.has_matplot()
  global _figure_index
  pyplot.figure(_figure_index)
  _figure_index += 1
  if(len(x_float_list) == 0 or len(x_float_list) != len(y_float_list)):
    raise IndexError('Attempt to draw graph with no x-points, or different number of x to y points')
  multilist = [x_float_list, y_float_list]
  multisort(multilist)
  x_min_max = min_max(multilist[0], margin=rg.graph_margin)
  y_min_max = min_max(multilist[1], margin=rg.graph_margin)
  myplot = pyplot.plot(x_float_list, y_float_list)
  pyplot.xlabel(x_axis_string)
  pyplot.ylabel(y_axis_string)
  pyplot.xlim  (x_min_max[0], x_min_max[1])
  pyplot.ylim  (y_min_max[0], y_min_max[1])
  matplotlib.pyplot.draw()

def make_root_multigraph(name_string, x_float_list_of_lists, x_axis_string, y_float_list_of_lists, y_axis_string):
  """
  Print several different graphs on the same canvas. Some default colour scheme is applied, but it may not be the best...

  - name_string  = name that will be given to the axes (histogram)
  - x_float_list_of_lists = list of lists. Each list will be used as the x-axis for a graph
  - x_axis_string         = string that will be used to label the x_axis
  - y_float_list_of_lists = list of lists. Each list will be used as the y-axis for a graph
  - y_axis_string         = string that will be used to label the y_axis

  E.g. common.make_root_multigraph('example', [[1.,2.,3.,4.], [1.,4.,9.,16.]], 'x', [[1.,2.,3.,4.],[1.,2.,3.,4.]], 'f(x)') will make a graph of f = x and  f = x^0.5
  """
  config.has_root()
  name_string += " "+str(len(_hist_persistent))
  total_x_list  = []
  total_y_list  = []
  for a_list in x_float_list_of_lists:  total_x_list += a_list
  for a_list in y_float_list_of_lists:  total_y_list += a_list
  x_min_max = min_max(total_x_list, margin=rg.graph_margin)
  y_min_max = min_max(total_y_list, margin=rg.graph_margin)
  hist   = ROOT.TH2D(name_string, ';'+x_axis_string+';'+y_axis_string, 1000, x_min_max[0], x_min_max[1], 1000, y_min_max[0], y_min_max[1])
  graphs = []
  for index in range( len(x_float_list_of_lists) ):
    graphs.append(ROOT.TGraph( len(x_float_list_of_lists[index]) ))
    ROOT.gStyle.SetPalette(int(len(x_float_list_of_lists)*1.25))
    graphs[-1].SetLineColor(ROOT.gStyle.GetColorPalette(index + int(len(x_float_list_of_lists)*0.25) )) #funny algebra to darken the colors slightly
    for i in range(len(x_float_list_of_lists[index])):
      graphs[-1].SetPoint(i, x_float_list_of_lists[index][i], y_float_list_of_lists[index][i])
    _graph_persistent.append(graphs[-1])
  _hist_persistent.append(hist)
  hist.SetStats(False)
  return (hist, graphs)

def make_matplot_multigraph(x_float_list_of_lists, x_axis_string, y_float_list_of_lists, y_axis_string):
  """
  Print several different graphs on the same axes. Some default colour scheme is applied, but it may not be the best...

  - x_float_list_of_lists = list of lists. Each list will be used as the x-axis for a graph
  - x_axis_string         = string that will be used to label the x_axis
  - y_float_list_of_lists = list of lists. Each list will be used as the y-axis for a graph
  - y_axis_string         = string that will be used to label the y_axis

  E.g. common.make_matplot_multigraph('example', [[1.,2.,3.,4.], [1.,4.,9.,16.]], 'x', [[1.,2.,3.,4.],[1.,2.,3.,4.]], 'f(x)') will make a graph of f = x and  f = x^0.5
  """
  config.has_matplot()
  global _figure_index
  pyplot.figure(_figure_index)
  _figure_index += 1
  total_x_list  = []
  total_y_list  = []
  for a_list in x_float_list_of_lists:  total_x_list += a_list
  for a_list in y_float_list_of_lists:  total_y_list += a_list
  x_min_max = min_max(total_x_list, margin=rg.graph_margin)
  y_min_max = min_max(total_y_list, margin=rg.graph_margin)
  for index in range( len(x_float_list_of_lists) ):
    multilist = [x_float_list_of_lists[index], y_float_list_of_lists[index]]
    multisort(multilist)
    myplot = pyplot.plot(multilist[0], multilist[1])
  pyplot.xlabel(x_axis_string)
  pyplot.ylabel(y_axis_string)
  pyplot.xlim  (x_min_max[0], x_min_max[1])
  pyplot.ylim  (y_min_max[0], y_min_max[1])
  matplotlib.pyplot.draw()

def make_matplot_scatter(x_float_list, x_axis_string, y_float_list, y_axis_string):
  """
  Make a matplot scatter graph with data taken from float lists and axes naemd after the axis strings.
  matplot can format using tex expressions - use '$some math expression$' to include math text in your labels

  - x_float_list  = list of x-data
  - x_axis_string = string used to label the x-axis
  - y_float_list  = list of y-data
  - y_axis_string = string used to label the y-axis

  After building the graph, use matplotlib.pyplot.show() to show something on the screen
  """
  config.has_matplot()
  global _figure_index
  pyplot.figure(_figure_index)
  _figure_index += 1
  if(len(x_float_list) == 0):
    raise IndexError('Attempt to draw histogram with no x-points')
  hist = pyplot.scatter(x_float_list, y_float_list, s=1)
  pyplot.xlabel(x_axis_string)
  pyplot.ylabel(x_axis_string)
  return hist

def wait_for_root():
  """
  Force python to halt processing until ROOT windows are closed
  """
  print('Close ROOT windows to continue')
  root_done = False
  while not root_done:
      root_done = True
      for canvas in _canvas_persistent:
          if not canvas == None:
              print(canvas)
              root_done = False
      time.sleep(0.01)

def clear_root():
  """
  Close root plots (and free memory)
  """
  global _canvas_persistent, _hist_persistent, _graph_persistent
  for canv  in _canvas_persistent: del(canv)
  for hist  in _hist_persistent:   del(hist)
  for graph in _graph_persistent:  del(graph)
  _canvas_persistent = []
  _hist_persistent = []
  _canvas_persistent = []

def wait_for_matplot():
  """Show any plots made using matplotlib on the screen"""
  config.has_matplot()
  matplotlib.pyplot.show()

def matplot_show_and_continue():
  """Show matplotlib plots and return to the script"""
  config.has_matplot()
  try:
    subprocess( matplotlib.pyplot.show, () )
  except:
    raise ImportError('matplot_show_and_continue is only available is (i) ROOT is not installed or (ii) you have python > 2.6')
    
__mp_subprocesses = []
__fk_subprocesses = []
def subprocess(function, args):
  """
  Make a function call in  a subprocess; return the subprocess pid
  - This uses the multiprocessing libary in the first instance - if multiprocessing is not available
    the function tries to use os.fork(); however, os.fork is not compatible with ROOT. If
  - multiprocessing is not available and ROOT is installed, this routine will throw an ImportError
  """
  try: 
    config.has_multiprocessing()
    __mp_subprocesses.append( multiprocessing.Process(target=function, args=args) )
    __mp_subprocesses[-1].start()
    return __mp_subprocesses[-1]
  except:
    try: 
      config.has_root()
      raise ImportError('Error - attempt to make a subprocess using fork when ROOT library is active')
    except ImportError:
      pid = os.fork()
      if pid == 0:
        try:    function(*args)
        except: os._exit(1)
        os._exit(0)
      else:
        __fk_subprocesses.append(pid)
        return pid
 
def kill_all_subprocesses():
  """
  Kill all subprocesses generated by common.subprocess call; automatically called at exit unless kill_subprocesses_at_exit is set to False
  Note that this makes a call to the os, which may take a bit of time to respond.
  """
  for ps in __mp_subprocesses:
    ps.terminate()
    time.sleep(0.01) #dont ask me why this is necessary...
  for pid in __fk_subprocesses:
    os.kill(pid, signal.SIGKILL)

def kolmogorov_smirnov_test(list_1, list_2):
  """
  Convenience wrapper for ROOT kolmogorov-smirnov test.
  - list_1 = list of floats that are sampled from some parent probability distribution
  - list_2 = list of floats that are sampled from other some parent distribution
  Returns double between 0. and 1. giving probability that list_1 and list_2 have the same parent distribution.
  """
  list_1 = sorted(list_1)
  list_2 = sorted(list_2)
  c_array_1 = ctypes.c_double*len(list_1)
  c_array_2 = ctypes.c_double*len(list_2)
  ca1 = c_array_1()
  ca2 = c_array_2()
  for i in range(len(list_1)): ca1[i]=ctypes.c_double(list_1[i])
  for i in range(len(list_2)): ca2[i]=ctypes.c_double(list_2[i])
  ks = ROOT.TMath.KolmogorovTest(len(list_1), ca1, len(list_2), ca2, '')
  return ks

def __atexit():
  """Calls some functions automatically at exit"""
  if(kill_subprocesses_at_exit):
    kill_all_subprocesses()
atexit.register(__atexit)


def make_grid(n_dimensions, n_per_dimension):
  """
  Make a rectangular n_dimensional grid of points evenly spaced between [-1,1] in each 
  dimension

  - n_dimensions     = number of dimensions
  - n_per_dimension  = number of points in each dimension; total number of points will be
                       n_per_dimension^n_dimensions

  Return value is a list of numpy.matrices with shape (n_dimensions, 1)
  """
  config.has_numpy()
  pos_vector = [numpy.matrix( [-1.]*n_dimensions )]
  for i in range(n_dimensions):
    pos_vector_copy = copy.deepcopy(pos_vector)
    for j in range(1, n_per_dimension):
      pos = (2.*j)/float(n_per_dimension-1)-1.
      for vec in pos_vector_copy:
        vec = copy.deepcopy(vec)
        vec[0,i] = pos
        pos_vector.append(vec)
  return pos_vector

def make_shell(n_per_dimension, ellipse, mean = None):
  """
  Make a shell of points that sit on a hyper-ellipsoid defined by ellipse matrix

  - n_per_dimension  = number of points in each dimension; total number of points will be
                       n_per_dimension^n_dimensions if n_per_dimension is even or
                       n_per_dimension^n_dimensions-1 if n_per_dimension is odd
  - ellipse          = matrix that defines the ellipse on which vector sits; should be a
                       numpy.matrix with shape (vec_length, vec_length)
  - mean             = vector that defines the centroid of the shell; should be a
                       numpy.array with shape (vec_length,)

  Points are defined on a (hyper-)cuboidal grid and then compressed so that lengths are 
  all 1. Doesn't necessarily mean points are evenly spaced. Return value is a list of 
  numpy.matrices with shape (n_dimensions, 1)
  """
  config.has_numpy()
  n_dimensions = numpy.shape(ellipse)[0]
  grid         = make_grid(n_dimensions, n_per_dimension)
  print("GRID\n", grid)
  if mean.any() == None:
      mean = numpy.zeros((n_dimensions,))
  shell        = []
  ellipse_inv  = numpy.linalg.inv(ellipse)
  for vector in grid:
    # vdot requires 1d array-like for some numpy versions
    vector_test = numpy.array(vector).flatten()
    if numpy.vdot(vector_test, vector_test) > float_tolerance:
      shell.append(normalise_vector(vector, ellipse_inv)+mean)
  return shell

def normalise_vector(vector, matrix_inverse):
  """
  Normalise vector so that vector.T() * matrix.inverse * vector = 1

  - vector         = the vector to normalise; should be a numpy.matrix with shape (vec_length,1)
  - matrix_inverse = inverse of matrix that defines the ellipse on which vector sits; should be a
                     numpy.matrix with shape (vec_length, vec_length)

  Return value is a list of numpy.matrices with shape (vec_length,1)
  """
  config.has_numpy()
  scale  = 1./(vector * matrix_inverse * vector.transpose())[0,0]**0.5
  print(vector, scale, end=' ')
  if scale != scale: raise ValueError #isnan and isinf not available in 2.5
  vector = vector*scale
  print(vector, vector * matrix_inverse * vector.transpose())
  return vector

def __function_with_queue(args):
  """
  Wrapper function to put multiprocessing output into a queue

  - args tuple of (function_call, queue, function_arg) where
      - function_call is a reference to the function that we want to wrap\n
      - queue is the queue that will hold return values from the function\n
      - function_arg is the argument to function_call\n
      - index is an index indicating function_arg's position in the inputs

  tuple of (index, Output) is placed into queue; if function_call throws an
  exception, the exception is placed on the queue instead
  """
  (function_call, queue, function_arg, index) = args
  try:
    queue.put((index, function_call(*function_arg)))
  except:
    queue.put((index, sys.exc_info()[1]))

def process_list(function_call, list_of_args, max_n_processes):
  """
  Run multiprocessing on a list of arguments

  - function_call multiprocess this function call
  - list_of_args list of tuples of arguments for function_call
  - max_n_processes maximum number of concurrent processes to use

  Returns list of return values, one for each function call. List is always
           sorted into same order as input.

  e.g. process_list(time.sleep, [(3, ), (6, ), (2, )], 2) will multiprocess
  the time.sleep function with inputs 3, 6 and 2 across 2 cores and return 
  list like [None, None, None].
  """
  manager = multiprocessing.Manager()
  queue = manager.Queue() # queue stores return values
  pool = multiprocessing.Pool(max_n_processes) # pool runs multiprocess
  # each process needs:
  #    reference to queue to put returns values in
  #    index (to sort return values)
  #    plus function call and argument
  new_list_of_args = [(function_call, queue, x, i) for i,x in enumerate(list_of_args)]
  # run the processes
  pool.map(__function_with_queue, new_list_of_args)
  # sort output into a list
  out_list = []
  while not queue.empty():
    out_list.append(queue.get())
  out_list.sort()
  for i,item in enumerate(out_list):
    out_list[i] = item[1]
  # cleanup
  pool.close()
  return out_list

def _sum_weight(weights, in_cut):
  n_points = len(in_cut)
  return sum([weights[i] for i in range(n_points) if in_cut[i]])

def _get_fit_ellipse_covariance_matrix(points, weights, in_cut):
    n_points = len(points)
    sum_weight = _sum_weight(weights, in_cut)
    dimension = len(points[0])
    mean = numpy.zeros(dimension)
    cov = numpy.zeros([dimension, dimension])
    for i in range(n_points):
        if in_cut[i]:
            a_point = points[i]
            for j in range(dimension):
                mean[j] += a_point[j]/sum_weight*weights[i]
                for k in range(dimension):
                    cov[j, k] += a_point[j]*a_point[k]/sum_weight*weights[i]
    for i in range(dimension):
        for j in range(dimension):
            cov[i, j] -= mean[i]*mean[j]
    return mean, cov

def _update_fit_ellipse_cut(points, cov_inv, mean, eps_cut):
    n_points = len(points)
    n_dim = 2
    in_cut = [True for i in range(n_points)]
    sqrt_det_inv = numpy.linalg.det(cov_inv)**(1./float(n_dim))
    for i in range(n_points):
        vec = numpy.array(points[i])-mean
        vec_t = numpy.transpose(vec)
        eps = numpy.dot(vec_t, numpy.dot(cov_inv, vec))/sqrt_det_inv
        in_cut[i] = eps < eps_cut
    return in_cut

def fit_ellipse(points, eps_cut, weights=None, max_number_of_iterations = 10, verbose = True):
    """
    Fit an ellipse of arbitrary dimension n to a set of points

    - points iterable of points; each point should be an iterable of floats of
             length n
    - eps_cut float cut value; only particles with 
              eps = x^T*V^{-1}*x*|V|**{1/n} < eps_{cut}
              are considered. The cut value is a normalised chi-squared. It
              should be positive.
    - weights list of floats, one for each point; use statistically weighted
              particles for the fit. Set to None to ignore weights.
    - max_number_of_iterations integer number of iterations; the ellipse fitting
              procedure is repeated several times to attempt to improve the
              fit of the ellipse. This sets a maximum number of repetitions.
    - verbose set to True to provide some verbose output during fitting

    Returns ellipse centre vector <x> and defining matrix V. The ensemble of 
    points on the ellipse is given by (x-<x>)^T*V^{-1}*(x-<x>) where x is a
    particle vector and V is the defining matrix.
    """
    n_points = len(points)
    old_det = 1.
    mean, cov = numpy.ones([2]), numpy.ones([2, 2])
    in_cut = [True for i in range(n_points)]
    if weights == None:
        weights = [1.,]*n_points
    iterations = 0
    try:
        while abs(numpy.linalg.det(cov)-old_det) > float_tolerance and \
              iterations < max_number_of_iterations:
            iterations += 1
            my_sum = 0
            for i in in_cut:
                if i == True:
                    my_sum += 1
            old_det = numpy.linalg.det(cov)
            mean, cov = _get_fit_ellipse_covariance_matrix(points, weights, in_cut)
            mat_inv = numpy.linalg.inv(cov)
            in_cut = _update_fit_ellipse_cut(points, mat_inv, mean, eps_cut)
    except Exception:
        if verbose:
            print("xboa.common.fit_ellipse(...) failed to converge; final iteration as follows.")
            sys.excepthook(*sys.exc_info())
    if verbose:
        print('Weight in cut:\n', _sum_weight(weights, in_cut))
        print("Means:\n", mean)
        print("Ellipse:\n", cov)
        print("Number of iterations:\n", iterations)
    return mean, cov

def make_root_ellipse_function(mean, cov, contours=None, xmin=-1e3, xmax=1e3, ymin=-1e3, ymax=1e3):
    """
    Make a ROOT TFunction for a given beam ellipse

    - mean sequence type of length>=2 (must allow reference by integer [index])
    - cov ellipse >= 2x2 symmetric numpy.array (must allow referencing by integer
          indices like [a, b])
    - contours iterable; draw contours at values of x^T V^{-1} x given by 
          elements. Uses ROOT default if equal to None.

    Returns a ROOT TFunction. Note ROOT TFunction does not like drawing
    small ellipses if the ellipse matrix is highly correlated (i.e. determinant
    near zero). A workaround is to make a TGraph with appropriate points (using
    e.g. formula given by this function). May be possible to fix by increasing
    the number of points in plot (func.SetNpy).
    """
    config.has_root()
    mat_inv = numpy.linalg.inv(cov)
    fit_func_str = "[2]*(x-[0])**2+[4]*(y-[1])**2+2*[3]*(x-[0])*(y-[1])"
    fit_func = ROOT.TF2("ellipse", fit_func_str)
    if contours != None:
        fit_func.SetContour(len(contours))        
        for i, contour in enumerate(contours):
            fit_func.SetContourLevel(i, contour)       
    if xmax == None or xmin == None or ymax == None or ymin == None:
        xmin = -1e3+mean[0]
        xmax = 1e3+mean[0]
        ymin = -1e3+mean[1]
        ymax = 1e3+mean[1]
       
    fit_func.SetRange(xmin, ymin, xmax, ymax)
    fit_func.SetParameter(0, mean[0])
    fit_func.SetParameter(1, mean[1])
    fit_func.SetParameter(2, mat_inv[0, 0])
    fit_func.SetParameter(3, mat_inv[0, 1])
    fit_func.SetParameter(4, mat_inv[1, 1])
    fit_func.SetLineColor(rg.fit_color)
    fit_func.SetLineStyle(rg.fit_style)
    _function_persistent.append(fit_func)
    return fit_func


def common_overview_doc(verbose = False):
  """Creates some summary documentation for the common module. If verbose is True then will also print any functions or data not included in summary"""
  common_doc = '\cCommon module contains a number of useful interfaces, defaults, data and ancillary functions that support the rest of the XBOA package.\n' 

  name_list = ['math', 'root', 'matplot', 'data', 'defaults', 'other_stuff']
  function_list = {
  'math'        : ['min_max', 'multisort', 'nd_newton_raphson1', 'nd_newton_raphson2'],
  'root'        : ['make_root_graph', 'make_root_histogram', 'make_root_multigraph', 'clear_root',  'wait_for_root', 'make_root_canvas'],
  'matplot'     : ['make_matplot_graph', 'make_matplot_histogram', 'make_matplot_multigraph', 'make_matplot_scatter', 'wait_for_matplot', 'matplot_show_and_continue'],
  'other_stuff' : ['get_bin_edges', 'histogram', 'substitute', 'build_installation', 'make_grid', 'make_shell', 'normalise_vector', 'kolmogorov_smirnov_test', 'kill_all_subprocesses'],
  'data'        : ['constants', 'pdg_pid_to_icool', 'pdg_pid_to_mars', 'pdg_pid_to_mass', 'pdg_pid_to_name', 'pdg_pid_to_charge', 'icool_pid_to_pdg', 'mars_pid_to_pdg', 'units'],
  'defaults'    : ['canvas_fill_color', 'canvas_highlight_color', 'default_margin', 'float_tolerance', 'graph_margin', 'histo_margin', 'python_version', 'xboa_version', 'kill_subprocesses_at_exit']
  }

  function_doc = {
  'math'        : 'Maths functions:',
  'root'        : 'Interfaces to ROOT plotting library:',
  'matplot'     : 'Interfaces to matplotlib plotting library:',
  'other_stuff' : 'Some other useful functions:',
  'data'        : 'Physics data:',
  'defaults'    : 'Defaults for e.g. root canvases, etc:',
  }

  if verbose:
    dir_common = dir(sys.modules[__name__])
    print('The following functions and data are in common but not in common_overview_doc:')
    for func in dir_common:
      found = False
      for func_sublist in list(function_list.values()):
        if func in func_sublist: found = True
      if not found: print(func, end=' ')
    print('\n')

    print('The following functions and data are in common_overview_doc but not in Common:')
    for func_sublist in list(function_list.values()):
      for func in func_sublist:
        if func not in dir_common:
          print(func, end=' ')
    print()

  doc = common_doc    
  for key in name_list:
    doc = doc + function_doc[key]+'\n'
    for item in function_list[key]:
      doc = doc+'  '+item+'\n'
  return doc

__doc__ = common_overview_doc()


