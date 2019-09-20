import unittest
import os
import operator
import bisect
import sys
import copy

try:
  import numpy
  from numpy import linalg
except ImportError:
  pass

try:
  import ROOT
  ROOT.gROOT.SetBatch(True)
except ImportError:
  pass

from xboa import *
from xboa.core import *
from xboa.hit   import Hit
from xboa.bunch import Bunch
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

#=======================================================================================================================#
#======================                BUNCH              ==============================================================#
#=======================================================================================================================#

def bunch_hit_equality_test(bunch1, bunch2, isEqual):
  if   bunch1.hit_equality(bunch2) and isEqual:     return 'pass'
  elif not bunch1.hit_equality(bunch2) and not isEqual: return 'pass'
  return 'fail'

def bunch_delete_test(bunch):
  bunch1 = bunch.deepcopy()
  del(bunch1)
  try:
    bunch1.bunch_weight()
    return 'fail'
  except:
    return 'pass'

def bunch_equality_test(bunch1, bunch2, isEqual):
  if   bunch1 == bunch2 and isEqual:     return 'pass'
  elif bunch1 != bunch2 and not isEqual: return 'pass'
  return 'fail'

def bunch_str_test(bunch):
  if type(str(bunch)) == type('string'): return 'pass'
  return 'fail'

def bunch_repr_test(bunch):
  new_bunch = eval(repr(bunch))
  if  new_bunch == bunch: return 'pass'
  print repr(bunch)
  return 'fail'

def bunch_copy_test(bunch):
  bunch1 = bunch.copy()
  if bunch1 is bunch: return 'pass'
  return 'fail'

def bunch_deepcopy_test(bunch):
  bunch1 = bunch.deepcopy()
  if bunch1 == bunch and not bunch1 is bunch: return 'pass'
  return 'fail'

def bunch_len_test(bunch):
  if len(bunch) == len(bunch.hits()): return 'pass'
  return 'fail'

def bunch_getitem_test(bunch):
  for index in range(len(bunch.hits())):
    if bunch[index] != bunch.hits()[index]:
        return 'fail'
  return 'pass'

def bunch_setitem_test(bunch):
  bunch1 = bunch.deepcopy()
  for index in range(len(bunch1)):
    bunch1[index] = bunch1[0]
    if bunch1[index] != bunch1[0]:
        return 'fail'
  return 'pass'

def bunch_conditional_remove_test(bunch):
  #def conditional_remove(self, variable_value_dict, comparator, value_is_nsigma_bool = False):
  pid = -13248324
  bunch1 = bunch.deepcopy()
  bunch1.append(Hit.new_from_dict({'x':100., 'pid':pid}))
  bunch1.conditional_remove({'pid':pid}, operator.eq)
  if len(bunch1.get_hits('pid', pid)) != 0:
    print 'failed - bunch1 wrong length',bunch1,bunch1.get_hits('pid', pid) 
    return 'fail'
  bunch1.append(Hit.new_from_dict({'x':100., 'pid':pid}))
  bunch1.conditional_remove({'pid':pid}, operator.ne)
  if len(bunch1.get_hits('pid', pid)) != 1:
    print 'failed - bunch1 wrong length',bunch1,bunch1.get_hits('pid', pid) 
    return 'fail'
  if len(bunch1) != 1: return 'fail'
  return 'pass'

def bunch_translate_test(bunch):
  bunch1      = bunch.deepcopy()
  translation = {'x':5,'px':2}
  bunch1.translate({'x':5,'px':2})
  for index in range(len(bunch)):
    for key,value in translation.iteritems():
      if not abs(bunch[index].get(key) + value - bunch1[index].get(key)) < __float_tol: return 'fail'
  bunch1      = bunch.deepcopy()
  translation = {'x':5,'px':2}
  bunch1.translate({'x':5,'px':2}, 'energy')
  for index in range(len(bunch)):
    if not bunch1[index].check(): return 'fail'
    for key,value in translation.iteritems():
      if not abs(bunch[index].get(key) + value - bunch1[index].get(key)) < __float_tol: return 'fail'
  return 'pass'

def bunch_abelian_transformation_test(bunch):
  bunch1 = bunch.deepcopy()
  bunch2 = bunch.deepcopy()
  bunch1.abelian_transformation(['x','px'], numpy.matrix([[1,0],[0,1]]), {'x':0,'px':0}, {'x':0,'px':0}, '')
  if bunch != bunch1: return 'fail'
  bunch1.abelian_transformation(['x','px'], numpy.matrix([[1,0],[0,1]]))
  if bunch != bunch1: return 'fail'
  R = numpy.matrix([[0.76,0.43],[0.76,0.29]])
  O = numpy.matrix([[1.3],  [-1.7]])
  T = numpy.matrix([[1.782],[2.35]])
  bunch1.abelian_transformation(['x','px'], R, {'x':T[0,0],'px':T[1,0]}, {'x':O[0,0],'px':O[1,0]}, 'energy')
  for key in range( len(bunch1) ):
    bunch2[key].abelian_transformation(['x','px'], R, {'x':T[0,0],'px':T[1,0]}, {'x':O[0,0],'px':O[1,0]}, 'energy')
    if bunch2[key] != bunch1[key]: return 'fail'
  return 'pass'

def bunch_transform_to_test(bunch):
  bunch1 = bunch.deepcopy()
  bunch1.set_covariance_matrix(False)
  origin        = {'x':6.,'px':7.}
  d1 = linalg.det(bunch1.covariance_matrix(['x','px']))
  bunch1.transform_to(['x','px','pz'], bunch1.covariance_matrix(['x','px','pz'])) #NOTE: May fail due to covariance_matrix
  target_matrix = numpy.matrix([[2,-1],[-1,3]])
  translation   = {'x':4.,'px':5.}
  trans_back    = {'x':-4.,'px':-5.}
  bunch1.transform_to(['x','px'], target_matrix, translation, origin, 'energy')
  bunch1.translate(trans_back, 'energy')
  covariances = bunch1.covariance_matrix(['x','px'], origin)
  covariances = covariances*(float(linalg.det( target_matrix ))/float( linalg.det(covariances) ))**0.5
  if abs(covariances[0,0] - target_matrix[0,0]) > __float_tol or \
     abs(covariances[1,0] - target_matrix[0,1]) > __float_tol or \
     abs(covariances[1,1] - target_matrix[1,1]) > __float_tol:
    print 'bunch_transform_to_test failed on matrix'
    print covariances
    print target_matrix
    return 'fail'
  d2 = linalg.det(bunch.covariance_matrix(['x','px']))
  if abs(d1 - d2) > __float_tol and abs( (d1-d2)/(d1+d2) )>__float_tol:
    print 'bunch_transform_to_test failed on determinants', d1, d2
    return 'fail'
  return 'pass'

def bunch_hits_test(bunch):
  if bunch.hits() is bunch._Bunch__hits: return 'pass'
  return 'fail'

def bunch_get_hits_test(bunch):
  hits = bunch.get_hits('station', 13, operator.ne)
  for hit in bunch.hits():
    if hit.get('station') != 13:
      if not hit in hits: return 'fail'
    if hit.get('station') == 13:
      if hit in hits: return 'fail'
  return 'pass'

