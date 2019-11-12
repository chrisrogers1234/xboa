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

try:
    import matplotlib
    import matplotlib.pyplot as pyplot
except ImportError:
    pass
import xboa.common
import xboa.common.config as config


def make_histogram(x_float_list, x_axis_string, n_x_bins,
                           y_float_list=[], y_axis_string='', n_y_bins=0,
                           weight_list=[], fig_index=None):
    """
    Make a matplot graph with data taken from float lists and axes naemd after 
    the axis strings. Return value is a tuple of (hist, graph)
    matplot can format using tex expressions - use '$some math expression$' to include math text in your labels

    - x_float_list  = list of x-data
    - x_axis_string = string used to label the x-axis
    - n_x_bins      = number of bins for x data
    - y_float_list  = list of y-data; if empty, a 1D histogram is made
    - y_axis_string = string used to label the y-axis
    - n_y_bins      = number of bins for y data
    - weight_list   = list of weights; if empty weights are taken to be 1
    - fig_index     = index of figure to use for plots; if None, make a new
                      figure

    After building the graph, use matplotlib.pyplot.show() to show something on the screen
    """
    config.has_matplot()
    config.has_numpy()
    fig_index = get_figure_index(fig_index)
    pyplot.figure(fig_index)
    if(len(x_float_list) == 0):
        raise IndexError('Attempt to draw histogram with no x-points')
    if not len(y_float_list) == len(x_float_list):
        if(weight_list == []):
            (n, my_bins) = numpy.histogram(a=x_float_list, bins=n_x_bins)
        else:
            (n, my_bins) = numpy.histogram(a=x_float_list, bins=n_x_bins, weights=weight_list)
        new_bins  = []
        new_n     = []
        index     = 0
        while(abs(n[index])<1.e-9 and index < len(n)):
            index += 1
        for i in range(index, len(n)-1):
            new_bins.append((my_bins[i] + my_bins[i+1])/2.)
            new_n.append(n[i])
        hist = pyplot.plot(new_bins, new_n)
        pyplot.xlabel(x_axis_string)
    else:
        if len(weight_list) == len(x_float_list):
            hist = pyplot.hist2d(x_float_list, y_float_list, weights=weight_list, bins=(n_x_bins,n_y_bins))
        else:
            hist = pyplot.hist2d(x_float_list, y_float_list, bins=(n_x_bins,n_y_bins))
        pyplot.xlabel(x_axis_string)
        pyplot.ylabel(y_axis_string)
    return fig_index

def make_graph(x_float_list, x_axis_string,
                       y_float_list, y_axis_string,
                       sort=True, fig_index=None, kwds={}):
    """
    Make a matplot graph with data taken from float lists. 
    
    Return value is a tuple of (hist, graph) matplot can format using tex 
    expressions - use '$some math expression$' to include math text in your 
    labels

    - x_float_list  = list of x-data
    - x_axis_string = string used to label the x-axis
    - y_float_list  = list of y-data
    - y_axis_string = string used to label the y-axis
    - sort          = boolean - set to true to automatically sort input data
    - fig_index     = index of figure to use for plots; if None, make a new
                      figure
    - kwds      = keyword argument dictionary.

    After building the graph, use matplotlib.pyplot.show() to show something on 
    the screen

    Returns the matplotlib figure index for this figure.
    """
    config.has_matplot()
    fig_index = get_figure_index(fig_index)
    pyplot.figure(fig_index)
    if(len(x_float_list) == 0 or len(x_float_list) != len(y_float_list)):
        msg = "Attempt to draw graph with %i x points and %i y points. "%\
              (len(x_float_list), len(y_float_list))
        msg += "They should be the same length, with at least 1 element."
        raise IndexError(msg)
    multilist = [x_float_list, y_float_list]
    if sort:
        xboa.common.multisort(multilist)
    x_min_max = xboa.common.min_max(multilist[0])
    y_min_max = xboa.common.min_max(multilist[1])
    myplot = pyplot.plot(x_float_list, y_float_list, **kwds)
    pyplot.xlabel(x_axis_string)
    pyplot.ylabel(y_axis_string)
    pyplot.xlim  (x_min_max[0], x_min_max[1])
    pyplot.ylim  (y_min_max[0], y_min_max[1])
    matplotlib.pyplot.draw()
    return fig_index

