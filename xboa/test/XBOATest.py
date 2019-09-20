"""
Test runner walks through the directory structure at xboa/test and searches for
test_*.py
"""


import os
try:
  import coverage
  my_coverage = coverage.coverage(source=['xboa.hit', 'xboa.bunch', 'xboa.common', 'xboa.tracking', 'xboa.algorithms'])
  my_coverage.start()
except Exception:
  my_coverage = None

import unittest
from io import StringIO
#import io.StringIO as StringIO
import sys
import time
import math
import string
try:
  import numpy
  from numpy import linalg
except ImportError:
  pass
import operator
import bisect

try:
    import ROOT
    ROOT.gROOT.SetBatch(True)
except ImportError:
    pass

class TestRunner(object):
    def __init__(self, test_log, test_dir, test_glob):
        print("Writing everything to "+test_log)
        self.test_log = unittest.runner._WritelnDecorator(open(test_log, 'w'))
        self.test_dir = test_dir
        self.test_glob = test_glob
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.result = None
        self.success = True
        self.failed_dirs = []
        sys.stdout = self.test_log
        sys.stderr = self.test_log

    def do_coverage(self):
        print("Making coverage report")
        if my_coverage != None:
          try:
              my_coverage.stop()
              my_coverage.html_report()
          except Exception:
              sys.excepthook(*sys.exc_info())

    def run_tests(self):
        if not os.path.isdir(self.test_dir):
            raise RuntimeError('Could not find test directory '+self.test_dir+\
                               ', cwd is'+os.getcwd())
        print("Searching for tests", file=self.stdout)
        listing = sorted([_dir for _dir, i, j in os.walk(self.test_dir)])
        print(listing, file=self.stdout)
        for directory in listing:
            self._do_tests(directory)
        return

    def _do_tests(self, dirpath):
        print('\nRunning tests in directory', dirpath)
        self.result = unittest.TextTestResult(sys.stdout , 1, 3)
        loader = unittest.TestLoader().discover(dirpath, self.test_glob)
        loader.run(self.result)
        print("errors:", len(self.result.errors),\
              "failures:", len(self.result.failures),\
              "skipped:", len(self.result.skipped),\
              "expectedFailures:", len(self.result.expectedFailures),\
              "unexpected successes:", len(self.result.unexpectedSuccesses))
        sys.stdout.flush()
        if not self.result.wasSuccessful():
            self.failed_dirs.append(dirpath)
        self.success = self.success and self.result.wasSuccessful()

if __name__ == '__main__':
    log = "test.log"
    runner = TestRunner(log, "./test_bunch", "test_*.py")
    runner.run_tests()
    runner.do_coverage()
    if runner.success:
        print('PASSED all tests')
    else:
        print('FAILED some tests')
        for directory in runner.failed_dirs:
            print('   ', directory)
    print("Test log written to "+log, file=runner.stdout)

