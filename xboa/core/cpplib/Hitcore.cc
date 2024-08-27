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

#include <ostream>
#include "cpplib/Hitcore.hh"

namespace xboa {
namespace core {

std::map<std::string, Hitcore::get_int_function> Hitcore::get_int_map;
std::map<std::string, Hitcore::get_dbl_function> Hitcore::get_dbl_map;
std::map<std::string, Hitcore::set_int_function> Hitcore::set_int_map;
std::map<std::string, Hitcore::set_dbl_function> Hitcore::set_dbl_map;
SmartPointer<WeightContext> Hitcore::weightContext;


void Hitcore::clear_global_weights() {
    weightContext->clearWeights();
}

Hitcore::Hitcore()
       : x_(0), y_(0), z_(0), t_(0), px_(0), py_(0), pz_(0),
         energy_(0), bx_(0), by_(0), bz_(0), ex_(0), ey_(0), ez_(0),
         sx_(0), sy_(0), sz_(0), local_weight_(1), path_length_(0),
         proper_time_(0), energy_deposited_(0), charge_(0),
         mass_(0), spill_(0), event_(0), particle_(0), station_(0),
         pid_(0), status_(0) {
}

void Hitcore::initialise_string_to_accessor_maps() {
    get_int_map["spill"] = &Hitcore::spill;
    get_int_map["event_number"] = &Hitcore::event;
    get_int_map["eventNumber"] = &Hitcore::event;
    get_int_map["particle_number"] = &Hitcore::particle;
    get_int_map["particleNumber"] = &Hitcore::particle;
    get_int_map["station"] = &Hitcore::station;
    get_int_map["status"] = &Hitcore::status;
    get_int_map["pid"] = &Hitcore::pid;

    get_dbl_map["x"] = &Hitcore::x;
    get_dbl_map["y"] = &Hitcore::y;
    get_dbl_map["z"] = &Hitcore::z;
    get_dbl_map["t"] = &Hitcore::t;

    get_dbl_map["px"] = &Hitcore::px;
    get_dbl_map["py"] = &Hitcore::py;
    get_dbl_map["pz"] = &Hitcore::pz;
    get_dbl_map["energy"] = &Hitcore::energy;

    get_dbl_map["bx"] = &Hitcore::bx;
    get_dbl_map["by"] = &Hitcore::by;
    get_dbl_map["bz"] = &Hitcore::bz;

    get_dbl_map["ex"] = &Hitcore::ex;
    get_dbl_map["ey"] = &Hitcore::ey;
    get_dbl_map["ez"] = &Hitcore::ez;

    get_dbl_map["sx"] = &Hitcore::sx;
    get_dbl_map["sy"] = &Hitcore::sy;
    get_dbl_map["sz"] = &Hitcore::sz;

    get_dbl_map["path_length"] = &Hitcore::path_length;
    get_dbl_map["proper_time"] = &Hitcore::proper_time;
    get_dbl_map["e_dep"] = &Hitcore::energy_deposited;
    get_dbl_map["charge"] = &Hitcore::charge;
    get_dbl_map["mass"] = &Hitcore::mass;

    get_dbl_map["local_weight"] = &Hitcore::local_weight;
    get_dbl_map["global_weight"] = &Hitcore::global_weight;
    get_dbl_map["weight"] = &Hitcore::total_weight;
} 
 
void Hitcore::initialise_string_to_mutator_maps() {
    set_int_map["spill"] = &Hitcore::set_spill;
    set_int_map["event_number"] = &Hitcore::set_event;
    set_int_map["eventNumber"] = &Hitcore::set_event;
    set_int_map["particle_number"] = &Hitcore::set_particle;
    set_int_map["particleNumber"] = &Hitcore::set_particle;
    set_int_map["station"] = &Hitcore::set_station;
    set_int_map["status"] = &Hitcore::set_status;
    set_int_map["pid"] = &Hitcore::set_pid;

    set_dbl_map["x"] = &Hitcore::set_x;
    set_dbl_map["y"] = &Hitcore::set_y;
    set_dbl_map["z"] = &Hitcore::set_z;
    set_dbl_map["t"] = &Hitcore::set_t;

    set_dbl_map["px"] = &Hitcore::set_px;
    set_dbl_map["py"] = &Hitcore::set_py;
    set_dbl_map["pz"] = &Hitcore::set_pz;
    set_dbl_map["energy"] = &Hitcore::set_energy;

    set_dbl_map["bx"] = &Hitcore::set_bx;
    set_dbl_map["by"] = &Hitcore::set_by;
    set_dbl_map["bz"] = &Hitcore::set_bz;

    set_dbl_map["ex"] = &Hitcore::set_ex;
    set_dbl_map["ey"] = &Hitcore::set_ey;
    set_dbl_map["ez"] = &Hitcore::set_ez;

    set_dbl_map["sx"] = &Hitcore::set_sx;
    set_dbl_map["sy"] = &Hitcore::set_sy;
    set_dbl_map["sz"] = &Hitcore::set_sz;

    set_dbl_map["path_length"] = &Hitcore::set_path_length;
    set_dbl_map["proper_time"] = &Hitcore::set_proper_time;
    set_dbl_map["e_dep"] = &Hitcore::set_energy_deposited;
    set_dbl_map["charge"] = &Hitcore::set_charge;
    set_dbl_map["mass"] = &Hitcore::set_mass;

    set_dbl_map["local_weight"] = &Hitcore::set_local_weight;
    set_dbl_map["global_weight"] = &Hitcore::set_global_weight;
}

std::vector<std::string> Hitcore::get_int_names() {
    std::string names_a[] = {
        "spill", "event_number", "particle_number",
        "station", "status", "pid", ""
    };
    std::vector<std::string> names(6);
    for (size_t i = 0; i < 6; i++)
        names[i] = names_a[i];
    return names;
}

std::vector<std::string> Hitcore::get_double_names() {
    std::string names_a[] = {
          "x", "y", "z", "t", "px", "py", "pz", "energy",
          "bx", "by", "bz", "ex", "ey", "ez",
          "sx", "sy", "sz",
          "path_length", "proper_time", "e_dep", "charge", "mass",
          "local_weight", "global_weight", ""};
    std::vector<std::string> names(24);
    for (size_t i = 0; i < 24; i++)
        names[i] = names_a[i];
    return names;
}

std::vector<std::string> Hitcore::get_names() {
    std::vector<std::string> int_names = get_int_names();
    std::vector<std::string> dbl_names = get_double_names();
    dbl_names.insert(dbl_names.end(), int_names.begin(), int_names.end());
    return dbl_names;
}

std::vector<std::string> Hitcore::set_int_names() {
    typedef std::map<std::string, set_int_function>::iterator set_it;
    std::vector<std::string> names;
    for (set_it it = set_int_map.begin(); it != set_int_map.end(); ++it) {
        names.push_back(it->first);
    }
    return names;
}

std::vector<std::string> Hitcore::set_double_names() {
    typedef std::map<std::string, set_dbl_function>::iterator set_it;
    std::vector<std::string> names;
    for (set_it it = set_dbl_map.begin(); it != set_dbl_map.end(); ++it) {
        names.push_back(it->first);
    }
    return names;
}

std::vector<std::string> Hitcore::set_names() {
    std::vector<std::string> int_names = set_int_names();
    std::vector<std::string> dbl_names = set_double_names();
    dbl_names.insert(dbl_names.end(), int_names.begin(), int_names.end());
    return dbl_names;
}


} // namespace core
} // namespace xboa

