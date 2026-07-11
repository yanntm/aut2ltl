// Phase 2 — the one crossing: composition as the |Q|-way case split,
// computing the idempotent-power map pi = {(x, x^pi)} on a doubled slot
// space.
//
// The pair space stacks a y-block (variables n..2n-1) above the x-block
// (variables 0..n-1, variable 0 adjacent to the terminal per the library
// convention). Every variable is a plain scalar (x_q / y_q — the space is
// fixed-size, so no array encoding); composition z = y·x at slot q is the
// paper's own case-split formula, one guarded assignment per state p of
// slot q's component, rendered with the GAL expression homomorphisms
// (assignExpr / predicate of libITS-gal, the CAV 2012 symbolic expression
// evaluation):
//
//   H_q  =  sum_p  [ y_q := x_{base_q + p} | (y_q & mask_q) ]
//                     o  [ y_q >> C_q == p ]
//
// The guards partition, so H_q is total; slots compose sequentially (each
// H_q writes only its own y_q, and the x-block is read-only). The payload
// contract fixes the packing (PackInfo): a slot value is
// (state << mark_bits[q]) | marks with a component-local state, and
// block_base[q] maps that state to its global slot index.
//
// pi is the pairing lfp {(x, x^j)}_{j>=1} filtered by the idempotence
// predicate. The aperiodic squaring shortcut (C4) is deferred: y <- y·y
// rewrites every y_q while reading the others, which needs a genuinely
// simultaneous step — pending a 2k-variable relation encoding.

#pragma once

#include <chrono>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include "ddd/DDD.h"
#include "ddd/Hom.h"

#include "its/Ordering.hh"
#include "its/gal/BoolExpression.hh"
#include "its/gal/ExprHom.hpp"
#include "its/gal/GALOrder.hh"
#include "its/gal/IntExpression.hh"

#include "findings.hh"
#include "primitives.hh"
#include "slotspace.hh"
#include "stats.hh"

namespace sossdd {

// The packing contract of slot values, declared by the Python slot model
// (slotmodel.py) and consumed here as numbers, never as convention.
struct PackInfo {
  std::vector<int> mark_bits;   // per slot: low bits carrying the mark set
  std::vector<int> block_base;  // per slot: global slot of its component's state 0
};

class Crossing {
public:
  Crossing(const std::string &name, const SlotSpace &space,
           const PackInfo &pack, const DDD &em1)
      : name_(name), n_(space.n_slots()), var_of_(space.var_of) {
    check_pack(space, pack);

    // The label-list index IS the DDD variable: slot i's x at var_of[i],
    // its y at n + var_of[i] (the pair space inherits the perm blockwise).
    labels_t labels(2 * static_cast<size_t>(n_));
    for (int i = 0; i < n_; ++i) {
      labels[static_cast<size_t>(space.var_of[i])] = "x_" + std::to_string(i);
      labels[static_cast<size_t>(n_ + space.var_of[i])] =
          "y_" + std::to_string(i);
    }
    vo_ = its::VarOrder(labels);
    go_ = std::make_unique<its::GalOrder>(&vo_);

    using its::IntExpression;
    using its::IntExpressionFactory;
    const auto var = [](const char *blk, int i) {
      return IntExpressionFactory::createVariable(
          its::Variable(blk + std::to_string(i)));
    };

    Hom step = GHom::id;
    Hom copy = GHom::id;
    its::BoolExpression idem = its::BoolExpressionFactory::createConstant(true);
    for (int q = 0; q < n_; ++q) {
      const IntExpression yq = var("y_", q);
      const int mask = (1 << pack.mark_bits[q]) - 1;
      const int states = space.doms[q] >> pack.mark_bits[q];
      const IntExpression st = IntExpressionFactory::createBinary(
          its::RSHIFT, yq, IntExpression(pack.mark_bits[q]));
      const IntExpression mk = IntExpressionFactory::createBinary(
          its::BITAND, yq, IntExpression(mask));

      d3::set<GHom>::type cases;
      its::BoolExpression idem_q =
          its::BoolExpressionFactory::createConstant(false);
      for (int p = 0; p < states; ++p) {
        const its::BoolExpression at_p = (st == IntExpression(p)).eval();
        const IntExpression via_x = IntExpressionFactory::createBinary(
            its::BITOR, var("x_", pack.block_base[q] + p), mk).eval();
        const IntExpression via_y = IntExpressionFactory::createBinary(
            its::BITOR, var("y_", pack.block_base[q] + p), mk).eval();
        cases.insert(its::assignExpr(yq, via_x, go_.get()) &
                     its::predicate(at_p, go_.get()));
        idem_q = idem_q || (at_p && (via_y == yq));
      }
      step = GHom::add(cases) & step;
      copy = its::assignExpr(yq, var("x_", q), go_.get()) & copy;
      idem = idem && idem_q;
    }
    step_ = step;
    idem_ = its::predicate(idem.eval(), go_.get());

    // The diagonal seed {(x, x)}: a placeholder y-block stacked above
    // EM1's x-block, then y := x slot by slot. Wrapped in ascending
    // variable order; the slot at y-variable n+v is slot_at[v].
    const std::vector<int> inv = space.slot_at();
    GDDD ycells = GDDD::one;
    for (int v = 0; v < n_; ++v)
      ycells = GDDD(n_ + v,
                    static_cast<GDDD::val_t>(space.identity_vals[inv[v]]),
                    ycells);
    diag_ = DDD(copy(ycells ^ GDDD(em1)));
  }

