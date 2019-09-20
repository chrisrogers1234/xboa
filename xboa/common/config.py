import xboa
import sys

PACKAGES = {}

try:
  import libMausCpp
  PACKAGES["maus"] = True
except:
  PACKAGES["maus"] = False

try:
  import ROOT
  ROOT.gStyle.SetPalette(1)
  PACKAGES["root"] = True
except ImportError:
  PACKAGES["root"] = False

try:
  import scipy
  PACKAGES["scipy"] = True
except ImportError:
  PACKAGES["scipy"] = False

try:
  import numpy
  from numpy import linalg
  from numpy import matrix
  PACKAGES["numpy"] = True
except ImportError:
  PACKAGES["numpy"] = False

try:
  import matplotlib
  from matplotlib import pyplot
  PACKAGES["matplot"] = True
except ImportError:
  PACKAGES["matplot"] = False

try:
  import multiprocessing
  PACKAGES["multiprocessing"] = True
except ImportError:
  PACKAGES["multiprocessing"] = False

try:
  import json
  PACKAGES["json"] = True
except ImportError:
  PACKAGES["json"] = False

def print_config():
    print "XBOA Version", xboa.__version__
    print "Python", sys.version.replace('\n', ' ')
    print "Following third party libraries are available:"
    for package in PACKAGES:
        if PACKAGES[package]:
            print "   ", package
    print "Following third party libraries are NOT available:"
    for package in PACKAGES:
        if not PACKAGES[package]:
            print "   ", package

def has_multiprocessing():
  """Raise an exception if multiprocessing libraries have not been imported properly"""
  if not PACKAGES["multiprocessing"]:
    raise ImportError("Attempt to use multiprocessing when library has not been imported - multiprocessing requires matplot >= 2.6")
  return True

def has_maus():
  """Raise an exception if MAUS tracking library has not been imported properly"""
  if not PACKAGES["maus"]:
    raise ImportError("Attempt to use maus when library has not been imported - check your maus installation")
  return True

def has_root():
  """Raise an exception if ROOT graphics libraries have not been imported properly"""
  if not PACKAGES["root"]:
    raise ImportError("Attempt to use root when library has not been imported - check your root installation")
  return True

def has_numpy():
  """Raise an exception if NumPy numerical algebra libraries have not been imported properly"""
  if not PACKAGES["numpy"]:
    raise ImportError("Attempt to use numpy when library has not been imported - check your numpy installation")
  return True

def has_scipy():
  """Raise an exception if SciPy math/analysis libraries have not been imported properly"""
  if not PACKAGES["scipy"]:
    raise ImportError("Attempt to use scipy when library has not been imported - check your scipy installation")
  return True


def has_matplot():
  """Raise an exception if NumPy numerical algebra libraries have not been imported properly"""
  if not PACKAGES["matplot"]:
    raise ImportError("Attempt to use matplotlib when library has not been imported - check your matplotlib installation")
  return True

def has_json():
  """Raise an exception if json data libraries have not been imported properly"""
  if not PACKAGES["json"]:
    raise ImportError("Attempt to use json when library has not been imported - check your json installation (python >= 2.6)")
  return True



