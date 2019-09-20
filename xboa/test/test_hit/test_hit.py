import pickle
import sys
import unittest
import xboa.core
from xboa.core import Hitcore
from xboa import *
from xboa.core import *
from xboa.hit import Hit
#from xboa.Bunch import Bunch
from xboa.common import rg
import xboa.common as Common
import xboa.common.config as config

import xboa.test.TestTools
run_test = xboa.test.TestTools.run_test
run_test_group = xboa.test.TestTools.run_test_group
__float_tol = xboa.test.TestTools.__float_tol
parse_tests = xboa.test.TestTools.parse_tests
__test_root_hist = xboa.test.TestTools.test_root_hist
__test_root_canvas = xboa.test.TestTools.test_root_canvas
__test_root_graph = xboa.test.TestTools.test_root_graph

import os
import StringIO
import sys
import time
import math
import string
import numpy
from numpy import linalg
import operator
import bisect
import gc

"""
Test script:
One test function for each app function; one test function for each module. Name of each function test is blah_test(...) 
Helper functions are private.
Return value 'fail'; 'warning'; 'pass'
Module test function is called test_module
So:
  to run Hit tests call test_hit()
"""
__float_tol = Common.float_tolerance

import copy

def hit_global_weight_test():
  Hit.clear_global_weights()
  hit = Hit.new_from_dict({"spill":1, "event_number":2, "particle_number":3})
  if (abs(hit.get("global_weight")-1.) > 1e-9): return 'fail'
  hit.set('global_weight', 0.5)
  if (abs(hit.get_global_weight()-0.5) > 1e-9): return 'fail'
  Hitcore.clear_global_weights()
  if (abs(hit.get_global_weight()-1.) > 1e-9): return 'fail'
  return 'pass'

def hit_equality_test(hit1, hit2, isEqual):
  if hit1 == hit2 and isEqual:     return 'pass'
  if hit1 != hit2 and not isEqual: return 'pass'
  return 'fail'

def hit_repr_test(hit):
  new_hit = eval(repr(hit))
  if new_hit == hit: return 'pass'
  return 'fail'

def hit_copy_test(hit):
  hit_copy  = copy.copy(hit)
  hit_copy2 = hit.copy()
  if hit_copy is hit and hit_copy2 is hit: return 'pass' #test for address
  return 'fail'

def hit_deep_copy_test(hit):
  hit_deep_copy  = copy.deepcopy(hit)
  hit_deep_copy2 = hit.deepcopy()
  if hit_deep_copy == hit and not hit_deep_copy is hit and hit_deep_copy2 == hit and not hit_deep_copy2 is hit: 
    return 'pass'
  return 'fail'

def hit_get_vector_test(hit):
  vec = hit.get_vector(['x','y'])
  test_pass = vec[0,0] == hit.get('x') and vec[0,1] == hit.get('y')
  vec = hit.get_vector(['x','y'], {'x':10.,'z':100.})
  test_pass = test_pass and vec[0,0] == hit.get('x')-10. and vec[0,1] == hit.get('y')
  if test_pass: return 'pass'
  return 'fail'

def hit_translate_test(hit):
  hit1 = hit.deepcopy()
  hit1.translate({'px':10., 'py':5.}, '')
  test_pass = abs(hit1.get('px')-hit.get('px')-10.) < __float_tol and abs(hit1.get('py')-hit.get('py')-5.) < __float_tol
  hit1 = hit.deepcopy()
  hit1.translate({'px':10., 'py':5.}, 'energy')
  test_pass = test_pass and abs(hit1.get('px')-hit.get('px')-10.) < __float_tol and abs(hit1.get('py')-hit.get('py')-5.) < __float_tol and hit1.check()
  if test_pass: return 'pass'
  return 'fail'

def hit_abelian_transformation_test(hit):
  hit1 = hit.deepcopy()
  hit1.abelian_transformation(['x','px'], numpy.matrix([[1,0],[0,1]]), {'x':0,'px':0}, {'x':0,'px':0}, '')
  test_pass = hit == hit1
  hit1.abelian_transformation(['x','px'], numpy.matrix([[1,0],[0,1]]))
  test_pass = test_pass and hit == hit1
  R = numpy.matrix([[0.76,0.43],[0.76,0.29]])
  O = numpy.matrix([[1.3],  [-1.7]])
  T = numpy.matrix([[1.782],[2.35]])
  hit1.abelian_transformation(['x','px'], R, {'x':T[0,0],'px':T[1,0]}, {'x':O[0,0],'px':O[1,0]}, 'energy')
  vec_out   = R*((hit.get_vector(['x','px']).transpose()) - O) + T + O
  test_pass = test_pass and abs(vec_out[0,0] - hit1.get('x')) < __float_tol and abs(vec_out[1,0] - hit1.get('px')) < __float_tol and hit1.check()
  if test_pass: return 'pass'
  return 'fail'

