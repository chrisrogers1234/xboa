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

std::string get_default_weight_docstring =
std::string("\n");

typedef WeightContext::HitId HitId;

PyObject* getDefaultWeight(PyObject* self, PyObject *args, PyObject *kwds) {
    // self was not initialised - something horrible happened
    if (!C_API::is_PyWeightContext(self)) {
        PyErr_SetString(PyExc_TypeError, "Failed to parse self as a PyWeightContext");
        return NULL;
    }
    PyWeightContext* pywc = reinterpret_cast<PyWeightContext*>(self);
    double weight = pywc->cppcontext_->getDefaultWeight();
    return Py_BuildValue("d", weight); // success, return a double
}

PyObject* setDefaultWeight(PyObject* self, PyObject *args, PyObject *kwds) {
    // self was not initialised - something horrible happened
    if (!C_API::is_PyWeightContext(self)) {
        PyErr_SetString(PyExc_TypeError, "Failed to parse self as a PyWeightContext");
        return NULL;
    }
    PyWeightContext* pywc = reinterpret_cast<PyWeightContext*>(self);
    double weight;
    if(PyArg_ParseTuple(args, "d", &weight) == 0) {
        PyErr_SetString(PyExc_TypeError, "Did not recognise argument as a double");
        return NULL;
    }
    pywc->cppcontext_->setDefaultWeight(weight);
    Py_RETURN_NONE; // success, return None
}

PyObject* setWeight(PyObject* self, PyObject *args, PyObject *kwds) {
    // self was not initialised - something horrible happened
    if (!C_API::is_PyWeightContext(self)) {
        PyErr_SetString(PyExc_TypeError, "Failed to parse self as a PyWeightContext");
        return NULL;
    }
    PyWeightContext* pywc = reinterpret_cast<PyWeightContext*>(self);
    double weight;
    int spill, event, particle;
    std::string argnames[] = {"weight", "spill", "event_number", "particle_number", "eventNumber", "particleNumber"};
    char* c_argnames[] = {argnames[0].data(), argnames[1].data(), argnames[2].data(),
                          argnames[3].data(), argnames[4].data(), argnames[5].data(),
                          NULL};
    int err = PyArg_ParseTupleAndKeywords(args, kwds, "|diiiii",
               c_argnames,
               &weight, &spill, &event, &particle, &event, &particle);
    if(err == 0) {
        PyErr_SetString(PyExc_KeyError,
                "Failed to parse variables in function PyWeightContext.setWeight");
        return NULL;
    }
    WeightContext::HitId hitid = {spill, event, particle};
    pywc->cppcontext_->setWeight(hitid, weight);
    Py_RETURN_NONE; // success, return None
}


PyObject* getWeight(PyObject* self, PyObject *args, PyObject *kwds) {
    // self was not initialised - something horrible happened
    if (!C_API::is_PyWeightContext(self)) {
        PyErr_SetString(PyExc_TypeError, "Failed to parse self as a PyWeightContext");
        return NULL;
    }
    PyWeightContext* pywc = reinterpret_cast<PyWeightContext*>(self);
    int spill, event, particle;
    std::string argnames[] = {"spill", "event_number", "particle_number", "eventNumber", "particleNumber"};
    char* c_argnames[] = {argnames[0].data(), argnames[1].data(), argnames[2].data(),
                          argnames[3].data(), argnames[4].data(), NULL};
    int err = PyArg_ParseTupleAndKeywords(args, kwds, "|iiiii",
               c_argnames,
               &spill, &event, &particle, &event, &particle);
    if(err == 0) {
        PyErr_SetString(PyExc_KeyError,
                "Failed to parse variables in function PyWeightContext.getWeight");
        return NULL;
    }
    WeightContext::HitId hitid = {spill, event, particle};
    double weight = pywc->cppcontext_->getWeight(hitid);
    return Py_BuildValue("d", weight); // success, return a double
}

