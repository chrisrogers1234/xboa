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
#include "utils/SmartPointer.hh"

#ifndef xboa_core_cpplib_WeightContext_hh
#define xboa_core_cpplib_WeightContext_hh


namespace xboa {
namespace core {

/** A weight context is a mapping from a WeightContext::HitId to a statistical weight
 *  The idea is to apply statistical weights to an entire track or set of hits. All
 *  Hits that have the same Spill, Event Number and Particle Number are considered
 *  to originate on the same track. Weight context supports applying a different
 *  weighting for in different circumstances by applying a new "context".
 *
 *  Weight contexts can be combined arithmetically , for example multiplied together
 *  or added.
 *
 */
class WeightContext {
  public:

    class HitId;
    class Add;
    class Subtract;
    class Multiply;
    class Divide;
    class Not;

    /** Add the weight context to the contexts mapping */
    inline WeightContext();
    inline ~WeightContext();

    inline WeightContext* clone();

    inline WeightContext(const WeightContext& rhs);

    /** Set weights to weights from rhs. Does not change the name, as that would break the name unique-ness rule.
     */
    inline WeightContext& operator=(const WeightContext& rhs);

    /** Get the weight for a hit id.
     */
    inline double getWeight(const HitId& id) const;
    /** Get the weight for a hit id.
     */
    inline void setWeight(const HitId& id, const double& weight);
    /** Clear all weights.
     */
    inline void clearWeights();

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

    /** If weight is 0.0, acquire the default weight, else set weight to 0.0. Set DefaultWeight to 0.0. */
    inline void op_not();

    /** Get default weight */
    inline double getDefaultWeight() const;
    /** Set default weight */
    inline void setDefaultWeight(const double& weight);

  private:
    std::map<HitId, double> globalWeightsContext_;
    double defaultWeight_ = 1.0;
    //static SmartPointer<WeightContext> currentContext;
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

class WeightContext::Add  {
  public:
    Add() {}
    inline WeightContext operate(const WeightContext& lhs, const WeightContext& rhs);
    inline WeightContext operate(const WeightContext& lhs, const double& rhs);
    inline WeightContext operate(const double& lhs, const WeightContext& rhs);
};

class WeightContext::Subtract  {
  public:
    Subtract() {}
    inline WeightContext operate(const WeightContext& lhs, const WeightContext& rhs);
    inline WeightContext operate(const WeightContext& lhs, const double& rhs);
    inline WeightContext operate(const double& lhs, const WeightContext& rhs);
};

class WeightContext::Multiply  {
  public:
    Multiply() {}
    inline WeightContext operate(const WeightContext& lhs, const WeightContext& rhs);
    inline WeightContext operate(const WeightContext& lhs, const double& rhs);
    inline WeightContext operate(const double& lhs, const WeightContext& rhs);
};

class WeightContext::Divide  {
  public:
    Divide() {}
    inline WeightContext operate(const WeightContext& lhs, const WeightContext& rhs);
    inline WeightContext operate(const WeightContext& lhs, const double& rhs);
    inline WeightContext operate(const double& lhs, const WeightContext& rhs);
};

class WeightContext::Not  {
  public:
    Not() {}
    inline WeightContext operate(const WeightContext& lhs);
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