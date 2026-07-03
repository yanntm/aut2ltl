"""The graded read-off assembler: `Final = STAY∞ ∨ LEAVE` from a trigger table.

Level-agnostic (algorithm.md, "k as a parameter"): the assembler never knows
the window width. A level hands it a `TriggerTable` — full-window entries
(`G`-wrapped law) and truncated-window entries (one-shot `start` law) — plus
the park-redundancy verdicts, all BDD reasoning having happened upstream in
`windows.py`. Each entry `(trigger, offset, target)` generates four shapes:

    law       trigger → X^offset sojourn(target)
    fairness  trigger joins target's enter-disjunction (full entries only)
    park      trigger ∧ X^offset G L(target)         (target ∈ F_all)
    leave     trigger ∧ X^offset leave(target)

Degenerate inputs need no cases: empty guards and empty tables collapse the
connectives, so a loop-free, exit-free, rejecting or single-state component
yields the reduced forms the algorithm derives; with an empty `starts` list
and per-state offset-1 triggers this emits the single-letter (k = 1) label,
clause for clause.
"""

from dataclasses import dataclass, field
from typing import Dict, List, NamedTuple, Set

import spot

from .pieces import Pieces

__all__ = ["TriggerEntry", "TriggerTable", "assemble"]

_F = spot.formula


class TriggerEntry(NamedTuple):
    """One window class: `trigger` fires ⇒ the run is at `target` after
    `offset` more letters."""
    trigger: "spot.formula"
    offset: int
    target: int


@dataclass
class TriggerTable:
    """A level's transcription data: `full` windows (law under `G`, triggers
    exist at every position), `starts` (truncated windows rooted at `q0`,
    position 0 only), and the targets whose park terms are subsumed
    (`Stay_k ⊆ Enter_k`, decided upstream)."""
    full: List[TriggerEntry] = field(default_factory=list)
    starts: List[TriggerEntry] = field(default_factory=list)
    park_redundant: Set[int] = field(default_factory=set)


def _or(fs: List["spot.formula"]) -> "spot.formula":
    return _F.Or(fs) if fs else _F.ff()


def _and(fs: List["spot.formula"]) -> "spot.formula":
    return _F.And(fs) if fs else _F.tt()


def _xn(f: "spot.formula", n: int) -> "spot.formula":
    for _ in range(n):
        f = _F.X(f)
    return f


def assemble(
    aut: "spot.twa_graph", C: Set[int], q0: int,
    table: TriggerTable, pieces: Pieces,
) -> "spot.formula":
    """The label `Final = STAY∞ ∨ LEAVE` of the component `C` with initial
    state `q0`, from a level's trigger table and the letter-level pieces.
    Assumes the level's preconditions hold and the acceptance of `aut` is
    state-based generalized Büchi."""
    states = sorted(C)

    def law(e: TriggerEntry) -> "spot.formula":
        return _F.Or([_F.Not(e.trigger), _xn(pieces.sojourn(e.target), e.offset)])

    # step = ⋀ (trigger → X^offset sojourn) — the G-wrapped transition law.
    step = _and([law(e) for e in table.full])
    start = [law(e) for e in table.starts]        # position 0 only, not G-wrapped

    # enter(s) = ⋁ triggers of the full entries into s (ff when none).
    by_target: Dict[int, List[TriggerEntry]] = {}
    for e in table.full:
        by_target.setdefault(e.target, []).append(e)

    def enter(s: int) -> "spot.formula":
        return _or([e.trigger for e in by_target.get(s, [])])

    # fair = every color entered infinitely often, or park on an F_all state
    # (after a full window, after a truncated window, or on q0 from position 0).
    m = aut.num_sets()
    colors: Dict[int, Set[int]] = {s: set(aut.state_acc_sets(s).sets()) for s in states}
    every_color = _and([
        _F.G(_F.F(_or([enter(s) for s in states if i in colors[s]])))
        for i in range(m)
    ])
    f_all = {s for s in states if len(colors[s]) == m}

    def park(e: TriggerEntry) -> "spot.formula":
        tail = pieces.loop_forever(e.target)
        assert tail is not None
        return _F.And([e.trigger, _xn(tail, e.offset)])

    def parkable(s: int) -> bool:
        return (s in f_all and pieces.loop_forever(s) is not None
                and s not in table.park_redundant)

    fair_parts = [every_color]
    if m > 0:                                   # m = 0: every_color is already true
        fair_parts += [
            _F.And([enter(s), _xn(pieces.loop_forever(s), by_target[s][0].offset)])
            for s in states
            if s in by_target and parkable(s)
        ]
        fair_parts = [fair_parts[0]] + [_F.F(p) for p in fair_parts[1:]]
        fair_parts += [park(e) for e in table.starts if parkable(e.target)]
        if q0 in f_all and pieces.loop_forever(q0) is not None \
                and q0 not in table.park_redundant:
            fair_parts.append(pieces.loop_forever(q0))
    fair = _or(fair_parts)

    stay = _and([pieces.sojourn(q0)] + start + [_F.G(step), fair])

    # LEAVE = exit from q0's stretch, exit after a truncated window, or
    # traverse (the law under U) to an exit after a full window.
    def exit_via(e: TriggerEntry) -> "spot.formula":
        return _F.And([e.trigger, _xn(pieces.leave(e.target), e.offset)])

    leave_parts = [pieces.leave(q0)]
    leave_parts += [exit_via(e) for e in table.starts
                    if pieces.leave(e.target) != _F.ff()]
    witness = _or([exit_via(e) for e in table.full
                   if pieces.leave(e.target) != _F.ff()])
    if witness != _F.ff():
        leave_parts.append(_and(
            [pieces.sojourn(q0)] + start + [_F.U(step, witness)]))

    return _F.Or([stay, _or(leave_parts)])