def bunch_standard_deviation_test(bunch):
  if bunch.standard_deviation('y') != bunch.moment(['y', 'y'])**0.5:
    return 'fail'
  if bunch.standard_deviation('p', {'p':10.}) != bunch.moment(['p', 'p'], {'p':10.})**0.5:
    return 'fail'
  return 'pass'

def bunch_moment_test(bunch):
  moment_list = ['x','x','px']
  mean_list   = {'x':1., 'px':2.}
  moment      = bunch.moment(moment_list, mean_list)
  this_moment = 0.
  for hit in bunch.hits():
    x = 1.
    for var in moment_list:
      x *= (hit.get(var) - mean_list[var])
    this_moment += x/bunch.bunch_weight()
  #ran into floating point issues hence weird test condition
  if abs(this_moment - moment)/abs(this_moment+moment) < __float_tol or abs(this_moment - moment) < __float_tol: return 'pass'
  return 'fail'

def bunch_moment_global_weight_test(bunch):
  # regression - moment was not picking up global weights properly
  bunch = bunch.deepcopy()
  bunch.set_covariance_matrix(False)
  bunch.clear_weights()
  for hit in bunch.hits():
    hit['local_weight'] = hit['x']
  print
  moment_x2 = bunch.moment(['x', 'x'])
  bunch.clear_weights()
  for hit in bunch.hits():
    hit['global_weight'] = hit['x']
  print
  if abs(moment_x2 - bunch.moment(['x', 'x'])) > __float_tol:
    print moment_x2, bunch.moment(['x', 'x'])
    bunch.clear_weights()
    testpass = 'fail'
  else:
    testpass = 'pass'
  bunch.clear_weights()
  return testpass


def bunch_mean_test(bunch):
  mean_list = ['x','x','px']
  mean      = bunch.mean(mean_list)
  this_mean = {'x':0., 'px':0.}
  for hit in bunch.hits():
    for var in mean_list:
      this_mean[var] += hit.get(var)/bunch.bunch_weight()
  for var in mean_list:
    if abs(this_mean[var] - mean[var]) < __float_tol: return 'pass'
  return 'fail'

def bunch_covariance_matrix_test(bunch):
  cov_list    = ['x','px','pz']
  origin_dict = {'x':2.}
  covariances = bunch.covariance_matrix(cov_list, origin_dict)
  origin_dict['px'] = bunch.mean(['px'])['px']
  origin_dict['pz'] = bunch.mean(['pz'])['pz']
  for i in range(len(cov_list)):
    for j in range(len(cov_list)):
      if abs(bunch.moment([cov_list[i], cov_list[j]],origin_dict) - covariances[i,j]) > __float_tol: 
        print cov_list[i],cov_list[j],'   ',bunch.moment([cov_list[i], cov_list[j]],origin_dict),covariances[i,j]
        return 'fail'
  covariances1 = bunch.covariance_matrix(cov_list)
  covariances2 = bunch.covariance_matrix(cov_list, {})
  covariances3 = bunch.covariance_matrix(cov_list, bunch.mean(cov_list))
  for i in range(len(cov_list)):
    for j in range(len(cov_list)):
      if abs(covariances1[i,j] - covariances2[i,j]) > __float_tol or abs(covariances1[i,j] - covariances3[i,j]) > __float_tol:
        print i,j,covariances1[i,j], covariances2[i,j], covariances3[i,j]
        return 'fail'
  return 'pass'

def bunch_bunch_weight_test(bunch):
  weight = 0.
  for key in bunch:
    weight += key.get('weight')
  if abs(bunch.bunch_weight() - weight) < __float_tol: return 'pass'
  return 'fail'

def bunch_clear_local_weights_test(bunch):
  bunch1 = bunch.deepcopy()
  for key in bunch1:
    key.set('local_weight', 0.5)
  bunch1.clear_local_weights()
  if abs(bunch1.bunch_weight() - bunch.bunch_weight()) < __float_tol: return 'pass'
  return 'fail'

def bunch_clear_global_weights_test(bunch):
  bunch1 = bunch.deepcopy()
  for key in bunch1:
    key['global_weight'] = 0.5
  bunch1.clear_global_weights()
  if abs(bunch1.bunch_weight() - bunch.bunch_weight()) < __float_tol: return 'pass'
  return 'fail'

def bunch_clear_weights_test(bunch):
  bunch1 = bunch.deepcopy()
  for key in bunch1:
    key.set('local_weight', 0.5)
    key.set('global_weight', 0.5)
  bunch1.clear_weights()
  if abs(bunch1.bunch_weight() - bunch.bunch_weight()) < __float_tol: return 'pass'
  return 'fail'

def bunch_cut_test(bunch):
  bunch1 = bunch.deepcopy()
  bunch1.clear_weights()
  bunch1.cut({'x':0.1, 'px':0.1}, operator.ge)
  for key in bunch1:
    if key.get('x') > 0.1 or key.get('px') > 0.1: 
      if abs(key.get('local_weight') ) > __float_tol: return 'fail'
    else:
      if abs(key.get('local_weight') -1. ) > __float_tol : return 'fail'
  bunch1.clear_local_weights()
  bunch1.cut({'amplitude x':0.}, operator.ge)
  if bunch1.bunch_weight() > 1e-9:
    return 'fail'
  bunch1.clear_local_weights()
  sigma_x = bunch1.moment(['x','x']) ** 0.5
  bunch1.cut({'x':1}, operator.ge, True, True)
  for key in bunch1:
    if key.get('x') - sigma_x > __float_tol: 
      if abs(key.get('global_weight') ) > __float_tol : 
        bunch1.clear_weights()
        return 'fail'
    else:
      if abs(key.get('global_weight') -1. ) > __float_tol:
        bunch1.clear_weights()
        return 'fail'
  bunch1.clear_weights()
  return 'pass'

def bunch_transmission_cut_test(bunch):
  test   = 'pass'
  bunch1 = bunch.deepcopy()
  bunch2 = Bunch()
  for hit in range(len(bunch1)/2):
    bunch2.append(bunch1[hit])
    bunch2[0]['particle_number'] += 1
  bunch1.transmission_cut(bunch2, global_cut=True, test_variable='event_number')
  for hit1 in bunch1:
    cut = True
    for hit2 in bunch2:
      if hit1['event_number'] == hit2['event_number']: cut = False
    if hit1['weight'] == 1. and cut:     test = 'fail'
    if hit1['weight'] == 0. and not cut: test = 'fail'
  bunch1.clear_weights()
  bunch1.transmission_cut(bunch2, global_cut=False, test_variable='event_number')
  for hit1 in bunch1:
    cut = True
    for hit2 in bunch2:
      if hit1['event_number'] == hit2['event_number']: cut = False
    if hit1['weight'] == 1. and cut:     test = 'fail'
    if hit1['weight'] == 0. and not cut: test = 'fail'
  bunch1.transmission_cut(bunch2, global_cut=False, test_variable=['event_number', 'particle_number'])
  for hit1 in bunch1:
    cut = True
    for hit2 in bunch2:
      if hit1['event_number'] == hit2['event_number'] and \
         hit1['particle_number'] == hit2['particle_number']: cut = False
    if hit1['weight'] == 1. and cut:     test = 'fail'
    if hit1['weight'] == 0. and not cut: test = 'fail'
  bunch1.clear_weights()
  return test

