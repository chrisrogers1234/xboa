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

#include <Python.h>
#include <structmember.h>

#include <iostream>
#include <string>

#include <string.h>
#include <stdio.h>

#include "utils/TypeConversions.hh"

#include "cpplib/Hitcore.hh"

// Define tells PyHitcore to import in "xboa include" mode
#define xboa_core_PyHitcore_cc
#include "pylib/PyHitcore.hh"
#undef xboa_core_PyHitcore_cc

namespace xboa {
namespace core {
namespace PyHitcore {

std::string get_docstring =
std::string("Get a variable from the Hitcore. Variables to choose from are:\n");

PyObject* get(PyObject* self, PyObject *args, PyObject *kwds) {
    PyHitcore* hc = reinterpret_cast<PyHitcore*>(self);
    // failed to cast or self was not initialised - something horrible happened
    if (hc == NULL || hc->hitcore_.get() == NULL) {
        PyErr_SetString(PyExc_TypeError, "Failed to parse self as a PyHitcore");
        return NULL;
    }
    const char*  variable_name_c_str;
    if(PyArg_ParseTuple(args, "s", &variable_name_c_str) == 0) {
        PyErr_SetString(PyExc_KeyError,
                "Failed to parse variable as a string in function Hitcore.get");
        return NULL;
    }

    std::string variable_name(variable_name_c_str);
    double value_dbl = 0.;
    if (hc->hitcore_->get_double(variable_name, &value_dbl)) {
        return Py_BuildValue("d", value_dbl); // success, return a double
    }

    int value_int = 0;
    if (hc->hitcore_->get_int(variable_name, &value_int)) {
        return Py_BuildValue("i", value_int); // success, return a double
    }
    PyErr_SetString(PyExc_KeyError, "Did not recognise variable in Hitcore.get");
    return NULL;
}

std::string get_variables_docstring =
std::string("Get a list of variables valid for calling from get(...).");

PyObject* get_variables(PyObject* self, PyObject *args, PyObject *kwds) {
  std::vector<std::string> names = Hitcore::get_names();
  PyObject* list = PyList_New(names.size());
  for(size_t i=0; i<names.size(); i++)
    PyList_SetItem(list, i, Py_BuildValue("s", names[i].c_str())); // ok?
  return list;
}

std::string set_docstring =
std::string("Set a variable in the Hitcore. Variables to choose from are:\n");

PyObject* set(PyObject* self, PyObject *args, PyObject *kwds) {
    PyHitcore* hc = reinterpret_cast<PyHitcore*>(self);
    // failed to cast or self was not initialised - something horrible happened
    if (hc == NULL || hc->hitcore_.get() == NULL) {
        PyErr_SetString(PyExc_TypeError, "Failed to parse self as a PyHitcore");
        return NULL;
    }
    const char*  variable_name_c_str;
    PyObject* py_value;
    if(PyArg_ParseTuple(args, "sO", &variable_name_c_str, &py_value) == 0) {
        PyErr_SetString(PyExc_KeyError,
                "Failed to parse variable as a string in function Hitcore.get");
        return NULL;
    }

    std::string variable_name(variable_name_c_str);
    double value_dbl = PyFloat_AsDouble(py_value);
    if (hc->hitcore_->set_double(variable_name, value_dbl))
        Py_RETURN_NONE; // success, return None

    int value_int = PyLong_AsLong(py_value);
    if (hc->hitcore_->set_int(variable_name, value_int))
        Py_RETURN_NONE; // success, return None

    PyErr_SetString(PyExc_KeyError, "Did not recognise variable in Hitcore.get");
    return NULL;
}

std::string set_variables_docstring =
std::string("Get a list of variables valid for calling from set(...).");

PyObject* set_variables(PyObject* self, PyObject *args, PyObject *kwds) {
  std::vector<std::string> names = Hitcore::set_names();
  PyObject* list = PyList_New(names.size());
  for(size_t i=0; i<names.size(); i++)
    PyList_SetItem(list, i, Py_BuildValue("s", names[i].c_str())); // ok?
  return list;
}

std::string clear_global_weights_docstring =
std::string("Set all global weights to 1.");

PyObject* clear_global_weights(PyObject* self, PyObject *args, PyObject *kwds) {
  Hitcore::clear_global_weights();
  Py_RETURN_NONE;
}

std::string dump_memory_docstring =
    std::string("Dump the hitcore elements that are currently in memory.\n\n")+
    std::string("Takes no arguments.\n\n")+
    std::string("Returns a dictionary mapping memory address (stored as an\n")+
    std::string("integer) to the number of active references to that memory\n")+
    std::string("address.");

PyObject* dump_memory(PyObject* self, PyObject *args, PyObject *kwds) {
    std::map<Hitcore*, size_t>* refs = SmartPointer<Hitcore>::get_context();
    const CppPyPointerToLongConverter<Hitcore> hc_conv;
    const CppPyIntConverter<size_t> size_t_conv;
    CppPyMapToDictConverter<Hitcore*, size_t> map_conv(&hc_conv, &size_t_conv);
    PyObject* memory = NULL;
    map_conv.convert(refs, &memory);
    return memory;
}

const char* module_docstring = "_hitcore module for the Hitcore class";

std::string class_docstring =
std::string("Hitcore provides core functionality and C++ bindings for Hit ")+
std::string("objects.\n\n")+
std::string("__init__(self)\nTakes no arguments and returns an empty Hitcore\n");

static PyMemberDef _members[] = {
{NULL} // sentinel
};

static PyMethodDef _methods[] = {
{"get", (PyCFunction)get,  METH_VARARGS|METH_KEYWORDS, NULL},
{"get_variables", (PyCFunction)get_variables,
                          METH_VARARGS/*METH_STATIC*/, get_variables_docstring.c_str()},
{"set", (PyCFunction)set, METH_VARARGS|METH_KEYWORDS, NULL},
{"set_variables", (PyCFunction)set_variables,
                          METH_VARARGS/*METH_STATIC*/, set_variables_docstring.c_str()},
{"clear_global_weights", (PyCFunction)clear_global_weights,
                          METH_VARARGS/*METH_STATIC*/, clear_global_weights_docstring.c_str()},
{"dump_memory", (PyCFunction)dump_memory,
                          METH_VARARGS/*METH_STATIC*/, dump_memory_docstring.c_str()},
{NULL} // sentinel
};

static PyTypeObject PyHitcoreType = {
    PyObject_HEAD_INIT(NULL)
    "_hitcore.Hitcore", /*tp_name*/
    sizeof(PyHitcore),  /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)_free, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_as_async (python3)*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    class_docstring.c_str(),           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    (richcmpfunc)_richcompare,	       /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    _methods,           /* tp_methods */
    _members,           /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)_init,      /* tp_init */
    (allocfunc)_alloc,    /* tp_alloc, called by new */
    0,                  /* tp_new */
    (freefunc)_free, /* tp_free, called by dealloc */
    0,                  /* tp_is_gc */
    0, /* tp_bases */
    0, /* tp_mro method resolution order */
    0, /* tp_cache */
    0, /* tp_subclasses */
    0, /* tp_weaklist */
    0, /* tp_del */
    1, /* tp_version_tag */
    0, /* tp_finalize */
};

PyObject *_alloc(PyTypeObject *type, Py_ssize_t nitems) {
    PyHitcore* hc = new PyHitcore();
    Py_REFCNT(hc) = 1;
    Py_TYPE(hc) = type;
    hc->hitcore_ = SmartPointer<Hitcore>(NULL);
    return reinterpret_cast<PyObject*>(hc);
}

int _init(PyObject* self, PyObject *args, PyObject *kwds) {
    PyHitcore* hc = reinterpret_cast<PyHitcore*>(self);
    // failed to cast or self was not initialised - something horrible happened
    if (hc == NULL) {
        PyErr_SetString(PyExc_TypeError,
                        "Failed to resolve self as PyHitcore in __init__");
        return -1;
    }
    // legal python to call initialised_object.__init__() to reinitialise, so
    // handle this case; SmartPointer takes ownership of the Hitcore
    if (hc->hitcore_.get() == NULL) {
        Hitcore* new_hc = new Hitcore();
        hc->hitcore_ = SmartPointer<Hitcore>(new_hc);
    }
    return 0;
}

void _free(PyHitcore * self) {
    if (self != NULL) {
        delete self;
    }
}

PyObject *_richcompare(PyObject *py_a, PyObject *py_b, int op_enum) {
    if (!C_API::check(py_a) || !C_API::check(py_b)) // must be PyHitcores
        Py_RETURN_FALSE;
    PyHitcore* hc_a = reinterpret_cast<PyHitcore*>(py_a);
    PyHitcore* hc_b = reinterpret_cast<PyHitcore*>(py_b);
    bool is_equal = hc_a->hitcore_.get() == hc_b->hitcore_.get();
    if (op_enum == Py_EQ) {
        if (is_equal) {
            Py_RETURN_TRUE;
        } else {
            Py_RETURN_FALSE;
        }
    } else if (op_enum == Py_NE) {
        if (is_equal) {
            Py_RETURN_FALSE;
        } else {
            Py_RETURN_TRUE;
        }
    } else {
        PyErr_SetString(PyExc_TypeError,
                      "Only Equals and Not Equals defined for Hitcore compare");
        return NULL;
    }    
}

static PyMethodDef _keywdarg_methods[] = {
    {NULL,  NULL}   /* sentinel */
};

std::map<Hitcore::HitId, double>* hitcore_global_weights_context =
                                         new std::map<Hitcore::HitId, double>();

static void update_set_get_maps() {
    xboa::core::Hitcore::set_global_weights_context(hitcore_global_weights_context);
    xboa::core::Hitcore::initialise_string_to_accessor_maps();
    xboa::core::Hitcore::initialise_string_to_mutator_maps();

    std::vector<std::string> names = xboa::core::Hitcore::get_names();
    for (size_t i = 0; i < names.size(); ++i) {
        get_docstring += "  - "+names[i]+"\n";
    }
    _methods[0].ml_doc = get_docstring.c_str();

    names = xboa::core::Hitcore::set_names();
    for (size_t i = 0; i < names.size(); ++i) {
        set_docstring += "  - "+names[i]+"\n";
    }
    _methods[1].ml_doc = set_docstring.c_str();
}

std::map<Hitcore*, std::size_t>* hitcore_smartpointer_context = new std::map<Hitcore*, std::size_t>();

static struct PyModuleDef hitcoredef = {
    PyModuleDef_HEAD_INIT,
    "_hitcore",     /* m_name */
    module_docstring,  /* m_doc */
    -1,                  /* m_size */
    _keywdarg_methods,    /* m_methods */
    NULL,                /* m_reload */
    NULL,                /* m_traverse */
    NULL,                /* m_clear */
    NULL,                /* m_free */
};

PyMODINIT_FUNC PyInit__hitcore(void) {
    SmartPointer<Hitcore>::set_context(hitcore_smartpointer_context);
    PyHitcoreType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&PyHitcoreType) < 0) return NULL;
    PyObject* module = PyModule_Create(&hitcoredef);
    if (module == NULL) return NULL;
    // updates the Hitcore get, set maps and sets docstrings
    update_set_get_maps();

    PyTypeObject* hc_type = &PyHitcoreType;
    Py_INCREF(hc_type);
    PyModule_AddObject(module, "Hitcore", reinterpret_cast<PyObject*>(hc_type));

    // C API 
    PyObject* hc_dict = PyModule_GetDict(module);
    PyObject* ceh_c_api = PyCapsule_New(reinterpret_cast<void*>
                                (C_API::create_empty_hitcore), NULL, NULL);
    PyObject* ghc_c_api = PyCapsule_New(reinterpret_cast<void*>
                                (C_API::get_hitcore), NULL, NULL);
    PyObject* shc_c_api = PyCapsule_New(reinterpret_cast<void*>
                                (C_API::set_hitcore), NULL, NULL);
    PyObject* check_c_api = PyCapsule_New(reinterpret_cast<void*>
                                (C_API::check), NULL, NULL);
    PyObject* gwc_c_api = PyCapsule_New(reinterpret_cast<void*>
                                (hitcore_global_weights_context), NULL, NULL);
    PyObject* spc_c_api = PyCapsule_New(reinterpret_cast<void*>
                                (hitcore_smartpointer_context), NULL, NULL);
    PyDict_SetItemString(hc_dict, "C_API_CREATE_EMPTY_HITCORE", ceh_c_api);
    PyDict_SetItemString(hc_dict, "C_API_GET_HITCORE", ghc_c_api);
    PyDict_SetItemString(hc_dict, "C_API_SET_HITCORE", shc_c_api);
    PyDict_SetItemString(hc_dict, "C_API_CHECK", check_c_api);
    PyDict_SetItemString(hc_dict, "C_API_GLOBAL_WEIGHTS_CONTEXT", gwc_c_api);
    PyDict_SetItemString(hc_dict, "C_API_SMARTPOINTER_CONTEXT", spc_c_api);

    return module;
}

SmartPointer<Hitcore> C_API::get_hitcore(PyObject* py_hc) {
    if (py_hc == NULL || py_hc->ob_type != &PyHitcoreType) {
        return SmartPointer<Hitcore>();
    }
    return reinterpret_cast<PyHitcore*>(py_hc)->hitcore_;
}

int C_API::set_hitcore(PyObject* py_hc_o, SmartPointer<Hitcore> hc) {
    if (py_hc_o == NULL || py_hc_o->ob_type != &PyHitcoreType) {
        PyErr_SetString(PyExc_TypeError,
                        "Could not resolve object to a Hitcore");
        return 0;
    }
    PyHitcore* py_hc = reinterpret_cast<PyHitcore*>(py_hc_o);
    py_hc->hitcore_ = hc;
    return 1;
}

PyObject *C_API::create_empty_hitcore() {
    return _alloc(&PyHitcoreType, 0);
}

bool C_API::check(PyObject* py_hc) {
    return (py_hc != NULL && py_hc->ob_type == &PyHitcoreType);
}

} // PyHitcore
} // core
} // xboa
