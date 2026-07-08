"""C4 — the walk+window transcription engine (paper §5.2, Theorem 5.10).

Transcribes `Cay(L)` into the flat brick vocabulary, per layer `R` rooted
at its entry class, with the class-memoized label `Final(c)`:

    sojourn(c)  =  L(c) W M(c)                       (⊤ when E(c) = ∅)
    step        =  ⋀_{c ∈ R} ( A(c) → X sojourn(c) )
    leave(c)    =  L(c) U ⋁_{d} ( E_d(c) ∧ X Final(d) )
    LEAVE(c)    =  leave(c) ∨ ( sojourn(c) ∧ ( step U ⋁_{c'} (A(c') ∧ X leave(c')) ) )
    STAY∞(R,c)  =  sojourn(c) ∧ G step ∧ W(R)
    Final(c)    =  STAY∞(R,c) ∨ LEAVE(c)

`W(R)` is the window engine's acceptance term: the constant verdict on a
trivially determined layer; on a (B)-determined layer the Proposition 5.15
normal form over the realizable recurring-window sets — collapsed to
`⋁_min ⋀ GF ŵ` when the accepting family is upward-closed within the
realizable sets, the general exact-set form otherwise (with the `FG`
conjuncts restricted to realizable windows, equivalent on confined tails).
A transient layer, and an all-rejecting one, take `W = ⊥`.

A layer anchored only at a width `k ≥ 2` is transcribed by the graded
grammar (Theorem 5.23, §5.7) at operating window width `κ = k + 1`: the
law's trigger moves from anchor letters to anchor windows `A_κ(c)`, and a
transient fold of depth `k` (`TR`/`TL`) threads the phase over the entry,
where a trailing window would still straddle it:

    step_κ  =  ⋀_{c ∈ R} ⋀_{w ∈ A_κ(c)} ( ŵ → X^κ sojourn(c) )
    TR_0(c) =  sojourn(c)
    TR_j(c) =  ⋁_{a ∈ L(c) ∪ M(c)} ( a ∧ X TR_{j−1}(c·a) )
    TL_0(c) =  leave(c) ∨ ( sojourn(c) ∧
                 ( step_κ U ⋁_{c',w ∈ A_κ(c')} ( ŵ ∧ X^κ leave(c') ) ) )
    TL_j(c) =  ⋁_{a ∈ E(c)} ( a ∧ X φ_{c·a} )
                 ∨ ⋁_{a ∈ L(c) ∪ M(c)} ( a ∧ X TL_{j−1}(c·a) )
    STAY∞_κ =  TR_k(r) ∧ G step_κ ∧ W(R)         Final(r) = STAY∞_κ ∨ TL_k(r)

with `sojourn`, `leave`, and the letter sets unchanged from width 1.

Operating stratum (outside it `transcribe` returns None and the caller
falls back): every layer anchored at some finite width — condition (A)
holds; every final-candidate layer with a PASS-graded (B) width and a
complete, conflict-free verdict table. A layer anchored at no width (the
scoped DG fallback of Prop 5.24) is not built here. Constructors collapse
`⊤`/`⊥` structurally — deterministic identities, not a simplifier — which
is what lets a terminal layer shed its law and reduce `STAY∞` to `W(R)`
alone.

Output is a Spot-syntax formula string over the concrete letters (cubes
over `AP`); the class-indexed sharing is the memo — rendering is one
string per class, reused at every exit toward that class.
"""
from __future__ import annotations

from typing import Dict, FrozenSet, List, Optional, Sequence, Tuple

from sosl.sos import Invariant, Letter, Word

from . import anchoring, windows
from .cayley import Cayley, build


# ------------------------------------------------------------------ #
# Formula strings with structural ⊤/⊥ collapses ("1" / "0").
# ------------------------------------------------------------------ #
def _or(parts: Sequence[str]) -> str:
    keep = [p for p in parts if p != "0"]
    if "1" in keep:
        return "1"
    if not keep:
        return "0"
    return keep[0] if len(keep) == 1 else "(" + " | ".join(keep) + ")"


def _and(parts: Sequence[str]) -> str:
    keep = [p for p in parts if p != "1"]
    if "0" in keep:
        return "0"
    if not keep:
        return "1"
    return keep[0] if len(keep) == 1 else "(" + " & ".join(keep) + ")"


def _x(p: str) -> str:
    return p if p in ("0", "1") else f"X({p})"


def _xn(p: str, n: int) -> str:
    for _ in range(n):
        p = _x(p)
    return p


def _g(p: str) -> str:
    return p if p in ("0", "1") else f"G({p})"


def _u(left: str, right: str) -> str:
    if right in ("0", "1"):
        return right
    if left == "0":
        return right
    if left == "1":
        return f"F({right})"
    return f"({left}) U ({right})"


def _w(left: str, right: str) -> str:
    if right == "1":
        return "1"
    if left == "0":
        return right
    if left == "1":
        return "1"
    if right == "0":
        return _g(left)
    return f"({left}) W ({right})"


