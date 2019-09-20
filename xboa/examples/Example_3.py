"""
\namespace xboa::examples::Example_3

Example code to read a file, make some cuts and then plot

\include xboa/examples/Example_3.py
"""

#############
# EXAMPLE 3 #
# CUTS      #
#############
#
# Load a data file; make some cuts; make some plots
# For this example, I require the ROOT library or matplotlib library
#

import xboa.hit
from xboa.hit import Hit
import xboa.bunch
from xboa.bunch import Bunch

import operator
import sys

print '========= XBOA example 3 ========='

#load data file
print "This example shows how to make cuts"
print "Loading file... "
bunch_list = Bunch.new_list_from_read_builtin('icool_for009', sys.prefix+'/share/xboa/data/for009.dat')
print "Loaded"

#make px histogram
bunch_list[0].root_histogram('px', 'MeV/c')
#throw away particles with px > 30 MeV/c OR < -30 MeV/c
#here, operator.ge is a function that returns TRUE if x1 >= x2
#so throw away particles with operator.ge(value, test) is TRUE
bunch_list[0].cut({'px':30.},  operator.ge)
#now use operator.le, which is a function that returns TRUE if x1 <= x2 
bunch_list[0].cut({'px':-30.}, operator.le)
#make px histogram again; note that axis range is modified to fit values of the data
bunch_list[0].root_histogram('px','MeV/c')

#reset all weights to one
#note that if you loaded a file with some weights in, these will be cleared
bunch_list[0].clear_weights()
#cut on transverse amplitude (in 4d x-y phase space)
#note global_cut=True => I make the cut for all bunches (based on event_number)
bunch_list[0].cut({'amplitude x y':30.}, operator.ge, global_cut=True)
n_stations = len(bunch_list)
#plot transverse amplitude
#note that the plot doesn't quite stop at 30 mm; this is because the 
#amplitudes have been recalculated with the new distribution and have
#moved slightly
bunch_list[0].root_histogram('amplitude x y','mm')

#plot transverse amplitude at a few points in the linac; look to see how much the amplitude blurs
bunch_list[n_stations/3].root_histogram('amplitude x y','mm')
bunch_list[2*n_stations/3].root_histogram('amplitude x y','mm')
bunch_list[-1].root_histogram('amplitude x y','mm')

#clear weights
for bunch in bunch_list:
  bunch.clear_weights()

#plot transmission
Bunch.root_graph(bunch_list, 'mean', ['z'], 'bunch_weight', '')

#cut on transmission in middle plane
#looks through all particles in bunch_list[0]; if it can't find the event_number in
#bunch_list[-1], set weight to 0
bunch_list[0].transmission_cut(bunch_list[-1], global_cut=True)
#plot transmission
Bunch.root_graph(bunch_list, 'mean', ['z'], 'bunch_weight', '')

#now wait for user to review plots before ending
print 'Press <return> key to finish'
raw_input()
Bunch.clear_global_weights()

