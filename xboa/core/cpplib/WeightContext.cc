#include <sstream>
#include "cpplib/WeightContext.hh"

namespace xboa {
namespace core {

WeightContext::WeightContext() {
    name_ = defaultName();
}

WeightContext::~WeightContext() {
    contexts_.erase(name_);
}

WeightContext::WeightContext(const WeightContext& rhs) :
                            globalWeightsContext_(rhs.globalWeightsContext_),
                            name_(rhs.name_),
                            defaultWeight_(rhs.defaultWeight_) {
}

std::map<std::string, WeightContext*> WeightContext::contexts_ = std::map<std::string, WeightContext*>();

size_t WeightContext::uniqueId_ = 1;
std::string WeightContext::defaultName() {
    std::stringstream ss;
    ss << "__default" << uniqueId_ << "__";
    uniqueId_++;
    return ss.str();
}


}
}

