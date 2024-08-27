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


#ifndef xboa_core_pylib_PyWeightContext_hh
#define xboa_core_pylib_PyWeightContext_hh

#include <Python.h>
#include "utils/SmartPointer.hh"

namespace xboa {
namespace core {

class WeightContext;

namespace PyWeightContext {

struct PyWeightContext {
    PyObject_HEAD;
    SmartPointer<WeightContext> cppcontext_;
};

namespace C_API {
PyWeightContext* create_empty_weightcontext();
bool is_PyWeightContext(PyObject* obj);
}

PyWeightContext* (*create_empty_weightcontext)() = NULL;
bool (*is_PyWeightContext)(PyObject*) = NULL;

int import_PyWeightContext() {
    PyObject* wc_module = PyImport_ImportModule("xboa.core._weight_context");
    if (wc_module == NULL) {
        return 0;
    }
    PyObject *wc_dict  = PyModule_GetDict(wc_module);

    // setup create_empty_hitcore function
    PyObject* cewc_c_api = PyDict_GetItemString(wc_dict,
                                               "C_API_CREATE_EMPTY_WEIGHTCONTEXT");
    void* cewc_void = PyCapsule_GetPointer(cewc_c_api, NULL);
    create_empty_weightcontext = reinterpret_cast<PyWeightContext* (*)()>(cewc_void);

    PyObject* ispwc_c_api = PyDict_GetItemString(wc_dict,
                                               "C_API_IS_PYWEIGHTCONTEXT");
    void* ispwc_void = PyCapsule_GetPointer(ispwc_c_api, NULL);

    is_PyWeightContext = reinterpret_cast<bool (*)(PyObject*)>(ispwc_void);

    delete create_empty_weightcontext();
    return 1;
}

}
}
}

#endif
