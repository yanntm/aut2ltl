"""The GraphViz backend: a `Figure` as `digraph` text.

Generic over any invariant and any alphabet. Two uses: a picture of an arbitrary
`.sos` (``dot -Tpng``), and the layout oracle whose node placement the finer
backends reuse (``dot -Tplain``, see `layout.py`). Pure text — no subprocess.

The model's classification maps onto dot attributes: every arrow is labeled with
the CLASSES whose columns take it, and the root — when the figure keeps the
identity — gets an incoming stub from nowhere (an initial-state marker, and the
only arrow that may enter it). Nothing else is inked: the key tree, the
idempotents and the monochrome cycles are properties of what is drawn, not
further things to draw.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from .model import Figure

# Rank/node separation, in inches: the ~2.2cm x ~1.4cm grid the figures want.
RANKSEP_IN = 0.87
NODESEP_IN = 0.55

# How hard the layout pulls an arrow's endpoints into line (see `_weight`).
ROOT_WEIGHT = 10
TREE_WEIGHT = 3

def pairs_label(fig: Figure) -> str:
    """The accepting pairs as one plain-text line, ``P = { ([b],[b]), … }``."""
    inner = ", ".join(f"([{s}],[{e}])" for s, e in fig.pairs())
    return f"P = {{ {inner} }}" if inner else "P = { }"


def lambda_label(fig: Figure) -> str:
    """The letter map as one plain-text line, ``λ: a ↣ [a], b ↣ [b]``. The arrow
    says whether λ is injective: a tail arrow when every letter names a class of
    its own, a plain maplet when some letters are aliases for one class."""
    arrow = "\u21a3" if fig.lambda_injective() else "\u21a6"
    items = [f"{','.join(names)} {arrow} [{fig.label_of(c)}]"
             for names, c in fig.lambda_map()]
    return "\u03bb: " + ", ".join(items)


def class_label(fig: Figure, cls: int) -> str:
    """A class as it is written everywhere in the figure: ``[a·b]``. Nodes and
    arrows alike name classes, never letters, so both wear the brackets."""
    return f"[{fig.label_of(cls)}]"


def dot_of(fig: Figure, name: str = "cayley", pairs: bool = True,
           rankdir: str = "LR") -> str:
    """The `digraph` for ``fig``: layered left-to-right by key length (one
    ``rank=same`` group per BFS layer), nodes and edges in the figure's canonical
    order, so the text is a deterministic function of the invariant. ``pairs``
    puts P under the drawing as the graph title (the object is ``<A, P>``; only
    ``A`` has a shape, so P is a caption). ``rankdir`` is the direction the BFS
    layers run in: ``LR`` (the root at the left) or ``TB`` (the root at the top)."""
    out: List[str] = [
        f"digraph {name} {{",
        f"  rankdir={rankdir};",
        f"  ranksep={RANKSEP_IN}; nodesep={NODESEP_IN};",
        '  node [shape=box, style=rounded, fontname="serif", margin="0.06,0.03"];',
        '  edge [fontname="serif", fontsize=10, arrowsize=0.7];',
    ]
    if pairs:
        out += [f'  label="{lambda_label(fig)}\\n{pairs_label(fig)}";',
                '  labelloc="b"; labeljust="c"; fontname="serif"; fontsize=11;']
    out.append("")
    for nd in fig.nodes:
        out.append(f'  {nd.ident} [label="{class_label(fig, nd.cls)}"];')
    root = fig.root()                 # None when the identity is elided: no stub
    if root is not None:
        out += ['  _init [shape=none, label="", width=0.02, height=0.02];',
                f"  _init -> {root.ident};"]   # the root, marked as an initial state
    out.append("")

    for layer in range(fig.layers()):
        same = [nd.ident for nd in fig.nodes if nd.layer == layer]
        if same:            # layer 0 is empty when the identity is elided
            out.append(f'  {{ rank=same; {" ".join(same)}; }}')
    out.append("")

    rank = {nd.cls: i for i, nd in enumerate(fig.nodes)}
    for (src, dst), cols in grouped(fig).items():
        marks = [e for e in fig.edges if (e.src, e.dst) == (src, dst)]
        labs = [class_label(fig, c) for c in sorted(cols, key=lambda c: rank[c])]
        attrs = [f'label="{",".join(labs)}"',
                 f"weight={_weight(fig, src, dst, marks)}"]
        a, b = fig.node_of(src).ident, fig.node_of(dst).ident
        out.append(f'  {a} -> {b} [{", ".join(attrs)}];')

    out.append("}")
    return "\n".join(out) + "\n"


def _weight(fig: Figure, src: int, dst: int, marks: List) -> int:
    """How hard dot pulls an arrow's endpoints into line. It minimizes the
    weighted spread of the coordinates across a rank, so weight is the lever for
    *length*: the root's arrows get the heaviest pull, because a root left free to
    drift away from its two successors is what makes them long diagonals; the rest
    of the key tree gets a lesser pull, so a key still reads as a straight path
    down from the root. Non-tree arrows are free to be long."""
    if fig.node_of(src).is_root:
        return ROOT_WEIGHT
    return TREE_WEIGHT if any(e.is_tree for e in marks) else 1


def grouped(fig: Figure) -> Dict[Tuple[int, int], List[int]]:
    """The figure's edges by endpoint pair, each with the class ids of the columns
    that take it. Columns that agree on a target share one arrow, labeled with all
    of them (``[a],[b]``), rather than stacking one arrow per column."""
    out: Dict[Tuple[int, int], List[int]] = {}
    for e in fig.edges:
        out.setdefault((e.src, e.dst), []).append(e.col)
    return out