def _implies(left: str, right: str) -> str:
    if right == "1" or left == "0":
        return "1"
    if left == "1":
        return right
    if right == "0":
        return f"!({left})"
    return f"(({left}) -> ({right}))"


class _Letters:
    """Letter-set rendering over the concrete alphabet."""

    def __init__(self, inv: Invariant) -> None:
        ab = inv.alphabet
        self.size = ab.size
        self.cube: List[str] = [
            "&".join(p if p in ab.true_aps(a) else "!" + p for p in ab.aps)
            for a in ab.letters()]
        # A window position is a λ-class, carried by a representative letter;
        # every concrete letter of that class has the same monoid action, so
        # the position renders as the whole class's letter-set, not the one
        # representative's cube. `class_cube[a]` is that set for `a`'s class.
        by_class: Dict[int, List[Letter]] = {}
        for a in ab.letters():
            by_class.setdefault(inv.letter_class[a], []).append(a)
        self.class_cube: List[str] = [
            self.set_(by_class[inv.letter_class[a]]) for a in ab.letters()]

    def set_(self, letters: Sequence[Letter]) -> str:
        if not letters:
            return "0"
        if len(letters) == self.size:
            return "1"
        return _or([self.cube[a] for a in letters])

    def window(self, w: Word) -> str:
        """`ŵ = w₁ ∧ X w₂ ∧ … ∧ X^{k−1} w_k` for a window word — each position
        the full λ-class it names (the class-set, not one representative)."""
        out = self.class_cube[w[-1]]
        for a in reversed(w[:-1]):
            out = _and([self.class_cube[a], _x(out)])
        return out


# ------------------------------------------------------------------ #
# The window term W(R).
# ------------------------------------------------------------------ #
def _window_term(cay: Cayley, layer_id: int, rep: windows.WindowReport,
                 lets: _Letters) -> Optional[str]:
    """The acceptance term of one layer, or None when no sound term is
    computable within the tested widths (the engine then declines)."""
    if rep.status == windows.TRANSIENT:
        return "0"
    if rep.trivial:
        return "1" if rep.verdict else "0"
    if rep.status != windows.PASS or rep.width is None:
        return None
    table = windows.realizable_verdicts(cay, layer_id, rep.width)
    if table is None:
        return None

    accepting = [s for s, v in table.items() if v]
    if not accepting:
        return "0"

    def gf_all(s: FrozenSet[Word]) -> str:
        return _and([f"GF({lets.window(w)})" for w in sorted(s)])

    upward = all(
        table[s2]
        for s in accepting for s2 in table if s <= s2)
    if upward:
        minimal = [s for s in accepting
                   if not any(s2 < s for s2 in accepting)]
        return _or([gf_all(s) for s in sorted(minimal, key=sorted)])

    seen: FrozenSet[Word] = frozenset().union(*table.keys())
    return _or([
        _and([gf_all(s)]
             + [f"FG(!({lets.window(w)}))" for w in sorted(seen - s)])
        for s in sorted(accepting, key=sorted)])


# ------------------------------------------------------------------ #
# Per-layer letter groupings.
# ------------------------------------------------------------------ #
def _by_dest(cay: Cayley, c: int, letters: Sequence[Letter]
             ) -> Dict[int, List[Letter]]:
    """`letters` grouped by the class each sends `c` to."""
    out: Dict[int, List[Letter]] = {}
    for a in letters:
        out.setdefault(cay.step(c, a), []).append(a)
    return out


# ------------------------------------------------------------------ #
# The two per-layer builders. Each writes `Final(c)` for every `c` of the
# layer into `final`; children (strictly lower layers) are already there.
# ------------------------------------------------------------------ #
def _sojourn(la: anchoring.LayerAnchoring, lets: _Letters, c: int) -> str:
    return ("1" if not la.exits[c]
            else _w(lets.set_(la.stutter[c]), lets.set_(la.move[c])))


def _leave(cay: Cayley, la: anchoring.LayerAnchoring, lets: _Letters,
           final: Dict[int, str], c: int) -> str:
    exit_arm = _or([
        _and([lets.set_(vs), _x(final[d])])
        for d, vs in sorted(_by_dest(cay, c, la.exits[c]).items())])
    return _u(lets.set_(la.stutter[c]), exit_arm)


def _layer_flat(cay: Cayley, la: anchoring.LayerAnchoring, lets: _Letters,
                final: Dict[int, str], wterm: str) -> None:
    """The width-1 bricks of Theorem 5.10 (§5.2)."""
    layer = la.layer
    sojourn = {c: _sojourn(la, lets, c) for c in layer}
    step = _and([
        _implies(lets.set_(la.anchors[c]), _x(sojourn[c]))
        for c in layer if la.anchors[c]])
    leave = {c: _leave(cay, la, lets, final, c) for c in layer}
    for c in layer:
        relay = _or([
            _and([lets.set_(la.anchors[c2]), _x(leave[c2])])
            for c2 in layer if la.anchors[c2]])
        big_leave = _or([leave[c], _and([sojourn[c], _u(step, relay)])])
        stay = _and([sojourn[c], _g(step), wterm])
        final[c] = _or([stay, big_leave])


