"""The figure model of an invariant: the Cayley graph of the algebra, classified.

One `Node` per class, one `Edge` per (class, letter), with every fact a drawing
wants to show already decided — root, idempotents, key tree, monochrome cycles.
Pure: no coordinates, no subprocess, no output syntax. See `algorithm.md`.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from ..alphabet import Alphabet, Letter, Word
from ..invariant import Invariant
from ..io.serialize import render_letter

# The centre dot joining letters of a key in a plain-text label ("a·b").
DOT = "·"
# The label of the identity class.
EPSILON = "ε"


@dataclass(frozen=True)
class Naming:
    """The display letters: the sequence of (machine letter, display name) that
    fixes both the order letters are tried in (hence the keys) and the order they
    are drawn in (hence the letter index carried by every edge)."""

    letters: Tuple[Tuple[Letter, str], ...]

    @classmethod
    def machine(cls, ab: Alphabet) -> "Naming":
        """The machine's own view: every letter under its Boolean-cube name, in
        canonical mask order (for a single ``a``: ``!a`` then ``a``)."""
        return cls(tuple((a, render_letter(ab, a)) for a in ab.letters()))

    @classmethod
    def renamed(cls, ab: Alphabet, spec: str) -> "Naming":
        """Parse a ``--rename`` spec: ``'a=a,!a=b'`` — a comma-separated list of
        ``<machine cube>=<display name>``, whose ORDER is the display order. Every
        letter of the alphabet must appear exactly once (a partial spec is an
        error: an undisplayed letter would silently drop edges)."""
        by_cube = {render_letter(ab, a): a for a in ab.letters()}
        seen: List[Tuple[Letter, str]] = []
        for item in spec.split(","):
            cube, _, name = item.strip().partition("=")
            if cube not in by_cube:
                raise ValueError(f"no such letter {cube!r}; alphabet is {sorted(by_cube)}")
            if not name:
                raise ValueError(f"no display name for {cube!r} in {item!r}")
            seen.append((by_cube[cube], name))
        got = [a for a, _ in seen]
        if sorted(got) != sorted(by_cube.values()):
            raise ValueError(f"rename must cover each letter exactly once, got {spec!r}")
        return cls(tuple(seen))

    @property
    def names(self) -> Tuple[str, ...]:
        """The display names, in display order."""
        return tuple(name for _, name in self.letters)

    def tokens(self) -> Tuple[str, ...]:
        """One identifier-safe token per letter, in display order: the display
        name stripped to its alphanumerics, or ``l<i>`` when that is empty or
        would collide. Used to build node ids from keys."""
        raw = [("".join(ch for ch in name if ch.isalnum())) for name in self.names]
        return tuple(r if r and raw.count(r) == 1 else f"l{i}" for i, r in enumerate(raw))


@dataclass(frozen=True)
class Node:
    """One congruence class, as drawn."""

    cls: int                      # class id in the Invariant
    key: Tuple[int, ...]          # display key, as letter indices (empty = identity)
    label: str                    # "a·b", or "ε" for the identity
    ident: str                    # id-safe node name ("ab", "eps")
    layer: int                    # BFS depth = len(key)
    is_root: bool                 # the adjoined identity [ε]
    is_idem: bool                 # M(c,c) = c, identity excluded


@dataclass(frozen=True)
class Edge:
    """One (class, letter) transition ``s -> M(s, λ(x))``, as drawn."""

    src: int                      # class id
    dst: int                      # class id
    letter_index: int             # index in the Naming's display order
    letter_name: str              # display name
    is_tree: bool                 # the key-tree (BFS-tree) edge of dst
    is_cycle: bool                # lies on a monochrome cycle of length >= 2
    is_loop: bool                 # src == dst


@dataclass(frozen=True)
class Figure:
    """The classified Cayley graph of one invariant, ready to render."""

    inv: Invariant
    naming: Naming
    nodes: Tuple[Node, ...]       # sorted by shortlex display key
    edges: Tuple[Edge, ...]       # sorted by (source key, letter index)

    def node_of(self, cls: int) -> Node:
        """The node of class ``cls``."""
        for nd in self.nodes:
            if nd.cls == cls:
                return nd
        raise KeyError(cls)

    def label_of(self, cls: int) -> str:
        """The display label of class ``cls``."""
        return self.node_of(cls).label

    def idempotents(self) -> Tuple[str, ...]:
        """The labels of the idempotent classes, shortlex order."""
        return tuple(nd.label for nd in self.nodes if nd.is_idem)

    def cycles(self) -> Dict[str, Tuple[Tuple[str, ...], ...]]:
        """Per display letter, the monochrome cycles of length >= 2, each as the
        tuple of its class labels (rotated to start at its shortlex-least node)."""
        return {name: _cycles_of(self, i) for i, name in enumerate(self.naming.names)}

    def pair_classes(self) -> Tuple[Tuple[int, int], ...]:
        """The accepting pairs P as class-id pairs ``(s, e)``, sorted shortlex by
        stem then loop. P completes the algebra into the object ``<A, P>``, so a
        drawing carries it — but as a *caption*, never as edges: an accepting pair
        is a pair of classes, not a transition."""
        rank = {nd.cls: i for i, nd in enumerate(self.nodes)}
        return tuple(sorted(self.inv.accept, key=lambda p: (rank[p[0]], rank[p[1]])))

    def pairs(self) -> Tuple[Tuple[str, str], ...]:
        """`pair_classes` under the display labels: ``([s], [e])``."""
        return tuple((self.label_of(s), self.label_of(e))
                     for s, e in self.pair_classes())

    def layers(self) -> int:
        """The number of BFS layers (the depth of the deepest key, plus one)."""
        return 1 + max(nd.layer for nd in self.nodes)


def _keys_by_bfs(inv: Invariant, naming: Naming) -> List[Tuple[int, ...]]:
    """The display key of every class: BFS from the identity, letters tried in
    display order, first arrival wins (= shortlex-least in display order). Asserts
    freshness (nothing enters the identity) and reachability."""
    n = inv.n
    key: List[Optional[Tuple[int, ...]]] = [None] * n
    key[inv.identity] = ()
    queue = deque([inv.identity])
    while queue:
        s = queue.popleft()
        for i, (a, _) in enumerate(naming.letters):
            t = inv.mult[s][inv.letter_class[a]]
            assert t != inv.identity, (
                f"edge {s} -{naming.names[i]}-> [eps]: the identity is adjoined and "
                f"must be a source (freshness); this table is not an invariant")
            if key[t] is None:
                key[t] = tuple(key[s]) + (i,)  # type: ignore[arg-type]
                queue.append(t)
    unreachable = [c for c in range(n) if key[c] is None]
    assert not unreachable, f"classes unreachable from [eps]: {unreachable}"
    return [k for k in key]  # type: ignore[misc]


def _cycles_of(fig: Figure, li: int) -> Tuple[Tuple[str, ...], ...]:
    """The cycles of length >= 2 of the functional graph ``s -> M(s, λ(x))`` for
    the letter of display index ``li``. Out-degree is 1, so one walk per node
    settles it: follow the successor, stamping the walk id; meeting a node of the
    *current* walk closes a cycle."""
    inv, letter = fig.inv, fig.naming.letters[li][0]
    step = [inv.mult[s][inv.letter_class[letter]] for s in range(inv.n)]
    walk = [-1] * inv.n      # which walk first saw this node
    order = [-1] * inv.n     # its position within that walk
    found: List[Tuple[str, ...]] = []
    for start in range(inv.n):
        if walk[start] != -1:
            continue
        s, path = start, []
        while walk[s] == -1:
            walk[s], order[s] = start, len(path)
            path.append(s)
            s = step[s]
        if walk[s] == start:                     # closed on the current walk
            cyc = path[order[s]:]
            if len(cyc) >= 2:                    # a self-loop is not a cycle here
                labels = [fig.label_of(c) for c in cyc]
                least = min(range(len(labels)), key=lambda i: labels[i])
                found.append(tuple(labels[least:] + labels[:least]))
    return tuple(sorted(found))


def figure_of(inv: Invariant, naming: Optional[Naming] = None) -> Figure:
    """The classified Cayley graph of ``inv`` under ``naming`` (default: the
    machine's letter order and cube names). Keys are recomputed by BFS in display
    order — `inv.keys` is shortlex-least in the *machine* order and is not
    reused. See `algorithm.md`."""
    naming = naming or Naming.machine(inv.alphabet)
    keys = _keys_by_bfs(inv, naming)
    tok = naming.tokens()

    def label(k: Sequence[int]) -> str:
        return DOT.join(naming.names[i] for i in k) if k else EPSILON

    def ident(k: Sequence[int]) -> str:
        return "".join(tok[i] for i in k) if k else "eps"

    order = sorted(range(inv.n), key=lambda c: (len(keys[c]), keys[c]))
    nodes = tuple(
        Node(cls=c, key=keys[c], label=label(keys[c]), ident=ident(keys[c]),
             layer=len(keys[c]), is_root=(c == inv.identity),
             is_idem=(c != inv.identity and inv.mult[c][c] == c))
        for c in order)

    tree = {(_parent(keys, c, inv, naming), keys[c][-1]): c
            for c in range(inv.n) if keys[c]}
    fig = Figure(inv=inv, naming=naming, nodes=nodes, edges=())
    on_cycle = _cycle_edges(fig)

    edges: List[Edge] = []
    for nd in nodes:
        for i, (a, name) in enumerate(naming.letters):
            dst = inv.mult[nd.cls][inv.letter_class[a]]
            edges.append(Edge(
                src=nd.cls, dst=dst, letter_index=i, letter_name=name,
                is_tree=(tree.get((nd.cls, i)) == dst),
                is_cycle=((nd.cls, i) in on_cycle),
                is_loop=(dst == nd.cls)))
    return Figure(inv=inv, naming=naming, nodes=nodes, edges=tuple(edges))


def _parent(keys: Sequence[Word], c: int, inv: Invariant, naming: Naming) -> int:
    """The class of the key of ``c`` minus its last letter — the source of ``c``'s
    key-tree edge. Requires ``keys[c]`` non-empty."""
    stem = keys[c][:-1]
    for d in range(inv.n):
        if keys[d] == stem:
            return d
    raise AssertionError(f"key prefix {stem} of class {c} names no class")


def _cycle_edges(fig: Figure) -> frozenset:
    """The set of ``(src, letter_index)`` whose edge lies on a monochrome cycle of
    length >= 2. Computed on a Figure whose nodes are set (labels are needed) but
    whose edges are not yet built."""
    marked = set()
    label_to_cls = {nd.label: nd.cls for nd in fig.nodes}
    for li in range(len(fig.naming.letters)):
        for cyc in _cycles_of(fig, li):
            for lab in cyc:
                marked.add((label_to_cls[lab], li))
    return frozenset(marked)
