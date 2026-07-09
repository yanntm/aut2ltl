// The five-primitive layer (§2.2 of the paper) mapped onto libDDD's
// multi-valued DDD core, with the thin helpers the engine reads through.
//
//   1. set algebra      — GDDD operator+ (∪), * (∩), - (∖): native.
//   2. comparison       — operator==: O(1) pointer equality on the
//                         unicity table.
//   3. relation apply   — libDDD's apply2k is strictly single-variable
//                         (it rewrites the top variable of its argument);
//                         the k-variable relational apply over an
//                         interleaved src/dst diagram is this engine's
//                         own homomorphism (relation module, with the
//                         letter relations).
//   4. fixpoints        — fixpoint(h + GHom::id) for the saturation
//                         discipline; the layered discipline is an
//                         explicit loop (layers are load-bearing for
//                         shortlex extraction and are kept).
//   5. quotient         — not native; small-side fallback at quotient
//                         time (recorded in the stats stream).
//
// Objects that live across engine steps must be held through the
// reference-counted wrappers (DDD, Hom), never bare GDDD/GHom: the
// library garbage-collects unreferenced nodes whenever it sees fit —
// memory management is libDDD's alone, this engine never triggers it.

#pragma once

#include "ddd/DDD.h"
#include "ddd/Hom.h"

namespace sossdd {

// Model count (number of assignment paths). libDDD counts in long
// double; narrowed here — exact well beyond any cardinality the ledgers
// tabulate.
inline double model_count(const GDDD &d) { return static_cast<double>(d.nbStates()); }

// Node count of one set (shared nodes counted once).
inline unsigned long long node_count(const GDDD &d) {
  return static_cast<unsigned long long>(d.size());
}

}  // namespace sossdd
