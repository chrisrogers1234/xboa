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

WeightContext* WeightContext::clone() {
    WeightContext* rhs = new WeightContext(*this);
    return rhs;
}

WeightContext& WeightContext::operator=(const WeightContext& rhs) {
    if (this == &rhs) {
        return *this;
    }
    globalWeightsContext_ = rhs.globalWeightsContext_;
    name_ = rhs.name_;
    defaultWeight_ = rhs.defaultWeight_;
    return *this;
}

double WeightContext::getWeight(HitId id) const {
    std::map<HitId, double>::const_iterator it = globalWeightsContext_.find(id);
    if (it == globalWeightsContext_.end()) {
        return defaultWeight_;
    }
    return it->second;
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

void WeightContext::setName(std::string name) {
    if (contexts_.find(name) != contexts_.end()) {
        throw std::runtime_error(
            "Cannot rename WeightContext - another WeightContext already "
            "exists with the same name and names must be unique.");
    }
    name_ = name;
    contexts_.erase(name_);
    contexts_[name] = this;
}

std::string WeightContext::getName() const {
    return name_;
}

}
}
