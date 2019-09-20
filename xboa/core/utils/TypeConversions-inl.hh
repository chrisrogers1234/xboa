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

namespace xboa {
namespace core {

bool PyCppIndexConverter::convert(PyObject* py_int, size_t* index) const {
    if (!PyInt_Check(py_int)) {
        PyErr_SetString(PyExc_TypeError, "Index was not an integer");
        return false;
    }
    Py_ssize_t py_index = PyInt_AsSsize_t(py_int);
    if (py_index < 0) {
        *index = abs(py_index+1);
    } else {
        *index = py_index;
    }
    if (has_length_ && *index >= length_) {
      PyErr_SetString(PyExc_IndexError,
                      "Index out of range");
      return false;
    }
    return true;
}

bool PyCppStringConverter::convert(PyObject* py_string,
                                   std::string* cpp_string) const {
    if (py_string && PyString_Check(py_string)) {
        // copies the string
        *cpp_string = std::string(PyString_AsString(py_string));
    } else {
        PyErr_SetString(PyExc_TypeError, "Failed to parse string");
        return false;
    }
    return true;
}

bool PyCppDoubleConverter::convert(PyObject* py_double, double* cpp_double) const {
    if (py_double && PyFloat_Check(py_double)) {
        // copies the double
        *cpp_double = PyFloat_AsDouble(py_double);
    } else {
        PyErr_SetString(PyExc_TypeError, "Failed to parse double");
        return false;
    }
    return true;
}


template <class ELEMENT>
bool PyCppListToVectorConverter<ELEMENT>::convert(
                                   PyObject* py_list,
                                   std::vector<ELEMENT>* std_vector) const {
    if (!py_list || !PyList_Check(py_list)) {
      PyErr_SetString(PyExc_TypeError,
                      "Failed to parse argument as list");
      return false;
    }

    size_t size = PyList_Size(py_list);
    *std_vector = std::vector<std::string>(size);
    for (size_t i = 0; i < size; ++i) {
        PyObject* item = PyList_GetItem(py_list, i); // borrowed reference
        if (item) {
            ELEMENT element;
            converter_->convert(item, &element);
            // copies the string
            std_vector->at(i) = element;
        } else {
            PyErr_SetString(PyExc_TypeError,
                            "Failed to parse element as a string");
            return false;
        }
    }
    return true;
}

template <class KEY, class VALUE>
bool PyCppDictToMapConverter<KEY, VALUE>::convert(
                                      PyObject* py_dict,
                                      std::map<KEY, VALUE>* std_map) const {
    if (std_map == NULL) {
        PyErr_SetString(PyExc_TypeError, "Bad input to conversion");
        return false;
    }
    if (py_dict == NULL || PyDict_Check(py_dict) == 0) {
        PyErr_SetString(PyExc_TypeError, "Not a dictionary");
        return false;
    }
    *std_map = std::map<KEY, VALUE>();

    // iterate over the dict
    PyObject *py_key, *py_value;
    Py_ssize_t pos = 0;
    while (PyDict_Next(py_dict, &pos, &py_key, &py_value)) {
        KEY key;
        VALUE value;
        if (key_c_->convert(py_key, &key) &&
            value_c_->convert(py_value, &value)) {
            (*std_map)[key] = value;
        } else { // exception should be set by child converter
            return false;
        }
    }
    return true;
}

template <class KEY, class VALUE>
bool CppPyMapToDictConverter<KEY, VALUE>::convert(
                                      const std::map<KEY, VALUE>* std_map,
                                      PyObject** py_dict) const {
    if (std_map == NULL || py_dict == NULL) {
        PyErr_SetString(PyExc_TypeError, "Bad input to conversion");
        return false;
    }
    *py_dict = PyDict_New();
    if (!py_dict) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to allocate dict");
        return false;
    }
    Py_INCREF(*py_dict);
    typename std::map<KEY, VALUE>::const_iterator it;
    for (it = std_map->begin(); it != std_map->end(); ++it) {
        PyObject *py_key, *py_value;
        if (key_c_->convert(&it->first, &py_key) &&
            value_c_->convert(&it->second, &py_value)) {
            PyDict_SetItem(*py_dict, py_key, py_value);
        } else {
            return false;
        }
    }
    return true;
}

bool CppPyDoubleConverter::convert(const double* cpp_double,
                                   PyObject** py_double) const {
    if (cpp_double == NULL || py_double == NULL) {
        PyErr_SetString(PyExc_TypeError, "Bad input to conversion");
        return false;
    }
    *py_double = PyFloat_FromDouble(*cpp_double);
    if (*py_double == NULL) {
        PyErr_SetString(PyExc_TypeError, "Failed to convert from double");
        return false;
    }
    return true;
}

template <class ELEMENT>
bool CppPyVectorToListConverter<ELEMENT>::convert(
                              const std::vector<ELEMENT>* std_vector,
                              PyObject** py_list) const {
    if (std_vector == NULL || py_list == NULL) {
        PyErr_SetString(PyExc_TypeError, "Bad input to conversion");
        return false;
    }

    *py_list = PyList_New(0);
    Py_INCREF(*py_list);
    for (size_t i = 0; i < std_vector->size(); ++i) {
        ELEMENT element = std_vector->at(i);
        PyObject* py_element;
        if (!converter_->convert(&element, &py_element)) {
            return false;
        }
        if (PyList_Append(*py_list, py_element) != 0) {
            PyErr_SetString(PyExc_RuntimeError,
                            "Failed to append element");
            return false;
        }
    }
    return true;
}

template <class PTR>
bool CppPyPointerToLongConverter<PTR>::convert(PTR* const* pointer,
                                               PyObject** py_long) const {
    if (pointer == NULL || py_long == NULL) {
        PyErr_SetString(PyExc_TypeError, "Bad input to conversion");
        return false;
    }
    PTR* ptr_pointer = *pointer;
    void* void_pointer = reinterpret_cast<void*>(ptr_pointer);
    *py_long = PyLong_FromVoidPtr(void_pointer);
    if (*py_long == NULL) {
        PyErr_SetString(PyExc_TypeError, "Conversion failed");
        return false;
    }
    return true;
}

template <class INT_TYPE>
bool CppPyIntConverter<INT_TYPE>::convert(const INT_TYPE* c_int,
                                          PyObject** py_long) const {
    if (c_int == NULL || py_long == NULL) {
        PyErr_SetString(PyExc_TypeError, "Bad input to conversion");
        return false;
    }
    long long my_long_long(*c_int);
    *py_long = PyLong_FromLongLong(my_long_long);
    if (*py_long == NULL) {
        PyErr_SetString(PyExc_TypeError, "Conversion failed");
        return false;
    }
    return true;
}

}
}

