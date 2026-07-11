"""The shared seam: a layer's scoped machine, decomposed to a reset cascade.

Both halves of the decomposition fallback (`algorithm.md`) reduce their
layer to a small deterministic machine and hand it to the bls gap bridge:
the stem half as explicit transformation images (`decompose_gens` on the
totalized within-layer machine), the loop half as a Spot automaton
(`decompose_aut` on the tail-restricted product acceptor). This module
builds those machines and records the seam's ledger row (cascade height,
per-level state counts, wall time). Formulas are not built here.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple, TYPE_CHECKING

import buddy
import spot

from aut2ltl.bls.cascade import CascadeHolder
from aut2ltl.bls.gap import decompose_gens
from aut2ltl.ltl.bdd_utils import build_point_bdd, get_ap_bdd_vars

from .. import cayley as _cayley

if TYPE_CHECKING:
    from aut2ltl.bls.cascade import Cascade
    from sosl.sos import Invariant


@dataclass(frozen=True)
class SeamRecord:
    """One ledger row of the decomposition seam."""

    n_states: int                 # scoped machine states (sink included)
    height: int                   # cascade levels
    level_sizes: Tuple[int, ...]  # per-level state counts
    n_configs: int                # configs in the cascade closure
    wall_s: float                 # decomposition wall time (seconds)

    def line(self) -> str:
        sizes = ",".join(str(s) for s in self.level_sizes)
        return (f"states={self.n_states} height={self.height} "
                f"levels=[{sizes}] configs={self.n_configs} "
                f"wall={self.wall_s:.2f}s")


@dataclass(frozen=True)
class StemCascade:
    """The stem half's decomposed layer: holder + the class → machine-state
    map (`sink` is the one extra absorbing state)."""

    holder: CascadeHolder
    record: SeamRecord
    class_state: Dict[int, int]
    sink: int


def stem_cascade(cay: "_cayley.Cayley", layer_id: int, *,
                 gap_cmd: str = "gap", timeout: int = 60) -> StemCascade:
    """Totalize the within-layer machine of `layer_id` with an absorbing exit
    sink and decompose it (counter-free by Prop 4.11, so the holonomy cascade
    is reset throughout). The cascade is enriched with the invariant's letter
    valuations so the bls operators can render guards."""
    inv: "Invariant" = cay.inv
    ab = inv.alphabet
    layer: Tuple[int, ...] = cay.layers[layer_id]
    state: Dict[int, int] = {c: i for i, c in enumerate(layer)}
    sink: int = len(layer)
    n: int = sink + 1

    letters: List[int] = list(ab.letters())
    gens: List[List[int]] = []
    for a in letters:
        img: List[int] = [0] * n
        for c, i in state.items():
            d = cay.step(c, a)
            img[i] = state.get(d, sink)
        img[sink] = sink
        gens.append(img)

    t0 = time.monotonic()
    casc: "Cascade" = decompose_gens(gens, gap_cmd=gap_cmd, timeout=timeout)
    wall = time.monotonic() - t0

    casc.aps = list(ab.aps)
    casc.letter_valuations = [
        {p: (p in set(ab.true_aps(a))) for p in ab.aps} for a in letters]
    casc.letter_masks = [
        sum(1 << i for i, p in enumerate(ab.aps) if p in set(ab.true_aps(a)))
        for a in letters]

    record = SeamRecord(
        n_states=n, height=casc.num_levels,
        level_sizes=tuple(lv.size for lv in casc.levels),
        n_configs=len(casc.all_configs()), wall_s=wall)
    return StemCascade(holder=CascadeHolder(casc), record=record,
                       class_state=state, sink=sink)


def covering_configs(holder: CascadeHolder, machine_state: int) -> Tuple[Tuple[int, ...], ...]:
    """All cascade configs covering one machine state: the fibre of the
    holonomy cover over it, within the closure — the lift section
    (`state_to_config`) plus every closure config `config_to_state` maps back
    to it. Sorted for deterministic emission order."""
    fibre: Set[Tuple[int, ...]] = {holder.config_of(machine_state)}
    for cfg in holder.all_configs():
        if holder.cascade.config_to_state.get(tuple(cfg)) == machine_state:
            fibre.add(tuple(cfg))
    return tuple(sorted(fibre))


@dataclass(frozen=True)
class ScopedAcceptor:
    """The loop half's scoped machine: the product `D × (confined walk)` as a
    deterministic complete Spot automaton (exit letters to a rejecting sink),
    with one entry state per layer class. Any product state paired with class
    `c` realizes `T_c` (residuals factor through the syntactic congruence), so
    the per-class entry choice is language-free; BFS-first is kept."""

    aut: "spot.twa_graph"
    entries: Dict[int, int]       # layer class -> product state index


def scoped_acceptor(cay: "_cayley.Cayley", layer_id: int,
                    aut_d: "spot.twa_graph") -> ScopedAcceptor:
    """Restrict the deterministic acceptor `aut_d` (deterministic, complete,
    state-based acceptance — `Language.det_parity_sbacc()`) to the states
    realizing the layer's tails: BFS the product with the prefix-class walk of
    `Cay(L)`, keep the pairs whose class lies in the layer, route every exit
    letter to an unmarked absorbing sink (rejecting under any min-even
    condition). Acceptance condition and state marks are copied from `aut_d`.
    The initial state is the BFS-first entry pair; per-class entries are
    reported for the caller to re-root (`set_init_state`)."""
    inv: "Invariant" = cay.inv
    ab = inv.alphabet
    layer: Set[int] = set(cay.layers[layer_id])

    # Letter of the invariant -> successor in D: match the letter's cube
    # (over D's own AP order, by name) against the deterministic edges.
    aps_d: List["spot.formula"] = list(aut_d.ap())
    ap_vars = get_ap_bdd_vars(aut_d)
    succ_d: List[Dict[int, int]] = [dict() for _ in range(aut_d.num_states())]
    marks_d: List[Optional["spot.mark_t"]] = [None] * aut_d.num_states()
    cubes: Dict[int, "buddy.bdd"] = {}
    for a in ab.letters():
        trues = set(ab.true_aps(a))
        mask = sum(1 << i for i, p in enumerate(aps_d) if str(p) in trues)
        cubes[a] = build_point_bdd(aut_d, mask, aps_d, ap_vars)
    for q in range(aut_d.num_states()):
        for e in aut_d.out(q):
            if marks_d[q] is None:
                marks_d[q] = e.acc
            for a, b in cubes.items():
                if (e.cond & b) != buddy.bddfalse:
                    succ_d[q][a] = e.dst

    # Product BFS from (init(D), [eps]); collect within-layer pairs.
    q0: int = aut_d.get_init_state_number()
    c0: int = inv.fold(())
    seen: Set[Tuple[int, int]] = {(q0, c0)}
    frontier: List[Tuple[int, int]] = [(q0, c0)]
    in_layer: List[Tuple[int, int]] = []
    while frontier:
        q, c = frontier.pop()
        if c in layer:
            in_layer.append((q, c))
        for a in ab.letters():
            nxt = (succ_d[q][a], cay.step(c, a))
            if nxt not in seen:
                seen.add(nxt)
                frontier.append(nxt)
    in_layer.sort()

    scoped = spot.make_twa_graph(aut_d.get_dict())
    scoped.copy_ap_of(aut_d)
    scoped.set_acceptance(aut_d.acc())
    idx: Dict[Tuple[int, int], int] = {}
    for pair in in_layer:
        idx[pair] = scoped.new_state()
    sink: int = scoped.new_state()
    scoped.new_edge(sink, sink, buddy.bddtrue)

    for (q, c), s in idx.items():
        marks = marks_d[q] if marks_d[q] is not None else spot.mark_t([])
        fan: Dict[int, "buddy.bdd"] = {}
        for a in ab.letters():
            nxt = (succ_d[q][a], cay.step(c, a))
            dst = idx.get(nxt, sink)
            fan[dst] = fan.get(dst, buddy.bddfalse) | cubes[a]
        for dst, cond in fan.items():
            scoped.new_edge(s, dst, cond, marks)

    entries: Dict[int, int] = {}
    for (q, c), s in idx.items():
        entries.setdefault(c, s)
    scoped.set_init_state(idx[in_layer[0]] if in_layer else sink)
    scoped.prop_state_acc(True)
    return ScopedAcceptor(aut=scoped, entries=entries)
