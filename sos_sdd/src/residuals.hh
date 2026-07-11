// Phases 3-4 — profiles and residuals, on the pair space produced by the
// crossing.
//
// Phase 3 (profiles, one slot-read): for a global automaton state g the
// loop verdict of an element x is A(g, x) = Acc(mk_e(st_e(g))) with
// e = x^pi — no orbit walk and no cycle detection anywhere in this path
// (idempotency of e makes the verdict a single indexed read; the C5
// invariant). Rendered on the y-block of pi's pair space as one predicate
// per g:
//
//   A_g  =  and_b  or_p'  [ y_{s_b + g_b} >> C == p' ]
//                       & [ (y_{s_b + p'} & mask) in accept[s_b + p'] ]
//
// (b ranges over the component blocks derived from block_base, s_b is the
// block's first slot, g_b the state's local component; the global
// acceptance is the conjunction of the per-block conditions — exactly the
// digest's formula when there is one block). The profile column
// S_g = predicate(A_g)(pi) is a set of (x, x^pi) pairs; two states agree
// on every element iff their columns are equal — an O(1) canonical
// comparison, which seeds Phase 4 without any per-pair quantification.
// The identity element rides along harmlessly: its verdict Acc(empty) is
// the same at every state, so it never separates a column.
//
// Phase 4 (residuals): the gfp on Q x Q, profile-seeded and refined by
// the deterministic letter-class steps — Moore partition refinement over
// the explicit (tiny) global state space, delta read off the class value
// maps. Oracle-free: no language query anywhere.

#pragma once

#include <chrono>
#include <map>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include "ddd/DDD.h"
#include "ddd/Hom.h"
#include "ddd/Hom_Basic.hh"

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

class Residuals {
public:
  // accept[q]: the mark masks slot q's component acceptance holds on —
  // the numeric grounding of the digest's formula (declared Python-side,
  // consumed here as numbers, like PackInfo).
  Residuals(const std::string &name, const SlotSpace &space,
            const PackInfo &pack,
            const std::vector<std::vector<int>> &accept,
            const std::vector<LetterClassRow> &classes)
      : name_(name), n_(space.n_slots()) {
    if (static_cast<int>(accept.size()) != n_)
      throw std::invalid_argument(name_ + ": malformed accept table");

    // Component blocks from block_base: contiguous slot runs, each slot
    // carrying its block's first slot as base and the block length as its
    // state count.
    for (int s = 0; s < n_; ++s) {
      if (pack.block_base[s] == s) starts_.push_back(s);
      if (starts_.empty() || pack.block_base[s] != starts_.back())
        throw std::invalid_argument(name_ + ": non-contiguous block at slot " +
                                    std::to_string(s));
    }
    long long g = 1;
    for (size_t b = 0; b < starts_.size(); ++b) {
      const int end = b + 1 < starts_.size() ? starts_[b + 1] : n_;
      const int size = end - starts_[b];
      for (int s = starts_[b]; s < end; ++s)
        if (space.doms[s] >> pack.mark_bits[s] != size)
          throw std::invalid_argument(
              name_ + ": slot " + std::to_string(s) +
              " state count disagrees with its block length");
      sizes_.push_back(size);
      g *= size;
      if (g > 32767)
        throw std::invalid_argument(
            name_ + ": global state space too large for the explicit "
            "Phase 3-4 rendering");
    }
    n_global_ = static_cast<int>(g);

    // The per-class deterministic step on global states, blockwise:
    // delta_b(p, c) is the state part of class c's image of the block's
    // identity value at local state p.
    delta_.assign(n_global_, std::vector<int>(classes.size()));
    for (int st = 0; st < n_global_; ++st) {
      const std::vector<int> locals = digits(st);
      for (size_t c = 0; c < classes.size(); ++c) {
        std::vector<int> nxt(starts_.size());
        for (size_t b = 0; b < starts_.size(); ++b) {
          const int slot = starts_[b] + locals[b];
          nxt[b] = classes[c].maps[slot][space.identity_vals[slot]] >>
                   pack.mark_bits[slot];
        }
        delta_[st][c] = index(nxt);
      }
    }

    // The A_g predicates, on the same pair-space labeling as the crossing.
    labels_t labels;
    for (int i = 0; i < n_; ++i) labels.push_back("x_" + std::to_string(i));
    for (int i = 0; i < n_; ++i) labels.push_back("y_" + std::to_string(i));
    vo_ = its::VarOrder(labels);
    go_ = std::make_unique<its::GalOrder>(&vo_);

    using its::BoolExpression;
    using its::BoolExpressionFactory;
    using its::IntExpression;
    using its::IntExpressionFactory;
    const auto yvar = [](int i) {
      return IntExpressionFactory::createVariable(
          its::Variable("y_" + std::to_string(i)));
    };
    for (int st = 0; st < n_global_; ++st) {
      const std::vector<int> locals = digits(st);
      BoolExpression a = BoolExpressionFactory::createConstant(true);
      for (size_t b = 0; b < starts_.size(); ++b) {
        const int slot = starts_[b] + locals[b];
        const IntExpression state = IntExpressionFactory::createBinary(
            its::RSHIFT, yvar(slot), IntExpression(pack.mark_bits[slot]));
        BoolExpression blk = BoolExpressionFactory::createConstant(false);
        for (int p = 0; p < sizes_[b]; ++p) {
          const int read = starts_[b] + p;
          const IntExpression mk = IntExpressionFactory::createBinary(
              its::BITAND, yvar(read),
              IntExpression((1 << pack.mark_bits[read]) - 1));
          BoolExpression acc = BoolExpressionFactory::createConstant(false);
          for (int m : accept[read]) acc = acc || (mk == IntExpression(m));
          blk = blk || ((state == IntExpression(p)) && acc);
        }
        a = a && blk;
      }
      prof_homs_.push_back(its::predicate(a.eval(), go_.get()));
    }
  }