PyObject* printAddress(PyObject* self, PyObject* args) {
    // self was not initialised - something horrible happened
    if (!C_API::is_PyWeightContext(self)) {
        PyErr_SetString(PyExc_TypeError, "Failed to parse self as a PyWeightContext");
        return NULL;
    }
    PyWeightContext* pywc = reinterpret_cast<PyWeightContext*>(self);
    std::cerr << "Address - pywc " << pywc << " Smartpointer " << &(pywc->cppcontext_) << " Smartpointer target " << pywc->cppcontext_.get() << std::endl;
    Py_RETURN_NONE; // success, return None
}

const char* module_docstring = "_weight_context module for the WeightContext class";

std::string class_docstring =
"WeightContext provides core functionality and C++ bindings for global weights "
"objects.\n\n";

static PyMemberDef _members[] = {
{NULL} // sentinel
};

static PyMethodDef _methods[] = {
{"get_default_weight", (PyCFunction)getDefaultWeight,  METH_VARARGS|METH_KEYWORDS, NULL},
{"set_default_weight", (PyCFunction)setDefaultWeight,  METH_VARARGS|METH_KEYWORDS, NULL},
{"get_weight", (PyCFunction)getWeight,  METH_VARARGS|METH_KEYWORDS, NULL},
{"set_weight", (PyCFunction)setWeight,  METH_VARARGS|METH_KEYWORDS, NULL},
{"print_address", (PyCFunction)printAddress,  METH_VARARGS, NULL},
{NULL} // sentinel
};

PyObject* richCompare(PyObject* self, PyObject* other, int op) {
    if (!C_API::is_PyWeightContext(self) or !C_API::is_PyWeightContext(other)) {
        PyErr_SetString(PyExc_NotImplementedError, "Not able to compare these object types");
        return NULL;
    }
    PyWeightContext* pywc1 = reinterpret_cast<PyWeightContext*>(self);
    PyWeightContext* pywc2 = reinterpret_cast<PyWeightContext*>(other);
    Py_RETURN_RICHCOMPARE(pywc1->cppcontext_.get(), pywc2->cppcontext_.get(), op);
}

PyObject *_alloc(PyTypeObject *type, Py_ssize_t nitems) {
    PyWeightContext* pywc = new PyWeightContext();
    pywc->cppcontext_ = SmartPointer<WeightContext>(new WeightContext());
    Py_SET_REFCNT(pywc, 1);
    Py_TYPE(pywc) = type;
    return reinterpret_cast<PyObject*>(pywc);
}


int _init(PyObject* self, PyObject *args, PyObject *kwds) {
    // self was not initialised - something horrible happened
    if (!C_API::is_PyWeightContext(self)) {
        PyErr_SetString(PyExc_TypeError, "Failed to parse self as a PyWeightContext");
        return -1;
    }
    return 0;
}

void _free(PyWeightContext * self) {
    if (self != NULL) {
        delete self;
    }
}

int parseArg(PyObject* o1, PyObject** f1, PyWeightContext** pywc1) {
    *f1 = PyNumber_Float(o1);
    *pywc1 = reinterpret_cast<PyWeightContext*>(o1);
    if (*f1 == nullptr) {
        PyErr_Clear();
        if (!C_API::is_PyWeightContext(o1)) {
            PyErr_SetString(PyExc_NotImplementedError, "Not able to add these object types");
            return 0;
        }
    } else {
        *pywc1 = nullptr; // it's a float after all
    }
    return 1;
}

template <class UnaryOperator>
PyObject *unary_operator(PyObject *o1) {
    if (!C_API::is_PyWeightContext(o1)) {
            PyErr_SetString(PyExc_NotImplementedError, "Did not recognise object");
            return 0;
    }
    PyWeightContext *pywc1 = reinterpret_cast<PyWeightContext*>(o1);
    WeightContext* wc1 = pywc1->cppcontext_.get();
    UnaryOperator op;
    WeightContext wc2 = op.operate(*wc1);
    PyWeightContext* pywc2 = C_API::create_empty_weightcontext();
    pywc2->cppcontext_.set(new WeightContext(wc2));
    return (PyObject*)pywc2;
}

