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

Operating stratum (outside it `transcribe` returns None and the caller
falls back): every layer 1-anchored — condition (A) at `k = 1`; every
final-candidate layer with a PASS-graded (B) width and a complete,
conflict-free verdict table. The graded engine (widths above 1) is not
built here. Constructors collapse `⊤`/`⊥` structurally — deterministic
identities, not a simplifier — which is what lets a terminal layer shed
its law and reduce `STAY∞` to `W(R)` alone.

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

    def set_(self, letters: Sequence[Letter]) -> str:
        if not letters:
            return "0"
        if len(letters) == self.size:
            return "1"
        return _or([self.cube[a] for a in letters])

    def window(self, w: Word) -> str:
        """`ŵ = w₁ ∧ X w₂ ∧ … ∧ X^{k−1} w_k` for a window word."""
        out = self.cube[w[-1]]
        for a in reversed(w[:-1]):
            out = _and([self.cube[a], _x(out)])
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
# The transcription.
# ------------------------------------------------------------------ #
def transcribe(inv: Invariant, k_b_max: int = 3) -> Optional[str]:
    """The defining formula of an aperiodic invariant on the flat-brick
    stratum, or None when a precondition fails: some layer is not
    1-anchored, or some final-candidate layer has no computable window
    term within width `k_b_max`."""
    cay: Cayley = build(inv)
    anch = anchoring.analyze(cay)
    if any(la.width != 1 for la in anch):
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
        layer = la.layer

        sojourn: Dict[int, str] = {
            c: ("1" if not la.exits[c]
                else _w(lets.set_(la.stutter[c]), lets.set_(la.move[c])))
            for c in layer}
        step = _and([
            _implies(lets.set_(la.anchors[c]), _x(sojourn[c]))
            for c in layer if la.anchors[c]])

        leave: Dict[int, str] = {}
        for c in layer:
            by_dest: Dict[int, List[Letter]] = {}
            for a in la.exits[c]:
                by_dest.setdefault(cay.step(c, a), []).append(a)
            exit_arm = _or([
                _and([lets.set_(vs), _x(final[d])])
                for d, vs in sorted(by_dest.items())])
            leave[c] = _u(lets.set_(la.stutter[c]), exit_arm)

        for c in layer:
            relay = _or([
                _and([lets.set_(la.anchors[c2]), _x(leave[c2])])
                for c2 in layer if la.anchors[c2]])
            big_leave = _or([
                leave[c],
                _and([sojourn[c], _u(step, relay)])])
            stay = _and([sojourn[c], _g(step), wterm[layer_id]])
            final[c] = _or([stay, big_leave])

    return final[inv.identity]
