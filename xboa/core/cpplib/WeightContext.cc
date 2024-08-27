#include <sstream>
#include "cpplib/WeightContext.hh"

namespace xboa {
namespace core {

//SmartPointer<WeightContext> WeightContext::currentContext = SmartPointer<WeightContext>();

/*
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
*/
/*
SmartPointer<WeightContext>& WeightContext::getCurrentContextMember() {
    //std::cerr << "GetCurrentContext " << this << " " << currentContext.get() << std::endl;
    //return currentContext;
}

void WeightContext::setCurrentContextMember(SmartPointer<WeightContext> context) {
    //currentContext = context;
    //std::cerr << "SetCurrentContext " << &currentContext << std::endl;
}
*/

/*
SmartPointer<WeightContext>& WeightContext::getCurrentContext() {
    std::cerr << "GetCurrentContext " << currentContext.get() << std::endl;
    return currentContext;
}

void WeightContext::setCurrentContext(SmartPointer<WeightContext> context) {
    currentContext = context;
    std::cerr << "SetCurrentContext " << &currentContext << std::endl;
}
*/
} // namespace core
} // namespace xboa

