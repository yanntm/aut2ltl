// Finding and defect types shared by the phase modules. Findings
// (budget exhaustion) carry their data and are translated to the
// catchable sos_sdd.errors classes at the binding; a LineStopped is an
// internal invariant violation — a defect by definition, translated to
// sos_sdd.errors.StopTheLine and never caught-and-ledgered.

#pragma once

#include <string>
#include <vector>

namespace sossdd {

struct LayerRow {
  int k;
  double card;
  unsigned long long nodes;
};

// Budget exhaustion: carries the phase that was running and the layer
// profile accumulated so far, so a killed run still yields its datum.
struct BudgetExhausted {
  bool is_time;
  int phase;
  std::vector<LayerRow> profile;
};

// An internal invariant violated (squaring vs pairing disagreement, a
// non-functional idempotent-power map, ...).
struct LineStopped {
  std::string what;
};

}  // namespace sossdd
