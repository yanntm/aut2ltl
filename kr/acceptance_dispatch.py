"""
acceptance_dispatch.py — direct hierarchy-class φ per Theorem 2 / construction
-ref §9.3, ORTHOGONAL to the Muller-DNF assembly (reachability.py untouched).

The Muller DNF (`reconstruct_ltl_paper_style`) is the general `Δ₂` form and the
explosive one: it enumerates good config-sets G and, per G, asserts the inf-set
is *exactly* G via ⋀_{C∈G}¬Fin(C) ∧ ⋀_{C∉G}Fin(C). For the simpler acceptance
classes Theorem 2 gives a direct φ that avoids both explosions.

**Büchi** (recurrence, `Π₂`). For a deterministic Büchi cascade, acceptance is
"some accepting config is visited infinitely often", so

    φ_Büchi := ⋁_{C ∈ accepting configs} ¬Fin(C)              (§9.3, Π₂)

— no `Fin(C∉G)` web and no good-set enumeration. Soundness: `¬Fin(C)` ≡
"C ∈ inf-set"; the i.o.-set of a run is strongly connected, so Büchi acceptance
`inf ∩ α ≠ ∅` ≡ `⋁_{C∈α} (C ∈ inf)` ≡ `⋁_{C∈α} ¬Fin(C)` (a transient accepting
C contributes `¬Fin(C) ≡ false`, harmless). Returns None when the cascade is
not Büchi so the caller falls back to the Muller path.

**coBüchi** (persistence, `Σ₂`) is the mirror: acceptance is `Inf(ρ) ∩ Marked =
∅` (the rejecting/marked configs are visited only finitely), so

    φ_coBüchi := ⋀_{C ∈ marked configs} Fin(C)               (§9.3, Σ₂)

— exact (no strongly-connected argument needed; a transient marked C contributes
`Fin(C) ≡ true`, harmless). GATE SUBTLETY: `decompose_aut`'s parity normalization
turns the natural `Fin(0)` into `Inf(0) | Fin(1)`, on which `acc().is_co_buchi()`
is False — so the gate recovers the natural acceptance via
`postprocess(.,"generic")` and tests `is_co_buchi` there (the `postprocess(.,
"coBuchi")` variant is UNSOUND — a recurrence cascade like GFa passes it). Büchi
is tried first, so coBüchi only sees genuinely-not-Büchi cascades.

Probe/verify: kr/testing/probe_buchi_dispatch.py and probe_cobuchi_dispatch.py
(equiv vs original, size A/B, gate). looping/weak are TODO.
"""

from __future__ import annotations
from typing import Optional

import kr.reachability_operators as _ops
from kr.fin import fin_c
from kr.ltl_builders import _And, _Or, _Not, _tt, _ff, _simp_f, _tree_size_f
from kr.cascade import Cascade


def is_buchi_cascade(casc: Cascade) -> bool:
    """True iff the cascade's normalized D carries a plain Büchi condition
    (`Inf(0)`), so the direct Büchi dispatch applies."""
    if casc.num_levels == 0 or casc.original_aut is None:
        return False
    try:
        return bool(casc.original_aut.acc().is_buchi())
    except Exception:
        return False


def is_cobuchi_cascade(casc: Cascade) -> bool:
    """True iff the cascade's language is coBüchi-recognizable (persistence), so
    the direct coBüchi dispatch applies. Tested on the NATURAL acceptance recovered
    via `postprocess(.,"generic")` — NOT on the cascade's parity-normalized
    condition (`Inf(0)|Fin(1)`, on which `is_co_buchi()` is False) and NOT via
    `postprocess(.,"coBuchi")` (unsound: recurrence cascades pass it)."""
    if casc.num_levels == 0 or casc.original_aut is None:
        return False
    try:
        import spot
        gen = spot.postprocess(casc.original_aut, "deterministic", "generic")
        return bool(gen.acc().is_co_buchi())
    except Exception:
        return False


def _reset_ops(casc: Cascade) -> None:
    """Fresh-build reset of the operator counters/memos (mirrors
    reconstruct_ltl_paper_style) so a dispatch build is independent and its
    size counters are accurate."""
    _ops.PAPER_REACH_CALLS = 0
    _ops.PAPER_FIN_CALLS = 0
    _ops.PAPER_MAX_LTL_SIZE = 0
    if hasattr(_ops, "_reach_memo"):
        _ops._reach_memo.clear()
    _ops._clear_casc_registry()
    _ops._register_casc(casc)
    if hasattr(_ops, "_lru_reach_strong"):
        _ops._lru_reach_strong.cache_clear()
    if hasattr(_ops, "_helper_memo"):
        _ops._helper_memo.clear()


def reconstruct_buchi(casc: Cascade) -> Optional["spot.formula"]:
    """Direct Büchi φ = ⋁_{C ∈ accepting configs} ¬Fin(C), or None if the
    cascade is not Büchi.

    α comes from `buchi_accepting_configs()` — the COVER-AWARE reader off the
    pruned config aut — NOT the lift-section `accepting_configs()`: on a genuine
    holonomy cover (duplicated accepting sinks) the lift section returns only one
    config per accepting state and the disjunction then UNDER-approximates
    (witness `F(a & X b)`: lift α={(1,2)} gives L⊊L(orig); cover α={(1,1),(1,2)}
    is exact). A transient accepting config only adds a `¬Fin(C)≡false` disjunct,
    so the (possibly looser) cover set stays sound."""
    if not is_buchi_cascade(casc):
        return None
    _reset_ops(casc)
    acc_cfgs = sorted(casc.buchi_accepting_configs())
    if not acc_cfgs:
        return _ff()    # Büchi with no recurrent accepting config -> empty
    res = _simp_f(_Or(*[_Not(fin_c(c, casc)) for c in acc_cfgs]))
    _ops.PAPER_MAX_LTL_SIZE = _tree_size_f(res)
    return res


def reconstruct_cobuchi(casc: Cascade) -> Optional["spot.formula"]:
    """Direct coBüchi φ = ⋀_{C ∈ marked configs} Fin(C), or None if the cascade
    is not coBüchi (persistence). α = `cobuchi_finite_configs()`, the cover-aware
    "visit finitely" set (dual of the Büchi reader). Empty α (nothing must be
    visited finitely) means every run is accepting -> `true`."""
    if not is_cobuchi_cascade(casc):
        return None
    _reset_ops(casc)
    fin_cfgs = sorted(casc.cobuchi_finite_configs())
    if not fin_cfgs:
        return _tt()    # coBüchi with no marked config -> all runs accept
    res = _simp_f(_And(*[fin_c(c, casc) for c in fin_cfgs]))
    _ops.PAPER_MAX_LTL_SIZE = _tree_size_f(res)
    return res


__all__ = ["is_buchi_cascade", "reconstruct_buchi",
           "is_cobuchi_cascade", "reconstruct_cobuchi"]
