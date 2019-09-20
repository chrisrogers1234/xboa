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

#ifndef xboa_core_Comparator_hh
#define xboa_core_Comparator_hh

#include <string>

namespace xboa {
namespace core {

/** Comparator is a class wrapper for a comparison of two doubles
 */
class Comparator {
  public:
    /** Default constructor - does nothing */
    Comparator() {}
    /** Default destructor - does nothing */
    virtual ~Comparator() {}

    /** Compare two doubles and return true of false */
    virtual bool compare(double variable, double cut_value) const = 0;
};


}
}

#endif
