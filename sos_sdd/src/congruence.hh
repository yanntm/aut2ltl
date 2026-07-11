// Phase 5 — the syntactic congruence, as symbolic partition refinement.
//
// The partition lives on the pair space with the y-block erased to zero
// (a setVarConst sweep), so Phase 3's profile columns — sets of
// (x, x^pi) pairs — project onto the same space as the closure's
// elements and every block is a set {(x, 0...0)}.
//
// Seed (paper Phase 5): split the erased EM1 by
//   ~w    the profile columns (A(g, x) agreement at every global state),
//   ~lin  the residual class of st_x(g) at every global state — a
//         slot-local value selection per residual class, OR-ed over the
//         class's member tuples.
// Refinement: the coarsest fixpoint stable under the letter classes,
// splitting each block by the preimages (per-class REVERSE homs) of
// every block. Right-invariance under the generators suffices; the
// rotation lemma licenses stopping there — no left translations, no
// two-sided contexts.
//
// Code invariant (C6): everything in this path is slot-local — Hom_Basic
// bricks only. This header must never include ExprHom / crossing
// machinery: a Comp-shaped relation inside this fixpoint would break the
// rotation-lemma argument, and the include list is the assertion.

#pragma once

#include <chrono>
#include <string>
#include <vector>

#include "ddd/DDD.h"
#include "ddd/Hom.h"
#include "ddd/Hom_Basic.hh"

#include "findings.hh"
#include "primitives.hh"
#include "slotspace.hh"
#include "stats.hh"

namespace sossdd {

class Congruence {
public:
  // Geometry and Phase 3-4 products: block starts/sizes over the slots,
  // per-global-state residual labels and profile columns, mark_bits for
  // the state part of a slot value. rev_classes are the per-letter-class
  // reverse homomorphisms of the closure.
  Congruence(const std::string &name, const SlotSpace &space,
             const std::vector<int> &mark_bits,
             const std::vector<int> &block_starts,
             const std::vector<int> &block_sizes,
             const std::vector<Hom> &rev_classes)
      : name_(name), n_(space.n_slots()), space_(space),
        mark_bits_(mark_bits), starts_(block_starts), sizes_(block_sizes),
        rev_classes_(rev_classes) {
    Hom erase = GHom::id;
    for (int q = 0; q < n_; ++q) erase = setVarConst(n_ + q, 0) & erase;
    erase_ = erase;
  }

  Congruence(const Congruence &) = delete;
  Congruence &operator=(const Congruence &) = delete;