def hit_mass_shell_condition_test(hit):
  test_pass = True
  hit1 = hit.deepcopy()
  if hit1.get('energy') < hit1.get('p') or hit1.get('energy') < hit1.get('mass'): return 'pass'
  for key in hit.mass_shell_variables():
    hit1.set(key, 1111.)
    hit1.mass_shell_condition(key)
    test_pass = test_pass and hit1.check()
    for key2 in ['px','py','pz','energy','mass']:
      test_pass = test_pass and abs( abs(hit1.get(key2)) - abs(hit.get(key2)) ) < __float_tol
  if test_pass: return 'pass'
  return 'fail'

def hit_get_test(hit):
  test_pass = True
  for key in hit.get_variables(): 
    try:
      value = hit.get(key)
      good  = True
      if type(key) == int:
        good = abs(hit._Hit__dynamic[key]-value) < __float_tol
      else:
        if   key in Hitcore.get_variables():
          good = abs(hit.get(key) - hit._Hit__hitcore.get(key)) < __float_tol
        elif key == 'p':               good = abs(math.sqrt(hit.get('px')**2+hit.get('py')**2+hit.get('pz')**2) - value) < __float_tol
        elif key == 'r':               good = abs(math.sqrt(hit.get('x')**2+hit.get('y')**2) - value) < __float_tol
        elif key == 'phi':             good = abs(math.atan(hit.get('y')/hit.get('x')) - value) < __float_tol \
                                        or ( abs(hit.get('x')) < __float_tol and abs(hit.get('y'))/hit.get('y')*(2.*value/math.pi)-1 < __float_tol) 
        elif key == 'pt':              good = abs(math.sqrt(hit.get('px')**2+hit.get('py')**2) - value) < __float_tol
        elif key == 'pphi':            good = abs(math.atan(hit.get('py')/hit.get('px')) - value) < __float_tol \
                                        or ( abs(hit.get('px')) < __float_tol and abs(hit.get('py'))/hit.get('py')*(2.*value/math.pi)-1 < __float_tol) 
        elif key == 'x\'':             good = abs(hit.get('px')/hit.get('pz')     - value) < __float_tol
        elif key == 'y\'':             good = abs(hit.get('py')/hit.get('pz')     - value) < __float_tol
        elif key == 't\'':             good = abs(-hit.get('energy')/hit.get('pz') - value) < __float_tol
        elif key == 'ct\'':            good = abs(-hit.get('energy')/hit.get('pz') - value) < __float_tol
        elif key == 'r\'':             good = abs(hit.get('pt')/hit.get('pz') - value) < __float_tol
        elif key == 'spin':            good = abs(math.sqrt(hit.get('sx')**2+hit.get('sy')**2+hit.get('sz')**2) - value) < __float_tol
        elif key == 'ct':              good = abs(hit.get('t')*Common.constants['c_light'] - value) < __float_tol
        elif key == '':                good = value == None
        elif key == 'weight':          good = abs(hit.get('local_weight')*hit.get('global_weight') - value) < __float_tol
        elif key == 'z\'':             good = abs(1. - value) < __float_tol #dz/dz is always 1!
        elif key == 'r_squared':       good = abs(hit['x']*hit['x']+hit['y']*hit['y'] - value) < __float_tol
        elif key == 'l_kin':           good = abs(hit['x']*hit['py']-hit['y']*hit['px'] - value) < __float_tol
        elif key == 'kinetic_energy':  good = abs(hit['energy']-hit['mass'] - value) < __float_tol
        elif key == 'global_weight':
          if hit.get('eventNumber') in Hit._Hit__global_weights_dict: good = abs(Hit._Hit__global_weights_dict[ hit.get('eventNumber') ] - value) < __float_tol
          else: good = abs(1. - value) < __float_tol
        else:
          print 'warning: key ',key,' not tested'
        if not good: print 'Get test failed with',key,value
    except ZeroDivisionError:
      good = True
    test_pass = test_pass and good
  if test_pass: return 'pass'
  return 'fail'

