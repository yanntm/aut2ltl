"""The per-run statistics record (`stats.json`) and its serializations.

One `RunStats` is emitted per (case, configuration): a flat record of the query
counts by phase, the split / column dimensions, the counterexample sizes, the
equivalence certification, wall time, and the final verdict. The driver writes
one JSON file per run and concatenates the records into a single CSV (one row
per run) via `CSV_FIELDS` / `csv_row`.

The field set is spec §7 verbatim; the three fields added in revision 2026-07-07b
(`n_classes_initial`, `stall_class`, `cex_policy`) are present. `to_dict` /
`CSV_FIELDS` share one field order so the JSON keys and the CSV columns never
drift apart.
"""
from __future__ import annotations

import dataclasses
import json
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

    wall_seconds: float = -1.0
    verdict: str = ""                # SOUND | FAIL | BUDGET | ACCEPTOR_ONLY | OVERSIZE | CRASH

    detail: str = ""                 # free-text note (error kind, blocking record)

    def to_dict(self) -> Dict[str, Any]:
        """The record as an ordered plain dict (declaration order)."""
        return dataclasses.asdict(self)

    def write_json(self, path: str) -> None:
        """Write the record as a one-object JSON file (stable key order)."""
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=2, sort_keys=False)
            fh.write("\n")


CSV_FIELDS: List[str] = [f.name for f in dataclasses.fields(RunStats)]


def csv_row(stats: RunStats) -> List[str]:
    """One CSV row (strings) for ``stats``, in `CSV_FIELDS` order."""
    d = stats.to_dict()
    return [_cell(d[name]) for name in CSV_FIELDS]


def _cell(value: Any) -> str:
    """Render a scalar for CSV: floats to 3 decimals, everything else ``str``."""
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def load_json(path: str) -> RunStats:
    """Read a `stats.json` back into a `RunStats` (missing keys keep defaults)."""
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    known = {f.name for f in dataclasses.fields(RunStats)}
    return RunStats(**{k: v for k, v in raw.items() if k in known})