# tests set and get
def bunch_set_geometric_momentum_test(bunch):
  geom = Bunch.get_geometric_momentum()
  Bunch.set_geometric_momentum(geom)
  if Bunch.get_geometric_momentum( ) != geom: return 'fail'
  Bunch.set_geometric_momentum(not geom)
  if Bunch.get_geometric_momentum( ) == geom: return 'fail'
  Bunch.set_geometric_momentum(geom)
  return 'pass'

def bunch_axis_list_to_covariance_list_test(bunch):
  geom = Bunch.get_geometric_momentum()
  Bunch.set_geometric_momentum(True)
  if Bunch.axis_list_to_covariance_list( ['x','y','z','t', 'ct'] ) != ['x','x\'','y','y\'','z','z\'','t','t\'', 'ct','ct\'']:   return 'fail'
  Bunch.set_geometric_momentum(False)
  if Bunch.axis_list_to_covariance_list( ['x','y','z','t', 'ct'] ) != ['x','px','y','py','z','pz','t','energy', 'ct','energy']: return 'fail'
  geom = not Bunch.get_geometric_momentum()
  return 'pass'

def bunch_convert_string_to_axis_list_test(bunch):
  if Bunch.convert_string_to_axis_list( 'x y z t ct' ) != ['x','y','z','t','ct']:   return 'fail'
  try:
    Bunch.convert_string_to_axis_list( 'x y z t ct bob' )
    return 'fail' #should throw
  except: pass
  return 'pass'

def bunch_get_axes_test(bunch):
  if Bunch.get_axes() != ['x','y','z','t','ct']: return 'fail'
  return 'pass'

def bunch_get_hit_variable_test(bunch):
  for var in Bunch.hit_get_variables():
    for hit in bunch.hits():
      try:
        value = bunch.get_hit_variable(hit, var)
        if type(var) is str:
          if var.find('amplitude') > 0 or var == '': return 'pass'
        if abs(value - hit.get(var)) > __float_tol: return 'fail'
      except ZeroDivisionError:
        pass
  return 'pass'

def bunch_list_get_hit_variable_test(bunch):
  var_list    = Bunch.hit_get_variables()[0:4]
  value_lists = bunch.list_get_hit_variable(var_list)
  for i in range(len(bunch.hits())):
    for j in range(len(var_list)):
      if type(var_list[j]) is str:
        if var_list[j].find('amplitude') < 0 and var_list[j] != '':
          target = bunch[i].get(var_list[j])
      else:
        target = bunch[i].get(var_list[j])
      if abs(value_lists[j][i] - target): return 'fail'
  return 'pass'
    
def bunch_get_test(bunch):
  Bunch.set_geometric_momentum(False)
  cov = bunch.covariance_matrix(['x','px','y','py'])
  for var in Bunch.get_variables():
    value = bunch.get(var, ['x','y'])
    if var == 'angular_momentum': 
      target = bunch.moment(['x','py'],{'x':0,'py':0})-bunch.moment(['y','px'],{'y':0,'px':0})
    if var == 'emittance': 
      target = linalg.det(cov)**0.25/bunch.hits()[0].get('mass')
    if var == 'dispersion': 
      target = bunch.moment(['x','energy'])*bunch.mean(['energy'])['energy']/bunch.moment(['energy','energy'])
    if var == 'dispersion_prime': 
      target = bunch.moment(['px','energy'])*bunch.mean(['energy'])['energy']/bunch.moment(['energy','energy'])
    if var == 'beta': 
      target = (cov[0,0] + cov[2,2])/2.*bunch.mean(['p'])['p']/bunch.get('emittance', ['x','y'])/bunch.hits()[0].get('mass')
    if var == 'alpha': 
      target = -(cov[0,1] + cov[2,3])/2./bunch.get('emittance', ['x','y'])/bunch.hits()[0].get('mass')
    if var == 'gamma':
      target = (cov[1,1] + cov[3,3])/2./bunch.mean(['p'])['p']/bunch.get('emittance', ['x','y'])/bunch.hits()[0].get('mass')
    if var == 'moment':
      target = bunch.moment(['x','y'])
    if var == 'mean':
      target = bunch.mean(['x'])['x']
    if var == 'bunch_weight': 
      target = bunch.bunch_weight()
    if var == 'standard_deviation': 
      target = bunch.standard_deviation(['x'])
    if abs(value - target) > abs(target)*__float_tol+__float_tol:
      print 'bunch_get_test:',var,target,value 
      return 'fail'
  return 'pass'
  
  Bunch.set_geometric_momentum(True)
  cov = bunch.covariance_matrix(['x','x\'','y','y\''])
  for var in Bunch.get_variables():
    value = bunch.get(var, ['x','y'])
    if var == 'angular_momentum': 
      target = (-cov[1,2]+cov[0,3]) * bunch.mean(['p'])['p']
    if var == 'emittance': 
      target = linalg.det(cov)**0.25 
    if var == 'dispersion': 
      target = -bunch.moment(['x','energy'])*bunch.mean(['energy'])['energy']/bunch.moment(['energy','energy'])
    if var == 'dispersion_prime': 
      target = bunch.moment(['px','energy'])*bunch.mean(['energy'])['energy']/bunch.moment(['energy','energy'])
    if var == 'beta': 
      target = (cov[0,0] + cov[2,2])/2./bunch.get('emittance', ['x','y'])
    if var == 'alpha': 
      target = (cov[0,1] + cov[2,3])/2./bunch.get('emittance', ['x','y'])
    if var == 'gamma':
      target = (cov[1,1] + cov[3,3])/2./bunch.get('emittance', ['x','y'])
    if var == 'moment':
      target = bunch.moment(['x','y'])
    if var == 'mean':
      target = bunch.mean(['x'])['x']
    if var == 'bunch_weight': 
      target = bunch.bunch_weight()
    if abs(value - target) > __float_tol: return 'fail'
  Bunch.set_geometric_momentum(False)
  return 'pass'

def bunch_get_amplitude_test(bunch):
  bunch1 = bunch.deepcopy()
  axis_list = ['x']
  amp = 0.
  Bunch.set_geometric_momentum(False)
  for hit in bunch1.hits():
    delta = Bunch.get_amplitude(bunch1, hit, axis_list)
    amp  += delta/float(len(bunch1.hits()))
  target = bunch1.get_emittance(axis_list,bunch1.covariance_matrix(['x','px']))*2.*len(axis_list)
  if abs(amp - target) > __float_tol:
    print 'Failed at geometric=False:',amp, target
    return 'fail'
  Bunch.set_geometric_momentum(True)
  if bunch1.covariances_set(): bunch1.set_covariance_matrix()
  amp = 0.
  for hit in bunch1.hits():
    amp += Bunch.get_amplitude(bunch1, hit, axis_list)/float(len(bunch1))
  target = bunch1.get_emittance(axis_list)*2.*len(axis_list)
  if abs(amp - target) > __float_tol:
    print 'Failed at geometric=True:',amp, target
    return 'fail'
  Bunch.set_geometric_momentum(False)
  return 'pass'

