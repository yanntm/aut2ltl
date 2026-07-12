"""The ladder tests: per-rung existence of a member inside the given-that
interval, with canonical members and refusal certificates.

Every rung is one instance of paper Lemma 4.1: an intersection-closed family
(a Moore family) is decided by its closure operator on `P_min`
(`rho(P_min) <= P_max`, least member `rho(P_min)`); a union-closed family by
its kernel on `P_max` (greatest member the kernel). The hulls per rung:
safety closure / interior (CAL5), the R-class forcing of obligations, the
recurrence Horn hull, and — for persistence — one complement flip of the
recurrence test (paper Prop 4.4).

The chain read-offs: a language is a *recurrence* (`GF` shape) iff no
linked stem `s` carries loops `f <=_H e` with `Val(s,e) = 1` and
`Val(s,f) = 0` — verdicts propagate down the H-order — and a *persistence*
(`FG` shape) iff the mirror holds. The H-order on idempotents is
`classify.primitives`' (`idempotents` / `leq_h_idem` — one implementation
in the repo); the decision path here is a direct violation scan, distinct
from the chain DP `classify.chains` runs over the same order, and the
corpus rung oracle holds the two paths to the same verdicts. `rec_hull` is
the matching closure operator: the Horn rule "(s,e) in Q, f <=_H e, f a
loop of s => (s,f) in Q" alternated with `saturate` to the joint least
fixpoint (the Horn rule alone does not produce a language — spec trap #10).

All pair sets here are assumed saturated (they denote languages); see
`algorithm.md` §5 for the ideas and the witness convention (on no, the
refusal `Witness` is the first pair pushed past the constraining endpoint,
in the key discipline order, as its canonical lasso).
"""
from __future__ import annotations

from typing import Dict, FrozenSet, List, Optional, Set, Tuple

from ..calculus.surgery import (
    complement,
    interior,
    is_cosafety,
    is_obligation,
    is_safety,
    is_saturated,
    r_classes,
    safety_closure,
    saturate,
)
from ..calculus.table import PairSet, Table
from ..calculus.witness import Witness
from ..classify.primitives import idempotents, leq_h_idem
from .interval import Interval

RungAnswer = Tuple[bool, Optional[PairSet], Optional[Witness]]
"""One rung verdict: `(exists, canonical member, refusal)` — the member is
the least one on Moore rungs (safety, obligation, recurrence), the greatest
on kernel rungs (co-safety, persistence); exactly one of the last two is
`None`."""


def h_below(table: Table) -> Dict[int, FrozenSet[int]]:
    """For every non-identity idempotent `e`, the non-identity idempotents
    `f <=_H e` (reflexive) — the ladder-shaped view of `classify.primitives`'
    H-order (`leq_h_idem`, the one-line `f.e == e.f == f` test). `O(|E|^2)`,
    cheap enough to compute per call."""
    inv = table.algebra
    idems = idempotents(inv)
    return {e: frozenset(f for f in idems if leq_h_idem(inv, f, e))
            for e in idems}


def _loops_by_stem(table: Table, pairs: PairSet) -> Dict[int, Tuple[Set[int], Set[int]]]:
    """Per linked stem, its loops split by verdict: `(ones, zeros)` where
    `e` is in `ones` iff `(s, e)` is in `pairs`."""
    split: Dict[int, Tuple[Set[int], Set[int]]] = {}
    for s, e in table.linked:
        ones, zeros = split.setdefault(s, (set(), set()))
        (ones if (s, e) in pairs else zeros).add(e)
    return split


def is_recurrence(table: Table, pairs: PairSet) -> bool:
    """The chain condition `m+ <= 0`: no linked stem `s` with loops
    `f <=_H e`, `Val(s,e) = 1`, `Val(s,f) = 0`. `pairs` must be saturated."""
    below = h_below(table)
    for ones, zeros in _loops_by_stem(table, pairs).values():
        for e in ones:
            if not below[e].isdisjoint(zeros):
                return False
    return True


def is_persistence(table: Table, pairs: PairSet) -> bool:
    """The mirror chain condition `m- <= 0`: no linked stem `s` with loops
    `f <=_H e`, `Val(s,e) = 0`, `Val(s,f) = 1`. `pairs` must be saturated."""
    below = h_below(table)
    for ones, zeros in _loops_by_stem(table, pairs).values():
        for e in zeros:
            if not below[e].isdisjoint(ones):
                return False
    return True


def _refusal(table: Table, overflow: PairSet, expected: bool,
             operation: str) -> Witness:
    """The refusal certificate: the first cell of the normative scan order
    whose linked pair lies in `overflow`, as its canonical lasso — globally
    minimal over all lassos certifying the refusal (calculus Prop W; every
    overflow pair is its own cell, so the scan terminates). `expected` is the
    bit the lasso carries against the endpoint the rung is constrained by
    (`False` against `L(P_max)` on Moore rungs, `True` against `L(P_min)` on
    kernel rungs)."""
    assert overflow, "refusal asked with an empty overflow"
    mult = table.mult
    for c, d in table.cells():
        e = table.idem(d)
        if (mult[c][e], e) in overflow:
            return Witness(alphabet=table.alphabet, stem=table.keys[c],
                           loop=table.keys[d], expected=expected,
                           operation=operation, cell=(c, d))
    raise AssertionError("overflow pairs unreachable by the cell scan")


