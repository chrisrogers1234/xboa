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

#ifndef xboa_core_utils_TypeConversions_hh
#define xboa_core_utils_TypeConversions_hh

#include <map>
#include <vector>
#include <string>

namespace xboa {
namespace core {

/** Abstraction for a converter from C++ to Python
 *
 *  Converts from CPP_TYPE to a PyObject.
 */
template <class CPP_TYPE>
class CppPyConverter {
  public:
    /** Constructor does nothing */
    CppPyConverter() {}
    /** Destructor does nothing */
    virtual ~CppPyConverter() {}
    /** Convert cpp_type to a PyObject, filling memory pointed by py_type. 
     *  - cpp_type: the cpp data to be read
     *  - py_type: allocates a new PyObject at this memory address. Should point
     *  to an allocated PyObject*.
     *  Returns true on success. py_type remains unfilled on failure and returns
     *  false.
     */
    virtual bool convert(const CPP_TYPE* cpp_type, PyObject** py_type) const = 0;
};

/** Abstraction for a converter from Python to C++
 *
 *  Converts from CPP_TYPE to a PyObject.
 */
template <class CPP_TYPE>
class PyCppConverter {
  public:
    /** Constructor does nothing */
    PyCppConverter() {}
    /** Destructor does nothing */
    virtual ~PyCppConverter() {}
    /** Convert py_type to a PyObject, filling memory pointed by cpp_type
     *  - py_type: the Python data to be read
     *  - cpp_type: puts a C++ object at this memory address. Should point to
     *  an allocated cpp_type (typically uses assignment operator to fill 
     *  cpp_type).
     *  Returns true on success.
     */
    virtual bool convert(PyObject* py_type, CPP_TYPE* cpp_type) const = 0;
};

/** Converts Py_ssize_t to C size_t, doing Python negative indices
 *
 *   - py_index Python signed index of an iterable with length elements
 *   - length number of elements in the iterable
 *   - size_t C unsigned index of an iterable. Caller allocates and owns memory
 *     belonging to index.
 *
 *  Convert a Py_ssize_t to a C size_t; if Py_ssize_t is negative, use the
 *  length parameter to make it positive. If the py_index is out of range for a
 *  vector of given length (too positive or too negative), raise an IndexError. 
 *  Returns true on success.
 */
class PyCppIndexConverter : public PyCppConverter<size_t> {
  public:
    PyCppIndexConverter() : has_length_(false), length_(0) {}
    PyCppIndexConverter(size_t sequence_length) : has_length_(true), length_(sequence_length) {}
    virtual ~PyCppIndexConverter() {}

    bool convert(PyObject* py_int, size_t* index) const;

  private:
    bool has_length_;
    size_t length_;
};

/** Converts PyString to C string */
class PyCppStringConverter : public PyCppConverter<std::string> {
  public:
    /** Constructor does nothing */
    PyCppStringConverter() {}
    /** Destructor does nothing */
    virtual ~PyCppStringConverter() {}
    /** Convert py_string to a C++ std::string */
    bool convert(PyObject* py_string, std::string* cpp_string) const;
};

class PyCppDoubleConverter : public PyCppConverter<double> {
  public:
    PyCppDoubleConverter() {}
    virtual ~PyCppDoubleConverter() {}

    bool convert(PyObject* py_double, double* cpp_double) const;
};


/** Converts a Python List to a vector of ELEMENT objects
 *
 *  ELEMENT must have a default constructor
 */
template <class ELEMENT>
class PyCppListToVectorConverter : public PyCppConverter<std::vector<ELEMENT> > {
  public:
    /** Construct the converter
     *
     *  - converter: converts an element of PyList to type ELEMENT
     *  Caller owns memory allocated to converter, it is a borrowed reference
     */
    PyCppListToVectorConverter(const PyCppConverter<ELEMENT>* converter)
    : converter_(converter){}
    /** Destructor does nothing */
    virtual ~PyCppListToVectorConverter() {}
    /** Convert the list from python to std::vector */
    bool convert(PyObject* py_list, std::vector<ELEMENT>* std_vector) const;

