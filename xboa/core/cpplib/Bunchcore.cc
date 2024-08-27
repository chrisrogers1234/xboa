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

#include <math.h>

#include <iostream>
#include "cpplib/Hitcore.hh"

#include "cpplib/Bunchcore.hh"

namespace xboa {
namespace core {

void Bunchcore::set_item(size_t i, SmartPointer<Hitcore> hit) {
    if (i >= hitcores_.size()) {
        hitcores_.resize(i+1, SmartPointer<Hitcore>(NULL));
    }
    // can delete an existing hit_
    hitcores_[i] = hit;
}

bool Bunchcore::del_item(size_t i) {
    // can delete an existing hit_
    if (i > hitcores_.size()) {
        return false;
    }
    hitcores_.erase(hitcores_.begin()+i);
    return true;
}


bool Bunchcore::get_moment(std::vector<std::string> axes,
            std::map<std::string, double> means,
            double* moment) {
    // check moment is valid
    if (moment == NULL)
        return false;
    // map from string to functions
    std::vector<Hitcore::get_dbl_function> function_vector(axes.size());
    for (size_t i = 0; i < axes.size(); ++i) {
        function_vector[i] = Hitcore::get_double_function(axes[i]);
        if (function_vector[i] == NULL)
            return false;
    }
    // extract means (assume mean map is filled)
    std::vector<double> mean_vector(axes.size());
    for (size_t i = 0; i < axes.size(); ++i) {
        mean_vector[i] = means[axes[i]];
    }

    // get sum of weights
    double weight_sum = bunch_weight();

    //extract moments
    *moment = 0.;
    for(size_t i = 0; i < hitcores_.size(); ++i) {
        Hitcore* hc = hitcores_[i].get();
        if (hc == NULL)
            continue;
        double my_moment = hc->total_weight()/weight_sum;
        for(size_t j = 0; j < axes.size(); ++j) {
            my_moment *= (*hc.*function_vector[j])() - mean_vector[j];
        }
        *moment += my_moment;
    }
    return true;
}

bool Bunchcore::covariance_matrix(std::vector<std::string> axes,
                                 std::map<std::string, double> means,
                                 std::vector< std::vector<double> >* covariances
                                 ) {
    size_t n_axes = axes.size();
    // Set up covariances is valid
    if (covariances == NULL)
        return false;
    covariances->resize(n_axes, std::vector<double>(n_axes, 0));
    // map from string to functions
    std::vector<Hitcore::get_dbl_function> function_vector(n_axes);
    for (size_t i = 0; i < n_axes; ++i) {
        function_vector[i] = Hitcore::get_double_function(axes[i]);
        if (function_vector[i] == NULL)
            return false;
    }
    // extract means (assume mean map is filled)
    std::vector<double> mean_vector(n_axes);
    for (size_t i = 0; i < n_axes; ++i) {
        mean_vector[i] = means[axes[i]];
    }
    // get sum of weights
    double weight_sum = bunch_weight();

    for(size_t i = 0; i < hitcores_.size(); ++i) {
        Hitcore* hc = hitcores_[i].get();
        if (hc == NULL)
            continue;
        double this_weight = hc->total_weight()/weight_sum;
        for(size_t j = 0; j < n_axes; ++j) {
            double this_value =
                       this_weight*((*hc.*function_vector[j])()-mean_vector[j]); 
            for(size_t k = 0; k < n_axes; ++k)
                (*covariances)[j][k] +=
                        this_value*((*hc.*function_vector[k])()-mean_vector[k]);
        }
    }
    return true;
}

bool Bunchcore::get_moment_tensor(
                    std::vector<std::string> axes,
                    size_t max_size,
                    std::vector<double>* moments,
                    std::vector<std::vector<size_t> >* index_by_power) {
    if (axes.size() == 0 || max_size == 0 ||
        moments == NULL || index_by_power == NULL) {
        return false;
    }
    size_t n_axes = axes.size();
    // map from string to functions
    std::vector<Hitcore::get_dbl_function> function_vector(n_axes);
    for (size_t i = 0; i < n_axes; ++i) {
        function_vector[i] = Hitcore::get_double_function(axes[i]);
        if (function_vector[i] == NULL)
            return false;
    }
    *index_by_power = get_index_by_power(max_size, n_axes);
    *moments = std::vector<double>(index_by_power->size(), 0.);
    double weight_sum = bunch_weight();
    if ( fabs(weight_sum) < 1e-15)
        return false;
    // build up moments
    for (size_t i = 0; i < hitcores_.size(); ++i) {
        Hitcore* hc = hitcores_[i].get();
        if (hc == NULL)
            continue;
        // get list of x[j]^k
        std::vector<std::vector<double> > powers(n_axes);
        for (size_t j = 0; j < n_axes; ++j) {
            double value = (*hc.*function_vector[j])(); // hc[axes[j]]
            powers[j] = std::vector<double>(max_size, value);
            powers[j].insert(powers[j].begin(), 1.);
            for (size_t k = 1; k <= max_size; ++k) {
                powers[j][k] *= powers[j][k-1]; // x[j][k] = x[j]*x[j]^(k-1)
            }
        }
        // make a list of powers of this hitcore; then multiply the moment
        std::vector<double> this_moments(index_by_power->size(),
                                         hc->total_weight());
        for (size_t j = 0; j < index_by_power->size(); ++j) {
            for (size_t k = 0; k < n_axes; ++k) {
                size_t power = (*index_by_power)[j][k];
                this_moments[j] *=  powers[k][power];
            }
            (*moments)[j] += this_moments[j]/weight_sum;
        }
    }
    return true;
}

std::vector<std::vector<size_t> > Bunchcore::get_index_by_power(size_t max_size,
                                                                size_t n_axes) {
    std::vector<size_t> current_index(n_axes, 0);
    std::vector<std::vector<size_t> > index_by_power =
                         get_index_by_power_recurse(max_size, 0, current_index);
    index_by_power.insert(index_by_power.begin(), current_index);
    return index_by_power;
}


std::vector<std::vector<size_t> > Bunchcore::get_index_by_power_recurse(
                                    size_t max_size,
                                    size_t axis,
                                    std::vector<size_t> current_index) {
    std::vector<std::vector<size_t> > index_by_power; //1, current_index);
    size_t current_sum = current_index[0]; // 0 if axis is 0
    if (axis >= current_index.size()) {
        return index_by_power;
    }
    for (size_t i = 1; i < axis; ++i)
        current_sum += current_index[i];
    for (size_t i = 0; current_sum + i <= max_size; ++i) {
        current_index[axis] = i;
        std::vector<std::vector<size_t> > new_index_by_power =
                                      get_index_by_power_recurse(max_size,
                                                                 axis+1,
                                                                 current_index);
        index_by_power.insert(index_by_power.end(),
                              new_index_by_power.begin(),
                              new_index_by_power.end());
        if (i > 0)
            index_by_power.push_back(current_index);
    }
    return index_by_power;
}

double Bunchcore::bunch_weight() {
    // get sum of weights
    double weight_sum = 0.;
    for(size_t i = 0; i < hitcores_.size(); ++i) {
        Hitcore* hc = hitcores_[i].get();
        if (hc == NULL)
            continue;
        weight_sum += hc->total_weight();
    }
    return weight_sum;
}

bool Bunchcore::cut_double(const std::string cut_variable,
                           const Comparator* comp,
                           const double cut_value,
                           const bool is_global) {
    // evaluate cut_variable
    Hitcore::get_dbl_function function =
                                     Hitcore::get_double_function(cut_variable);
    if (function == NULL)
        return false;
    // iterate over the hitcores, cutting
    for (size_t i = 0; i < hitcores_.size(); ++i) {
        Hitcore* hc = hitcores_[i].get();
        // ignore NULLs
        if (hc == NULL)
            continue;
        const double value = (*hc.*function)();
        try {
            int comparison = comp->compare(value, cut_value);
            if (comparison == 1) {
                if (is_global) {
                    hc->set_global_weight(0.);
                } else {
                    hc->set_local_weight(0.);
                }
            }
        } catch (std::logic_error& err) {
            return false;
        }
    }
    return true;
}
}
}