def make_multigraph(x_float_list_of_lists, x_axis_string,
                            y_float_list_of_lists, y_axis_string,
                            fig_index=None, kwds=[]):
    """
    Print several different graphs on the same axes. 

    - x_float_list_of_lists = list of lists. Each list will be used as the 
                              x-axis for a graph
    - x_axis_string         = string that will be used to label the x_axis
    - y_float_list_of_lists = list of lists. Each list will be used as the 
                              y-axis for a graph
    - y_axis_string         = string that will be used to label the y_axis
    - fig_index             = index of figure to use for plots; if None, make a
                              new figure
    - kwds                  = list of keyword arguments (dictionaries). Defaults
                              are used if list is length 0.

    E.g. make_matplot_multigraph(
                [[1.,2.,3.,4.], [1.,4.,9.,16.]], 'x',
                [[1.,2.,3.,4.],[1.,2.,3.,4.]], 'f(x)') 
    will make a graph of f = x and  f = x^0.5
    """
    config.has_matplot()
    fig_index = get_figure_index(fig_index)
    pyplot.figure(fig_index)
    total_x_list  = []
    total_y_list  = []
    for a_list in x_float_list_of_lists:
        total_x_list += a_list
    for a_list in y_float_list_of_lists:  total_y_list += a_list
    x_min_max = min_max(total_x_list, margin=rg.graph_margin)
    y_min_max = min_max(total_y_list, margin=rg.graph_margin)
    for index in range( len(x_float_list_of_lists) ):
        if index < len(kwds):
            kwd_args = kwds[index]
        multilist = [x_float_list_of_lists[index], y_float_list_of_lists[index]]
        xboa.common.multisort(multilist)
        myplot = pyplot.plot(multilist[0], multilist[1], **kwd_args)
    pyplot.xlabel(x_axis_string)
    pyplot.ylabel(y_axis_string)
    pyplot.xlim  (x_min_max[0], x_min_max[1])
    pyplot.ylim  (y_min_max[0], y_min_max[1])
    matplotlib.pyplot.draw()
    return fig_index

def make_scatter(x_float_list, x_axis_string, y_float_list, y_axis_string, fig_index=None, kwds={}):
    """
    Make a matplot scatter graph with data taken from float lists and axes naemd after the axis strings.
    matplot can format using tex expressions - use '$some math expression$' to include math text in your labels

    - x_float_list  = list of x-data
    - x_axis_string = string used to label the x-axis
    - y_float_list  = list of y-data
    - y_axis_string = string used to label the y-axis
    - fig_index = index of figure to use for plots; if None, make a new figure
    - kwds      = keyword argument dictionary.

    After building the graph, use matplotlib.pyplot.show() to show something on the screen

    Returns the fig_index used to make the plot
    """
    config.has_matplot()
    fig_index = get_figure_index(fig_index)
    pyplot.figure(fig_index)
    if(len(x_float_list) == 0 or len(x_float_list) != len(y_float_list)):
        msg = "Attempt to draw graph with %i x points and %i y points. "%\
              (len(x_float_list), len(y_float_list))
        msg += "They should be the same length, with at least 1 element."
        raise IndexError(msg)
    hist = pyplot.scatter(x_float_list, y_float_list, s=1, **kwds)
    pyplot.xlabel(x_axis_string)
    pyplot.ylabel(y_axis_string)
    return fig_index

def wait_for_matplot(block=False):
    """
    Show any plots made using matplotlib on the screen
    - block: set to True to block python until windows are closed; set to False
             to continue running python
    """
    config.has_matplot()
    matplotlib.pyplot.show(block)

def get_figure_index(fig_index):
    """Get a unique figure index or return fig_index if != None"""
    global FIGURE_INDEX
    if fig_index != None:
        return fig_index
    FIGURE_INDEX += 1
    return FIGURE_INDEX
        
FIGURE_INDEX = 0