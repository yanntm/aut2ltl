"""C4 — the walk+window transcription engine (paper §4.2, Theorem 4.10).

Transcribes `Cay(L)` into the flat brick vocabulary, per layer `R` rooted
at its entry class, with the class-memoized label `Final(c)`:

    sojourn(c)  =  L(c) W M(c)                       (⊤ when E(c) = ∅)
    step        =  ⋀_{c ∈ R} ( A(c) → X sojourn(c) )
    leave(c)    =  L(c) U ⋁_{d} ( E_d(c) ∧ X Final(d) )
    LEAVE(c)    =  leave(c) ∨ ( sojourn(c) ∧ ( step U ⋁_{c'} (A(c') ∧ X leave(c')) ) )
    STAY∞(R,c)  =  sojourn(c) ∧ G step ∧ W(R)
    Final(c)    =  STAY∞(R,c) ∨ LEAVE(c)

`W(R)` is the window engine's acceptance term: the constant verdict on a
trivially determined layer; on a (B)-determined layer the Proposition 5.4
normal form over the realizable recurring-window sets — collapsed to
`⋁_min ⋀ GF ŵ` when the accepting family is upward-closed within the
realizable sets, the general exact-set form otherwise (with the `FG`
conjuncts restricted to realizable windows, equivalent on confined tails).
A transient layer, and an all-rejecting one, take `W = ⊥`.

A layer anchored only at a width `k ≥ 2` is transcribed by the graded
grammar (Theorem 4.13, §4.3) at operating window width `κ = k + 1`: the
law's trigger moves from anchor letters to anchor windows `An_κ(c)`, a
transient fold of depth `k` (`TR`/`TL`) threads the phase over the entry,
where a trailing window would still straddle it, and the seam bricks
`seam(c)` close the exit-chain across that straddling band — an exit whose
last within-layer change falls within `k` steps of the transient's end is
certified by a window opening *inside* the transient, too early for
`TL_0`'s `U`; the thread pins the class, so the certificate needs no
escort (`c ∈ dom(act_R(w))` squeezes the window's span into the layer):

    step_κ  =  ⋀_{c ∈ R} ⋀_{w ∈ An_κ(c)} ( ŵ → X^κ sojourn(c) )
    TR_0(c) =  sojourn(c)
    TR_j(c) =  ⋁_{a ∈ L(c) ∪ M(c)} ( a ∧ X TR_{j−1}(c·a) )
    seam(c)    =  ⋁_{c' ∈ R} ⋁_{w ∈ An_κ(c'), c ∈ dom(act_R(w))} ( ŵ ∧ X^κ leave(c') )
    step_th(c) =  ⋀_{c' ∈ R} ⋀_{w ∈ An_κ(c'), c ∈ dom(act_R(w))}
                    ( ŵ → X^κ ( sojourn(c') ∨ leave(c') ) )
    TL_0(c) =  leave(c) ∨ ( sojourn(c) ∧
                 ( step_κ U ⋁_{c',w ∈ An_κ(c')} ( ŵ ∧ X^κ leave(c') ) ) )
    TL_j(c) =  ⋁_{a ∈ E(c)} ( a ∧ X φ_{c·a} )
                 ∨ ( step_th(c) ∧ ⋁_{a ∈ L(c) ∪ M(c)} ( a ∧ X TL_{j−1}(c·a) ) )
                 ∨ seam(c)                                        j = 1..k
    STAY∞_κ =  TR_k(r) ∧ G step_κ ∧ W(R)         Final(r) = STAY∞_κ ∨ TL_k(r)

with `sojourn`, `leave`, and the letter sets unchanged from width 1.
`step_th(c)` — the dom-restricted law at a thread node, the step-side twin
of `seam(c)` — rides the thread's *continue* branch and nothing else. It
closes the soundness side of the same straddling band the seam closes for
completeness: a move at a position in `[t+k, t+2k)` has its certifying
window opening inside the transient, where `TL_0`'s `U` asserts no
triggers, so without it the `U`-witness can fire on letters alone while
the true walk has already left the layer. The dom restriction keeps every
asserted trigger truthful (the thread pins the class, and
`c ∈ dom(act_R(w))` squeezes the window's span into the layer); on the
exit branch it is vacuous, and on the seam branch it would wrongly demand
a sojourn after an exit the seam itself certifies. The consequence keeps
a `leave` arm as a valve: the pinned landing may be followed by stutters
and an exit with no intervening move, where `sojourn`'s weak-until is cut
by the exit letter — `leave(c')` is exactly that continuation, and a
realized `leave` is a sound conclusion in its own right.

Operating stratum (outside it `transcribe` returns None and the caller
falls back): every layer anchored at some finite width — condition (A)
holds; every final-candidate layer with a PASS-graded (B) width and a
complete, conflict-free verdict table. A layer anchored at no width (the
scoped DG fallback of Prop 4.14) is not built here. Constructors collapse
`⊤`/`⊥` structurally — deterministic identities, not a simplifier — which
is what lets a terminal layer shed its law and reduce `STAY∞` to `W(R)`
alone.

Output is a hash-consed `spot.formula`, never a string: the class-indexed
memo makes `Final(d)` one node reused at every exit toward `d`, and Spot's
hash-consing keeps that sharing in the emitted DAG. Flattening it to a
string is the caller's (measured, often astronomical) business.

Three renderings sit on top of the bricks, each exactness-preserving by the
label contract (any exact label of the tail language serves) and each
switchable through `Rendering` so its contribution can be measured:

  - *guard synthesis* — every letter set in a guard position (the `L/M/E/A`
    sets, the target-grouped exit fans, the λ-classes of a window's
    positions) is a minimized formula over `AP`, not a union of concrete
    cubes (paper §2.1's set-as-formula convention);
  - *guard grouping* — an exit fan is one disjunct per **target class**,
    `⋁_d ((⋁_{a: c·a = d} a) ∧ X φ_d)`, not one per letter (paper §6,
    rendering 1);
  - *residual indexing* — an exit child is keyed by the **residual** of its
    target class, so branches that diverge in class but re-merge in future
    share one label. Only the `X φ_target` slots coarsen; the within-layer
    machinery stays class-keyed. The shared label is always one the R-order
    induction has already built (exits point strictly down the R-order, and
    a residual's representative is the class of its deepest layer), which is
    what keeps the memo acyclic.

`transcribe` returns only the root label. Setting `SOS2LTL_TRACE` (or the
global `TRANSLATOR_TRACE_ON`) dumps every brick as one structured line —
`[engine] layer=… brick=… class=… formula=…` — in the order the R-order
descent builds them, child-first, which is the derivation the paper's §5.2
label stack reads as. `formula=` is the raw brick, simplification off.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Callable, Dict, FrozenSet, List, Optional, Sequence, Tuple

import spot

from sosl.sos import Invariant, Letter, Word

from . import anchoring, windows
from .cayley import Cayley, build
from .guards import Guards
from .readoffs import residual_partition

# On when either SOS2LTL_TRACE or the global TRANSLATOR_TRACE_ON is set (presence;
# value ignored), or when a caller flips it. Every message is built inside
# `if _TRACE:`, so a disabled trace costs nothing — `str(formula)` on a shared DAG
# is O(unfolded tree). One structured line per brick, child-first in the R-order
# descent: that order *is* the derivation the label stack reads as.
_TRACE = "SOS2LTL_TRACE" in os.environ or "TRANSLATOR_TRACE_ON" in os.environ


def _trace(layer_id: int, brick: str, cls: Optional[int],
           f: "spot.formula") -> None:
    if _TRACE:
        where = "" if cls is None else f" class={cls}"
        print(f"[engine] layer={layer_id} brick={brick}{where} formula={f}",
              file=sys.stderr)


@dataclass(frozen=True)
class Rendering:
    """Which of the three exactness-preserving renderings are applied. All on
    is the engine's normal operation; the flags exist so E10's ledger can
    price each sharing against the plain rendering."""

    guards: bool = True     # minimized AP formulas vs unions of letter cubes
    group: bool = True      # exit fans per target class vs per letter
    residual: bool = True   # exit children keyed by residual vs by class


DEFAULT = Rendering()

_TT = spot.formula.tt()
_FF = spot.formula.ff()


# ------------------------------------------------------------------ #
# Formula constructors with structural ⊤/⊥ collapses.
# ------------------------------------------------------------------ #
def _or(parts: Sequence["spot.formula"]) -> "spot.formula":
    keep = [p for p in parts if p != _FF]
    if any(p == _TT for p in keep):
        return _TT
    if not keep:
        return _FF
    return keep[0] if len(keep) == 1 else spot.formula.Or(keep)


def _and(parts: Sequence["spot.formula"]) -> "spot.formula":
    keep = [p for p in parts if p != _TT]
    if any(p == _FF for p in keep):
        return _FF
    if not keep:
        return _TT
    return keep[0] if len(keep) == 1 else spot.formula.And(keep)


def _const(p: "spot.formula") -> bool:
    return p == _TT or p == _FF


def _x(p: "spot.formula") -> "spot.formula":
    return p if _const(p) else spot.formula.X(p)


def _xn(p: "spot.formula", n: int) -> "spot.formula":
    for _ in range(n):
        p = _x(p)
    return p


def _g(p: "spot.formula") -> "spot.formula":
    return p if _const(p) else spot.formula.G(p)


def _f(p: "spot.formula") -> "spot.formula":
    return p if _const(p) else spot.formula.F(p)


def _u(left: "spot.formula", right: "spot.formula") -> "spot.formula":
    if _const(right):
        return right
    if left == _FF:
        return right
    if left == _TT:
        return _f(right)
    return spot.formula.U(left, right)


def _w(left: "spot.formula", right: "spot.formula") -> "spot.formula":
    if right == _TT or left == _TT:
        return _TT
    if left == _FF:
        return right
    if right == _FF:
        return _g(left)
    return spot.formula.W(left, right)


def _implies(left: "spot.formula", right: "spot.formula") -> "spot.formula":
    if right == _TT or left == _FF:
        return _TT
    if left == _TT:
        return right
    if right == _FF:
        return spot.formula.Not(left)
    return spot.formula.Implies(left, right)


# ------------------------------------------------------------------ #
# Letter sets and windows, as minimized AP formulas.
# ------------------------------------------------------------------ #
class _Letters:
    """The guard renderer, plus the window term `ŵ` over λ-classes."""

    def __init__(self, inv: Invariant, minimize: bool = True) -> None:
        self.guards = Guards(inv.alphabet, minimize=minimize)
        # A window position is a λ-class, carried by a representative letter;
        # every concrete letter of that class has the same monoid action, so
        # the position renders as the whole class's letter set, not the one
        # representative's cube. `_class_guard[a]` is that set for `a`'s class.
        by_class: Dict[int, List[Letter]] = {}
        for a in inv.alphabet.letters():
            by_class.setdefault(inv.letter_class[a], []).append(a)
        self._class_guard: List["spot.formula"] = [
            self.guards.render(by_class[inv.letter_class[a]])
            for a in inv.alphabet.letters()]
        self._windows: Dict[Word, "spot.formula"] = {}

    def set_(self, letters: Sequence[Letter]) -> "spot.formula":
        return self.guards.render(letters)

    def window(self, w: Word) -> "spot.formula":
        """`ŵ = w₁ ∧ X w₂ ∧ … ∧ X^{k−1} w_k` for a window word — each position
        the full λ-class it names (the class-set, not one representative)."""
        hit = self._windows.get(w)
        if hit is None:
            hit = self._class_guard[w[-1]]
            for a in reversed(w[:-1]):
                hit = _and([self._class_guard[a], _x(hit)])
            self._windows[w] = hit
        return hit


# ------------------------------------------------------------------ #
# The window term W(R).
# ------------------------------------------------------------------ #
def _window_term(cay: Cayley, layer_id: int, rep: windows.WindowReport,
                 lets: _Letters) -> Optional["spot.formula"]:
    """The acceptance term of one layer, or None when no sound term is
    computable within the tested widths (the engine then declines)."""
    if rep.status == windows.TRANSIENT:
        return _FF
    if rep.trivial:
        return _TT if rep.verdict else _FF
    if rep.status != windows.PASS or rep.width is None:
        return None
    table = windows.realizable_verdicts(cay, layer_id, rep.width)
    if table is None:
        return None

    accepting = [s for s, v in table.items() if v]
    if not accepting:
        return _FF

    def gf_all(s: FrozenSet[Word]) -> "spot.formula":
        return _and([_g(_f(lets.window(w))) for w in sorted(s)])

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
             + [_f(_g(spot.formula.Not(lets.window(w))))
                for w in sorted(seen - s)])
        for s in sorted(accepting, key=sorted)])


# ------------------------------------------------------------------ #
# Per-layer letter groupings.
# ------------------------------------------------------------------ #
def _self(c: int) -> int:
    """The identity key — a fan whose children are indexed by class."""
    return c


class _Exits:
    """The exit children of the transcription: what an arrow leaving a layer
    points at. Without residual indexing the key is the target class and the
    label is its `Final`. With it, the key is the target's residual and the
    label is the `Final` of that residual's representative — the first class
    of the residual the R-order induction built, hence one lying in the
    deepest layer that carries it.

    Substituting is exact (a residual is a tail language, and `Final` is an
    exact label of it) and acyclic: exits point strictly down the R-order, so
    the representative is always already built when an exit reaches it."""

    def __init__(self, inv: Invariant, final: Dict[int, "spot.formula"],
                 residual: bool) -> None:
        self.final = final
        self.on = residual
        self.residual: Tuple[int, ...] = residual_partition(inv)
        self.rep_of: Dict[int, int] = {}

    def key(self, d: int) -> int:
        return self.residual[d] if self.on else d

    def label(self, j: int) -> "spot.formula":
        return self.final[self.rep_of[j] if self.on else j]

    def built(self, classes: Sequence[int]) -> None:
        """Register a freshly labelled layer's classes as residual
        representatives — deepest layer first, so the first registration wins
        and later (higher) layers reuse it."""
        for c in classes:
            self.rep_of.setdefault(self.residual[c], c)


def _by_key(cay: Cayley, c: int, letters: Sequence[Letter],
            key: "Callable[[int], int]") -> Dict[int, List[Letter]]:
    """`letters` grouped by the key of the class each sends `c` to."""
    out: Dict[int, List[Letter]] = {}
    for a in letters:
        out.setdefault(key(cay.step(c, a)), []).append(a)
    return out


def _fan(cay: Cayley, lets: _Letters, c: int, letters: Sequence[Letter],
         key: "Callable[[int], int]", label: "Callable[[int], spot.formula]",
         group: bool) -> "spot.formula":
    """The fan of `letters` out of `c`, each arm guarding the label of what it
    lands on — a class, or (under residual indexing) a residual.

    Grouped (paper §6, rendering 1) this is `⋁_j ( (⋁_{a : key(c·a) = j} a) ∧
    X label(j) )` — one disjunct per distinct child, its guard the whole
    letter set aiming there, collapsing to `X label(j)` when every letter
    agrees. Grouping on the child key rather than on the target class is what
    lets the two renderings compose: letters that diverge in class but re-merge
    in residual land in one arm. Ungrouped it is one disjunct per letter: the
    same language, one arm per arrow of `Cay(L)`."""
    if not group:
        return _or([_and([lets.set_([a]), _x(label(key(cay.step(c, a))))])
                    for a in sorted(letters)])
    return _or([
        _and([lets.set_(vs), _x(label(j))])
        for j, vs in sorted(_by_key(cay, c, letters, key).items())])


# ------------------------------------------------------------------ #
# The two per-layer builders. Each writes `Final(c)` for every `c` of the
# layer into `final`; children (strictly lower layers) are already there.
# ------------------------------------------------------------------ #
def _sojourn(la: anchoring.LayerAnchoring, lets: _Letters,
             c: int) -> "spot.formula":
    return (_TT if not la.exits[c]
            else _w(lets.set_(la.stutter[c]), lets.set_(la.move[c])))


def _leave(cay: Cayley, la: anchoring.LayerAnchoring, lets: _Letters,
           exit_: "_Exits", rend: Rendering, c: int) -> "spot.formula":
    return _u(lets.set_(la.stutter[c]),
              _fan(cay, lets, c, la.exits[c], exit_.key, exit_.label,
                   rend.group))


def _layer_flat(cay: Cayley, la: anchoring.LayerAnchoring, layer_id: int,
                lets: _Letters, final: Dict[int, "spot.formula"],
                exit_: "_Exits", rend: Rendering,
                wterm: "spot.formula") -> None:
    """The width-1 bricks of Theorem 4.10 (§4.2)."""
    layer = la.layer
    sojourn = {c: _sojourn(la, lets, c) for c in layer}
    step = _and([
        _implies(lets.set_(la.anchors[c]), _x(sojourn[c]))
        for c in layer if la.anchors[c]])
    leave = {c: _leave(cay, la, lets, exit_, rend, c) for c in layer}
    if _TRACE:
        for c in layer:
            _trace(layer_id, "sojourn", c, sojourn[c])
        _trace(layer_id, "step", None, step)
        for c in layer:
            _trace(layer_id, "leave", c, leave[c])
    for c in layer:
        relay = _or([
            _and([lets.set_(la.anchors[c2]), _x(leave[c2])])
            for c2 in layer if la.anchors[c2]])
        big_leave = _or([leave[c], _and([sojourn[c], _u(step, relay)])])
        stay = _and([sojourn[c], _g(step), wterm])
        final[c] = _or([stay, big_leave])
        if _TRACE:
            _trace(layer_id, "STAY", c, stay)
            _trace(layer_id, "LEAVE", c, big_leave)
            _trace(layer_id, "Final", c, final[c])


def _seam(arms: Sequence[Tuple[anchoring.AnchorWindow, "spot.formula"]],
          c: int) -> "spot.formula":
    """`seam(c)` — the anchor-window arms readable at `c` (Thm 4.13): at a
    thread node the class `c` is known exactly, so `c ∈ dom(act_R(w))`
    squeezes the window's whole span into the layer, pins its landing class,
    and `leave` concludes — the certificate needs no escort."""
    return _or([term for w, term in arms if c in w.domain])


def _layer_graded(cay: Cayley, la: anchoring.LayerAnchoring, layer_id: int,
                  k: int, lets: _Letters, final: Dict[int, "spot.formula"],
                  exit_: "_Exits", rend: Rendering,
                  wterm: "spot.formula") -> None:
    """The graded bricks of Theorem 4.13 (§4.3) for a `k`-anchored layer,
    operating at window width `κ = k + 1`."""
    layer = la.layer
    kappa = k + 1
    sojourn = {c: _sojourn(la, lets, c) for c in layer}
    leave = {c: _leave(cay, la, lets, exit_, rend, c) for c in layer}
    aw = anchoring.anchor_windows(cay, layer_id, kappa)

    step = _and([
        _implies(lets.window(w.word), _xn(sojourn[c], kappa))
        for c in layer for w in aw[c]])

    def inside(c: int) -> Tuple[Letter, ...]:
        return la.stutter[c] + la.move[c]

    # Transient fold trees TR_j, TL_j for j = 0..k, class-indexed, bottom-up.
    tr: Dict[int, "spot.formula"] = dict(sojourn)             # TR_0(c) = sojourn(c)
    for _ in range(k):
        prev = tr
        tr = {c: _fan(cay, lets, c, inside(c), _self, prev.__getitem__,
                      rend.group)
              for c in layer}

    # One arm per anchor window (c', w): ŵ ∧ X^κ leave(c'). The relay — the
    # `U`-witness of TL_0 — disjoins all of them; seam(c) keeps those whose
    # domain contains the thread's class; step_th(c) asserts the law over
    # the same dom-restricted windows on the thread's continue branch.
    arms: List[Tuple[anchoring.AnchorWindow, "spot.formula"]] = [
        (w, _and([lets.window(w.word), _xn(leave[cp], kappa)]))
        for cp in layer for w in aw[cp]]
    relay = _or([term for _, term in arms])
    seam = {c: _seam(arms, c) for c in layer}
    step_th = {
        c: _and([
            _implies(lets.window(w.word), _xn(sojourn[cp], kappa))
            for cp in layer for w in aw[cp] if c in w.domain])
        for c in layer}
    tl: Dict[int, "spot.formula"] = {                         # TL_0(c)
        c: _or([leave[c], _and([sojourn[c], _u(step, relay)])])
        for c in layer}
    for _ in range(k):
        prev = tl
        tl = {c: _or([_fan(cay, lets, c, la.exits[c], exit_.key, exit_.label,
                           rend.group),
                      _and([step_th[c],
                            _fan(cay, lets, c, inside(c), _self,
                                 prev.__getitem__, rend.group)]),
                      seam[c]])
              for c in layer}

    if _TRACE:
        for c in layer:
            _trace(layer_id, "sojourn", c, sojourn[c])
            _trace(layer_id, "leave", c, leave[c])
            _trace(layer_id, "seam", c, seam[c])
            _trace(layer_id, "step_th", c, step_th[c])
        _trace(layer_id, "step_kappa", None, step)
    for c in layer:
        stay = _and([tr[c], _g(step), wterm])                # STAY∞_κ(R, c)
        final[c] = _or([stay, tl[c]])                        # Final(c)
        if _TRACE:
            _trace(layer_id, f"TR_{k}", c, tr[c])
            _trace(layer_id, f"TL_{k}", c, tl[c])
            _trace(layer_id, "Final", c, final[c])


# ------------------------------------------------------------------ #
# Committed-accepting classes (the §4.3 committed base case).
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
def labels(inv: Invariant, k_b_max: int = 3,
           rend: Rendering = DEFAULT) -> Optional[Dict[int, "spot.formula"]]:
    """The full class-indexed memo `Final(c)` — an exact label of the tail
    language `T_c` for every class `c` — or None when a precondition fails:
    some layer anchors at no width (condition (A) fails — the scoped
    fallback is not built here), or some final-candidate layer has no
    computable window term within width `k_b_max`. `transcribe` is the
    root-only wrapper; the memo itself is the grounding surface for
    per-class diagnostics."""
    cay: Cayley = build(inv)
    anch = anchoring.analyze(cay)
    if any(la.width is None for la in anch):
        return None
    lets = _Letters(inv, minimize=rend.guards)

    wterm: List[Optional["spot.formula"]] = []
    for i in range(len(cay.layers)):
        rep = windows.analyze_layer(cay, i, k_max=k_b_max)
        wterm.append(_window_term(cay, i, rep, lets))
    if any(t is None for t in wterm):
        return None

    final: Dict[int, "spot.formula"] = {}
    exit_ = _Exits(inv, final, rend.residual)

    # Deepest layers first: exits only ever point strictly down the R-order.
    for layer_id in reversed(range(len(cay.layers))):
        la = anch[layer_id]
        assert la.width is not None  # guarded above
        term = wterm[layer_id]
        assert term is not None
        _trace(layer_id, "window", None, term)
        committed = [c for c in la.layer if _committed(cay, c)]
        if len(committed) < len(la.layer):
            if la.width == 1:
                _layer_flat(cay, la, layer_id, lets, final, exit_, rend,
                            term)
            else:
                _layer_graded(cay, la, layer_id, la.width, lets, final,
                              exit_, rend, term)
        # A committed-accepting class takes Final = true directly, its
        # reachable region being entirely in P (the co-safety base case,
        # paper §4.3); the constant outranks any brick, flat or graded.
        for c in committed:
            final[c] = _TT
            _trace(layer_id, "committed", c, _TT)
        exit_.built(la.layer)

    return final


def transcribe(inv: Invariant, k_b_max: int = 3,
               rend: Rendering = DEFAULT) -> Optional["spot.formula"]:
    """The defining formula of an aperiodic invariant on the anchored
    stratum — the root of the `labels` memo — or None when a precondition
    fails (see `labels`)."""
    memo = labels(inv, k_b_max, rend)
    return None if memo is None else memo[inv.identity]
