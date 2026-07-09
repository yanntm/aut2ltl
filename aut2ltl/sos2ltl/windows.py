"""Condition (B) — window-determined acceptance of each final-candidate layer.

A layer `R` is (B)-determined at width `k'` when, for tails confined to `R`,
the acceptance verdict is a function of the set of recurring `k'`-windows
(Definition 5.7 of `research_notes/sos_toltl.md`). Because `R` is strongly
connected, every within-layer cycle is reachable from every class of `R`, so
the per-class quantification of the definition collapses to one test per
layer.

The tester is bounded and census-sized. A confined ultimately-periodic tail
ending on a cycle `z` at class `d` has verdict `(d·e, e) ∈ P` with `e` the
idempotent power of `[z]`, and its recurring `k'`-window set is the set of
cyclic `k'`-factors of `z` (over the λ-quotient alphabet). Three stages:

  1. *final candidacy* — a layer with no within-layer cycle can host no
     infinite confined tail and needs no window term;
  2. *the trivial pass* — the exact set of cycle classes per anchor class,
     by closure over `(class in R, accumulated word class)` pairs; if every
     reachable cycle verdict is the same, the verdict function is constant
     and (B) holds at every width;
  3. *the bounded test* — enumerate cycle words up to length `2·|R|·|𝒞|`
     (breadth-first, shortest cycles first, one node-count guard per anchor
     class), group by recurring window set per width, and compare verdicts:
     a conflict is a FAIL with a replayable witness pair of lassos; a
     conflict-free width is a cap-bounded PASS when the enumeration
     completed, and UNDECIDED when the guard tripped. The cap must scale
     with `|𝒞|`, not with `|Σ_λ|`: a cycle's verdict folds its word through
     the whole algebra, so conflicting loops can be longer than any bound
     local to the layer.

The two asymmetries of stage 3 are what make it usable. A *conflict* is exact
evidence — two confined lassos, equal recurring window sets, opposite verdicts —
so it refutes (B) at that width even from a truncated enumeration; only a
*conflict-free* width needs the enumeration to have completed before it may be
called a PASS. And the enumeration, being exponential in the cap, is almost
always truncated, so what it reaches first decides what the tester can see:
breadth-first with a per-anchor budget, since a conflict routinely pairs cycles
at two *different* anchor classes and a shared budget lets the first anchor
starve the rest.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, FrozenSet, List, Optional, Set, Tuple

from sosl.sos import Invariant, Lasso, Letter, Word

from .cayley import Cayley

PASS = "PASS"
FAIL = "FAIL"
UNDECIDED = "UNDECIDED"
TRANSIENT = "TRANSIENT"


@dataclass(frozen=True)
class WindowReport:
    """The condition-(B) analysis of one layer.

    `width` is the smallest tested width with no verdict conflict (None when
    every tested width conflicts or the layer is transient); `status` is the
    verdict at `width` — PASS (exact or trivial), UNDECIDED (conflict-free
    but the enumeration guard tripped), FAIL (every tested width conflicts),
    TRANSIENT (no within-layer cycle, no window term needed). `trivial`
    means stage 2 proved the verdict function constant, with `verdict` the
    constant (None otherwise). `fail_witness` maps
    each conflicting width to a pair of lassos with equal recurring window
    sets and different verdicts (replayable against any acceptor)."""

    layer: Tuple[int, ...]
    status: str
    width: Optional[int]
    trivial: bool
    verdict: Optional[bool]
    fail_witness: Dict[int, Tuple[Lasso, Lasso]]


def _rep_letters(inv: Invariant) -> List[Letter]:
    """One representative letter per λ-class, least mask first."""
    seen: Set[int] = set()
    reps: List[Letter] = []
    for a in inv.alphabet.letters():
        c = inv.letter_class[a]
        if c not in seen:
            seen.add(c)
            reps.append(a)
    return reps


def _cycle_classes(inv: Invariant, member: FrozenSet[int],
                   reps: List[Letter], d: int) -> Set[int]:
    """The classes of all words labeling within-layer cycles at `d`: closure
    of `(class in R, accumulated word class)` from `(d, [ε])`, collecting
    the accumulated class whenever the walk returns to `d`."""
    start = (d, inv.identity)
    seen: Set[Tuple[int, int]] = {start}
    stack: List[Tuple[int, int]] = [start]
    out: Set[int] = set()
    while stack:
        c, m = stack.pop()
        for a in reps:
            c2 = inv.mult[c][inv.letter_class[a]]
            if c2 not in member:
                continue
            m2 = inv.mult[m][inv.letter_class[a]]
            if c2 == d:
                out.add(m2)
            if (c2, m2) not in seen:
                seen.add((c2, m2))
                stack.append((c2, m2))
    return out


def _verdict(inv: Invariant, d: int, loop_cls: int) -> bool:
    """The verdict of any tail cycling with loop class `loop_cls` at `d`."""
    e = inv.idempotent_power(loop_cls)
    return (inv.mult[d][e], e) in inv.accept


def _recurring_windows(z: Word, k: int) -> FrozenSet[Word]:
    """The recurring `k`-window set of `z^ω`: cyclic `k`-factors of `z`."""
    reps = (k + len(z) - 1) // len(z) + 1
    zz = z * reps
    return frozenset(zz[i:i + k] for i in range(len(z)))


def _cycles(inv: Invariant, member: FrozenSet[int], reps: List[Letter],
            d: int, cap: int, budget: List[int]) -> Tuple[List[Word], bool]:
    """All words of length ≤ `cap` labeling within-layer walks `d → d`,
    shortest first; decrements `budget[0]` per visited node and reports whether
    the guard tripped (True = enumeration incomplete).

    Breadth-first, not depth-first: the enumeration is exponential in `cap`, so
    on any layer worth testing the guard trips long before it completes, and
    what survives in `out` is whatever the traversal reached first. Shortest
    cycles are the ones a verdict conflict is likeliest to sit on (a conflict
    needs only two cycles with the same window set), so the truncation must
    keep them — a DFS keeps one deep branch instead and can miss a length-1
    conflict entirely."""
    out: List[Word] = []
    queue: Deque[Tuple[int, Word]] = deque([(d, ())])
    while queue:
        c, w = queue.popleft()
        for a in reps:
            c2 = inv.mult[c][inv.letter_class[a]]
            if c2 not in member:
                continue
            budget[0] -= 1
            if budget[0] < 0:
                return out, True
            w2 = w + (a,)
            if c2 == d:
                out.append(w2)
            if len(w2) < cap:
                queue.append((c2, w2))
    return out, False


def analyze_layer(cay: Cayley, layer_id: int, k_max: int = 3,
                  node_budget: int = 200_000) -> WindowReport:
    """The condition-(B) analysis of layer `layer_id` of `cay`."""
    inv = cay.inv
    layer = cay.layers[layer_id]
    member = frozenset(layer)
    reps = _rep_letters(inv)

    # Stage 1 — candidacy: some within-layer edge cycle must exist.
    per_class_cycles: Dict[int, Set[int]] = {
        d: _cycle_classes(inv, member, reps, d) for d in layer}
    if not any(per_class_cycles.values()):
        return WindowReport(layer=layer, status=TRANSIENT, width=None,
                            trivial=False, verdict=None, fail_witness={})

    # Stage 2 — the trivial pass: one verdict across all reachable cycles.
    verdicts: Set[bool] = {
        _verdict(inv, d, m)
        for d, ms in per_class_cycles.items() for m in ms}
    if len(verdicts) == 1:
        return WindowReport(layer=layer, status=PASS, width=1, trivial=True,
                            verdict=next(iter(verdicts)), fail_witness={})

    # Stage 3 — bounded test on enumerated cycle words. Each anchor class gets
    # its own budget: a conflict is a pair of cycles at *different* anchors as
    # often as at one, so a budget shared across the loop would let the first
    # anchor starve the rest and hide the conflict behind an UNDECIDED.
    cap = 2 * len(layer) * inv.n
    samples: List[Tuple[int, Word]] = []
    incomplete = False
    for d in layer:
        words, tripped = _cycles(inv, member, reps, d, cap, [node_budget])
        incomplete = incomplete or tripped
        samples.extend((d, z) for z in words)

    fail_witness: Dict[int, Tuple[Lasso, Lasso]] = {}
    width: Optional[int] = None
    for k in range(1, k_max + 1):
        table: Dict[FrozenSet[Word], Tuple[bool, int, Word]] = {}
        conflict: Optional[Tuple[Lasso, Lasso]] = None
        for d, z in samples:
            v = _verdict(inv, d, inv.fold(z))
            wset = _recurring_windows(z, k)
            prev = table.get(wset)
            if prev is None:
                table[wset] = (v, d, z)
            elif prev[0] != v:
                conflict = (Lasso(inv.keys[prev[1]], prev[2]),
                            Lasso(inv.keys[d], z))
                break
        if conflict is not None:
            fail_witness[k] = conflict
        elif width is None:
            width = k
            break

    if width is not None:
        # Conflict-free at `width`, but only over the cycles enumerated: a
        # cap-bounded PASS when the enumeration completed, otherwise no verdict.
        status = UNDECIDED if incomplete else PASS
    else:
        # A conflict is a *witness pair* — two confined lassos with equal
        # recurring window sets and opposite verdicts — so it refutes (B) at
        # that width exactly, whether or not the enumeration finished. FAIL
        # here means: conflicted at every tested width.
        status = FAIL
    return WindowReport(layer=layer, status=status, width=width,
                        trivial=False, verdict=None,
                        fail_witness=fail_witness)


def realizable_verdicts(cay: Cayley, layer_id: int, k: int,
                        node_budget: int = 200_000,
                        ) -> Optional[Dict[FrozenSet[Word], bool]]:
    """The verdict per realizable recurring `k`-window set of layer
    `layer_id`, over the cap-bounded cycle enumeration — the table
    Proposition 5.15's window normal form reads. None when the enumeration
    guard trips or two same-set cycles disagree (the caller must not build
    a window term from an incomplete or conflicted table)."""
    inv = cay.inv
    layer = cay.layers[layer_id]
    member = frozenset(layer)
    reps = _rep_letters(inv)
    cap = 2 * len(layer) * inv.n
    table: Dict[FrozenSet[Word], bool] = {}
    for d in layer:
        words, tripped = _cycles(inv, member, reps, d, cap, [node_budget])
        if tripped:
            return None
        for z in words:
            v = _verdict(inv, d, inv.fold(z))
            wset = _recurring_windows(z, k)
            if table.setdefault(wset, v) != v:
                return None
    return table


def analyze(cay: Cayley, k_max: int = 3,
            node_budget: int = 200_000) -> Tuple[WindowReport, ...]:
    """The condition-(B) analysis of every layer, indexed by layer id."""
    return tuple(
        analyze_layer(cay, i, k_max=k_max, node_budget=node_budget)
        for i in range(len(cay.layers)))
