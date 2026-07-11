"""Loop half — the acceptance term off the scoped acceptor's decomposition.

Where (C) fails at every affordable width on a final-candidate layer (or
(A) fails on one), the verdict on confined tails cannot be read off the
invariant's walk (paper §6, the floor). This module consumes what [BLS22]
consumed: the deterministic acceptor, tail-restricted by
`machine.scoped_acceptor`, KR-decomposed through the gap bridge, its
acceptance lifted to cascade configurations and encoded as a Boolean
combination of `Fin(C)` — the existing bls acceptance-dispatch ladder
(acc → weak → buchi → cobuchi → muller), unchanged. The emitted label
defines `T_c ∩ confined` from the class's entry; it serves as `W(R)` /
`Ω(R, c)` inside `STAY∞`'s confinement context, which masks the sink's
verdict. Exactness is NOT by construction on this branch — the
conformance gate is the only correctness authority; a gate failure is
stop-the-line (theory adjudicates).

DAG-only: the label is a hash-consed `spot.formula`; nothing here
stringifies.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from aut2ltl.bls.cascade import CascadeHolder
from aut2ltl.bls.gap import decompose_aut
from aut2ltl.bls.hierarchy_class import hierarchy_class

from .machine import ScopedAcceptor, SeamRecord, scoped_acceptor

from .. import cayley as _cayley

if TYPE_CHECKING:
    import spot


class LoopDecline(Exception):
    """The scoped decomposition or the member chain could not produce a
    label (a resource cap, a GAP failure) — a decline, never a verdict."""


@dataclass(frozen=True)
class LoopEmission:
    """The acceptance label for one layer class, with its ledger row."""

    formula: "spot.formula"
    technique: str                # winning member of the dispatch ladder
    cls: int                      # the layer class the label is rooted at
    record: SeamRecord


def loop_acceptance(cay: "_cayley.Cayley", layer_id: int,
                    aut_d: "spot.twa_graph", cls: Optional[int] = None, *,
                    gap_cmd: str = "gap", timeout: int = 60) -> LoopEmission:
    """Emit the confined-tail acceptance label of `layer_id`, rooted at layer
    class `cls` (default: the least class with an entry). `aut_d` is the
    language's deterministic state-based acceptor
    (`Language.det_parity_sbacc()`) — the presentation this branch, alone in
    the extraction, consults."""
    scoped: ScopedAcceptor = scoped_acceptor(cay, layer_id, aut_d)
    if not scoped.entries:
        raise LoopDecline(f"layer {layer_id}: no reachable tail state")
    if cls is None:
        cls = min(scoped.entries)
    if cls not in scoped.entries:
        raise LoopDecline(f"layer {layer_id}: class {cls} has no entry")
    scoped.aut.set_init_state(scoped.entries[cls])

    t0 = time.monotonic()
    try:
        casc = decompose_aut(scoped.aut, gap_cmd=gap_cmd, timeout=timeout)
    except Exception as e:
        raise LoopDecline(f"decomposition failed: {e}") from e
    wall = time.monotonic() - t0

    holder = CascadeHolder(casc)
    res = hierarchy_class(holder)
    if not res.ok:
        raise LoopDecline(f"member chain declined: {res.diagnosis}")

    record = SeamRecord(
        n_states=scoped.aut.num_states(), height=casc.num_levels,
        level_sizes=tuple(lv.size for lv in casc.levels),
        n_configs=len(casc.all_configs()), wall_s=wall)
    return LoopEmission(formula=res.formula, technique=res.technique_str(),
                        cls=cls, record=record)
