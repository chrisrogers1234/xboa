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

#ifndef xboa_core_utils_SmartPointer_hh
#define xboa_core_utils_SmartPointer_hh

#include <iostream>
#include <map>
#include <stdexcept>

namespace xboa {
namespace core {

/** SmartPointer is a templated SmartPointer object that does reference counting
 *
 *  SmartPointer holds a global std::map that maps memory addresses to an
 *  integer reference count. If the reference count for a particular address
 *  goes to 0, SmartPointer deletes it. Reference count for a particular type
 *  is shared for all objects of that type called by a particular .so library.
 *  Note that the reference count is probably not shared between differnt .so
 *  libraries (e.g. Python import files). This may cause trouble downstream. See
 *  e.g. extern keyword.
 */
template <typename Ptr>
class SmartPointer {
public:
    /** Constructor initialises ptr_ to NULL */
    SmartPointer();

    /** Constructor sets ptr_ and increments the ref count*/
    explicit SmartPointer(Ptr* ptr);

    /** Copy constructor sets ptr_ and increments the ref count*/
    SmartPointer(const SmartPointer& smart_ptr);

    /** Assignment operator sets ptr_ and increments the ref count*/
    SmartPointer& operator=(const SmartPointer& smart_ptr);

    /** Destructor decrements reference count.
     *
     *  Deletes ptr_ if ref_count is 0
     */
    ~SmartPointer();

    /** Set ptr_ to pointer. 
     *
     *  If ptr_ is initially not NULL, decrements reference count.
     */
    inline void set(Ptr* pointer);

    /** Return ptr_; ptr_ is still owned by SmartPointer */
    inline Ptr* get();

    /** Return the number of references to ptr_ */
    std::size_t ref_count() {return ref_count(ptr_);}
    /** Return the number of references to ptr_ */
    static std::size_t ref_count(Ptr* ptr);

    /** Return value of ptr_ */
    inline Ptr& operator*();
    /** Dereference ptr_ */
    inline Ptr* operator->();
    /** Return mapping of Pointers to references for Ptr type */
    static std::map<Ptr*, std::size_t>* get_context();
    /** Set mapping of Pointers to references for Ptr type */
    static void set_context(std::map<Ptr*, std::size_t>* refs);
private:
    void decref(Ptr* ptr_);
    void incref(Ptr* ptr_);

    Ptr* ptr_;
    static std::map<Ptr*, std::size_t>* ref_count_;
};

template <typename Ptr>
SmartPointer<Ptr>::SmartPointer() : ptr_(NULL) {
}

template <typename Ptr>
SmartPointer<Ptr>::SmartPointer(Ptr* ptr_) : ptr_(NULL) {
    set(ptr_);
}

template <typename Ptr>
SmartPointer<Ptr>::SmartPointer(const SmartPointer<Ptr>& smart_ptr)
  : ptr_(NULL) {
    set(smart_ptr.ptr_);
}

template <typename Ptr>
SmartPointer<Ptr>& SmartPointer<Ptr>::operator=(
                                           const SmartPointer<Ptr>& smart_ptr) {
    set(smart_ptr.ptr_);
    return *this;
}

template <typename Ptr>
SmartPointer<Ptr>::~SmartPointer() {
    decref(ptr_);
}

template <typename Ptr>
void SmartPointer<Ptr>::set(Ptr* pointer) {

    decref(ptr_);
    ptr_ = pointer;
    incref(pointer);
}

template <typename Ptr>
Ptr* SmartPointer<Ptr>::get() {
    return ptr_;
}

template <typename Ptr>
void SmartPointer<Ptr>::decref(Ptr* ptr_) {
    if (ref_count_ == NULL)
        throw std::runtime_error(
                        "Attempt to use SmartPointer when no context was set");
    if (ref_count_->find(ptr_) == ref_count_->end())
        return;
    --(*ref_count_)[ptr_];
    if ((*ref_count_)[ptr_] == 0) {
        delete ptr_;
        ref_count_->erase(ptr_);
    }
}

template <typename Ptr>
std::size_t SmartPointer<Ptr>::ref_count(Ptr* ptr) {
    if (ref_count_->find(ptr) == ref_count_->end())
        return 0;
    return (*ref_count_)[ptr];
}


template <typename Ptr>
void SmartPointer<Ptr>::incref(Ptr* ptr_) {
    if (ptr_ == NULL) {
        return;
    }
    ++(*ref_count_)[ptr_];
}

template <typename Ptr>
Ptr& SmartPointer<Ptr>::operator*() {
    if (ptr_ == NULL) {
        throw std::invalid_argument("Attempt to dereference a NULL pointer");
    }
    return *ptr_;
}

template <typename Ptr>
Ptr* SmartPointer<Ptr>::operator->() {
    return ptr_;
}

template <typename Ptr>
std::map<Ptr*, std::size_t>* SmartPointer<Ptr>::get_context() {
    return ref_count_;
}

template <typename Ptr>
void SmartPointer<Ptr>::set_context(std::map<Ptr*, std::size_t>* refs) {
    ref_count_ = refs;
}

template <typename Ptr>
std::map<Ptr*, std::size_t>* SmartPointer<Ptr>::ref_count_ = NULL;
} // core
} // xboa

// Potential fix for extern stuff; define a SmartPointer "context" which sets up
// the ref_count_ map and hand this around at start up (e.g. import time).
// May be possible to do something using extern keyword. I stuggled to extern
// static member functions, due to obscure C++ syntax issues.


#endif
