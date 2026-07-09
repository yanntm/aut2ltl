// Phase 1: the letter-class homomorphisms (right multiplication) and the
// layered closure of EM1 from the identity element, layers kept — they
// are the length half of shortlex keying and the extraction path.
//
// A letter class acts on one slot as a total function on packed values:
//   (q', S) -> (dst[q'], S | marks[q'])
// realized as a sum over values of Hom_Basic bricks
// (setVarConst & varEqState), composed commutatively across slots (all
// slots step together; the factors touch disjoint variables). The full
// step is the union over classes; the alphabet itself never appears.

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
  std::string least;        // lex-least letter of the class (a cube string)
  long long count = 0;      // number of letters in the class
  std::vector<int> dst;     // per-state destination
  std::vector<int> marks;   // per-state mark mask
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
      : name_(std::move(name)), space_(space) {
    space_.check(name_);
    d3::set<GHom>::type step_parts;
    for (const auto &c : classes) {
      d3::set<GHom>::type slots;
      for (int i = 0; i < space_.n_states; ++i) {
        d3::set<GHom>::type cases;
        for (int v = 0; v < space_.dom(); ++v) {
          const int q = space_.state_of(v);
          const int w = space_.pack(c.dst[q], space_.marks_of(v) | c.marks[q]);
          cases.insert(setVarConst(i, w) & varEqState(i, v));
        }
        slots.insert(GHom::add(cases));
      }
      Hom h = GHom::ccompose(slots);
      class_homs_.push_back(h);
      step_parts.insert(h);
    }
    step_ = GHom::add(step_parts);
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

  std::string name_;
  SlotSpace space_;
  std::vector<Hom> class_homs_;
  Hom step_;
  DDD identity_;
  DDD em1_;
  std::vector<DDD> layers_;
  std::vector<LayerRow> profile_;
  int depth_ = -1;
  bool built_ = false;
};

}  // namespace sossdd
