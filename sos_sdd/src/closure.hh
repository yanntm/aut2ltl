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
#include <string>
#include <utility>
#include <vector>

#include "ddd/DDD.h"
#include "ddd/Hom.h"
#include "ddd/Hom_Basic.hh"

#include "primitives.hh"
#include "slotspace.hh"
#include "stats.hh"

namespace sossdd {

struct LetterClassRow {
  std::string least;                   // lex-least letter of the class
  long long count = 0;                 // number of letters in the class
  std::vector<std::vector<int>> maps;  // per slot: value -> value
};

struct LayerRow {
  int k;
  double card;
  unsigned long long nodes;
};

// Budget exhaustion findings (translated to sos_sdd.errors classes at the
// binding); they carry the layer profile accumulated so far.
struct BudgetExhausted {
  bool is_time;
  int phase;
  std::vector<LayerRow> profile;
};

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
        d3::set<GHom>::type cases;
        d3::set<GHom>::type rev_cases;
        for (int v = 0; v < space_.doms[i]; ++v) {
          const int w = c.maps[i][v];
          cases.insert(setVarConst(i, w) & varEqState(i, v));
          // The reverse relation is multi-valued (a value may have many
          // preimages); the same brick shape handles it as a union.
          rev_cases.insert(setVarConst(i, v) & varEqState(i, w));
        }
        slots.insert(GHom::add(cases));
        rev_slots.insert(GHom::add(rev_cases));
      }
      Hom h = GHom::ccompose(slots);
      class_homs_.push_back(h);
      step_parts.insert(h);
      rev_parts.insert(GHom::ccompose(rev_slots));
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
    st.emit(Record("phase").add("phase", 1LL)
                .add("rounds", static_cast<long long>(k))
                .add("em1", model_count(em1_))
                .add("depth", static_cast<long long>(depth_))
                .add("nodes_final", node_count(em1_)));
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
    std::vector<std::vector<int>> elems;
    callback_t cb = [&elems](state_t &path) {
      elems.emplace_back(path.begin(), path.end());
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
    GDDD d = GDDD::one;
    for (int i = space_.n_slots() - 1; i >= 0; --i)
      d = GDDD(i, static_cast<GDDD::val_t>(elem[i]), d);
    return DDD(d);
  }

  std::string name_;
  SlotSpace space_;
  std::vector<LetterClassRow> classes_;
  std::vector<Hom> class_homs_;
  Hom step_;
  Hom rev_step_;
  DDD identity_;
  DDD em1_;
  std::vector<DDD> layers_;
  std::vector<LayerRow> profile_;
  int depth_ = -1;
  bool built_ = false;
};

}  // namespace sossdd
