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

#ifndef xboa_core_cpplib_Bunchcore_hh
#define xboa_core_cpplib_Bunchcore_hh

#include <map>
#include <vector>
#include <string>
#include <memory>
#include "cpplib/Hitcore.hh"
#include "utils/SmartPointer.hh"
#include "utils/Comparator.hh"

namespace xboa {
namespace core {

/**
 *  Bunchcore provides functions for calculations on a bunch of particles
 *
 *  Set of core functions for Bunch python module
 *  I want to improve speed - the thing I really worry about is the time taken 
 *  to calc moments. My optimisation is to use Hitcore.get_x() etc directly
 *  rather than requiring the python type lookups etc
 *
 *  Bunchcore is a list of SmartPointer to Hitcore objects. Note that it is poor
 *  form to use a SmartPointer (C++ smart pointer). Here I have to do it because
 *  Python can own the pointer when working from Python API; in which case
 *  PyHitcore can own the memory; but C++ can own the pointer when working from
 *  C++ API; in which case Bunchcore has to own the memory
 */
class Bunchcore {
public:
    /** Constructor - does nothing */
    Bunchcore() {}

    /** Destructor - does nothing
     *
     *  Nb: SmartPointer is responsible for cleaning up member data
     */
    ~Bunchcore() {}

    /** Set the ith element
     *  - i index of the element to return. If element i does not exist, extend
     *    the vector to include element i.
     */
    void set_item(size_t i, ::xboa::core::SmartPointer<Hitcore> hit);

    /** Get the ith element
     *  - i index of the element to return. If element i does not exist, returns
     *      NULL
     */
    SmartPointer<Hitcore> get_item(size_t i) {return hitcores_.at(i);}

    /** Return the length of hitcores_ */
    size_t length() {return hitcores_.size();}

    /** Calculate a moment of the hits in Bunchcore
     *  - axes: vector of axis names that index the moment axes
     *  - means: map that holds means; if mean for an axis is not stored,
     *    Bunchcore will calculate it.
     *  - moment: fills value with sum(x_i-mean_i)**2/n
     *  Returns true on success, false on failure
     */
    bool get_moment(std::vector<std::string> axes,
                    std::map<std::string, double> means,
                    double* moment);

    /** Calculate a covariance matrix (combination of second moments)
     *  - axes: vector of axis names that index the moment axes
     *  - means: map that holds means; if mean for an axis is not stored,
     *    Bunchcore will calculate it.
     *  - covariances: fills value with second moments of axes variables
     *  Returns true on success, false no failure
     */
    bool covariance_matrix(std::vector<std::string> axes,
                           std::map<std::string, double> means,
                           std::vector< std::vector<double> >* covariances
    );

    /** Inner loop of the cut function, called when cutting on a double value
     *  - cut_variable: string that indexes the variable to be cut on
     *  - comparator: Python function that does the comparison
     *  - cut: value of the cut
     *  - is_global: set to true to apply the cut to global weights; or false to
     *    apply the cut to local weights
     *  Return true on success, false on failure
     */
    bool cut_double(const std::string cut_variable,
                    const Comparator* comp,
                    const double cut_value,
                    const bool is_global);

    /** Optimisation when getting many moments. Get all natural moments up to
     *  some maximum order "max_order".
     *  - axes: set of variables for which moments will be calculated; should be
     *    strings from Hitcore.get_names()
     *  - max_order: moments in the moment tensor will have maximum sum of the
     *    powers of each element given by max_order
     *  - moments: vector will be overwritten with moments. Should point to an
     *    initialised vector (caller owns the memory).
     *  - index_by_power: vector will be overwritten with a vector holding the
     *    moment indices, e.g. if index_by_power[6] = [2, 0, 1, 2] it means that
     *    moments[6] holds the moment <x_0^2*x_2^1*x_3^2>.
     *  Returns true if the calculation was successful; false if the calculation
     *  failed.
     */
    bool get_moment_tensor(
                    std::vector<std::string> axes,
                    size_t max_order,
                    std::vector<double>* moments,
                    std::vector<std::vector<size_t> >* index_by_power);

    /** Get the list of variables used for calculating moment tensors.
     *  - max_order: maximum sum of powers in an index
     *  - n_axes: number of axes (length of each index)
     *  Return value is an index as described in e.g. get_moment_tensor, i.e.
     *  index_by_power = [2, 0, 1, 2] refers to x_0^2*x_2^1*x_3^2 for some
     *  vector x
     */
    static std::vector<std::vector<size_t> > get_index_by_power(
                                                      size_t max_order,
                                                      size_t n_axes);

    /** Get the sum of total_weight of hitcores in the bunch */
    double bunch_weight();

private:
    std::vector< SmartPointer<Hitcore> > hitcores_;

    static std::vector<std::vector<size_t> > get_index_by_power_recurse(
                                    size_t max_size,
                                    size_t axis,
                                    std::vector<size_t> current_index);

    std::vector< std::vector<int> > get_index_by_power_one_scale(int size);
};
} // core
} // xboa
#endif  // xboa_core_cpplib_Bunchcore_hh

