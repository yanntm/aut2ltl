// The C4 squaring shortcut — the 2k-variable relation encoding recorded
// in ../README.md ("The squaring shortcut (C4 completion)").
//
// The squaring map z -> z·z is materialized ONCE as an interleaved
// relation diagram R = {(z ⧉ z·z) : z in EM1} on a dedicated 2n-variable
// space — slot q becomes the pair r_q = var 2q+1 (pre, read-only) above
// w_q = var 2q (post, write-only); variable 0 stays adjacent to the
// terminal and the numbering is collision-free, so a GalOrder over it is
// well-defined. The step is the paper's case split verbatim,
//
//   H_q  =  sum_p [ w_q := r_{base_q+p} | (r_q & mask_q) ]
//                    o  [ r_q >> C_q == p ]
//
// and is hazard-free BY CONSTRUCTION: every guard and rhs mentions only
// r-variables, every write targets a w-variable, so written set and read
// set are disjoint and the sequential composition equals the
// simultaneous Comp — no ordering argument needed. (The transparent
// DoubleVars doubling of libITS bin/ToTransRel.cpp was rejected for this
// step: correct for GAL's sequential semantics, but Comp's cross-slot
// reads need the OLD values and the colliding numbers make the frozen
// copies unaddressable by a GalOrder.)
//
// R is iterated by applyRel, a relational-product homomorphism carrying
// the R sub-diagram (the Apply2k pattern): it travels two R-levels per
// set variable while descending the z-block of the crossing's pair
// space, matches the set value on R's pre level, emits the post values,
// and turns into the identity exactly where R exhausts (the x-block).
// The loop P_{j+1} = applyRel(R)(P_j) from the diagonal holds one pair
// per x, so its O(1) set fixpoint is pointwise idempotence — the
// fixpoint IS the idempotence test and the result is {(x, x^pi)}. Cap
// ceil(log2 |EM1|) + 1: an orbit of index i, period d has x^(2^j)
// stable iff 2^j >= i and d | 2^j, both settled by the cap if ever —
// squaring converges iff every orbit period is a power of two, which is
// why it is a shortcut, never a verdict.

#pragma once

#include <chrono>
#include <cmath>
#include <memory>
#include <string>
#include <vector>

#include "ddd/DDD.h"
#include "ddd/Hom.h"

#include "its/Ordering.hh"
#include "its/gal/BoolExpression.hh"
#include "its/gal/ExprHom.hpp"
#include "its/gal/GALOrder.hh"
#include "its/gal/IntExpression.hh"

#include "crossing.hh"
#include "findings.hh"
#include "primitives.hh"
#include "slotspace.hh"
#include "stats.hh"

namespace sossdd {

// Duplicate every variable of a set into an adjacent (pre, post) pair
// with collision-free numbering: (q, v) -> (2q+1: v) above (2q: v). A
// renumbering variant of libITS' DoubleVars.
class DupeVars : public StrongHom {
public:
  GDDD phiOne() const { return GDDD::one; }
  GHom phi(int var, int val) const {
    return GDDD(2 * var + 1, static_cast<GDDD::val_t>(val)) ^
           GDDD(2 * var, static_cast<GDDD::val_t>(val)) ^ GHom(this);
  }
  bool operator==(const StrongHom &) const { return true; }
  size_t hash() const { return 76543211; }
  _GHom *clone() const { return new DupeVars(); }
};

GHom applyRel(const GDDD &rel);

// The relational product: rewrite the top block of the argument through
// the interleaved relation `rel` — two rel-levels per set variable
// (match the value on the pre level, emit the post values), identity
// once rel exhausts. Matching is by depth; rel's variable numbers are
// not consulted.
class ApplyRel : public StrongHom {
public:
  explicit ApplyRel(const GDDD &rel) : rel_(rel) {}

  GDDD phiOne() const { return GDDD::one; }

  GHom phi(int var, int val) const {
    for (GDDD::const_iterator it = rel_.begin(); it != rel_.end(); ++it) {
      if (it->first != val) continue;
      d3::set<GHom>::type out;
      const GDDD &post = it->second;
      for (GDDD::const_iterator jt = post.begin(); jt != post.end(); ++jt)
        out.insert(GDDD(var, jt->first) ^ applyRel(jt->second));
      return GHom::add(out);
    }
    return GHom(GDDD::null);
  }