  private:
    const PyCppConverter<ELEMENT>* converter_;
};

/** Converts a generic pointer to object type PTR to a PyLong
 */
template <class PTR>
class CppPyPointerToLongConverter : public CppPyConverter<PTR*> {
  public:
    /** Constructor does nothing */
    CppPyPointerToLongConverter() {}
    /** Destructor does nothing */
    virtual ~CppPyPointerToLongConverter() {}
    /** Convert pointer to a PyLong */
    bool convert(PTR* const* pointer, PyObject** py_long) const;
};

/** Converts a generic integer type to a PyLong */
template <class INT_TYPE>
class CppPyIntConverter : public CppPyConverter<INT_TYPE> {
  public:
    /** Constructor does nothing */
    CppPyIntConverter() {}
    /** Destructor does nothing */
    virtual ~CppPyIntConverter() {}
    /** Convert integer to a PyLong; cast to a long long first and then back to
     *  a PyLong. Assumes that this will retain sufficient information.
     */
    bool convert(const INT_TYPE* pointer, PyObject** py_long) const;
};

/** Converts a PyDict to a std::map */
template <class KEY, class VALUE>
class PyCppDictToMapConverter : public PyCppConverter<std::map<KEY, VALUE> > {
  public:
    /** Construct the converter
     *
     *  - key_converter: converts a key of PyDict to type KEY
     *  - value_converter: converts a value of PyDict to type VALUE
     *  Caller owns memory allocated to key_converter and value_converter; they
     *  are borrowed references
     */
    PyCppDictToMapConverter(const PyCppConverter<KEY>* key_converter,
                            const PyCppConverter<VALUE>* value_converter)
       : key_c_(key_converter), value_c_(value_converter) {}
    /** Destructor does nothing */
    virtual ~PyCppDictToMapConverter() {}
    /** Convert from PyDict to std::map */
    bool convert(PyObject* py_dict, std::map<KEY, VALUE>* std_map) const;

  private:
    const PyCppConverter<KEY>* key_c_;
    const PyCppConverter<VALUE>* value_c_;
};

/** Converts a std::map to a PyDict */
template <class KEY, class VALUE>
class CppPyMapToDictConverter : public CppPyConverter<std::map<KEY, VALUE> > {
  public:
    /** Construct the converter
     *
     *  - key_converter: converts a type KEY to a key of PyDict
     *  - value_converter: converts a type VALUE to a value of PyDict 
     *  Caller owns memory allocated to key_converter and value_converter; they
     *  are borrowed references
     */
    CppPyMapToDictConverter(const CppPyConverter<KEY>* key_converter,
                            const CppPyConverter<VALUE>* value_converter)
       : key_c_(key_converter), value_c_(value_converter) {}
    /** Destructor does nothing */
    virtual ~CppPyMapToDictConverter() {}
    /** Convert from std::map to PyDict */
    bool convert(const std::map<KEY, VALUE>* std_map, PyObject** py_dict) const;

  private:
    const CppPyConverter<KEY>* key_c_;
    const CppPyConverter<VALUE>* value_c_;
};


/** Converts a double to a PyFloat */
class CppPyDoubleConverter : public CppPyConverter<double> {
  public:
    /** Constructor does nothing */
    CppPyDoubleConverter() {}
    /** Destructor does nothing */
    virtual ~CppPyDoubleConverter() {}
    /** Convert from a double to a PyFloat */
    bool convert(const double* cpp_double, PyObject** py_double) const;
};

/** Converts a std::vector to a PyList
 *
 *  ELEMENT must have a default constructor
 */
template <class ELEMENT>
class CppPyVectorToListConverter : public CppPyConverter<std::vector<ELEMENT> > {
  public:
    /** Construct the converter
     *
     *  - converter: converts a type ELEMENT to an element of PyList
     *  Caller owns memory allocated to converter; it is a borrowed reference
     */
    CppPyVectorToListConverter(const CppPyConverter<ELEMENT>* converter) : converter_(converter){}
    /** Destructor does nothing */
    virtual ~CppPyVectorToListConverter() {}
    /** Convert from a vector of ELEMENTS to a PyList */
    bool convert(const std::vector<ELEMENT>* std_vector, PyObject** py_list) const ;

  private:
    const CppPyConverter<ELEMENT>* converter_;
};

}
}

#include "TypeConversions-inl.hh"

#endif // xboa_core_utils_TypeConversions_hh