def bunch_histogram_var_bins_test(bunch):
  testpass = True
  bin_x = range(-100,100)
  bin_y = [-0.1,0.1,1.0]
  bin_weights = [[0]*(len(bin_x)-1)]
  for hit in bunch:
    if hit['y']> -0.1*Common.units['m'] and hit['y']<0.1*Common.units['m']:
      i = bisect.bisect_right(bin_x, hit['x'])-1
      if i>=0 and i<len(bin_weights[0]): bin_weights[0][i] += hit['weight']
  h1    = bunch.histogram_var_bins('x', bin_x, 'mm')
  h2    = bunch.histogram_var_bins('x', bin_x, 'mm', 'y', bin_y, 'm')

  bunch1 = bunch.deepcopy()
  bunch1.cut({'x':-100.}, operator.le)
  bunch1.cut({'x': 100.}, operator.ge)
  testpass &= h1[1] == bin_x and h1[2] ==[]
  testpass &= abs(h1[0].sum()-bunch1.bunch_weight()) < __float_tol #I assume binning has been done ok - tested in Common.histogram()

  bunch2 = bunch.deepcopy()
  bunch2.cut({'x':-100., 'y':-0.1*Common.units['m']}, operator.le)
  bunch2.cut({'x': 100., 'y': 1.0*Common.units['m']}, operator.ge)
  testpass &= h2[1] == bin_x and h2[2] == bin_y
  testpass &= abs(h2[0].sum().sum()-bunch2.bunch_weight()) < __float_tol #I assume binning has been done ok - tested in Common.histogram()

  if testpass: return 'pass'
  return 'fail'

def bunch_histogram_test(bunch):
  h1 = bunch.histogram('x')
  h2 = bunch.histogram('x', 'm', 'y', 'mm', nx_bins=13, ny_bins=11, xmin=-2., xmax=3., ymin=-4., ymax=4.)
  (xmin,xmax) = (min(bunch.list_get_hit_variable(['x'], ['mm'])[0]),max(bunch.list_get_hit_variable(['x'], ['mm'])[0]) )
  testpass  = True
  testpass &= (h1[1][0]-xmin)<__float_tol and (h1[1][-1]-xmax)<__float_tol and h1[2]==[]
  testpass &= (h2[1][0]+2.*Common.units['m'])<__float_tol  and (h2[1][13]-3.*Common.units['m'])<__float_tol and len(h2[1])==14 #nbins+1
  testpass &= (h2[2][0]+4.*Common.units['mm'])<__float_tol and (h2[2][11]-4.*Common.units['mm'])<__float_tol and len(h2[2])==12 #nbins+1
  if testpass: return 'pass'
  return 'fail'

#  def root_graph(bunches, x_axis_string, x_axis_list, y_axis_string, y_axis_list, x_axis_units='', y_axis_units='', canvas='', comparator=None, xmin=None, xmax=None, ymin=None, ymax=None, 
#                 line_color=rg.line_color, line_style=rg.line_style, line_width=rg.line_width, fill_color=rg.graph_fill_color, hist_title_string=''):

def __bunch_cmp(b1, b2):
  return cmp(b1.get_emittance(['x','y']), b2.get_emittance(['x','y']))

def bunch_root_graph_test(bunch_dict):
  canvas,hist,graph = Bunch.root_graph(bunch_dict, 'mean', ['z'], 'emittance',    ['x','y'], 'mm', 'm')
  canvas,hist,graph = Bunch.root_graph(bunch_dict, 'mean', ['z'], 'bunch_weight', [],        'mm', 'm')
  canvas = ''
  canvas,hist,graph = Bunch.root_graph(bunch_dict, 'mean', ['z'], 'emittance',    ['x','y'], 'mm', 'm', canvas, __bunch_cmp, -10., 100., -20., 200., 1, 2, 3, 4, 'mrs title')
  testpass = __test_root_hist(hist,'mean( z ):emittance( x,y )', 'mean( z ) [mm]','emittance( x y ) [m]', -10., 100., -20., 200., rg.line_color, rg.line_style, rg.line_width, rg.fill_color, 'mrs title')
  try:    list_of_bunches = bunch_dict.values()
  except: list_of_bunches = bunch_dict
  x_list,y_list = [],[]
  for b in list_of_bunches:
    x_list.append(b.mean(['z'])['z'])
    y_list.append(b.get_emittance(['x','y'])*1e-3)
  Common.multisort([y_list,x_list])
  testpass &= __test_root_graph(graph, 'mean( z ):emittance( x,y )', x_list, y_list, 1, 2, 3, 4)
  if testpass: return 'pass' #need to test new options
  return 'fail'

def bunch_root_histogram_test(bunch):
  #check that defaults are set or non-defaults are passed correctly to hist
  (canvas,hist) = bunch.root_histogram('energy','MeV')
  (canvas,hist) = bunch.root_histogram('x','mm','px','MeV/c', 3, 7, canvas, -25, 45, -17, 22, 1, 2, 3, 4, True, 'baby title')
  testpass = __test_root_hist(hist,'mean( z ):emittance( x,y )', 'x [mm]','px [MeV/c]', -25., 45., -17., 22., 1, 2, 3, 4, 'baby title')
  if testpass: return 'pass' #need to test new options
  return 'fail'

def bunch_root_scatter_graph_test(bunch):
  #check that defaults are set or non-defaults are passed correctly to hist
  (canvas,hist,graph) = bunch.root_scatter_graph('energy','p')
  (canvas,hist,graph) = bunch.root_scatter_graph('x','px','m','GeV/c', True, canvas,-25,45,-17,22,1,2,3,4,'abc')
  x_l,y_l = [],[]
  for hit in bunch: 
    x_l.append(hit['x']*1e-3)
    y_l.append(hit['px']*1e-3)
  Common.multisort([x_l,y_l])
  testpass  = __test_root_hist (hist,  'energy:p', 'x [m]','px [GeV/c]', -25., 45., -17., 22., rg.line_color, rg.line_style, rg.line_width, rg.fill_color, 'abc')
  testpass &= __test_root_graph(graph, 'energy:p', x_l, y_l, 1, 2, 3, 4)
  if testpass: return 'pass'
  return 'fail' #need to test new options

def bunch_matplot_graph_test(bunch_dict):
  canvas1 = Bunch.matplot_graph(bunch_dict, 'mean', ['z'], 'bunch_weight', [], 'mm')
  canvas2 = Bunch.matplot_graph(bunch_dict, 'mean', ['z'], 'emittance',    ['x','y'], 'mm', 'm')
  return 'pass'

def bunch_matplot_histogram_test(bunch):
  canvas1 = bunch.matplot_histogram('x','mm','px','MeV/c')
  canvas2 = bunch.matplot_histogram('energy','MeV')
  return 'pass'

def bunch_matplot_scatter_graph_test(bunch):
  canvas1 = bunch.matplot_scatter_graph('x','px','mm','MeV/c')
  canvas1 = bunch.matplot_scatter_graph('energy','p')
  return 'pass'

def bunch_list_get_test(bunch_dict):
  var_list  = ['beta', 'mean']
  axis_list = [['x','y'], ['z']]
  Bunch.list_get(bunch_dict,var_list, axis_list)
  return 'pass'

