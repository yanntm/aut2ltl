"""The figure model of an invariant: the multiplication table of the algebra,
classified.

One `Node` per class, one `Edge` per (class, *column*) — every column of `M`, not
only the columns the letters name — with every fact a drawing wants to show
already decided: root, idempotents, key tree, monochrome cycles. The identity is
elided by default (its row and column are fixed by the axiom); pass
`elide_identity=False` to keep it. Pure: no coordinates, no subprocess, no output
syntax. See `algorithm.md`.
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
# An arrow label breaks to a new line once a line would exceed this many characters
# (measured on the plain text, "[a·b]" = 5). A full table's labels list several
# classes, and one long line is what lies across whatever the arrow passes. 12 fits
# two three-character classes on a line ("[a·a],[b·a]").
WRAP_CHARS = 12


def wrap(items: Sequence[str], width: int = WRAP_CHARS) -> List[List[int]]:
    """The indices of ``items`` grouped into lines, greedily: a line takes items
    until the next one would push it past ``width`` characters (counting the commas
    that join them). Never empty — an item longer than ``width`` gets its own line.
    Both backends wrap the same way; only the newline syntax differs."""
    lines: List[List[int]] = [[]]
    used = 0
    for i, it in enumerate(items):
        if lines[-1] and used + 1 + len(it) > width:
            lines.append([])
            used = 0
        used += (1 if lines[-1] else 0) + len(it)
        lines[-1].append(i)
    return lines


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
    """One entry of the multiplication table, ``s -> M(s, c)``, as drawn: the
    product of the source class by the class of one *column*."""

    src: int                      # class id
    dst: int                      # class id: M(src, col)
    col: int                      # class id of the column multiplied by
    is_tree: bool                 # the key-tree (BFS-tree) edge of dst
    is_cycle: bool                # lies on a monochrome cycle of length >= 2
    is_loop: bool                 # src == dst


@dataclass(frozen=True)
class Figure:
    """The classified multiplication table of one invariant, ready to render."""

    inv: Invariant
    naming: Naming
    nodes: Tuple[Node, ...]       # DRAWN classes, sorted by shortlex display key
    edges: Tuple[Edge, ...]       # sorted by (source key, column key)
    labels: Tuple[str, ...]       # display label of EVERY class, by class id
    elided: bool                  # is the identity dropped from the drawing?

    def node_of(self, cls: int) -> Node:
        """The node of class ``cls``. Raises for the identity of an elided figure:
        it is a class of the algebra but not a thing on the page."""
        for nd in self.nodes:
            if nd.cls == cls:
                return nd
        raise KeyError(cls)

    def label_of(self, cls: int) -> str:
        """The display label of class ``cls`` — of every class, drawn or not, so
        that a caption may still name the identity of an elided figure."""
        return self.labels[cls]

    def columns(self) -> Tuple[int, ...]:
        """The class ids of the drawn columns of ``M``: every class, minus the
        identity when it is elided. Node order (shortlex by key)."""
        return tuple(nd.cls for nd in self.nodes)

    def root(self) -> Optional[Node]:
        """The identity node ``[ε]``, or None when the figure elides it. The
        backends mark it the way an initial state is marked; an elided figure has
        no such node and gets no stub."""
        return next((nd for nd in self.nodes if nd.is_root), None)

    def idempotents(self) -> Tuple[str, ...]:
        """The labels of the idempotent classes, shortlex order."""
        return tuple(nd.label for nd in self.nodes if nd.is_idem)

    def cycles(self) -> Dict[str, Tuple[Tuple[str, ...], ...]]:
        """Per drawn column, the monochrome cycles of length >= 2, each as the tuple
        of its class labels (rotated to start at its shortlex-least node). Keyed by
        the column's class label."""
        return {self.label_of(c): _cycles_of(self, c) for c in self.columns()}

    def letter_class(self, letter_index: int) -> int:
        """The class ``λ(x)`` named by the letter at display index ``letter_index``
        — the class an arrow on that letter multiplies by."""
        return self.inv.letter_class[self.naming.letters[letter_index][0]]

    def lambda_map(self) -> Tuple[Tuple[Tuple[str, ...], int], ...]:
        """The letter map λ, grouped by its image: for each class named by at least
        one letter (in node order), the display names of *all* the letters naming
        it. Grouping is the point — it is what shows λ collapsing letters.

        The class of a letter is always keyed by a letter (a one-letter word is in
        it), so two letters sharing a class are two names for one generator, and
        only one of them survives as the key."""
        groups: Dict[int, List[str]] = {}
        for i, name in enumerate(self.naming.names):
            groups.setdefault(self.letter_class(i), []).append(name)
        rank = {nd.cls: i for i, nd in enumerate(self.nodes)}
        return tuple((tuple(groups[c]), c)
                     for c in sorted(groups, key=lambda c: rank[c]))

    def lambda_injective(self) -> bool:
        """Is λ injective — does every letter name a class of its own? When it is,
        the letters *are* the generators; when it is not, some are aliases."""
        return all(len(names) == 1 for names, _ in self.lambda_map())

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


