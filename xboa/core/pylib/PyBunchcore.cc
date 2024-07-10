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
#include "structmember.h"
#include <iostream>


#include "utils/TypeConversions.hh"
#include "utils/PythonComparator.hh"

// Define tells PyHitcore to import in "xboa include" mode
#define xboa_core_pylib_PyBunchcore_cc
#include "pylib/PyBunchcore.hh"
#undef  xboa_core_pylib_PyBunchcore_cc

#include "pylib/PyHitcore.hh"

namespace xboa {
namespace core {

namespace PyBunchcore {

PyObject *alloc(PyTypeObject *type, Py_ssize_t nitems) {
    PyBunchcore* bc = new PyBunchcore();
    Py_SET_REFCNT(bc, 1);
    Py_TYPE(bc) = type;
    return reinterpret_cast<PyObject*>(bc);
}

int init(PyObject* self, PyObject *args, PyObject *kwds) {
    PyBunchcore* bc = reinterpret_cast<PyBunchcore*>(self);
    // failed to cast or self was not initialised - something horrible happened
    if (bc == NULL) {
        PyErr_SetString(PyExc_TypeError,
                        "Failed to resolve self as Bunchcore in __init__");
        return -1;
    }
    // legal python to call initialised_object.__init__() to reinitialise, so
    // handle this case
    if (bc->bunchcore_ == NULL) {
        bc->bunchcore_ = new Bunchcore();
    }
    return 0;
}

void dealloc(PyBunchcore* self) {
    if (self != NULL) {
        if (self->bunchcore_ != NULL) {
            delete self->bunchcore_;
            self->bunchcore_ = NULL;
        }
        delete self;
    }
}

std::string get_item_docstring = 
    std::string("Get an element in the Bunchcore\n")+
    std::string("  - index: integer indexing the element in the Bunchcore.\n")+
    std::string("    Supports negative indices, meaning index from the end.\n")+
    std::string("Returns a Hitcore if the value was\n")+
    std::string("allocated or None if the value was not allocated. Raises\n")+
    std::string("an IndexError if the value is out of range or TypeError for\n")+
    std::string("incorrect inputs\n");

PyObject* get_item(PyObject* self, PyObject *args, PyObject *kwds) {
    Bunchcore* bc = reinterpret_cast<PyBunchcore*>(self)->bunchcore_;
    if (bc == NULL) { // not possible! (Haha)
        PyErr_SetString(PyExc_TypeError,
                        "Failed to interpret self as a Bunchcore");
        return NULL;
    }
    // Extract index and check bounds
    static char *kwlist[] = {const_cast<char*>("index"), NULL};
    PyObject* py_index;
    if (PyArg_ParseTupleAndKeywords(args, kwds, "O|", kwlist, &py_index) == 0)
        return NULL;
    size_t index;
    if (!PyCppIndexConverter(bc->length()).convert(py_index, &index))
        return NULL;
    // Extract the data from the hitcores_ array; if it is NULL, return None
    SmartPointer<Hitcore> hc = bc->get_item(index);
    if (hc.get() == NULL) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    // Wrap in a PyHitcore and return
    PyObject* py_return = PyHitcore::create_empty_hitcore();
    PyHitcore::PyHitcore* py_hc =
                             reinterpret_cast<PyHitcore::PyHitcore*>(py_return);
    if (py_hc == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to allocate Hitcore");
        return NULL;
    }
    py_hc->hitcore_ = hc;
    return py_return;
}

std::string set_item_docstring = 
    std::string("Set an element in the Bunchcore\n")+
    std::string("  - index: integer indexing the element in the Bunchcore.\n")+
    std::string("    Supports negative indices, meaning index from the end.\n")+
    std::string("  - value: Hitcore object.\n")+
    std::string("Raises an IndexError if the index is out of range.\n");

PyObject* set_item(PyObject* self, PyObject *args, PyObject *kwds) {
    Bunchcore* bc = reinterpret_cast<PyBunchcore*>(self)->bunchcore_;
    if (bc == NULL) { // not possible! (Haha)
        PyErr_SetString(PyExc_TypeError,
                        "Failed to interpret self as a Bunchcore");
        return NULL;
    }
    // Extract arguments
    static char *kwlist[] = {const_cast<char*>("value"),
                             const_cast<char*>("index"),
                             NULL};
    PyObject *py_index, *py_hc;
    if (PyArg_ParseTupleAndKeywords(args, kwds, "OO|", kwlist,
                                    &py_hc, &py_index) == 0) {
        return NULL;
    }
    // Get the index
    size_t index;
    if (!PyCppIndexConverter().convert(py_index, &index))
        return NULL;
    // Get the Hitcore smart pointer
    if (!PyHitcore::check(py_hc)) {
        PyErr_SetString(PyExc_TypeError,
                        "Failed to interpret value as a Hitcore");
        return NULL;
    }

    PyHitcore::PyHitcore* py_hc_alt =
                                 reinterpret_cast<PyHitcore::PyHitcore*>(py_hc);

    // Py_INCREF(py_hc);
    bc->set_item(index, py_hc_alt->hitcore_);
    Py_RETURN_NONE;
}

std::string del_item_docstring = "Pass\n";

PyObject* del_item(PyObject* self, PyObject *args, PyObject *kwds) {
    Bunchcore* bc = reinterpret_cast<PyBunchcore*>(self)->bunchcore_;
    if (bc == NULL) { // not possible! (Haha)
        PyErr_SetString(PyExc_TypeError,
                        "Failed to interpret self as a Bunchcore");
        return NULL;
    }
    // Extract index and check bounds
    static char *kwlist[] = {const_cast<char*>("index"), NULL};
    PyObject* py_index;
    if (PyArg_ParseTupleAndKeywords(args, kwds, "O|", kwlist, &py_index) == 0)
        return NULL;
    size_t index;
    if (!PyCppIndexConverter(bc->length()).convert(py_index, &index))
        return NULL;
    bc->del_item(index);
    Py_RETURN_NONE;
}
std::string length_docstring = 
    std::string("Return the length of the Bunchcore.\n");

PyObject* length(PyObject* self, PyObject *args, PyObject *kwds) {
    Bunchcore* bc = reinterpret_cast<PyBunchcore*>(self)->bunchcore_;
    if (bc == NULL) { // not possible! (Haha)
        PyErr_SetString(PyExc_TypeError,
                        "Failed to interpret self as a Bunchcore");
        return NULL;
    }
    PyObject* py_length = PyLong_FromSize_t(bc->length());
    if (py_length == NULL) { // not possible! (Haha)
        PyErr_SetString(PyExc_RuntimeError,
                        "Failed to make a Long");
        return NULL;
    }
    return py_length;
}

std::string moment_docstring =
    std::string("Calculate a moment.\n")+
    std::string(" - axes: list of strings that defines the axes over which\n")+
    std::string("   the calculation is made.\n")+
    std::string(" - means: dict defining centre about which the moment is\n")+
    std::string("   calculated. If a variable is missing, calculate the\n")+
    std::string("   mean and use that.")+
    std::string("Moment m is given by\n")+
    std::string("  m = \\Sigma_j{\\Pi_i[w*(u_{ij}-<u_i>)]}/w\n")+
    std::string("Where: u_{i} is a variable listed in axes; i indexes the\n")+
    std::string("axis and j indexes the hit; w is the total weight; <u_i>\n")+
    std::string("is the mean.\n")+
    std::string("Return value is a float.\n");

PyObject* moment(PyObject* self, PyObject *args, PyObject *kwds) {
    Bunchcore* bc = reinterpret_cast<PyBunchcore*>(self)->bunchcore_;
    if (bc == NULL) { // not possible! (Haha)
        PyErr_SetString(PyExc_TypeError,
                        "Failed to interpret self as a Bunchcore");
        return NULL;
    }
    // Extract arguments to pyobjects
    static char *kwlist[] = {const_cast<char*>("axes"),
                             const_cast<char*>("means"),
                             NULL};
    PyObject *py_axes, *py_means;
    if (PyArg_ParseTupleAndKeywords(args, kwds, "OO|", kwlist,
                                    &py_axes, &py_means) == 0)
        return NULL;

    // convert arguments to C objects
    std::vector<std::string> axes;
    std::map<std::string, double> means;
    PyCppStringConverter string_conv;
    PyCppDoubleConverter double_conv;
    PyCppListToVectorConverter<std::string> list_conv(&string_conv);
    PyCppDictToMapConverter<std::string, double> dict_conv(&string_conv,
                                                           &double_conv);
    if (!list_conv.convert(py_axes, &axes))
        return NULL;
    if (!dict_conv.convert(py_means, &means))
        return NULL;

    // call moment calculation routine
    double moment;
    if(!bc->get_moment(axes, means, &moment)) {
        PyErr_SetString(PyExc_ValueError, "Failed to calculate moment");
        return NULL;
    }

    // return
    PyObject* py_moment = PyFloat_FromDouble(moment);
    Py_INCREF(py_moment);
    return py_moment;
}


std::string covariance_matrix_docstring = 
    std::string("Calculate the covariance matrix.\n")+
    std::string(" - axes: list of strings that defines the axes over which\n")+
    std::string("   the calculation is made.\n")+
    std::string(" - means: dict defining centre about which the matrix is\n")+
    std::string("   calculated. If a variable is missing, calculate the\n")+
    std::string("   mean and use that.\n")+
    std::string("Covariance matrix is a matrix with elements <u_{i}, u_{j}>,")+
    std::string("where i, j index the axis from axes so that <u_{i}, u_{j}>\n")+
    std::string("is a second moment.\n")+
    std::string("Return value is a list of list of floats.\n");

PyObject* covariance_matrix(PyObject* self, PyObject *args, PyObject *kwds) {
    Bunchcore* bc = reinterpret_cast<PyBunchcore*>(self)->bunchcore_;
    if (bc == NULL) { // not possible! (Haha)
        PyErr_SetString(PyExc_TypeError,
                        "Failed to interpret self as a Bunchcore");
        return NULL;
    }
    // Extract arguments to pyobjects
    static char *kwlist[] = {const_cast<char*>("axes"),
                             const_cast<char*>("means"),
                             NULL};
    PyObject *py_axes, *py_means;
    if (PyArg_ParseTupleAndKeywords(args, kwds, "OO|", kwlist,
                                    &py_axes, &py_means) == 0)
        return NULL;
    // convert arguments to C objects
    std::vector<std::string> axes;
    std::map<std::string, double> means;
    PyCppStringConverter string_conv;
    PyCppDoubleConverter double_conv;
    PyCppListToVectorConverter<std::string> list_conv(&string_conv);
    PyCppDictToMapConverter<std::string, double> dict_conv(&string_conv,
                                                           &double_conv);
    if (!list_conv.convert(py_axes, &axes))
        return NULL;
    if (!dict_conv.convert(py_means, &means))
        return NULL;
    // call matrix calculation routine
    std::vector< std::vector<double> > matrix;
    if (!bc->covariance_matrix(axes, means, &matrix)) {
        PyErr_SetString(PyExc_ValueError,
                        "Failed to calculate covariance matrix");
        return NULL;
    }
    // convert to pymatrix
    CppPyDoubleConverter double_out;
    CppPyVectorToListConverter<double> vec_out(&double_out);
    CppPyVectorToListConverter<std::vector<double> > vec_vec_out(&vec_out);
    PyObject* py_list;
    if (!vec_vec_out.convert(&matrix, &py_list))
        return NULL;
    return py_list;
}

std::string cut_double_docstring = 
    std::string("Set statistical weight to 0 for a variable of double type.\n")+
    std::string(" - cut_variable: string that indexes the variable to be\n")+
    std::string("   cut on.\n")+
    std::string(" - comparator: Python callable (function) that does the\n")+
    std::string("   comparison. Should take two float arguments and return\n")+
    std::string("   a boolean.\n")+
    std::string(" - cut: will cut if comparator(hit_value, cut) returns\n")+
    std::string("   true.\n")+
    std::string(" - is_global: set to True to change global_weight; or\n")+
    std::string("   False to change local_weight\n")+
    std::string("Returns None\n");

PyObject* cut_double(PyObject* self, PyObject *args, PyObject *kwds) {
    Bunchcore* bc = reinterpret_cast<PyBunchcore*>(self)->bunchcore_;
    if (bc == NULL) { // not possible! (Haha)
        PyErr_SetString(PyExc_TypeError,
                        "Failed to interpret self as a Bunchcore");
        return NULL;
    }
    // Extract arguments
    static char *kwlist[] = {const_cast<char*>("cut_variable"),
                             const_cast<char*>("comparator"),
                             const_cast<char*>("cut"),
                             const_cast<char*>("is_global"),
                             NULL};
    PyObject *py_comparator = NULL;
    PyObject *py_is_global = NULL;
    const char* cut_var_c_str = NULL;
    double cut = 0.;
    if (PyArg_ParseTupleAndKeywords(args, kwds, "sOdO|", kwlist,
                      &cut_var_c_str, &py_comparator, &cut, &py_is_global) == 0)
        return NULL;
    if (cut_var_c_str == NULL || py_comparator == NULL) {
        PyErr_SetString(PyExc_TypeError,
                        "Missing mandatory arguments");
        return NULL;
    }
    if (PyCallable_Check(py_comparator) == 0) {
        PyErr_SetString(PyExc_TypeError,
                        "Comparator not callable");
        return NULL;
    }
    // convert to cpp
    bool is_global = py_is_global == NULL || PyObject_IsTrue(py_is_global) == 1;
    std::string cut_variable(cut_var_c_str);
    utils::PythonComparator comp(py_comparator);
    // call bunchcore core function
    bool is_okay = bc->cut_double(cut_variable, &comp, cut, is_global);
    if (!is_okay) {
        PyErr_SetString(PyExc_TypeError, "Failed to call cut_double");
        return NULL;        
    }
    // return none
    Py_RETURN_NONE;
}

std::string moment_tensor_docstring =
    std::string("\n");

PyObject* moment_tensor(PyObject* self, PyObject *args, PyObject *kwds) {
    Bunchcore* bc = reinterpret_cast<PyBunchcore*>(self)->bunchcore_;
    if (bc == NULL) { // not possible! (Haha)
        PyErr_SetString(PyExc_TypeError,
                        "Failed to interpret self as a Bunchcore");
        return NULL;
    }
    // Extract arguments
    static char *kwlist[] = {const_cast<char*>("axes"),
                             const_cast<char*>("max_power"),
                             NULL};
    PyObject* py_axes;
    int max_power = -1;
    if (PyArg_ParseTupleAndKeywords(args, kwds, "Oi|", kwlist,
                                                    &py_axes, &max_power) == 0)
        return NULL;
    if (max_power < 0) {
        PyErr_SetString(PyExc_ValueError, "Negative maximum power");
        return NULL;
    }
    PyCppStringConverter str_conv;
    PyCppListToVectorConverter<std::string> list_conv(&str_conv);
    std::vector<std::string> axes;
    list_conv.convert(py_axes, &axes);
    std::vector<std::vector<size_t> > index_by_power;
    std::vector<double> moments;
    bool ok = bc->get_moment_tensor(axes, max_power, &moments, &index_by_power);
    if (!ok) {
        PyErr_SetString(PyExc_RuntimeError, "Failed during moment tensor call");
        return NULL;
    }
    CppPyDoubleConverter double_converter;
    CppPyVectorToListConverter<double> vec_converter(&double_converter);
    PyObject* py_list;
    vec_converter.convert(&moments, &py_list);
    return py_list;
}

std::string index_by_power_docstring =
    std::string("Get the list of variables used for calculating moment\n")+
    std::string("tensors.\n")+
    std::string("  - max_order: maximum sum of powers in an index\n")+
    std::string("  - n_axes: number of axes (length of each index)\n")+
    std::string("Return value is an index as described in e.g.\n")+
    std::string("get_moment_tensor, i.e.index_by_power = [2, 0, 1, 2] means\n")+
    std::string(" x_0^2*x_2^1*x_3^2 for some vector x\n");


PyObject* index_by_power(PyObject* self, PyObject *args, PyObject *kwds) {
    // Extract arguments
    static char *kwlist[] = {const_cast<char*>("max_power"),
                             const_cast<char*>("n_axes"),
                             NULL};
    int max_power = -1;
    int n_axes = -1;
    if (PyArg_ParseTupleAndKeywords(args, kwds, "ii|", kwlist,
                                                      &max_power, &n_axes) == 0)
        return NULL;
    if (max_power < 0) {
        PyErr_SetString(PyExc_ValueError, "Negative maximum power");
        return NULL;
    }
    if (n_axes < 1) {
        PyErr_SetString(PyExc_ValueError, "Number of axes must be at least 1");
        return NULL;
    }
    std::vector<std::vector<size_t> > powers =
                               Bunchcore::get_index_by_power(max_power, n_axes);
    // Now convert to python
    CppPyIntConverter<size_t> size_t_converter;
    CppPyVectorToListConverter<size_t> vec_converter(&size_t_converter);
    CppPyVectorToListConverter<std::vector<size_t> >
                                              vec_vec_converter(&vec_converter);
    PyObject* py_list = NULL;
    vec_vec_converter.convert(&powers, &py_list);
    return py_list;
}

static PyMemberDef Bunchcore_members[] = {
    {NULL},
};

static PyMethodDef Bunchcore_methods[] = {
    {"set_item",  (PyCFunction)set_item, METH_VARARGS|METH_KEYWORDS, set_item_docstring.c_str()},
    {"get_item",  (PyCFunction)get_item, METH_VARARGS|METH_KEYWORDS, get_item_docstring.c_str()},
    {"del_item",  (PyCFunction)del_item, METH_VARARGS|METH_KEYWORDS, del_item_docstring.c_str()},
    {"length",    (PyCFunction)length,   METH_VARARGS|METH_KEYWORDS, length_docstring.c_str()},
    {"moment",    (PyCFunction)moment, METH_VARARGS|METH_KEYWORDS, moment_docstring.c_str()},
    {"covariance_matrix", (PyCFunction)covariance_matrix, METH_VARARGS|METH_KEYWORDS, covariance_matrix_docstring.c_str()},
    {"cut_double", (PyCFunction)cut_double, METH_VARARGS|METH_KEYWORDS, cut_double_docstring.c_str()},
    {"moment_tensor", (PyCFunction)moment_tensor, METH_VARARGS|METH_KEYWORDS, moment_tensor_docstring.c_str()},
    {"index_by_power", (PyCFunction)index_by_power, METH_VARARGS|METH_KEYWORDS, index_by_power_docstring.c_str()},
    {NULL}
};

static PySequenceMethods Bunchcore_as_seq = {
    (lenfunc)length, //lenfunc PySequenceMethods.sq_length
    0, //binaryfunc PySequenceMethods.sq_concat
    0, //ssizeargfunc PySequenceMethods.sq_repeat
    0, //ssizeargfunc PySequenceMethods.sq_item
    0, //ssizeobjargproc PySequenceMethods.sq_ass_item
    0, //objobjproc PySequenceMethods.sq_contains
    0, //binaryfunc PySequenceMethods.sq_inplace_concat
    0, //ssizeargfunc PySequenceMethods.sq_inplace_repeat
};

static PyTypeObject PyBunchcoreType = {
    PyObject_HEAD_INIT(NULL)
    "_bunchcore.Bunchcore",     /*tp_name*/
    sizeof(Bunchcore),         /*tp_basicsize*/
    sizeof(xboa::core::PyHitcore::PyHitcore),  /*tp_itemsize*/
    (destructor)dealloc,     /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    &Bunchcore_as_seq,          /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Bunchcore objects",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    Bunchcore_methods,           /* tp_methods */
    Bunchcore_members,           /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)init,      /* tp_init */
    (allocfunc)alloc,   /* tp_alloc */
    0,                 /* tp_new */
    (freefunc)dealloc, /* tp_free, called by dealloc */
};

const char* module_docstring = "_bunchcore module for the Bunchcore class";

static struct PyModuleDef bunchcoredef = {
    PyModuleDef_HEAD_INIT,
    "_bunchcore",     /* m_name */
    module_docstring,  /* m_doc */
    -1,                  /* m_size */
    NULL,    /* m_methods */
    NULL,                /* m_reload */
    NULL,                /* m_traverse */
    NULL,                /* m_clear */
    NULL,                /* m_free */
};

PyMODINIT_FUNC PyInit__bunchcore(void) {
    PyBunchcoreType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&PyBunchcoreType) < 0) {
        return NULL;
    }
    PyObject* module = PyModule_Create(&bunchcoredef);
    if (module == NULL) {
        return NULL;
    }

