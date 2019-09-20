/** This file is a part of xboa
 *  
 *  xboa is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *  
 *  xboa is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY, without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *  
 *  You should have received a copy of the GNU General Public License
 *  along with xboa in the doc folder.  If not, see 
 *  <http://www.gnu.org/licenses/>.
**/


#ifndef xboa_core_pylib_PyHitcore_hh
#define xboa_core_pylib_PyHitcore_hh

#include <Python.h>

#include "utils/SmartPointer.hh"
#include "cpplib/Hitcore.hh"

namespace xboa {
namespace core {
namespace PyHitcore {

/** PyHitcore is the python implementation of the C++ Hitcore
 */
struct PyHitcore {
    PyObject_HEAD;
    SmartPointer<Hitcore> hitcore_;
};
}
}
}

// Don't #define this unless you know what you are doing. It tells PyHitcore
// that caller is an xboa core library.
// If undefined, we import in "external library" mode (do this if you are not
// sure)
#ifdef xboa_core_PyHitcore_cc

namespace xboa {
namespace core {

class Hitcore; // note this is just in xboa::core namespace

namespace PyHitcore {
/** @namespace C_API defines functions that can be accessed by other C libraries
 *  to interface directly to Py_Hitcore.
 *
 *  To access these functions call int import_PyHitcore() otherwise you
 *  will get a segmentation fault. The import will place the C_API functions in
 *  the xboa::core::Hitcore namespace.
 *
 *  Note these are the functions that can be accessed to provide interfaces to
 *  the Py_Hitcore; access to Hitcore is available through the regular C++ 
 *  routines defined in xboa/core/Hitcore.hh
 */
namespace C_API {

/** Allocate a new PyHitcore
 *
 *  \returns PyHitcore* cast as a PyObject* with hitcore_ pointer set to
 *  NULL. Caller owns the memory allocated to PyHitcore*
 */
static PyObject *create_empty_hitcore();

/** Return the C++ hit associated with PyHitcore
 *
 *  \param py_hitcore PyHitcore* cast as a PyObject*. Python representation
 *         of the hitcore
 *
 *  \returns An SmartPointer to NULL on failure. On success returns a
 *  SmartPointer to Hitcore. py_hitcore still owns a reference to the Hitcore.
 */
static SmartPointer<Hitcore> get_hitcore(PyObject* py_hitcore);

/** Set the C++ hitcore associated with a PyHitcore
 *
 *  \param py_hitcore PyHitcore* cast as a PyObject*. Python representation
 *               of the Hitcore
 *  \param hitcore C++ representation of the Hitcore. PyHitcore
 *             takes ownership of the memory allocated to hitcore
 *
 *  \returns 1 on success, 0 on failure and raises a TypeError
 */
static int set_hitcore(PyObject* py_hitcore, SmartPointer<Hitcore> hitcore);

/** Check that object is a PyHitcore
 *
 *  \param object the object to be checked
 *
 *  \returns true on success, false on failure
 */
static bool check(PyObject *object);
}

/** _alloc allocates memory for PyHitcore
 *
 *  @param type - pointer to a PyHitcore object, as defined in
 *         PyHitcore.cc
 *
 *  returns a PyHitcore* (cast as a PyObject*); caller owns this memory
 */
static PyObject *_alloc(PyTypeObject *type, Py_ssize_t nitems);

/** _init initialises an allocated PyHitcore object
 *
 *  @param self an initialised PyHitcore* cast as a PyObject*; caller owns this
 *         memory
 *  @param args not used
 *  @param kwds not used
 *
 *  @returns 0 on success; -1 on failure
 */
static int _init(PyObject* self, PyObject *args, PyObject *kwds);

/** deallocate memory
 *
 *  @params self an initialised PyHitcore*; memory will be freed by
 *          this function
 */
static void _free(PyHitcore* self);

/** rich compare
 *
 *  @params compare a and b hitcores; only implements == and !=
 *
 *  Returns boolean depending on the memory address of the wrapped hitcore
 */
static PyObject *_richcompare(PyObject *a, PyObject *b, int op);

/** Initialise hitcore module
 *
 *  This is called by import hitcore; it initialises the Hitcore type allowing
 *  user to construct and call methods on Hitcore objects
 */
PyMODINIT_FUNC inithitcore(void);

/** Get the value of a hit variable, referenced by string
 *  
 *  \param self - not used
 *  \param args - not used
 *  \param kwds - keyword arguments; variable, string name of a variable
 */
static PyObject* get(PyObject* self, PyObject *args, PyObject *kwds);

/** Set the value of a hit variable, referenced by string
 *  
 *  \param self - not used
 *  \param args - not used
 *  \param kwds - keyword arguments; variable, string name of a variable
 */
static PyObject* set(PyObject* self, PyObject *args, PyObject *kwds);
}
}
}

