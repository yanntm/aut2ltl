// pybind11 entry point of the sos_sdd core. The Python-facing surface is
// specified in ../README.md and typed by ../contract.py: coarse-grained
// calls only — no per-node traffic crosses the binding.
//
// Currently exposed: selftest(stats), which exercises the primitive layer
// and the instrumentation hooks on a toy slot space — set algebra and
// comparison, model counts, single-variable relational apply, and the
// layered-vs-saturation fixpoint disciplines cross-checked for equality.

#include <fstream>
#include <memory>
#include <string>

#include <pybind11/pybind11.h>

#include "ddd/DDD.h"
#include "ddd/Hom.h"

#include "primitives.hh"
#include "stats.hh"

namespace py = pybind11;

namespace {

using namespace sossdd;

// stats argument: None (disabled), a path (JSONL file), or a Python
// callable receiving each record as a str.
Stats make_stats(const py::object &stats) {
  if (stats.is_none()) return Stats();
  if (py::isinstance<py::str>(stats)) {
    auto out = std::make_shared<std::ofstream>(stats.cast<std::string>());
    return Stats(
        [out](const std::string &line) {
          *out << line << '\n';
          out->flush();
        },
        /*gc_per_op=*/true);
  }
  py::function fn = stats.cast<py::function>();
  return Stats([fn](const std::string &line) { fn(line); }, /*gc_per_op=*/true);
}

py::dict selftest(const py::object &stats_obj) {
  Stats st = make_stats(stats_obj);
  st.emit(Record("config").add("selftest", true));

  constexpr int kVars = 3;
  constexpr GDDD::val_t kDom = 5;

  // Diagonal set A = { (i, i, i) : i < kDom }, built bottom-up.
  DDD A;
  {
    Stats::Op op = st.op(0, "build-A");
    GDDD a = GDDD::null;
    for (GDDD::val_t i = 0; i < kDom; ++i) {
      GDDD path = GDDD::one;
      for (int v = kVars - 1; v >= 0; --v) path = GDDD(v, i, path);
      a = a + path;
    }
    A = a;
    op.rec().add("nodes_final", node_count(A));
  }

  // Set algebra + O(1) comparison sanity.
  DDD B = DDD(A) + GDDD(0, 0, GDDD(1, 1, GDDD(2, 2)));
  bool algebra_ok = (A * B == A) && (B - A != GDDD::null) && ((B - A) + A == B);

  // Single-variable relation on the top variable: src i -> dst (i+1)%kDom,
  // as the strictly-2-level diagram apply2k expects.
  GDDD rel = GDDD::null;
  for (GDDD::val_t i = 0; i < kDom; ++i)
    rel = rel + GDDD(0, i, GDDD(0, static_cast<GDDD::val_t>((i + 1) % kDom)));
  GHom step = apply2k(rel);

  // Layered fixpoint from a single seed, rounds counted and reported.
  DDD seed(GDDD(0, 0, GDDD(1, 0, GDDD(2, 0))));
  DDD layered(seed);
  long long rounds = 0;
  {
    Stats::Op op = st.op(1, "layered-closure");
    for (;;) {
      Stats::Op round_op = st.op(1, "closure-step");
      GDDD next = layered + step(layered);
      ++rounds;
      round_op.rec()
          .add("round", rounds)
          .add("card", model_count(next))
          .add("nodes", node_count(next));
      round_op.close();
      if (next == layered) break;
      layered = next;
    }
    op.rec().add("rounds", rounds).add("nodes_final", node_count(layered));
  }

  // Saturation-style discipline on the same seed; must agree exactly.
  DDD saturated;
  {
    Stats::Op op = st.op(1, "saturation-closure");
    saturated = fixpoint(step + GHom::id)(seed);
    op.rec().add("nodes_final", node_count(saturated));
  }
  bool disciplines_agree = (saturated == layered);

  collect();
  st.emit(Record("verdict")
              .add("status", "OK")
              .add("card_A", model_count(A))
              .add("table_peak", static_cast<unsigned long long>(GDDD::peak())));

  py::dict res;
  res["card_A"] = model_count(A);
  res["nodes_A"] = node_count(A);
  res["algebra_ok"] = algebra_ok;
  res["card_closure"] = model_count(layered);
  res["rounds"] = rounds;
  res["disciplines_agree"] = disciplines_agree;
  res["table_peak"] = static_cast<unsigned long long>(GDDD::peak());
  return res;
}

}  // namespace

PYBIND11_MODULE(_core, m) {
  m.doc() = "sos_sdd symbolic engine core (libDDD)";
  m.attr("__version__") = "0.0.1";
  m.def("selftest", &selftest, py::arg("stats") = py::none(),
        "Exercise the primitive layer and instrumentation hooks (C1).");
  // TODO: bind build(input, config, until_phase) -> SoS
  // TODO: bind align(SoS, SoS) -> SoS
  // TODO: register exception translation onto sos_sdd.errors classes
}
