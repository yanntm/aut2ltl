"""The per-run statistics record and its serialization.

One `RunStats` is emitted per (case, configuration): a flat record of the query
counts by phase, the split / column dimensions, the counterexample sizes, the
equivalence certification, wall time, and the final verdict.

**A CSV row is the only carrier.** `CSV_FIELDS` / `csv_row` write it and
`parse_row` reads it back, so one field order serves the campaign's
`results.csv`, the cluster shards `reap.sh` concatenates, and the row a bounded
child run hands to its parent on stdout.

The field set is spec §7 verbatim.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class RunStats:
    """A single learner run's metrics — spec §7.

    Every field a run did not reach keeps its declared default (``-1`` for a
    count that never ran, ``""`` for an unset tag), so a `BUDGET` / error row
    still serializes with the full column set.
    """

    case_id: str
    config_id: str
    seed: int = 0

    ap_count: int = -1
    ref_classes: int = -1
    learned_classes: int = -1

    n_member_total: int = -1
    n_member_fill: int = -1
    n_member_harvest: int = -1
    n_member_saturation: int = -1
    n_member_pcache: int = -1

    n_equiv: int = -1
    n_splits: int = -1
    n_columns_lin: int = -1
    n_columns_om: int = -1

    n_saturation_checks: int = -1
    n_saturation_escalations: int = -1

    n_classes_initial: int = -1
    stall_class: str = ""            # none | transient | permanent

    # Equivalence queries whose aligned graph failed the functionality guard, so
    # the closure oracle decided them (spec §9 row F10). Each is a counterexample
    # to the factoring conjecture.
    n_guard_firings: int = -1
    # Did the FINAL (certifying) equivalence query fire the guard? On a `SOUND`
    # run it must not: that table is canonical, so its fold is the syntactic
    # morphism (spec §9 row F10, the hard edge).
    guard_fired_final: int = -1

    cex_policy: str = "minimal"      # minimal | first | padded:<k>

    max_cex_stem: int = -1
    max_cex_loop: int = -1
    max_query_word_len: int = -1

    eq_certification: str = ""       # reps | bounded:<B> | exact

    # Associativity of the exported multiplication table (spec §7, row P7/F8):
    # brute-force over class triples on the produced export; "n/a" when no
    # export was produced (refusal, BUDGET, CRASH, OVERSIZE).
    export_associative: str = "n/a"  # true | false | n/a

    # The Lemma 5.2 congruence check on the final table (spec §3.2 step 6):
    # "true" recorded for free on a saturated run (its final sweep ran clean),
    # computed by the check phase on ablation fixpoints, "n/a" when no
    # certified fixpoint was reached (BUDGET, CRASH, OVERSIZE). Gated by rows
    # P9/P10; E2's recount keys on it.
    fixpoint_congruent: str = "n/a"  # true | false | n/a

    wall_seconds: float = -1.0
    verdict: str = ""                # SOUND | FAIL | BUDGET | ACCEPTOR_ONLY | OVERSIZE | CRASH

    detail: str = ""                 # free-text note (error kind, blocking record)

    def to_dict(self) -> Dict[str, Any]:
        """The record as an ordered plain dict (declaration order)."""
        return dataclasses.asdict(self)



CSV_FIELDS: List[str] = [f.name for f in dataclasses.fields(RunStats)]
# `from __future__ import annotations` makes `field.type` the *source string*
# ("int"), never the type object — so the coercion `parse_row` applies is keyed
# by that string.
_FIELD_TYPES: Dict[str, str] = {f.name: str(f.type)
                                for f in dataclasses.fields(RunStats)}


def csv_row(stats: RunStats) -> List[str]:
    """One CSV row (strings) for ``stats``, in `CSV_FIELDS` order."""
    d = stats.to_dict()
    return [_cell(d[name]) for name in CSV_FIELDS]


def _cell(value: Any) -> str:
    """Render a scalar for CSV: floats to 3 decimals, everything else ``str``."""
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def parse_row(row: List[str]) -> RunStats:
    """A `csv_row` read back into a `RunStats` — the inverse of `csv_row`, over
    `CSV_FIELDS` order. Each cell is coerced to its declared field type (a short
    row keeps the remaining defaults), so a row that crossed a process boundary
    reconstructs the record it was written from."""
    out = RunStats(case_id="", config_id="")
    for name, cell in zip(CSV_FIELDS, row):
        declared = _FIELD_TYPES[name]
        if declared == "int":
            value: Any = int(cell)
        elif declared == "float":
            value = float(cell)
        else:
            value = cell
        setattr(out, name, value)
    return out