#else  // xboa_core_pylib_PyHitcore_cc

/** xboa::core::PyHitcore C API objects
 *
 *  Because of the way python does shared libraries, we have to explicitly
 *  import C functions via the Python API, which is done at import time. This
 *  mimics the functions in xboa::core::PyHitcore. Full documentation is
 *  found there.
 */
namespace xboa {
namespace core {
namespace PyHitcore {

/** import the PyHitcore C_API
 *
 *  Makes the Python functions in C_API available in the xboa::core::PyHitcore
 *  namespace, for other python/C code.
 *
 *  @returns 0 if the import fails; return 1 if it is a success
 */
int import_PyHitcore();

bool (*check)(PyObject *object) = NULL;
PyObject* (*create_empty_hitcore)() = NULL;
int (*get_hitcore)(PyObject* py_hitcore, ::xboa::core::Hitcore* hitcore) = NULL;
int (*set_hitcore)(PyObject* py_hc, ::xboa::core::Hitcore* hitcore) = NULL;
}
}
}

int xboa::core::PyHitcore::import_PyHitcore() {
    PyObject* hc_module = PyImport_ImportModule("xboa.core._hitcore");
    if (hc_module == NULL) {
        return 0;
    }
    PyObject *hc_dict  = PyModule_GetDict(hc_module);

    // setup create_empty_hitcore function
    PyObject* ceh_c_api = PyDict_GetItemString(hc_dict,
                                               "C_API_CREATE_EMPTY_HITCORE");
    void* ceh_void = PyCapsule_GetPointer(ceh_c_api, NULL);
    create_empty_hitcore = reinterpret_cast<PyObject* (*)()>(ceh_void);

    // setup get_hitcore function
    PyObject* ghc_c_api = PyDict_GetItemString(hc_dict, "C_API_GET_HITCORE");
    void* ghc_void = PyCapsule_GetPointer(ghc_c_api, NULL);
    get_hitcore = reinterpret_cast<int(*)(PyObject*, Hitcore*)>(ghc_void);

    // setup set_hitcore function
    PyObject* shc_c_api = PyDict_GetItemString(hc_dict, "C_API_SET_HITCORE");
    void* shc_void = PyCapsule_GetPointer(shc_c_api, NULL);
    set_hitcore = reinterpret_cast<int (*)(PyObject*, Hitcore*)>(shc_void);

    // setup check function
    PyObject* check_c_api = PyDict_GetItemString(hc_dict,
                                               "C_API_CHECK");
    void* check_void =PyCapsule_GetPointer(check_c_api, NULL);
    check = reinterpret_cast<bool (*)(PyObject*)>(check_void);

    // setup global weights context (see hitcore document)
    PyObject* gwc_c_api = PyDict_GetItemString(hc_dict,
                                               "C_API_GLOBAL_WEIGHTS_CONTEXT");
    void* gwc_void = PyCapsule_GetPointer(gwc_c_api, NULL);

    std::map<Hitcore::HitId, double>* gwc =
                reinterpret_cast< std::map<Hitcore::HitId, double>*> (gwc_void);
    Hitcore::set_global_weights_context(gwc);

    // setup smartpointer context (see hitcore document)
    PyObject* spc_c_api = PyDict_GetItemString(hc_dict,
                                               "C_API_SMARTPOINTER_CONTEXT");
    void* spc_void = PyCapsule_GetPointer(spc_c_api, NULL);

    std::map<Hitcore*, std::size_t>* spc =
                reinterpret_cast< std::map<Hitcore*, std::size_t>*>(spc_void);
    SmartPointer<Hitcore>::set_context(spc);

    if ((create_empty_hitcore == NULL) ||
        (set_hitcore == NULL) ||
        (check == NULL) ||
        (get_hitcore == NULL))
        return 0;
    Hitcore::initialise_string_to_accessor_maps();
    Hitcore::initialise_string_to_mutator_maps();

    return 1;
}

#endif  // xboa_core_pylib_PyHitcore_cc
#endif  // xboa_core_pylib_PyHitcore_hh