def rec_hull(table: Table, q: PairSet) -> PairSet:
    """The least superset of `q` closed under both the recurrence Horn rule

        (s, e) in Q,  f <=_H e,  (s, f) linked   =>   (s, f) in Q

    and conjugacy saturation — the closure operator of the recurrence rungs
    (`ρ` of paper Lemma 4.1 for the chain-condition family). Alternates the
    rule with `saturate` until stable; at most `|linked|` rounds since each
    round grows the set. `q` must be saturated."""
    below = h_below(table)
    linked = table.linked
    out: Set[Tuple[int, int]] = set(q)
    while True:
        added: List[Tuple[int, int]] = []
        for s, e in out:
            for f in below[e]:
                if (s, f) in linked and (s, f) not in out:
                    added.append((s, f))
        if not added:
            return frozenset(out)
        out.update(added)
        out = set(saturate(table, frozenset(out)))


def rung_of(table: Table, pairs: PairSet) -> str:
    """The Manna-Pnueli class of `L(pairs)`, lowest rung first: `clopen`,
    `guarantee`, `safety`, `obligation`, `recurrence`, `persistence`,
    `reactivity`. A pure read-off composition of the rung predicates — the one
    output-metric helper GT2 takes (spec §4). `pairs` must be saturated."""
    if is_safety(table, pairs) and is_cosafety(table, pairs):
        return "clopen"
    if is_cosafety(table, pairs):
        return "guarantee"
    if is_safety(table, pairs):
        return "safety"
    if is_obligation(table, pairs):
        return "obligation"
    rec, per = is_recurrence(table, pairs), is_persistence(table, pairs)
    if rec and per:
        return "obligation"
    if rec:
        return "recurrence"
    if per:
        return "persistence"
    return "reactivity"


# --- the rung existence tests (paper Props 4.2-4.4) --------------------------


def exists_safety(iv: Interval) -> RungAnswer:
    """Is there a safety `B` in the interval? `safety_closure(P_min) <= P_max`
    (paper Prop 4.2); on yes the closure is the least member among ALL
    omega-regular safety languages, not merely on-table ones."""
    hull = safety_closure(iv.table, iv.p_min)
    if hull <= iv.p_max:
        return True, hull, None
    return False, None, _refusal(iv.table, hull - iv.p_max, False, "exists_safety")


def exists_cosafety(iv: Interval) -> RungAnswer:
    """Is there a co-safety `B` in the interval? `P_min <= interior(P_max)`
    (paper Prop 4.2 dual); on yes the interior is the greatest member."""
    kernel = interior(iv.table, iv.p_max)
    if iv.p_min <= kernel:
        return True, kernel, None
    return False, None, _refusal(iv.table, iv.p_min - kernel, True, "exists_cosafety")


def forced(iv: Interval) -> Tuple[FrozenSet[FrozenSet[int]], FrozenSet[FrozenSet[int]]]:
    """The R-classes the interval constrains (paper Prop 4.3): forced to 1 —
    containing a stem of `P_min`; forced to 0 — containing a stem of a linked
    pair outside `P_max`. One pass each over `r_classes(table)`; each R-class
    is its frozen stem set."""
    classes = r_classes(iv.table)
    stems_min = {s for (s, e) in iv.p_min}
    stems_out = {s for (s, e) in iv.table.linked - iv.p_max}
    forced1 = frozenset(r for r in classes if not r.isdisjoint(stems_min))
    forced0 = frozenset(r for r in classes if not r.isdisjoint(stems_out))
    return forced1, forced0


def exists_obligation(iv: Interval) -> RungAnswer:
    """Is there an obligation `B` in the interval? Exists iff no R-class is
    forced both ways (paper Prop 4.3); least member theta = forced-1 exactly,
    greatest theta = not-forced-0 — both asserted saturated, in the interval,
    and `is_obligation` (CAL5)."""
    forced1, forced0 = forced(iv)
    linked = iv.table.linked
    stems1 = frozenset().union(*forced1) if forced1 else frozenset()
    least = frozenset(p for p in linked if p[0] in stems1)
    if forced1 & forced0:
        return False, None, _refusal(iv.table, least - iv.p_max, False,
                                     "exists_obligation")
    stems0 = frozenset().union(*forced0) if forced0 else frozenset()
    greatest = frozenset(p for p in linked if p[0] not in stems0)
    for name, member in (("least", least), ("greatest", greatest)):
        assert is_saturated(iv.table, member), f"obligation {name} not saturated"
        assert iv.p_min <= member <= iv.p_max, f"obligation {name} left the interval"
        assert is_obligation(iv.table, member), f"obligation {name} fails is_obligation"
    return True, least, None


def exists_recurrence(iv: Interval) -> RungAnswer:
    """Is there a recurrence (`GF` shape) `B` in the interval?
    `rec_hull(P_min) <= P_max` (paper Prop 4.4); on yes the hull is the least
    on-table member."""
    hull = rec_hull(iv.table, iv.p_min)
    assert is_recurrence(iv.table, hull), "rec_hull output fails is_recurrence"
    if hull <= iv.p_max:
        return True, hull, None
    return False, None, _refusal(iv.table, hull - iv.p_max, False,
                                 "exists_recurrence")


def exists_persistence(iv: Interval) -> RungAnswer:
    """Is there a persistence (`FG` shape) `B` in the interval? One complement
    flip of the recurrence test (paper Prop 4.4): `B` is a persistence in
    `[P_min, P_max]` iff `B^c` is a recurrence in `[P_max^c, P_min^c]`. On yes
    the greatest member is `rec_hull(P_max^c)^c`."""
    hull = rec_hull(iv.table, complement(iv.table, iv.p_max))
    if hull.isdisjoint(iv.p_min):
        greatest = complement(iv.table, hull)
        assert is_persistence(iv.table, greatest), \
            "persistence greatest fails is_persistence"
        return True, greatest, None
    return False, None, _refusal(iv.table, hull & iv.p_min, True,
                                 "exists_persistence")
