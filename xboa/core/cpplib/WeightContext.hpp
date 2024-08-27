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

WeightContext::WeightContext() {
    //std::cerr << "Weight Context Ctor this " << this << " currentContext " << currentContext.get() << " " << &currentContext << std::endl;
}

WeightContext::~WeightContext() {
    //std::cerr << "Weight Context Dtor this " << this << " currentContext " << currentContext.get() << " " << &currentContext << std::endl;
}

WeightContext::WeightContext(const WeightContext& rhs) :
                            globalWeightsContext_(rhs.globalWeightsContext_),
                            defaultWeight_(rhs.defaultWeight_) {
}

WeightContext* WeightContext::clone() {
    WeightContext* rhs = new WeightContext(*this);
    return rhs;
}

WeightContext& WeightContext::operator=(const WeightContext& rhs) {
    if (this == &rhs) {
        return *this;
    }
    globalWeightsContext_ = rhs.globalWeightsContext_;
    defaultWeight_ = rhs.defaultWeight_;
    return *this;
}

double WeightContext::getWeight(const HitId& id) const {
    std::map<HitId, double>::const_iterator it = globalWeightsContext_.find(id);
    if (it == globalWeightsContext_.end()) {
        return defaultWeight_;
    }
    return it->second;
}

void WeightContext::setWeight(const HitId& id, const double& weight) {
    globalWeightsContext_[id] = weight;
}

void WeightContext::clearWeights() {
    globalWeightsContext_.clear();

}

void WeightContext::adoptHits(const WeightContext& rhs) {
    std::map<HitId, double>::iterator hint = globalWeightsContext_.begin();
    for (std::map<HitId, double>::const_iterator it = rhs.globalWeightsContext_.begin(); it != rhs.globalWeightsContext_.end(); ++it) {
        // should only insert if not found in the map (according to c++.com)
        globalWeightsContext_.insert(hint, std::pair<HitId, double>(it->first, defaultWeight_));
    }
}

void WeightContext::add(const WeightContext& rhs) {
    adoptHits(rhs); // SHOULD now have all of rhs hits in this->globalWeightsContext_
    for (std::map<HitId, double>::const_iterator it = globalWeightsContext_.begin(); it != globalWeightsContext_.end(); ++it) {
        const HitId& id = it->first;
        globalWeightsContext_[id] += rhs.getWeight(id);
    }
    defaultWeight_ += rhs.defaultWeight_;
}

void WeightContext::subtract(const WeightContext& rhs) {
    adoptHits(rhs); // SHOULD now have all of rhs hits in this->globalWeightsContext_
    for (std::map<HitId, double>::const_iterator it = globalWeightsContext_.begin(); it != globalWeightsContext_.end(); ++it) {
        const HitId& id = it->first;
        globalWeightsContext_[id] -= rhs.getWeight(id);
    }
    defaultWeight_ -= rhs.defaultWeight_;
}

void WeightContext::multiply(const WeightContext& rhs) {
    adoptHits(rhs); // SHOULD now have all of rhs hits in this->globalWeightsContext_
    for (std::map<HitId, double>::const_iterator it = globalWeightsContext_.begin(); it != globalWeightsContext_.end(); ++it) {
        const HitId& id = it->first;
        globalWeightsContext_[id] *= rhs.getWeight(id);
    }
    defaultWeight_ *= rhs.defaultWeight_;
}

void WeightContext::divide(const WeightContext& rhs) {
    adoptHits(rhs); // SHOULD now have all of rhs hits in this->globalWeightsContext_
    for (std::map<HitId, double>::const_iterator it = globalWeightsContext_.begin(); it != globalWeightsContext_.end(); ++it) {
        const HitId& id = it->first;
        globalWeightsContext_[id] /= rhs.getWeight(id);
    }
    defaultWeight_ /= rhs.defaultWeight_;
}

void WeightContext::add(const double& rhs) {
    for (std::map<HitId, double>::const_iterator it = globalWeightsContext_.begin(); it != globalWeightsContext_.end(); ++it) {
        const HitId& id = it->first;
        globalWeightsContext_[id] += rhs;
    }
    defaultWeight_ += rhs;
}

void WeightContext::subtract(const double& rhs) {
    for (std::map<HitId, double>::const_iterator it = globalWeightsContext_.begin(); it != globalWeightsContext_.end(); ++it) {
        const HitId& id = it->first;
        globalWeightsContext_[id] -= rhs;
    }
    defaultWeight_ -= rhs;
}

void WeightContext::multiply(const double& rhs) {
    for (std::map<HitId, double>::const_iterator it = globalWeightsContext_.begin(); it != globalWeightsContext_.end(); ++it) {
        const HitId& id = it->first;
        globalWeightsContext_[id] *= rhs;
    }
    defaultWeight_ *= rhs;
}

void WeightContext::divide(const double& rhs) {
    for (std::map<HitId, double>::const_iterator it = globalWeightsContext_.begin(); it != globalWeightsContext_.end(); ++it) {
        const HitId& id = it->first;
        globalWeightsContext_[id] /= rhs;
    }
    defaultWeight_ /= rhs;
}

double WeightContext::getDefaultWeight() const {
    return defaultWeight_;
}

void WeightContext::setDefaultWeight(const double& weight) {
    defaultWeight_ = weight;
}

WeightContext WeightContext::Add::operate(const WeightContext& lhs, const WeightContext& rhs) {
    WeightContext wc1 = lhs;
    wc1.add(rhs);
    return wc1;
}

WeightContext WeightContext::Add::operate(const WeightContext& lhs, const double& rhs) {
    WeightContext wc1 = lhs;
    wc1.add(rhs);
    return wc1;
}

WeightContext WeightContext::Add::operate(const double& lhs, const WeightContext& rhs) {
    WeightContext wc1 = rhs;
    wc1.add(lhs);
    return wc1;
}


WeightContext WeightContext::Multiply::operate(const WeightContext& lhs, const WeightContext& rhs) {
    WeightContext wc1 = lhs;
    wc1.multiply(rhs);
    return wc1;
}

WeightContext WeightContext::Multiply::operate(const WeightContext& lhs, const double& rhs) {
    WeightContext wc1 = lhs;
    wc1.multiply(rhs);
    return wc1;
}

WeightContext WeightContext::Multiply::operate(const double& lhs, const WeightContext& rhs) {
    WeightContext wc1 = rhs;
    wc1.multiply(lhs);
    return wc1;
}


WeightContext WeightContext::Subtract::operate(const WeightContext& lhs, const WeightContext& rhs) {
    WeightContext wc1 = lhs;
    wc1.subtract(rhs);
    return wc1;
}

WeightContext WeightContext::Subtract::operate(const WeightContext& lhs, const double& rhs) {
    WeightContext wc1 = lhs;
    wc1.subtract(rhs);
    return wc1;
}

WeightContext WeightContext::Subtract::operate(const double& lhs, const WeightContext& rhs) {
    throw(std::string("not implemented"));
}


WeightContext WeightContext::Divide::operate(const WeightContext& lhs, const WeightContext& rhs) {
    WeightContext wc1 = lhs;
    wc1.divide(rhs);
    return wc1;
}

WeightContext WeightContext::Divide::operate(const WeightContext& lhs, const double& rhs) {
    WeightContext wc1 = lhs;
    wc1.divide(rhs);
    return wc1;
}

WeightContext WeightContext::Divide::operate(const double& lhs, const WeightContext& rhs) {
    throw(std::string("not implemented"));
}



}
}
