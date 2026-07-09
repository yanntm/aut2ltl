"""Slot models: the numeric engine payload — per-slot domains, identity
values, and per-slot letter-class value maps. All packing semantics live
here; the C++ core sees only domains and maps.

Single automaton: one slot per state, value pack(q, S) = (q << |C|) | S.
Asynchronous product (alphabet disjoint union — a component letter drives
its component and fixes the rest, mark namespaces disjoint):
  - factored coordinates: component slot blocks concatenated; a lifted
    class acts on its block and is the identity elsewhere.
  - flat coordinates: one slot per global state tuple, values packing
    (joint destination, union of marks with per-component bit offsets) —
    exponential by nature, the predicted-blowup side of the E3 study.
"""

import itertools
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from .letters import letter_classes
from .model import Automaton, Product


@dataclass(frozen=True)
class SlotClass:
    least: str
    count: int
    maps: Tuple[Tuple[int, ...], ...]  # per slot: value -> value


@dataclass(frozen=True)
class SlotModel:
    name: str
    doms: Tuple[int, ...]
    identity: Tuple[int, ...]
    classes: Tuple[SlotClass, ...]

    def payload(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "doms": list(self.doms),
            "identity": list(self.identity),
            "classes": [
                {"least": c.least, "count": c.count,
                 "maps": [list(m) for m in c.maps]}
                for c in self.classes
            ],
        }


def pack(q: int, marks: int, n_marks: int) -> int:
    return (q << n_marks) | marks


def unpack(v: int, n_marks: int) -> Tuple[int, int]:
    return v >> n_marks, v & ((1 << n_marks) - 1)


def from_automaton(aut: Automaton) -> SlotModel:
    """One slot per state; every slot shares the class's value map."""
    dom = aut.states << aut.marks
    classes: List[SlotClass] = []
    for c in letter_classes(aut):
        vmap = tuple(
            pack(c.dst[q], marks | c.marks[q], aut.marks)
            for v in range(dom)
            for q, marks in (unpack(v, aut.marks),)
        )
        classes.append(SlotClass(c.least, c.count, (vmap,) * aut.states))
    return SlotModel(
        name=aut.name,
        doms=(dom,) * aut.states,
        identity=tuple(pack(q, 0, aut.marks) for q in range(aut.states)),
        classes=tuple(classes),
    )


def async_factored(p: Product) -> SlotModel:
    """Component slot blocks concatenated (the paper's factored
    coordinates): additive diagram size for multiplicative cardinality.
    Lifted classes are ordered by (component, least letter); their least
    letter is prefixed with the component index (disjoint alphabets)."""
    if p.mode != "async":
        raise NotImplementedError("synchronous products arrive with E4")
    comps = [from_automaton(a) for a in p.components]
    doms = tuple(d for m in comps for d in m.doms)
    identity = tuple(v for m in comps for v in m.identity)
    id_maps = [tuple(range(d)) for d in doms]
    classes: List[SlotClass] = []
    offset = 0
    for ci, m in enumerate(comps):
        block = len(m.doms)
        for c in m.classes:
            maps = list(id_maps)
            maps[offset:offset + block] = list(c.maps)
            classes.append(SlotClass(f"{ci}:{c.least}", c.count, tuple(maps)))
        offset += block
    return SlotModel(p.name, doms, identity, tuple(classes))


def async_flat(p: Product) -> SlotModel:
    """One slot per global state tuple, joint values packed as
    (destination tuple index << total marks) | union mask with
    per-component mark offsets. Everything here is exponential in the
    component count — deliberately (Lemma 4.2's side of E3)."""
    if p.mode != "async":
        raise NotImplementedError("synchronous products arrive with E4")
    auts = p.components
    comps = [letter_classes(a) for a in auts]
    joint_states = list(itertools.product(*(range(a.states) for a in auts)))
    index = {js: i for i, js in enumerate(joint_states)}
    total_marks = sum(a.marks for a in auts)
    offsets = list(itertools.accumulate([0] + [a.marks for a in auts]))[:-1]
    dom = len(joint_states) << total_marks
    mask = (1 << total_marks) - 1

    classes: List[SlotClass] = []
    for ci, aut in enumerate(auts):
        for c in comps[ci]:
            vmap: List[int] = []
            for v in range(dom):
                js, marks = joint_states[v >> total_marks], v & mask
                q = js[ci]
                dst = list(js)
                dst[ci] = c.dst[q]
                vmap.append((index[tuple(dst)] << total_marks)
                            | marks | (c.marks[q] << offsets[ci]))
            classes.append(SlotClass(f"{ci}:{c.least}", c.count,
                                     (tuple(vmap),) * len(joint_states)))
    return SlotModel(p.name + "_flat",
                     (dom,) * len(joint_states),
                     tuple(index[js] << total_marks for js in joint_states),
                     tuple(classes))