    Py_INCREF(&PyBunchcoreType);
    PyModule_AddObject(module, "Bunchcore", (PyObject *)&PyBunchcoreType);
    // import pyhitcore C_API
    PyHitcore::import_PyHitcore();
    PyObject* py_obj_hc =  xboa::core::PyHitcore::create_empty_hitcore();
    PyHitcore::PyHitcore* hc = reinterpret_cast<PyHitcore::PyHitcore*>(py_obj_hc); 
    SmartPointer<Hitcore>::set_context(hc->hitcore_.get_context());
    // C API
    PyObject* bc_dict = PyModule_GetDict(module);
    PyObject* ceb_c_api = PyCapsule_New(reinterpret_cast<void*>
                                (C_API::create_empty_bunchcore), NULL, NULL);
    PyObject* gbc_c_api = PyCapsule_New(reinterpret_cast<void*>
                                (C_API::get_bunchcore), NULL, NULL);
    PyObject* sbc_c_api = PyCapsule_New(reinterpret_cast<void*>
                                (C_API::set_bunchcore), NULL, NULL);
    PyDict_SetItemString(bc_dict, "C_API_CREATE_EMPTY_BUNCHCORE", ceb_c_api);
    PyDict_SetItemString(bc_dict, "C_API_GET_BUNCHCORE", gbc_c_api);
    PyDict_SetItemString(bc_dict, "C_API_SET_BUNCHCORE", sbc_c_api);

    return module;
}


namespace C_API {
PyObject *create_empty_bunchcore() {
    return alloc(&PyBunchcoreType, 0);
}

Bunchcore* get_bunchcore(PyObject* py_bunchcore) {
    PyBunchcore* bc = reinterpret_cast<PyBunchcore*>(py_bunchcore);
    if (!bc || !bc->bunchcore_) {
        PyErr_SetString(PyExc_TypeError,
                        "Failed to get bunchcore");
        return NULL;
    }
    return bc->bunchcore_;
}

int set_bunchcore(PyObject* py_bunchcore, Bunchcore* bunchcore) {
    PyBunchcore* bc = reinterpret_cast<PyBunchcore*>(py_bunchcore);
    if (!bc)
        return 0;
    bc->bunchcore_ = bunchcore;
    return 1;
}
} // C_API

}
}
}

