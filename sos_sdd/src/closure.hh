// Phase 1: the letter-class homomorphisms (right multiplication) and the
// layered closure of EM1 from the identity element, layers kept — they
// are the length half of shortlex keying and the extraction path.
//
// A letter class acts on each slot as a total function on its values,
// given extensionally (`maps[slot][v] = w` — the packing that produced
// the values is the Python side's business). Per slot it is a sum over
// values of Hom_Basic bricks (setVarConst & varEqState), composed
// commutatively across slots (all slots step together; the factors touch
// disjoint variables). The full step is the union over classes; the
// alphabet itself never appears.

#pragma once

#include <chrono>
#include <memory>
#include <string>
#include <utility>
#include <vector>

#include "ddd/DDD.h"
#include "ddd/Hom.h"
#include "ddd/Hom_Basic.hh"

#include "congruence.hh"
#include "crossing.hh"
#include "findings.hh"
#include "primitives.hh"
#include "residuals.hh"
#include "slotspace.hh"
#include "squaring.hh"
#include "stats.hh"

namespace sossdd {

class SoSCore {
public:
  SoSCore(std::string name, SlotSpace space,
          const std::vector<LetterClassRow> &classes)
      : name_(std::move(name)), space_(std::move(space)), classes_(classes) {
    space_.check(name_);
    for (const auto &c : classes_)
      check_class(c);
    d3::set<GHom>::type step_parts;
    d3::set<GHom>::type rev_parts;
    for (const auto &c : classes_) {
      d3::set<GHom>::type slots;
      d3::set<GHom>::type rev_slots;
      for (int i = 0; i < space_.n_slots(); ++i) {
        const int x = space_.var_of[i];
        d3::set<GHom>::type cases;
        d3::set<GHom>::type rev_cases;
        for (int v = 0; v < space_.doms[i]; ++v) {
          const int w = c.maps[i][v];
          cases.insert(setVarConst(x, w) & varEqState(x, v));
          // The reverse relation is multi-valued (a value may have many
          // preimages); the same brick shape handles it as a union.
          rev_cases.insert(setVarConst(x, v) & varEqState(x, w));
        }
        slots.insert(GHom::add(cases));
        rev_slots.insert(GHom::add(rev_cases));
      }
      Hom h = GHom::ccompose(slots);
      class_homs_.push_back(h);
      step_parts.insert(h);
      Hom rev = GHom::ccompose(rev_slots);
      rev_class_homs_.push_back(rev);
      rev_parts.insert(rev);
    }
    step_ = GHom::add(step_parts);
    rev_step_ = GHom::add(rev_parts);
    identity_ = DDD(space_.identity());
  }

  // Layered BFS from the identity: layer k holds the elements first
  // reached by words of length k (frontier-driven — every length-(k+1)
  // word extends a length-k word, so stepping the frontier suffices).
  void close(Stats &st, long long node_budget, double time_budget) {
    const auto t0 = std::chrono::steady_clock::now();
    DDD current = identity_;
    DDD frontier = identity_;
    layers_ = {frontier};
    profile_ = {{0, 1.0, node_count(identity_)}};
    st.emit(Record("layer").add("k", 0LL).add("card", 1.0)
                .add("nodes", node_count(identity_)));
    int k = 0;
    for (;;) {
      Stats::Op op(st, 1, "closure-step");
      DDD next = DDD(step_(frontier)) - current;
      ++k;
      op.rec().add("round", static_cast<long long>(k))
          .add("card", model_count(next))
          .add("nodes", node_count(next));
      op.close();
      if (next == DDD()) break;
      current = current + next;
      frontier = next;
      layers_.push_back(next);
      profile_.push_back({k, model_count(next), node_count(next)});
      st.emit(Record("layer").add("k", static_cast<long long>(k))
                  .add("card", model_count(next)).add("nodes", node_count(next)));
      if (node_budget > 0 &&
          static_cast<long long>(GDDD::statistics()) > node_budget)
        throw BudgetExhausted{false, 1, profile_};
      const std::chrono::duration<double> dt =
          std::chrono::steady_clock::now() - t0;
      if (time_budget > 0 && dt.count() > time_budget)
        throw BudgetExhausted{true, 1, profile_};
    }
    em1_ = current;
    depth_ = k - 1;
    built_ = true;
    close_secs_ =
        std::chrono::duration<double>(std::chrono::steady_clock::now() - t0)
            .count();
    st.emit(Record("phase").add("phase", 1LL)
                .add("rounds", static_cast<long long>(k))
                .add("em1", model_count(em1_))
                .add("depth", static_cast<long long>(depth_))
                .add("nodes_final", node_count(em1_)));
  }

