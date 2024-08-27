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

#ifndef xboa_core_cpplib_Hitcore_hh
#define xboa_core_cpplib_Hitcore_hh

#include <iostream>
#include <string>
#include <map>
#include <vector>
#include <stdexcept>

#include "cpplib/WeightContext.hh"

namespace xboa {
namespace core {

/** Hitcore class provides the core "hit" object - i.e. object corresponding to
 *  a particle crossing an output plane or detector. Mostly just a container for
 *  kinematic data.
 *
 *  Following are doubles:
 *  -  x: Horizontal position
 *  -  y: Vertical position
 *  -  z: Longitudinal position
 *  -  t: time
 *
 *  -  px: Momentum in x direction
 *  -  py: Momentum in y direction
 *  -  pz: Momentum in z direction
 *  -  energy: Energy
 *
 *  -  bx: Magnetic field in x direction
 *  -  by: Magnetic field in y direction
 *  -  bz: Magnetic field in z direction 
 *
 *  -  ex: Electric field in x direction
 *  -  ey: Electric field in y direction
 *  -  ez: Electric field in z direction 
 *
 *  -  sx: Spin in x direction
 *  -  sy: Spin in y direction
 *  -  sz: Spin in z direction
 *
 *  -  path_length: total distance traversed by the particle
 *  -  proper_time: time elapsed in particle reference frame
 *  -  energy_deposited: energy deposited by the particle in material
 *  -  charge: particle charge
 *  -  mass: particle mass
 *  -  local_weight: Local weight 
 *  -  global_weight: Global weight; note that this is shared across hits. See
 *     below.
 *
 *  Following are integers:
 *  -  spill: The spill within which the particle was read out
 *  -  event: The event within which the particle was discovered
 *  -  particle: The particle within the event
 *  -  station: The readout station at which the particle was discovered
 *  -  pid: Particle PDG Particle ID
 *  -  status: Particle status
 *
 *  Note that many parameters are code dependent - e.g. some codes use z for
 *  vertical axis; some codes do not provide spin or energy deposited etc.
 *
 *  Additionally following static (global) members are defined:
 *  - get_int_map: maps variable name to integer accessor function
 *  - set_int_map: maps variable name to integer mutator function
 *  - get_dbl_map: maps variable name to double accessor function
 *  - set_dbl_map: maps variable name to double mutator function
 *  - global_weight_map_: maps <spill, event, particle> to global weight
 *
 *  Accessing data by a string that corresponds to the data name is also
 *  supported. A mapping of std::string variable name to accessors (getters) and
 *  mutators (setters) is stored internally; get_double/etc will do the map
 *  lookup and return the appropriate value. This is used by the Python API.
 *
 *  Global weight is a special variable that pertains to a particular
 *  combination of spill && event && particle. It can be used for globally
 *  weighting an event across e.g. analysis in two different detectors.
 *
 *  We define a Global weight "context" as the mapping that maps the <spill,
 *  event, particle> to a global weight; it is possible to change the global
 *  weight context at runtime, for example to run an analysis with several
 *  different sets of global cuts concurrently. This is only available from C
 *  API right now, and implementation is not very thorough.
 *
 *  Note that when calling from Python, strange things can happen; each .so file
 *  will define different names for static and global variables and the same
 *  variable can be initialised once for each .so file at a different memory
 *  address. So in Python, we have to be careful that if we want to use shared
 *  globals, these shared global objects are managed carefully at runtime. This
 *  is done by PyHitcore (which exports statics via the import_PyHitcore
 *  function
 */
class Hitcore {
  public:
    typedef double (Hitcore::*get_dbl_function)();
    typedef void (Hitcore::*set_dbl_function)(double);

    /** Constructor initialises everything to zero, except local_weight which
     *  initialises to 1
     */
    Hitcore();

    /** Destructor does nothing */
    ~Hitcore() {}

    /** Get double value referenced by key;
     *  - key: string name of the variable, chosen from get_dbl_map keys
     *  - value: get_double fills value on success with the target value
     *  Return true on success, false on failure
     */
    inline bool get_double(std::string key, double* value);

    /** Set double for value referenced by key;
     *  - key: string name of the variable, chosen from get_dbl_map keys
     *  - value: set_double writes value into the Hitcore
     *  Return true on success, false on failure
     */
    inline bool set_double(std::string key, double value);

    /** Get int value referenced by key;
     *  - key: string name of the variable, chosen from get_dbl_map keys
     *  - value: get_int fills value on success with the target value
     *  Return true on success, false on failure
     */
    inline bool get_int(std::string variable, int* value);