  bool operator==(const StrongHom &h) const {
    return rel_ == ((const ApplyRel &)h).rel_;
  }
  size_t hash() const { return rel_.hash() * 8527; }
  _GHom *clone() const { return new ApplyRel(*this); }
  void mark() const { rel_.mark(); }

private:
  GDDD rel_;
};

inline GHom applyRel(const GDDD &rel) {
  if (rel == GDDD::one) return GHom::id;
  if (rel == GDDD::null) return GHom(GDDD::null);
  return ApplyRel(rel);
}

class Squaring {
public:
  Squaring(const std::string &name, const SlotSpace &space,
           const PackInfo &pack)
      : name_(name), n_(space.n_slots()), var_of_(space.var_of) {
    // The interleaved space inherits the perm blockwise: slot q's
    // (post, pre) pair sits at variables (2·var_of[q], 2·var_of[q]+1) —
    // the dupe gadget doubles positionally, so this is its layout.
    labels_t labels(2 * static_cast<size_t>(n_));
    for (int q = 0; q < n_; ++q) {
      labels[static_cast<size_t>(2 * space.var_of[q])] =
          "w_" + std::to_string(q);
      labels[static_cast<size_t>(2 * space.var_of[q] + 1)] =
          "r_" + std::to_string(q);
    }
    vo_ = its::VarOrder(labels);
    go_ = std::make_unique<its::GalOrder>(&vo_);

    using its::IntExpression;
    using its::IntExpressionFactory;
    const auto rvar = [](int q) {
      return IntExpressionFactory::createVariable(
          its::Variable("r_" + std::to_string(q)));
    };
    const auto wvar = [](int q) {
      return IntExpressionFactory::createVariable(
          its::Variable("w_" + std::to_string(q)));
    };

    Hom step = GHom::id;
    for (int q = 0; q < n_; ++q) {
      const IntExpression rq = rvar(q);
      const int mask = (1 << pack.mark_bits[q]) - 1;
      const int states = space.doms[q] >> pack.mark_bits[q];
      const IntExpression st = IntExpressionFactory::createBinary(
          its::RSHIFT, rq, IntExpression(pack.mark_bits[q]));
      const IntExpression mk = IntExpressionFactory::createBinary(
          its::BITAND, rq, IntExpression(mask));
      d3::set<GHom>::type cases;
      for (int p = 0; p < states; ++p) {
        const its::BoolExpression at_p = (st == IntExpression(p)).eval();
        const IntExpression via = IntExpressionFactory::createBinary(
            its::BITOR, rvar(pack.block_base[q] + p), mk).eval();
        cases.insert(its::assignExpr(wvar(q), via, go_.get()) &
                     its::predicate(at_p, go_.get()));
      }
      step = GHom::add(cases) & step;
    }
    step_ = step;
  }

  Squaring(const Squaring &) = delete;
  Squaring &operator=(const Squaring &) = delete;

  // R = step(dupe(EM1)) — built once; |R| must equal |EM1| (the map is
  // total and functional), a violation is a defect.
  void build_rel(Stats &st, const DDD &em1) {
    Stats::Op op(st, 2, "square-rel");
    rel_ = DDD(step_(GHom(DupeVars())(em1)));
    op.rec().add("card", model_count(rel_)).add("nodes", node_count(rel_));
    if (model_count(rel_) != model_count(em1))
      throw LineStopped{name_ + ": squaring relation is not functional (" +
                        std::to_string(model_count(rel_)) + " pairs for " +
                        std::to_string(model_count(em1)) + " elements)"};
  }

  // The capped squaring loop from the diagonal {(x, x)}. Returns true
  // and holds pi on convergence; false when the cap passes without a
  // fixpoint (some orbit period is not a power of two — the expected
  // divergence, a finding for the caller to record, never an error).
  bool run(Stats &st, const DDD &diag, double em1_count,
           long long node_budget, double time_budget,
           const std::vector<LayerRow> &profile) {
    const auto t0 = std::chrono::steady_clock::now();
    const int cap = static_cast<int>(
        std::ceil(std::log2(em1_count < 2.0 ? 2.0 : em1_count))) + 1;
    DDD p = diag;
    for (int round = 1;; ++round) {
      Stats::Op op(st, 2, "square-step");
      DDD next = DDD(applyRel(static_cast<const GDDD &>(rel_))(p));
      op.rec().add("round", static_cast<long long>(round))
          .add("card", model_count(next))
          .add("nodes", node_count(next));
      op.close();
      if (model_count(next) != em1_count)
        throw LineStopped{name_ + ": squaring step lost pairs (" +
                          std::to_string(model_count(next)) + " for " +
                          std::to_string(em1_count) + ")"};
      if (next == p) {
        pi_ = p;
        rounds_ = round;
        converged_ = true;
        return true;
      }
      p = next;
      if (round > cap) {
        rounds_ = round;
        return false;
      }
      if (node_budget > 0 &&
          static_cast<long long>(GDDD::statistics()) > node_budget)
        throw BudgetExhausted{false, 2, profile};
      const std::chrono::duration<double> dt =
          std::chrono::steady_clock::now() - t0;
      if (time_budget > 0 && dt.count() > time_budget)
        throw BudgetExhausted{true, 2, profile};
    }
  }

  // -- readings --------------------------------------------------------
  const DDD &pi() const {
    if (!converged_)
      throw std::logic_error(name_ + ": squaring did not converge");
    return pi_;
  }
  int rounds() const { return rounds_; }

  // Explicit (z, z·z) rows of R — a test/debug reading. Reversed paths
  // run in variable order (evens post, odds pre); slot q's pair sits at
  // (2·var_of[q], 2·var_of[q]+1), un-permuted back to slot order.
  std::vector<std::pair<std::vector<int>, std::vector<int>>>
  rel_pairs(size_t limit) const {
    if (model_count(rel_) > static_cast<double>(limit))
      throw std::invalid_argument(name_ + ": R larger than the explicit cap");
    std::vector<std::pair<std::vector<int>, std::vector<int>>> out;
    const int n = n_;
    const std::vector<int> &vof = var_of_;
    callback_t cb = [&out, n, &vof](state_t &path) {
      std::vector<int> pre(n), post(n);
      for (int q = 0; q < n; ++q) {
        post[q] = *(path.rbegin() + 2 * vof[q]);
        pre[q] = *(path.rbegin() + 2 * vof[q] + 1);
      }
      out.emplace_back(std::move(pre), std::move(post));
    };
    iterate(static_cast<const GDDD &>(rel_), &cb);
    return out;
  }

private:
  std::string name_;
  int n_;
  std::vector<int> var_of_;  // slot -> variable (the C9 perm)
  its::VarOrder vo_;
  std::unique_ptr<its::GalOrder> go_;
  Hom step_;   // the interleaved case split (writes w, reads r only)
  DDD rel_;    // R = {(z ⧉ z·z)}
  DDD pi_;     // {(x, x^pi)} on the crossing pair space, once converged
  int rounds_ = 0;
  bool converged_ = false;
};

}  // namespace sossdd
