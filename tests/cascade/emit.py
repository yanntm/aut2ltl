"""K-E4: the config normal-form emitter (Prop C.7 / Cor C.8), DAG-only.

Formulas are `spot.formula` objects — spot hash-conses, so shared subterms stay
shared (a DAG); nothing is ever flattened to a string here (the caller
translates the formula object directly for the conformance gate). Atoms `A_e`
follow the K-E4 grammar; `omega` assembles Cor C.8's one-sided / exact-set form
plus the park disjuncts.
"""
from __future__ import annotations

from functools import reduce
from typing import Dict, FrozenSet, List, Tuple

import spot

from aut2ltl.sos2ltl.anchoring import LayerAnchoring, analyze_layer
from aut2ltl.sos2ltl.cayley import Cayley
from sosl.sos import Invariant

from tests.cascade.config_machine import Edge, concrete_letters, quotient_letters

TT = spot.formula.tt()
FF = spot.formula.ff()


def _cube(inv: Invariant, mask: int) -> spot.formula:
    """The concrete letter `mask` as a conjunction of AP literals."""
    lits = []
    trues = set(inv.alphabet.true_aps(mask))
    for p in inv.alphabet.aps:
        ap = spot.formula.ap(p)
        lits.append(ap if p in trues else spot.formula.Not(ap))
    return spot.formula.And(lits) if lits else TT


def letterset(inv: Invariant, masks) -> spot.formula:
    """The Boolean formula of a set of concrete letter masks (a λ-preimage):
    `⋁_mask cube(mask)`. Empty ⟹ ff."""
    ms = sorted(set(masks))
    if not ms:
        return FF
    return spot.formula.Or([_cube(inv, m) for m in ms])


def _Xn(f: spot.formula, n: int) -> spot.formula:
    for _ in range(n):
        f = spot.formula.X(f)
    return f


def qletter_masks(inv: Invariant, d: int):
    """Concrete masks of quotient letter `d`."""
    return concrete_letters(inv)[d]


def pin(anc: LayerAnchoring, inv: Invariant, m: Tuple[int, ...]):
    """`pin(m)` (K-E4): fold the buffer's quotient letters; return `('CONST', t)`
    if some letter is a within-layer constant (last such wins, identities after
    fix it), else `('ID', None)`."""
    state = ("ID", None)
    for d in m:
        kind = anc.letter_kind.get(qletter_masks(inv, d)[0], "neutral")
        if kind.startswith("reset("):
            t = int(kind[len("reset("):-1])
            state = ("CONST", t)
        # neutral (identity) leaves state unchanged
    return state


def atom(inv: Invariant, anc: LayerAnchoring, e: Edge, k: int) -> spot.formula:
    """`A_e` for edge `e=((q,m),a)`, `|m|=k` (K-E4 grammar). DAG node."""
    (q, m), a = e
    ahat = letterset(inv, qletter_masks(inv, a))                 # â
    # m̂ = ⋀_i X^{i-1}(letter-set of m_i)
    mhat_terms = [_Xn(letterset(inv, qletter_masks(inv, m[i])), i)
                  for i in range(len(m))]
    mhat = spot.formula.And(mhat_terms) if mhat_terms else TT
    core = spot.formula.And([mhat, _Xn(ahat, k)])                # m̂ ∧ X^k â
    p, t = pin(anc, inv, m)
    if p == "CONST":
        assert t == q, (e, t, q)                                 # unreachable else
        return core
    st_q = letterset(inv, anc.stutter[q])                        # St(q)
    an_q = letterset(inv, anc.anchors[q])                        # An(q)
    return spot.formula.And([an_q, spot.formula.X(spot.formula.U(st_q, core))])


def _GF(f: spot.formula) -> spot.formula:
    return spot.formula.G(spot.formula.F(f))


def source_classes(F: FrozenSet[Edge]) -> FrozenSet[int]:
    return frozenset(q for (q, _m), _a in F)


def park_verdict(inv: Invariant, anc: LayerAnchoring, d: int) -> str:
    """The parked-at-`d` verdict on the frozen restriction `({d}, St(d))`:
    'accept' / 'reject' if every St(d)-loop idempotent agrees, else 'mixed'
    (then Ω_d needs the Prop 5.4 window emitter — flagged, not built here)."""
    st_masks = anc.stutter[d]
    if not st_masks:
        return "reject"
    # loop classes reachable by St(d) letters, from the identity
    reach = {inv.identity}
    frontier = [inv.identity]
    while frontier:
        c = frontier.pop()
        for a in st_masks:
            n = inv.mult[c][inv.letter_class[a]]
            if n not in reach:
                reach.add(n)
                frontier.append(n)
    verdicts = set()
    for c in reach:
        if c == inv.identity:
            continue
        e = inv.idempotent_power(c)
        verdicts.add((inv.mult[d][e], e) in inv.accept)
    if verdicts == {True}:
        return "accept"
    if verdicts == {False} or not verdicts:
        return "reject"
    return "mixed"


def omega(inv: Invariant, anc: LayerAnchoring, R: FrozenSet[int], k: int,
          accepting_multi: List[FrozenSet[Edge]],
          minimal: List[FrozenSet[Edge]]) -> Tuple[spot.formula, List[int]]:
    """Assemble `Ω(R,·)` (Cor C.8 upward-closed rec-form + parks), DAG-only.
    `accepting_multi`/`minimal` are the ≥2-class accepted F and its minimal
    elements (from the decider). Returns the formula and the list of classes
    whose park verdict is 'mixed' (Ω_d unbuilt — a caveat, not a failure)."""
    disj: List[spot.formula] = []
    # rec form: ⋁_{S minimal accepted, ≥2 classes} ⋀_{e∈S} GF A_e
    for S in minimal:
        disj.append(spot.formula.And([_GF(atom(inv, anc, e, k)) for e in S]))
    # parks: accepting parked classes d get F(An(d) ∧ X G St(d)) and the entry
    # park G St(d); Ω_d = ⊤ when the frozen restriction is uniformly accepting.
    mixed: List[int] = []
    for d in sorted(R):
        pv = park_verdict(inv, anc, d)
        if pv == "mixed":
            mixed.append(d)
        if pv == "accept":
            an_d = letterset(inv, anc.anchors[d])
            st_d = letterset(inv, anc.stutter[d])
            g_st = spot.formula.G(st_d)
            disj.append(spot.formula.F(
                spot.formula.And([an_d, spot.formula.X(g_st)])))
            disj.append(g_st)                       # entry park
    return (spot.formula.Or(disj) if disj else FF), mixed

