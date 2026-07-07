"""Condition (A) — the anchoring width of each Cayley layer.

A layer `R` (an R-class of the algebra, an SCC of `Cay(L)`) is *k-anchored*
when the within-layer action of every word readable in `R` of length at
least `k` is a partial identity (a neutral window, attributing nothing) or a
partial constant (an anchor window, resetting the layer onto its target) —
Definitions 5.4/5.5 of `research_notes/sos_toltl.md`; mixed actions are what
the condition excludes. The width ladder is monotone in `k`, and the first
passing width is decided by one fixpoint on the layer's action sets
(Lemma 5.6(v)): iterate the sets `𝒜_j` of within-layer actions of readable
length-`j` words, extended letter by letter, to their closing cycle.

Per layer this module reports the width-1 letter classification
(`exit | neutral | reset(t) | mixed`, a partial identity on a single class
being a diagonal reset — it names its class), the letter sets
`L(c)/M(c)/E(c)/A(c)` the engine's bricks quantify over, the smallest
passing width (`None` = the layer anchors at no width), and the layer action
monoid `𝒜_R` — every within-layer action of a readable word.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

from sosl.sos import Invariant, Letter

from .cayley import Cayley

Window = Tuple[Letter, ...]
"""A length-`k` word over `Σ_λ`, the graded engine's window (Def 5.5)."""

Action = Tuple[Optional[int], ...]
"""A within-layer action: for each position in the layer's sorted class
tuple, the class reached (a member of the layer) or None (the word is not
readable from there). The empty action (all None) is never stored."""


@dataclass(frozen=True)
class LayerAnchoring:
    """The condition-(A) analysis of one layer."""

    layer: Tuple[int, ...]
    letter_kind: Dict[Letter, str]          # 'exit'|'neutral'|'reset(t)'|'mixed'
    stutter: Dict[int, Tuple[Letter, ...]]  # L(c): letters fixing c
    move: Dict[int, Tuple[Letter, ...]]     # M(c): within-layer, not fixing c
    exits: Dict[int, Tuple[Letter, ...]]    # E(c): letters leaving the layer
    anchors: Dict[int, Tuple[Letter, ...]]  # A(c): letters resetting onto c
    width: Optional[int]                    # smallest passing k, None = FAIL
    monoid: FrozenSet[Action]               # 𝒜_R, actions of all readable words


def _identity(act: Action, layer: Tuple[int, ...]) -> bool:
    """Partial identity: every defined position maps to its own class."""
    return all(d is None or d == layer[i] for i, d in enumerate(act))


def _constant(act: Action) -> bool:
    """Partial constant: one image class across the defined positions."""
    return len({d for d in act if d is not None}) == 1


def _clean(act: Action, layer: Tuple[int, ...]) -> bool:
    return _identity(act, layer) or _constant(act)


def _letter_action(inv: Invariant, layer: Tuple[int, ...],
                   member: FrozenSet[int], a: Letter) -> Action:
    """The within-layer action of letter `a`: defined where source and image
    both lie in the layer."""
    d = inv.letter_class[a]
    return tuple(
        inv.mult[c][d] if inv.mult[c][d] in member else None for c in layer)


def _extend(acts: Set[Action], letter_acts: List[Action],
            pos: Dict[int, int]) -> Set[Action]:
    """The actions of one-letter-longer readable words: compose each action
    with each letter's action, dropping compositions with empty domain."""
    out: Set[Action] = set()
    for f in acts:
        for g in letter_acts:
            h = tuple(
                g[pos[fc]] if fc is not None else None for fc in f)
            if any(d is not None for d in h):
                out.add(h)
    return out