  // pi: the (x, x^pi) map; columns / labels / locals: Phase 3-4 readings
  // per global state (locals[g] = per-block local states of g).
  void run(Stats &st, const DDD &pi, const std::vector<DDD> &columns,
           const std::vector<int> &labels,
           const std::vector<std::vector<int>> &locals,
           long long node_budget, double time_budget,
           const std::vector<LayerRow> &profile) {
    const auto t0 = std::chrono::steady_clock::now();
    const auto guard = [&](int rounds_so_far) {
      (void)rounds_so_far;
      if (node_budget > 0 &&
          static_cast<long long>(GDDD::statistics()) > node_budget)
        throw BudgetExhausted{false, 5, profile};
      const std::chrono::duration<double> dt =
          std::chrono::steady_clock::now() - t0;
      if (time_budget > 0 && dt.count() > time_budget)
        throw BudgetExhausted{true, 5, profile};
    };

    blocks_ = {DDD(erase_(pi))};

    // ~w: two-way split by every erased profile column.
    {
      Stats::Op op(st, 5, "seed-profiles");
      for (const DDD &col : columns) {
        const DDD in = DDD(erase_(col));
        split_two_way(in);
        guard(0);
      }
      op.rec().add("blocks", static_cast<long long>(blocks_.size()));
    }

    // ~lin: split by the residual class of st_x(g), every global state.
    int n_labels = 0;
    for (int l : labels) n_labels = n_labels > l + 1 ? n_labels : l + 1;
    if (n_labels > 1) {
      Stats::Op op(st, 5, "seed-residuals");
      for (size_t g = 0; g < labels.size(); ++g) {
        for (int c = 0; c < n_labels; ++c) {
          // {x : st_x(g) in residual class c}: OR over member states g'
          // of an AND over blocks of one slot-value selection.
          d3::set<GHom>::type members;
          for (size_t t = 0; t < labels.size(); ++t) {
            if (labels[t] != c) continue;
            Hom sel = GHom::id;
            for (size_t b = 0; b < starts_.size(); ++b) {
              const int slot = starts_[b] + locals[g][b];
              d3::set<GHom>::type vals;
              for (int v = 0; v < space_.doms[slot]; ++v)
                if (v >> mark_bits_[slot] == locals[t][b])
                  vals.insert(varEqState(slot, v));
              sel = GHom::add(vals) & sel;
            }
            members.insert(sel);
          }
          const Hom h = GHom::add(members);
          std::vector<DDD> next;
          for (const DDD &blk : blocks_) {
            const DDD in = DDD(h(blk));
            if (in == DDD() || in == blk) { next.push_back(blk); continue; }
            next.push_back(in);
            next.push_back(blk - in);
          }
          blocks_ = std::move(next);
          guard(0);
        }
      }
      op.rec().add("blocks", static_cast<long long>(blocks_.size()));
    }
    const size_t seed_blocks = blocks_.size();

    // gfp: split by letter-class preimages until a full sweep is stable.
    int rounds = 0;
    for (;;) {
      Stats::Op op(st, 5, "refine-round");
      const size_t before = blocks_.size();
      for (const Hom &rev : rev_classes_) {
        // Preimages of the current blocks, frozen for this class sweep.
        std::vector<DDD> pres;
        pres.reserve(blocks_.size());
        for (const DDD &blk : blocks_) pres.push_back(DDD(rev(blk)));
        for (const DDD &pre : pres) split_two_way(pre);
        guard(rounds);
      }
      ++rounds;
      op.rec().add("round", static_cast<long long>(rounds))
          .add("blocks", static_cast<long long>(blocks_.size()));
      op.close();
      if (blocks_.size() == before) break;
    }
    built_ = true;
    st.emit(Record("phase")
                .add("phase", 5LL)
                .add("seed_blocks", static_cast<long long>(seed_blocks))
                .add("rounds", static_cast<long long>(rounds))
                .add("classes", static_cast<long long>(blocks_.size())));
  }

  // -- readings --------------------------------------------------------
  size_t n_classes() const { require(); return blocks_.size(); }

  // Every ~-class as its explicit x-value tuples — a test/debug reading;
  // Phase 6 consumes the blocks symbolically.
  std::vector<std::vector<std::vector<int>>> classes(size_t limit) const {
    require();
    std::vector<std::vector<std::vector<int>>> out;
    for (const DDD &blk : blocks_) {
      if (model_count(blk) > static_cast<double>(limit))
        throw std::invalid_argument(name_ + ": class larger than the cap");
      std::vector<std::vector<int>> elems;
      const int n = n_;
      callback_t cb = [&elems, n](state_t &path) {
        // Paths run top-down; keep the x half, slot 0 first.
        elems.emplace_back(path.rbegin(), path.rbegin() + n);
      };
      iterate(static_cast<const GDDD &>(blk), &cb);
      out.push_back(std::move(elems));
    }
    return out;
  }

private:
  void require() const {
    if (!built_)
      throw std::logic_error(name_ + ": phase 5 has not been run");
  }

  // Replace every block by its intersection with / difference from `in`.
  void split_two_way(const DDD &in) {
    std::vector<DDD> next;
    next.reserve(blocks_.size());
    for (const DDD &blk : blocks_) {
      const DDD inter = DDD(blk * in);
      if (inter == DDD() || inter == blk) { next.push_back(blk); continue; }
      next.push_back(inter);
      next.push_back(blk - inter);
    }
    blocks_ = std::move(next);
  }

  std::string name_;
  int n_;
  SlotSpace space_;
  std::vector<int> mark_bits_;
  std::vector<int> starts_;
  std::vector<int> sizes_;
  std::vector<Hom> rev_classes_;
  Hom erase_;
  std::vector<DDD> blocks_;  // the partition, on the erased pair space
  bool built_ = false;
};

}  // namespace sossdd
