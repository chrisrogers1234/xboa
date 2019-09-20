from xboa import *
from xboa.core import *
from xboa.hit   import Hit
from xboa.bunch import Bunch
import xboa.common as Common
from xboa.common import rg

import unittest
import tempfile
import time
import subprocess
import os
import sys
import time
import math
import string
import numpy
from numpy import linalg
import operator
import bisect

import xboa.test.TestTools
run_test = xboa.test.TestTools.run_test
run_test_group = xboa.test.TestTools.run_test_group
__float_tol = xboa.test.TestTools.__float_tol
parse_tests = xboa.test.TestTools.parse_tests

#=======================================================================================================================#
#======================                SYSTEM             ==============================================================#
#=======================================================================================================================#
#
# I don't test that the program dies gracefully if it runs out of memory
# 

def print_mem_usage():
    pid = os.getpid()
    mem_usage = float(os.popen('ps -p %d -o %s | tail -1' % (pid, "rss")).read())
    print "Memory usage for process", os.getpid(), mem_usage
    return mem_usage

def system_mem_test(verbose=True):
  # Test memory usage isn't too huge
  # Test bunch cleans up after itself
  # We allocate new memory in this test and then deallocate it. Python process
  # will increase its buffer but the buffer should be empty by the end. Then
  # run again - python process should not increase buffer size by much as on
  # second iteration we 
  import gc
  gc.collect() #force a memory cleanup
  mem_usage_b4 = print_mem_usage()
  bunch_list=[]
  print "Allocating memory"
  for i in range(3):
    bunch_list.append(Bunch())
    for i in range(10000):
      bunch_list[-1].append(Hit())
      bunch_list[-1][0].get('x')
      bunch_list[-1][0].set('x', 1.)
      bunch_list[-1][0].set('global_weight', 0.5)
      bunch_list[-1][0].get('global_weight') # this function was leaking
    bunch_list[-1].moment(['x'])
  Hit.clear_global_weights()
  mem_usage = print_mem_usage()
  print "Cleaning memory"
  bunch = bunch_list[0]
  while len(bunch) > 0:
    del bunch[0]

  bunch_list.remove(bunch_list[0])
  del bunch_list
  Hit.clear_global_weights()
  gc.collect() #force a memory cleanup
  mem_usage = print_mem_usage()
  if verbose:
    print "Memory usage after cleanup in Mb (target 0 Mb):",mem_usage,'(absolute)',mem_usage-mem_usage_b4,'(difference)'
  if mem_usage-mem_usage_b4 > 1000.: return "warn" # looks like memory leak...
  return "pass"

def system_xboa9f_test_1():
  data = os.path.join('/', sys.prefix, 'share' ,'xboa', 'data')
  temp = tempfile.mkstemp()[1]
  print 'Writing test xboa9f data to ', temp
  proc = subprocess.Popen(['XBOA9f',
                           '-i='+data+'/for009.dat',
                           '-c='+data+'/ecalc9f.inp',
                           '-o='+temp])
  proc.wait()
  if proc.returncode == 0:
      return 'pass'
  else:
      return 'fail'

def test_example(example_name):
  here = os.getcwd()
  os.chdir(os.path.expandvars('$HOME'))
  proc = subprocess.Popen(['python', '-m', 'xboa.examples.'+example_name],
                          stdin=subprocess.PIPE, stdout=sys.stdout,
                          stderr=subprocess.STDOUT)
  while proc.returncode == None:
      proc.communicate(input='\n')
      time.sleep(1)
  proc.wait()
  os.chdir(here)
  if proc.returncode != 0:
      return 'fail'
  return 'pass'

def test_system(test_examples=False):
  test_results = []
  run_test([], system_mem_test, () ) # first time can make the python memory buffer expand - so don't put into test
  run_test(test_results, system_mem_test, () ) # now should work okay - but so dodgy we only return a warn on failure
  run_test(test_results, system_xboa9f_test_1, ())
  run_test(test_results, test_example, ('Example_1',) )
  run_test(test_results, test_example, ('Example_2',) )
  run_test(test_results, test_example, ('Example_3',) )
  run_test(test_results, test_example, ('Example_4',) )
  (passes,fails,warns) = parse_tests(test_results)
  print '\n==============\n||  SYSTEM   ||\n=============='
  print 'Passed ',passes,' tests\nFailed ',fails,' tests\n',warns,' warnings\n\n\n'
  return (passes,fails,warns)


class SystemTestCase(unittest.TestCase):
  def test_system_all(self):
      passes, fails, warns = test_system(True)
      self.assertEqual(fails, 0)

if __name__ == '__main__':
  unittest.main()