def bunch_new_hit_shell_test():
  ellipse   = Bunch.build_penn_ellipse(6*Common.units['mm'], Common.pdg_pid_to_mass[13], 333.,0.,200.,0.,4*Common.units['T'],1.)
  bunch     = Bunch.new_hit_shell(3, ellipse, ['x','px','y','py'], 'energy', defaults={'pid':-13,'mass':Common.pdg_pid_to_mass[13],'pz':200.})
  bunch_amp = Bunch.get_amplitude(bunch, bunch[0], ['x','y'], ellipse)
  for hit in bunch:
    if abs(Bunch.get_amplitude(bunch, hit, ['x','y'], ellipse) - bunch_amp) > Common.float_tolerance:
      return 'fail'
  return 'pass'

def bunch_maus_root_io_test(_bunch_not_used):
  out = 'pass'
  file_types = filter(lambda format: format.find('maus_root') >= 0, Hit.file_types())
  formats = {'maus_root_primary':40, #10 spills, 4 primaries per spill
             'maus_root_virtual_hit':90, #3 planes, 10 spills, 3 primaries per spill (1 primary misses)
             'maus_root_scifi_trackpoint':0,
             'maus_root_scifi_and_tof':0,
             'maus_root_step':0 } # trust test_factory test
  for format in file_types:
    bunch = Bunch.new_from_read_builtin(format, sys.prefix+'/share/xboa/data/maus_*s?.root')
    id_dict = {}
    for hit in bunch:
        _id = (hit['spill'], hit['event_number'], hit['particle_number'], hit['station'])
        if _id in id_dict: # check that ids are unique
            out = 'fail'
        else:
            id_dict[_id] = True
    if formats[format] != len(bunch):
        print 'bunch_maus_root_io_test fail on format', format, 'length', len(bunch)
        out = 'fail'
    if out == 'fail':
      print 'bunch_maus_root_io_test', format
      print 'spill', 'event', 'track', 'statn'
      for _id in id_dict.keys():
        for i in _id:
          print str(i).rjust(5),
        print
  return out

def bunch_builtin_io_test(bunch):
  out = 'pass'
  print Hit.file_types()
  file_types = filter(lambda format: format.find('maus_root') < 0, Hit.file_types())
  for format in file_types:
    try:
      bunch.hit_write_builtin(format, 'bunch_builtin_io_test.gz')
      bunch1 = Bunch.new_from_read_builtin(format, 'bunch_builtin_io_*s?.gz')
      if format == 'icool_for003' or format == 'mars_1' or format == 'g4beamline_bl_track_file': #no station in these formats, defaults to 0
        for i in range( len(bunch1) ): bunch1[i]['station'] = bunch[i]['station']
      if bunch.covariances_set() and bunch.means_set():
        bunch1.set_covariance_matrix(use_internal_covariance_matrix=True, covariance_matrix=bunch._Bunch__covs, mean_dict=bunch._Bunch__means)
    except Exception:
      sys.excepthook(*sys.exc_info())
      bunch1 = None #force a fail on exception
    os.remove('bunch_builtin_io_test.gz')
    if format.find('maus') >= 0:
      for i, hit in enumerate(bunch1): # write op does not conserve particle_number
        bunch1[i]['particle_number'] = bunch[i]['particle_number']
        bunch1[i]['event_number'] = bunch[i]['event_number']
        if format.find('primary') >= 0:
          bunch1[i]['station'] = bunch[i]['station']
        if format.find('maus_json') >= 0:
          bunch1[i]['spill'] = bunch[i]['spill']
    if bunch != bunch1:
      print 'Builtin io failed with format',format
      try:
        print 'Input length',len(bunch),'Output length',len(bunch1)
        counter = 0
        for i,hit in enumerate(bunch):
          if bunch[i] != bunch1[i] and counter < 10:
            print 'Reference:', bunch[i], '\n', 'Test:', bunch1[i], '\n'
            counter += 1
          elif bunch[i] != bunch1[i]:
            print 'Further fails exist but were not printed...'
            break
      except:
        sys.excepthook(*sys.exc_info())
      out = 'fail'
  return out

def bunch_builtin_io_test_function_test(bunch):
    bunch.hit_write_builtin('icool_for003', 'bunch_builtin_io_test.gz')
    ref_bunch = Bunch.new_from_read_builtin(format, 'bunch_builtin_io_*s?.gz')
    ref_hits = [hit for hit in ref_bunch if hit['x'] > 1]
    test_bunch = Bunch.new_from_read_builtin(format, 'bunch_builtin_io_*s?.gz', lambda hit: hit['x'] > 1)
    self.assertEqual(len(ref_hits), len(test_bunch))
    for ref_hit, test_hit in zip(ref_hits, test_bunch):
        self.assertEqual(ref_hit, test_hit)


def bunch_dict_builtin_io_test(bunch_dict):
  # we aren't interested in hit details, only number of hits in each station
  # bunch_dict is not sorted by station, so we first count how many hits there are in each station
  total_hit_count       = 0
  hit_list_per_station = {}
  bunch_dict = copy.deepcopy(bunch_dict)
  events = []
  for key, bunch in bunch_dict.iteritems():
    for hit in bunch:
      station = hit['station']
      if not station in hit_list_per_station:
          hit_list_per_station[station] = []
      hit_list_per_station[station].append(hit)
      total_hit_count += 1

  for format in filter(lambda format: format.find('maus_root') < 0 and format.find('maus_json_primary') < 0, Hit.file_types()):
    print "bunch_dict_builtin_io_test format:", format
    Bunch.hit_write_builtin_from_dict(bunch_dict, format, 'bunch_dict_builtin_io_test.'+format)
    bunch_dict1 = Bunch.new_dict_from_read_builtin(format, 'bunch_dict_builtin_io_*s?.'+format)
    bunch_list1 = Bunch.new_list_from_read_builtin(format, 'bunch_dict_builtin_io_*s?.'+format)
    os.remove('bunch_dict_builtin_io_test.'+format)
    if format == 'icool_for003' or format == 'mars_1' or format == 'maus_json_primary' or format == 'g4beamline_bl_track_file':
      if len(bunch_dict1) != 1 or len(bunch_dict1[0]) != total_hit_count: return 'fail'
      if len(bunch_list1) != 1 or len(bunch_list1[0]) != total_hit_count: return 'fail'
    else:
      if len(bunch_dict1) != len(hit_list_per_station):
        print '    len in',len(hit_list_per_station),'len out',len(bunch_dict1), format, [bunch[0]['station'] for bunch in bunch_dict1.values()]
        return 'fail'
      for key in bunch_dict1.keys():
        if len(bunch_dict1[key]) != len(hit_list_per_station[key]):
          for i,hit in enumerate(hit_list_per_station[key]): print 'in_'+str(i)+' ',hit['particle_number'],hit['event_number'],hit['station'],hit in hit_list_per_station[key]
          for i,hit in enumerate(bunch_dict1[key]):          print 'out_'+str(i),hit['particle_number'],hit['event_number'],hit['station'],hit in bunch_dict1[key]
          print 'station:',key,'n_hits_in:',len(hit_list_per_station[key]),'n_hits_out:',len(bunch_dict1[key]), format
          return 'fail'
  return 'pass'

def __test_comptor(hit1, hit2):
  return cmp(hit2['eventNumber'], hit1['eventNumber'])

def __test_truth(hit):
  return hit['eventNumber'] == 3

