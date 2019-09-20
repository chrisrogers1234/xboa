def keep_root_object(root_object):
    """
    Make a root object persistent.
    """
    _root_object_persistent.append(root_object)


## privates
_canvas_persistent      = []
_hist_persistent        = []
_graph_persistent       = []
_legend_persistent      = []
_function_persistent      = []
_root_object_persistent = []
