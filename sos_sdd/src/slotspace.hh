// The slot space: one multi-valued DDD variable per slot, each with its
// own domain — heterogeneous on purpose, factored product coordinates
// concatenate blocks of different component types. Packing semantics
// live on the Python side (slotmodel.py); here a slot is a domain size
// and an identity value. Slot i is stored at DDD variable var_of[i]
// (the C9 slot permutation — an indirection, never a re-semantics:
// every payload table stays slot-indexed); variable 0 is adjacent to
// the terminal (the library convention — required by the expression
// homomorphisms and the SDD growth path).

#pragma once

#include <stdexcept>
#include <string>
#include <vector>

#include "ddd/DDD.h"

namespace sossdd {

// One letter-behavior class acting on the slot space: a total function
// on each slot's values, given extensionally (`maps[slot][v] = w` — the
// packing that produced the values is the Python side's business).
struct LetterClassRow {
  std::string least;                   // lex-least letter of the class
  long long count = 0;                 // number of letters in the class
  std::vector<std::vector<int>> maps;  // per slot: value -> value
};

struct SlotSpace {
  std::vector<int> doms;
  std::vector<int> identity_vals;
  std::vector<int> var_of;  // slot -> DDD variable (a bijection)

  int n_slots() const { return static_cast<int>(doms.size()); }

  // slot stored at each variable — the inverse permutation.
  std::vector<int> slot_at() const {
    std::vector<int> inv(var_of.size());
    for (size_t i = 0; i < var_of.size(); ++i)
      inv[static_cast<size_t>(var_of[i])] = static_cast<int>(i);
    return inv;
  }

  // DDD edge values are val_t; every slot domain must fit (recorded
  // guard — escape hatches are a split encoding or a wider val_t build).
  void check(const std::string &name) const {
    if (doms.size() != identity_vals.size() || doms.empty())
      throw std::invalid_argument(name + ": malformed slot space");
    if (var_of.size() != doms.size())
      throw std::invalid_argument(name + ": slot permutation size mismatch");
    std::vector<bool> seen(var_of.size(), false);
    for (int v : var_of) {
      if (v < 0 || v >= n_slots() || seen[static_cast<size_t>(v)])
        throw std::invalid_argument(name +
                                    ": slot_perm is not a permutation");
      seen[static_cast<size_t>(v)] = true;
    }
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

  // One path holding slot-ordered values, wrapped in ascending variable
  // order (variable 0 innermost, adjacent to the terminal).
  GDDD path(const std::vector<int> &slot_vals) const {
    const std::vector<int> inv = slot_at();
    GDDD d = GDDD::one;
    for (int v = 0; v < n_slots(); ++v)
      d = GDDD(v, static_cast<GDDD::val_t>(slot_vals[inv[v]]), d);
    return d;
  }

  GDDD identity() const { return path(identity_vals); }

  // Reorder one reversed path (variable 0 first) back to slot order —
  // explicit readings return slot tuples, the perm stays invisible.
  std::vector<int> unpermute(const std::vector<int> &by_var) const {
    std::vector<int> out(var_of.size());
    for (size_t i = 0; i < var_of.size(); ++i)
      out[i] = by_var[static_cast<size_t>(var_of[i])];
    return out;
  }
};

}  // namespace sossdd