  Residuals(const Residuals &) = delete;
  Residuals &operator=(const Residuals &) = delete;

  // Phase 3: the profile columns S_g = predicate(A_g)(pi), kept — they
  // are the seed and the debug reading. Budgets as in the other phases.
  void profiles(Stats &st, const DDD &pi, long long node_budget,
                double time_budget, const std::vector<LayerRow> &profile) {
    const auto t0 = std::chrono::steady_clock::now();
    pi_ = pi;
    columns_.clear();
    for (int g = 0; g < n_global_; ++g) {
      Stats::Op op(st, 3, "profile-column");
      columns_.push_back(DDD(prof_homs_[g](pi_)));
      op.rec().add("state", static_cast<long long>(g))
          .add("card", model_count(columns_.back()))
          .add("nodes", node_count(columns_.back()));
      op.close();
      if (node_budget > 0 &&
          static_cast<long long>(GDDD::statistics()) > node_budget)
        throw BudgetExhausted{false, 3, profile};
      const std::chrono::duration<double> dt =
          std::chrono::steady_clock::now() - t0;
      if (time_budget > 0 && dt.count() > time_budget)
        throw BudgetExhausted{true, 3, profile};
    }
    // Seed classes by canonical column identity (O(1) per comparison).
    seed_.assign(n_global_, -1);
    std::vector<DDD> reps;
    for (int g = 0; g < n_global_; ++g) {
      for (size_t r = 0; r < reps.size(); ++r)
        if (columns_[g] == reps[r]) { seed_[g] = static_cast<int>(r); break; }
      if (seed_[g] < 0) {
        seed_[g] = static_cast<int>(reps.size());
        reps.push_back(columns_[g]);
      }
    }
    have_profiles_ = true;
    st.emit(Record("phase")
                .add("phase", 3LL)
                .add("states", static_cast<long long>(n_global_))
                .add("distinct_columns", static_cast<long long>(reps.size())));
  }

