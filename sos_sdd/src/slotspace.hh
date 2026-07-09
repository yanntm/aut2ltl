// The slot space: one multi-valued DDD variable per slot, each with its
// own domain — heterogeneous on purpose, factored product coordinates
// concatenate blocks of different component types. Packing semantics
// live on the Python side (slotmodel.py); here a slot is a domain size
// and an identity value. Slot i is DDD variable i, and variable 0 is
// adjacent to the terminal (the library convention — required by the
// expression homomorphisms and the SDD growth path).

#pragma once

#include <stdexcept>
#include <string>
#include <vector>

#include "ddd/DDD.h"

namespace sossdd {

struct SlotSpace {
  std::vector<int> doms;
  std::vector<int> identity_vals;

  int n_slots() const { return static_cast<int>(doms.size()); }

  // DDD edge values are val_t; every slot domain must fit (recorded
  // guard — escape hatches are a split encoding or a wider val_t build).
  void check(const std::string &name) const {
    if (doms.size() != identity_vals.size() || doms.empty())
      throw std::invalid_argument(name + ": malformed slot space");
    for (size_t i = 0; i < doms.size(); ++i) {
      if (doms[i] > 32767)
        throw std::invalid_argument(
            name + ": slot " + std::to_string(i) + " domain " +
            std::to_string(doms[i]) +
            " exceeds val_t; split encoding or wider libDDD val_t required");
      if (identity_vals[i] < 0 || identity_vals[i] >= doms[i])
        throw std::invalid_argument(name + ": identity value out of domain");
    }
  }

  GDDD identity() const {
    GDDD d = GDDD::one;
    for (int i = 0; i < n_slots(); ++i)
      d = GDDD(i, static_cast<GDDD::val_t>(identity_vals[i]), d);
    return d;
  }
};

}  // namespace sossdd
