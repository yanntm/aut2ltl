// pybind11 entry point of the sos_sdd core. The Python-facing surface is
// specified in ../README.md and typed by ../contract.py: coarse-grained
// calls only — no per-node traffic crosses the binding.
//
// Currently exposed: selftest(stats), which exercises the primitive layer
// and the instrumentation hooks on a toy slot space — set algebra and
// comparison, model counts, single-variable relational apply, and the
// layered-vs-saturation fixpoint disciplines cross-checked for equality;
// build(payload, config, until_phase) running phases 0..4 (closure; the
// crossing / idempotent-power map; profiles and the residual refinement)
// on a numeric digest payload.

#include <fstream>
#include <memory>
#include <string>
#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "ddd/DDD.h"
#include "ddd/Hom.h"

#include "closure.hh"
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
    return Stats([out](const std::string &line) {
      *out << line << '\n';
      out->flush();
    });
  }
  py::function fn = stats.cast<py::function>();
  return Stats([fn](const std::string &line) { fn(line); });
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
  DDD rel;
  for (GDDD::val_t i = 0; i < kDom; ++i)
    rel = rel + GDDD(0, i, GDDD(0, static_cast<GDDD::val_t>((i + 1) % kDom)));
  Hom step = apply2k(rel);

  // Layered fixpoint from a single seed, rounds counted and reported.
  DDD seed(GDDD(0, 0, GDDD(1, 0, GDDD(2, 0))));
  DDD layered(seed);
  long long rounds = 0;
  {
    Stats::Op op = st.op(1, "layered-closure");
    for (;;) {
      Stats::Op round_op = st.op(1, "closure-step");
      DDD next = layered + step(layered);
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

[[noreturn]] void not_implemented(const std::string &msg) {
  PyErr_SetString(PyExc_NotImplementedError, msg.c_str());
  throw py::error_already_set();
}

// The engine consumes the switches it implements and refuses the rest
// loudly — switches are contract, silent ignoring would fake a sweep.
void check_config(const py::dict &config) {
  const auto want = [&](const char *key, const char *only) {
    if (config.contains(key)) {
      const auto v = py::cast<std::string>(py::str(config[key]));
      if (v != only)
        not_implemented(std::string(key) + "=" + v + " (only " + only +
                        " is implemented)");
    }
  };
  want("slot_perm", "natural");
  want("slot_encoding", "packed");
  want("alpha", "top");
  want("fp1", "layered");
  want("fp5", "layered");
}

SoSCore build(const py::dict &payload, const py::dict &config,
              int until_phase) {
  if (until_phase < 1 || until_phase > 5)
    not_implemented("until_phase=" + std::to_string(until_phase) +
                    " (only phases 1..5 are implemented)");
  check_config(config);

  SlotSpace space{py::cast<std::vector<int>>(payload["doms"]),
                  py::cast<std::vector<int>>(payload["identity"])};
  std::vector<LetterClassRow> classes;
  for (const auto &item : payload["classes"]) {
    const auto d = py::cast<py::dict>(item);
    LetterClassRow row;
    row.least = py::cast<std::string>(d["least"]);
    row.count = py::cast<long long>(d["count"]);
    row.maps = py::cast<std::vector<std::vector<int>>>(d["maps"]);
    classes.push_back(std::move(row));
  }

  SoSCore core(py::cast<std::string>(payload["name"]), space, classes);
  const py::object stats_obj = config.contains("stats")
                                   ? py::object(config["stats"])
                                   : py::object(py::none());
  Stats st = make_stats(stats_obj);
  st.emit(Record("config").add("name", core.name())
              .add("until_phase", static_cast<long long>(until_phase)));
  const long long node_budget =
      config.contains("node_budget") ? py::cast<long long>(config["node_budget"]) : 0;
  const double time_budget =
      config.contains("time_budget") ? py::cast<double>(config["time_budget"]) : 0.0;
  core.close(st, node_budget, time_budget);
  if (until_phase >= 2) {
    // The squaring shortcut is deferred (pending a 2k-variable relation
    // encoding of the simultaneous step); only the general pairing runs.
    const std::string square =
        config.contains("square") ? py::cast<std::string>(config["square"])
                                  : "off";
    if (square != "off")
      not_implemented("square=" + square +
                      " (squaring shortcut deferred; only off is implemented)");
    PackInfo pack{py::cast<std::vector<int>>(payload["mark_bits"]),
                  py::cast<std::vector<int>>(payload["block_base"])};
    core.cross(st, pack, node_budget, time_budget);
    if (until_phase >= 3) {
      const auto accept =
          py::cast<std::vector<std::vector<int>>>(payload["accept"]);
      core.residuate(st, pack, accept, node_budget, time_budget, until_phase);
    }
    if (until_phase >= 5)
      core.congruence(st, pack, node_budget, time_budget);
  }
  return core;
}

py::list profile_to_py(const std::vector<LayerRow> &profile) {
  py::list rows;
  for (const auto &r : profile)
    rows.append(py::make_tuple(r.k, r.card, r.nodes));
  return rows;
}

}  // namespace

PYBIND11_MODULE(_core, m) {
  m.doc() = "sos_sdd symbolic engine core (libDDD)";
  m.attr("__version__") = "0.0.1";

  m.def("selftest", &selftest, py::arg("stats") = py::none(),
        "Exercise the primitive layer and instrumentation hooks (C1).");

  py::class_<SoSCore>(m, "SoS")
      .def_property_readonly("name", &SoSCore::name)
      .def("em1_count", &SoSCore::em1_count)
      .def("pi_count", &SoSCore::pi_count)
      .def("pi_nodes", &SoSCore::pi_nodes)
      .def(
          "pi_pairs",
          [](const SoSCore &s, size_t limit) {
            py::list out;
            for (const auto &[x, y] : s.pi_pairs(limit))
              out.append(py::make_tuple(py::tuple(py::cast(x)),
                                        py::tuple(py::cast(y))));
            return out;
          },
          py::arg("limit") = 100000,
          "Every (x, x^pi) pair as raw slot values (test/debug reading).")
      .def("n_states", &SoSCore::n_states,
           "Global automaton states (mixed-radix over the component "
           "blocks, block 0 most significant).")
      .def(
          "residual_classes",
          [](const SoSCore &s) {
            py::list out;
            for (const auto &cls : s.residual_classes())
              out.append(py::tuple(py::cast(cls)));
            return out;
          },
          "The residual partition: global state ids grouped by language "
          "equality, classes ordered by least member.")
      .def(
          "profile_rows",
          [](const SoSCore &s, size_t limit) {
            py::list out;
            for (const auto &[x, bits] : s.profile_rows(limit))
              out.append(py::make_tuple(py::tuple(py::cast(x)),
                                        py::tuple(py::cast(bits))));
            return out;
          },
          py::arg("limit") = 100000,
          "Every element with its loop-verdict bits A(q, x) per global "
          "state (test/debug reading).")
      .def("congruence_count", &SoSCore::congruence_count,
           "Number of syntactic-congruence classes of EM1.")
      .def(
          "congruence_classes",
          [](const SoSCore &s, size_t limit) {
            py::list out;
            for (const auto &cls : s.congruence_classes(limit)) {
              py::list elems;
              for (const auto &e : cls) elems.append(py::tuple(py::cast(e)));
              out.append(elems);
            }
            return out;
          },
          py::arg("limit") = 100000,
          "Every ~-class as explicit element tuples (test/debug reading).")
      .def_property_readonly("depth", &SoSCore::depth)
      .def_property_readonly(
          "layers", [](const SoSCore &s) { return profile_to_py(s.profile()); })
      .def_property_readonly("nodes", [](const SoSCore &s) {
        const auto n = s.nodes();
        return py::make_tuple(n.first, n.second);
      })
      .def(
          "elements",
          [](const SoSCore &s, size_t limit) {
            py::list out;
            for (const auto &e : s.elements(limit))
              out.append(py::tuple(py::cast(e)));
            return out;
          },
          py::arg("limit") = 100000,
          "Every EM1 element as raw slot values (test/debug reading).")
      .def(
          "shortlex_words",
          [](const SoSCore &s, size_t limit) {
            // Elements as raw slot-value tuples (the caller owns the
            // packing); words as the least letter of each class.
            py::list out;
            const auto &classes = s.classes();
            for (const auto &[elem, word] : s.shortlex_words(limit)) {
              py::list letters;
              for (int c : word)
                letters.append(classes[static_cast<size_t>(c)].least);
              out.append(py::make_tuple(py::tuple(py::cast(elem)),
                                        py::tuple(letters)));
            }
            return out;
          },
          py::arg("limit") = 100000,
          "Every EM1 element with its shortlex word (test/debug reading).");

  m.def("build", &build, py::arg("payload"), py::arg("config"),
        py::arg("until_phase"),
        "Run phases 0..until_phase on a numeric digest payload.");

  // Budget findings surface as the Python-side Finding classes; invariant
  // violations as StopTheLine (a defect, never caught-and-ledgered).
  py::register_exception_translator([](std::exception_ptr p) {
    try {
      if (p) std::rethrow_exception(p);
    } catch (const BudgetExhausted &e) {
      const py::object cls =
          py::module_::import("sos_sdd.errors")
              .attr(e.is_time ? "TimeBudget" : "DiagramBudget");
      py::list profile;
      for (const auto &r : e.profile)
        profile.append(py::make_tuple(r.k, r.card, r.nodes));
      PyErr_SetObject(cls.ptr(), cls(e.phase, profile).ptr());
    } catch (const LineStopped &e) {
      const py::object cls =
          py::module_::import("sos_sdd.errors").attr("StopTheLine");
      PyErr_SetObject(cls.ptr(), cls(e.what).ptr());
    }
  });
}
