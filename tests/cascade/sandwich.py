"""K-E7 sandwich scan: the absorption/group map on ALG-5's loop classes.

For idempotent loop classes `e ≠ e′` sharing a base `x` and covered set `F`
(hence equal cyclic window data), the sandwich identities `e·e′·e J e`,
`e′·e·e′ J e′` (draft C.4) are tested against the invariant's 𝒥-order. C.17 is
refuted on paper (Theorem C.12′), so this is a *map*: it classifies where the
identities fail and by what mechanism (absorption / group / other). Two positive
controls are mandatory (K-E0 step 3): the floor witness's frozen layer
(absorption, `e·z·e = z <_J e`) and `EvenBlocks` (group, `f·z·f = z <_J f`).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Optional, Tuple

from sosl.sos import Invariant

from tests.cascade.config_machine import Closed, Edge, Node, all_closures


def two_sided_ideals(inv: Invariant) -> Dict[int, FrozenSet[int]]:
    """`ideal[b]` = the principal two-sided ideal `S¹·b·S¹` (all `M(M(g,b),h)`),
    computed by the left/right multiplication closure. `a ∈ ideal[b]` is the
    𝒥-order `a ≤_J b`. The unit `inv.identity` is a class, so `b ∈ ideal[b]`."""
    classes = range(inv.n)
    out: Dict[int, FrozenSet[int]] = {}
    for b in classes:
        reach = {b}
        frontier = [b]
        while frontier:
            y = frontier.pop()
            for g in classes:
                for z in (inv.mult[g][y], inv.mult[y][g]):
                    if z not in reach:
                        reach.add(z)
                        frontier.append(z)
        out[b] = frozenset(reach)
    return out


def j_leq(a: int, b: int, ideals: Dict[int, FrozenSet[int]]) -> bool:
    return a in ideals[b]


def j_equiv(a: int, b: int, ideals: Dict[int, FrozenSet[int]]) -> bool:
    return a in ideals[b] and b in ideals[a]


def j_minimal(a: int, ideals: Dict[int, FrozenSet[int]]) -> bool:
    """`a`'s 𝒥-class is minimal: nothing lies strictly 𝒥-below it (a zero-like
    sink). `a·e·a = a` for `e·a·e` etc. bottoms out here."""
    return all(j_equiv(t, a, ideals) for t in ideals[a])


@dataclass
class SandwichFail:
    """One failing idempotent pair at a shared base/covered-set."""

    base: Node
    F: FrozenSet[Edge]
    e: int
    ep: int
    s: int          # e·e′·e
    sp: int         # e′·e·e′
    mechanism: str  # 'absorption' | 'group' | 'other' | 'BUG'
    splits: bool    # e, e′ give different verdicts over EntrySt(base)


def _val(inv: Invariant, s: int, e: int) -> bool:
    return (inv.mult[s][e], e) in inv.accept


def scan(inv: Invariant, closures: Dict[Tuple[int, Node], Closed],
         aperiodic: bool,
         entryst: Optional[Dict[Node, FrozenSet[int]]] = None
         ) -> Tuple[List[SandwichFail], int]:
    """Run the sandwich test over every `(base x, covered set F)` idempotent
    pair. Returns the failures and the PASS count. `s = e·e′·e` is always
    𝒥-below `e` (and `sp = e′·e·e′` below `e′`), so the mechanism turns on where
    a broken sandwich lands:
      - non-aperiodic invariant                        → `group`;
      - aperiodic, the sink is 𝒥-minimal (a zero)      → `absorption`;
      - aperiodic, the sink is 𝒥-strictly-below but not
        minimal                                        → `other` (K-E2 hunt);
      - aperiodic, `J(sink,·)` holds yet inequality    → `BUG` (contradicts the
        Lemma C.16 localization)."""
    ideals = two_sided_ideals(inv)

    # group CL across entries by (base x, covered set F): the idempotent loop
    # classes sharing exactly that recurring data.
    idems: Dict[Tuple[Node, FrozenSet[Edge]], set] = {}
    for (c, x), cl in closures.items():
        if cl is None:
            continue
        for F, d in cl:
            if inv.mult[d][d] == d:                 # idempotent loop class only
                idems.setdefault((x, F), set()).add(d)

    fails: List[SandwichFail] = []
    passes = 0
    for (x, F), es in idems.items():
        order = sorted(es)
        for i in range(len(order)):
            for j in range(i + 1, len(order)):     # unordered pairs
                e, ep = order[i], order[j]
                s = inv.mult[inv.mult[e][ep]][e]    # e·e′·e
                sp = inv.mult[inv.mult[ep][e]][ep]  # e′·e·e′
                if s == e and sp == ep:
                    passes += 1
                    continue
                if not aperiodic:
                    mech = "group"
                else:
                    # per identity: 'jfail' (broke 𝒥) is a real sandwich failure;
                    # 'j' (𝒥 held, ≠) in an aperiodic monoid contradicts C.16.
                    jf1 = not j_equiv(s, e, ideals)
                    jf2 = not j_equiv(sp, ep, ideals)
                    if jf1 or jf2:
                        # 𝒥-comparable idempotents: the lower dominates the
                        # product (zero absorption, the floor witness's `z <_J e`).
                        # 𝒥-equivalent idempotents that still drop below are the
                        # genuine third-mechanism candidate.
                        mech = ("other" if j_equiv(e, ep, ideals)
                                else "absorption")
                    else:
                        mech = "BUG"
                est = entryst.get(x, frozenset()) if entryst else frozenset()
                splits = any(_val(inv, st, e) != _val(inv, st, ep) for st in est)
                fails.append(SandwichFail(x, F, e, ep, s, sp, mech, splits))
    return fails, passes


def scan_layer(inv: Invariant, R: FrozenSet[int], k: int,
               aperiodic: bool, budget: int = 10 ** 6
               ) -> Tuple[List[SandwichFail], int]:
    """Convenience: run ALG-5 over layer `R` at width `k`, then the scan."""
    return scan(inv, all_closures(inv, R, k, budget), aperiodic)
