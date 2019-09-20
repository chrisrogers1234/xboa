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

#ifndef xboa_core_pylib_PyBunchcore_hh
#define xboa_core_pylib_PyBunchcore_hh

#include <Python.h>
#include "cpplib/Bunchcore.hh"

// Don't #define this unless you know what you are doing. It tells PyBunchcore
// that caller is an xboa core library.
// If undefined, we import in "external library" mode (do this if you are not
// sure)
#ifdef xboa_core_pylib_PyBunchcore_cc

namespace xboa {
namespace core {

class Bunchcore; // note this is just in xboa::core namespace

namespace PyBunchcore {

/** PyBunchcore is the python implementation of the C++ Bunchcore. Provides
 *  python wrappers for most of the C++ functions
 */
struct PyBunchcore {
    PyObject_HEAD;
    Bunchcore* bunchcore_;
};

/** @namespace C_API defines functions that can be accessed by other C libraries
 *  to interface directly to PyBunchcore.
 *
 *  To access these functions call int import_PyBunchcore() otherwise you
 *  will get a segmentation fault. The import will place the C_API functions in
 *  the xboa::core::Bunchcore namespace.
 *
 *  Note these are the functions that can be accessed to provide interfaces to
 *  the PyBunchcore; access to Bunchcore is available through the regular C++ 
 *  routines defined in xboa/core/Bunchcore.hh
 */
namespace C_API {

/** Allocate a new PyBunchcore
 *
 *  \returns PyBunchcore* cast as a PyObject* with bunchcore_ pointer set to
 *  NULL. Caller owns the memory allocated to PyBunchcore*
 */
static PyObject *create_empty_bunchcore();

/** Return the C++ hit associated with PyBunchcore
 *
 *  \param py_bunchcore PyBunchcore* cast as a PyObject*. Python representation
 *         of the bunchcore
 *
 *  \returns NULL on failure and raises a TypeError. On success returns the
 *  Bunchcore. py_bunchcore still owns the memory allocated to the Bunchcore.
 */
static Bunchcore* get_bunchcore(PyObject* py_bunchcore);

/** Set the C++ Bunchcore associated with a PyBunchcore
 *
 *  \param py_bunchcore PyBunchcore* cast as a PyObject*. Python representation
 *               of the Bunchcore
 *  \param bunchcore C++ representation of the Bunchcore. PyBunchcore
 *             takes ownership of the memory allocated to bunchcore
 *
 *  \returns 1 on success, 0 on failure and raises a TypeError
 */
static int set_bunchcore(PyObject* py_bunchcore, Bunchcore* bunchcore);
}

/** _init initialises an allocated PyBunchcore object
 *
 *  @param self an initialised PyBunchcore* cast as a PyObject*; caller owns this
 *         memory
 *  @param args not used
 *  @param kwds not used
 *
 *  @returns 0 on success; -1 on failure
 */
static int init(PyObject* self, PyObject *args, PyObject *kwds);

/** allocate memory
 *
 *  @params type Bunchcore type
 *  @params nitems not used (always initialised to 0 length)
 */
static PyObject *alloc(PyTypeObject *type, Py_ssize_t nitems);


/** deallocate memory
 *
 *  @params self an initialised PyBunchcore*; memory will be freed by
 *          this function
 */
static void dealloc(PyBunchcore* self);

/** Initialise bunchcore module
 *
 *  This is called by import bunchcore; it initialises the Bunchcore type
 *  allowing user to construct and call methods on Bunchcore objects
 */
PyMODINIT_FUNC initbunchcore(void);

/** Get the PyHitcore at index i
 *  
 *  \param self - the PyBunchcore
 *  \param args - not used
 *  \param kwds - keyword arguments; index, integer index of the hitcore
 *
 *  Raises RangeError if i < -len(Bunchcore) or i >= len(Bunchcore); raises 
 *  ValueError if element at i is NULL. Treats negative indices as "from the
 *  back" in the usual pythonic way.
 */
static PyObject* get_item(PyObject* self, PyObject *args, PyObject *kwds);

/** Set the PyHitcore at index i
 *  
 *  \param self - the PyBunchcore
 *  \param args - not used
 *  \param kwds - keyword arguments;
 *              - index, integer index of the hitcore
 *              - hitcore, PyHitcore object
 *  Extends the Bunchcore so that index is valid; treats negative indices as
 *  "from the back" in the usual pythonic way. Raises RangeError if 
 *  i < -len(Bunchcore)
 */
static PyObject* set_item(PyObject* self, PyObject *args, PyObject *kwds);

/** Get the PyBunchcore length
 *  
 *  \param self - the PyBunchcore
 *  \param args - not used
 *  \param kwds - not used
 *  Returns the integer length of the PyBunchcore
 */
static PyObject* length(PyObject* self, PyObject *args, PyObject *kwds);

/** Get a moment of the PyBunchcore elements
 *  
 *  \param self - the PyBunchcore
 *  \param args - not used
 *  \param kwds - axes, means
 *  Returns the double moment
 */
static PyObject* moment(PyObject* self, PyObject *args, PyObject *kwds);

/** Get a covariance_matrix of the PyBunchcore elements
 *  
 *  \param self - the PyBunchcore
 *  \param args - not used
 *  \param kwds - axes, means
 *  Returns the covariance matrix as a list of lists of floats
 */
static PyObject* covariance_matrix(PyObject* self, PyObject *args, PyObject *kwds);

/** Get a tensor of the PyBunchcore element moments
 *  
 *  \param self - the PyBunchcore
 *  \param args - not used
 *  \param kwds - axes, max_size
 *  Returns a tuple of lists like [moments, power indices]
 */
static PyObject* moment_tensor(PyObject* self, PyObject *args, PyObject *kwds);

/** Get a tensor of the PyBunchcore element moments
 *  
 *  \param self - the PyBunchcore
 *  \param args - not used
 *  \param kwds - max_size, n_axes
 *  Returns a list like power_indices
 */
static PyObject* index_by_power(PyObject* self, PyObject *args, PyObject *kwds);


/** Cut based on a value defined in Hitcore::get_double_names()
 *  
 *  \param self - the PyBunchcore
 *  \param args - not used
 *  \param kwds - cut_variable, comparator, cut_value, is_local
 *  Returns PyNone (just does the cut)
 */
static PyObject* cut_double(PyObject* self, PyObject *args, PyObject *kwds);
}
}
}

