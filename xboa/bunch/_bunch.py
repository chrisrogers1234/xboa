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

import glob
import string
import copy
import gzip
import io
import operator
import math
import sys
import bisect

try: 
  import json
except ImportError:
  pass

try:
  import ROOT
except ImportError:
  pass
try:
  import numpy
  from numpy import matrix
  from numpy import linalg
except ImportError:
  pass

import xboa.common as Common
import xboa.common.config as config
import xboa.hit.factory
from xboa.hit.factory import MausRootReconHitFactory
from xboa.hit.factory import MausRootHitFactory
from xboa.hit import Hit
from xboa.hit import BadEventError 
from xboa.core import Hitcore
from xboa.core import Bunchcore
from xboa.common import rg as rg

class Bunch:
  """
  Represents a bunch of particles. Methods to: 

  - Read/write from a file
  - Calculate arbitrary moments
  - Apply cuts
  - Calculate emittances, beta functions etc
  - Extract hit data as float or arrays of floats
  - Plots (with ROOT imported)
  """
  
  def __init__(self):
    """Initialise to an empty bunch. Alternatively use static initialisers defined below - I prefer static initialisers"""
    self.__hits    = []
    self.__bunchcore = Bunchcore()
    self.__covs    = None
    self.__means   = {}

  def __str__(self):
    """Return an abbreviated string like <Bunch of n Hits>"""
    return '<Bunch of '+str(len(self.__hits))+' Hits>'

  def __repr__(self):
    """Return a long string that contains data in every hit"""
    covs = 'None'
    if self.__covs != None:
      covs = 'numpy.'+repr(self.__covs)
    out = 'Bunch.new_from_hits( ['
    for hit in self.__hits:
      out += str(hit)+',\n'
    out += '],'+covs+','+repr(self.__means)+')'
    return out

  def __copy__(self):
    """Make a copy but use references to self's data"""
    copy = self
    return copy
  
  def copy(self):
    return self.__copy__()

  def __deepcopy__(self, target):
    """Make a copy and copy self's data"""
    target = eval(self.__repr__())
    target.__covs  = copy.deepcopy(self.__covs)
    target.__means = copy.deepcopy(self.__means)
    return target
  
  def deepcopy(self):
    """Make a copy and copy self's data"""
    target = Bunch()
    return self.__deepcopy__(target)

  def __len__(self):
    """Number of hits"""
    return len(self.__hits)
  
  def __getitem__(self, key):
    """Called by subscript operator, returns the key^th hit in the bunch"""
    return self.__hits[key]
  
  def __setitem__(self, key, value):
    """Called by subscript operator, sets the key^th hit in the bunch"""
    self.__hits[key] = value
    self.__bunchcore.set_item(value._Hit__hitcore, key)

  def __delitem__(self, key):
    """Called by remove method, deletes the key^th hit in the bunch"""
    self.__hits.__delitem__(key)
    self.__bunchcore.__delitem__(key)

  def __del__(self):
    """Called by del"""
    for hit in self.__hits:
        del(hit)
    self.__bunchcore = Bunchcore()

  def __eq__(self, target, float_tolerance=Common.float_tolerance):
    """Return true if all hits in self are the same as all hits in target, and set_covariance_matrix data are the same"""
    if type(target)      != type(self):          return False
    if len(self.__hits)  != len(target.__hits):  return False
    for key,value in self.__means.items():
      if not key in target.__means:                                      return False
      if abs(self.__means[key] - target.__means[key]) > float_tolerance: return False
    try:
      if not all(self.__covs == target.__covs): return False
    except:
      try:
        if self.__covs != target.__covs: return False 
      except:
        return True
    for index in range(len(self.__hits)):
      if self.__hits[index].__ne__( target.__hits[index], float_tolerance): return False
    return True

  def __ne__(self, target, float_tolerance=Common.float_tolerance):
    """Return true if any hits in self are not the same as the corresponding hit in target"""
    return not self.__eq__(target, float_tolerance)

  def append(self, hit):
    """Append a hit to Bunch self"""
    self.__bunchcore.set_item(hit._Hit__hitcore, len(self.__hits))
    self.__hits.append(hit)

  @classmethod
  def new_from_hits(cls, hits_list, covs=None, means={},weights=[]):
    """
    Return a bunch from a list of hits, making a deepcopy of the hits (so allocating new memory for each hit)

    - hits_list = list of Hit objects

    e.g. myBunch = new_from_hits([hit1, hit2, hit3]) will return a new bunch containing hit1, hit2, hit3
    """
    bunch = Bunch()
    for hit in hits_list:
      new_hit = hit.deepcopy()
      bunch.append( new_hit )
    bunch.__covs    = covs
    bunch.__means   = means
    return bunch

  @classmethod
  def new_dict_from_read_builtin(cls, file_type_string, file_name, indexing_variable='station', test_function=None):
    """
    Return a dict of all bunches in a file using a built-in format

    - file_type_string  = string from Hit.file_types() that defines the 
                          formatting of the file
    - file_name         = name of the file that contains hit data. The file
                         name can have wildcards (*, ?) in which case events
                         from all matching files will be loaded.
    - indexing_variable = variable that will be used to define a bunch
    - test_function = ignored if None. Otherwise, Hits with test_function(hit)
                      == False will not be loaded.

    For example,
    bunch_dict = new_dict_from_read_builtin('icool_for003', 'for003.dat', 'pid')
    will return a new dict of bunches loaded from for003.dat in icool_for003 
    format, where each entry in the dict will be a reference from a pid value
    to a bunch.

    As another example,
    bunch_dict = new_dict_from_read_builtin('icool_for009',
                                            'for009.dat',
                                            'station') 
    will return a new dict of bunches loaded from for009.dat in icool_for009
    format, where each entry in the dict will be a reference from a station
    value to a bunch
    """
    bunch = Bunch.new_from_read_builtin(file_type_string,
                                        file_name,
                                        test_function)
    return bunch.split(indexing_variable)

  def split(self, indexing_variable):
    """
    Split a bunch into a number of sub-bunches according to an "indexing variable"

    Split a bunch into a number of sub-bunches, so that each sub-bunch has the
    same value of an "indexing variable"

    - indexing_variable: string variable name

    Returns a dict, whose keys are the value of indexing variable and whose values
    are the sub-bunch corresponding to that value.

    e.g. bunch_dict = bunch.split("station") will return a dict like
    { 1:bunch_1, 4:bunch_4, 5:bunch_5} where bunch_1 has hits from station 1,
    bunch_4 has hits from station 4 and bunch_5 has hits from station 5
    """
    bunch_dict = {}
    for hit in self.__hits:
        if not hit.check():
            pass
        if not int(hit.get(indexing_variable)) in bunch_dict:
            bunch_dict[ int(hit.get(indexing_variable)) ] = Bunch()
        bunch_dict[ int(hit.get(indexing_variable)) ].append(hit)
    return bunch_dict


  @classmethod
  def new_list_from_read_builtin(cls, file_type_string, file_name, sort_variable = 'station', test_function = None):
    """
    Return a sorted list of all bunches in a file using a built-in format

    - file_type_string  = string from Hit.file_types() that defines the
                          formatting of the file
    - file_name         = name of the file that contains hit data. The file
                         name can have wildcards (*, ?) in which case events
                         from all matching files will be loaded.
    - sort_variable     = variable that will be used to define a bunch and used
                          for sort order
    - test_function = ignored if None. Otherwise, Hits with test_function(hit)
                      == False will not be loaded.

    e.g. bunch_list = new_list_from_read_builtin('icool_for003', 'for003.dat', 'pid') will return a new list of bunches
    loaded from for003.dat in icool_for003 format, where each entry in the list will contain only one pid value with first entry
    having lowest pid

    e.g. bunch_list = new_list_from_read_builtin('icool_for009', 'for009.dat', 'station') will return a new list of bunches
    loaded from for009.dat in icool_for009 format, where each entry in the list will contain only one station value with first entry
    having lowest station
    """
    bunch_dict = Bunch.new_dict_from_read_builtin(file_type_string, file_name, sort_variable, test_function)
    key_list   = []
    bunch_list = []
    for key in bunch_dict:
      key_list.append(key)
    key_list.sort()
    for key in key_list:
      bunch_list.append(bunch_dict[key])
    return bunch_list

  @classmethod
  def new_from_read_builtin(cls, file_type_string, file_name_glob, test_function=None, number_of_hits=-1):
    """
    Initialise a bunch from a file using a built in format

    - file_type_string = string from Hit.file_types() that defines the file
                         format
    - file_name_glob   = string that defines the file name to be used. The file
                         name can have wildcards (*, ?) in which case events
                         from all matching files will be loaded.
    - test_function    = Hits with test_function(hit) == False will be ignored,
                         unless test_function == None
    - number_of_hits   = only loads the first number_of_hits Hits

    e.g. myBunch = Bunch.new_from_read_builtin('icool_for009', for009.dat, lambda hit: hit['station'] == 1, 1000)
    will return a bunch containing first 1000 hits from for009.dat with stationNumber=1
    """
    if not file_type_string in Hit.file_types():
        err_string = 'Attempt to load file of unknown file type '+\
                     str(file_type_string)+' - try one of '+\
                     str(Hit.file_types())
        raise IOError(err_string)
    file_name_list = glob.glob(file_name_glob)
    if len(file_name_list) == 0:
        raise IOError("Could not find file matching name "+str(file_name_glob))
    if file_type_string.find('maus_root') > -1:
      hit_list = []
      for file_name in file_name_list:
          print("Loading", file_name)
          hit_list += Bunch.read_maus_root_file(
                                          file_name,
                                          number_of_hits,
                                          list_of_maus_types=[file_type_string],
                                          test_function=test_function
                                  )
      return Bunch.new_from_hits(hit_list)
    elif file_type_string.find('maus_') > -1:
      hit_list = []
      for file_name in file_name_list:
          print("Loading", file_name)
          hit_list += Bunch.read_maus_json_file(
                                          file_name,
                                          number_of_hits,
                                          list_of_maus_types=[file_type_string]
                                  )
      hit_list = [hit for hit in hit_list if test_function == None or test_function(hit)]
      return Bunch.new_from_hits(hit_list)
    bunch = Bunch()
    for file_name in file_name_list:
        print("Loading", file_name)
        filehandle = Bunch.setup_file(file_type_string, file_name)
        while(len(bunch) < number_of_hits or number_of_hits < 0):
          try:
              hit = Hit.new_from_read_builtin(file_type_string, filehandle)
          except(EOFError):
              break
          except(BadEventError):
              continue
          if (not test_function) or test_function(hit):
              bunch.append(hit)
        filehandle.close()
    return bunch

  @classmethod
  def new_from_read_user(cls, format_list, format_units_dict, filehandle, number_of_skip_lines, test_function=None, number_of_hits=-1):
    """
    Initialise a bunch from a file using a user defined format

    - format_list       = ordered list of variables from get_variables() that contains the particle variables on each line of your input file
    - format_units_dict = dict of variables:units that are used to transform to internal system of units
    - filehandle        = file handle, created using e.g. filehandle = open('for009.dat')
    - number_of_skip_lines = integer; skip this many lines at the start of the file
    - test_function    = Hits with test_function(hit) == False will be ignored, unless test_function==None
    - number_of_hits   = only loads the first number_of_hits Hits. Will read to end of file if this is negative

    e.g. myBunch = Bunch.new_from_read_user(['x','y','z','px','py','pz'], {'x':'mm', 'y':'mm', 'z':'mm', 'px':'MeV/c', 'py':'MeV/c', 'pz':'MeV/c'}, my_input_file, 3)
    will skip the first 3 lines of the file and then read in all events from my_input_file, assuming the formatting listed
    """
    for dummy in range(number_of_skip_lines):
      filehandle.readline()
    bunch = Bunch()
    while(len(bunch.__hits) < number_of_hits or number_of_hits < 0):
      try:    hit = Hit.new_from_read_user(format_list, format_units_dict, filehandle)
      except(EOFError): break
      if   test_function == None: bunch.append(hit)
      elif test_function(hit):    bunch.append(hit)
    filehandle.close()
    return bunch

  @classmethod
  def new_hit_shell(cls, n_per_dimension, ellipse, set_variable_list, mass_shell_variable, defaults={}):
    """
    Create a set of particles that sit on the shell of an ellipse in some arbitrary dimensional space

    - n_per_dimension   = number of particles in each dimension. Total number of particles is n_per_dimension^dimension
    - ellipse           = numpy.matrix that defines the ellipse of particles
    - set_variable_list = list of set variables that defines what each dimension in the ellipse corresponds to
    - mass_shell_variable = variable that will be used to set the mass shell condition for each hit
    - defaults            = dict of default set variables that each hit will get. Hit variables will be added to defaults.

    e.g. new_bunch_as_hit_shell(2, numpy.matrix([[1,0],[0,1]]),['x','y'],'energy',{'pid':-13,'mass':Common.pdg_pid_to_mass[13],'pz':200.})
    will make a set of muons on a circle in x-y space with 200. MeV/c momentum. Event number is automatically allocated 
    incrementing from 0.
    """
    grid  = Common.make_shell(n_per_dimension, ellipse)
    bunch = Bunch()
    for ev,vector in enumerate(grid):
      bunch.append(Hit.new_from_dict(defaults))
      for i,var in enumerate(set_variable_list):
        bunch[-1][var]            += vector[0,i]
      bunch[-1]['event_number'] = ev
      bunch[-1].mass_shell_condition(mass_shell_variable)
    return bunch

  def read_maus_root_file(file_name, number_of_hits=-1, list_of_maus_types=None, test_function = None):
    """
    Read hits from a maus ROOT file

    - file_name = name of the file to read
    - number_of_hits = integer maximum number of hits to read in. If negative,
      this variable is ignored. Note that XBOA will read in a complete spill,
      check if it has reached the maximum, then reject any excess.
    - list_of_maus_types = only make hits from these types
    - test_function = return hits for which test_function(hit) == True
    Returns a list of hits
    """
    config.has_maus()
    config.has_root()
    if list_of_maus_types == None:
        list_of_maus_types = MausRootHitFactory.file_types() +\
                             MausRootReconHitFactory.file_types()
    try:
        root_file = ROOT.TFile(file_name, "READ")
        root_tree = root_file.Get("Spill")
        hits = []
        for maus_type in list_of_maus_types:
            if maus_type in MausRootHitFactory.file_types():
                fac = MausRootHitFactory(root_tree, maus_type, 0, test_function)
            elif maus_type in MausRootReconHitFactory.file_types():
                fac = MausRootReconHitFactory(root_tree, maus_type, 0, test_function)
            while number_of_hits < 0 or len(hits) < number_of_hits:
                try:
                    hits.append(fac.make_hit())
                except BadEventError:
                    break
        root_file.Close()
    except AttributeError:
        sys.excepthook(*sys.exc_info())
        print("Failed while reading events from file", file_name)
    return hits
  read_maus_root_file = staticmethod(read_maus_root_file)

  def read_maus_json_file(file_name, number_of_hits=-1,
                          list_of_maus_types=['maus_json_virtual_hit',
                                              'maus_json_primary',
                                              'maus_json_special_virtual_hit']):
    """
    Initialise a bunch from a MAUS file.

    - file_name      = string that defines the file_name to be used
    - list_of_maus_types = loads all specified types from the MAUS file
    """
    config.has_json()
    json_file = open(file_name, 'r')
    hits = []
    for maus_type in list_of_maus_types:
        fac = xboa.hit.factory.MausJsonHitFactory(json_file, maus_type)
        while number_of_hits < 0 or len(hits) < number_of_hits:
            try:
                hits.append(fac.make_hit())
            except BadEventError:
                break
    json_file.close()
    return hits
  read_maus_json_file = staticmethod(read_maus_json_file)

  def setup_file(file_format_type_string, file_name):
    """Returns a file handle with special phrases and characters stripped. Returned file_handle contains only hit data"""
    filehandle = open(file_name, 'r')
    if not file_format_type_string in Hit.file_types():
      raise KeyError('Could not find filetype '+file_format_type_string+' - Options are '+str(Hit.file_types()))
    for dummy in range(Bunch.__number_of_header_lines[file_format_type_string]):
      filehandle.readline()
    if file_format_type_string == 'g4beamline_bl_track_file' or file_format_type_string == 'g4beamline_bl_track_file_2':
      open_file  = filehandle
      filehandle = io.StringIO()
      try:
        line = open_file.readline()
        while( len(line) > 0 ):
          if('cm cm cm' in line and line[0] == '#') :   Hit.set_g4bl_unit('cm')
          elif('mm mm mm' in line and line[0] == '#') : Hit.set_g4bl_unit('mm')
          elif(line[0] == '#' or line[0] == '\n'): pass
          else: filehandle.write(line)
          line = open_file.readline()
      except IOError: pass
      open_file.close()
      filehandle.seek(0)
    return filehandle
  setup_file = staticmethod(setup_file)

  def translate(self, dict_variables_values, mass_shell_variable=''):
    """
    Translate all events in the bunch by dict_variables_values

    - dict_variables_values = dict of variable names from Hit.set_variables() to variable values
    - mass_shell_variable   = set mass shell variable so that E^2=p^2+m^2 after translation. 
                                Does nothing if equal to ''

    e.g. bunch.translate({'pz':-10,'z':100}, 'energy') reduces particle pz by 10 MeV/c and increases 
      E by 100 mm then sets E so that mass shell condition is still obeyed  
    """
    for hit in self.__hits:
      hit.translate(dict_variables_values, mass_shell_variable)
   ##
  def abelian_transformation(self, rotation_list, rotation_matrix, translation_dict={}, origin_dict={}, mass_shell_variable=''):
    """
    Perform an Abelian Transformation on all variables in the bunch so that V_{out} - O = R*(V_{in}-O)+T

    - rotation_list = list of Hit.set_variables() strings that defines the vector V
    - rotation_matrix = matrix R
    - translation_dict = dict of Hit.set_variables() strings to values that defines the vector T
    - mass_shell_variable   = set mass shell variable so that E^2=p^2+m^2 after transformation. 
                                Does nothing if equal to ''
    - origin_dict = dict of Hit.set_variables() strings to values that defines the vector O. Defaults to
                  bunch mean.

    e.g. bunch.abelian_transformation(['x','px','z'], [[1,0.1,0],[0,1,0],[0,0,1]], {'z':1000}, 'pz') has
         V_{in} = ('x','px','z')
         R = 1   0.1  0
             0   1    0
             0   0    1
         T = (0,0,1000)
         O = bunch mean
    (This is like a drift). Note that 'z' has to be explicitly included in the rotation to be present in T
    """
    for hit in self.__hits:
      hit.abelian_transformation(rotation_list, rotation_matrix, translation_dict, origin_dict, mass_shell_variable)
    
  def transform_to(self, transform_list, target_covariances, translation_dict={}, origin_dict={}, mass_shell_variable=''):
    """
    Perform a linear transformation on all particles in the bunch to get a bunch with covariance matrix 
    similar to target_covariances. The transformation always has determinant 1, and so is emittance conserving.
    Then performs a translation using translation_dict

    - transform_list = list of Hit.set_variables() strings that defines the vector V
    - target_covariances = target covariance matrix. Must be n*n dimensions where n is the length of transform_list
    - translation_dict = dict of Hit.set_variables() strings to values that defines a translation
    - origin_dict = dict of Hit.set_variables() strings to values that defines the vector O. Defaults to
                      bunch mean.
    - mass_shell_variable   = set mass shell variable so that E^2=p^2+m^2 after transformation. 
                            Does nothing if equal to \'\'

    e.g. bunch.transform_to(['x','px'], [[1,0],[0,1]], {'pz':10}, 'energy') will apply a transformation to all hits in the 
    bunch that diagonalises the bunch and makes Var(x,x) equal to Var(px,px), but conserving emittance; then will add 
    10 to pz for all tracks; then adjust energy to keep mass shell condition.
    """
    ### transformation to turn covariance matrix into unity matrix
    config.has_numpy()
    (self_evals, self_evecs) = linalg.eigh(self.covariance_matrix(transform_list, origin_dict))
    unite = matrix(numpy.zeros((len(transform_list),len(transform_list))))
    for i in range(len(transform_list)): unite[i,i] = self_evals[i]**0.5
    unite      = linalg.inv(self_evecs*unite)
    ### transformation to turn unity matrix into target_covariances
    (target_evals, target_evecs) = linalg.eigh(target_covariances)
    ununite = matrix(numpy.zeros((len(transform_list),len(transform_list))))
    for i in range(len(transform_list)): ununite[i,i] = target_evals[i]**0.5
    ununite      = target_evecs*ununite
    ### force determinant to 1 =>emittance conservation
    transform  = ununite*unite
    power      = 1./float(len(transform_list))
    transform  = transform/(abs(linalg.det(transform))**power)
    self.abelian_transformation(transform_list, transform, translation_dict, origin_dict, mass_shell_variable)
  
  def period_transformation(self, offset, frequency, variable='t'):
    """
    Transform all hit's variable from a linear space to a periodic space with some frequency and offset

    - offset    = float that defines the offset
    - frequency = float that defines the frequency of the periodic space
    - variable  = string from hit_set_variables. variable for which the periodicity is applied

    e.g. bunch.period_transformation( dt, rf_freq) would transform all times into a range between
      (-0.5/rf_freq, 0.5/rf_freq). Hits with 't' = n*dt would transform to t=0 (n arbitrary integer)
    Used to transform a set of many rf buckets into one rf bucket, for calculating longitudinal emittance etc
    """
    for hit in self:
      hit[variable] -= offset #all points relative to offset
      number_pulses  = hit[variable]*frequency+0.5
      #      if number_pulses < 0.: number_pulses -= 1. #this is weird!
      hit[variable] -= math.floor(number_pulses)/frequency

  def hits(self):
    """Returns the list of all hits in the bunch"""
    return self.__hits

  def get_hits(self, variable, value, comparator=operator.eq):
    """ 
    Returns a list of all hits in the bunch with comparator(variable, value) == True
    By default comparator is equality operator, so returns a list of all hits in the bunch with variable == value

    - variable   = string from Hit.get_variables()
    - value      = value for comparison
    - comparator = function that operates on a hit and returns a boolean

    e.g. get_hits('eventNumber', 50) returns a list of all hits in the bunch with hitNumber 50
    e.g. get_hits('eventNumber', 50, operator.lt) returns a list of all hits in the bunch with hitNumber less than 50
    """
    some_hits = []
    for key in self.__hits:
      if comparator(self.get_hit_variable(key, variable), value):
        some_hits.append(key)
    return some_hits

  def hit_equality(self, target, float_tolerance=Common.float_tolerance):
    """
    Return True if all hits in self are the same as all hits in target

    - target = bunch to test against
    """
    if len(self) != len(target): return False
    for i in range( len(self) ):
      if self[i] != target[i]: return False
    return True

  def conditional_remove(self, variable_value_dict, comparator, value_is_nsigma_bool = False):
    """
    For when a cut is not good enough, remove hits from the bunch altogether if comparator(value, get([variable])) is False

    - variable_value_dict = dict of Bunch.get_variables() to the cut value; cut if the hit variable has value > value
    - value_is_nsigma_bool = boolean; if True, value is the number of standard deviations
    - global_cut = boolean; if True, apply cut to global weights; else apply to local weights

    e.g. bunch.cut({'energy':300,}, operator.ge) removes particles if they have 
         ge(hit.get('energy'),300) here operator.ge is a functional representation of the >= operator 
         ge(hit.get('energy'),300) is the same as (hit.get('energy') >= 300)

    A whole load of useful comparators can be found in the operator module. e.g. ge is >=; le is <=; etc
    See also python built-in function "filter".
    """
    for variable, cut_value in variable_value_dict.items():
      if(value_is_nsigma_bool):
        cut_value *= self.standard_deviation(variable, self.mean([variable]))**0.5
      # optimisation for amplitude cut: calculate covariance matrix first
      # optimisation for gt/lt: sort the hit_value_list first then cut
      hit_value_list = self.list_get_hit_variable([variable])[0]
      new_hits = []
      for i in range ( len(hit_value_list) ):
        if not comparator(hit_value_list[i], cut_value): 
          new_hits.append(self.__hits[i])
      self.__hits = new_hits
      self.__bunchcore = Bunchcore()
      for i, value in enumerate(new_hits):
        self.__bunchcore.set_item(value._Hit__hitcore, i)


  def standard_deviation(self, variable, variable_mean={}):
    """
    Return a standard deviation, given by sum( (u-u_mean)**2 )**0.5 where u is the variable specified

    - variable = a variable from Hit.get_variables(). Can be a list, in which
                   case only the first hit is taken
    - variable_mean = use this as u_mean rather than calculating a priori. Can
                    be a dict, in which case if variable is in the keys will
                    use that value.

    e.g. bunch.standard_deviation('x') returns the standard deviation of x

    e.g. bunch.standard_deviation('x', 1.) returns the standard deviation of x
         about a mean of 1.

    e.g. bunch.standard_deviation(['x'], {'x':1.}) returns the standard
         deviation of x about a mean of 1.
    """
    a_variable = variable
    if type(variable) == type([]):
        a_variable = variable[0]
    a_variable_mean = variable_mean
    if type(variable_mean) != type({}):
        a_variable_mean = {a_variable:variable_mean}
    return self.moment([a_variable, a_variable], a_variable_mean)**0.5
        

  def moment(self, variable_list, variable_mean_dict={}):
    """
    Return a moment, sum( (u1 - u1_mean)*(u2-u2_mean)*(etc)) where u is a set of Hit get_variables indexed by variable_list

    - variable_list = list of strings that index the moment
    - variable_mean_dict = dict of variable to means for moment calculation. Assume bunch mean if no value is specified

    e.g. bunch.moment(['x','x'], {'x':0.1}) returns the variance of x about a mean of 0.1

    e.g. bunch.moment(['x','px']) returns the covariance of x,px about the bunch mean
    """
    bunch_weight = self.bunch_weight()
    if abs(bunch_weight) < 1e-9: raise ZeroDivisionError('Trying to find moment of bunch with 0 weight')
    if self.__covs != None and len(variable_list) == 2:
      axis_list = Bunch.axis_list_to_covariance_list(Bunch.__axis_list)
      try:
        i1 = axis_list.index(variable_list[0])
        i2 = axis_list.index(variable_list[1])
        return float(self.__covs[i1,i2]) # not numpy.float64
      except ValueError:
        pass
    if variable_mean_dict == {}:
      variable_mean_dict = self.mean(variable_list)
    try:
      moment = self.__bunchcore.moment(variable_list, variable_mean_dict)
      return moment
    except: #variables not in bunchcore.get_variable list
      mean_list = []
      for var in variable_list:
        mean_list.append(variable_mean_dict[var])
      moment = 0
      for hit in self.__hits:
        change = 1.
        for index in range(len(variable_list)):
          change *= self.get_hit_variable(hit, variable_list[index]) - mean_list[index]
        moment += change*hit.get('weight')
      return moment/self.bunch_weight()

  def mean(self, variable_list):
    """
    Return dict of variables to means

    - variable_list = list of strings to calculate means

    e.g. bunch.mean(['x','px']) returns a dict like {'x':x_mean, 'px':px_mean}
    """
    variable_mean_dict = {}
    for var in variable_list:
      if not var in variable_mean_dict:
        if not var in self.__means:
          variable_mean_dict[var] = self.moment([var], {var:0.0})
        else:
          variable_mean_dict[var] = self.__means[var]
    return variable_mean_dict

  def covariance_matrix(self, get_variable_list, origin_dict={}):
    """
    Return covariance matrix of variables

    - variable_list = list of strings to calculate covariance
    - origin_dict   = dict of strings to values for origin about which covariances are calculated. Defaults to mean

    e.g. bunch.covariance_matrix(['x','px'], {'x':0, 'px':0}) returns a matrix like [[Var(x,x), Var(x,px)], [Var(x,px), Var(px,px)]
    """
    config.has_numpy()
    dim = len(get_variable_list)
    cov = matrix(numpy.zeros((dim,dim)))
    origin_dict1 = copy.deepcopy(origin_dict)
    origin_list  = []
    for var in get_variable_list:
      if not var in origin_dict1:
        origin_dict1[var] = self.mean([var])[var]
      origin_list.append(origin_dict1[var])
    try:
      covariances = self.__bunchcore.covariance_matrix(get_variable_list, origin_list)
      for i1 in range(dim):
        for i2 in range(i1, dim):
          cov[i1,i2] = covariance_list[i1][i2]
      return cov
    except:
      pass
    for i1 in range(dim):
      for i2 in range(i1, dim):
        covariance_list = [get_variable_list[i1], get_variable_list[i2]]
        cov[i1,i2]     = self.moment(covariance_list, origin_dict1)
        cov[i2,i1]     = cov[i1,i2]
    return cov
  
  def set_covariance_matrix(self, use_internal_covariance_matrix=True, covariance_matrix=None, mean_dict={}):
    """
    Choose whether to use an internal covariance matrix for calculations

    - use_internal_covariance_matrix = boolean. If set to True, x-boa will recalculate its internal covariance matrix and use this 
                                     for some calculations. If set to False, x-boa will calculate the covariance matrix each time. 
    - covariance_matrix              = NumPy matrix. x-boa will use this matrix as the internal covariance matrix; should be a 10x10 matrix ordered like
                                     (x, px, y, py, z, pz, t, enegry, ct, energy). Ignored if equal to None
    - mean_dict                      = dict of variables to means. x-boa will use this dict to index means; should contain means of
                                     (x, px, y, py, z, pz, t, enegry, ct, energy). Ignored if equal to None

    As a speed optimisation, x-boa can calculate a covariance matrix and use this for all calculations involving covariances, i.e. Twiss parameters, emittances, amplitudes etc. Otherwise x-boa will re-calculate this each time, which can be slow. Be careful though - x-boa does not automatically detect for hits being added or removed from the bunch, etc. The user must call this function each time the bunch changes (events added, weightings changed, etc) to update the internal covariance matrix
    """
    if use_internal_covariance_matrix:
      if covariance_matrix == None:
        self.__covs = self.covariance_matrix(Bunch.axis_list_to_covariance_list(Bunch.__axis_list))
      else: self.__covs = covariance_matrix
      if mean_dict == {}:
        self.__means = self.mean(Bunch.axis_list_to_covariance_list(Bunch.__axis_list))
      else: self.__means = mean_dict
    else:
      self.__covs  = None
      self.__means = {}

  def covariances_set(self):
    """If internal covariances are set by set_covariance_matrix, return True; else return False"""
    return self.__covs != None


  def means_set(self):
    """If means are set by set_covariance_matrix, return True; else return False"""
    return self.__means != {}

  def bunch_weight(self):
    """Return statistical weight of all hits in the bunch"""
    weight = 0
    for key in self.__hits:
      weight += key.get('weight')
    return weight
  
  def clear_local_weights(self):
    """Set local_weight of all hits in the bunch to 1"""
    for key in self.__hits:
      key.set('local_weight', 1)
  
  def clear_global_weights():
    """Set global_weight of all hits in the bunch to 1"""
    Hit.clear_global_weights()
  clear_global_weights = staticmethod(clear_global_weights)

  def clear_weights(self):
    """Set global_weight and local_weight of all hits in the bunch to 1"""
    self.clear_local_weights()
    self.clear_global_weights()
  
  def cut(self, variable_value_dict, comparator, value_is_nsigma_bool = False, global_cut = False):
    """
    Set weight of hits in the bunch to 0 if comparator(value, get([variable])) is False

    - variable_value_dict = dict of Bunch.get_variables() to the cut value; cut if the hit variable has value > value
    - comparator = callable; comparator(value, cut_value) returns true, cut the variable (set weight to 0.)
    - value_is_nsigma_bool = boolean; if True, value is the number of standard deviations
    - global_cut = boolean; if True, apply cut to global weights; else apply to local weights

    e.g. bunch.cut({'energy':300,}, operator.ge) sets weight of particles to zero if they have 
         ge(hit.get('energy'),300) here operator.ge is a functional representation of the >= operator 
         ge(hit.get('energy'),300) is the same as (hit.get('energy') >= 300)

    A whole load of useful comparators can be found in the operator module. e.g. ge is >=; le is <=; etc
    """
    if global_cut: set_var = 'global_weight'
    else:          set_var = 'local_weight'
    for variable, cut_value in variable_value_dict.items():
      if(value_is_nsigma_bool):
        cut_value *= self.moment([variable, variable], self.mean([variable]))**0.5
      # check for non-int get variables
      if variable in Hitcore.get_variables() and type(Hit()[variable]) == type(0.):
        self.__bunchcore.cut_double(variable, comparator, cut_value, global_cut)
      else:
        self._cut(variable, comparator, cut_value, set_var)

  def _cut(self, variable, comparator, cut_value, set_var):
      hit_value_list = self.list_get_hit_variable([variable])[0]
      for i in range ( len(hit_value_list) ):
        if comparator(hit_value_list[i], cut_value):
          self.__hits[i].set(set_var, 0)

  def transmission_cut(self, test_bunch, global_cut=False, test_variable=['spill', 'event_number', 'particle_number'], float_tolerance=Common.float_tolerance):
    """
    Set weight of hits in the bunch to 0 if no events can be found in test_bunch with the
    same test_variable

    - test_bunch = bunch to test against
    - global_cut = if True, apply cut to global weights
    - test_variable = cut a hit in self if no hits are found in test_bunch with
                      the same test_variable. If test_variable is a list, then
                      cut from self if no hits are found in test_bunch with all
                      test_variables the same.

    E.g. bunch.transmission_cut( some_other_bunch, True ) will apply a global 
         cut if a hit with the same [spill, event_number, particle_number] is
         not in some_other_bunch (for all hits)
    """
    if global_cut: wt = 'global_weight'
    else:          wt = 'local_weight'
    hit_list = [[] for i in range(len(test_bunch))]
    if type(test_variable) == type(''):
        test_variable = [test_variable]
    for i in range( len(test_bunch) ):
        for var in test_variable:
            hit_list[i].append(test_bunch[i][var])
    hit_list.sort()
    for hit in self:
      weight     = 0
      hit_value  = [hit[var] for var in test_variable]
      next_value = bisect.bisect_left(hit_list, hit_value)
      if next_value > -1 and next_value < len(hit_list):
        diff = [abs(hit_list[next_value][i]-hit_value[i]) for i in range(len(hit_value))]
        diff = sum(diff)
        if diff < float_tolerance:   weight = hit[wt]
      if next_value+1 < len(hit_list):
        diff = [abs(hit_list[next_value+1][i]-hit_value[i]) for i in range(len(hit_value))]
        diff = sum(diff)
        if diff < float_tolerance: weight = hit[wt]
      hit.set(wt, weight)

  def get_beta (self, axis_list, geometric=None):
    """
    Return the bunch beta function, defined by

    - For normalised beta = Sum_{i} Var(x_i)*p/(emittance*mass*n)
    - For geometric beta = Sum_{i} Var(x_i)/(emittance*n)
  
    where x_i is a position variable from axis_list.

    - axis_list = list of axes strings

    and n is the length of axis_list. E.g.
    ~~~~~~~~~~~~~~~{.py}
    get_beta(['x','y']) 
    ~~~~~~~~~~~~~~~
    will return ( Var(x,x)+Var(y,y) )/(2*pz*emittance(['x','y')*mass)
    """
    if geometric == None: geometric = Bunch.__geometric_momentum
    beta      = 0.0
    emittance = self.get_emittance(axis_list, None, geometric)
    for axis in axis_list:
      beta += self.moment([axis,axis], self.mean([axis]))
    if not geometric:
      beta *= self.mean(['p'])['p']/(emittance*self.hits()[0].get('mass')*float(len(axis_list)))
    else:
      beta /= emittance*float(len(axis_list))
    return beta

  def get_gamma(self, axis_list, geometric=None):
    """
    Return the bunch gamma function, defined by

    - For normalised gamma = Sum_{i} Var(p_i)/(pz*emittance*mass*n)
    - For geometric gamma = Sum_{i} Var(p_i)/(emittance*n)

    where p_i is a momentum variable from axis_list.

    - axis_list = list of axes strings

    and n is the length of axis_list. E.g.
    ~~~~~~~~~~~~~~~{.py}
    get_gamma(['x','y'])
    ~~~~~~~~~~~~~~~
    will return ( Var(p_x)+Var(p_y) )/(2*pz*emittance(['x','y')*mass)
    """
    if geometric == None: geometric = Bunch.__geometric_momentum
    gamma     = 0.0
    emittance = self.get_emittance(axis_list)
    for axis in axis_list:
      mom    = self.momentum_variable(axis, geometric)
      gamma += self.moment([mom,mom], self.mean([mom]))
    if not geometric:
      gamma /= self.mean(['p'])['p']*self.hits()[0].get('mass')
    gamma /= (emittance*len(axis_list))
    return gamma
  
  def get_alpha(self, axis_list, geometric=None):
    """
    Return the bunch alpha function, defined by

    - For normalised alpha = Sum_{i} Cov(x_i, p_i)/(emittance*mass*n)
    - For geometric alpha = Sum_{i} Cov(x_i, p_i)/(emittance*n)

    where p_i is a momentum variable from axis_list.

    - axis_list = list of axes strings

    and n is the length of axis_list. E.g. 
    ~~~~~~~~~~~~~~~{.py}
    get_alpha(['x','y'])
    ~~~~~~~~~~~~~~~
    will return ( Var(p_x)+Var(p_y) )/(2*emittance(['x','y')*mass)
    """
    if geometric == None: geometric = Bunch.__geometric_momentum
    alpha     = 0.0
    emittance = self.get_emittance(axis_list)
    for axis in axis_list:
      mom    = self.momentum_variable(axis, geometric)
      alpha += self.moment([axis,mom], self.mean([axis, mom]))
    if not geometric:
      alpha /= (emittance*self.hits()[0].get('mass')*len(axis_list))
    else:
      alpha /= emittance*len(axis_list)
    return -alpha

  def get_dispersion(self, axis):
    """
    Return the bunch dispersion D in axis q, defined by

    - D = cov(q,E)*mean(E)/var(E)
    - axis = string from axis_list that defines the axis q

    E.g.
    ~~~~~~~~~~~~~~~{.py}
    my_bunch.get_dispersion('y')
    ~~~~~~~~~~~~~~~
    would return the dispersion in the y-direction
    """
    return self.moment([axis,'energy'])*self.mean(['energy'])['energy']/self.moment(['energy','energy'])

  def get_dispersion_rsquared(self):
    """
    Return a special bunch dispersion defined by

    - D = (<r2,E>-<r2>*<E>)*mean(E)/var(E)

    where <> are raw moments (not central moments)
    """
    mean_dict = {'r_squared':0., 'energy':0.}
    return (self.moment(['r_squared','energy'],mean_dict)-(self.moment(['x','x'])+self.moment(['y','y']))*self.mean(['energy'])['energy'])\
           *self.mean(['energy'])['energy']/self.moment(['energy','energy'])


  def get_dispersion_prime(self, axis, geometric = None):
    """
    Return the bunch dispersion prime D in axis q, defined by

    - D' = cov(p_q,E)*mean(E)/var(E)
    - axis = string from axis_list that defines the axis q

    E.g.
    ~~~~~~~~~~~~~~~{.py}
    my_bunch.get_dispersion('y')
    ~~~~~~~~~~~~~~~
    would return the dispersion in the y-direction
    """
    mom = Bunch.momentum_variable(axis, geometric)
    return self.moment([mom,'energy'])*self.mean(['energy'])['energy']/self.moment(['energy','energy'])

  def get_decoupled_emittance(self, coupled_axis_list, emittance_axis_list, covariance_matrix=None, geometric=None):
    """Reserved for future development"""
    # the problem here is the sort order of the eigenvalues, which doesn't necessarily reflect what was in the
    # original array
    if geometric == None: geometric = Bunch.__geometric_momentum
    coupled_axis_list2 = []
    emit_var           = []
    for ax in Bunch.__axis_list:
      if ax in emittance_axis_list:
        emit_var.append(len(coupled_axis_list2)) #mark position of emittance variables
      if ax in coupled_axis_list or ax in emittance_axis_list:
        coupled_axis_list2.append(ax) #build sorted list of coupled variables
    cov_var_list  = Bunch.axis_list_to_covariance_list(coupled_axis_list2)
    my_cov    = copy.deepcopy(covariance_matrix)
    if my_cov == None:
      my_cov = self.__cov_mat_picker(coupled_axis_list2)
      if my_cov == None: 
        my_cov = self.covariance_matrix(cov_var_list)
    (evalues, ematrix) = numpy.linalg.eig(my_cov)
    ematrix = matrix(ematrix)
    my_cov  = matrix(my_cov)
    array_out = []
    for var in emit_var:
      array_out = array_out+[float(evalues[2*var]), float(evalues[2*var+1])]
    print(array_out)
    print('Undiagonalisation:')
    print(ematrix*numpy.diagflat(evalues)*ematrix.T)
    print(ematrix)
    print(numpy.diagflat(evalues))
    cov_out = numpy.diagflat(array_out)
    return self.get_emittance(emittance_axis_list, covariance_matrix=cov_out, geometric=geometric)
    """
    Return the decoupled n dimensional normalised RMS emittance of the bunch

    - emittance = (|V|**(1/2n))/mass

    where n is the number of elements in axis list and V is a covariance matrix
    with elements V_{ij} = cov(u_i, u_j) where u is a vector of elements in the
    axis_list and their momentum conjugates, u = (q_i, p_i). 
    The slight subtlety is that the emittance is calculated with any coupling between
    axis_list and the elements in coupled_axis_list removed by a transformation.
    In particular, I calculate the eigenvalues of the matrix generated from
    emittance_axis_list+coupled_axis_list (duplicated elements removed) and return the 
    product of eigenvaues pertaining to emittance_axis_list

    - coupled_axis_list = list of axes from Bunch.get_axes().
    - emittance_axis_list = list of axes from Bunch.get_axes().
    - covariance_matrix = if specified, use this covariance matrix rather than 
                            calculating a new one each time.
    - geometric = if specified, use geometric variables (dx/dz, dy/dz, etc) rather
                    than normalised variables (px, py, pz).

    E.g. 
    ~~~~~~~~~~~~~~~{.py}
    get_decoupled_emittance(['x','y'], ['x'])
    ~~~~~~~~~~~~~~~
    will return
      |V|**(1/2)
    where V is the matrix with elements
      V = Var(x',x')  Cov(x',px')
          Cov(x',px') Var(px',px')
    and |V| is the determinant. Here x' indicates x following a decoupling
    transformation (to remove, for example, rotation due to solenoid field).
    """

  def get_emittance(self, axis_list, covariance_matrix=None, geometric = None):
    """
    Return the n dimensional normalised emittance of the bunch

    - emittance = (|V|**(1/2n))/mass

    where n is the number of elements in axis list and V is a covariance matrix
    with elements V_{ij} = cov(u_i, u_j) where u is a vector of elements in the
    axis_list and their momentum conjugates, u = (q_i, p_i)

    - axis_list = list of axes from Bunch.get_axes().
    - covariance_matrix = if specified, use this covariance matrix rather than 
                            calculating a new one each time.
    - geometric = if specified, use geometric variables (dx/dz, dy/dz, etc) rather
                    than normalised variables (px, py, pz).

    E.g.
    ~~~~~~~~~~~~~~~{.py}
    get_emittance(['x'])
    ~~~~~~~~~~~~~~~
    will return
      |V|**(1/2)
    where V is the matrix with elements
      V = Var(x,x)  Cov(x,px)
          Cov(x,px) Var(px,px)
    and |V| is the determinant.
    """
    if geometric is None: geometric = Bunch.__geometric_momentum
    cov_list  = Bunch.axis_list_to_covariance_list(axis_list)
    my_cov    = copy.deepcopy(covariance_matrix)
    if my_cov is None:
      my_cov = self.__cov_mat_picker(axis_list)
      if my_cov is None: 
        my_cov = self.covariance_matrix(cov_list)
    emittance = linalg.det(my_cov)**(1./len(cov_list))
    if not Bunch.__geometric_momentum:
      emittance /= self.__hits[0].get('mass')
    return float(emittance)
  
  def get_kinetic_angular_momentum(self, rotation_axis_dict={'x':0,'y':0,'px':0,'py':0,'x\'':0,'y\'':0}):
    """
    Return the bunch kinetic angular momentum about some arbitrary axis, defined by

    - L = <x py> - <y px> (momentum variables)
    - L = <p>*(<x y'> - <y x'>) (geometric variables)
        
    - rotation_axis_dict = dict that defines the axis of rotation
    """
    if not Bunch.__geometric_momentum: 
      return self.moment(['x','py'], rotation_axis_dict) - self.moment(['y','px'], rotation_axis_dict)
    else:
      return (self.moment(['x','y\''], rotation_axis_dict) - self.moment(['y','x\''], rotation_axis_dict)) * self.mean(['pz'])['pz']

  def get_canonical_angular_momentum(self, bz=None, field_axis_dict={'x':0, 'y':0}, rotation_axis_dict={'x':0,'y':0,'px':0,'py':0}):
    """
    Return the bunch canonical angular momentum about some arbitrary axis, defined by

    - L = <x py> - <y px> + e Bz (<x^2>+y^2) (momentum variables)
    - L = <p>*(<x y'> - <y x'>) + e Bz (<x^2>+y^2) (geometric variables)
        
    - bz = nominal on-axis magnetic field - where axis is as; defaults to the field of the 1st particle in the bunch
    - field_axis_dict = dict that defines the nominal solenoid axis
    - rotation_axis_dict = dict that defines the axis of rotation
    """
    if bz==None: 
      bz = (self[0]['bz'])
    return self.get_kinetic_angular_momentum(rotation_axis_dict) + \
           Common.constants['c_light']*bz*(self.moment(['x','x'], field_axis_dict) + self.moment(['y','y'], field_axis_dict))/2.

  def momentum_variable(axis_variable, geometric_momentum):
    """
    Return the momentum conjugate for axis_variable
    """
    if not axis_variable in Bunch.__axis_list:
      raise IndexError(str(axis_variable)+' does not appear to be an axis variable. Options are '+str(Bunch.get_axes()))
    if type(axis_variable) == int:
      if geometric_momentum:
        return Hit.get_variables()[axis_variable]+'\''
      else:
        return Hit.get_variables()[axis_variable+4]
    if geometric_momentum:
      return axis_variable+'\''
    elif axis_variable == 't' or axis_variable == 'ct' or axis_variable==3:
      return 'energy'
    else:
      return 'p'+axis_variable
  momentum_variable = staticmethod(momentum_variable)

  def get_amplitude (bunch, hit, axis_list, covariance_matrix=None, mean_dict={}, geometric=None):
    """
    Return the particle amplitude for a hit relative to a bunch, defined by

    - amplitude = emittance*x^T.V^-1.x

    where x is a vector of particle coordinates and V is a covariance matrix

    - bunch = bunch from which the covariance matrix is calculated
    - hit   = hit from which the particle vector is taken
    - axis_list = list of axes that defines the covariance matrix and particle vector
    - covariance_matrix = if this is not set to None, will use this covariance_matrix 
          for the calculation rather than taking one from bunch. Should be a numpy matrix
          like "x","px","y","py"
    E.g. 
    ~~~~~~~{.py}
    Bunch.get_amplitude(my_bunch, my_hit, ['x','y'])
    ~~~~~~~
    will return
        emittance*(x,px,y,py)^T*V^{-1}(x,px,y,py)*(x,px,y,py)
    """
    if geometric == None: geometric = Bunch.__geometric_momentum
    cov_list  = Bunch.axis_list_to_covariance_list(axis_list, geometric)
    if mean_dict == {}:   
      mean_dict = bunch.__mean_picker(axis_list)
      if mean_dict == {}:
        mean_dict = bunch.mean(cov_list)
    my_vector = hit.get_vector(cov_list, mean_dict)
    my_cov    = copy.deepcopy( covariance_matrix )
    if my_cov is None:
      my_cov = bunch.__cov_mat_picker(axis_list)
      if my_cov is None:
        my_cov = bunch.covariance_matrix(cov_list)
    my_amp = my_vector*linalg.inv(my_cov)*my_vector.T
    return float(my_amp[0,0])*bunch.get_emittance(axis_list, my_cov)
  get_amplitude = staticmethod(get_amplitude)

  def axis_list_to_covariance_list(axis_list, geometric=None):
    """
    Convert from a list of position variables to a list of position
    and conjugate momentum variables

    - axis_list = list of strings from get_axes()
    """
    if geometric == None: geometric = Bunch.__geometric_momentum
    cov_list  = []
    for axis in axis_list:
      cov_list.append(axis)
      cov_list.append(Bunch.momentum_variable(axis, geometric))
    return cov_list
  axis_list_to_covariance_list = staticmethod(axis_list_to_covariance_list)
  
  def convert_string_to_axis_list(axis_string):
    """
    Return a list of axes from a string.

    - axis_string = string that contains a list of axis. Either format
        as axis_strings separated by white space or as a python list
        of axis_strings
    """
    axis_list = []
    try: 
      axis_list = eval(axis_string) #try to evaluate it as a list
    except: 
      axis_list = axis_string.split(' ') #assume it is a white space separated dataset instead
    for key in axis_list:
      if not key in Bunch.__axis_list:
        raise KeyError('Could not resolve '+str(axis_string)+' into a list of axes.')
    return axis_list
  convert_string_to_axis_list = staticmethod(convert_string_to_axis_list)

  def set_geometric_momentum(new_value_bool):
    """
    Set the default for conjugate momenta; either geometric (x', y', etc) or kinetic (px, py, etc)

    - new_value_bool = if True, use geometric momenta. If False, use kinetic momenta (default)
    """
    Bunch.__geometric_momentum  = new_value_bool
  set_geometric_momentum = staticmethod(set_geometric_momentum)

  def get_geometric_momentum():
    """
    Set the default for conjugate momenta; either geometric (x', y', etc) or kinetic (px, py, etc)

    - new_value_bool = if True, use geometric momenta. If False, use kinetic momenta (default)
    """
    return Bunch.__geometric_momentum
  get_geometric_momentum = staticmethod(get_geometric_momentum)

  def get_axes():
    """Return list of axis variables (position-type variables)"""
    return Bunch.__axis_list
  get_axes = staticmethod(get_axes)
  
  def get_hit_variable(self, hit, variable_name, covariance_matrix=None, mean_dict={}):
    """
    Return axis variable for hit. Special power is that it can calculate amplitude, unlike hit.get(blah)

    - hit = a Hit object
    - variable_name = either a variable from Hit.get_variables() or an amplitude variable.
        amplitude variables should be formatted like 'amplitude x y' or 'amplitude x y t'
    - covariance_matrix = use a pre-calculated covariance matrix, or calculate if set to None
    """
    if type(variable_name) == str:
      if variable_name.find('amplitude') > -1:
        axis_list = Bunch.convert_string_to_axis_list(variable_name[10:len(variable_name)])
        return Bunch.get_amplitude(self, hit, axis_list, covariance_matrix, mean_dict)
    return hit.get(variable_name)

  def list_get_hit_variable(self, list_of_variables, list_of_units=[]):
    """
    Return a list of get_hit_variable results, one element for each hit in the bunch

    - variable_name = either a variable from Hit.get_variables() or an amplitude variable.
        amplitude variables should be formatted like 'amplitude x y' or 'amplitude x y t'
        i.e. amplitude followed by a list of axes separated by white space
    - covariance_matrix = use a pre-calculated covariance matrix, or calculate if set to None
    """
    values = []
    for dummy in list_of_variables:
      values.append([])
    for i in range(len(list_of_variables)):
      covariance_matrix = None
      mean_dict = None
      var = list_of_variables[i]
      if type(var) is str:
        if(var.find('amplitude') > -1):
          axis_list = Bunch.convert_string_to_axis_list(var[10:len(var)])
          covariance_list = Bunch.axis_list_to_covariance_list(axis_list)
          covariance_matrix = self.covariance_matrix(covariance_list)
          mean_dict = self.mean(covariance_list)
      for hit in self.__hits:
        values[i].append( self.get_hit_variable(hit, var, covariance_matrix, mean_dict) )
        if not list_of_units == []: 
          values[i][-1] /= Common.units[list_of_units[i]]
    return values
  
  def get(self, variable_string, variable_list):
    """
    Return a bunch variable taken from the list Bunch.get_variables()

    - variable_string = string variable from Bunch.get_variables()
    - variable_list   = list of variables (see below, a bit complicated)

    For 'bunch_weight', axis_list is ignored

    For 'dispersion', 'dispersion_prime' the first value of variable_list is used. It should be taken from the list Bunch.get_axes()

    For 'mean', the first value in variable_list is used. It should be taken from the list Bunch.hit_get_variables()

    For others, variable_list should be a list taken from Bunch.get_axes()

    E.g. bunch.get('emittance', ['x','y']) would get emittance x y

    E.g. bunch.get('mean', ['x','px','z']) would return mean of x; px and z are ignored
    """
    if not variable_string in Bunch.__get_dict:
      raise KeyError(variable_string+' not available. Options are '+str(Bunch.get_variables()))
    else:
      return self.__get_dict[variable_string](self, variable_list)
  
  def list_get(dict_of_bunches, list_of_variables, list_of_axis_lists):
    """
    Get a list of lists of variables from each bunch in the dict_of_bunches

    - dict_of_bunches   = dict of bunches from which the lists will be taken
    - list_of_variables = list of variables that will be used in the calculation
    - list_of_axis_lists = axis_list that will be used in the calculation of the 
        corresponding variable

    E.g. list_get(my_dict_of_bunches, ['mean', 'emittance'], [['z'],['x','y']])
      would calculate a list of two arrays: (i) mean z; (ii) emittance x y

    Output is sorted by the first variable in the list. This might be useful to interface
    with E.g. a plotting package
    """
    values = []
    for dummy in list_of_variables:
      values.append([])
    for key, bunch in dict_of_bunches.items():
      for i in range(len(list_of_variables)):
        values[i].append(bunch.get(list_of_variables[i], list_of_axis_lists[i]))
    Common.multisort(values)
    return values
  list_get = staticmethod(list_get)

  def get_variables():
    """Return a list of variables suitable for calls to Bunch.get"""
    return Bunch.__get_list
  get_variables = staticmethod(get_variables)

  def hit_get_variables():
    """Return a list of variables suitable for calls to Bunch.get"""
    return Hit.get_variables()+['amplitude x', 'amplitude y', 'amplitude x y', 'amplitude ct', 'amplitude x y ct']
  hit_get_variables = staticmethod(hit_get_variables)

  def hit_write_builtin(self, file_type_string, file_name, user_comment=None):
    """
    Write the hits in the bunch using some built-in format to the file file_name

    - file_type_string = string that controls which predefined file type will be used
    - file_name = string that defines the file name
    - user_comment = comment to be included in file header (e.g. problem title)
    """
    if not file_type_string in Hit.file_types(): raise IOError('Attempt to write file of unknown file type '+str(file_type_string)+' - try one of '+str(Hit.file_types()))
    Hit.write_list_builtin_formatted(self.__hits, file_type_string, file_name, user_comment)
    return
  
  def hit_write_builtin_from_dict(dict_of_bunches, file_type_string, file_name, user_comment=None):
    """
    Write the hits in the dict of bunches using some built-in format to the file file_name

    - dict_of_bunches = list of hits
    - file_type_string = string that controls which predefined file type will be used
    - file_name = string that defines the file name
    - user_comment = comment to be included in file header (e.g. problem title)
    """
    if not file_type_string in Hit.file_types(): raise IOError('Attempt to write file of unknown file type '+str(file_type_string)+' - try one of '+str(Hit.file_types()))
    all_hits = []
    for key,value in dict_of_bunches.items():
      all_hits += value.hits()
    Hit.write_list_builtin_formatted(all_hits, file_type_string, file_name)
  hit_write_builtin_from_dict = staticmethod(hit_write_builtin_from_dict)
  
  def hit_write_user(self, format_list, format_units_dict, file_handle, separator=' ', comparator=None):
    """
    Write the hits in the bunch in some user defined format to file_handle, in an order defined by comparator

    - format_list = ordered list of strings from get_variables()
    - format_units_dict = dict of formats from format_list to units
    - file_handle = file handle made using e.g. open() command to which hits are written
    - separator = separator that is used to separate hits
    - comparator = comparator that is used for sorting prior to writing the file; if left as None, no sorting is performed

    e.g. aBunch.hit_write_user(['x','px','y','py'], ['x':'m','y':'m','px':'MeV/c','py':'MeV/c'], some_file, '@') would make output like
    0.001@0.002@0.001@0.002 
    0.003@0.004@0.003@0.004 
    in some_file
    """
    if not comparator==None:
      self.__hits.sort(comparator)
    for hit in self.__hits:
      hit.write_user_formatted(format_list, format_units_dict, file_handle, separator)

  def build_ellipse_2d(beta, alpha, emittance, p, mass, geometric):
    """
    Build a 2x2 ellipse matrix, given by
    For geometric = true

    - var(x, x)  = beta*emittance
    - var(x, x') = alpha*emittance
    - var(x',x') = gamma*emittance

    For geometric = false

    - var(x, x ) = beta*emittance*mass/p
    - var(x, px) = alpha*emittance*mass
    - var(px,px) = gamma*emittance*mass*p
    """
    config.has_numpy()
    cov = matrix(numpy.zeros((2,2)))
    gamma = (1.+alpha**2)/beta
    if beta <= 0.:
      raise ValueError("Beta "+str(beta)+" must be positive")
    if emittance <= 0.:
      raise ValueError("Emittance "+str(emittance)+" must be positive")
    if geometric:
      cov[0,0] = beta *emittance
      cov[1,0] = -alpha*emittance
      cov[0,1] = cov[1,0]
      cov[1,1] = gamma*emittance
    if not geometric:
      cov[0,0] = beta *emittance*mass/p
      cov[1,0] = -alpha*emittance*mass
      cov[0,1] = cov[1,0]
      cov[1,1] = gamma*emittance*mass*p
    return cov
  build_ellipse_2d = staticmethod(build_ellipse_2d)

  def build_MR_ellipse():
    """
    Not implemented
    """