def bunch_user_io_test(bunch):
  fh = open('bunch_user_io_test', 'w')
  fh.write('test output\n')
  format_list = ['eventNumber', 'eventNumber', 'pid', 'status', 't', 'local_weight', 'x', 'y', 'z', 'px', 'py', 'pz', 'sx', 'sy', 'sz', 'station', 'particleNumber', 'charge']
  units_dict  = {'eventNumber':'', 'particleNumber':'', 'pid':'', 'status':'', 't':'s', 'local_weight':'', 'x':'m', 'y':'m', 'z':'m', 'px':'GeV/c', 'py':'GeV/c', 'pz':'GeV/c', 'sx':'', 'sy':'', 'sz':'', 'station':'', 'charge':''}
  
  bunch.hit_write_user(format_list, units_dict, fh)
  fh.close()
  fh = open('bunch_user_io_test', 'r')
  bunch1 = Bunch.new_from_read_user(format_list, units_dict, fh, 1)
  for hit in bunch1: hit.mass_shell_condition('energy')
  if  len(bunch1) != len(bunch):
    raise RuntimeError('bunches of different length')
  if not bunch.hit_equality(bunch1):
    counter = 0
    for i in range(len(bunch)):
      if bunch[i] != bunch1[i] and counter < 5:
        print i, bunch[i], '\n', bunch1[i], '\n'
        counter += 1
    raise RuntimeError('bunch not equal to bunch1')
  fh.close()
  fh = open('bunch_user_io_test', 'w')
  bunch.hit_write_user(format_list, units_dict, fh, comparator=__test_comptor)
  fh.close()
  fh = open('bunch_user_io_test', 'r')
  bunch1 = Bunch.new_from_read_user(format_list, units_dict, fh, 0, __test_truth)
  nhits = 0
  os.remove('bunch_user_io_test')
  for hit in bunch: 
    if __test_truth(hit): nhits+=1
  if len(bunch1) != nhits: raise RuntimeError('bunch1 length '+str(len(bunch1))+' != nhits '+str(nhits))
  for hit in bunch1:
    if hit['eventNumber'] != 3: return 'fail'
  return 'pass'
#  def new_from_read_user(format_list, format_units_dict, filehandle, number_of_skip_lines, station_number=None, number_of_hits=-1):

def set_covariances_test(bunch):
  print 'set covariances test not defined'
  return 'fail'

def bunch_get_dispersion_rsquared_test(bunch):
  dr2 = (bunch.moment(['r_squared','energy'],{'r_squared':0.,'energy':0})-(bunch.moment(['x','x'])+bunch.moment(['y','y']))*bunch.mean(['energy'])['energy'])\
        *bunch.mean(['energy'])['energy']/bunch.moment(['energy','energy'])
  dr2_test = bunch.get_dispersion_rsquared()
  if abs(dr2 - dr2_test) < __float_tol: return 'pass'
  return 'fail'

def bunch_canonical_angular_momentum_test(bunch):
  field_axis_dict    = {'x':5., 'y':3.}
  rotation_axis_dict = {'x':1.,'y':4.,'px':2.,'py':-1.}
  bz    = 5.*Common.units['T']
  l_can =  bunch.get_kinetic_angular_momentum(rotation_axis_dict) \
           + Common.constants['c_light']*bz*(bunch.moment(['x','x'], field_axis_dict) \
           + bunch.moment(['y','y'], field_axis_dict))/2.
  test_lcan = bunch.get_canonical_angular_momentum(bz, field_axis_dict, rotation_axis_dict)
  if abs(l_can - test_lcan) < __float_tol: return 'pass'
  return 'fail'

def bunch_period_transformation_test(bunch):
  for frequency in [10., 100., 1000.]:
    for offset in [0.1,0.2,0.3,0.4,0.5]:
      bunch.period_transformation(offset, frequency, 'z')
      for hit in bunch:
        if abs(hit['z'])-1./frequency > __float_tol:
          print 'bunch_period_transformation_test failed with frequency',frequency,' offset ',offset,' z out ',hit['z']
          return 'fail'
  return 'pass'

def bunch_build_ellipse_2d_test():
  ell1_test = [[ 1331.29542168, -316.9751004 ], [ -316.9751004, 377.35131   ]]
  ell2_test = [[  2.52000000e+03, -3.00000000e+00],[ -3.00000000e+00, 1.78571429e-02]]
  ell1      = Bunch.build_ellipse_2d(420., 0.5, 6., 200., Common.pdg_pid_to_mass[13], False)
  ell2 = Bunch.build_ellipse_2d(420., 0.5, 6., 200., Common.pdg_pid_to_mass[13], True)
  for i in range(2):
    for j in range(2):
      if abs(ell1[i,j]-ell1_test[i][j]) > Common.float_tolerance: return 'fail'
  for i in range(2):
    for j in range(2):
      if abs(ell2[i,j]-ell2_test[i][j]) > Common.float_tolerance: return 'fail'
  return 'pass'

def bunch_build_ellipse_penn_test():
  mu_bunch = Bunch()
  test_ellipse = numpy.matrix([[ 1055.52708433,    -0.,             0.,          -632.87811819],
                               [   -0.,           760.21504469,   632.87811819,     0.        ],
                               [    0.,           632.87811819,  1055.52708433,    -0.        ],
                               [ -632.87811819,     0.,            -0.,           760.21504469]])
  ellipse = Bunch.build_penn_ellipse(6., Common.pdg_pid_to_mass[13], 333., 0., 200., 0., 4.*Common.units['T'], +1.)
  for i,a in enumerate(ellipse.flatten().tolist()):
    x = ellipse.flatten().tolist()[0][i]
    y = test_ellipse.flatten().tolist()[0][i]
    if abs(x - y) > __float_tol*1e3:
      print 'FAILED',i,x,y,x-y,'\noutput ellipse\n',ellipse,'\ntest ellipse\n',test_ellipse
      return 'fail'

  test_ellipse = numpy.matrix([[ 0.0306599,      -4.08799,             0,      -5.08241],
                               [  -4.08799,       1421.63,       5.08241,             0],
                               [         0,       5.08241,     0.0306599,      -4.08799],
                               [  -5.08241,             0,      -4.08799,       1421.63]])
  ellipse = Bunch.build_penn_ellipse(2., Common.pdg_pid_to_mass[11], 3., 4., 100., 5., 6., -1.)
  for i,a in enumerate(ellipse.flatten().tolist()):
    x = ellipse.flatten().tolist()[0][i]
    y = test_ellipse.flatten().tolist()[0][i]
    if abs(x - y) > __float_tol*1e3:
      print 'FAILED',i,x,y,x-y,'\noutput ellipse\n',ellipse,'\ntest ellipse\n',test_ellipse
      return 'fail'
  return 'pass'

def bunch_set_covariance_matrix_test(bunch, is_set):
  bunch_copy = bunch.deepcopy()
  bunch_copy.append(Hit.new_from_dict({'x':1e10}))
  mean_equal = bunch_copy.mean(['x'])['x'] == bunch.mean(['x'])['x']
  cov_equal = bunch_copy.moment(['x', 'x']) == bunch.moment(['x', 'x'])
  if is_set == mean_equal and \
     is_set == cov_equal and \
     bunch.covariances_set() == is_set and \
     bunch.means_set() == is_set: 
    return 'pass'
  print "Failed bunch_set_covariance_matrix_test with", is_set, mean_equal, \
        cov_equal, bunch.covariances_set(), bunch.means_set()
  return 'fail'