#else  // #ifdef xboa_core_PyBunchcore_cc

/** xboa::core::PyHitcore C API objects
 *
 *  Because of the way python does shared libraries, we have to explicitly
 *  import C functions via the Python API, which is done at import time. This
 *  mimics the functions in xboa::core::PyHitcore. Full documentation is
 *  found there.
 */
namespace xboa {
namespace core {
namespace PyBunchcore {

/** import the PyHitcore C_API
 *
 *  Makes the Python functions in C_API available in the xboa::core::PyHitcore
 *  namespace, for other python/C code.
 *
 *  @returns 0 if the import fails; return 1 if it is a success
 */
int import_PyBunchcore();


PyObject* (*create_empty_bunchcore)() = NULL;
int (*get_bunchcore)(PyObject* py_bunchcore, Bunchcore* bunchcore) = NULL;
Bunchcore* (*set_bunchcore)(PyObject* py_hc) = NULL;
}
}
}

int xboa::core::PyBunchcore::import_PyBunchcore() {
  Hitcore::initialise_string_to_accessor_maps();
  Hitcore::initialise_string_to_mutator_maps();

  PyObject* hc_module = PyImport_ImportModule("xboa.core._hitcore");
  if (hc_module == NULL) {
      return 0;
  } else {
    throw std::string("PyHitcore import Not implemented!");
    PyObject *hc_dict  = PyModule_GetDict(hc_module);

    // setup create_empty_hitcore function
    PyObject* ceh_c_api = PyDict_GetItemString(hc_dict,
                                               "C_API_CREATE_EMPTY_HITCORE");
    void* ceh_void = reinterpret_cast<void*>(PyCObject_AsVoidPtr(ceh_c_api));
    PyHitcore::create_empty_hitcore =
                                    reinterpret_cast<PyObject* (*)()>(hem_void);

    // setup get_hitcore function
    PyObject* ghc_c_api = PyDict_GetItemString(hc_dict,
                                               "C_API_GET_HITCORE");
    void* ghc_void = reinterpret_cast<void*>(PyCObject_AsVoidPtr(ghc_c_api));
    PyHitcore::get_hitcore =
                            reinterpret_cast<Hitcore* (*)(PyObject*)>(ghc_void);

    // setup set_hitcore function
    PyObject* shc_c_api = PyDict_GetItemString(hc_dict,
                                               "C_API_SET_HITCORE");
    void* shc_void = reinterpret_cast<void*>(PyCObject_AsVoidPtr(shc_c_api));
    PyHitcore::set_hitcore =
             reinterpret_cast<int (*)(PyObject*, Hitcore*)>(shc_void);
    if ((create_empty_hitcore == NULL) ||
        (set_hitcore == NULL) ||
        (get_hitcore == NULL))
        return 0;
  }
  return 1;
}

#endif  // #ifdef xboa_core_pylib_PyBunchcore_cc
#endif  // #ifdef xboa_core_pylib_PyBunchcore_hh

