// The slot space: one multi-valued DDD variable per source state of the
// automaton, packed domain V = Q x 2^C with pack(q, S) = (q << |C|) | S.
// Variable ids are slot indices; natural order puts slot 0 on top.

#pragma once

#include <stdexcept>
#include <string>

#include "ddd/DDD.h"

namespace sossdd {

struct SlotSpace {
  int n_states;
  int n_marks;

  int dom() const { return n_states << n_marks; }
  int mark_mask() const { return (1 << n_marks) - 1; }
  GDDD::val_t pack(int q, int marks) const {
    return static_cast<GDDD::val_t>((q << n_marks) | marks);
  }
  int state_of(int v) const { return v >> n_marks; }
  int marks_of(int v) const { return v & mark_mask(); }

  // DDD edge values are val_t; the packed encoding must fit (recorded
  // guard — escape hatches are a split encoding or a wider val_t build).
  void check(const std::string &name) const {
    if (dom() > 32767)
      throw std::invalid_argument(
          name + ": packed slot domain " + std::to_string(dom()) +
          " exceeds val_t; split encoding or wider libDDD val_t required");
  }

  // The identity element: every slot q holds (q, no marks).
  GDDD identity() const {
    GDDD d = GDDD::one;
    for (int i = n_states - 1; i >= 0; --i)
      d = GDDD(i, pack(i, 0), d);
    return d;
  }
};

}  // namespace sossdd