def _layer_graded(cay: Cayley, la: anchoring.LayerAnchoring, layer_id: int,
                  k: int, lets: _Letters, final: Dict[int, str],
                  wterm: str) -> None:
    """The graded bricks of Theorem 5.23 (§5.7) for a `k`-anchored layer,
    operating at window width `κ = k + 1`."""
    layer = la.layer
    kappa = k + 1
    sojourn = {c: _sojourn(la, lets, c) for c in layer}
    leave = {c: _leave(cay, la, lets, final, c) for c in layer}
    aw = anchoring.anchor_windows(cay, layer_id, kappa)

    step = _and([
        _implies(lets.window(w), _xn(sojourn[c], kappa))
        for c in layer for w in aw[c]])

    def within(c: int) -> Dict[int, List[Letter]]:
        return _by_dest(cay, c, la.stutter[c] + la.move[c])

    # Transient fold trees TR_j, TL_j for j = 0..k, class-indexed, bottom-up.
    tr: Dict[int, str] = dict(sojourn)                        # TR_0(c) = sojourn(c)
    for _ in range(k):
        tr = {c: _or([_and([lets.set_(vs), _x(tr[d])])
                      for d, vs in sorted(within(c).items())])
              for c in layer}

    relay = _or([                                             # ⋁_{c',w∈A_κ(c')} ŵ ∧ X^κ leave(c')
        _and([lets.window(w), _xn(leave[cp], kappa)])
        for cp in layer for w in aw[cp]])
    tl: Dict[int, str] = {                                    # TL_0(c)
        c: _or([leave[c], _and([sojourn[c], _u(step, relay)])])
        for c in layer}
    for _ in range(k):
        tl = {c: _or([
            _or([_and([lets.set_(vs), _x(final[d])])
                 for d, vs in sorted(_by_dest(cay, c, la.exits[c]).items())]),
            _or([_and([lets.set_(vs), _x(tl[d])])
                 for d, vs in sorted(within(c).items())])])
              for c in layer}

    for c in layer:
        stay = _and([tr[c], _g(step), wterm])                # STAY∞_κ(R, c)
        final[c] = _or([stay, tl[c]])                        # Final(c)


# ------------------------------------------------------------------ #
# Committed-accepting classes (§6.3 strength stratification).
# ------------------------------------------------------------------ #
def _committed(cay: Cayley, c: int) -> bool:
    """Whether every ω-word from class `c` is accepted — the tail language
    `T_c = Σ^ω`. Exactly when every linked pair whose stem is reachable from
    `c` in `Cay(L)` lies in `P`: from `c` no continuation can reach a
    rejecting recurrence. Then `Final(c)` collapses to `true` (the co-safety
    template), short-circuiting the walk bricks — an `O(|𝒞|²)` read-off."""
    inv = cay.inv
    reach: set = set()
    stack = [c]
    while stack:
        x = stack.pop()
        if x in reach:
            continue
        reach.add(x)
        for a in range(inv.alphabet.size):
            stack.append(cay.step(x, a))
    accept = inv.accept
    return all(pair in accept
               for pair in inv.linked_pairs() if pair[0] in reach)


# ------------------------------------------------------------------ #
# The transcription.
# ------------------------------------------------------------------ #
def transcribe(inv: Invariant, k_b_max: int = 3) -> Optional[str]:
    """The defining formula of an aperiodic invariant on the anchored
    stratum, or None when a precondition fails: some layer anchors at no
    width (condition (A) fails — the scoped fallback is not built here), or
    some final-candidate layer has no computable window term within width
    `k_b_max`."""
    cay: Cayley = build(inv)
    anch = anchoring.analyze(cay)
    if any(la.width is None for la in anch):
        return None
    lets = _Letters(inv)

    wterm: List[Optional[str]] = []
    for i in range(len(cay.layers)):
        rep = windows.analyze_layer(cay, i, k_max=k_b_max)
        wterm.append(_window_term(cay, i, rep, lets))
    if any(t is None for t in wterm):
        return None

    final: Dict[int, str] = {}
    # Deepest layers first: exits only ever point strictly down the R-order.
    for layer_id in reversed(range(len(cay.layers))):
        la = anch[layer_id]
        assert la.width is not None  # guarded above
        term = wterm[layer_id]
        assert term is not None
        committed = [c for c in la.layer if _committed(cay, c)]
        if la.width == 1:
            _layer_flat(cay, la, lets, final, term)
        elif len(committed) < len(la.layer):
            # A k≥2 (graded) layer with a non-committed class: the graded
            # exit-chain collapse (Theorem 5.23) is not proven exact, so
            # decline to the DG baseline rather than risk an
            # under-approximation. A fully committed graded layer needs no
            # brick — every class takes Final = true below.
            return None
        # §6.3: a committed-accepting class takes Final = true directly, its
        # reachable region being entirely in P (co-safety template).
        for c in committed:
            final[c] = "1"

    return final[inv.identity]
