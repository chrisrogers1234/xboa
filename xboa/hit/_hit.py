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

import copy
import xboa.common as Common
import xboa.common.config as config
import math
import gzip
import warnings
import array
try:
  import json
except ImportError:
  pass

from xboa.core import Hitcore
import xboa.hit.factory
try:
  import numpy
  from numpy import matrix
except ImportError:
  pass #safety provided by calls to Common.has_numpy whenever I use this library

class BadEventError(IOError):
    """
    BadEventError is raised if Hit reads a bad 
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class Hit(object):
  """
  Represents a particle at a point in some phase space. Hit contains functions for i/o, 
  as well as accessors for rectangular or cylindrical coordinate systems and functions to
  perform translations, abelian transformations etc.

  Hit has the following variables (stored for real in C struct Hitcore)

  - **x** transverse horizontal position
  - **y** transverse vertical position
  - **z** longitudinalposition
  - **t** time
  - **px** transverse horizontal component of momentum
  - **py** transverse vertical component of momentum
  - **pz** longitudinal component of momentum
  - **energy** total energy
  - **local_weight** local statistical weight (for a particular hit)
  - **mass** particle mass
  - **bx** horizontal component of magnetic field
  - **by** vertical component of magnetic field
  - **bz** longitudinal component of magnetic field
  - **ex** x component of electric field
  - **ey** y component of electric field
  - **ez** z component of electric field
  - **sx** x component of spin vector
  - **sy** y component of spin vector
  - **sz** z component of spin vector
  - **path_length** total distance traversed by a particle
  - **proper_time** proper time of the particle
  - **e_dep** energy deposited, as registered by a Monte Carlo code
  - **charge** particle charge, in units of electron charge
  - **station** output plane index
  - **pid** PDG particle ID (am I an electron? am I a proton?)
  - **status** is the particle track okay? (code dependent)
  - **spill** indexes the spill (for MICE)
  - **event_number** indexes the event
  - **particle_number** indexes the particle track within the event

  Additionally,

  - global_weight is a global statistical weight (for a particular particle).
    All hits with the same (spill, event_number, particle_number) will register
    the same global weight.
  """
  #this lets python define a global vtable rather than one for each instance
  __slots__ = ['__hitcore']

  def __init__(self):
    """Initialise to an empty event. Alternatively use static initialisers defined below - I prefer static initialisers"""
    self.__hitcore = Hitcore()

  def __repr__(self):
    """Formatting for print command"""
    return 'Hit.new_from_dict('+repr(self.dict_from_hit())+')'

  def __copy__(self):
    """Shallow copy i.e. copy as reference"""
    hitCopy = self
    return hitCopy

  def __deepcopy__(self, target):
    """Deep copy i.e. copy as data"""
    target = Hit.new_from_dict(self.dict_from_hit())
    return target
    
  def __eq__(self, target, float_tolerance=Common.float_tolerance):
    """Test for equality of data values between self and target"""
    if type(self) != type(target):       return False
    for key in self.__hitcore.get_variables():
      if abs(self.__hitcore.get(key) - target.__hitcore.get(key)) > float_tolerance: return False
    return True

  def __ne__(self, target, float_tolerance=Common.float_tolerance):
    """Test for inequality of data values between self and target"""
    return not self.__eq__(target, float_tolerance)
  
  def __getitem__(self, variable):
    """Mimic some aspects of dict"""
    return self.get(variable)
  
  def __setitem__(self, variable, value):
    """Mimic some aspects of dict"""
    return self.set(variable, value)

  def __del__(self):
    """Clean up"""
    del(self.__hitcore)
  
  # static initialisers #############
  def new_from_dict(set_dict, mass_shell_string=''):
    """
    Static function returns a new hit object, setting data using string:value dict. Then forces E^2=p^2+m^2 by changing mass_shell_string.

    - set_dict = dict of string:value pairs where strings are from set_variables()
    - mass_shell_string = string from list mass_shell_variables that references the value that will be changed to force E^2=p^2+m^2

    e.g. myHit = Hit.new_from_dict({'x':5, 'y':0, 'z':100, 'px':0, 'py':5, 'pz':200, 'pid':-13}, 'energy' )
    """
    my_hit = Hit()
    for k,v in set_dict.items():
      my_hit.set(k, v)
    if(mass_shell_string != ''):
      my_hit.mass_shell_condition(mass_shell_string)
    return my_hit
  new_from_dict = staticmethod(new_from_dict)

  def new_from_read_builtin(format, filehandle):
    """
    Static function returns a new hit object, read from filehandle with a built-in format

    - format     = string from the list file_types() that defines the format of the input
    - filehandle = filehandle from which the hit object will be read

    e.g. myHit = Hit.new_from_read_builtin('zgoubi', myfile)
    Note that this will read one event, typically corresponding to one line in <filehandle>
    """
    if format == 'opal_loss':
      hit = Hit()
      opal_read = hit.__read_opal_loss_file(filehandle)        
      return hit
    else:
      return xboa.hit.factory.BuiltinHitFactory(format, filehandle).make_hit()
  new_from_read_builtin = staticmethod(new_from_read_builtin)

  def new_from_read_user(format_list, format_units_dict, filehandle, mass_shell_condition=''):
    """
    Static function returns a new hit object sets data using string/value pairs from set_dict and forces E^2=p^2+m^2 by changing mass_shell_string

    - format_list       = ordered list of variables from get_variables() that contains the particle variables on each line of your input file
    - format_units_dict = dict of variables:units that are used to transform to internal system of units
    - filehandle        = file handle, created using e.g. filehandle = open('for009.dat')

    e.g. myHit = Hit.new_from_read_user(['x','y','z','px','py','pz'], {'x':'mm', 'y':'mm', 'z':'mm', 'px':'MeV/c', 'py':'MeV/c', 'pz':'MeV/c'}, my_input_file)
    """
    return xboa.hit.factory.UserHitFactory(
              format_list,
              format_units_dict,
              filehandle,
              mass_shell_condition
        ).make_hit()
  new_from_read_user = staticmethod(new_from_read_user)

  @classmethod
  def new_list_from_maus_root(cls, format, root_tree, entry_number = 0):
    """
    Static function returns a list of hit objects found in the spill

    - format       = type to take from the maus file.
    - root_tree    = TTree containing maus spill data, of type ROOT.TTree
    - entry_number = index of the spill entry in the TTree

    Returns a list of hit objects. Station number will be taken from the relevant maus_type. event_number will be given by the spill_number. track_number will be given by
    the index on mc_events or recon_events
    """
    fac = xboa.hit.factory.factory.MausRootHitFactory(format, root_tree, entry_number)
    hit_list = [hit for hit in fac.hit_generator()]
    return hit_list

  @classmethod
  def new_list_from_maus_json(cls, format, filehandle):
    """
    Static function returns a list of hit objects found in the spill

    - format = type to take from the maus file.
    - filehandle = filehandle containing json formatted data

    Returns a list of hit objects. Station number will be taken from the 
    relevant maus_type. event_number will be given by the spill_number. 
    track_number will be given by the index on mc_events or recon_events.
    """
    fac = xboa.hit.factory.factory.MausJsonHitFactory(format, file_handle)
    hit_list = [hit for hit in fac.hit_generator()]
    return hit_list
    
  def copy(self):
    """Return a shallow copy of self (copying data as references)"""
    return self.__copy__()

  def deepcopy(self):
    """Return a deep copy of target (deep copying target's data to self as well)"""
    target = Hit()
    target = copy.deepcopy(self)
    return target

  # Transformations #################
  def get_vector(self, get_variable_list, origin_dict={}):
    """
    Return a numpy vector of data values taking data from get_variable_list, relative to some origin

    - get_variable_list = list of variable strings from get_variables()
    - origin_dict       = dict of variable strings to origin value; if not set, assumes 0

    e.g. transverse_vector = myHit.get_vector(['x', 'y', 'px', 'py'])
    """
    config.has_numpy()
    my_list = []
    for key in get_variable_list:
      if key in origin_dict: origin = origin_dict[key]
      else:                  origin = 0.
      my_list.append(self.get(key) - origin)
    return matrix(numpy.array(my_list))

  def translate(self, translation_dict, mass_shell_string):
    """
    Iterate over translation_dict and add the value in the dict to the value stored in Hit. Then force E^2 = p^2 + m^2

    - translation_dict = dict of strings from list set_variables() to floats
    - mass_shell_string = string from list mass_shell_variables()
    """
    for k,v in translation_dict.items():
      self.set(k, v+self.get(k))
    self.mass_shell_condition(mass_shell_string)

  def abelian_transformation(self, rotation_list, rotation_matrix, translation_dict={}, origin_dict={}, mass_shell_variable=''):
    """
    Perform an abelian transformation about the origin, i.e. V_out - O = R*(V_in-O) + T. 
    Then force E^2 = p^2 + m^2

    - rotation_list       = list of variables to be rotated
    - rotation_matrix     = matrix R
    - translation_dict    = dict of strings from set_variables() to floats. Becomes O
    - mass_shell_variable = string from list mass_shell_variables()
    - origin_dict         = dict of strings from set_variables() to floats. Becomes t

    e.g. hit.abelian_transformation(['x','px'], array[[1,0.5],[0,1]],{'x':10},'energy') will
    look like a drift space plus a translation
    """
    vector = (self.get_vector(rotation_list)).transpose()
    origin = copy.deepcopy(origin_dict)
    trans  = copy.deepcopy(translation_dict)
    for key in rotation_list:
      if not key in origin: origin[key] = 0
      if not key in trans:  trans [key] = 0
    for i in range( len(rotation_list) ):
      vector[i,0] -= origin[rotation_list[i]]
    vector = rotation_matrix*vector
    for i in range( len(rotation_list) ):
      self.set(rotation_list[i], float(vector[i,0]+trans[rotation_list[i]]+origin[rotation_list[i]]))
    self.mass_shell_condition(mass_shell_variable)
    return self

  def mass_shell_condition(self, variable_string, float_tolerance = 1.e-6):
    """
    Change variable represented by variable_string to force E^2 = p^2 + m^2

    - variable_string = string which should be one of the list mass_shell_variables().

    If mass shell condition cannot be obeyed, set variable to 0.0 and return False. Else return True
    """
    if(variable_string == ''):
      return
    px = self.get('px')
    py = self.get('py')
    pz = self.get('pz')
    e  = self.get('energy')
    m  = self.get('mass')
    if(variable_string == 'p'):
      self.set('p',  ( (e-m)*(e+m) )**0.5 )
    elif(variable_string == 'px'):#get direction right!
      val = (e*e-m*m-py*py-pz*pz)
      if val>float_tolerance:
        self.set('px', abs(val)**1.5/val )
      else:
        self.set('px', 0.)
        return False
    elif(variable_string == 'py'):
      val = (e*e-m*m-px*px-pz*pz)
      if val>float_tolerance:
        self.set('py', abs(val)**1.5/val )
      else:
        self.set('py', 0.)
        return False
    elif(variable_string == 'pz'):
      val = (e*e-m*m-px*px-py*py)
      if val>float_tolerance:
        self.set('pz', abs(val)**1.5/val )
      else:
        self.set('pz', 0.)
        return False
    elif(variable_string == 'energy'):
      self.set('energy', (m*m+px*px+py*py+pz*pz) **0.5 )
    else:
      raise IndexError('mass_shell_condition did not recognise \''+str(variable_string)+'\'. Options are '+str(self.__mass_shell_variables))
    return True

  # Manipulators ################

  def get(self, key):
    """
    Return the value referenced by key

    - key = string which should be one of the list get_variables()
    """
    try:
        return self.__hitcore.get(key)
    except Exception:
        pass
    if(key in self.__get_variables):
        return self.__get_variables[key](self)
    else:
        raise IndexError('Key \''+str(key)+'\' could not be found for Hit.get() - should be one of '+str(Hit.get_variables()))
  
  def set(self, key, value):
    """
    Set the value referenced by key

    - key   = string which should be one of the list get_variables()
    - value = float
    """
    try:
      self.__hitcore.set(key, value)
      return
    except: pass
    if(key in self.__set_variables):
      self.__set_variables[key](self, value)
    else: 
      raise IndexError('Key \''+str(key)+'\' could not be found for Hit.set() - should be one of '+str(Hit.set_variables()))

  def check(self, tolerance_float=1e-3):
    """Return True if mass shell condition is obeyed and pid is correct for the mass else return False"""
    pid = self.get('pid')
    if (not abs(pid) in Common.pdg_pid_to_mass) and (not pid in Hit.__bad_pids) and (not pid == 0):
      print('pid not recognised',self.get('pid'))
      return False
    if abs(pid) in list(Common.pdg_pid_to_mass.keys()):
      if abs(self.get('mass')-Common.pdg_pid_to_mass[abs(pid)]) > tolerance_float:
        print('Mass',self.get('mass'),'does not match pid',self.get('pid'))
        return False
    if  abs(round(self.get('p')**2 + self.get('mass')**2) - round(self.get('energy')**2))  > tolerance_float :
      return False
    return True

  def dict_from_hit(self):
    """
    Return a dict that uniquely defines the hit, so that new_from_dict(dict_from_hit(hit)) returns a copy of hit
    """
    my_dict = {}
    for key in self.__hitcore.set_variables(): 
      my_dict[key] = self.__hitcore.get(key)
    return my_dict

  # IO ###################

  def write_builtin_formatted(self, format, file_handle):
    """
    Write to a file formatted according to built-in file_type format

    - format = string from file_types
    - file_handle = file handle made using e.g. open() command

    e.g. aHit.write_builtin_formatted('icool_for009', for009_dat) would write aHit in icool_for009 format to for009_dat
    """
    if( format.find('maus') > -1 ):
      raise IOError("Can't write single maus hits, only lists of hits")
    if( format.find('icool') > -1 ):
      self.set('pid', Common.pdg_pid_to_icool[self.get('pid')])
    if( format.find('mars') > -1 ):
      self.set('pid', Common.pdg_pid_to_mars [self.get('pid')])
    self.__write_formatted(self.__file_formats[format], self.__file_units[format], file_handle)
    if( format.find('icool') > -1 ):
      self.set('pid', Common.icool_pid_to_pdg[self.get('pid')])
    if( format.find('mars') > -1 ):
      self.set('pid', Common.mars_pid_to_pdg [self.get('pid')])

  @classmethod
  def write_list_builtin_formatted(cls, list_of_hits, file_type_string, file_name, user_comment=None):
    """
    Write a list of hits to a file formatted according to built-in file_type format

    - format = string from file_types
    - file_handle = file handle made using e.g. open() command
    - user_comment = comment included in some output formats (e.g. problem title, etc)

    For example,
      aHit.write_list_builtin_formatted([hit1, hit2] 'icool_for009', 'for009_dat') 
    would write hit1, hit2 in icool_for009 format to for009_dat
    """
    if file_type_string not in cls.__file_types:
      raise IOError(f"Did not recognise file type {file_type_string}, should be one of {cls.__file_types}")
    if( file_type_string.find('maus_root') > -1 ):
      raise IOError("Can't write maus_root formats")
    filehandle = Hit.open_filehandle_for_writing(file_type_string, file_name, user_comment)
    if( file_type_string.find('maus') > -1 ):
      maus_tree = Hit.get_maus_tree(list_of_hits, file_type_string)
      for spill_number, item in enumerate(maus_tree):
        item["maus_event_type"] = "Spill"
        item["spill_number"] = spill_number
        print(json.dumps(item), file=filehandle)
      return
    sort_key = lambda hit: hit["station"]
    list_of_hits = sorted(list_of_hits, key=sort_key)
    old_hit = None
    current_hits = []
    for hit_in in list_of_hits:
      if old_hit == None or sort_key(hit_in) == sort_key(old_hit):
        current_hits.append(hit_in)
      else:
        for hit_out in current_hits:
          try:    hit_out.write_builtin_formatted(file_type_string, filehandle)
          except: pass
        current_hits = [hit_in]
      old_hit = hit_in
    for hit_out in current_hits:
      try:
        hit_out.write_builtin_formatted(file_type_string, filehandle)
      except:
        print('Warning - failed to write ',hit_out)
    filehandle.close()
    return

  def open_filehandle_for_writing(file_type_string, file_name, user_comment=None):
    """
    Open a file handle of the specified type for writing. Some filehandles need special care, e.g. some are gzipped etc

    - file_type_string = open filehandle for this file type
    - file_name        = string name of the file
    """
    filehandle = None
    filehandle = open(file_name, 'w')
    filehandle.write(Hit.file_header(file_type_string, user_comment))
    return filehandle
  open_filehandle_for_writing = staticmethod(open_filehandle_for_writing)

  def file_header(file_type_string, user_comment=None):
    """
    Return the file_header for the given file_type. Optionally, can add a user comment

    - file_type_string = header returned for this file type. Select from file_types()
    - user_comment     = add a user comment - default is 'File generated by xboa'

    e.g. Hit.file_header('icool_for009', 'This is my for009 file') would set 'This is my for009 file' 
    as a user comment and return the header string
    """
    if user_comment == None: file_header = Hit.__file_headers[file_type_string].replace(str('<user>'), str(Hit.__default_user_string))
    else:                    file_header = Hit.__file_headers[file_type_string].replace(str('<user>'), str(user_comment))
    return file_header
  file_header = staticmethod(file_header)

  def write_user_formatted(self, format_list, format_units_dict, file_handle, separator=' '):
    """
    Write to a file formatted according to built-in file_type format

    - format_list = ordered list of strings from get_variables()
    - format_units_dict = dict of formats from format_list to units
    - file_handle = file handle made using e.g. open() command

    e.g. aHit.write_user_formatted(['x','px','y','py'], ['x':'m','y':'m','px':'MeV/c','py':'MeV/c'], some_file, '@') would make output like
    0.001@0.002@0.001@0.002 in some_file
    """
    self.__write_formatted(format_list, format_units_dict, file_handle, separator)

  def file_types():
    """Static function returns a list of available file types"""
    return Hit.__file_types
  file_types = staticmethod(file_types)

  def get_maus_dict(self, type_name):
    """
    Convert from hit to a maus dict for MAUS IO

    - type_name = name of the maus type to generate

    Returns a tuple of (maus_dict, spill_number)
    """
    maus_dict = {}
    three_vec_conversions = Hit.__maus_three_vec_conversions[type_name]
    conversion_dict = Hit.__maus_variable_conversions[type_name]
    for maus_name, xboa_suffix in three_vec_conversions.items():
      maus_dict[maus_name] = {}
      for xyz in ['x','y','z']:
        maus_dict[maus_name][xyz] = self[xboa_suffix+xyz]
    for maus_key, xboa_key in conversion_dict.items():
      maus_dict[maus_key] = self[xboa_key]
    for key, value in Hit._Hit__file_units[type_name]:
      xboa_dict[key] *= Hit._Hit__file_units[type_name][key]
    return (maus_dict, self['event_number'])


  def get_maus_tree(list_of_hits, type_name):
    """
    Convert from list of hits to a tree of maus objects

    - list_of_hits = list of hits to be converted
    - type_name = maus type, used to define position in the maus tree

    Return value is a list of maus spills (each of which is a data tree)
    """
    # tried to be fairly general here; this should work for any tree that has all hit data
    # stored either directly at the same level or in three vectors at the same level
    # if we need to put pid here, momentum there, etc... then we need to think again
    return Hit.__get_maus_tree_recursive(list_of_hits,  [["event_number"]]+Hit.__maus_paths[type_name], type_name)
  get_maus_tree = staticmethod(get_maus_tree)

  # static data that describe the class #################

  def mass_shell_variables():
    """Static function returns a list of variables suitable for mass_shell_condition calls"""
    return Hit.__mass_shell_variables
  mass_shell_variables = staticmethod(mass_shell_variables)

  def get_variables():
    """Static function returns a list of variable suitable for get calls"""
    return Hit.__get_keys
  get_variables = staticmethod(get_variables)
  
  def set_variables():
    """Static function returns a list of variable suitable for set calls"""
    return Hit.__set_keys
  set_variables = staticmethod(set_variables)


  # get and set variables ####################  
  def get_p   (self):
    """Returns total momentum of the hit"""
    return (self.get('px')**2+self.get('py')**2+self.get('pz')**2)**0.5
  
  def get_r   (self): 
    """Returns transverse distance (i.e. in x,y space) from 0,0"""
    return     (self.get('x')**2+self.get('y')**2)**0.5
  
  def get_phi (self): 
    """Returns transverse angle (i.e. in x,y space) in range (-pi, pi); phi = 0. is positive y and phi = pi/2 is positive x"""
    return math.atan2(self['y'], self['x'])
  
  def get_pt  (self): 
    """Returns transverse momentum of the hit"""
    return     (self['px']**2+self['py']**2)**0.5
  
  def get_pphi(self): 
    """Returns transverse angle of momentum (i.e. in px,py space) in range (-pi, pi); phi = 0. is positive py and phi = pi/2 is positive px"""
    return math.atan2(self['py'], self['px'])
  
  def get_r_squared(self): 
    """Returns x divergence i.e. px/pz of the hit"""
    return     (self['x']**2+self['y']**2)
  
  def get_xP  (self): 
    """Returns x divergence i.e. px/pz of the hit"""
    return     (self['px']/self['pz'])
  
  def get_yP  (self): 
    """Returns y divergence i.e. py/pz of the hit"""
    return     (self['py']/self['pz'])
  
  def get_tP  (self):
    """Returns t \'divergence\' i.e. E/pz of the hit"""
    return     (-self['energy']/self['pz'])
  
  def get_rP  (self):
    """Returns dr/dz = pt/pz of the hit"""
    return     (self.get('pt')/self['pz'])
  
  def get_spin(self): 
    """Returns absolute value of the spin"""
    return     (self.get('sx')**2+self.get('sy')**2+self.get('sz')**2)**0.5
  
  def get_ct  (self): 
    """Returns speed_of_light*t of the hit"""
    return     (self['t']*Common.constants['c_light'])
  
  def get_ek  (self): 
    """Returns total energy - mass, ie kinetic energy of the hit"""
    return     self['energy'] - self.get('mass')
  
  def set_ek  (self, value_float): 
    """Sets kinetic energy = total energy - mass of the hit"""
    self['energy'] = value_float + self.get('mass')
  
  def get_l_kin(self): 
    """Returns kinetic angular momentum about the z-axis. 
    To use a different axis, you will have to perform your own transformation"""
    return self['x']*self['py'] - self['y']*self['px']
  
  def set_ct  (self, value_float): 
    """Sets t = value_float/c_light"""
    self['t'] = value_float/Common.constants['c_light']
  
  def set_p(self, value_float):
    """Set p to value_float keeping momentum direction constant"""
    p = self.get_p()
    if(p == 0):
      self.set('pz', 1.)
    scale = value_float/self.get_p()
    self['px'] *= scale
    self['py'] *= scale
    self['pz'] *= scale
  
  def set_xP  (self, value_float):
    """Set x\' to value_float keeping pz constant"""
    if(math.fabs(self['pz']) < 1e-9): raise FloatingPointError('Cant set x\' while pz is 0')
    self['px']     = value_float*self['pz']
  
  def set_yP  (self, value_float): 
    """Set y\' to value_float keeping pz constant"""
    if(math.fabs(self['pz']) < 1e-9): raise FloatingPointError('Cant set y\' while pz is 0')
    self['py']     = value_float*self['pz']
  
  def set_tP  (self, value_float): 
    """Set t\' (dt/dz=-E/pz) to value_float keeping pz constant; note sign of pz may change"""
    if(math.fabs(self['pz']) < 1e-9): raise FloatingPointError('Cant set t\' while pz is 0')
    self['energy'] = -value_float*self['pz']
    if self['pz'] < 0.: 
      self['energy'] *= -1.
      self['pz']     *= -1.
    if self['energy'] < self.get('mass'): raise FloatingPointError('Energy less than muon mass')
  
  def get_weight(self):
    """Returns total weight for this Hit"""
    return self.get('global_weight')*self.get('local_weight')

  def clear_global_weights(): 
    """Set all global weights to 1"""
    Hitcore.clear_global_weights()
  clear_global_weights = staticmethod(clear_global_weights)

  def delete_global_weights():
    """Clear memory allocated to global weights - also resets global weights to 1"""
    raise NotImplementedError("delete_global_weights is deprecated - please use clear_global_weights")
  delete_global_weights = staticmethod(delete_global_weights)

  def get_local_weight(self):
    """Returns local weight for this Hit"""
    return self.get('local_weight')
  
  def set_local_weight(self, value):
    """Set local weight for this Hit to be value"""
    self.set('local_weight', value)

  def get_global_weight(self):
    """Returns global weight for this Hit"""
    return self.get('global_weight')
  
  def set_global_weight(self, value):
      """Set global weight for this Hit to be value"""
      self.set('global_weight', value)

  def set_g4bl_unit(unit):
    """
    g4beamline_track_file can take different units for length - set the unit here

    - unit = string that is a unit of length

    e.g. set_g4bl_unit('m') would set the length unit to metres
    """
    Hit.__file_units['g4beamline_bl_track_file']['x'] = unit
    Hit.__file_units['g4beamline_bl_track_file']['y'] = unit
    Hit.__file_units['g4beamline_bl_track_file']['z'] = unit
  set_g4bl_unit = staticmethod(set_g4bl_unit)

  def __getstate__(self):
    """
    Used by python pickle module for serialisation

    Returns a dict as in dict_from_hit
    """
    return self.dict_from_hit()

  def __setstate__(self, state):
    """
    Used by python pickle module for deserialisation
    - state: a dictionary object defined by dict_from_hit
    Sets self to be equal to new_from_dict(state)
    """
    self.__init__()
    for k,v in state.items():
      self.set(k, v)

  #write formatted output - don't touch mass or pid beyond reading them
  def __write_formatted(self, format_list, format_units_dict, file_handle, separator=' '):
    for key in format_list:
      if key == '': value = 0
      else:         value = Hit._default_var_types[key](self.get(key)/Common.units[ format_units_dict[key] ])
      file_handle.write( str( value )+separator)
    file_handle.write('\n')

  # extract virtual hits from the root tree
  def __get_maus_root_virtual_hits(mc_event, track_number):
    hit_list = []
    for i in range(mc_event.GetVirtualHitsSize()):
      maus_hit = mc_event.GetAVirtualHit(i)
      pid = maus_hit.GetParticleId()
      hit_dict = {'pid':pid, 't':maus_hit.GetTime(), 'charge':maus_hit.GetCharge(), 'proper_time':maus_hit.GetProperTime(),
                'path_length':maus_hit.GetPathLength(), 'station':maus_hit.GetStationId(),
                'x':maus_hit.GetPosition().x(), 'y':maus_hit.GetPosition().y(), 'z':maus_hit.GetPosition().z(),
                'px':maus_hit.GetMomentum().x(), 'py':maus_hit.GetMomentum().y(), 'pz':maus_hit.GetMomentum().z(),
                'bx':maus_hit.GetBField().x(), 'by':maus_hit.GetBField().y(), 'bz':maus_hit.GetBField().z(),
                'ex':maus_hit.GetEField().x(), 'ey':maus_hit.GetEField().y(), 'ez':maus_hit.GetEField().z(),
                'particle_number':maus_hit.GetTrackId()}
      hit_dict['mass'] = Common.pdg_pid_to_mass[abs(pid)]
      if hit_dict['pid'] != 0:
          hit_list.append(Hit.new_from_dict(hit_dict, 'energy'))
      else:
          print('Warning - pid 0 detected in maus_root_virtual_hit; hit will not be loaded')
    return hit_list
  __get_maus_root_virtual_hits = staticmethod(__get_maus_root_virtual_hits)

  def __get_maus_root_primary_hits(mc_event, track_number):
    maus_hit = mc_event.GetPrimary()
    pid = maus_hit.GetParticleId()
    hit_dict = {'pid':pid, 'energy':maus_hit.GetEnergy(), 't':maus_hit.GetTime(),
                'x':maus_hit.GetPosition().x(), 'y':maus_hit.GetPosition().y(), 'z':maus_hit.GetPosition().z(),
                'px':maus_hit.GetMomentum().x(), 'py':maus_hit.GetMomentum().y(), 'pz':maus_hit.GetMomentum().z()}
    hit_dict['particle_number'] = 0
    hit_dict['charge'] = Common.pdg_pid_to_charge[abs(pid)]
    hit_dict['mass'] = Common.pdg_pid_to_mass[abs(pid)]
    return [Hit.new_from_dict(hit_dict, 'energy')]
  __get_maus_root_primary_hits = staticmethod(__get_maus_root_primary_hits)

  # split a list into sub lists where items in sublist have item1[sort_value] == item2[sort_value]
  def __split_list_by_equality(a_list, sort_attribute):
    a_dict = {}
    for item in a_list:
      value = item[sort_attribute]
      if not value in a_dict: a_dict[value] = []
      a_dict[value].append(item)
    return list(a_dict.values())
  __split_list_by_equality = staticmethod(__split_list_by_equality)

  # recursively reconstruct the maus_path
  def __get_maus_tree_recursive(list_of_hits, maus_path, format):
    if len(maus_path) == 1:
      if type(maus_path[0]) == type(""):
        if len(list_of_hits) > 1:
            for hit in list_of_hits:
                print(hit)
            raise IOError("More than one hit for maus key")
        return {maus_path[0]:list_of_hits[0].get_maus_dict(format)[0]}
      if type(maus_path[0]) == type([]):
        return [hit.get_maus_dict(format)[0] for hit in list_of_hits]
    if type(maus_path[0]) == type([]):
      list_of_hits_new = Hit.__split_list_by_equality(list_of_hits, maus_path[0][0])
      my_output = [Hit.__get_maus_tree_recursive(x, maus_path[1:], format) for x in list_of_hits_new]
      if len(maus_path) == 1:
        output = []
        for out in my_output: output += out
      else: output = my_output
      return my_output
    if type(maus_path[0]) == type(""):
      return {maus_path[0]:Hit.__get_maus_tree_recursive(list_of_hits, maus_path[1:], format)}
  __get_maus_tree_recursive = staticmethod(__get_maus_tree_recursive)

  # split a list into sub lists where items in sublist have item1[sort_value] == item2[sort_value]
  def __split_list_by_equality(a_list, sort_attribute):
    a_dict = {}
    for item in a_list:
      value = item[sort_attribute]
      if not value in a_dict: a_dict[value] = []
      a_dict[value].append(item)
    return list(a_dict.values())
  __split_list_by_equality = staticmethod(__split_list_by_equality)

  def __return_one(self, value=''):
    return 1.

  def __do_nothing(self, value = ''):
    pass
  
  #internal data
  #information on available types
  __file_types           = ['icool_for009', 'icool_for003', 'g4beamline_bl_track_file', 'g4beamline_bl_track_file_2', 'mars_1'] #'opal_loss'
  __file_types          += ['maus_json_virtual_hit', 'maus_json_primary', 'maus_json_special_virtual_hit']
  try:
    config.has_maus()
    __file_types          += ['maus_root_virtual_hit', 'maus_root_primary', 'maus_root_step', 'maus_root_scifi_trackpoint', 'maus_root_scifi_and_tof']
  except ImportError:
    pass

  __mass_shell_variables = ['', 'p', 'px', 'py', 'pz', 'energy']
  __get_variables        = {'p':get_p,'r':get_r,'phi':get_phi,'pt':get_pt,'pphi':get_pphi,'x\'':get_xP,'y\'':get_yP,'t\'':get_tP, 'ct\'':get_tP,'r\'':get_rP,'spin':get_spin,
                           'weight':get_weight,'ct':get_ct,'r_squared':get_r_squared,'z\'':__return_one,'kinetic_energy':get_ek,
                           'l_kin':get_l_kin,'':__do_nothing}
  __set_variables        = {'p':set_p,'x\'':set_xP,'y\'':set_yP,'t\'':set_tP,'ct':set_ct,'kinetic_energy':set_ek,'':__do_nothing}
  _default_var_types    = {'x':float,'y':float,'z':float,'t':float,'px':float,'py':float,'pz':float,'energy':float,'bx':float,'by':float,'bz':float,
                            'ex':float,'ey':float,'ez':float,'eventNumber':int, 'event_number':int, 'particleNumber':int, 'particle_number':int, 'pid':int,'status':int,'station':int,'local_weight':float,
                            'sx':float,'sy':float,'sz':float,'mass':float,'path_length':float,'proper_time':float,'e_dep':float, 'charge':float}

  __get_keys = []
  __set_keys = []
  __static_dummy = Hitcore()
  for key in __static_dummy.get_variables(): 
    __get_keys.append(key)
  for key in __static_dummy.set_variables(): 
    __set_keys.append(key)
  for key, value in __get_variables.items(): 
    __get_keys.append(key)
  for key, value in __set_variables.items(): 
    __set_keys.append(key)
  for key, value in __get_variables.items():
    if not key in _default_var_types:
      _default_var_types[key] = float #assume everything else is a float


  __maus_three_vec_conversions = { # maus three vectors are sub-dicts of virtual_hit
    "maus_json_virtual_hit":{"position":"", "momentum":"p", "b_field":"b", "e_field":"e"},
    "maus_json_primary":{"position":"", "momentum":"p"}
  }

  __maus_variable_conversions = {
    "maus_json_virtual_hit":{"station_id":"station", "particle_id":"pid", "track_id":"particle_number", "time":"t", "mass":"mass", "charge":"charge", "proper_time":"proper_time", "path_length":"path_length"},
    "maus_json_primary":{"particle_id":"pid", "time":"t", "energy":"energy"} # we also force "mass" from "pid"
  }

  __maus_paths             = {
      "maus_json_virtual_hit":["mc_events", ["particle_number"], "virtual_hits", ["station"]],
      "maus_json_primary":["mc_events", ["particle_number"], "primary"],
  }

  __maus_root_mc_types = {
        "maus_root_virtual_hit": lambda x, y: Hit.__get_maus_root_virtual_hits(x, y),
        "maus_root_primary": lambda x, y: Hit.__get_maus_root_primary_hits(x, y)
  }
  __maus_root_recon_types = {}

  #formatting information
  __file_formats = {
    'icool_for009' : ['eventNumber', 'particleNumber', 'pid', 'status', 'station', 't', 'x', 'y', 'z', 'px', 'py', 'pz', 'bx', 'by', 'bz', 'local_weight', 
                         'ex', 'ey', 'ez', '', 'sx', 'sy', 'sz'],
    'icool_for003' : ['eventNumber', 'particleNumber', 'pid', 'status', 't', 'local_weight', 'x', 'y', 'z', 'px', 'py', 'pz', 'sx', 'sy', 'sz'],
    'g4beamline_bl_track_file'  : ['x','y','z','px','py','pz','t','pid','eventNumber','particleNumber', '','local_weight'],
    'g4beamline_bl_track_file_2'  : ['x','y','z','px','py','pz','t','pid','eventNumber','particleNumber', '','local_weight', '', '', ''],
    'ZGoubi'       : [],
    'Turtle'       : [],
    'MadX'         : [],
    'mars_1'       : ['eventNumber','pid','x','y','z','px','py','pz','energy','ct','local_weight']
  }
  __file_units = {
    'icool_for009' : {'eventNumber':'', 'particleNumber':'', 'pid':'', 'status':'', 'station':'', 't':'s', 'x':'m', 'y':'m', 'z':'m', 'px':'GeV/c', 'py':'GeV/c', 
    'pz':'GeV/c', 'bx':'T', 'by':'T', 'bz':'T', 'local_weight':'', 
                         'ex':'GV/m', 'ey':'GV/m', 'ez':'GV/m', 'sx':'', 'sy':'', 'sz':'', '':''},
    'icool_for003' : {'eventNumber':'', 'particleNumber':'', 'pid':'', 'status':'', 't':'s', 'local_weight':'', 'x':'m', 'y':'m', 'z':'m', 'px':'GeV/c', 'py':'GeV/c', 'pz':'GeV/c', 'sx':'', 'sy':'', 'sz':''},
    'g4beamline_bl_track_file'  : {'x':'mm','y':'mm','z':'mm','px':'MeV/c','py':'MeV/c','pz':'MeV/c','t':'ns','pid':'','eventNumber':'','station':'','local_weight':'', 'particleNumber':''},
    'g4beamline_bl_track_file_2'  : {'x':'mm','y':'mm','z':'mm','px':'MeV/c','py':'MeV/c','pz':'MeV/c','t':'ns','pid':'','eventNumber':'','station':'','local_weight':'', 'particleNumber':''},
    'ZGoubi'       : {},
    'Turtle'       : {},
    'MadX'         : {},
    'mars_1'       : {'eventNumber':'','pid':'','x':'mm','y':'mm','z':'mm','px':'GeV/c','py':'GeV/c','pz':'GeV/c','energy':'GeV','ct':'cm','local_weight':''},
    'maus_json_virtual_hit': {},
    'maus_json_primary': {},
    }

  __file_headers = {
    'icool_for003':'<user>\n0. 0. 0. 0. 0. 0. 0. 0.\n',
    'icool_for009':'#<user>\n#  units = [s] [m]  [GeV/c] [T] [V/m]\nevt par typ  flg   reg    time        x           y           z           Px          Py          Pz          Bx          By          Bz          wt          Ex          Ey          Ez          arclength   polX        polY        polZ\n',
    'g4beamline_bl_track_file':'#BLTrackFile <user>\n#x y z Px Py Pz t PDGid EvNum TrkId Parent weight\n',
    'g4beamline_bl_track_file_2':'#BLTrackFile <user>\n#x y z Px Py Pz t PDGid EvNum TrkId Parent weight\n',
    'ZGoubi':'',
    'Turtle':'',
    'MadX':'',
    'mars_1':'',
    'maus_json_virtual_hit':'',
    'maus_json_primary':'',
  }
  __default_user_string = 'File generated by X_BOA'
  
  def __event_cmp(lhs, rhs):
    return cmp(lhs.get('eventNumber'), rhs.get('eventNumber'))
  __event_cmp = staticmethod(__event_cmp)
  
  def __station_cmp(lhs, rhs):
    return cmp(lhs.get('station'), rhs.get('station'))
  __station_cmp = staticmethod(__station_cmp)

  
  __hit_sort_comparator = {
    'icool_for009': __event_cmp,
    'icool_for003': __event_cmp,
    'g4beamline_bl_track_file': __event_cmp,
    'g4beamline_bl_track_file_2': __event_cmp,
    'ZGoubi': __event_cmp,
    'Turtle': __event_cmp,
    'MadX': __event_cmp,
    'maus_json_virtual_hit': __event_cmp,
    'maus_json_primary': __event_cmp,
    'mars_1': __event_cmp,
  }

  __angular_momentum_centroid = (0.,0.,0.)
  __angular_momentum_vector   = (0.,0.,1.)
  __bad_pids = []

  __maus_root_mc_types = {
        "maus_root_virtual_hit": lambda x, y: Hit.__get_maus_root_virtual_hits(x, y),
        "maus_root_primary": lambda x, y: Hit.__get_maus_root_primary_hits(x, y)
  }
  __maus_root_recon_types = {}

  __opal_ignore_probes = ["RING"]
  __opal_probes = {}
  __opal_pid = 0

  def hit_overview_doc(verbose = False):
    """Creates some summary documentation for the Hit class. If verbose is True then will also print any functions or data not included in summary"""
    name_list = ['initialise', 'get', 'set', 'transform', 'io', 'ancillary']
    function_list = {
    'initialise' : ['new_from_dict', 'new_from_read_builtin', 'new_from_read_user', 'copy', 'deepcopy'],    
    'get'        : ['get', 'get_ct', 'get_ek', 'get_global_weight', 'get_l_kin', 'get_local_weight', 'get_p', 'get_phi', 'get_pphi', 'get_pt', 'get_r', 'get_rP', 'get_r_squared', 'get_spin', 'get_tP', 'get_vector', 'get_weight', 'get_xP', 'get_yP'],
    'set'        : ['set', 'set_ct', 'set_ek', 'set_local_weight', 'set_p', 'set_tP', 'set_variables', 'set_xP', 'set_yP', 'set_global_weight'],
    'transform'  : ['abelian_transformation', 'translate', 'mass_shell_condition'],
    'io'         : ['file_header', 'file_types', 'set_g4bl_unit', 'write_builtin_formatted', 'write_list_builtin_formatted', 'write_user_formatted', 'open_filehandle_for_writing', 'get_maus_dict', 'get_maus_paths', 'get_maus_tree'],
    'ancillary'  : ['check','clear_global_weights', 'delete_global_weights', 'get_bad_pids', 'set_bad_pids', 'dict_from_hit', 'mass_shell_variables', 'get_variables']
    }
    function_doc = {
    'initialise':'Functions that can be used to initialise a Hit in various different ways:',
    'get'       :'Functions to get Hit data',
    'set'       :'Functions to set Hit data',
    'transform' :'Functions that transform a Hit in some way:',
    'io'        :'Output and some input helper functions:',
    'ellipse':'Functions to calculate beam ellipses based on Twiss parameters etc:',
    'ancillary':'Some other useful functions'
    }
    hit_doc = '\nHit class stores all data for a Hit on e.g. a detector - so for example, (x,y,z) and (px,py,pz) data. Mimics a string-indexed dict; full documentation for internal variables is given below under Hitcore. In brief, gettable variables are\n'+str(Hit.get_variables())+'\n and settable variables are\n'+str(Hit.set_variables())+'.\n Call using e.g. my_hit[\'x\'] = 3. Also has IO functions and a few other useful functions.\n'
    dir_hit = dir(Hit)
    if verbose:
      print('The following functions and data are in Bunch but not in overview_doc:')
      for func in dir_hit:
        found = False
        for func_sublist in list(function_list.values()):
          if func in func_sublist: found = True
        if not found: print(func, end=' ')
      print('\n')

      print('The following functions and data are in bunch_overview_doc but not in Bunch:')
      for func_sublist in list(function_list.values()):
        for func in func_sublist:
          if func not in dir_hit:
            print(func, end=' ')
      print()

    doc = hit_doc    
    for key in name_list:
      doc = doc + function_doc[key]+'\n'
      for item in function_list[key]:
        doc = doc+'  '+item+'\n'
    return doc
  hit_overview_doc = staticmethod(hit_overview_doc)

__doc__ = Hit.hit_overview_doc()

