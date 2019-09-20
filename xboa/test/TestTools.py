import os

import io
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

import xboa.common as Common

__float_tol = Common.float_tolerance

def run_test_group(test_results, list_of_functions, list_of_args, alignment=40):
  for i in range(len(list_of_functions)):
    run_test(test_results, list_of_functions[i], list_of_args[i])

def run_test(test_results, function, args, alignment=40):
  test_out  = None
  test_name = function.__name__
  test_name += ' '*(alignment - len(test_name))
  try:
    test_out = str(function(*args))
  except Exception:
    print(('Unhandled exception in test',function.__name__))
    sys.excepthook(*sys.exc_info())
    test_out = 'fail'
  except:
    sys.excepthook(*sys.exc_info())
    raise
  finally:
    sys.stdout.flush()
    sys.stderr.flush()
  test_results.append(test_name+test_out)

def parse_tests(test_results, verbose_bool = True):
  passes = 0
  fails  = 0
  warns  = 0
  for line in test_results:
    if verbose_bool: print(line)
    if   string.find(line, 'fail') >-1: fails +=1
    elif string.find(line, 'False')>-1: fails +=1
    elif string.find(line, 'pass') >-1: passes+=1
    elif string.find(line, 'True') >-1: passes+=1
    elif string.find(line, 'None') >-1: warns +=1
    elif string.find(line, 'warn') < 0: warns +=1 #no output at all => warn
    
    if   string.find(line, 'warn')>-1:  warns +=1
  
  return (passes, fails, warns)


def test_root_hist(hist, name, x_label, y_label, xmin, xmax, ymin, ymax, line_color, line_style, line_width, fill_color, title):
  minmax_hist = [hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax(), hist.GetYaxis().GetXmin(), hist.GetYaxis().GetXmax()]
  minmax_user = [xmin, xmax, ymin, ymax]
  for i in range(4):
    if abs(minmax_hist[i]-minmax_user[i])>Common.float_tolerance:
      print(('test_root_hist failed on minmax',i,'with expected',minmax_user[i],'actual',minmax_hist[i]))
      return False
#  print '@'+hist.GetXaxis().GetTitle()+'@','@'+x_label+'@',':','@'+hist.GetYaxis().GetTitle()+'@','@'+y_label+'@',':',hist.GetTitle(),title,':',hist.GetLineColor(),line_color,':'
#  print hist.GetLineStyle(),line_style,':',hist.GetFillColor(),fill_color,':',hist.GetLineStyle(),line_style,':',hist.GetFillColor(),fill_color
  testpass  = hist.GetXaxis().GetTitle()==x_label and hist.GetYaxis().GetTitle()==y_label and hist.GetTitle()==title
#  print testpass,hist.GetXaxis().GetTitle()==x_label,hist.GetYaxis().GetTitle()==y_label,hist.GetTitle()==title
  testpass &= hist.GetLineColor()==line_color and hist.GetLineStyle()==line_style and hist.GetFillColor()==fill_color
#  print testpass
  testpass &= hist.GetLineStyle()==line_style and hist.GetFillColor()==fill_color
#  print testpass
  return testpass

def test_root_canvas(canvas, name, title, bg_color, highlight_color, border_mode, frame_color):
  testpass  = True
  testpass &= canvas.GetName().find(name) > -1
  testpass &= canvas.GetTitle()          == title
  testpass &= canvas.GetFillColor()      == bg_color 
  testpass &= canvas.GetBorderMode()     == border_mode
  testpass &= canvas.GetFrameFillColor() == frame_color
  return testpass  

def test_root_canvas(canvas, name, title, bg_color, highlight_color, border_mode, frame_color):
  testpass  = True
  testpass &= canvas.GetName().find(name) > -1
  testpass &= canvas.GetTitle()          == title
  testpass &= canvas.GetFillColor()      == bg_color 
  testpass &= canvas.GetBorderMode()     == border_mode
  testpass &= canvas.GetFrameFillColor() == frame_color
  return testpass  


def test_root_graph(graph, name_string, x_list, y_list, line_color, line_style, line_width, fill_color):
  testpass = True
  testpass &= graph.GetN()==len(x_list)
  x   = graph.GetX()
  y   = graph.GetY()
  for i in range( len(x_list) ): testpass &= abs(x[i]-x_list[i])<__float_tol and abs(y[i]-y_list[i])<__float_tol
#  for i in range( len(x_list) ): print x[i],x_list[i],':',y[i],y_list[i]
  testpass &= graph.GetLineColor() == line_color
  testpass &= graph.GetLineStyle() == line_style
  testpass &= graph.GetLineWidth() == line_width
  testpass &= graph.GetFillColor() == fill_color
#  print graph.GetLineColor(),line_color,':',graph.GetLineStyle(),line_style,':',graph.GetLineWidth(),line_width,':',graph.GetFillColor(),fill_color,':'
  return testpass

