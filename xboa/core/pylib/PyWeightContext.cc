#include "pylib/PyWeightContext.hh"

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

#include "cpplib/WeightContext.hh"

#include "pylib/PyWeightContext.hh"

namespace xboa {
namespace core {
namespace PyWeightContext {

struct PyWeightContext {
    PyObject_HEAD;
    WeightContext cppcontext_;
};

std::string get_default_weight_docstring =
std::string("\n");

typedef WeightContext::HitId HitId;

PyObject* get_default_weight(PyObject* self, PyObject *args, PyObject *kwds) {
    PyWeightContext* pywc = reinterpret_cast<PyWeightContext*>(self);
    // failed to cast or self was not initialised - something horrible happened
    if (pywc == NULL) {
        PyErr_SetString(PyExc_TypeError, "Failed to parse self as a PyWeightContext");
        return NULL;
    }
    double weight = pywc->cppcontext_.getDefaultWeight();
    return Py_BuildValue("d", weight); // success, return a double
}

const char* module_docstring = "_weight_context module for the WeightContext class";

std::string class_docstring =
"WeightContext provides core functionality and C++ bindings for global weights "
"objects.\n\n";

static PyMemberDef _members[] = {
{NULL} // sentinel
};

static PyMethodDef _methods[] = {
{"get_default_weight", (PyCFunction)get_default_weight,  METH_VARARGS|METH_KEYWORDS, NULL},
{NULL} // sentinel
};

PyObject *_alloc(PyTypeObject *type, Py_ssize_t nitems) {
    PyWeightContext* pywc = new PyWeightContext();
    Py_SET_REFCNT(pywc, 1);
    Py_TYPE(pywc) = type;
    return reinterpret_cast<PyObject*>(pywc);
}

int _init(PyObject* self, PyObject *args, PyObject *kwds) {
    PyWeightContext* pywc = reinterpret_cast<PyWeightContext*>(self);
    // failed to cast or self was not initialised - something horrible happened
    if (pywc == NULL) {
        PyErr_SetString(PyExc_TypeError,
                        "Failed to resolve self as PyWeightContext in __init__");
        return -1;
    }
    return 0;
}

void _free(PyWeightContext * self) {
    if (self != NULL) {
        delete self;
    }
}


static PyTypeObject PyWeightContextType = {
    PyObject_HEAD_INIT(NULL)
    "_weight_context.WeightContext", /*tp_name*/
    sizeof(PyWeightContext),  /*tp_basicsize*/
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
    0,                     /* tp_traverse */
    0,                     /* tp_clear */
    0,                     /* tp_richcompare */
    0,                     /* tp_weaklistoffset */
    0,                     /* tp_iter */
    0,                     /* tp_iternext */
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

static PyMethodDef _keywdarg_methods[] = {
    {NULL,  NULL}   /* sentinel */
};

static struct PyModuleDef weight_context_def = {
    PyModuleDef_HEAD_INIT,
    "_weight_context",     /* m_name */
    module_docstring,  /* m_doc */
    -1,                  /* m_size */
    _keywdarg_methods,    /* m_methods */
    NULL,                /* m_reload */
    NULL,                /* m_traverse */
    NULL,                /* m_clear */
    NULL,                /* m_free */
};

PyMODINIT_FUNC PyInit__weight_context(void) {
    PyWeightContextType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&PyWeightContextType) < 0) {
        return NULL;
    }
    PyObject* module = PyModule_Create(&weight_context_def);
    if (module == NULL) {
        return NULL;
    }

    PyTypeObject* pywc_type = &PyWeightContextType;
    Py_INCREF(pywc_type);
    PyModule_AddObject(module, "WeightContext", reinterpret_cast<PyObject*>(pywc_type));

    return module;
}

} // PyWeightContext
} // core
} // xboa