def bunch_test(bunch):
  test_results = []
  tests = [bunch_delete_test, bunch_str_test, bunch_repr_test, bunch_copy_test, bunch_deepcopy_test, bunch_len_test, 
           bunch_getitem_test, bunch_setitem_test, bunch_conditional_remove_test, 
           bunch_hits_test, bunch_get_hits_test, bunch_mean_test, bunch_moment_test, bunch_moment_global_weight_test, 
           bunch_standard_deviation_test, bunch_axis_list_to_covariance_list_test, bunch_convert_string_to_axis_list_test,
           bunch_set_geometric_momentum_test, bunch_get_axes_test, bunch_get_test, bunch_get_hit_variable_test, bunch_list_get_hit_variable_test, 
           bunch_builtin_io_test, 
           bunch_user_io_test, bunch_get_dispersion_rsquared_test, bunch_canonical_angular_momentum_test, bunch_period_transformation_test, 
           bunch_bunch_weight_test, bunch_clear_local_weights_test, bunch_clear_global_weights_test, bunch_clear_weights_test, bunch_cut_test, 
           bunch_transmission_cut_test, bunch_histogram_var_bins_test, bunch_histogram_test]
  run_test_group(test_results, tests, [(bunch,)]*len(tests))

  try:
    config.has_numpy()
    tests = [bunch_covariance_matrix_test, bunch_translate_test, bunch_abelian_transformation_test,bunch_transform_to_test, bunch_get_amplitude_test]
    args  = [(bunch,)]*len(tests)
    for i in range(len(tests)):
      run_test(test_results, tests[i], args[i])
  except ImportError:
    test_results.append('Warning - could not find NumPy. Skipping NumPy dependent tests')
  try: 
    config.has_root()
    tests = [bunch_root_histogram_test, bunch_root_scatter_graph_test]
    args  = [(bunch,)]*len(tests)
    for i in range(len(tests)):
      run_test(test_results, tests[i], args[i])
  except ImportError:
    test_results.append('Warning - could not find ROOT. Skipping ROOT dependent tests')
  try: 
    config.has_matplot()
    tests = [bunch_matplot_histogram_test, bunch_matplot_scatter_graph_test]
    args  = [(bunch,)]*len(tests)
    for i in range(len(tests)):
      run_test(test_results, tests[i], args[i])
  except ImportError:
    test_results.append('Warning - could not find matplotlib. Skipping matplotlib dependent tests')
  return parse_tests(test_results)

def cut_bc_test():
  """
  Test the private member function _cut and accompanying Bunchcore._cut_double
  """
  bunch = Bunch()
  test = bunch.cut({"x":0.}, operator.ge) == None # regression for bug where
                                                  # hit initialisation wasn't
                                                  # done properly
  hit_1 = Hit.new_from_dict({'x':-1., 'local_weight':1., 'event_number':1})
  hit_2 = Hit.new_from_dict({'x':+1., 'local_weight':1., 'event_number':2})
  bunch = Bunch.new_from_hits([hit_1, hit_2])
  bunch.cut({"x":0.}, operator.ge)
  test &= abs(bunch[0]['local_weight']-1.) < 1e-9
  test &= abs(bunch[1]['local_weight']) < 1.e-9
  test &= abs(bunch[0]['global_weight']-1.) < 1e-9
  test &= abs(bunch[1]['global_weight']-1.) < 1.e-9

  bunch.clear_weights()
  bunch.cut({"x":0.}, operator.ge, global_cut = True)
  test &= abs(bunch[0]['local_weight']-1.) < 1e-9
  test &= abs(bunch[1]['local_weight']-1.) < 1e-9
  test &= abs(bunch[0]['global_weight']-1.) < 1e-9
  test &= abs(bunch[1]['global_weight']) < 1.e-9

  bunch.clear_weights()
  bunch.cut({"event_number":2}, operator.eq, global_cut = True)
  test &= abs(bunch[0]['local_weight']-1.) < 1e-9
  test &= abs(bunch[1]['local_weight']-1.) < 1e-9
  test &= abs(bunch[0]['global_weight']-1.) < 1e-9
  test &= abs(bunch[1]['global_weight']) < 1.e-9

  bunch.clear_weights()
  bunch.cut({"event_number":2}, operator.eq)
  test &= abs(bunch[0]['local_weight']-1.) < 1e-9
  test &= abs(bunch[1]['local_weight']) < 1.e-9
  test &= abs(bunch[0]['global_weight']-1.) < 1e-9
  test &= abs(bunch[1]['global_weight']-1.) < 1e-9

  bunch.cut({"x":0}, operator.ge) # can we pass integers instead of floats
  try:
    bunch.cut({"x":0}, bunch.cut) # incorrect function type (not a comparator)
    test = False
  except TypeError:
    pass

  try:
    bunch.cut({"x":0}, 1) # incorrect type (not a function)
    test = False
  except TypeError:
    pass

  try:
    bunch.cut({"x":"fish"}, operator.eq) # incorrect type
    test = False
  except TypeError:
    pass

  if test:
    return 'pass'
  else:
    return 'fail'