template <class BinaryOperator>
PyObject *binary_operator(PyObject *o1, PyObject *o2) {
    PyObject *f1, *f2;
    PyWeightContext *pywc1, *pywc2;
    if (parseArg(o1, &f1, &pywc1) == 0) {
        return nullptr;
    }
    if (parseArg(o2, &f2, &pywc2) == 0) {
        return nullptr;
    }

    if (pywc1 == nullptr && pywc2 == nullptr) { // shouldn't ever get here?
        PyErr_SetString(PyExc_NotImplementedError, "Not able to operate on these object types");
        return nullptr;
    }


    BinaryOperator op;
    WeightContext wc3;
    if (pywc1 != nullptr) {
        WeightContext* wc1 = pywc1->cppcontext_.get();
        if (pywc2 == nullptr) {
            double d2 = PyFloat_AsDouble(f2);
            wc3 = op.operate(*wc1, d2);
        } else {
            WeightContext* wc2 = pywc2->cppcontext_.get();
            wc3 = op.operate(*wc1, *wc2);
        }
    } else {
        WeightContext* wc2 = pywc2->cppcontext_.get();
        if (pywc1 == nullptr) {
            double d1 = PyFloat_AsDouble(f1);
            try {
                wc3 = op.operate(d1, *wc2);
            } catch (...) {
                PyErr_SetString(PyExc_NotImplementedError, "Could not accept number as left hand operand");
                return nullptr;
            }
        }
    }
    PyWeightContext* pywc3 = C_API::create_empty_weightcontext();
    pywc3->cppcontext_.set(new WeightContext(wc3));
    return (PyObject*)pywc3;
}

static PyNumberMethods weightContextNumeric = {
    .nb_add = binary_operator<WeightContext::Add>,
    .nb_subtract = binary_operator<WeightContext::Subtract>,
    .nb_multiply = binary_operator<WeightContext::Multiply>,
    .nb_invert = unary_operator<WeightContext::Not>,
    .nb_true_divide = binary_operator<WeightContext::Divide>
};

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
    &weightContextNumeric,      /*tp_as_number*/
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
    richCompare,           /* tp_richcompare */
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

PyWeightContext* C_API::create_empty_weightcontext() {
    PyWeightContext* pywc = new PyWeightContext();
    pywc->cppcontext_ = SmartPointer<WeightContext>(new WeightContext());
    Py_SET_REFCNT(pywc, 1);
    Py_TYPE(pywc) = &PyWeightContextType;
    return pywc;
}

bool C_API::is_PyWeightContext(PyObject* obj) {
     if (PyObject_IsInstance(obj, (PyObject*)&PyWeightContextType)) {
        return true;
    }
    return false;
}

/** NOTE this is the reference counting for the smart pointers */
std::map<WeightContext*, std::size_t>* weightcontext_smartpointer_context =
                                    new std::map<WeightContext*, std::size_t>();

PyMODINIT_FUNC PyInit__weight_context(void) {
    SmartPointer<WeightContext>::set_context(weightcontext_smartpointer_context);

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

    // C API
    PyObject* wc_dict = PyModule_GetDict(module);
    PyObject* cewc_c_api = PyCapsule_New(reinterpret_cast<void*>
                                (C_API::create_empty_weightcontext), NULL, NULL);
    PyDict_SetItemString(wc_dict, "C_API_CREATE_EMPTY_WEIGHTCONTEXT", cewc_c_api);

    PyObject* ispwc_c_api = PyCapsule_New(reinterpret_cast<void*>
                                (C_API::is_PyWeightContext), NULL, NULL);
    PyDict_SetItemString(wc_dict, "C_API_IS_PYWEIGHTCONTEXT", ispwc_c_api);

    return module;
}

} // PyWeightContext
} // core
} // xboa