def _cycles_of(fig: Figure, col: int) -> Tuple[Tuple[str, ...], ...]:
    """The cycles of length >= 2 of the functional graph ``s -> M(s, col)`` for one
    column. Out-degree is 1, so one walk per node settles it: follow the successor,
    stamping the walk id; meeting a node of the *current* walk closes a cycle."""
    inv = fig.inv
    step = [inv.mult[s][col] for s in range(inv.n)]
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


def figure_of(inv: Invariant, naming: Optional[Naming] = None,
              elide_identity: bool = True) -> Figure:
    """The classified multiplication table of ``inv`` under ``naming`` (default:
    the machine's letter order and cube names): one node per class and one edge per
    table entry ``M(s, c)``, over EVERY column ``c``.

    ``elide_identity`` (the default) drops ``[ε]`` from the drawing, node and
    column alike — its row and column are fixed by the identity axiom, so they are
    the one part of ``M`` a reader reconstructs without being shown it. Pass False
    to draw the whole table, identity included.

    Keys are recomputed by BFS in display order — `inv.keys` is shortlex-least in
    the *machine* order and is not reused. The BFS runs over the letters and from
    the identity in every case: keys are words, and the identity is a class of the
    algebra whether or not it reaches the page. See `algorithm.md`."""
    naming = naming or Naming.machine(inv.alphabet)
    keys = _keys_by_bfs(inv, naming)
    tok = naming.tokens()

    def label(k: Sequence[int]) -> str:
        return DOT.join(naming.names[i] for i in k) if k else EPSILON

    def ident(k: Sequence[int]) -> str:
        return "".join(tok[i] for i in k) if k else "eps"

    labels = tuple(label(keys[c]) for c in range(inv.n))
    order = sorted(range(inv.n), key=lambda c: (len(keys[c]), keys[c]))
    drawn = [c for c in order if not (elide_identity and c == inv.identity)]
    nodes = tuple(
        Node(cls=c, key=keys[c], label=labels[c], ident=ident(keys[c]),
             layer=len(keys[c]), is_root=(c == inv.identity),
             is_idem=(c != inv.identity and inv.mult[c][c] == c))
        for c in drawn)

    # The key tree is a letter fact: the edge of dst is the one out of its key's
    # parent, on the COLUMN the key's last letter names.
    tree = {(_parent(keys, c, inv, naming), inv.letter_class[naming.letters[keys[c][-1]][0]]): c
            for c in range(inv.n) if keys[c]}
    fig = Figure(inv=inv, naming=naming, nodes=nodes, edges=(),
                 labels=labels, elided=elide_identity)
    on_cycle = _cycle_edges(fig)

    edges: List[Edge] = []
    for nd in nodes:
        for col in fig.columns():
            dst = inv.mult[nd.cls][col]
            edges.append(Edge(
                src=nd.cls, dst=dst, col=col,
                is_tree=(tree.get((nd.cls, col)) == dst),
                is_cycle=((nd.cls, col) in on_cycle),
                is_loop=(dst == nd.cls)))
    return Figure(inv=inv, naming=naming, nodes=nodes, edges=tuple(edges),
                  labels=labels, elided=elide_identity)


def _parent(keys: Sequence[Word], c: int, inv: Invariant, naming: Naming) -> int:
    """The class of the key of ``c`` minus its last letter — the source of ``c``'s
    key-tree edge. Requires ``keys[c]`` non-empty."""
    stem = keys[c][:-1]
    for d in range(inv.n):
        if keys[d] == stem:
            return d
    raise AssertionError(f"key prefix {stem} of class {c} names no class")


def _cycle_edges(fig: Figure) -> frozenset:
    """The set of ``(src, column)`` whose edge lies on a monochrome cycle of length
    >= 2. Computed on a Figure whose nodes are set (labels are needed) but whose
    edges are not yet built."""
    marked = set()
    label_to_cls = {lab: c for c, lab in enumerate(fig.labels)}
    for col in fig.columns():
        for cyc in _cycles_of(fig, col):
            for lab in cyc:
                marked.add((label_to_cls[lab], col))
    return frozenset(marked)
