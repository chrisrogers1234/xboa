#include <sstream>
#include "cpplib/WeightContext.hh"

namespace xboa {
namespace core {

std::map<std::string, WeightContext*> WeightContext::contexts_;
size_t WeightContext::uniqueId_ = 1;
std::string WeightContext::defaultName() {
    std::stringstream ss;
    ss << "__default" << uniqueId_ << "__";
    uniqueId_++;
    return ss.str();
}


}
}

