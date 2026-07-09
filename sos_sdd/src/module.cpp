// pybind11 entry point of the sos_sdd core. The Python-facing surface is
// specified in ../README.md and typed by ../contract.py: coarse-grained
// calls only (build / align / SoS methods) — no per-node traffic crosses
// the binding. Exceptions raised here translate to the classes in
// ../errors.py via the registrations below (wired when the core lands).

#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
  m.doc() = "sos_sdd symbolic engine core (libDDD)";
  m.attr("__version__") = "0.0.0";
  // TODO: bind build(input, config, until_phase) -> SoS
  // TODO: bind align(SoS, SoS) -> SoS
  // TODO: register exception translation onto sos_sdd.errors classes
}