def analyze_layer(cay: Cayley, layer_id: int) -> LayerAnchoring:
    """The condition-(A) analysis of layer `layer_id` of `cay`."""
    inv = cay.inv
    layer = cay.layers[layer_id]
    member = frozenset(layer)
    pos: Dict[int, int] = {c: i for i, c in enumerate(layer)}
    letters = inv.alphabet.letters()

    letter_kind: Dict[Letter, str] = {}
    stutter: Dict[int, List[Letter]] = {c: [] for c in layer}
    move: Dict[int, List[Letter]] = {c: [] for c in layer}
    exits: Dict[int, List[Letter]] = {c: [] for c in layer}
    anchors: Dict[int, List[Letter]] = {c: [] for c in layer}
    letter_acts: List[Action] = []
    for a in letters:
        act = _letter_action(inv, layer, member, a)
        domain = [layer[i] for i, d in enumerate(act) if d is not None]
        for c in layer:
            d = inv.mult[c][inv.letter_class[a]]
            if d not in member:
                exits[c].append(a)
            elif d == c:
                stutter[c].append(a)
            else:
                move[c].append(a)
        if not domain:
            letter_kind[a] = "exit"
            continue
        letter_acts.append(act)
        images = {d for d in act if d is not None}
        if len(images) == 1:
            # A constant action anchors its target — the diagonal case
            # ({t↦t} alone, also an identity) included: it names its class.
            anchors[next(iter(images))].append(a)
        if _identity(act, layer):
            letter_kind[a] = "neutral"
        elif len(images) == 1:
            letter_kind[a] = f"reset({next(iter(images))})"
        else:
            letter_kind[a] = "mixed"

    # Lemma 5.6(v): iterate 𝒜_j to its closing cycle over set space.
    width: Optional[int]
    monoid: Set[Action] = set()
    if not letter_acts:
        width = 1  # no readable word at all: vacuously 1-anchored
    else:
        history: List[Set[Action]] = []
        seen: Dict[FrozenSet[Action], int] = {}
        acts: Set[Action] = set(letter_acts)
        while frozenset(acts) not in seen:
            seen[frozenset(acts)] = len(history)
            history.append(acts)
            monoid |= acts
            acts = _extend(acts, letter_acts, pos)
        cycle_start = seen[frozenset(acts)]
        clean = [all(_clean(a, layer) for a in s) for s in history]
        if not all(clean[cycle_start:]):
            width = None
        else:
            dirty = [j for j, ok in enumerate(clean) if not ok]
            width = dirty[-1] + 2 if dirty else 1  # 𝒜_j at history[j] has length j+1

    return LayerAnchoring(
        layer=layer,
        letter_kind=letter_kind,
        stutter={c: tuple(v) for c, v in stutter.items()},
        move={c: tuple(v) for c, v in move.items()},
        exits={c: tuple(v) for c, v in exits.items()},
        anchors={c: tuple(v) for c, v in anchors.items()},
        width=width,
        monoid=frozenset(monoid),
    )


def analyze(cay: Cayley) -> Tuple[LayerAnchoring, ...]:
    """The condition-(A) analysis of every layer, indexed by layer id."""
    return tuple(analyze_layer(cay, i) for i in range(len(cay.layers)))


def anchor_windows(cay: Cayley, layer_id: int,
                   kappa: int) -> Dict[int, Tuple[Window, ...]]:
    """`A_κ(c)` per target class: the length-`kappa` words over `Σ_λ` whose
    within-layer action is a partial constant onto `c` (Def 5.5, Thm 5.23).

    A word is readable from `c ∈ R` iff folding it from `c` never leaves the
    layer (right multiplication descends the R-order, so an escaped walk never
    returns — Prop 5.21(i)); its action is constant onto its single image
    class, the diagonal case (identity on a singleton domain) included. Words
    with two or more image classes are neutral windows, attributing nothing,
    and belong to no `A_κ(c)`."""
    inv = cay.inv
    layer = cay.layers[layer_id]
    member = frozenset(layer)
    out: Dict[int, List[Window]] = {c: [] for c in layer}
    for combo in itertools.product(inv.alphabet.letters(), repeat=kappa):
        classes = [inv.letter_class[a] for a in combo]
        images: Set[int] = set()
        for c in layer:
            cur = c
            for d in classes:
                cur = inv.mult[cur][d]
                if cur not in member:
                    break
            else:
                images.add(cur)
        if len(images) == 1:
            out[next(iter(images))].append(combo)
    return {c: tuple(v) for c, v in out.items()}