#    Build a 6x6 ellipse using the Mais-Ripken parameterisation - not implemented
    raise NotImplementedError('Mais-Ripken methods will be released later')
  build_MR_ellipse = staticmethod(build_MR_ellipse)
  
  def build_ET_ellipse():
    """
    Not implemented
    """
#    Build a 6x6 ellipse using the Edwards-Teng parameterisation
    raise NotImplementedError('Edwards-Teng methods will be released later')
  build_ET_ellipse = staticmethod(build_ET_ellipse)

  def build_ellipse_from_transfer_matrix( M ):
    """
    Not implemented
    """
#    Build an ellipse using the transfer matrix M such that M.T() * ellipse * M = ellipse
    raise NotImplementedError('This function not ready yet')
  build_ellipse_from_transfer_matrix = staticmethod(build_ellipse_from_transfer_matrix)

  def build_penn_ellipse(emittance_t, mass, beta_t, alpha_t, p, Ltwiddle_t, bz, q):
    """
    Build an ellipse using Penn formalism for solenoids. 

    - emittance_t = nominal beam emittance
    - mass        = particle mass
    - beta_t      = transverse beta function
    - alpha_t     = transverse alpha function
    - p           = reference momentum
    - Ltwiddle_t  = normalised canonical angular momentum
    - bz          = magnetic field strength
    - q           = particle charge

    Output ellipse is a 4*4 matrix with elements v_ij where i,j indexes the vector (x,px,y,py)
    """
    if beta_t <= 0.:
      raise ValueError("Beta "+str(beta_t)+" must be positive")
    if emittance_t <= 0.:
      raise ValueError("Emittance "+str(emittance_t)+" must be positive")
    if mass <= 0.:
      raise ValueError("Mass "+str(mass)+" must be positive")

    k       =  Common.constants['c_light']*bz/2./p
    gamma_t =  (1+alpha_t*alpha_t+(beta_t*k - Ltwiddle_t)*(beta_t*k-Ltwiddle_t))/beta_t
    s_xx    =  emittance_t*mass*beta_t/p
    s_xpx   = -emittance_t*mass*alpha_t
    s_pxpx  =  emittance_t*mass*p*gamma_t
    s_xpy   = -emittance_t*mass*(beta_t*k-Ltwiddle_t)*q
    covariance_matrix = numpy.matrix([
    [s_xx,   s_xpx,    0.,    s_xpy],
    [s_xpx, s_pxpx,-s_xpy,        0],
    [   0., -s_xpy,  s_xx,    s_xpx],
    [s_xpy,     0., s_xpx,   s_pxpx],
    ])
    return covariance_matrix
  build_penn_ellipse = staticmethod(build_penn_ellipse)

  def histogram(self, x_axis_string, x_axis_units='', y_axis_string='', y_axis_units='', nx_bins=None, ny_bins=None, xmin=None, xmax=None, ymin=None, ymax=None):
    """
    Returns a binned 1D or 2D histogram of hits in the bunch (but doesnt draw anything or call any plotting package).

    - x_axis_string = string for call to get_hit_variables()
    - x_axis_units  = units for x axis
    - y_axis_string = string for call to get_hit_variables(). If string is empty, makes a 1D histogram
    - y_axis_units  = units for y axis
    - nx_bins       = force histogram to use this number of bins for the x-axis rather than choosing number of bins itself
    - ny_bins       = force histogram to use this number of bins for the y-axis rather than choosing number of bins itself
    - xmin          = float that overrides auto-detection of minimum x-axis value
    - xmax          = float that overrides auto-detection of maximum x-axis value
    - ymin          = float that overrides auto-detection of minimum y-axis value
    - ymax          = float that overrides auto-detection of maximum y-axis value

    Return value is a list of bin weights for a 1D histogram or a list of lists of bin weights for a 2D histogram
    """
    config.has_numpy()
    weights              = self.list_get_hit_variable(['weight'], [''])[0]
    x_points             = self.list_get_hit_variable([x_axis_string], [x_axis_units])[0]
    y_bins               = None
    if xmin!=None: xmin*=Common.units[x_axis_units]
    if xmax!=None: xmax*=Common.units[x_axis_units]
    if ymin!=None: ymin*=Common.units[y_axis_units]
    if ymax!=None: ymax*=Common.units[y_axis_units]
    if y_axis_string=='': 
      (nx_bins, ny_bins, dummy) = Common.n_bins(len(x_points), nx_bins, 1)
    else:
      y_points                  = self.list_get_hit_variable([y_axis_string], [y_axis_units])[0]
      (nx_bins, ny_bins, dummy) = Common.n_bins(len(y_points), nx_bins, ny_bins, 2)
      y_bins                    = Common.get_bin_edges(y_points, ny_bins, ymin, ymax)
    x_bins = Common.get_bin_edges(x_points, nx_bins, xmin, xmax)
    return self.histogram_var_bins(x_axis_string, x_bins, x_axis_units, y_axis_string, y_bins, y_axis_units)

  def histogram_var_bins(self, x_axis_string, x_bins, x_axis_units='', y_axis_string='', y_bins=None, y_axis_units=''):
    """
    Returns a binned histogram of hits in the bunch.

    Requires numpy

    - x_axis_string = string for call to get_hit_variables()
    - x_bins        = list of bin edges used to generate the histogram
    - x_axis_units  = units for x axis
    - y_axis_string = string for call to get_hit_variables()
    - y_bins        = list of bin edges used to generate the histogram
    - y_axis_units  = units for y axis

    Return value is a tuple containing ((bin weights array),x_bins,y_bins). The bin weights array is always nx*ny, with ny defaulting to 1 in the case of a 1d histogram.
    """
    config.has_numpy()
    weights    = self.list_get_hit_variable(['weight'], [''])[0]
    x_points = self.list_get_hit_variable([x_axis_string], [x_axis_units])[0]
    if y_axis_string == '':
      return Common.histogram(x_points, x_bins, weights=weights)
    else:
      y_points = self.list_get_hit_variable([y_axis_string], [y_axis_units])[0]
      return Common.histogram(x_points, x_bins, y_points, y_bins, weights=weights)

  def root_histogram(self, x_axis_string, x_axis_units='', y_axis_string='', y_axis_units='', nx_bins=None, ny_bins=None, canvas=None, xmin=None, xmax=None, ymin=None, ymax=None,
                        line_color=rg.line_color, line_style=rg.line_style, line_width=rg.line_width, fill_color=rg.fill_color, stats=rg.stats, hist_title_string='', draw_option=''):
    """
    Prints a 1D or 2D histogram of hits in the bunch. Axes are automatically detected
    to encapsulate all data.

    Needs correct root installation.

    - x_axis_string = string for call to get_hit_variables()
    - x_axis_units  = units for x axis
    - y_axis_string = string for call to get_hit_variables(). If string is empty, makes a 1D histogram
    - y_axis_units  = units for y axis
    - nx_bins       = force root_histogram to use this number of bins for the x-axis rather than choosing number of bins itself
    - ny_bins       = force root_histogram to use this number of bins for the y-axis rather than choosing number of bins itself
    - canvas        = if canvas=None, root_histogram will create a new tcanvas and plot histograms on that
                 else will plot on the existing canvas, attempting to plot on existing axes
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

    e.g. bunch.root_histogram('x', 'cm', 'py', 'GeV/c') will histogram x vs py. 
    Returns a tuple of the (canvas, histogram)
    """
    weights  = []
    num_events = float(len(self))
    x_points = self.list_get_hit_variable([x_axis_string], [x_axis_units])[0]
    if y_axis_string == '' and nx_bins==None:
      nx_bins = int(num_events/10.)
    if not y_axis_string == '' and draw_option=='': 
      draw_option = 'COL'
      y_points = self.list_get_hit_variable([y_axis_string], [y_axis_units])[0]
      if nx_bins == None: nx_bins = int(num_events**0.7/10.)
      if ny_bins == None: ny_bins = int(num_events**0.7/10.)
    else: y_points = []
    for key in self.__hits:
      weights.append(key.get('weight'))
    if not x_axis_units == '': x_axis_units = " ["+x_axis_units+"]"
    if not y_axis_units == '': y_axis_units = " ["+y_axis_units+"]"
    x_name   = x_axis_string+x_axis_units
    y_name   = y_axis_string+y_axis_units
    num_evts = 0.
    for hit in self.__hits: 
      if abs(hit.get('weight')) > 0.: num_evts += 1.
    name = x_axis_string
    if not y_axis_string == '': name  += ":"+y_axis_string
    if canvas == '' or canvas == None: canvas = Common.make_root_canvas(name)
    else:
      draw_option += 'same'
      canvas.cd()
    hist = Common.make_root_histogram(name, x_points, x_name, nx_bins, y_points, y_name, ny_bins, weights, xmin, xmax, ymin, ymax,
                        line_color, line_style, line_width, fill_color, stats, hist_title_string)
    hist.SetStats(False)
    hist.Draw(draw_option)
    canvas.Update()
    return (canvas, hist)

  def root_scatter_graph(self, x_axis_string, y_axis_string, x_axis_units='', y_axis_units='', include_weightless=True, canvas=None, xmin=None, xmax=None, ymin=None, ymax=None, 
                    line_color=rg.line_color, line_style=rg.line_style, line_width=rg.line_width, fill_color=rg.graph_fill_color, hist_title_string=''):
    """
    Prints a 2d scatter plot of Hit.get(...) data over a dict of bunches.

    Needs correct root installation.

    - x_axis_string = string for call to Bunch.get_hit_variable() used to calculate x-values
    - x_axis_units  = units for x axis
    - y_axis_string = string for call to Bunch.get_hit_variable() used to calculate y-values
    - y_axis_units  = units for y axis
    - include_weightless = set to True to plot hits with <= 0. weight
    - canvas = if canvas=None, root_graph will create a new tcanvas and plot graphs on that
                 else will plot on the existing canvas, attempting to plot on existing axes
    - xmin       = float that overrides auto-detection of minimum x-axis value
    - xmax       = float that overrides auto-detection of maximum x-axis value
    - ymin       = float that overrides auto-detection of minimum y-axis value
    - ymax       = float that overrides auto-detection of maximum y-axis value
    - line_color = int that sets the line colour of the histogram
    - line_style = int that sets the line style of the histogram
    - line_width = int that sets the line width of the histogram
    - fill_color = int that sets the fill color of the histogram
    - hist_title_string = specify the string that will appear as a title on the canvas
    - fit_ellipse = set to True to draw a fitted ellipse  corresponding to the relevant covariances matrix

    e.g. bunch.root_scatter_graph('x', 'p', 'cm', 'MeV/c') will graph x vs p. 
    Returns a tuple of (canvas, histogram, graph) where the histogram contains
    the axes.
    """
    fit_ellipse=False # hard coded - I am not sure this is the right way
    x_points = []
    y_points = []
    for hit in self:
      if abs(hit['weight'])>Common.float_tolerance or include_weightless:
        x_points.append(self.get_hit_variable(hit, x_axis_string)/Common.units[x_axis_units])
        y_points.append(self.get_hit_variable(hit, y_axis_string)/Common.units[y_axis_units])
    name = x_axis_string+":"+y_axis_string
    if not x_axis_units == '': x_axis_string += " ["+x_axis_units+"]"
    if not y_axis_units == '': y_axis_string += " ["+y_axis_units+"]"
    graph = Common.make_root_graph(name, x_points, x_axis_string, y_points, y_axis_string, True, xmin, xmax, ymin, ymax, 
                    line_color, line_style, line_width, fill_color, hist_title_string)
    if canvas == '' or canvas==None:
      canvas = Common.make_root_canvas(name)
      graph[0].SetStats(False)
      graph[0].Draw()
    else:
      canvas.cd()
    graph[1].Draw('p')
    if fit_ellipse:
      points = [(x_points[i], y_points[i]) for i in range(len(x_points))]
      mean, cov = Common.fit_ellipse(points, -1., self.list_get_hit_variable(['weight'])[0], 1, True)
      func = Common.make_root_ellipse_function(mean, cov, [1.],
                                               graph[0].GetXaxis().GetXmin(),
                                               graph[0].GetXaxis().GetXmax(),
                                               graph[0].GetYaxis().GetXmin(),
                                               graph[0].GetYaxis().GetXmax())
      func.Draw('SAME')
      _function_persistent.append(fit_func)
    canvas.Update()
    return (canvas, graph[0], graph[1])
  
  def root_graph(bunches, x_axis_string, x_axis_list, y_axis_string, y_axis_list, x_axis_units='', y_axis_units='', canvas='', comparator=None, xmin=None, xmax=None, ymin=None, ymax=None, 
                 line_color=rg.line_color, line_style=rg.line_style, line_width=rg.line_width, fill_color=rg.graph_fill_color, hist_title_string=''):
    """
    Prints a graph of Bunch.get(...) data over a set of bunches and returns the root canvas.

    Needs correct root installation.

    - bunches       = either a dict or a list of bunches
    - x_axis_string = string for call to Bunch.get() used to calculate x axis variables
    - x_axis_list   = list of variables for call to Bunch.get() used to calculate x axis variables
    - x_axis_units  = units for x axis
    - y_axis_string = string for call to Bunch.get() used to calculate y axis variables
    - y_axis_list   = list of variables for call to Bunch.get() used to calculate y axis variables
    - y_axis_units  = units for y axis
    - canvas        = if canvas=None, root_graph will create a new tcanvas and plot graphs on that
                        else will plot on the existing canvas, attempting to plot on existing axes
    - comparator    = comparator of bunch1, bunch2 - if none given, will sort by x-axis value
    - xmin          = float that overrides auto-detection of minimum x-axis value
    - xmax          = float that overrides auto-detection of maximum x-axis value
    - ymin          = float that overrides auto-detection of minimum y-axis value
    - ymax          = float that overrides auto-detection of maximum y-axis value
    - line_color    = int that sets the line colour of the histogram
    - line_style    = int that sets the line style of the histogram
    - line_width    = int that sets the line width of the histogram
    - fill_color    = int that sets the fill color of the histogram
    - hist_title_string = specify the string that will appear as a title on the canvas

    e.g. root_graph(bunch_dict, 'mean', ['x'], 'emittance', ['x','y'], 'cm', 'mm') will graph mean x vs emittance x y. 
    Returns a tuple of (canvas, histogram, graph) where the histogram contains the axes
    """
    x_points        = []
    y_points        = []
    list_of_bunches = []
    try:    list_of_bunches = list(bunches.values())
    except: list_of_bunches = bunches
    if comparator != None:
      list_of_bunches.sort(comparator)
    for i, bunch in enumerate(list_of_bunches):
      try:
          x_points.append(bunch.get(x_axis_string, x_axis_list)/Common.units[x_axis_units])
          y_points.append(bunch.get(y_axis_string, y_axis_list)/Common.units[y_axis_units])
      except Exception:
          if len(x_points) > len(y_points):
              x_points.pop(-1)
          sys.excepthook(*sys.exc_info())
          print('Failed to get data from bunch', i)
    x_axis_string += "( "
    y_axis_string += "( "
    for value in x_axis_list: x_axis_string += value+" "
    for value in y_axis_list: y_axis_string += value+" "
    x_axis_string += ")"
    y_axis_string += ")"
    name = x_axis_string+":"+y_axis_string
    if not x_axis_units == '': x_axis_string += " ["+x_axis_units+"]"
    if not y_axis_units == '': y_axis_string += " ["+y_axis_units+"]"
    graph = Common.make_root_graph(name, x_points, x_axis_string, y_points, y_axis_string, comparator==None, xmin, xmax, ymin, ymax, 
                                   line_color, line_style, line_width, fill_color, hist_title_string)
    if canvas == '' or canvas == None:
      canvas = Common.make_root_canvas(name)
      graph[0].SetStats(False)
      graph[0].Draw()
    else:
      canvas.cd()
    graph[1].Draw('l')
    canvas.Update()
    return (canvas, graph[0], graph[1])
  root_graph = staticmethod(root_graph)

  def matplot_histogram(self, x_axis_string, x_axis_units='', y_axis_string='', y_axis_units='', canvas=None, comparator=None):
    """
    Prints a 1D or 2D histogram of hits in the bunch. Axes are automatically detected
    to encapsulate all data. Use Bunch.cut(...) to shrink the axes.

    Needs correct matplot installation.

    - x_axis_string = string for call to get_hit_variables()
    - x_axis_units  = units for x axis
    - y_axis_string = string for call to get_hit_variables(). If string is empty, makes a 1D histogram
    - y_axis_units  = units for y axis
    - comparator    = comparator of bunch1, bunch2 - if none given, will sort by x-axis value

    e.g. bunch.matplot_histogram('x', 'cm', 'py', 'GeV/c') will histogram x vs py. 

    To display plots, call Common.wait_for_matplot() - script waits until all matplot windows are closed
    """
    weights    = []
    
    num_evts = 0.
    for hit in self.__hits:
      if abs(hit.get('weight')) > 0.: num_evts += 1.
    n_bins = num_evts/10.+1.;
    
    x_points   = self.list_get_hit_variable([x_axis_string], [x_axis_units])[0]
    if not y_axis_string == '': 
      y_points = self.list_get_hit_variable([y_axis_string], [y_axis_units])[0]
      n_bins = num_evts**0.5/10.+1.;
    else: y_points = []
    for key in self.__hits:
      weights.append(key.get('weight'))
    if not x_axis_units == '': x_axis_units = " ["+x_axis_units+"]"
    if not y_axis_units == '': y_axis_units = " ["+y_axis_units+"]"
    x_name   = x_axis_string+x_axis_units
    y_name   = y_axis_string+y_axis_units
    sort = True
    if comparator != None:
      sort = False
    figure = Common.make_matplot_histogram( x_points, x_name, int(n_bins), y_points, y_name, int(n_bins), weight_list=weights)

  def matplot_scatter_graph(self, x_axis_string, y_axis_string, x_axis_units='', y_axis_units='', include_weightless=True):
    """
    Prints a 2d scatter plot of Hit.get(...) data over a dict of bunches.

    Needs correct matplot installation.

    - x_axis_string = string for call to Bunch.get_hit_variable() used to calculate x-values
    - x_axis_units  = units for x axis
    - y_axis_string = string for call to Bunch.get_hit_variable() used to calculate y-values
    - y_axis_units  = units for y axis
    - include_weightless = set to True to plot hits with <= 0. weight

    e.g. bunch.matplot_scatter_graph('x', 'cm', 'p', 'MeV/c') will graph x vs p. 

    To display plots, call Common.wait_for_matplot() - script waits until all matplot windows are closed
    """
    x_points = []
    y_points = []
    for hit in self:
      if abs(hit['weight'])>Common.float_tolerance or include_weightless:
        x_points.append(self.get_hit_variable(hit, x_axis_string)/Common.units[x_axis_units])
        y_points.append(self.get_hit_variable(hit, y_axis_string)/Common.units[y_axis_units])
    if not x_axis_units == '': x_axis_string += " ["+x_axis_units+"] "
    if not y_axis_units == '': y_axis_string += " ["+y_axis_units+"] "
    graph = Common.make_matplot_scatter(x_points, x_axis_string, y_points, y_axis_string)
  
  def matplot_graph(bunches, x_axis_string, x_axis_list, y_axis_string, y_axis_list, x_axis_units='', y_axis_units='', comparator=None):
    """
    Prints a graph of Bunch.get(...) data over a dict of bunches.

    Needs correct matplot installation.

    - x_axis_string = string for call to Bunch.get() used to calculate x axis variables
    - x_axis_list   = list of variables for call to Bunch.get() used to calculate x axis variables
    - y_axis_string = string for call to Bunch.get() used to calculate y axis variables
    - y_axis_list   = list of variables for call to Bunch.get() used to calculate y axis variables
    - x_axis_units  = units for x axis
    - y_axis_units  = units for y axis
    - comparator    = comparator of bunch1, bunch2 - if none given, will sort by x-axis value

    e.g. bunch.matplot_graph('mean', ['x'], 'cm', 'emittance', ['x','y'], 'mm') will graph mean x vs emittance x y. 

    To display plots, call Common.wait_for_matplot() - script waits until all matplot windows are closed
    """
    x_points = []
    y_points = []
    try:    list_of_bunches = list(bunches.values())
    except: list_of_bunches = bunches
    if comparator != None:
      list_of_bunches.sort(comparator)
    for bunch in list_of_bunches:
      x_points.append(bunch.get(x_axis_string, x_axis_list)/Common.units[x_axis_units])
      y_points.append(bunch.get(y_axis_string, y_axis_list)/Common.units[y_axis_units])
    x_axis_string += "( "
    y_axis_string += "( "
    for value in x_axis_list: x_axis_string += value+" "
    for value in y_axis_list: y_axis_string += value+" "
    x_axis_string += ") "
    y_axis_string += ") "
    if not x_axis_units == '': x_axis_string += " ["+x_axis_units+"] "
    if not y_axis_units == '': y_axis_string += " ["+y_axis_units+"] "
    graph = Common.make_matplot_graph(x_points, x_axis_string, y_points, y_axis_string)
    return graph
  matplot_graph = staticmethod(matplot_graph)