  // Phase 2: build the crossing on the doubled slot space and compute the
  // idempotent-power map pi — by the general pairing, the squaring
  // shortcut, or both compared (the `square` mode; the shortcut design is
  // recorded in ../README.md). A wall budget spans the whole build, so
  // only the remainder after the closure is granted here.
  void cross(Stats &st, const PackInfo &pack, long long node_budget,
             double time_budget, const std::string &square) {
    require();
    const auto t0 = std::chrono::steady_clock::now();
    double remaining = 0.0;
    if (time_budget > 0) {
      remaining = time_budget - close_secs_;
      if (remaining <= 0) throw BudgetExhausted{true, 2, profile_};
    }
    cross_ = std::make_shared<Crossing>(name_, space_, pack, em1_);
    if (square != "on")
      cross_->run(st, model_count(em1_), node_budget, remaining, profile_);
    if (square != "off") {
      sq_ = std::make_shared<Squaring>(name_, space_, pack);
      sq_->build_rel(st, em1_);
      const bool conv = sq_->run(st, cross_->diag(), model_count(em1_),
                                 node_budget, remaining, profile_);
      if (square == "check") {
        // Converged: one O(1) comparison; disagreement is a defect.
        // Diverged: the expected outcome on non-power-of-two orbit
        // periods — a recorded finding, the pairing's pi stands.
        if (conv && !(sq_->pi() == cross_->pi()))
          throw LineStopped{name_ +
                            ": squaring and pairing disagree on pi (C4)"};
        st.emit(Record("op").add("phase", 2LL).add("op", "square-outcome")
                    .add("mode", square).add("converged", conv)
                    .add("rounds", static_cast<long long>(sq_->rounds())));
      } else {  // "on" — shortcut trusted
        if (!conv)
          throw LineStopped{name_ + ": square=on but the shortcut did not "
                            "converge (an orbit period is not a power of "
                            "two); use square=check or off"};
        cross_->adopt_pi(st, sq_->pi(), model_count(em1_), sq_->rounds());
      }
    }
    cross_secs_ =
        std::chrono::duration<double>(std::chrono::steady_clock::now() - t0)
            .count();
  }

  // A derived core sharing the acceptance-free table (Phases 0-2:
  // letter homs, EM1 + layers, the crossing's pi) with this one, its
  // Acc-dependent phases (3-5) unrun — the same-table calculus (§6.2)
  // re-runs them under a different accept table. Sharing is by
  // refcount (DDD/Hom) and shared_ptr (the crossing); nothing is
  // recomputed or copied deeply.
  SoSCore fork(const std::string &name) const {
    require();
    SoSCore c(*this);
    if (!name.empty()) c.name_ = name;
    c.resid_.reset();
    c.cong_.reset();
    c.resid_secs_ = 0.0;
    return c;
  }

  // Phases 3-4: the profile columns on pi's pair space, then (when
  // until_phase reaches 4) the residual refinement on the global states.
  // Write-once: a core carries at most one accept table — fork() first
  // to derive under another one.
  void residuate(Stats &st, const PackInfo &pack,
                 const std::vector<std::vector<int>> &accept,
                 long long node_budget, double time_budget, int until_phase) {
    if (resid_)
      throw std::logic_error(name_ + ": phase 3 already run — fork() to "
                             "derive under another accept table");
    double remaining = 0.0;
    if (time_budget > 0) {
      remaining = time_budget - close_secs_ - cross_secs_;
      if (remaining <= 0) throw BudgetExhausted{true, 3, profile_};
    }
    const auto t0 = std::chrono::steady_clock::now();
    resid_ = std::make_shared<Residuals>(name_, space_, pack, accept, classes_);
    resid_->profiles(st, crossing().pi(), node_budget, remaining, profile_);
    if (until_phase >= 4) resid_->refine(st);
    resid_secs_ =
        std::chrono::duration<double>(std::chrono::steady_clock::now() - t0)
            .count();
  }

