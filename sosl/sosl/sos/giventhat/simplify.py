"""The operation: `simplify( I(neg_phi), I(K) ) -> I(B)`, the greedy driver.

Given the interval (GT1) and the bounded quotient engine (GT3), pick a *smaller*
legal `B`: two `.sos` in, one `.sos` out with `L(B) & L(K) = L(neg_phi) & L(K)`
([DPT25] Thm 1) and `|C(B)|` no worse than any of the three reference points
(`neg_phi`, `P_min`, `P_max`). It is the algebraic double of [DPT25]'s
Bounded-by-Minato: they pick a simpler Boolean *label*, we pick a smaller
*table*.

The engine is a greedy over congruences. From each admissible seed
(`pi_{neg_phi}`, the identity, optionally the stutter congruence) it merges two
blocks at a time — in the *current* quotient, composing the maps (trap #9) —
keeping every merge whose `admits` test still passes, until none does; then it
reads off the least and greatest recognized members. The global answer is the
class-count `argmin` over all recorded members and the three reference points,
so the never-regress contract holds by construction.

**Honesty (spec §6):** exact minimization is conjectured NP-hard; this is a
heuristic with an exact test inside it. The output is `|C|` *achieved*, never
*minimal* (trap #15) — nothing here claims otherwise.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from ..calculus import reduce
from ..calculus.surgery import intersection, r_classes, safety_closure
from ..calculus.table import PairSet, Table
from ..calculus.witness import Witness
from ..invariant import Invariant
from .interval import Interval, k_refutes_phi, k_settles_phi
from .ladder import rec_hull, rung_of
from .quotient import (
    Quotient,
    admits,
    compose,
    congruence,
    greatest_member,
    hull,
    least_member,
    syntactic_congruence,
)
from .stutter import exists_stutter_invariant, stutter_seeds

Closure = Callable[[Table, PairSet], PairSet]


@dataclass(frozen=True)
class Options:
    """Knobs for `simplify`. `stutter` adds the stutter congruence as a third
    seed; `require` constrains every candidate to one Manna-Pnueli rung via the
    joint closure of paper Lemma 5.2 (Moore rungs only — see `_rung_closure`)."""

    stutter: bool = True
    require: Optional[str] = None


@dataclass(frozen=True)
class Simplification:
    """The outcome. On SETTLED / REFUTED the model-checking question is answered
    and there is no `B` (the minimal witness lasso is the certificate); on
    SIMPLIFIED, `invariant = reduce(b)` is what gets dumped."""

    verdict: str                       # "SETTLED" | "REFUTED" | "SIMPLIFIED"
    witness: Optional[Witness] = None
    b: Optional[PairSet] = None
    invariant: Optional[Invariant] = None
    side: Optional[str] = None         # "relax" | "restrict" | "reference"
    seed: Optional[str] = None         # "syntactic" | "identity" | "stutter"
    bits: int = 0
    classes: Dict[str, int] = field(default_factory=dict)
    rung: Tuple[str, str] = ("", "")
    stutter: Tuple[bool, bool] = (False, False)
    stutter_verdict: str = ""


# --- constrained mode (paper Lemma 5.2) ------------------------------------


def _obligation_closure(table: Table, pairs: PairSet) -> PairSet:
    """The least obligation superset of `pairs`: turn on every linked pair whose
    stem shares an R-class with a stem of `pairs` (the ladder's least-obligation
    member, as a table closure operator)."""
    stems = {s for (s, e) in pairs}
    forced1 = {s for r in r_classes(table) if not r.isdisjoint(stems) for s in r}
    return frozenset(p for p in table.linked if p[0] in forced1)


def _rung_closure(require: Optional[str], table: Table) -> Optional[Closure]:
    """The table closure operator for a required rung, or `None` when
    unconstrained. Only the Moore (grow-from-`P_min`) rungs are wired — the
    kernel rungs (`cosafety`, `persistence`) need the dual and are refused."""
    if require is None:
        return None
    if require == "safety":
        return safety_closure
    if require == "obligation":
        return _obligation_closure
    if require == "recurrence":
        return rec_hull
    if require == "stutter":
        from .stutter import sc
        return sc
    raise NotImplementedError(
        f"--require {require}: only safety / obligation / recurrence / stutter "
        f"are wired (kernel rungs need the dual closure; spec §6.5)")


def _least(quot: Quotient, iv: Interval, closure: Optional[Closure]) -> PairSet:
    """The least member recognized by `quot` and (if `closure` is set) on the
    required rung — the joint least fixpoint of `hull` alternated with `closure`
    (paper Lemma 5.2). Both operators are extensive and monotone, so the
    ascending iteration converges in at most `|linked|` rounds."""
    if closure is None:
        return least_member(quot, iv)
    cur = iv.p_min
    while True:
        nxt = hull(quot, closure(iv.table, cur))
        if nxt == cur:
            return cur
        cur = nxt


def _admits(quot: Quotient, iv: Interval, closure: Optional[Closure]) -> bool:
    """`quot` admits a member (on the required rung, if any): the joint hull of
    `P_min` stays under `P_max`."""
    if closure is None:
        return admits(quot, iv)
    return _least(quot, iv, closure) <= iv.p_max


# --- the greedy ------------------------------------------------------------


def _merge_candidates(pi: Quotient):
    """Every one-merge refinement of `pi`, deterministically: for each unordered
    pair of non-identity blocks in key-discipline order, the congruence
    identifying them (closed on the quotient) composed back onto the source."""
    q = pi.table
    blocks = sorted((c for c in range(q.n) if c != q.identity),
                    key=lambda c: (len(q.keys[c]), q.keys[c]))
    for i in range(len(blocks)):
        for j in range(i + 1, len(blocks)):
            b, bp = blocks[i], blocks[j]
            sub = congruence(q, [(b, bp)])
            yield compose(pi, sub), (q.keys[b], q.keys[bp])


def _greedy(pi0: Quotient, iv: Interval, closure: Optional[Closure]) -> Quotient:
    """Merge blocks while an admissible merge remains, taking at each step the
    admissible candidate that collapses the most classes (ties by merged-block
    key). Terminates: each accepted merge strictly lowers the class count."""
    pi = pi0
    while True:
        best: Optional[Quotient] = None
        best_key: Optional[Tuple[int, object]] = None
        for cand, tie in _merge_candidates(pi):
            if not _admits(cand, iv, closure):
                continue
            key = (cand.n, tie)
            if best_key is None or key < best_key:
                best, best_key = cand, key
        if best is None:
            return pi
        pi = best


def simplify(iv: Interval, opts: Options = Options()) -> Simplification:
    """The operation. Endpoint verdicts first (GT1); else the greedy over the
    seeds, then the class-count `argmin` over all recorded members and the three
    reference points. Asserts the [DPT25] soundness law on the emission
    (`B & P_K == P_min`) and re-quotients under `check=True`."""
    settled, w = k_settles_phi(iv)
    if settled:
        return Simplification(verdict="SETTLED", witness=w, bits=iv.bits)
    refuted, w = k_refutes_phi(iv)
    if refuted:
        return Simplification(verdict="REFUTED", witness=w, bits=iv.bits)

    closure = _rung_closure(opts.require, iv.table)

    seeds: List[Tuple[str, Quotient]] = [
        ("syntactic", syntactic_congruence(iv.table, iv.p_neg_phi)),
        ("identity", congruence(iv.table, [])),
    ]
    if opts.stutter:
        seeds.append(("stutter", congruence(iv.table, stutter_seeds(iv.table))))

    # pi_{neg_phi} is always admissible unconstrained: P_neg_phi is
    # pi_{neg_phi}-recognizable and in the interval (spec §6.2 step 2 / A3).
    if closure is None:
        assert admits(seeds[0][1], iv), (
            "pi_neg_phi inadmissible — convicts Prop 4.2 or syntactic_congruence")

    # Candidate members: (pairs, side, seed). Reference points are always legal.
    cands: List[Tuple[PairSet, str, str]] = [
        (iv.p_neg_phi, "reference", "neg_phi"),
        (iv.p_min, "reference", "p_min"),
        (iv.p_max, "reference", "p_max"),
    ]
    for name, pi0 in seeds:
        if not _admits(pi0, iv, closure):
            continue
        final = _greedy(pi0, iv, closure)
        cands.append((_least(final, iv, closure), "relax", name))
        if closure is None:
            cands.append((greatest_member(final, iv), "restrict", name))

    # Score by class count; ties prefer relax over restrict over reference, then
    # the earlier candidate (deterministic).
    side_rank = {"relax": 0, "restrict": 1, "reference": 2}
    scored = [(reduce(iv.table, ps, check=False).n, side_rank[side], idx, ps, side, seed)
              for idx, (ps, side, seed) in enumerate(cands)]
    _, _, _, b, side, seed = min(scored)

    # [DPT25] Thm 1 as a set identity, always on (spec §6.3).
    assert intersection(iv.table, b, iv.p_k) == iv.p_min, (
        "soundness law B & P_K == P_min violated (upstream bug)")

    inv_b = reduce(iv.table, b, check=True)
    stutter_verdict, _ = exists_stutter_invariant(iv)

    from ..classify.stutter import is_stutter_invariant
    classes = {
        "neg_phi": reduce(iv.table, iv.p_neg_phi, check=False).n,
        "k": reduce(iv.table, iv.p_k, check=False).n,
        "table": iv.table.n,
        "p_min": reduce(iv.table, iv.p_min, check=False).n,
        "p_max": reduce(iv.table, iv.p_max, check=False).n,
        "b": inv_b.n,
    }
    return Simplification(
        verdict="SIMPLIFIED", b=b, invariant=inv_b, side=side, seed=seed,
        bits=iv.bits, classes=classes,
        rung=(rung_of(iv.table, iv.p_neg_phi), rung_of(iv.table, b)),
        stutter=(is_stutter_invariant(reduce(iv.table, iv.p_neg_phi, check=False)),
                 is_stutter_invariant(inv_b)),
        stutter_verdict=stutter_verdict)