  // Phase 4: Moore refinement of the seed under the class steps.
  void refine(Stats &st) {
    require_profiles();
    std::vector<int> labels = seed_;
    int rounds = 0;
    for (;;) {
      Stats::Op op(st, 4, "refine-round");
      std::map<std::vector<int>, int> canon;
      std::vector<int> next(n_global_);
      for (int g = 0; g < n_global_; ++g) {
        std::vector<int> sig{labels[g]};
        for (const int d : delta_[g]) sig.push_back(labels[d]);
        next[g] = canon.emplace(sig, static_cast<int>(canon.size()))
                      .first->second;
      }
      ++rounds;
      op.rec().add("round", static_cast<long long>(rounds))
          .add("classes", static_cast<long long>(canon.size()));
      op.close();
      const bool stable = next == labels;
      labels = std::move(next);
      if (stable) break;
    }
    labels_ = labels;
    refined_ = true;
    int n_classes = 0;
    for (int l : labels_) n_classes = n_classes > l + 1 ? n_classes : l + 1;
    st.emit(Record("phase")
                .add("phase", 4LL)
                .add("rounds", static_cast<long long>(rounds))
                .add("classes", static_cast<long long>(n_classes)));
  }

  // -- readings --------------------------------------------------------
  int n_states() const { return n_global_; }

  // The residual partition: global state ids grouped by class, classes
  // ordered by least member. Global indexing is mixed-radix over the
  // blocks, block 0 most significant (= the state id itself when the
  // space has one block).
  std::vector<std::vector<int>> classes() const {
    require_refined();
    std::vector<std::vector<int>> out;
    std::vector<int> where(n_global_, -1);
    for (int g = 0; g < n_global_; ++g) {
      if (where[labels_[g]] < 0) {
        where[labels_[g]] = static_cast<int>(out.size());
        out.emplace_back();
      }
      out[where[labels_[g]]].push_back(g);
    }
    return out;
  }

  // Explicit profile matrix — a test/debug reading: every (x, bits) row
  // with bits[g] = A(g, x), obtained by membership of the (x, x^pi) pair
  // in the symbolic column S_g (so it exercises the real Phase 3 path).
  std::vector<std::pair<std::vector<int>, std::vector<int>>>
  profile_rows(size_t limit) const {
    require_profiles();
    if (model_count(pi_) > static_cast<double>(limit))
      throw std::invalid_argument(name_ + ": pi larger than the explicit cap");
    std::vector<std::pair<std::vector<int>, std::vector<int>>> out;
    const int n = n_;
    std::vector<std::vector<int>> pairs;  // full 2n-value paths, slot 0 first
    callback_t cb = [&pairs](state_t &path) {
      pairs.emplace_back(path.rbegin(), path.rend());
    };
    iterate(static_cast<const GDDD &>(pi_), &cb);
    for (const auto &p : pairs) {
      // Variable 0 adjacent to the terminal: wrap upward from slot 0.
      GDDD one = GDDD::one;
      for (int i = 0; i < 2 * n; ++i)
        one = GDDD(i, static_cast<GDDD::val_t>(p[i]), one);
      std::vector<int> bits(n_global_);
      for (int g = 0; g < n_global_; ++g)
        bits[g] = (DDD(one * columns_[g]) == DDD()) ? 0 : 1;
      out.emplace_back(std::vector<int>(p.begin(), p.begin() + n), bits);
    }
    return out;
  }

private:
  void require_profiles() const {
    if (!have_profiles_)
      throw std::logic_error(name_ + ": phase 3 has not been run");
  }
  void require_refined() const {
    if (!refined_)
      throw std::logic_error(name_ + ": phase 4 has not been run");
  }

  // Global state <-> per-block locals, block 0 most significant.
  std::vector<int> digits(int g) const {
    std::vector<int> out(starts_.size());
    for (size_t b = starts_.size(); b-- > 0;) {
      out[b] = g % sizes_[b];
      g /= sizes_[b];
    }
    return out;
  }
  int index(const std::vector<int> &locals) const {
    int g = 0;
    for (size_t b = 0; b < starts_.size(); ++b) g = g * sizes_[b] + locals[b];
    return g;
  }

  std::string name_;
  int n_;
  int n_global_ = 0;
  std::vector<int> starts_;              // first slot of each block
  std::vector<int> sizes_;               // states per block
  std::vector<std::vector<int>> delta_;  // [global state][class] -> global
  its::VarOrder vo_;
  std::unique_ptr<its::GalOrder> go_;
  std::vector<Hom> prof_homs_;  // A_g predicates on the pair space
  DDD pi_;
  std::vector<DDD> columns_;  // S_g, kept
  std::vector<int> seed_;
  std::vector<int> labels_;
  bool have_profiles_ = false;
  bool refined_ = false;
};

}  // namespace sossdd