    /** Set int for value referenced by key;
     *  - key: string name of the variable, chosen from get_int_map keys
     *  - value: set_int writes value into the Hitcore
     *  Return true on success, false on failure
     */
    inline bool set_int(std::string variable, int value);


    /** Return the member function pointer for a given key
     *  - key: string name of the variable, chosen from get_dbl_map keys
     *  Returns a  member function pointer or NULL on failure
     */
    inline static get_dbl_function get_double_function(std::string key);

    /** Get x */
    double x() {return x_;}
    /** Get y */
    double y() {return y_;}
    /** Get z */
    double z() {return z_;}
    /** Get time */
    double t() {return t_;}

    /** Get px */
    double px() {return px_;}
    /** Get py */
    double py() {return py_;}
    /** Get pz */
    double pz() {return pz_;}
    /** Get energy */
    double energy() {return energy_;}

    /** Get local statistical weight for this hit*/
    double local_weight() {return local_weight_;}

    /** Get global statistical weight for this spill/event/particle*/
    inline double global_weight();

    /** Get product of local weight and global weight */
    inline double total_weight() {return local_weight_*global_weight();}

    /** Get bx */
    double bx() {return bx_;}
    /** Get by */
    double by() {return by_;}
    /** Get bz */
    double bz() {return bz_;}

    /** Get ex */
    double ex() {return ex_;}
    /** Get ey */
    double ey() {return ey_;}
    /** Get ez */
    double ez() {return ez_;}

    /** Get sx */
    double sx() {return sx_;}
    /** Get sy */
    double sy() {return sy_;}
    /** Get sz */
    double sz() {return sz_;}

    /** Get the particle mass */
    double mass() {return mass_;}
    /** Get the path length */
    double path_length() {return path_length_;}
    /** Get the proper time */
    double proper_time() {return proper_time_;}
    /** Get the energy deposited */
    double energy_deposited() {return energy_deposited_;}
    /** Get the charge */
    double charge() {return charge_;}

    /** Get the spill number */
    int spill() {return spill_;}
    /** Get the event number */
    int event() {return event_;}
    /** Get the particle number */
    int particle() {return particle_;}
    /** Get the station */
    int station() {return station_;}
    /** Get the pid */
    int pid() {return pid_;}
    /** Get the status */
    int status() {return status_;}

    /** Set x */
    void set_x(double x) {x_ = x;}
    /** Set y */
    void set_y(double y) {y_ = y;}
    /** Set z */
    void set_z(double z) {z_ = z;}
    /** Set time */
    void set_t(double t) {t_ = t;}

    /** Set px */
    void set_px(double px) {px_ = px;}
    /** Set py */
    void set_py(double py) {py_ = py;}
    /** Set pz */
    void set_pz(double pz) {pz_ = pz;}
    /** Set energy */
    void set_energy(double energy) {energy_ = energy;}

    /** Set mass */
    void set_mass(double mass) {mass_ = mass;}
    /** Set local weight */
    void set_local_weight(double local_weight) {local_weight_ = local_weight;}
    /** Set global weight, based on this particles spill, event, particle */
    inline void set_global_weight(double global_weight);

    /** Set bx */
    void set_bx(double bx) {bx_ = bx;}
    /** Set by */
    void set_by(double by) {by_ = by;}
    /** Set bz */
    void set_bz(double bz) {bz_ = bz;}

    /** Set ex */
    void set_ex(double ex) {ex_ = ex;}
    /** Set ey */
    void set_ey(double ey) {ey_ = ey;}
    /** Set ez */
    void set_ez(double ez) {ez_ = ez;}

    /** Set sx */
    void set_sx(double sx) {sx_ = sx;}
    /** Set sy */
    void set_sy(double sy) {sy_ = sy;}
    /** Set sz */
    void set_sz(double sz) {sz_ = sz;}

    /** Set the path length */
    void set_path_length(double path_length) {path_length_ = path_length;}
    /** Set the proper time */
    void set_proper_time(double proper_time) {proper_time_ = proper_time;}
    /** Set the energy deposited */
    void set_energy_deposited(double energy_deposited)
                                    {energy_deposited_ = energy_deposited;}
    /** Set the charge */
    void set_charge(double charge) {charge_ = charge;}

