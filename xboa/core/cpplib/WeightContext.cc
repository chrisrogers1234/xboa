#include <sstream>
#include "cpplib/WeightContext.hh"

namespace xboa {
namespace core {

SmartPointer<WeightContext> WeightContext::currentContext = SmartPointer<WeightContext>();


WeightContext::~WeightContext() {
}

WeightContext::WeightContext() {
}


WeightContext::WeightContext(const WeightContext& rhs) :
                            globalWeightsContext_(rhs.globalWeightsContext_),
                            defaultWeight_(rhs.defaultWeight_) {
}


SmartPointer<WeightContext> WeightContext::getCurrentContext() {
    return currentContext;
}

void WeightContext::setCurrentContext(SmartPointer<WeightContext> context) {
    currentContext = context;
}

} // namespace core
} // namespace xboa

