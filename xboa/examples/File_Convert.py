#!/usr/bin/python
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
Set of algorithms for transforming between different file formats and bunch structures. Reads in input command file, by default file_convert.inp, and uses information to read beam in a user specified file format and output in a different user specified file format. Command line options are:
  -c=<filename>   <filename> is the input control file (default is 'file_convert.inp')
e.g. ./File_Convert.py -c=my_control_data.inp

Input file cav contain the following control variables and data, one on each line. Hash (#) or exclamation mark (!) symbols are comments.

Mandatory data to control input and output formats:
    file_in    <filename>
    format_in  <format_string>
    file_out   <filename>
    format_out <format_string>

The rest of the control variables are optional:
If you need to define a station or region from the input file:
    station_in <value>
Otherwise the routine will add all stations/regions to the output

To perform a transformation in phase space, about some origin, to a desired covariance matrix:
    rotate     <variable1> <variable2> ... one label for each axis in the rotation
    origin     <variable1> <value>
    origin     <variable2> <value>
    ...
    covariance <variable1> <variable2> <value>
If not defined, values default to 0. The covariance matrix should be symmetric and positive definite. The rotation will be scaled such that emittance is conserved. If called as a python script, this function requires a correct installation of NumPy on the user's PC

To perform a translation in phase space:
    translate <variable1> <value1> <variable2> <value2> ... one variable/value pair for each variable to be translated

To enforce E^2 + p^2 = m^2:
    mass_shell_condition <momentum_variable>
<momentum_variable> should be one of energy, p, px, py, pz. This is the variable that is changed to maintain the mass shell condition

To make 1d histograms or 2d scatter plots of either input or output data:
    plot_format <format> (default is png)
    scatter_in     <x-axis_variable> <x-units> <y-axis_variable> <y-units>
    ... one line for each histogram
    scatter_out    <x-axis_variable> <x-units> <y-axis_variable> <y-units>
    ... one line for each histogram
    histogram_in     <x-axis_variable> <x-units>
    ... one line for each histogram
    histogram_out     <x-axis_variable> <x-units>
    ... one line for each histogram
You can do as many of these as you like. If called as python script, this function requires a correct PyRoot installation on the user's PC

The routine goes like:
(i)   read input data
(ii)  make input plots
(iii) apply rotation
(iv)  apply translation
(v)   make output plots
(vi)  write output data

Possible formats are:
    icool_for009
    icool_for003
    g4beamline_bl_track_file
    g4mice_special_hit

Possible variables are:
    local_weight
    energy
    pid
    ey
    ex
    ez
    pz
    px
    py
    station
    status
    proper_time
    path_length
    sx
    bx
    by
    bz
    sz
    sy
    particleNumber
    eventNumber
    mass
    t
    y
    x
    z
    x'
    y'
    p
    global_weight
    t'

Possible units are:
    GeV
    cm
    GeV/c2
    GeV/c
    MeV
    GHz
    GV/m
    mus
    Gauss
    mum
    ns
    GV
    degree
    MeV/c2
    mT
    echarge
    T
    kT
    coulomb
    mm
    m
    radians
    km
    s
    MV
    MHz
    GV/mm
    MeV/c

Obviously feel free to take this python script as a basis to hack with...
"""

try:
  import common
  import hit
  from hit import Hit
  import bunch
  from bunch import Bunch
except ImportError:
  print 'Error during x-boa import. Check your x-boa installation is in the PYTHONPATH environment variable'
  raise ImportError

try:
  import sys
  import copy
  import operator
  import math
  import string
except ImportError:
  print 'Error during python import. Check your python installation.'
  raise ImportError

debug    = False #Set to true for full error output

def file_convert(control_file):
  lines = read_control(control_file)
  bunch = read_input(lines)
  plots(lines, bunch, True)
  rotate(lines, bunch)
  translate(lines, bunch)
  mass_shell_condition(lines, bunch)
  plots(lines, bunch, False)
  write_output(lines, bunch)

def read_control(filename):
  fh    = open(filename)
  lines = fh.readlines()
  lines_read = []
  for i in range( len(lines) ): #strip comments then split into words
    (line,dummy,dummy) = lines[i].partition('#')
    (line,dummy,dummy) = line.partition('!')
    line = line.split()
    if len(line) > 0: lines_read.append(line)
  return lines_read

def read_input(lines):
  file_in   = ''
  format_in = ''
  station   = None
  for line in lines:
    if line[0] == 'file_in':     file_in   = line[1]
    if line[0] == 'format_in':   format_in = line[1]
    if line[0] == 'station_in':  station   = int(line[1])
  if station == None:
    print 'Reading file \''+file_in+'\' of type \''+format_in+'\''
    bunch = Bunch.new_from_read_builtin(format_in, file_in)
  else:
    print 'Reading station',station,'from file \''+file_in+'\' of type \''+format_in+'\''
    bunch = Bunch.new_dict_from_read_builtin(format_in, file_in)[station]
  print 'Loaded',bunch
  return bunch

def write_output(lines, bunch):
  file_out   = ''
  format_out = ''
  for line in lines:
    if line[0] == 'file_out':   file_out   = line[1]
    if line[0] == 'format_out': format_out = line[1]
  bunch.hit_write_builtin(format_out, file_out)
  print 'Written a',format_out,'file to',file_out

def rotate(lines, bunch):
  variables        = []
  origin           = {}
  for line in lines:
    if line[0] == 'rotate':
      for i in range(1,len(line)): variables.append(line[i])
    if line[0] == 'origin': origin[line[1]] = float(line[2])
  if len(variables) <= 1: return
  import numpy
  target_matrix    = numpy.zeros( (len(variables),len(variables)))
  for line in lines:
    if line[0] == 'covariance':
      i1 = variables.index(line[1])
      i2 = variables.index(line[2])
      target_matrix[i1,i2] = float(line[3])
      target_matrix[i2,i1] = float(line[3])
  print 'Rotation in variables\n',variables,'\nto matrix\n',target_matrix,'\nabout origin\n',origin
  bunch.transform_to(variables, target_matrix, origin)
  print 'gives\n',bunch.covariance_matrix(variables, origin)

def translate(lines, bunch):
  translation = {}
  for line in lines:
    if line[0] == 'translate':
      for i in range(1,len(line),2): 
        translation[ line[i] ] = float(line[i+1])
  print 'Translating through\n',translation
  bunch.translate(translation)

def mass_shell_condition(lines, bunch):
  for line in lines:
    if line[0] == 'mass_shell_condition': 
      print 'Changing momentum variable',line[1],'to force E^2 = p^2 + m^2'
      for hit in bunch:
        hit.mass_shell_condition(line[1])
      return

def plots(lines, bunch, do_in):
  histogram_format = 'png'
  print 'Making plots'
  for line in lines:
    if line[0] == 'histogram_format': histogram_format = line[0]
  for line in lines:
    if line[0] == 'histogram_in'  and do_in:     bunch.root_histogram(line[1], line[2]).Print(line[1]+'_in.'+histogram_format)
    if line[0] == 'histogram_out' and not do_in: bunch.root_histogram(line[1], line[2]).Print(line[1]+'_out.'+histogram_format)
    if line[0] == 'scatter_in'  and do_in:       bunch.root_scatter_graph(line[1], line[3], line[2], line[4])\
                                                      .Print(line[1]+'_vs_'+line[3]+'_in.'+histogram_format)
    if line[0] == 'scatter_out' and not do_in:   bunch.root_scatter_graph(line[1], line[3], line[2], line[4])\
                                                      .Print(line[1]+'_vs_'+line[3]+'_out.'+histogram_format)

def main(argv=None):
  contname = 'file_convert.inp'
  if len(sys.argv) > 1: 
    (arg_name,dummy,argument) = sys.argv[1].partition('=')
    if arg_name == '-c': contname = argument
    else: print 'Warning - didnt recognise command line argument',arg
  
  if sys.argv[0].find( 'File_Convert' ) > -1:
    if debug: file_convert(contname)
    else:
      try: file_convert(contname)
      except Exception, error:
        print 'There was a problem during execution. Error was:\n',error

if __name__ == "__main__":
    sys.exit(main())