def hit_set_test(hit):
  test_pass = True
  for key in hit.set_variables():
    try:
      hit1  = hit.deepcopy()
      if key == '':
        test_pass = test_pass and hit1 == hit
      elif type(hit1.get(key)) == type(1.):
        hit1.set(key, 1000.)
        test_pass = test_pass and abs(hit1.get(key) - 1000.) < __float_tol
      elif type(hit1.get(key) == type(1)):
        hit1.set(key, 211)
        test_pass = test_pass and (hit1.get(key) == 211) 
      elif type(hit1.get(key)) == type('string'):
        hit1.set(key, 'some_string')
        test_pass = test_pass and hit1.get(key) == 'some_string'
      if not test_pass: 
        print 'Set test failed with key \''+str(key)+'\'',hit1.get(key), type(hit1.get(key))
        return 'fail'
    except:
      pass
  if test_pass: return 'pass'
  else:         return 'fail'

def hit_check_test(hit):
  hit1 = hit.deepcopy()
  hit1.set('pid', -13)
  hit1.set('mass', Common.pdg_pid_to_mass[abs(hit1.get('pid') )])
  hit1.mass_shell_condition('energy')
  test_pass = hit1.check()
  hit1.set('pid', -11)
  test_pass = test_pass and not hit1.check()
  hit1.set('pid', -13)
  hit1.set('mass', Common.pdg_pid_to_mass[11])
  test_pass = test_pass and not hit1.check()
  hit1.set('pid', 11)
  test_pass = test_pass and not hit1.check()
  hit1.mass_shell_condition('energy')
  test_pass = test_pass and hit1.check()
  hit1.set('pid', int(2e6))
  hit1.set('mass', 0.)
  hit1.mass_shell_condition('energy')
  test_pass = test_pass and not hit1.check()
  hit1.set('pid', int(0))
  test_pass = test_pass and hit1.check()
  if test_pass: return 'pass'
  return 'fail'

def hit_clear_global_weights_test(hit):
  hit.set('global_weight', 1000.)
  Hit.clear_global_weights()
  test_pass = abs(hit.get('global_weight') - 1.) < __float_tol
  if test_pass: return 'pass'
  return 'fail'

#This function tests:
#read_builtin_formatted(self, format, filehandle)
#new_from_read_builtin(format, filehandle)
#write_builtin_formatted(self, format, file_handle)
#  
#group io operations will have to be tested in Bunch
#open_filehandle_for_writing
#write_list_builtin_formatted
def hit_io_builtin_formatted_test(hit):
  test_pass_all = True
  for key in Hit.file_types():
    test_pass = True
    filehandle = open('out_test', 'w')
    if not filehandle: return 'warning - could not open file out_test'
    try:
      hit.write_builtin_formatted(key, filehandle)
      if key.find('maus') > -1: test_pass = False
    except IOError:
      if key.find('maus') == -1 and key.find('muon1_csv') == -1:
        test_pass = False
    filehandle.close()

    os.remove('out_test')
    if test_pass == False:
      print 'Failed on builtin format', key
      test_pass_all = False
  if test_pass_all: return 'pass'
  return 'fail'


def hit_io_user_formatted_test(hit):
  test_pass         = True
  format_list       = _Hit__file_formats['icool_for009']
  format_units_dict = _Hit__file_units['icool_for009']
  fh                = open('out_test','w')
  if not filehandle: return 'warning - could not open file out_test'
  hit.write_user_formatted(format_list, format_units_dict, fh, separator=' ')
  fh.close()
  
  fh = open('out_test','r')
  if not filehandle: return 'warning - could not open file out_test'
  hit1 = Hit()
  hit1.read_user_formatted(format_list, format_units_dict, fh)
  test_pass = test_pass and hit1 == hit
  fh.close()

  fh = open('out_test','r')
  if not filehandle: return 'warning - could not open file out_test'
  hit1 = Hit()
  hit1 = new_from_read_user(format_list, format_units_dict, fh)
  test_pass = test_pass and hit1 == hit
  fh.close()

  if test_pass: return 'pass'
  return 'fail'

def hit_set_g4bl_unit_test(hit):
  hit.set_g4bl_unit('cm')
  filehandle = open('set_g4bl_unit_test', 'w')
  if not filehandle: return 'warning - could not open file out_test'
  hit.write_builtin_formatted('g4beamline_bl_track_file', filehandle)
  filehandle.close()
  filehandle = open('set_g4bl_unit_test', 'r')
  hit.set_g4bl_unit('mm')
  hit1 = Hit.new_from_read_builtin('g4beamline_bl_track_file',filehandle)
  os.remove('set_g4bl_unit_test')
  for i in ['x','y','z']:
    if hit[i]/Common.units['cm'] != hit1[i]/Common.units['mm']: 
      print 'Failed set_g4bl_unit_test',hit[i],hit1[i]
      return 'fail'
  return 'pass'