  // Phase 5: the syntactic congruence — partition refinement on the
  // erased pair space, seeded by the Phase 3-4 products, refined by the
  // per-class reverse letter homs (slot-local only; no Comp).
  void congruence(Stats &st, const PackInfo &pack, long long node_budget,
                  double time_budget) {
    if (cong_)
      throw std::logic_error(name_ + ": phase 5 already run — fork() to "
                             "derive under another accept table");
    double remaining = 0.0;
    if (time_budget > 0) {
      remaining = time_budget - close_secs_ - cross_secs_ - resid_secs_;
      if (remaining <= 0) throw BudgetExhausted{true, 5, profile_};
    }
    const Residuals &r = residuals();
    std::vector<std::vector<int>> locals;
    for (int g = 0; g < r.n_states(); ++g) locals.push_back(r.locals_of(g));
    cong_ = std::make_shared<Congruence>(name_, space_, pack.mark_bits,
                                         r.block_starts(), r.block_sizes(),
                                         rev_class_homs_);
    cong_->run(st, crossing().pi(), r.columns(), r.state_labels(), locals,
               node_budget, remaining, profile_);
  }

  // -- shortlex extraction (the C7 mechanism, reused by witnesses) ----
  // The minimal layer gives the length; a backward preimage pass builds
  // the can-still-reach sets; a forward walk chooses at each step the
  // least class whose (deterministic) image stays inside the next set.
  // A backward letter choice would minimize the wrong end (reverse-lex).
  std::vector<int> shortlex_of(const std::vector<int> &elem) const {
    require();
    DDD target = singleton(elem);
    int k = -1;
    for (size_t j = 0; j < layers_.size(); ++j)
      if (!(DDD(target * layers_[j]) == DDD())) { k = static_cast<int>(j); break; }
    if (k < 0)
      throw std::invalid_argument(name_ + ": element is not in EM1");
    std::vector<DDD> reach(static_cast<size_t>(k) + 1);
    reach[k] = target;
    for (int j = k; j > 0; --j)
      reach[j - 1] = DDD(rev_step_(reach[j]));
    std::vector<int> word;
    std::vector<int> cur = space_.identity_vals;
    for (int j = 0; j < k; ++j) {
      bool advanced = false;
      for (size_t c = 0; c < classes_.size(); ++c) {
        std::vector<int> nxt(cur.size());
        for (size_t i = 0; i < cur.size(); ++i)
          nxt[i] = classes_[c].maps[i][cur[i]];
        if (!(DDD(singleton(nxt) * reach[j + 1]) == DDD())) {
          word.push_back(static_cast<int>(c));
          cur = std::move(nxt);
          advanced = true;
          break;
        }
      }
      if (!advanced)
        throw std::logic_error(name_ + ": extraction walk stuck (bug)");
    }
    return word;
  }

  const std::vector<LetterClassRow> &classes() const { return classes_; }

  // Explicit enumeration of EM1 (raw slot values, natural order) — a
  // test/debug reading; symbolic consumers never enumerate.
  std::vector<std::vector<int>> elements(size_t limit) const {
    require();
    if (em1_count() > static_cast<double>(limit))
      throw std::invalid_argument(name_ + ": EM1 larger than the explicit cap");
    // Paths run top-down; reversed they are variable order, un-permuted
    // back to slot order for the reading.
    std::vector<std::vector<int>> elems;
    const SlotSpace &sp = space_;
    callback_t cb = [&elems, &sp](state_t &path) {
      elems.push_back(sp.unpermute({path.rbegin(), path.rend()}));
    };
    iterate(static_cast<const GDDD &>(em1_), &cb);
    return elems;
  }

  // Every element with its shortlex word (test/debug reading —
  // quotient-time extraction is per-representative).
  std::vector<std::pair<std::vector<int>, std::vector<int>>>
  shortlex_words(size_t limit) const {
    std::vector<std::pair<std::vector<int>, std::vector<int>>> out;
    for (const auto &e : elements(limit))
      out.emplace_back(e, shortlex_of(e));
    return out;
  }

