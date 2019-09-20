"""
\namespace xboa::examples::Example_2

Example code to read a file and make some plots

\include xboa/examples/Example_2.py
"""

#############
# EXAMPLE 2 #
# PLOTTING  #
#############
#
# Load a data file; make some plots
#

#try to import the XBOA library - if this fails, review the installation procedure
from xboa  import *
from xboa.hit   import Hit
from xboa.bunch import Bunch
import xboa.common as common
import xboa.common.config as config
import sys

#some input data
filename = sys.prefix+'/share/xboa/data/for009.dat'
filetype = "icool_for009" #some other options are "g4mice_virtual_hit", "icool_for003", "g4mice_special_hit"

print '========= XBOA example 2 ========='

#try to load an input file
#this will load the for009 file, and make a list of "bunches", one for each region
#a list is a python version of an array
print "This example shows how to make plots\nYou will need to have access to either ROOT library or the matplotlib library to make plots"
print "First loading the data... "
bunch_list = Bunch.new_list_from_read_builtin(filetype, filename)
print "Loaded"

#make some plots
#first try to make plots with ROOT if PyROOT exists
try:
  print 'Trying to make some plots using PyROOT plotting package'
  config.has_root() #check for PyRoot library
  #momentum distribution at start and end
  bunch_list[0] .root_histogram('p', 'MeV/c')
  bunch_list[-1].root_histogram('p', 'MeV/c')

  #energy-time scatter plot at start
  bunch_list[0].root_scatter_graph('t', 'energy', 'ns', 'MeV/c')

  #histogram at start; note that in the first instance it *looks* like a scatter plot
  #but it is not; hence I draw the same histogram twice, once as a pseudo-scatter
  #and once as a contour plot
  bunch_list[0].root_histogram('t', 'ns', 'energy', 'MeV/c')
  (canvas, hist) = bunch_list[0] .root_histogram('t', 'ns', 'energy', 'MeV/c')
  hist.Draw('CONT')
  canvas.Update()

  #evolution of RMS emittance in x along the beamline
  Bunch.root_graph(bunch_list, 'mean', ['z'], 'emittance', ['x'],     'm', 'mm')
  Bunch.root_graph(bunch_list, 'mean', ['z'], 'emittance', ['x','y'], 'm', 'mm')
except ImportError:
  print "PyROOT not detected - skipping PyROOT graphics"
  
#now try to make plots with matplotlib if matplotlib exists
try:
  print 'Trying to make some plots using matplotlib plotting package'
  config.has_matplot() #check for matplot library
  #momentum distribution at start and end
  bunch_list[0] .matplot_histogram('p', 'MeV/c')
  bunch_list[-1].matplot_histogram('p', 'MeV/c')

  #energy-time scatter plot at start
  bunch_list[0].matplot_scatter_graph('t', 'energy', 'ns', 'MeV/c')

  #histogram at start; note that in the first instance it *looks* like a scatter plot
  #but it is not; hence I draw the same histogram twice, once as a pseudo-scatter
  #and once as a contour plot
  bunch_list[0].matplot_histogram('t', 'ns', 'energy', 'MeV/c')

  #evolution of RMS emittance in x along the beamline
  Bunch.matplot_graph(bunch_list, 'mean', ['z'], 'emittance', ['x'],     'm', 'mm')
  Bunch.matplot_graph(bunch_list, 'mean', ['z'], 'emittance', ['x','y'], 'm', 'mm')

  try:
    common.show_matplot_and_continue()
  except: #bug - if you have PyROOT and use python < 2.6, show_matplot_and_continue() fails
    pass # give up on matplot
except ImportError:
  print "Matplotlib not detected - skipping matplotlib graphics"


#now wait for user to review plots before ending
print 'Press <return> key to finish'
raw_input()