    /** Set the spill number */
    void set_spill(int spill) {spill_ = spill;}
    /** Set the event */
    void set_event(int event) {event_ = event;}
    /** Set the particle */
    void set_particle(int particle) {particle_ = particle;}
    /** Set the station */
    void set_station(int station) {station_ = station;}
    /** Set the pid */
    void set_pid(int pid) {pid_ = pid;}
    /** Set the status */
    void set_status(int status) {status_ = status;}

    /** Set up the string -> accessor mappings used by get_double and get_int
     *
     *  Call once in e.g. python module import
     */
    static void initialise_string_to_accessor_maps();

    /** Get vector of variable names which can be used by "get_double" */
    static std::vector<std::string> get_double_names();

    /** Get vector of variable names which can be used by "get_int" */
    static std::vector<std::string> get_int_names();

    /** Get vector of variable names which can be used by "get_int" or
     *  "get_double"
     */
    static std::vector<std::string> get_names();

    /** Set up the string -> mutator mappings used by set_double and set_int
     *
     *  Call once in e.g. python module import
     */
    static void initialise_string_to_mutator_maps();

    /** Get vector of variable names which can be used by "set_double" */
    static std::vector<std::string> set_double_names();

    /** Get vector of variable names which can be used by "set_int" */
    static std::vector<std::string> set_int_names();

    /** Get vector of variable names which can be used by "set_int" or
     *  "set_double"
     */
    static std::vector<std::string> set_names();

    /** Clear the global weights map */
    static void clear_global_weights();

    /** Print the global weights map */
    static void print_global_weights(std::ostream& out);

    static SmartPointer<WeightContext> weightContext;

  private:
    double x_;
    double y_;
    double z_;
    double t_;

    double px_;
    double py_;
    double pz_;
    double energy_;

    double bx_;
    double by_;
    double bz_;

    double ex_;
    double ey_;
    double ez_;

    double sx_;
    double sy_;
    double sz_;

    double local_weight_;
    double path_length_;
    double proper_time_;
    double energy_deposited_;
    double charge_;
    double mass_;

    int spill_;
    int event_;
    int particle_;
    int station_;
    int pid_;
    int status_;

    Hitcore(Hitcore& hc) {}
    Hitcore& operator=(const Hitcore& hc) {return *this;}

    typedef int (Hitcore::*get_int_function)();
    static std::map<std::string, get_int_function> get_int_map;
    typedef void (Hitcore::*set_int_function)(int);
    static std::map<std::string, set_int_function> set_int_map;

    static std::map<std::string, get_dbl_function> get_dbl_map;
    static std::map<std::string, set_dbl_function> set_dbl_map;

};

bool Hitcore::get_int(std::string variable, int* value) {
    std::map<std::string, get_int_function>::iterator it =
                                                    get_int_map.find(variable);
    if (it == get_int_map.end() || value == NULL)
        return false;
    get_int_function getter = it->second;
    *value = (this->*getter)();
    return true;
}

bool Hitcore::set_int(std::string variable, int value) {
    std::map<std::string, set_int_function>::iterator it =
                                                    set_int_map.find(variable);
    if (it == set_int_map.end())
        return false;
    set_int_function setter = it->second;
    (this->*setter)(value);
    return true;
}

bool Hitcore::get_double(std::string variable, double* value) {
    std::map<std::string, get_dbl_function>::iterator it =
                                                    get_dbl_map.find(variable);
    if (it == get_dbl_map.end() || value == NULL)
        return false;
    get_dbl_function getter = it->second;
    *value = (this->*getter)();
    return true;
}

bool Hitcore::set_double(std::string variable, double value) {
    std::map<std::string, set_dbl_function>::iterator it =
                                                    set_dbl_map.find(variable);
    if (it == set_dbl_map.end())
        return false;
    set_dbl_function setter = it->second;
    (this->*setter)(value);
    return true;
}

Hitcore::get_dbl_function Hitcore::get_double_function(std::string key) {
    std::map<std::string, get_dbl_function>::iterator it =
                                                    get_dbl_map.find(key);
    if (it == get_dbl_map.end())
        return NULL;
    return it->second;
}

void Hitcore::set_global_weight(double global_weight) {
    WeightContext::HitId hitid(spill_, particle_, event_);
    weightContext->setWeight(hitid, global_weight);
}

double Hitcore::global_weight() {
    WeightContext::HitId hitid(spill_, particle_, event_);
    double wt = weightContext->getWeight(hitid);
    return wt;
}

} // namespace core
} // namespace xboa

#endif // xboa_core_cpplib_Hitcore_hh


