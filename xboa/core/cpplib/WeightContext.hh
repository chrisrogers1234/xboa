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

#include <map>
#include <stdexcept>

#ifndef xboa_core_cpplib_PyWeightContext_hh
#define xboa_core_cpplib_PyWeightContext_hh


namespace xboa {
namespace core {

/** A weight context is a mapping from a WeightContext::HitId to a statistical weight
 *
 *  WeightContext is a wrapper to a map from HitId to double weight; methods are
 *  provided to combine weightcontexts using arithmetic operators
 *
 *  Weight contexts are referenced via a string lookup table
 *
 */
class WeightContext {
  public:

    class HitId;

    /** Add the weight context to the contexts mapping */
    WeightContext();
    ~WeightContext();

    inline WeightContext* clone();

    WeightContext(const WeightContext& rhs);

    /** Set weights to weights from rhs. Does not change the name, as that would break the name unique-ness rule.
     */
    inline WeightContext& operator=(const WeightContext& rhs);

    /** Get the weight for a hit id.
     */
    inline double getWeight(HitId id) const;

    /** Add hitIds in rhs to *this::globalWeightsContext_ and set the new
     *  weights to the default. To be explicit, we don't set the weights from
     *  rhs, just the Ids.
     */
    inline void adoptHits(const WeightContext& rhs);

    /** For each hit in rhs, add weight in rhs to weight in this. Also add together defaultWeights. */
    inline void add(const WeightContext& rhs);
    /** For each hit in rhs, subtract weight in rhs to weight in this. Also subtract defaultWeights.*/
    inline void subtract(const WeightContext& rhs);
    /** For each hit in rhs, multiply weight in rhs to weight in this. Also multiply defaultWeights.*/
    inline void multiply(const WeightContext& rhs);
    /** For each hit in rhs, divide weight in this by weight in rhs. Also divide defaultWeights.*/
    inline void divide(const WeightContext& rhs);

    /** Add rhs to each weight in this and add defaultWeight. */
    inline void add(const double& rhs);
    /** Subtract rhs from each weight in this and subtract from defaultWeight. */
    inline void subtract(const double& rhs);
    /** Multiply each weight by rhs in this and also defaultWeight. */
    inline void multiply(const double& rhs);
    /** Divide each weight by rhs in this and also defaultWeight. */
    inline void divide(const double& rhs);

    /** Get default weight */
    inline double getDefaultWeight() const;
    /** Set default weight */
    inline void setDefaultWeight(const double& weight);

    /** Set name. Update contexts_ */
    inline void setName(std::string name);
    /** Get name. */
    inline std::string getName() const;

    static WeightContext* getContext(std::string name);
    static void setContext(std::string name, WeightContext* context);

    static WeightContext* getCurrentContext();
    static void setCurrentContext(WeightContext* context);

  private:
    std::map<HitId, double> globalWeightsContext_;
    std::string name_;
    double defaultWeight_ = 1.0;
    static std::map<std::string, WeightContext*> contexts_;
    static size_t uniqueId_;
    static std::string defaultName();
    static WeightContext* currentContext;
};

class WeightContext::HitId  {
  public:
    HitId(int spill, int event, int particle)
      : spill_(spill), event_(event), particle_(particle) {
    }

    inline bool operator<(const HitId&) const;
    int spill_;
    int event_;
    int particle_;
};

typedef WeightContext::HitId HitId;

bool WeightContext::HitId::operator<(const WeightContext::HitId& rhs) const {
    if (spill_ == rhs.spill_) {
        if (event_ == rhs.event_) {
            return particle_ < rhs.particle_;
        } else {
            return event_ < rhs.event_;
        }
    } else {
        return spill_ < rhs.spill_;
    }
}


}
}

#include "cpplib/WeightContext.hpp"

#endif