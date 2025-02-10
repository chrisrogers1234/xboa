import sys

def require_modules(modules):
    """
    Check if modules in modules are imported

    - modules: if a string, name of a module; if a list, list of names of a
                   module

    Returns None if modules are imported

    Throws ImportError if one or more modules are not available
    """
    if type(modules) == type(""):
        modules = [modules]
    err_list = []
    for module_name in modules:
        if module_name not in sys.modules:
            err_list.append(module_name)
    if len(err_list):
        raise ImportError(f"Could not find required modules: {str(err_list)}")
