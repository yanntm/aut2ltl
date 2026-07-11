"""Stem half — Prop 4.14 with the cascade extractor (paper §6, stem half).

On a layer anchored at no affordable width, the scoped fallback's inner
extractor is swapped from DG-on-`𝒜_R` to the holonomy cascade of the
totalized within-layer machine (`machine.stem_cascade`). The exit
disjunction is emitted directly through the [BLS22] reach family: the
family's continuation parameter `τ` is Prop 4.14's insertion point, so no
standalone finite-word formula is ever materialized —

    θ_c   =  ⋁_{d}  ( guard(exit letters c → d)  ∧  X Final(d) )
    ρ_c   =  ⋁_{C covering c}  reach(ι_R, ∅, ⊥, C, θ_c)
    label =  ⋁_{c : E(c) ≠ ∅}  ρ_c            (⋁ over the layer's classes)

Being at a config covering `c` means "not yet exited" (the sink is
absorbing), so an exit letter firing there is the unique first exit and at
most one disjunct fires — Prop 4.14's proof verbatim. On a final-candidate
layer the assembly gains the confined arm: `(SAFE ∧ Ω) ∨ ⋁ ρ_c`, with `Ω`
supplied by the loop half (`Ω = None` asserts the preflight: a run cannot
stay in the layer forever).

Exact by construction (gated anyway, like every branch); the E11 ledger
prices it against DG-on-`𝒜_R`. DAG-only: hash-consed `spot.formula`
throughout, the family's per-holder memos carried by the `StemCascade`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Optional, TYPE_CHECKING

from aut2ltl.bls.operators.reach import reach
from aut2ltl.ltl.builders import _And, _Not, _Or, _X, _ff, _simp_f

from .machine import StemCascade, SeamRecord, covering_configs, stem_cascade

from .. import anchoring as _anchoring
from .. import cayley as _cayley
from ..guards import Guards

if TYPE_CHECKING:
    import spot


@dataclass(frozen=True)
class StemEmission:
    """The layer's label rooted at its entry class, with the ledger row."""

    formula: "spot.formula"
    entry: int
    record: SeamRecord


def stem_label(cay: "_cayley.Cayley", layer_id: int,
               anch: "_anchoring.LayerAnchoring", entry: int,
               children: Mapping[int, "spot.formula"], guards: Guards,
               omega: Optional["spot.formula"] = None, *,
               sc: Optional[StemCascade] = None,
               gap_cmd: str = "gap", timeout: int = 60) -> StemEmission:
    """Emit `Final(entry)` for the (A)-failing layer `layer_id` through the
    cascade extractor. `children` maps every exit target class `d` (strictly
    below in the R-order) to its memoized label `Final(d)`; `omega` is the
    loop half's confined-tail term on a final-candidate layer, None on a
    transient one (asserted: no exit-free class may exist then). A prebuilt
    `sc` shares one decomposition (and its reach memos) across the layer's
    entry classes."""
    if sc is None:
        sc = stem_cascade(cay, layer_id, gap_cmd=gap_cmd, timeout=timeout)
    holder = sc.holder
    iota = holder.config_of(sc.class_state[entry])

    exit_disjuncts = []
    for c in cay.layers[layer_id]:
        exits = anch.exits.get(c, ())
        if not exits:
            if omega is None:
                raise AssertionError(
                    f"layer {layer_id}: class {c} has no exit and no omega "
                    "(final-candidate layer needs the loop half)")
            continue
        fan: Dict[int, list] = {}
        for a in exits:
            fan.setdefault(cay.step(c, a), []).append(a)
        theta = _Or(*[_And(guards.render(letters), _X(children[d]))
                      for d, letters in sorted(fan.items())])
        for cfg in covering_configs(holder, sc.class_state[c]):
            exit_disjuncts.append(
                reach(iota, None, _ff(), cfg, theta, holder))

    label = _Or(*exit_disjuncts) if exit_disjuncts else _ff()
    if omega is not None:
        safe_targets = []
        for c in cay.layers[layer_id]:
            exits = anch.exits.get(c, ())
            if not exits:
                continue
            exit_guard = guards.render(exits)
            for cfg in covering_configs(holder, sc.class_state[c]):
                safe_targets.append(
                    reach(iota, None, _ff(), cfg, exit_guard, holder))
        safe = _Not(_Or(*safe_targets)) if safe_targets else None
        label = _Or(_And(safe, omega) if safe is not None else omega, label)
    return StemEmission(formula=_simp_f(label), entry=entry, record=sc.record)
