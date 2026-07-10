"""
aut2ltl/printer.py — human-browsable trace renderers for a Translator's input and
output.

Two formatters used by the per-translator `if _TRACE:` traces (see e.g.
`daisy2`/`daisystar`): `format_language` renders the *concrete twa a translator
pulled* from its input `Language` (the representation actually in play, not an
abstract language), and `format_result` renders the `LTLResult` it returns. Both
are plain string builders — the CALLER prints — so nothing here runs unless the
translator's guard already fired; the load-bearing rule (never build a trace string
unless it will be printed) is enforced at the call site, not here.

Verbosity is the printer's OWN control (`AUT2LTL_TRACE_VERBOSITY`), independent of
the on/off `TRANSLATOR_TRACE_ON` gate the translators read:
  stats (default) — id + automaton size / formula metrics.
  full            — additionally dump each distinct input twa's HOA to a browsable
                    file (`AUT2LTL_TRACE_DIR`, default `logs/trace/`, deduped by
                    `Language.id`) and cite the path, and show a NOT_LTL witness.

Core-level: it knows `Language` / `LTLResult` (typing-only) and reuses the leaf
`ltl` metric/printer helpers (core -> leaf, the sound direction).
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

import spot

from aut2ltl.ltl.metrics import dag_metrics
from aut2ltl.ltl.printers import format_gated

if TYPE_CHECKING:
    from aut2ltl.language import Language
    from aut2ltl.result import LTLResult


# Where level-2 HOA dumps go (created on demand); browse it after a traced run.
_TRACE_DIR = os.getenv("AUT2LTL_TRACE_DIR", "logs/trace")

# Flatten gate for the formula rendered in a result trace: a large reconstruction
# prints the placeholder (its dag/tree metrics carry the size anyway), keeping the
# human log readable. An O(DAG) probe — never an unbounded flatten.
_FLATTEN_LIMIT = int(os.getenv("AUT2LTL_TRACE_FLATTEN_LIMIT", "400"))


def _full() -> bool:
    """True at max verbosity — the printer's own `AUT2LTL_TRACE_VERBOSITY` control,
    independent of the on/off trace gate. At `full`/`hoa` the input twa's HOA is
    dumped to a browsable file; otherwise only stats are rendered."""
    return os.getenv("AUT2LTL_TRACE_VERBOSITY", "stats").strip().lower() in ("full", "hoa")


def _dump_hoa(lang: "Language", aut: "spot.twa_graph") -> str:
    """Write `aut` to `<AUT2LTL_TRACE_DIR>/<lang.id>.hoa` (once — the id dedupes a
    re-presented language to a single file) and return the path. The one
    side-effecting step, reached only at level 2."""
    os.makedirs(_TRACE_DIR, exist_ok=True)
    path = os.path.join(_TRACE_DIR, f"{lang.id}.hoa")
    if not os.path.exists(path):
        from aut2ltl.ltl.twa import dump_hoa
        with open(path, "w") as fh:
            fh.write(dump_hoa(aut))
    return path


def format_language(lang: "Language", aut: "spot.twa_graph") -> str:
    """One-line summary of the *twa the translator pulled* (`aut`), tagged with its
    `Language.id`: states / edges / atomic propositions / acceptance sets and
    determinism. At level 2, also dump the full HOA to a browsable file and cite it.
    All metrics are O(automaton); no language operation is triggered here."""
    parts = [
        f"id={lang.id}",
        f"states={aut.num_states()}",
        f"edges={aut.num_edges()}",
        f"ap={len(aut.ap())}",
        f"acc={aut.acc().num_sets()}[{aut.acc()}]",
        f"det={'yes' if spot.is_deterministic(aut) else 'no'}",
    ]
    if _full():
        parts.append(f"hoa={_dump_hoa(lang, aut)}")
    return " ".join(parts)


def format_result(res: "LTLResult") -> str:
    """One-line summary of an `LTLResult`: status + contributing techniques, then on
    OK the size metrics (dag / temporal / tree / sharing) and the gated formula text
    (a placeholder when too large to flatten); on a NOK the diagnosis (and, at level
    2, a NOT_LTL witness)."""
    head = f"{res.status.value} [{res.technique_str()}]"
    if res.ok and res.formula is not None:
        m = dag_metrics(res.formula)
        text = format_gated(res.formula, limit=_FLATTEN_LIMIT)
        return (f"{head} dag={m.dag_nodes} temporal={m.temporal_nodes} "
                f"tree={m.tree_nodes} sharing={m.sharing:.1f}x  {text}")
    tail = f"  {res.diagnosis}" if res.diagnosis else ""
    if _full() and res.witness is not None:
        tail += f"  witness={res.witness}"
    return head + tail


__all__ = ["format_language", "format_result"]