  // -- phase 2 readings ----------------------------------------------
  double pi_count() const { return crossing().pi_count(); }
  unsigned long long pi_nodes() const { return crossing().pi_nodes(); }
  std::vector<std::pair<std::vector<int>, std::vector<int>>>
  pi_pairs(size_t limit) const { return crossing().pi_pairs(limit); }

  // Explicit (z, z·z) rows of the squaring relation R — a test/debug
  // reading; raises when no squaring mode ran.
  std::vector<std::pair<std::vector<int>, std::vector<int>>>
  square_rel_pairs(size_t limit) const {
    if (!sq_)
      throw std::logic_error(name_ + ": squaring has not been run");
    return sq_->rel_pairs(limit);
  }

  // -- phase 3-4 readings ----------------------------------------------
  int n_states() const { return residuals().n_states(); }
  std::vector<std::vector<int>> residual_classes() const {
    return residuals().classes();
  }
  std::vector<std::pair<std::vector<int>, std::vector<int>>>
  profile_rows(size_t limit) const { return residuals().profile_rows(limit); }

  // -- phase 5 readings ------------------------------------------------
  size_t congruence_count() const { return cong().n_classes(); }
  std::vector<std::vector<std::vector<int>>>
  congruence_classes(size_t limit) const { return cong().classes(limit); }

  // -- readings ------------------------------------------------------
  const std::string &name() const { return name_; }
  double em1_count() const { require(); return model_count(em1_); }
  int depth() const { require(); return depth_; }
  const std::vector<LayerRow> &profile() const { require(); return profile_; }
  std::pair<unsigned long long, unsigned long long> nodes() const {
    require();
    const auto live = static_cast<unsigned long long>(GDDD::statistics());
    const auto peak = static_cast<unsigned long long>(GDDD::peak());
    return {node_count(em1_), peak > live ? peak : live};
  }

private:
  void require() const {
    if (!built_)
      throw std::logic_error(name_ + ": phase 1 has not been run");
  }

  const Crossing &crossing() const {
    if (!cross_)
      throw std::logic_error(name_ + ": phase 2 has not been run");
    return *cross_;
  }

  const Residuals &residuals() const {
    if (!resid_)
      throw std::logic_error(name_ + ": phase 3 has not been run");
    return *resid_;
  }

  const Congruence &cong() const {
    if (!cong_)
      throw std::logic_error(name_ + ": phase 5 has not been run");
    return *cong_;
  }

  void check_class(const LetterClassRow &c) const {
    if (static_cast<int>(c.maps.size()) != space_.n_slots())
      throw std::invalid_argument(name_ + ": class " + c.least +
                                  " has wrong slot count");
    for (int i = 0; i < space_.n_slots(); ++i) {
      if (static_cast<int>(c.maps[i].size()) != space_.doms[i])
        throw std::invalid_argument(name_ + ": class " + c.least +
                                    " map size mismatch at slot " +
                                    std::to_string(i));
      for (int w : c.maps[i])
        if (w < 0 || w >= space_.doms[i])
          throw std::invalid_argument(name_ + ": class " + c.least +
                                      " maps outside the domain");
    }
  }

  DDD singleton(const std::vector<int> &elem) const {
    return DDD(space_.path(elem));
  }

  std::string name_;
  SlotSpace space_;
  std::vector<LetterClassRow> classes_;
  std::vector<Hom> class_homs_;
  std::vector<Hom> rev_class_homs_;
  Hom step_;
  Hom rev_step_;
  DDD identity_;
  DDD em1_;
  std::vector<DDD> layers_;
  std::vector<LayerRow> profile_;
  std::shared_ptr<Crossing> cross_;
  std::shared_ptr<Squaring> sq_;
  std::shared_ptr<Residuals> resid_;
  std::shared_ptr<Congruence> cong_;
  int depth_ = -1;
  double close_secs_ = 0.0;
  double cross_secs_ = 0.0;
  double resid_secs_ = 0.0;
  bool built_ = false;
};

}  // namespace sossdd
