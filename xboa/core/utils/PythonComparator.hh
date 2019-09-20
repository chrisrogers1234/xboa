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

#ifndef xboa_core_utils_PythonComparator_hh
#define xboa_core_utils_PythonComparator_hh

#include <string>
#include <stdexcept>
#include "utils/Comparator.hh"

namespace xboa {
namespace core {
namespace utils {

/** PythonComparator is a class wrapper for a comparison of two doubles using
 *  a python function to do the comparison.
 */
class PythonComparator : public Comparator {
  public:
    /** Constructor borrows py_cmp - caller owns py_cmp */
    PythonComparator(PyObject* py_cmp);
    /** Destructor does nothing */
    virtual ~PythonComparator() {}
    /** Call py_cmp to do a comparison of variable and cut_value
     *
     *  - variable: first variable for comparison, should be able to evaluate as
     *    a PyFloat using Py_BuildValue.
     *  - cut_value: second variable for comparison, should be able to evaluate as
     *    a PyFloat using Py_BuildValue.
     *
     *  Builds a tuple (variable, cut_value) to call py_cmp(variable, cut_value)
     *  Returns true if py_cmp returns Py_True; false if py_cmp returns Py_False
     *  Else throws and exception.
     */
    bool compare(double variable, double cut_value) const;

  private:
    PyObject* py_cmp_;
};

PythonComparator::PythonComparator(PyObject* py_cmp)
  :  py_cmp_(py_cmp) {
    if (PyCallable_Check(py_cmp_) == 0)
        py_cmp_ = NULL;
}

bool PythonComparator::compare(double variable, double cut_value) const {
    if (py_cmp_ == NULL)
        return false;
    PyObject *args = Py_BuildValue("dd", variable, cut_value);
    PyObject *ret_bool = PyObject_CallObject(py_cmp_, args);
    if (ret_bool == NULL || !PyBool_Check(ret_bool)) {
        throw std::logic_error("Failed to call python comparator");
    }
    // I could check ret_bool using PyBool_Check I guess, and set a failflag in
    // the class
    return ret_bool == Py_True;
}

}
}
}

#endif