#privates
  def __mean_for_get(self, variable_list):
    return self.mean(variable_list)[variable_list[0]]
  
  def __weight_for_get(self, variable_list):
    return self.bunch_weight()

  def __ang_mom_for_get(self, variable_list):
    return self.get_kinetic_angular_momentum()

  def __dispersion_for_get(self, variable_list):
    return self.get_dispersion(variable_list[0])
  
  def __dispersion_prime_for_get(self, variable_list):
    return self.get_dispersion_prime(variable_list[0])

  def __cov_mat_picker(self, axis_list):
    config.has_numpy()
    if self.__covs == None: return None
    covs      = numpy.zeros( (2*len(axis_list),2*len(axis_list) ))
    ind = []
    for axis in axis_list:
      ind.append( Bunch.__axis_list.index( axis ) )
    for i in range( len(ind) ):
      for j in range( len(ind) ):
        covs[2*i,  2*j]   = self.__covs[2*ind[i],   2*ind[j]]
        covs[2*i+1,2*j]   = self.__covs[2*ind[i]+1, 2*ind[j]]
        covs[2*i+1,2*j+1] = self.__covs[2*ind[i]+1, 2*ind[j]+1]
        covs[2*i,  2*j+1] = self.__covs[2*ind[i],   2*ind[j]+1]
    return covs

  def __mean_picker(self, var_list):
    if self.__means == None or self.__means == {}: return {}
    means = {}
    all_list = Bunch.axis_list_to_covariance_list(var_list)
    try:
      for var in all_list: means[var] = self.__means[var]
    except:
      return {}
    return means
    
  __number_of_header_lines = {'icool_for009':3, 'icool_for003':2, 'g4beamline_bl_track_file':0, 'g4beamline_bl_track_file_2':0, 'zgoubi':0, 'turtle':0, 'madx':0,'mars_1':0, 'maus_json_virtual_hit':0, 'maus_json_primary':0, 'opal_loss':1}
  __axis_list              = ['x','y','z','t', 'ct']
  __get_dict               = {'angular_momentum':__ang_mom_for_get, 'emittance':get_emittance, 'dispersion':__dispersion_for_get, 
                             'dispersion_prime':__dispersion_prime_for_get, 'beta':get_beta, 'alpha':get_alpha, 'gamma':get_gamma, 
                             'moment':moment, 'mean':__mean_for_get, 'bunch_weight':__weight_for_get, 'standard_deviation':standard_deviation}
  __geometric_momentum     = False

  __get_list               = []
  for key,value in __get_dict.items():
    __get_list.append(key)

  def bunch_overview_doc(verbose = False):
    """Creates some summary documentation for the Bunch class. If verbose is True then will also print any functions or data not included in summary"""
    name_list = ['initialise', 'transforms', 'hit', 'moments', 'weights', 'twiss', 'twiss_help', 'io', 'ellipse', 'root', 'matplotlib', 'generic graphics']
    function_list = {
    'initialise' : ['new_dict_from_read_builtin', 'new_from_hits', 'new_from_read_builtin', 'new_from_read_user', 'new_list_from_read_builtin', 'new_hit_shell', 'copy', 'deepcopy'],    
    'transforms' : ['abelian_transformation', 'period_transformation', 'transform_to', 'translate'],
    'hit'        : ['get', 'get_hit_variable', 'get_hits', 'hit_equality', 'list_get', 'list_get_hit_variable', 'append', 'hits', 'hit_get_variables', 'get_variables', 'get_amplitude'],
    'moments'    : ['mean', 'moment', 'covariance_matrix'],
    'weights'    : ['bunch_weight', 'clear_global_weights', 'clear_local_weights', 'clear_weights', 'cut', 'transmission_cut', 'conditional_remove'],  
    'twiss'      : ['get_emittance', 'get_beta', 'get_alpha', 'get_gamma', 'get_emittance', 'get_canonical_angular_momentum', 'get_dispersion', 'get_dispersion_prime','get_dispersion_rsquared', 'get_kinetic_angular_momentum'],
    'twiss_help' : ['convert_string_to_axis_list', 'covariances_set', 'means_set', 'momentum_variable', 'set_geometric_momentum', 'set_covariance_matrix', 'get_axes', 'get_geometric_momentum', 'axis_list_to_covariance_list'],
    'io'         : ['hit_write_builtin', 'hit_write_builtin_from_dict', 'hit_write_user', 'setup_file', 'read_maus_file'],
    'ellipse'    : ['build_ellipse_2d', 'build_ellipse_from_transfer_matrix', 'build_penn_ellipse'], #, 'build_ET_ellipse', 'build_MR_ellipse'
    'root'       : ['root_graph',    'root_histogram',    'root_scatter_graph'],    
    'matplotlib' : ['matplot_graph', 'matplot_histogram', 'matplot_scatter_graph'],
    'generic graphics': ['histogram', 'histogram_var_bins'],
    }
    function_doc = {
    'initialise':'Functions that can be used to initialise a Bunch in various different ways:',
    'transforms':'Functions that transform all data in the bunch in some way:',
    'hit':'Functions to examine individual hits within the bunch:',
    'moments':'Functions to calculate beam moments:',
    'weights':'Functions to access and modify statistical weights:',
    'twiss':'Functions to calculate Twiss parameters, etc, in the bunch:',
    'twiss_help':'Helper functions to aid Twiss parameter calculation:',
    'io':'Output and some input helper functions:',
    'ellipse':'Functions to calculate beam ellipses based on Twiss parameters etc:',
    'root':'Interfaces to root plotting library:',
    'matplotlib':'Interfaces to matplotlib plotting library:',
    'generic graphics':'General algorithms to support graphics functions:',
    }
    bunch_doc = """
Bunch class is a container class for a set of hits. The main purpose is to store a set of hits that are recorded at an output station in some tracking code. Functions are provided to calculate Twiss parameters, RMS emittances etc for this bunch. List of functions:
"""
    dir_bunch = dir(Bunch)
    if verbose:
      print('The following functions and data are in Bunch but not in overview_doc:')
      for func in dir_bunch:
        found = False
        for func_sublist in list(function_list.values()):
          if func in func_sublist: found = True
        if not found: print(func, end=' ')
      print('\n')

      print('The following functions and data are in bunch_overview_doc but not in Bunch:')
      for func_sublist in list(function_list.values()):
        for func in func_sublist:
          if func not in dir_bunch:
            print(func, end=' ')
      print()

    doc = bunch_doc    
    for key in name_list:
      doc = doc + function_doc[key]+'\n'
      for item in function_list[key]:
        doc = doc+'  '+item+'\n'
    __doc__ = doc
    return doc
  bunch_overview_doc = staticmethod(bunch_overview_doc)

#summary documentation
__doc__ = Bunch.bunch_overview_doc()


