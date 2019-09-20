"""
\namespace xboa::examples::Example_1

Example code to read a file and perform some data access operations

\include xboa/examples/Example_1.py
"""
###############
# EXAMPLE 1   #
# FILE IO     #
# DATA ACCESS #
###############
#
# Load a data file; print some data stuff
#

#try to import the XBOA library - if this fails, review the installation procedure
from xboa  import *
from xboa.hit   import Hit
from xboa.bunch import Bunch
import sys


print '========= XBOA example 1 ========='
print "In this example, I will do some basic file i/o and data manipulation"
#input data
#by default this is installed at file_location
filename = sys.prefix+'/share/xboa/data/for009.dat'
filetype = "icool_for009" #some other options are "maus_root_virtual_hit", (requires libMausCpp.so in python path), "icool_for003", "g4blTrackFile", ...

#try to load an input file
#this will load the for009 file, and make a list of "bunches", one for each region
#a list is a python version of an array
print "Data can be loaded using new_list_from_read_builtin(filetype, filename) for builtin types"
print 'List of builtin types:'
print Hit.file_types()
print 'For non-builtin types, you would use new_from_read_user(format_list, format_units_dict, filehandle, number_of_skip_lines)'
print 'I\'ll try to load some example data that came with your installation...'
try:
  bunch_list = Bunch.new_list_from_read_builtin(filetype, filename)
except IOError:
  'Oh dear, I couldn\'t load the example data - I wonder if it was installed in the default place ('+filename+')?\nTry inputting a new location:'
  filename = raw_input()
  bunch_list = Bunch.new_list_from_read_builtin(filetype, filename)
  print "Loaded"

print '\n====== HIT ======'
print 'A hit is the intersection of a particle trajectory with a detector or output plane'
my_hit = bunch_list[0][10]
print 'Normally you would access hit data using my_hit[get_variable], for example'
print 'my_hit[\'x\']: ',my_hit['x']
print 'my_hit[\'px\'] (x component of momentum vector):',my_hit['px']
print 'my_hit[\'l_kin\'] (kinetic angular momentum):',my_hit['l_kin']
print 'Possible get_variables are:'
print my_hit.get_variables()
print 't is time, r is radius, x\' is dx/dz, bx is magnetic field in x direction, ex is electric field in x direction'
print 'You can modify data in a hit in the way you would expect, i.e. my_hit[\'px\'] = 1.'
my_hit['px'] = 1.
print 'my_hit[\'px\']: ',my_hit['px'],'\n'
print 'If you change the momentum, you will need to readjust the hit to make sure that it obeys E^2 = p^2 + m^2'
print 'Do this using mass_shell_condition(some_variable), e.g. my_hit.mass_shell_condition(\'energy\')'
print '(px,py,pz),energy,mass,E^2-p^2 before:\n',(my_hit['px'],my_hit['py'],my_hit['pz']),my_hit['energy'],my_hit['mass'],(my_hit['energy']**2-my_hit['p']**2)**0.5
my_hit.mass_shell_condition('energy')
print '(px,py,pz),energy,mass,E^2-p^2 after:\n',(my_hit['px'],my_hit['py'],my_hit['pz']),my_hit['energy'],my_hit['mass'],(my_hit['energy']**2-my_hit['p']**2)**0.5

print '\n====== BUNCH ======'
print 'A bunch is a collection of individual hits'
my_bunch = bunch_list[0]
print 'Here\'s some example data that can be calculated by Bunch'
print 'Number of hits in bunch:     ',len(my_bunch)
print 'Statistical weight of bunch: ',my_bunch.bunch_weight()
print 'mean (x,px):                 ',my_bunch.mean(['x','px'])
print 'standard deviation in x      ',my_bunch.moment(['x','x'])**0.5
print 'Twiss beta_x                 ',my_bunch.get_beta(['x'])
print 'x emittance                  ',my_bunch.get_emittance(['x'])
print 'x-y emittance                ',my_bunch.get_emittance(['x','y']),'  (for coupled systems e.g. solenoids)'
print 'x-px covariance matrix       ',my_bunch.covariance_matrix(['x','px'])
print 'Another way of accessing the same data is using the get(variable, axes) function:'
print 'my_bunch.get(\'gamma\', [\'x\',\'y\'])    ',my_bunch.get('gamma',['x','y']),'   (Penn gamma for coupled systems)'
print 'Possible data types:\n',my_bunch.get_variables()
print 'Possible axes:\n',my_bunch.get_axes()
print 'To loop over e.g. the first 10 hits in a bunch, do something like \nfor hit in my_bunch[0:10]:\n  print hit[\'event_number\'],'
for hit in my_bunch[0:10]:
  print hit['event_number'],
print '\nTo loop over all hits in a bunch, do something like \nfor hit in my_bunch:\n  print hit[\'event_number\'],'

print '\nThere\'s lots more out there... to get documentation on a module, try using inline help. So on the python command line, do something like\n  import xboa.Hit\n  help(xboa.Hit)\n'



#now wait for user to review plots before ending
print 'Press <return> key to finish'
raw_input()