def hit_get_maus_tree_test(hit_list): # also test get_list_of_maus_dicts
  test_pass = True
  for name in ['maus_json_virtual_hit']:
    maus_tree = Hit.get_maus_tree(hit_list, name)
    ev_dict = {}
    for hit in hit_list: ev_dict[hit['event_number']] = True
    test_pass = test_pass and len(maus_tree) == len(ev_dict.keys())
    test_pass = test_pass and len(maus_tree[0]["mc_events"][0]["virtual_hits"]) > 0
    if not test_pass:
      print json.dumps(maus_tree, indent=2)
  if test_pass: return 'pass'
  return 'fail'

def hit_test(hit): #test a hit - hit should be physical otherwise tests will give false negatives (e.g. no negative energy)
  test_results = []
  tests = [hit_repr_test, hit_copy_test, hit_deep_copy_test, hit_get_vector_test, hit_translate_test, hit_abelian_transformation_test, 
           hit_mass_shell_condition_test, hit_get_test, hit_set_test, hit_check_test, hit_set_g4bl_unit_test, hit_io_builtin_formatted_test, 
           hit_clear_global_weights_test]
  run_test_group(test_results, tests, [(hit,)]*len(tests))
  return  parse_tests(test_results)

def test_hit():
  test_results = []
  (passes, fails, warns) = (0,0,0)
  run_test(test_results, hit_global_weight_test, ())
  hit           = Hit.new_from_dict({'x':1.,'y':2.,'z':10.,'t':1.,'px':3.,'py':10.,'pz':200.,'pid':13,'mass':Common.pdg_pid_to_mass[13], 'charge':-1}, 'energy')
  hit_list      = [hit]
  hit_list.append(Hit.new_from_dict({'x':0.,'y':0.,'z':0.,'t':0.,'px':0.,'py':0.,'pz':0.,'pid':13,'mass':Common.pdg_pid_to_mass[13], 'station':1, 'charge':-1}, 'energy'))
  hit_list.append(Hit.new_from_dict({'x':0.,'y':0.,'z':0.,'t':0.,'px':0.,'py':0.,'pz':-200.,'pid':13,'mass':Common.pdg_pid_to_mass[13], 'station':2, 'charge':-1}, 'energy'))

  hit1          = Hit.new_from_dict({'x':1.,'y':2.,'z':10.,'t':1.,'px':3.,'py':10.,'pz':200.,'pid':13,'mass':Common.pdg_pid_to_mass[13], 'charge':-1}, 'energy')
  hit2          = Hit.new_from_dict({'x':1.,'y':2.,'z':10.,'t':1.,'px':3.,'py':10.,'pz':200.,'pid':13,'mass':Common.pdg_pid_to_mass[13],'station':1, 'charge':-1}, 'energy')
  junk          = 0

  for key in hit_list:
    (apass, afail, awarn) = hit_test(key)
    passes += apass
    fails  += afail
    warns  += awarn

  run_test_group(test_results, [hit_get_maus_tree_test], [(hit_list,), (hit_list,)])
  
  args  = [(hit, hit,  True), (hit, junk, False), (hit, hit1, True), (hit, hit2, False)]
  run_test_group(test_results, [hit_equality_test]*4, args)

  (passesEq, failsEq, warnsEq) = parse_tests(test_results)
  passes += passesEq
  fails  += failsEq
  warns  += warnsEq
  print '\n============\n||  HIT   ||\n============'
  print 'Passed ',passes,' tests\nFailed ',fails,' tests\n',warns,' warnings\n\n\n'
  return (passes,fails,warns)

class HitTest(unittest.TestCase):
    def test_hit_all(self):
        passes, fails, wanrs = test_hit()
        self._test_hit_memory()
        self.assertEqual(fails, 0)

    def _test_hit_memory(self):
        gc.collect()
        hitcore_memory = Hitcore.dump_memory()
        for address, number_of_allocations in hitcore_memory.iteritems():
            if number_of_allocations != 0:
                print "Hitcore not deleted at address", address, \
                      "with", number_of_allocations, "remaining references"
        self.assertEqual(sum(hitcore_memory.values()), 0)

    def test_hit_pickling(self):
        ref_hit = Hit.new_from_dict({'x':1.,'y':2.,'z':10.,'t':1.,
                                     'px':3.,'py':10.,'pz':200.,'pid':13,
                                     'mass':Common.pdg_pid_to_mass[13],
                                     'charge':-1}, 'energy')
        hit_str = pickle.dumps(ref_hit)
        test_hit = pickle.loads(hit_str)
        self.assertEqual(ref_hit, test_hit)

if __name__ == "__main__":
  unittest.main()


