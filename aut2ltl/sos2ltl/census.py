"""E1/E2 census side channel — env-gated condition-(A)/(B) layer statistics.

`SOS2LTL_CENSUS`, when set to a path, turns collection on: `census_line`
returns one JSON record per input (its per-layer condition-(A) anchoring widths
and condition-(B) window verdicts, plus prefix-independence and the aperiodicity
flag). A survey run over a census folder can then append these records and yield
the E1/E2 tables as a byproduct, while survey owns the per-input timeout and
process isolation. Unset (the default), `CENSUS` is falsy and the caller skips
the whole thing, leaving the translator untouched.

One record is one line: build it early (before formula synthesis) so the
statistics persist even when the later emit blows the per-input cap. Any failure
inside the build is captured into an `error` field, never propagated — the census
must not turn a faithful translation into a crash.
"""
from __future__ import annotations

import json
import os
from collections import Counter
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from sosl.sos import Invariant

# Env-gated: a path to append records to, or None (collection off). The
# guard is a plain `if CENSUS: print(..., file=CENSUS_FH)` at the call site.
# `CENSUS_FH` is the append handle, opened once (line-buffered so concurrent
# survey subprocesses interleave whole records, never partial lines).
CENSUS = os.environ.get("SOS2LTL_CENSUS")
CENSUS_FH = open(CENSUS, "a", buffering=1) if CENSUS else None


def _layer_record(a: Any, w: Any) -> Dict[str, Any]:
    """The census fields of one layer: its condition-(A) reading (`a`) and its
    condition-(B) reading (`w`), both indexed by the same layer id."""
    kinds: Counter = Counter(
        k.split("(")[0] for k in a.letter_kind.values())  # reset(t) -> reset
    return {
        "size": len(a.layer),
        "a_width": a.width,
        "kinds": dict(kinds),
        "b_status": w.status,
        "b_width": w.width,
        "b_trivial": w.trivial,
    }


def census_line(inv: "Invariant", aperiodic: bool) -> str:
    """A one-line JSON census record of `inv`: the per-layer (A)/(B) statistics
    plus top-level aperiodicity and prefix-independence. Self-contained and
    exception-safe — a build failure yields an `error` record, never a raise."""
    rec: Dict[str, Any] = {"n": inv.n, "aperiodic": aperiodic}
    try:
        from . import anchoring, windows
        from .cayley import build
        from .readoffs import is_prefix_independent

        cay = build(inv)
        anchs = anchoring.analyze(cay)
        wins = windows.analyze(cay)
        rec["prefix_independent"] = is_prefix_independent(inv)
        rec["layers"] = [_layer_record(a, w) for a, w in zip(anchs, wins)]
    except Exception as e:  # a census failure is a datum, not a crash
        rec["error"] = f"{type(e).__name__}: {e}"
    return json.dumps(rec, separators=(",", ":"))