  Crossing(const Crossing &) = delete;
  Crossing &operator=(const Crossing &) = delete;

  // Compute pi by the general pairing: close {(x, x)} under y <- y·x,
  // holding every (x, x^j), then keep the unique idempotent per orbit.
  // time_budget is the remaining wall allowance (0 = unlimited); profile
  // is the closure's layer profile, attached to budget findings.
  void run(Stats &st, double em1_count, long long node_budget,
           double time_budget, const std::vector<LayerRow> &profile) {
    const auto t0 = std::chrono::steady_clock::now();
    int rounds = 0;
    DDD p = diag_;
    for (;;) {
      Stats::Op op(st, 2, "pairing-step");
      DDD next = p + DDD(step_(p));
      ++rounds;
      op.rec().add("round", static_cast<long long>(rounds))
          .add("card", model_count(next))
          .add("nodes", node_count(next));
      op.close();
      if (next == p) break;
      p = next;
      if (node_budget > 0 &&
          static_cast<long long>(GDDD::statistics()) > node_budget)
        throw BudgetExhausted{false, 2, profile};
      const std::chrono::duration<double> dt =
          std::chrono::steady_clock::now() - t0;
      if (time_budget > 0 && dt.count() > time_budget)
        throw BudgetExhausted{true, 2, profile};
    }
    {
      Stats::Op op(st, 2, "idem-select");
      pi_ = DDD(idem_(p));
      op.rec().add("card", model_count(pi_)).add("nodes", node_count(pi_));
    }
    if (model_count(pi_) != em1_count)
      throw LineStopped{name_ + ": pi is not functional (" +
                        std::to_string(model_count(pi_)) + " pairs for " +
                        std::to_string(em1_count) + " elements)"};
    built_ = true;
    st.emit(Record("phase")
                .add("phase", 2LL)
                .add("pairing_rounds", static_cast<long long>(rounds))
                .add("pi_nodes", node_count(pi_)));
  }

  // Adopt an externally computed pi (the squaring shortcut under
  // square="on") — same functionality check as run(), same readings
  // afterward. The orchestration seam; the shortcut itself lives in
  // squaring.hh.
  void adopt_pi(Stats &st, const DDD &pi, double em1_count, int rounds) {
    pi_ = pi;
    if (model_count(pi_) != em1_count)
      throw LineStopped{name_ + ": pi is not functional (" +
                        std::to_string(model_count(pi_)) + " pairs for " +
                        std::to_string(em1_count) + " elements)"};
    built_ = true;
    st.emit(Record("phase")
                .add("phase", 2LL)
                .add("squaring", "trusted")
                .add("square_rounds", static_cast<long long>(rounds))
                .add("pi_nodes", node_count(pi_)));
  }

  // -- readings --------------------------------------------------------
  const DDD &diag() const { return diag_; }
  const DDD &pi() const { require(); return pi_; }
  double pi_count() const { require(); return model_count(pi_); }
  unsigned long long pi_nodes() const { require(); return node_count(pi_); }

  // Explicit enumeration of the (x, x^pi) pairs as raw slot values — a
  // test/debug reading; symbolic consumers apply pi_ as a set.
  std::vector<std::pair<std::vector<int>, std::vector<int>>>
  pi_pairs(size_t limit) const {
    require();
    if (pi_count() > static_cast<double>(limit))
      throw std::invalid_argument(name_ + ": pi larger than the explicit cap");
    std::vector<std::pair<std::vector<int>, std::vector<int>>> out;
    const int n = n_;
    const std::vector<int> &vof = var_of_;
    // Paths run top-down; reversed they are variable order (x-block then
    // y-block), un-permuted back to slot order for the reading.
    callback_t cb = [&out, n, &vof](state_t &path) {
      std::vector<int> x(static_cast<size_t>(n)), y(static_cast<size_t>(n));
      for (int i = 0; i < n; ++i) {
        x[static_cast<size_t>(i)] = *(path.rbegin() + vof[i]);
        y[static_cast<size_t>(i)] = *(path.rbegin() + n + vof[i]);
      }
      out.emplace_back(std::move(x), std::move(y));
    };
    iterate(static_cast<const GDDD &>(pi_), &cb);
    return out;
  }

private:
  void require() const {
    if (!built_)
      throw std::logic_error(name_ + ": phase 2 has not been run");
  }

  void check_pack(const SlotSpace &space, const PackInfo &pack) const {
    if (static_cast<int>(pack.mark_bits.size()) != n_ ||
        static_cast<int>(pack.block_base.size()) != n_)
      throw std::invalid_argument(name_ + ": malformed pack info");
    for (int q = 0; q < n_; ++q) {
      const int states = space.doms[q] >> pack.mark_bits[q];
      if (pack.mark_bits[q] < 0 || states < 1 ||
          pack.block_base[q] < 0 || pack.block_base[q] + states > n_)
        throw std::invalid_argument(
            name_ + ": pack info of slot " + std::to_string(q) +
            " addresses outside the slot space");
    }
  }

  std::string name_;
  int n_;
  std::vector<int> var_of_;  // slot -> variable (the C9 perm)
  its::VarOrder vo_;
  std::unique_ptr<its::GalOrder> go_;
  Hom step_;   // y <- y·x   (pairing step, the case split)
  Hom idem_;   // selects pairs whose y-column is idempotent
  DDD diag_;   // {(x, x) : x in EM1}
  DDD pi_;     // {(x, x^pi)} once run() completes
  bool built_ = false;
};

}  // namespace sossdd