def test_bunch():
  test_results = []
  run_test(test_results, cut_bc_test, ())
  Hit.clear_global_weights()
  hit_list1 = [Hit.new_from_dict({'t':1.,'x':0.,'y':0.,'px':0.,'py':0.,'energy':226.,'mass':Common.pdg_pid_to_mass[13], 'pid':13, 'eventNumber':0, 'charge':-1.},'pz'),
               Hit.new_from_dict({'t':0.,'x':0.,'y':0.,'px':0.,'py':0.,'energy':227.,'mass':Common.pdg_pid_to_mass[13], 'pid':13, 'eventNumber':1, 'charge':-1.},'pz'),
               Hit.new_from_dict({'t':0.,'x':1.,'y':0.,'px':0.,'py':0.,'energy':226.,'mass':Common.pdg_pid_to_mass[13], 'pid':13, 'eventNumber':2, 'charge':-1.},'pz'),
               Hit.new_from_dict({'t':0.,'x':0.,'y':1.,'px':0.,'py':0.,'energy':226.,'mass':Common.pdg_pid_to_mass[13], 'pid':13, 'eventNumber':3, 'charge':-1.},'pz'),
               Hit.new_from_dict({'t':0.,'x':0.,'y':0.,'px':1.,'py':0.,'energy':226.,'mass':Common.pdg_pid_to_mass[13], 'pid':13, 'eventNumber':4, 'charge':-1.},'pz'),
               Hit.new_from_dict({'t':0.,'x':0.,'y':0.,'px':0.,'py':1.,'energy':226.,'mass':Common.pdg_pid_to_mass[11], 'pid':11, 'eventNumber':5, 'charge':-1.},'pz'),
               Hit.new_from_dict({'t':0.,'x':0.,'y':0.,'px':0.,'py':1.,'energy':226.,'mass':Common.pdg_pid_to_mass[13], 'pid':13, 'eventNumber':6, 'charge':-1.},'pz')]
  hit_list2 = [Hit.new_from_dict({'t':2.,'x':0.,'y':0.,'px':0.,'py':0.,'energy':226.,'mass':Common.pdg_pid_to_mass[13], 'pid':13, 'z':100., 'eventNumber':0, 'station':1, 'charge':-1.},'pz'),
               Hit.new_from_dict({'t':0.,'x':0.,'y':0.,'px':0.,'py':0.,'energy':228.,'mass':Common.pdg_pid_to_mass[13], 'pid':13, 'z':100., 'eventNumber':1, 'station':1, 'charge':-1.},'pz'),
               Hit.new_from_dict({'t':0.,'x':2.,'y':0.,'px':0.,'py':0.,'energy':226.,'mass':Common.pdg_pid_to_mass[13], 'pid':13, 'z':100., 'eventNumber':2, 'station':1, 'charge':-1.},'pz'),
               Hit.new_from_dict({'t':0.,'x':0.,'y':2.,'px':0.,'py':0.,'energy':226.,'mass':Common.pdg_pid_to_mass[13], 'pid':13, 'z':100., 'eventNumber':3, 'station':1, 'charge':-1.},'pz'),
               Hit.new_from_dict({'t':0.,'x':0.,'y':0.,'px':2.,'py':0.,'energy':226.,'mass':Common.pdg_pid_to_mass[13], 'pid':13, 'z':100., 'eventNumber':4, 'station':1, 'charge':-1.},'pz'),
               Hit.new_from_dict({'t':0.,'x':0.,'y':0.,'px':0.,'py':2.,'energy':226.,'mass':Common.pdg_pid_to_mass[13], 'pid':13, 'z':100., 'eventNumber':5, 'station':1, 'charge':-1.},'pz')]
  hit_list3 = [Hit.new_from_dict({'t':3.,'x':0.,'y':0.,'px':0.,'py':0.,'energy':226.,'mass':Common.pdg_pid_to_mass[13], 'pid':13, 'z':200., 'eventNumber':0, 'station':2, 'charge':-1.},'pz'),
               Hit.new_from_dict({'t':0.,'x':0.,'y':0.,'px':0.,'py':0.,'energy':229.,'mass':Common.pdg_pid_to_mass[13], 'pid':13, 'z':200., 'eventNumber':1, 'station':2, 'charge':-1.},'pz'),
               Hit.new_from_dict({'t':0.,'x':3.,'y':0.,'px':0.,'py':0.,'energy':226.,'mass':Common.pdg_pid_to_mass[13], 'pid':13, 'z':200., 'eventNumber':2, 'station':2, 'charge':-1.},'pz'),
               Hit.new_from_dict({'t':0.,'x':0.,'y':3.,'px':0.,'py':0.,'energy':226.,'mass':Common.pdg_pid_to_mass[13], 'pid':13, 'z':200., 'eventNumber':3, 'station':2, 'charge':-1.},'pz'),
               Hit.new_from_dict({'t':0.,'x':0.,'y':0.,'px':3.,'py':0.,'energy':226.,'mass':Common.pdg_pid_to_mass[13], 'pid':13, 'z':200., 'eventNumber':4, 'station':2, 'charge':-1.},'pz'),
               Hit.new_from_dict({'t':0.,'x':0.,'y':0.,'px':0.,'py':3.,'energy':226.,'mass':Common.pdg_pid_to_mass[13], 'pid':13, 'z':200., 'eventNumber':5, 'station':2, 'charge':-1.},'pz')]
  hit_list4 = []
  for i in range(-100,100):
    hit_list4.append(Hit.new_from_dict({'t':i,'x':i*i,'y':2./(i*i+0.1),'px':1./(i+0.1),'py':10./(i+0.5),'energy':226.+abs(i),'mass':Common.pdg_pid_to_mass[13], 'pid':13, 'z':200.+i, 'eventNumber':i+100, 'station':2, 'charge':-1.},'pz'))
  bunch    = Bunch.new_from_hits(hit_list1)
  bunch2   = bunch
  bunch3   = bunch.deepcopy()
  bunch3.set_covariance_matrix()
  bunch4   = bunch3.deepcopy()
  bunch_dict = {0:bunch, 1:bunch2, 2:Bunch.new_from_hits(hit_list3), 3:Bunch.new_from_hits(hit_list2), 4:bunch3, 5:bunch4, 6:Bunch.new_from_hits(hit_list4)}
  bunch_list = [bunch, bunch2, Bunch.new_from_hits(hit_list3), Bunch.new_from_hits(hit_list2), bunch3,   bunch4, Bunch.new_from_hits(hit_list4)]
  set_list   = [False, False,  False, False, True, True, False]
  (passes, fails, warns) = (0,0,0)

  for key,a_bunch in bunch_dict.iteritems():
    print '\nTesting bunch',key
    (my_passes, my_fails, my_warns) = bunch_test(a_bunch)
    passes += my_passes
    fails  += my_fails
    warns  += my_warns
  print '\n\n'

  for i, a_bunch in enumerate(bunch_list):
      run_test(test_results, bunch_set_covariance_matrix_test, (a_bunch, set_list[i]))
  tests = [ bunch_equality_test,    bunch_equality_test,    bunch_equality_test,
            bunch_equality_test,    bunch_equality_test,    bunch_equality_test,
            bunch_list_get_test,    bunch_dict_builtin_io_test, 
            bunch_build_ellipse_2d_test, bunch_build_ellipse_penn_test ]
  args  = [(bunch,  bunch2, True), (bunch,  bunch3, False), (bunch3, bunch4, True),
           (bunch,  bunch2, True), (bunch,  bunch3, False), (bunch3, bunch4, True),  
           (bunch_dict,),           (bunch_dict,),
           (),                          ()]
  run_test_group(test_results, tests, args)

  try:
    config.has_numpy()
    run_test(test_results,bunch_new_hit_shell_test, () )
  except ImportError:
    test_results.append('Warning - could not find numpy. Skipping numpy dependent tests')
  try:
    config.has_root()
    run_test(test_results,bunch_root_graph_test, (bunch_dict,) )
    run_test(test_results,bunch_root_graph_test, (bunch_list,) )
  except ImportError:
    test_results.append('Warning - could not find ROOT. Skipping ROOT dependent tests')
  try:
    config.has_matplot()
    run_test(test_results, bunch_matplot_graph_test, (bunch_dict,) )
    run_test(test_results, bunch_matplot_graph_test, (bunch_list,) )
  except ImportError:
    test_results.append('Warning - could not find matplot. Skipping matplot dependent tests')

  try:
    config.has_maus()
    run_test(test_results, bunch_maus_root_io_test, (bunch_dict,) )
  except ImportError:
    test_results.append('Warning - could not find maus. Skipping matplot dependent tests')
  (passesEq, failsEq, warnsEq) = parse_tests(test_results)
  passes += passesEq
  fails  += failsEq
  warns  += warnsEq
  Bunch.clear_global_weights()
  print '\n==============\n||  BUNCH   ||\n=============='
  print 'Passed ',passes,' tests\nFailed ',fails,' tests\n',warns,' warnings\n\n\n'
  return (passes,fails,warns)

class BunchTestCase(unittest.TestCase):
    def test_bunch_all(self):
        passes, fails, warns = test_bunch()
        self.assertEqual(fails, 0)

if __name__ == "__main__":
  unittest.main()


